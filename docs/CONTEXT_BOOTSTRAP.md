# Context Bootstrap Contract

OODA chats are disposable working rooms. Durable project truth lives in repositories, PRs, committed state files, research artifacts, and OODA work orders/traces.

The bootstrap contract exists so a human can enter a new ChatGPT conversation with very little context and still recover the right project state quickly.

## Minimal input

For an existing project, the human should usually provide only:

- repository or project name;
- immediate intent;
- optional PR/task/branch identifier when relevant.

Examples:

```text
Jump into example-org/research-project. Goal: decide the next research move. Use OODA. Do not execute yet.
```

```text
Review example-app PR #31 under OODA.
```

```text
Jump into analytics-project. Revisit the current valuation/model-risk question.
```

For a new idea:

```text
New project idea: a browser extension that analyzes a workflow while I browse. OODA it with me. Do not build yet.
```

## Bootstrap behavior

The assistant/controller should:

1. identify the repository or confirm the idea is new;
2. establish current Git/PR/repository truth;
3. load only the minimum durable state needed for the immediate intent;
4. separate observed facts from interpretation;
5. surface the current objective, gate/blocker, and materially relevant recent change;
6. remain discussion-only until execution is explicitly chosen;
7. create a work order only when the idea has earned agent time.

## Default state-source priority

Use the narrowest relevant combination of:

1. `.ooda/project.json` for routing/authority metadata;
2. `AGENTS.md` for standing project operating rules;
3. `PROJECT_STATE.md` or equivalent current-state file;
4. the specific PR/issue/branch/task named by the user;
5. the latest directly relevant report or research artifact;
6. recent commits only when needed to resolve what changed.

Do not read the entire repository, all historical docs, all PRs, or old conversations by default.

## Bootstrap output

A concise bootstrap should normally report:

```text
PROJECT
CURRENT TRUTH
CURRENT OBJECTIVE
OPEN GATE / BLOCKER
MATERIAL RECENT CHANGE
RECOMMENDED NEXT OODA MOVE
```

The output is orientation, not permission to act.

## Local-only exception

If material work exists only on the user's machine and is not committed/pushed, request or accept a tiny local-state card instead of a terminal transcript:

```text
LOCAL STATE
repo: example-project
branch: agent/fix-recovery
HEAD: abc123
dirty: yes
task: repair duplicate writer recovery
tests: focused suite green
important: not pushed yet
```

## Principle

**Chat history is optional context. Durable repository state is authoritative context.**
