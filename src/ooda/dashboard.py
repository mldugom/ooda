from __future__ import annotations

import html
import json
import os
import socket
import subprocess
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .policy import BlockerError, parse_blocker
from urllib.parse import urlparse


def _e(value: object) -> str:
    return html.escape(str(value if value is not None else ""))


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _section(path: Path, heading: str) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    target = f"## {heading}".strip().lower()
    out: list[str] = []
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


def _git_state(repo: Path) -> dict[str, str]:
    def run(*args: str) -> str:
        try:
            cp = subprocess.run(
                ["git", "-C", str(repo), *args],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=2,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return cp.stdout.strip() if cp.returncode == 0 else ""

    branch = run("branch", "--show-current") or "detached"
    head = run("rev-parse", "--short", "HEAD") or "—"
    dirty = "yes" if run("status", "--porcelain") else "no"
    return {"branch": branch, "head": head, "dirty": dirty}


def _latest_json(directory: Path) -> tuple[Path | None, dict]:
    try:
        candidates = [p for p in directory.glob("*.json") if p.is_file()]
    except OSError:
        candidates = []
    if not candidates:
        return None, {}
    path = max(candidates, key=lambda p: p.stat().st_mtime)
    return path, _read_json(path)


def _collect_project(repo: Path) -> dict:
    project_path = repo / ".ooda" / "project.json"
    project = _read_json(project_path)
    work_path, work = _latest_json(repo / ".ooda" / "work-orders")
    trace_path, trace = _latest_json(repo / ".ooda" / "traces")
    state_path = repo / "PROJECT_STATE.md"
    view_path = repo / ".ooda" / "project-view.json"
    view = _read_json(view_path)
    if view.get("schema") != "ooda/project-view/v1":
        view = {}
    git = _git_state(repo)

    objective = _section(state_path, "Current objective") or "No current objective recorded"
    blockers = _section(state_path, "Open decisions / blockers") or "None recorded"
    next_gate = _section(state_path, "Next gate") or trace.get("next_gate") or "No gate recorded"

    work_id = work.get("id") or (work_path.stem if work_path else "—")
    trace_work_id = trace.get("work_order_id")
    result = trace.get("result") if isinstance(trace.get("result"), dict) else {}
    result_state = result.get("state") or "—"
    result_summary = result.get("summary") or "—"

    if not work:
        stage = "orient"
        controller = "idle"
    elif trace and trace_work_id == work.get("id"):
        if result_state in {"blocked", "budget_exhausted"}:
            stage = "observe"
            # A blocker that still permits exploration must not render as "nothing
            # can happen" -- that reading is what stalled whole research lanes.
            controller = "blocked"
            if result_state == "blocked":
                try:
                    blocker = parse_blocker(result.get("blocker") or "blocked")
                except BlockerError:
                    blocker = None
                if blocker is not None and blocker.exploration_allowed:
                    controller = f"blocked: {blocker.blocker_type} (exploration open)"
        elif result_state == "needs_human_gate":
            stage = "review"
            controller = "needs human gate"
        else:
            stage = "review"
            controller = "awaiting review"
    else:
        stage = "act"
        controller = "active"

    freshness_source = max(
        [p for p in (project_path, work_path, trace_path, state_path, view_path) if p and p.exists()],
        key=lambda p: p.stat().st_mtime,
        default=project_path,
    )
    try:
        updated = time.strftime("%Y-%m-%d %H:%M", time.localtime(freshness_source.stat().st_mtime))
    except OSError:
        updated = "—"

    ladder = view.get("objective_ladder") if isinstance(view.get("objective_ladder"), list) else []
    timeline = view.get("timeline") if isinstance(view.get("timeline"), list) else []
    stakeholder_summary = view.get("stakeholder_summary") if isinstance(view.get("stakeholder_summary"), str) else ""

    return {
        "repo": repo,
        "project_id": project.get("project_id") or repo.name,
        "project_class": project.get("project_class") or "—",
        "objective": objective,
        "stage": stage,
        "controller": controller,
        "work_order": work_id,
        "role": work.get("role") or "—",
        "profile": work.get("profile") or "—",
        "lenses": work.get("lenses") if isinstance(work.get("lenses"), list) else [],
        "claim": work.get("claim_level") or "n-a",
        "result_state": result_state,
        "result_summary": result_summary,
        "blocker": (result.get("blocker") if isinstance(result.get("blocker"), dict) else None),
        "blockers": blockers,
        "next_gate": next_gate,
        "branch": git["branch"],
        "head": git["head"],
        "dirty": git["dirty"],
        "updated": updated,
        "objective_ladder": ladder,
        "timeline": timeline,
        "stakeholder_summary": stakeholder_summary,
    }


def discover_projects(root: Path) -> list[dict]:
    repos: list[Path] = []
    if (root / ".ooda" / "project.json").is_file():
        repos.append(root)
    if root.is_dir():
        for child in sorted(root.iterdir()):
            if child.is_dir() and (child / ".ooda" / "project.json").is_file():
                repos.append(child)
    return [_collect_project(repo) for repo in repos]


def _pill(value: str) -> str:
    cls = "".join(ch if ch.isalnum() else "-" for ch in value.lower()).strip("-")
    return f'<span class="pill p-{_e(cls)}">{_e(value)}</span>'


def _project_view_html(project: dict) -> str:
    ladder = project.get("objective_ladder") or []
    timeline = project.get("timeline") or []
    if not ladder and not timeline:
        return ""

    ladder_bits: list[str] = []
    for item in ladder:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "provisional")
        marker = {"completed": "✓", "current": "●", "provisional": "○"}.get(status, "○")
        label = item.get("label") or ""
        ladder_bits.append(
            f'<div class="ladder-step s-{_e(status)}"><span>{marker}</span><b>{_e(label)}</b></div>'
        )

    latest = [item for item in timeline[-5:] if isinstance(item, dict)]
    timeline_bits = [
        '<div class="timeline-row timeline-head"><b>TIME</b><b>DECISION</b><b>SO WHAT</b><b>BIGGER IDEA</b></div>'
    ]
    for item in latest:
        timeline_bits.append(
            '<div class="timeline-row">'
            f'<span>{_e(item.get("at", ""))}</span>'
            f'<span>{_e(item.get("decision", ""))}</span>'
            f'<span>{_e(item.get("so_what", ""))}</span>'
            f'<span>{_e(item.get("bigger_idea", ""))}</span>'
            '</div>'
        )

    return f"""
      <details class="narrative">
        <summary>Project view · {len(timeline)} material decision{'s' if len(timeline) != 1 else ''}</summary>
        <div class="narrative-grid">
          <div>
            <div class="eyebrow">OBJECTIVE LADDER</div>
            <div class="ladder">{''.join(ladder_bits) or '<span class="muted">No ladder recorded</span>'}</div>
          </div>
          <div>
            <div class="eyebrow">RECENT DECISION TIMELINE</div>
            <div class="timeline-mini">{''.join(timeline_bits) if latest else '<span class="muted">No pivots recorded</span>'}</div>
          </div>
        </div>
      </details>
    """


