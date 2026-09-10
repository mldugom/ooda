from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import uuid
from importlib.resources import files
from pathlib import Path

from .charter import SCHEMA as CHARTER_SCHEMA, diff_charter, new_charter, validate_charter
from .layout import GROK_SKILLS, SKILL_REFERENCES
from .policy import (
    BLOCKED_FOR,
    BlockerError,
    lens_budget_ok,
    BLOCKER_CHALLENGE,
    BLOCKER_TYPES,
    CLAIM_CEILINGS,
    Blocker,
    parse_blocker,
    project_state_warnings,
    validation_route,
)
from .preflight import preflight

ROLES = {
    "controller",
    "researcher",
    "product-strategist",
    "architect",
    "engineer",
    "validator",
    "portfolio-manager",
    "trader",
    "risk-manager",
}
LENSES = {
    "boyd",
    "stanley-lehman",
    "taleb",
    "scientific",
    "statistical",
    "model-risk",
    "value-of-information",
    "causal-mechanism",
    "market-microstructure",
    "portfolio",
    "reliability-systems",
    "product-user",
    "security-abuse",
}
CLAIMS = {"discovery", "evidence", "qualification", "n-a"}
PROJECT_CLASSES = {
    "quantitative-research",
    "trading-research",
    "data-ml-system",
    "software-product",
    "analytical-product",
    "infrastructure",
}


