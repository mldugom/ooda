# OODA

**OODA is a provider-neutral operating doctrine and control system for AI-assisted research, engineering, product development, and consequential decision-making.**

OODA keeps execution bounded without making thought narrow.

The project is intentionally small. It does not replace your current agent runtime, Git workflow, or monitor. It gives them a shared doctrine and a pair of lightweight contracts.

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
      OODA work order
            |
            v
   existing Grok Build workflow
   /start -> plan/build -> /handoff
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

## Immediate use

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

# In a project repository
ooda init --project-id tenniskal --project-class quantitative-research
ooda doctor

# Create a bounded task contract
ooda work-order \
  --objective "Test one non-overlapping lead/lag hypothesis" \
  --role researcher \
  --profile quantitative-research \
  --lenses scientific,statistical,market-microstructure \
  --claim-level discovery \
  --output .ooda/work-orders/R6E-01.json
```

Use the generated work order as the execution contract for the Grok session. After the session, emit a trace:

```bash
ooda trace \
  --work-order .ooda/work-orders/R6E-01.json \
  --result-state completed \
  --summary "Study completed; no predictive lift" \
  --output .ooda/traces/R6E-01.json
```

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
docs/EXECUTION_MODEL.md         Lawrence/ChatGPT/Grok workflow
docs/TRANSITION_PLAN.md         current -> future migration
docs/DESIGN_RATIONALE.md        research and repo lessons
docs/PROJECT_ADOPTION.md        how projects opt in
docs/AGENT_OPS_MONITOR.md       monitor boundary
```

## Design constraints

- Provider-neutral core; provider-specific behavior lives under `providers/`.
- One role + one profile + normally no more than three lenses per bounded action.
- Discovery, Evidence, and Qualification require increasing rigor.
- No agent self-certification, self-merge, protected-ref promotion, live-capital action, or consequential authority unless a project explicitly grants it.
- Agent Ops Monitor remains an observer, not an orchestrator or source of truth.
- The current Grok workflow is preserved during V1 shadow-mode adoption.
- New infrastructure must be earned by repeated usage, not imagined in advance.

## Publish as `mldugom/ooda`

This repository is clean-slate. It does not require modifying `grok-skills`.

If GitHub CLI is authenticated on the local machine:

```bash
./scripts/publish-github.sh
```

Otherwise create an empty private `mldugom/ooda` repository, then add it as `origin` and push `main`. The OODA repository is already initialized and committed.
