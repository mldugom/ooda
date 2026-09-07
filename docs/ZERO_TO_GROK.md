# Zero to Grok with OODA

This is the copy/paste path from a fresh machine/repo checkout to an OODA Controller conversation and, when warranted, a bounded worker mission.

The example uses `mldugom/AutotoxPassport`, an existing iOS product repo. Because it already has substantial documentation, adopt it with the thin `.ooda/` overlay rather than generating starter boilerplate.

---

## A. First-time OODA install

```bash
mkdir -p ~/repos
cd ~/repos

git clone git@github.com:mldugom/ooda.git
cd ooda
bash install.sh

ooda help
```

If your shell cannot find `ooda`, ensure `~/.local/bin` is on `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Persist that line in `~/.zshrc` only if your shell does not already include it.

`bash install.sh` installs/symlinks:

- `ooda` CLI;
- Grok `/ooda` worker skill;
- Grok `/ooda-controller` Controller skill.

---

## B. Existing repo is already checked out

Assume this already exists:

```text
~/repos/AutotoxPassport
```

Go there:

```bash
cd ~/repos/AutotoxPassport
```

Adopt it into OODA:

```bash
ooda init \
  --project-id AutotoxPassport \
  --project-class software-product

ooda doctor
```

Do **not** use `--scaffold` for an existing mature repo unless you explicitly want the missing starter files created. AutotoxPassport already has architecture/process/diagram/product documentation, so the thin overlay is preferable.

This creates:

```text
.ooda/
  project.json
  work-orders/
  traces/
```

It does not rewrite the application code or existing docs.

---

## C. Open Grok and ask a repo-level question

From the target repo directory:

```bash
cd ~/repos/AutotoxPassport
grok-safe
```

Then in Grok:

```text
/ooda-controller Jump into AutotoxPassport. Use only the minimum durable repo/control state needed to orient. I want to think about <your question>. Do not do deep code archaeology or implementation yourself; if deeper evidence is required, propose the smallest worker/orientation mission.
```

Concrete example:

```text
/ooda-controller Jump into AutotoxPassport. I want to decide what the highest-value next product/engineering move is for the prototype. Use compact current state only. If you need deeper product or architecture facts, propose the smallest orientation spike rather than loading the whole repo yourself.
```

The Controller should normally end with one of:

```text
KEEP THINKING
PROPOSE MISSION
HUMAN GATE
NO ACTION
```

The Controller is allowed to help frame raw thoughts and construct missions. It is not the deep researcher/engineer.

---

## D. If the Controller needs deeper repo facts

A good Controller response may propose an orientation spike such as:

```text
PROPOSE MISSION
role: architect
profile: ios-swiftui
lenses: product-user, reliability-systems
claim: n-a
objective: Inspect only the existing architecture, key app entrypoints, and current backlog necessary to identify the smallest coherent next vertical slice. Return concise constraints and recommended boundary; do not implement.
```

Create that mission from the shell:

```bash
ooda mission \
  "Inspect only the existing architecture, key app entrypoints, and current backlog necessary to identify the smallest coherent next vertical slice. Return concise constraints and recommended boundary; do not implement." \
  --role architect \
  --profile ios-swiftui \
  --lenses product-user,reliability-systems \
  --claim n-a \
  --id ATP-ORIENT-001
```

Default output:

```text
.ooda/work-orders/ATP-ORIENT-001.json
```

---

## E. Execute the bounded worker mission

Start a separate Grok worker session from the same repo:

```bash
cd ~/repos/AutotoxPassport
grok-safe
```

Then:

```text
/start
/ooda .ooda/work-orders/ATP-ORIENT-001.json
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

Bring the handoff/result back to Lawrence + ChatGPT and/or the Controller for review/reorientation.

---

## F. Record the result

Example successful orientation spike:

```bash
ooda trace \
  --work-order .ooda/work-orders/ATP-ORIENT-001.json \
  --result completed \
  --summary "Architecture/product orientation completed; returned bounded candidate vertical slice and constraints."
```

Default output:

```text
.ooda/traces/ATP-ORIENT-001.json
```

If the spike invalidates the idea instead:

```bash
ooda trace \
  --work-order .ooda/work-orders/ATP-ORIENT-001.json \
  --result negative_finding \
  --summary "Current architecture/user workflow does not support the proposed slice without a materially broader redesign."
```

---

## G. Ask the Controller to re-orient

Return to your Controller conversation, or start a fresh one:

```bash
cd ~/repos/AutotoxPassport
grok-safe
```

Then:

```text
/ooda-controller Re-observe AutotoxPassport from the latest active work orders/traces and compact project state. ATP-ORIENT-001 is complete. What is the best next bounded move?
```

A fresh Controller session is fine. Durable state, not chat history, is the memory.

---

## H. If you already know the bounded implementation task

You do not need an orientation spike just to obey ceremony.

Example:

```bash
cd ~/repos/AutotoxPassport

ooda mission \
  "Implement the approved bounded SwiftUI vertical slice described in the current project docs. Do not broaden scope into unrelated AR, BLE, persistence, or backend work." \
  --role engineer \
  --profile ios-swiftui \
  --lenses product-user,reliability-systems \
  --claim n-a \
  --id ATP-ENG-001

grok-safe
```

Then in Grok:

```text
/start
/ooda .ooda/work-orders/ATP-ENG-001.json
```

After handoff/review:

```bash
ooda trace \
  --work-order .ooda/work-orders/ATP-ENG-001.json \
  --result completed \
  --summary "Approved SwiftUI vertical slice implemented and verified; ready for human/ChatGPT integration review."
```

---

## I. Open the Control Room

From anywhere after OODA is installed:

```bash
ooda dashboard
```

The dashboard is a derived observation surface. It does not replace Git, work orders, traces, tests, PRs, or human authority.

---

# The shortest version

First time only:

```bash
cd ~/repos
git clone git@github.com:mldugom/ooda.git
cd ooda
bash install.sh
```

Adopt existing repo once:

```bash
cd ~/repos/AutotoxPassport
ooda init --project-id AutotoxPassport --project-class software-product
ooda doctor
```

Talk to the Controller:

```bash
cd ~/repos/AutotoxPassport
grok-safe
```

```text
/ooda-controller Jump into AutotoxPassport. I want to think about <question>. Stay controller-sized; if deep evidence is needed, propose the smallest worker mission.
```

That is enough to start using OODA.
