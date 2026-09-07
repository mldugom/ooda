from __future__ import annotations

import os
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path


def _grok_binary() -> str | None:
    explicit = os.environ.get("GROK_BIN")
    if explicit:
        return explicit

    default = Path.home() / ".grok" / "bin" / "grok"
    if default.is_file() and os.access(default, os.X_OK):
        return str(default)

    return shutil.which("grok")


def main() -> None:
    grok_bin = _grok_binary()
    if not grok_bin:
        print(
            "grok-safe: Grok CLI not found. Set GROK_BIN or ensure `grok` is on PATH.",
            file=sys.stderr,
        )
        raise SystemExit(1)

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
