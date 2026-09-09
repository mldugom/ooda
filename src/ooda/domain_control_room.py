from __future__ import annotations

import os
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
    critical_path = str(view.get("critical_path") or _section(brief, "CRITICAL PATH") or "").strip()

    return {
        "goal": goal or "Goal not yet explicit — Controller should orient before consequential work.",
        "decision": decision or "Decision served not yet explicit.",
        "bottleneck": bottleneck or str(project.get("blockers") or "Current bottleneck not yet explicit."),
        "mission": mission or "No current mission recorded.",
        "why_now": why_now or "Resolve the current bottleneck before committing the next consequential mission.",
        "critical_path": critical_path,
    }


def _domain_grid(project: Dict[str, Any]) -> str:
    o = _orientation(project)
    return f"""
      <div class="domain-orientation-grid">
        <div class="domain-card domain-goal"><small>GOAL / VALUE FUNCTION</small><b>{legacy._e(o['goal'])}</b></div>
        <div class="domain-card"><small>DECISION SERVED</small><b>{legacy._e(o['decision'])}</b></div>
        <div class="domain-card bottleneck"><small>CURRENT BOTTLENECK</small><b>{legacy._e(o['bottleneck'])}</b></div>
        <div class="domain-card current-mission"><small>CURRENT MISSION</small><b>{legacy._e(o['mission'])}</b></div>
        <div class="domain-card"><small>WHY NOW</small><b>{legacy._e(o['why_now'])}</b></div>
      </div>
    """


def _project_card(project: Dict[str, Any]) -> str:
    o = _orientation(project)
    summary = project.get("stakeholder_summary") or "No stakeholder summary recorded yet."
    critical = o.get("critical_path") or summary
    _current, next_if = legacy._current_and_next(project)
    return f"""
    <section class="project-card domain-first-control-room">
      <style>
        .domain-orientation-grid{{display:grid;grid-template-columns:1.25fr 1fr 1fr;gap:9px;margin:12px 0 10px}}
        .domain-card{{background:var(--paper2);border:1px solid var(--rule);border-radius:7px;padding:10px 11px;min-width:0}}
        .domain-card small,.domain-card b{{display:block}}.domain-card b{{margin-top:3px;font-size:12px}}
        .domain-goal{{grid-column:span 2;border-top:3px solid var(--accent)}}
        .bottleneck{{border-top:3px solid #b7904b}}.current-mission{{border-top:3px solid #4c78a8}}
        .domain-control-strip{{display:grid;grid-template-columns:1.2fr 1fr;gap:9px;margin:0 0 10px}}
        .critical-path-card{{background:var(--paper2);border:1px solid var(--rule);border-radius:7px;padding:10px 11px}}
        .critical-path-card small,.critical-path-card b{{display:block}}.critical-path-card b{{margin-top:3px}}
        .technical-objective{{color:var(--muted);font-size:10px;margin-top:4px;max-width:1000px}}
        @media(max-width:1050px){{.domain-orientation-grid,.domain-control-strip{{grid-template-columns:1fr}}.domain-goal{{grid-column:auto}}}}
      </style>
      <div class="project-title">
        <div>
          <div class="eyebrow">DOMAIN / VALUE CONTROL</div>
          <h2>{legacy._e(project.get('project_id'))}</h2>
          <p>{legacy._e(o['goal'])}</p>
          <div class="technical-objective">Technical/project-state objective: {legacy._e(project.get('objective'))}</div>
        </div>
        <div class="state-badges">
          <span class="badge">{legacy._e(project.get('stage'))}</span>
          <span class="badge">{legacy._e(project.get('claim'))}</span>
        </div>
      </div>

      {_domain_grid(project)}

      <div class="domain-control-strip">
        <div class="gate-band" style="margin-top:0">
          <small>CURRENT HUMAN / CONTROL GATE</small>
          <b>{legacy._e(project.get('next_gate'))}</b>
        </div>
        <div class="critical-path-card">
          <small>NEXT IF CURRENT GATE PASSES</small>
          <b>{legacy._e(next_if)}</b>
        </div>
      </div>

      <div class="summary-context">
        <div class="critical-path-card">
          <small>VALUE CRITICAL PATH / CURRENT ORIENTATION</small>
          <b>{legacy._e(critical)}</b>
        </div>
        {legacy._context_html(project)}
      </div>

      {legacy._ooda_rail_html(project)}
      {legacy._attention_html(project)}

      <div class="cockpit-grid">
        <div class="left-stack">
          <div class="pane">
            <div class="pane-head"><b>VALUE CRITICAL PATH</b><span>evidence stages are provenance, not the roadmap</span></div>
            <div class="ladder">{legacy._ladder_html(project)}</div>
          </div>
          <div class="pane efficiency-pane">
            <div class="pane-head"><b>FEEDBACK-LOOP EFFICIENCY</b><span>cost × time to verified feedback</span></div>
            {legacy._efficiency_chart(project)}
          </div>
        </div>
        <div class="pane timeline-pane">
          <div class="pane-head"><b>MATERIAL DECISION TIMELINE</b><span>{len(project.get('timeline') or [])} pivots</span></div>
          <div class="timeline">{legacy._timeline_html(project)}</div>
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
