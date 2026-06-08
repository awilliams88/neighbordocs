from __future__ import annotations

from typing import Any
import gradio as gr
from gradio.themes import Soft

from env.config import (
    APP_DESCRIPTION,
    APP_TITLE,
    GITHUB_URL,
    SPACE_URL,
)
from core.analyzer import (
    add_user_message,
    analyze_journal_ui,
    chat_respond_ui,
    reset_reflection_ui,
)
from ui.examples import render_examples


def get_theme() -> Any:
    """Returns the custom soft theme configured for dark slate violet styling."""
    # Match the custom CSS with a dark violet Gradio theme.
    theme = Soft(
        primary_hue="violet",
        secondary_hue="slate",
        neutral_hue="slate",
    )
    return theme


def create_app() -> gr.Blocks:
    """Creates and lays out the Gradio interface for InnerSpace."""
    with gr.Blocks(title=APP_TITLE) as demo:
        # Store the analyzed journal for follow-up chat context.
        journal_context_state = gr.State(value="")

        # Header states the product purpose and guiding promise.
        gr.Markdown(
            f"# {APP_TITLE}\n{APP_DESCRIPTION}",
            elem_id="nd-header",
        )
        gr.Markdown(
            "Turn a journal entry into a grounded reframe, one tiny next step, and a calmer question to carry forward.",
            elem_id="nd-kicker",
        )

        with gr.Row(elem_classes=["nd-main-grid"]):
            # Left column collects journal text or file input.
            with gr.Column(scale=1, elem_classes=["nd-input-panel"]):
                gr.Markdown("## Journal Entry ✍️")
                notes_input = gr.Textbox(
                    label="Write your thoughts here...",
                    lines=8,
                    placeholder="Express your thoughts freely. What happened today? How are you feeling?",
                    elem_id="nd-journal-input",
                )

                distress_slider = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=5,
                    step=1,
                    label="Current distress level",
                    elem_classes=["nd-slider"],
                )

                with gr.Accordion("📂 Upload entry from file", open=False):
                    file_input = gr.File(
                        label="Upload text or markdown log (.txt, .md)",
                        file_types=[".txt", ".md"],
                    )

                run_button = gr.Button(
                    "Analyze Thoughts",
                    variant="primary",
                    elem_classes=["nd-btn"],
                )

            # Right column displays the coaching chat panel.
            with gr.Column(scale=1, elem_classes=["nd-output-panel"]):
                gr.Markdown("## Mindful Coach 👨‍⚕️")
                chatbot = gr.Chatbot(
                    label="Mindful CBT Coach",
                    elem_classes=["nd-chatbot"],
                    show_label=False,
                )
                with gr.Row(elem_classes=["nd-chat-row"]):
                    chat_input = gr.Textbox(
                        placeholder="Type your reply here...",
                        show_label=False,
                        lines=1,
                        max_lines=3,
                        scale=4,
                        elem_classes=["nd-chat-input"],
                    )
                    send_button = gr.Button(
                        "Send",
                        variant="secondary",
                        min_width=140,
                        elem_classes=["nd-send-btn"],
                    )

        # Underneath both panels, display CBT Analysis report cards.
        with gr.Column(elem_classes=["nd-analysis-section"]):
            gr.Markdown("## Cognitive Analysis 🧐")
            with gr.Row(elem_classes=["nd-card-grid"]):
                sentiment_output = gr.Textbox(
                    label="Dominant Emotions 😝",
                    lines=5,
                    interactive=False,
                    elem_classes=["nd-output-card", "nd-emotions-card"],
                )
                areas_output = gr.Textbox(
                    label="Affected Life Areas 🎯",
                    lines=5,
                    interactive=False,
                    elem_classes=["nd-output-card", "nd-areas-card"],
                )
                distortions_output = gr.Textbox(
                    label="Cognitive Distortions 🧠",
                    lines=5,
                    interactive=False,
                    elem_classes=["nd-output-card", "nd-distortions-card"],
                )
            with gr.Row(elem_classes=["nd-card-grid"]):
                reframe_output = gr.Textbox(
                    label="Balanced Reframe 👨‍🏫",
                    lines=5,
                    interactive=False,
                    elem_classes=["nd-output-card", "nd-reframe-card"],
                )
                next_step_output = gr.Textbox(
                    label="Tiny Next Step 🏃",
                    lines=5,
                    interactive=False,
                    elem_classes=["nd-output-card", "nd-next-step-card"],
                )

        # Example cards populate the form without running inference automatically.
        render_examples(file_input, notes_input, distress_slider)

        gr.Markdown(
            f"[GitHub repo]({GITHUB_URL}) | [Hugging Face Space]({SPACE_URL})",
            elem_id="nd-links",
        )

        # Diagnostics stay at the end and remain collapsed during normal use.
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

        # Reset the coach before each new analysis run.
        reset_event = run_button.click(
            fn=reset_reflection_ui,
            inputs=[],
            outputs=[chatbot, chat_input, model_output],
        )

        # Analysis populates report cards, chat, and context state.
        reset_event.then(
            fn=analyze_journal_ui,
            inputs=[file_input, notes_input, distress_slider],
            outputs=[
                extracted_output,
                model_output,
                sentiment_output,
                areas_output,
                distortions_output,
                reframe_output,
                next_step_output,
                chatbot,
                journal_context_state,
            ],
        )

        # Both enter key and button submit chat replies.
        user_msg_event = chat_input.submit(
            fn=add_user_message,
            inputs=[chatbot, chat_input],
            outputs=[chatbot, chat_input],
            queue=False,
        )
        user_msg_event.then(
            fn=chat_respond_ui,
            inputs=[chatbot, journal_context_state],
            outputs=[chatbot, model_output],
        )

        # Chat submission
        send_event = send_button.click(
            fn=add_user_message,
            inputs=[chatbot, chat_input],
            outputs=[chatbot, chat_input],
            queue=False,
        )
        send_event.then(
            fn=chat_respond_ui,
            inputs=[chatbot, journal_context_state],
            outputs=[chatbot, model_output],
        )

    return demo
