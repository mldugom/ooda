from __future__ import annotations

import datetime as dt
import html
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .dashboard import discover_projects


def _e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""))


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _session_context(repo: Path) -> Optional[Dict[str, Any]]:
    """Read optional provider/session telemetry written by provider adapters."""
    data = _read_json(repo / ".ooda" / "session-telemetry.json")
    if data.get("schema") != "ooda/session-telemetry/v1":
        return None

    used = data.get("context_used")
    limit = data.get("context_limit")
    pct = data.get("context_percent")
    if not isinstance(pct, (int, float)) and isinstance(used, (int, float)) and isinstance(limit, (int, float)) and limit > 0:
        pct = max(0.0, min(100.0, float(used) / float(limit) * 100.0))

    return {
        "used": int(used) if isinstance(used, (int, float)) else None,
        "limit": int(limit) if isinstance(limit, (int, float)) and limit > 0 else None,
        "pct": float(pct) if isinstance(pct, (int, float)) else None,
        "provider": str(data.get("provider") or "provider"),
        "model": str(data.get("model") or data.get("model_id") or ""),
        "effort": str(data.get("effort") or ""),
        "session_cost": float(data["session_cost_usd"]) if isinstance(data.get("session_cost_usd"), (int, float)) else None,
        "session_cost_kind": str(data.get("session_cost_kind") or ""),
        "balance": float(data["account_balance"]) if isinstance(data.get("account_balance"), (int, float)) else None,
        "currency": str(data.get("account_currency") or "USD"),
        "updated_at": str(data.get("updated_at") or ""),
    }


