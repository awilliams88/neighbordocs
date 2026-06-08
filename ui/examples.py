from __future__ import annotations

from html import escape
import gradio as gr

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


def render_examples(
    file_input: gr.File, notes_input: gr.Textbox, distress_slider: gr.Slider
) -> gr.Column:
    """Renders the examples section and sets up click handlers."""
    with gr.Column(elem_classes=["nd-examples-section"]) as section:
        gr.Markdown("## Try a Scenario 🎲")
        with gr.Row(elem_classes=["nd-example-grid"]):
            for example in EXAMPLE_CARDS:
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
    return section
