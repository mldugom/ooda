# LDPS Lifecycle Archaeology — how one prediction system actually got built

> **Partly superseded.** `LDPS_PRACTICE_CORPUS.md` corrects two conclusions below from a structural reading of the code: the baseline count (§ *Stages that never appeared*) and the calibration timing (§ *Where the sequence doubled back*). The original findings are left as written.

| Repo | SHA | Depth |
|---|---|---|
| `ooda` | `0cc4303` (`0cc43037e21f8c073a7ae7fecab86eb66fa6b292`, origin/main) | full |
| `ldps` | `194ae57` (`194ae57cc5110bd9b6ee5329a9aff40ef6dcef57`) | **full** — see precondition |
| `tenniskal` | `8b541e9` (`8b541e93830e04e4ecea4cfb29c9fed6d2d2c05e`) | full, lineage only |
| `crypto-innout` | `670c334` (`670c33403783847ddb2bdffce34211a7822e458b`) | full, lineage only |

**Role:** researcher · **Profiles:** quantitative-research, ml-research, data-engineering · **Lenses:** scientific, model-risk, value-of-information · **Claim ceiling:** discovery · **Authority:** read-only on consumer repos; deliverables written uncommitted to the `ooda` tree.

**Precondition — satisfied.** A bounded `fetch --depth=1000` exceeded the repository's total history, so the clone is **fully unshallowed**: no `.git/shallow`, one root commit, 116 commits spanning **2026-04-18 → 2026-07-27**. History is complete, not truncated; archaeology proceeds.

**Scoping.** Derived findings only, paths at directory level; no filenames, hypothesis names, factor names, objectives or findings text. Market families are named only as standard public bet types, since target drift cannot be answered otherwise.

Extractor: `scripts/ldps_lifecycle_archaeology.py`. Tables: `ldps_stage_timeline.csv`, `ldps_archaeology.json`.

---

## Question 0 — lineage: sibling by code, ancestor by lesson

`ldps` and `tenniskal` share **zero commits** and **zero byte-identical blobs**; the only common paths are `.gitignore` and `README.md`, and roots are independent (`a5a6e067` vs `4e1801a4`). `ldps` is not a git ancestor of `tenniskal`.

Domains differ: `ldps` is an **MLB** system (283 of 328 data files under an MLB tree) trading on **Kalshi**; `tenniskal` is tennis on Kalshi. The 798 "tennis" strings in `ldps` sit inside one raw Kalshi market snapshot — incidental venue data, not a modelled sport.

The lineage is real and one-way. `tenniskal` references `ldps` in **22 files, from its very first commit** (2026-09-06), as named carried-forward lessons — tokens of the form `ldps_<lesson>` in its `src/`, `research/` and `.ooda/` trees. `ldps` never references `tenniskal`. Chronology agrees: `ldps` ends 2026-07-27, `tenniskal` begins six weeks later.

**Framing consequence.** This is archaeology of an earlier stage of the same operator's program, not an independent second corpus. No comparative claim beyond plain observation follows.

## Method and the measurement hazard

Stage membership is assigned by ordered path rules (first match wins); where a stage's only matches were claimed by an earlier rule the extractor reports it **SHADOWED** rather than asserting absence. Two stages hit this, both reported below.

The dominant hazard is bulk import. Three commits added **182 of 376 files (48%)** at once: `345d9ec` (116 files, 07-03), `bb5cd1c` (41, 07-12), `194ae57` (25, 07-27). Files inside such a commit share one date and carry **no order relative to each other**.

## Reconstruction: first appearance by stage

| Stage | First seen | Resolved? | Files |
|---|---|---|---|
| docs | 2026-04-18 | yes (initial commit) | 33 |
| backtesting, features, models, validation, eval-metric, ingestion, decision-surface, portfolio/staking, config, notebooks | 2026-07-03 | **no — all in `345d9ec`** | 11 stages |
| monitoring | 2026-07-09 | yes (`582e359`, cohort 14) | 5 |
| calibration | 2026-07-27 | no (`194ae57`, cohort 25) | 6 |

**The headline result is negative: git cannot establish the build order of `ldps`.** Eleven of fourteen stages first appear in one commit; only three are separately dated, one being the initial README. Any claim that this system was built "data → features → model → validation" would be invention.

Recoverable instead is the order of work **after** the 07-03 import, where ~194 files arrived incrementally. One sub-sequence there is finely ordered: an exploratory "atlas" phase ran 07-07 18:09 → 07-08 16:53, commits roughly every 20 minutes, moving through price-band and context diagnostics, then a selector layer, then the first modelling tree. That segment is genuine build-order evidence.

**Stages that never appeared.** No stage is truly absent, but two are vestigial:

- **baselines** — exactly **one** file in 376 carries `baseline` in its name, added in the repository's **final commit** (07-27), and it is a portfolio-audit freeze, not a predictive baseline. The word appears as content in 68 files, so the idea existed; as a durable named artifact the stage is absent for the repository's whole life.
- **target definition** — only **two** filename matches ever, both settlement scripts, **both now in `archive/`**. No target-definition artifact exists at HEAD.

