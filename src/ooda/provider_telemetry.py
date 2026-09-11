from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

SCHEMA = "ooda/session-telemetry/v1"
PROVIDER_REPORTED = "PROVIDER_REPORTED"
UNAVAILABLE = "UNAVAILABLE"


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _find_repo(start: Path) -> Optional[Path]:
    try:
        current = start.expanduser().resolve()
    except OSError:
        current = start.expanduser()
    for candidate in [current] + list(current.parents):
        if (candidate / ".ooda" / "project.json").is_file():
            return candidate
    return None


def _as_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _write(repo: Path, data: Dict[str, Any]) -> Path:
    target = repo / ".ooda" / "session-telemetry.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".json.tmp")
    temp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(target)
    return target


def record_grok_payload(payload: Dict[str, Any]) -> Optional[Path]:
    """Persist only provider-reported session facts useful for continuity.

    OODA deliberately does not infer per-mission spend from coarse status-line
    snapshots. Mission economics, request-level billing, prompts, credentials,
    and arbitrary provider payload fields are not persisted here.
    """
    workspace = payload.get("workspace") if isinstance(payload.get("workspace"), dict) else {}
    current_dir = str(workspace.get("current_dir") or payload.get("cwd") or os.getcwd())
    repo = _find_repo(Path(current_dir))
    if repo is None:
        return None

    model = payload.get("model") if isinstance(payload.get("model"), dict) else {}
    context = payload.get("context_window") if isinstance(payload.get("context_window"), dict) else {}
    cost = payload.get("cost") if isinstance(payload.get("cost"), dict) else {}
    effort = payload.get("effort") if isinstance(payload.get("effort"), dict) else {}
    effort_level = str(effort.get("level") or "")

    data: Dict[str, Any] = {
        "schema": SCHEMA,
        "provider": "grok",
        "model": str(model.get("display_name") or model.get("id") or "Grok"),
        "model_id": str(model.get("id") or ""),
        "session_id": str(payload.get("session_id") or ""),
        "effort": effort_level,
        "effort_provenance": PROVIDER_REPORTED if effort_level else UNAVAILABLE,
        "worker_effort": None,
        "worker_effort_provenance": UNAVAILABLE,
        "updated_at": _now_iso(),
        "telemetry_source": "grok-status-line-json",
    }

    fields = {
        "context_used": _as_number(context.get("context_tokens")),
        "context_limit": _as_number(context.get("context_window_size")),
        "context_percent": _as_number(context.get("used_percentage")),
        "session_input_tokens": _as_number(context.get("session_input_tokens")),
        "session_output_tokens": _as_number(context.get("session_output_tokens")),
    }
    for key, value in fields.items():
        if value is not None:
            data[key] = float(value) if key == "context_percent" else int(value)

    session_cost = _as_number(cost.get("total_cost_usd"))
    if session_cost is not None:
        data["session_cost_usd"] = session_cost
        data["session_cost_kind"] = "provider-metered"
        data["session_cost_provenance"] = PROVIDER_REPORTED

    return _write(repo, data)
