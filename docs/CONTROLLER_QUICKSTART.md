# OODA Controller Quickstart

## Install / update OODA

From `~/repos/ooda` on the OODA branch/version you want to use:

```bash
bash install.sh
```

This installs/symlinks:

```text
ooda
/ooda
/ooda-controller
```

The install is idempotent when the expected symlinks already exist. Internal install scripts remain available under `scripts/`, but normal users should not need them.

## Start a Controller conversation

Start Grok using the same bounded runtime you already use:

```bash
grok-safe
```

Then invoke:

```text
/ooda-controller
```

or provide an initial thought directly:

```text
/ooda-controller I think Tenniskal may be over-focusing on trade intensity. Help me decide whether this deserves a new research spike.
```

The Controller does **not** automatically turn every thought into work.

## Typical conversations

### Raw idea / Intake

```text
/ooda-controller What if we add a browser extension that records prediction-market snapshots while I browse?
```

Expected Controller outcome:

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

You can ask the Controller to turn an approved idea into an execution contract:

```text
/ooda-controller We have decided to build the first browser-extension vertical slice. Construct the smallest robust mission for it.
```

The Controller should return or create fields for:

```text
project
objective
role
profile
lenses
claim level
allowed scope
forbidden scope
verification
budget
stop conditions
authority
documentation impact
why this move now
```

If it cannot bound the task without deep facts, it should **not** load the entire repo itself. It should say what evidence is missing and propose a short orientation spike first.

Example:

```text
PROPOSE MISSION
orientation spike:
  role: architect
  profile: browser-extension
  objective: Inspect only the current extension entrypoints/data flow and return the minimum interface constraints needed to bound the vertical-slice mission.
  output: concise constraints + candidate boundary
```

After that spike returns, the Controller constructs the final execution mission.

This is why we do not need a separate permanent work-order-builder bot.

### Cross-project control

```text
/ooda-controller What actually needs my attention right now?
```

Expected answer is a short human-gate / blocked / active-mission view, not repository archaeology.

### Specific project

```text
/ooda-controller Crypto-Innout is accruing data. Should we send another worker in or leave it alone?
```

The Controller checks compact current state. If deep evidence is needed to answer, it proposes a `researcher`, `validator`, or other worker mission rather than doing the research itself.

## OODA inside the Controller

The Controller uses OODA compactly:

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

The Controller proposes a mission. The worker remains a separate bounded Grok session:

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

Examples that often deserve a documentation target:

- new subsystem/component boundary -> architecture diagram;
- new domain entities/relationships -> domain model/glossary;
- new data/process/authority flow -> process/data-flow diagram;
- new operator/user workflow -> flow + operating guide;
- new CLI/configuration -> command cheat sheet/examples;
- new research method/evidence gate -> methodology/validation note.

The executing worker reassesses impact before handoff.

For broad structural changes, an `architect` may review the structure/diagram. For consequential consistency checks, a `validator` may audit the documentation against implementation/evidence.

Do not create documentation for every local code change, and do not create a permanent documentation-auditor role. See `docs/DOCUMENTATION_STEWARDSHIP.md`.

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
- **HUMAN GATE** — Lawrence/ChatGPT must review or authorize something first.
- **NO ACTION** — let current work/accrual continue; do not create busywork.

## Key boundaries

> **Think enough to route. Delegate anything that needs evidence or implementation.**

> **When mission construction needs deep facts, dispatch orientation first instead of expanding Controller context.**
