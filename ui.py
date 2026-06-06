from __future__ import annotations

import gradio as gr
from typing import Any

from config import (
    APP_DESCRIPTION,
    APP_TITLE,
    GITHUB_URL,
    SPACE_URL,
)
from core import analyze_journal_ui


def get_theme() -> Any:
    """Returns the custom soft theme configured for dark slate violet styling."""
    theme = gr.themes.Soft(  # type: ignore
        primary_hue="violet",
        secondary_hue="slate",
        neutral_hue="slate",
    )
    return theme


def create_app() -> gr.Blocks:
    """Creates and lays out the Gradio interface for InnerSpace."""
    with gr.Blocks(title=APP_TITLE) as demo:
        gr.Markdown(
            f"# {APP_TITLE}\n{APP_DESCRIPTION}",
            elem_id="nd-header",
        )

        with gr.Row():
            # Left Column: Journal Entry
            with gr.Column(scale=1):
                gr.Markdown("### ✍️ Today's Journal Entry")
                notes_input = gr.Textbox(
                    label="Write your thoughts here...",
                    lines=10,
                    placeholder="Express your thoughts freely. What happened today? How are you feeling?",
                    elem_id="nd-journal-input",
                )

                with gr.Accordion("📂 Upload entry from file", open=False):
                    file_input = gr.File(
                        label="Upload text or markdown log (.txt, .md)",
                        file_types=[".txt", ".md"],
                    )

                run_button = gr.Button(
                    "Analyze Entry & Reflect",
                    variant="primary",
                    elem_classes=["nd-btn"],
                )

            # Right Column: Reflector Coach and Analytical Dashboard
            with gr.Column(scale=1):
                with gr.Tabs():
                    with gr.TabItem("💭 Reflective CBT Coach"):
                        reflection_output = gr.Textbox(
                            label="Cognitive Reflector Coach Prompt",
                            lines=12,
                            elem_classes=["nd-output-box", "nd-coach-box"],
                        )
                    with gr.TabItem("📊 Cognitive Distortion & Mood Dashboard"):
                        sentiment_output = gr.Textbox(
                            label="Dominant Emotions & Mood",
                            lines=4,
                            elem_classes=["nd-output-box"],
                        )
                        areas_output = gr.Textbox(
                            label="Tagged Life Areas",
                            lines=3,
                            elem_classes=["nd-output-box"],
                        )
                        distortions_output = gr.Textbox(
                            label="Cognitive Distortions Detected",
                            lines=5,
                            elem_classes=["nd-output-box", "nd-distortions-box"],
                        )
                    with gr.TabItem("📝 Entry Logs"):
                        extracted_output = gr.Textbox(
                            label="Extracted Journal Text",
                            lines=7,
                            elem_classes=["nd-output-box"],
                        )
                        model_output = gr.Textbox(
                            label="System execution logs",
                            lines=5,
                            elem_classes=["nd-log-box"],
                        )

        # Demo examples for one-click test runs
        gr.Examples(
            examples=[
                [
                    None,
                    "Today was a disaster. I made a typo in the main deployment script and broke the production build for 15 minutes. My manager was disappointed. I always screw up important things. I'm sure they are going to fire me next week.",
                ],
                [
                    None,
                    "Had an amazing weekend! Met up with an old high school friend. We talked for hours over coffee and reminsiced. I felt so connected and energized. Need to remember to reach out to people more often.",
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
            fn=analyze_journal_ui,
            inputs=[file_input, notes_input],
            outputs=[
                extracted_output,
                model_output,
                sentiment_output,
                areas_output,
                distortions_output,
                reflection_output,
            ],
        )

    return demo
