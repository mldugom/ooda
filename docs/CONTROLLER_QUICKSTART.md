# OODA Controller Quickstart

## Install

Clone path:

```bash
git clone https://github.com/mldugom/ooda.git
cd ooda
bash install.sh
```

Or pip from GitHub:

```bash
python3 -m pip install "git+https://github.com/mldugom/ooda.git"
ooda setup
```

Both paths provide `ooda`, `grok-safe`, `/ooda`, and `/ooda-controller` after setup.

## Start one Controller conversation

From a target repo:

```bash
grok-safe
```

Then:

```text
/ooda-controller
```

or:

```text
/ooda-controller I think this project may be focusing on the wrong user workflow. Help me decide whether this deserves a discovery spike.
```

The Controller does **not** automatically turn every thought into work.

## Preferred one-window flow

```text
CONTROLLER
raw thought
    |
    v
PROPOSE / CONSTRUCT MISSION
    |
    | execution authorized
    v
INLINE CHILD WORKER
isolated deep context
    |
    v
concise result / evidence / trace
    |
    v
CONTROLLER re-observes
```

You do not need a separate terminal for every worker. The child remains context-isolated even when it appears nested under the Controller session.

Default to one active child mission at a time. Use separate sessions/worktrees only when duration, concurrency, isolation, or independent review makes them materially useful.

## Raw idea / Intake

```text
/ooda-controller What if we add a lightweight browser workflow for this problem?
```

Possible outcome:

```text
KEEP THINKING
```

or:

```text
PROPOSE MISSION
project: <existing or proposed>
role: product-strategist
profile: browser-extension
lenses: product-user, value-of-information, stanley-lehman
claim: discovery
objective: <bounded product discovery objective>
```

## Robust mission construction

```text
/ooda-controller We have decided to build the first vertical slice. Construct the smallest robust mission for it.
```

The Controller should create/propose project, objective, role, profile, lenses, claim level, allowed/forbidden scope, verification, budget, stop conditions, authority, documentation impact, and why this move now.

If it cannot bound the task without deep facts, it should dispatch a short orientation child first rather than loading the whole repo itself.

Example:

```text
orientation child:
  role: architect
  profile: full-stack
  objective: Inspect only the current entrypoints/data flow and return the minimum interface constraints needed to bound the vertical-slice mission.
  output: concise constraints + candidate boundary
```

After the child returns, the Controller constructs the final execution mission.

## Inline execution

Once the mission is explicit and execution is authorized, the Controller may dispatch one child worker directly in the same Grok session.

The child should:

- receive the work order plus minimum task context;
- own deep code/research/data context;
- obey mission scope, authority, budget, and stops;
- verify the result;
- return a concise handoff/evidence summary;
- persist useful trace/handoff state before a materially different mission begins.

The Controller should not absorb the child's full transcript.

## Cross-project control

```text
/ooda-controller What actually needs my attention right now?
```

Expected answer is a short human-gate / blocked / active-mission view, not repository archaeology.

## OODA inside the Controller

```text
OBSERVE
compact current control truth
    |
    v
ORIENT
project + role/profile/lenses + key uncertainty
    |
    v
DECIDE
KEEP THINKING / PROPOSE MISSION / HUMAN GATE / NO ACTION
    |
    v
ACT
construct / dispatch mission / surface gate / do nothing
    |
    v
RE-OBSERVE
from child result, trace, PR, or human decision
```

## What the Controller normally reads

- `.ooda/project.json` / registry metadata;
- concise project-state summaries;
- active work orders;
- latest useful traces;
- human gates;
- relevant PR state;
- freshness/blockers.

Normally not:

- full source trees;
- raw datasets;
- long research reports;
- broad web research;
- full PR diffs;
- worker transcripts.

## Controller outcomes

- **KEEP THINKING** — stay conversational; do not spend worker resources yet.
- **PROPOSE MISSION** — one bounded worker mission is worth doing and may be dispatched inline after authorization.
- **HUMAN GATE** — a human/ChatGPT decision or authorization is required first.
- **NO ACTION** — let current work/accrual continue; do not create busywork.

## Session durability

Keep the Controller open while it is useful. Restart whenever context becomes large or stale.

The restart is cheap because project state, work orders, traces, Git/PR state, and explicit human decisions are the durable memory.

## Key boundaries

> **Think enough to route. Delegate anything that needs deep evidence or implementation.**

> **One Controller UI does not mean one context. Inline child workers keep deep task context isolated.**
