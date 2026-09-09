from __future__ import annotations

"""Mission economics aggregation — turns the telemetry ledger plus mission
lifecycle files (work orders, traces) into honest, provenance-tagged
answers to "what did this cost", at mission / session / project /
portfolio scope.

## Root cause of the dogfood failure

A real Tenniskal mission had a work order and a TRACE, yet Cost Guzzlers
showed its spend under `session/unattributed`. The cause is that
`telemetry_ledger.record_snapshot` can only attribute a delta to "the one
work order with no trace yet" *at the moment the snapshot is appended*.
Grok Build's supported status-line hook reports a *cumulative* session
cost roughly every ~10 minutes (or on session change), not one event per
request (see `telemetry_ledger` module docstring). If a mission is
created and its TRACE is written before the next status-line refresh —
entirely plausible for a short, well-scoped mission — every ledger event
carrying that mission's real spend is appended *after* the work order
already has a trace. At that instant `_current_open_work_order_id` sees
zero open work orders, so the whole delta lands in `session/unattributed`
even though the mission is fully described by durable fields. This gets
systematically worse for short/cheap missions — exactly the missions a
Feedback-loop Efficiency chart most wants a point for.

## The fix: attribute by delta INTERVAL, not by point timestamp

A first cut at this fix compared each ledger event's own `at` timestamp
to a completed mission's [created_at, completed_at] window. That still
misses the common case where Grok's refresh cadence is coarser than the
mission itself:

    06:00  cumulative snapshot = $1.00
    06:02  mission starts
    06:07  mission completes
    06:10  cumulative snapshot = $1.45   <- delta $0.45 recorded here

The $0.45 delta represents spend accrued over [06:00, 06:10] — the
interval since the *previous* snapshot for that session — not spend that
happened at the instant 06:10. A point-timestamp rule sees `at=06:10`,
which is after `completed_at=06:07`, and leaves the mission unattributed.

Every ledger event's real claim is therefore an INTERVAL, not a point:
`interval_start` = the previous recorded snapshot's `at` for the same
`session_id` (None if this is that session's first recorded snapshot —
the interval before it is unknown), `interval_end` = this event's own
`at`. A delta is attributed to a mission only when the mission's window
overlaps that interval, and only when exactly one mission's window does
— multiple missions overlapping the same coarse interval (two sequential
missions inside one refresh window, or two genuinely concurrent ones)
leaves it unattributed, because OODA cannot tell which mission the spend
actually belongs to. `interval_start = None` (the session's first
recorded snapshot) is unattributed unconditionally, even if it lands
inside a mission's window — that cumulative reading may include spend
that predates the mission entirely, and there is no prior boundary to
prove otherwise.

This is still an interval attribution, not a request-level one: OODA
does not proportionally split a delta by wall-clock duration and does
not assume uniform spend across the interval. If unrelated activity
happened in the same coarse interval as a mission, that activity's
cost is indistinguishable from the mission's own and is included in
whatever the interval attributes to — a real limitation of coarse
provider telemetry, not something this module can see past. Mission
spend from this module is therefore useful for OODA's own
feedback-efficiency measurement, but it is not request-level billing.

The result is always LOCAL_DERIVED
(`telemetry_ledger.ATTRIBUTED_SPEND_PROVENANCE`): attribution to a named
mission is always OODA's own inference, never a fact a provider billed
against a mission, regardless of how exact the per-event deltas that fed
into it were. A grouping over individually EXACT_API/PROVIDER_REPORTED
values never becomes EXACT_API itself.

## What this module does not do

- It does not infer mission economics from filesystem mtimes.
- It does not manufacture costs for missions with no ledger events whose
  interval overlaps their window — those report `attributed_spend_usd =
  None`, `spend_provenance = UNAVAILABLE`, not zero.
- It does not backfill missions that predate the telemetry ledger.
- It does not proportionally split a coarse delta across the wall-clock
  duration of the interval, and does not assume uniform spend within it.
- If Grok's refresh cadence means a mission's true boundary cost reading
  is imprecise, that imprecision is inherited honestly (still
  LOCAL_DERIVED, never upgraded to a stronger claim) rather than hidden.
"""

