from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

# Load environment variables on import
import runtime  # noqa: F401
from config import (  # noqa: E402
    ENTRY_LIMIT,
    MODEL_ID,
    PARAMETER_COUNT,
    SUPPORTED_SUFFIXES,
)

# Global variables for model caching
_tokenizer: Any = None
_model: Any = None


@dataclass(frozen=True)
class JournalReport:
    """Dataclass holding structured journaling reflections and coach responses."""

    entry_text: str
    model_path: str
    sentiment: str
    areas: str
    distortions: str
    reflection: str


# ZeroGPU compatibility helper: uses spaces.GPU if available, else a local fallback
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


def get_model_and_tokenizer() -> tuple[Any, Any]:
    """Loads and returns the tokenizer and model from HF lazily."""
    global _model, _tokenizer
    if _model is None:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        print(f"Loading tokenizer for {MODEL_ID}...")
        _tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID,
            token=os.environ.get("HF_TOKEN"),
        )
        print(f"Loading model {MODEL_ID}...")
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            low_cpu_mem_usage=True,
            token=os.environ.get("HF_TOKEN"),
        )
        # Move model to CUDA if available eagerly
        if torch.cuda.is_available():
            print("Moving model to CUDA device...")
            _model = _model.to("cuda")
    return _model, _tokenizer


def run_model_inference(prompt: str) -> tuple[str, str]:
    """Orchestrates model inference using local CPU/GPU first, and falls back to Serverless API on failure."""
    log_lines: list[str] = []
    try:
        log_lines.append("Initializing local model execution...")
        model, tokenizer = get_model_and_tokenizer()
        device = str(model.device)
        log_lines.append(f"Running local model execution on device: {device}...")

        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(device)

        print("Generating response...")
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response: str = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]
        log_lines.append("Local model execution completed successfully.")
        return response, "\n".join(log_lines)
    except Exception as e:
        import traceback

        traceback.print_exc()
        log_lines.append(
            f"Local model execution failed: {e}. Falling back to serverless API..."
        )

    # Serverless API Fallback path
    log_lines.append(
        f"Initiating Hugging Face Serverless Inference API ({MODEL_ID})..."
    )
    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(MODEL_ID, token=os.environ.get("HF_TOKEN"))
        messages = [{"role": "user", "content": prompt}]
        completion = client.chat_completion(messages=messages, max_tokens=512)
        response = completion.choices[0].message.content or ""
        log_lines.append("Serverless API execution completed successfully.")
        return response, "\n".join(log_lines)
    except Exception as e:
        log_lines.append(f"Serverless API execution failed: {e}.")
        log_lines.append("Falling back to local CPU heuristics...")
        return "", "\n".join(log_lines)


def extract_journal_text(file_path: str | None) -> str:
    """Reads journal entry from a text or markdown file."""
    if not file_path:
        return ""
    try:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix in SUPPORTED_SUFFIXES:
            return path.read_text(encoding="utf-8", errors="ignore").strip()
        return f"Unsupported file: {suffix}. Try a text or markdown file."
    except Exception as e:
        return f"Error reading diary file: {e}"


def analyze_journal(file_path: str | None, raw_text: str) -> JournalReport:
    """Extracts sentiment, tags life areas, detects cognitive distortions, and runs CBT coaching."""
    entry_text = ""
    if file_path:
        entry_text = extract_journal_text(file_path)
    if not entry_text:
        entry_text = raw_text.strip()

    if not entry_text:
        return JournalReport(
            entry_text="",
            model_path="No entry provided.",
            sentiment="- Please write something first.",
            areas="- None",
            distortions="- None",
            reflection="I'm here to listen whenever you're ready to share.",
        )

    trimmed_entry = entry_text[:ENTRY_LIMIT]

    # Run inference
    prompt = _build_journal_prompt(trimmed_entry)
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

    # Parse sections or use fallbacks
    if response.strip():
        sentiment, areas, distortions, reflection = _parse_sections(response)
    else:
        sentiment = _build_sentiment_fallback(trimmed_entry)
        areas = _build_areas_fallback(trimmed_entry)
        distortions = _build_distortions_fallback(trimmed_entry)
        reflection = _build_reflection_fallback(trimmed_entry)

    return JournalReport(
        entry_text=trimmed_entry,
        model_path=model_path,
        sentiment=sentiment,
        areas=areas,
        distortions=distortions,
        reflection=reflection,
    )


def _build_journal_prompt(entry: str) -> str:
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


