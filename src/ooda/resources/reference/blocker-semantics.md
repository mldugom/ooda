# Blocker semantics

A bare `blocked` loses the information that decides what may still happen. It is
not a valid result. Every blocker is typed and scoped.

```
blocker_type        scientific | data | environment | authority | promotion | sequencing
blocked_for         exploration | evidence | qualification | production | capital
claim_ceiling       discovery | evidence | qualification | n-a
exploration_allowed yes | no
target              scientific only — the exact unidentifiable quantity
```

## The two rules

**Stages describe evidence, not permission.** `sequencing` is a historical label.
It never bars work on its own. An unqualified stage does not block the next one.

**A claim ceiling is not a work ceiling.** Exploration survives every blocker
except a `scientific` one whose `blocked_for` includes exploration — and that
applies only to its named target.

## Worked cases

| Situation | type | blocked_for | exploration |
|---|---|---|---|
| Multi-regime qualification not ready | promotion | qualification | **yes** |
| A path-dependent quantity, observed only at sparse snapshots | scientific | exploration, evidence, qualification (target: that quantity) | **no, for that target only** |
| A comparator source never joined, n=0 | data | evidence (that comparison only) | **yes** |
| Remote environment lacks the host snapshot | environment | evidence, qualification | **yes** (code, not evaluation) |
| Real-money trading | authority | capital | **yes** |

The trap is the second row of scope: a single named comparison can be genuinely
undefined while the research programme around it is entirely unblocked. Record the
narrow truth, not the broad one.

## Challenge before idling

Before returning BLOCK or NO ACTION, answer in one line:

```
Cheap honest experiment available? yes/no — <what, or why not>
```

If yes, propose it instead of declining. The question is a control invariant, not
prose to reproduce: one line, no heading, no restatement.

## Legacy traces

A pre-vnext trace carrying bare `blocked` parses as `blocker_type: legacy`. It is
readable and does not bar exploration, but it must be re-typed before it can
support a claim or a promotion.
