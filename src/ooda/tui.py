from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .dashboard import discover_projects
from .provider_telemetry import _fetch_deepseek_balance, _find_repo

DEFAULT_MODEL = "deepseek-v4-pro"
PHASES = ("OBSERVE", "ORIENT", "DECIDE", "ACT", "VERIFY")


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _short(value: Any, width: int) -> str:
    text = " ".join(str(value or "").split())
    if width <= 1:
        return text[: max(0, width)]
    if len(text) <= width:
        return text
    return text[: width - 1].rstrip() + "…"


def _wrap(value: Any, width: int, limit: int = 2) -> List[str]:
    text = " ".join(str(value or "").split())
    if not text:
        return ["—"]
    lines = textwrap.wrap(text, width=max(10, width), break_long_words=False, break_on_hyphens=False)
    if len(lines) > limit:
        lines = lines[:limit]
        lines[-1] = _short(lines[-1], max(2, width - 1))
    return lines or ["—"]


def _telemetry(repo: Path) -> Dict[str, Any]:
    data = _read_json(repo / ".ooda" / "session-telemetry.json")
    return data if data.get("schema") == "ooda/session-telemetry/v1" else {}


def _project_provider(project: Dict[str, Any]) -> str:
    repo = project.get("repo")
    if isinstance(repo, Path):
        telemetry = _telemetry(repo)
        if telemetry.get("provider"):
            return str(telemetry["provider"])
        meta = _read_json(repo / ".ooda" / "project.json")
        execution = meta.get("execution") if isinstance(meta.get("execution"), dict) else {}
        if execution.get("current_provider"):
            return str(execution["current_provider"])
    return "provider"


def _current_rung(project: Dict[str, Any]) -> str:
    for item in project.get("objective_ladder") or []:
        if isinstance(item, dict) and item.get("status") == "current":
            return str(item.get("label") or "")
    return str(project.get("objective") or "No current objective recorded")


def _next_rung(project: Dict[str, Any]) -> str:
    ladder = [x for x in (project.get("objective_ladder") or []) if isinstance(x, dict)]
    for i, item in enumerate(ladder):
        if item.get("status") == "current" and i + 1 < len(ladder):
            return str(ladder[i + 1].get("label") or "")
    return str(project.get("next_gate") or "No next rung recorded")


def _phase(project: Dict[str, Any]) -> str:
    controller = str(project.get("controller") or "").lower()
    if "human gate" in controller or "awaiting review" in controller:
        return "DECIDE"
    stage = str(project.get("stage") or "orient").lower()
    return {
        "observe": "OBSERVE",
        "orient": "ORIENT",
        "act": "ACT",
        "review": "VERIFY",
    }.get(stage, "ORIENT")


def _phase_rail(project: Dict[str, Any]) -> str:
    current = _phase(project)
    return " ─ ".join(("● " if phase == current else "○ ") + phase for phase in PHASES)


def _balance() -> Optional[float]:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        return None
    result = _fetch_deepseek_balance(key)
    if result and isinstance(result.get("account_balance"), (int, float)):
        return float(result["account_balance"])
    return None


def _context_label(repo: Path) -> str:
    telemetry = _telemetry(repo)
    used = telemetry.get("context_used")
    limit = telemetry.get("context_limit")
    if isinstance(used, (int, float)) and isinstance(limit, (int, float)) and limit > 0:
        pct = float(used) / float(limit) * 100.0
        return f"{pct:.0f}% ctx"
    return "ctx n/a"


def _cost_label(repo: Path) -> str:
    telemetry = _telemetry(repo)
    cost = telemetry.get("session_cost_usd")
    if isinstance(cost, (int, float)):
        marker = "~$" if telemetry.get("session_cost_kind") == "tui-estimate" else "$"
        return f"{marker}{float(cost):.2f} session"
    return "session $ n/a"