def _parse_sections(response: str) -> tuple[str, str, str, str]:
    """Parses model response containing CBT sections."""
    sentiment = "- Emotions not resolved."
    areas = "- Life areas not resolved."
    distortions = "- Distortions not resolved."
    reflection = "How are you feeling about these thoughts today?"

    try:
        parts = response.split("=== EMOTIONS ===")
        if len(parts) > 1:
            rest = parts[1]
            parts2 = rest.split("=== LIFE AREAS ===")
            if len(parts2) > 1:
                sentiment = parts2[0].strip()
                rest = parts2[1]
                parts3 = rest.split("=== COGNITIVE DISTORTIONS ===")
                if len(parts3) > 1:
                    areas = parts3[0].strip()
                    rest = parts3[1]
                    parts4 = rest.split("=== REFLECTION ===")
                    if len(parts4) > 1:
                        distortions = parts4[0].strip()
                        reflection = parts4[1].strip()
                    else:
                        distortions = rest.strip()
    except Exception:
        pass

    return sentiment, areas, distortions, reflection


def _build_sentiment_fallback(text: str) -> str:
    """Keyword-based sentiment fallback."""
    lowered = text.lower()
    emotions = []
    if any(w in lowered for w in ["sad", "down", "cry", "hurt", "grief", "lonely"]):
        emotions.append("- Sadness / Loneliness")
    if any(
        w in lowered for w in ["angry", "mad", "annoy", "frustrate", "hate", "irritate"]
    ):
        emotions.append("- Anger / Frustration")
    if any(
        w in lowered
        for w in ["happy", "glad", "great", "excite", "joy", "peace", "love"]
    ):
        emotions.append("- Joy / Contentment")
    if any(
        w in lowered for w in ["anxious", "worry", "afraid", "scare", "fear", "nervous"]
    ):
        emotions.append("- Anxiety / Concern")

    if not emotions:
        return "- Neutral / Reflective mood"
    return "\n".join(emotions)


def _build_areas_fallback(text: str) -> str:
    """Keyword-based life areas fallback."""
    lowered = text.lower()
    areas = []
    if any(w in lowered for w in ["work", "job", "office", "career", "boss", "task"]):
        areas.append("- Career & Work")
    if any(
        w in lowered
        for w in [
            "family",
            "mom",
            "dad",
            "kid",
            "child",
            "wife",
            "husband",
            "friend",
            "relationship",
        ]
    ):
        areas.append("- Relationships & Social")
    if any(
        w in lowered for w in ["health", "sick", "doctor", "gym", "run", "eat", "body"]
    ):
        areas.append("- Health & Wellness")
    if any(w in lowered for w in ["money", "pay", "buy", "budget", "cost", "finances"]):
        areas.append("- Finances")

    if not areas:
        return "- Personal Growth & General Life"
    return "\n".join(areas)


def _build_distortions_fallback(text: str) -> str:
    """Keyword-based cognitive distortions fallback."""
    lowered = text.lower()
    distortions = []
    if any(w in lowered for w in ["always", "never", "nothing", "everything"]):
        distortions.append(
            "- All-or-Nothing Thinking (viewing things in black-and-white)"
        )
    if any(
        w in lowered
        for w in ["ruined", "disaster", "fail", "worst", "end of the world"]
    ):
        distortions.append("- Catastrophizing (expecting the worst outcome)")
    if any(w in lowered for w in ["must", "should", "ought"]):
        distortions.append("- 'Should' Statements (unrealistic self-imposed rules)")

    if not distortions:
        return "- None detected (heuristics analysis)"
    return "\n".join(distortions)


def _build_reflection_fallback(text: str) -> str:
    """Rule-based CBT coach reflection fallback."""
    lowered = text.lower()
    if "work" in lowered or "job" in lowered:
        return "What would a small, manageable step towards easing this work pressure look like today?"
    if "always" in lowered or "never" in lowered:
        return "You mentioned things 'always' or 'never' going this way. Can you think of a single exception?"
    return "What is one kind thing you can say to yourself about these thoughts today?"


@spaces.GPU(duration=30)
def analyze_journal_ui(
    file_path: str | None,
    raw_text: str,
) -> tuple[str, str, str, str, str, str]:
    """Gradio entry point decorated with spaces.GPU for ZeroGPU compliance."""
    report = analyze_journal(file_path, raw_text)
    return (
        report.entry_text,
        report.model_path,
        report.sentiment,
        report.areas,
        report.distortions,
        report.reflection,
    )
