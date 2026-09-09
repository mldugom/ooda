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

## Mission economics aggregation

`ooda.mission_economics` is the one reusable rollup layer behind the cost
surfaces below. It never infers economics from filesystem modification
times, never manufactures a mission's cost when no telemetry covers it
(reports `None`/`UNAVAILABLE`, not `$0`), and never backfills missions
that predate the telemetry ledger.

**Mission lifecycle.** A mission is a work order plus its trace: `created_at`
(work order), `completed_at` (trace), `elapsed_minutes` (derived), result
state, and a verified flag. An open mission (no trace yet) has no
`completed_at`/`elapsed_minutes`.

**Mission spend — the completed-mission attribution fix.** Live attribution
(`telemetry_ledger.record_snapshot`) can only attribute a delta to "the one
work order with no trace yet" *at the moment the snapshot is appended*.
Grok's status-line hook reports a *cumulative* session cost roughly every
~10 minutes (or on session change) rather than per request, so a mission
that is created and traced-complete before the next refresh has its real
spend appended *after* the trace already exists — at that instant zero
work orders are "open", so the live rule alone puts the whole delta in
`session/unattributed`, even though the mission's durable fields fully
describe it. `mission_economics.attribute_events` fixes this
retroactively: once a mission is complete, its window
`[work_order.created_at, trace.completed_at]` is known for good, and every
ledger event whose own `at` timestamp falls inside exactly one mission's
window is attributed to that mission — independent of what "the currently
open work order" looked like at write time. An event inside zero windows
stays unattributed; an event inside more than one (overlapping/concurrent
missions) is left unattributed too — OODA will not guess which of two
concurrent missions paid for it. The result is always `LOCAL_DERIVED`
(never `EXACT_API`, even when every per-event delta that fed it was
itself `EXACT_API`/`PROVIDER_REPORTED`): attribution to a named mission is
always OODA's own inference, never a billed fact.

**Rollups.** `mission_economics.session_spend`, `project_rollup` (today /
7d / 30d / all recorded telemetry / top missions / by-provider), and
`portfolio_rollup` (spend by discovered OODA project + portfolio total)
all reuse the same ledger and lifecycle data, with the same honesty rules.

## Feedback-loop Efficiency

The chart plots one bounded mission per point:

- x-axis = mission spend — an explicit `trace.economics.cost_usd` when one
  was manually recorded, otherwise the ledger's windowed attribution
  above (a manual figure is never required if the ledger can defensibly
  provide the spend);
- y-axis = minutes from explicit work-order `created_at` to trace `completed_at`;
- point state = completed, negative finding, blocked, budget exhausted, or human gate;
- hover/detail includes mission id, provider, spend, minutes, result/gate
  state, and cost provenance.

Lower-left is generally better: cheaper and faster verified feedback. The chart intentionally measures feedback efficiency rather than task volume. It only renders once at least 3 valid points exist; below that it shows a one-line note instead of an empty chart.

OODA does **not** infer missing cost or timestamps from filesystem modification times. Old or incomplete missions remain absent from the chart until real economics/timing are recorded.

## Cost surfaces

The project panel shows a compact **COST** register (Today / 7 days /
Recorded, top mission, dominant provider) from `project_rollup`, and keeps
**COST GUZZLERS** as a ranked table of missions by attributed spend (same
windowed attribution as above, falling back to an in-flight mission's live
attribution when no completed window exists yet). A **SPEND OVER TIME**
chart appears only once there are at least 5 distinct dated telemetry
observations for a meaningful trend — otherwise it is omitted entirely
rather than shown empty. The hero KPI row adds a **Recorded spend** figure
only once at least one project on the page has recorded telemetry.

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
