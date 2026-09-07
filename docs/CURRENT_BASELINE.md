# Current Stack Baseline

OODA is designed around an existing working system rather than pretending it does not exist.

## Manual paradigm

```text
HUMAN + CHATGPT
  -> decide a bounded task
  -> configured worker/provider in the target repository
  -> existing project instructions/lifecycle
  -> tests / research artifacts
  -> branch / PR / handoff
  -> human + ChatGPT review
  -> explicit merge/promotion decision
```

## Existing agent runtime value to preserve

Useful existing capabilities may include:

- narrow session bootstrap;
- bounded lifecycle and handoff conventions;
- efficiency/context/cost controls;
- safe provider launcher discipline;
- provider-neutral handoff semantics.

OODA wraps these capabilities with provider-neutral mission/trace contracts rather than requiring a runtime rewrite.

## Control Room

Useful monitor properties:

- provider-neutral rendering;
- objective/current-state visibility;
- agent/worker lanes;
- human decision queue;
- Git remains authoritative;
- monitor does not certify or merge.

Keep this boundary. OODA traces may feed a monitor; the monitor does not become OODA's source of truth.

## Project truth remains local

OODA does not centralize all project knowledge.

A research repo keeps its methodology/history locally. A production system keeps its runtime protections locally. A product repo keeps its product/architecture docs locally. An analytical project keeps its assumptions locally.

`.ooda/project.json` only points the Controller toward the project's authority/state sources and default constraints.
