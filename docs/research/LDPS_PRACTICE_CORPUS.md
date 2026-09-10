# LDPS as a Practice Corpus — carried-forward lessons and pipeline anatomy

| Repo | SHA |
|---|---|
| `ldps` | `194ae57cc5110bd9b6ee5329a9aff40ef6dcef57` (`194ae57`) |
| `tenniskal` | `8b541e93830e04e4ecea4cfb29c9fed6d2d2c05e` (`8b541e9`) |
| `ooda` | `0cc43037e21f8c073a7ae7fecab86eb66fa6b292` (`0cc4303`, origin/main) |

**Role:** researcher · **Profiles:** quantitative-research, ml-research, data-engineering · **Lenses:** scientific, model-risk, value-of-information · **Claim ceiling:** discovery · **Authority:** read-only on consumer repos; deliverables uncommitted in the `ooda` tree.

**Scope note.** Parts C and D were descoped by the operator mid-mission; this covers Parts A and B only. Structural reading only — no chronology claims beyond `LDPS_LIFECYCLE_ARCHAEOLOGY.md`, with one correction to it noted in Part B. Derived findings only: paths at directory level, no hypotheses, findings text or strategy detail. Machine-readable inventory: `ldps_practice_corpus.json`.

---

# Part A — the carried-forward lessons

## A correction to the premise

The mission states that tenniskal references ldps "in 22 files via `ldps_<lesson>` tokens." The 22-file count is right; the mechanism is not. There are **exactly five** distinct `ldps_*` tokens. The other references are prose, concentrated in `AGENTS.md`, `README.md` and four `research/` documents. So the retrospective is mostly narrative, with five points hardened into identifiers — and, as it turns out, the hardening is where the signal is.

## The five tokens

| Token | Where | Kind | Lesson (one line) |
|---|---|---|---|
| `ldps_sbr_lesson` | `src/`, `tests/` | METHOD | The prior system's data source is a *schema lesson*, not a usable source for the new sport — registered as a non-source so it cannot be mistaken for one. |
| `ldps_principles` | `.ooda/work-orders/`, `research/` | INFRASTRUCTURE | Seven ingestion invariants are worth porting even when no code is. |
| `ldps_source_truth` | `.ooda/traces/` | INFRASTRUCTURE | Record what a source *actually is* at the interface level; the assumed integration and the real one differed. |
| `ldps_parser_path` | `.ooda/traces/` | INFRASTRUCTURE | A reuse assessment concluded a materially new component was needed, not a narrow extension. |
| `ldps_wholesale` | `.ooda/work-orders/` | METHOD | "Do not copy wholesale" as a machine-checkable mission field (`copy_ldps_wholesale: false`), not advice. |

## Themes

**1. Source truth (`ldps_sbr_lesson`, `ldps_source_truth`).** Both lessons are about the same failure: believing a source is what its name or its field labels claim. The sharpest artifact in the whole corpus sits here. tenniskal's source registry carries the prior system's source as a **first-class row with `role: schema_lesson_not_a_tennis_source`** and `timestamp_quality: label_without_observation_time` — a negative result promoted to a structural entry, so the only way to reach for it is to read why you must not. The companion rule, recorded in a prereg table as *a field name is not an observation time*, is the general form.

**2. Ingestion integrity (`ldps_principles`).** Seven named invariants ported without code: raw page preservation, immutable snapshots, content hashing, normalized identity, fail-loud coverage, never silently shrink the universe, derive open-to-close from stored quotes. Five of the seven are about *provenance under later doubt* rather than correctness now.

**3. Reuse governance (`ldps_wholesale`, plus the dominant prose line).** "Reference implementation, not a dependency to copy wholesale" appears in `AGENTS.md`, `README.md`, a research doc, and as a boolean mission field. It is the most-repeated lesson in the corpus and is present in tenniskal's **first commit**.

**4. Reuse assessment as a preserved negative (`ldps_parser_path`).** A trace records that the prior parser could not be narrowly extended, and why. This is the one place a negative reuse result was written down where a future reader will find it.

## Sequencing / method / infrastructure

Sorted as the mission asks: **three INFRASTRUCTURE, two METHOD, zero SEQUENCING.**

That absence is the finding. Not one of the five hardened lessons says *do X before Y*. tenniskal's `AGENTS.md` does contain sequencing rules — prefer small end-to-end slices over platform building; pre-register hypotheses before outcome/P&L optimization; do not begin the next stage until the current one is authorized — and they read as direct responses to what ldps's anatomy shows (Part B: a large platform, 65% modeling, no target artifact, no tests). But they sit in a general rules list and are **not attributed to ldps**. Reading them as ldps lessons would be inference, so it is flagged as inference here and not counted.

