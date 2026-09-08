from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

from .grok_statusline import DEFAULT_REFRESH_SECONDS, configure_status_line


def _grok_binary() -> str | None:
    explicit = os.environ.get("GROK_BIN")
    if explicit:
        return explicit

    default = Path.home() / ".grok" / "bin" / "grok"
    if default.is_file() and os.access(default, os.X_OK):
        return str(default)

    return shutil.which("grok")


def _workflows_explicitly_disabled(text: str) -> bool:
    section = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        match = re.fullmatch(r"\[([^]]+)\]", line)
        if match:
            section = match.group(1).strip().lower()
            continue
        if section == "workflows":
            match = re.fullmatch(r"enabled\s*=\s*(true|false)", line, flags=re.IGNORECASE)
            if match:
                return match.group(1).lower() == "false"
    return False


def _grok_config_path() -> Path:
    return Path(os.environ.get("GROK_HOME", str(Path.home() / ".grok"))).expanduser() / "config.toml"


def _warn_if_workflows_disabled() -> None:
    if os.environ.get("GROK_WORKFLOWS") not in {None, ""}:
        return
    config = _grok_config_path()
    try:
        text = config.read_text(encoding="utf-8")
    except OSError:
        return
    if _workflows_explicitly_disabled(text):
        print(
            "grok-safe: warning: [workflows] enabled=false in ~/.grok/config.toml. "
            "OODA Controller inline workflow/subagent delegation may be unavailable. "
            "OODA will not modify this user setting automatically.",
            file=sys.stderr,
        )


def _ooda_cli() -> str | None:
    explicit = os.environ.get("OODA_BIN")
    if explicit:
        return explicit

    default = Path.home() / ".local" / "bin" / "ooda"
    if default.is_file() and os.access(default, os.X_OK):
        return str(default)

    return shutil.which("ooda")


def _configure_ooda_status_line() -> None:
    if os.environ.get("OODA_GROK_STATUSLINE", "1").lower() in {"0", "false", "no", "off"}:
        return

    ooda_bin = _ooda_cli()
    if not ooda_bin:
        return

    try:
        refresh = int(os.environ.get("OODA_GROK_STATUSLINE_REFRESH_SECONDS", str(DEFAULT_REFRESH_SECONDS)))
    except ValueError:
        refresh = DEFAULT_REFRESH_SECONDS
    refresh = max(1, min(86400, refresh))

    changed = configure_status_line(
        _grok_config_path(),
        command=f"{shlex.quote(ooda_bin)} statusline",
        refresh_seconds=refresh,
    )
    if changed:
        print(
            f"grok-safe: configured OODA Grok status line (refresh {refresh}s). Restart Grok to load it.",
            file=sys.stderr,
        )


def main() -> None:
    grok_bin = _grok_binary()
    if not grok_bin:
        print(
            "grok-safe: Grok CLI not found. Set GROK_BIN or ensure `grok` is on PATH.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    _configure_ooda_status_line()
    _warn_if_workflows_disabled()

    policy = (
        files("ooda")
        .joinpath("resources")
        .joinpath("EFFICIENT_AGENT.md")
        .read_text(encoding="utf-8")
    )

    command = [grok_bin, "--rules", policy]

    max_turns = os.environ.get("OODA_GROK_MAX_TURNS")
    if max_turns:
        command.extend(["--max-turns", max_turns])

    if os.environ.get("OODA_GROK_NO_SUBAGENTS", "0").lower() in {"1", "true", "yes"}:
        command.append("--no-subagents")

    command.extend(sys.argv[1:])
    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    main()
