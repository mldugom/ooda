---
name: ooda
description: Execute one bounded OODA mission without replacing project-local lifecycle or authority.
when-to-use:
  - execute OODA work order
  - route bounded research engineering product or finance work
user-invocable: true
disable-model-invocation: true
argument-hint: "[work-order path or bounded objective]"
metadata:
  short-description: OODA bounded worker adapter
---

# /ooda — Bounded Worker Adapter

Execute one bounded mission inside its envelope, re-orienting when reality
changes. Do not replace project-local instructions, `/start`, `/handoff`, Git
authority, or human integration gates.

## Is this small?

Deterministic, reversible, local, no empirical claim, no architecture change, no
production or capital effect → fix it, run the targeted test, report in a line or
two. No evidence packet, no validator, no documentation review, no dashboard
update. Skip the rest of this file.

## 1. Observe

Establish branch/HEAD/dirty truth and read only the durable state the objective
needs. **Authority depends on the question:** the runtime owns live state, Git
owns repository state, the frozen artifact owns the preregistered contract, the
verified trace owns what a mission concluded. PROJECT_STATE and dashboards never
outrank the owner of the fact. Flag stale state rather than acting on it; if you
cannot see the runtime, say so instead of inferring it.

If the mission depends on local datasets, an operator-host runtime, private
files, live processes, GPUs, or credentials — **verify they are present here
before doing data-dependent work.** If they are absent, stop and return the route
("code built here, evaluation must run on host X"). Do not implement blind
against data you cannot see.

If the work order conflicts with repository truth, stop and report the conflict
rather than silently adapting.

## 2. Orient

State the key uncertainty that could invalidate the action. Honor any supplied
claim ceiling. `role` / `profile` / `lens` are optional — if the mission supplied
none, direct scientific constraints are sufficient; do not invent ceremony.

For predictive or modelling work, read `reference/predictive-science.md` and
confirm the mission has a target charter before substantial modelling. If the
target is unclear or moving, stop and get it frozen first.

## 3. Decide

State the single bounded action and why it has high information value now. Check
allowed vs forbidden scope, verification, budget, stop condition, authority.
If the objective materially changes, stop rather than expanding scope.

## 4. Act

Cheapest sufficient investigation; targeted verification first. Preserve project
scientific and engineering invariants. Green tests are not certification.
Discovery cannot self-promote. Do not merge, force-push, mutate live runtime, or
touch capital without explicit authority.

**Prefer deterministic checks over prose assertions.** Where the project has (or
can cheaply gain) executable checks for point-in-time correctness, split
membership, holdout sealing, target construction, missingness, leakage fields,
arithmetic identities, or metric invariants — run them and report their result.
Code asserts admissibility; you interpret it.

Re-observe during execution: if a material new fact appears, ask whether it
changes orientation, and stop for a new decision if the objective or authority no
longer holds. Bounded tactical corrections inside scope are fine.

If a materially different idea appears, capture it as a compact note and continue
the current subject. It belongs in a fork or a later mission, not this one.

## 5. Report — compact durable record

```text
RESULT:      completed | negative_finding | blocked | budget_exhausted | needs_human_gate
EVIDENCE:    the finding, with sample/metric/uncertainty where empirical
ARTIFACTS:   pointers, not contents
NON-CLAIMS:  what this does NOT establish, and the claim ceiling reached
BLOCKER:     typed, if blocked (see below)
NEXT UNKNOWN: highest-value uncertainty this exposed
HUMAN GATE:  decision needed, or none
STATE:       branch/commit/PR pointer
```

Do not restate the work order, replay the session, or paste raw output. Do not
duplicate mutable facts a fresh session can query authoritatively.

**A negative result is a success.** No signal, insufficient data, weak features,
poorly conditioned target, not identifiable — report it plainly and stop. Do not
respond by adding features, trying more models, or changing the target. Changing
a frozen target is a re-orientation decision for the Controller and the operator,
never a worker's edit.

### If blocked, type it

```
blocker_type:        scientific | data | environment | authority | promotion | sequencing
blocked_for:         exploration | evidence | qualification | production | capital
claim_ceiling:       discovery | evidence | qualification | n-a
exploration_allowed: yes | no
target:              (scientific only — the exact unidentifiable quantity)
```

Stages describe evidence, never permission. `sequencing` alone never stops work.
Before reporting blocked, answer in one line:
`Cheap honest experiment available? yes/no — <what, or why not>`. Do not restate
the question or give it a section.

## Load on demand

- `reference/predictive-science.md` — predictive/modelling work
- `reference/visualization.md` — choosing an evidence surface
- `reference/validation-routing.md` — is independent validation needed?
- `reference/documentation-impact.md` — did the conceptual surface change?
- `reference/runtime-reliability.md` — live processes, locking, mutable substrates

## Design rule

> Make current truth cheap to establish and feedback cheap to preserve — without
> skipping orientation or verification.
