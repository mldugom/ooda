# Routing vocabulary — optional

Roles, profiles, and lenses showed no measurable gain on ordinary data-science
work in the vnext ablation, where a generic worker with none of them scored
joint-top. They are aids, never mandatory. Before attaching one, ask:

> Will this descriptor materially change worker behavior?

If no, omit it and state the scientific constraints directly instead.

Default lens count is **0–1**. Two or more require a concrete stated reason.
Three is the hard cap.

## Roles — accountability, when useful

`controller` `researcher` `product-strategist` `architect` `engineer` `validator`
`portfolio-manager` `trader` `risk-manager`

## Profiles — expertise, when useful

Quant/ML: `quantitative-research` `statistics` `data-science` `ml-research`
`ml-engineering` `data-engineering`. AI: `llm-engineering` `agent-systems`
`evaluation` `retrieval`. Software: `backend` `frontend` `full-stack` `api`
`saas` `analytics-product` `automation`. Finance: `quant-markets`
`fundamental-valuation` `portfolio-construction` `market-microstructure` `risk`.
Ops: `reliability` `deployment` `observability`.

## Lenses — where they do earn their place

These are specialist perspectives a generic worker genuinely may not bring:

| Lens | Question |
|---|---|
| `market-microstructure` | Is this executable at real prices and timing? |
| `security-abuse` | What permissions, secrets, attack paths, privacy risks? |
| `reliability-systems` | Restart, duplication, stale state, partial failure? |
| `portfolio` | Correlation, concentration, capacity, opportunity cost? |
| `taleb` | Fragility, ruin, nonlinear downside, removable complexity? |
| `causal-mechanism` | Association or mechanism? What confounds it? |
| `value-of-information` | What cheapest experiment could change the decision? |
| `stanley-lehman` | Is the objective deceptive? What stepping stone is ignored? |

`scientific`, `statistical`, and `model-risk` are largely covered by
`reference/predictive-science.md` for quantitative missions — prefer loading that
over attaching the lens names.

Required combinations still hold where consequence is real: real-money trading
needs microstructure plus portfolio plus risk review before live use; externally
deployed software needs `security-abuse` before release.
