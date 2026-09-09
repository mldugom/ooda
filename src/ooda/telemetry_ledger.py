from __future__ import annotations

"""Small local append-only, provider-neutral telemetry ledger.

Telemetry is derived operational data. It is never project authority — it
answers "what cost money?", it does not decide anything. One JSONL file per
repo at `.ooda/telemetry/events.jsonl`; each line is one
`ooda/telemetry-event/v1` record.

Grok Build's supported status-line hook reports *cumulative session*
totals (context occupancy, session cost), re-emitted on every status
update (roughly every 10 minutes, or on session change) rather than one
event per API request. Recording every snapshot verbatim would double
count. Each snapshot is therefore turned into a *delta* event (the
increase since the last known snapshot for that session_id) before it is
appended, and an unchanged snapshot is a no-op rather than a duplicate
row. This keeps "cumulative session cost" correct without requiring a
proxy on model traffic.

Mission attribution is conservative: a delta is attributed to a work
order only when exactly one work order in the repo has no trace yet (an
unambiguous single open mission). Any other state — no open work order,
or more than one — is recorded as unattributed. OODA does not invent
mission economics.

No prompts, completions, or credentials are ever written here.
"""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .xai_usage import EXACT_API, LOCAL_DERIVED, UNAVAILABLE, is_present, parse_usage

SCHEMA = "ooda/telemetry-event/v1"
LEDGER_RELATIVE_PATH = Path(".ooda") / "telemetry" / "events.jsonl"


def _now_iso() -> str:
    import datetime as dt

    return dt.datetime.now(dt.timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def ledger_path(repo: Path) -> Path:
    return repo / LEDGER_RELATIVE_PATH


def _current_open_work_order_id(repo: Path) -> Optional[str]:
    """The one work order with no trace yet, if unambiguous. See module
    docstring — this is deliberately conservative."""
    work_orders_dir = repo / ".ooda" / "work-orders"
    traces_dir = repo / ".ooda" / "traces"
    if not work_orders_dir.is_dir():
        return None

    traced_ids = set()
    if traces_dir.is_dir():
        for path in traces_dir.glob("*.json"):
            trace = _read_json(path)
            work_order_id = trace.get("work_order_id")
            if work_order_id:
                traced_ids.add(str(work_order_id))

    open_ids: List[str] = []
    for path in work_orders_dir.glob("*.json"):
        data = _read_json(path)
        work_order_id = str(data.get("id") or path.stem)
        if work_order_id not in traced_ids:
            open_ids.append(work_order_id)

    if len(open_ids) == 1:
        return open_ids[0]
    return None


def _last_event(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    last: Optional[Dict[str, Any]] = None
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict):
                    last = record
    except OSError:
        return None
    return last


def _last_event_for_session(path: Path, session_id: str) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    last: Optional[Dict[str, Any]] = None
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict) and record.get("session_id") == session_id:
                    last = record
    except OSError:
        return None
    return last


