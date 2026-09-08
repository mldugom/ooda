# Live Control Room

`ooda dashboard` is a local read-only companion UI over durable OODA project state. It does not replace `ooda view`; the terminal renderer remains the compact canonical human view.

## What the Control Room shows

For every adopted repo with `.ooda/project.json`, the Control Room renders:

- a left project sidebar instead of horizontal tabs;
- current stakeholder summary and human/next gate;
- provider/model/context/session-cost/account-balance telemetry when a provider adapter can supply it;
- a compact `OBSERVE -> ORIENT -> DECIDE -> ACT -> VERIFY` rail with the current phase emphasized;
- a compact `NOW | WAITING ON / GATE | NEXT IF CURRENT GATE PASSES` attention strip;
- the full objective ladder (`completed`, exactly one `current`, downstream `provisional`);
- the latest material decision pivots displayed as `TIME | DECISION | IMMEDIATE CONSEQUENCE | PROGRAM IMPACT`;
- a Feedback-loop Efficiency chart when exact mission cost and start/completion timestamps exist;
- Git/controller/mission freshness metadata.

The selected project is remembered across the 15-second auto-refresh when browser local storage is available. Each sidebar row can show provider, model, context percentage, session cost, and account balance without opening the project panel.

The Control Room follows OODA's default editorial/FiveThirtyEight-inspired visual language: warm cream page, off-white surfaces, serif display headings, restrained blue emphasis, thin warm rules, and evidence-first tables. See [`STYLE_GUIDE.md`](STYLE_GUIDE.md).

The default browser refresh is 15 seconds. Override it with `OODA_DASHBOARD_REFRESH_SECONDS`.

The default local HTTP port is **8792**. Override it with `OODA_DASHBOARD_PORT`. If the preferred port is occupied by a foreign service, OODA selects the next free local port rather than reusing the wrong UI.

## Compact OODA rail

The Control Room no longer gives each OODA phase a large content tile. The phase rail is intentionally small: it answers which phase the project is currently in without consuming dashboard space.

The attention strip carries the more useful operational information:

- **NOW** — the current objective / current ladder rung;
- **WAITING ON / GATE** — the actual blocker or human gate;
- **NEXT IF CURRENT GATE PASSES** — the first downstream provisional rung, clearly conditional rather than authorized.

## Material decision timeline

The durable JSON schema remains `at | decision | so_what | bigger_idea`. Human-facing labels are now clearer:

- `decision` -> **DECISION**;
- `so_what` -> **IMMEDIATE CONSEQUENCE**;
- `bigger_idea` -> **PROGRAM IMPACT**.

Timeline rows should read like a data scientist briefing a CTO: plain language, but specific. Name the dataset, model, experiment, gate, feature family, system, decisive number/constraint, and authorization boundary when they materially drove the decision. Do not simplify away a fact that changes what the project may do next.

## Feedback-loop Efficiency

The chart plots one bounded mission per point:

- x-axis = recorded mission cost;
- y-axis = minutes from explicit work-order `created_at` to trace `completed_at`;
- point state = completed, negative finding, blocked, budget exhausted, or human gate.

Lower-left is generally better: cheaper and faster verified feedback. The chart intentionally measures feedback efficiency rather than task volume.

OODA does **not** infer missing cost or timestamps from filesystem modification times. Old or incomplete missions remain absent from the chart until exact economics/timing are recorded.

## Provider telemetry

Provider adapters may write:

```text
.ooda/session-telemetry.json
```

using the provider-neutral `ooda/session-telemetry/v1` contract. Useful fields include provider, model, effort, context used/limit/percentage, session token counts, session cost, account balance, source, and update time. Missing values remain unknown rather than becoming zero.

### Grok

The Grok command status-line adapter writes telemetry from Grok's native structured status payload on normal status-line updates. Session cost comes from Grok's provider meter. The Grok Build account-level Extra Usage balance is not exposed through that payload, so OODA does not scrape the Grok UI to fabricate it.

The Grok TUI surface needs **no port**; Grok invokes the command status line on session changes plus its timed refresh. See [`GROK_TUI.md`](GROK_TUI.md).

### DeepSeek

The experimental DeepSeek flavor uses a non-fatal DeepSeek-TUI `turn_end` hook to write model/context/token telemetry. If the runner supplies a session-cost value, OODA displays it as an estimate (`~$`). If `DEEPSEEK_API_KEY` is available to OODA, the adapter may query DeepSeek's account balance endpoint no more than once every ten minutes and display that separately as actual balance.

The hook opens no port. Balance checks are outbound HTTPS only. See [`DEEPSEEK.md`](DEEPSEEK.md).

## Authority

The dashboard is derived observation state. `PROJECT_STATE.md`, work orders, traces, domain research artifacts, Git/tests, and explicit human gates remain authoritative. `.ooda/project-view.json` is durable human orientation, not permission to start downstream work.