def _human_number(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return str(value)


def _stage_key(project: Dict[str, Any]) -> str:
    stage = str(project.get("stage") or "orient").lower()
    if stage == "review":
        return "verify"
    if stage in {"observe", "orient", "act"}:
        return stage
    return "orient"


def _context_html(project: Dict[str, Any]) -> str:
    repo = project.get("repo")
    telemetry = _session_context(repo) if isinstance(repo, Path) else None
    if telemetry:
        top = "SESSION · " + telemetry["provider"].upper()
        if telemetry["model"]:
            top += " · " + telemetry["model"]
        pct = telemetry["pct"]
        pct_label = f"{pct:.1f}%" if isinstance(pct, float) else "context n/a"
        bar_width = f"{pct:.2f}%" if isinstance(pct, float) else "0%"
        if telemetry["used"] is not None and telemetry["limit"] is not None:
            context_detail = f"{_human_number(telemetry['used'])} / {_human_number(telemetry['limit'])}"
        else:
            context_detail = "provider did not expose exact context occupancy"
        economics: List[str] = []
        if telemetry["session_cost"] is not None:
            prefix = "~$" if telemetry["session_cost_kind"] == "tui-estimate" else "$"
            economics.append(f"{prefix}{telemetry['session_cost']:.3f} session")
        if telemetry["balance"] is not None:
            economics.append(f"{telemetry['currency']} {telemetry['balance']:.2f} balance")
        econ = " · ".join(economics) or "cost/balance unavailable"
        return f"""
        <div class="context-card">
          <div class="context-top">
            <span>{_e(top)}</span>
            <b>{_e(pct_label)}</b>
          </div>
          <div class="context-bar"><i style="width:{_e(bar_width)}"></i></div>
          <div class="context-foot"><span>{_e(context_detail)}</span><span>{_e(econ)}</span></div>
        </div>
        """
    return """
      <div class="context-card context-unavailable">
        <div class="context-top"><span>SESSION TELEMETRY</span><b>unavailable</b></div>
        <div class="context-bar"><i style="width:0%"></i></div>
        <div class="context-foot"><span>Provider adapter has not written telemetry yet.</span><span>No value inferred.</span></div>
      </div>
    """


def _ooda_rail_html(project: Dict[str, Any]) -> str:
    current = _stage_key(project)
    phases = [("observe", "OBSERVE"), ("orient", "ORIENT"), ("decide", "DECIDE"), ("act", "ACT"), ("verify", "VERIFY")]
    bits: List[str] = []
    for idx, (key, label) in enumerate(phases):
        cls = "rail-step current" if key == current else "rail-step"
        bits.append(f'<span class="{cls}">{label}</span>')
        if idx < len(phases) - 1:
            bits.append('<span class="rail-arrow">→</span>')
    return '<div class="ooda-rail">' + "".join(bits) + "</div>"


def _current_and_next(project: Dict[str, Any]) -> tuple[str, str]:
    ladder = [x for x in (project.get("objective_ladder") or []) if isinstance(x, dict)]
    current = str(project.get("objective") or "No current objective recorded")
    next_if = "Re-orient after the current gate; no downstream rung is committed."
    current_idx = -1
    for idx, item in enumerate(ladder):
        if item.get("status") == "current":
            current = str(item.get("label") or current)
            current_idx = idx
            break
    if current_idx >= 0:
        for item in ladder[current_idx + 1 :]:
            if item.get("status") == "provisional" and item.get("label"):
                next_if = str(item["label"])
                break
    return current, next_if


def _attention_html(project: Dict[str, Any]) -> str:
    current, next_if = _current_and_next(project)
    gate = str(project.get("next_gate") or "No human/next gate recorded")
    controller = str(project.get("controller") or "")
    blockers = str(project.get("blockers") or "")
    if controller == "active" and blockers and blockers.lower() not in {"none recorded", "none"}:
        waiting = blockers
    else:
        waiting = gate
    return f"""
    <div class="attention-strip">
      <div><small>NOW</small><b>{_e(current)}</b></div>
      <div><small>WAITING ON / GATE</small><b>{_e(waiting)}</b></div>
      <div><small>NEXT IF CURRENT GATE PASSES</small><b>{_e(next_if)}</b></div>
    </div>
    """


def _ladder_html(project: Dict[str, Any]) -> str:
    ladder = project.get("objective_ladder") or []
    if not ladder:
        return '<div class="empty-state">No durable objective ladder yet. Run <code>ooda view</code> after Controller orientation.</div>'
    bits: List[str] = []
    for item in ladder:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "provisional")
        marker = {"completed": "✓", "current": "●", "provisional": "○"}.get(status, "○")
        current = '<span class="current-tag">CURRENT</span>' if status == "current" else ""
        bits.append(
            f'<div class="ladder-row {status}"><div class="marker">{marker}</div>'
            f'<div><b>{_e(item.get("label") or "")}</b>{current}</div></div>'
        )
    return "".join(bits)


def _timeline_html(project: Dict[str, Any]) -> str:
    timeline = [x for x in (project.get("timeline") or []) if isinstance(x, dict)]
    if not timeline:
        return '<div class="empty-state">No material decision timeline yet.</div>'
    latest = timeline[-6:]
    rows = [
        '<div class="timeline-row timeline-head"><b>TIME</b><b>DECISION</b><b>IMMEDIATE CONSEQUENCE</b><b>PROGRAM IMPACT</b></div>'
    ]
    for item in latest:
        rows.append(
            '<div class="timeline-row">'
            f'<span>{_e(item.get("at") or "")}</span>'
            f'<span>{_e(item.get("decision") or "")}</span>'
            f'<span>{_e(item.get("so_what") or "")}</span>'
            f'<span>{_e(item.get("bigger_idea") or "")}</span>'
            "</div>"
        )
    if len(timeline) > len(latest):
        rows.append(
            f'<div class="timeline-more">Showing latest {len(latest)} of {len(timeline)} material decisions · '
            '<code>ooda view --all</code> for full history</div>'
        )
    return "".join(rows)


