from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

from .policy import BlockerError, parse_blocker


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
    target = f"## {heading}".lower()
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


def _latest_json(directory: Path) -> tuple[Path | None, dict]:
    try:
        candidates = [p for p in directory.glob("*.json") if p.is_file()]
    except OSError:
        candidates = []
    if not candidates:
        return None, {}
    try:
        path = max(candidates, key=lambda p: p.stat().st_mtime)
    except OSError:
        return None, {}
    return path, _read_json(path)


def _git_state(repo: Path) -> dict[str, str]:
    def run(*args: str) -> str:
        try:
            cp = subprocess.run(
                ["git", "-C", str(repo), *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=2,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return cp.stdout.strip() if cp.returncode == 0 else ""

    return {
        "branch": run("branch", "--show-current") or "detached",
        "head": run("rev-parse", "--short", "HEAD") or "—",
        "dirty": "yes" if run("status", "--porcelain") else "no",
    }


def _view(repo: Path) -> dict:
    data = _read_json(repo / ".ooda" / "project-view.json")
    return data if data.get("schema") == "ooda/project-view/v1" else {}


def _session(repo: Path) -> dict:
    data = _read_json(repo / ".ooda" / "session-telemetry.json")
    return data if data.get("schema") == "ooda/session-telemetry/v1" else {}


def _collect_project(repo: Path) -> Dict[str, Any]:
    project_path = repo / ".ooda" / "project.json"
    project = _read_json(project_path)
    state_path = repo / "PROJECT_STATE.md"
    view = _view(repo)
    work_path, work = _latest_json(repo / ".ooda" / "work-orders")
    trace_path, trace = _latest_json(repo / ".ooda" / "traces")
    session = _session(repo)
    git = _git_state(repo)

    result = trace.get("result") if isinstance(trace.get("result"), dict) else {}
    result_state = str(result.get("state") or "")
    result_summary = str(result.get("summary") or "").strip()
    work_id = str(work.get("id") or (work_path.stem if work_path else ""))

    objective = _section(state_path, "Current objective")
    blockers = _section(state_path, "Open decisions / blockers")
    state_gate = _section(state_path, "Next gate")

    brief = repo / ".ooda" / "domain-decision-brief.md"
    goal = str(view.get("goal") or _section(brief, "VALUE FUNCTION") or "").strip()
    decision = str(view.get("decision_served") or _section(brief, "DECISIONS") or "").strip()
    bottleneck = str(view.get("current_bottleneck") or _section(brief, "CURRENT BOTTLENECK") or blockers).strip()
    stakeholder = str(view.get("stakeholder_summary") or "").strip()
    next_step = str(view.get("human_gate") or view.get("next_gate") or state_gate or trace.get("next_gate") or "").strip()

    if not work:
        status = "Ready to choose next work"
    elif trace and trace.get("work_order_id") == work.get("id"):
        if result_state == "needs_human_gate":
            status = "Needs your decision"
        elif result_state == "blocked":
            status = "Research constraint identified"
            try:
                blocker = parse_blocker(result.get("blocker") or "blocked")
            except BlockerError:
                blocker = None
            if blocker is not None and blocker.exploration_allowed:
                status = "Constraint identified; research can continue"
        elif result_state in {"completed", "negative_finding"}:
            status = "Result ready to review"
        else:
            status = "Result recorded"
    else:
        status = "Work in progress"

    candidates = [p for p in (project_path, state_path, work_path, trace_path, repo / ".ooda" / "project-view.json") if p and p.exists()]
    try:
        newest = max(candidates, key=lambda p: p.stat().st_mtime)
        updated = time.strftime("%Y-%m-%d %H:%M", time.localtime(newest.stat().st_mtime))
    except (ValueError, OSError):
        updated = "—"

    return {
        "repo": repo,
        "project_id": str(project.get("project_id") or repo.name),
        "project_class": str(project.get("project_class") or ""),
        "goal": goal,
        "decision": decision,
        "current_question": objective,
        "evidence": result_summary or stakeholder,
        "uncertainty": bottleneck,
        "next_step": next_step,
        "status": status,
        "result_state": result_state,
        "work_order": work_id,
        "branch": git["branch"],
        "head": git["head"],
        "dirty": git["dirty"],
        "updated": updated,
        "timeline": view.get("timeline") if isinstance(view.get("timeline"), list) else [],
        "session": session,
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


def render_html(projects: list[dict], refresh_seconds: int, root: Path) -> str:
    """Compatibility entry point for callers that imported dashboard.render_html."""
    from .compact_control_room import render_html as render

    return render(projects, refresh_seconds, root)
