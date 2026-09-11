from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from urllib.parse import quote

from .cli import load, validate_project
from .dashboard import discover_projects
from .grok_safe import _grok_binary
from .layout import SKILL_REFERENCES
from .policy import project_state_warnings

WORKSTREAM_SCHEMA = "ooda/workstream/v1"
DEFAULT_ORIENTATION_OBJECTIVE = (
    "Orient on current authoritative repository, data, and runtime state; identify the business/modeling decision "
    "this project is trying to improve and the single highest-value modeling or engineering step to take next."
)


def _repo(start: Path) -> Optional[Path]:
    try:
        current = start.expanduser().resolve()
    except OSError:
        current = start.expanduser()
    for candidate in [current] + list(current.parents):
        if (candidate / ".ooda" / "project.json").is_file():
            return candidate
    return None


def _resource_path(*parts: str):
    return files("ooda").joinpath("resources", *parts)


def _expected_skill_files() -> Dict[str, bytes]:
    out = {"skills/ooda/SKILL.md": _resource_path("grok", "skills", "ooda", "SKILL.md").read_bytes()}
    for ref in SKILL_REFERENCES["ooda"]:
        out[f"skills/ooda/reference/{ref}"] = _resource_path("reference", ref).read_bytes()
    return out


def framework_fingerprint() -> str:
    digest = hashlib.sha256()
    parts: Iterable[tuple[str, bytes]] = [
        ("EFFICIENT_AGENT.md", _resource_path("EFFICIENT_AGENT.md").read_bytes()),
        *_expected_skill_files().items(),
    ]
    for name, body in sorted(parts):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(body)
        digest.update(b"\0")
    return digest.hexdigest()


def _grok_home() -> Path:
    return Path(os.environ.get("GROK_HOME", str(Path.home() / ".grok"))).expanduser()


def skill_freshness_errors() -> list[str]:
    home = _grok_home()
    errors: list[str] = []
    for rel, expected in _expected_skill_files().items():
        path = home / rel
        try:
            actual = path.read_bytes()
        except OSError:
            errors.append(f"missing {path}")
            continue
        if actual != expected:
            errors.append(f"stale {path}")
    return errors


def _ooda_home() -> Path:
    return Path(os.environ.get("OODA_HOME", str(Path.home() / ".ooda"))).expanduser()


def _workstream_path(repo: Path) -> Path:
    key = hashlib.sha256(str(repo.resolve()).encode("utf-8")).hexdigest()[:16]
    return _ooda_home() / "workstreams" / f"{repo.name}-{key}.json"


def _read_workstream(repo: Path) -> Dict[str, Any]:
    path = _workstream_path(repo)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict) or data.get("schema") != WORKSTREAM_SCHEMA:
        return {}
    return data


def _write_workstream(repo: Path, session_id: str, *, allow_subagents: bool) -> Path:
    path = _workstream_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema": WORKSTREAM_SCHEMA,
        "repo": str(repo.resolve()),
        "session_id": session_id,
        "framework_fingerprint": framework_fingerprint(),
        "allow_subagents": bool(allow_subagents),
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def _session_root(repo: Path) -> Path:
    return _grok_home() / "sessions" / quote(str(repo.resolve()), safe="")


def _session_ids(repo: Path) -> set[str]:
    root = _session_root(repo)
    try:
        return {p.name for p in root.iterdir() if p.is_dir()}
    except OSError:
        return set()


def _latest_session(repo: Path, candidates: set[str]) -> Optional[str]:
    root = _session_root(repo)
    ranked: list[tuple[float, str]] = []
    for session_id in candidates:
        session_dir = root / session_id
        marker = session_dir / "summary.json"
        try:
            stamp = marker.stat().st_mtime if marker.exists() else session_dir.stat().st_mtime
        except OSError:
            continue
        ranked.append((stamp, session_id))
    return max(ranked)[1] if ranked else None


def _project(repo: Path) -> Dict[str, Any]:
    projects = discover_projects(repo)
    return projects[0] if projects else {"repo": repo, "project_id": repo.name}


def _nonempty(value: Any) -> str:
    return " ".join(str(value or "").split())


def print_next(repo: Path) -> int:
    p = _project(repo)
    rows = [
        ("Business objective", p.get("goal")),
        ("Decision to improve", p.get("decision")),
        ("Current question", p.get("current_question")),
        ("Evidence so far", p.get("evidence")),
        ("Still uncertain", p.get("uncertainty")),
        ("Next highest-value step", p.get("next_step")),
    ]
    print(f"{p.get('project_id') or repo.name}")
    for label, value in rows:
        text = _nonempty(value)
        if text:
            print(f"{label}: {text}")

    current_keys = ("current_question", "evidence", "uncertainty", "next_step")
    if not any(_nonempty(p.get(key)) for key in current_keys):
        print("Current decision state: not yet refreshed from authoritative repository/data/runtime sources.")
        print("Next action: run `ooda run` to orient on current truth before choosing modeling work.")
    return 0


