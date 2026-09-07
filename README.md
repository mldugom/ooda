# OODA

**OODA is a provider-neutral operating doctrine and control system for AI-assisted research, engineering, product development, and consequential decision-making.**

OODA keeps execution bounded without making thought narrow.

The project is intentionally small. It does not replace your current agent runtime, Git workflow, or monitor. It gives them a shared doctrine and lightweight execution contracts.

## 60-second mental model

There are three different things that are easy to confuse:

1. **`ooda work-order` creates a contract file.** It does **not** launch Grok.
2. **Grok `/ooda <work-order>` reads that contract and executes the bounded mission.** Today you start Grok manually with the existing runtime.
3. **`ooda trace` creates the durable result record after the mission.** It does **not** inspect Grok logs, Git, tests, or costs automatically in V1.

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
        `ooda work-order ...`
        writes a JSON contract only
                    |
                    v
        CURRENT MANUAL PROVIDER STEP
                 `grok-safe`
                    |
                 `/start`
                    |
        `/ooda .ooda/work-orders/<task>.json`
                    |
                    v
               GROK BUILD
             one bounded mission
                    |
                    v
                `/handoff`
             Git / tests / PR
                    |
                    v
          LAWRENCE + CHATGPT
        review / accept / correct
                    |
                    v
                 RESULT
                    |
        `ooda trace --work-order ...`
        writes a durable result JSON
                    |
                    v
               NEXT OODA LOOP
```

**Rule of thumb:** think broadly, orient intelligently, act narrowly, verify reality, preserve what matters.

## What runs underneath the hood today?

| Step | What actually happens | What does **not** happen |
|---|---|---|
| `ooda init` | Writes `.ooda/project.json`, creates work-order/trace directories, and optionally creates missing starter docs. | Does not launch an agent, initialize Git, commit, or push. |
| `ooda doctor` | Reads and validates `.ooda/project.json`; reports whether expected durable state docs exist. | Does not repair files or inspect the full repository. |
| `ooda work-order` | Validates role/lenses/claim level, applies safe default budgets/authority/stop conditions, and writes `ooda/work-order/v1` JSON. | Does not launch Grok, inspect Git, fill project-specific scope, or decide whether the task is scientifically valid. |
| `grok-safe` | Existing Grok runtime launcher with your current efficiency/safety controls. | OODA does not replace it in V1. |
| `/start` | Existing Grok lifecycle bootstrap for repository/Git/project state. | OODA does not replace it in V1. |
| `/ooda <file>` | Grok's thin OODA adapter reads the work order, verifies current truth/authority, orients under the selected role/profile/lenses, and executes the bounded mission. | Does not gain merge, promotion, live-capital, or other authority not already granted. |
| `/handoff` | Existing lifecycle verifies work, pushes/updates PR where appropriate, reports truthful state, and returns control to the human/ChatGPT review gate. | Does not self-certify or self-merge. |
| `ooda trace` | Validates the work order, copies its routing metadata, records your result state/summary, and writes a trace skeleton for durable outcome/provenance. | Does not scrape Grok logs, infer OODA reasoning, inspect tests/Git, or calculate cost automatically. |
| `ooda validate` | Validates one OODA JSON contract against the lightweight V1 rules. | Does not validate the underlying scientific/engineering claim. |

### Does a worker call `grok-safe` underneath the hood?

**Not today. There is no OODA worker in V1.** The current flow is deliberately manual: create a work order, start `grok-safe`, run `/start`, then run `/ooda <work-order>`.

When the future local supervisor/worker is built, it should launch the configured provider through the provider adapter and preserve the same runtime safety/budget semantics as `grok-safe`. A daemon may not literally invoke a zsh shell function named `grok-safe`; the invariant is that it must **not bypass those controls by launching raw Grok with different defaults**.

Future shape:

```text
OODA WORK ORDER
      |
      v
LOCAL SUPERVISOR / WORKER
      |
      | validate contract + authority + budget
      v
PROVIDER ADAPTER
      |
      | Grok adapter preserves current grok-safe semantics
      v
