from __future__ import annotations

import html
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .dashboard import discover_projects


def _e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""))


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _session_context(repo: Path) -> Optional[Dict[str, Any]]:
    """Read optional provider/session context telemetry.

    OODA never scrapes provider terminal UI. Providers or future adapters may
    write .ooda/session-telemetry.json using this deliberately tiny contract.
    """
    data = _read_json(repo / ".ooda" / "session-telemetry.json")
    if data.get("schema") != "ooda/session-telemetry/v1":
        return None
    used = data.get("context_used")
    limit = data.get("context_limit")
    if not isinstance(used, (int, float)) or not isinstance(limit, (int, float)) or limit <= 0:
        return None
    pct = max(0.0, min(100.0, float(used) / float(limit) * 100.0))
    return {
        "used": int(used),
        "limit": int(limit),
        "pct": pct,
        "provider": str(data.get("provider") or "provider"),
        "updated_at": str(data.get("updated_at") or ""),
    }


def _human_number(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return str(value)


def _stage_key(project: Dict[str, Any]) -> str:
    stage = str(project.get("stage") or "orient").lower()
    if stage == "review":
        return "verify"
    if stage in {"observe", "orient", "act"}:
        return stage
    return "orient"


def _context_html(project: Dict[str, Any]) -> str:
    repo = project.get("repo")
    telemetry = _session_context(repo) if isinstance(repo, Path) else None
    if telemetry:
        return f"""
        <div class="context-card">
          <div class="context-top">
            <span>SESSION CONTEXT · {_e(telemetry['provider'])}</span>
            <b>{telemetry['pct']:.1f}%</b>
          </div>
          <div class="context-bar"><i style="width:{telemetry['pct']:.2f}%"></i></div>
          <div class="context-foot">
            <span>{_human_number(telemetry['used'])} / {_human_number(telemetry['limit'])}</span>
            <span>{_e(telemetry['updated_at'])}</span>
          </div>
        </div>
        """
    return """
      <div class="context-card context-unavailable">
        <div class="context-top"><span>SESSION CONTEXT</span><b>provider UI</b></div>
        <div class="context-bar"><i style="width:0%"></i></div>
        <div class="context-foot">
          <span>OODA does not scrape terminal chrome.</span>
          <span>Optional telemetry hook ready.</span>
        </div>
      </div>
    """


def _ooda_loop_html(project: Dict[str, Any]) -> str:
    current = _stage_key(project)
    phases = [
        ("observe", "OBSERVE", project.get("blockers") or "Current facts / blockers"),
        ("orient", "ORIENT", f"{project.get('role') or 'controller'} / {project.get('profile') or 'general'}"),
        ("decide", "DECIDE", project.get("work_order") or "No active mission"),
        ("act", "ACT", project.get("result_state") or project.get("controller") or "idle"),
        ("verify", "VERIFY", project.get("next_gate") or "No gate recorded"),
    ]
    bits: List[str] = []
    for idx, (key, label, detail) in enumerate(phases):
        cls = "loop-step current" if key == current else "loop-step"
        bits.append(
            f'<div class="{cls}"><small>{idx + 1}</small><b>{label}</b><span>{_e(detail)}</span></div>'
        )
        if idx < len(phases) - 1:
            bits.append('<div class="loop-arrow">→</div>')
    return '<div class="loop">' + "".join(bits) + "</div>"


def _ladder_html(project: Dict[str, Any]) -> str:
    ladder = project.get("objective_ladder") or []
    if not ladder:
        return '<div class="empty-state">No durable objective ladder yet. Run <code>ooda view</code> after Controller orientation.</div>'
    bits: List[str] = []
    for item in ladder:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "provisional")
        marker = {"completed": "✓", "current": "●", "provisional": "○"}.get(status, "○")
        current = '<span class="current-tag">CURRENT</span>' if status == "current" else ""
        bits.append(
            f'<div class="ladder-row {status}"><div class="marker">{marker}</div>'
            f'<div><b>{_e(item.get("label") or "")}</b>{current}</div></div>'
        )
    return "".join(bits)


def _timeline_html(project: Dict[str, Any]) -> str:
    timeline = [x for x in (project.get("timeline") or []) if isinstance(x, dict)]
    if not timeline:
        return '<div class="empty-state">No material decision timeline yet.</div>'
    latest = timeline[-6:]
    rows = ['<div class="timeline-row timeline-head"><b>TIME</b><b>DECISION</b><b>SO WHAT</b><b>BIGGER IDEA</b></div>']
    for item in latest:
        rows.append(
            '<div class="timeline-row">'
            f'<span>{_e(item.get("at") or "")}</span>'
            f'<span>{_e(item.get("decision") or "")}</span>'
            f'<span>{_e(item.get("so_what") or "")}</span>'
            f'<span>{_e(item.get("bigger_idea") or "")}</span>'
            "</div>"
        )
    if len(timeline) > len(latest):
        rows.append(
            f'<div class="timeline-more">Showing latest {len(latest)} of {len(timeline)} material decisions · '
            '<code>ooda view --all</code> for full history</div>'
        )
    return "".join(rows)


