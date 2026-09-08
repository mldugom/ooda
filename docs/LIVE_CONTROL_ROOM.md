# Live Control Room

`ooda dashboard` is a local read-only companion UI over durable OODA project state. It does not replace `ooda view`; the terminal renderer remains the compact canonical human view.

## What the Control Room shows

For every adopted repo with `.ooda/project.json`, the Control Room renders:

- current stakeholder summary;
- current human/next gate;
- a visual `OBSERVE -> ORIENT -> DECIDE -> ACT -> VERIFY` loop with the current phase emphasized;
- the full visible objective ladder (`completed`, exactly one `current`, downstream `provisional`);
- the latest material decision pivots (`TIME | DECISION | SO WHAT | BIGGER IDEA`);
- Git/controller/mission freshness metadata.

Multiple projects are shown as tabs rather than stacked full-height cockpits. The selected project is remembered across the 15-second auto-refresh when browser local storage is available.

The Control Room follows OODA's default editorial/FiveThirtyEight-inspired visual language: warm cream page, off-white surfaces, serif display headings, restrained blue emphasis, thin warm rules, and evidence-first tables. See [`STYLE_GUIDE.md`](STYLE_GUIDE.md).

The default browser refresh is 15 seconds. Override it with `OODA_DASHBOARD_REFRESH_SECONDS`.

The default local HTTP port is now **8792**. Override it with `OODA_DASHBOARD_PORT`. If the preferred port is occupied by a foreign service, OODA selects the next free local port rather than reusing the wrong UI.

## Grok terminal companion

OODA 0.3.3 also exposes current objective, next gate, worker state, context usage, and latest pivot through Grok Build's supported command status-line hook. That TUI surface needs **no port**; Grok runs it on session changes plus a 10-minute timed refresh. See [`GROK_TUI.md`](GROK_TUI.md).

## Session context telemetry

OODA does **not** scrape provider terminal chrome. When no structured context telemetry exists, the Control Room says `provider UI` and the provider's native context meter remains authoritative.

Provider adapters may optionally write:

```text
.ooda/session-telemetry.json
```

with this minimal contract:

```json
{
  "schema": "ooda/session-telemetry/v1",
  "provider": "grok",
  "context_used": 29000,
  "context_limit": 500000,
  "updated_at": "2026-09-08T01:30:00-04:00"
}
```

When present, the Control Room renders both the absolute context meter and percentage. This file is optional derived telemetry, not project authority.

OODA intentionally does not calculate or display session dollar cost in this release.

## Authority

The dashboard is derived observation state. `PROJECT_STATE.md`, work orders, traces, domain research artifacts, Git/tests, and explicit human gates remain authoritative. `.ooda/project-view.json` is durable human orientation, not permission to start downstream work.
