"""
Module responsible for orchestrating the overall journal entry analysis.
Brings together inference, file extraction, response parsing, and heuristic fallbacks.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Any

# Dynamic import fallback for ZeroGPU runtime environment compatibility
try:
    import spaces  # type: ignore
except ImportError:

    class _LocalSpacesFallback:
        @staticmethod
        def GPU(
            duration: int = 30,
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
                return function

            return decorator

    spaces = _LocalSpacesFallback()

from config import ENTRY_LIMIT, MODEL_ID, PARAMETER_COUNT
from inference import run_model_inference, run_chat_inference
from parser import extract_journal_text, parse_sections


@dataclass(frozen=True)
class JournalReport:
    """Structure containing the raw entry, execution context, and parsed reflection results."""

    entry_text: str
    model_path: str
    sentiment: str
    areas: str
    distortions: str
    reflection: str


def build_journal_prompt(entry: str) -> str:
    """Builds prompt instructing the model to parse thoughts and reflect CBT style."""
    return f"""You are a gentle and insightful cognitive reflection coach. Analyze the following private journal entry and provide structured feedback. Your response must contain four sections separated by '=== SECTION ===' markers:

=== EMOTIONS ===
- [Identify 1-3 dominant emotions found in the text]

=== LIFE AREAS ===
- [List 1-2 affected life areas, e.g. Work, Relationships, Health]

=== COGNITIVE DISTORTIONS ===
- [List any distortions such as Catastrophizing, All-or-Nothing thinking, or write 'None detected' if none found]

=== REFLECTION ===
[Provide a gentle, open-ended question to help the writer reflect deeper on their thoughts.]

Journal entry:
"{entry}" """


def analyze_journal(file_path: str | None, raw_text: str) -> JournalReport:
    """Orchestrates text extraction, model inference, and output parsing with backup fallbacks."""
    entry_text = ""
    if file_path:
        entry_text = extract_journal_text(file_path)
    if not entry_text:
        entry_text = raw_text.strip()

    # Handle empty submissions gracefully
    if not entry_text:
        return JournalReport(
            entry_text="",
            model_path="No entry provided.",
            sentiment="- Please write something first.",
            areas="- None",
            distortions="- None",
            reflection="I'm here to listen whenever you're ready to share.",
        )

    # Respect the length limits
    trimmed_entry = entry_text[:ENTRY_LIMIT]

    # Generate prompt and run inference via inference engine
    prompt = build_journal_prompt(trimmed_entry)
    response, log_details = run_model_inference(prompt)

    model_path = "\n".join(
        [
            f"Primary model: {MODEL_ID}",
            f"Parameters: {PARAMETER_COUNT}",
            "Execution flow: local GPU (ZeroGPU Space) with serverless fallback",
            "---",
            log_details,
        ]
    )

    # Route output parsing: split sections if model succeeded, otherwise return error strings
    if response.strip():
        sentiment, areas, distortions, reflection = parse_sections(response)
    else:
        sentiment = "- Analysis unavailable"
        areas = "- Analysis unavailable"
        distortions = "- Analysis unavailable"
        reflection = "An error occurred during model analysis. Please check your network connection or Hugging Face access token."

    return JournalReport(
        entry_text=trimmed_entry,
        model_path=model_path,
        sentiment=sentiment,
        areas=areas,
        distortions=distortions,
        reflection=reflection,
    )


@spaces.GPU(duration=30)
def analyze_journal_ui(
    file_path: str | None,
    raw_text: str,
) -> tuple[str, str, str, str, str, list[dict[str, str]], str]:
    """Gradio-compatible entry point decorated for Hugging Face ZeroGPU compatibility."""
    report = analyze_journal(file_path, raw_text)
    return (
        report.entry_text,
        report.model_path,
        report.sentiment,
        report.areas,
        report.distortions,
        [{"role": "assistant", "content": report.reflection}],
        report.entry_text,
    )


@spaces.GPU(duration=30)
def chat_respond_ui(
    history: list[dict[str, str]] | None,
    user_message: str,
    journal_context: str,
) -> tuple[list[dict[str, str]], str, str]:
    """Gradio-compatible chat handler decorated for Hugging Face ZeroGPU compatibility.

    Returns:
        tuple containing:
        - updated history list of dicts
        - cleared user message textbox string ("")
        - updated system logs string
    """
    updated_history = list(history) if history else []
    if not user_message.strip():
        return updated_history, "", "Empty user message. No inference run."

    # Append user message to history
    updated_history.append({"role": "user", "content": user_message})

    # Build system prompt with context
    if journal_context.strip():
        system_prompt = (
            "You are a gentle and insightful cognitive reflection coach. "
            "Help the user explore their thoughts using Cognitive Behavioral Therapy (CBT) techniques. "
            "Keep your replies warm, empathetic, and supportive. Ask gentle, open-ended questions. "
            "Here is the context of their daily journal entry to help guide the conversation:\n"
            f'"{journal_context.strip()}"'
        )
    else:
        system_prompt = (
            "You are a gentle and insightful cognitive reflection coach. "
            "Help the user explore their thoughts using Cognitive Behavioral Therapy (CBT) techniques. "
            "Keep your replies warm, empathetic, and supportive. Ask gentle, open-ended questions."
        )

    response, log_details = run_chat_inference(updated_history, system_prompt)

    # Append coach reply to history
    updated_history.append({"role": "assistant", "content": response})

    # Prepare logs
    model_logs = "\n".join(
        [
            "Chat Session active.",
            "Execution flow: local GPU (ZeroGPU Space) with serverless fallback",
            "---",
            log_details,
        ]
    )

    return updated_history, "", model_logs
