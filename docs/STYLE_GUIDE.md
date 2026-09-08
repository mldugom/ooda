# OODA Visual Style

Status: default visual language for OODA-owned browser dashboards, project cockpits, reports, charts, and lightweight analytical surfaces.

## Direction

Use the established OODA / FiveThirtyEight-inspired editorial data-journalism style as the default visual language unless a project has a material reason to diverge.

The goal is not brand imitation. The goal is a consistent analytical presentation style: warm paper/cream backgrounds, high-contrast black typography, restrained accent colors, thin rules, compact labels, editorial hierarchy, and charts/tables that prioritize evidence over decoration.

## Default palette

```text
page/background   warm cream   #f4eedc
surface/paper     off-white     #fffdf7
ink               near-black    #24211d
muted text        warm gray     #756d62
rules/borders     tan-gray      #d7ccb7
accent            data blue     #4c78a8
accent light      pale blue     #e9f0f7
warning/gate      warm sand     #f4ebd6
negative/block    pale red      #f5e5e0
secondary fill    warm cream    #f8f3e8
```

Use other colors only when they encode real semantic distinctions. Do not introduce decorative gradients, neon colors, glassmorphism, or dark-mode-first styling into OODA-owned analytical surfaces without a project-specific reason.

## Typography

- Editorial/display headings: Georgia or a similar readable serif.
- UI, labels, tables, annotations, controls: system sans-serif (`-apple-system`, BlinkMacSystemFont, `Segoe UI`, Arial).
- Small uppercase/letter-spaced labels are appropriate for section eyebrows and table headers.
- Prefer compact but readable type over oversized dashboard typography.

## Layout

- Warm cream page background with off-white cards/panels.
- Thin borders and restrained shadows.
- Generous whitespace around major sections, compact spacing inside analytical tables.
- Keep decision-critical content visible rather than hiding it behind accordions.
- Prefer one coherent editorial page with clear sections to a dense app-shell aesthetic.
- When the Control Room contains multiple projects, switch projects with tabs rather than stacking full project cockpits vertically.

## Charts and tables

- Use direct labels, explanatory titles, and annotations that answer the decision question.
- Avoid chart junk and ornamental legends when inline labels are clearer.
- Use exact tables when precision matters; charts when shape, trend, distribution, calibration, or relationship matters.
- Keep axes, rules, gridlines, and secondary marks visually quiet.
- Highlight one focal series/decision with the accent color; de-emphasize comparison/background series.
- Preserve uncertainty, missingness, and point-in-time semantics visibly when they matter to the claim.

## OODA-specific semantics

- Current human gate should be visually prominent but not alarming unless blocked.
- Objective ladder:
  - completed: normal ink with completion marker;
  - current: blue accent emphasis;
  - provisional: muted.
- OODA loop should use restrained cream cards and a blue accent for the current phase.
- Timeline should read like an editorial evidence table, not a chat/activity feed.
- Context telemetry is optional secondary metadata, never the focal point.

## Scope

This is the default for OODA-owned UI and for project-owned analytical surfaces created under OODA when no stronger project-specific design language exists. Existing project visual systems do not need to be rewritten merely for conformity.

When new OODA UI is added, preserve this style unless the human explicitly asks for another visual direction.
