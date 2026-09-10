# LDPS — gaps, guards, and abandoned work

**Assessed:** `ldps` `194ae57` · `tenniskal` `8b541e9` · `crypto-innout` `670c334` · `ooda` `0cc4303`

**Role:** researcher · **Profiles:** quantitative-research, ml-research, data-engineering · **Lenses:** scientific, model-risk, value-of-information · **Claim ceiling:** discovery · **Authority:** read-only on consumer repos; deliverables uncommitted in the `ooda` tree.

Derived findings only; paths at directory level. Machine-readable: `ldps_gaps_and_abandoned.json`. n=1, discovery ceiling.

## Two supersessions, stated first

**1. `LDPS_LIFECYCLE_ARCHAEOLOGY.md` said "there is no negative-findings register, and the reason must be inferred by reading each module." Half wrong.** A register exists at the doc layer: a 535-line experimentation narrative whose stated purpose is *understanding why prior catalogs were invalid*, which names an archived hypothesis catalog, its destination, its size, and the reason it was invalidated (built on corrupted in-sample data). There is also a decision log and 84 distinct `T-<TAG>` decision IDs across the docs. The per-file half of my claim stands — see Part D.

**2. `LDPS_PRACTICE_CORPUS.md` called `ldps_parser_path`'s missing `external/` path "the third such dangling reference found in this program." Wrong.** `external/` is **deliberately gitignored with a written reason**: a vendored third-party tool with its own git repo and a 76 MB dataset, to be managed upstream rather than vendored. That is documented exclusion, not drift, and it does not belong with the other cases. This matters for the cross-cutting question below, where I had been counting it.

---

# C1 — why calibration is disconnected from the daily path

**It is lane-partitioned, not disconnected.** ldps has two subsystems with different discipline, and the answer differs by lane.

**Kalshi lane — deliberate and documented.** All six calibration modules live here, plus Platt scaling in four files and Brier in nineteen. The live card carries an explicit comment setting *calibration policy to "none" for now*, with a stated precondition — no calibration-report history exists yet to fit on — and a pointer to the named policy module that would do it. This is not forgotten and not half-wired. It is a deferral with the reason written at the call site, and it is the only live path in the repo that references calibration or the honesty guards at all.

**MLB lane — no evidence either way.** This lane carries six of the eight live paths, and **all six reference calibration zero times**. There are no calibration modules, no Platt, no isotonic. I looked for evidence the disconnect was deliberate — an evaluation that rejected it, a partial wiring, a commented-out call — and found none. There is also no evidence it was forgotten. **Absence of evidence; I am not inventing a decision that left no trace.**

**Was the live probability checked by another route? Partly, yes — and this narrows the exposure.** Brier *is* computed in the MLB lane at development time: a walk-forward module uses sklearn's `brier_score_loss`, and two research modules compute model Brier against **baseline Brier** — a skill score against the de-vigged market. So the probabilities feeding the daily runners were checked for *discrimination and skill against the market* before promotion.

What is absent is narrower but still real: **no reliability curve on the live probability, and no calibration transform applied before position sizing.** A model can beat the market on Brier while being systematically over-confident, and fractional-Kelly sizing scales with the probability, not with the skill score. That specific exposure stands. It is a gap in the reliability dimension only, not the blanket "uncalibrated p" the mission framed — the corpus checks more than it appeared to.

One incidental finding while tracing the runner: it sets its project root to a **hardcoded absolute path on one machine**.

# C2 — have the honesty guards silently stopped firing?

They still fire where they are called. The finding is *where they are not called*.

| Directory | Modules | Import the guards |
|---|---|---|
| `data/mlb/eda` | 85 | 20 |
| `data/mlb/eda/atlas` | 10 | 6 |
| `data/mlb/eda/selector` | 4 | **0** |
| `data/mlb/modeling` (all subtrees) | 116 | **0** |
| `data/mlb/pipeline` | 9 | 0 |
| `data/mlb/ingestion` | 12 | 0 |
| `data/kalshi` | 42 | 1 |

**The guard boundary stops at the discovery layer.** The selector, the entire 116-module modeling tree, the market factory, the trend engine and every live card sit outside it. A code path did grow around the guards — it is the whole production half of the system.

**The guards' own stated invariant is false in this tree.** The placebo module declares itself *the ONLY place shuffling is allowed*. A placebo threshold function is independently reimplemented **four times** outside it — twice in the Kalshi lane, twice in the MLB modeling-research tree — each with its own hardcoded seed (7, 11, 17, 18).

