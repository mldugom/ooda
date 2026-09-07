# OODA

**OODA is a provider-neutral operating system for bounded AI-assisted research, engineering, product work, and consequential decisions.**

> Think broadly. Orient quickly. Act narrowly. Verify reality. Preserve what matters.

Git/project artifacts remain authoritative. Chat sessions and dashboards are replaceable views.

---

## Install

### From GitHub with pip

Once this repository is public:

```bash
python3 -m pip install "git+https://github.com/mldugom/ooda.git"
ooda setup
```

That installs the executable commands:

```text
ooda
grok-safe
```

`ooda setup` then installs the bundled Grok skills and efficiency policy into `~/.grok`:

```text
/ooda
/ooda-controller
```

The Python distribution is named **`ooda-ai`** because the PyPI name `ooda` belongs to an unrelated project. There is no PyPI release yet, so use the GitHub install above rather than `pip install ooda`.

### From a clone

```bash
mkdir -p ~/repos
cd ~/repos
git clone https://github.com/mldugom/ooda.git
cd ooda
bash install.sh
```

The clone installer provides the same everyday surfaces:

```text
ooda
grok-safe
/ooda
/ooda-controller
```

Then:

```bash
ooda help
```

---

## The commands you actually need

| Command | What it does | Example |
|---|---|---|
| `ooda setup` | Install bundled Grok skills/policy after a pip install. | `ooda setup` |
| `ooda init` | Adopt or scaffold a repo for OODA. | `ooda init --project-id example-app --project-class software-product` |
| `ooda doctor` | Check a repo or one OODA JSON contract. | `ooda doctor` |
| `ooda mission` | Create one bounded worker mission. | `ooda mission "Inspect the current API boundary" --role architect --profile api --claim n-a` |
| `ooda trace` | Record what happened after a mission. | `ooda trace --work-order .ooda/work-orders/TASK-01.json --result completed --summary "Boundary documented"` |
| `ooda dashboard` | Open an optional local OODA Control Room checkout. | `ooda dashboard` |
| `grok-safe` | Launch Grok with OODA's bounded efficiency policy. | `grok-safe` |

Compatibility aliases remain available but are not normal-use commands:

- `ooda work-order` = `ooda mission`
- `ooda validate FILE` = deprecated; use `ooda doctor FILE`

Developer/internal scripts stay under `scripts/`; ordinary users should not need them.

---

## 60-second operating model

```text
HUMAN + CHATGPT
raw ideas / strategy / challenge
        |
        v
 OODA CONTROLLER
 Intake / Proposal / Control
        |
        | idea earns work
        v
   OODA MISSION
 Observe -> Orient -> Decide
        |
        v
  BOUNDED WORKER
      Act
        |
        v
 Git / PR / evidence / handoff
        |
        v
      TRACE
 result + verification + next gate
        |
        +---------------------> next Observe
        |
        v
 HUMAN / CHATGPT REVIEW
```

The Controller chooses **what should happen next**. Workers load the deeper project-specific context required to actually do it.

---

# Typical daily use

## 1. Bounce an idea off the Controller

From the target repo:

```bash
grok-safe
```

Then:

```text
/ooda-controller I think this product may be solving the wrong workflow. Help me decide whether that deserves a product-discovery spike.
```

The Controller normally ends with one of:

- `KEEP THINKING`
- `PROPOSE MISSION`
- `HUMAN GATE`
- `NO ACTION`

It does not do deep research/code work itself. If robust routing needs deeper facts, it proposes a small orientation spike first.

## 2. Create a mission

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

Important mission arguments:

| Argument | Meaning | Required? |
|---|---|---:|
| objective | One coherent bounded outcome/question. Positional or `--objective`. | yes |
| `--role` | Who owns the judgment/action. | yes |
| `--profile` | Expertise needed by that role. | yes |
| `--claim` | `discovery`, `evidence`, `qualification`, or `n-a`. | yes |
| `--lenses` | Comma-separated perspectives; normally no more than 3. | no |
| `--project-id` | Defaults to current directory name. | no |
| `--id` | Stable mission ID; otherwise generated. | no |
| `--output` | Defaults to `.ooda/work-orders/<id>.json`. | no |
| `--max-turns` | Worker turn budget; default 6. | no |
| `--max-investigation-steps` | Investigation budget; default 8. | no |

The mission is the durable result of **Observe -> Orient -> Decide** and the control envelope for **Act**.

## 3. Execute it

```bash
grok-safe
```

Inside Grok:

```text
/start
/ooda .ooda/work-orders/ARCH-01.json
```

The worker re-observes current truth, orients under the mission, acts only inside the bounded envelope, verifies the result, checks documentation impact, and hands off through the project's normal lifecycle.

If reality invalidates the mission assumptions, the worker should stop/re-orient rather than efficiently completing the wrong task.

## 4. Record the result

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

- `completed`
- `negative_finding`
- `blocked`
- `budget_exhausted`
- `needs_human_gate`

A trace is not chain-of-thought. It is concise decision provenance and feedback for the next loop.

---

# Adopt an existing repo

If a repository already has useful documentation, add only the thin OODA overlay:

```bash
cd ~/repos/example-app

ooda init \
  --project-id example-app \
  --project-class software-product

ooda doctor
```

Do **not** use `--scaffold` just because OODA supports it. Existing architecture/process/product documentation should remain authoritative.

Then:

```bash
grok-safe
```

```text
/ooda-controller Jump into this repo. Use only the minimum durable state required to orient. What deserves attention next? If deeper evidence is required, propose the smallest worker mission rather than doing deep work yourself.
```

See `docs/ZERO_TO_GROK.md` for the complete copy/paste flow.

---

# New repo starter pack