## Where the sequence doubled back

- **Calibration came last** (07-27, the final day). Live decision surfaces appeared 07-17 and monitoring/daily runners 07-09 — operator-facing surfaces and scheduled runners existed **8 to 18 days before any calibration code**.
- **The baseline was frozen on the last day**, after every model family was built and scored.
- **A metric layer was re-cut wholesale.** Seven re-scoring modules landed on 07-07 with a global scorer, against a scoring module already in the 07-03 import — results existed before that scoring generation did.
- **The backtesting document post-dates backtesting code** by two days (doc 07-05; code inside the 07-03 import).
- **Retro-numbering.** In the atlas phase an artifact numbered `D0c` was committed *third*, after `D1` and `D2` — the numbering asserts a sequence the commits contradict.
- **Point-in-time semantics** first appear inside the 07-03 import, so whether PIT settled before or after feature work is unresolvable.

## Rework concentration

| | Top module | Commits |
|---|---|---|
| Naive | a project state file, then two docs trees | 14, 13, 8 |
| Corrected (designed churn removed) | `data/mlb/eda/` | 12 |

Naive ranking finds only state and status documents. After removing them the most-rewritten module is the **exploratory analysis tree** (12 commits), then two ingestion modules (7 each). Rework concentrated in exploration and data intake, not modelling or evaluation.

## Approaches abandoned

31 files were abandoned: **27 archived in place**, 4 deleted. By stage: features 7, models 7, ingestion 6, portfolio/staking 3, validation 2, other 6, across five `archive/` directories.

Version suffixes tell the same story: **96 modules carry `_v1`**, plus `_v1_1` (9), `_v52` (7), `_v5` (6) and a tail through `_v6`. At least five generations of one catalog family coexist at HEAD.

**Negative results were preserved as code, not as findings.** Archiving rather than deleting keeps *what* was dropped readable. Nothing records *why*: there is no negative-findings register and the archived files carry no verdict, so the reason must be inferred by reading each module.

## Composition (non-data files at HEAD)

| Class | Files | Lines | Share |
|---|---|---|---|
| Modeling | 210 | 108,150 | **65.4%** |
| Scaffolding | 93 | 33,001 | 20.0% |
| Evaluation | 60 | 24,224 | 14.6% |

The entire codebase lives *under* `data/`: there is no `src/` tree and no test directory anywhere in the repository.

## Question 1 — ex-ante commitment

Ex-ante commitment happened, in two cases, and failed in three.

**Held.** A process document was committed 07-06, two days before the modelling tree appeared (07-08 06:41); a validation harness 07-07 20:51, ten hours before it. Both strictly precede the work they govern.

**Failed.** A formal selector specification was committed in the **same commit** as the D12–D16 work it specifies (`582e359`, 07-09 23:06). The baseline freeze arrived in the final commit. The backtesting document trailed its code by two days.

So: twice, early, and not once modelling was underway. Both instances predate the first modelling directory; after 07-08 every candidate governing artifact is co-committed with its work or retroactive.

## Question 2 — charter retro-test

**(a) Could a charter written at the start have described what `ldps` built?** No. Of the frozen fields, `decision_time`, `primary_metrics`, `stop_rule` and `resource_budget` have **zero occurrences** anywhere in the repository, and the target moved across at least five market families in nine days: away-win (07-03), total/margin (07-08), away run-line (07-09), home moneyline (07-10), home run-line and a market-trend family (07-12). A charter frozen 07-03 would describe about the first two days of a hundred-day repository.

**(b) Where would the fingerprint have drifted?** At minimum four target changes (07-08, 07-09, 07-10, 07-12), one metric re-cut (07-07) and one baseline definition (07-27) — six events, five inside one week. `holdout` semantics also shift, season-indexed and leave-one-season-out schemes appearing at different dates.

**(c) Real catch, or false alarm?** Both, and the split is legible. The 07-07 metric re-cut and the 07-27 baseline are what the mechanism exists to catch: success redefined after results existed, comparator fixed last. The 07-08→07-12 target moves are harder to call violations — they read as a system-factory program deliberately sweeping market families, where changing target *is* the method, and a frozen `target` would fire on every sweep step. On this history the charter yields roughly **two true positives and four alarms against intended exploration**, suggesting the mechanism discriminates by *which* frozen field moves, not by whether the fingerprint changed. n=1, discovery-level, not a validated property.

## What this data cannot answer

- **Build order for 11 of 14 stages.** Needs commits contemporaneous with the work; a 116-file import erases order permanently.
- **Why anything was abandoned.** Needs a negative-findings register, or a verdict field on archived modules.
- **Whether the target sweep was planned or reactive.** Would need the target recorded before each sweep step — what a charter supplies, which is why (c) cannot be settled from this corpus alone.
- **Whether work preceded its commit.** All 116 commits carry agreeing author and committer timestamps, so no rebase distortion is present — but nothing dates work done before a bulk import.
