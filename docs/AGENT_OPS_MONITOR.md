# OODA Control Room Boundary

The bundled `ooda dashboard` is an **optional read-only coordination view** over durable OODA project state. OODA owns doctrine/contracts; the Control Room owns rendering and freshness.

It is a companion to the terminal view, not a second source of project truth.

## Current implementation

`ooda dashboard` scans OODA-adopted repositories under `OODA_PROJECTS_ROOT` (default `~/repos`) and derives compact state from:

```text
.ooda/project.json
PROJECT_STATE.md
active/recent work orders
latest useful traces
optional .ooda/project-view.json
local Git state
optional .ooda/session-telemetry.json
        |
        v
read-only OODA Control Room
```

The current Control Room:

- shows projects as horizontal tabs;
- remembers the selected project across refresh when browser local storage is available;
- defaults to a 15-second browser refresh;
- surfaces stakeholder summary and human/next gate;
- renders the `OBSERVE -> ORIENT -> DECIDE -> ACT -> VERIFY` loop;
- renders the full visible objective ladder and recent material decision pivots;
- shows Git/controller/mission freshness metadata;
- may show provider context usage when a provider adapter writes the optional session-telemetry contract.

The launcher verifies service identity before reusing a port. If the preferred port belongs to another local service, OODA chooses the next free local port.

## OODA owns

- operating doctrine;
- Controller contract;
- roles/profiles/lenses;
- work-order/mission contract;
- run trace;
- project-view semantics;
- budget/stop/authority semantics;
- provider-neutral control boundaries.

## Project repositories own

- actual code/data/research truth;
- Git state;
- project-specific constraints;
- scientific and production artifacts;
- concise current-state documents;
- project-local authority.

## The Control Room owns

- rendering;
- freshness;
- cross-project portfolio view;
- current objective / OODA stage visibility;
- active mission / worker visibility;
- claim-level visibility;
- human decision queue;
- useful control tables/visuals.

It must not become authority merely because it can display OODA state.

## Terminal relationship

OODA's terminal surfaces and browser Control Room read the same durable project orientation:

```text
inside Grok:  /ooda-controller where are we?
shell:        ooda view
browser:      ooda dashboard
```

Grok owns its native TUI chrome and Workflow/subagent panel. OODA does not scrape or patch provider terminal chrome.

## Controller-sized fields

The preferred cross-project state is intentionally small:

- project / project class;
- current objective;
- OODA stage;
- role / profile / lenses;
- claim level;
- active mission;
- provider/worker when known;
- branch/PR when relevant;
- latest trace/result;
- blocker / human gate;
- freshness.

Detailed code, raw datasets, research histories, and full agent transcripts stay out of Controller context.

## Future observation plane

A repository watcher remains a deliberately deferred extension. If earned later, it may automate detection of default-branch advances, PR changes, selected state-file changes, and new OODA traces/work orders.

That future watcher would feed observation events into the same Control Room and Controller boundaries. It must not automatically create consequential work, certify results, merge code, promote models, or touch live runtime/capital.

## Design rule

> Automate observation before automating judgment.