For a brand-new project:

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

OODA creates only the operating spine:

| File | Purpose |
|---|---|
| `README.md` | Project purpose and entrypoint. |
| `AGENTS.md` | Standing rules, invariants, authority/safety boundaries. |
| `PROJECT_STATE.md` | Small current-truth/objective/blocker/next-gate summary. |
| `.ooda/project.json` | Routing + authority metadata. |
| `.ooda/work-orders/` | Durable bounded missions. |
| `.ooda/traces/` | Durable results / negative findings / next gates. |
| `.ooda/README.md` | Explains the thin OODA overlay. |

OODA deliberately does **not** scaffold empty `ARCHITECTURE.md`, `DOMAIN.md`, or `PROCESS.md` files. Those are earned when real work creates durable concepts worth documenting.

Project classes:

- `quantitative-research`
- `trading-research`
- `data-ml-system`
- `software-product`
- `analytical-product`
- `infrastructure`

---

# Roles, profiles, lenses, claims

Use this decision rule:

| Concept | Question |
|---|---|
| **Role** | Who owns the next decision/action? |
| **Profile** | What expertise do they need? |
| **Lenses** | What perspectives could materially change orientation? |
| **Claim** | How strongly will we rely on the result? |

Roles:

| Role | Primary job |
|---|---|
| `controller` | route / stop / escalate |
| `researcher` | discover/test what may be true |
| `product-strategist` | decide what problem/workflow is worth solving |
| `architect` | design system/experiment/interface |
| `engineer` | implement bounded work |
| `validator` | independently challenge correctness/claims |
| `portfolio-manager` | allocation/correlation/concentration |
| `trader` | execution/liquidity/timing/slippage |
| `risk-manager` | tails/ruin/exposure/model/operational risk |

Profiles are extensible expertise labels such as `quantitative-research`, `api`, `browser-extension`, `reliability`, `full-stack`, or project-specific labels such as `ios-swiftui`.

A useful lens pattern is usually:

1. one epistemic lens — `scientific`, `statistical`, `model-risk`, `causal-mechanism`;
2. one domain lens — `market-microstructure`, `portfolio`, `product-user`, `security-abuse`, `reliability-systems`;
3. optionally one challenge/opportunity lens — `taleb`, `stanley-lehman`, `value-of-information`, or explicit `boyd` when adaptation itself is the issue.

OODA/Boyd is already the backbone; you do not need to select the `boyd` lens every time.

For the full value tables and trigger questions, see `docs/SELECTION_REFERENCE.md`.

---

# Documentation discipline

Documentation is a completion obligation, not another permanent bot.

The active worker asks whether the mission materially changed domain concepts, architecture, process/data/control flow, interfaces, methodology, CLI/configuration, or operator behavior.

If not:

```text
DOCUMENTATION: none
```

If yes, update the smallest durable artifact that prevents rediscovery. An Architect reviews structural diagrams/models when warranted; a Validator independently checks consequential documentation when warranted.

See `docs/DOCUMENTATION_STEWARDSHIP.md`.

---

# `grok-safe`

`grok-safe` is bundled with OODA. It locates the Grok CLI at `GROK_BIN`, `~/.grok/bin/grok`, or on `PATH`, then launches it with the bundled efficiency policy plus:

```text
--max-turns 6
--no-subagents
```

Override the turn cap when intentionally needed:

```bash
OODA_GROK_MAX_TURNS=10 grok-safe
```

The wrapper does not contain credentials or an xAI API key.

---

# Optional Control Room

`ooda dashboard` uses an existing local Control Room checkout when available:

```text
~/repos/agent-ops-monitor
```

For another location:

```bash
OODA_CONTROL_ROOM_DIR=/path/to/control-room ooda dashboard
```

If no checkout exists, you may provide an accessible repository explicitly:

```bash
OODA_CONTROL_ROOM_REPO=<clone-url> ooda dashboard
```

The dashboard is derived observation state. It does not certify, merge, or replace Git/project truth.

---

# Fresh ChatGPT conversations

Start with very little context:

```text
Jump into <repo>. Use OODA. Goal: <current question>.
```

or:

```text
Review PR #<n> under OODA. Use current repo truth, not old chat state.
```

or:

```text
New project idea: <idea>. OODA it with me. Don't build yet.
```

The repo/project state is durable memory; chats are working rooms.

---

# What OODA deliberately does not automate yet

- automatic consequential dispatch;
- self-merge;
- model/research self-certification;
- live-capital actions;
- giant central code/context ingestion;
- autonomous provider selection;
- always-on scheduling.

Usage earns automation.

---

# Deeper reference

- `OODA.md` — doctrine and loop semantics
- `contracts/WORK_ORDER.md` — mission/work-order contract
- `contracts/TRACE.md` — feedback/provenance contract
- `docs/CONTROLLER.md` — thin Controller contract
- `docs/CONTROLLER_QUICKSTART.md` — Controller usage
- `docs/SELECTION_REFERENCE.md` — exact roles/profiles/lenses/claims/project classes
- `docs/ZERO_TO_GROK.md` — zero-to-running end-to-end cheat sheet
- `docs/ROUTING.md` — routing rationale
- `docs/DOCUMENTATION_STEWARDSHIP.md` — durable diagrams/domain/process/cheat-sheet rules
- `docs/CONTEXT_BOOTSTRAP.md` — fresh-chat/repo bootstrap
- `docs/EXECUTION_MODEL.md` — human + ChatGPT + Controller + worker model
- `docs/PROJECT_ADOPTION.md` — adding OODA to repos
- `docs/REPO_WATCHER.md` — future observation collector

**If the front door starts feeling complicated again, treat that as an OODA product bug.**
