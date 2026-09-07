# Current Stack Baseline

OODA is designed around the current working system rather than pretending it does not exist.

## Current manual paradigm

```text
Lawrence + ChatGPT
  -> decide a bounded task
  -> Grok Build in the target repository
  -> existing project instructions/lifecycle
  -> tests / research artifacts
  -> branch / PR / handoff
  -> ChatGPT + Lawrence review
  -> explicit merge/promotion decision
```

## `grok-skills`

Current value to preserve outside OODA:
- narrow `/start` bootstrap;
- bounded lifecycle and handoff conventions;
- efficiency/context/cost controls;
- `grok-safe` runtime discipline;
- provider-neutral handoff semantics.

OODA does not require changing or merging new infrastructure into `grok-skills` during V1.

An experimental GitHub-backed Grok worker/transport exists in the current `grok-skills` development history. OODA V1 does not adopt it automatically. If issue-driven local dispatch proves desirable later, it must be evaluated as a Phase-4 supervisor capability against OODA's provider-neutral contracts.

## Agent Ops Monitor

Current monitor strengths:
- provider-neutral rendering;
- objectives/backlog visibility;
- agent lanes;
- human decision queue;
- Git remains authoritative;
- monitor does not certify or merge.

Keep this boundary. OODA traces may become a future input; the monitor does not become OODA's controller.

## Project truth remains local

OODA does not centralize all project knowledge.

Examples:
- Tenniskal's research state remains in Tenniskal.
- Crypto-Innout's runtime/research protections remain in Crypto-Innout.
- LDPS's methodology/history remains in LDPS.
- IOND's valuation assumptions remain in IOND.

`.ooda/project.json` only points the controller toward the project's authority/state sources and default constraints.
