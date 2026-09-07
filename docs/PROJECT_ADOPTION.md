# Project Adoption

Projects opt into OODA without reorganizing their existing documentation.

## Existing repository — thin overlay only

Create `.ooda/project.json` in the target project:

```bash
ooda init --project-id <id> --project-class <class>
ooda doctor
```

Recommended project contract:

```json
{
  "schema": "ooda/project/v1",
  "project_id": "example",
  "project_class": "software-product",
  "authority": {"integration_owner": "human", "self_merge": false, "live_capital": false},
  "state_sources": ["AGENTS.md", "PROJECT_STATE.md", "README.md"],
  "execution": {"current_provider": "grok", "existing_lifecycle": "preserve"},
  "monitor": {"enabled": false}
}
```

This is a routing contract, not a second giant PROJECT_STATE.

## New repository — minimal OODA-ready scaffold

For a new repo, initialize Git normally and ask OODA to create only the small durable operating spine:

```bash
mkdir my-project && cd my-project
git init
ooda init \
  --project-id my-project \
  --project-class software-product \
  --scaffold
ooda doctor
```

`--scaffold` creates, only when missing:

```text
README.md
AGENTS.md
PROJECT_STATE.md
.ooda/
  project.json
  README.md
  work-orders/
  traces/
```

The generated Markdown files are intentionally short:

- `README.md` — purpose and entrypoint;
- `AGENTS.md` — standing operating/safety rules plus project-specific invariants;
- `PROJECT_STATE.md` — current objective, current truth, blockers, next gate;
- `.ooda/README.md` — explains that OODA is a thin overlay, not a second PM system.

Existing docs are never silently overwritten by `--scaffold`. `--force` replaces only `.ooda/project.json`.

After bootstrap, replace placeholders with the project's actual purpose/invariants/current truth before substantial execution.

## Project classes

- `quantitative-research`
- `trading-research`
- `data-ml-system`
- `software-product`
- `analytical-product`
- `infrastructure`

Projects may use more specific profiles/tags without changing the core classes.

## Context bootstrap

A fresh ChatGPT conversation should normally need only repository + immediate intent. See `docs/CONTEXT_BOOTSTRAP.md` and `docs/CHATGPT_USAGE.md`.

Do not solve session continuity by growing project docs indefinitely. Persist only durable conclusions and current truth.

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
- model-risk + reliability-systems + taleb for consequential changes.

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
