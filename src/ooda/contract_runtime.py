from __future__ import annotations

import datetime as dt
import sys
from typing import Any, Dict, Optional


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def enrich_contract(data: Dict[str, Any], *, trace_cost_usd: Optional[float] = None) -> Dict[str, Any]:
    enriched = dict(data)
    schema = enriched.get("schema")
    if schema == "ooda/work-order/v1" and not enriched.get("created_at"):
        enriched["created_at"] = _now_iso()
    if schema == "ooda/trace/v1":
        if not enriched.get("completed_at"):
            enriched["completed_at"] = _now_iso()
        if trace_cost_usd is not None:
            economics = dict(enriched.get("economics") or {})
            economics["cost_usd"] = float(trace_cost_usd)
            enriched["economics"] = economics
    return enriched


def _extract_trace_cost(argv: list[str]) -> Optional[float]:
    if "--cost-usd" not in argv:
        return None
    idx = argv.index("--cost-usd")
    if idx + 1 >= len(argv):
        raise ValueError("--cost-usd requires a numeric value")
    try:
        value = float(argv[idx + 1])
    except ValueError as exc:
        raise ValueError("--cost-usd requires a numeric value") from exc
    if value < 0:
        raise ValueError("--cost-usd must be >= 0")
    del argv[idx : idx + 2]
    return value


def run_cli() -> None:
    """Run the existing CLI while enriching durable contracts at the write boundary.

    This keeps the public work-order/trace schema backward compatible while ensuring
    new CLI-created missions have exact creation/completion timestamps. Trace cost is
    optional and is recorded only when the caller explicitly supplies --cost-usd.
    """
    from . import cli

    try:
        trace_cost = _extract_trace_cost(sys.argv) if len(sys.argv) > 1 and sys.argv[1] == "trace" else None
    except ValueError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(2)

    original_dump = cli.dump

    def timestamped_dump(path, data):
        original_dump(path, enrich_contract(data, trace_cost_usd=trace_cost))

    cli.dump = timestamped_dump
    cli.main()
