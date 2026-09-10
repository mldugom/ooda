# OODA minimalization audit

This branch is intentionally removing framework machinery that does not directly improve prediction work or prevent a measured failure.

## Keep

- fact-scoped truth and typed blockers
- execution-locality routing
- project-native integrity checks
- Grok launcher and a small session snapshot (model, context, session id/cost when provider-reported)
- concise prediction-science references loaded on demand
- read-only stakeholder dashboard
- compatibility reading of existing project/work-order/trace artifacts while repositories migrate

## Collapse

- dashboard presentation into one stakeholder surface
- provider telemetry into one Grok-only session snapshot
- normal user workflow toward `next`, `run`, `continue`, `check`, `dashboard`

## Delete from the active product

- parked DeepSeek/CodeWhale runtime and TUI
- mission-cost attribution, telemetry ledger, cost-guzzler and feedback-efficiency machinery
- layered dashboard stack (`control_room` + `domain_control_room`)

The cost-attribution subsystem is removed rather than repaired because the provider telemetry is interval/coarse and cannot defensibly assign spend to short or overlapping missions. Session-level provider-reported cost can remain useful without pretending OODA knows per-mission billing.

The dashboard should describe the business/modeling decision in normal data-science language. Framework identifiers belong under technical details, not in the primary reading path.
