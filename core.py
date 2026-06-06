from __future__ import annotations

import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from pypdf import PdfReader

# Load environment variables on import
import runtime  # noqa: F401

# Monkey-patch to fix compatibility issues of older OpenBMB model code in newer transformers
try:
    import transformers.utils
    import transformers.utils.import_utils

    transformers.utils.is_torch_fx_available = lambda: True  # type: ignore
    transformers.utils.import_utils.is_torch_fx_available = lambda: True  # type: ignore

    # Patch PreTrainedModel.get_expanded_tied_weights_keys to handle list-based _tied_weights_keys in older models
    from transformers import PreTrainedModel

    original_get_expanded_tied_weights_keys = (
        PreTrainedModel.get_expanded_tied_weights_keys
    )

    def patched_get_expanded_tied_weights_keys(
        self, all_submodels: bool = False
    ) -> dict:
        if hasattr(self, "_tied_weights_keys") and isinstance(
            self._tied_weights_keys, list
        ):
            new_tied_weights = {}
            for key in self._tied_weights_keys:
                new_tied_weights[key] = "model.embed_tokens.weight"
            self._tied_weights_keys = new_tied_weights
        return original_get_expanded_tied_weights_keys(
            self, all_submodels=all_submodels
        )

    PreTrainedModel.get_expanded_tied_weights_keys = (
        patched_get_expanded_tied_weights_keys  # type: ignore
    )
except ImportError:
    pass

from config import (  # noqa: E402
    MODEL_ID,
    PARAMETER_COUNT,
    PDF_PAGE_LIMIT,
    PREVIEW_LIMIT,
    SUPPORTED_SUFFIXES,
)

# Global variables for model caching
_tokenizer: Any = None
_model: Any = None


@dataclass(frozen=True)
class DocumentReport:
    """Dataclass to hold the structured results of a document analysis."""

    preview: str
    model_path: str
    key_details: str
    summary: str
    checklist: str


# ZeroGPU compatibility helper: uses spaces.GPU if available, else a local fallback
try:
    import spaces  # type: ignore
except ImportError:

    class _LocalSpacesFallback:
        @staticmethod
        def GPU(
            duration: int = 30,
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
                return function

            return decorator

    spaces = _LocalSpacesFallback()


def get_model_and_tokenizer() -> tuple[Any, Any]:
    """Loads and returns the tokenizer and model from HF, using compatibility patches for newer transformers versions."""
    global _model, _tokenizer
    if _model is None:
        import logging
        import warnings

        # Ignore transformers v4.50+ GenerationMixin inheritance warning (both standard warnings and loggers)
        warnings.filterwarnings(
            "ignore",
            message=".*GenerationMixin.*",
        )

        class GenerationMixinFilter(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                return "GenerationMixin" not in record.getMessage()

        logging.getLogger("transformers").addFilter(GenerationMixinFilter())

        from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

        print(f"Loading tokenizer for {MODEL_ID}...")
        _tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID,
            trust_remote_code=True,
            token=os.environ.get("HF_TOKEN"),
        )

        print(f"Loading configuration for {MODEL_ID}...")
        config = AutoConfig.from_pretrained(
            MODEL_ID,
            trust_remote_code=True,
            token=os.environ.get("HF_TOKEN"),
        )
        # Fix transformers v4.45+ configuration incompatibility with OpenBMB's custom modeling_minicpm.py
        if hasattr(config, "rope_scaling") and isinstance(config.rope_scaling, dict):
            rope_type = config.rope_scaling.get(
                "type", config.rope_scaling.get("rope_type")
            )
            if rope_type in (None, "default"):
                config.rope_scaling = None
            else:
                config.rope_scaling.setdefault("type", rope_type)
                config.rope_scaling.setdefault("factor", 1.0)

        print(f"Loading model {MODEL_ID}...")
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            config=config,
            dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            token=os.environ.get("HF_TOKEN"),
        )
        # Move model to CUDA if available eagerly
        if torch.cuda.is_available():
            print("Moving model to CUDA device...")
            _model = _model.to("cuda")
    return _model, _tokenizer


