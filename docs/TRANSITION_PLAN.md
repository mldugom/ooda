# Transition Plan — Manual OODA to a Future Control Plane

The migration rule is: **do not destabilize a working system to prove the future one.**

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

## Phase 1 — OODA shadow/manual mode

Add OODA beside the current system:

- existing projects may add `.ooda/project.json`;
- new repos may use `ooda init --scaffold` for a minimal operating spine;
- fresh ChatGPT sessions bootstrap from narrow durable repo truth instead of giant handoffs;
- substantial new work gets an `ooda/work-order/v1` mission;
- the configured provider executes it;
- useful outcomes get an `ooda/trace/v1` record;
- project-local lifecycle behavior remains authoritative.

Success criteria:

- less scope drift;
- less repeated research;
- faster fresh-chat/project bootstrap;
- better distinction between discovery/evidence/qualification;
- no material slowdown for simple work;
- useful cross-domain routing for research, software, product, and infrastructure.

## Phase 2 — Thin provider adapters

Provider details stay under `providers/` while missions/traces remain provider-neutral.

The adapter should validate current state, authority, and stop conditions without copying the whole OODA repo into hidden runtime state.

## Phase 3 — Control Room integration

Only after real traces exist:

- the optional Control Room consumes derived OODA fields such as role, profile, lenses, claim level, cycle state, cost, verification, stop reason, and human gate;
- the dashboard remains read-only with Git/project evidence authoritative;
- displayed fields should be driven by information actually proven useful during real OODA usage.

## Phase 4 — Repository watcher / observation plane

Automate observation before dispatch or judgment.

A small local process may:

- poll an allowlist of repositories;
- detect default-branch advances, PR changes, selected state-file changes, and new OODA traces/work orders;
- keep last-seen SHAs/cursors in a small local state store;
- update a Control Room and surface candidate human-review/orientation events.

It does **not** automatically create consequential tasks, merge code, promote models, or touch live capital/runtime.

See `docs/REPO_WATCHER.md`.

## Phase 5 — Local deterministic supervisor

After repeated manual routing patterns are obvious:

- supervisor reads project contract + mission;
- may consume events from the repo watcher;
- dispatches the configured provider for explicitly allowed work;
- enforces budgets and classified stop conditions;
- collects trace + Git/test evidence;
- requests a human gate for consequential actions.

The supervisor is deterministic control logic, not the chief scientist.

## Phase 6 — Always-on local host

A small local host may run the watcher/supervisor, schedules allowed work, stores operational metadata, and updates the Control Room.

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

## Phase 7 — Multi-provider routing

Only after provider-neutral contracts are proven:

- different providers may own architecture/research/implementation according to policy;
- lower-cost providers may handle high-volume bounded work;
- provider selection is a policy decision, not a project rewrite.

## Explicitly not migrated automatically

Do not automatically import every capability from an existing agent runtime into OODA. Lifecycle implementation, local runtime coupling, issue-polling experiments, dashboards, and provider-specific session state should each re-earn their place against OODA's provider-neutral boundaries.
