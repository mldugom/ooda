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
    """Strip markdown decoration while preserving domain identifiers.

    Underscores are part of real feature/field names (rel_trade_intensity,
    date_x_series) and must not be stripped along with markdown emphasis
    markers, or the rendered vocabulary becomes unreadable and untraceable
    back to source."""
    text = str(value or "")
    text = re.sub(r"[`*#]+", "", text)
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


def _orientation(project: Dict[str, Any]) -> Dict[str, Any]:
    """Domain/value orientation for the current project.

    Each field carries a paired `<field>_set` flag so the template can render
    an explicit "not yet recorded" state instead of fallback prose that reads
    like a real (if vague) answer. A fresh Controller session or CI fixture
    with no `.ooda/domain-decision-brief.md` and no populated
    `project-view.json` orientation fields is a common, legitimate state —
    it should look visibly unset, not like the project has been oriented and
    found wanting."""
    repo = project.get("repo")
    if not isinstance(repo, Path):
        repo = Path(".")
    brief = repo / ".ooda" / "domain-decision-brief.md"
    view = _view(repo)
    current = _current_ladder_item(project)

    goal = str(view.get("goal") or _section(brief, "VALUE FUNCTION") or "").strip()
    decision = str(view.get("decision_served") or _section(brief, "DECISIONS") or "").strip()
    bottleneck = str(view.get("current_bottleneck") or _section(brief, "CURRENT BOTTLENECK") or "").strip()
    mission = str(view.get("current_mission") or current.get("label") or project.get("objective") or "").strip()
    why_now = str(view.get("why_now") or view.get("stakeholder_summary") or "").strip()

    return {
        "goal": _compact(goal, 180),
        "goal_set": bool(goal),
        "decision": _compact(decision, 190),
        "decision_set": bool(decision),
        "bottleneck": _compact(bottleneck or project.get("blockers") or "", 190),
        "bottleneck_set": bool(bottleneck or project.get("blockers")),
        "mission": _compact(mission, 180),
        "mission_set": bool(mission),
        "why_now": _compact(why_now, 190),
        "why_now_set": bool(why_now),
    }


def _field_or_unset(label: str, value: str, is_set: bool, extra_cls: str = "") -> str:
    if is_set:
        return f'<div class="domain-card {extra_cls}"><small>{legacy._e(label)}</small><b>{legacy._e(value)}</b></div>'
    return (
        f'<div class="domain-card domain-card-unset {extra_cls}"><small>{legacy._e(label)}</small>'
        '<span class="unset-chip">Not yet recorded</span></div>'
    )


def _orientation_html(project: Dict[str, Any]) -> str:
    """Meaning register: what the project is for, in as few words as
    possible. Never repeats the human-gate/control text below."""
    o = _orientation(project)
    why_now = (
        f'<div class="why-now"><small>WHY NOW</small><b>{legacy._e(o["why_now"])}</b></div>'
        if o["why_now_set"]
        else ""
    )
    return f"""
      <div class="domain-orientation-grid">
        {_field_or_unset("GOAL", o['goal'], o['goal_set'], "domain-goal")}
        {_field_or_unset("DECISION", o['decision'], o['decision_set'])}
      </div>
      {why_now}
    """


