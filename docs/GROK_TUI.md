# Grok TUI integration

OODA 0.3.3 uses Grok Build's supported command status-line hook to surface compact OODA control state inside the Grok terminal.

## What appears

The status line reads Grok session JSON plus local OODA artifacts and renders:

```text
tenniskal │ Grok 4.6 │ 12% ctx │ main
OODA ● Design the R7 preregistration │ GATE → Approve the R7 preregistration mission │ worker: idle
LAST PIVOT → R6 integrated
```

The third line appears only when the terminal is wide enough and a material timeline pivot exists.

Sources remain local/durable:

- Grok session JSON: model, context percentage, current directory, branch
- `.ooda/project-view.json`: current ladder rung and latest material pivot
- `PROJECT_STATE.md`: next gate fallback/current objective fallback
- latest work order / TRACE: worker/gate state

## Refresh behavior

No server and no port are required for the TUI status line.

Grok invokes the command whenever session state changes. OODA also configures a 600-second (`10 minute`) timed refresh so changes made outside the active turn eventually appear while the session is idle.

Override the timer before launching:

```bash
OODA_GROK_STATUSLINE_REFRESH_SECONDS=60 grok-safe
```

Disable OODA's status-line configuration:

```bash
OODA_GROK_STATUSLINE=0 grok-safe
```

## Installation / refresh

```bash
cd ~/repos/ooda
git checkout main
git pull --ff-only
bash install.sh
```

Then launch normally:

```bash
grok-safe
```

`grok-safe` safely replaces only the `[ui.status_line]` block in `~/.grok/config.toml`, preserves other Grok settings, and writes a timestamped backup when that block changes.

## Interaction boundary

Grok's supported status-line API allows custom command output (up to five lines), ANSI color, hyperlinks, and timed refreshes. It does not expose a custom hover/menu API. OODA therefore uses the supported live multi-line status surface rather than patching or scraping Grok's TUI.

The browser Control Room remains separate and uses its own local HTTP port.
