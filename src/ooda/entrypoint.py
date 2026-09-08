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

    from .cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