def dump(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def write_if_missing(path: Path, content: str) -> str:
    if path.exists():
        return f"SKIP  {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"CREATE {path}"


def project_scaffold(project_id: str) -> dict[str, str]:
    return {
        "README.md": f"""# {project_id}\n\n## Purpose\n\nDescribe the user/problem, research question, system, or product this repository exists to serve.\n\n## Current state\n\nSee `PROJECT_STATE.md` for concise current truth and `AGENTS.md` for standing operating rules.\n\n## OODA\n\nThis repository uses OODA as an execution doctrine. Project-specific routing/authority metadata lives in `.ooda/project.json`; work orders and traces live under `.ooda/`. OODA does not replace project truth, Git, tests, or human integration authority.\n""",
        "AGENTS.md": """# AGENTS.md\n\n## Repository purpose\n\nKeep this section specific to this project. State what the repository does and what must remain true.\n\n## Operating rules\n\n- Repository state and committed project documents are authoritative over chat history.\n- Bootstrap narrowly: read only the minimum state needed for the active objective.\n- Use one bounded OODA work order for substantial agent execution.\n- Preserve project-specific safety, data-integrity, research, and production boundaries.\n- Do not self-merge, self-certify consequential claims, promote protected refs/models, modify live systems, or spend real money without explicit authority.\n- Preserve useful negative findings when they prevent repeated wasted work.\n\n## Project-specific invariants\n\nAdd the few non-negotiable rules that are unique to this repository. Avoid turning this file into a history log.\n\n## Current provider\n\nGrok Build is the current execution provider unless the project explicitly states otherwise. Existing lifecycle commands remain valid; OODA supplies the work contract around them.\n""",
        "PROJECT_STATE.md": """# Project State\n\n## Current objective\n\nNot yet defined.\n\n## Phase\n\nBootstrap.\n\n## Current truth\n\nRecord only the small set of facts a fresh session needs to orient correctly.\n\n## Open decisions / blockers\n\n- None recorded yet.\n\n## Next gate\n\nDefine the first meaningful objective before spending agent resources.\n\n## Maintenance rule\n\nKeep this file concise. Update it when project truth or the next gate materially changes; do not use it as a chronological transcript.\n""",
        ".ooda/README.md": """# OODA project overlay\n\nThis directory is a thin routing/execution overlay, not a second project-management system.\n\n- `project.json` — project class, authority, and durable state-source hints.\n- `work-orders/` — bounded execution contracts worth preserving.\n- `traces/` — concise outcome/decision provenance when durable value exists.\n\nThe project repository remains authoritative for code, research artifacts, tests, and current project truth.\n""",
    }


def validate_project(d):
    errors = []
    if d.get("schema") != "ooda/project/v1":
        errors.append("schema must be ooda/project/v1")
    if not d.get("project_id"):
        errors.append("project_id is required")
    if d.get("project_class") not in PROJECT_CLASSES:
        errors.append("unknown project_class")
    if not isinstance(d.get("authority"), dict):
        errors.append("authority object is required")
    return errors


def validate_work_order(d):
    errors = []
    if d.get("schema") != "ooda/work-order/v1":
        errors.append("schema must be ooda/work-order/v1")
    for key in ("id", "project_id", "objective", "claim_level"):
        if not d.get(key):
            errors.append(f"{key} is required")
    # role/profile are optional routing aids: the vnext ablation found no
    # measurable gain from them on ordinary work, so they are never required.
    if d.get("role") and d.get("role") not in ROLES:
        errors.append("unknown role")
    if d.get("claim_level") not in CLAIMS:
        errors.append("unknown claim_level")
    lenses = d.get("lenses") or []
    if not isinstance(lenses, list):
        errors.append("lenses must be a list")
    else:
        unknown = [x for x in lenses if x not in LENSES]
        if unknown:
            errors.append("unknown lenses: " + ", ".join(unknown))
        ok, why = lens_budget_ok(lenses, justification=d.get("lens_justification", ""))
        if not ok:
            errors.append(why)
    if not isinstance(d.get("authority"), dict):
        errors.append("authority object is required")
    return errors


def validate_trace(d):
    errors = []
    if d.get("schema") != "ooda/trace/v1":
        errors.append("schema must be ooda/trace/v1")
    if not d.get("work_order_id"):
        errors.append("work_order_id is required")
    if not d.get("project_id"):
        errors.append("project_id is required")
    if not isinstance(d.get("ooda"), dict):
        errors.append("ooda object is required")
    result = d.get("result")
    if not isinstance(result, dict):
        errors.append("result object is required")
    elif result.get("state") == "blocked":
        try:
            blocker = parse_blocker(result.get("blocker") or "blocked")
        except BlockerError as exc:
            errors.append(f"invalid blocker: {exc}")
        else:
            if blocker.needs_retyping:
                # Readable, not fatal: old traces must keep loading.
                errors.append(
                    "WARN blocked result carries no typed blocker; re-type it "
                    "(blocker_type/blocked_for/claim_ceiling) before relying on it"
                )
    return errors


def validate_file(path: Path):
    data = load(path)
    schema = data.get("schema")
    if schema == "ooda/project/v1":
        return validate_project(data)
    if schema == "ooda/work-order/v1":
        return validate_work_order(data)
    if schema == "ooda/trace/v1":
        return validate_trace(data)
    return [f"unknown schema: {schema!r}"]


def cmd_init(a):
    base = Path(a.path)
    target = base / ".ooda" / "project.json"
    if target.exists() and not a.force:
        print(f"Refusing to overwrite {target}; use --force", file=sys.stderr)
        return 2
    data = {
        "schema": "ooda/project/v1",
        "project_id": a.project_id,
        "project_class": a.project_class,
        "authority": {
            "integration_owner": "human",
            "self_merge": False,
            "live_capital": False,
        },
        "state_sources": ["AGENTS.md", "PROJECT_STATE.md", "README.md"],
        "execution": {"current_provider": "grok", "existing_lifecycle": "preserve"},
        "monitor": {"enabled": False},
    }
    dump(target, data)
    (base / ".ooda" / "work-orders").mkdir(parents=True, exist_ok=True)
    (base / ".ooda" / "traces").mkdir(parents=True, exist_ok=True)
    print(target)
    if a.scaffold:
        for rel, content in project_scaffold(a.project_id).items():
            print(write_if_missing(base / rel, content))
    return 0


def _report_validation(path: Path) -> int:
    try:
        errors = validate_file(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {path}: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"FAIL {path}: {error}")
        return 1
    print(f"PASS {path}")
    return 0


def cmd_doctor(a):
    explicit = getattr(a, "target", None) or getattr(a, "path", None) or "."
    target = Path(explicit)
    if target.is_file():
        return _report_validation(target)

    project = target / ".ooda" / "project.json"
    if not project.exists():
        print(f"MISSING {project}", file=sys.stderr)
        return 2
    rc = _report_validation(project)
    if rc:
        return rc

    for rel in ("AGENTS.md", "PROJECT_STATE.md", "README.md", ".ooda/README.md"):
        path = target / rel
        print(("FOUND " if path.exists() else "INFO  ") + str(path))

    contract_errors = 0
    for pattern in (".ooda/work-orders/*.json", ".ooda/traces/*.json"):
        for path in sorted(target.glob(pattern)):
            contract_errors += int(_report_validation(path) != 0)
    return 1 if contract_errors else 0


def cmd_work_order(a):
    objective = getattr(a, "objective", None) or getattr(a, "objective_text", None)
    if not objective:
        print("FAIL objective is required", file=sys.stderr)
        return 2

    lenses = [x.strip() for x in a.lenses.split(",") if x.strip()]
    work_order_id = a.id or f"ooda-{dt.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    data = {
        "schema": "ooda/work-order/v1",
        "id": work_order_id,
        "project_id": a.project_id or Path.cwd().name,
        "objective": objective,
        "claim_level": a.claim_level,
        "scope": {"allowed": [], "forbidden": []},
        "verification": [],
        "budget": {
            "max_turns": a.max_turns,
            "max_investigation_steps": a.max_investigation_steps,
        },
        "stop_conditions": [
            "current durable state conflicts with task assumptions",
            "objective materially changes",
            "required authority is not granted",
            "budget is exhausted",
        ],
        "authority": {
            "may_merge": False,
            "may_promote_model": False,
            "may_modify_live_runtime": False,
            "may_spend_real_money": False,
        },
    }
    errors = validate_work_order(data)
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 2
    # Optional routing aids appear only when they were actually chosen.
    if a.role:
        data["role"] = a.role
    if a.profile:
        data["profile"] = a.profile
    if lenses:
        data["lenses"] = lenses
    if getattr(a, "lens_justification", ""):
        data["lens_justification"] = a.lens_justification
    env_requires = getattr(a, "env_requires", None) or []
    if env_requires:
        data["environment_requirements"] = list(env_requires)

    target = Path(a.output or f".ooda/work-orders/{work_order_id}.json")
    dump(target, data)
    print(target)
    return 0


