from __future__ import annotations

import os

os.environ.setdefault("GRADIO_SSR_MODE", "false")

from src.neighbordocs.ui import create_app

demo = create_app()

if __name__ == "__main__":
    demo.launch()
