from __future__ import annotations

"""Parsing/derivation for xAI-shaped inference `usage` objects.

OODA does not proxy model traffic and does not scrape provider UIs. This
module only interprets a `usage`-shaped mapping if one is actually present
in a payload OODA is handed (today: Grok Build's supported status-line
JSON hook; potentially a future payload). It never fabricates a value.

Ground truth (xAI): `usage.cost_in_usd_ticks` is exact billed cost in
hundred-billionths of a dollar -> USD = ticks / 1e10.

Every derived field carries an explicit provenance so a caller can never
present an estimate as exact:

- EXACT_API      the provider's own billed-usage field, verbatim or a pure
                  unit conversion of it (e.g. ticks -> USD).
- LOCAL_DERIVED  computed locally from two or more EXACT_API readings
                  (e.g. a delta between two cumulative session totals).
- ESTIMATED      a non-authoritative guess (e.g. a runner's own estimate).
- UNAVAILABLE    the source field was not present.
"""

from typing import Any, Dict, Optional

EXACT_API = "EXACT_API"
LOCAL_DERIVED = "LOCAL_DERIVED"
ESTIMATED = "ESTIMATED"
UNAVAILABLE = "UNAVAILABLE"

TICKS_PER_USD = 1e10


def ticks_to_usd(ticks: Any) -> Optional[float]:
    """Exact conversion per xAI ground truth: USD = ticks / 1e10."""
    value = _as_number(ticks)
    if value is None:
        return None
    return value / TICKS_PER_USD


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


def _as_int(value: Any) -> Optional[int]:
    number = _as_number(value)
    return None if number is None else int(number)


def parse_usage(usage: Any) -> Dict[str, Any]:
    """Parse one xAI-shaped `usage` object into per-request metrics.

    Returns a flat dict of `<metric>` / `<metric>_provenance` pairs. A
    metric absent from `usage` is UNAVAILABLE, never zero and never
    inferred. Field names follow xAI's `usage` object; nested
    prompt-token-detail objects (cached tokens) and completion-token-detail
    objects (reasoning tokens) are read defensively since exact key shapes
    can vary by API version.
    """
    if not isinstance(usage, dict):
        usage = {}

    result: Dict[str, Any] = {}

    def put(name: str, value: Any, provenance: str) -> None:
        result[name] = value
        result[f"{name}_provenance"] = provenance

    cost_ticks = usage.get("cost_in_usd_ticks")
    cost_usd = ticks_to_usd(cost_ticks)
    put("cost_usd", cost_usd, EXACT_API if cost_usd is not None else UNAVAILABLE)

    input_tokens = _as_int(
        usage.get("prompt_tokens") if "prompt_tokens" in usage else usage.get("input_tokens")
    )
    put("input_tokens", input_tokens, EXACT_API if input_tokens is not None else UNAVAILABLE)

    prompt_details = usage.get("prompt_tokens_details")
    cached = None
    if isinstance(prompt_details, dict):
        cached = _as_int(prompt_details.get("cached_tokens"))
    if cached is None:
        cached = _as_int(usage.get("cached_tokens") if "cached_tokens" in usage else usage.get("cached_input_tokens"))
    put("cached_input_tokens", cached, EXACT_API if cached is not None else UNAVAILABLE)

    if input_tokens is not None and cached is not None:
        put("uncached_input_tokens", max(0, input_tokens - cached), LOCAL_DERIVED)
    else:
        put("uncached_input_tokens", None, UNAVAILABLE)

    output_tokens = _as_int(
        usage.get("completion_tokens") if "completion_tokens" in usage else usage.get("output_tokens")
    )
    put("output_tokens", output_tokens, EXACT_API if output_tokens is not None else UNAVAILABLE)

    completion_details = usage.get("completion_tokens_details")
    reasoning = None
    if isinstance(completion_details, dict):
        reasoning = _as_int(completion_details.get("reasoning_tokens"))
    if reasoning is None:
        reasoning = _as_int(usage.get("reasoning_tokens"))
    put("reasoning_tokens", reasoning, EXACT_API if reasoning is not None else UNAVAILABLE)

    total_tokens = _as_int(usage.get("total_tokens"))
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
        put("total_tokens", total_tokens, LOCAL_DERIVED)
    else:
        put("total_tokens", total_tokens, EXACT_API if total_tokens is not None else UNAVAILABLE)

    tools = _as_int(usage.get("num_server_side_tools_used"))
    put("server_tool_count", tools, EXACT_API if tools is not None else UNAVAILABLE)

    service_tier = usage.get("service_tier")
    put("service_tier", str(service_tier) if service_tier else None, EXACT_API if service_tier else UNAVAILABLE)

    if input_tokens and cached is not None:
        put("cache_hit_pct", max(0.0, min(100.0, cached / input_tokens * 100.0)), LOCAL_DERIVED)
    else:
        put("cache_hit_pct", None, UNAVAILABLE)

    return result


def is_present(usage: Any) -> bool:
    return isinstance(usage, dict) and bool(usage)
