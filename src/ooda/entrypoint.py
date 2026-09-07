from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "dashboard":
        from .dashboard import launch

        del sys.argv[1]
        raise SystemExit(launch())

    from .cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
