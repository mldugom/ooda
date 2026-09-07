# Project Adoption

Projects opt into OODA without reorganizing their existing documentation.

## Install once

Pip from GitHub:

```bash
python3 -m pip install "git+https://github.com/mldugom/ooda.git"
ooda setup
```

Or from a clone:

```bash
git clone https://github.com/mldugom/ooda.git
cd ooda
bash install.sh
```

Normal use then happens through `ooda`, `grok-safe`, `/ooda-controller`, and `/ooda`.

## Existing repository — thin overlay only

```bash
cd ~/repos/example-project
ooda init --project-id example-project --project-class software-product
ooda doctor
```

Recommended project contract shape:

```json
{
  "schema": "ooda/project/v1",
  "project_id": "example-project",
  "project_class": "software-product",
  "authority": {"integration_owner": "human", "self_merge": false, "live_capital": false},
  "state_sources": ["AGENTS.md", "PROJECT_STATE.md", "README.md"],
  "execution": {"current_provider": "grok", "existing_lifecycle": "preserve"},
  "monitor": {"enabled": false}
}
```

This is a routing contract, not a second giant project-state document.

If the repo already has useful architecture/domain/process documentation, do not scaffold replacements. Add only `.ooda/` and preserve the repo's existing durable truth.

## New repository — minimal scaffold

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

Existing docs are never silently overwritten by `--scaffold`. `--force` replaces only `.ooda/project.json`.

Do **not** scaffold empty `ARCHITECTURE.md`, `DOMAIN.md`, `PROCESS.md`, or similar files just because the project uses OODA. Those documents are earned when real work materially changes a durable mental model.

## Everyday mission flow

```bash
ooda mission \
  "<one bounded objective>" \
  --role <role> \
  --profile <profile> \
  --claim <discovery|evidence|qualification|n-a> \
  [--lenses lens1,lens2,lens3] \
  [--id TASK-01]
```

Mission output defaults to `.ooda/work-orders/<id>.json`.

After execution:

```bash
ooda trace \
  --work-order .ooda/work-orders/<id>.json \
  --result <completed|negative_finding|blocked|budget_exhausted|needs_human_gate> \
  --summary "<truthful concise result>"
```

Trace output defaults to `.ooda/traces/<work-order-id>.json`.

Use `ooda doctor` for project health and `ooda doctor <json-file>` for individual contract validation.

## Project classes

| Class | Use for |
|---|---|
| `quantitative-research` | Statistical/empirical research repos. |
| `trading-research` | Market research with trading/execution constraints. |
| `data-ml-system` | ML/data pipelines, evaluation, serving, and model systems. |
| `software-product` | Apps, SaaS, extensions, APIs, user-facing software. |
| `analytical-product` | Decision-support, valuation, scenario, analytics products. |
| `infrastructure` | Runtime, deployment, observability, orchestration/control-plane work. |

See `docs/SELECTION_REFERENCE.md` for routing values and examples.

## Typical software-product routing

1. `product-strategist` + `product-user` + `value-of-information` — establish the smallest useful workflow;
2. `architect` + relevant software profile + `security-abuse`/`reliability-systems` — design a thin vertical slice;
3. `engineer` — implement the bounded slice;
4. `validator` — independently review security/reliability/correctness when warranted.

## Typical research routing

1. `researcher` + appropriate research profile + `scientific`/`statistical` — discovery;
2. preserve negative findings and selection history;
3. use `validator` for independent evidence/qualification review;
4. do not infer production authority from research success.

## Context bootstrap

A fresh ChatGPT conversation should normally need only repository + immediate intent. See `docs/CONTEXT_BOOTSTRAP.md` and `docs/CHATGPT_USAGE.md`.

Do not solve session continuity by growing project docs indefinitely. Persist only durable conclusions and current truth.
