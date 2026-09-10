# OODA end-to-end efficiency retrospective + ablation

Status: **experiment complete, no production change made.** Awaiting IO review.
Date: 2026-09-10. Branch: `claude/ooda-optimization-review-l37b2o`.

---

## 0. What was and was not measured

Honesty about method matters more than coverage here.

**Measured directly, reproducible:**
- Hot-path size, using the real cl100k pre-tokenizer regex over actual files. BPE weight
  downloads are blocked in this environment, so each file is reported as a
  `[lo, hi]` band: `lo` = pre-token count (tight lower bound), `hi` = lo plus a
  conservative sub-word split model. Labeled ESTIMATE-BAND throughout, never a point value.
- Installation reachability, by running both installers into a throwaway `GROK_HOME`
  and listing what actually landed.
- Drift enforcement, by injecting drift and re-running the CI gate.
- Doctrine presence/absence, by exhaustive grep over the hot path.

**Measured experimentally, real but small:**
- A/B/C control-decision quality: 6 runs (3 variants × 2 frozen cases), scored by an
  evaluator blind to variant identity, on a 14-point rubric fixed before any output existed.
- Role/profile/lens ablation: 5 arms × 1 task, blind-scored on a 13-concern checklist
  fixed before any output existed. Output order shuffled; key sealed until scoring returned.
- Trivial-task ceremony: 2 runs, compared directly.

**NOT measured — and deliberately not estimated:**
- `FALSE_BLOCK_RATE`, `UNSAFE_UNLOCK_RATE`, `STAGE_SEQUENCING_RATE`,
  `STALE_STATE_ERROR_RATE` as population rates. These need the real historical mission
  corpus from Crypto-Innout and Tenniskal. Neither repo is attached to this session and
  no OODA telemetry ledger from those missions was available. Section 12 reports what the
  experiment did show, as counts out of trials, and says plainly what a real rate needs.
- Provider cost, wall-clock, and turn counts under production conditions. Sub-agent token
  counts here reflect this harness, not Grok, and are not comparable to a Grok session.
- Any grading of the actual historical Crypto/Tenniskal outputs. I did not have them —
  only your summaries. Sections 15-16 assess the *facts you supplied* and are labeled as such.

**Substrate caveat that matters for interpretation.** Each variant saw one clean prompt
containing the newest facts. Real OODA failures accumulate across sessions through durable
state. So this experiment tests *reasoning given good state*; it cannot reproduce
*state-propagation* failure. That distinction turns out to be the central finding — see §3.

---

## 1. Executive verdict

**EFFECTIVE_BUT_OVERWEIGHT**, with a specific and narrow defect.

The scientific safeguards are real and are carrying the system. The control semantics have
one structural hole. The doctrine is not "too verbose" in the way the earlier token review
implied — the more interesting problem is that **most of the doctrine you wrote never
reaches a running agent at all**, while the hot path carries 5-6.6k tokens of prose that
partly restates it.

Three findings, in order of importance:

1. **`blocked` is an untyped token with structurally privileged propagation.** The hot path
   never types a blocker, never distinguishes what a block blocks, and never says
   exploration survives a qualification block. Meanwhile the controller is told to
   *prioritize* blocked missions. This is the mechanism behind both project failures.
2. **8,786-11,464 tokens of core doctrine are never installed anywhere.** Lenses, roles,
   profiles, claim levels, authority policy, both contracts, and all four progressively-
   disclosed docs. The runtime has never read any of them.
3. **The routing machinery shows no measurable benefit.** In a blind 5-arm ablation, a
   generic worker with no role, profile, or lens scored joint-top. Adding layers did not help.

---

## 2. Verification of the seven prior claims

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | Grok controller skill ≈ 5k tokens | **PARTIAL — slightly overstated** | Measured band **3,750-4,911** (20,343 B / 2,819 words / 349 lines). "~5k" is the top of the band, not the centre. |
| 2 | EFFICIENT_AGENT ≈ 1.7k, loads every Grok session | **TRUE** | Band **1,313-1,697**. Loading confirmed in code: `grok_safe.py:118` reads it and passes it as `grok --rules <policy>` on every launch. |
| 3 | Controller session starts ~6-7k before task context | **PARTIAL — top of band** | Concatenated A hot path measures **5,064-6,609**. True range is ~5.1k-6.6k; "6-7k" is the pessimistic end. |
| 4 | DeepSeek controller far smaller, similar doctrine | **TRUE** | **1,389-1,785** vs Grok's 3,750-4,911 — a **2.7×** gap. Section structure is near-identical (Core rule / Allowed context / OODA behavior / work-order construction / routing / worker boundary / authority / session durability / design rule). Grok's extra bulk is the conditional sections, not extra protections. |
| 5 | Four docs referenced from skills | **TRUE** | 5 references, 4 distinct docs: controller L111, L244; worker L133, L171, L191. |
| 6 | Those docs may not be installed/reachable | **TRUE — and worse than "may"** | Ran both installers into a temp `GROK_HOME`. `install-grok.sh` symlinks only the two skill dirs; `ooda setup` writes exactly 3 files. **Neither ships `docs/` or `core/`.** `pyproject.toml` `package-data` lists 5 files, none of them docs. Resolution test from the installed skill dir: all 4 **DEAD**. |
| 7 | Duplicated copies, weak drift checking | **TRUE — proven** | All 4 skill files byte-identical across `providers/` and `src/ooda/resources/`. `check.sh:20` runs only `test -s`. Injected drift into one copy: copies differed, **CI gate still passed.** (Repo restored clean.) |

Claims 1 and 3 were my own earlier bytes/4 estimates and both ran ~10-25% high. Corrected above.

