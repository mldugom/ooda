# OODA

## Product purpose

OODA exists to help a human and frontier coding/research agents build useful prediction systems faster and more honestly.

The default use case is end-to-end quantitative work: data ingestion, point-in-time dataset construction, baselines, model development, held-out evaluation, economic decision rules, position sizing where relevant, production execution, and monitoring for data/model degradation.

OODA is not a project-management framework and not an organizational chart for agents. It should reduce the amount of framework the operator has to think about.

The product test is simple:

> Does this help us answer an economically meaningful modeling question faster, while preventing mistakes that would make the answer untrustworthy?

If a feature does neither, it does not belong on the ordinary path.

## Product shape

OODA should stay small:

1. **Deterministic Python kernel** — authority, evidence integrity, execution locality, validation, and consequence boundaries.
2. **Thin CLI** — the normal human interface.
3. **Frontier-agent runner** — launch or resume bounded work in the right repository and environment.
4. **Read-only dashboard** — business/data-science status, derived from project evidence.
5. **Prediction-systems knowledge** — concise references loaded only when they change a scientific or engineering decision.

The preferred everyday interface is intentionally small:

```text
ooda next       # what is the highest-value unresolved question?
ooda run        # execute one bounded experiment or engineering task
ooda continue   # resume the same provider workstream
ooda check      # validate project/evidence integrity
ooda dashboard  # read-only stakeholder view
```

Compatibility commands may exist while old projects migrate, but they are not the target product.

## How OODA thinks about prediction work

OODA does **not** impose a universal stage ladder. It maintains a dependency map around the decision the model exists to improve:

```text
business / capital decision
        ↓
prediction needed for that decision
        ↓
authoritative data and observation process
        ↓
point-in-time dataset / target contract
        ↓
current benchmark
        ↓
candidate model or signal
        ↓
held-out evidence and uncertainty
        ↓
decision policy and realistic economics
        ↓
risk / sizing policy when applicable
        ↓
production execution
        ↓
data, model, calibration, and economic monitoring
```

These are dependencies, not mandatory stages. A mature repository may already satisfy most of them. OODA should identify the unresolved dependency most likely to change the decision, not force the project to revisit completed work.

A useful next-action question is:

> What uncertainty, if resolved honestly and cheaply, has the highest chance of changing the decision?

## Prediction-systems knowledge

Agents using OODA should understand what a defensible end-to-end prediction system requires without the operator having to reinvent the checklist on every project.

The reusable knowledge covers:

- **Ingestion and source health:** timestamps, revisions, missingness, backfills, stale feeds, deduplication, event time vs processing time, schema changes.
- **Target and dataset construction:** decision time, horizon, label availability, censoring, point-in-time joins, survivorship, eligibility, leakage, reproducibility.
- **Benchmarks:** trivial baselines, incumbent systems, market-implied probabilities, de-vigged prices, or another already-used comparator.
- **Model development:** feature value, ablations, regularization, placebo/permutation checks, complexity discipline, failure to beat the benchmark.
- **Evaluation:** temporal validation, held-out testing, proper scoring rules, uncertainty, subgroup/tail stability, calibration when probability magnitude matters.
- **Decision economics:** thresholds, ranking, expected value, fees, spread, slippage, liquidity, latency, capacity, turnover, and realistic simulation.
- **Capital and staking:** edge uncertainty, probability reliability, correlation, concentration, drawdown limits, sizing rules, and explicit separation between research evidence and real-money eligibility.
- **Production:** deterministic pipelines, versioned artifacts, reproducible features, fallback behavior, observability, and training/live consistency.
- **Monitoring:** source freshness, population drift, model-performance drift, calibration drift, economic drift, regime change, and invalidation of upstream assumptions.
- **Reassessment:** investigate, recalibrate, retrain, reduce exposure, replace, or do nothing based on decision impact rather than generic alerts.

The framework knows what must be considered. Each project owns its domain-specific implementation.

## Data stays where it lives

Execution locality is a core invariant.

When authoritative data, a live process, private files, credentials, or hardware are not available in the agent environment:

- the agent may still write deterministic code and test it against fixtures;
- real data-dependent execution runs where the authoritative data live;
- OODA names one reproducible entry point and one compact result artifact;
- raw datasets and verbose logs do not need to be copied into model context.

This must be automatic on the supported execution path. It must not depend on the operator remembering to run a separate preflight after work has already started.

## Scientific and economic integrity

OODA is flexible about which experiment comes next and rigid about whether consequential evidence is honest.

Hard protections should be few and mechanically testable:

- **Point-in-time correctness.** Future information may not enter historical predictions.
- **Evidence priority.** Work may be exploratory at any time, but evidence cannot later be represented as preregistered or ex-ante unless priority is provable.
- **Reference integrity.** OODA-owned references must resolve; deliberate external or gitignored dependencies must be explicitly distinguished from missing artifacts.
- **Project-native checks.** Consequential evidence must pass the repository's real data/model integrity checks at the boundary where the evidence is accepted.
- **Independent validation for consequential claims.** A worker does not self-certify qualification, production safety, or capital eligibility.
- **Probability reliability when probability magnitude drives decisions.** Ranking-only work is not forced through a calibration ritual; sizing, expected-value thresholds, or capital allocation that consume `p` require suitable reliability evidence.
- **Capital is a separate consequence boundary.** A useful model result is not automatically permission to risk money.
- **Human authority remains explicit** for merge, live mutation, deployment, or capital where the project requires it.

