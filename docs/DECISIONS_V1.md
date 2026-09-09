# OODA V1 Decisions

This file records decisions that should not be rediscovered from chat history.

## Identity

OODA is a provider-neutral control system, not a rename or fork of any specific agent runtime.

Provider-specific runtimes and skills may be reference implementations. OODA may learn from them without inheriting local-runtime coupling by default.

## Mission

**OODA is a provider-neutral operating doctrine and control system for AI-assisted research, engineering, product development, and consequential decision-making.**

Finance/ML/data science are first-class domains, not the boundary. SaaS, apps, APIs, browser extensions, analytical products, automation, and agent systems use the same core doctrine.

## Existing execution is preserved

During V1:

- human + ChatGPT remain the creative/strategic upstream layer;
- a configured provider executes bounded missions;
- project-local start/handoff, Git/PR, testing, and human integration behavior remain authoritative;
- OODA adds a work order before substantial execution and a trace after useful outcomes;
- existing provider infrastructure is not rewritten merely to adopt OODA.

## Roles

Universal:
1. Controller
2. Researcher
3. Product Strategist
4. Architect
5. Engineer
6. Validator

Finance extension:
7. Portfolio Manager
8. Trader / Execution Strategist
9. Risk Manager

Expertise is expressed through profiles rather than proliferating specialist bots.

## Lenses

V1 lenses:
- Boyd / OODA
- Stanley–Lehman / novelty and stepping stones
- Taleb / fragility, convexity, optionality, via negativa
- Scientific
- Statistical
- Model Risk
- Value of Information
- Causal / Mechanism
- Market Microstructure
- Portfolio
- Reliability / Systems
- Product / User
- Security / Abuse

Default: one role + one profile + no more than three lenses for one bounded action.

## Claim levels

1. Discovery — cheap learning; not promotion eligible.
2. Evidence — meaningful scrutiny and reproducibility.
3. Qualification — sufficient rigor for consequential reliance, subject to explicit human gate.
4. N/A — ordinary implementation/product work with no empirical claim promotion.

Rigor scales with claim, use, materiality, and downside.

## Research visualization

Visual output follows an escalation ladder rather than a “plot everything” default:

1. text/table for exact values and gates;
2. diagnostic plot when visual shape/path/relationship changes the decision;
3. durable panel only for a stable view that will be revisited;
4. research dashboard only when several stable panels support one recurring workflow;
5. live monitor only when wall-clock freshness can change an action and decision-time availability is explicit.

A dashboard is a curated derived observation surface, not a folder browser and not a second source of research truth. Historical experiment numbering should not become the permanent dashboard navigation model by default.

See `docs/RESEARCH_VISUALIZATION.md`.

## Control Room

Remain separate and read-only.

Generate real OODA traces first, then design monitor ingestion around information proven useful. The monitor does not become OODA's Controller or source of truth.

## Automation

V1 is manual/shadow control.

Do not yet assume:

- autonomous consequential dispatch;
- background workers;
- automatic provider routing;
- retries;
- always-on scheduling;
- database/job queue;
- automatic merge;
- model promotion;
- live-capital execution.

Each future automation should consume the same provider-neutral work-order/trace boundary and be earned by repeated manual use.
