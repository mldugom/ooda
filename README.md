# OODA

**OODA is a provider-neutral operating doctrine and control system for AI-assisted research, engineering, product development, and consequential decision-making.**

OODA keeps execution bounded without making thought narrow.

The project is intentionally small. It does not replace your current agent runtime, Git workflow, or monitor. It gives them a shared doctrine and lightweight execution contracts.

## Cheat sheet

### Current operating paradigm

```text
LAWRENCE + CHATGPT
ideas / goals / challenge / prioritization
          |
          v
NARROW CONTEXT BOOTSTRAP
read only enough durable repo truth to orient
          |
          v
IS THIS WORTH AGENT TIME?
      /         \
    no           yes
    |             |
keep thinking     v
             OODA WORK ORDER
             role + profile + lenses
             scope + authority + stop conditions
                    |
                    v
               GROK BUILD
          grok-safe -> /start -> /ooda
             one bounded mission
                    |
                    v
                /handoff
             Git / tests / PR
                    |
                    v
          LAWRENCE + CHATGPT
        review / accept / correct
                    |
                    v
                OODA TRACE
          durable lesson / outcome
                    |
                    v
               NEXT OODA LOOP
```

**Rule of thumb:** think broadly, orient intelligently, act narrowly, verify reality, preserve what matters.

### OODA command table

| Command | What it does | Typical use |
|---|---|---|
| `ooda init --project-id <id> --project-class <class>` | Adds the minimal `.ooda/project.json` routing overlay to an existing repo. | Adopt an existing project without changing its docs. |
| `ooda init --project-id <id> --project-class <class> --scaffold` | Creates the minimal OODA starter pack when files are missing. | Start a new OODA-ready repo. |
| `ooda doctor` | Validates the project overlay and reports whether expected durable state files exist. | Run after adoption/scaffolding or when project setup looks wrong. |
| `ooda work-order ... --output <file>` | Creates one bounded `ooda/work-order/v1` execution contract. | Turn a decision into a Grok mission. |
| `ooda trace --work-order <file> ... --output <file>` | Creates an `ooda/trace/v1` result record tied to a work order. | Preserve a useful outcome, negative finding, blocker, or lesson. |
| `ooda validate <file>` | Validates an OODA project, work-order, or trace JSON contract. | Check a contract before execution or commit. |
| `./scripts/check.sh` | Runs the OODA unit/contract test suite and validates examples. | Before merging OODA framework changes. |
| `./scripts/install-cli.sh` | Installs/symlinks the local `ooda` command. | One-time local setup. |
| `./scripts/install-grok.sh` | Installs/symlinks the single Grok `/ooda` skill without replacing existing lifecycle skills. | One-time Grok adapter setup. |

### Current Grok session commands

OODA does **not** replace your existing Grok lifecycle.

| Command | Purpose in the current paradigm |
|---|---|
| `grok-safe` | Start Grok with the existing bounded runtime/efficiency controls. |
| `/start` | Establish current checkout, Git state, durable project truth, and objective. |
| `/ooda <work-order>` | Load the bounded OODA mission, role, profile, lenses, authority, and stop conditions. |
| `/checkpoint` | Persist/verify an in-progress session when it will continue. |
| `/handoff` | Verify, push/open-or-update PR, report truthful completion state, then stop for review. |
| `/end` | Finish the existing lifecycle when appropriate under the project's current rules. |

### OODA starter-pack files

`ooda init --scaffold` creates only the following minimal operating spine, and only when the files do not already exist.

| File / directory | What it is for | What should live there |
|---|---|---|
| `README.md` | Stable project identity. | What the project does, why it exists, basic usage, major architecture. |
| `AGENTS.md` | Standing instructions and invariants for agents. | Safety rules, do-not-touch areas, scientific/engineering invariants, authority boundaries. |
| `PROJECT_STATE.md` | Small current-state checkpoint. | Current objective, phase/gate, important recent truth, blockers, immediate next work. Keep it concise. |
| `.ooda/project.json` | OODA routing/authority overlay. | Project ID/class, integration authority, state sources, current provider/lifecycle settings. Not project history. |
| `.ooda/README.md` | Local explanation of the OODA overlay. | How this repo uses work orders/traces and what `.ooda/` is for. |
| `.ooda/work-orders/` | Bounded execution contracts. | One file per substantial mission worth agent resources. |
| `.ooda/traces/` | Durable execution outcomes. | Concise Observe/Orient/Decide/Act result, verification, cost, stop reason, useful negative findings. |

The starter pack is deliberately **not** a giant documentation framework. Add more files only when repeated project usage earns them.

