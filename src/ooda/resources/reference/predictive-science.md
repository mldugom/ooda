# Predictive science — defaults

Load for any predictive or modelling mission. These are defaults, not laws;
depart from them deliberately and say why.

## Start here, in this order

```
decision -> target / decision time -> authoritative data location
-> local deterministic dataset build -> baseline / metrics / invariants
-> compact evidence -> interpretation -> next unknown
```

Answer those before feature programmes, complex models, or qualification chains.
A simple end-to-end baseline that produces a measured number beats a large
feature effort that produces none.

Concretely: raw outcomes → a simple rating or feature set → probability metrics
→ compare against the baseline and, where one exists, the market.

## Data stays where it lives; code moves to the data

Spend model reasoning on choosing the question, naming the confounds, designing
the test, and interpreting the result. Do not spend it on bulk data transport,
row-by-row inspection, arithmetic, schema rediscovery, or chaining stable steps
by hand. **The model is not the data plane.**

1. Identify the decision and the authoritative data.
2. Establish where that data actually lives.
3. Check whether this environment can reach it (`ooda preflight`).
4. If not, that is **routing, not a block** — write and test the deterministic
   code here against fixtures, and run it where the data is.
5. Prefer an existing reusable Python entry point; create one only when the
   workflow is repeated, stable, and semantically one operation.
6. Run the deterministic part outside the model; return compact evidence.

The operator is not the pipeline. If a remote agent cannot reach the host, it
returns **one** exact command — not twelve manual steps.

```bash
python -m alpha.research.broad_baseline \
  --snapshot data/radar.sqlite \
  --summary-json result.json
```

## Python-first for deterministic work

Preference order: an existing Python module or CLI → a small new one when it
earns its existence → SQL executed from Python → shell as thin launch glue →
a manual multi-command sequence only when genuinely simpler and one-off.

Python handles SQLite, CSV/JSON/Parquet, feature construction, metrics,
invariants, branching, reuse, tests, and structured output better than a long
shell pipeline. This applies to research computation, dataset construction,
metric evaluation, and scientific validation — not to every engineering task.

An abstraction earns its existence only when it reduces repeated tool calls,
context volume, operator error, scientific inconsistency, or duplicated logic.
`pytest -q tests/test_x.py` does not need a wrapper.

## Reuse authoritative derived artifacts

Before replaying expensive upstream work, ask whether a derived artifact already
answers the downstream question. **Reuse it while its upstream contract holds.**
A fresh session or a new worker is not a reason to recompute.

If an expensive replay already produced a frozen evaluation set, a downstream
comparison reads that set. It replays the history only when the construction of
the artifact itself is what the mission is challenging.

Recompute when the upstream contract changed — source, target definition,
filters, split, as-of date — or when the mission challenges how the artifact was
built. Never reuse a stale artifact silently.

## Compact evidence, not transcripts

Deterministic output should be machine-readable and bounded — a small JSON
summary plus artifact pointers, not a large stdout dump:

```json
{"experiment": "broad_baseline", "dataset_sha256": "...", "n": 10000,
 "target": "...", "target_prevalence": 0.47,
 "metrics": {"C0": {}, "C1": {}, "C2": {}},
 "invariants": {"pit": "PASS", "holdout_overlap": 0, "prospective_inspected": false},
 "artifacts": ["..."]}
```

Before running anything expected to be verbose: filter, aggregate, redirect, or
summarise deterministically. Prefer a `summary.json`, a SQL aggregate count,
`pytest -q`, or a targeted `grep`. Avoid `cat` on a large CSV, dumping a whole
table, printing every prediction, or reading a large derived dataset when an
aggregate is enough.


## Target charter — freeze it before modelling

Nine fields, written once, small:

```
DECISION           repeated action we are improving
TARGET             exactly what outcome is predicted
WHY IT MATTERS     link from that outcome back to the decision
DECISION TIME      what information is legally available then
BASELINE           the simple thing that must be beaten
PRIMARY METRICS    how success is judged
HOLDOUT            what may never be tuned against
STOP RULE          when to stop modelling and reconsider data or target
RESOURCE BUDGET    expected ceiling
```

`ooda charter --new` writes one; `ooda charter --diff` detects goalpost movement.

Changing DECISION, TARGET, DECISION TIME, BASELINE, PRIMARY METRICS, or HOLDOUT
redefines success. That is a re-orientation decision requiring the evidence that
motivated it. **A disappointing model is not that evidence.**

## Traps that have actually cost us

- **missing != zero.** An unpopulated schema field is not a zero feature.
- **schema field exists != feature populated.** Count populated and unconfounded
  features, not advertised ones.
- **censored != negative.** A truncated observation is not a failed one.
- **historically downloadable != known at decision time.** Point-in-time or it
  did not happen.
- **target measurable != target useful.** A target you can compute may still not
  improve the decision.
- **a threshold near the outcome's mode produces noise labels.** If the cut sits
  between p50 and p75, the label is largely noise. Plot the outcome distribution
  with the threshold marked *before* modelling, and sweep the threshold —
  including a cost-adjusted one (`> 1 + c` for round-trip cost `c`).
- **base rate is not 50%.** Check it before treating "beats 50%" as a bar.
- **shared-denominator transforms confound.** Features and outcome built from a
  common denominator leak mechanically; surface them.
- **market price must not enter an independent fair-value model** unless the
  model explicitly intends to use market information.
- **a sealed holdout scored repeatedly is tuning data.** One look, at the end.
- **prospective confirmation must stay prospective.** Never inspect its labels.
- **a temporal split of the same substrate is not independent OOS.** It is
  evidence, never qualification.

## Metrics

For probability forecasts use log loss, Brier, calibration (report bin count and
per-bin n), and a discrimination measure. Accuracy is rarely primary. Compare
against both a constant baseline and empirical prevalence.

## Stop rules

Bound the search: N candidate families, or "once baseline metrics exist", or "if
the target is not identifiable". Never "find the best possible model".

## Negative results

No signal, insufficient sample, weak features, poorly conditioned target, not
identifiable — all are successful outcomes. Report and re-orient. Do not add
features, try more models, or move the target in response.
