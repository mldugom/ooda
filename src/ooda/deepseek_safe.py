from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

DEFAULT_CONTROLLER_MODEL = "deepseek-v4-pro"


def _deepseek_binary() -> Optional[str]:
    explicit = os.environ.get("OODA_DEEPSEEK_BIN")
    if explicit:
        return explicit
    # DeepSeek-TUI was renamed to CodeWhale in 2026. Prefer the current
    # binary, but keep the legacy name as a compatibility fallback.
    return shutil.which("codewhale") or shutil.which("deepseek")


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


def _skills_ready() -> bool:
    for home in _candidate_homes():
        if (home / "skills" / "ooda-controller" / "SKILL.md").is_file() and (
            home / "skills" / "ooda" / "SKILL.md"
        ).is_file():
            return True
    return False


def main() -> None:
    binary = _deepseek_binary()
    if not binary:
        print(
            "deepseek-safe: CodeWhale not found. Install the current DeepSeek-capable runner first "
            "(`npm install -g --prefix \"$HOME/.local\" codewhale`) and verify `codewhale --version`.",
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