def cmd_trace(a):
    work_order = load(Path(a.work_order))
    errors = validate_work_order(work_order)
    if errors:
        for error in errors:
            print(f"FAIL work order: {error}", file=sys.stderr)
        return 2
    data = {
        "schema": "ooda/trace/v1",
        "work_order_id": work_order["id"],
        "project_id": work_order["project_id"],
        "provider": a.provider,
        "claim_level": work_order["claim_level"],
        "ooda": {"observe": "", "orient": "", "decide": "", "act": ""},
        "result": {"state": a.result_state, "summary": a.summary},
        "non_claims": "",
        "next_unknown": "",
        "verification": {"status": "not_recorded", "tests": [], "artifacts": []},
        "economics": {"turns": None, "tool_calls": None, "cost_usd": None},
        "next_gate": "Human/ChatGPT review",
    }
    # Optional descriptors survive into the trace only when the mission used them.
    for key in ("role", "profile"):
        if work_order.get(key):
            data[key] = work_order[key]
    if work_order.get("lenses"):
        data["lenses"] = work_order["lenses"]

    if a.result_state == "blocked":
        if not a.blocker_type:
            print(
                "FAIL a blocked result needs --blocker-type "
                f"({'|'.join(BLOCKER_TYPES[:-1])}). A bare `blocked` loses the "
                "information that decides what may still happen.",
                file=sys.stderr,
            )
            return 2
        blocker = Blocker(
            blocker_type=a.blocker_type,
            blocked_for=tuple(a.blocked_for or ()),
            claim_ceiling=a.claim_ceiling or "n-a",
            target=a.blocker_target,
            note=a.summary,
        )
        data["result"]["blocker"] = blocker.to_dict()
        if blocker.exploration_allowed:
            print(
                "NOTE exploration remains allowed under this blocker. "
                f"Answer before idling: {BLOCKER_CHALLENGE}",
                file=sys.stderr,
            )
    elif a.blocker_type:
        print("FAIL --blocker-type only applies to --result blocked", file=sys.stderr)
        return 2
    target = Path(a.output or f".ooda/traces/{work_order['id']}.json")
    dump(target, data)
    print(target)
    return 0


