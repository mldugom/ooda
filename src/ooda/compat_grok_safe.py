from __future__ import annotations

from .compat import patch_importlib_resources


def main() -> None:
    patch_importlib_resources()
    from .grok_safe import main as grok_safe_main

    grok_safe_main()


if __name__ == "__main__":
    main()
