from __future__ import annotations

import sys


PARKED_MESSAGE = (
    "deepseek-safe: DeepSeek/CodeWhale is parked and unqualified. "
    "Use `grok-safe` as the active OODA reference provider. See docs/BACKLOG.md."
)


def main() -> None:
    # Intentionally fail closed while the DeepSeek/CodeWhale experiment is
    # parked. Keeping this console entrypoint prevents stale local installs
    # from silently launching an unqualified provider path.
    print(PARKED_MESSAGE, file=sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
