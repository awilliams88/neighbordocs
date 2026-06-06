from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from .config import (
    DEFAULT_MODEL_KEY,
    MODEL_CHOICES,
    MODEL_KEY_BY_LABEL,
    PDF_PAGE_LIMIT,
    PREVIEW_LIMIT,
    SUPPORTED_SUFFIXES,
)


@dataclass(frozen=True)
class DocumentReport:
    preview: str
    model_path: str
    key_details: str
    summary: str
    checklist: str


def extract_text(file_path: str | None) -> str:
    if not file_path:
        return "No file uploaded."

    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf_text(path)

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore").strip()

    allowed = ", ".join(sorted(SUPPORTED_SUFFIXES))
    return f"Unsupported file type: {suffix or 'unknown'}. Try one of: {allowed}."


def analyze_document(
    file_path: str | None,
    notes: str,
    model_label: str | None,
) -> DocumentReport:
    text = extract_text(file_path)
    preview = text[:PREVIEW_LIMIT] if text else "No readable text found."
    user_context = notes.strip()
    model_choice = get_model_choice(model_label)

    model_path = _build_model_path(model_choice)
    key_details = _build_key_details(text)
    summary = _build_summary(text, user_context, model_choice)
    checklist = _build_checklist(text, user_context, model_choice)

    return DocumentReport(
        preview=preview,
        model_path=model_path,
        key_details=key_details,
        summary=summary,
        checklist=checklist,
    )


def get_model_choice(model_label: str | None) -> dict[str, str]:
    key = MODEL_KEY_BY_LABEL.get(model_label or "", DEFAULT_MODEL_KEY)
    return MODEL_CHOICES[key]


def _extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages[:PDF_PAGE_LIMIT]]
    text = "\n".join(part.strip() for part in pages if part.strip())
    return text or "No text could be extracted from the PDF."


def _build_model_path(model_choice: dict[str, str]) -> str:
    return "\n".join(
        [
            f"Selected path: {model_choice['label']}",
            f"Primary model: {model_choice['model']}",
            f"Sponsor surface: {model_choice['sponsor']}",
            f"Parameter compliance: {model_choice['parameters']}",
            f"Status: {model_choice['status']}",
        ]
    )


def _build_summary(text: str, notes: str, model_choice: dict[str, str]) -> str:
    if not text or text == "No file uploaded.":
        return "Upload a document to generate a plain-English explanation."

    bullets = [
        "Readable document text was extracted and prepared for small-model reasoning.",
        f"Recommended sponsor path: {model_choice['label']}.",
        f"Why this path fits: {model_choice['best_for']}",
        "The final model-backed version will explain the document, surface obligations, and identify dates or next actions.",
    ]

    if notes:
        bullets.append(f"User context captured: {notes}")

    return "\n".join(f"- {bullet}" for bullet in bullets)


def _build_key_details(text: str) -> str:
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


def _build_checklist(text: str, notes: str, model_choice: dict[str, str]) -> str:
    if not text or text == "No file uploaded.":
        return "- Upload a PDF, TXT, or MD file."

    items = [
        "Confirm the document type and sender.",
        "Look for due dates, payment amounts, signatures, or missing attachments.",
        "Ask a follow-up question if any term or obligation is unclear.",
        f"Use the selected model path for: {model_choice['best_for']}",
    ]

    if notes:
        items.append(
            "Use the user notes as context when generating the final model-backed answer."
        )

    return "\n".join(f"- {item}" for item in items)


def _extract_unique(patterns: list[str], text: str) -> list[str]:
    values: list[str] = []
    for pattern in patterns:
        values.extend(match.group(0).strip() for match in re.finditer(pattern, text))
    return list(dict.fromkeys(values))


def _guess_document_type(text: str) -> str:
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
