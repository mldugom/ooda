# OODA

OODA is a provider-neutral operating doctrine and control system for AI-assisted research, engineering, product development, and consequential decision-making.

Its purpose is simple:

> Explore broadly, orient intelligently, choose bounded high-value actions, execute safely, verify reality, and continuously learn.

Mnemonic:

> **Think broadly. Orient intelligently. Act narrowly. Verify reality. Preserve what we learn.**

OODA keeps project truth in Git and durable repository artifacts rather than in long-running chat sessions. The current reference execution provider is Grok Build, but the work-order, trace, authority, claim-level, and project-view contracts are provider-neutral.

## Core operating model

```text
HUMAN + CHATGPT
      |
ONE OODA CONTROLLER SESSION
      |
      +--> bounded child worker
             isolated context
             |
       concise result / TRACE
             |
      Controller re-orients
```

**One Controller UI does not mean one context.** The Controller should think enough to route, then delegate anything that needs deep code archaeology, data analysis, implementation, web research, or independent validation.

## Durable project artifacts

An adopted project may contain:

```text
.ooda/project.json          project class, authority, state-source hints
.ooda/project-view.json     objective ladder, material decision timeline, stakeholder summary
.ooda/work-orders/*.json    bounded execution contracts
.ooda/traces/*.json         concise durable outcome/evidence records
PROJECT_STATE.md            concise authoritative current project truth
```

Git, tests, research artifacts, and project-specific state remain authoritative. The project view is a derived orientation surface, not a second source of truth.

## Everyday commands

```bash
ooda help
ooda init --project-id example --project-class software-product
ooda doctor
ooda mission "Implement the bounded slice" --role engineer --profile backend --claim n-a
ooda trace --work-order .ooda/work-orders/<id>.json --result completed --summary "..."
ooda view
ooda dashboard
```

`ooda view` renders the objective ladder, latest material decision pivots, and current stakeholder summary. `ooda dashboard` opens the bundled local Control Room.

## Grok reference flavor

Install/refresh from a checkout:

```bash
cd ~/repos/ooda
git checkout main
git pull --ff-only
bash install.sh
```

Then from an adopted project:

```bash
grok-safe
```

Inside Grok:

```text
/ooda-controller
/ooda <mission-file>
```

The Grok flavor includes:

- the OODA Controller and worker skills;
- the OODA efficiency policy;
- `grok-safe`, which preserves one-Controller + isolated-child workflows;
- a Grok-native OODA status-line command that can display project/model/context plus current objective, human gate, worker state, and latest pivot.

If an older `grok-skills` installation left this line in your shell startup file:

```bash
source "$HOME/repos/grok-skills/shell/grok-safe.zsh"
```

`bash install.sh` now migrates that exact managed hook away because it defines a shell function named `grok-safe` that shadows OODA's installed executable and disables subagents by default. The installer backs up the shell startup file before changing it. In the current shell, run `unset -f grok-safe 2>/dev/null || true` once after migration.

See `docs/GROK_TUI.md` for the status-line boundary and `docs/PROVIDER_FLAVORS.md` for the provider-neutral architecture.

## OODA Controller

The Controller owns orientation and routing. It may use:

- `.ooda/project.json`;
- concise `PROJECT_STATE.md`;
- optional `.ooda/project-view.json`;
- active work orders;
- latest useful trace;
- current Git/PR/test state;
- relevant blockers and human gates.

It should not read the entire repository by default.

Default outcomes are:

- `KEEP THINKING`
- `PROPOSE MISSION`
- `HUMAN GATE`
- `NO ACTION`

Roles represent accountability; profiles represent expertise; lenses represent the few analytical perspectives likely to change the decision.

## Roles

OODA V1 roles are:

- `controller`
- `researcher`
- `product-strategist`
- `architect`
- `engineer`
- `validator`
- `portfolio-manager`
- `trader`
- `risk-manager`

Projects may use domain-specific profiles such as quantitative research, statistics, data engineering, ML, LLM/agent systems, backend/frontend/fullstack, market microstructure, portfolio construction, risk, reliability, deployment, and observability.

