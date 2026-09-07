# Role and Lens Routing

OODA routing should be understandable enough to do by hand before it is automated.

The controller chooses:

1. one accountable **role**;
2. one **profile** describing the expertise needed;
3. normally two or three **lenses** that materially improve orientation;
4. a claim level when the work makes an empirical/research claim.

OODA itself is always the backbone. Do not select `boyd` merely to prove that OODA is being used.

## Step 1 — choose the role by the decision being owned

| Primary question | Role |
|---|---|
| What is true, interesting, or worth testing? | `researcher` |
| What user problem/value proposition should we pursue? | `product-strategist` |
| How should the system/experiment/interface be designed? | `architect` |
| How should the approved bounded change be implemented? | `engineer` |
| How could this be wrong or fail independent review? | `validator` |
| Where should scarce risk/capital be allocated? | `portfolio-manager` |
| Can the theoretical edge be executed in the real market? | `trader` |
| What can cause unacceptable downside or ruin? | `risk-manager` |
| What work should happen next across stages/providers? | `controller` |

If two roles seem equally primary, the task is probably too broad. Split the work unless the second role is only a review perspective.

## Documentation is not a separate role

Documentation is a completion concern attached to the role that owns the work.

- `engineer` / `researcher` / other active worker: first documentation-impact assessment;
- `architect`: structure/diagram/domain/process review when substantial conceptual boundaries changed;
- `validator`: independent truth/consistency audit when documentation accuracy is consequential;
- `controller`: decides whether documentation belongs inside the current work order or a small follow-up mission.

Do not add `documentation-auditor`, `diagram-bot`, or similar permanent roles merely to enforce documentation hygiene. See `docs/DOCUMENTATION_STEWARDSHIP.md`.

## Work-order construction is a Controller capability

Do not add a permanent work-order-construction bot by default.

The Controller should construct robust work orders from compact durable control state. If it lacks the domain/code/research evidence required to bound the task correctly, it should request a short orientation spike under an existing role and then build the work order from the returned evidence.

Examples:

- uncertain product problem -> `product-strategist` spike;
- unknown architecture boundary -> `architect` spike;
- missing empirical fact -> `researcher` spike;
- questionable prior implementation/claim -> `validator` spike;
- narrow technical feasibility uncertainty -> `engineer` spike.

This keeps the Controller context-light without weakening planning quality.

## Step 2 — choose the profile by expertise

Profiles are not authority roles. They specialize a role without creating another bot.

Examples:

- `quantitative-research`
- `statistical-modeling`
- `data-science`
- `ml-engineering`
- `data-engineering`
- `agent-systems`
- `backend`
- `frontend`
- `full-stack`
- `browser-extension`
- `saas`
- `fundamental-valuation`
- `quant-markets`
- `market-microstructure`
- `reliability`

Profiles may grow organically; they do not need a central registry before use.

## Step 3 — choose lenses by what could change the decision

A lens is worth activating only when it is likely to change orientation, experiment design, execution, or review.

A useful default pattern is:

### One epistemic lens

Choose the dominant truth-quality concern:

- `scientific` — falsification, evidence, reproducibility;
- `statistical` — uncertainty, sample size, multiplicity, calibration;
- `model-risk` — leakage, overfit, selection, misuse, drift;
- `causal-mechanism` — mechanism versus correlation/confounding.

### One domain/implementation lens

Choose the context-specific constraint:

- `market-microstructure` — quotes, liquidity, fills, timing, adverse selection;
- `portfolio` — allocation, correlation, concentration, capacity;
- `product-user` — user problem, workflow, MVP, adoption;
- `security-abuse` — permissions, secrets, privacy, attack/abuse surface;
- `reliability-systems` — restart, stale state, idempotency, partial failure.

### Optional challenge/opportunity lens

Add only when useful:

- `taleb` — fragility, tails, convexity, via negativa, barbell;
- `stanley-lehman` — novelty, stepping stones, deceptive objectives;
- `value-of-information` — cheapest test that could change the decision;
- `boyd` — explicit adaptation/orientation emphasis when the environment is changing rapidly or current orientation may be stale.

## Typical routes

| Work | Role / profile | Lenses |
|---|---|---|
| Early quantitative hypothesis | researcher / quantitative-research | scientific + statistical + value-of-information |
| Backtest/model validation | validator / statistical-modeling | model-risk + statistical + scientific |
| Tennis/market signal research | researcher / quant-markets | statistical + market-microstructure + scientific |
| Trading execution study | trader / market-microstructure | market-microstructure + statistical + taleb |
| Portfolio sizing | portfolio-manager / quant-markets | portfolio + statistical + taleb |
| Runtime recovery bug | engineer / reliability | reliability-systems + security-abuse if relevant + taleb if downside is asymmetric |
| New SaaS idea | product-strategist / saas | product-user + value-of-information + stanley-lehman |
| SaaS architecture | architect / full-stack | product-user + security-abuse + reliability-systems |
| Chrome extension implementation | engineer / browser-extension | security-abuse + product-user + reliability-systems |
| Independent app release review | validator / full-stack | security-abuse + reliability-systems + product-user |
| New subsystem/domain/process documentation after implementation | architect / matching domain profile | reliability-systems or product-user as relevant; add another lens only if it changes the model |
| Independent documentation/diagram truth check | validator / matching domain profile | choose lenses matching the risk being verified |

## Claim levels

- `discovery`: interesting enough to investigate; cheap falsification is appropriate.
- `evidence`: the claim must survive meaningful validation, realistic economics, and reproducibility.
- `qualification`: the claim may be relied upon; stronger frozen/sealed/independent evidence is expected.
- `n-a`: implementation/product work where no empirical research claim is being promoted.

## Routing principle

**Choose the role by accountability. Choose the profile by expertise. Choose lenses by what could materially change the decision. Use existing roles for planning/documentation review instead of growing a bot taxonomy.**