GROK / future provider
      |
      v
Git + tests + artifacts + handoff
      |
      v
OODA TRACE + HUMAN GATE
```

## Can `--objective` be a really long prompt?

**Technically yes.** V1 requires only a non-empty string and does not impose an OODA length limit. The practical ceiling is whatever your shell/OS can pass as one command-line argument.

**Operationally, do not use `objective` as a giant chat transcript or project dump.** A work order is a control contract, not a replacement for repository state or a full prompt archive.

Good objective:

```text
Implement one Chrome-extension vertical slice that captures the current market title and price from the supported page, stores it locally, and renders it in the popup. Do not add auth, cloud storage, payments, or multi-site support. Verify on one fixture and one real supported page.
```

Poor objective:

```text
<30,000 words of previous chats, architecture discussion, terminal logs, and every idea we have ever had>
```

For a genuinely detailed task, prefer:

```text
objective: "Implement the bounded slice described in docs/tasks/extension-v0.md. Do not expand beyond that brief."
```

Then keep the detailed specification in the repository where both ChatGPT and Grok can load it only when needed. After `ooda work-order` generates the JSON skeleton, edit its `scope`, `verification`, and any project-specific stop conditions before execution when the mission needs more precision.

A multi-paragraph objective is fine if it is still one coherent bounded mission.

---

# Command cheat sheet

## OODA CLI commands

| Command | Purpose | Produces/changes |
|---|---|---|
| `ooda init` | Adopt a repo or create the OODA overlay. | `.ooda/project.json`, directories; optional starter docs. |
| `ooda doctor` | Check basic OODA project setup. | Read-only report. |
| `ooda work-order` | Create one bounded execution contract. | `ooda/work-order/v1` JSON. |
| `ooda trace` | Create one durable result/provenance record. | `ooda/trace/v1` JSON. |
| `ooda validate` | Validate an OODA JSON contract. | Read-only PASS/FAIL. |

## Framework scripts

| Command | Purpose |
|---|---|
| `./scripts/install-cli.sh` | Symlink the `ooda` CLI into `~/.local/bin` (or `$OODA_BIN_DIR`). |
| `./scripts/install-grok.sh` | Symlink the single Grok `/ooda` adapter into `~/.grok/skills/ooda` (or `$GROK_HOME`). |
| `./scripts/check.sh` | Run unit/contract tests and validate examples. |
| `./scripts/publish-github.sh` | Create/publish the OODA GitHub repo with authenticated `gh`, if `origin` does not already exist. |

## Current Grok commands used with OODA

| Command | Purpose in the current paradigm |
|---|---|
| `grok-safe` | Start Grok with the existing bounded runtime/efficiency controls. |
| `/start` | Establish checkout, Git state, durable project truth, and current objective. |
| `/ooda <work-order>` | Load and execute the bounded OODA mission. |
| `/checkpoint` | Persist/verify an in-progress session when it will continue. |
| `/handoff` | Verify, push/open-or-update PR, report truthful completion state, then stop for review. |
| `/end` | Finish the existing lifecycle when appropriate under the project's current rules. |

---

# Complete CLI reference

## `ooda init`

Create or replace the project's thin OODA routing overlay. With `--scaffold`, also create the minimal starter-pack docs **only when missing**.

### Syntax

```bash
ooda init \
  --project-id <id> \
  --project-class <class> \
  [--path <directory>] \
  [--scaffold] \
  [--force]
```

### Arguments

| Argument | Required? | Meaning | Default / choices |
|---|---:|---|---|
| `--project-id` | yes | Stable project identifier stored in `.ooda/project.json`. | Free string; normally repo name. |
| `--project-class` | yes | Broad routing class for the project. | `quantitative-research`, `trading-research`, `data-ml-system`, `software-product`, `analytical-product`, `infrastructure` |
| `--path` | no | Directory in which to create/read the OODA overlay. | `.` |
| `--scaffold` | no | Create minimal `README.md`, `AGENTS.md`, `PROJECT_STATE.md`, and `.ooda/README.md` when they are missing. | off |
| `--force` | no | Replace `.ooda/project.json` if it already exists. Starter Markdown docs are still never overwritten. | off |

### Existing-repo example

```bash
cd ~/repos/tenniskal
ooda init \
  --project-id tenniskal \
  --project-class quantitative-research
