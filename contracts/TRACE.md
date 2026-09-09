# `ooda/trace/v1`

A trace records decision provenance without storing private chain-of-thought.

It is not a transcript.

## OODA meaning

The trace is the durable feedback edge from one action into the next observation.

```text
WORK ORDER
   |
   v
ACT
worker executes bounded mission
   |
   v
RE-OBSERVE
what actually happened?
   |
   v
TRACE
concise O / O / D / A + verification + result
   |
   v
NEXT ORIENTATION
Controller / Lawrence / ChatGPT decide what follows
```

The trace exists so future sessions do not need to reconstruct the same reasoning from commits, chat history, and stale summaries.

## What a trace records

- work-order ID;
- provider/model/agent when known;
- repository base/head and PR when relevant;
- concise Observe / Orient / Decide / Act summaries;
- result state;
- verification;
- costs/turns/tool calls when known;
- material findings, especially negative findings;
- documentation impact/result when material;
- human gate or next decision.

## OODA fields

### OBSERVE
Record the verified state that mattered to the result, especially when it differed from assumptions.

Examples:

- branch/PR/base truth;
- actual available data/support;
- test/reliability state;
- missing dependency;
- stale or contradictory project state.

### ORIENT
Record the **decision-relevant orientation**, not private chain-of-thought.

Useful content includes:

- role/profile/lenses used;
- key uncertainty or risk;
- important alternative explanation;
- reason a previously attractive path was rejected.

### DECIDE
Record the bounded action actually chosen, including any legitimate in-mission correction.

If the objective materially changed and execution stopped, say so rather than pretending the original mission completed.

### ACT
Record what was changed/tested/executed and the evidence produced.

## Quantitative research feedback

For material work under `quantitative-research`, `statistics`, `data-science`, `ml-research`, `quant-markets`, or an equivalent project profile, preserve the smallest useful research evidence packet so the next loop does not depend on terminal prose.

The packet may be embedded in the trace or point to an authoritative research artifact. Useful fields are:

```text
QUESTION: decision uncertainty tested
DATA: sample / snapshot / support / PIT-as-of semantics
ANALYSIS: statistic, model, comparison, or experiment run
KEY EVIDENCE: compact n + metric/effect + sensitivity/uncertainty + verdict table
INTERPRETATION: what can and cannot now be claimed
ARTIFACT DECISION: none | table | diagram | diagnostic | durable-panel | dashboard
ARTIFACTS: durable markdown/CSV/JSON/HTML/figure paths
DASHBOARD IMPACT: none | refresh existing panel | proposed panel | dashboard update required
NEXT UNKNOWN: highest-value uncertainty exposed by the result
```

Do not create redundant artifacts when an existing result document/report already contains this information. The requirement is legible durable feedback, not file count.

See `docs/QUANTITATIVE_RESEARCH_LOOP.md` and `docs/RESEARCH_VISUALIZATION.md`.

## Documentation result

When documentation impact was assessed, the trace/handoff should state either:

```text
DOCUMENTATION: none — conceptual/domain/interface/process surface unchanged
```

or a concise list such as:

```text
DOCUMENTATION:
- updated docs/ARCHITECTURE.md data-flow diagram
- updated README CLI example
- validator checked diagram against final interfaces
```

This is an audit signal, not a requirement to create documentation for every task. See `docs/DOCUMENTATION_STEWARDSHIP.md`.

## Result states

Typical result states are:

- `completed` — bounded objective completed with stated verification;
- `negative_finding` — useful evidence says the candidate/path did not survive;
- `blocked` — external/state/authority dependency prevents valid execution;
- `budget_exhausted` — more work requires a new resource decision;
- `needs_human_gate` — execution/review reached an authority boundary.

A negative finding is a successful trace outcome when it prevents repeated wasted work.

## Trace quality

A useful trace is small enough for the Controller to read cheaply and strong enough that a future worker does not need to replay the session.

Prefer:

- concrete facts;
- artifact/test references;
- explicit limitations;
- negative results;
- next gate.

Avoid:

- private chain-of-thought;
- long chronological logs;
- raw terminal output unless it is itself the relevant artifact;
- claims stronger than the work order's allowed claim level.

## Control Room use

The trace is intended to become a provider-neutral input to the OODA Control Room / Agent Ops Monitor.

The dashboard may index the latest useful trace and historical trace chain, but it remains a view. The trace and underlying project/Git evidence are authoritative.

## Design principle

> The action is not operationally complete until its useful feedback can enter the next OODA loop.
