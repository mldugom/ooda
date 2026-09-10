# `ooda/work-order/v1`

A work order is the durable execution contract behind an OODA **mission**. It is
the boundary between creative discussion and bounded execution: small enough to
read in seconds, precise enough to prevent silent scope expansion.

```bash
ooda mission ...
```

The schema stays `ooda/work-order/v1` so workers and providers do not depend on
product wording.

## The lean default

Eight fields. This is what an ordinary mission carries:

```text
OBJECTIVE             one bounded outcome
WHY NOW               the decision served, and why this is the highest-value move
AUTHORITATIVE INPUTS  pointers to the truth the worker should read
CRITICAL FACTS        <= 10 facts the worker cannot safely discover late
ALLOWED               scope
FORBIDDEN             scope
EXPECTED OUTPUT       what comes back
STOP CONDITION        when to stop, always present
```

**Pointers, not history.** Do not pre-load old traces, whole research histories,
PROJECT_STATE prose, doctrine, dashboards, or unrelated PRs. The worker fetches
depth on demand. Context is a cost the mission pays on every turn.

## Optional, only when they bind

```text
CLAIM CEILING     discovery | evidence | qualification | n-a
AUTHORITY         when the default deny-list is not enough
BUDGET            small | medium | large, or explicit turns/tool calls
ROLE              accountability descriptor
PROFILE           expertise descriptor
LENSES            0-1 by default
ENVIRONMENT       requirements this mission needs from its execution environment
```

`role`, `profile`, and `lenses` are **optional routing aids, not required
fields**. The vnext ablation found no measurable gain from them on ordinary
data-science work, where a worker given none scored joint-top. Attach one only
when it will materially change worker behavior; state the scientific constraints
directly otherwise. Two or more lenses require `lens_justification`; three is the
hard cap. See `reference/routing-vocabulary.md` for where they do earn a place.

## Environment preflight

A mission that needs local datasets, an operator-host runtime, private files,
live processes, GPUs, or credentials declares them:

```json
"environment_requirements": ["path:data/tape.sqlite", "env:XAI_API_KEY"],
"environment_route_to": "the operator host that holds the snapshot"
```

`ooda preflight --work-order FILE` verifies them **before** dispatch. An entire
remote research cycle was once implemented against data the environment did not
have; this check is what prevents the repeat.

## Mission economics

A consequential mission states the decision served, what result would change it,
and a resource budget. If those cannot be stated honestly, the answer is KEEP
THINKING or a small orientation spike — not a larger mission. Do not create work
because a historical stage number comes next.

## Stop conditions

Every mission has one. "Once baseline metrics are computed", "once the bug is
reproduced and fixed", "after N candidate families", "if the environment lacks
the data", "if the target is not identifiable". Never "find the best possible
model".

## Stop and re-orient

If durable state materially conflicts with the assumptions the mission was built
on, the worker stops and returns for re-orientation rather than adapting scope
silently.

See `examples/work-order.json` for the lean shape and
`examples/work-order-specialist.json` for a case where descriptors earn their
tokens.
