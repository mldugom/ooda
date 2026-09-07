# OODA V1 Decisions

This file records the decisions that should not be rediscovered from chat history.

## Identity

OODA is a clean-slate repository.

It is **not** a rename, forked codebase, or transition branch of `grok-skills`.

`grok-skills` is a reference implementation and current operating asset. OODA may learn from it but does not inherit its code or local-runtime coupling by default.

## Mission

**OODA is a provider-neutral operating doctrine and control system for AI-assisted research, engineering, product development, and consequential decision-making.**

Finance/ML/data science are first-class domains, not the boundary of the system. SaaS, apps, APIs, browser extensions, analytical products, automation, and agent systems use the same core doctrine.

## Current execution is preserved

During V1:
- Lawrence + ChatGPT remain the creative/strategic upstream layer.
- Existing Grok Build remains the execution provider.
- Existing project-local `/start`, `/handoff`, Git/PR, testing, and human integration behavior remains authoritative.
- OODA adds a work order before substantial execution and a trace after outcome/review.
- No existing Grok infrastructure is removed or rewritten merely to adopt OODA.

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

Rigor scales with claim, use, materiality, and downside.

## Agent Ops Monitor

Remain separate and read-only.

Do not change the monitor for OODA V1. Generate real OODA traces first, then design monitor ingestion around information proven useful.

## Automation

V1 is shadow/manual control.

Do not yet add:
- autonomous dispatch;
- background workers;
- DeepSeek routing;
- retries;
- Raspberry Pi scheduling;
- database/job queue;
- automatic merge;
- model promotion;
- live-capital execution.

Each future automation must consume the same provider-neutral work-order/trace boundary and must be earned by repeated manual use.