def record_snapshot(
    repo: Path,
    *,
    provider: str,
    model: str,
    session_id: str,
    cumulative_session_cost_usd: Optional[float],
    cumulative_session_cost_provenance: str,
    context_used: Optional[int] = None,
    session_input_tokens: Optional[int] = None,
    session_output_tokens: Optional[int] = None,
    usage: Any = None,
) -> Optional[Path]:
    """Append one delta event for a session snapshot, or no-op if the
    snapshot is unchanged from the last one recorded for this session
    (duplicate status-line refresh with no new activity)."""
    path = ledger_path(repo)
    session_id = session_id or "unknown-session"

    fingerprint = (context_used, session_input_tokens, session_output_tokens, cumulative_session_cost_usd)
    previous = _last_event_for_session(path, session_id)
    if previous is not None and previous.get("_fingerprint") == list(fingerprint):
        return None  # idempotent: nothing changed since the last snapshot

    previous_cost = previous.get("cumulative_session_cost_usd") if previous else None
    delta_cost: Optional[float] = None
    delta_provenance = UNAVAILABLE

    request_usage = parse_usage(usage) if is_present(usage) else None
    if request_usage and request_usage.get("cost_usd") is not None:
        delta_cost = request_usage["cost_usd"]
        delta_provenance = EXACT_API
    elif cumulative_session_cost_usd is not None:
        if isinstance(previous_cost, (int, float)) and cumulative_session_cost_usd >= previous_cost:
            delta_cost = cumulative_session_cost_usd - previous_cost
        else:
            delta_cost = cumulative_session_cost_usd  # first snapshot, or session reset
        delta_provenance = LOCAL_DERIVED if delta_cost is not None else UNAVAILABLE

    work_order_id = _current_open_work_order_id(repo)

    event: Dict[str, Any] = {
        "schema": SCHEMA,
        "id": str(uuid.uuid4()),
        "at": _now_iso(),
        "provider": provider,
        "model": model,
        "session_id": session_id,
        "work_order_id": work_order_id,
        "attribution": "mission" if work_order_id else "unattributed",
        "delta_cost_usd": delta_cost,
        "delta_cost_provenance": delta_provenance,
        "cumulative_session_cost_usd": cumulative_session_cost_usd,
        "cumulative_session_cost_provenance": cumulative_session_cost_provenance,
        "context_used": context_used,
        "session_input_tokens": session_input_tokens,
        "session_output_tokens": session_output_tokens,
        "_fingerprint": list(fingerprint),
    }
    if request_usage:
        event["request_usage"] = request_usage

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return path


def read_events(repo: Path) -> List[Dict[str, Any]]:
    path = ledger_path(repo)
    if not path.is_file():
        return []
    events: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict):
                    events.append(record)
    except OSError:
        return []
    return events


def cumulative_mission_cost(repo: Path) -> Dict[str, float]:
    """Sum of attributed exact/derived deltas per work-order id. Never
    includes unattributed spend — that would be inventing mission
    economics."""
    totals: Dict[str, float] = {}
    for event in read_events(repo):
        work_order_id = event.get("work_order_id")
        delta = event.get("delta_cost_usd")
        if work_order_id and isinstance(delta, (int, float)):
            totals[work_order_id] = totals.get(work_order_id, 0.0) + delta
    return totals


def cost_guzzlers(repo: Path, limit: int = 5) -> List[Dict[str, Any]]:
    """Top missions/requests by exact cost, most expensive first. Each row
    aggregates by work_order_id (or 'unattributed session spend' when
    none), carrying total cost, token totals, and cache-hit% when the
    contributing events had exact per-request usage."""
    groups: Dict[str, Dict[str, Any]] = {}
    for event in read_events(repo):
        key = event.get("work_order_id") or f"unattributed:{event.get('session_id')}"
        label = event.get("work_order_id") or "session (unattributed)"
        group = groups.setdefault(
            key,
            {"label": label, "cost_usd": 0.0, "input_tokens": 0, "cached_input_tokens": 0, "has_exact_usage": False},
        )
        delta = event.get("delta_cost_usd")
        if isinstance(delta, (int, float)):
            group["cost_usd"] += delta
        usage = event.get("request_usage") or {}
        if usage.get("input_tokens") is not None:
            group["input_tokens"] += usage["input_tokens"]
            group["has_exact_usage"] = True
        if usage.get("cached_input_tokens") is not None:
            group["cached_input_tokens"] += usage["cached_input_tokens"]

    rows = list(groups.values())
    for row in rows:
        if row["has_exact_usage"] and row["input_tokens"]:
            row["cache_hit_pct"] = max(0.0, min(100.0, row["cached_input_tokens"] / row["input_tokens"] * 100.0))
        else:
            row["cache_hit_pct"] = None
    rows.sort(key=lambda r: r["cost_usd"], reverse=True)
    return rows[:limit]