The lessons that survived as identifiers are the ones about *data you can be deceived by*. The lessons about *order of work* either were not learned as transferable, or were learned and not written down as such.

## One structural failure in the chain

`ldps_parser_path` names an absolute path under an `external/` directory that **does not exist in the committed ldps repository**. The reuse assessment was performed against a working copy containing files never committed. The same path is required by ldps's own pipeline orchestrator (Part B). This is the third instance in this program of a durable artifact citing something that was never persisted.

---

# Part B — pipeline anatomy

Read from code, not history. Stage-by-stage in `ldps_practice_corpus.json`.

**Flow.** A single orchestrator (`data/mlb/`) runs three phases — fetch, build, model. Fetch normalizes odds and refreshes schedule/results/stats via `ingestion/` (12 modules); build computes feature tables in `pipeline/` (9 modules) into a master dataset; model runs a hypothesis engine over that dataset and rebuilds a dashboard. Downstream, `modeling/` (27 modules plus a 24-module market factory) turns surviving candidates into scored systems, and a daily runner produces a paper card.

**Generation.** The engine evaluates a catalog of ~80 hypotheses against the master dataset, reporting n, win rate, market-implied probability, edge, ROI and P&L, with bootstrap CIs, t-stats and a walk-forward fold consistency score. Model families are narrow: ridge and ridge-logit dominate, with logistic regression, decision-tree/rule search and some clustering. **sklearn is imported in 13 of 317 modules.** This is a rule-and-factor search system, not a machine-learning system.

**Baseline — present, but unnamed.** The prior report found one baseline-named file, added last. Structurally that understates it: the **de-vigged market price is the comparator everywhere**, appearing 2,738 times across 96 modules, and edge is defined against it throughout. ldps did measure against something — the hardest available benchmark — it just never made "baseline" an artifact. Closing-line value, by contrast, appears only five times.

**Evaluation is the strongest part of the system, and the 15%-of-lines figure undersells it.** A small `honesty/` package holds three load-bearing controls: a **split guard** (current season sealed, expanding walk-forward, with an `assert_unsealed()` that raises so sealed data cannot reach discovery by accident); a **placebo noise floor** (permutes only the outcome label, only within the discovery window, within-season to preserve base rates, and returns a threshold rather than a P&L so it cannot be mistaken for a result); and a **single fixed evaluator** through which every generator's bets pass, producing net-of-vig ROI, the placebo p95 floor, leave-one-season-out consistency and a ledger entry. One backtest module openly declares its own look-ahead caveat in its docstring. This is real model-risk discipline, deliberately built.

**Calibration — a correction.** `LDPS_LIFECYCLE_ARCHAEOLOGY.md` reported calibration first appearing on the final day. Structurally, the calibration *module* is a refactor: its docstring states the body was cut unmodified from a movement-research harness added five days earlier. Calibration math therefore predates the calibration-named file, though still by days, not months. Brier score, an offset-logistic reliability fit and bucketed reliability live in that module; Platt scaling appears separately. It is the one stage that is **not load-bearing** — nothing in the daily path calls it.

**Market machinery is the most developed layer.** Settlement/resolution handling touches 275 modules, edge computation 207, bankroll 75, Kelly 66, fees 43. Position sizing is fractional-Kelly, and the four stake-aggregation modes for combining multiple systems on the same game are compared explicitly rather than assumed. The live path trains on completed prior seasons, scores current-season out-of-sample rows, and builds a live slate — paper only.

**Testing.** **Zero `pytest` or `unittest` imports across 317 modules.** No `tests/` directory and no `src/` tree — the entire codebase sits under `data/`. Of eight files matching test-like names, six are statistical tests or backtests; one is a one-line connectivity print; exactly one is a genuine correctness check, a parity harness proving a streaming refactor reproduced the previous path's output before it was trusted.

**So: does each stage exist, is it load-bearing, is it tested?** Fourteen of fifteen stages exist; the exception is target definition, which has no artifact at HEAD. Twelve are load-bearing. **None is covered by an automated test.** The verification that does exist is statistical — split guards, noise floors, LOSO, parity checks — not mechanical. In a system whose failure mode is leakage rather than exceptions, that is a defensible allocation, and the corpus makes the choice legible rather than accidental.
