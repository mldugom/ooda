from __future__ import annotations

import html
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

from .dashboard import discover_projects, _read_json


def _e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""))


def _current_gate(project: Dict[str, Any]) -> str:
    repo = project.get("repo")
    if isinstance(repo, Path):
        view = _read_json(repo / ".ooda" / "project-view.json")
        if view.get("schema") == "ooda/project-view/v1":
            gate = view.get("human_gate") or view.get("next_gate")
            if gate:
                return str(gate)
    return str(project.get("next_step") or "")


def _fresh_projects(root: Path) -> List[Dict[str, Any]]:
    projects = discover_projects(root)
    out: List[Dict[str, Any]] = []
    for project in projects:
        item = dict(project)
        gate = _current_gate(item)
        if gate:
            item["next_step"] = gate
        out.append(item)
    return out


def _field(label: str, value: Any, *, strong: bool = False) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    cls = " decision-field strong" if strong else " decision-field"
    return f'<div class="{cls.strip()}"><small>{_e(label)}</small><b>{_e(text)}</b></div>'


def _session_html(project: Dict[str, Any]) -> str:
    session = project.get("session") if isinstance(project.get("session"), dict) else {}
    if not session:
        return ""
    bits: List[str] = []
    model = str(session.get("model") or "").strip()
    if model:
        bits.append(model)
    pct = session.get("context_percent")
    if isinstance(pct, (int, float)):
        bits.append(f"{float(pct):.0f}% context")
    cost = session.get("session_cost_usd")
    if isinstance(cost, (int, float)):
        bits.append(f"${float(cost):.3f} session")
    if not bits:
        return ""
    return '<div class="session-strip"><small>ACTIVE AGENT SESSION</small><b>' + _e(" · ".join(bits)) + '</b></div>'


def _timeline_html(project: Dict[str, Any]) -> str:
    timeline = [x for x in (project.get("timeline") or []) if isinstance(x, dict)]
    if not timeline:
        return ""
    rows: List[str] = []
    for item in timeline[-3:]:
        decision = str(item.get("decision") or "").strip()
        impact = str(item.get("so_what") or item.get("bigger_idea") or "").strip()
        if not decision:
            continue
        rows.append(
            '<div class="decision-row">'
            f'<span>{_e(item.get("at") or "")}</span>'
            f'<b>{_e(decision)}</b>'
            f'<em>{_e(impact)}</em>'
            '</div>'
        )
    if not rows:
        return ""
    return '<details class="decision-history"><summary>Recent material decisions</summary>' + "".join(rows) + '</details>'


def _project_card(project: Dict[str, Any]) -> str:
    goal = _field("BUSINESS OBJECTIVE", project.get("goal"), strong=True)
    decision = _field("DECISION THIS WORK SHOULD IMPROVE", project.get("decision"), strong=True)
    current = _field("CURRENT MODELING / ENGINEERING QUESTION", project.get("current_question"), strong=True)
    evidence = _field("EVIDENCE SO FAR", project.get("evidence"))
    uncertainty = _field("WHAT IS STILL UNCERTAIN", project.get("uncertainty"))
    next_step = _field("NEXT HIGHEST-VALUE STEP", project.get("next_step"), strong=True)

    technical_bits = [
        f"repository: {_e(project.get('repo'))}",
        f"git: {_e(project.get('branch'))} @ {_e(project.get('head'))}",
        f"dirty: {_e(project.get('dirty'))}",
    ]
    if project.get("work_order"):
        technical_bits.append(f"work id: {_e(project.get('work_order'))}")
    if project.get("result_state"):
        technical_bits.append(f"result state: {_e(project.get('result_state'))}")
    if project.get("project_class"):
        technical_bits.append(f"project type: {_e(project.get('project_class'))}")

    return f"""
    <section class="project-card stakeholder-dashboard">
      <div class="project-header">
        <div>
          <small>PROJECT</small>
          <h2>{_e(project.get('project_id'))}</h2>
        </div>
        <div class="status-badge">{_e(project.get('status'))}</div>
      </div>
      <div class="business-objective">
        {goal}
        {decision}
        {current}
      </div>
      <div class="evidence-grid">
        {evidence}
        {uncertainty}
      </div>
      {next_step}
      {_session_html(project)}
      {_timeline_html(project)}
      <details class="technical-details">
        <summary>Technical details</summary>
        <p>{' · '.join(technical_bits)}</p>
        <small>Updated {_e(project.get('updated'))}</small>
      </details>
    </section>
    """