## Lenses

Current OODA lenses:

- `boyd`
- `stanley-lehman`
- `taleb`
- `scientific`
- `statistical`
- `model-risk`
- `value-of-information`
- `causal-mechanism`
- `market-microstructure`
- `portfolio`
- `reliability-systems`
- `product-user`
- `security-abuse`

Normally select no more than three for one bounded action. OODA/Boyd is the backbone; do not mechanically select the `boyd` lens for every mission.

## Claim levels

- `discovery` — exploratory evidence or hypotheses worth investigating
- `evidence` — repeatable evidence supporting a bounded claim
- `qualification` — sufficiently controlled evidence for a consequential promotion decision
- `n-a` — ordinary engineering/product work where claim promotion is not the objective

A worker cannot promote its own claim by assertion.

## Default-deny authority

Unless an explicit human gate grants otherwise, OODA does not authorize:

- merging or force-pushing protected refs;
- self-certifying consequential models;
- promoting discovery/evidence by assertion;
- touching live systems or capital;
- spending capital;
- protected cleanup;
- expanding a mission beyond its bounded objective.

## Trace result states

Trace result states are:

- `completed`
- `negative_finding`
- `blocked`
- `budget_exhausted`
- `needs_human_gate`

Negative findings are first-class durable evidence when they prevent repeated wasted work.

## Project view

The optional `.ooda/project-view.json` answers three human questions cheaply:

1. Where are we?
2. Why did the project change direction?
3. What larger objective does the current gate serve?

Its objective ladder contains exactly one `current` rung. Downstream `provisional` rungs are directional hypotheses, not authorized future missions. They may be reordered, replaced, skipped, or abandoned.

The timeline records only material pivots using:

```text
TIME | DECISION | SO WHAT | BIGGER IDEA
```

Routine commands, file reads, and ordinary test runs do not belong there.

See `docs/PROJECT_VIEW.md`.

## Control Room

The bundled Control Room is a local read-only coordination surface. It can show:

- project tabs;
- current objective and human gate;
- live OODA loop state;
- objective ladder;
- material decision timeline;
- Git/controller/mission freshness metadata;
- optional provider/session telemetry when available.

The browser UI is not authority. It derives from repository state and can be rebuilt at any time.

Run:

```bash
ooda dashboard
```

The default port is `8792`; if occupied, OODA searches forward for a free local port.

## Provider-neutral direction

OODA separates:

```text
OODA core contracts and doctrine
        |
provider adapter / runner
        |
inference provider / model
```

That allows future flavors such as Grok, DeepSeek, Google, local/Ollama, Codex, Pi, or others without rewriting project state.

The next provider should be qualified against real frozen project fixtures rather than benchmark claims alone. Tenniskal and Crypto-Innout are good orientation-replay cases because a fresh Controller should reconstruct the same durable project truth regardless of provider.

See `docs/PROVIDER_FLAVORS.md`.

## Documentation stewardship

Document durable understanding, not activity.

- minor work with no conceptual change: `DOCUMENTATION: none`;
- material structural/domain/process/data-flow changes: update the smallest durable artifact;
- architects own or review durable architecture/domain/process diagrams when substantial;
- validators check consequential documentation when the work is broad enough to require it.

## Installation modes

Checkout install:

```bash
git clone https://github.com/mldugom/ooda.git ~/repos/ooda
cd ~/repos/ooda
bash install.sh
```

Pip users may install the package and then run:

```bash
ooda setup
```

to install the current Grok skills/policy into `~/.grok`.

## Design principles

- Project truth belongs in the project.
- Git is durable memory; chats are disposable.
- Think broadly, then execute narrowly.
- Use the strongest model where orientation matters; use bounded cheaper workers where appropriate.
- Preserve negative findings.
- Avoid recursive agent fan-out.
- Human gates remain explicit for consequential actions.
- The Control Room observes; it does not certify.
- Provider adapters are replaceable; OODA contracts are durable.
- Action is not operationally complete until useful feedback can enter the next loop.
