from __future__ import annotations

from pathlib import Path
from env.config import SUPPORTED_SUFFIXES


def extract_journal_text(file_path: str | None) -> str:
    """Reads journal entry from a text or markdown file, catching any disk or format errors."""
    # Empty file inputs fall back to the text box.
    if not file_path:
        return ""
    try:
        # Accept only the supported private text formats.
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix in SUPPORTED_SUFFIXES:
            return path.read_text(encoding="utf-8", errors="ignore").strip()
        return f"Unsupported file: {suffix}. Try a text or markdown file."
    except Exception as e:
        return f"Error reading diary file: {e}"


def parse_sections(response: str) -> tuple[str, str, str, str, str, str]:
    """Extracts CBT elements from the model's structured text response using section markers."""
    # Defaults keep the UI usable if parsing is incomplete.
    sentiment = "- Emotions not resolved."
    areas = "- Life areas not resolved."
    distortions = "- Distortions not resolved."
    reframe = "- Balanced reframe not resolved."
    next_step = "- Tiny next step not resolved."
    reflection = "How are you feeling about these thoughts today?"

    try:
        # Split the generated text by the required section markers.
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
                    parts4 = rest.split("=== BALANCED REFRAME ===")
                    if len(parts4) > 1:
                        distortions = parts4[0].strip()
                        rest = parts4[1]
                        parts5 = rest.split("=== TINY NEXT STEP ===")
                        if len(parts5) > 1:
                            reframe = parts5[0].strip()
                            rest = parts5[1]
                            parts6 = rest.split("=== REFLECTION ===")
                            if len(parts6) > 1:
                                next_step = parts6[0].strip()
                                reflection = parts6[1].strip()
                            else:
                                next_step = rest.strip()
                    else:
                        old_parts = rest.split("=== REFLECTION ===")
                        if len(old_parts) > 1:
                            distortions = old_parts[0].strip()
                            reflection = old_parts[1].strip()
                        else:
                            distortions = rest.strip()
    except Exception:
        # Keep defaults if the model output cannot be split.
        pass

    return sentiment, areas, distortions, reframe, next_step, reflection