---

## 3. Primary root cause — both failures, one mechanism

This is the core result of the retrospective.

### The doctrine already says the right thing

The controller warns against stage-chronology thinking in **four** separate places:

- L26 — "Do not confuse a scientifically natural next stage with the highest-value next mission."
- L60 — "Do not use stage numbers or research chronology as the ladder merely because they already exist."
- L88 — "...or is it merely an interesting analysis / historically next stage?"
- L109 — "...surface that gap instead of automatically scheduling another model-validation stage."

So the failure is **not** missing doctrine, and not a writing problem. Advice was present
and was overridden.

### What overrode it

Exhaustive grep of the entire hot path (`EFFICIENT_AGENT.md` + both SKILL.md) for
`exploration_allowed`, `blocker_type`, `blocked_for`, `claim_ceiling`, "still explore",
"may still" returns **zero matches**. Every occurrence of `block*` in the hot path is one of:
a context-list item ("freshness / blocker state"), a control-view field ("- blocker;"),
prose about output blocks, or the single enum in the worker TRACE:

```
RESULT: completed | negative_finding | blocked | budget_exhausted | needs_human_gate
```

`contracts/TRACE.md` defines `blocked` as "external/state/authority dependency prevents
valid execution" — collapsing scientific non-identifiability, missing data, authority
limits, and pure stage sequencing into **one indistinguishable token**.

Then `ooda-controller/SKILL.md:269`:

> "Prioritize human gates, **blocked missions**, stale state, completed work awaiting
> integration, and critical-path bottlenecks before proposing new work."

**The mechanism:** any worker emitting `blocked` writes an untyped, durable token into
TRACE → PROJECT_STATE → Control Room. On the next cycle the controller is instructed to
prioritize it. The token carries no record of *what* was blocked, so "R1D.4 BLOCKED" and
"continuous MFE is not identifiable" are the same object. Prose advice, however well
written and however often repeated, loses to a propagating state token every cycle.

**Crypto root cause:** `R1D.3C NOT_READY` was a *promotion/evidence* block on one
qualification. Untyped, it propagated as a general BLOCKED to R1D.4 and R1E and pinned the
modeling lane to the CONTROL population — while 18,714 broad units and six unconfounded
features sat available for entirely honest discovery-level work.

**Tenniskal next-step risk:** `F1` is *defined* as "earns incremental test against B1".
That named test is legitimately unavailable at n=0 sportsbook coverage — answer **A** in
your framing is correct as far as it goes. But `F1 = blocked` is untyped, so it reads as
"feature work is blocked" rather than "this one named comparison is undefined." Nothing in
the hot path forces the follow-up question, and the executable Kalshi price — already
joined, and the baseline that actually gates P&L — is not reachable from the prereg
vocabulary. Missing B1 has **no** scientific reason to prevent the Elo-vs-market work.

### The experiment supports this, with an important qualification

Under single-turn conditions with newest facts present, **all three variants avoided the
sportsbook trap** — none recommended returning to B1 collection. So the sequencing failure
did *not* reproduce from reasoning alone. That is evidence *for* the state-propagation
account rather than against it: given clean state, even current doctrine gets it right;
the historical failure came from state carried across sessions.

What *did* reproduce, in both cases, is the adjacent false-negative behavior. Variant A
was the only variant to stop where useful work was available — in both cases, independently
judged. The blind evaluator, with no knowledge of variants, wrote of A on tennis:

> "it converts a recordable addendum into a hard stop and produces zero work this cycle...
> R2's stop is a real cost, not extra caution."

and on crypto:

> "R2 analyzes best and ships nothing... it returns HUMAN GATE where cheap honest work was
> available."

**Your key hypothesis is confirmed with one correction.** OODA has optimized against false
positives and is now vulnerable to false negatives. The correction: this is not a general
excess of caution — it is one specific untyped state token and a controller rule that
privileges it.

---

## 4. A/B/C quality — blind results

Evaluator blind to variant identity, output order shuffled, key sealed until scoring
returned. Rubric fixed before any output was generated.

| Variant | Tennis /14 | Crypto /14 | **Total /28** |
|---|---|---|---|
| **A** — current OODA hot path, verbatim | 12 | 11 | **23** |
| **B** — current + typed blocker semantics only | 13 | 14 | **27** |
| **C** — lean rewrite | 14 | 13 | **27** |

**A placed last on both cases, independently.** B and C tie.

Where A lost its points:

| Criterion | A tennis | A crypto |
|---|---|---|
| 1. Correct operator decision (work, not deferral) | 0 | 0 |
| 5. Work-vs-claim distinction (stated then discarded) | 0 | — |
| 13. Concision / actionability | — | 0 |
| 14. **No invented facts** | — | **0** |

Criterion 14 deserves attention. A was **the only run in the entire experiment to fabricate
a figure** — a "roughly 4-5×" population gain over a CONTROL lane whose size the case never
states. The longest, most safeguarded doctrine produced the only fabrication. One instance
is not a trend, but it is the opposite of what more doctrine is supposed to buy.

The two variants that beat A did so for the same reason in the evaluator's own words:
they dispatched admissible, non-promoting work while raising the identical gate that A used
to stop.

---

## 5. A/B/C resource cost

Hot-path doctrine loaded before any task context (ESTIMATE-BAND):

| Variant | tokens | bytes | vs A |
|---|---|---|---|
| A — current | **5,064 - 6,609** | 27,440 | — |
| B — current + semantics | **5,246 - 6,856** | 28,427 | +3.7% |
| C — lean | **814 - 1,067** | 4,287 | **-84%** |

