# Project Adoption

Projects opt into OODA without reorganizing their existing documentation.

## Minimal project file

Create `.ooda/project.json` in the target project.

Recommended fields:

```json
{
  "schema": "ooda/project/v1",
  "project_id": "example",
  "project_class": "software-product",
  "authority": {"integration_owner": "human", "self_merge": false, "live_capital": false},
  "state_sources": ["AGENTS.md", "PROJECT_STATE.md"],
  "execution": {"current_provider": "grok", "existing_lifecycle": "preserve"},
  "monitor": {"enabled": false}
}
```

This is a routing contract, not a second giant PROJECT_STATE.

## Project classes

- `quantitative-research`
- `trading-research`
- `data-ml-system`
- `software-product`
- `analytical-product`
- `infrastructure`

Projects may use more specific tags without changing the core classes.

## Suggested pilots

### Tenniskal
Class: `quantitative-research`

Default orientation:
- researcher / quantitative-research;
- scientific + statistical + market-microstructure;
- Discovery until the stage explicitly advances.

### Crypto-Innout
Class: `trading-research`

Default orientation depends on task:
- researcher / quant-markets for research;
- engineer / reliability for runtime work;
- model-risk + reliability + taleb for consequential changes.

Live-capital authority remains false.

### IOND
Class: `analytical-product`

Default orientation:
- researcher / fundamental-valuation for model work;
- product-strategist / analytics-product for dashboard/product work;
- causal-mechanism + model-risk + product-user as needed.

### LDPS
Class: `quantitative-research`

Use as a methodology/reference source first. Do not make OODA adoption an LDPS-wide refactor.

## SaaS / app / Chrome extension

Class: `software-product`.

Typical routing:
1. product-strategist + product-user + value-of-information — establish the smallest useful workflow;
2. architect + full-stack/browser-extension + security-abuse — design a thin vertical slice;
3. engineer — implement;
4. validator + security-abuse + reliability-systems — review before release.

OODA should prevent both failure modes:
- shipping a technically polished product nobody needs;
- overengineering infrastructure before a vertical slice proves the workflow.
