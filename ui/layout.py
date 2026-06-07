from __future__ import annotations

from html import escape
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

# Examples to demonstrate the app
EXAMPLE_CARDS = [
    {
        "title": "Launch-Day Spiral",
        "distress": 8,
        "text": "I demoed my hackathon app and the button froze right when everyone was watching. My face got hot, I joked awkwardly, and now I keep thinking the whole project looks amateur.",
    },
    {
        "title": "Group Chat Ghost",
        "distress": 6,
        "text": "I posted a meme in the group chat and nobody reacted. Now I feel like I misread the vibe and everyone secretly thinks I am annoying.",
    },
    {
        "title": "Side-Quest Overload",
        "distress": 7,
        "text": "I opened my todo list and somehow started reorganizing my desk, updating app icons, and reading docs. The main task is still untouched, so maybe I have zero discipline.",
    },
    {
        "title": "Coffee Shop Fumble",
        "distress": 4,
        "text": "I dropped my coffee at a crowded cafe and everyone looked over. It was over in ten seconds, but my brain keeps replaying it like a public trial.",
    },
    {
        "title": "Calendar Chaos",
        "distress": 7,
        "text": "I missed a meeting because I read the time zone wrong. My manager said it was okay, but I am convinced this proves I cannot be trusted with real responsibility.",
    },
    {
        "title": "Creative Blank Screen",
        "distress": 5,
        "text": "I sat down to write something fun and produced one terrible sentence in forty minutes. Maybe I only like the idea of being creative and not the actual work.",
    },
    {
        "title": "Fitness App Shame",
        "distress": 6,
        "text": "My fitness app congratulated me for a three-minute walk, and somehow that made me feel worse. Everyone else is doing real workouts while I am celebrating crumbs.",
    },
    {
        "title": "Roommate Sink Saga",
        "distress": 5,
        "text": "The dishes are in the sink again, and I am rehearsing a dramatic speech in my head. If I say something, I will sound petty; if I do not, I will explode.",
    },
    {
        "title": "Tiny Typo Doom",
        "distress": 8,
        "text": "I sent a project update with a typo in the headline. Nobody mentioned it, but I keep imagining everyone questioning whether I pay attention to details.",
    },
    {
        "title": "Overcooked Dinner",
        "distress": 3,
        "text": "I tried making dinner for friends and burned the garlic immediately. They laughed kindly, but I felt embarrassed and wanted to order takeout and disappear.",
    },
    {
        "title": "Unread Email Mountain",
        "distress": 7,
        "text": "My inbox has become a haunted forest. Every unread email feels like proof I am behind, irresponsible, and about to miss something important.",
    },
    {
        "title": "Presentation Freeze",
        "distress": 9,
        "text": "I have a presentation tomorrow and I keep picturing myself forgetting everything. I know the slides, but my brain is acting like I am walking into disaster.",
    },
    {
        "title": "Birthday Overthink",
        "distress": 5,
        "text": "A friend replied to my birthday invite with just 'maybe.' I know people are busy, but now I am wondering if nobody actually wants to come.",
    },
    {
        "title": "Comparison Scroll",
        "distress": 6,
        "text": "I saw someone online ship a polished AI demo in one weekend. My app suddenly feels tiny, late, and kind of embarrassing.",
    },
    {
        "title": "Budget Oops",
        "distress": 6,
        "text": "I ordered delivery twice this week even though I said I would save money. It feels like one small choice proves I cannot stick to anything.",
    },
    {
        "title": "New Hobby Wobble",
        "distress": 4,
        "text": "I went to a beginner pottery class and made a bowl that looks like a tired pancake. Everyone else seemed naturally good, and I felt silly for trying.",
    },
    {
        "title": "Reply-All Panic",
        "distress": 8,
        "text": "I accidentally replied-all with a question that was meant for one person. It was harmless, but my stomach dropped and now I want to avoid email forever.",
    },
    {
        "title": "Weekend Reset Guilt",
        "distress": 5,
        "text": "I spent most of Sunday resting instead of being productive. Now it is evening and I feel like I wasted the whole weekend and fell behind my life.",
    },
    {
        "title": "Tiny Win Suspicion",
        "distress": 3,
        "text": "Something actually went well today, and instead of enjoying it I keep waiting for the catch. Calm feels suspicious, like I missed a problem somewhere.",
    },
    {
        "title": "Bug Fix Whiplash",
        "distress": 8,
        "text": "I fixed one bug in my app and two new weird things appeared. I am starting to think I am just moving the problem around instead of actually improving it.",
    },
]


def get_theme() -> Any:
    """Returns the custom soft theme configured for dark slate violet styling."""
    # Match the custom CSS with a dark violet Gradio theme.
    theme = Soft(
        primary_hue="violet",
        secondary_hue="slate",
        neutral_hue="slate",
    )
    return theme


def _example_card_html(title: str, distress: int, text: str) -> str:
    """Builds a compact example preview with distress shown on the right."""
    return (
        '<div class="nd-example-copy">'
        '<div class="nd-example-head">'
        f"<span>{escape(title)}</span>"
        f"<strong>{distress}/10</strong>"
        "</div>"
        f"<p>{escape(text)}</p>"
        "</div>"
    )


def _select_example(text: str, distress: int) -> tuple[None, str, int]:
    """Populates the journal form from an example card."""
    return None, text, distress


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
                        scale=1,
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
        with gr.Column(elem_classes=["nd-examples-section"]):
            gr.Markdown("## Try a Scenario 🎲")
            for row_start in range(0, len(EXAMPLE_CARDS), 4):
                with gr.Row(elem_classes=["nd-example-grid"]):
                    for example in EXAMPLE_CARDS[row_start : row_start + 4]:
                        with gr.Column(elem_classes=["nd-example-card"]):
                            gr.HTML(
                                _example_card_html(
                                    str(example["title"]),
                                    int(example["distress"]),
                                    str(example["text"]),
                                )
                            )
                            use_example = gr.Button(
                                "Use example",
                                size="sm",
                                elem_classes=["nd-example-btn"],
                            )
                            use_example.click(
                                fn=lambda text=str(example["text"]), distress=int(example["distress"]): (
                                    _select_example(text, distress)
                                ),
                                inputs=[],
                                outputs=[file_input, notes_input, distress_slider],
                                queue=False,
                            )

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
