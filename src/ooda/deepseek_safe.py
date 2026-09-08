from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

DEFAULT_CONTROLLER_MODEL = "deepseek-v4-pro"


def _deepseek_binary() -> Optional[str]:
    explicit = os.environ.get("OODA_DEEPSEEK_BIN")
    if explicit:
        return explicit
    return shutil.which("deepseek")


def _skills_ready() -> bool:
    home = Path(os.environ.get("DEEPSEEK_HOME", str(Path.home() / ".deepseek"))).expanduser()
    return (home / "skills" / "ooda-controller" / "SKILL.md").is_file() and (
        home / "skills" / "ooda" / "SKILL.md"
    ).is_file()


def main() -> None:
    binary = _deepseek_binary()
    if not binary:
        print(
            "deepseek-safe: DeepSeek-TUI not found. Install the DeepSeek-endorsed TUI first "
            "(`npm install -g deepseek-tui`) and verify `deepseek --version`.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if not _skills_ready():
        print(
            "deepseek-safe: OODA DeepSeek skills are not installed. Run `ooda setup deepseek` first.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    env = os.environ.copy()
    env.setdefault("DEEPSEEK_MODEL", DEFAULT_CONTROLLER_MODEL)
    command = [binary]
    command.extend(sys.argv[1:])
    raise SystemExit(subprocess.call(command, env=env))


if __name__ == "__main__":
    main()
