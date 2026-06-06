from __future__ import annotations

import os

os.environ.setdefault("GRADIO_SSR_MODE", "false")

from src.neighbordocs.runtime import patch_asyncio_cleanup_warning

patch_asyncio_cleanup_warning()

from src.neighbordocs import gpu as _gpu_runtime  # noqa: E402,F401
from src.neighbordocs.ui import create_app  # noqa: E402
from src.neighbordocs.styles import CUSTOM_CSS  # noqa: E402

demo = create_app()

if __name__ == "__main__":
    demo.launch(css=CUSTOM_CSS)
