# OODA Controller Quickstart

## Install / update the Grok skills

From `~/repos/ooda` on the OODA branch/version you want to use:

```bash
./scripts/install-grok.sh
```

This installs/symlinks both:

```text
/ooda
/ooda-controller
```

If `/ooda` is already the expected symlink, the installer leaves it alone and continues to install `/ooda-controller`.

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

## When a worker is warranted

The Controller proposes a work order. The worker remains a separate bounded Grok session:

```text
CONTROLLER
    |
    | proposes/creates work order
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

## What the Controller may read

Normally:

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
- **PROPOSE MISSION** — one bounded worker mission is worth doing.
- **HUMAN GATE** — Lawrence/ChatGPT must review or authorize something first.
- **NO ACTION** — let current work/accrual continue; do not create busywork.

## Key boundary

> **Think enough to route. Delegate anything that needs evidence or implementation.**
