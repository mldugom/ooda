# OODA Controller Quickstart

## Install / update OODA

Pip from GitHub:

```bash
python3 -m pip install "git+https://github.com/mldugom/ooda.git"
ooda setup
```

Or from a clone:

```bash
git clone https://github.com/mldugom/ooda.git
cd ooda
bash install.sh
```

Both paths provide:

```text
ooda
grok-safe
/ooda
/ooda-controller
```

## Start a Controller conversation

From a target repo:

```bash
grok-safe
```

Then:

```text
/ooda-controller
```

or provide an initial thought:

```text
/ooda-controller I think this project may be focusing on the wrong user workflow. Help me decide whether this deserves a discovery spike.
```

The Controller does **not** automatically turn every thought into work.

## Typical conversations

### Raw idea / Intake

```text
/ooda-controller What if we add a lightweight browser workflow for this problem?
```

Expected outcome may be:

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

### Robust mission construction

```text
/ooda-controller We have decided to build the first vertical slice. Construct the smallest robust mission for it.
```

The Controller should return or create fields for project, objective, role, profile, lenses, claim level, allowed/forbidden scope, verification, budget, stop conditions, authority, documentation impact, and why this move now.

If it cannot bound the task without deep facts, it should **not** load the entire repo itself. It should identify the missing evidence and propose a short orientation spike first.

Example:

```text
PROPOSE MISSION
orientation spike:
  role: architect
  profile: full-stack
  objective: Inspect only the current entrypoints/data flow and return the minimum interface constraints needed to bound the vertical-slice mission.
  output: concise constraints + candidate boundary
```

After the spike returns, the Controller constructs the final execution mission.

This is why OODA does not need a separate permanent work-order-builder bot.

### Cross-project control

```text
/ooda-controller What actually needs my attention right now?
```

Expected answer is a short human-gate / blocked / active-mission view, not repository archaeology.

### Specific project

```text
/ooda-controller This project is currently collecting evidence. Should we send another worker in or leave it alone?
```

The Controller checks compact current state. If deep evidence is needed, it proposes an appropriate worker mission rather than doing the research itself.

## OODA inside the Controller

```text
OBSERVE
read compact current control truth
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
construct mission / request orientation spike / surface gate / do nothing
    |
    v
RE-OBSERVE
from worker trace, PR, or new human decision
```

It should not make the loop slower by producing ceremonial analysis.

## When a worker is warranted

```text
CONTROLLER
    |
    | proposes/creates mission
    v
PROJECT WORKER
    |
  grok-safe
  /start
  /ooda .ooda/work-orders/<task>.json
    |
  /handoff
    v
TRACE / HUMAN REVIEW
    |
    v
CONTROLLER re-observes
```

Keeping the worker separate protects the Controller's small context surface.

## Documentation stewardship

The Controller should include documentation in a mission only when the change is likely to alter durable understanding.

Examples:

- new subsystem/component boundary -> architecture diagram;
- new domain entities/relationships -> domain model/glossary;
- new data/process/authority flow -> process/data-flow diagram;
- new operator/user workflow -> flow + operating guide;
- new CLI/configuration -> command cheat sheet/examples;
- new research method/evidence gate -> methodology/validation note.

The executing worker reassesses impact before handoff. An `architect` may review substantial structural documentation; a `validator` may independently audit consequential truth/consistency.

Do not create documentation for every local code change, and do not create a permanent documentation-auditor role.

## What the Controller may read

Normally:

- `.ooda/project.json` / registry metadata;
- concise project-state summaries;
- active missions/work orders;
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
- **PROPOSE MISSION** — one bounded worker mission is worth doing.
- **HUMAN GATE** — a human/ChatGPT decision or authorization is required first.
- **NO ACTION** — let current work/accrual continue; do not create busywork.

## Key boundaries

> **Think enough to route. Delegate anything that needs evidence or implementation.**

> **When mission construction needs deep facts, dispatch orientation first instead of expanding Controller context.**
