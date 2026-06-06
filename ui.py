# Module responsible for creating and laying out the Gradio interface.
# Connects UI input components to core logical workflows.

from __future__ import annotations

from typing import Any
import gradio as gr
from gradio.themes import Soft

from config import (
    APP_DESCRIPTION,
    APP_TITLE,
    GITHUB_URL,
    SPACE_URL,
)
from core import analyze_journal_ui, chat_respond_ui


def get_theme() -> Any:
    """Returns the custom soft theme configured for dark slate violet styling."""
    theme = Soft(
        primary_hue="violet",
        secondary_hue="slate",
        neutral_hue="slate",
    )
    return theme


def create_app() -> gr.Blocks:
    """Creates and lays out the Gradio interface for InnerSpace."""
    with gr.Blocks(title=APP_TITLE) as demo:
        # Hidden state variable to hold the parsed journal text as context for the chat session
        journal_context_state = gr.State(value="")

        gr.Markdown(
            f"# {APP_TITLE}\n{APP_DESCRIPTION}",
            elem_id="nd-header",
        )

        with gr.Row():
            # Left Column: Journal Entry Inputs
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

            # Right Column: Chatbot Coach & Card Dashboard
            with gr.Column(scale=1):
                # Chatbot Coach section
                chatbot = gr.Chatbot(
                    label="💭 Reflective CBT Coach",
                    height=320,
                    elem_classes=["nd-chatbot"],
                )
                with gr.Row():
                    chat_input = gr.Textbox(
                        placeholder="Type your reply here...",
                        show_label=False,
                        scale=4,
                        elem_classes=["nd-chat-input"],
                    )
                    send_button = gr.Button(
                        "Send",
                        variant="secondary",
                        scale=1,
                        elem_classes=["nd-send-btn"],
                    )

                # Dashboard Row
                with gr.Row():
                    sentiment_output = gr.Textbox(
                        label="📊 Dominant Emotions",
                        lines=3,
                        interactive=False,
                        elem_classes=["nd-output-card", "nd-emotions-card"],
                    )
                    areas_output = gr.Textbox(
                        label="🏷️ Affected Life Areas",
                        lines=3,
                        interactive=False,
                        elem_classes=["nd-output-card", "nd-areas-card"],
                    )
                    distortions_output = gr.Textbox(
                        label="⚠️ Cognitive Distortions",
                        lines=3,
                        interactive=False,
                        elem_classes=["nd-output-card", "nd-distortions-card"],
                    )

        # Bottom Accordion: Diagnostics and Logs
        with gr.Accordion("⚙️ Diagnostics & System Execution Logs", open=False):
            extracted_output = gr.Textbox(
                label="Extracted Journal Text",
                lines=3,
                interactive=False,
                elem_classes=["nd-log-box"],
            )
            model_output = gr.Textbox(
                label="System execution logs",
                lines=4,
                interactive=False,
                elem_classes=["nd-log-box"],
            )

        # Preloaded examples for one-click test runs
        gr.Examples(
            examples=[
                [
                    None,
                    "Today was a disaster. I made a typo in the main deployment script and broke the production build for 15 minutes. My manager was disappointed. I always screw up important things. I'm sure they are going to fire me next week.",
                ],
                [
                    None,
                    "I've been working 12-hour days all week. I feel completely exhausted, but if I take a break, my team will fall behind and it'll be my fault. I just need to push through, but I can barely think straight.",
                ],
                [
                    None,
                    "I got promoted to senior engineer, but I'm terrified. I only got it because they like me, not because I'm actually good at this. Soon they'll assign me a complex task, I'll fail, and everyone will realize I'm a fraud.",
                ],
                [
                    None,
                    "My best friend forgot my birthday. They didn't even text me. I thought we were close, but clearly they don't value our friendship as much as I do. I should just stop talking to them entirely.",
                ],
                [
                    None,
                    "I've had a headache for two days. I googled it and it says it could be a brain tumor. I'm terrified. I can't focus on anything else and I feel like my life is ending.",
                ],
                [
                    None,
                    "Had an amazing weekend! Met up with an old high school friend. We talked for hours over coffee and reminisced. I felt so connected and energized.",
                ],
            ],
            inputs=[file_input, notes_input],
        )

        gr.Markdown(
            f"[GitHub repo]({GITHUB_URL}) | [Hugging Face Space]({SPACE_URL})",
            elem_id="nd-links",
        )

        # Main button triggers analysis, feeds first message into chatbot and sets context
        run_button.click(
            fn=analyze_journal_ui,
            inputs=[file_input, notes_input],
            outputs=[
                extracted_output,
                model_output,
                sentiment_output,
                areas_output,
                distortions_output,
                chatbot,
                journal_context_state,
            ],
        )

        # Bind chatbot message submit events
        chat_input.submit(
            fn=chat_respond_ui,
            inputs=[chatbot, chat_input, journal_context_state],
            outputs=[chatbot, chat_input, model_output],
        )
        send_button.click(
            fn=chat_respond_ui,
            inputs=[chatbot, chat_input, journal_context_state],
            outputs=[chatbot, chat_input, model_output],
        )

    return demo
