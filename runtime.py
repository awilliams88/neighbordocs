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


def load_env_file() -> None:
    """Loads environment variables from a .env file if present in the current, parent, or grandparent directory."""
    import os
    from pathlib import Path

    # Search for .env in current directory, parent (submodule parent), or grandparent
    for path in [Path(".env"), Path("../.env"), Path("../../.env")]:
        if path.is_file():
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key:
                            os.environ.setdefault(key, val)
                break  # Stop searching once we successfully find and load a .env file
            except Exception:
                pass


__all__: list[str] = ["patch_asyncio_cleanup_warning", "load_env_file"]
