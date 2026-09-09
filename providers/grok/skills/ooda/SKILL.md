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
  short-description: OODA bounded worker adapter
---

# /ooda — Bounded Worker Adapter

OODA is a provider-neutral operating doctrine. This skill is only the Grok worker adapter.

Do not replace project-local instructions, `/start`, `/handoff`, Git authority, or human integration gates.

A work order is the durable output of Observe → Orient → Decide. Your job is to execute Act inside its envelope while continuing to re-observe and re-orient when reality changes.

## 1. Observe

Before acting:
- establish repository/branch/HEAD/dirty/worktree truth;
- read the minimum durable state needed for the objective;
- identify applicable project instructions and protected surfaces;
- identify prior relevant results, including negative findings;
- identify relevant domain/architecture/process documentation when the mission touches those concepts;
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

Identify the key uncertainty/risk that could invalidate the chosen action. If the work order lacks enough orientation to execute safely, stop for clarification/re-orientation rather than inventing assumptions.

## 3. Decide

State the single bounded action you intend to take and why it has high information/value relative to broader work.

Check:
- allowed vs forbidden scope;
- verification expectations;
- budget;
- stop conditions;
- authority;
- foreseeable documentation impact.

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

### Re-observe during execution

Do not treat the work order as a blind completion command.

If a material new fact appears:

1. re-observe the new state;
2. ask whether it changes the mission's orientation;
3. continue only if the bounded objective/authority remain valid;
4. otherwise stop and return for a new OODA decision.

Bounded tactical corrections are allowed when they serve the same objective and remain inside scope/authority.

### Documentation-impact gate

Before handoff, assess whether the mission materially changed how the system/research should be understood.

Check for changes to:
- domain concepts/entities;
- architecture/component boundaries;
- data/process/authority flows;
- interfaces/contracts;
- user/operator workflows;
- research methodology/evidence gates;
- public commands/configuration;
- durable negative findings worth preserving.

If none changed, report:

`DOCUMENTATION: none — conceptual surface unchanged`

If material impact exists, update the smallest durable documentation artifact inside allowed scope. Prefer simple Markdown diagrams/cheat sheets/process flows that remain diffable.

For substantial structural changes, an `architect` review may be warranted. For consequential truth/consistency checks, a separate `validator` mission may be warranted. Do not create extra roles for routine documentation.

See `docs/DOCUMENTATION_STEWARDSHIP.md` in the OODA doctrine repo when available.

### Research-visualization gate

For quantitative/data-science/research work, visual output must earn its complexity.

Use this order:

1. **text/table** when exact values, a short ranking, or a pass/fail gate answers the question;
2. **diagnostic plot** when shape, path, tails, calibration, missingness, PIT/leakage, or relationship structure matters;
3. **durable panel** only when the same stable diagnostic will be revisited across missions/stages;
4. **research dashboard** only when several stable panels support one recurring operator workflow;
5. **live monitor** only when wall-clock freshness can change an operator action and decision-time availability is explicit.

Do not make one dashboard tab per research step, do not plot merely because a metric exists, and do not silently expand a bounded research mission into dashboard construction.

If visualization work is material, record one of `none`, `diagnostic`, `durable-panel`, `dashboard`, or `live-monitor` in the RESULT/TRACE plus the decision question it serves. A diagnostic plot should state the sample/provenance and what outcome would change the decision. A durable panel/dashboard must have stable sample/metric/timestamp semantics and remain derived from authoritative research artifacts.

If a dashboard becomes warranted but is outside the work-order scope, stop at a proposed panel contract and return to the Controller instead of building it opportunistically.

See `docs/RESEARCH_VISUALIZATION.md` in the OODA doctrine repo when available.

## 5. Re-observe and report

At completion return a concise OODA TRACE summary:

- OBSERVE: verified current state relevant to the task;
- ORIENT: role/profile/lenses + key uncertainty/risk;
- DECIDE: bounded action chosen;
- ACT: what changed/tested;
- RESULT: completed | negative_finding | blocked | budget_exhausted | needs_human_gate, plus the factual/technical finding;
- SO WHAT: immediate practical implication in plain stakeholder language;
- BIGGER IDEA: how the result changes or advances the larger project/research/product objective;
- VERIFICATION: tests/artifacts/evidence;
- DOCUMENTATION: none or durable docs updated/created;
- COST: turns/tool calls/cost when available;
- NEXT GATE: human/ChatGPT decision or next bounded loop.

`SO WHAT` and `BIGGER IDEA` are not marketing summaries. Name the concrete dataset, model, experiment, gate, feature family, system, or user decision whenever possible. Avoid vague relative pronouns such as “it”, “this”, or “the idea” when the actual noun is available.

For trivial administrative missions, keep these implication blocks to one line or omit them when they would add no information. For research, validation, architecture, product, and consequential engineering missions, include them.

Do not emit private chain-of-thought. Report decision provenance and evidence only.

## Design rule

> Cycle quickly by making current truth cheap to establish and feedback cheap to preserve—not by skipping orientation or verification.