def _run_objective(repo: Path, supplied: Optional[str]) -> str:
    if supplied and supplied.strip():
        return supplied.strip()
    p = _project(repo)
    return (
        _nonempty(p.get("next_step"))
        or _nonempty(p.get("current_question"))
        or DEFAULT_ORIENTATION_OBJECTIVE
    )


def _prompt(repo: Path, objective: str) -> str:
    p = _project(repo)
    context = []
    for label, key in (
        ("Business objective", "goal"),
        ("Decision this work should improve", "decision"),
        ("Current question", "current_question"),
        ("Evidence already established", "evidence"),
        ("Important uncertainty", "uncertainty"),
    ):
        value = _nonempty(p.get(key))
        if value:
            context.append(f"{label}: {value}")
    context_text = "\n".join(context)
    return (
        "Use the ooda skill. Execute one bounded piece of prediction-system work in this repository.\n\n"
        f"Objective: {objective}\n"
        + ("\nCurrent decision context:\n" + context_text + "\n" if context_text else "")
        + "\nOperating constraints:\n"
        "- Treat PROJECT_STATE.md, project-view.json, dashboard text, and prior chat as orientation only. Before calling a mutable fact current, verify it from its authoritative Git, runtime, data, or frozen scientific source.\n"
        "- Before expensive or data-dependent work, establish which data/runtime is authoritative and whether it is available here.\n"
        "- Keep authoritative/private data where it lives. If execution must happen elsewhere, prepare deterministic code here and return one reproducible command plus one compact result artifact.\n"
        "- Use the repository's own integrity/tests at the boundary where evidence is accepted.\n"
        "- Preserve negative findings; do not manufacture a narrative or add model complexity merely because a result disappoints.\n"
        "- Do not merge, deploy, mutate live systems, risk capital, or self-certify a consequential claim without explicit authority.\n"
        "- Stay on this objective. Use normal business and data-science language in updates; internal OODA labels are secondary technical detail.\n"
        "- Do not repeat PIDs, commit hashes, live counts, or other fast-changing implementation facts in the stakeholder summary unless the user explicitly asks for technical detail.\n"
    )