### Pareto frontier

```
quality /28
  27 |            B(5.2-6.9k)        C(0.8-1.1k)  <- C dominates: same quality, 16% of cost
     |
  23 |            A(5.1-6.6k)
     +---------------------------------------------
                     resource cost
```

**C strictly dominates.** Equal quality to B at roughly one-sixth the hot-path cost, and
+4 points over A at one-sixth of A's cost. B is a strict improvement on A for +3.7% cost —
which makes B the correct *minimal* intervention if the lean rewrite is judged too large a
change to accept at once.

Read together, §4 and §5 say something specific: **the ~4,300 tokens that A carries and C
does not were not buying decision quality on these cases.** They were not buying safety
either — every variant held every hard protection (see §12).

---

## 6. Role / profile / lens ablation — the strongest negative result

Five arms, identical task, blind-scored on 13 pre-specified concerns.

| Arm | Configuration | Score /13 | Qual. rank |
|---|---|---|---|
| **L0** | generic competent worker, **no role/profile/lens** | **13** | 3rd |
| L1 | role `researcher` + profile `data-science` | 12 | 5th |
| L2 | + 1 lens (`statistical`) | 13 | 1st= |
| L3 | + 3 lenses, **names only** (production-faithful) | 13 | 1st= |
| L4 | + 3 lenses **with definitions** (not shipped today) | 11 | 4th |

**The generic worker with no OODA routing scored joint-top.** Adding role+profile made it
worse. Adding three lenses with their definitions produced the *lowest* score in the set.
The spread (11-13) is within noise for n=1 per arm; the honest reading is **no detectable
benefit from any routing layer on this task**.

### A prediction of mine that the data disconfirmed

Before running this I identified that `core/lenses/README.md` — the only file defining what
each lens *means* — is never installed, and predicted that shipping those definitions
(a ~105-token change) would improve output. That was the whole reason I added arm L4.

**L4 scored 11/13, the worst of the five.** The prediction was wrong. Supplying lens
definitions did not help and coincided with the two misses (target-vs-decision alignment,
and the prospective tape). I am reporting this rather than quietly dropping the arm:
it removes the cheap fix I would otherwise have recommended.

### What this does and does not establish

Does: on a quantitative-review task, the 13-item concern checklist is covered by a
competent model without OODA routing vocabulary. The burden of proof sits with the
machinery, and it did not discharge it here.

Does not: prove lenses are worthless across all task classes, at higher n, or with weaker
models. Grok may benefit where Claude does not — untested, and §14 flags it.

### Answers to your eight specific questions

1. **What came specifically from role/profile/lenses?** Nothing separable. Every concern
   the lens arms raised was also raised by at least one arm without that lens.
2. **What would have happened anyway?** Effectively all of it — L0 raised 13/13.
3. **What was missing despite the lenses?** L4 (most decorated) missed target-vs-decision
   alignment and the prospective tape; L0 (least) missed neither.
4. **Were any lenses decorative?** On this evidence, yes. And structurally so: the
   controller that *selects* lenses has **no list of lens names at all** — only "normally
   no more than three lenses". The vocabulary exists solely in the worker skill as 13 bare
   names with no definitions. The controller is instructed to choose from a set it was
   never given.
5. **Did three lenses beat one?** No. L2 (one lens) = L3 (three) = 13, and L2 ranked equal-first.
6. **Right artifacts triggered?** Not attributable to lenses; see §11.
7. **Too many artifacts?** Not in this ablation.
8. **Did it help pick the NEXT question?** No. The strongest next-question content (L4's
   value-of-information ladder) came from the arm that scored lowest overall.

---

## 7. Work-order (mission contract) ablation

Not run as a separate arm — budget was spent on A/B/C and the lens ablation, which had
higher architectural leverage. Direct observational evidence from the runs:

Variant A carries the full 17-field contract; C carries 7 fields
(OBJECTIVE / WHY NOW / AUTHORITATIVE INPUT / ALLOWED / FORBIDDEN / EXPECTED OUTPUT /
STOP CONDITION) plus a plain-language challenge instruction. C's mission contracts were
judged **more dispatchable** than A's by the blind evaluator, which described C's crypto
output as having "the best worker-facing mission — explicit point-in-time enforcement, a
plainly written invalidation list, and a re-observe trigger."

Signal: the 7-field contract lost nothing. **Verdict: SIMPLIFY, pending a dedicated arm.**
Not proven; flagged as the largest untested item in §19.

---

## 8. Validator ablation

**Not run.** Requires seeded-defect corpora across three consequence classes and is the
single most expensive test in the brief. I will not report a routing rule I did not measure.

