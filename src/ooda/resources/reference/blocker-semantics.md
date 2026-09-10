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
It never bars work on its own. "R1D.3C not qualified" does not block R1D.4.

**A claim ceiling is not a work ceiling.** Exploration survives every blocker
except a `scientific` one whose `blocked_for` includes exploration — and that
applies only to its named target.

## Worked cases

| Situation | type | blocked_for | exploration |
|---|---|---|---|
| Multi-regime qualification not ready | promotion | qualification | **yes** |
| Continuous MFE, only five scheduled observations | scientific | exploration, evidence, qualification (target: continuous MFE/MAE) | **no, for that target only** |
| Sportsbook B1 never joined, n=0 | data | evidence (the B1 comparison only) | **yes** |
| Remote environment lacks the host snapshot | environment | evidence, qualification | **yes** (code, not evaluation) |
| Real-money trading | authority | capital | **yes** |

The Tenniskal case is the trap: a named F1-vs-B1 test can be genuinely undefined
while the research programme is entirely unblocked. Record the narrow truth.

## Challenge before idling

Before returning BLOCK or NO ACTION, answer in writing: *is there a cheap,
scientifically honest experiment available now that does not violate the current
claim or authority ceiling?* If yes, propose it.

## Legacy traces

A pre-vnext trace carrying bare `blocked` parses as `blocker_type: legacy`. It is
readable and does not bar exploration, but it must be re-typed before it can
support a claim or a promotion.