**In fairness, these are not sloppy copies.** The guard permutes the *outcome label within a season*, to preserve each season's base rate. The four reimplementations permute the *feature within a date block*. That is a different scheme, defensible and arguably stricter at a daily-slate grain. The cost is not a wrong method: it is four untested implementations of the system's most important control, no shared definition of what the noise floor means, and a documented invariant that no longer holds.

**The failure mode is not hypothetical here.** The docs record an incident in which an input feed was archived and **silently stale for roughly three months at 0% coverage** before an audit caught it and re-wired it. That is the exact shape of the risk the question asks about — a control or feed that stops firing without saying so — realised once, on a feed rather than a guard, and caught by manual audit rather than by any automated check.

# The general sweep

Judged against what the corpus shows this operator actually cares about — leakage prevention, market-relative edge, honest evaluation — four things were never built:

1. **Any automated test on the guards.** Zero `pytest`/`unittest` imports across 317 modules. The controls that make the research honest have no mechanical protection.
2. **A freshness or coverage assertion on inputs.** Cost is evidenced: the three-month silent staleness above.
3. **A reliability check in the lane carrying most live paths** (C1).
4. **A single shared definition of the noise floor** (C2) — five now exist.

# Part D — the abandoned work

**Archived in place: 26 modules, 13,447 lines**, in five clusters — exploratory analysis (14 files / 9,084 lines), pipeline (6 / 1,902), an early application layer (3 / 1,455), ingestion (2 / 833), notebooks (1 / 173). What was tried is legible from the modules themselves: alternative grid and combination searches, a counterfactual bankroll, an alternative de-vig/consensus benchmark, early rule-discovery and settlement paths.

**Deleted: 4 files** — two terminal/command scratch files and two generated report directories, all in categories the `.gitignore` already excludes. Nothing of research substance was deleted.

**Can a future reader learn why?** **At cluster level, yes. At file level, no.**

Only **1 of 26** archived modules carries an archival reason in its header; the other 25 retain their original purpose docstring with no verdict, so a reader opening one cannot tell whether it was superseded, invalidated, or merely paused. The commit messages touching archive paths are `updates` and `system explore`.

But the doc layer carries the verdicts the files lack: the experimentation narrative states that a 133-system catalog was archived *because it was built on corrupted in-sample data*, and a doc registry marks superseded documents with status glyphs, replacement modules, and dated decision tags. So the negative result was **not lost** — it was recorded one level up from where a reader browsing the code would look.

# The cross-cutting question — committed artifacts citing what was never persisted

Correcting my own count first: **one of the four candidate cases does not belong.** `ldps`'s `external/` is deliberately excluded with a written justification. That leaves crypto-innout's three `cio-` traces and tenniskal's orphan `work_order_id` as genuine.

Sweeping ldps for further instances, with deliberate exclusions filtered out:

- **Doc references:** 118 distinct unresolvable path-like references. 55 are explained by `.gitignore` (generated artifacts). Of the remaining 63, resolving relative paths and renames leaves **19 truly dangling** — 9 modules, 7 documents, 3 data files. Roughly 1.3% of path references in the docs.
- **Absolute paths:** **105 of 376 files (28%)** hardcode one machine's filesystem path, 148 occurrences. Not a missing artifact, but the same class of defect: a committed reference that resolves nowhere but the author's laptop.
- **One new instance, and it is the sharpest in the study.** The `.gitignore` carries a carefully reasoned exception exempting forward ledgers from the CSV rule, because *committing them gives git-timestamped, tamper-evident proof that picks preceded outcomes*. **Zero ledger files are committed.** The mechanism built specifically to prove ex-ante commitment was configured, justified in writing, and never used — the same operator, the same failure mode that Phase 1 found in tenniskal's empty work-order→trace interval and Phase 3B found when ex-ante commitment stopped once modelling began. Third repository, third instance, and here the machinery existed.

**The pattern.** Strip the deliberate exclusion and what remains is one property, shared across three repositories and both adoption states: **a committed artifact names something, and nothing checks that the name resolves.** The `.gitignore` proves the operator already distinguishes deliberate absence from accidental absence, and writes the distinction down. No tool in any of the three repositories reads that distinction, so both kinds of absence look identical to every reader and every process downstream.