def render_html(projects: list[dict], refresh_seconds: int, root: Path) -> str:
    active = sum(p["controller"] == "active" for p in projects)
    blocked = sum(p["controller"] == "blocked" for p in projects)
    review = sum(p["stage"] == "review" for p in projects)
    rows: list[str] = []
    cards: list[str] = []

    for p in projects:
        lenses = " ".join(_pill(str(x)) for x in p["lenses"][:3]) or '<span class="muted">none</span>'
        rows.append(
            f"""
            <tr>
              <td><b>{_e(p['project_id'])}</b><small>{_e(p['project_class'])}</small></td>
              <td class="objective">{_e(p['objective'])}</td>
              <td>{_pill(p['stage'])}</td>
              <td><b>{_e(p['role'])}</b><small>{_e(p['profile'])}</small></td>
              <td>{_pill(p['claim'])}</td>
              <td><b>{_e(p['work_order'])}</b><small>{_e(p['controller'])}</small></td>
              <td><b>{_e(p['branch'])}</b><small>{_e(p['head'])} · dirty {_e(p['dirty'])}</small></td>
              <td>{_e(p['next_gate'])}</td>
              <td>{_e(p['updated'])}</td>
            </tr>
            """
        )
        stakeholder = (
            f'<div class="stakeholder"><small>CURRENT STAKEHOLDER SUMMARY</small><b>{_e(p["stakeholder_summary"])}</b></div>'
            if p.get("stakeholder_summary")
            else ""
        )
        cards.append(
            f"""
            <section class="project">
              <div class="project-head">
                <div>
                  <div class="eyebrow">PROJECT CONTROL</div>
                  <h2>{_e(p['project_id'])}</h2>
                  <p>{_e(p['objective'])}</p>
                </div>
                <div>{_pill(p['stage'])}{_pill(p['claim'])}</div>
              </div>
              <div class="facts">
                <div><small>Controller</small><b>{_e(p['controller'])}</b></div>
                <div><small>Mission</small><b>{_e(p['work_order'])}</b></div>
                <div><small>Role / profile</small><b>{_e(p['role'])}</b><span>{_e(p['profile'])}</span></div>
                <div><small>Git</small><b>{_e(p['branch'])}</b><span>{_e(p['head'])} · dirty {_e(p['dirty'])}</span></div>
                <div><small>Lenses</small>{lenses}</div>
              </div>
              <div class="lane">
                <div><small>OBSERVE</small><b>{_e(p['blockers'])}</b></div>
                <span>→</span>
                <div><small>ORIENT</small><b>{_e(p['role'])} / {_e(p['profile'])}</b></div>
                <span>→</span>
                <div><small>DECIDE</small><b>{_e(p['work_order'])}</b></div>
                <span>→</span>
                <div><small>ACT / RESULT</small><b>{_e(p['result_state'])}</b><span>{_e(p['result_summary'])}</span></div>
                <span>→</span>
                <div><small>NEXT GATE</small><b>{_e(p['next_gate'])}</b></div>
              </div>
              {stakeholder}
              {_project_view_html(p)}
            </section>
            """
        )

    if not rows:
        rows.append(
            """
            <tr><td colspan="9" class="empty">
            No OODA-adopted projects found. Run <code>ooda init ...</code> in a repo under the projects root.
            </td></tr>
            """
        )

    auto = f'<meta http-equiv="refresh" content="{refresh_seconds}">' if refresh_seconds > 0 else ""
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{auto}
<title>OODA Control Room</title>
<style>
:root{{--cream:#f4eedc;--paper:#fffdf7;--ink:#24211d;--muted:#756d62;--rule:#d7ccb7;--blue:#4c78a8;--shadow:0 10px 30px rgba(53,42,27,.07)}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--cream);color:var(--ink);font:14px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}
main{{max-width:1500px;margin:auto;padding:28px}}h1,h2,p{{margin:0}}h1,h2{{font-family:Georgia,serif}}h1{{font-size:34px}}h2{{font-size:24px}}small,.muted{{color:var(--muted)}}small{{display:block;font-size:11px;margin-top:3px}}
.hero{{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:18px}}.hero p{{color:var(--muted);margin-top:7px}}
button{{border:1px solid var(--rule);border-radius:8px;background:var(--paper);padding:9px 12px;font:inherit;font-weight:700;cursor:pointer}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}}.kpi,.panel,.project{{background:var(--paper);border:1px solid var(--rule);box-shadow:var(--shadow);border-radius:12px}}
.kpi{{padding:14px 16px}}.kpi b{{font-size:27px;display:block}}.panel{{padding:14px;margin-bottom:20px}}table{{width:100%;border-collapse:collapse;min-width:1050px}}
.table-wrap{{overflow:auto}}th{{font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);text-align:left;padding:9px 8px;border-bottom:1px solid var(--rule)}}td{{padding:10px 8px;border-bottom:1px solid #e8dfcf;vertical-align:top}}
.objective{{max-width:390px}}.pill{{display:inline-block;border:1px solid var(--rule);border-radius:999px;padding:3px 8px;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;background:#f6f0e3;margin:1px}}
.p-act,.p-active,.p-evidence{{background:#e9f0f7}}.p-review,.p-qualification{{background:#f4ebd6}}.p-observe,.p-blocked{{background:#f5e5e0}}.p-orient,.p-discovery{{background:#eee9f4}}
.project{{padding:18px;margin:14px 0}}.project-head{{display:flex;justify-content:space-between;gap:20px}}.project-head p{{color:var(--muted);margin-top:5px;max-width:900px}}.eyebrow{{font-size:10px;letter-spacing:.15em;font-weight:800;color:var(--muted);margin-bottom:5px}}
.facts{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:15px 0}}.facts>div{{border-top:1px solid var(--rule);padding-top:9px}}.facts b,.facts span{{display:block}}
.lane{{display:flex;align-items:stretch;gap:8px;overflow:auto;border-top:1px solid var(--rule);padding-top:14px}}.lane>div{{min-width:180px;flex:1;background:#f8f3e8;border:1px solid #e5dac7;border-radius:9px;padding:10px}}.lane>span{{align-self:center;color:var(--muted)}}
.stakeholder{{margin-top:14px;padding:12px 14px;background:#f8f3e8;border:1px solid #e5dac7;border-radius:9px}}.stakeholder b{{display:block;font-size:15px;margin-top:3px}}
.narrative{{margin-top:12px;border-top:1px solid var(--rule);padding-top:10px}}.narrative summary{{cursor:pointer;font-weight:800}}.narrative-grid{{display:grid;grid-template-columns:minmax(220px,.7fr) minmax(0,1.8fr);gap:20px;margin-top:12px}}
.ladder{{display:grid;gap:5px}}.ladder-step{{display:grid;grid-template-columns:22px 1fr;gap:6px;align-items:start;padding:5px 0}}.ladder-step.s-provisional{{color:var(--muted)}}.ladder-step.s-current b{{text-decoration:underline;text-underline-offset:3px}}
.timeline-mini{{border:1px solid #e5dac7;border-radius:8px;overflow:hidden}}.timeline-row{{display:grid;grid-template-columns:100px minmax(140px,.8fr) minmax(180px,1.2fr) minmax(180px,1.2fr);gap:10px;padding:8px 10px;border-top:1px solid #eee5d6}}.timeline-row:first-child{{border-top:0}}.timeline-head{{font-size:10px;color:var(--muted);letter-spacing:.06em;background:#f8f3e8}}.timeline-row span{{min-width:0}}
.empty{{text-align:center;padding:28px;color:var(--muted)}}code{{background:#eee6d7;padding:2px 5px;border-radius:4px}}
@media(max-width:900px){{main{{padding:16px}}.kpis{{grid-template-columns:repeat(2,1fr)}}.facts{{grid-template-columns:1fr 1fr}}.hero{{align-items:start;flex-direction:column}}.narrative-grid{{grid-template-columns:1fr}}.timeline-mini{{overflow:auto}}.timeline-row{{min-width:760px}}}}
</style>
</head>
<body>
<main>
<div class="hero">
  <div>
    <div class="eyebrow">LOCAL · DERIVED · READ-ONLY</div>
    <h1>OODA Control Room</h1>
    <p>Controller-sized state reconstructed from OODA-adopted repos under {_e(root)}. Git/project artifacts remain authoritative.</p>
  </div>
  <div>
    <button onclick="location.reload()">Refresh now</button>
    <small>{'Auto refresh every ' + str(refresh_seconds) + 's' if refresh_seconds > 0 else 'Auto refresh off'}</small>
  </div>
</div>

<div class="kpis">
  <div class="kpi"><small>Projects</small><b>{len(projects)}</b></div>
  <div class="kpi"><small>Active missions</small><b>{active}</b></div>
  <div class="kpi"><small>Awaiting review</small><b>{review}</b></div>
  <div class="kpi"><small>Blocked</small><b>{blocked}</b></div>
</div>

<div class="panel">
  <div class="table-wrap">
  <table>
    <thead><tr><th>Project</th><th>Objective</th><th>Stage</th><th>Role</th><th>Claim</th><th>Mission</th><th>Git</th><th>Next gate</th><th>Updated</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  </div>
</div>

{''.join(cards)}
</main>
</body>
</html>"""


class _Handler(BaseHTTPRequestHandler):
    root = Path.home() / "repos"
    refresh_seconds = 60

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

    def log_message(self, fmt: str, *args: object) -> None:
        return


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def serve() -> None:
    root = Path(os.environ.get("OODA_PROJECTS_ROOT", str(Path.home() / "repos"))).expanduser()
    port = int(os.environ.get("OODA_DASHBOARD_PORT", "8791"))
    refresh = max(0, int(os.environ.get("OODA_DASHBOARD_REFRESH_SECONDS", "60")))
    _Handler.root = root
    _Handler.refresh_seconds = refresh
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"OODA Control Room serving http://127.0.0.1:{port}/")
    server.serve_forever()


def launch() -> int:
    port = int(os.environ.get("OODA_DASHBOARD_PORT", "8791"))
    url = f"http://127.0.0.1:{port}/"
    if not _port_open(port):
        log_dir = Path.home() / ".ooda"
        log_dir.mkdir(parents=True, exist_ok=True)
        log = (log_dir / "dashboard.log").open("a", encoding="utf-8")
        subprocess.Popen(
            [sys.executable, "-m", "ooda.dashboard", "--serve"],
            stdout=log,
            stderr=log,
            start_new_session=True,
            close_fds=True,
        )
        for _ in range(20):
            if _port_open(port):
                break
            time.sleep(0.1)
        else:
            print(f"OODA dashboard failed to start; see {log_dir / 'dashboard.log'}", file=sys.stderr)
            return 2
    print(url)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    return 0


def main() -> None:
    if "--serve" in sys.argv[1:]:
        serve()
        return
    raise SystemExit(launch())


if __name__ == "__main__":
    main()
