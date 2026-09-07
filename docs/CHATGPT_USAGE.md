# ChatGPT Usage

This is the human-facing entrypoint to OODA. You should not need giant handoffs or long-lived chats to resume work.

## Four default prompts

### Jump into an existing project

```text
Jump into <repo>. Use OODA. Goal: <goal>.
```

ChatGPT should bootstrap from durable repo truth, report current orientation, and stay discussion-only unless the human asks to execute.

### Resume specific work

```text
Continue <repo> PR #<n>. Use current repo truth, not old chat state.
```

Prefer a PR/issue/branch identifier over pasting large transcripts.

### Review agent work

```text
Review <repo> PR #<n> under OODA.
```

ChatGPT should inspect the actual diff/evidence and challenge scope, correctness, scientific claims, architecture, documentation impact, and authority.

### Start a new idea

```text
New project idea: <idea>. OODA it with me. Do not build yet.
```

Stay in free-form human + ChatGPT exploration until the idea earns execution resources.

## Controller relationship

The OODA Controller is a thin third chair for:

- raw-thought intake;
- deciding whether an idea has earned agent resources;
- constructing/proposing bounded missions;
- choosing role/profile/lenses/claim level;
- surfacing blockers and human gates;
- re-orienting from worker traces.

It should not absorb deep code/research/web/data context. If robust mission construction requires deeper facts, it proposes a short orientation spike to the appropriate worker first.

## When to create a mission

Create one only when:

- a concrete agent action is worth spending resources on;
- the objective is sufficiently clear to bound;
- authority and protected scope can be stated;
- there is a useful success/verification condition.

Do not create missions for ordinary brainstorming.

```bash
ooda mission \
  "<one bounded objective>" \
  --role <role> \
  --profile <profile> \
  --claim <discovery|evidence|qualification|n-a> \
  [--lenses lens1,lens2,lens3] \
  [--id TASK-01]
```

The durable schema remains `ooda/work-order/v1`; `mission` is the human-facing name.

## Conversation hygiene

Use fresh chats aggressively. A conversation is a working room, not permanent project memory.

Good durable state lives in Git/GitHub, `AGENTS.md`, `PROJECT_STATE.md` or equivalent, `.ooda/project.json`, PRs/issues, earned domain/architecture/process documentation, research artifacts, and OODA missions/traces.

Persist useful conclusions rather than retaining context merely because it was expensive to create.

## Review boundary

```text
HUMAN + CHATGPT
    -> OODA Controller / mission construction
    -> bounded worker execution
    -> Git/PR/handoff
    -> human + ChatGPT review
    -> OODA trace
```

A worker does not gain merge, promotion, or live-capital authority merely because a task uses OODA.

## Documentation impact during review

When a worker changes substantial domain concepts, subsystem boundaries, process/data/control flow, interfaces, methodology, or operator behavior, review whether a durable diagram/model/cheat sheet/process guide should be updated.

Do not create documentation for activity alone. See `docs/DOCUMENTATION_STEWARDSHIP.md`.
