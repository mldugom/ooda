# Current Execution Model — Lawrence + ChatGPT + OODA Controller + Grok Build

## Purpose

OODA does **not** replace the current working Grok execution paradigm. It standardizes the boundary around it and keeps cross-project context small.

## The current loop

```text
LAWRENCE + CHATGPT
raw ideas / goals / creative challenge
        |
        v
 OODA CONTROLLER
 Intake / Proposal / Control
        |
        | idea earns work
        v
 OODA MISSION
 durable `ooda/work-order/v1`
 Observe -> Orient -> Decide
        |
        v
 GROK BUILD WORKER
 existing repo + current lifecycle
 /start -> /ooda <mission> -> /handoff
        |
        v
 Git branch / PR / evidence
        |
        v
 CHATGPT + LAWRENCE REVIEW
        |
     accept / correct / reject
        |
        v
 OODA TRACE
        |
        v
 Controller re-observes
```

## Responsibilities

### Lawrence
- supplies goals, judgment, preferences, capital/risk authority, and final consequential decisions;
- may change direction at any time;
- owns human integration authority.

### ChatGPT
- creative/strategic counterpart upstream;
- helps challenge goals and interpret results;
- can bounce raw thoughts through the Controller instead of doing repetitive repository archaeology;
- reviews worker handoffs/evidence;
- should challenge scope, science, architecture, documentation impact, and claims rather than merely relay prompts.

### OODA Controller
- thin conversational/control agent;
- reads compact control state, not deep project context;
- Intake: triages raw thoughts;
- Proposal: constructs/proposes bounded missions;
- Control: surfaces blockers/human gates/next moves;
- chooses role/profile/lenses/claim level;
- requests a small orientation spike when robust mission construction needs deeper facts;
- does not become the researcher/engineer itself.

### OODA mission/work order
- durable provider-neutral result of Observe -> Orient -> Decide;
- contains one objective, routing, scope, verification, budget, stops, and authority;
- controls Act without becoming a transcript.

Human-facing creation is normally:

```bash
ooda mission \
  "<bounded objective>" \
  --role <role> \
  --profile <profile> \
  --claim <claim> \
  [--lenses lens1,lens2,lens3] \
  [--id TASK-01]
```

The underlying schema remains `ooda/work-order/v1`.

### Grok Build worker
- current execution provider;
- may research, architect, engineer, or validate according to the mission;
- loads mission-specific deep context that the Controller deliberately avoids;
- follows project-local rules and existing Grok lifecycle;
- re-observes/re-orients when material new facts invalidate assumptions;
- reports documentation impact before handoff;
- does not gain merge, promotion, or capital authority from OODA.

### Git/GitHub
- durable implementation and review boundary;
- branch/PR state remains authoritative for code changes.

### Trace
- concise result/evidence/next-gate record;
- feeds the next Observe step;
- is not a transcript or private chain-of-thought.

Human-facing creation is normally:

```bash
ooda trace \
  --work-order .ooda/work-orders/<id>.json \
  --result <state> \
  --summary "<truthful concise result>"
```

### OODA Control Room
- display/freshness/audit-index layer;
- `ooda dashboard` opens it locally;
- not a source of truth, certifier, dispatcher, or merge authority.

## Session pattern

1. Discuss freely with ChatGPT and/or the Controller.
2. When ready to act, construct one mission.
3. Start one Grok worker session in the target project.
4. Use the project's existing `/start` behavior.
5. Run `/ooda <mission-file>`.
6. Worker executes one substantial bounded work unit.
7. Worker verifies and assesses documentation impact.
8. Worker uses the project's current `/handoff` convention.
9. ChatGPT/Lawrence review.
10. Persist a concise trace.
11. Controller re-observes and recommends the next loop only when useful.

## Correction loops

A correction is not automatically a new mission. If the same objective remains valid and the correction is bounded, resume/continue. If the objective, authority, protected scope, claim level, or architecture materially changes, create a new mission.

## Documentation stewardship

Documentation is part of durable orientation, not activity logging.

A mission may deserve architecture/domain/process/flow/cheat-sheet/methodology documentation when the work materially changes a stable mental model. The active worker assesses impact first; Architect and Validator roles may be used when structural or consequential review is warranted.

See `docs/DOCUMENTATION_STEWARDSHIP.md`.

## What is deliberately not automated yet

- automatic consequential dispatch;
- automatic retries;
- automatic merge;
- model promotion;
- live trading/capital actions;
- giant central context ingestion;
- autonomous provider routing;
- Raspberry Pi scheduling.

Those are future control-plane capabilities. They must consume the same mission/trace contracts after the manual process proves them.