def cmd_preflight(a):
    """Check the environment before a data-dependent mission, not after."""
    requirements = list(a.requires or [])
    route_to = a.route_to
    if a.work_order:
        mission = load(Path(a.work_order))
        requirements += list(mission.get("environment_requirements") or [])
        route_to = route_to or mission.get("environment_route_to")
    if not requirements:
        print("PREFLIGHT no environment requirements declared; nothing to verify")
        return 0
    report = preflight(requirements, route_to=route_to)
    for result in report.results:
        mark = "OK  " if result.satisfied else "MISS"
        print(f"{mark} {result.requirement.kind}:{result.requirement.value} — {result.detail}")
    if report.satisfied:
        print("PREFLIGHT ok")
        return 0
    print(f"PREFLIGHT blocked — {report.handoff()}", file=sys.stderr)
    return 3


def cmd_charter(a):
    """Freeze the prediction target so it cannot move quietly."""
    if a.diff:
        old, new = (load(Path(x)) for x in a.diff)
        change = diff_charter(old, new)
        if not change.requires_reorientation:
            print("CHARTER unchanged on frozen fields")
            return 0
        print("CHARTER re-orientation required: " + ", ".join(change.changed))
        print(change.reason, file=sys.stderr)
        return 4
    if a.check:
        data = load(Path(a.check))
        errors = validate_charter(data)
        for error in errors:
            print(f"FAIL charter: {error}", file=sys.stderr)
        if errors:
            return 2
        print("CHARTER ok")
        return 0
    if a.new:
        template = new_charter(**{k: f"<{k}>" for k in (
            "decision", "target", "why_target_matters", "decision_time", "baseline",
            "primary_metrics", "holdout", "stop_rule", "resource_budget")})
        target = Path(a.output)
        if target.exists():
            print(f"REFUSE {target} exists", file=sys.stderr)
            return 1
        dump(target, template)
        print(target)
        return 0
    print("FAIL choose one of --new, --check FILE, --diff OLD NEW", file=sys.stderr)
    return 2


def cmd_route_validation(a):
    route = validation_route(a.signal, elevated_uncertainty=a.uncertain)
    print(f"CONSEQUENCE {route.consequence}")
    print(f"INDEPENDENT VALIDATOR {route.independent_validator}")
    print(f"DETERMINISTIC CHECKS {'yes' if route.deterministic_checks else 'no'}")
    print(route.reason)
    return 0


def cmd_state_check(a):
    """Warn when durable orientation prose has absorbed mutable runtime facts."""
    path = Path(a.file)
    if not path.is_file():
        print(f"FAIL {path} not found", file=sys.stderr)
        return 2
    warnings = project_state_warnings(path.read_text(encoding="utf-8"))
    if not warnings:
        print(f"STATE ok {path} carries orientation, not runtime truth")
        return 0
    for w in warnings:
        print(f"WARN {path}:{w.line_number} {w.reason}\n     {w.line}", file=sys.stderr)
    print(
        f"\n{len(warnings)} mutable fact(s) frozen into prose. "
        "Point at the authoritative surface instead; prose never outranks it.",
        file=sys.stderr,
    )
    return 0 if a.warn_only else 1


def cmd_validate(a):
    print("INFO `ooda validate` is kept for compatibility; prefer `ooda doctor FILE`.", file=sys.stderr)
    return _report_validation(Path(a.file))


def _resource_text(*parts: str) -> str:
    return files("ooda").joinpath("resources", *parts).read_text(encoding="utf-8")


