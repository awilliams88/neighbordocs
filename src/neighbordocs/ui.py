from __future__ import annotations

import gradio as gr

from .config import (
    APP_DESCRIPTION,
    APP_TITLE,
    DEFAULT_MODEL_KEY,
    GITHUB_URL,
    MODEL_CHOICES,
    MODEL_LABELS,
    RUNTIME_LABELS,
    SPACE_URL,
)
from .core import analyze_document


def create_app() -> gr.Blocks:
    # Use Soft theme as base
    theme = gr.themes.Soft(
        primary_hue="teal",
        secondary_hue="slate",
        neutral_hue="slate",
    )

    with gr.Blocks(title=APP_TITLE, theme=theme) as demo:
        gr.Markdown(
            f"# {APP_TITLE}\n{APP_DESCRIPTION}",
            elem_id="nd-header",
        )

        with gr.Row():
            # Left Column: Inputs & Controls
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="Upload Document (.pdf, .txt, .md)",
                    file_types=[".pdf", ".txt", ".md"],
                )
                notes_input = gr.Textbox(
                    label="User Context / Instructions",
                    lines=4,
                    placeholder="Example: summarize this notice and give me a checklist of things to remember.",
                )
                with gr.Row():
                    model_input = gr.Dropdown(
                        choices=MODEL_LABELS,
                        value=MODEL_CHOICES[DEFAULT_MODEL_KEY]["label"],
                        label="Model Strategy",
                        interactive=True,
                    )
                    runtime_input = gr.Dropdown(
                        choices=RUNTIME_LABELS,
                        value=RUNTIME_LABELS[0],
                        label="Runtime Target",
                        interactive=True,
                    )
                run_button = gr.Button(
                    "Analyze Document", variant="primary", elem_classes=["nd-btn"]
                )

            # Right Column: Clean Tabbed Outputs
            with gr.Column(scale=1.2):
                with gr.Tabs():
                    with gr.TabItem("📄 Summary & Checklist"):
                        summary_output = gr.Textbox(
                            label="Plain-English Summary",
                            lines=8,
                            elem_classes=["nd-output-box"],
                        )
                        checklist_output = gr.Textbox(
                            label="Next-Action Checklist",
                            lines=6,
                            elem_classes=["nd-output-box"],
                        )
                    with gr.TabItem("🔍 Key Details"):
                        key_details_output = gr.Textbox(
                            label="Extracted Details & Alerts",
                            lines=14,
                            elem_classes=["nd-output-box"],
                        )
                    with gr.TabItem("📝 Text Preview"):
                        extracted_output = gr.Textbox(
                            label="Extracted Text (First 2,000 Chars)",
                            lines=14,
                            elem_classes=["nd-output-box"],
                        )
                    with gr.TabItem("⚙️ Execution Log"):
                        model_output = gr.Textbox(
                            label="Status logs",
                            lines=14,
                            elem_classes=["nd-log-box"],
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
            inputs=[file_input, notes_input, model_input, runtime_input],
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
    runtime_label: str | None,
) -> tuple[str, str, str, str, str]:
    report = analyze_document(file_path, notes, model_label, runtime_label)
    return (
        report.preview,
        report.model_path,
        report.key_details,
        report.summary,
        report.checklist,
    )