def _prelaunch(repo: Path) -> tuple[Optional[str], list[str]]:
    errors = skill_freshness_errors()
    grok = _grok_binary()
    if not grok:
        errors.append("Grok CLI not found; set GROK_BIN or put grok on PATH")
    try:
        project_errors = validate_project(load(repo / ".ooda" / "project.json"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        project_errors = [str(exc)]
    errors.extend(f"project: {error}" for error in project_errors)
    return grok, errors


def run_work(repo: Path, objective: Optional[str], *, allow_subagents: bool = False) -> int:
    objective = _run_objective(repo, objective)
    grok, errors = _prelaunch(repo)
    if errors:
        for error in errors:
            print(f"CHECK FAILED: {error}", file=sys.stderr)
        if any(error.startswith(("missing ", "stale ")) for error in errors):
            print("Refresh the installed OODA skill before launching: ooda setup --force", file=sys.stderr)
        return 2
    assert grok is not None

    before = _session_ids(repo)
    command = [grok, "--cwd", str(repo), "--rules", _resource_path("EFFICIENT_AGENT.md").read_text(encoding="utf-8")]
    if allow_subagents:
        command.append("--subagents")
    # Grok's interactive CLI accepts the initial prompt as the positional PROMPT.
    # --prompt is not a valid flag in the current CLI; -p/--single is headless.
    command.append(_prompt(repo, objective))
    rc = subprocess.call(command)

    # A normal interactive launch creates a new Grok session. Record only a
    # newly observed session id. Falling back to "most recent" could silently
    # bind OODA to an unrelated Grok conversation, which is worse than refusing
    # continuation and asking for a fresh run.
    new_ids = _session_ids(repo) - before
    session_id = _latest_session(repo, new_ids)
    if session_id:
        _write_workstream(repo, session_id, allow_subagents=allow_subagents)
    elif rc == 0:
        print("OODA run: Grok exited normally but no new session id was observed; `ooda continue` will fail closed.", file=sys.stderr)
    return rc


def continue_work(repo: Path) -> int:
    grok, errors = _prelaunch(repo)
    stream = _read_workstream(repo)
    if not stream:
        errors.append("no OODA workstream is recorded for this repository; start with `ooda run`")
    else:
        if stream.get("repo") != str(repo.resolve()):
            errors.append("recorded workstream belongs to a different repository")
        if stream.get("framework_fingerprint") != framework_fingerprint():
            errors.append("the recorded agent session predates the current OODA rules; start a fresh `ooda run` rather than resuming stale instructions")
        session_id = str(stream.get("session_id") or "")
        if not session_id:
            errors.append("recorded workstream has no session id")
        elif not (_session_root(repo) / session_id).is_dir():
            errors.append(f"recorded Grok session {session_id} is no longer present")
    if errors:
        for error in errors:
            print(f"CHECK FAILED: {error}", file=sys.stderr)
        if any(error.startswith(("missing ", "stale ")) for error in errors):
            print("Refresh the installed OODA skill before continuing: ooda setup --force", file=sys.stderr)
        return 2
    assert grok is not None
    session_id = str(stream["session_id"])
    command = [
        grok,
        "--cwd", str(repo),
        "--rules", _resource_path("EFFICIENT_AGENT.md").read_text(encoding="utf-8"),
        "--resume", session_id,
    ]
    if bool(stream.get("allow_subagents")):
        command.append("--subagents")
    rc = subprocess.call(command)
    if rc == 0:
        _write_workstream(repo, session_id, allow_subagents=bool(stream.get("allow_subagents")))
    return rc


def check(repo: Path) -> int:
    failures = 0
    try:
        errors = validate_project(load(repo / ".ooda" / "project.json"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    if errors:
        failures += 1
        for error in errors:
            print(f"FAIL project setup: {error}")
    else:
        print("OK   project setup")

    grok = _grok_binary()
    if grok:
        print(f"OK   Grok CLI: {grok}")
    else:
        failures += 1
        print("FAIL Grok CLI not found")

    freshness = skill_freshness_errors()
    if freshness:
        failures += 1
        for error in freshness:
            print(f"FAIL OODA skill: {error}")
        print("     Fix before agent work: ooda setup --force")
    else:
        print("OK   installed OODA worker skill matches this checkout")

    state = repo / "PROJECT_STATE.md"
    if state.is_file():
        warnings = project_state_warnings(state.read_text(encoding="utf-8"))
        if warnings:
            print(f"WARN PROJECT_STATE contains {len(warnings)} mutable runtime fact(s); runtime/Git should own those facts")
        else:
            print("OK   project state keeps mutable runtime facts out of prose")

    stream = _read_workstream(repo)
    if stream:
        if stream.get("framework_fingerprint") != framework_fingerprint():
            failures += 1
            print("FAIL saved agent session predates this OODA build; do not continue it")
        else:
            session_id = str(stream.get("session_id") or "")
            if session_id and (_session_root(repo) / session_id).is_dir():
                print("OK   saved agent session is resumable under the current OODA rules")
            else:
                failures += 1
                print("FAIL saved agent session is missing")
    return 1 if failures else 0


def help_text() -> str:
    return """OODA — minimal prediction-work interface

Everyday commands:
  ooda next                     show the trusted decision context and next step
  ooda run [\"objective\"]       launch one Grok workstream in this repository; if omitted, orient on current truth first
  ooda continue                 resume the exact OODA-started Grok session
  ooda check                    check framework/project integrity without using model tokens
  ooda dashboard                open the read-only stakeholder dashboard

`ooda run` uses one agent by default. Add `--allow-subagents` only when parallel specialist work is genuinely useful.
Existing init/doctor/mission/trace/preflight commands remain available as compatibility paths while adopted repositories migrate.
"""


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"help", "-h", "--help"}:
        print(help_text(), end="")
        return 0

    command = argv[0]
    repo = _repo(Path.cwd())
    if repo is None:
        print("OODA: run this command inside an adopted repository containing .ooda/project.json", file=sys.stderr)
        return 2

    if command == "next":
        return print_next(repo)
    if command == "check":
        return check(repo)
    if command == "continue":
        return continue_work(repo)
    if command == "run":
        parser = argparse.ArgumentParser(prog="ooda run", add_help=True)
        parser.add_argument("objective", nargs="?", help="bounded modeling/research/engineering objective; if omitted, orient on current truth or use the trusted recorded next step")
        parser.add_argument("--allow-subagents", action="store_true", help="explicitly enable Grok subagents for this workstream")
        args = parser.parse_args(argv[1:])
        return run_work(repo, args.objective, allow_subagents=args.allow_subagents)
    print(f"Unknown minimal command: {command}", file=sys.stderr)
    return 2