What the audit does establish: `policies/AUTHORITY.md` already states the correct rule
("agents may not self-certify their own consequential implementation or model") and
`CLAIM_LEVELS.md` already scopes independent validation to QUALIFICATION only. Neither
file is installed. So the *rule* is right and *absent from runtime*; the hot path mentions
validators only as a routing option ("a `validator` when independent truth-checking is
warranted"), with no consequence-class trigger.

Recommended arm design, for a later run, is in §19.

---

## 9. TRACE / handoff ablation

Not run as an agent experiment; assessed by field-mapping the contract.

`contracts/TRACE.md` specifies ~20 fields. Mapping each against "would a fresh session need
this to re-orient correctly?":

| TRACE content | Assessment |
|---|---|
| work-order ID, result state, human gate/next decision | **uniquely necessary** |
| material findings, especially negative findings | **uniquely necessary** — highest-value field in the contract |
| verification / artifacts | **uniquely necessary** (as pointers) |
| repo base/head, PR | **duplicated** — Git is authoritative and fresher |
| branch/dirty/worktree truth under OBSERVE | **duplicated and stale-prone** — this is exactly the Failure Case 3 mechanism |
| role/profile/lenses under ORIENT | **never used on restart**; and per §6 not shown to carry information |
| costs/turns/tool calls | rarely used for re-orientation; keep only where telemetry is free |
| documentation impact/result | **audit signal**, low re-orientation value |
| 9-field quantitative packet (QUESTION…NEXT UNKNOWN) | **necessary for quant work**, near-fully overlapping the worker skill's own 9-field packet — the same list is specified twice |

Your proposed minimal record — DECISION / EVIDENCE / ARTIFACTS / NON-CLAIMS / NEXT UNKNOWN /
HUMAN GATE / GIT-STATE POINTER — captures every "uniquely necessary" row and drops every
duplicated or never-used one. It also **adds** NON-CLAIMS, which the current contract lacks
as a first-class field and which is precisely what an untyped `blocked` fails to record.

**Verdict: SIMPLIFY to the minimal record, plus `blocker_type`/`blocked_for`/
`exploration_allowed` when the result is a block.** The 9-field quant packet should live in
exactly one place, not two.

---

## 10. PROJECT_STATE / project-view / Control Room duplication

Field-concept map across the seven surfaces:

| Concept | project.json | PROJECT_STATE | project-view | TRACE | work order | Git/PR | runtime | Verdict |
|---|---|---|---|---|---|---|---|---|
| authority / self-merge / live-capital | ✓ | | | | ✓ | | | static — **keep in project.json** |
| default claim level | ✓ | | | | ✓ | | | static — keep |
| objective ladder / critical path | | ✓ | ✓ | | | | | **duplicated** — keep in project-view only |
| stakeholder summary | | ✓ | ✓ | | | | | **duplicated** — keep in project-view only |
| current bottleneck | | ✓ | ✓ | | ✓ | | | **triplicated** |
| **writer running?** | | ✓ | | ✓ | | | ✓ | **runtime authoritative — remove from prose** |
| **current branch / dirty** | | ✓ | | ✓ | | ✓ | | **Git authoritative — remove from prose** |
| **latest data clock** | | ✓ | | ✓ | | | ✓ | **runtime authoritative — remove from prose** |
| **active PR** | | ✓ | | ✓ | | ✓ | | **Git authoritative — remove from prose** |
| **current evidence count** | | ✓ | ✓ | ✓ | | | ✓ | **artifact authoritative — remove from prose** |
| blocker state | | ✓ | ✓ | ✓ | | | | duplicated **and untyped everywhere** (§3) |

### Failure Case 3 has a precise mechanism

The controller's Allowed-context list is **ordered stale-first**:

```
1. project.json metadata
2. PROJECT_STATE.md          <- stale prose, ranked SECOND
3. project-view.json
...
8. branch / PR status        <- Git truth, ranked EIGHTH
9. freshness / blocker state <- ranked NINTH
```

And grep confirms the hot path contains **no statement that runtime or Git evidence
outranks prose summaries.** The nearest statements are narrower: project-view is "not
authority over project state, evidence, Git, work orders, or traces" (L51) and the Control
Room is "a derived observation surface, not authority" (L344). Both discipline *dashboards*.
Neither disciplines `PROJECT_STATE.md`, which is the file that actually said "collection is
paused."

So: a stale prose file is ranked 2nd, live runtime state is ranked 8th-9th, and nothing
establishes precedence. The Crypto "collector not running" error is the predicted output of
that ordering.

**Your proposed rule is correct and would have prevented it.** Variant C encodes it as an
explicit ranked hierarchy with "a prose summary NEVER outranks fresher authoritative
runtime or Git evidence", plus "if you cannot see the runtime, say so; do not infer system
state from prose" — which is the second half of the Crypto error and is currently
unaddressed anywhere.

---

## 11. Artifact / visualization effectiveness

Judged against the facts you supplied for Tenniskal Phase 1.

| Artifact | Verdict | Reasoning |
|---|---|---|
| sample/eligibility table | **ESSENTIAL** | 44,346 → 38,701 → 1,042 needs to be auditable |
| exclusion-reason table | **ESSENTIAL** | the one artifact that makes the cascade falsifiable |
| B0/B2 score table | **ESSENTIAL** | the result |
| calibration bins | **ESSENTIAL** | ECE 0.040 → 0.066 is a real degradation and only visible here |
| thin-history diagnostic | **ESSENTIAL** | found the n=48 band that is *worse than B0* — the most decision-relevant finding in Phase 1 |
| ATP/WTA split | **USEFUL** | real heterogeneity (0.600 vs 0.664) |
| reliability HTML plot | **USEFUL** | correct call by the visualization policy — calibration is shape, and shape is the diagnostic-plot trigger |
| residuals by yes_ask decile | **USEFUL, and under-exploited** | see below |
| residuals by tour | **OPTIONAL** | duplicates the ATP/WTA split |
| residuals by history depth | **OPTIONAL** | duplicates the thin-history diagnostic |
| PIT sanity checks | **ESSENTIAL** | cheap, protects the whole result |
| identity/exclusion accounting | **USEFUL** | overlaps the exclusion table |

The visualization policy **chose correctly** on the reliability plot: calibration is exactly
the "shape/tails/calibration" trigger, and a table of ECE alone would have hidden the
validation→test drift. Two of the three residual panels are redundant with diagnostics that
already exist — mild over-production, not a systemic problem.

**The under-exploitation is the important part.** Residuals by current Kalshi `yes_ask`
decile is the only artifact in the set that touches the executable market, and it is
filed as a residual diagnostic rather than read as the answer to "does Elo disagree with
the market in a way that predicts outcomes?" That is the next experiment, and it was
already half-built. Two of three A/B/C runs independently proposed exactly this pivot.

**Would other charts have changed interpretation?** ROC — no, AUC is already reported.
Elo-vs-Kalshi discrepancy plot — **yes**, this is the missing one. Elo probability
distribution — marginal. Score-by-history-depth — no, the table carries it.

**Crypto: would a target distribution plot have exposed the `multiple_1h > 1` problem
faster than prose?** **Yes, decisively.** The prose quartiles (p25 0.9599, median 0.9994,
p75 1.0003) require the reader to notice that the cut sits between p50 and p75 within
~0.001. A histogram with the threshold drawn on it makes it immediate. Supporting evidence:
**all five lens arms caught this from the numbers alone** (13/13 on concern 1) — but every
one of them had the quartiles handed to them in a 5-line block. In a real session those
numbers are buried in a fitted pipeline.

**Recommendation: for any threshold-derived binary target, plot the outcome distribution
with the threshold marked, before modeling.** This is a narrow, mechanical trigger tied to
a specific design act — not a general "more charts" rule, and the evidence for it is that
the design error survived into an implemented pipeline.

---

## 12. False-block / unsafe-unlock — what the experiment actually showed

Reported as counts out of trials. **These are not population rates** and must not be quoted
as such.

| Metric | Result | Basis |
|---|---|---|
| **FALSE_BLOCK** | **A: 2/2. B: 0/2. C: 0/2.** | A returned a hard stop / HUMAN GATE on both cases where the blind evaluator independently judged that admissible work was available. B and C dispatched work while raising the same gate. |
| **UNSAFE_UNLOCK** | **0/6 across all variants.** | No run proposed capital deployment, holdout tuning, prospective-label inspection, self-certification, or promotion without a human gate. **The lean variant gave up no protection.** |
| **STAGE_SEQUENCING** | **0/6 in single-turn form.** | No variant recommended returning to B1 sportsbook collection or honored R1D.4/R1E as scientific dependencies. Confirms the failure is state-propagated, not reasoning-level (§3). |
| **STALE_STATE_ERROR** | **not triggered; 0/6.** | Both cases presented newest facts explicitly, so the stale-vs-fresh conflict never arose. This metric was **not** tested. §10 assesses the mechanism structurally instead. |
| **UNNECESSARY_VALIDATION** | **not measured** (§8). | |
| **UNNECESSARY_ARTIFACT** | assessed observationally in §11: 2 of 12 Tenniskal artifacts redundant. | |
| **REORIENTATION_SUCCESS** | **6/6.** | Every variant preferred the newer independent orientation over the older stage status when both were present. |

The one that matters: **A false-blocked on 2 of 2, B and C on 0 of 2, and nobody
unsafe-unlocked.** That is the whole thesis of this retrospective in one row.

---

## 13. What is earning its cost, and what is not

### Provably earning its cost

- **PIT / leakage discipline.** Named by every lens arm unprompted; you report it worked in
  both real projects.
- **Identifiability refusal.** All 3 crypto runs correctly refused continuous MFE/MAE as
  non-identifiable *while* proposing the identifiable discrete-cadence alternative. This is
  the single best-behaved mechanism in the system: it blocks a claim without blocking
  thought — exactly the behavior the untyped `blocked` token fails to produce elsewhere.
- **Sealed-holdout / prospective discipline.** 6/6 preserved, including the leanest variant.
- **Authority boundaries.** 6/6. `AUTHORITY.md` is 147-202 tokens and its rules were
  honored even by C, which does not load that file.
- **Claim ceilings.** 6/6 refused to call development work qualification.
- **Negative-finding preservation** (TRACE). Cheap, and the thin-history n=48 finding is
  precisely the kind of result that gets re-discovered expensively if dropped.

### Not earning its cost

- **Untyped `blocked`.** Actively harmful — §3. Net negative, not merely wasteful.
- **Stale-first Allowed-context ordering.** Actively harmful — §10.
- **Role / profile / lens routing.** No detectable benefit (§6), and structurally broken
  (controller has no lens vocabulary; definitions never installed).
- **The ~4,300 tokens A carries over C.** Bought no quality and no safety (§4, §5, §12).
- **Duplicated 9-field quant packet** in both worker skill and TRACE contract.
- **Two of three Tenniskal residual panels.**
- **The `providers/` ↔ `src/ooda/resources/` duplication.** Pure maintenance cost, zero
  runtime benefit, unenforced (§2 claim 7).
- **Four dead `docs/` references.** Cost tokens; can send an agent hunting for absent files.

### Neither — write-only

**8,786-11,464 tokens** of doctrine that never reaches any runtime: `core/lenses`,
`core/roles`, `core/profiles`, `policies/CLAIM_LEVELS.md`, `policies/AUTHORITY.md`,
`contracts/WORK_ORDER.md`, `contracts/TRACE.md`, and the four referenced docs. The wider
`docs/` corpus is **28,836-37,191 tokens across 29 files, zero installed.**

**This is the direct answer to "is the documentation killing us?"** No — and not in the way
expected. The docs cost *nothing* in context because they never load. The real cost is that
the doctrine you wrote is not reaching your agents, while the hot path carries 5-6.6k tokens
that partly restate it from memory.

---

## 14. Provider separation

| Mechanism | Classification |
|---|---|
| OODA loop, blocker semantics, truth hierarchy, claim levels, authority, hard protections | **CORE** |
| Work-order / TRACE shape | **CORE** |
| `--rules` policy injection, `~/.grok/skills/` layout, `--no-subagents`, `--max-turns`, status-line hook, xAI cost telemetry | **GROK ADAPTER** |
| `agent_spawn` / `agent_wait` / `agent_result`, `deepseek-v4-flash` child vs `-pro` parent | **DEEPSEEK ADAPTER** |
| Repo-driven bootstrap, `CLAUDE.md` conventions | **CLAUDE ADAPTER — does not exist yet** |

Two things are currently mis-filed:

1. **`EFFICIENT_AGENT.md` context tiers (150k/175k/200k/250k) are in the always-loaded
   core policy but are provider-specific.** They assume a Grok-sized window and will
   mislead on any provider with different economics.
2. **There is no Claude adapter at all**, yet Claude is now doing consequential work
   (the Crypto mission). The observed Claude failure modes you list — arithmetic slips,
   the 31.5h/7.5h error, set-subtraction presentation, the lift tie bug — are exactly what a
   Claude adapter should target with an arithmetic/invariant self-check. Right now Claude
   runs with no OODA adapter and no `--rules` equivalent.

**Do not bake the Grok context tiers into core.** Move them to the Grok adapter.

---

## 15. Crypto broad mission — data-science review

Assessed from the facts you supplied. I did not have the actual output.

**Strong, and worth preserving as reference behavior:**
Admitted the remote-snapshot limitation instead of proceeding; did not fabricate C0/C1/C2;
corrected the 31.5h→7.5h error; reconciled the executable set; tested published-count
identity; preserved holdout and prospective; distinguished 7-populated / 6-unconfounded from
15-advertised; raised the target-conditioning concern; caught the tie-handling lift bug
(constant predictor reporting 2.0 instead of 1.0); used invariant testing; separated
continuous MFE from discrete cadence; invented no P&L.

That list is a **strong** scientific performance. The safeguards are working.

**Inefficiencies:**
- **The target should have been challenged before implementation, not after.** With
  median 0.9994 against a `>1` cut, the label is substantially noise-assigned. All five
  lens arms caught this from the quartiles in seconds. Building the pipeline first and
  surfacing the concern afterward is the ordering error — and it is a *sequencing* symptom
  again: the mission was "implement broad modeling", so the endpoint went unquestioned.
- **A full PR before real baselines had run was premature.** C0/C1/C2 could not execute in
  that environment; the PR is a proposal about untested code.
- **The remote environment was the wrong venue for a data-dependent mission.** This should
  have been caught at routing. Nothing in the hot path asks "does the execution environment
  have the data this mission needs?" — a one-line preflight would have prevented the whole
  wasted cycle. **This is a real gap and it is not addressed by any variant, including mine.**
- **Length and process reporting** exceeded what the next decision required.

**On your deeper question — is `multiple_1h > 1` the right first target?** On the evidence:
measurable, but likely not decision-useful. p25 0.9599 / p75 1.0003 means the cut sits inside
the noise band, and — the sharpest form of the point, raised by one lens arm — because
p75 > 1, the positive rate is **not** ~50%, so "beats 50% accuracy" may already be cleared
by a constant predictor. The right first move is a threshold sweep with the round-trip cost
floor `c` applied (`multiple_1h > 1 + c`), not a model. This is the pragmatic-data-science
verdict you asked for: **measurable but probably not decision-useful — which is not the
same as invalid.**

---

## 16. Tenniskal Phase 1 — data-science review

Assessed from the facts you supplied.

**Strong:** frozen reproducible Elo contract; prices excluded from Elo (the critical PIT
guard); 38,701-row replay; explicit "not independent OOS" warning; probability metrics
rather than accuracy; calibration reported; ATP/WTA slices; thin-history diagnosis;
exclusion reasons; no ROI claim. `B2_KEEP_REJECT = KEEP` is correct — logloss 0.693→0.642
and AUC 0.500→0.677 on the later split is a real improvement.

**Answers to your specific questions:**

- **Was B0=0.5 enough?** For a two-contract market, p=0.5 is the *structurally* correct
  null and defensible. But it is weak, and **empirical prevalence should also be shown** —
  cheap, and it guards against any residual favorite/underdog labeling asymmetry.
- **Is ECE sample/bin choice sensible?** Cannot verify without the bin spec. Flag: at
  n=417 with default 10 bins that is ~42 per bin, so ECE 0.066 has wide error bars. Report
  bin count and per-bin n, or use an adaptive-width estimator.
- **How much to rely on the internal "test"?** Not much. It is a temporal split of the same
  discovery substrate. It is the *right* thing to have computed and the *wrong* thing to
  qualify on. Treat as EVIDENCE, never QUALIFICATION.
- **Does thin-history n=48 warn meaningfully?** **Yes — and it is the most actionable
  finding in Phase 1.** logloss 0.711 vs B0's 0.693 means Elo is *worse than a coin flip*
  below 10 prior matches. That is an abstain rule, not a caveat. n=48 is small, so treat as
  a strong prior for an abstain band, confirmed prospectively — and **stratify, do not
  delete**, those rows. (One A/B/C run proposed dropping them and was correctly docked for
  selecting on observed outcome.)
- **Does the yes_ask-decile residual reveal useful structure?** **Yes — this is the next
  experiment.** See §11.
- **Is "F1 blocked because B1 missing" an artificial process gate?** **Partly — your
  framing A is right, B is the trap.** The named F1-vs-B1 test is genuinely undefined at
  n=0. But `blocked` untyped propagates as "feature work is blocked", which is false.
  Correct record: `blocker_type: data; blocked_for: evidence (B1 comparison only);
  exploration_allowed: yes`.
- **Does missing sportsbook B1 matter to the operator's next decision?** **No.** The
  operator trades against Kalshi, not against a sportsbook. The executable Kalshi price is
  the economically correct market baseline and is already joined. Sportsbook consensus was
  a proxy for exactly this, and the real thing is in hand.
- **Should next work be Elo-vs-Kalshi disagreement?** **Yes.** Two of three blind runs
  reached this independently. The sharpest framing came from a run that asked whether the
  signed Elo-vs-price disagreement exceeds the spread that must be crossed — which converts
  a research question into the P&L question.
- **Too much process state relative to scientific result?** Yes, mildly. Same pattern as
  Crypto.

---

## 17. Minimum viable OODA

Your candidate architecture survives the ablation, with two amendments.

```
USER / IO
   |
   v
FRESH OBSERVATION          <- ranked truth hierarchy; runtime/Git > prose
   |
   v
DECISION + VALUE + HIGHEST-VALUE UNKNOWN
   |
   v
   +--< low consequence? --> DO IT. verify. one-line record. STOP.     [amendment 1]
   |
   v
SMALLEST USEFUL MISSION    <- 7-field contract + plain-language challenges
   |
   v
WORKER                     <- environment preflight: is the data here? [amendment 2]
   |
   v
EVIDENCE
   |
   v
CLAIM / AUTHORITY CHECK    <- typed blockers; claim ceilings; hard protections
   |
   v
NEXT DECISION              <- chosen from evidence, never from stage numbering
```

**Amendment 1 — an explicit low-consequence short-circuit, taken *before* the OODA
scaffold.** This comes from a result against my own design. On the trivial-fix case:

| | tokens emitted |
|---|---|
| A (current) | **420-531** |
| C (lean) | 616-763 |

**A was leaner than C on the trivial task.** A recognized it explicitly — "Domain/value
preflight is not warranted; running it here would be ceremony" — and skipped straight to a
minimal work order. C ran its full OBSERVE/ORIENT/DECIDE/ACT plus durable record. So
**Failure Case 7 does not reproduce against current OODA**: today's doctrine handles the
trivial engineering task well, because its many "do not create ceremony" escapes do real
work. My lean rewrite made this *worse* by making the scaffold mandatory. The short-circuit
must be a branch taken before the loop, not a paragraph inside it.

(C did earn one thing here: it alone flagged that previously-recorded lift numbers may have
been computed through the buggy tie path and need recomputation — a real follow-up A missed.)

**Amendment 2 — an execution-environment preflight.** "Does the environment running this
mission have the data/host access the mission needs?" One line. Neither current OODA nor any
variant has it, and its absence cost the entire Crypto remote cycle (§15).

### Blocker model verdict

Your proposed 4-field model is **sufficient and not too bureaucratic** — B scored 27/28 for
+3.7% hot-path cost. Two refinements from the runs:

- `claim_ceiling` is nearly always derivable from `blocked_for`. **Consider dropping it**
  to 3 fields; the runs used it as a restatement.
- Add the explicit rule that carried the weight: **`blocker_type: sequencing` is never on
  its own sufficient to stop work.** This is the single sentence that addresses both
  documented failures.

The forcing question — *"is there a cheap, scientifically honest experiment available now
that does not violate the claim ceiling?"*, answered **in writing** before any BLOCK or
NO ACTION — is what converted A's two false blocks into zero. Keep it mandatory and written;
an optional version will be skipped exactly when it is most needed.

---

## 18. Disposition of every mechanism

| Mechanism | Verdict | Note |
|---|---|---|
| User intake | **KEEP** | cheap, works |
| Domain/value orientation | **SIMPLIFY** | 4 questions inline; drop the 34-line preflight to on-demand |
| Controller | **SIMPLIFY** | 3,750-4,911 → ~800-1,100 |
| Mission construction | **SIMPLIFY** | 17 fields → 7 + challenges (§7, untested) |
| Role | **SIMPLIFY** | keep as a one-word accountability label; drop the routing table to on-demand |
| Profile | **MERGE into role** | no separable benefit (§6) |
| Lenses | **MERGE into mission text** | replace names with the plain-language challenges that could invalidate the result |
| Claim level | **KEEP** | 4/4 correct; the ceiling concept is load-bearing |
| Worker bootstrap / context load | **SIMPLIFY** | apply the truth hierarchy |
| Worker execution | **KEEP** | |
| Tools / repo reading | **KEEP** | EFFICIENT_AGENT budgets are the best-written doctrine in the repo |
| Research artifact production | **KEEP** | |
| Visualization policy | **KEEP + one trigger** | add the threshold-target distribution plot (§11) |
| Independent validator | **KEEP, route by consequence** | rule exists in `AUTHORITY.md`; **install it** |
| TRACE | **SIMPLIFY** | minimal record + typed blocker (§9) |
| Handoff | **MERGE into TRACE** | |
| PROJECT_STATE | **SIMPLIFY** | static intent only; strip all mutable facts (§10) |
| Project view | **KEEP** | genuinely useful for "why did we change direction" |
| Control Room | **KEEP** | already correctly framed as derived |
| Documentation stewardship | **LOAD_ON_DEMAND** | currently dead reference |
| Next-mission selection | **KEEP + fix** | must be evidence-driven; typed blockers are the fix |
| Provider wrapper | **KEEP, re-scope** | move context tiers out of core (§14) |
| Telemetry | **KEEP** | the only thing that could ever produce the real rates in §12 |
| Session restart / rehydration | **SIMPLIFY** | truth hierarchy + minimal record |
| `providers/` ↔ `resources/` duplication | **REMOVE** | single source + build step, or enforce with `diff` |
| Four dead `docs/` references | **REMOVE or make reachable** | |
| Untyped `blocked` | **REMOVE** | replace with typed blocker |
| Stale-first context ordering | **REMOVE** | replace with truth hierarchy |

---

## 19. Expected reductions, risks, and what would change

**Expected hot-path reduction:** 5,064-6,609 → ~1,000-1,400 tokens (**~80%**), including
Amendment 1 and 2 which add back a little over bare C. Per controller invocation. Worker
skill (1,912-2,533) is expected to compress similarly but was not variant-tested.

**Expected complexity reduction:** 24 mechanisms → ~14 active, 4 on-demand, 6 removed
or merged. Two source-of-truth duplications eliminated.

### Risks of the lean design — stated honestly

1. **Ceremony escapes are load-bearing.** Demonstrated, not hypothetical: A beat C on the
   trivial task precisely because of its "do not create ceremony" escapes (§17).
   Amendment 1 addresses it; it is unverified.
2. **Untested on Grok.** All 13 runs were on this harness. A leaner prompt may underperform
   on a model that benefits from more explicit scaffolding. **Re-run A/B/C on Grok before
   adopting.**
3. **n is small.** 2 cases × 3 variants for A/B/C; 1 task × 5 arms for lenses; single
   evaluator. Directionally consistent (A last on both cases, independently) but not
   powered for small differences. The B-vs-C tie at 27/28 is **not** resolved by this data.
4. **Absence of evidence on validators.** §8 was not run. Do not lean out validation on the
   strength of this report.
5. **Compression can silently drop a protection.** Mitigation: 0/6 unsafe unlocks is
   encouraging but is 6 trials. Any lean adoption should ship with the hard-protection list
   as an explicit checklist, and Failure Cases 4/5/6 as regression tests.
6. **`docs/` and `core/` becoming reachable may change behavior in untested ways** — the L4
   result (definitions made it *worse*) is a live warning against assuming installation is
   automatically good.

### Exact minimum files that would change, if accepted

**Would change (7):**
```
providers/grok/skills/ooda-controller/SKILL.md    rewrite: thin router + typed blockers + truth hierarchy
providers/grok/skills/ooda/SKILL.md               same treatment; de-duplicate the quant packet
src/ooda/resources/grok/skills/... (both)         mirror, or eliminate via single-source build
src/ooda/resources/EFFICIENT_AGENT.md             move context tiers to Grok adapter
scripts/check.sh                                  add `diff` gate between the two copies
pyproject.toml                                    add reference/ files to package-data
contracts/TRACE.md                                minimal record + typed blocker fields
```

**Would be added (1 dir):**
```
providers/grok/skills/*/reference/*.md            project-view, domain-preflight, visualization,
                                                  quant-loop, doc-stewardship — on-demand
```

**Explicitly NOT changed:** `policies/AUTHORITY.md`, `policies/CLAIM_LEVELS.md` (both
correct as written — they need *installing*, not editing), all `docs/` content,
`examples/`, the CLI, telemetry, dashboards, Control Room.

---

## 20. SO WHAT / BIGGER IDEA / HUMAN GATE

**SO WHAT.** Current OODA is scientifically sound and structurally over-weight in one
specific, fixable way. Its safeguards held in 6/6 blind runs including the leanest variant —
you have not been buying safety with those 4,300 extra hot-path tokens. What you have been
buying is a false-block rate: current doctrine stopped where useful work was available in
2 of 2 blind cases, and produced the experiment's only fabricated number. Two changes carry
almost all the value: **type the blocker** and **rank runtime truth above prose**. Together
they are ~250 tokens and they address all three documented failures.

**BIGGER IDEA.** OODA's failure was not writing the wrong doctrine — the anti-sequencing
rule is stated four separate times in the controller. It was expressing the *right* doctrine
as **prose advice** while expressing the *wrong* doctrine as a **propagating data
structure**. `RESULT: blocked` is a durable, untyped token that the controller is instructed
to prioritize; four paragraphs of correct advice lose to it every cycle. The general lesson
for agent systems: **anything that must survive across sessions has to be a typed field, not
a sentence.** Prose is for the current turn; state is forever. That also explains why the
single-turn experiment could not reproduce the sequencing failure — given clean state, even
current doctrine gets it right. The bug lives in what persists.

The corollary is the write-only doctrine: 8,786-11,464 tokens defining lenses, roles, claim
levels, authority, and both contracts, none of it installed. The question "is the
documentation killing us?" has an inverted answer — **it costs nothing because it never
loads, and that is the problem.**

**HUMAN GATE — IO decision required. Nothing will be implemented until you rule.**

1. **Adopt B (semantics only, +3.7% cost) or C (lean, -84%)?** They tie at 27/28 and this
   experiment does not separate them. B is the low-risk minimal intervention; C additionally
   buys the token reduction and the truth hierarchy. My recommendation: **adopt B's
   semantics and C's truth hierarchy immediately (~250 tokens, addresses all three
   failures), and gate the full lean rewrite on a Grok re-run.**
2. **Approve a Grok re-run of A/B/C before any rewrite?** Risk 2 is unmitigated otherwise.
3. **Accept the role/profile/lens finding?** It is one task at n=1 and it contradicts a
   substantial design investment. Options: accept and merge lenses into mission text; or
   commission a wider ablation before deciding.
4. **Authorize the untested items** — work-order ablation (§7) and validator ablation (§8) —
   as a follow-up mission?
5. **Confirm the two amendments** (low-consequence short-circuit; environment preflight),
   both of which came from results against the lean design rather than for it.

**STOP.** No production OODA file has been modified. This report is the only artifact.
