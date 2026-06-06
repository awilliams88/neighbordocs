from __future__ import annotations

import gradio as gr

from .config import (
    APP_DESCRIPTION,
    APP_TITLE,
    DEFAULT_MODEL_KEY,
    GITHUB_URL,
    MODEL_CHOICES,
    MODEL_LABELS,
    SPACE_URL,
)
from .core import analyze_document


def create_app() -> gr.Blocks:
    with gr.Blocks(title=APP_TITLE) as demo:
        gr.Markdown(
            f"# {APP_TITLE}\n{APP_DESCRIPTION}",
            elem_id="nd-header",
        )

        with gr.Row():
            file_input = gr.File(
                label="Document",
                file_types=[".pdf", ".txt", ".md"],
                elem_classes=["nd-panel"],
            )
            notes_input = gr.Textbox(
                label="Context",
                lines=7,
                placeholder="Example: explain this bill and tell me what I need to do next.",
                elem_classes=["nd-panel"],
            )

        model_input = gr.Dropdown(
            choices=MODEL_LABELS,
            value=MODEL_CHOICES[DEFAULT_MODEL_KEY]["label"],
            label="Model strategy",
            interactive=True,
            elem_classes=["nd-panel"],
        )

        run_button = gr.Button("Analyze", variant="primary", elem_classes=["nd-action"])

        with gr.Row():
            extracted_output = gr.Textbox(
                label="Extracted text",
                lines=12,
                elem_classes=["nd-panel"],
            )
            model_output = gr.Textbox(
                label="Selected model path",
                lines=8,
                elem_classes=["nd-panel"],
            )

        with gr.Row():
            key_details_output = gr.Textbox(
                label="Key details",
                lines=10,
                elem_classes=["nd-panel"],
            )
            checklist_output = gr.Textbox(
                label="Next-action checklist",
                lines=10,
                elem_classes=["nd-panel"],
            )

        summary_output = gr.Textbox(
            label="Plain-English summary",
            lines=10,
            elem_classes=["nd-panel"],
        )

        gr.Examples(
            examples=[
                [
                    "examples/sample_bill.txt",
                    "Explain what I owe and what happens next.",
                ],
                [
                    "examples/school_notice.txt",
                    "Summarize what a parent needs to remember.",
                ],
            ],
            inputs=[file_input, notes_input],
        )

        gr.Markdown(
            f"[GitHub repo]({GITHUB_URL}) | [Hugging Face Space]({SPACE_URL})",
            elem_id="nd-links",
        )

        run_button.click(
            fn=_analyze_for_ui,
            inputs=[file_input, notes_input, model_input],
            outputs=[
                extracted_output,
                model_output,
                key_details_output,
                summary_output,
                checklist_output,
            ],
        )

    return demo


def _analyze_for_ui(
    file_path: str | None,
    notes: str,
    model_label: str | None,
) -> tuple[str, str, str, str, str]:
    report = analyze_document(file_path, notes, model_label)
    return (
        report.preview,
        report.model_path,
        report.key_details,
        report.summary,
        report.checklist,
    )
