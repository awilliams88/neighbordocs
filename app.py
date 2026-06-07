from __future__ import annotations

import os
from env.runtime import patch_asyncio_cleanup_warning
from ui.styles import CUSTOM_CSS
from ui.layout import create_app, get_theme

# Gradio SSR is noisy in Spaces for this app.
os.environ.setdefault("GRADIO_SSR_MODE", "false")

# Hide a harmless Gradio teardown warning in local runs.
patch_asyncio_cleanup_warning()

# Build the Space app once for Gradio to discover.
demo = create_app()

if __name__ == "__main__":
    # Keep direct Python launch available for Space and smoke tests.
    demo.launch(theme=get_theme(), css=CUSTOM_CSS)