def _install_text(target: Path, content: str, *, force: bool) -> int:
    if target.exists() or target.is_symlink():
        try:
            existing = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            existing = None
        if existing == content:
            print(f"ALREADY {target}")
            return 0
        if not force:
            print(f"REFUSE {target} exists and differs; rerun with --force to replace", file=sys.stderr)
            return 1
        if target.is_symlink():
            target.unlink()

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"INSTALL {target}")
    return 0


def _setup_items(grok_home: Path):
    """Every file `ooda setup` installs, including on-demand references.

    References are installed beside the skill that names them so a relative
    `reference/X.md` resolves from any project working directory.
    """
    items = [
        (grok_home / "policies" / "EFFICIENT_AGENT.md", _resource_text("EFFICIENT_AGENT.md")),
    ]
    for skill in GROK_SKILLS:
        items.append((
            grok_home / "skills" / skill / "SKILL.md",
            _resource_text("grok", "skills", skill, "SKILL.md"),
        ))
        for ref in SKILL_REFERENCES[skill]:
            items.append((
                grok_home / "skills" / skill / "reference" / ref,
                _resource_text("reference", ref),
            ))
    return items


def cmd_setup(a):
    grok_home = Path(os.environ.get("GROK_HOME", str(Path.home() / ".grok"))).expanduser()
    items = _setup_items(grok_home)

    failures = sum(_install_text(path, content, force=a.force) for path, content in items)
    if failures:
        return 2

    print(f"OODA Grok skills configured ({len(items)} files).")
    print("Use `grok-safe`, then `/ooda-controller` or `/ooda <mission-file>`.")
    return 0


def cmd_dashboard(a):
    monitor_dir = Path(
        os.environ.get("OODA_CONTROL_ROOM_DIR", str(Path.home() / "repos" / "agent-ops-monitor"))
    ).expanduser()
    script = monitor_dir / "scripts" / "agent-monitor"

    if not script.is_file():
        repo = os.environ.get("OODA_CONTROL_ROOM_REPO")
        if not repo:
            print(
                "Control Room is optional and is not installed at "
                f"{monitor_dir}. Set OODA_CONTROL_ROOM_REPO to an accessible clone URL "
                "or OODA_CONTROL_ROOM_DIR to an existing checkout.",
                file=sys.stderr,
            )
            return 2
        monitor_dir.parent.mkdir(parents=True, exist_ok=True)
        rc = subprocess.call(["git", "clone", repo, str(monitor_dir)])
        if rc:
            return rc

    return subprocess.call(["bash", str(script)])


def cmd_help(_a):
    parser().print_help()
    return 0


def _add_work_order_arguments(q):
    q.add_argument("objective_text", nargs="?", help="bounded objective; may also be supplied with --objective")
    q.add_argument("--objective", help="compatibility form of the objective")
    q.add_argument("--role", choices=sorted(ROLES), help="optional accountability descriptor")
    q.add_argument("--profile", help="optional expertise descriptor")
    q.add_argument("--lenses", default="", help="0-1 by default; 2+ needs --lens-why")
    q.add_argument("--lens-why", dest="lens_justification", default="",
                   help="concrete reason two or more lenses are warranted")
    q.add_argument("--env-requires", action="append", default=[], metavar="KIND:VALUE",
                   help="environment requirement, e.g. path:/data/tape.sqlite (repeatable)")
    q.add_argument("--claim", "--claim-level", dest="claim_level", required=True, choices=sorted(CLAIMS))
    q.add_argument("--project-id")
    q.add_argument("--id")
    q.add_argument("--max-turns", type=int, default=6)
    q.add_argument("--max-investigation-steps", type=int, default=8)
    q.add_argument("--output", help="defaults to .ooda/work-orders/<id>.json")
    q.set_defaults(func=cmd_work_order)