import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .telemetry_ledger import ATTRIBUTED_SPEND_PROVENANCE, read_events
from .xai_usage import LOCAL_DERIVED, UNAVAILABLE

__all__ = [
    "mission_lifecycle",
    "attribute_events",
    "mission_economics_report",
    "cost_guzzlers",
    "session_spend",
    "project_rollup",
    "portfolio_rollup",
    "daily_spend_series",
    "MIN_SPEND_TREND_DAYS",
]

MIN_SPEND_TREND_DAYS = 5


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def parse_time(value: Any) -> Optional[dt.datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def _work_orders(repo: Path) -> Dict[str, Dict[str, Any]]:
    work_orders_dir = repo / ".ooda" / "work-orders"
    out: Dict[str, Dict[str, Any]] = {}
    if not work_orders_dir.is_dir():
        return out
    for path in sorted(work_orders_dir.glob("*.json")):
        data = _read_json(path)
        work_id = str(data.get("id") or path.stem)
        out[work_id] = data
    return out


def _traces_by_work_order(repo: Path) -> Dict[str, Dict[str, Any]]:
    traces_dir = repo / ".ooda" / "traces"
    out: Dict[str, Dict[str, Any]] = {}
    if not traces_dir.is_dir():
        return out
    for path in sorted(traces_dir.glob("*.json")):
        trace = _read_json(path)
        work_id = str(trace.get("work_order_id") or "")
        if work_id:
            out[work_id] = trace
    return out


def mission_lifecycle(repo: Path) -> List[Dict[str, Any]]:
    """One record per work order, whether or not it has a trace yet.

    A completed mission (has both a created_at and a completed_at, with
    completed strictly after created) carries `elapsed_minutes`; an open
    mission carries `elapsed_minutes = None`. Fields prefixed with `_`
    are internal parsed datetimes for window arithmetic and are stripped
    by `mission_economics_report`."""
    work_orders = _work_orders(repo)
    traces = _traces_by_work_order(repo)

    missions: List[Dict[str, Any]] = []
    for work_id, work in work_orders.items():
        created = parse_time(work.get("created_at"))
        trace = traces.get(work_id)
        completed_raw = trace.get("completed_at") if trace else None
        completed = parse_time(completed_raw)
        result = trace.get("result") if trace and isinstance(trace.get("result"), dict) else {}
        economics = trace.get("economics") if trace and isinstance(trace.get("economics"), dict) else {}
        elapsed: Optional[float] = None
        if created and completed and completed > created:
            elapsed = (completed - created).total_seconds() / 60.0

        result_state = result.get("state") if trace else None
        verified = bool(trace) and result_state not in (None, "blocked", "budget_exhausted")

        manual_cost = economics.get("cost_usd")
        missions.append(
            {
                "mission_id": work_id,
                "created_at": work.get("created_at"),
                "completed_at": completed_raw,
                "elapsed_minutes": elapsed,
                "result_state": result_state,
                "verified": verified if trace else False,
                "provider": str(trace.get("provider")) if trace and trace.get("provider") else None,
                "manual_cost_usd": float(manual_cost) if isinstance(manual_cost, (int, float)) else None,
                "manual_cost_provenance": str(economics.get("cost_usd_provenance") or LOCAL_DERIVED)
                if isinstance(manual_cost, (int, float))
                else None,
                "_created_dt": created,
                "_completed_dt": completed,
            }
        )
    return missions


def _completed_windows(missions: List[Dict[str, Any]]) -> List[tuple]:
    return [
        (m["mission_id"], m["_created_dt"], m["_completed_dt"])
        for m in missions
        if m["_created_dt"] is not None and m["_completed_dt"] is not None and m["_completed_dt"] > m["_created_dt"]
    ]


def _session_intervals(repo: Path) -> List[Dict[str, Any]]:
    """One record per ledger event carrying the delta's real time claim: the
    interval since the previous recorded snapshot for the same session, not
    the event's own point timestamp (see module docstring). `interval_start`
    is None for a session's first recorded snapshot — the interval before it
    is genuinely unknown, not "zero-length"."""
    last_at_by_session: Dict[str, dt.datetime] = {}
    intervals: List[Dict[str, Any]] = []
    for event in read_events(repo):
        session_id = str(event.get("session_id") or "unknown-session")
        at = parse_time(event.get("at"))
        intervals.append(
            {
                "session_id": session_id,
                "interval_start": last_at_by_session.get(session_id),
                "interval_end": at,
                "event": event,
            }
        )
        if at is not None:
            last_at_by_session[session_id] = at
    return intervals


def _overlapping_missions(windows: List[tuple], start: Optional[dt.datetime], end: Optional[dt.datetime]) -> List[str]:
    """Missions whose [created_at, completed_at] window overlaps the delta
    interval [start, end]. `start=None` (session's first recorded snapshot)
    never overlaps anything — see module docstring on why that interval is
    conservatively unknown rather than attributable."""
    if start is None or end is None:
        return []
    return [mid for mid, m_start, m_end in windows if m_start <= end and m_end >= start]


def attribute_events(repo: Path, missions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
    """Retroactively attribute ledger deltas to completed missions by
    overlap between the delta's INTERVAL (previous snapshot -> this one,
    for the same session) and a mission's [created_at, completed_at]
    window — see module docstring. Returns a dict keyed by mission_id,
    plus a `"__unattributed__"` bucket for deltas whose interval matches
    zero or (ambiguously) more than one mission window, or whose interval
    start is unknown (a session's first recorded snapshot)."""
    if missions is None:
        missions = mission_lifecycle(repo)
    windows = _completed_windows(missions)

    totals: Dict[str, Dict[str, Any]] = {}
    unattributed_spend = 0.0
    unattributed_by_session: Dict[str, float] = {}

    for item in _session_intervals(repo):
        event = item["event"]
        delta = event.get("delta_cost_usd")
        if not isinstance(delta, (int, float)):
            continue
        matches = _overlapping_missions(windows, item["interval_start"], item["interval_end"])
        if len(matches) == 1:
            mid = matches[0]
            bucket = totals.setdefault(
                mid,
                {
                    "spend_usd": 0.0,
                    "event_count": 0,
                    "session_ids": set(),
                    "providers": set(),
                    "models": set(),
                    "cumulative_readings": [],
                },
            )
            bucket["spend_usd"] += delta
            bucket["event_count"] += 1
            if event.get("session_id"):
                bucket["session_ids"].add(event["session_id"])
            if event.get("provider"):
                bucket["providers"].add(event["provider"])
            if event.get("model"):
                bucket["models"].add(event["model"])
            cum = event.get("cumulative_session_cost_usd")
            if isinstance(cum, (int, float)):
                bucket["cumulative_readings"].append(cum)
        else:
            unattributed_by_session[item["session_id"]] = unattributed_by_session.get(item["session_id"], 0.0) + delta
            unattributed_spend += delta

    results: Dict[str, Dict[str, Any]] = {}
    for mid, bucket in totals.items():
        readings = bucket["cumulative_readings"]
        results[mid] = {
            "attributed_spend_usd": bucket["spend_usd"],
            "spend_provenance": ATTRIBUTED_SPEND_PROVENANCE,
            "event_count": bucket["event_count"],
            "session_id": next(iter(bucket["session_ids"])) if len(bucket["session_ids"]) == 1 else None,
            "provider": next(iter(bucket["providers"])) if len(bucket["providers"]) == 1 else None,
            "model": next(iter(bucket["models"])) if len(bucket["models"]) == 1 else None,
            "start_cumulative_session_cost_usd": readings[0] if readings else None,
            "end_cumulative_session_cost_usd": readings[-1] if readings else None,
        }
    results["__unattributed__"] = {"spend_usd": unattributed_spend, "by_session": unattributed_by_session}
    return results


def mission_economics_report(repo: Path) -> List[Dict[str, Any]]:
    """Full per-mission economics: lifecycle + attributed spend.

    Spend prefers an explicit `trace.economics.cost_usd` (a manually
    recorded figure) when present, and falls back to the ledger's
    windowed attribution otherwise — per MISSION, "do not require
    economics.cost_usd to have been manually copied into TRACE if the
    telemetry ledger can defensibly provide the mission spend." A
    completed mission with no ledger events in its window and no manual
    figure reports `attributed_spend_usd = None`, `spend_provenance =
    UNAVAILABLE` — never a manufactured zero."""
    missions = mission_lifecycle(repo)
    attributed = attribute_events(repo, missions)

    out: List[Dict[str, Any]] = []
    for m in missions:
        record = {k: v for k, v in m.items() if not k.startswith("_")}
        econ = attributed.get(m["mission_id"])
        if m["manual_cost_usd"] is not None:
            record["attributed_spend_usd"] = m["manual_cost_usd"]
            record["spend_provenance"] = m["manual_cost_provenance"]
            record["session_id"] = econ["session_id"] if econ else None
            record["start_cumulative_session_cost_usd"] = econ["start_cumulative_session_cost_usd"] if econ else None
            record["end_cumulative_session_cost_usd"] = econ["end_cumulative_session_cost_usd"] if econ else None
        elif econ is not None:
            record["attributed_spend_usd"] = econ["attributed_spend_usd"]
            record["spend_provenance"] = econ["spend_provenance"]
            record["session_id"] = econ["session_id"]
            record["provider"] = m["provider"] or econ["provider"]
            record["start_cumulative_session_cost_usd"] = econ["start_cumulative_session_cost_usd"]
            record["end_cumulative_session_cost_usd"] = econ["end_cumulative_session_cost_usd"]
        else:
            record["attributed_spend_usd"] = None
            record["spend_provenance"] = UNAVAILABLE
            record["session_id"] = None
            record["start_cumulative_session_cost_usd"] = None
            record["end_cumulative_session_cost_usd"] = None
        out.append(record)
    return out


def cost_guzzlers(repo: Path, limit: int = 5) -> List[Dict[str, Any]]:
    """Top missions/buckets by attributed spend.

    Prefers interval-based lifecycle attribution (a completed mission's
    [created_at, completed_at] window overlapping the delta's own
    [previous snapshot, this snapshot] interval — see module docstring)
    over the live per-event `work_order_id` written at snapshot time —
    this is what recovers a completed-fast mission's spend out of
    `session/unattributed` even when the mission's TRACE existed before
    the next status-line refresh.

    Falls back to the event's own live `work_order_id` only when the
    delta's interval matches zero mission windows (typically: an
    in-flight mission with no trace yet, so no window can be built) — an
    in-flight mission still gets its live real-time attribution, exactly
    as before this module existed. A delta whose interval is ambiguous
    (matches more than one window) is never rescued by the live fallback
    — ambiguity always wins over a guess."""
    missions = mission_lifecycle(repo)
    windows = _completed_windows(missions)

    groups: Dict[str, Dict[str, Any]] = {}
    for item in _session_intervals(repo):
        event = item["event"]
        matches = _overlapping_missions(windows, item["interval_start"], item["interval_end"])
        if len(matches) == 1:
            key = matches[0]
            label = matches[0]
        elif not matches and event.get("work_order_id"):
            key = str(event["work_order_id"])
            label = key
        else:
            key = f"unattributed:{event.get('session_id')}"
            label = "session/unattributed"
        group = groups.setdefault(
            key,
            {"label": label, "spend_usd": 0.0, "input_tokens": 0, "cached_input_tokens": 0, "has_exact_usage": False},
        )
        delta = event.get("delta_cost_usd")
        if isinstance(delta, (int, float)):
            group["spend_usd"] += delta
        usage = event.get("request_usage") or {}
        if usage.get("input_tokens") is not None:
            group["input_tokens"] += usage["input_tokens"]
            group["has_exact_usage"] = True
        if usage.get("cached_input_tokens") is not None:
            group["cached_input_tokens"] += usage["cached_input_tokens"]

    rows = list(groups.values())
    for row in rows:
        row["provenance"] = ATTRIBUTED_SPEND_PROVENANCE
        if row["has_exact_usage"] and row["input_tokens"]:
            row["cache_hit_pct"] = max(0.0, min(100.0, row["cached_input_tokens"] / row["input_tokens"] * 100.0))
        else:
            row["cache_hit_pct"] = None
    rows.sort(key=lambda r: r["spend_usd"], reverse=True)
    return rows[:limit]


def session_spend(repo: Path) -> Dict[str, Any]:
    """Current/cumulative spend for the most recently recorded session."""
    events = read_events(repo)
    if not events:
        return {"session_id": None, "cumulative_session_cost_usd": None, "provenance": UNAVAILABLE}
    last = events[-1]
    cost = last.get("cumulative_session_cost_usd")
    return {
        "session_id": last.get("session_id"),
        "cumulative_session_cost_usd": cost if isinstance(cost, (int, float)) else None,
        "provenance": str(last.get("cumulative_session_cost_provenance") or UNAVAILABLE)
        if isinstance(cost, (int, float))
        else UNAVAILABLE,
    }


def daily_spend_series(repo: Path) -> List[Dict[str, Any]]:
    """Ledger spend grouped by UTC calendar date, sorted ascending —
    the input to a spend-over-time trend. Never backfills days with no
    events; only dates that actually have recorded telemetry appear."""
    by_day: Dict[str, float] = {}
    for event in read_events(repo):
        at = parse_time(event.get("at"))
        delta = event.get("delta_cost_usd")
        if at is None or not isinstance(delta, (int, float)):
            continue
        day = at.date().isoformat()
        by_day[day] = by_day.get(day, 0.0) + delta
    return [{"date": day, "spend_usd": spend} for day, spend in sorted(by_day.items())]


def _window_sum(events: List[Dict[str, Any]], *, since: Optional[dt.datetime]) -> float:
    total = 0.0
    for event in events:
        at = parse_time(event.get("at"))
        delta = event.get("delta_cost_usd")
        if at is None or not isinstance(delta, (int, float)):
            continue
        if since is not None and at < since:
            continue
        total += delta
    return total


def project_rollup(repo: Path, *, now: Optional[dt.datetime] = None, top_n: int = 5) -> Dict[str, Any]:
    """TODAY / 7d / 30d / all-recorded-telemetry spend for one project,
    plus its top missions by attributed spend and a by-provider
    breakdown (only populated when the ledger actually names a
    provider)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    events = read_events(repo)
    has_data = any(isinstance(e.get("delta_cost_usd"), (int, float)) for e in events)

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_total = _window_sum(events, since=today_start)
    d7_total = _window_sum(events, since=now - dt.timedelta(days=7))
    d30_total = _window_sum(events, since=now - dt.timedelta(days=30))
    all_total = _window_sum(events, since=None)

    by_provider: Dict[str, float] = {}
    for event in events:
        provider = event.get("provider")
        delta = event.get("delta_cost_usd")
        if provider and isinstance(delta, (int, float)):
            by_provider[str(provider)] = by_provider.get(str(provider), 0.0) + delta

    missions = mission_economics_report(repo)
    completed = [
        m
        for m in missions
        if m.get("completed_at") and isinstance(m.get("attributed_spend_usd"), (int, float))
    ]
    top_missions = sorted(completed, key=lambda m: m["attributed_spend_usd"], reverse=True)[:top_n]

    return {
        "today_usd": today_total,
        "last_7d_usd": d7_total,
        "last_30d_usd": d30_total,
        "all_time_usd": all_total,
        "provenance": LOCAL_DERIVED if has_data else UNAVAILABLE,
        "has_data": has_data,
        "top_missions": top_missions,
        "by_provider": by_provider,
    }


def portfolio_rollup(root: Path, *, now: Optional[dt.datetime] = None) -> Dict[str, Any]:
    """Spend by discovered OODA project under `root`, plus the total
    across all of them. Only counts projects that actually have recorded
    telemetry; a project with no ledger contributes 0 and is flagged
    `has_data: False` rather than silently omitted."""
    from .dashboard import discover_projects

    projects = discover_projects(root)
    rows: List[Dict[str, Any]] = []
    total = 0.0
    any_data = False
    for project in projects:
        repo = project.get("repo")
        if not isinstance(repo, Path):
            continue
        roll = project_rollup(repo, now=now)
        rows.append(
            {
                "project_id": project.get("project_id") or repo.name,
                "all_time_usd": roll["all_time_usd"],
                "has_data": roll["has_data"],
            }
        )
        if roll["has_data"]:
            total += roll["all_time_usd"]
            any_data = True

    rows.sort(key=lambda r: r["all_time_usd"], reverse=True)
    return {
        "projects": rows,
        "total_usd": total,
        "provenance": LOCAL_DERIVED if any_data else UNAVAILABLE,
        "has_data": any_data,
    }
