from __future__ import annotations

# Application metadata and descriptions
APP_TITLE = "InnerSpace"
APP_DESCRIPTION = "Privacy-first offline cognitive journal & reflection coach."

# Journal settings
SUPPORTED_SUFFIXES = {".txt", ".md"}
ENTRY_LIMIT = 5000  # Character limit for daily logs

# Repositories URLs
GITHUB_URL = "https://github.com/awilliams88/innerspace"
SPACE_URL = "https://huggingface.co/spaces/build-small-hackathon/innerspace"

# Targeted OpenBMB model configuration
MODEL_ID = "openbmb/MiniCPM5-1B-SFT"
ADAPTER_REPO_ID = "build-small-hackathon/inner-space-1b-sft-cbt"
SPONSOR_NAME = "OpenBMB"
PARAMETER_COUNT = "1.2B"
