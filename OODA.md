# OODA Operating Doctrine

## Mission

OODA is a provider-neutral operating doctrine and control system for AI-assisted research, engineering, product development, and consequential decision-making.

Its purpose is to maximize adaptive learning and useful output while controlling cost, fragility, epistemic error, and operational risk.

## Two spaces

### 1. Creative thinking space

Lawrence and ChatGPT may discuss raw thoughts, goals, product ideas, investment theses, strange hypotheses, models, architectures, and cross-domain connections without creating a task.

No work order is required until an idea deserves meaningful execution resources or repository mutation.

### 2. Execution space

Once an idea is worth acting on, OODA creates a bounded execution contract.

This boundary protects creativity from bureaucracy and protects execution from uncontrolled scope.

## The loop

### OBSERVE — establish reality

Determine what is actually true before reasoning from it.

Typical observations include:
- repository, branch, HEAD, dirty state, worktree type, active PRs;
- current durable state and explicit authority;
- data availability, provenance, timestamps, missingness, and prior artifacts;
- prior experiments, including negative results;
- actual costs, failures, test state, constraints, protected surfaces, and unknowns.

Separate verified facts from inference.

### ORIENT — synthesize and challenge

Orientation is the intellectual center of OODA.

Apply one accountable role, one expertise profile, and the smallest useful lens set. Normally activate no more than three lenses.

Orientation should:
- form competing explanations, not one narrative;
- challenge potentially deceptive objectives;
- seek interesting anomalies and stepping stones;
- inspect fragility, tail risk, and irreversible downside;
- assess uncertainty and selection effects;
- connect evidence to the user's actual objective;
- consider whether doing nothing is better.

Bounded work does not mean bounded imagination.

### DECIDE — choose one high-value move

Select the smallest action that materially reduces uncertainty, creates value, or resolves a dependency.

A decision should establish:
- what is being tested or changed;
- why this action has high information or economic value;
- what would falsify or invalidate it;
- the cost/risk/authority envelope;
- why broader work is not yet justified.

A decision is a hypothesis about which action is worth taking.

### ACT — execute and verify

Execute only the chosen move. Verify the result. Persist the minimum durable evidence needed to prevent rediscovery. Feed the outcome into the next observation.

An action may be a research experiment, architecture decision, product prototype, code change, model validation, portfolio analysis, execution study, or risk review.

Act also includes a **documentation-impact check**: if the work materially changed how the domain, architecture, process, interfaces, operator workflow, research method, commands, or authority should be understood, update the smallest durable artifact that prevents future confusion.

## OODA is embedded in the operating system

OODA should appear in the way work is selected and verified, not as decorative terminology.

### Repository level

Durable project state supports **Observe**:

- `.ooda/project.json` — routing/authority hints;
- `PROJECT_STATE.md` — concise current truth and next gate;
- `AGENTS.md` — standing invariants/authority;
- stable domain/architecture/process documentation — durable orientation substrate;
- Git/PR/tests/artifacts — execution evidence.

### Work-order level

A work order is the compact output of **Observe → Orient → Decide** and the envelope for **Act**:

```text
current truth
    ↓
role/profile/lenses
    ↓
one bounded objective
    ↓
scope + verification + budget + stops + authority
```

The contract should be explicit enough to prevent drift but not so verbose that constructing it becomes the work.

### Worker level

The worker runs the loop inside the mission:

```text
observe current task truth
        ↓
orient to uncertainty/risk
        ↓
decide next bounded tactic
        ↓
act + verify
        ↓
new observation
```

When a major new fact invalidates the mission's assumptions or authority envelope, the worker stops and returns for re-orientation instead of blindly completing the original plan.

### Trace level

The trace is the feedback edge into the next loop. It records concise Observe / Orient / Decide / Act provenance, verification, result, documentation impact when material, and the next human/control gate.

## Loop speed

OODA is not a ceremonial waterfall. Tiny obvious work may compress the loop. High-uncertainty or consequential work may re-observe and re-orient several times before action.

The goal is not merely to cycle faster. It is to maintain a more accurate orientation and make better bounded moves.

Faster OODA does **not** mean filling out more forms faster. It means:

- current state is cheap to reconstruct;
- orientation uses only the context that can change the decision;
- missions are small enough to produce feedback quickly;
- surprising evidence triggers re-orientation early;
- useful results/negative findings are persisted so the next loop starts ahead.

## Controller and worker separation

The OODA Controller keeps portfolio/context overhead small.

It may:

- accept raw thoughts;
- decide whether an idea deserves worker resources;
- propose/construct bounded work orders;
- select role/profile/lenses/claim level;
- surface blockers/human gates;
- re-orient from worker traces.

It should not become the deep researcher or engineer.

If robust work-order construction requires facts outside compact control state, the Controller first dispatches a short orientation spike to a `researcher`, `architect`, `validator`, or other appropriate worker, then constructs the work order from the returned evidence.

This gives us a useful rule:

> **Think enough to route; investigate enough to orient; delegate the expensive context.**

## Documentation stewardship

Documentation is part of durable orientation.

The purpose is not to document activity. It is to preserve explanations that reduce future context cost and prevent incorrect mental models.

Material candidates include:

- domain models and glossaries;
- architecture/component diagrams;
- data/process/authority flows;
- interfaces/contracts;
- command/configuration cheat sheets;
- research methodology and evidence gates;
- stable negative findings.

The active worker first assesses documentation impact. An `architect` should review structure when boundaries/flows changed materially. A `validator` may independently audit documentation when accuracy is consequential or the conceptual change is broad.

Do not create a permanent documentation-auditor role. See `docs/DOCUMENTATION_STEWARDSHIP.md`.

## Operating principles

1. **Free-form thought upstream; structured execution downstream.**
2. **Search widely; act narrowly.**
3. **Use the cheapest process that can support the claim being made.**
4. **Exploration is encouraged; promotion requires evidence.**
5. **Preserve useful negative information.**
6. **Prefer reversible experiments before irreversible commitments.**
7. **Treat cost, context, and attention as scarce capital.**
8. **Protect against ruin before optimizing expected gain.**
9. **Separate research, portfolio construction, execution, and risk authority when money is involved.**
10. **Separate development from validation for consequential models and systems.**
11. **Verify substrate before trusting sophistication built on top of it.**
12. **Usage earns automation. Automation does not precede understanding.**
13. **Git and project evidence remain authoritative; dashboards are views.**
14. **Human/Integration Owner authority cannot be implied from green tests or agent confidence.**
15. **Substantial conceptual change deserves a documentation-impact check before handoff.**
16. **The action is not operationally complete until useful feedback can enter the next loop.**

## Intellectual foundations

OODA uses ideas, not personalities.

- **Boyd:** orientation, feedback, adaptation, decisions as hypotheses and actions as tests.
- **Stanley/Lehman:** ambitious objectives may be deceptive; novelty and stepping stones can uncover paths objective optimization misses.
- **Taleb:** focus on nonlinear exposure, fragility, ruin, convexity, optionality, and via negativa.
- **Scientific method:** falsification, replication, explicit uncertainty, and evidence proportional to the claim.
- **Model risk:** limitations, validation, monitoring, intended use, data quality, and independent challenge.

These are lenses available during orientation, not mandatory personas that all run on every task.
