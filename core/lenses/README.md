# Lenses

A lens answers: **what intellectual perspective should shape orientation?**

The controller normally selects no more than three lenses for one bounded action.

| Lens | Primary question | Typical use |
|---|---|---|
| `boyd` | Has our orientation become stale? What feedback changes the next move? | controller, strategy, adaptation |
| `stanley-lehman` | Is the objective deceptive? What novel stepping stone are we ignoring? | exploration, discovery, product/architecture search |
| `taleb` | Where is fragility, ruin, nonlinear downside, convexity, optionality, or removable complexity? | risk, portfolios, architecture, experiments |
| `scientific` | What is the falsifiable claim? What result would reject it? | all research |
| `statistical` | What is uncertainty, power, multiplicity, calibration, and sampling error? | models, backtests, experiments |
| `model-risk` | Leakage, selection, proxy error, misuse, drift, invalid scope, limitations? | ML/quant validation |
| `value-of-information` | What cheapest experiment could change the decision? | research planning, controller, product MVP |
| `causal-mechanism` | Is this association or mechanism? What confounds it? | feature research, valuation, product analytics |
| `market-microstructure` | Is this signal executable at real prices and timing? | trading research |
| `portfolio` | What happens at book level: correlation, concentration, capacity, opportunity cost? | portfolio construction |
| `reliability-systems` | What happens on restart, duplication, stale state, partial failure, dependency loss? | runtimes, pipelines, agent systems |
| `product-user` | Who has the problem, what is the smallest useful workflow, what proves value? | SaaS, apps, extensions |
| `security-abuse` | What permissions, secrets, attack paths, privacy or abuse risks exist? | external software, auth, agents, extensions |

## Lens rules

- Lenses do not grant authority.
- Lenses are not personalities and do not need separate bots.
- Add a lens only when it changes real decisions repeatedly.
- For consequential model qualification, `scientific` + `model-risk` are normally required.
- For externally deployed apps, `security-abuse` is normally required before release.
- For real-money trading, `market-microstructure` + `portfolio` + `taleb`/risk review are normally required before live use.
