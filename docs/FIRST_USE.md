# First Use — Tomorrow's Workflow

## Install OODA locally

From the OODA repository:

```bash
./scripts/install-cli.sh
./scripts/install-grok.sh
```

Both installers create symlinks back to the OODA repository. They do not copy the whole repo into hidden runtime state.

If `~/.local/bin` is not on `PATH`, either add it once or call `~/repos/ooda/scripts/ooda` directly.

The Grok installer adds exactly one `/ooda` skill and does not touch existing lifecycle skills.

## Pilot 1 — Tenniskal

In the Tenniskal repository:

```bash
mkdir -p .ooda
cp ~/repos/ooda/examples/projects/tenniskal.json .ooda/project.json
ooda doctor
```

Then use the normal Lawrence + ChatGPT dialogue to decide the next real task.

ChatGPT should produce/finalize a work order. You can create the skeleton locally:

```bash
ooda work-order \
  --project-id tenniskal \
  --objective "<one bounded research objective>" \
  --role researcher \
  --profile quantitative-research \
  --lenses scientific,statistical,market-microstructure \
  --claim-level discovery \
  --output .ooda/work-orders/<task>.json
```

Edit the generated scope, verification, and stop conditions so they match the actual research stage.

Start Grok exactly as you do today:

```text
grok-safe
/start
/ooda .ooda/work-orders/<task>.json
```

Grok does one bounded task and uses the project's existing handoff convention.

Bring the handoff/PR/result back to ChatGPT for review.

After the outcome is known:

```bash
ooda trace \
  --work-order .ooda/work-orders/<task>.json \
  --result-state completed \
  --summary "<truthful one-line outcome>" \
  --output .ooda/traces/<task>.json
```

Fill the concise Observe/Orient/Decide/Act and verification fields before committing the trace if it contains durable value.

## Pilot 2 — Crypto-Innout

Adopt the same overlay:

```bash
mkdir -p .ooda
cp ~/repos/ooda/examples/projects/crypto-innout.json .ooda/project.json
ooda doctor
```

Do **not** use OODA adoption as permission to touch live runtime, protected data, or blocked research stages. Current Crypto-Innout project authority remains stronger than generic OODA defaults.

For runtime/reliability work, a typical route is:

```text
role: engineer
profile: reliability
lenses: reliability-systems, taleb, boyd
claim_level: n-a
```

For model/research work:

```text
role: researcher or validator
profile: quantitative-research / quant-markets
lenses: scientific, statistical, model-risk
claim_level: discovery/evidence/qualification as appropriate
```

## App / SaaS / Chrome-extension example

Do not start with infrastructure.

First work order:

```text
role: product-strategist
profile: browser-extension or saas
lenses: product-user, value-of-information, stanley-lehman
claim_level: discovery
objective: prove one useful user workflow with the thinnest vertical slice
```

Architecture work follows only after the product question is sufficiently clear:

```text
role: architect
profile: browser-extension/full-stack
lenses: product-user, security-abuse, reliability-systems
claim_level: n-a
```

Then Engineer implements the bounded vertical slice and Validator checks security/reliability before external release.

## What to measure during the first two pilots

Do not build analytics yet. Manually note:
- Was the work order helpful or ceremony?
- Did role/profile/lenses materially improve orientation?
- Did scope drift decrease?
- Were stop conditions useful?
- Did the agent preserve negative findings?
- Did we spend fewer turns rediscovering state?
- What information would we genuinely want Agent Ops Monitor to show?

Those observations determine OODA V1.1.
