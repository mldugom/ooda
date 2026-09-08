from __future__ import annotations

import datetime as dt
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

SCHEMA = "ooda/session-telemetry/v1"
DEEPSEEK_CONTEXT_LIMIT = 1_000_000
BALANCE_TTL_SECONDS = 600


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


def _write(repo: Path, data: Dict[str, Any]) -> None:
    target = repo / ".ooda" / "session-telemetry.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".json.tmp")
    temp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(target)


def record_grok_payload(payload: Dict[str, Any]) -> Optional[Path]:
    workspace = payload.get("workspace") if isinstance(payload.get("workspace"), dict) else {}
    current_dir = str(workspace.get("current_dir") or payload.get("cwd") or os.getcwd())
    repo = _find_repo(Path(current_dir))
    if repo is None:
        return None

    model = payload.get("model") if isinstance(payload.get("model"), dict) else {}
    context = payload.get("context_window") if isinstance(payload.get("context_window"), dict) else {}
    cost = payload.get("cost") if isinstance(payload.get("cost"), dict) else {}
    effort = payload.get("effort") if isinstance(payload.get("effort"), dict) else {}

    data: Dict[str, Any] = {
        "schema": SCHEMA,
        "provider": "grok",
        "model": str(model.get("display_name") or model.get("id") or "Grok"),
        "model_id": str(model.get("id") or ""),
        "effort": str(effort.get("level") or ""),
        "session_id": str(payload.get("session_id") or ""),
        "updated_at": _now_iso(),
        "telemetry_source": "grok-status-line-json",
    }

    context_used = _as_number(context.get("context_tokens"))
    context_limit = _as_number(context.get("context_window_size"))
    context_pct = _as_number(context.get("used_percentage"))
    session_input = _as_number(context.get("session_input_tokens"))
    session_output = _as_number(context.get("session_output_tokens"))
    session_cost = _as_number(cost.get("total_cost_usd"))

    if context_used is not None:
        data["context_used"] = int(context_used)
    if context_limit is not None:
        data["context_limit"] = int(context_limit)
    if context_pct is not None:
        data["context_percent"] = context_pct
    if session_input is not None:
        data["session_input_tokens"] = int(session_input)
    if session_output is not None:
        data["session_output_tokens"] = int(session_output)
    if session_cost is not None:
        data["session_cost_usd"] = session_cost
        data["session_cost_kind"] = "provider-metered"

    _write(repo, data)
    return repo / ".ooda" / "session-telemetry.json"


def _balance_due(existing: Dict[str, Any], now: float) -> bool:
    stamp = existing.get("balance_checked_unix")
    return not isinstance(stamp, (int, float)) or now - float(stamp) >= BALANCE_TTL_SECONDS


def _fetch_deepseek_balance(api_key: str) -> Optional[Dict[str, Any]]:
    request = urllib.request.Request(
        "https://api.deepseek.com/user/balance",
        headers={"Authorization": "Bearer " + api_key, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=3.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    infos = payload.get("balance_infos")
    if not isinstance(infos, list):
        return None
    usd = next((x for x in infos if isinstance(x, dict) and x.get("currency") == "USD"), None)
    if usd is None and infos:
        usd = infos[0] if isinstance(infos[0], dict) else None
    if not isinstance(usd, dict):
        return None
    total = _as_number(usd.get("total_balance"))
    topped = _as_number(usd.get("topped_up_balance"))
    granted = _as_number(usd.get("granted_balance"))
    result: Dict[str, Any] = {"currency": str(usd.get("currency") or "")}
    if total is not None:
        result["account_balance"] = total
    if topped is not None:
        result["account_topped_up_balance"] = topped
    if granted is not None:
        result["account_granted_balance"] = granted
    return result


def record_deepseek_turn(payload: Dict[str, Any], env: Optional[Dict[str, str]] = None) -> Optional[Path]:
    env = dict(os.environ if env is None else env)
    workspace = str(payload.get("workspace") or env.get("DEEPSEEK_WORKSPACE") or os.getcwd())
    repo = _find_repo(Path(workspace))
    if repo is None:
        return None

    existing = _read_json(repo / ".ooda" / "session-telemetry.json")
    totals = payload.get("totals") if isinstance(payload.get("totals"), dict) else {}
    usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
    model = str(payload.get("model") or env.get("DEEPSEEK_MODEL") or "deepseek-v4-pro")
    provider = str(payload.get("provider") or "deepseek")

    data: Dict[str, Any] = {
        "schema": SCHEMA,
        "provider": provider,
        "model": model,
        "model_id": model,
        "session_id": str(payload.get("session_id") or env.get("DEEPSEEK_SESSION_ID") or ""),
        "mode": str(payload.get("mode") or env.get("DEEPSEEK_MODE") or ""),
        "updated_at": _now_iso(),
        "telemetry_source": "deepseek-tui-turn-end-hook",
    }

    conversation_tokens = _as_number(totals.get("conversation_tokens"))
    session_tokens = _as_number(totals.get("session_tokens"))
    input_tokens = _as_number(totals.get("input_tokens"))
    output_tokens = _as_number(totals.get("output_tokens"))
    if conversation_tokens is not None:
        data["context_used"] = int(conversation_tokens)
        data["context_limit"] = DEEPSEEK_CONTEXT_LIMIT
        data["context_percent"] = max(0.0, min(100.0, conversation_tokens / DEEPSEEK_CONTEXT_LIMIT * 100.0))
        data["context_source"] = "turn_end.totals.conversation_tokens"
    if session_tokens is not None:
        data["session_tokens"] = int(session_tokens)
    if input_tokens is not None:
        data["session_input_tokens"] = int(input_tokens)
    elif _as_number(usage.get("input_tokens")) is not None:
        data["session_input_tokens"] = int(_as_number(usage.get("input_tokens")) or 0)
    if output_tokens is not None:
        data["session_output_tokens"] = int(output_tokens)
    elif _as_number(usage.get("output_tokens")) is not None:
        data["session_output_tokens"] = int(_as_number(usage.get("output_tokens")) or 0)

    session_cost = _as_number(env.get("DEEPSEEK_SESSION_COST"))
    if session_cost is not None:
        data["session_cost_usd"] = session_cost
        data["session_cost_kind"] = "tui-estimate"

    now = time.time()
    for key in (
        "account_balance",
        "account_topped_up_balance",
        "account_granted_balance",
        "account_currency",
        "balance_checked_unix",
        "balance_updated_at",
    ):
        if key in existing:
            data[key] = existing[key]

    api_key = env.get("DEEPSEEK_API_KEY")
    if api_key and _balance_due(existing, now):
        balance = _fetch_deepseek_balance(api_key)
        if balance:
            if "account_balance" in balance:
                data["account_balance"] = balance["account_balance"]
            if "account_topped_up_balance" in balance:
                data["account_topped_up_balance"] = balance["account_topped_up_balance"]
            if "account_granted_balance" in balance:
                data["account_granted_balance"] = balance["account_granted_balance"]
            data["account_currency"] = balance.get("currency") or "USD"
            data["balance_checked_unix"] = now
            data["balance_updated_at"] = _now_iso()

    _write(repo, data)
    return repo / ".ooda" / "session-telemetry.json"


def deepseek_hook_main() -> int:
    try:
        payload = json.load(__import__("sys").stdin)
    except (OSError, json.JSONDecodeError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    record_deepseek_turn(payload)
    return 0
