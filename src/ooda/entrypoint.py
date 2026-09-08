from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) > 2 and sys.argv[1] == "setup" and sys.argv[2] == "deepseek":
        from .deepseek_setup import setup_deepseek

        force = "--force" in sys.argv[3:]
        raise SystemExit(setup_deepseek(force=force))

    if len(sys.argv) > 3 and sys.argv[1] == "doctor" and sys.argv[2] == "--provider" and sys.argv[3] == "deepseek":
        from .deepseek_setup import doctor_deepseek

        raise SystemExit(doctor_deepseek())

    if len(sys.argv) > 1 and sys.argv[1] == "deepseek-telemetry":
        from .provider_telemetry import deepseek_hook_main

        raise SystemExit(deepseek_hook_main())

    if len(sys.argv) > 1 and sys.argv[1] == "tui":
        from .tui import main as tui_main

        del sys.argv[1]
        raise SystemExit(tui_main(sys.argv[1:]))

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
            "  tui [path]                  open the OODA-native terminal cockpit (DeepSeek/CodeWhale runtime)\n"
            "  view                        render objective ladder, decision timeline, and stakeholder summary\n"
            "  setup deepseek              install OODA DeepSeek skills + telemetry hook\n"
            "  doctor --provider deepseek  check DeepSeek runner, skills, sandbox, and balance access\n"
            "  trace ... --cost-usd N      optionally record exact/known mission cost for feedback-efficiency chart\n"
            "  statusline                  render the Grok-native OODA status line (normally invoked by Grok)"
        )
        raise SystemExit(0)

    from .contract_runtime import run_cli

    run_cli()


if __name__ == "__main__":
    main()
