# Research Visualization and Dashboard Policy

OODA treats visualizations as evidence surfaces, not decoration and not mandatory output.

The goal is to make a fresh human or agent able to answer **what question is being tested, what evidence changed the decision, and what should happen next** without turning every research step into another permanent dashboard tab.

## Core rule

> Use the smallest visual surface that changes a decision. Promote a visualization into a durable dashboard only when the same decision will be revisited.

A research mission does **not** earn a chart merely because data exists. A chart does **not** earn a dashboard panel merely because it looks useful once.

## Visualization ladder

Use this escalation order.

### 0. Text or table

Prefer text/table when the decision is driven by:

- one or a few scalar results;
- a short ranked list;
- a pass/fail gate;
- exact values that need comparison more than shape;
- a compact candidate inventory.

Example: three preregistered features with `n`, Spearman rho, and support/reject verdicts are usually clearer as a table than three bar charts.

### 1. Diagnostic plot

Create one bounded plot when shape matters to the decision, for example:

- distribution, skew, tails, multimodality;
- calibration or residual structure;
- time/event path;
- relationship/nonlinearity;
- missingness/coverage by segment;
- leakage/PIT boundary inspection;
- outlier or regime behavior.

A diagnostic plot should state:

1. **decision question** — what uncertainty the plot resolves;
2. **sample/provenance** — what rows/window/as-of rule it uses;
3. **visual encoding** — what axes/groups actually mean;
4. **decision consequence** — what result would change the next action.

Do not build a multi-tab UI for a one-off diagnostic.

### 2. Durable research panel

Promote a plot/table into a durable research panel only when at least one is true:

- the same diagnostic will be revisited across multiple missions;
- the panel represents a frozen research invariant or gate;
- later stages need the same view for comparison;
- the operator repeatedly needs it to orient without reopening raw artifacts.

A durable panel must have stable semantics. If its sample, target, timestamp, peer definition, or feature meaning is still being searched, keep it as an experiment artifact instead.

### 3. Research dashboard

Build or extend a dashboard only when several durable panels answer a **recurring operator decision** from one coherent data contract.

A research dashboard should curate, not concatenate. It should not mirror the research folder or create one tab for every experiment/R-number.

Default sections for quantitative research:

1. **Overview** — current research question, claim ceiling, human gate, stakeholder summary, candidate inventory.
2. **Evidence** — only the few durable plots/tables that explain the current scientific conclusion.
3. **Data / PIT quality** — coverage, missingness, freshness/as-of semantics, leakage checks, sample provenance.
4. **Candidates / Model** — frozen hypotheses, individual vs combined status, baseline comparison, evaluation metrics when authorized.
5. **Live** — only once the project has a decision-time/live feature contract; show current candidate state and source freshness, not historically-downloadable-only features.
6. **Drift / Monitoring** — only after a model or recurring decision rule exists; data drift, model drift, calibration drift, and operational health belong here later.

Sections that have no current decision use should stay absent or visibly dormant rather than being filled with placeholder charts.

### 4. Live monitor

A live panel is justified only when information changes with wall-clock time and an operator may act differently because of it.

Every live panel must expose:

- `as_of` / freshness;
- decision-time availability rather than historical retrievability;
- source/provenance;
- missing/unknown distinctly from zero;
- stale-data behavior;
- action/gate the panel informs.

Do not put historical-only sources into a Live tab merely because they can be downloaded later.

## Plot-vs-dashboard decision test

Before producing UI, answer these in order:

1. **What exact decision or uncertainty needs visual help?**
2. **Would a table/text answer it equally well?** If yes, stop there.
3. **Does shape/path/relationship matter?** If yes, make one diagnostic plot.
4. **Will this exact view be reused after the mission?** If no, keep it as an artifact/report figure.
5. **Do three or more stable views support the same recurring operator workflow?** If yes, a dashboard may be warranted.
6. **Is the underlying semantic contract frozen enough to compare over time?** If no, do not promote it yet.

## Research mission behavior

For data-science/research work, the worker should make an explicit visualization decision during execution:

- `none` — text/table is sufficient;
- `diagnostic` — one-off figure tied to the current hypothesis/gate;
- `durable-panel` — stable view worth carrying forward;
- `dashboard` — recurring multi-panel operator surface;
- `live-monitor` — time-sensitive decision surface with freshness semantics.

This is guidance, not a new required work-order schema field. Record it in the mission result/TRACE when visualization work is material.

A worker must not silently expand a bounded research mission into a dashboard build. If a dashboard becomes warranted but is outside scope, report the proposed panel contract and return to the Controller for a separate mission.

## Dashboard panel contract

A durable panel should be describable in a few lines:

```text
question: what recurring decision does this panel support?
source: authoritative artifact/table/query
sample: exact universe / filter / timestamp semantics
metric: exact calculation and units
view: chart/table type and encodings
freshness: static snapshot or live as-of rule
failure state: what missing/stale/invalid data looks like
action: what decision can change because of this panel
```

If these cannot be stated, the panel is not ready to be durable.

## Anti-patterns

Avoid:

- one dashboard tab per research step;
- plotting every metric because it exists;
- mixing discovery, frozen evidence, and live operation without labels;
- presenting a correlation plot as a predictive/model claim;
- silently changing sample definitions behind an existing panel;
- putting future information or historical-only data into a live view;
- giant embedded JSON/HTML artifacts when compact derived panel data is sufficient;
- dashboards that become a second source of truth instead of rendering authoritative artifacts.

## Tenniskal application

Tenniskal is a useful example because its existing research workbench accumulated stage-shaped tabs (`Maturation`, `Movement`, `Market Quality`, `Relationships / Alpha Map`, `Lead / Lag`, `Event Explorer`) and large embedded R6 artifacts. That is useful archaeology, but it is not the desired long-lived research product.

The preferred Tenniskal research dashboard is a **decision-oriented workbench**:

### Overview

- current question: whether the frozen R7 specification/stability test is authorized / what it establishes once run;
- claim ceiling and discovery-vs-OOS distinction;
- frozen candidate inventory;
- current human gate and next research rung.

### Research Evidence

Curate only the evidence that still matters to the current thesis:

- market maturation / usable decision-time window;
- typical pre-match repricing magnitude versus quote noise;
- R6E raw forward-|move| candidate relationships;
- R6F relative-vs-raw incremental evidence;
- later R7 predictive/stability evidence when authorized.

Do not keep one permanent tab for each R-number just because the artifact exists.

### Data / PIT Quality

- ATP/WTA sample size and coverage;
- decision-time timestamp/PIT checks;
- peer-count coverage at frozen `T`;
- missingness / stale quote coverage;
- exact source segment / Git SHA / as-of provenance.

### Candidate / Model Lab

- H-P1/H-P2/H-R1/H-R2/H-R3 status;
- individual versus C1 combined test status;
- baseline and evaluation metrics after R7 is authorized;
- explicit labels: discovery-substrate stability vs later independent OOS.

### Live

Keep dormant until the project has a live decision-time scoring contract. When activated, it should show the current match candidate, Kalshi price/market state, model/fair probability once such a model exists, devigged external reference when legally/technically available at decision time, disagreement/edge, freshness, and execution constraints.

### Drift

Do not build yet. Add only after a recurring model exists and there is something meaningful to compare across time: feature distribution drift, calibration/model drift, source coverage/freshness, and execution quality.

## Design principle

> Research artifacts explain individual experiments. A research dashboard explains the current scientific state of the program and the decisions that remain.
