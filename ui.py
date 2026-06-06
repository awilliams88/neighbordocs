from __future__ import annotations

import gradio as gr

from typing import Any

from config import (
    APP_DESCRIPTION,
    APP_TITLE,
    GITHUB_URL,
    SPACE_URL,
)
from core import analyze_document_ui


def get_theme() -> Any:
    """Returns the custom soft theme configured for dark slate styling."""
    theme = gr.themes.Soft(  # type: ignore
        primary_hue="teal",
        secondary_hue="slate",
        neutral_hue="slate",
    )
    return theme


def create_app() -> gr.Blocks:
    """Creates and lays out the Gradio interface with custom Codex styling."""
    # Gradio blocks container for the interface
    with gr.Blocks(title=APP_TITLE) as demo:
        gr.Markdown(
            f"# {APP_TITLE}\n{APP_DESCRIPTION}",
            elem_id="nd-header",
        )

        with gr.Row():
            # Left Column: User Input panels
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="Upload Document (.pdf, .txt, .md)",
                    file_types=[".pdf", ".txt", ".md"],
                )
                notes_input = gr.Textbox(
                    label="User Context / Instructions",
                    lines=6,
                    placeholder="Example: summarize this notice and give me a checklist of things to remember.",
                )
                run_button = gr.Button(
                    "Analyze Document", variant="primary", elem_classes=["nd-btn"]
                )

            # Right Column: Tabbed Output panels
            with gr.Column(scale=1):
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

        # Demo examples for one-click test runs
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

        # Trigger logic execution on button click
        run_button.click(
            fn=analyze_document_ui,
            inputs=[file_input, notes_input],
            outputs=[
                extracted_output,
                model_output,
                key_details_output,
                summary_output,
                checklist_output,
            ],
        )

    return demo
