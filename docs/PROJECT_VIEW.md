# Project View

OODA projects may keep an optional human-facing control artifact at:

```text
.ooda/project-view.json
```

Its purpose is simple: make it cheap for a human or fresh Controller session to answer **where are we, why did the project change direction, and what larger objective does the current gate serve?**

It is a derived orientation surface. `PROJECT_STATE.md`, work orders, traces, Git, tests, research artifacts, and project authority remain authoritative.

## Schema

```json
{
  "schema": "ooda/project-view/v1",
  "project_id": "example",
  "objective_ladder": [
    {"status": "completed", "label": "Understand the current substrate"},
    {"status": "current", "label": "Test the frozen hypotheses"},
    {"status": "provisional", "label": "Evaluate live execution"}
  ],
  "timeline": [
    {
      "at": "2026-09-08",
      "decision": "Freeze the candidate hypothesis set",
      "so_what": "The next predictive test cannot add features after seeing results.",
      "bigger_idea": "The research program moves from exploration into controlled testing; outcome-driven feature redesign remains unauthorized."
    }
  ],
  "stakeholder_summary": "The candidate hypotheses are frozen. The next consequential question is whether they survive the controlled predictive test."
}
```

## Objective ladder

The ladder is the project's current theory of how today's question connects to the larger objective.

- `completed` — sufficiently established/completed to move on;
- `current` — the one question or gate being actively resolved;
- `provisional` — a downstream hypothesis/plan, subject to reorder, replacement, skipping, or abandonment.

There must be exactly one `current` rung.

**The ladder is directional, not contractual.** Rungs below `current` are not approved missions and must not become momentum-driven roadmap commitments.

## Decision timeline

The timeline is not an activity log. Add a row only when the project's mental model, priority, evidence interpretation, gate, or authorized direction materially changes.

The durable JSON field names remain stable, while human-facing labels are intentionally clearer:

| JSON field | Display label | Question |
|---|---|---|
| `at` | `TIME` | When did the material pivot happen? |
| `decision` | `DECISION` | What concrete dataset/model/experiment/gate/system decision changed? |
| `so_what` | `IMMEDIATE CONSEQUENCE` | What changes operationally or scientifically now? |
| `bigger_idea` | `PROGRAM IMPACT` | What does this enable, rule out, or change in the larger objective? |

Write each row like a data scientist briefing a CTO: simple enough to scan, specific enough to act on. Name the concrete dataset, model, experiment, gate, feature family, system, or user decision. Include the decisive number or constraint when it materially drove the pivot. When authority matters, state what the decision still does **not** authorize.

Example:

Bad:

> R6 worked and we can move forward.

Better:

> **DECISION:** Freeze five R7 market-state hypotheses. **IMMEDIATE CONSEQUENCE:** R7 may test only the frozen intensity, acceleration, and staleness definitions; no features may be added after outcomes are joined. **PROGRAM IMPACT:** Tenniskal moves from exploratory market-state discovery to preregistered predictive testing; ROI search remains unauthorized.

Do not add rows for shell commands, file reads, ordinary tests, routine worker chatter, or every intermediate implementation detail.

If the history becomes noisy, explicitly consolidate adjacent rows into a smaller number of meaningful pivots while preserving the causal decision chain. Traces remain the detailed durable evidence trail.

## Current stakeholder summary

The summary is normally one or two sentences answering:

1. where are we now;
2. what has materially been learned or decided;
3. what is the next consequential question or gate.

Refresh it whenever a new material timeline row is added.

## Terminal

From an adopted project:

```bash
ooda view
```

By default this renders the objective ladder, the latest eight decision pivots, and the current stakeholder summary. The timeline displays `IMMEDIATE CONSEQUENCE` and `PROGRAM IMPACT` while preserving the existing JSON field names.

```bash
ooda view --all
ooda view --json
```

A user can also ask the provider Controller for `timeline`, `show timeline`, or `where are we`; when the artifact exists, the Controller should render or summarize this same durable object rather than replaying old chat history.

## Browser Control Room

The bundled `ooda dashboard` Control Room reads the same `.ooda/project-view.json`.

For the selected project it shows:

- current stakeholder summary and human/next gate;
- a compact OODA phase rail rather than five large phase tiles;
- `NOW | WAITING ON / GATE | NEXT IF CURRENT GATE PASSES`;
- the full visible objective ladder;
- the latest material timeline pivots;
- provider/model/context/cost/balance telemetry when available;
- Feedback-loop Efficiency when exact mission economics/timing exist;
- Git/controller/mission freshness metadata.

Multiple projects are presented in a left sidebar. The selected project persists across refresh when browser local storage is available.

There is no second dashboard-specific history.

## Relationship to other OODA artifacts

```text
PROJECT_STATE.md       = concise authoritative current project truth
work orders / traces   = bounded execution + evidence provenance
project-view.json      = human mental model of the path and current meaning
```

The project view should make context cheaper, not create another project-management bureaucracy.
