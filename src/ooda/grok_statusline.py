from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

STATUS_HEADER = "[ui.status_line]"
DEFAULT_REFRESH_SECONDS = 600


def _read_json(path: Path) -> Dict[str, Any]:
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


def _latest_json(directory: Path) -> Dict[str, Any]:
    try:
        candidates = [p for p in directory.glob("*.json") if p.is_file()]
    except OSError:
        return {}
    if not candidates:
        return {}
    try:
        path = max(candidates, key=lambda p: p.stat().st_mtime)
    except OSError:
        return {}
    return _read_json(path)


def _find_repo(start: Path) -> Optional[Path]:
    try:
        start = start.expanduser().resolve()
    except OSError:
        start = start.expanduser()
    candidates = [start] + list(start.parents)
    for path in candidates:
        if (path / ".ooda" / "project.json").is_file():
            return path
    return None


def _project_state(repo: Path) -> Dict[str, str]:
    project = _read_json(repo / ".ooda" / "project.json")
    view = _read_json(repo / ".ooda" / "project-view.json")
    if view.get("schema") != "ooda/project-view/v1":
        view = {}

    ladder = view.get("objective_ladder") if isinstance(view.get("objective_ladder"), list) else []
    current = ""
    for item in ladder:
        if isinstance(item, dict) and item.get("status") == "current":
            current = str(item.get("label") or "").strip()
            break
    if not current:
        current = _section(repo / "PROJECT_STATE.md", "Current objective")

    trace = _latest_json(repo / ".ooda" / "traces")
    work = _latest_json(repo / ".ooda" / "work-orders")
    next_gate = _section(repo / "PROJECT_STATE.md", "Next gate") or str(trace.get("next_gate") or "").strip()

    if not work:
        worker = "idle"
    else:
        result = trace.get("result") if isinstance(trace.get("result"), dict) else {}
        if trace.get("work_order_id") == work.get("id"):
            state = str(result.get("state") or "done")
            worker = "gate" if state == "needs_human_gate" else state
        else:
            worker = "active"

    timeline = view.get("timeline") if isinstance(view.get("timeline"), list) else []
    latest = timeline[-1] if timeline and isinstance(timeline[-1], dict) else {}
    pivot = str(latest.get("decision") or "").strip()

    return {
        "project_id": str(project.get("project_id") or repo.name),
        "current": current,
        "next_gate": next_gate,
        "worker": worker,
        "pivot": pivot,
    }


def _clip(text: str, width: int) -> str:
    text = " ".join(text.split())
    if width <= 1:
        return text[:width]
    if len(text) <= width:
        return text
    return text[: max(1, width - 1)].rstrip() + "…"


def render(payload: Dict[str, Any], *, columns: Optional[int] = None) -> str:
    workspace = payload.get("workspace") if isinstance(payload.get("workspace"), dict) else {}
    model = payload.get("model") if isinstance(payload.get("model"), dict) else {}
    context = payload.get("context_window") if isinstance(payload.get("context_window"), dict) else {}

    current_dir = str(workspace.get("current_dir") or os.getcwd())
    repo = _find_repo(Path(current_dir))
    project_id = repo.name if repo else Path(current_dir).name
    state = _project_state(repo) if repo else {
        "project_id": project_id,
        "current": "",
        "next_gate": "",
        "worker": "idle",
        "pivot": "",
    }

    model_name = str(model.get("display_name") or "Grok")
    used = context.get("used_percentage")
    try:
        ctx = f"{int(round(float(used)))}% ctx"
    except (TypeError, ValueError):
        ctx = "? ctx"
    branch = str(workspace.get("branch") or "").strip()

    width = columns or int(os.environ.get("COLUMNS", "120") or 120)
    line1_bits = [state["project_id"], model_name, ctx]
    if branch:
        line1_bits.append(branch)
    line1 = _clip(" │ ".join(line1_bits), width)

    current = state["current"] or "No OODA current objective recorded"
    gate = state["next_gate"] or "No gate recorded"
    line2 = _clip(f"OODA ● {current} │ GATE → {gate} │ worker: {state['worker']}", width)

    lines = [line1, line2]
    if width >= 120 and state["pivot"]:
        lines.append(_clip(f"LAST PIVOT → {state['pivot']}", width))
    return "\n".join(lines) + "\n"


def _toml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def configure_status_line(
    config_path: Path,
    *,
    command: str,
    refresh_seconds: int = DEFAULT_REFRESH_SECONDS,
    backup: bool = True,
) -> bool:
    config_path = config_path.expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    old = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    lines = old.splitlines()

    out: List[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == STATUS_HEADER:
            i += 1
            while i < len(lines):
                stripped = lines[i].strip()
                if stripped.startswith("[") and stripped.endswith("]"):
                    break
                i += 1
            continue
        out.append(lines[i])
        i += 1

    while out and not out[-1].strip():
        out.pop()
    if out:
        out.append("")
    out.extend([
        STATUS_HEADER,
        'type = "command"',
        f"command = {_toml_quote(command)}",
        f"refresh_interval = {int(refresh_seconds)}",
    ])
    new = "\n".join(out).rstrip() + "\n"
    if new == old:
        return False

    if backup and config_path.exists() and old:
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(config_path, config_path.with_name(config_path.name + f".backup.{stamp}"))
    config_path.write_text(new, encoding="utf-8")
    return True


def main(argv: Optional[List[str]] = None) -> int:
    del argv
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    sys.stdout.write(render(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