def _project_sidebar_lines(projects: List[Dict[str, Any]], selected_repo: Path, width: int, max_lines: int = 13) -> List[str]:
    lines: List[str] = []
    for project in projects:
        repo = project.get("repo")
        selected = isinstance(repo, Path) and repo.resolve() == selected_repo.resolve()
        marker = "●" if selected else "○"
        name = str(project.get("project_id") or (repo.name if isinstance(repo, Path) else "project"))
        provider = _project_provider(project)
        model = ""
        if isinstance(repo, Path):
            t = _telemetry(repo)
            model = str(t.get("model") or "")
        lines.append(_short(f"{marker} {name}", width))
        detail = provider if not model else f"{provider} · {model}"
        lines.append(_short("  " + detail, width))
        if isinstance(repo, Path):
            lines.append(_short("  " + _context_label(repo) + " · " + _cost_label(repo), width))
        if len(lines) >= max_lines:
            break
    return lines[:max_lines]


def _right_panel_lines(project: Dict[str, Any], width: int, last_response: str) -> List[str]:
    lines: List[str] = []
    lines.append("CURRENT")
    lines.extend("  " + x for x in _wrap(_current_rung(project), width - 2, limit=2))
    lines.append("")
    lines.append("WAITING ON")
    waiting = project.get("next_gate") if "human gate" in str(project.get("controller") or "").lower() else project.get("blockers")
    lines.extend("  " + x for x in _wrap(waiting or "No explicit human dependency", width - 2, limit=2))
    lines.append("")
    lines.append("OODA  " + _short(_phase_rail(project), max(10, width - 6)))
    lines.append("")
    lines.append("OBJECTIVE")
    ladder = [x for x in (project.get("objective_ladder") or []) if isinstance(x, dict)]
    for item in ladder[:5]:
        status = item.get("status")
        marker = {"completed": "✓", "current": "●", "provisional": "○"}.get(status, "○")
        lines.append(_short(f"  {marker} {item.get('label') or ''}", width))
    if not ladder:
        lines.append("  No durable objective ladder yet")
    lines.append("")
    lines.append("LAST MATERIAL DECISION")
    timeline = [x for x in (project.get("timeline") or []) if isinstance(x, dict)]
    if timeline:
        latest = timeline[-1]
        decision = str(latest.get("decision") or "")
        impact = str(latest.get("so_what") or "")
        lines.extend("  " + x for x in _wrap(decision, width - 2, limit=2))
        if impact:
            lines.extend("  → " + x for x in _wrap(impact, max(10, width - 4), limit=1))
    else:
        lines.append("  No material decision recorded")
    lines.append("")
    lines.append("NEXT IF GATE PASSES")
    lines.extend("  " + x for x in _wrap(_next_rung(project), width - 2, limit=2))
    lines.append("")
    worker = f"{project.get('role') or 'worker'} · {project.get('work_order') or '—'} · {project.get('controller') or 'idle'}"
    lines.append("WORKER  " + _short(worker, max(10, width - 8)))
    if last_response:
        lines.append("")
        lines.append("LAST RESPONSE")
        lines.extend("  " + x for x in _wrap(last_response, width - 2, limit=4))
    return lines


