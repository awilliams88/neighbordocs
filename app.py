from __future__ import annotations

import os

# Disable Gradio Server-Side Rendering
os.environ.setdefault("GRADIO_SSR_MODE", "false")

# Patch asyncio to ignore minor event loop warnings on teardown and load .env variables
from runtime import load_env_file, patch_asyncio_cleanup_warning  # noqa: E402

load_env_file()
patch_asyncio_cleanup_warning()

# Import UI components and CSS styling
from styles import CUSTOM_CSS  # noqa: E402
from ui import create_app, get_theme  # noqa: E402

# Build Gradio app block
demo = create_app()
theme = get_theme()

# Start local test server if run as script
if __name__ == "__main__":
    demo.launch(theme=theme, css=CUSTOM_CSS)
