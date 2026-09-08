from __future__ import annotations

from .compat import patch_importlib_resources


def main() -> None:
    patch_importlib_resources()
    from .deepseek_safe import main as deepseek_safe_main

    deepseek_safe_main()


if __name__ == "__main__":
    main()