def _project_card(project: Dict[str, Any]) -> str:
    summary = project.get("stakeholder_summary") or "No stakeholder summary recorded yet."
    return f"""
    <section class="project-card">
      <div class="project-title">
        <div>
          <div class="eyebrow">PROJECT CONTROL</div>
          <h2>{_e(project.get('project_id'))}</h2>
          <p>{_e(project.get('objective'))}</p>
        </div>
        <div class="state-badges">
          <span class="badge">{_e(project.get('stage'))}</span>
          <span class="badge">{_e(project.get('claim'))}</span>
        </div>
      </div>

      <div class="gate-band">
        <small>CURRENT HUMAN GATE / NEXT GATE</small>
        <b>{_e(project.get('next_gate'))}</b>
      </div>

      <div class="summary-context">
        <div class="stakeholder">
          <small>CURRENT STAKEHOLDER SUMMARY</small>
          <b>{_e(summary)}</b>
        </div>
        {_context_html(project)}
      </div>

      <div class="section-label">LIVE OODA LOOP</div>
      {_ooda_loop_html(project)}

      <div class="cockpit-grid">
        <div class="pane">
          <div class="pane-head"><b>OBJECTIVE LADDER</b><span>directional, not contractual</span></div>
          <div class="ladder">{_ladder_html(project)}</div>
        </div>
        <div class="pane timeline-pane">
          <div class="pane-head"><b>MATERIAL DECISION TIMELINE</b><span>{len(project.get('timeline') or [])} pivots</span></div>
          <div class="timeline">{_timeline_html(project)}</div>
        </div>
      </div>

      <div class="meta-strip">
        <span><b>Git</b> {_e(project.get('branch'))} @ {_e(project.get('head'))} · dirty {_e(project.get('dirty'))}</span>
        <span><b>Controller</b> {_e(project.get('controller'))}</span>
        <span><b>Mission</b> {_e(project.get('work_order'))}</span>
        <span><b>Updated</b> {_e(project.get('updated'))}</span>
      </div>
    </section>
    """


