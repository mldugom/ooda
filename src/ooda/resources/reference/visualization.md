# Evidence surfaces

Produce an artifact only when it changes interpretation. Do not auto-generate
plots, dashboards, or HTML reports.

Order of preference:

1. **text/table** — exact values, rankings, pass/fail gates
2. **diagnostic plot** — when shape, tails, calibration, missingness, PIT, or
   relationship structure is the uncertainty
3. **durable panel** — the same diagnostic will be revisited across missions
4. **dashboard** — several stable panels serve one recurring operator workflow
5. **live monitor** — wall-clock freshness can change an action

Three triggers where a plot reliably earns its place:

- **threshold target near the distribution mode** → outcome distribution with the
  threshold drawn on it, before modelling
- **probability forecast** → calibration/reliability plot
- **model vs market** → signed disagreement against outcome

Record `none | diagnostic | durable-panel | dashboard | live-monitor` plus the
decision question it serves. A diagnostic states its sample and provenance and
what result would change the decision.

If a dashboard becomes warranted but is outside scope, return a proposed panel
contract instead of building it.
