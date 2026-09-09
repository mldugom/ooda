# OODA Backlog

Backlog items are explicitly **not current work**. They are preserved so a useful experiment can be revisited without letting it compete with a working reference path.

## Grok account usage / spend telemetry

Status: **open telemetry gap; session telemetry already supported**.

The current Grok status-line adapter already records provider-supplied context occupancy and, when Grok supplies it, provider-metered `cost.total_cost_usd` into `.ooda/session-telemetry.json`; the Control Room renders context percentage/tokens and session cost without inventing values.

Desired follow-on:

- make context usage and session spend visually explicit in the Control Room;
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
