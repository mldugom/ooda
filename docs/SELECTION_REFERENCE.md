# OODA Selection Reference

This is the copy/paste reference for the main OODA descriptors used by `ooda init`, `ooda mission`, the Controller, workers, traces, and the Control Room.

## Selection rule

| Descriptor | Question it answers | Selection rule |
|---|---|---|
| **Project class** | What broad kind of repository/work is this? | Choose one stable class for the repo. Do not change it for every task. |
| **Role** | Who owns the next judgment/action? | Choose exactly one accountable role for a bounded mission. |
| **Profile** | What expertise should that role bring? | Choose the most relevant expertise label; projects may extend the vocabulary. |
| **Lenses** | What perspectives could materially change orientation? | Normally choose 0–3. Do not add lenses decoratively. |
| **Claim** | How strongly will we rely on the result? | Use `n-a` for ordinary implementation/product tasks; research claims use discovery/evidence/qualification. |

---

## Roles — exact V1 values

| Value | Owns / does | Use when the primary question is | Do not use as |
|---|---|---|---|
| `controller` | Routes, stops, escalates, proposes bounded missions, surfaces gates. | “What should happen next?” | Deep researcher/engineer/validator. |
| `researcher` | Discovers, investigates, tests hypotheses, gathers evidence. | “What may be true or worth testing?” | Final certifier of its own consequential claim. |
| `product-strategist` | Frames user problem, workflow, value proposition, MVP priority. | “What problem or product move is worth pursuing?” | Implementation owner. |
| `architect` | Designs system, experiment, interfaces, data/process boundaries. | “How should this be structured?” | Broad implementation worker by default. |
| `engineer` | Implements one bounded approved change. | “How do we build/fix this slice?” | Independent validator of its own work. |
| `validator` | Independently challenges correctness, evidence, security, model/research claims. | “How could this be wrong or fail?” | Primary builder of the thing it validates. |
| `portfolio-manager` | Allocation, correlation, concentration, portfolio construction. | “Where/how much scarce capital or risk should be allocated?” | Execution/microstructure specialist. |
| `trader` | Execution realism, liquidity, timing, fills, slippage. | “Can this edge actually be executed?” | Portfolio allocator. |
| `risk-manager` | Tails, ruin, exposure, model/operational downside. | “What can cause unacceptable loss/failure?” | General-purpose reviewer when no risk question exists. |

**Rule:** if two roles seem equally primary, the mission may be too broad. Split it unless the second role is only a review perspective.

---

## Claim levels — exact values

| Value | Meaning | Typical evidence burden | Example |
|---|---|---|---|
| `discovery` | Interesting enough to explore; not yet something to rely on. | Cheap falsification, sound exploratory method, clear limitations. | “This behavior may predict an outcome; test it.” |
| `evidence` | Stronger support that should survive meaningful validation. | Reproducibility, realistic assumptions/economics, uncertainty, stronger temporal/generalization checks. | “This signal survives held-out validation and realistic costs.” |
| `qualification` | Result may be relied upon for consequential use. | Frozen provenance/spec, strong independent/sealed/prospective validation, relevant stress/security/reliability/execution controls, explicit human promotion. | “This model is qualified for the approved production use.” |
| `n-a` | No empirical/research claim is being promoted. | Engineering/product verification appropriate to the task. | “Implement this navigation flow.” |

**Important:** a worker cannot self-promote `discovery` → `evidence` → `qualification` merely by assertion or green tests.

---

## Lenses — exact V1 values

A lens is an orientation aid, not a role or authority grant.

| Value | What it emphasizes | Good trigger/question |
|---|---|---|
| `boyd` | Orientation quality, feedback, adaptation speed, stale mental models. | “Is our current orientation already obsolete?” |
| `stanley-lehman` | Novelty, stepping stones, deceptive objectives, open-ended search. | “Are we over-optimizing an objective whose path is unknowable?” |
| `taleb` | Fragility, convexity, tails, optionality, ruin, via negativa. | “What happens if our assumptions are badly wrong?” |
| `scientific` | Falsifiability, evidence, reproducibility, alternative explanations. | “What observation would disconfirm this?” |
| `statistical` | Uncertainty, sample size, multiplicity, calibration, variance. | “Is this effect distinguishable from noise/selection?” |
| `model-risk` | Leakage, overfit, misuse, drift, selection, limitations. | “How could this model look good for the wrong reason?” |
| `value-of-information` | Cheapest experiment that can change the decision. | “What is the smallest useful test?” |
| `causal-mechanism` | Mechanism vs correlation/confounding. | “Why should X cause Y rather than merely co-move?” |
| `market-microstructure` | Quotes, spreads, liquidity, fills, latency, adverse selection. | “Does paper edge survive actual market mechanics?” |
| `portfolio` | Allocation, correlation, concentration, capacity. | “How does this interact with the rest of the book?” |
| `reliability-systems` | Restarts, stale state, partial failure, idempotency, observability. | “What happens when this process fails halfway?” |
| `product-user` | User problem, workflow, adoption, usefulness, MVP. | “Does this solve a real user workflow?” |
| `security-abuse` | Permissions, privacy, secrets, attack/abuse surfaces. | “How could this be exploited or expose data?” |