def _human_gate_html(project: Dict[str, Any], gate: str, next_if: str) -> str:
    """Control register: the single strongest affordance on the page. States
    the bottleneck, the exact ask of the human, and what happens if they say
    yes — once each, not repeated across separate cards."""
    o = _orientation(project)
    bottleneck = (
        f'<b>{legacy._e(o["bottleneck"])}</b>' if o["bottleneck_set"] else '<span class="unset-chip">Not yet recorded</span>'
    )
    return f"""
    <div class="human-gate-band">
      <div class="human-gate-head"><span class="human-gate-flag">HUMAN GATE — ACTION NEEDED</span></div>
      <div class="human-gate-body">
        <div><small>BOTTLENECK</small>{bottleneck}</div>
        <div class="human-gate-ask"><small>DECIDE</small><b>{legacy._e(gate)}</b></div>
        <div><small>IF THE GATE PASSES</small><b>{legacy._e(next_if)}</b></div>
      </div>
    </div>
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
    _current, next_if = legacy._current_and_next(project)
    gate = _compact(project.get("next_gate") or "No human/next gate recorded", 190)
    next_if = _compact(next_if, 190)
    technical = _compact(project.get("objective") or "", 220)
    telemetry = legacy._telemetry_summary_html(project)
    telemetry_block = (
        f'<div class="telemetry-register"><div class="pane-head"><b>SESSION TELEMETRY</b></div>{telemetry}</div>'
        if telemetry
        else ""
    )
    guzzler_block = legacy._cost_guzzler_html(project)
    return f"""
    <section class="project-card domain-first-control-room domain-compact-control-room">
      <style>
        .project-card.domain-compact-control-room{{max-width:1180px}}
        .human-gate-band{{border:1px solid var(--gate-strong);border-left:5px solid var(--gate-strong);background:var(--gate);border-radius:9px;padding:12px 14px;margin:11px 0 10px;box-shadow:0 2px 10px rgba(183,144,75,.12)}}
        .human-gate-head{{margin-bottom:8px}}
        .human-gate-flag{{font-size:11px;font-weight:900;letter-spacing:.1em;color:#7a5a20}}
        .human-gate-body{{display:grid;grid-template-columns:1fr 1.3fr 1fr;gap:12px;align-items:start}}
        .human-gate-body small{{display:block;font-size:11px;color:#7a5a20;font-weight:800;letter-spacing:.04em}}
        .human-gate-body b{{display:block;margin-top:4px;font-size:14px;line-height:1.4}}
        .human-gate-ask{{border-left:1px solid rgba(122,90,32,.3);border-right:1px solid rgba(122,90,32,.3);padding:0 12px}}
        .human-gate-ask b{{font-size:16px}}
        .domain-orientation-grid{{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:0 0 8px}}
        .domain-card{{background:var(--paper2);border:1px solid var(--rule);border-radius:8px;padding:10px 12px;min-width:0}}
        .domain-card small,.domain-card b{{display:block}}.domain-card b{{margin-top:4px;font-size:13px;line-height:1.35}}
        .domain-card-unset{{background:transparent;border-style:dashed}}
        .unset-chip{{display:inline-block;margin-top:5px;font-size:11px;color:var(--muted);font-style:italic;border:1px dashed var(--rule);border-radius:99px;padding:2px 8px}}
        .domain-goal{{border-top:3px solid var(--accent)}}
        .why-now{{display:grid;grid-template-columns:82px 1fr;gap:10px;align-items:start;background:#fbf8f0;border:1px solid var(--rule);border-radius:8px;padding:9px 11px;margin-bottom:2px}}
        .why-now b{{font-size:12px;line-height:1.35}}
        .tech-details{{margin-top:5px;color:var(--muted);font-size:11px}}.tech-details summary{{cursor:pointer}}
        .tech-details p{{margin-top:4px;max-width:900px}}
        .compact-timeline-row{{display:grid;grid-template-columns:84px minmax(190px,.95fr) minmax(250px,1.25fr);gap:10px;padding:8px 10px;border-bottom:1px solid #ebe2d2}}
        .compact-timeline-head{{font-size:10px;color:var(--muted);background:var(--paper2);letter-spacing:.05em}}
        .compact-timeline-row span{{min-width:0;line-height:1.4}}
        .cockpit-grid{{grid-template-columns:minmax(320px,.9fr) minmax(0,1.4fr)}}
        .ooda-rail{{margin-top:10px}}
        .telemetry-register{{margin-top:10px;max-width:640px;border:1px solid var(--rule);border-top:0;border-radius:0 0 7px 7px;padding:11px 13px 9px}}
        .telemetry-register .pane-head{{margin:-11px -13px 9px;border:1px solid var(--rule);border-bottom:0;border-radius:7px 7px 0 0;padding:6px 11px;background:var(--paper2)}}
        .telemetry-register .pane-head b{{font-size:11px}}
        .telemetry-register .telemetry-summary{{grid-template-columns:repeat(3,1fr)}}
        .telemetry-register .context-card{{border-radius:0 0 7px 7px;border-top:0}}
        @media(max-width:640px){{.telemetry-register .telemetry-summary{{grid-template-columns:repeat(2,1fr)}}}}
        @media(max-width:1050px){{.domain-orientation-grid,.cockpit-grid,.human-gate-body{{grid-template-columns:1fr}}.human-gate-ask{{border-left:0;border-right:0;border-top:1px solid rgba(122,90,32,.3);border-bottom:1px solid rgba(122,90,32,.3);padding:8px 0}}.compact-timeline-row{{grid-template-columns:76px 1fr}}.compact-timeline-row span:last-child{{grid-column:2}}}}
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

      {_human_gate_html(project, gate, next_if)}

      {_orientation_html(project)}

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
          {guzzler_block}
        </div>
        <div class="pane timeline-pane">
          <div class="pane-head"><b>RECENT DECISIONS</b><span>{len(project.get('timeline') or [])} total</span></div>
          <div class="timeline">{_compact_timeline_html(project)}</div>
        </div>
      </div>

      {telemetry_block}

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