def _parse_time(value: Any) -> Optional[dt.datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def _mission_points(repo: Path) -> List[Dict[str, Any]]:
    work_orders: Dict[str, Dict[str, Any]] = {}
    for path in sorted((repo / ".ooda" / "work-orders").glob("*.json")):
        data = _read_json(path)
        if data.get("id"):
            work_orders[str(data["id"])] = data

    points: List[Dict[str, Any]] = []
    for path in sorted((repo / ".ooda" / "traces").glob("*.json")):
        trace = _read_json(path)
        work_id = str(trace.get("work_order_id") or "")
        work = work_orders.get(work_id, {})
        started = _parse_time(work.get("created_at"))
        completed = _parse_time(trace.get("completed_at"))
        economics = trace.get("economics") if isinstance(trace.get("economics"), dict) else {}
        cost = economics.get("cost_usd")
        result = trace.get("result") if isinstance(trace.get("result"), dict) else {}
        if started is None or completed is None or not isinstance(cost, (int, float)) or completed <= started:
            continue
        points.append(
            {
                "id": work_id or path.stem,
                "minutes": (completed - started).total_seconds() / 60.0,
                "cost": max(0.0, float(cost)),
                "state": str(result.get("state") or "completed"),
                "provider": str(trace.get("provider") or "provider"),
            }
        )
    return points[-24:]


def _efficiency_chart(project: Dict[str, Any]) -> str:
    repo = project.get("repo")
    if not isinstance(repo, Path):
        return '<div class="chart-empty">No repository path available.</div>'
    points = _mission_points(repo)
    if not points:
        return (
            '<div class="chart-empty"><b>No exact mission economics yet.</b><span>'
            'The chart starts when work orders carry <code>created_at</code> and traces carry '
            '<code>completed_at</code> + exact/recorded <code>cost_usd</code>. OODA does not infer these from file mtimes.'</span></div>'
        )

    width, height = 560, 220
    left, right, top, bottom = 52, 18, 16, 38
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_cost = max(max(p["cost"] for p in points), 0.01)
    max_min = max(max(p["minutes"] for p in points), 1.0)
    dots: List[str] = []
    for p in points:
        x = left + (p["cost"] / max_cost) * plot_w
        y = top + plot_h - (p["minutes"] / max_min) * plot_h
        state = "".join(ch if ch.isalnum() else "-" for ch in p["state"].lower()).strip("-")
        title = f"{p['id']} · {p['provider']} · ${p['cost']:.3f} · {p['minutes']:.0f} min · {p['state']}"
        dots.append(f'<circle class="dot dot-{_e(state)}" cx="{x:.1f}" cy="{y:.1f}" r="5"><title>{_e(title)}</title></circle>')

    return f"""
    <svg class="efficiency-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Feedback-loop efficiency: mission cost versus minutes to trace or gate">
      <line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" />
      <line class="axis" x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" />
      <text class="axis-label" x="{left}" y="{height - 8}">$0</text>
      <text class="axis-label" text-anchor="end" x="{left + plot_w}" y="{height - 8}">${max_cost:.2f}</text>
      <text class="axis-label" x="8" y="{top + 4}">{max_min:.0f}m</text>
      <text class="axis-label" x="8" y="{top + plot_h}">0m</text>
      {''.join(dots)}
    </svg>
    <div class="chart-caption">Lower-left is better: cheaper mission, faster verified feedback. Points require explicit timestamps and recorded cost.</div>
    """


def _sidebar_meta(project: Dict[str, Any]) -> str:
    repo = project.get("repo")
    telemetry = _session_context(repo) if isinstance(repo, Path) else None
    if not telemetry:
        return f"{_e(project.get('stage') or 'orient')} · telemetry n/a"
    bits = [telemetry["provider"]]
    if telemetry["model"]:
        bits.append(telemetry["model"])
    if telemetry["pct"] is not None:
        bits.append(f"{telemetry['pct']:.0f}% ctx")
    if telemetry["session_cost"] is not None:
        prefix = "~$" if telemetry["session_cost_kind"] == "tui-estimate" else "$"
        bits.append(f"{prefix}{telemetry['session_cost']:.2f}")
    if telemetry["balance"] is not None:
        bits.append(f"bal {telemetry['balance']:.2f}")
    return " · ".join(_e(x) for x in bits)


def _project_card(project: Dict[str, Any]) -> str:
    summary = project.get("stakeholder_summary") or "No stakeholder summary recorded yet."
    return f"""
    <section class="project-card">
      <div class="project-title">
        <div>
          <div class="eyebrow">PROJECT CONTROL</div>
          <h2>{_e(project.get('project_id'))}</h2>
          <p>{_e(project.get('objective'))}</p>
        </div>
        <div class="state-badges">
          <span class="badge">{_e(project.get('stage'))}</span>
          <span class="badge">{_e(project.get('claim'))}</span>
        </div>
      </div>

      <div class="gate-band">
        <small>CURRENT HUMAN GATE / NEXT GATE</small>
        <b>{_e(project.get('next_gate'))}</b>
      </div>

      <div class="summary-context">
        <div class="stakeholder">
          <small>CURRENT STAKEHOLDER SUMMARY</small>
          <b>{_e(summary)}</b>
        </div>
        {_context_html(project)}
      </div>

      {_ooda_rail_html(project)}
      {_attention_html(project)}

      <div class="cockpit-grid">
        <div class="left-stack">
          <div class="pane">
            <div class="pane-head"><b>OBJECTIVE LADDER</b><span>directional, not contractual</span></div>
            <div class="ladder">{_ladder_html(project)}</div>
          </div>
          <div class="pane efficiency-pane">
            <div class="pane-head"><b>FEEDBACK-LOOP EFFICIENCY</b><span>cost × time to verified feedback</span></div>
            {_efficiency_chart(project)}
          </div>
        </div>
        <div class="pane timeline-pane">
          <div class="pane-head"><b>MATERIAL DECISION TIMELINE</b><span>{len(project.get('timeline') or [])} pivots</span></div>
          <div class="timeline">{_timeline_html(project)}</div>
        </div>
      </div>

      <div class="meta-strip">
        <span><b>Git</b> {_e(project.get('branch'))} @ {_e(project.get('head'))} · dirty {_e(project.get('dirty'))}</span>
        <span><b>Controller</b> {_e(project.get('controller'))}</span>
        <span><b>Mission</b> {_e(project.get('work_order'))}</span>
        <span><b>Updated</b> {_e(project.get('updated'))}</span>
      </div>
    </section>
    """


def render_html(projects: List[Dict[str, Any]], refresh_seconds: int, root: Path) -> str:
    active = sum(p.get("controller") == "active" for p in projects)
    review = sum(p.get("stage") == "review" for p in projects)
    blocked = sum(p.get("controller") == "blocked" for p in projects)
    auto = f'<meta http-equiv="refresh" content="{refresh_seconds}">' if refresh_seconds > 0 else ""

    nav: List[str] = []
    panels: List[str] = []
    for idx, project in enumerate(projects):
        name = str(project.get("project_id") or f"project-{idx + 1}")
        active_cls = " active" if idx == 0 else ""
        nav.append(
            f'<button class="project-nav{active_cls}" data-project-tab="{idx}" '
            f'data-project-name="{_e(name)}" role="tab" aria-selected="{"true" if idx == 0 else "false"}" '
            f'onclick="showProject({idx}, this.dataset.projectName)">'
            f'<span class="project-nav-top"><b>{_e(name)}</b><i>{_e(project.get("stage") or "orient")}</i></span>'
            f'<small>{_sidebar_meta(project)}</small></button>'
        )
        panels.append(
            f'<div class="project-panel{active_cls}" data-project-panel="{idx}" role="tabpanel">'
            f'{_project_card(project)}</div>'
        )

    if projects:
        project_area = (
            '<div class="control-layout"><aside class="project-sidebar" role="tablist" aria-label="Projects">'
            '<div class="sidebar-head"><span>PROJECTS</span><small>provider · context · cost</small></div>'
            + "".join(nav)
            + '</aside><div class="project-panels">'
            + "".join(panels)
            + "</div></div>"
        )
    else:
        project_area = '<div class="empty-room">No OODA-adopted projects found under this projects root.</div>'

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{auto}
<title>OODA Control Room</title>
<style>
:root{{--bg:#f4eedc;--paper:#fffdf7;--paper2:#f8f3e8;--ink:#24211d;--muted:#756d62;--rule:#d7ccb7;--accent:#4c78a8;--accent-soft:#e9f0f7;--gate:#f4ebd6;--danger:#f5e5e0;--shadow:0 8px 24px rgba(64,49,28,.08)}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}
main{{max-width:1580px;margin:auto;padding:24px 26px 40px}}
h1,h2,p{{margin:0}}h1,h2{{font-family:Georgia,"Times New Roman",serif;font-weight:700}}h1{{font-size:34px;letter-spacing:-.02em}}h2{{font-size:27px}}
small{{color:var(--muted);font-size:11px}}code{{background:#eee6d7;border:1px solid var(--rule);padding:1px 5px;border-radius:4px}}
.hero{{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:12px}}.hero p{{color:var(--muted);margin-top:5px}}.eyebrow{{font-size:10px;font-weight:800;letter-spacing:.15em;color:var(--muted)}}
button{{font:inherit}}.hero button{{background:var(--paper);color:var(--ink);border:1px solid var(--rule);border-radius:6px;padding:8px 11px;font-weight:700;cursor:pointer;box-shadow:0 1px 0 rgba(0,0,0,.03)}}.hero>div:last-child{{display:grid;justify-items:end;gap:3px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px}}.kpi{{background:var(--paper);border:1px solid var(--rule);border-radius:7px;padding:8px 11px}}.kpi b{{display:block;font:700 19px/1.1 Georgia,"Times New Roman",serif;margin-top:1px}}
.control-layout{{display:grid;grid-template-columns:245px minmax(0,1fr);gap:12px;align-items:start}}.project-sidebar{{background:var(--paper);border:1px solid var(--rule);border-radius:9px;overflow:hidden;position:sticky;top:12px;box-shadow:0 3px 12px rgba(64,49,28,.05)}}.sidebar-head{{padding:10px 12px;background:var(--paper2);border-bottom:1px solid var(--rule)}}.sidebar-head span,.sidebar-head small{{display:block}}.sidebar-head span{{font-size:10px;font-weight:900;letter-spacing:.14em}}.project-nav{{width:100%;appearance:none;background:transparent;color:var(--ink);border:0;border-bottom:1px solid #ebe2d2;padding:10px 12px;text-align:left;cursor:pointer}}.project-nav:last-child{{border-bottom:0}}.project-nav:hover{{background:#fbf7ed}}.project-nav.active{{background:var(--accent-soft);box-shadow:inset 3px 0 0 var(--accent)}}.project-nav-top{{display:flex;align-items:center;justify-content:space-between;gap:8px}}.project-nav-top b{{font-size:13px}}.project-nav-top i{{font-size:9px;font-style:normal;text-transform:uppercase;color:var(--muted);letter-spacing:.05em}}.project-nav small{{display:block;margin-top:3px;line-height:1.35}}
.project-panel{{display:none}}.project-panel.active{{display:block}}.project-card{{background:var(--paper);border:1px solid var(--rule);border-radius:10px;padding:17px;box-shadow:var(--shadow)}}.project-title{{display:flex;justify-content:space-between;gap:20px}}.project-title p{{color:var(--muted);margin-top:4px;max-width:1000px}}
.state-badges{{white-space:nowrap}}.badge{{display:inline-block;border:1px solid var(--rule);background:var(--paper2);border-radius:999px;padding:3px 8px;margin-left:5px;text-transform:uppercase;font-size:9px;font-weight:800;letter-spacing:.04em}}
.gate-band{{margin-top:12px;border-left:4px solid #b7904b;background:var(--gate);padding:9px 11px}}.gate-band small,.gate-band b{{display:block}}.gate-band b{{margin-top:2px;font-size:14px}}
.summary-context{{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(300px,.8fr);gap:9px;margin:9px 0 10px}}.stakeholder,.context-card{{background:var(--paper2);border:1px solid var(--rule);border-radius:7px;padding:10px 11px}}.stakeholder small,.stakeholder b{{display:block}}.stakeholder b{{margin-top:3px}}
.context-top,.context-foot{{display:flex;justify-content:space-between;gap:12px}}.context-top{{font-size:11px;font-weight:800;letter-spacing:.04em}}.context-foot{{font-size:10px;color:var(--muted);margin-top:5px}}.context-bar{{height:6px;background:#e7decd;border:1px solid var(--rule);border-radius:99px;overflow:hidden;margin-top:7px}}.context-bar i{{display:block;height:100%;background:var(--accent)}}.context-unavailable .context-bar i{{background:#c9beaa}}
.ooda-rail{{display:flex;align-items:center;gap:8px;padding:6px 2px;color:var(--muted);font-size:9px;font-weight:900;letter-spacing:.08em}}.rail-step{{padding:2px 5px;border-radius:99px}}.rail-step.current{{background:var(--accent);color:white}}.rail-arrow{{color:#aa9e89}}
.attention-strip{{display:grid;grid-template-columns:1fr 1.15fr 1fr;border:1px solid var(--rule);border-radius:7px;overflow:hidden;margin:2px 0 12px}}.attention-strip>div{{padding:8px 10px;background:var(--paper2);border-right:1px solid var(--rule)}}.attention-strip>div:last-child{{border-right:0}}.attention-strip small,.attention-strip b{{display:block}}.attention-strip b{{font-size:12px;margin-top:2px}}
.cockpit-grid{{display:grid;grid-template-columns:minmax(300px,.72fr) minmax(0,1.75fr);gap:11px}}.left-stack{{display:grid;gap:11px;align-content:start}}.pane{{border:1px solid var(--rule);background:var(--paper);border-radius:8px;overflow:hidden}}.pane-head{{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:9px 11px;border-bottom:1px solid var(--rule);background:var(--paper2)}}.pane-head span{{font-size:10px;color:var(--muted)}}
.ladder{{padding:7px 11px}}.ladder-row{{display:grid;grid-template-columns:24px 1fr;gap:7px;padding:5px 0;border-bottom:1px solid #ebe2d2}}.ladder-row:last-child{{border-bottom:0}}.ladder-row.provisional{{color:var(--muted)}}.ladder-row.current{{color:#2f5f8f;background:linear-gradient(90deg,var(--accent-soft),transparent);margin:0 -11px;padding:6px 11px}}.marker{{font-weight:900}}.current-tag{{display:inline-block;margin-left:7px;font-size:9px;border:1px solid var(--accent);color:#2f5f8f;background:#f4f8fc;padding:1px 5px;border-radius:99px;vertical-align:2px}}
.timeline{{overflow:auto}}.timeline-row{{display:grid;grid-template-columns:88px minmax(170px,.9fr) minmax(210px,1.15fr) minmax(210px,1.15fr);gap:9px;padding:7px 9px;border-bottom:1px solid #ebe2d2;min-width:790px}}.timeline-head{{font-size:9px;color:var(--muted);background:var(--paper2);letter-spacing:.05em}}.timeline-row span{{min-width:0}}.timeline-more{{padding:8px 10px;color:var(--muted);font-size:11px}}
.efficiency-pane{{min-height:170px}}.efficiency-chart{{display:block;width:100%;height:auto;padding:8px 8px 0}}.axis{{stroke:#b9ad98;stroke-width:1}}.axis-label{{font-size:9px;fill:#756d62}}.dot{{fill:var(--accent);stroke:#fffdf7;stroke-width:2}}.dot-blocked,.dot-budget-exhausted{{fill:#9f5d4d}}.dot-negative-finding{{fill:#7b7b69}}.dot-needs-human-gate{{fill:#b7904b}}.chart-caption{{font-size:10px;color:var(--muted);padding:0 10px 9px}}.chart-empty{{padding:14px 12px;color:var(--muted)}}.chart-empty b,.chart-empty span{{display:block}}.chart-empty span{{margin-top:4px;font-size:11px}}
.empty-state,.empty-room{{padding:16px;color:var(--muted);background:var(--paper);border:1px solid var(--rule)}}.meta-strip{{display:flex;flex-wrap:wrap;gap:15px;border-top:1px solid var(--rule);padding-top:9px;margin-top:11px;color:var(--muted);font-size:10px}}.meta-strip b{{color:var(--ink)}}
@media(max-width:1050px){{main{{padding:14px}}.kpis{{grid-template-columns:repeat(2,1fr)}}.control-layout{{grid-template-columns:1fr}}.project-sidebar{{position:static;display:flex;overflow:auto}}.sidebar-head{{min-width:130px}}.project-nav{{min-width:190px;border-right:1px solid #ebe2d2;border-bottom:0}}.summary-context,.cockpit-grid,.attention-strip{{grid-template-columns:1fr}}.attention-strip>div{{border-right:0;border-bottom:1px solid var(--rule)}}.attention-strip>div:last-child{{border-bottom:0}}.hero,.project-title{{align-items:start;flex-direction:column}}}}
</style>
<script>
function showProject(index, name) {{
  document.querySelectorAll('[data-project-panel]').forEach(function(el, i) {{
    el.classList.toggle('active', i === index);
  }});
  document.querySelectorAll('[data-project-tab]').forEach(function(el, i) {{
    var active = i === index;
    el.classList.toggle('active', active);
    el.setAttribute('aria-selected', active ? 'true' : 'false');
  }});
  try {{ localStorage.setItem('ooda.activeProject', name || ''); }} catch (e) {{}}
}}
window.addEventListener('DOMContentLoaded', function() {{
  var tabs = Array.prototype.slice.call(document.querySelectorAll('[data-project-tab]'));
  if (!tabs.length) return;
  var saved = '';
  try {{ saved = localStorage.getItem('ooda.activeProject') || ''; }} catch (e) {{}}
  var idx = tabs.findIndex(function(tab) {{ return tab.dataset.projectName === saved; }});
  if (idx < 0) idx = 0;
  showProject(idx, tabs[idx].dataset.projectName);
}});
</script>
</head>
<body>
<main>
  <div class="hero">
    <div>
      <div class="eyebrow">LOCAL · DERIVED · READ-ONLY</div>
      <h1>OODA Control Room</h1>
      <p>Live companion view for durable OODA state under {_e(root)}. Git/project artifacts remain authoritative.</p>
    </div>
    <div>
      <button onclick="location.reload()">Refresh now</button>
      <small>{"Auto refresh every " + str(refresh_seconds) + "s" if refresh_seconds > 0 else "Auto refresh off"}</small>
    </div>
  </div>
  <div class="kpis">
    <div class="kpi"><small>Projects</small><b>{len(projects)}</b></div>
    <div class="kpi"><small>Active missions</small><b>{active}</b></div>
    <div class="kpi"><small>Human gates / review</small><b>{review}</b></div>
    <div class="kpi"><small>Blocked</small><b>{blocked}</b></div>
  </div>
  {project_area}
</main>
</body>
</html>"""


class _Handler(BaseHTTPRequestHandler):
    root = Path.home() / "repos"
    refresh_seconds = 15

    def do_GET(self) -> None:
        if urlparse(self.path).path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        body = render_html(discover_projects(self.root), self.refresh_seconds, self.root).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        return


def serve() -> None:
    root = Path(os.environ.get("OODA_PROJECTS_ROOT", str(Path.home() / "repos"))).expanduser()
    port = int(os.environ.get("OODA_DASHBOARD_PORT", "8792"))
    refresh = max(0, int(os.environ.get("OODA_DASHBOARD_REFRESH_SECONDS", "15")))
    _Handler.root = root
    _Handler.refresh_seconds = refresh
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"OODA Control Room serving http://127.0.0.1:{port}/")
    server.serve_forever()


def main() -> None:
    if "--serve" in sys.argv[1:]:
        serve()
        return
    from .dashboard_launcher import launch
    raise SystemExit(launch())


if __name__ == "__main__":
    main()
