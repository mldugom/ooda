from __future__ import annotations

import os
import subprocess
import sys
from importlib.resources import files
from pathlib import Path


def main() -> None:
    grok_bin = Path(os.environ.get("GROK_BIN", str(Path.home() / ".grok/bin/grok"))).expanduser()
    if not grok_bin.is_file():
        print(
            f"grok-safe: Grok binary not found at {grok_bin}\n"
            "Set GROK_BIN=/path/to/grok if your installation lives elsewhere.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    policy = files("ooda").joinpath("GROK_SAFE.md").read_text(encoding="utf-8")
    cmd = [
        str(grok_bin),
        "--rules",
        policy,
        "--max-turns",
        os.environ.get("GROK_SAFE_MAX_TURNS", "6"),
        "--no-subagents",
        *sys.argv[1:],
    ]
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