```

### New-repo example

```bash
mkdir -p ~/repos/my-extension
cd ~/repos/my-extension
git init

ooda init \
  --project-id my-extension \
  --project-class software-product \
  --scaffold
```

### Under the hood

`init` writes `.ooda/project.json` with human integration ownership, `self_merge=false`, `live_capital=false`, Grok as the current provider, and `existing_lifecycle=preserve`. It also creates `.ooda/work-orders/` and `.ooda/traces/`. `--scaffold` calls a tiny starter-template generator; it skips existing Markdown rather than overwriting it.

---

## `ooda doctor`

Check that a repository has a valid OODA project overlay and report whether the expected durable-state files exist.

### Syntax

```bash
ooda doctor [--path <directory>]
```

### Arguments

| Argument | Required? | Meaning | Default |
|---|---:|---|---|
| `--path` | no | Project directory to inspect. | `.` |

### Example

```bash
cd ~/repos/tenniskal
ooda doctor
```

### Under the hood

`doctor` validates `.ooda/project.json`, then reports whether `AGENTS.md`, `PROJECT_STATE.md`, `README.md`, and `.ooda/README.md` exist. Missing Markdown is informational; missing/invalid `.ooda/project.json` is a failure.

---

## `ooda work-order`

Create the provider-neutral contract for **one substantial bounded mission**.

### Syntax

```bash
ooda work-order \
  --objective <text> \
  --role <role> \
  --profile <profile> \
  [--lenses <comma-separated-lenses>] \
  --claim-level <level> \
  [--project-id <id>] \
  [--id <work-order-id>] \
  [--max-turns <n>] \
  [--max-investigation-steps <n>] \
  --output <path>
```

### Arguments

| Argument | Required? | Meaning | Default / choices |
|---|---:|---|---|
| `--objective` | yes | The bounded outcome/question the worker should pursue. Can be multi-paragraph, but should remain one coherent mission. | Any non-empty string. |
| `--role` | yes | Who owns the next judgment/action. | `controller`, `researcher`, `product-strategist`, `architect`, `engineer`, `validator`, `portfolio-manager`, `trader`, `risk-manager` |
| `--profile` | yes | Domain expertise needed by the selected role. | Free string, e.g. `quantitative-research`, `browser-extension`, `reliability`, `fundamental-valuation`. |
| `--lenses` | no | Comma-separated perspectives used during orientation. | empty; known lenses only; normally <=3. |
| `--claim-level` | yes | Strength of claim/reliance intended. | `discovery`, `evidence`, `qualification`, `n-a` |
| `--project-id` | no | Project identifier to store in the work order. | Current directory name. |
| `--id` | no | Stable work-order identifier. | Auto-generated `ooda-YYYYMMDD-xxxxxx`. |
| `--max-turns` | no | Provider-session turn budget recorded in the contract. | `6` |
| `--max-investigation-steps` | no | Investigation-step budget recorded in the contract. | `8` |
| `--output` | yes | JSON file to create. Parent directories are created automatically. | none |

### Research example

```bash
ooda work-order \
  --project-id tenniskal \
  --id R6E-01 \
  --objective "Test one non-overlapping lead/lag hypothesis without outcomes, ROI, or portfolio optimization." \
  --role researcher \
  --profile quantitative-research \
  --lenses scientific,statistical,market-microstructure \
  --claim-level discovery \
  --max-turns 6 \
  --max-investigation-steps 8 \
  --output .ooda/work-orders/R6E-01.json
```

### Product/engineering example

```bash
ooda work-order \
  --project-id my-extension \
  --objective "Implement one popup vertical slice that reads the supported page title and displays it locally. No auth, cloud backend, payments, or multi-site support." \
  --role engineer \
  --profile browser-extension \
  --lenses product-user,security-abuse,reliability-systems \
  --claim-level n-a \
  --output .ooda/work-orders/EXT-001.json
