from __future__ import annotations

# Application metadata and descriptions
APP_TITLE = "NeighborDocs"
APP_DESCRIPTION = "Plain-English help for everyday paperwork."

# File processing and size thresholds
SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md"}
PDF_PAGE_LIMIT = 3
PREVIEW_LIMIT = 2000

# Repositories URLs
GITHUB_URL = "https://github.com/awilliams88/neighbordocs"
SPACE_URL = "https://huggingface.co/spaces/build-small-hackathon/neighbordocs"

# Targeted OpenBMB model configuration
MODEL_ID = "openbmb/MiniCPM5-1B-SFT"
SPONSOR_NAME = "OpenBMB"
PARAMETER_COUNT = "1.2B"
