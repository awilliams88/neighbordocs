from __future__ import annotations

import gradio as gr

from .config import APP_DESCRIPTION, APP_TITLE, GITHUB_URL, SPACE_URL
from .core import analyze_document


def create_app() -> gr.Blocks:
    with gr.Blocks(title=APP_TITLE) as demo:
        gr.Markdown(f"# {APP_TITLE}\n{APP_DESCRIPTION}")

        with gr.Row():
            file_input = gr.File(
                label="Document",
                file_types=[".pdf", ".txt", ".md"],
            )
            notes_input = gr.Textbox(
                label="Context",
                lines=7,
                placeholder="Example: explain this bill and tell me what I need to do next.",
            )

        run_button = gr.Button("Analyze", variant="primary")

        with gr.Row():
            extracted_output = gr.Textbox(label="Extracted text", lines=12)
            summary_output = gr.Textbox(label="Plain-English summary", lines=12)

        checklist_output = gr.Textbox(label="Next-action checklist", lines=8)

        gr.Markdown(f"[GitHub repo]({GITHUB_URL}) | [Hugging Face Space]({SPACE_URL})")

        run_button.click(
            fn=_analyze_for_ui,
            inputs=[file_input, notes_input],
            outputs=[extracted_output, summary_output, checklist_output],
        )

    return demo


def _analyze_for_ui(file_path: str | None, notes: str) -> tuple[str, str, str]:
    report = analyze_document(file_path, notes)
    return report.preview, report.summary, report.checklist
