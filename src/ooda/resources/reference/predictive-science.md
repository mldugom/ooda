# Predictive science — defaults

Load for any predictive or modelling mission. These are defaults, not laws;
depart from them deliberately and say why.

## Start here, in this order

```
decision -> target -> decision time -> baseline -> sample -> split -> metrics
-> holdout -> stop rule
```

Answer those before feature programmes, complex models, or qualification chains.
A simple end-to-end baseline that produces a measured number beats a large
feature effort that produces none.

Tennis: results → Elo → probability metrics → compare with market.
Crypto: buy-time features → target → C0/C1/C2 → evaluate.

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
