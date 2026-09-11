from __future__ import annotations

import sys


_MINIMAL = {"next", "run", "continue", "check"}


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "help"

    if command in _MINIMAL or command in {"help", "-h", "--help"}:
        from .workflow import main as workflow_main

        raise SystemExit(workflow_main(sys.argv[1:]))

    if command == "dashboard":
        from .dashboard_launcher import launch

        del sys.argv[1]
        raise SystemExit(launch())

    if command == "view":
        from .project_view import main as view_main

        del sys.argv[1]
        raise SystemExit(view_main(sys.argv[1:]))

    if command == "statusline":
        from .grok_statusline import main as statusline_main

        del sys.argv[1]
        raise SystemExit(statusline_main(sys.argv[1:]))

    if command == "legacy-help":
        from .cli import parser

        parser().print_help()
        raise SystemExit(0)

    # Compatibility path for adopted repositories that still use the v1
    # work-order/trace/preflight commands. It is deliberately not the primary
    # interface and can be removed after real project migration proves it unused.
    from .contract_runtime import run_cli

    run_cli()


if __name__ == "__main__":
    main()
