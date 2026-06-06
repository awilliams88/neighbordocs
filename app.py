from __future__ import annotations

from pathlib import Path

import gradio as gr
from pypdf import PdfReader


def extract_text(file_path: str | None) -> str:
    if not file_path:
        return "No file uploaded."

    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages[:3]]
        text = "\n".join(part.strip() for part in pages if part.strip())
        return text or "No text could be extracted from the PDF."

    if path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    return f"Unsupported file type: {path.suffix}. Try PDF, TXT, or MD."


def summarize_document(file_path: str | None, notes: str) -> tuple[str, str]:
    text = extract_text(file_path)
    preview = text[:2000] if text else "No readable text found."

    summary = (
        "NeighborDocs MVP summary:\n"
        "- This document helper is scaffolded and ready for model integration.\n"
        "- It currently extracts basic text from PDFs and plain text files.\n"
        "- Next step: add OCR, language detection, and sponsor-model reasoning."
    )
    if notes.strip():
        summary += f"\n\nUser notes:\n{notes.strip()}"

    return preview, summary


with gr.Blocks(title="NeighborDocs") as demo:
    gr.Markdown("# NeighborDocs\nA small document helper for everyday paperwork.")
    with gr.Row():
        file_input = gr.File(
            label="Upload a PDF, TXT, or MD file", file_types=[".pdf", ".txt", ".md"]
        )
        notes_input = gr.Textbox(
            label="Optional notes",
            lines=8,
            placeholder="Add context, e.g. explain this bill to me in plain English.",
        )
    run_button = gr.Button("Analyze document", variant="primary")
    extracted_output = gr.Textbox(label="Extracted text preview", lines=10)
    summary_output = gr.Textbox(label="Summary and next steps", lines=10)

    run_button.click(
        summarize_document,
        inputs=[file_input, notes_input],
        outputs=[extracted_output, summary_output],
    )


if __name__ == "__main__":
    demo.launch()
