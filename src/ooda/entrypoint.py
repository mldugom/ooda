from __future__ import annotations

import sys


_PARKED_PROVIDER_MESSAGE = (
    "DeepSeek/CodeWhale is parked and unqualified. Grok via `grok-safe` is the active reference provider. "
    "See docs/BACKLOG.md."
)


def main() -> None:
    # DeepSeek/CodeWhale experimental operator paths are intentionally parked.
    # Keep the implementation modules in-tree for later re-evaluation, but do
    # not expose them as a normal execution path while Grok is the reference.
    if len(sys.argv) > 2 and sys.argv[1] == "setup" and sys.argv[2] == "deepseek":
        print(_PARKED_PROVIDER_MESSAGE, file=sys.stderr)
        raise SystemExit(2)

    if len(sys.argv) > 3 and sys.argv[1] == "doctor" and sys.argv[2] == "--provider" and sys.argv[3] == "deepseek":
        print(_PARKED_PROVIDER_MESSAGE, file=sys.stderr)
        raise SystemExit(2)

    if len(sys.argv) > 1 and sys.argv[1] == "tui":
        print(_PARKED_PROVIDER_MESSAGE, file=sys.stderr)
        raise SystemExit(2)

    # Hidden compatibility hook for an already-configured CodeWhale install.
    # It is inert unless CodeWhale is launched separately by the operator.
    if len(sys.argv) > 1 and sys.argv[1] == "deepseek-telemetry":
        from .provider_telemetry import deepseek_hook_main

        raise SystemExit(deepseek_hook_main())

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
            "  view                        render objective ladder, decision timeline, and stakeholder summary\n"
            "  trace ... --cost-usd N      optionally record exact/known mission cost for feedback-efficiency chart\n"
            "  statusline                  render the Grok-native OODA status line (normally invoked by Grok)\n"
            "\nProvider status:\n"
            "  Grok                        active reference flavor via `grok-safe`\n"
            "  DeepSeek / CodeWhale        parked; see docs/BACKLOG.md"
        )
        raise SystemExit(0)

    from .contract_runtime import run_cli

    run_cli()


if __name__ == "__main__":
    main()
