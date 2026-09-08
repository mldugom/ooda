# Current Stack Baseline

OODA is designed around a working human + agent system rather than pretending that durable project truth lives in chat.

## Current operating paradigm

```text
HUMAN + CHATGPT
      |
      v
Grok native TUI via grok-safe
      |
      v
/ooda-controller
compact Observe -> Orient -> Decide
      |
      | authorized bounded work
      v
OODA work order
      |
      v
isolated child workflow/worker
      |
      v
RESULT / SO WHAT / BIGGER IDEA
trace + Git/test evidence
      |
      v
Controller re-observes
      |
      v
human integration / promotion gate
```

The Controller stays context-light. Deep evidence, code, data analysis, experiments, implementation, or independent validation belong in bounded worker context.

## Durable state

The replaceable conversational/runtime views reconstruct from durable project state:

```text
PROJECT_STATE.md
.ooda/project.json
.ooda/work-orders/
.ooda/traces/
optional .ooda/project-view.json
project-local research/code/docs
Git / PR / test evidence
```

`.ooda/project-view.json` carries the human orientation layer: objective ladder, material decision timeline, and stakeholder summary. It is not authority.

## Human surfaces

The same durable orientation can be viewed through three surfaces:

```text
Grok conversation   /ooda-controller where are we?
Shell               ooda view
Browser             ooda dashboard
```

`ooda view` is the compact canonical terminal renderer.

The browser Control Room is a read-only portfolio companion. It currently shows project tabs, current gate, stakeholder summary, live OODA loop, objective ladder, recent material pivots, Git/controller/mission freshness, and optional provider context telemetry.

OODA does not patch or scrape Grok's native terminal chrome. Grok owns the native TUI and Workflow/subagent panel; OODA owns the control contracts and durable state rendered through that environment.

## Current Grok runtime value to preserve

The reference Grok flavor currently provides:

- narrow session bootstrap;
- one Controller with isolated inline child workers;
- bounded work-order lifecycle and concise handoff conventions;
- efficiency/context controls;
- safe launcher discipline;
- provider-neutral result/trace semantics.

OODA wraps these capabilities rather than requiring a runtime rewrite.

## Provider-neutral boundary

Grok is the current reference flavor, not OODA's ontology.

Runner/harness and inference-provider details may change later without changing:

- work-order meaning;
- trace semantics;
- roles/profiles/lenses;
- claim levels;
- objective-ladder semantics;
- project-local evidence;
- human merge/model-promotion/live-capital gates.

The next-provider implementation is intentionally deferred. See `docs/PROVIDER_FLAVORS.md`.

## Project truth remains local

OODA does not centralize all project knowledge.

A research repo keeps methodology/history locally. A production system keeps runtime protections locally. A product repo keeps product/architecture docs locally. An analytical project keeps assumptions locally.

`.ooda/project.json` only points the Controller toward the project's authority/state sources and default constraints.
