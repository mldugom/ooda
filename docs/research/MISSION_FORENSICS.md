# Mission Forensics — tenniskal mission timeline reconstructed from git

| Repo | SHA | Role in this study |
|---|---|---|
| `ooda` | `0cc43037e21f8c073a7ae7fecab86eb66fa6b292` (`0cc4303`, origin/main) | framework under assessment |
| `tenniskal` | `8b541e93830e04e4ecea4cfb29c9fed6d2d2c05e` (`8b541e9`) | 22 work orders / 23 traces |
| `crypto-innout` | `670c33403783847ddb2bdffce34211a7822e458b` (`670c334`) | non-adopter case |

**Profiles:** data-engineering, quantitative-research · **Lenses:** value-of-information, reliability-systems, statistical · **Claim ceiling:** discovery · **Authority:** read-only, default-deny. No repository was modified.

**Cost is UNAVAILABLE.** No telemetry ledger exists in either repo and no trace carries `cost_usd`. Nothing below is a cost estimate, and none is inferred from elapsed time or diff size. Stated once; not revisited.

Derived table: `mission_timeline.csv` (22 rows); aggregates `mission_forensics.json`; extractor `scripts/mission_forensics.py`. Objectives, verification text and findings are never read or emitted; paths are aggregated to top-level directory.

## 1. What git can and cannot establish

Work orders carry a date-only `created`; traces carry no completion field. Git commit metadata is the only timeline, and it records **when an artifact entered version control**, not when work happened. Committer and author timestamps agree on all 22 missions, so no rebase distortion is present.

## 2. Ordering: the work-order → trace interval is empty

| Relationship | Missions |
|---|---|
| Work order and trace introduced by the **same commit** | 20 / 22 |
| Trace committed **before** its work order | 2 / 22 (−0.29 h, −0.63 h) |
| Trace committed after its work order | 0 / 22 |

Elapsed time is 0.0 h for 20 missions and negative for two. Contract and outcome enter the repository atomically, so git **cannot distinguish a pre-committed contract from one written alongside its result**: the versioned record carries no evidence that any work order preceded its own execution. Two missions show the reverse order explicitly — the trace arrived with the feature commit, the work order was backfilled 17–38 minutes later.

This voids the requested elapsed-time and between-artifact scope measures as specified. Scope below is measured on the commit that *introduces* each mission — a different and weaker quantity.

## 3. Batching

22 missions entered via **17 distinct commits** over 45.7 hours (2026-09-08T03:25Z → 2026-09-10T01:05Z). One commit (`b4443a3`) introduced 6 work orders and 5 traces at once — a bulk backfill covering missions 1–6, which therefore share one indivisible footprint. The other 16 commits each introduced exactly one pair.

## 4. Mission scope (introducing-commit footprint, `.ooda/` excluded)

| Measure | min | median | max |
|---|---|---|---|
| Files changed | 1 | 3 | 23 |
| Insertions | 5 | 219 | 8,289 |
| Gap to previous mission (h) | 0.0 | 0.48 | 19.8 |

n=22 in one repository over two days; observed range, not an estimate. The 8,289-insertion and 23-file mission are the same one (a data-source spike); missions 1–6 all report the shared backfill footprint of 7 files / 1,220 insertions.

## 5. Rework is confined to state documents

Files touched inside the ranges of two or more missions whose work orders were committed within 72 hours, counting only pairs from **different** commits:

| File class | Missions | Distinct commits |
|---|---|---|
| `PROJECT_STATE.md` | 22 | 17 |
| research state document (`.md`) | 16 | 11 |
| research artifact | 2 | 2 |
| research artifact | 2 | 2 |

Four files total. The two heavily-touched ones are the durable state documents the doctrine requires each mission to update, so their churn is designed behaviour. Substantive research artifacts revisited by a later mission: **two files, one pair each** — very little thrash, though with the work-order→trace interval empty this measures co-commit overlap, not genuine revision.

## 6. Sequence is a consistent protocol, not ad hoc

Mission IDs resolve into families that repeat one cycle:

```
prereg → validate → correct → revalidate
```

It appears twice in full — fair-value (11–15) and P(win) (18–21) — and partially for R7 (7–9). Corrections are small (5–246 insertions), consistent with validation catching narrow defects cheaply. Eight of 22 missions are validation or correction steps, and validators carry `role: validator`, distinct from the mission they check. The progression is repeated and directional, not opportunistic.

## 7. The orphan (23 traces, 22 work orders)

`tk-r7-prereg-amend-validate-2026-09-08` is a trace whose `work_order_id` names a work order that **never existed in any commit on any branch**. It is a `validator`-role, 3-lens, `claim_level: n-a` trace recording independent validation of the R7 prereg amendment, committed 1m47s after the amendment's own pair.

An independent validation ran and was recorded with no contract governing it. `validate_trace` requires `work_order_id` to be non-empty but never checks that it resolves, so `ooda doctor` passes the file. The corpus's one broken reference sits on exactly the step the authority policy relies on for independence.

## 8. The three-lens quota was present from the first mission

Lens counts in commit order: missions 1–21 use exactly 3; mission 22 uses 0. There is **no gradual emergence** — the first mission committed already spends the full budget, and the count never varies until it drops to zero at the end. Four distinct lenses appear; nine of thirteen are never selected. Whether this constant is judgment repeated 21 times or a template copied forward cannot be settled from artifact content alone.

## 9. What this data cannot answer

- **Whether any work order preceded its execution.** Needs the work order committed, or signed-timestamped, *before* the worker starts. Nothing less separates contract from post-hoc record.
- **Real duration, cost, or turns.** Needs a trace completion timestamp and a session ledger. Both absent.
- **Whether rework was avoided or merely uncommitted.** Revisions squashed before commit are invisible.
- **Whether 3 lenses reflect deliberation.** Needs the routing decision recorded separately from the mission it produces.

## 10. crypto-innout: drift, not decision

crypto-innout was **never `ooda init`-ed** — `.ooda/project.json` has never existed in any commit. Across 116 commits in 4.6 days, exactly one commit ever touched `.ooda/`, and no commit message anywhere mentions OODA. The string `ooda` has never appeared in `AGENTS.md` in any revision; that file documents a different operating model (Human + ChatGPT Integration Owner → interactive Grok Build) with no OODA reference. The single trace that landed (`ci-pit-panel-slice0-impl`) arrived as one of 8 files inside a 1,931-line feature commit — swept in with an implementation, not committed as a deliberate OODA step. `.ooda/` is not gitignored in either repo, so nothing mechanical prevented these files from being tracked.

The decisive evidence is dangling references. Two committed research documents cite three parent traces — `cio-program-reorient-2026-09-07`, `cio-pit-panel-reuse-2026-09-07`, `cio-pit-panel-contract-2026-09-08` — and **all three have zero adding commits on any branch**. Durable research artifacts in this repository were written *as though* an OODA orientation chain existed and was citable; the artifacts in that chain were produced somewhere and never persisted. Note also the prefix split: every cited trace uses `cio-`, while the one trace that survives uses `ci-`. So OODA was reached for here, repeatedly, and left no durable record — the failure is a missing persistence step at the end of the loop, not a judgement that the framework was not worth using. That is drift, and it is the opposite diagnosis from non-adoption by decision. This is a single-repository observation at discovery ceiling; confirming it needs the sessions that produced the `cio-` traces, which are outside git.
