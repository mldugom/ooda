# Agent Ops Monitor Boundary

Agent Ops Monitor remains a separate repository and a read-only coordination view.

## OODA owns
- operating doctrine;
- roles/profiles/lenses;
- work-order contract;
- run trace;
- budget/stop/authority semantics.

## Project repositories own
- actual code/data/research truth;
- Git state;
- project-specific constraints;
- scientific and production artifacts.

## Agent Ops Monitor owns
- rendering;
- freshness;
- portfolio/backlog visibility;
- agent lane visibility;
- human decision queue.

It must not become the orchestrator merely because it can display OODA state.

## Future OODA-derived fields

After real usage proves useful, a monitor exporter may derive:
- work_order_id;
- OODA stage;
- role;
- profile;
- lenses;
- claim level;
- provider;
- cost/turn/tool-call metrics;
- verification state;
- stop reason;
- next human gate;
- negative finding / durable lesson reference.

The monitor should consume these as observations. It does not decide the next action or certify the result.

## Why integration is deferred

The current monitor already has value and existing project integrations. OODA V1 should first produce real traces. Only then should the monitor schema be changed around information that proved useful in practice.
