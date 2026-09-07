# OODA

**OODA is a provider-neutral operating system for bounded AI-assisted research, engineering, product work, and consequential decisions.**

The basic idea:

> Think broadly. Orient quickly. Act narrowly. Verify reality. Preserve what matters.

OODA is intentionally small. Git/project artifacts remain authoritative. Chat sessions and dashboards are replaceable views.

---

## Start here

### Install once

From the OODA repo:

```bash
cd ~/repos/ooda
bash install.sh
```

That installs:

- the `ooda` command;
- Grok `/ooda` worker skill;
- Grok `/ooda-controller` control skill.

Then:

```bash
ooda help
```

### The commands you actually need

| Command | What it does | Main arguments | Example |
|---|---|---|---|
| `ooda init` | Adopt/scaffold a repo for OODA. | `--project-id`, `--project-class`, optional `--scaffold`, `--path` | `ooda init --project-id tenniskal --project-class quantitative-research` |
| `ooda doctor` | Check the current repo, another repo, or one OODA JSON contract. | optional path/file | `ooda doctor` or `ooda doctor .ooda/work-orders/R6E-01.json` |
| `ooda mission` | Create one bounded worker mission. | objective, `--role`, `--profile`, `--claim`, optional `--lenses`, `--id` | see below |
| `ooda trace` | Record what happened after a mission. | `--work-order`, `--result`, `--summary`, optional `--provider` | see below |
| `ooda dashboard` | Open the local OODA Control Room. | none; refresh interval is configurable by env var | `ooda dashboard` |

Compatibility aliases remain available but are not part of normal use:

- `ooda work-order` = `ooda mission`
- `ooda validate FILE` = deprecated; use `ooda doctor FILE`

Developer/internal scripts remain under `scripts/`; normal users should not need them.

---

# 60-second operating model

```text
LAWRENCE + CHATGPT
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

The Controller chooses **what should happen next**. Workers load the deep project-specific context required to actually do it.

---

# Typical daily use

## 1. Bounce an idea off the Controller

Start Grok with your existing bounded launcher:

```bash
grok-safe
```

Then:

```text
/ooda-controller I think Tenniskal may be over-focusing on trade intensity. Is this worth another research spike?
```

The Controller normally ends with one of:

- `KEEP THINKING`
- `PROPOSE MISSION`
- `HUMAN GATE`
- `NO ACTION`

It does not do deep research/code work itself. If it needs evidence to construct a robust mission, it proposes a small orientation spike first.

## 2. Create a mission

Friendly form:

```bash
ooda mission \
  "Test one non-overlapping lead/lag hypothesis" \
  --role researcher \
  --profile quantitative-research \
  --lenses scientific,statistical,market-microstructure \
  --claim discovery \
  --id R6E-01
```

This writes by default:

```text
.ooda/work-orders/R6E-01.json
```

Important mission arguments:

| Argument | Meaning | Required? |
|---|---|---:|
| objective | One coherent bounded outcome/question. May be supplied positionally or with `--objective`. | yes |
| `--role` | Who owns the judgment/action. | yes |
| `--profile` | Expertise needed by that role. | yes |
| `--claim` | `discovery`, `evidence`, `qualification`, or `n-a`. | yes |
| `--lenses` | Comma-separated perspectives; normally no more than 3. | no |
| `--project-id` | Defaults to current directory name. | no |
| `--id` | Stable mission ID; otherwise generated. | no |
| `--output` | Defaults to `.ooda/work-orders/<id>.json`. | no |
| `--max-turns` | Worker turn budget; default 6. | no |
| `--max-investigation-steps` | Investigation budget; default 8. | no |

The mission file is the durable result of **Observe -> Orient -> Decide** and the control envelope for **Act**.

## 3. Execute it

Inside the target repo:

```text
grok-safe
/start
/ooda .ooda/work-orders/R6E-01.json
```

The worker:

1. re-observes current repo/project truth;
2. orients under the mission role/profile/lenses;
3. confirms the bounded decision/scope;
4. acts;
5. re-observes if material new facts appear;
6. verifies;
7. reports documentation impact;
8. hands off through the existing project lifecycle.

If reality invalidates the mission assumptions, the worker should stop/re-orient rather than efficiently completing the wrong task.

## 4. Record the result

```bash
ooda trace \
  --work-order .ooda/work-orders/R6E-01.json \
  --result negative_finding \
  --summary "No meaningful predictive lift"
