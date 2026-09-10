from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "dashboard":
        from .dashboard_launcher import launch

        del sys.argv[1]
        raise SystemExit(launch())

    if len(sys.argv) > 1 and sys.argv[1] == "view":
        from .project_view import main as view_main

        del sys.argv[1]
        raise SystemExit(view_main(sys.argv[1:]))

    if len(sys.argv) > 1 and sys.argv[1] == "statusline":
        from .grok_statusline import main as statusline_main

        del sys.argv[1]
        raise SystemExit(statusline_main(sys.argv[1:]))

    if len(sys.argv) > 1 and sys.argv[1] == "help":
        from .cli import parser

        parser().print_help()
        print(
            "\nAdditional bundled commands:\n"
            "  view                        render the current project view\n"
            "  statusline                  render the Grok-native status line\n"
            "\nExecution provider:\n"
            "  Grok Build                  active reference provider via `grok-safe`"
        )
        raise SystemExit(0)

    from .contract_runtime import run_cli

    run_cli()


if __name__ == "__main__":
    main()
