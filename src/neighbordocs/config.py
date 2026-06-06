from __future__ import annotations

APP_TITLE = "NeighborDocs"
APP_DESCRIPTION = "Plain-English help for everyday paperwork."

SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md"}
PDF_PAGE_LIMIT = 3
PREVIEW_LIMIT = 2000

GITHUB_URL = "https://github.com/awilliams88/neighbordocs"
SPACE_URL = "https://huggingface.co/spaces/build-small-hackathon/neighbordocs"

MODEL_PLAN = [
    {
        "name": "pypdf",
        "role": "Basic PDF text extraction",
        "status": "active",
        "parameters": "not a model",
    },
    {
        "name": "nvidia/NVIDIA-Nemotron-Parse-v1.1",
        "role": "Planned layout-aware document parsing",
        "status": "planned",
        "parameters": "<1B class",
    },
    {
        "name": "Small <=4B text reasoner",
        "role": "Planned summary, obligations, deadlines, and next actions",
        "status": "planned",
        "parameters": "<=4B target",
    },
]
