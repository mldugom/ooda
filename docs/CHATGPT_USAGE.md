# ChatGPT Usage

This is the human-facing entrypoint to OODA. Lawrence should not need giant handoffs or long-lived chats to resume work.

## Four default prompts

### Jump into an existing project

```text
Jump into tenniskal. Use OODA. Goal: <goal>.
```

ChatGPT should bootstrap from durable repo truth, report current orientation, and stay discussion-only unless Lawrence asks to execute.

### Resume specific work

```text
Continue tenniskal PR #18. Use current repo truth, not old chat state.
```

Prefer a PR/issue/branch identifier over pasting large transcripts.

### Review Grok work

```text
Review crypto-innout PR #31 under OODA.
```

ChatGPT should inspect the actual diff/evidence and challenge scope, correctness, scientific claims, architecture, and authority.

### Start a new idea

```text
New project idea: <idea>. OODA it with me. Do not build yet.
```

Stay in free-form Lawrence + ChatGPT exploration until the idea earns execution resources.

## Conversation hygiene

Use fresh chats aggressively. A conversation is a working room, not permanent project memory.

Good durable state lives in:

- Git/GitHub;
- `AGENTS.md`;
- `PROJECT_STATE.md` or equivalent;
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

## Review boundary

Current default:

```text
Lawrence + ChatGPT
    -> OODA work order
    -> existing Grok Build execution
    -> Git/PR/handoff
    -> ChatGPT + Lawrence review
    -> OODA trace
```

Grok does not gain merge, promotion, or live-capital authority merely because a task uses OODA.
