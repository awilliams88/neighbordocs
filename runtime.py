from __future__ import annotations

import os
from pathlib import Path
import asyncio.base_events as base_events
from typing import Any


def patch_asyncio_cleanup_warning() -> None:
    """Patches asyncio EventLoop __del__ method to ignore harmless file descriptor cleanup warnings in notebook/interactive runs."""
    # Skip patching when the runtime does not expose the cleanup hook.
    original_del = getattr(base_events.BaseEventLoop, "__del__", None)
    if original_del is None or getattr(original_del, "_innerspace_patched", False):
        return

    # Preserve normal cleanup while ignoring the known invalid-fd warning.
    def patched_del(self: Any) -> None:
        try:
            original_del(self)
        except ValueError as exc:
            if str(exc) != "Invalid file descriptor: -1":
                raise

    # Mark the patched function so repeated imports stay idempotent.
    setattr(patched_del, "_innerspace_patched", True)
    setattr(base_events.BaseEventLoop, "__del__", patched_del)


def load_env() -> None:
    """Loads environment variables from .env if present in the current or parent directory."""
    # Search the project folder before its parent workspace.
    for path in [Path(".env"), Path("../.env")]:
        if path.is_file():
            try:
                # Parse simple KEY=value lines without adding a dependency.
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip("'\""))
                break
            except Exception:
                # Ignore malformed local env files during app startup.
                pass


# Load local secrets before model or Modal clients are used.
load_env()
