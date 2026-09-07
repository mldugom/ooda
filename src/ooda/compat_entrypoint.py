from __future__ import annotations

from .compat import patch_importlib_resources


def main() -> None:
    patch_importlib_resources()
    from .entrypoint import main as entrypoint_main

    entrypoint_main()


if __name__ == "__main__":
    main()
