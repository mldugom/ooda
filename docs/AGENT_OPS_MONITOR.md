# OODA Control Room Boundary

A Control Room is an **optional read-only coordination view**. OODA owns doctrine/contracts; a dashboard implementation owns rendering and freshness.

## OODA owns

- operating doctrine;
- Controller contract;
- roles/profiles/lenses;
- work-order/mission contract;
- run trace;
- budget/stop/authority semantics;
- future collector/supervisor semantics.

## Project repositories own

- actual code/data/research truth;
- Git state;
- project-specific constraints;
- scientific and production artifacts;
- concise current-state documents.

## A Control Room owns

- rendering;
- freshness;
- cross-project portfolio view;
- current objective / OODA stage visibility;
- active mission / worker visibility;
- claim-level visibility;
- human decision queue;
- useful control charts/tables.

It must not become authority merely because it can display OODA state.

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

## Future collector

A small collector may derive Control Room state from:

```text
.ooda/project.json
PROJECT_STATE.md
active missions
latest useful traces
Git / PR state
human gates
        |
        v
sanitized control snapshot
        |
        v
OODA Control Room
```

The dashboard cache/snapshot is disposable and rebuildable. It is not a second source of project truth.

## Public package behavior

`ooda dashboard` is optional. It uses an existing checkout at `OODA_CONTROL_ROOM_DIR`, or an explicitly configured `OODA_CONTROL_ROOM_REPO` clone URL. OODA does not require a dashboard to use the Controller, missions, traces, or `grok-safe`.

## Design rule

> Automate observation before automating judgment.
