# OODA

**A provider-neutral control system for bounded AI-assisted research, engineering, product work, and consequential decisions.**

> Think broadly. Orient quickly. Act narrowly. Verify reality. Preserve what matters.

Git/project artifacts are durable truth. Controller chats, child workers, and dashboards are replaceable views.

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
| `ooda dashboard` | Open the bundled local Control Room. |
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

## `grok-safe`

`grok-safe` finds the Grok CLI from `GROK_BIN`, `~/.grok/bin/grok`, or your shell `PATH`, then adds OODA's bounded execution policy.

There is **no default global session-turn cap** because a Controller may remain open across multiple bounded missions. Mission/work-order budgets are the primary bounded unit.

For a deliberate hard session cap:

```bash
OODA_GROK_MAX_TURNS=12 grok-safe
```

Subagents are enabled so the Controller can use isolated child workers. OODA policy restricts broad fan-out and defaults to one Controller child mission at a time.

For a strict session with child agents disabled:

```bash
OODA_GROK_NO_SUBAGENTS=1 grok-safe
```

## Control Room

The dashboard is bundled with OODA; no second repository is required.

```bash
ooda dashboard
```

It opens a local read-only Control Room on `127.0.0.1:8791`, scans OODA-adopted repos under `~/repos`, and reconstructs compact state from `.ooda/project.json`, `PROJECT_STATE.md`, the latest work order/trace, and local Git state.

It has **Refresh now** and defaults to a 60-second browser refresh.

Configuration:

```bash
OODA_PROJECTS_ROOT=/path/to/repos ooda dashboard
OODA_DASHBOARD_PORT=8899 ooda dashboard
OODA_DASHBOARD_REFRESH_SECONDS=30 ooda dashboard
```

The dashboard is derived observation state. It does not modify projects, certify results, merge code, or replace Git/project truth.

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
- [`docs/DOCUMENTATION_STEWARDSHIP.md`](docs/DOCUMENTATION_STEWARDSHIP.md) — documentation discipline
- [`contracts/WORK_ORDER.md`](contracts/WORK_ORDER.md) — mission contract
- [`contracts/TRACE.md`](contracts/TRACE.md) — feedback contract

**If the front door starts feeling complicated again, treat that as an OODA product bug.**
