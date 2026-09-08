from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

SCHEMA = "ooda/project-view/v1"
STATUSES = {"completed", "current", "provisional"}
DEFAULT_LIMIT = 8


def _read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def validate_project_view(data: dict) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if not data.get("project_id"):
        errors.append("project_id is required")
    summary = data.get("stakeholder_summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("stakeholder_summary must be a non-empty string")

    ladder = data.get("objective_ladder")
    if not isinstance(ladder, list) or not ladder:
        errors.append("objective_ladder must be a non-empty list")
    else:
        current_count = 0
        for i, item in enumerate(ladder):
            if not isinstance(item, dict):
                errors.append(f"objective_ladder[{i}] must be an object")
                continue
            if item.get("status") not in STATUSES:
                errors.append(f"objective_ladder[{i}].status must be completed, current, or provisional")
            if item.get("status") == "current":
                current_count += 1
            if not isinstance(item.get("label"), str) or not item.get("label", "").strip():
                errors.append(f"objective_ladder[{i}].label must be a non-empty string")
        if current_count != 1:
            errors.append("objective_ladder must contain exactly one current rung")

    timeline = data.get("timeline")
    if not isinstance(timeline, list):
        errors.append("timeline must be a list")
    else:
        for i, item in enumerate(timeline):
            if not isinstance(item, dict):
                errors.append(f"timeline[{i}] must be an object")
                continue
            for key in ("at", "decision", "so_what", "bigger_idea"):
                if not isinstance(item.get(key), str) or not item.get(key, "").strip():
                    errors.append(f"timeline[{i}].{key} must be a non-empty string")
    return errors


def load_project_view(repo: Path) -> dict:
    path = repo / ".ooda" / "project-view.json"
    if not path.is_file():
        return {}
    try:
        data = _read_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {}
    return data if not validate_project_view(data) else {}


def _wrap_cell(value: str, width: int) -> List[str]:
    words = value.split()
    if not words:
        return [""]
    lines: List[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _timeline_table(entries: List[dict]) -> str:
    widths = (14, 34, 50, 50)
    headers = ("TIME", "DECISION", "IMMEDIATE CONSEQUENCE", "PROGRAM IMPACT")
    out = [
        "  ".join(h.ljust(w) for h, w in zip(headers, widths)),
        "  ".join(("─" * w) for w in widths),
    ]
    for entry in entries:
        cells = [
            _wrap_cell(str(entry.get("at", "")), widths[0]),
            _wrap_cell(str(entry.get("decision", "")), widths[1]),
            _wrap_cell(str(entry.get("so_what", "")), widths[2]),
            _wrap_cell(str(entry.get("bigger_idea", "")), widths[3]),
        ]
        height = max(len(cell) for cell in cells)
        for row in range(height):
            out.append(
                "  ".join(
                    (cell[row] if row < len(cell) else "").ljust(width)
                    for cell, width in zip(cells, widths)
                ).rstrip()
            )
        out.append("")
    return "\n".join(out).rstrip()


def render_text(data: dict, *, limit: int = DEFAULT_LIMIT) -> str:
    errors = validate_project_view(data)
    if errors:
        raise ValueError("; ".join(errors))

    ladder_lines: List[str] = []
    ladder = data["objective_ladder"]
    for i, item in enumerate(ladder):
        status = item["status"]
        marker = {"completed": "✓", "current": "● CURRENT", "provisional": "○"}[status]
        ladder_lines.append(f"{marker} {item['label']}")
        if i < len(ladder) - 1:
            ladder_lines.append("    ↓")

    timeline = data.get("timeline", [])
    shown = timeline if limit <= 0 else timeline[-limit:]
    project_id = data["project_id"]
    parts = [
        f"OBJECTIVE LADDER — {project_id}",
        "\n".join(ladder_lines),
        "",
        f"OODA TIMELINE — {project_id}",
        _timeline_table(shown) if shown else "No material decision pivots recorded yet.",
        "",
        "CURRENT STAKEHOLDER SUMMARY",
        data["stakeholder_summary"].strip(),
    ]
    if limit > 0 and len(timeline) > limit:
        parts.insert(-2, f"Showing latest {limit} of {len(timeline)} timeline entries. Use --all for the full history.\n")
    return "\n".join(parts).rstrip() + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="ooda view", description="Render the durable OODA project view.")
    parser.add_argument("path", nargs="?", default=".", help="Project repository path (default: current directory)")
    parser.add_argument("--all", action="store_true", help="Show the full timeline instead of the latest entries")
    parser.add_argument("--json", action="store_true", help="Print the underlying project-view JSON")
    args = parser.parse_args(argv)

    repo = Path(args.path).expanduser()
    path = repo / ".ooda" / "project-view.json"
    if not path.is_file():
        print(
            f"No durable project view at {path}. Ask /ooda-controller to create one after a material orientation or decision gate.",
            file=sys.stderr,
        )
        return 2
    try:
        data = _read_json(path)
        errors = validate_project_view(data)
        if errors:
            raise ValueError("; ".join(errors))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid project view: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print(render_text(data, limit=0 if args.all else DEFAULT_LIMIT), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
