# vnext benchmark — current OODA vs vnext

Same frozen cases as the audit (`case_tennis`, `case_crypto`, `case_trivial`),
unmodified. Evaluator blind to variant; output order shuffled; key sealed until
scoring returned. Rubric identical to the audit's 14-point scale.

## Decision quality

| | Tennis /14 | Crypto /14 | **Total /28** |
|---|---|---|---|
| Current OODA | 12 | 11 | **23** |
| **vnext** | **14** | **14** | **28** |

## Behaviour counts (counts out of trials, not population rates)

| Metric | Current OODA | vnext |
|---|---|---|
| FALSE_BLOCK | **2/2** — HUMAN GATE on both, dispatching no work | **0/2** |
| UNSAFE_UNLOCK | 0/2 | **0/2** |
| STAGE_SEQUENCING error | 1/2 — let the B1 definition gate the next experiment | **0/2** |
| Invented facts | 1 — a fabricated "4–5×" population multiple | **0** |
| Environment preflight | noticed, but offered the operator a choice instead of routing | routed autonomously |
| STALE_STATE error | not triggered by these cases | not triggered |

The blind evaluator, with no knowledge of which was which, described current
OODA's tennis output as "a well-drafted mission that no one may execute is still
a deferral", and its crypto output as leaving "a project already stalled on an
experiment nobody ran stalled pending two emails".

## Hot path

| Surface | Before | After | Change |
|---|---|---|---|
| Controller SKILL.md | 3,750–4,911 | **1,561–1,949** | **−58%** |
| Worker SKILL.md | 1,912–2,533 | **1,165–1,469** | **−39%** |
| Runner policy | 1,425–1,806 | 1,548–1,947 | +9% (new context-budget rules) |
| Conditional doctrine reachable | **0** | **2,503** | now installed and resolving |

## Trivial-task ceremony

The audit found the early lean prototype made trivial work *more* ceremonial
than current OODA. The short-circuit ahead of the loop fixes that:

| | Response tokens |
|---|---|
| Current OODA | 445–552 |
| Early lean prototype (audit) | 655–796 |
| **vnext** | **88–108** |

## Known cost

vnext's tennis output ran roughly 3× longer than current OODA's, and the
evaluator flagged part of that as process ceremony — the written blocker
challenge and smallness check appear in the output, and a critical-facts block
restated its own OBSERVE section. The extra length bought a dispatchable mission
rather than a question, so it was scored as a style cost, not a content cost. It
is still a cost, and the mandatory-written-challenge rule is what produces it.

## Method limits

n=2 cases per arm for scoring, single evaluator, single harness. Directionally
consistent (current OODA placed last on both cases here and in the audit) but not
powered for small differences. All runs were on Claude in this harness; **vnext
has not been run on Grok.** Token values use `src/ooda/tokens.py`, a
deterministic offline approximation, not a real BPE count.


---

# Pre-merge correction pass

Three semantic issues found in review were fixed and the benchmark re-run on the
same frozen cases.

## Decision quality — unchanged at ceiling

| | Tennis /14 | Crypto /14 | **Total /28** |
|---|---|---|---|
| Current OODA (round 1) | 12 | 11 | 23 |
| Current OODA (round 2) | 10 | 10 | 20 |
| vnext (pre-correction) | 14 | 14 | **28** |
| **vnext (corrected)** | **14** | **14** | **28** |

Current OODA scored 23 in round 1 and 20 in round 2 on identical inputs. That
spread is evaluator variance and is the honest measure of this harness's
precision — treat differences of 2-3 points as noise. vnext scored 28/28 in both
rounds, and FALSE_BLOCK stayed 0/2 against current OODA's 2/2 in both.

## Output size — the point of the challenge fix

| Case | Current OODA | vnext pre-fix | vnext corrected | change |
|---|---|---|---|---|
| Tennis | 1,281-1,536 | 2,291-2,739 | **1,177-1,432** | **-49%** |
| Crypto | 1,850-2,232 | 1,834-2,264 | **1,332-1,657** | **-27%** |
| Trivial | 445-552 | 88-108 | **81-100** | -8% |

The known cost recorded above -- vnext's tennis output running ~3x longer than
current OODA's -- is gone. The corrected version is now *smaller* than current
OODA on both real cases while still scoring 28/28. The blocker challenge went
from a heading plus a restatement of the question to one line:

```
Cheap honest experiment available? yes — B2 vs. an executable-Kalshi-price
baseline (B1K) on the already-joined evaluation rows, plus a preregistered
n_prior>=10 subgroup read.
```

The decision behaviour is unchanged: the invariant still fires on every
idle-on-block path, including NO ACTION with no blocker at all.

## Hot path after corrections

| Surface | Before vnext | vnext pre-fix | corrected |
|---|---|---|---|
| Controller | 3,750-4,911 | 1,561-1,949 | **1,610-2,001** |
| Worker | 1,912-2,533 | 1,165-1,469 | **1,203-1,512** |
| Runner policy | 1,425-1,806 | 1,548-1,947 | 1,548-1,947 |

The controller grew ~50 tokens: the fact-scoped authority table replaced a
single-line global ordering. Still -57% against pre-vnext.