def run_model_inference(prompt: str) -> tuple[str, str]:
    """Orchestrates model inference using local CPU/GPU first, and falls back to Serverless API on failure."""
    log_lines: list[str] = []
    try:
        log_lines.append("Initializing local model execution...")
        model, tokenizer = get_model_and_tokenizer()
        device = str(model.device)
        log_lines.append(f"Running local model execution on device: {device}...")

        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(device)

        print("Generating response...")
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response: str = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]
        log_lines.append("Local model execution completed successfully.")
        return response, "\n".join(log_lines)
    except Exception as e:
        import traceback

        traceback.print_exc()
        log_lines.append(
            f"Local model execution failed: {e}. Falling back to serverless API..."
        )

    # Serverless API Fallback path
    log_lines.append(
        f"Initiating Hugging Face Serverless Inference API ({MODEL_ID})..."
    )
    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(MODEL_ID, token=os.environ.get("HF_TOKEN"))
        messages = [{"role": "user", "content": prompt}]
        completion = client.chat_completion(messages=messages, max_tokens=512)
        response = completion.choices[0].message.content or ""
        log_lines.append("Serverless API execution completed successfully.")
        return response, "\n".join(log_lines)
    except Exception as e:
        log_lines.append(f"Serverless API execution failed: {e}.")
        log_lines.append("Falling back to local CPU heuristics...")
        return "", "\n".join(log_lines)


def extract_text(file_path: str | None) -> str:
    """Extracts raw text from PDF, TXT, or MD files based on suffix."""
    if not file_path:
        return "No file uploaded."

    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        if suffix == ".pdf":
            return _extract_pdf_text(path)

        if suffix in {".txt", ".md"}:
            return path.read_text(encoding="utf-8", errors="ignore").strip()

        allowed = ", ".join(sorted(SUPPORTED_SUFFIXES))
        return f"Unsupported file type: {suffix or 'unknown'}. Try one of: {allowed}."
    except Exception as e:
        return f"Error reading file: {e}"


def analyze_document(file_path: str | None, notes: str) -> DocumentReport:
    """Main orchestrator: extracts text, runs model inference, parses sections, and returns the report."""
    text = extract_text(file_path)
    preview = text[:PREVIEW_LIMIT] if text else "No readable text found."
    user_context = notes.strip()

    # Generate prompt for the model
    prompt = _build_model_prompt(preview, user_context)

    # Run inference (will use local ZeroGPU if CUDA available, else Serverless API)
    response, log_details = run_model_inference(prompt)

    # Combine selection log with execution log
    model_path = "\n".join(
        [
            f"Primary model: {MODEL_ID}",
            f"Parameters: {PARAMETER_COUNT}",
            "Execution flow: local GPU (on ZeroGPU Space) with hybrid serverless fallback",
            "---",
            log_details,
        ]
    )

    # Parse response sections or fall back to rule-based parser on failures
    if response.strip():
        key_details, summary, checklist = _parse_sections(response)
    else:
        key_details = _build_key_details(text)
        summary = _build_summary(text, user_context)
        checklist = _build_checklist(text, user_context)

    return DocumentReport(
        preview=preview,
        model_path=model_path,
        key_details=key_details,
        summary=summary,
        checklist=checklist,
    )


def _extract_pdf_text(path: Path) -> str:
    """Extracts text from the first pages of a PDF file using pypdf."""
    try:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages[:PDF_PAGE_LIMIT]]
        text = "\n".join(part.strip() for part in pages if part.strip())
        return text or "No text could be extracted from the PDF."
    except Exception as e:
        return f"Error reading PDF file: {e}"


def _build_model_prompt(text: str, notes: str) -> str:
    """Builds the structured text prompt for the reasoning model."""
    user_context = f"\nUser request/context: {notes}" if notes.strip() else ""
    return f"""You are a helpful paperwork assistant. Analyze the following document text and notes, then return a response containing three sections separated by '=== SECTION ===' markers:

=== KEY DETAILS ===
- Likely document type: [E.g., bill, utility invoice, school form, receipt]
- Dates found: [E.g., June 15, 2026, 2026-06-15]
- Amounts found: [E.g., $100.00, $25.00]
- Key Warnings: [List any late fees, signatures required, or attention items]

=== SUMMARY ===
A plain-English explanation of what the document is, who it is from, and what it means in simple terms. Keep it to 2-3 bullet points.

=== CHECKLIST ===
A step-by-step next-action checklist for the user (e.g. - [ ] pay before June 15, - [ ] sign and return to teacher).

{user_context}

Document text:
{text}"""


