# OODA Control Room / Agent Ops Boundary

The existing `mldugom/agent-ops-monitor` repository is being repurposed as the **OODA Control Room** rather than replaced.

It remains a separate repository and a read-only coordination view. OODA owns the doctrine/contracts; the monitor repo owns the lightweight HTML observation surface.

## OODA owns

- operating doctrine;
- Controller contract;
- roles/profiles/lenses;
- work-order contract;
- run trace;
- budget/stop/authority semantics;
- future collector/supervisor semantics.

## Project repositories own

- actual code/data/research truth;
- Git state;
- project-specific constraints;
- scientific and production artifacts;
- concise current-state documents.

## OODA Control Room owns

- rendering;
- freshness;
- cross-project portfolio view;
- current objective / OODA stage visibility;
- active work-order / worker visibility;
- claim-level visibility;
- human decision queue;
- purpose-built control charts/tables.

It must not become the authority merely because it can display OODA state.

## Controller-sized fields

The preferred cross-project state is intentionally small:

- project / project class;
- current objective;
- OODA stage;
- role / profile / lenses;
- claim level;
- active work order;
- provider/worker when known;
- branch/PR when relevant;
- latest trace/result;
- blocker / human gate;
- freshness.

Detailed code, raw datasets, research histories, and full agent transcripts stay out of Controller context.

## Current first pass

The monitor repo now has an OODA-oriented renderer on `chatgpt/ooda-control-room-v1` that keeps compatibility with existing `agent-ops-monitor/v1` and `v2` snapshots.

Existing snapshots are mapped into a best-effort OODA view. Exporters may add an optional `ooda` overlay to provide exact role/profile/lenses/claim/work-order/trace/gate state.

This is intentionally observation-first. The dashboard does not dispatch workers yet.

## Future collector

After real OODA work orders/traces exist, a small collector should derive the Control Room snapshot from:

```text
.ooda/project.json
PROJECT_STATE.md
active work orders
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

## Design rule

> Automate observation before automating judgment.
