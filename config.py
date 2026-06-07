from __future__ import annotations

# App copy shown in the Gradio header.
APP_TITLE = "Inner 🧠 Space"
APP_DESCRIPTION = "Local-first cognitive journal & reflection coach."

# Journal inputs are limited to small private text files.
SUPPORTED_SUFFIXES = {".txt", ".md"}
ENTRY_LIMIT = 5000

# Public links shown in the Space footer.
GITHUB_URL = "https://github.com/awilliams88/innerspace"
SPACE_URL = "https://huggingface.co/spaces/build-small-hackathon/innerspace"

# Model metadata keeps docs, logs, and UI aligned.
MODEL_ID = "openbmb/MiniCPM5-1B-SFT"
ADAPTER_REPO_ID = "build-small-hackathon/inner-space-1b-sft-cbt"
SPONSOR_NAME = "OpenBMB"
PARAMETER_COUNT = "1.2B"