def _parse_sections(response: str) -> tuple[str, str, str]:
    """Parses response containing === KEY DETAILS ===, === SUMMARY ===, and === CHECKLIST === sections."""
    key_details = "- No key details extracted by model."
    summary = "No model summary generated."
    checklist = "- No actions extracted by model."

    try:
        if "=== KEY DETAILS ===" in response:
            parts = response.split("=== KEY DETAILS ===")
            rest = parts[1]
            if "=== SUMMARY ===" in rest:
                subparts = rest.split("=== SUMMARY ===")
                key_details = subparts[0].strip()
                rest = subparts[1]
                if "=== CHECKLIST ===" in rest:
                    subparts2 = rest.split("=== CHECKLIST ===")
                    summary = subparts2[0].strip()
                    checklist = subparts2[1].strip()
                else:
                    summary = rest.strip()
            else:
                if "=== CHECKLIST ===" in rest:
                    subparts2 = rest.split("=== CHECKLIST ===")
                    key_details = subparts2[0].strip()
                    checklist = subparts2[1].strip()
                else:
                    key_details = rest.strip()
        elif "=== SUMMARY ===" in response:
            parts = response.split("=== SUMMARY ===")
            rest = parts[1]
            if "=== CHECKLIST ===" in rest:
                subparts2 = rest.split("=== CHECKLIST ===")
                summary = subparts2[0].strip()
                checklist = subparts2[1].strip()
            else:
                summary = rest.strip()
        elif "=== CHECKLIST ===" in response:
            parts = response.split("=== CHECKLIST ===")
            checklist = parts[1].strip()
        else:
            summary = response.strip()
    except Exception:
        summary = response.strip()

    return key_details, summary, checklist


def _build_summary(text: str, notes: str) -> str:
    """Generates a rule-based plain-English explanation fallback."""
    if not text or text == "No file uploaded.":
        return "Upload a document to generate a plain-English explanation."

    bullets = [
        "Readable document text was extracted and prepared for small-model reasoning.",
        f"Primary model: {MODEL_ID}",
        "The model-backed version will explain the document, surface obligations, and identify dates or next actions.",
    ]

    if notes:
        bullets.append(f"User context captured: {notes}")

    return "\n".join(f"- {bullet}" for bullet in bullets)


def _build_key_details(text: str) -> str:
    """Extracts dates, amounts, and guesses document type as a fallback."""
    if not text or text == "No file uploaded.":
        return "- No document details found yet."

    dates = _extract_unique(
        [
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
            r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
            r"\b\d{4}-\d{2}-\d{2}\b",
        ],
        text,
    )
    money = _extract_unique([r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?"], text)
    document_type = _guess_document_type(text)

    lines = [f"- Likely document type: {document_type}"]
    lines.append(f"- Dates found: {', '.join(dates[:5]) if dates else 'none found'}")
    lines.append(f"- Amounts found: {', '.join(money[:5]) if money else 'none found'}")

    if "due" in text.lower():
        lines.append(
            "- Attention: the document appears to mention a due date or deadline."
        )
    if "late fee" in text.lower():
        lines.append("- Attention: the document appears to mention a late fee.")
    if "permission" in text.lower():
        lines.append(
            "- Attention: the document appears to require permission or approval."
        )

    return "\n".join(lines)


def _build_checklist(text: str, notes: str) -> str:
    """Generates next actions checklist as a fallback."""
    if not text or text == "No file uploaded.":
        return "- Upload a PDF, TXT, or MD file."

    items = [
        "Confirm the document type and sender.",
        "Look for due dates, payment amounts, signatures, or missing attachments.",
        "Ask a follow-up question if any term or obligation is unclear.",
    ]

    if notes:
        items.append(
            "Use the user notes as context when generating the final model-backed answer."
        )

    return "\n".join(f"- {item}" for item in items)


def _extract_unique(patterns: list[str], text: str) -> list[str]:
    """Finds all unique regex matches in text."""
    values: list[str] = []
    for pattern in patterns:
        values.extend(match.group(0).strip() for match in re.finditer(pattern, text))
    return list(dict.fromkeys(values))


def _guess_document_type(text: str) -> str:
    """Guesses document category based on keyword matching."""
    lowered = text.lower()
    if any(word in lowered for word in ["amount due", "balance", "late fee", "bill"]):
        return "bill or payment notice"
    if any(word in lowered for word in ["permission slip", "field trip", "school"]):
        return "school or family notice"
    if any(word in lowered for word in ["receipt", "invoice", "statement"]):
        return "receipt, invoice, or statement"
    if any(word in lowered for word in ["signature", "application", "form"]):
        return "form or application"
    return "general document"


@spaces.GPU(duration=30)
def analyze_document_ui(
    file_path: str | None,
    notes: str,
) -> tuple[str, str, str, str, str]:
    """Gradio UI entry point decorated with spaces.GPU for ZeroGPU compliance."""
    report = analyze_document(file_path, notes)
    return (
        report.preview,
        report.model_path,
        report.key_details,
        report.summary,
        report.checklist,
    )
