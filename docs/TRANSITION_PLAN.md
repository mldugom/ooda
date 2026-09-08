# Transition Plan — Manual OODA to a Future Control Plane

The migration rule is: **do not destabilize a working system to prove the future one.**

## Current status

| Phase | Status |
|---|---|
| 0 — Existing workflow preserved | **active / preserved** |
| 1 — OODA shadow/manual mode | **implemented and dogfooded** |
| 2 — Thin provider adapters | **Grok reference flavor implemented; second provider parked/deferred** |
| 3 — Control Room integration | **implemented** |
| 4 — Repository watcher / observation plane | **deferred** |
| 5 — Local deterministic supervisor | **deferred** |
| 6 — Always-on local host | **deferred** |
| 7 — Multi-provider routing | **design documented; implementation deferred** |

Deferred phases are not missing release blockers. They should be commissioned only when real operating evidence makes them the highest-value next OODA product slice.

## Phase 0 — Existing workflow preserved

```text
HUMAN + CHATGPT
      -> bounded provider session
      -> project-local rules
      -> branch/tests/artifacts
      -> handoff/PR
      -> human + ChatGPT integration gate
```

No OODA dependency is required for existing work to continue.

## Phase 1 — OODA shadow/manual mode — implemented

Current OODA supports:

- `.ooda/project.json` adoption;
- `ooda init --scaffold` for a minimal operating spine;
- narrow durable bootstrap for fresh sessions;
- provider-neutral `ooda/work-order/v1` missions;
- `ooda/trace/v1` feedback records;
- `.ooda/project-view.json` for the human objective ladder, material decision timeline, and stakeholder summary;
- project-local lifecycle and authority remaining authoritative.

The dogfooded operating model is one Controller session plus isolated bounded child workers where the provider supports them.

## Phase 2 — Thin provider adapters — Grok reference implemented

Provider details stay under `providers/` while missions/traces remain provider-neutral.

The current Grok flavor supplies:

- `grok-safe` launcher discipline;
- packaged `/ooda-controller` and `/ooda` skills;
- workflow/subagent availability checks;
- bounded one-child-at-a-time execution guidance;
- project-view maintenance/rendering behavior.

A DeepSeek/CodeWhale second-provider experiment was implemented briefly in OODA 0.4 and then parked after dogfooding exposed runner churn, UI/runtime mismatch, telemetry ambiguity, and extra maintenance surface before qualification completed. Its code is retained as dormant experimental material, but Grok is again the sole active reference flavor.

The provider-flavor boundary and qualification plan are documented in `docs/PROVIDER_FLAVORS.md`; the parked DeepSeek lane and re-entry criteria are recorded in `docs/BACKLOG.md`.

A future adapter should validate current state, authority, and stop conditions without copying the whole OODA repo into hidden runtime state.

## Phase 3 — Control Room integration — implemented

The bundled read-only `ooda dashboard` now consumes derived OODA state and shows:

- stakeholder summary and current human/next gate;
- live OODA loop;
- objective ladder and recent material pivots;
- Git/controller/mission freshness;
- optional provider context telemetry;
- project tabs with selected-project persistence.

The Control Room remains read-only with Git/project evidence authoritative. `ooda view` remains the compact canonical shell renderer.

## Phase 4 — Repository watcher / observation plane — deferred

Automate observation before dispatch or judgment.

A future small local process may:

- poll an allowlist of repositories;
- detect default-branch advances, PR changes, selected state-file changes, and new OODA traces/work orders;
- keep last-seen SHAs/cursors in a small local state store;
- update the Control Room and surface candidate human-review/orientation events.

It does **not** automatically create consequential tasks, merge code, promote models, or touch live capital/runtime.

See `docs/REPO_WATCHER.md`.

## Phase 5 — Local deterministic supervisor — deferred

After repeated manual routing patterns are obvious:

- supervisor reads project contract + mission;
- may consume events from the repo watcher;
- dispatches the configured provider for explicitly allowed work;
- enforces budgets and classified stop conditions;
- collects trace + Git/test evidence;
- requests a human gate for consequential actions.

The supervisor is deterministic control logic, not the chief scientist.

## Phase 6 — Always-on local host — deferred

A future small local host may run the watcher/supervisor, schedule allowed work, store operational metadata, and update the Control Room.

```text
GitHub repos
      |
      v
repo watcher
      |
      v
human + ChatGPT / OODA Controller
      |
      v
OODA mission
      |
      v
deterministic supervisor
      |
      +--> configured provider(s)
      +--> local sandbox/tests
      |
      v
OODA trace + Git evidence
      |
      v
human integration gate
```

## Phase 7 — Multi-provider routing — design documented, implementation deferred

Only after provider-neutral contracts are proven and a second provider is actually needed:

- different providers may own architecture/research/implementation according to policy;
- lower-cost providers may handle high-volume bounded work;
- provider selection is a policy decision, not a project rewrite;
- provider qualification should replay frozen read-only project-orientation cases before consequential work is delegated.

The DeepSeek/CodeWhale experiment is the current concrete backlog item for this phase, not active implementation. See `docs/BACKLOG.md` before reopening it.

See `docs/PROVIDER_FLAVORS.md`.

## Explicitly not migrated automatically

Do not automatically import every capability from an existing agent runtime into OODA. Lifecycle implementation, local runtime coupling, issue-polling experiments, dashboards, and provider-specific session state should each re-earn their place against OODA's provider-neutral boundaries.
