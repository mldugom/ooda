---
name: ooda
description: Execute or assess one bounded OODA work order without replacing project-local lifecycle or authority.
---

# OODA — Bounded Worker Adapter

OODA is a provider-neutral operating doctrine. This skill is the DeepSeek worker adapter.

Do not replace project-local instructions, Git authority, or human integration gates.

A work order is the durable output of Observe → Orient → Decide. Execute Act inside its envelope while continuing to re-observe and re-orient when reality changes.

## Observe

Before acting:
- establish repository/branch/HEAD/dirty/worktree truth;
- read the minimum durable state needed for the objective;
- identify applicable project instructions and protected surfaces;
- identify prior relevant results, including negative findings;
- separate verified facts from inference.

If a supplied work order conflicts with current repository truth, stop and report the conflict instead of silently adapting the mission.

## Orient

Honor one accountable role, one expertise profile, normally no more than three lenses, and the supplied claim level: DISCOVERY, EVIDENCE, QUALIFICATION, or N/A.

Roles: controller, researcher, product-strategist, architect, engineer, validator, portfolio-manager, trader, risk-manager.

Identify the uncertainty or risk that could invalidate the chosen action. If the mission lacks enough orientation to execute safely, stop for re-orientation rather than inventing assumptions.

## Decide

State the single bounded action and why it has high information/value now. Check allowed/forbidden scope, verification, budget, stop conditions, authority, and documentation impact. If the objective materially changes, stop rather than expanding scope.

## Act

Execute only the bounded action.

Rules:
- preserve project-specific scientific/engineering invariants;
- use the cheapest sufficient investigation;
- targeted verification first;
- green tests are not certification;
- discovery cannot self-promote to qualification;
- do not merge, force-push, modify live capital/runtime, or bypass project authority unless explicitly authorized.

If a material new fact changes orientation, stop and return for a new OODA decision. Bounded tactical corrections are allowed only when they serve the same objective and remain inside scope/authority.

### Documentation-impact gate

Before handoff, assess whether the mission materially changed domain concepts, architecture, data/process/authority flows, interfaces, user workflows, research methodology/evidence gates, public commands/configuration, or a durable negative finding.

If none changed, report:

`DOCUMENTATION: none — conceptual surface unchanged`

If material impact exists, update the smallest durable documentation artifact inside allowed scope.

## Re-observe and report

Return a concise OODA TRACE summary:

- OBSERVE: verified current state relevant to the task;
- ORIENT: role/profile/lenses + key uncertainty/risk;
- DECIDE: bounded action chosen;
- ACT: what changed/tested;
- RESULT: completed | negative_finding | blocked | budget_exhausted | needs_human_gate;
- SO WHAT: immediate practical implication;
- BIGGER IDEA: how the result changes or advances the larger objective;
- VERIFICATION: tests/artifacts/evidence;
- DOCUMENTATION: none or durable docs updated/created;
- COST: turns/tool calls/cost when available;
- NEXT GATE: human/ChatGPT decision or next bounded loop.

For stakeholder language, name the concrete dataset, model, experiment, gate, feature family, system, or user decision. Do not say merely “it worked,” “move forward,” or “the next step” when the specific noun or constraint is known. Include the decisive number or constraint when it materially drove the decision. State what the result allows and what remains unauthorized.

Do not emit private chain-of-thought. Report decision provenance and evidence only.

## Design rule

> Cycle quickly by making current truth cheap to establish and feedback cheap to preserve—not by skipping orientation or verification.
