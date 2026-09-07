# `ooda/work-order/v1`

A work order is the durable execution contract behind an OODA **mission**.

Human-facing CLI terminology is deliberately simpler:

```bash
ooda mission ...
```

The underlying provider-neutral schema remains `ooda/work-order/v1` so workers/providers do not depend on product wording.

A mission/work order is the boundary between creative discussion and bounded execution. It should be small enough to read quickly and precise enough to prevent silent scope expansion.

## OODA placement

The work order is the compact durable result of:

```text
OBSERVE
current truth / authority / constraints
    |
    v
ORIENT
role + profile + lenses + uncertainty
    |
    v
DECIDE
one bounded move worth taking now
    |
    v
WORK ORDER / MISSION
scope + verification + budget + stops + authority
    |
    v
ACT
worker execution
```

Do not turn the contract into a transcript of orientation. Preserve only the decision-relevant result.

## Required concepts

- project and task identity;
- objective;
- role, profile, and selected lenses;
- claim level;
- allowed and forbidden scope;
- verification or expected evidence;
- budget;
- stop conditions;
- authority.

## Human-friendly construction

Typical direct CLI use:

```bash
ooda mission \
  "Test one non-overlapping lead/lag hypothesis" \
  --role researcher \
  --profile quantitative-research \
  --lenses scientific,statistical,market-microstructure \
  --claim discovery \
  --id R6E-01
```

By default this writes:

```text
.ooda/work-orders/R6E-01.json
```

The Controller may construct the same contract conversationally. If it lacks facts required to bound the mission correctly, it should first request a short orientation spike rather than pulling deep project context into the Controller session.

## Documentation impact

For substantial changes, the mission may identify likely documentation targets such as architecture, domain model, process/data flow, interface contract, methodology, or command/operator guide.

This is a planning hint, not a mandatory documentation deliverable for every change. The active worker reassesses documentation impact before handoff. See `docs/DOCUMENTATION_STEWARDSHIP.md`.

## Stop/re-orient rule

If current durable state materially conflicts with the assumptions used to construct the mission, the worker should stop and return for re-orientation rather than silently changing scope.

See `examples/work-order.json` for the underlying JSON shape.
