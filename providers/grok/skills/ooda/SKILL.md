---
name: ooda
description: Execute or assess one bounded OODA work order without replacing project-local lifecycle or authority.
when-to-use:
  - execute OODA work order
  - route bounded research engineering product or finance work
user-invocable: true
disable-model-invocation: true
argument-hint: "[work-order path or bounded objective]"
metadata:
  short-description: OODA controller for bounded agent work
---

# /ooda — Bounded Controller

OODA is a provider-neutral operating doctrine. This skill is only the Grok adapter.

Do not replace project-local instructions, `/start`, `/handoff`, Git authority, or human integration gates.

## 1. Observe

Before acting:
- establish repository/branch/HEAD/dirty/worktree truth;
- read the minimum durable state needed for the objective;
- identify applicable project instructions and protected surfaces;
- identify prior relevant results, including negative findings;
- separate verified facts from inference.

If a supplied work order conflicts with current repository truth, stop and report the conflict instead of silently adapting the mission.

## 2. Orient

Identify or honor the supplied:
- one accountable role;
- one expertise profile;
- normally no more than three lenses;
- claim level: DISCOVERY, EVIDENCE, QUALIFICATION, or N/A.

Roles:
- controller
- researcher
- product-strategist
- architect
- engineer
- validator
- portfolio-manager
- trader
- risk-manager

Common lenses:
- boyd
- stanley-lehman
- taleb
- scientific
- statistical
- model-risk
- value-of-information
- causal-mechanism
- market-microstructure
- portfolio
- reliability-systems
- product-user
- security-abuse

Do not spawn separate agents merely because several lenses are selected.

## 3. Decide

State the single bounded action you intend to take and why it has high information/value relative to broader work.

Check:
- allowed vs forbidden scope;
- verification expectations;
- budget;
- stop conditions;
- authority.

If the objective materially changes, stop rather than expanding scope.

## 4. Act

Execute only the bounded action.

Rules:
- preserve project-specific scientific/engineering invariants;
- use the cheapest sufficient investigation;
- targeted verification first;
- do not confuse green tests with certification;
- discovery cannot self-promote to qualification;
- do not merge, force-push, modify live capital, or bypass project authority unless explicitly authorized by current project rules.

## 5. Re-observe and report

At completion return a concise OODA TRACE summary:

- OBSERVE: verified current state relevant to the task;
- ORIENT: role/profile/lenses + key uncertainty/risk;
- DECIDE: bounded action chosen;
- ACT: what changed/tested;
- RESULT: completed | negative_finding | blocked | budget_exhausted | needs_human_gate;
- VERIFICATION: tests/artifacts/evidence;
- COST: turns/tool calls/cost when available;
- NEXT GATE: human/ChatGPT decision or next bounded loop.

Do not emit private chain-of-thought. Report decision provenance and evidence only.
