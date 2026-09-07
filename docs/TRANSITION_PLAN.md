# Transition Plan — Current Stack to Future OODA Control Plane

The migration rule is: **do not destabilize the current working system to prove the future one.**

`grok-skills`, current project instructions, current Grok Build usage, and Agent Ops Monitor remain operationally intact during OODA V1.

## Phase 0 — Current state (preserved)

```text
Lawrence + ChatGPT
      -> bounded Grok prompt/session
      -> project-local rules
      -> branch/tests/artifacts
      -> handoff/PR
      -> ChatGPT + Lawrence integration gate

agent-ops-monitor = observer only
```

No OODA dependency is required for existing work to continue.

## Phase 1 — OODA V1 shadow mode

Add OODA beside the current system.

Changes:
- OODA exists as its own repo.
- Pilot projects may add `.ooda/project.json`.
- ChatGPT creates `ooda/work-order/v1` before substantial new work.
- Existing Grok Build executes it manually.
- Outcome gets an `ooda/trace/v1` record.
- No existing Grok lifecycle behavior is replaced.

Success criteria:
- less scope drift;
- less repeated research;
- better distinction between discovery/evidence/qualification;
- no material slowdown for simple work;
- useful cross-domain routing for both quant and product/software work.

Pilot order:
1. Tenniskal — clean sequential research proof.
2. Crypto-Innout — containment/reliability/engineering proof.
3. IOND — valuation + analytical-product proof.
4. LDPS — reference/methodology mine; retrofit only selectively.

## Phase 2 — Thin Grok adapter

After shadow mode is useful:
- install one `/ooda` controller skill for Grok;
- keep provider-specific details under `providers/grok/`;
- controller validates work order, current state, authority, and stop conditions;
- do **not** install the entire OODA repo into `~/.grok`.

The provider adapter should be replaceable without changing work orders or traces.

## Phase 3 — Monitor integration

Only after real traces exist:
- Agent Ops Monitor consumes derived OODA fields such as role, profile, lenses, claim level, cycle state, cost, verification, stop reason, and human gate;
- resolve existing monitor schema drift as a separate monitor task;
- monitor remains read-only with Git/project evidence authoritative.

This phase should be driven by information we actually want to see after real OODA usage.

## Phase 4 — Local supervisor

After repeated manual routing patterns are obvious:
- local supervisor reads project contract + work order;
- dispatches the configured provider;
- enforces budgets and classified stop conditions;
- collects trace + Git/test evidence;
- requests human gate for consequential actions.

The supervisor is deterministic control logic, not the chief scientist.

## Phase 5 — Raspberry Pi deployment

The Pi hosts the supervisor, schedules allowed work, stores operational metadata, and updates the monitor.

```text
Lawrence + ChatGPT
      |
      v
OODA work order
      |
      v
Pi deterministic supervisor
      |
      +--> Grok: architecture/research/engineering
      +--> future lower-cost worker: bounded production tasks
      +--> local sandbox/tests
      |
      v
OODA trace + Git evidence
      |
      v
human integration gate
```

## Phase 6 — Multi-provider routing

Only after provider-neutral contracts are proven:
- Grok may remain lead researcher/architect;
- cheaper providers may handle high-volume bounded implementation/data work;
- provider selection is a policy decision, not a project rewrite.

## Explicitly not migrated automatically

Do not automatically copy from `grok-skills` into OODA:
- lifecycle implementation;
- local runtime coupling;
- GitHub worker/issue-polling experiments;
- dashboards;
- provider-specific session state.

Those are reference implementations. Each capability must be re-earned against OODA's clean provider boundary.
