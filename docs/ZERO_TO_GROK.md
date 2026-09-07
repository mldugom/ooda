# Zero to Grok with OODA

This is the copy/paste path from a fresh machine to one OODA Controller conversation that can dispatch bounded child workers when needed.

## A. First-time install

### Clone — recommended

```bash
mkdir -p ~/repos
cd ~/repos
git clone https://github.com/mldugom/ooda.git
cd ooda
bash install.sh
```

If the installer says `~/.local/bin` was not active in the current shell, run the exact `export PATH=...` line it prints (or open a new terminal).

Verify:

```bash
ooda help
grok-safe --help
```

### Or pip from GitHub

```bash
python3 -m pip install "git+https://github.com/mldugom/ooda.git"
ooda setup
```

This provides `ooda`, `grok-safe`, `/ooda`, `/ooda-controller`, and the bundled Grok efficiency policy after setup.

## B. Adopt an existing checked-out repo

```bash
cd ~/repos/example-app

ooda init \
  --project-id example-app \
  --project-class software-product

ooda doctor
```

For an existing repo with useful docs, normally do **not** use `--scaffold`. OODA adds only:

```text
.ooda/
  project.json
  work-orders/
  traces/
```

## C. Open one Controller conversation

```bash
cd ~/repos/example-app
grok-safe
```

Then:

```text
/ooda-controller Jump into this repo. Use only the minimum durable repo/control state needed to orient. I want to think about <your question>. If deeper evidence or implementation is required, construct the smallest bounded mission and delegate it rather than absorbing the deep task context yourself.
```

Possible outcomes:

```text
KEEP THINKING
PROPOSE MISSION
HUMAN GATE
NO ACTION
```

## D. When deeper facts are needed

The Controller may create/propose an orientation mission such as:

```text
role: architect
profile: full-stack
lenses: product-user, reliability-systems
claim: n-a
objective: Inspect only the architecture, key entrypoints, and current durable state needed to identify the smallest coherent next vertical slice. Return concise constraints and a recommended boundary; do not implement.
```

A durable contract can be created with:

```bash
ooda mission \
  "Inspect only the architecture, key entrypoints, and current durable state needed to identify the smallest coherent next vertical slice. Return concise constraints and a recommended boundary; do not implement." \
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

## E. Preferred: inline child execution

When execution is authorized and Grok child agents are available, the Controller may dispatch the bounded work order **inside the same Controller session**.

```text
CONTROLLER
    |
    | work order explicit
    v
CHILD WORKER
separate deep context
    |
    v
/handoff + concise evidence/result
    |
    v
CONTROLLER re-observes
```

The child owns deep code/research/data context. The Controller should receive only the compact result required for the next decision.

Default to one active child mission at a time.

You do not need to open another terminal just because a worker exists.

## F. Optional: standalone worker session

Use a separate session when duration, concurrency, isolation, or independent review makes it materially better:

```bash
cd ~/repos/example-app
grok-safe
```

```text
/start
/ooda .ooda/work-orders/ORIENT-001.json
```

Both inline and standalone workers obey the same mission contract.

## G. Record durable feedback

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

Negative findings should be preserved too:

```bash
ooda trace \
  --work-order .ooda/work-orders/ORIENT-001.json \
  --result negative_finding \
  --summary "Current architecture/user workflow does not support the proposed slice without a materially broader redesign."
```

## H. Re-orient

In the same Controller conversation:

```text
Re-observe from ORIENT-001 and the latest durable state. What is the best next bounded move?
```

Or restart Grok and `/ooda-controller`. A fresh Controller is fine because durable state—not chat history—is the memory.

## I. Dashboard

```bash
ooda dashboard
```

The bundled local Control Room scans OODA-adopted repos under `~/repos` and shows compact project/mission/trace/Git state. It has manual refresh and defaults to a 60-second browser refresh.

For a different project root:

```bash
OODA_PROJECTS_ROOT=/path/to/repos ooda dashboard
```

## Shortest version

```bash
# install once
cd ~/repos
git clone https://github.com/mldugom/ooda.git
cd ooda
bash install.sh

# adopt one repo
cd ~/repos/example-app
ooda init --project-id example-app --project-class software-product
ooda doctor

# one Controller UI
grok-safe
```

Then:

```text
/ooda-controller Jump into this repo. Help me think about <question>. Stay controller-sized. If the idea earns work, construct a bounded mission and use an isolated child worker for the deep task when appropriate.
```
