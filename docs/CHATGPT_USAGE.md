# ChatGPT Usage

This is the human-facing entrypoint to OODA. Lawrence should not need giant handoffs or long-lived chats to resume work.

ChatGPT remains the creative/strategic counterpart. The OODA Controller is the thin control/portfolio counterpart that helps turn approved intent into bounded worker missions without forcing ChatGPT to carry every repo's operational context.

## Four default prompts

### Jump into an existing project

```text
Jump into tenniskal. Use OODA. Goal: <goal>.
```

ChatGPT should bootstrap from durable repo truth, report current orientation, and stay discussion-only unless Lawrence asks to execute.

When the next step becomes execution planning, ChatGPT may hand the compact intent to the OODA Controller for routing/work-order construction instead of doing repo archaeology itself.

### Resume specific work

```text
Continue tenniskal PR #18. Use current repo truth, not old chat state.
```

Prefer a PR/issue/branch identifier over pasting large transcripts.

### Review Grok work

```text
Review crypto-innout PR #31 under OODA.
```

ChatGPT should inspect the actual diff/evidence and challenge scope, correctness, scientific claims, architecture, documentation impact, and authority.

### Start a new idea

```text
New project idea: <idea>. OODA it with me. Do not build yet.
```

Stay in free-form Lawrence + ChatGPT exploration until the idea earns execution resources.

## ChatGPT ↔ Controller interaction

Use the Controller when a thought has moved from exploration toward operational routing.

```text
LAWRENCE + CHATGPT
free-form thought / strategy
        |
        | idea has earned execution?
        v
OODA CONTROLLER
intake / orient / construct work order
        |
        | missing deep facts?
        +------> orientation spike worker
        |             |
        |<------------+
        v
bounded work order
        |
        v
worker
```

ChatGPT does not have to manually inspect every codebase just to construct the next task. The Controller should use compact state and, when necessary, request a small researcher/architect/validator/product-strategist spike to obtain missing orientation evidence.

There is no default permanent `work-order-builder` bot. Work-order construction is a Controller capability; deep mission design is delegated under an existing substantive role when needed.

## Conversation hygiene

Use fresh chats aggressively. A conversation is a working room, not permanent project memory.

Good durable state lives in:

- Git/GitHub;
- `AGENTS.md`;
- `PROJECT_STATE.md` or equivalent;
- stable domain/architecture/process documentation;
- `.ooda/project.json`;
- PRs/issues;
- research artifacts;
- OODA work orders and traces.

Do not preserve context merely because it was expensive to create. Persist the useful conclusion instead.

## When to create a work order

Create one only when:

- a concrete agent action is worth spending resources on;
- the objective is sufficiently clear to bound;
- authority and protected scope can be stated;
- there is a useful success/verification condition.

Do not create work orders for ordinary brainstorming.

If the objective cannot be bounded because important evidence is missing, create a **small orientation spike** rather than a vague large implementation task.

## OODA inside work selection

A good transition from thought to work should feel like:

```text
OBSERVE
What is currently true / what do we already know?
        |
        v
ORIENT
What uncertainty matters? Which role/profile/lenses should look at it?
        |
        v
DECIDE
What is the smallest move worth resources now?
        |
        v
ACT
Execute bounded work and verify it.
```

The purpose is faster useful feedback, not more ceremony.

## Documentation review

When reviewing substantial work, ask whether the change created a durable explanation gap.

Examples:

- new subsystem -> architecture diagram/overview;
- new domain concepts -> domain model/glossary;
- new data/process/authority flow -> flow diagram;
- new CLI/config -> cheat sheet/examples;
- new research/evidence method -> methodology note;
- material negative result -> trace/research-state reference.

The worker first assesses documentation impact. Use an architect for broad structural documentation review and a validator when independent truth-checking is justified. Do not require an extra documentation bot for routine changes.

See `docs/DOCUMENTATION_STEWARDSHIP.md`.

## Review boundary

Current default:

```text
Lawrence + ChatGPT
    -> OODA Controller intake/work-order construction
    -> existing Grok Build worker execution
    -> Git/PR/handoff
    -> ChatGPT + Lawrence review
    -> OODA trace
    -> Controller re-observes
```

Grok does not gain merge, promotion, or live-capital authority merely because a task uses OODA.
