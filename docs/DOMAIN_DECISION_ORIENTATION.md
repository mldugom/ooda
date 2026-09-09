# Domain-First Decision Orientation

OODA should not optimize a project for activity, model sophistication, or data volume. It should keep the project aligned with the real decisions that create value in the domain.

## Core rule

> Start from the operator's decision and value function, then work backward to the evidence, model, data, and system needed to improve that decision.

This is especially important in data science. Attractive analyses are cheap to generate and expensive to mistake for progress.

## Why this sits in the Controller

Do not create a permanent extra project-manager agent by default. The Controller already owns routing and next-mission choice, so it should perform a lightweight domain/value check before committing resources.

The Controller remains thin. It should not become the domain expert. When the domain decision process is unclear, it should commission a short `product-strategist`, `researcher`, `trader`, `risk-manager`, or other appropriate orientation spike to learn the decision workflow before sending a worker into the data.

## Optional project decision brief

Projects where domain workflow materially affects priority may keep a compact durable brief, for example:

```text
.ooda/domain-decision-brief.md
```

The brief is not a status log. Update it only when the project's value function, decision workflow, constraints, or critical path materially changes.

A useful brief answers:

```text
DOMAIN / USER
Who actually makes the consequential decision?

VALUE FUNCTION
What does success mean in domain terms: revenue, avoided loss, risk-adjusted return, time saved, quality, safety, adoption, etc.?

DECISIONS
Which repeated decisions create or destroy that value?

DECISION WORKFLOW
What information is available, what choice is made, what action follows, and what outcome is observed?

CURRENT BOTTLENECK
What currently prevents a better decision: data, measurement, causal understanding, prediction, calibration, execution, workflow, adoption, or risk?

CRITICAL PATH
What must become true before the project can deliver value?

NON-GOALS / SEDUCTIVE DETOURS
What work may look sophisticated but is not currently on the critical path?
```

## Controller value check

Before proposing a consequential mission, ask compactly:

1. **Decision served** — what real user/operator/business decision becomes better if this mission succeeds?
2. **Value link** — how can that better decision create value or reduce loss/risk?
3. **Bottleneck** — is the current constraint really data/modeling, or something upstream/downstream such as workflow, execution, calibration, or measurement?
4. **Information value** — is this the cheapest high-information way to reduce the important uncertainty?
5. **Critical-path test** — does the mission advance a condition required for value, or is it merely interesting analysis?

If these answers are weak or contradictory, prefer `KEEP THINKING` or a small domain-orientation spike over a larger data/model mission.

## Quantitative projects

For quantitative/data-science projects, the preferred sequence is often:

```text
real decision
    -> value / loss function
    -> decision constraints and timing
    -> evidence needed
    -> data availability / measurement
    -> model or analysis
    -> decision rule
    -> execution / workflow
    -> realized outcome
```

The sequence is not mandatory, but the Controller should know where the current mission sits in it.

### Example: trading research

A profitable trading system ultimately needs to support decisions such as:

- trade or skip;
- which side/instrument;
- at what executable price and time;
- how much to size;
- when to exit or stop.

A model that predicts market movement magnitude may be scientifically useful while still being off the direct critical path to `trade/skip` if the project cannot yet estimate fair value or direction. The Controller should surface that distinction instead of automatically scheduling the next model-validation stage.

## Relationship to the objective ladder

The objective ladder is the project's current theory of the **value critical path**, not a commitment to research-stage chronology.

- every current rung should connect to a real decision/value bottleneck;
- completed rungs should represent material capabilities/evidence that cleared a bottleneck, not merely completed task numbers;
- provisional downstream rungs are hypotheses, not commitments;
- a material domain insight may reorder or replace downstream rungs;
- completion of a technically successful rung does not force execution of the next historical stage.

For example, after a successful R7 market-movement study, a tennis trading project may legitimately move the current rung to `Establish signed fair value versus executable price` rather than automatically making `R8` the next rung if signed fair value is the larger business bottleneck.

## Project view and Control Room mapping

Domain-first orientation should be visible without creating a second dashboard source of truth.

Use the existing `.ooda/project-view.json` as the compact derived surface:

- **`objective_ladder`** — write it as the value critical path whenever the domain/value structure materially affects priority;
- **current rung** — name the current decision bottleneck, not merely the next stage identifier;
- **`stakeholder_summary`** — for domain-driven projects prefer concise wording such as:

```text
Goal: <real value outcome>.
Current bottleneck: <what blocks the important decision>.
What we know: <durable evidence/capability>.
Current mission: <bounded question/action>.
Why now: <value-of-information / critical-path reason>.
```

- **timeline `bigger_idea`** — connect each material pivot to the real domain/value objective.

The Control Room already renders the stakeholder summary and objective ladder. This makes the paradigm visible in the dashboard without adding redundant dashboard-only state. The dashboard remains derived; the domain brief, project state, evidence, work orders, traces, and Git remain authoritative.

When a later UI revision adds dedicated `GOAL`, `BOTTLENECK`, or `CRITICAL PATH` labels, those should still derive from the same durable project orientation rather than becoming separate project-management truth.

## Work-order consequence

For consequential missions, preserve two short fields when meaningful:

```text
DECISION SERVED: the real operator/user/business decision this mission improves
VALUE HYPOTHESIS: why resolving this uncertainty is expected to create value or remove a critical-path blocker
```

These are orientation outputs, not invitations to invent business facts. If they cannot be stated honestly, stop and orient before execution.

## Agile / iterative implication

Domain-first does not mean pretending the long-range path is knowable in advance. The critical path itself is a hypothesis that should change when evidence changes.

That is why the loop is:

```text
domain decision + value
        |
        v
current bottleneck
        |
        v
highest-information bounded mission
        |
        v
artifact / evidence / result
        |
        v
re-evaluate the critical path
```

A project can therefore be uncertain about what comes three steps later while still being explicit about why the current step deserves resources.

## Design principle

> Domain understanding determines which questions are worth answering; data science determines how well we can answer them.
