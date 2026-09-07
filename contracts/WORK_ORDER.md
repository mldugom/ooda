# `ooda/work-order/v1`

A work order is the boundary between creative discussion and bounded execution.

It should be small enough to read quickly and precise enough to prevent silent scope expansion.

## OODA meaning

A work order is not merely a task ticket. It is the durable output of a compressed **Observe → Orient → Decide** cycle and the control envelope for **Act**.

```text
OBSERVE
current truth / authority / prior results
        |
        v
ORIENT
role + profile + lenses + uncertainty
        |
        v
DECIDE
one bounded high-value move
        |
        v
WORK ORDER
scope + verification + budget + stops
        |
        v
ACT
worker executes and re-observes
```

The goal is not to write more fields. The goal is to make sure the action is based on current reality, a conscious orientation, and one explicit decision.

## Required concepts

A work order should establish:

- project and task identity;
- objective;
- role, profile, and selected lenses;
- claim level;
- allowed and forbidden scope;
- verification or expected evidence;
- budget;
- stop conditions;
- authority.

## Four OODA checks before execution

### OBSERVE — what current truth is this mission based on?

Before dispatch, confirm the minimum authoritative state needed for the task:

- project/current-state source;
- relevant Git/PR state when applicable;
- active authority and protected surfaces;
- prior material results, especially negative findings;
- known blocker/freshness issue.

Do not copy all of that into the work order. Reference durable sources when possible.

### ORIENT — why this role/lens combination?

The work order should make the selected orientation legible through:

- one accountable role;
- one expertise profile;
- normally no more than three lenses;
- claim level;
- the material uncertainty/risk implied by the objective and verification plan.

If routing cannot be chosen without deep evidence, run a small orientation/research/architecture spike first instead of pretending the Controller already knows the answer.

### DECIDE — why this bounded move now?

The objective should represent one decision about what is worth doing next.

A strong objective answers:

- what changes or gets tested;
- what is deliberately out of scope;
- what useful uncertainty/value this move resolves;
- what would cause the mission to stop or return for re-orientation.

### ACT — what envelope controls execution?

`scope`, `verification`, `budget`, `stop_conditions`, and `authority` define the Act envelope.

The worker may adapt tactics inside that envelope, but a material objective/authority/scope change requires a new OODA decision rather than silent mission expansion.

## Documentation impact

Every substantial mission has a documentation-impact check before handoff.

Do **not** create documentation mechanically. Instead ask whether the mission materially changed how the domain, architecture, process, data flow, interfaces, operator workflow, research method, commands, or authority model should be understood.

If impact is foreseeable, include the smallest necessary documentation in allowed scope and verification.

Example:

```text
allowed scope:
- implement the new ingestion boundary
- update docs/ARCHITECTURE.md if the boundary materially changes

verification:
- focused tests pass
- architecture diagram matches final component/data flow
- README command example remains accurate
```

If the impact becomes clear only during execution, the worker assesses it before handoff. See `docs/DOCUMENTATION_STEWARDSHIP.md`.

## Work-order construction

The OODA Controller may construct or propose work orders from compact control state.

It should not become a deep planner by loading the entire code/research context. If robust construction requires facts the Controller does not have, use this pattern:

```text
raw thought / control question
        |
        v
CONTROLLER
identify missing orientation evidence
        |
        v
SHORT ORIENTATION SPIKE
researcher / architect / validator as appropriate
        |
        v
concise returned evidence
        |
        v
CONTROLLER
construct robust bounded work order
        |
        v
WORKER
```

This preserves Controller efficiency while improving task quality.

## Re-orientation during execution

A work order is not a command to blindly finish.

The worker should stop/re-observe when:

- current durable state conflicts with assumptions;
- a major new fact invalidates orientation;
- the objective materially changes;
- required authority is missing;
- the budget is exhausted;
- verification reveals that a different mission is now required.

A bounded tactical correction inside the same objective can continue. A changed objective or authority envelope becomes a new work order.

## Example

See `examples/work-order.json`.

## Design principle

> A work order should make the next action narrow without making the thinking that selected it narrow.