def render_html(projects: List[Dict[str, Any]], refresh_seconds: int, root: Path) -> str:
    cards = "".join(_project_card(project) for project in projects)
    if not cards:
        cards = '<div class="empty">No OODA-adopted repositories found under this projects root.</div>'
    refresh = (
        f'<meta http-equiv="refresh" content="{int(refresh_seconds)}">'
        if refresh_seconds > 0
        else ""
    )
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{refresh}
<title>OODA Control Room</title>
<style>
:root{{--bg:#f4f1e8;--paper:#fffdf8;--ink:#24221f;--muted:#726d64;--rule:#d8d0c0;--accent:#1f5b4f;--soft:#edf3f0}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{max-width:1180px;margin:auto;padding:28px 20px 60px}} h1,h2,p{{margin:0}} h1{{font-size:30px}} h2{{font-size:25px}}
header{{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:18px}} header p{{color:var(--muted);max-width:700px}}
.root{{font-size:11px;color:var(--muted);word-break:break-all}} .project-card{{background:var(--paper);border:1px solid var(--rule);border-radius:12px;padding:18px;margin:14px 0;box-shadow:0 8px 24px rgba(45,40,30,.05)}}
.project-header{{display:flex;justify-content:space-between;gap:16px;align-items:center;border-bottom:1px solid var(--rule);padding-bottom:12px;margin-bottom:13px}} small{{display:block;color:var(--muted);font-size:10px;font-weight:800;letter-spacing:.07em}}
.status-badge{{font-size:12px;font-weight:800;background:var(--soft);border:1px solid #c8d8d2;border-radius:999px;padding:6px 10px}}
.business-objective{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}} .evidence-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}}
.decision-field{{border:1px solid var(--rule);border-radius:8px;padding:11px 12px;background:#fff}} .decision-field.strong{{border-top:3px solid var(--accent)}} .decision-field b{{display:block;margin-top:5px;font-size:14px;line-height:1.4}}
.project-card>.decision-field{{margin-top:10px;background:var(--soft)}} .session-strip{{margin-top:10px;padding:8px 10px;border-left:3px solid var(--accent);background:#f7faf8}} .session-strip b{{font-size:12px}}
.technical-details,.decision-history{{margin-top:11px;color:var(--muted)}} summary{{cursor:pointer;font-weight:700}} .technical-details p{{margin-top:6px;font-size:12px}}
.decision-row{{display:grid;grid-template-columns:90px 1fr 1.2fr;gap:10px;padding:7px 0;border-bottom:1px solid #eee8dc;font-size:12px}} .decision-row em{{font-style:normal;color:var(--muted)}}
.empty{{background:var(--paper);border:1px dashed var(--rule);border-radius:10px;padding:18px;color:var(--muted)}}
@media(max-width:800px){{.business-objective,.evidence-grid,.decision-row{{grid-template-columns:1fr}} header,.project-header{{align-items:flex-start;flex-direction:column}}}}
</style>
</head>
<body><main>
<header><div><h1>Prediction Work</h1><p>What are we trying to improve, what do we know, what remains uncertain, and what should we do next?</p></div><div class="root">{_e(root)}</div></header>
{cards}
</main></body></html>"""


class _Handler(BaseHTTPRequestHandler):
    root = Path.home() / "repos"
    refresh_seconds = 15

    def do_GET(self) -> None:
        if urlparse(self.path).path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        body = render_html(_fresh_projects(self.root), self.refresh_seconds, self.root).encode("utf-8")
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
    print(f"OODA dashboard serving http://127.0.0.1:{port}/")
    server.serve_forever()


def main() -> None:
    if "--serve" in sys.argv[1:]:
        serve()
        return
    from .dashboard_launcher import launch

    raise SystemExit(launch())


if __name__ == "__main__":
    main()
