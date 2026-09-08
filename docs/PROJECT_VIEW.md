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
      "bigger_idea": "The research program is moving from exploration into controlled testing."
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

The columns are intentionally stakeholder-facing:

| Field | Question |
|---|---|
| `at` | When did the material pivot happen? |
| `decision` | What did we choose or change? |
| `so_what` | What immediate practical consequence follows? |
| `bigger_idea` | How does that consequence affect the larger research/product/business objective? |

Write `so_what` and `bigger_idea` in plain language. Name the concrete dataset, model, experiment, gate, feature family, system, or user decision whenever possible. Avoid vague phrases such as “it worked”, “the idea”, or “the next step” when the actual noun is available.

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

By default this renders the objective ladder, the latest eight decision pivots, and the current stakeholder summary.

```bash
ooda view --all
ooda view --json
```

A user can also ask `/ooda-controller` for `timeline`, `show timeline`, or `where are we`; when the artifact exists, the Controller should render or summarize this same durable object rather than replaying old chat history.

OODA does not patch or scrape the provider's terminal chrome. In Grok, the native TUI and Workflow/subagent panel remain Grok-owned; OODA supplies the durable state and Controller/worker behavior rendered within that terminal session.

## Browser Control Room

The bundled `ooda dashboard` Control Room reads the same `.ooda/project-view.json`.

For the selected project it shows:

- current stakeholder summary;
- current human/next gate;
- the live OODA loop;
- the full visible objective ladder;
- the latest material timeline pivots;
- Git/controller/mission freshness metadata.

Multiple projects are presented as horizontal tabs rather than stacked full project cockpits. The selected project persists across refresh when browser local storage is available.

There is no second dashboard-specific history.

## Relationship to other OODA artifacts

```text
PROJECT_STATE.md       = concise authoritative current project truth
work orders / traces   = bounded execution + evidence provenance
project-view.json      = human mental model of the path and current meaning
```

The project view should make context cheaper, not create another project-management bureaucracy.
