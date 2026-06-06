from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from .config import PDF_PAGE_LIMIT, PREVIEW_LIMIT, SUPPORTED_SUFFIXES


@dataclass(frozen=True)
class DocumentReport:
    preview: str
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


def analyze_document(file_path: str | None, notes: str) -> DocumentReport:
    text = extract_text(file_path)
    preview = text[:PREVIEW_LIMIT] if text else "No readable text found."
    user_context = notes.strip()

    summary = _build_summary(text, user_context)
    checklist = _build_checklist(text, user_context)

    return DocumentReport(preview=preview, summary=summary, checklist=checklist)


def _extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages[:PDF_PAGE_LIMIT]]
    text = "\n".join(part.strip() for part in pages if part.strip())
    return text or "No text could be extracted from the PDF."


def _build_summary(text: str, notes: str) -> str:
    if not text or text == "No file uploaded.":
        return "Upload a document to generate a plain-English explanation."

    bullets = [
        "This first version extracts readable document text and prepares it for small-model reasoning.",
        "The final app will explain the document, surface obligations, and identify dates or next actions.",
        "The next implementation step is adding the selected sponsor model path from the README.",
    ]

    if notes:
        bullets.append(f"User context captured: {notes}")

    return "\n".join(f"- {bullet}" for bullet in bullets)


def _build_checklist(text: str, notes: str) -> str:
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
