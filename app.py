# Entry point for the InnerSpace Gradio application.
# Configures environment variables, patches warnings, and launches the interface.

from __future__ import annotations

import os
from runtime import patch_asyncio_cleanup_warning
from styles import CUSTOM_CSS
from ui import create_app, get_theme

# Disable Gradio Server-Side Rendering
os.environ.setdefault("GRADIO_SSR_MODE", "false")

# Patch asyncio to ignore minor event loop warnings on teardown
patch_asyncio_cleanup_warning()

# Build Gradio app block
demo = create_app()
theme = get_theme()

# Start local test server if run as script
if __name__ == "__main__":
    demo.launch(theme=theme, css=CUSTOM_CSS)
