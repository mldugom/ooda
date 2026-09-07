# OODA

**OODA is a provider-neutral control system for bounded AI-assisted research, engineering, product work, and consequential decisions.**

> Think broadly. Orient quickly. Act narrowly. Verify reality. Preserve what matters.

Git/project artifacts remain authoritative. Controller chats, worker sessions, and dashboards are replaceable views.

---

## Install

### Clone install — recommended

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

Commands are installed under `~/.local/bin`. If that directory was not already on your shell `PATH`, the installer adds it to your shell startup file and prints the one-line `export PATH=...` command needed to activate it in the current terminal.

Then verify:

```bash
ooda help
grok-safe --help
```

### Pip from GitHub

```bash
python3 -m pip install "git+https://github.com/mldugom/ooda.git"
ooda setup
```

The Python distribution is named `ooda-ai`; there is no PyPI release yet.

---

## Everyday commands

| Command | Purpose |
|---|---|
| `ooda setup` | Install bundled Grok skills/policy after a pip install. |
| `ooda init` | Adopt or scaffold a repository. |
| `ooda doctor` | Validate the current OODA project/contracts. |
| `ooda mission` | Create one bounded mission/work order. |
| `ooda trace` | Record durable mission outcome/feedback. |
| `ooda dashboard` | Open the bundled local OODA Control Room. |
| `grok-safe` | Launch Grok with OODA's bounded execution policy. |

Compatibility aliases such as `ooda work-order` and `ooda validate` remain for old usage but are not part of the normal surface.

---

## The operating model

```text
HUMAN + CHATGPT
raw thought / strategy / challenge
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
 BOUNDED CHILD WORKER
 deep context isolated from Controller
        |
        v
 Git / evidence / handoff / trace
        |
        v
 CONTROLLER RE-OBSERVES
        |
        v
 next thought / gate / mission
```

The important implementation detail is that **the child worker does not require a separate terminal window**.

When Grok supports child agents, `/ooda-controller` may construct a bounded mission and dispatch one child worker inside the same Controller session. The worker receives the deep project context; the Controller should receive only the concise result/evidence needed to re-orient.

A separate session or worktree remains useful when duration, concurrency, isolation, or independent review materially justify it.

The Controller itself stays thin.

---

## Start using OODA on an existing repo

Suppose your project already exists at `~/repos/my-app`:

```bash
cd ~/repos/my-app

ooda init \
  --project-id my-app \
  --project-class software-product

ooda doctor
```

For an existing repo with useful docs, normally **do not** use `--scaffold`. OODA adds only the `.ooda/` control overlay.

Then launch:

```bash
grok-safe
```

Inside Grok:

```text
/ooda-controller Jump into this repo. Use only the minimum durable state needed to orient. Help me decide what deserves work next. If deeper evidence is needed, create/propose the smallest bounded worker mission rather than doing the deep work yourself.
```

You can keep that Controller conversation open while it is useful. Restart it whenever its context becomes large or stale; durable project state, work orders, traces, Git/PR state, and explicit human decisions are the real memory.

---

## Missions

You can let the Controller construct them, or create one directly:

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

If you intentionally launch a standalone worker session instead of an inline Controller child:

```bash
grok-safe
```

```text
/start
/ooda .ooda/work-orders/ARCH-01.json
```

---

## Traces

After a mission:

```bash
ooda trace \
  --work-order .ooda/work-orders/ARCH-01.json \
  --result completed \
  --summary "Architecture orientation completed; returned the next bounded implementation boundary."
```

Default output:

```text
.ooda/traces/ARCH-01.json
```

Trace result states:

```text
completed
negative_finding
blocked
budget_exhausted
needs_human_gate
```

A trace is concise decision provenance and feedback, not chain-of-thought.

---

## `grok-safe`

`grok-safe` finds Grok from `GROK_BIN`, `~/.grok/bin/grok`, or your shell `PATH` and launches it with the bundled OODA efficiency policy.

Default turn cap:

```text
6
```

Override when intentionally warranted:

```bash
OODA_GROK_MAX_TURNS=10 grok-safe
```

Subagents are available because the Controller can use them as bounded context-isolated workers. OODA policy discourages broad fan-out and defaults to one Controller child mission at a time.

For a deliberately strict session with child agents disabled:

```bash
OODA_GROK_NO_SUBAGENTS=1 grok-safe
```

The wrapper contains no credentials or xAI API key.

---

## Control Room

The dashboard is bundled with OODA; it no longer requires a second repository.

```bash
ooda dashboard
```

It opens a local read-only Control Room on `127.0.0.1:8791`, scans OODA-adopted repositories under `~/repos`, and reconstructs controller-sized state from:

- `.ooda/project.json`
- `PROJECT_STATE.md`
- latest work order
- latest trace
- local Git branch / HEAD / dirty state

It includes a **Refresh now** button and defaults to browser refresh every 60 seconds.

Configuration:

```bash
OODA_PROJECTS_ROOT=/path/to/repos ooda dashboard
OODA_DASHBOARD_PORT=8899 ooda dashboard
OODA_DASHBOARD_REFRESH_SECONDS=30 ooda dashboard
```

The dashboard is derived observation state. It does not certify, merge, modify projects, or replace Git/project truth.

---

## New repo starter pack

For a brand-new repository:

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

OODA scaffolds only:

| File | Purpose |
|---|---|
| `README.md` | Project entrypoint. |
| `AGENTS.md` | Standing invariants and authority. |
| `PROJECT_STATE.md` | Concise current truth and next gate. |
| `.ooda/project.json` | Routing / project metadata. |
| `.ooda/work-orders/` | Bounded missions. |
| `.ooda/traces/` | Durable feedback. |
| `.ooda/README.md` | Thin-overlay explanation. |

Architecture/domain/process docs are created only when real project complexity earns them.

---

## Routing cheat sheet

| Concept | Question |
|---|---|
| **Project class** | What broad kind of project is this? |
| **Role** | Who owns the next decision/action? |
| **Profile** | What expertise should that role bring? |
| **Lenses** | What perspectives could materially change orientation? |
| **Claim** | How strongly will we rely on the result? |

See [`docs/SELECTION_REFERENCE.md`](docs/SELECTION_REFERENCE.md) for the exact values, descriptions, and examples.

---

## Documentation discipline

Documentation is a completion obligation, not another permanent bot.

When work materially changes domain concepts, architecture, process/data/control flow, interfaces, methodology, public commands, or operator behavior, update the smallest durable artifact that prevents future rediscovery.

See [`docs/DOCUMENTATION_STEWARDSHIP.md`](docs/DOCUMENTATION_STEWARDSHIP.md).

---

## Deeper reference

- [`OODA.md`](OODA.md) — doctrine and loop semantics
- [`docs/CONTROLLER.md`](docs/CONTROLLER.md) — thin Controller contract
- [`docs/CONTROLLER_QUICKSTART.md`](docs/CONTROLLER_QUICKSTART.md) — Controller usage
- [`docs/SELECTION_REFERENCE.md`](docs/SELECTION_REFERENCE.md) — roles/profiles/lenses/claims/project classes
- [`docs/ZERO_TO_GROK.md`](docs/ZERO_TO_GROK.md) — zero-to-running cheat sheet
- [`contracts/WORK_ORDER.md`](contracts/WORK_ORDER.md) — mission contract
- [`contracts/TRACE.md`](contracts/TRACE.md) — feedback contract

**If the front door starts feeling complicated again, treat that as an OODA product bug.**
