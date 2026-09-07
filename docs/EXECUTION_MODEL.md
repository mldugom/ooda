# Current Execution Model — Lawrence + ChatGPT + OODA Controller + Grok Build

## Purpose

OODA V1 does **not** replace the current working Grok execution paradigm. It standardizes the boundary around it and introduces a thin Controller that can absorb portfolio/control overhead without becoming a deep worker.

## The current loop

```text
LAWRENCE + CHATGPT
raw ideas / goals / challenge / prioritization
        |
        v
OODA CONTROLLER
Intake: worth worker time?
        |
   +----+------------------+
   |                       |
  no                      yes
   |                       |
keep thinking              v
                    enough orientation?
                     /            \
                   no              yes
                   |                |
           orientation spike       |
       researcher/architect/etc.    |
                   |                |
                   +-------> OODA WORK ORDER
                                  |
                                  v
                             GROK WORKER
                     grok-safe -> /start -> /ooda
                        one bounded mission
                                  |
                                  v
                              /handoff
                         Git / tests / PR
                                  |
                                  v
                         LAWRENCE + CHATGPT
                          integration review
                           /             \
                       accept         correct/reject
                         |                |
                         v                v
                       merge       bounded correction
                         |
                         v
                       TRACE
                         |
                         v
                    CONTROLLER
                     re-observes
```

## Responsibilities

### Lawrence
- supplies goals, judgment, preferences, capital/risk authority, and final consequential decisions;
- may change direction at any time;
- owns human integration authority.

### ChatGPT
- creative/strategic counterpart upstream;
- explores raw ideas without forcing task creation;
- bounces strategy and constraints with the Controller;
- reviews Grok handoffs and evidence;
- challenges scope, science, architecture, and claims rather than merely relaying prompts.

### OODA Controller
- thin conversational control/portfolio agent;
- reads only compact durable control state;
- triages raw thoughts into KEEP THINKING / PROPOSE MISSION / HUMAN GATE / NO ACTION;
- chooses role/profile/lenses/claim level;
- constructs or proposes robust work orders from compact evidence;
- requests a short orientation spike when deep facts are needed to construct the mission correctly;
- surfaces blockers, stale state, completed work awaiting review, and human gates;
- does not become the researcher/engineer/validator merely to make a work order more detailed.

### OODA contracts/doctrine
- define Observe → Orient → Decide → Act behavior;
- define work-order/trace semantics;
- preserve budget, stop, authority, claim, and documentation-impact discipline;
- do not replace the provider.

### Grok Build worker
- current execution provider;
- may research, architect, engineer, validate, trade-analyze, or otherwise act according to the work order;
- follows project-local rules and the existing Grok lifecycle;
- re-observes/re-orients if material reality changes during execution;
- assesses documentation impact before handoff;
- does not gain merge, promotion, or capital authority from OODA.

### Git/GitHub
- durable implementation and review boundary;
- branch/PR state remains authoritative for code changes.

### OODA Control Room / Agent Ops Monitor
- derived display/freshness/control-room layer;
- helps humans and the Controller observe projects cheaply;
- not a source of truth, certifier, or merge authority.

## OODA is embedded at each layer

### Observe

Cheap current truth comes from:

- `.ooda/project.json`;
- `PROJECT_STATE.md`;
- `AGENTS.md`;
- relevant domain/architecture/process docs;
- active work orders/traces;
- Git/PR/tests/artifacts.

### Orient

The Controller/worker selects one role, one profile, normally ≤3 lenses, claim level, and the uncertainty/risk that matters.

### Decide

One bounded objective is selected because it has the best current information/value relative to broader work.

### Act

The worker executes inside explicit scope/verification/budget/stop/authority boundaries and feeds the result back through a trace.

Faster OODA is achieved by smaller context, clearer current state, tighter missions, early re-orientation, and durable feedback—not by mechanically adding paperwork.

## Work-order construction pattern

The Controller owns work-order construction, but does not have unlimited context.

```text
raw thought
   |
   v
Controller can bound it from compact state?
       /                     \
     yes                      no
      |                        |
      v                        v
work order            orientation spike
                      (existing worker role)
                               |
                               v
                      concise evidence/constraints
                               |
                               v
                           Controller
                               |
                               v
                           work order
```

This avoids a separate permanent work-order-builder bot while preserving planning quality.

## Documentation stewardship

Documentation is part of bounded completion when a change materially alters durable understanding.

Before handoff, the active worker asks whether the mission changed:

- domain concepts/entities;
- architecture/component boundaries;
- data/process/authority flows;
- interfaces/contracts;
- user/operator workflows;
- research methodology/evidence gates;
- public commands/configuration.

If not, record `documentation impact: none` and move on.

If yes, update the smallest durable artifact. Use an `architect` review for substantial structural diagrams/models and a `validator` check when accuracy is consequential. Do not create a permanent documentation-auditor role for routine changes.

See `docs/DOCUMENTATION_STEWARDSHIP.md`.

## Session pattern

For a typical current mission:

1. Discuss freely with ChatGPT and/or the Controller.
2. Controller decides whether the idea has earned worker resources.
3. If missing orientation evidence prevents a robust work order, run a short spike first.
4. Controller proposes/creates one OODA work order.
5. Start one Grok worker session in the target project.
6. Use the project's existing `/start` behavior.
7. Run `/ooda <work-order>`.
8. Worker executes one substantial bounded unit, re-observing on surprises.
9. Worker assesses documentation impact and uses the project's current `/handoff` convention.
10. ChatGPT/Lawrence review.
11. Persist a concise OODA trace after the outcome is known.
12. Controller re-observes the trace/gate and selects the next move.

## Correction loops

A correction is not automatically a new mission. If the same objective remains valid and the correction is bounded, resume/continue. If the objective, authority, protected scope, claim level, or architecture materially changes, create a new work order.

## What V1 deliberately does not automate yet

- autonomous deep planning inside the Controller;
- unrestricted repo/web crawling by the Controller;
- automatic consequential dispatch;
- automatic merge;
- model promotion;
- live trading;
- dashboard certification authority;
- Raspberry Pi scheduling;
- multi-provider autonomous routing.

The Control Room may refresh automatically and future collectors may automate observation. Judgment/dispatch automation should be earned from real OODA usage.