Exploration should remain open unless the target itself is shown to be scientifically unidentifiable or unsafe to pursue.

## Why these protections exist

Every mandatory mechanism should map to a measured failure or a clearly stated experimental hypothesis.

| Mechanism | Measured failure it addresses |
|---|---|
| Automatic execution-locality check | Remote Crypto work proceeded before discovering the authoritative snapshot was unavailable |
| Evidence-priority record | Tenniskal work-order/trace ordering failures and an LDPS forward-ledger mechanism that was designed but never used |
| Reference resolution with deliberate-absence annotation | Real dangling references existed, while naive checking also produced many false positives for intentionally external artifacts |
| Project-native integrity boundary | LDPS honesty guards worked where called but production/modeling paths grew around them |
| Conditional probability-reliability requirement | Live LDPS paths used probability magnitude for sizing without demonstrated live reliability |
| Preserve negative findings | Repeated work becomes likely when failed hypotheses are not durable and discoverable |
| Reuse valid derived artifacts | Tenniskal-style expensive historical recomputation is unnecessary when the upstream contract has not changed |

A proposal with no measured failure behind it should normally remain out of the core until real work demonstrates its value.

## Language contract

Primary user-facing language must be understandable to a data-science lead, CEO, portfolio manager, or business stakeholder.

Use terms such as:

- business objective
- decision we are trying to improve
- current benchmark
- model being evaluated
- evidence so far
- what remains uncertain
- next highest-value experiment
- data health
- model health
- probability reliability
- economic performance
- research / production / real-money status

Legitimate data-science terms such as calibration, holdout, leakage, backtest, expected value, drawdown, and feature drift are welcome when they add precision.

Internal framework labels, unexplained acronyms, work-order IDs, provider session IDs, commit hashes, role/profile/lens names, and project shorthand such as `C2` or `R1D.4` belong in technical details, not the primary summary. If a project already uses an identifier, OODA should pair it with a human description.

## Agent and session model

Default to one capable agent for one bounded workstream.

Use a second independent validator when the claim is consequential. Use parallel subagents only when workstreams are genuinely independent or require isolated context.

OODA should own provider session metadata so the operator can resume a workstream without manually managing chat windows. A new provider session should correspond to a materially new workstream, not to framework ceremony.

The framework must not recreate a multi-agent organization on top of providers that already support coding agents, sessions, tools, and subagents.

## Dashboard contract

The dashboard is read-only and derived. It is not project truth.

The default view should answer:

1. What business or capital objective are we pursuing?
2. What decision are we trying to make now?
3. What is the current benchmark?
4. What model or hypothesis is being evaluated?
5. What has actually been demonstrated?
6. What remains uncertain?
7. Are the data healthy?
8. Is the model reliable for its intended use?
9. Is the system research-only, production-ready, or eligible for real-money use?
10. What is the next highest-value experiment?

Technical identifiers, Git state, exact metrics, artifact fingerprints, run/session IDs, and test details should remain available behind an expandable technical section.

## What OODA should not become

The ordinary product should not require:

- a permanent controller persona or chat session;
- a stage ladder;
- roles, profiles, or lenses to perform ordinary work;
- a mission-economics subsystem with no routing decision attached to it;
- a custom RPC layer, scheduler, remote filesystem, or data mover;
- a bespoke agent swarm;
- duplicate data-science logic that already belongs in the project repository;
- dashboards that present framework mechanics as business meaning;
- new artifacts whose only purpose is satisfying OODA itself.

Compatibility surfaces may remain temporarily, but compatibility is not a reason to keep dead architecture indefinitely.

## Complexity rule

Every retained runtime module must do at least one of these:

1. materially help choose or execute a modeling/engineering decision; or
2. mechanically prevent a measured integrity/operational failure.

Otherwise it should be collapsed, moved to compatibility-only code, or deleted.

Tests may be larger than the runtime. That is desirable if they preserve the failure corpus.

## Acceptance standard

OODA is in a good place when:

- the operator spends attention on data, models, market/business mechanics, results, and hypotheses rather than framework administration;
- the supported run path automatically handles execution locality and provenance before expensive work begins;
- every artifact OODA emits is understood by one integrity checker;
- the measured failure corpus cannot silently pass;
- intentional exceptions do not produce an alarm rate high enough to train the operator to ignore OODA;
- a fresh install and an upgrade install behave the same;
- a deliberately undisciplined Crypto-style workflow is safer without becoming slower through ceremony;
- a disciplined Tenniskal-style workflow stays lightweight;
- the same kernel can later support slower-horizon real-estate forecasting without embedding prediction-market-specific logic;
- real project work demonstrates lower friction or better integrity than working without OODA.

Once those conditions hold, OODA should be frozen. Future framework changes require either a concrete failure observed during real prediction work or measured evidence that the change reduces time/tokens or improves decision quality.
