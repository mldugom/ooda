# OODA

**A provider-neutral control system for bounded AI-assisted research, engineering, product work, and consequential decisions.**

> Think broadly. Orient quickly. Act narrowly. Verify reality. Preserve what matters.

Git/project artifacts are durable truth. Controller chats, child workers, terminal views, and dashboards are replaceable views.

## Install

Recommended:

```bash
mkdir -p ~/repos
cd ~/repos
git clone https://github.com/mldugom/ooda.git
cd ooda
bash install.sh
```

This installs:

```text
ooda
grok-safe
/ooda
/ooda-controller
```

Commands live under `~/.local/bin`. If that directory was not already on `PATH`, the installer updates your shell startup file and prints the `export PATH=...` line needed for the current terminal.

Verify:

```bash
ooda help
grok-safe --help
```

Pip-from-GitHub also works:

```bash
python3 -m pip install "git+https://github.com/mldugom/ooda.git"
ooda setup
```

The distribution name is `ooda-ai`; there is no PyPI release yet.

## Commands

| Command | Purpose |
|---|---|
| `ooda setup` | Install bundled Grok skills/policy after pip install. |
| `ooda init` | Adopt or scaffold a repo. |
| `ooda doctor` | Validate project/contracts. |
| `ooda mission` | Create one bounded mission/work order. |
| `ooda trace` | Record durable mission outcome/feedback. |
| `ooda view` | Render the project's objective ladder, decision timeline, and stakeholder summary in the shell. |
| `ooda dashboard` | Open the bundled local browser Control Room. |
| `grok-safe` | Launch Grok with OODA's bounded policy. |

Compatibility aliases such as `ooda work-order` and `ooda validate` remain but are not normal-use commands.

## One Controller, isolated child workers

```text
HUMAN + CHATGPT
raw thought / strategy
        |
        v
 OODA CONTROLLER
 Intake / Proposal / Control
        |
        | idea earns work
        v
 WORK ORDER / MISSION
 Observe -> Orient -> Decide
        |
        v
 INLINE CHILD WORKER
 isolated deep task context
        |
        v
 evidence / handoff / trace
        |
        v
 CONTROLLER RE-OBSERVES
```

A worker does **not** require another terminal window.

When Grok supports child agents, `/ooda-controller` may construct a bounded work order and dispatch one child worker inside the same Controller session. The child owns deep code/research/data context; the Controller should receive only the concise result needed to re-orient.

Default to one active child mission at a time. Use separate top-level sessions/worktrees only when duration, concurrency, isolation, or independent review materially justify them.

Keep a Controller open while useful. Restart it whenever context gets large or stale. Durable state—not chat history—is the memory.

## Adopt an existing repo

```bash
cd ~/repos/my-app

ooda init \
  --project-id my-app \
  --project-class software-product

ooda doctor

grok-safe
```

Then inside Grok:

```text
/ooda-controller Jump into this repo. Use only the minimum durable state needed to orient. Help me decide what deserves work next. If deeper evidence or implementation is needed, construct the smallest bounded mission and delegate it rather than absorbing the deep task context yourself.
```

For existing repos with useful docs, normally do **not** use `--scaffold`.

## Human-facing project view

Projects that benefit from a compact history of **why the project changed direction** may keep:

```text
.ooda/project-view.json
```

It contains:

- an objective/research ladder with exactly one current rung;
- a material decision timeline: `TIME | DECISION | SO WHAT | BIGGER IDEA`;
- a rolling stakeholder summary.

Downstream ladder rungs are provisional hypotheses/plans, not authorized future missions.

Render it in the shell:

```bash
ooda view
ooda view --all
```

The same object is available to `/ooda-controller` for `timeline`, `show timeline`, or `where are we`, and is rendered by the browser Control Room. See [`docs/PROJECT_VIEW.md`](docs/PROJECT_VIEW.md).

## Terminal and GUI surfaces

OODA deliberately has more than one view over the same durable state:

```text
Grok native TUI
  grok-safe
  /ooda-controller
  native Workflow/subagent panel when Grok provides it

OODA terminal view
  ooda view
  /ooda-controller where are we?
  /ooda-controller timeline

OODA browser view
  ooda dashboard
```

OODA does **not** patch or scrape Grok's native terminal chrome. Grok owns its TUI and Workflow panel; OODA owns the Controller/worker contracts and the durable project view rendered inside the conversation or through `ooda view`. The browser Control Room is a read-only companion over the same project state.

## Missions

Direct creation is available when you already know the bounded task:

```bash
ooda mission \
  "Inspect the current service boundary and return the minimum constraints needed for the next implementation slice" \
  --role architect \
  --profile api \
  --lenses product-user,reliability-systems \
  --claim n-a \
  --id ARCH-01
```

Default output:

```text
.ooda/work-orders/ARCH-01.json
```

A work order is the durable result of **Observe → Orient → Decide** and the control envelope for **Act**.

A standalone worker session remains available when useful:

```bash
grok-safe
```

```text
/start
/ooda .ooda/work-orders/ARCH-01.json
```

## Traces

```bash
ooda trace \
  --work-order .ooda/work-orders/ARCH-01.json \
  --result completed \
  --summary "Architecture orientation completed; returned the next bounded implementation boundary."
```

Trace states:

```text
completed
negative_finding
blocked
budget_exhausted
needs_human_gate
```

A trace is concise decision provenance and feedback, not chain-of-thought.

For material research/product/architecture/validation results, OODA workers and the Controller should distinguish:

```text
RESULT       factual/technical finding
SO WHAT      immediate practical implication
BIGGER IDEA  connection to the larger project objective
```

## `grok-safe`

`grok-safe` finds the Grok CLI from `GROK_BIN`, `~/.grok/bin/grok`, or your shell `PATH`, then adds OODA's bounded execution policy.

There is **no default global session-turn cap** because a Controller may remain open across multiple bounded missions. Mission/work-order budgets are the primary bounded unit.

For a deliberate hard session cap:

```bash
OODA_GROK_MAX_TURNS=12 grok-safe
```

Subagents are enabled so the Controller can use isolated child workers. OODA policy restricts broad fan-out and defaults to one Controller child mission at a time.

If Grok's user config explicitly contains `[workflows] enabled=false`, `grok-safe` warns because the Controller's inline workflow/subagent path may be unavailable. OODA does not rewrite that user setting.

For a strict session with child agents disabled:

```bash
OODA_GROK_NO_SUBAGENTS=1 grok-safe
```

## Control Room

The dashboard is bundled with OODA; no second repository is required.

```bash
ooda dashboard
```

It opens a local read-only Control Room, scans OODA-adopted repos under `~/repos`, and reconstructs compact state from `.ooda/project.json`, `PROJECT_STATE.md`, the latest work order/trace, optional `.ooda/project-view.json`, and local Git state.

The current Control Room shows projects as horizontal tabs, remembers the selected project across refreshes, and displays the stakeholder summary, current human/next gate, live OODA loop, objective ladder, latest material timeline pivots, and Git/controller/mission freshness. Its default browser refresh is **15 seconds**.

The launcher reuses a port only when the existing service identifies as the expected OODA Control Room. If the preferred port is occupied by another local service, OODA selects the next free local port.

Configuration:

```bash
OODA_PROJECTS_ROOT=/path/to/repos ooda dashboard
OODA_DASHBOARD_PORT=8899 ooda dashboard
OODA_DASHBOARD_REFRESH_SECONDS=30 ooda dashboard
```

The dashboard is derived observation state. It does not modify projects, certify results, merge code, or replace Git/project truth.

## Project cockpit direction

Do not turn the portfolio Control Room into a giant notebook/artifact warehouse. Analytical projects may earn a separate lightweight project cockpit with stable `Overview / Research / Live / Health` surfaces.

OODA should standardize the decision-useful interface while the project owns its domain analytics. No plot is required unless a visualization actually helps answer the current decision. See [`docs/PROJECT_COCKPIT.md`](docs/PROJECT_COCKPIT.md).

## Provider flavors

OODA core is provider-neutral even though Grok is the current reference execution flavor. Provider-specific concerns—launcher, terminal harness, child-context mechanism, model selection, effort, and quota—must not redefine work orders, traces, claim levels, human gates, or project truth.

The next-provider implementation is intentionally deferred until it is worth spending on. See [`docs/PROVIDER_FLAVORS.md`](docs/PROVIDER_FLAVORS.md).

## New repo starter pack

```bash
mkdir -p ~/repos/my-project
cd ~/repos/my-project
git init
ooda init \
  --project-id my-project \
  --project-class software-product \
  --scaffold

ooda doctor
```

OODA scaffolds only the operating spine: `README.md`, `AGENTS.md`, `PROJECT_STATE.md`, `.ooda/project.json`, `.ooda/work-orders/`, `.ooda/traces/`, and `.ooda/README.md`.

Architecture/domain/process docs are created only when real project complexity earns them.

## Routing reference

| Concept | Question |
|---|---|
| **Project class** | What broad kind of project is this? |
| **Role** | Who owns the next decision/action? |
| **Profile** | What expertise should that role bring? |
| **Lenses** | What perspectives could materially change orientation? |
| **Claim** | How strongly will we rely on the result? |

See [`docs/SELECTION_REFERENCE.md`](docs/SELECTION_REFERENCE.md) for exact values and examples.

## Deeper docs

- [`OODA.md`](OODA.md) — doctrine
- [`docs/CONTROLLER.md`](docs/CONTROLLER.md) — Controller contract
- [`docs/CONTROLLER_QUICKSTART.md`](docs/CONTROLLER_QUICKSTART.md) — one-window Controller flow
- [`docs/ZERO_TO_GROK.md`](docs/ZERO_TO_GROK.md) — install-to-running cheat sheet
- [`docs/SELECTION_REFERENCE.md`](docs/SELECTION_REFERENCE.md) — roles/profiles/lenses/claims/project classes
- [`docs/PROJECT_VIEW.md`](docs/PROJECT_VIEW.md) — objective ladder, timeline, stakeholder summary
- [`docs/LIVE_CONTROL_ROOM.md`](docs/LIVE_CONTROL_ROOM.md) — current browser Control Room behavior and telemetry boundary
- [`docs/PROJECT_COCKPIT.md`](docs/PROJECT_COCKPIT.md) — generalized Overview/Research/Live/Health design
- [`docs/PROVIDER_FLAVORS.md`](docs/PROVIDER_FLAVORS.md) — provider-neutral runner/inference adapter plan
- [`docs/DOCUMENTATION_STEWARDSHIP.md`](docs/DOCUMENTATION_STEWARDSHIP.md) — documentation discipline
- [`contracts/WORK_ORDER.md`](contracts/WORK_ORDER.md) — mission contract
- [`contracts/TRACE.md`](contracts/TRACE.md) — feedback contract

**If the front door starts feeling complicated again, treat that as an OODA product bug.**