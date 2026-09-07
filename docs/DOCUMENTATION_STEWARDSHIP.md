# Documentation Stewardship

Documentation is part of the product/research surface, not a separate afterthought or a permanent bot role.

The goal is to preserve the few durable explanations that let a fresh human or agent understand the domain, architecture, process, interfaces, and operating rules without replaying chat history or reverse-engineering the codebase.

## Core rule

> If a substantial change alters how the system is understood, operated, extended, validated, or reasoned about, the work is not fully handed off until documentation impact has been assessed.

This does **not** mean every code change creates documentation.

## Who owns documentation?

Documentation is a cross-cutting completion obligation.

- The active `engineer`, `researcher`, `product-strategist`, `trader`, or other worker first assesses documentation impact as part of the bounded mission.
- An `architect` should own or review durable structure when a change introduces or materially changes a subsystem, domain model, interface boundary, data flow, process flow, or architecture decision.
- A `validator` can act as the independent documentation auditor when the documentation must be checked against implementation/evidence, especially for consequential or broad changes.
- The `controller` only decides whether documentation work is warranted and whether it belongs inside the current mission or requires a small follow-up mission. It should not read the whole codebase to write documentation itself.

Do not create a permanent `documentation-auditor` role merely to enforce this policy.

## Documentation impact gate

Before handoff, ask:

1. Did the change alter a domain concept, architectural boundary, interface, control flow, data flow, operator workflow, research methodology, public command, invariant, or decision process?
2. Would a capable new contributor misunderstand the system without an updated diagram/overview/reference?
3. Did we learn something durable that will prevent repeated archaeology or repeated failed experiments?
4. Did a new CLI/configuration/operational process appear that deserves a cheat sheet or example?
5. Did an existing document become materially false or misleading?

If all answers are **no**, record `documentation impact: none` in the handoff/trace and move on.

If any answer is **yes**, update the smallest durable artifact that fixes the gap.

## What deserves durable documentation?

| Change | Preferred durable artifact |
|---|---|
| New subsystem, service, data pipeline, agent topology, or major boundary | Architecture/domain overview + simple diagram |
| Important domain concepts or entities | Domain model / glossary / relationship diagram |
| New or materially changed user/operator workflow | Process-flow diagram + short operating guide |
| New CLI, commands, flags, configuration, or recurring procedure | README cheat sheet / command reference / examples |
| New interface or contract between components | Interface/contract document with inputs, outputs, invariants |
| New scientific/research method or evidence gate | Methodology/validation note + claim/stop criteria |
| Material authority/safety invariant | `AGENTS.md`, policy, or project-specific invariant document |
| Material current-state/gate change | `PROJECT_STATE.md` |
| Durable negative result or failed path worth not repeating | OODA trace and relevant research-state/catalog reference |
| Minor refactor, local bug fix, test-only change with no conceptual effect | Usually no new documentation |

## Prefer diagrams that answer a question

Do not draw diagrams decoratively. A diagram should reduce ambiguity about one of:

- **domain:** what entities/concepts exist and how they relate;
- **architecture:** what components exist and what crosses boundaries;
- **process:** what sequence/gates/actions move work forward;
- **data:** where data originates, transforms, persists, and is consumed;
- **authority:** who/what may decide, execute, approve, or promote;
- **research:** how discovery becomes evidence and possibly qualification.

ASCII/Mermaid-style diagrams in Markdown are preferred when sufficient because they remain diffable and easy for agents to read.

## Documentation review pattern

Use the cheapest sufficient pattern:

```text
bounded implementation/research
        |
        v
worker assesses documentation impact
        |
     none? ------ yes -----> handoff
        |
       no
        v
update smallest durable doc
        |
   structural / broad?
     /          \
   no            yes
   |              |
worker verifies   architect reviews structure
                  |
            consequential / uncertain?
                  |
             validator checks truth
                  |
                  v
               handoff
```

Architect + Validator is **not** required for every change. Use them when the conceptual surface or downside justifies the extra review.

## Work-order guidance

When documentation impact is already foreseeable, include it in allowed scope and verification.

Example:

```text
allowed scope:
- implement the new ingestion boundary
- update docs/ARCHITECTURE.md data-flow diagram if the boundary changes

verification:
- tests pass
- architecture diagram matches final implementation
- README command example still works
```

When impact is unknown until implementation, the worker assesses it before `/handoff`.

## Trace / handoff guidance

A useful handoff or trace should record one of:

```text
DOCUMENTATION: none — behavior/interface/domain model unchanged
```

or:

```text
DOCUMENTATION:
- updated docs/ARCHITECTURE.md for new ingestion boundary
- added README command example
- validator checked diagram against final interfaces
```

This provides an audit signal without turning documentation into ceremony.

## Anti-patterns

Avoid:

- chronological documentation dumps that duplicate Git history;
- diagrams that are never updated because they are too elaborate;
- one document per feature regardless of conceptual value;
- using an architect merely as a technical writer;
- requiring independent doc audits for trivial changes;
- allowing substantial architecture/process changes to exist only in code or chat.

## Design principle

> Document durable understanding, not activity.
