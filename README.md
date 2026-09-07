# OODA

**OODA is a provider-neutral operating doctrine and control system for AI-assisted research, engineering, product development, and consequential decision-making.**

OODA keeps execution bounded without making thought narrow.

The project is intentionally small. It does not replace your current agent runtime, Git workflow, or monitor. It gives them a shared doctrine and lightweight execution contracts.

## What OODA is

OODA applies John Boyd's Observe → Orient → Decide → Act loop as the control grammar for AI-assisted work.

- **Observe:** establish current reality before interpretation.
- **Orient:** synthesize facts through the smallest useful set of roles, expertise profiles, and analytical lenses.
- **Decide:** choose one high-value bounded action.
- **Act:** execute, verify, and feed the result back into observation.

Orientation is deliberately broad. Bounded execution is not permission for narrow thinking.

## Current operating model

```text
Lawrence + ChatGPT
  raw ideas / goals / creative dialogue
            |
            v
  narrow context bootstrap from durable repo truth
            |
            v
      OODA work order
            |
            v
   existing Grok Build workflow
   /start -> /ooda -> work -> /handoff
            |
            v
    ChatGPT + Lawrence review
            |
            v
       OODA run trace
            |
            v
 Agent Ops Monitor (later ingestion)
```

Today, Grok remains the execution provider. OODA does not replace `grok-safe`, `/start`, `/handoff`, GitHub PR review, or the human integration gate.

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

The scaffold creates only the minimal durable operating spine when files are missing:

```text
README.md
AGENTS.md
PROJECT_STATE.md
.ooda/
  project.json
  README.md
  work-orders/
  traces/
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

## Role and lens routing

Choose:

- **role by accountability** — who owns the decision/action;
- **profile by expertise** — what domain capability is needed;
- **lenses by what could materially change the decision**;
- **claim level by how strongly the result will be relied upon**.

OODA itself is always the backbone, so `boyd` does not need to be redundantly selected for every task. Normally activate no more than three lenses. See `docs/ROUTING.md`.

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
