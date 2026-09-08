from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path
from typing import List, Optional, Tuple

from .provider_telemetry import _fetch_deepseek_balance

HOOK_NAME = "ooda-telemetry"
HOOK_HEADER = "[[hooks.hooks]]"


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


def _toml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _split_header_blocks(lines: List[str]) -> List[List[str]]:
    blocks: List[List[str]] = []
    current: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and current:
            blocks.append(current)
            current = []
        current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _remove_ooda_hook_blocks(lines: List[str]) -> List[str]:
    result: List[str] = []
    for block in _split_header_blocks(lines):
        if block and block[0].strip() == HOOK_HEADER:
            name = ""
            for line in block[1:]:
                match = re.match(r'^\s*name\s*=\s*["\']([^"\']+)["\']\s*$', line)
                if match:
                    name = match.group(1)
                    break
            if name == HOOK_NAME:
                continue
        result.extend(block)
    return result


def _hooks_enabled(lines: List[str]) -> Optional[bool]:
    in_hooks = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("["):
            in_hooks = stripped == "[hooks]"
            continue
        if in_hooks:
            match = re.match(r"^enabled\s*=\s*(true|false)\s*$", stripped, flags=re.IGNORECASE)
            if match:
                return match.group(1).lower() == "true"
    return None


def configure_hook(config_path: Path, command: str) -> Tuple[bool, Optional[str]]:
    config_path = config_path.expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    old = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    lines = _remove_ooda_hook_blocks(old.splitlines())
    enabled = _hooks_enabled(lines)
    warning: Optional[str] = None

    if not any(line.strip() == "[hooks]" for line in lines):
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend(["[hooks]", "enabled = true"])
        enabled = True
    elif enabled is False:
        warning = "CodeWhale hooks are globally disabled; OODA telemetry is installed but will not fire until [hooks] enabled=true."

    if lines and lines[-1].strip():
        lines.append("")
    lines.extend(
        [
            HOOK_HEADER,
            f"name = {_toml_quote(HOOK_NAME)}",
            'event = "turn_end"',
            f"command = {_toml_quote(command)}",
            "background = true",
            "continue_on_error = true",
        ]
    )
    new = "\n".join(lines).rstrip() + "\n"
    if new == old:
        return False, warning

    if config_path.exists() and old:
        import datetime as dt

        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(config_path, config_path.with_name(config_path.name + f".ooda-backup.{stamp}"))
    config_path.write_text(new, encoding="utf-8")
    return True, warning


def _ooda_binary() -> Optional[str]:
    explicit = os.environ.get("OODA_BIN")
    if explicit:
        return explicit
    default = Path.home() / ".local" / "bin" / "ooda"
    if default.is_file() and os.access(default, os.X_OK):
        return str(default)
    return shutil.which("ooda")


def _runner_binary() -> Optional[str]:
    explicit = os.environ.get("OODA_DEEPSEEK_BIN")
    if explicit:
        return explicit
    return shutil.which("codewhale") or shutil.which("deepseek")


def _primary_home() -> Path:
    explicit = os.environ.get("CODEWHALE_HOME") or os.environ.get("DEEPSEEK_HOME")
    if explicit:
        return Path(explicit).expanduser()
    return Path.home() / ".codewhale"


def _candidate_homes() -> List[Path]:
    homes: List[Path] = []
    for value in (
        os.environ.get("CODEWHALE_HOME"),
        os.environ.get("DEEPSEEK_HOME"),
        str(Path.home() / ".codewhale"),
        str(Path.home() / ".deepseek"),
    ):
        if not value:
            continue
        path = Path(value).expanduser()
        if path not in homes:
            homes.append(path)
    return homes


def setup_deepseek(force: bool = False) -> int:
    home = _primary_home()
    items = [
        (
            home / "skills" / "ooda" / "SKILL.md",
            _resource_text("deepseek", "skills", "ooda", "SKILL.md"),
        ),
        (
            home / "skills" / "ooda-controller" / "SKILL.md",
            _resource_text("deepseek", "skills", "ooda-controller", "SKILL.md"),
        ),
    ]
    failures = sum(_install_text(path, content, force=force) for path, content in items)
    if failures:
        return 2

    ooda_bin = _ooda_binary()
    if not ooda_bin:
        print("WARN OODA executable not found; skipping CodeWhale telemetry hook configuration.", file=sys.stderr)
    else:
        config = home / "config.toml"
        changed, warning = configure_hook(config, f"{ooda_bin} deepseek-telemetry")
        print(("CONFIGURE " if changed else "ALREADY ") + str(config) + " OODA turn-end telemetry hook")
        if warning:
            print("WARN " + warning, file=sys.stderr)

    print("OODA DeepSeek skills configured for CodeWhale.")
    print("Controller model: deepseek-v4-pro; delegated child model: deepseek-v4-flash.")
    print("Use `deepseek-safe`, then invoke the `ooda-controller` skill.")
    return 0


def doctor_deepseek() -> int:
    binary = _runner_binary()
    if not binary:
        print("FAIL CodeWhale binary not found (legacy `deepseek` is also accepted)")
        return 2
    print(f"PASS DeepSeek runner: {binary}")

    missing = []
    for name in ("ooda", "ooda-controller"):
        found = None
        for home in _candidate_homes():
            path = home / "skills" / name / "SKILL.md"
            if path.is_file():
                found = path
                break
        if found:
            print(f"PASS skill: {found}")
        else:
            path = _primary_home() / "skills" / name / "SKILL.md"
            print(f"FAIL skill missing: {path}")
            missing.append(path)

    try:
        result = subprocess.run(
            [binary, "doctor", "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"WARN CodeWhale doctor --json unavailable: {exc}")
        result = None

    if result is not None and result.returncode == 0:
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict):
            print(f"INFO model: {payload.get('default_text_model') or 'unknown'}")
            api = payload.get("api_key") if isinstance(payload.get("api_key"), dict) else {}
            print(f"INFO API key source: {api.get('source') or 'unknown'}")
            sandbox = payload.get("sandbox") if isinstance(payload.get("sandbox"), dict) else {}
            if sandbox.get("available"):
                print(f"PASS sandbox: {sandbox.get('kind') or 'available'}")
            else:
                print("WARN sandbox unavailable or not reported")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        balance = _fetch_deepseek_balance(api_key)
        if balance and "account_balance" in balance:
            print(f"PASS DeepSeek account balance endpoint: {balance['account_balance']} {balance.get('currency') or ''}".rstrip())
        else:
            print("WARN DeepSeek account balance endpoint did not return a usable balance")
    else:
        print("INFO DEEPSEEK_API_KEY is not exported; saved CodeWhale auth may still work, but OODA cannot query account balance directly.")

    return 2 if missing else 0