```

### Under the hood

`work-order`:

1. parses the comma-separated lens list;
2. validates the selected role, lenses, and claim level;
3. generates an ID unless supplied;
4. fills safe defaults:
   - empty `scope.allowed` and `scope.forbidden`;
   - empty `verification` list;
   - configured budgets;
   - stop on state conflict, objective change, missing authority, or budget exhaustion;
   - `may_merge=false`;
   - `may_promote_model=false`;
   - `may_modify_live_runtime=false`;
   - `may_spend_real_money=false`;
5. writes formatted JSON to `--output`.

**It does not launch Grok.** Review/edit the generated JSON when project-specific scope or verification needs to be explicit, then start the provider separately.

---

## `ooda trace`

Create a concise durable result record tied to an existing work order.

A trace is **not a transcript and not chain-of-thought**. It records observable decision provenance, evidence, outcome, economics when known, and the next gate.

### Syntax

```bash
ooda trace \
  --work-order <path> \
  --result-state <state> \
  --summary <text> \
  [--provider <provider>] \
  --output <path>
```

### Arguments

| Argument | Required? | Meaning | Default / choices |
|---|---:|---|---|
| `--work-order` | yes | Existing `ooda/work-order/v1` JSON that produced this run. | path |
| `--result-state` | yes | Outcome classification. | `completed`, `negative_finding`, `blocked`, `budget_exhausted`, `needs_human_gate` |
| `--summary` | yes | Truthful concise result summary. | free string |
| `--provider` | no | Provider that executed the mission. | `grok` |
| `--output` | yes | Trace JSON file to create. | path |

### Successful-result example

```bash
ooda trace \
  --work-order .ooda/work-orders/R6E-01.json \
  --result-state completed \
  --summary "Study completed; no predictive lift beyond current price state." \
  --provider grok \
  --output .ooda/traces/R6E-01.json
```

### Negative-finding example

```bash
ooda trace \
  --work-order .ooda/work-orders/FEATURE-07.json \
  --result-state negative_finding \
  --summary "Signal disappeared under non-overlapping temporal validation; do not revisit without materially new data." \
  --output .ooda/traces/FEATURE-07.json
```

### Under the hood

`trace`:

1. reads and validates the work order;
2. copies its project ID, role, profile, lenses, and claim level;
3. records the provider, result state, and your summary;
4. creates blank `observe`, `orient`, `decide`, and `act` fields;
5. initializes verification to `not_recorded` with empty tests/artifacts;
6. initializes turns/tool calls/cost to `null`;
7. sets the next gate to `Human/ChatGPT review`;
8. writes formatted JSON to `--output`.

In V1 you or the executing agent should fill the concise OODA/verification/economics fields when they are known and worth preserving. The command does **not** automatically infer them.

---

## `ooda validate`

Validate one OODA project, work-order, or trace JSON file.

### Syntax

```bash
ooda validate <file>
```

### Argument

| Argument | Required? | Meaning |
|---|---:|---|
| `file` | yes | Path to `.ooda/project.json`, a work order, or a trace. |

### Example

```bash
ooda validate .ooda/work-orders/R6E-01.json
```

Expected success output:

```text
PASS
```

### Under the hood

The validator checks the lightweight contract shape, known enums, required fields, authority-object presence, and the <=3-lens rule. It does **not** prove that the research result, code, data, or economic claim is correct.

---

# Framework script reference

## `./scripts/install-cli.sh`

One-time local CLI install.

```bash
cd ~/repos/ooda
./scripts/install-cli.sh
```

Creates a symlink:

```text
~/.local/bin/ooda -> ~/repos/ooda/scripts/ooda
```

Set `OODA_BIN_DIR` to choose another install directory:

```bash
OODA_BIN_DIR="$HOME/bin" ./scripts/install-cli.sh
```

It refuses to overwrite an existing destination.

## `./scripts/install-grok.sh`

One-time current-provider adapter install.

```bash
cd ~/repos/ooda
./scripts/install-grok.sh
```

Creates one symlink:

```text
~/.grok/skills/ooda -> ~/repos/ooda/providers/grok/skills/ooda
```

Set `GROK_HOME` to target another Grok home. Existing lifecycle skills are untouched. The installer refuses to overwrite an existing `/ooda` adapter.

## `./scripts/check.sh`

Run OODA's local framework verification:

```bash
cd ~/repos/ooda
./scripts/check.sh
```

Runs the Python unit tests and validates the example project/work-order/trace contracts. Expected final line:

```text
OODA CHECK: PASS
```

## `./scripts/publish-github.sh`

Initial publication helper for a fresh OODA repository that does not already have `origin`.

```bash
./scripts/publish-github.sh
```

Environment overrides:

| Variable | Default | Meaning |
|---|---|---|
| `OODA_GITHUB_OWNER` | `mldugom` | GitHub owner. |
| `OODA_GITHUB_REPO` | `ooda` | Repository name. |
| `OODA_GITHUB_VISIBILITY` | `private` | Visibility passed to authenticated `gh`. |

If `origin` already exists, it exits instead of changing it. This script is for initial publication, not ordinary pushes.

---

# OODA starter pack

`ooda init --scaffold` creates only the following minimal operating spine, and only when files do not already exist.

```text
my-project/
├── README.md
├── AGENTS.md
├── PROJECT_STATE.md
└── .ooda/
    ├── project.json
    ├── README.md
    ├── work-orders/
    └── traces/
