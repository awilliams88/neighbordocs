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


__all__: list[str] = ["patch_asyncio_cleanup_warning"]
