# Future Repository Watcher

A future OODA control-plane component may continuously observe an operator-configured allowlist of repositories, commits, PRs, and selected project-state changes.

This is intentionally **not** part of the initial OODA execution path. First prove the manual contracts.

## Purpose

The watcher should answer:

- what changed across active repositories?;
- which projects have stale or conflicting durable state?;
- which PRs or branches need human/ChatGPT review?;
- which OODA missions completed, stalled, or changed orientation?;
- which project should the Controller consider next?

It should not silently decide consequential work, merge code, promote models, or trade capital.

## Minimal future architecture

```text
GitHub repositories
  commits / PRs / issues / selected files
                |
                v
         OODA repo watcher
                |
       normalize + checkpoint
                |
        local event/state store
                |
       +--------+---------+
       |                  |
       v                  v
   Control Room       OODA Controller
 display/freshness    candidate next moves
       |                  |
       +--------+---------+
                v
          human/ChatGPT gate
```

## Recommended first implementation

For a local always-on host, prefer simple GitHub API polling over a public webhook service:

1. keep a configured allowlist of active repositories;
2. poll repository HEADs, open PRs, and recent commits at a modest interval;
3. store only cursors/last-seen SHAs and normalized events;
4. fetch project state files only when their SHA changes;
5. emit monitor state and candidate alerts;
6. require human/ChatGPT approval before dispatching new consequential work.

Polling is less elegant than webhooks but fits a private local host without requiring an internet-exposed receiver. Webhooks can replace polling later if a stable endpoint becomes worthwhile.

## What it should watch first

- default-branch HEAD changes;
- open/updated PRs;
- `.ooda/project.json` changes;
- `PROJECT_STATE.md` / current-state file changes;
- OODA work-order/trace additions;
- explicit human-review gates.

Do not begin by indexing every file or every commit diff across every repository.

## Event example

```json
{
  "repo": "example-org/example-project",
  "kind": "default_branch_advanced",
  "old_sha": "...",
  "new_sha": "...",
  "observed_at": "...",
  "needs_orientation": true
}
```

## Safety boundary

Watcher authority is observation only by default.

A later Controller may recommend or dispatch low-consequence work only after repeated manual usage proves the routing rules. Merge, model promotion, live runtime changes, and capital deployment remain explicit authority gates.

## Principle

**Automate observation before automating judgment.**