### Role / profile / lens selection

Use this sequence:

| Choice | Question to answer |
|---|---|
| **Role** | Who owns the next judgment or action? |
| **Profile** | What expertise does that role need for this mission? |
| **Lens 1** | What epistemic/control perspective could change the decision? |
| **Lens 2** | What domain perspective is necessary? |
| **Lens 3 (optional)** | What challenge/opportunity perspective would materially improve orientation? |
| **Claim level** | How strongly will we rely on the result: Discovery, Evidence, Qualification, or N/A? |

Normally use **one role + one profile + no more than three lenses**. OODA/Boyd is already the backbone, so `boyd` does not need to be selected mechanically for every task. See `docs/ROUTING.md`.

## What OODA is

OODA applies John Boyd's Observe → Orient → Decide → Act loop as the control grammar for AI-assisted work.

- **Observe:** establish current reality before interpretation.
- **Orient:** synthesize facts through the smallest useful set of roles, expertise profiles, and analytical lenses.
- **Decide:** choose one high-value bounded action.
- **Act:** execute, verify, and feed the result back into observation.

Orientation is deliberately broad. Bounded execution is not permission for narrow thinking.

## Install locally

From `~/repos/ooda`:

```bash
./scripts/install-cli.sh
./scripts/install-grok.sh
```

The installers create symlinks back to the OODA repository. They do not copy the whole framework into hidden runtime state.

## Adopt an existing project

```bash
cd ~/repos/tenniskal
ooda init --project-id tenniskal --project-class quantitative-research
ooda doctor
```

OODA adds only `.ooda/project.json` unless you explicitly ask for a scaffold.

## Start a new OODA-ready repository

```bash
mkdir ~/repos/my-project
cd ~/repos/my-project
git init

ooda init \
  --project-id my-project \
  --project-class software-product \
  --scaffold

ooda doctor
```

Existing Markdown files are never silently overwritten.

## Create a bounded task contract

```bash
ooda work-order \
  --objective "Test one non-overlapping lead/lag hypothesis" \
  --role researcher \
  --profile quantitative-research \
  --lenses scientific,statistical,market-microstructure \
  --claim-level discovery \
  --output .ooda/work-orders/R6E-01.json
```

Use the generated work order as the execution contract for the Grok session. After the outcome is known, preserve a trace if it has durable value:

```bash
ooda trace \
  --work-order .ooda/work-orders/R6E-01.json \
  --result-state completed \
  --summary "Study completed; no predictive lift" \
  --output .ooda/traces/R6E-01.json
```

## Fresh ChatGPT conversations

Do not paste giant project histories by default. A fresh chat should normally start with one line such as:

```text
Jump into mldugom/tenniskal. Goal: decide the next R6E move. Use OODA. Do not execute yet.
```

ChatGPT/controller bootstraps from narrow durable repo truth. See `docs/CONTEXT_BOOTSTRAP.md` and `docs/CHATGPT_USAGE.md`.

## Repo map

```text
OODA.md                         doctrine
core/roles/                     accountability roles
core/profiles/                  expertise profiles
core/lenses/                    analytical perspectives
policies/                       authority + claim rigor
contracts/                      work-order and trace contracts
providers/grok/                 thin current-provider adapter
examples/projects/              example project overlays
src/ooda/                       tiny provider-neutral CLI
docs/CONTEXT_BOOTSTRAP.md       fresh-chat/project bootstrap contract
docs/CHATGPT_USAGE.md           human-facing entry patterns
docs/ROUTING.md                 role/profile/lens selection rules
docs/EXECUTION_MODEL.md         Lawrence/ChatGPT/Grok workflow
docs/PROJECT_ADOPTION.md        existing/new repo adoption
docs/TRANSITION_PLAN.md         current -> watcher/Pi/multi-provider migration
docs/REPO_WATCHER.md            future cross-repo observation plane
docs/DESIGN_RATIONALE.md        research and repo lessons
docs/AGENT_OPS_MONITOR.md       monitor boundary
```

## Design constraints

- Provider-neutral core; provider-specific behavior lives under `providers/`.
- One role + one profile + normally no more than three lenses per bounded action.
- Discovery, Evidence, and Qualification require increasing rigor.
- No agent self-certification, self-merge, protected-ref promotion, live-capital action, or consequential authority unless a project explicitly grants it.
- Agent Ops Monitor remains an observer, not an orchestrator or source of truth.
- The current Grok workflow is preserved during V1 shadow-mode adoption.
- Automate observation before automating judgment.
- New infrastructure must be earned by repeated usage, not imagined in advance.