```

Default output:

```text
.ooda/traces/R6E-01.json
```

Trace arguments:

| Argument | Meaning | Required? |
|---|---|---:|
| `--work-order` | Mission that produced this result. | yes |
| `--result` | `completed`, `negative_finding`, `blocked`, `budget_exhausted`, or `needs_human_gate`. | yes |
| `--summary` | Concise truthful outcome. | yes |
| `--provider` | Defaults to `grok`. | no |
| `--output` | Defaults to `.ooda/traces/<work-order-id>.json`. | no |

A trace is not chain-of-thought. It is concise decision provenance and feedback for the next loop.

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

Profiles are expertise labels such as `quantitative-research`, `browser-extension`, `reliability`, `full-stack`, or `fundamental-valuation`.

A useful lens pattern is usually:

1. one epistemic lens — `scientific`, `statistical`, `model-risk`, `causal-mechanism`;
2. one domain lens — `market-microstructure`, `portfolio`, `product-user`, `security-abuse`, `reliability-systems`;
3. optionally one challenge/opportunity lens — `taleb`, `stanley-lehman`, `value-of-information`, or explicit `boyd` when adaptation itself is the issue.

OODA/Boyd is already the backbone; you do not need to select the `boyd` lens every time.

---

# Documentation discipline

Documentation is a completion obligation, not another permanent bot.

The active worker first asks whether the mission materially changed:

- domain concepts;
- architecture/boundaries;
- process/data/control flow;
- interfaces/contracts;
- methodology;
- CLI/configuration;
- operator behavior.

If not:

```text
DOCUMENTATION: none
```

If yes, update the smallest durable artifact that prevents rediscovery. An Architect reviews structural diagrams/models when warranted; a Validator independently checks consequential documentation when warranted.

See `docs/DOCUMENTATION_STEWARDSHIP.md`.

---

# Control Room

Open it with:

```bash
ooda dashboard
```

If `~/repos/agent-ops-monitor` is missing, OODA clones the configured Control Room repo there first.

The local dashboard shows controller-sized state:

- projects/current objectives;
- OODA stage;
- role/profile/lenses;
- claim level;
- active mission/worker;
- PR/handoff;
- human gates;
- latest trace;
- freshness/blockers;
- derived audit trail as the collector matures.

Default local refresh is controlled by the monitor launcher. Example:

```bash
AGENT_MONITOR_REFRESH_SECONDS=30 ooda dashboard
```

The dashboard is derived state. It does not certify, merge, or replace Git/project truth.

---

# Fresh ChatGPT conversations

You should be able to start with very little context:

```text
Jump into tenniskal. Use OODA. Goal: decide the next R6E move.
```

or:

```text
Review crypto-innout PR #27 under OODA.
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
- Raspberry Pi scheduling.

Usage earns automation.

---

# Deeper reference

- `OODA.md` — doctrine and loop semantics
- `contracts/WORK_ORDER.md` — mission/work-order contract
- `contracts/TRACE.md` — feedback/provenance contract
- `docs/CONTROLLER.md` — thin Controller contract
- `docs/CONTROLLER_QUICKSTART.md` — Controller usage
- `docs/ROUTING.md` — roles/profiles/lenses
- `docs/DOCUMENTATION_STEWARDSHIP.md` — durable diagrams/domain/process/cheat-sheet rules
- `docs/CONTEXT_BOOTSTRAP.md` — fresh-chat/repo bootstrap
- `docs/EXECUTION_MODEL.md` — Lawrence + ChatGPT + Controller + worker model
- `docs/PROJECT_ADOPTION.md` — adding OODA to repos
- `docs/REPO_WATCHER.md` — future observation collector

**If the front door starts feeling complicated again, treat that as an OODA product bug.**