def render_html(projects: List[Dict[str, Any]], refresh_seconds: int, root: Path) -> str:
    active = sum(p.get("controller") == "active" for p in projects)
    review = sum(p.get("stage") == "review" for p in projects)
    blocked = sum(p.get("controller") == "blocked" for p in projects)
    auto = f'<meta http-equiv="refresh" content="{refresh_seconds}">' if refresh_seconds > 0 else ""

    tabs: List[str] = []
    panels: List[str] = []
    for idx, project in enumerate(projects):
        name = str(project.get("project_id") or f"project-{idx + 1}")
        active_cls = " active" if idx == 0 else ""
        tabs.append(
            f'<button class="project-tab{active_cls}" data-project-tab="{idx}" '
            f'data-project-name="{_e(name)}" role="tab" aria-selected="{"true" if idx == 0 else "false"}" '
            f'onclick="showProject({idx}, this.dataset.projectName)">'
            f'<span>{_e(name)}</span><small>{_e(project.get("stage") or "orient")}</small></button>'
        )
        panels.append(
            f'<div class="project-panel{active_cls}" data-project-panel="{idx}" role="tabpanel">'
            f'{_project_card(project)}</div>'
        )

    if projects:
        project_area = (
            '<div class="project-tabs" role="tablist" aria-label="Projects">'
            + "".join(tabs)
            + '</div><div class="project-panels">'
            + "".join(panels)
            + "</div>"
        )
    else:
        project_area = '<div class="empty-room">No OODA-adopted projects found under this projects root.</div>'

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{auto}
<title>OODA Control Room</title>
<style>
:root{{--bg:#f4eedc;--paper:#fffdf7;--paper2:#f8f3e8;--ink:#24211d;--muted:#756d62;--rule:#d7ccb7;--accent:#4c78a8;--accent-soft:#e9f0f7;--gate:#f4ebd6;--danger:#f5e5e0;--shadow:0 8px 24px rgba(64,49,28,.08)}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}
main{{max-width:1500px;margin:auto;padding:26px 28px 40px}}
h1,h2,p{{margin:0}}h1,h2{{font-family:Georgia,"Times New Roman",serif;font-weight:700}}h1{{font-size:34px;letter-spacing:-.02em}}h2{{font-size:27px}}
small{{color:var(--muted);font-size:11px}}code{{background:#eee6d7;border:1px solid var(--rule);padding:1px 5px;border-radius:4px}}
.hero{{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:15px}}.hero p{{color:var(--muted);margin-top:5px}}.eyebrow,.section-label{{font-size:10px;font-weight:800;letter-spacing:.15em;color:var(--muted)}}
button{{font:inherit}}
.hero button{{background:var(--paper);color:var(--ink);border:1px solid var(--rule);border-radius:6px;padding:8px 11px;font-weight:700;cursor:pointer;box-shadow:0 1px 0 rgba(0,0,0,.03)}}.hero>div:last-child{{display:grid;justify-items:end;gap:3px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:15px}}.kpi{{background:var(--paper);border:1px solid var(--rule);border-radius:8px;padding:11px 13px;box-shadow:0 2px 8px rgba(64,49,28,.04)}}.kpi b{{display:block;font:700 23px/1.1 Georgia,"Times New Roman",serif;margin-top:2px}}
.project-tabs{{display:flex;gap:0;overflow:auto;border-bottom:2px solid var(--ink);margin:4px 0 0}}.project-tab{{appearance:none;background:transparent;color:var(--muted);border:0;border-top:3px solid transparent;padding:10px 17px 9px;cursor:pointer;text-align:left;min-width:150px}}.project-tab span,.project-tab small{{display:block}}.project-tab span{{font-weight:800;font-size:14px;color:inherit}}.project-tab small{{font-size:9px;letter-spacing:.08em;text-transform:uppercase;margin-top:1px}}.project-tab:hover{{background:rgba(255,253,247,.52);color:var(--ink)}}.project-tab.active{{background:var(--paper);color:var(--ink);border-top-color:var(--accent)}}.project-tab.active small{{color:var(--accent);font-weight:800}}
.project-panel{{display:none}}.project-panel.active{{display:block}}
.project-card{{background:var(--paper);border:1px solid var(--rule);border-top:0;border-radius:0 0 10px 10px;padding:19px;box-shadow:var(--shadow)}}.project-title{{display:flex;justify-content:space-between;gap:20px}}.project-title p{{color:var(--muted);margin-top:4px;max-width:1000px}}
.state-badges{{white-space:nowrap}}.badge{{display:inline-block;border:1px solid var(--rule);background:var(--paper2);border-radius:999px;padding:3px 8px;margin-left:5px;text-transform:uppercase;font-size:9px;font-weight:800;letter-spacing:.04em}}
.gate-band{{margin-top:14px;border-left:4px solid #b7904b;background:var(--gate);padding:10px 12px}}.gate-band small,.gate-band b{{display:block}}.gate-band b{{margin-top:2px;font-size:15px}}
.summary-context{{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(260px,.7fr);gap:10px;margin:10px 0 16px}}.stakeholder,.context-card{{background:var(--paper2);border:1px solid var(--rule);border-radius:7px;padding:11px 12px}}.stakeholder small,.stakeholder b{{display:block}}.stakeholder b{{margin-top:3px}}
.context-top,.context-foot{{display:flex;justify-content:space-between;gap:12px}}.context-top{{font-size:11px;font-weight:800;letter-spacing:.05em}}.context-foot{{font-size:11px;color:var(--muted);margin-top:5px}}.context-bar{{height:7px;background:#e7decd;border:1px solid var(--rule);border-radius:99px;overflow:hidden;margin-top:8px}}.context-bar i{{display:block;height:100%;background:var(--accent)}}.context-unavailable .context-bar i{{background:#c9beaa}}
.section-label{{margin:12px 0 7px}}.loop{{display:grid;grid-template-columns:minmax(150px,1fr) 25px minmax(150px,1fr) 25px minmax(150px,1fr) 25px minmax(150px,1fr) 25px minmax(150px,1fr);gap:5px;align-items:stretch}}.loop-step{{border:1px solid var(--rule);background:var(--paper2);border-radius:7px;padding:10px}}.loop-step small,.loop-step b,.loop-step span{{display:block}}.loop-step b{{font-size:12px;margin:2px 0}}.loop-step span{{font-size:11px;color:var(--muted)}}.loop-step.current{{border:2px solid var(--accent);background:var(--accent-soft);padding:9px}}.loop-step.current b{{color:#2f5f8f}}.loop-arrow{{display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:18px}}
.cockpit-grid{{display:grid;grid-template-columns:minmax(280px,.72fr) minmax(0,1.7fr);gap:12px;margin-top:14px}}.pane{{border:1px solid var(--rule);background:var(--paper);border-radius:8px;overflow:hidden}}.pane-head{{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:10px 12px;border-bottom:1px solid var(--rule);background:var(--paper2)}}.pane-head span{{font-size:11px;color:var(--muted)}}
.ladder{{padding:8px 12px}}.ladder-row{{display:grid;grid-template-columns:25px 1fr;gap:7px;padding:6px 0;border-bottom:1px solid #ebe2d2}}.ladder-row:last-child{{border-bottom:0}}.ladder-row.provisional{{color:var(--muted)}}.ladder-row.current{{color:#2f5f8f;background:linear-gradient(90deg,var(--accent-soft),transparent);margin:0 -12px;padding:7px 12px}}.marker{{font-weight:900}}.current-tag{{display:inline-block;margin-left:7px;font-size:9px;border:1px solid var(--accent);color:#2f5f8f;background:#f4f8fc;padding:1px 5px;border-radius:99px;vertical-align:2px}}
.timeline{{overflow:auto}}.timeline-row{{display:grid;grid-template-columns:90px minmax(170px,.9fr) minmax(190px,1.15fr) minmax(190px,1.15fr);gap:10px;padding:8px 10px;border-bottom:1px solid #ebe2d2;min-width:760px}}.timeline-head{{font-size:10px;color:var(--muted);background:var(--paper2);letter-spacing:.06em}}.timeline-row span{{min-width:0}}.timeline-more{{padding:8px 10px;color:var(--muted);font-size:11px}}
.empty-state,.empty-room{{padding:18px;color:var(--muted);background:var(--paper);border:1px solid var(--rule)}}.meta-strip{{display:flex;flex-wrap:wrap;gap:16px;border-top:1px solid var(--rule);padding-top:10px;margin-top:12px;color:var(--muted);font-size:11px}}.meta-strip b{{color:var(--ink)}}
@media(max-width:1000px){{main{{padding:14px}}.kpis{{grid-template-columns:repeat(2,1fr)}}.summary-context,.cockpit-grid{{grid-template-columns:1fr}}.loop{{display:flex;overflow:auto}}.loop-step{{min-width:180px}}.loop-arrow{{min-width:20px}}.hero,.project-title{{align-items:start;flex-direction:column}}.project-tabs{{margin-top:8px}}.project-tab{{min-width:135px}}}}
</style>
<script>
function showProject(index, name) {{
  document.querySelectorAll('[data-project-panel]').forEach(function(el, i) {{
    el.classList.toggle('active', i === index);
  }});
  document.querySelectorAll('[data-project-tab]').forEach(function(el, i) {{
    var active = i === index;
    el.classList.toggle('active', active);
    el.setAttribute('aria-selected', active ? 'true' : 'false');
  }});
  try {{ localStorage.setItem('ooda.activeProject', name || ''); }} catch (e) {{}}
}}
window.addEventListener('DOMContentLoaded', function() {{
  var tabs = Array.prototype.slice.call(document.querySelectorAll('[data-project-tab]'));
  if (!tabs.length) return;
  var saved = '';
  try {{ saved = localStorage.getItem('ooda.activeProject') || ''; }} catch (e) {{}}
  var idx = tabs.findIndex(function(tab) {{ return tab.dataset.projectName === saved; }});
  if (idx < 0) idx = 0;
  showProject(idx, tabs[idx].dataset.projectName);
}});
</script>
</head>
<body>
<main>
  <div class="hero">
    <div>
      <div class="eyebrow">LOCAL · DERIVED · READ-ONLY</div>
      <h1>OODA Control Room</h1>
      <p>Live companion view for durable OODA state under {_e(root)}. Git/project artifacts remain authoritative.</p>
    </div>
    <div>
      <button onclick="location.reload()">Refresh now</button>
      <small>{"Auto refresh every " + str(refresh_seconds) + "s" if refresh_seconds > 0 else "Auto refresh off"}</small>
    </div>
  </div>
  <div class="kpis">
    <div class="kpi"><small>Projects</small><b>{len(projects)}</b></div>
    <div class="kpi"><small>Active missions</small><b>{active}</b></div>
    <div class="kpi"><small>Human gates / review</small><b>{review}</b></div>
    <div class="kpi"><small>Blocked</small><b>{blocked}</b></div>
  </div>
  {project_area}
</main>
</body>
</html>"""


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
    port = int(os.environ.get("OODA_DASHBOARD_PORT", "8791"))
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