```

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

---

# Work order vs trace

Think of these as the two bookends around execution:

```text
BEFORE EXECUTION                         AFTER EXECUTION

work order                               trace
---------                                -----
What are we trying to do?                What actually happened?
Who owns the action?                     What result state occurred?
What expertise/lenses apply?             What was verified?
What can/can't be touched?               What evidence/artifacts exist?
What claim level is allowed?             What did it cost?
What is the budget?                      What should happen next?
When must the agent stop?                What should we remember?
What authority exists?

          \                              /
           \                            /
            ------ bounded run --------
```

A **work order is prospective control**. A **trace is retrospective provenance**.

Neither one replaces code, research artifacts, project state, Git history, tests, or the PR.

---

# Role / profile / lens selection

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

Examples:

| Mission | Role | Profile | Lenses | Claim |
|---|---|---|---|---|
| Explore a tennis lead/lag signal | `researcher` | `quantitative-research` | `scientific,statistical,market-microstructure` | `discovery` |
| Design a Chrome extension vertical slice | `architect` | `browser-extension` | `product-user,security-abuse,reliability-systems` | `n-a` |
| Implement that slice | `engineer` | `browser-extension` | `security-abuse,reliability-systems,product-user` | `n-a` |
| Challenge a model before promotion | `validator` | `quantitative-research` | `scientific,model-risk,statistical` | `qualification` |
| Decide portfolio allocation | `portfolio-manager` | `quant-markets` | `portfolio,taleb,statistical` | `evidence` or `qualification` |

---

# Fresh ChatGPT conversations

Do not paste giant project histories by default. A fresh chat should normally start with one line such as:

```text
Jump into mldugom/tenniskal. Goal: decide the next R6E move. Use OODA. Do not execute yet.
```

Or:

```text
Continue crypto-innout PR #27. Use current repo truth, not old chat state.
```

Or:

```text
New project idea: Chrome extension for X. OODA it with me. Don't build yet.
```

ChatGPT/controller bootstraps from narrow durable repo truth. See `docs/CONTEXT_BOOTSTRAP.md` and `docs/CHATGPT_USAGE.md`.

---

# What OODA is

OODA applies John Boyd's Observe → Orient → Decide → Act loop as the control grammar for AI-assisted work.

- **Observe:** establish current reality before interpretation.
- **Orient:** synthesize facts through the smallest useful set of roles, expertise profiles, and analytical lenses.
- **Decide:** choose one high-value bounded action.
- **Act:** execute, verify, and feed the result back into observation.

Orientation is deliberately broad. Bounded execution is not permission for narrow thinking.

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
