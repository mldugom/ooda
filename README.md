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

## Roles, profiles, and lenses — optional

These are **routing aids, not required fields**. A vnext ablation found no
measurable gain from them on ordinary data-science work, where a worker given
none scored joint-top. Attach one only when it will materially change worker
behavior; otherwise state the scientific constraints directly. A mission with no
role, profile, or lens is valid.

Roles:

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

**Default lens count is 0–1.** Two or more require a concrete stated reason
(`--lens-why`); three is the hard cap. Lenses genuinely earn their place on
specialist domains — market microstructure, security, reliability, portfolio,
risk — where a generic worker may not bring the perspective. For quantitative
work, prefer loading `reference/predictive-science.md` over attaching
`scientific`/`statistical`/`model-risk` by name.

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

- `completed`
- `negative_finding` — **a successful outcome.** No signal, insufficient sample,
  weak features, poorly conditioned target, not identifiable. Preserve it and
  re-orient; do not respond by adding features, trying more models, or moving the
  target.
- `blocked` — must be **typed** (below)
- `budget_exhausted`
- `needs_human_gate`

### Typed blockers

A bare `blocked` is not a valid result: it loses the information that decides
what may still happen, and a controller that prioritises blocked missions will
keep re-surfacing a stall that was never real.

```
blocker_type        scientific | data | environment | authority | promotion | sequencing
blocked_for         exploration | evidence | qualification | production | capital
claim_ceiling       discovery | evidence | qualification | n-a
exploration_allowed yes | no
target              the exact quantity or comparison affected
```

Two rules enforced in code (`ooda.policy`, covered by
`tests/test_vnext_regressions.py`):

- **Stages describe evidence, not permission.** `sequencing` never bars work.
- **A claim ceiling is not a work ceiling.** Exploration survives every blocker
  except a scientific one covering exploration, and that binds only its target.

Pre-vnext traces carrying a bare `blocked` still load, as `blocker_type: legacy`;
they do not bar exploration but must be re-typed before supporting a claim.

## Truth hierarchy

```
runtime > git > frozen artifact > trace > project state > project view/dashboard
```

Fresher authoritative evidence beats stale summary prose, always. PROJECT_STATE
carries durable orientation — goal, current decision, bottleneck, strongest
evidence, claim ceilings, active blocker, next unknown, human gate, pointers. It
does **not** carry mutable runtime facts that can be queried authoritatively, and
it never outranks them.

## Environment preflight

A mission needing local datasets, an operator-host runtime, private files, live
processes, GPUs, or credentials declares them and is checked before dispatch:

```bash
ooda preflight --work-order .ooda/work-orders/R6E-01.json
```

An entire remote research cycle was once implemented against data the environment
did not have. This is the check that prevents the repeat.

## Prediction charter

For consequential predictive work, freeze the target before substantial
modelling:

```bash
ooda charter --new
ooda charter --diff old.json new.json    # detects goalpost movement
```

Changing decision, target, decision time, baseline, primary metrics, or holdout
redefines success and requires an explicit re-orientation decision with the
evidence that motivated it. **A disappointing model is not that evidence.**

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
