from __future__ import annotations

APP_TITLE = "NeighborDocs"
APP_DESCRIPTION = "Plain-English help for everyday paperwork."

SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md"}
PDF_PAGE_LIMIT = 3
PREVIEW_LIMIT = 2000
DEFAULT_MODEL_KEY = "nvidia_parse"
DEFAULT_RUNTIME_KEY = "cpu"

GITHUB_URL = "https://github.com/awilliams88/neighbordocs"
SPACE_URL = "https://huggingface.co/spaces/build-small-hackathon/neighbordocs"

MODEL_CHOICES = {
    "nvidia_parse": {
        "label": "NVIDIA Nemotron Parse + tiny reasoner",
        "model": "nvidia/NVIDIA-Nemotron-Parse-v1.1",
        "parameters": "<1B parser + <=4B reasoner target",
        "sponsor": "NVIDIA",
        "best_for": "Forms, bills, reports, tables, structured PDFs, and document intelligence.",
        "status": "recommended path",
    },
    "openbmb_vision": {
        "label": "OpenBMB MiniCPM-V document vision",
        "model": "openbmb/MiniCPM-V-4.6",
        "parameters": "1B class",
        "sponsor": "OpenBMB",
        "best_for": "Image uploads, screenshots, scanned paperwork, OCR-heavy documents.",
        "status": "candidate path",
    },
    "cohere_multilingual": {
        "label": "Cohere Tiny Aya multilingual explanation",
        "model": "Cohere Tiny Aya family (3.35B)",
        "parameters": "3.35B",
        "sponsor": "Cohere",
        "best_for": "Translation, multilingual summaries, cross-lingual paperwork help.",
        "status": "candidate path",
    },
    "tiny_local": {
        "label": "Tiny local reasoner",
        "model": "MiniCPM 1B / <=4B local text model",
        "parameters": "<=4B target",
        "sponsor": "Tiny Titan / Off the Grid",
        "best_for": "Small CPU/ZeroGPU-friendly summary and checklist generation.",
        "status": "badge path",
    },
}

MODEL_LABELS = [choice["label"] for choice in MODEL_CHOICES.values()]
MODEL_KEY_BY_LABEL = {choice["label"]: key for key, choice in MODEL_CHOICES.items()}

RUNTIME_CHOICES = {
    "cpu": {
        "label": "CPU demo runtime",
        "status": "active on current Space",
        "best_for": "Rule-based MVP analysis, fast local testing, and stable public demos.",
    },
    "zerogpu": {
        "label": "ZeroGPU model runtime",
        "status": "ready for model-backed integration",
        "best_for": "NVIDIA/OpenBMB/Cohere model calls once the selected model path is wired.",
    },
}

RUNTIME_LABELS = [choice["label"] for choice in RUNTIME_CHOICES.values()]
RUNTIME_KEY_BY_LABEL = {choice["label"]: key for key, choice in RUNTIME_CHOICES.items()}
