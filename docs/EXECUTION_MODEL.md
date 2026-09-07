# Current Execution Model — Lawrence + ChatGPT + Grok Build

## Purpose

OODA V1 does **not** replace the current working Grok execution paradigm. It standardizes the boundary around it.

## The current loop

```text
LAWRENCE
   +
CHATGPT
   |
   | raw ideas, goals, creative challenge, prioritization
   v
DECISION: worth agent time?
   |
   +-- no --> keep discussing / stop
   |
   +-- yes
        |
        v
   OODA WORK ORDER
        |
        v
   GROK BUILD
   existing repo + existing local runtime
        |
        | /start if useful
        | one bounded task
        | current repo-specific rules
        | tests / research artifact
        | /handoff when implementation is ready
        v
   GIT BRANCH / PR / HANDOFF
        |
        v
CHATGPT + LAWRENCE
integration / scientific / product review
        |
    +---+---+
    |       |
 accept   correct/reject
    |       |
    v       v
 merge    bounded correction
    |
    v
OODA TRACE
```

## Responsibilities

### Lawrence
- supplies goals, judgment, preferences, capital/risk authority, and final consequential decisions;
- may change direction at any time;
- owns human integration authority.

### ChatGPT
- creative/strategic counterpart upstream;
- helps turn raw intent into a bounded OODA work order;
- reviews Grok's handoff and evidence;
- should challenge scope, science, architecture, and claims rather than merely relay prompts.

### OODA
- doctrine and execution contract;
- chooses role/profile/lenses/claim level for the action;
- preserves decision provenance;
- does not replace the provider.

### Grok Build
- current provider and worker;
- may research, architect, engineer, or audit according to the work order;
- follows project-local rules and the existing Grok lifecycle;
- does not gain merge, promotion, or capital authority from OODA.

### Git/GitHub
- durable implementation and review boundary;
- branch/PR state remains authoritative for code changes.

### Agent Ops Monitor
- display/freshness layer;
- not a source of truth, certifier, dispatcher, or merge authority.

## Session pattern

For current Grok Build sessions:

1. Discuss freely with ChatGPT.
2. When ready to act, create one OODA work order.
3. Start one Grok session in the target project.
4. Use the project's existing `/start` behavior if useful.
5. Give Grok the work order and ask it to operate under the selected role/profile/lenses.
6. Grok executes one substantial work unit.
7. Grok uses the project's current handoff convention.
8. ChatGPT/Lawrence review.
9. Persist a concise OODA trace after the outcome is known.
10. Start a new loop for a materially different mission.

## Correction loops

A correction is not automatically a new mission. If the same objective remains valid and the correction is bounded, resume/continue. If the objective, authority, protected scope, claim level, or architecture materially changes, create a new work order.

## What V1 deliberately does not automate

- issue polling;
- background workers;
- autonomous provider routing;
- automatic retries;
- automatic merge;
- model promotion;
- live trading;
- Agent Ops Monitor control;
- Raspberry Pi scheduling;
- DeepSeek dispatch.

Those are future control-plane capabilities. They must consume the same work-order/trace contracts after the manual process proves them.
