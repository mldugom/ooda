from __future__ import annotations

import importlib
import importlib.resources
from pathlib import Path


def patch_importlib_resources() -> None:
    """Provide importlib.resources.files on older Python clone runtimes."""
    if hasattr(importlib.resources, "files"):
        return

    def files(package: str):
        module = importlib.import_module(package)
        module_file = getattr(module, "__file__", None)
        if not module_file:
            raise RuntimeError(f"cannot resolve package resources for {package}")
        return Path(module_file).resolve().parent

    importlib.resources.files = files  # type: ignore[attr-defined]
