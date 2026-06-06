from __future__ import annotations

import asyncio.base_events as base_events
from typing import Any


def patch_asyncio_cleanup_warning() -> None:
    """Patches asyncio EventLoop __del__ method to ignore harmless file descriptor cleanup warnings in notebook/interactive runs."""
    original_del = getattr(base_events.BaseEventLoop, "__del__", None)
    if original_del is None or getattr(original_del, "_neighbordocs_patched", False):
        return

    def patched_del(self: Any) -> None:
        try:
            original_del(self)
        except ValueError as exc:
            if str(exc) != "Invalid file descriptor: -1":
                raise

    patched_del._neighbordocs_patched = True  # type: ignore[attr-defined]
    base_events.BaseEventLoop.__del__ = patched_del  # type: ignore[method-assign]


def load_env() -> None:
    """Loads environment variables from .env if present in the current or parent directory."""
    import os
    from pathlib import Path

    for path in [Path(".env"), Path("../.env")]:
        if path.is_file():
            try:
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip("'\""))
                break  # Stop after loading the first found .env file
            except Exception:
                pass


# Load environment variables at startup
load_env()


__all__: list[str] = ["patch_asyncio_cleanup_warning"]