### Useful lens pattern

Normally:

1. one **epistemic** lens: `scientific`, `statistical`, `model-risk`, or `causal-mechanism`;
2. one **domain/implementation** lens: `market-microstructure`, `portfolio`, `product-user`, `security-abuse`, or `reliability-systems`;
3. optionally one **challenge/opportunity** lens: `taleb`, `stanley-lehman`, `value-of-information`, or `boyd`.

OODA/Boyd is already the operating backbone. You do **not** need the `boyd` lens on every mission.

---

## Project classes — exact values

Project class is repo-level routing metadata. Keep it broad and stable.

| Value | Use for | Examples |
|---|---|---|
| `quantitative-research` | Research repos centered on empirical/statistical hypotheses and evidence. | Sports factors, demand forecasting research, experimental signal research. |
| `trading-research` | Research tied directly to market execution, trading systems, or trading-specific constraints. | Market strategy research with fills/costs/liquidity constraints. |
| `data-ml-system` | Data/ML pipelines, model-serving systems, ML infrastructure/products where the system is central. | Feature/model pipelines, evaluation systems, ML services. |
| `software-product` | Apps, SaaS, extensions, APIs, user-facing software products. | Browser extensions, mobile apps, SaaS applications. |
| `analytical-product` | Decision-support/valuation/analytics products combining analysis with a user-facing output. | Valuation dashboards, scenario-analysis tools. |
| `infrastructure` | Runtime, deployment, observability, orchestration, platform/control-plane infrastructure. | Agent supervisor, collectors, deployment tooling. |

---

## Profiles — V1 families

Profiles are expertise labels. Unlike roles/claims/lenses/project classes, projects may extend this vocabulary.

| Family | Common values | Use for |
|---|---|---|
| ML / data | `quantitative-research`, `statistics`, `data-science`, `ml-research`, `ml-engineering`, `data-engineering` | Statistical/data/model work. |
| AI | `llm-engineering`, `agent-systems`, `evaluation`, `retrieval` | LLM, agents, RAG, eval systems. |
| Software / product | `backend`, `frontend`, `full-stack`, `api`, `browser-extension`, `saas`, `analytics-product`, `automation` | Product/application engineering and design. |
| Finance | `quant-markets`, `fundamental-valuation`, `portfolio-construction`, `market-microstructure`, `risk` | Markets/valuation/portfolio work. |
| Operations | `reliability`, `deployment`, `observability` | Runtime and operational systems. |

For platform-specific expertise not yet in the central list, use a clear project-local profile such as `ios-swiftui`, rather than inventing a new role.

---

## Result states — exact trace values

| Value | Meaning |
|---|---|
| `completed` | The bounded mission was completed; review/next gate still applies. |
| `negative_finding` | The mission produced a useful negative result worth preserving. |
| `blocked` | A concrete external/state/authority dependency prevents completion. |
| `budget_exhausted` | The bounded turn/investigation budget was reached before completion. |
| `needs_human_gate` | A human/ChatGPT/integration decision is required before continuing. |

---

## Controller outcomes

| Outcome | Meaning |
|---|---|
| `KEEP THINKING` | Stay conversational; the idea has not earned worker resources yet. |
| `PROPOSE MISSION` | One bounded worker mission is justified. |
| `HUMAN GATE` | A decision/authority/review is required before more work. |
| `NO ACTION` | Current accrual/work should continue; do not create busywork. |

---

## Fast examples

| Situation | Project class | Role / profile | Lenses | Claim |
|---|---|---|---|---|
| Explore a mobile app feature | `software-product` | `product-strategist / ios-swiftui` | `product-user`, `value-of-information` | `discovery` |
| Design mobile architecture | `software-product` | `architect / ios-swiftui` | `product-user`, `security-abuse`, `reliability-systems` | `n-a` |
| Implement bounded app feature | `software-product` | `engineer / ios-swiftui` | `product-user`, `reliability-systems` | `n-a` |
| Independent app review | `software-product` | `validator / ios-swiftui` | `security-abuse`, `reliability-systems`, `product-user` | `n-a` |
| Quant hypothesis spike | `quantitative-research` | `researcher / quantitative-research` | `scientific`, `statistical`, `value-of-information` | `discovery` |
| Model validation | `quantitative-research` | `validator / statistics` | `model-risk`, `statistical`, `scientific` | `evidence` or `qualification` depending on intended reliance |
| Runtime repair | `infrastructure` or project’s existing class | `engineer / reliability` | `reliability-systems`, `taleb` | `n-a` |