def render_screen(
    projects: List[Dict[str, Any]],
    selected_repo: Path,
    *,
    model: str = DEFAULT_MODEL,
    balance: Optional[float] = None,
    last_response: str = "",
    width: int = 120,
) -> str:
    width = max(88, width)
    sidebar_w = min(28, max(22, width // 4))
    right_w = width - sidebar_w - 3
    selected = next(
        (
            p
            for p in projects
            if isinstance(p.get("repo"), Path) and p["repo"].resolve() == selected_repo.resolve()
        ),
        None,
    )
    if selected is None:
        selected = {
            "repo": selected_repo,
            "project_id": selected_repo.name,
            "objective": "No OODA project state loaded",
            "next_gate": "Run ooda init or open an adopted repo",
            "blockers": "Project is not OODA-adopted",
            "stage": "orient",
            "controller": "idle",
            "objective_ladder": [],
            "timeline": [],
        }

    title_left = " PROJECTS "
    title_right = f" {str(selected.get('project_id') or selected_repo.name).upper()} "
    top = "┌" + title_left + "─" * max(0, sidebar_w - len(title_left)) + "┬" + title_right + "─" * max(0, right_w - len(title_right)) + "┐"

    left = _project_sidebar_lines(projects, selected_repo, sidebar_w - 2)
    right = _right_panel_lines(selected, right_w - 2, last_response)
    rows = max(len(left), len(right), 19)
    body: List[str] = [top]
    for i in range(rows):
        l = left[i] if i < len(left) else ""
        r = right[i] if i < len(right) else ""
        body.append("│ " + l.ljust(sidebar_w - 1) + "│ " + r.ljust(right_w - 1) + "│")

    body.append("├" + "─" * sidebar_w + "┴" + "─" * right_w + "┤")
    command_hint = "/ooda-controller <thought>  /ooda <mission>  /refresh  /help  /quit"
    body.append("│ " + _short(command_hint, width - 3).ljust(width - 2) + "│")
    body.append("├" + "─" * (width - 1) + "┤")
    context = _context_label(selected_repo)
    cost = _cost_label(selected_repo)
    bal = f"balance ${balance:.2f}" if balance is not None else "balance n/a"
    footer = f"DeepSeek · {model} · max · {context} · {cost} · {bal}"
    body.append("│ " + _short(footer, width - 3).ljust(width - 2) + "│")
    body.append("└" + "─" * (width - 1) + "┘")
    return "\n".join(body)


def route_input(text: str) -> Tuple[str, Optional[str]]:
    stripped = text.strip()
    if not stripped:
        return "local", None
    command, _, remainder = stripped.partition(" ")
    command = command.lower()
    if command in {"/quit", "/exit", "/q"}:
        return "quit", None
    if command == "/help":
        return "help", None
    if command == "/refresh":
        return "refresh", None
    if command in {"/ooda-controller", "/ooda-contorller"}:
        operator = remainder.strip() or (
            "Orient from durable repository state. Return the current objective, material blocker or human gate, "
            "and the single next control action. Do not do deep worker work unless explicitly authorized."
        )
        return "prompt", "Use the ooda-controller skill.\n\nOperator input:\n" + operator
    if command == "/ooda":
        operator = remainder.strip() or "Read the active bounded OODA work order and execute only inside its scope and authority."
        return "prompt", "Use the ooda skill.\n\nOperator input:\n" + operator
    if stripped.startswith("/"):
        return "error", (
            "Unknown OODA TUI command. Provider-native slash menus are not screen-forwarded through app-server; "
            "OODA-owned /ooda-controller and /ooda are implemented directly. Use /help."
        )
    return "prompt", stripped


class CodeWhaleClient:
    def __init__(self, repo: Path, model: str = DEFAULT_MODEL, binary: Optional[str] = None) -> None:
        self.repo = repo
        self.model = model
        self.binary = binary or os.environ.get("OODA_CODEWHALE_BIN") or shutil.which("codewhale")
        if not self.binary:
            raise RuntimeError("CodeWhale not found; install it with `npm install -g --prefix \"$HOME/.local\" codewhale`.")
        env = os.environ.copy()
        env.setdefault("DEEPSEEK_MODEL", model)
        self.proc = subprocess.Popen(
            [self.binary, "app-server", "--stdio"],
            cwd=str(repo),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        if self.proc.stdin is None or self.proc.stdout is None:
            raise RuntimeError("CodeWhale app-server stdio could not be opened")
        self._next_id = 1
        self._request("healthz", {})
        started = self._request("thread/start", {"model": model, "cwd": str(repo)})
        thread_id = started.get("thread_id") if isinstance(started, dict) else None
        if not thread_id:
            raise RuntimeError("CodeWhale did not return a thread_id from thread/start")
        self.thread_id = str(thread_id)

    def _request(self, method: str, params: Dict[str, Any]) -> Any:
        if self.proc.stdin is None or self.proc.stdout is None:
            raise RuntimeError("CodeWhale app-server is not connected")
        request_id = self._next_id
        self._next_id += 1
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        self.proc.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self.proc.stdin.flush()
        while True:
            line = self.proc.stdout.readline()
            if not line:
                rc = self.proc.poll()
                raise RuntimeError(f"CodeWhale app-server exited before replying (rc={rc})")
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(message, dict) or message.get("id") != request_id:
                continue
            if isinstance(message.get("error"), dict):
                error = message["error"]
                raise RuntimeError(str(error.get("message") or error))
            return message.get("result")

    def prompt(self, text: str) -> str:
        result = self._request(
            "prompt/request",
            {"thread_id": self.thread_id, "prompt": text},
        )
        if isinstance(result, dict):
            if result.get("model"):
                self.model = str(result["model"])
            return str(result.get("output") or "")
        return str(result or "")

    def close(self) -> None:
        try:
            if self.proc.poll() is None:
                self._request("shutdown", {})
        except Exception:
            pass
        finally:
            if self.proc.poll() is None:
                self.proc.terminate()


def _help_text() -> str:
    return (
        "/ooda-controller <thought> — invoke the OODA Controller skill\n"
        "/ooda <mission or work-order path> — invoke the bounded OODA worker skill\n"
        "/refresh — reread durable OODA project state\n"
        "/help — show commands\n"
        "/quit — exit\n\n"
        "Plain text is sent to the same persistent DeepSeek thread. CodeWhale is the hidden runtime; "
        "provider-native slash menus are not exposed through its app-server API."
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="ooda tui", description="OODA-native terminal cockpit backed by CodeWhale/DeepSeek")
    parser.add_argument("path", nargs="?", default=".", help="adopted project repo (default: current directory)")
    parser.add_argument("--provider", default="deepseek", choices=["deepseek"], help="interactive runtime provider")
    parser.add_argument("--model", default=os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL))
    args = parser.parse_args(argv)

    requested = Path(args.path).expanduser()
    repo = _find_repo(requested) or _find_repo(Path.cwd())
    if repo is None:
        print("ooda tui: open an OODA-adopted repository (missing .ooda/project.json)", file=sys.stderr)
        return 2

    root = Path(os.environ.get("OODA_PROJECTS_ROOT", str(Path.home() / "repos"))).expanduser()
    projects = discover_projects(root)
    if not any(isinstance(p.get("repo"), Path) and p["repo"].resolve() == repo.resolve() for p in projects):
        projects = discover_projects(repo.parent)

    try:
        client = CodeWhaleClient(repo, model=args.model)
    except (OSError, RuntimeError) as exc:
        print(f"ooda tui: {exc}", file=sys.stderr)
        return 2

    start_balance = _balance()
    current_balance = start_balance
    last_response = ""
    try:
        while True:
            projects = discover_projects(root) or discover_projects(repo.parent)
            width = shutil.get_terminal_size((120, 40)).columns
            print("\033[2J\033[H", end="")
            print(
                render_screen(
                    projects,
                    repo,
                    model=client.model,
                    balance=current_balance,
                    last_response=last_response,
                    width=width,
                )
            )
            try:
                user_text = input("> ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            action, payload = route_input(user_text)
            if action == "quit":
                break
            if action == "local":
                continue
            if action == "refresh":
                last_response = "Durable project state refreshed."
                continue
            if action == "help":
                last_response = _help_text()
                continue
            if action == "error":
                last_response = payload or "Unknown command"
                continue
            if action == "prompt" and payload:
                print("\nworking…", flush=True)
                try:
                    last_response = client.prompt(payload).strip() or "(no model text returned)"
                except RuntimeError as exc:
                    last_response = "Runtime error: " + str(exc)
                # Account balance is provider-reported and cheap enough to refresh after a completed turn.
                # Its delta is not labeled session cost because other concurrent provider usage could contribute.
                current_balance = _balance()
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
