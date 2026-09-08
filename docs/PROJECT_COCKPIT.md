# Project Cockpit

OODA's portfolio Control Room and a project's analytical/research dashboard solve different problems.

- **OODA Control Room** — portfolio/control orientation across projects: current objective, stage, mission, gate, Git state, ladder, timeline, stakeholder summary.
- **Project cockpit** — domain-specific evidence and live/health views needed to understand one project's current research/product decisions.

Do not turn the OODA Control Room into an artifact warehouse or a project-specific analytics application.

## Recommended project shape

A mature analytical/research project may converge toward four stable views:

```text
OVERVIEW | RESEARCH | LIVE | HEALTH
```

### Overview

Use the durable OODA project view:

- objective ladder;
- current gate;
- decision timeline;
- current stakeholder summary.

### Research

Show only evidence that helps answer the current research question or preserves an important frozen historical result.

A research mission may publish **zero or more decision-useful views**. Do not force a plot because a research step exists.

A useful view should answer:

```text
QUESTION
What decision/research question does this view answer?

VIEW
metric | table | chart | diagram

SO WHAT
What did the evidence establish or rule out?

BIGGER IDEA
How does the result affect the larger research objective?

SOURCE
Which frozen artifact/data produced the view?
```

Choose the representation that carries the information best:

- a number when one number answers the question;
- a table when exact comparisons matter;
- a chart when shape, distribution, trend, calibration, or relationship matters;
- a diagram when process, causality, hierarchy, or architecture is the question;
- text when a visualization would add decoration rather than information.

Do not scrape every notebook, PNG, table, or report into the dashboard. Curate evidence around decisions.

### Live

Do not invent a live model view before the project has a qualified candidate.

Use explicit terminology:

- **signal candidate** — a feature/hypothesis eligible for testing;
- **model candidate** — a frozen predictive model under evaluation;
- **live candidate** — a model/version that has passed the required OOS/execution gates and is allowed into paper/live evaluation.

Before a live candidate exists, the Live view should say so and show the gate that must be passed next.

Once a live candidate exists, project-specific views may include current observations, predictions, reference prices, executable prices, decision state, freshness, and operator gates.

### Health

Health exists before model drift exists.

Early-stage health can include:

- source freshness;
- coverage;
- schema/data integrity;
- point-in-time integrity;
- missingness;
- source availability;
- research/live semantic parity;
- feature distribution stability when meaningful.

After a model exists, add model-specific monitoring only when earned:

- feature drift;
- prediction drift;
- calibration drift;
- performance degradation;
- research vs live parity.

## Implementation bias

Prefer lightweight local HTML/data contracts for durable shared views. Notebooks and ipywidgets remain excellent exploratory tools, but should not become the only long-lived operational interface merely because plots were created there first.

OODA should standardize the **decision-useful contract and orientation primitives**, while each project owns its domain analytics.

## Current implementation boundary

OODA V1 project view implements only the generalized Overview primitives: ladder, timeline, and stakeholder summary.

The Research/Live/Health cockpit is a design direction, not a mandatory scaffold. Add those surfaces only when a project has enough durable analytical needs to justify them.