def parser():
    p = argparse.ArgumentParser(prog="ooda", description="Bounded AI work without carrying the whole project in chat")
    subs = p.add_subparsers(dest="command")

    q = subs.add_parser("help", help="show the everyday command surface")
    q.set_defaults(func=cmd_help)

    q = subs.add_parser("init", help="adopt or scaffold an OODA project")
    q.add_argument("--project-id", required=True)
    q.add_argument("--project-class", required=True, choices=sorted(PROJECT_CLASSES))
    q.add_argument("--path", default=".")
    q.add_argument("--scaffold", action="store_true", help="create minimal OODA-ready project docs when missing")
    q.add_argument("--force", action="store_true", help="replace .ooda/project.json only; scaffold docs are never overwritten")
    q.set_defaults(func=cmd_init)

    q = subs.add_parser("doctor", help="check a project or one OODA JSON contract")
    q.add_argument("target", nargs="?", help="project directory or OODA JSON file; default: current directory")
    q.add_argument("--path", help=argparse.SUPPRESS)
    q.set_defaults(func=cmd_doctor)

    q = subs.add_parser("mission", help="create one bounded worker mission")
    _add_work_order_arguments(q)

    q = subs.add_parser("work-order", help=argparse.SUPPRESS)
    _add_work_order_arguments(q)

    q = subs.add_parser("trace", help="record a mission result")
    q.add_argument("--work-order", required=True)
    q.add_argument(
        "--result", "--result-state",
        dest="result_state",
        required=True,
        choices=["completed", "negative_finding", "blocked", "budget_exhausted", "needs_human_gate"],
    )
    q.add_argument("--summary", required=True)
    q.add_argument("--provider", default="grok")
    q.add_argument("--blocker-type", choices=sorted(t for t in BLOCKER_TYPES if t != "legacy"),
                   help="required when --result blocked")
    q.add_argument("--blocked-for", action="append", choices=sorted(BLOCKED_FOR), default=[],
                   help="what the blocker prevents (repeatable)")
    q.add_argument("--claim-ceiling", choices=sorted(CLAIM_CEILINGS))
    q.add_argument("--blocker-target", help="scientific blockers: the exact unidentifiable quantity")
    q.add_argument("--output", help="defaults to .ooda/traces/<work-order-id>.json")
    q.set_defaults(func=cmd_trace)

    q = subs.add_parser("preflight", help="check this environment can run a mission")
    q.add_argument("--requires", action="append", default=[], metavar="KIND:VALUE",
                   help="path:/data/x.sqlite | command:psql | env:API_KEY | host_service:collector")
    q.add_argument("--work-order", help="read environment_requirements from a mission file")
    q.add_argument("--route-to", help="where the mission should run instead")
    q.set_defaults(func=cmd_preflight)

    q = subs.add_parser("charter", help="freeze or diff a prediction target charter")
    q.add_argument("--new", action="store_true", help="write a charter template")
    q.add_argument("--check", metavar="FILE", help="validate a charter")
    q.add_argument("--diff", nargs=2, metavar=("OLD", "NEW"), help="detect goalpost movement")
    q.add_argument("--output", default=".ooda/charter.json")
    q.set_defaults(func=cmd_charter)

    q = subs.add_parser("state-check", help="flag mutable runtime facts frozen into PROJECT_STATE prose")
    q.add_argument("file", nargs="?", default="PROJECT_STATE.md")
    q.add_argument("--warn-only", action="store_true", help="never exit non-zero")
    q.set_defaults(func=cmd_state_check)

    q = subs.add_parser("route-validation", help="route validation by consequence")
    q.add_argument("--signal", action="append", default=[], help="repeatable consequence signal")
    q.add_argument("--uncertain", action="store_true", help="elevated uncertainty or risk")
    q.set_defaults(func=cmd_route_validation)

    q = subs.add_parser("setup", help="install OODA Grok skills and efficiency policy into ~/.grok")
    q.add_argument("--force", action="store_true", help="replace differing OODA skill/policy files")
    q.set_defaults(func=cmd_setup)

    q = subs.add_parser("dashboard", help="open an existing optional OODA Control Room checkout")
    q.set_defaults(func=cmd_dashboard)

    q = subs.add_parser("validate", help=argparse.SUPPRESS)
    q.add_argument("file")
    q.set_defaults(func=cmd_validate)
    return p


def main():
    p = parser()
    args = p.parse_args()
    if not getattr(args, "command", None):
        p.print_help()
        raise SystemExit(0)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
