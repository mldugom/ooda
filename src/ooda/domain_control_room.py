from __future__ import annotations

import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

from . import control_room as legacy
from .dashboard import discover_projects


def _section(path: Path, heading: str) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    target = f"## {heading}".strip().lower()
    out: List[str] = []
    collecting = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if collecting:
                break
            collecting = stripped.lower() == target
            continue
        if collecting and stripped:
            out.append(stripped.lstrip("- ").strip())
    return " ".join(out).strip()


def _view(repo: Path) -> Dict[str, Any]:
    data = legacy._read_json(repo / ".ooda" / "project-view.json")
    return data if data.get("schema") == "ooda/project-view/v1" else {}


def _current_ladder_item(project: Dict[str, Any]) -> Dict[str, Any]:
    for item in project.get("objective_ladder") or []:
        if isinstance(item, dict) and item.get("status") == "current":
            return item
    return {}


def _plain(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"[`*_#]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _compact(value: Any, limit: int = 190) -> str:
    text = _plain(value)
    if len(text) <= limit:
        return text
    cut = text[: limit + 1]
    boundary = max(cut.rfind(". "), cut.rfind("; "), cut.rfind(", "))
    if boundary >= int(limit * 0.55):
        cut = cut[: boundary + 1]
    else:
        cut = cut[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;.") + "…"


def _orientation(project: Dict[str, Any]) -> Dict[str, str]:
    repo = project.get("repo")
    if not isinstance(repo, Path):
        return {}
    brief = repo / ".ooda" / "domain-decision-brief.md"
    view = _view(repo)
    current = _current_ladder_item(project)

    goal = str(view.get("goal") or _section(brief, "VALUE FUNCTION") or "").strip()
    decision = str(view.get("decision_served") or _section(brief, "DECISIONS") or "").strip()
    bottleneck = str(view.get("current_bottleneck") or _section(brief, "CURRENT BOTTLENECK") or "").strip()
    mission = str(view.get("current_mission") or current.get("label") or project.get("objective") or "").strip()
    why_now = str(view.get("why_now") or view.get("stakeholder_summary") or "").strip()

    return {
        "goal": _compact(goal or "Goal not yet explicit — orient before consequential work.", 180),
        "decision": _compact(decision or "Decision served not yet explicit.", 190),
        "bottleneck": _compact(bottleneck or project.get("blockers") or "Current bottleneck not yet explicit.", 190),
        "mission": _compact(mission or "No current mission recorded.", 180),
        "why_now": _compact(why_now or "Resolve the current bottleneck before committing the next consequential mission.", 190),
    }


def _domain_grid(project: Dict[str, Any]) -> str:
    o = _orientation(project)
    return f"""
      <div class="domain-orientation-grid">
        <div class="domain-card domain-goal"><small>GOAL</small><b>{legacy._e(o['goal'])}</b></div>
        <div class="domain-card"><small>DECISION</small><b>{legacy._e(o['decision'])}</b></div>
        <div class="domain-card bottleneck"><small>BOTTLENECK</small><b>{legacy._e(o['bottleneck'])}</b></div>
        <div class="domain-card current-mission"><small>CURRENT MISSION</small><b>{legacy._e(o['mission'])}</b></div>
      </div>
      <div class="why-now"><small>WHY NOW</small><b>{legacy._e(o['why_now'])}</b></div>
    """


def _compact_timeline_html(project: Dict[str, Any]) -> str:
    timeline = [x for x in (project.get("timeline") or []) if isinstance(x, dict)]
    if not timeline:
        return '<div class="empty-state">No material decision timeline yet.</div>'
    latest = timeline[-4:]
    rows = ['<div class="compact-timeline-row compact-timeline-head"><b>DATE</b><b>DECISION</b><b>WHY IT MATTERS</b></div>']
    for item in latest:
        impact = str(item.get("so_what") or item.get("bigger_idea") or "")
        rows.append(
            '<div class="compact-timeline-row">'
            f'<span>{legacy._e(_compact(item.get("at"), 18))}</span>'
            f'<span>{legacy._e(_compact(item.get("decision"), 175))}</span>'
            f'<span>{legacy._e(_compact(impact, 210))}</span>'
            '</div>'
        )
    if len(timeline) > len(latest):
        rows.append(
            f'<div class="timeline-more">Latest {len(latest)} of {len(timeline)} decisions · '
            '<code>ooda view --all</code> for history</div>'
        )
    return "".join(rows)


def _project_card(project: Dict[str, Any]) -> str:
    o = _orientation(project)
    _current, next_if = legacy._current_and_next(project)
    gate = _compact(project.get("next_gate") or "No human/next gate recorded", 190)
    next_if = _compact(next_if, 190)
    technical = _compact(project.get("objective") or "", 220)
    return f"""
    <section class="project-card domain-first-control-room domain-compact-control-room">
      <style>
        .project-card.domain-compact-control-room{{max-width:1180px}}
        .domain-orientation-grid{{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:11px 0 8px}}
        .domain-card{{background:var(--paper2);border:1px solid var(--rule);border-radius:8px;padding:11px 12px;min-width:0}}
        .domain-card small,.domain-card b{{display:block}}.domain-card b{{margin-top:4px;font-size:13px;line-height:1.35}}
        .domain-goal{{border-top:3px solid var(--accent)}}
        .bottleneck{{border-top:3px solid #b7904b}}.current-mission{{border-top:3px solid #4c78a8}}
        .why-now{{display:grid;grid-template-columns:82px 1fr;gap:10px;align-items:start;background:#fbf8f0;border:1px solid var(--rule);border-radius:8px;padding:9px 11px;margin-bottom:9px}}
        .why-now b{{font-size:12px;line-height:1.35}}
        .domain-control-strip{{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:0 0 10px}}
        .next-card{{background:var(--paper2);border:1px solid var(--rule);border-radius:7px;padding:9px 11px}}
        .next-card small,.next-card b{{display:block}}.next-card b{{margin-top:3px;font-size:12px;line-height:1.35}}
        .tech-details{{margin-top:5px;color:var(--muted);font-size:10px}}.tech-details summary{{cursor:pointer}}
        .tech-details p{{margin-top:4px;max-width:900px}}
        .compact-timeline-row{{display:grid;grid-template-columns:84px minmax(190px,.95fr) minmax(250px,1.25fr);gap:10px;padding:8px 10px;border-bottom:1px solid #ebe2d2}}
        .compact-timeline-head{{font-size:9px;color:var(--muted);background:var(--paper2);letter-spacing:.05em}}
        .compact-timeline-row span{{min-width:0;line-height:1.4}}
        .cockpit-grid{{grid-template-columns:minmax(320px,.9fr) minmax(0,1.4fr)}}
        .ooda-rail{{margin-top:2px}}
        @media(max-width:1050px){{.domain-orientation-grid,.domain-control-strip,.cockpit-grid{{grid-template-columns:1fr}}.compact-timeline-row{{grid-template-columns:76px 1fr}}.compact-timeline-row span:last-child{{grid-column:2}}}}
      </style>
      <div class="project-title">
        <div>
          <div class="eyebrow">DOMAIN / VALUE CONTROL</div>
          <h2>{legacy._e(project.get('project_id'))}</h2>
          <details class="tech-details"><summary>Technical state</summary><p>{legacy._e(technical)}</p></details>
        </div>
        <div class="state-badges">
          <span class="badge">{legacy._e(project.get('stage'))}</span>
          <span class="badge">{legacy._e(project.get('claim'))}</span>
        </div>
      </div>

      {_domain_grid(project)}

      <div class="domain-control-strip">
        <div class="gate-band" style="margin-top:0">
          <small>CURRENT GATE</small>
          <b>{legacy._e(gate)}</b>
        </div>
        <div class="next-card">
          <small>NEXT IF GATE PASSES</small>
          <b>{legacy._e(next_if)}</b>
        </div>
      </div>

      <div class="summary-context">
        <div class="stakeholder">
          <small>SESSION</small>
          <b>Project orientation above is the cockpit. Evidence/history stay below.</b>
        </div>
        {legacy._context_html(project)}
      </div>

      {legacy._ooda_rail_html(project)}

      <div class="cockpit-grid">
        <div class="left-stack">
          <div class="pane">
            <div class="pane-head"><b>VALUE CRITICAL PATH</b><span>provenance, not stage numbering</span></div>
            <div class="ladder">{legacy._ladder_html(project)}</div>
          </div>
          <div class="pane efficiency-pane">
            <div class="pane-head"><b>FEEDBACK-LOOP EFFICIENCY</b><span>cost × time to verified feedback</span></div>
            {legacy._efficiency_chart(project)}
          </div>
        </div>
        <div class="pane timeline-pane">
          <div class="pane-head"><b>RECENT DECISIONS</b><span>{len(project.get('timeline') or [])} total</span></div>
          <div class="timeline">{_compact_timeline_html(project)}</div>
        </div>
      </div>

      <div class="meta-strip">
        <span><b>Git</b> {legacy._e(project.get('branch'))} @ {legacy._e(project.get('head'))} · dirty {legacy._e(project.get('dirty'))}</span>
        <span><b>Controller</b> {legacy._e(project.get('controller'))}</span>
        <span><b>Mission</b> {legacy._e(project.get('work_order'))}</span>
        <span><b>Updated</b> {legacy._e(project.get('updated'))}</span>
      </div>
    </section>
    """


def render_html(projects: List[Dict[str, Any]], refresh_seconds: int, root: Path) -> str:
    original = legacy._project_card
    legacy._project_card = _project_card
    try:
        return legacy.render_html(projects, refresh_seconds, root)
    finally:
        legacy._project_card = original


class _Handler(BaseHTTPRequestHandler):
    root = Path.home() / "repos"
    refresh_seconds = 15

    def do_GET(self) -> None:
        if urlparse(self.path).path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        body = render_html(discover_projects(self.root), self.refresh_seconds, self.root).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        return


def serve() -> None:
    root = Path(os.environ.get("OODA_PROJECTS_ROOT", str(Path.home() / "repos"))).expanduser()
    port = int(os.environ.get("OODA_DASHBOARD_PORT", "8792"))
    refresh = max(0, int(os.environ.get("OODA_DASHBOARD_REFRESH_SECONDS", "15")))
    _Handler.root = root
    _Handler.refresh_seconds = refresh
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"OODA Control Room serving http://127.0.0.1:{port}/")
    server.serve_forever()


def main() -> None:
    if "--serve" in sys.argv[1:]:
        serve()
        return
    from .dashboard_launcher import launch
    raise SystemExit(launch())


if __name__ == "__main__":
    main()
