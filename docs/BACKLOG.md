# OODA Backlog

Backlog items are explicitly **not current work**. They are preserved so a useful experiment can be revisited without letting it compete with a working reference path.

## Grok account usage / spend telemetry

Status: **cost/context observability implemented (session + optional per-request); account-level balance still an open gap**.

The Grok status-line adapter records provider-supplied context occupancy and, when Grok supplies it, provider-metered `cost.total_cost_usd` into `.ooda/session-telemetry.json`. It additionally accepts an optional xAI-shaped `usage` object (`src/ooda/xai_usage.py`) — `cost_in_usd_ticks` (exact, `USD = ticks / 1e10`), cached/uncached input split, reasoning tokens, server-side tool count, service tier — parsed only when actually present in the payload, never fabricated. Every derived field carries explicit provenance (`EXACT_API` / `LOCAL_DERIVED` / `ESTIMATED` / `UNAVAILABLE`).

Each status-line snapshot is turned into a delta event in a small local append-only ledger (`.ooda/telemetry/events.jsonl`, `src/ooda/telemetry_ledger.py`) rather than recorded verbatim, since Grok's payload reports *cumulative* session totals, not one event per request; duplicate snapshots are a no-op. A delta is attributed to a work order only when exactly one work order in the repo has no trace yet (unambiguous open mission) — otherwise it is recorded `unattributed`. This is intentionally conservative: OODA does not invent mission economics.

The Control Room's telemetry register (built on Control Room V2) shows a compact MODEL / EFFORT / CONTEXT % / SESSION COST / CURRENT MISSION ATTRIBUTED SPEND / CACHE HIT % summary with a progressive-disclosure drill-down for input/cached/output/reasoning/tool/service-tier detail, and a text-first COST GUZZLERS ranking of missions by attributed spend, each row carrying an explicit SOURCE provenance. Both are absent (not empty panels) until real data exists.

**Mission-spend provenance is categorical, not a function of per-request precision.** Session-cumulative provider cost can be exact/provider-metered (`EXACT_API`) — Grok's own meter genuinely reports that number. But attribution of any part of that spend to a *named mission* is always OODA's own inference: the delta between two cumulative snapshots, assigned to whichever work order is the sole unambiguous open one at that moment. That inference is `LOCAL_DERIVED` even when the underlying per-request `usage.cost_in_usd_ticks` was itself exact — xAI never bills a named OODA mission. The UI therefore never labels a mission ranking "exact-cost missions"; it is "COST GUZZLERS" / "attributed spend" with an explicit `LOCAL_DERIVED` tag on every row (`telemetry_ledger.ATTRIBUTED_SPEND_PROVENANCE`).

**Effort visibility.** Grok's supported status-line payload already includes `effort.level` for the session that invoked the hook — this is the **parent/Controller session's** effort, and OODA now surfaces it (`effort` / `effort_provenance` in `.ooda/session-telemetry.json`, rendered as the EFFORT field in the Control Room summary). **Child/worker effort is a separate, currently unanswerable question**: "Grok owns its native TUI chrome and Workflow/subagent panel" (see `AGENT_OPS_MONITOR.md`, `CURRENT_BASELINE.md`) and there is no supported hook that fires for an individual subagent/child session — OODA does not scrape or patch that provider-owned chrome to get one. `worker_effort` is therefore always recorded and rendered as `UNAVAILABLE`, never assumed to equal the parent's effort (no runtime documentation establishes that children inherit it).

**Child-agent spend visibility**, per `ZERO_TO_GROK.md`'s two supported delegation modes:
- **Inline child execution** (the Controller dispatches a bounded work order inside the same Controller session): the child runs inside the same Grok process/session, so its token/cost usage is folded into that session's single cumulative `cost.total_cost_usd` meter. It is **not separately observable** through the status-line hook — OODA cannot and does not attempt to split a session's cumulative cost between "Controller" and "inline child" activity.
- **Standalone worker session** (a separate `grok-safe` launch, `/start` + `/ooda <work-order>`): this is a distinct Grok process with its own session_id and its own status-line hook invocations, so it writes its **own independent session-cumulative telemetry** (to whichever repo's `.ooda/` it is running in) — it is observable, but as a second, separate session total, not as a component of the parent's.

Still open:

- as of this implementation, Grok Build's supported status-line hook does **not** appear to pass through a raw per-request `usage` object in practice — today's real telemetry is session-cumulative only (context %, `cost.total_cost_usd`), so the per-request fields above render `UNAVAILABLE` until/unless Grok's payload includes one. The parser is forward-compatible and fully tested against synthetic payloads shaped like xAI's raw API `usage` object;
- if xAI exposes a **supported Grok/Build account-usage endpoint**, add weekly usage-pool percentage/reset and Extra Usage Credits balance with explicit provenance;
- keep missing values unknown rather than estimating them;
- do not scrape Grok web/app pages or private endpoints;
- do not confuse the xAI **Management API** billing endpoints with Grok app/Build usage. Management API `/v1/billing/teams/{team_id}/usage` and prepaid-balance endpoints cover xAI API-team billing; Grok's shared weekly pool / Extra Usage Credits are a different product surface unless xAI documents a supported bridge.

Until a supported Grok/Build account endpoint exists, the authoritative account-level weekly usage / Extra Usage balance remains the Grok Settings → Usage surface. OODA may show provider-reported per-session context/cost, but must not label API-team billing as Grok Build spend.

## DeepSeek second-provider flavor — parked

Status: **parked / unqualified**.

The September 2026 DeepSeek/CodeWhale experiment proved that the provider-neutral OODA boundary is plausible, but the runner integration introduced too much instability for the current operating loop: the DeepSeek-TUI package was renamed/deprecated during setup, the CodeWhale runtime/UI surface diverged from the desired OODA operator experience, authoritative context/cost telemetry was incomplete in the stdio path, and the Tenniskal/Crypto qualification sequence was not completed.

Current decision: use **Grok via `grok-safe` as the sole active reference flavor**. Keep the DeepSeek implementation code in the repository as dormant experimental material, but do not expose or qualify it as a normal operator path.

Revisit only when the second-provider lane is again the highest-value constraint and all of these are true:

- a stable supported DeepSeek-capable runner/runtime interface exists;
- OODA can present one consistent operator surface without depending on the provider's native TUI;
- `/ooda-controller` and `/ooda` semantics are first-class in that surface;
- context, token, session-cost, and account-balance telemetry have explicit provenance and missing values remain unknown;
- bounded isolated child delegation can select the intended worker model without changing authority;
- frozen read-only Tenniskal and Crypto-Innout orientation cases pass before consequential work is allowed;
- the provider lane remains thinner than rebuilding a general-purpose agent runtime inside OODA.

Until then, provider expansion remains a backlog item under the transition plan's deferred multi-provider work.
