# Quantitative Research Feedback Loop

OODA should make quantitative research easier to understand **while it is happening**, not only after a final model or dashboard exists.

The purpose of this policy is to turn each material data-science mission into a compact learning loop without forcing a chart, notebook, or dashboard update every time.

## Core rule

> Every material quantitative mission should leave behind the smallest durable artifact that makes the new evidence easy to re-observe.

This is not a requirement to plot everything. It is a requirement to preserve the useful reduction of the work.

The default profiles covered are:

- `quantitative-research`
- `statistics`
- `data-science`
- `ml-research`
- `quant-markets`

Projects may opt other profiles into the same behavior.

## Quantitative OODA loop

### OBSERVE — make the data state visible

Capture the minimum facts needed to understand what was actually analyzed:

- authoritative dataset / artifact / snapshot;
- sample universe and support (`n`);
- decision-time / PIT / as-of semantics when relevant;
- important missingness or coverage constraints;
- target, feature family, and baseline if modeling is involved;
- source Git SHA / analysis artifact when material.

Do not make the operator reconstruct the sample from code or chat.

### ORIENT — reduce the scientific question

State the decision question in plain language and identify:

- hypothesis or uncertainty;
- claim ceiling: discovery, evidence, qualification, or n-a;
- primary metric / statistical comparison;
- major alternative explanation or leakage risk;
- what result would materially change the next action.

A useful orientation is often one paragraph, a small table, or a simple pipeline diagram.

### DECIDE — choose the evidence surface before producing it

Choose the smallest output that will make the result easy to understand later:

1. **summary** — short explanation of what was tested and why;
2. **table** — exact values, support, effects, uncertainty, candidate status, or gates;
3. **diagram** — data flow, experiment design, feature/target boundary, model stack, or stage progression when structure is otherwise hard to remember;
4. **diagnostic plot** — only when distribution, path, calibration, residuals, regimes, missingness, tails, or relationships matter;
5. **durable dashboard panel** — only when the same stable question will be revisited.

The visualization ladder in `RESEARCH_VISUALIZATION.md` still applies. This policy adds **artifact cadence**, not chart volume.

### ACT — leave a compact research evidence packet

When a mission produces new quantitative evidence that changes orientation, preserve a compact packet in the project rather than returning only terminal prose.

A packet normally contains some subset of:

```text
QUESTION
What uncertainty was tested?

DATA
What exact sample / snapshot / PIT rule was used?

ANALYSIS
What comparison/model/statistic was run?

KEY EVIDENCE
A compact table of n, effect/metric, uncertainty/sensitivity, and verdict.

INTERPRETATION
What can we now say? What can we still not say?

ARTIFACT DECISION
none | table | diagram | diagnostic | durable-panel | dashboard

ARTIFACTS
Paths to the durable markdown/CSV/JSON/HTML/figure outputs.

DASHBOARD IMPACT
none | refresh existing panel | proposed panel | dashboard update required

NEXT UNKNOWN
What uncertainty now has highest value to resolve?
```

The packet may live in an existing research result document, TRACE, generated report, or project-specific artifact. Do **not** create a redundant file when an authoritative artifact already serves the purpose.

### VERIFY — check understanding, not only code

Verification should answer both:

- **execution validity** — tests, invariants, leakage/PIT, reproducibility, provenance;
- **interpretation validity** — effect size, sample support, sensitivity, uncertainty, claim ceiling, and explicit non-claims.

Green tests alone are not a research interpretation.

## Default artifact behavior

### Produce automatically when useful

For a material quantitative result, workers should normally produce at least one compact durable evidence surface without waiting for the operator to ask.

Examples:

- candidate comparison table;
- feature coverage table;
- calibration table/plot;
- sample/PIT diagram;
- model-vs-baseline table;
- experiment-stage diagram;
- bounded HTML result card/report;
- updated durable dashboard panel when an existing panel contract is directly affected.

### Do not produce automatically when it adds noise

Skip new artifacts when the mission is:

- purely administrative;
- a design-only freeze with no new quantitative evidence and the design is already clear;
- a tiny correction that does not alter interpretation;
- completely answered by an existing artifact with only a one-line state change.

Record `ARTIFACT DECISION: none` and why when the choice is material.

## Dashboard stewardship

If a project has a research dashboard contract, a worker should assess dashboard impact on every material quantitative result.

- If the result changes an **existing durable panel** and updating it is inside scope, refresh the panel from authoritative artifacts.
- If the result warrants a **new durable panel** but dashboard work is outside scope, return a proposed panel contract rather than silently expanding the mission.
- Do not update dashboard layout merely because a new research stage number exists.
- Do not turn discovery artifacts into permanent navigation by default.

Dashboard code and generated HTML remain derived views; research artifacts and data remain authoritative.

## Visual QA for dashboards

A dashboard change is not verified only because HTML was generated.

When the environment supports browser capture, dashboard verification should include:

- one desktop screenshot (roughly 1366–1600 px wide);
- one narrower screenshot (roughly 900–1100 px wide);
- no clipped/overlapping labels or cards;
- readable hierarchy at normal zoom;
- chart axes/units/sample labels visible;
- no misleading truncation or hidden provenance;
- empty/stale states distinguishable from zero.

If browser capture is unavailable, run structural/smoke checks and report that visual inspection is still pending instead of claiming the dashboard "looks good."

## Relationship to Agile Data Science

Quantitative work often has no reliable long-range schedule because each result changes what is worth doing next. OODA handles that uncertainty by making each loop legible:

```text
uncertain question
      |
      v
bounded analysis
      |
      v
reduce / summarize / diagram / visualize
      |
      v
new evidence
      |
      v
next highest-value question
```

The substitute for a rigid research deadline is **fast, durable learning feedback**.

## Design principle

> Research should be uncertain about the next answer, not opaque about what was just learned.
