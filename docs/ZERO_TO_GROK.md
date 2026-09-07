# Zero to Grok with OODA

This is the copy/paste path from a fresh machine to an OODA Controller conversation and, when warranted, a bounded worker mission.

---

## A. First-time install

### Pip from GitHub

Once the repository is public:

```bash
python3 -m pip install "git+https://github.com/mldugom/ooda.git"
ooda setup
ooda help
```

This installs:

- `ooda` command;
- `grok-safe` command;
- Grok `/ooda` worker skill;
- Grok `/ooda-controller` Controller skill;
- bundled Grok efficiency policy.

The distribution name is `ooda-ai`; do not run `pip install ooda`, which is a different project.

### Or install from a clone

```bash
mkdir -p ~/repos
cd ~/repos
git clone https://github.com/mldugom/ooda.git
cd ooda
bash install.sh
ooda help
```

If a clone install cannot find `ooda`, ensure `~/.local/bin` is on `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## B. Adopt an existing checked-out repo

Assume an existing product repo is already at:

```text
~/repos/example-app
```

If it already has useful README/architecture/process documentation, add only OODA's thin overlay:

```bash
cd ~/repos/example-app

ooda init \
  --project-id example-app \
  --project-class software-product

ooda doctor
```

Do **not** use `--scaffold` just because it exists. Use it for a new/empty repo that needs the starter pack, not to compete with existing durable documentation.

This creates:

```text
.ooda/
  project.json
  work-orders/
  traces/
```

It does not rewrite application code or existing project docs.

---

## C. Open Grok and ask a repo-level question

From the target repo:

```bash
cd ~/repos/example-app
grok-safe
```

Then in Grok:

```text
/ooda-controller Jump into this repo. Use only the minimum durable repo/control state needed to orient. I want to think about <your question>. Do not do deep code archaeology or implementation yourself; if deeper evidence is required, propose the smallest worker/orientation mission.
```

Example:

```text
/ooda-controller I want to decide the highest-value next product/engineering move. Use compact current state only. If you need deeper product or architecture facts, propose the smallest orientation spike rather than loading the whole repo yourself.
```

The Controller normally ends with one of:

```text
KEEP THINKING
PROPOSE MISSION
HUMAN GATE
NO ACTION
```

---

## D. If the Controller needs deeper repo facts

A Controller may propose an orientation spike such as:

```text
PROPOSE MISSION
role: architect
profile: full-stack
lenses: product-user, reliability-systems
claim: n-a
objective: Inspect only the architecture, key entrypoints, and current durable backlog/state necessary to identify the smallest coherent next vertical slice. Return concise constraints and a recommended boundary; do not implement.
```

Create it:

```bash
ooda mission \
  "Inspect only the architecture, key entrypoints, and current durable backlog/state necessary to identify the smallest coherent next vertical slice. Return concise constraints and a recommended boundary; do not implement." \
  --role architect \
  --profile full-stack \
  --lenses product-user,reliability-systems \
  --claim n-a \
  --id ORIENT-001
```

Default output:

```text
.ooda/work-orders/ORIENT-001.json
```

---

## E. Execute the bounded worker mission

Start a separate worker session from the same repo:

```bash
cd ~/repos/example-app
grok-safe
```

Then:

```text
/start
/ooda .ooda/work-orders/ORIENT-001.json
```

The worker should:

```text
OBSERVE current repo/task truth
        ↓
ORIENT under role/profile/lenses
        ↓
DECIDE one bounded tactic
        ↓
ACT + verify
        ↓
RE-OBSERVE
        ↓
/handoff
```

Bring the handoff/result to the human + ChatGPT and/or the Controller for review/reorientation.

---

## F. Record the result

```bash
ooda trace \
  --work-order .ooda/work-orders/ORIENT-001.json \
  --result completed \
  --summary "Architecture/product orientation completed; returned a bounded candidate vertical slice and constraints."
```

Default output:

```text
.ooda/traces/ORIENT-001.json
```

For a useful negative result:

```bash
ooda trace \
  --work-order .ooda/work-orders/ORIENT-001.json \
  --result negative_finding \
  --summary "Current architecture/user workflow does not support the proposed slice without a materially broader redesign."
```

---

## G. Ask the Controller to re-orient

Return to the Controller conversation, or start a fresh one:

```bash
cd ~/repos/example-app
grok-safe
```

Then:

```text
/ooda-controller Re-observe this repo from the latest active work orders/traces and compact project state. ORIENT-001 is complete. What is the best next bounded move?
```

A fresh Controller session is fine. Durable state, not chat history, is the memory.

---

## H. If you already know the bounded implementation task

Do not create an orientation spike just for ceremony.

```bash
cd ~/repos/example-app

ooda mission \
  "Implement the approved bounded vertical slice described in the current project docs. Do not broaden into unrelated subsystems." \
  --role engineer \
  --profile full-stack \
  --lenses product-user,reliability-systems \
  --claim n-a \
  --id ENG-001

grok-safe
```

Then in Grok:

```text
/start
/ooda .ooda/work-orders/ENG-001.json
```

After handoff/review:

```bash
ooda trace \
  --work-order .ooda/work-orders/ENG-001.json \
  --result completed \
  --summary "Approved vertical slice implemented and verified; ready for integration review."
```

---

## I. Optional Control Room

The Control Room is optional and may live in another repository or local checkout:

```bash
OODA_CONTROL_ROOM_DIR=/path/to/control-room ooda dashboard
```

or, when you have an accessible clone URL:

```bash
OODA_CONTROL_ROOM_REPO=<clone-url> ooda dashboard
```

The dashboard is derived observation state. It does not replace Git, work orders, traces, tests, PRs, or human authority.

---

# Shortest version

First-time pip install:

```bash
python3 -m pip install "git+https://github.com/mldugom/ooda.git"
ooda setup
```

Adopt an existing repo once:

```bash
cd ~/repos/example-app
ooda init --project-id example-app --project-class software-product
ooda doctor
```

Talk to the Controller:

```bash
grok-safe
```

```text
/ooda-controller Jump into this repo. I want to think about <question>. Stay controller-sized; if deep evidence is needed, propose the smallest worker mission.
```

That is enough to start using OODA.
