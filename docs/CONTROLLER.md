# OODA Controller — Thin Portfolio Control Agent

The OODA Controller is a **thin portfolio/control agent**, not a research or engineering worker.

Its purpose is to keep Lawrence + ChatGPT out of repetitive repository archaeology while also preventing a master agent from accumulating every project's code, data, and research context.

## Controller context budget

The Controller normally reads only:

1. project registry / `.ooda/project.json` metadata;
2. a very small current-state summary per project;
3. active OODA work orders;
4. latest useful trace per project;
5. unresolved human gates;
6. Git/PR status relevant to active missions;
7. freshness / blocker state.

It does **not** normally read source trees, datasets, long research histories, raw logs, or full PR diffs.

## Controller job

```text
OBSERVE portfolio state
        |
        v
ORIENT which project / mission needs attention
        |
        v
DECIDE next bounded role + profile + lenses + claim level
        |
        v
CREATE / SELECT OODA WORK ORDER
        |
        v
DISPATCH RECOMMENDATION
        |
        v
WORKER AGENT loads project-specific context and executes
        |
        v
HANDOFF / PR / TRACE
        |
        v
CONTROLLER RE-OBSERVES
        |
        v
HUMAN / CHATGPT GATE when required
```

## Authority

The Controller may recommend and route bounded work. By default it may not:

- perform deep research itself when a worker can be dispatched;
- silently expand a mission;
- merge or force-push protected refs;
- certify research/model claims;
- modify live systems or capital;
- bypass project-local authority;
- convert stale dashboard state into project truth.

## Sessions are disposable

The Controller should feel persistent to the human operator, but its chat/session is **not** durable memory.

A Controller session may be restarted at any time and reconstruct its state from compact durable artifacts. This prevents an immortal chat from accumulating stale assumptions, irrelevant code context, and excessive token cost.

```text
Controller session A ----\
Controller session B -----+--> same compact durable control state
Controller session C ----/
```

## Worker boundary

When the next move requires research, code inspection, web research, implementation, validation, or detailed PR review, the Controller should create/select a bounded work order and hand it to the appropriate worker.

Examples:

- research spike -> `researcher` worker;
- system design -> `architect` worker;
- implementation -> `engineer` worker;
- independent challenge -> `validator` worker;
- execution realism -> `trader` worker;
- portfolio allocation -> `portfolio-manager` worker;
- tail/ruin review -> `risk-manager` worker.

The worker loads the **mission-specific** context that the Controller deliberately did not carry.

## Control Room / dashboard relationship

The dashboard is the Controller's human-readable observation surface.

It should prioritize:

- project;
- current objective;
- OODA stage;
- active work order;
- role/profile/lenses;
- claim level;
- worker/provider;
- branch/PR when relevant;
- latest trace/result;
- blocker;
- human gate;
- freshness.

The dashboard remains derived state. Git, project artifacts, work orders, traces, and explicit human decisions remain authoritative.

## Design rule

> Keep the Controller broad enough to choose the next mission, but too context-poor to become the worker.
