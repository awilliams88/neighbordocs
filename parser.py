# Module responsible for diary text file parsing and model output parsing.
# Extracts raw text from inputs and parses structured response blocks.

from __future__ import annotations

from pathlib import Path
from config import SUPPORTED_SUFFIXES


def extract_journal_text(file_path: str | None) -> str:
    """Reads journal entry from a text or markdown file, catching any disk or format errors."""
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


def parse_sections(response: str) -> tuple[str, str, str, str]:
    """Extracts CBT elements from the model's structured text response using section markers."""
    sentiment = "- Emotions not resolved."
    areas = "- Life areas not resolved."
    distortions = "- Distortions not resolved."
    reflection = "How are you feeling about these thoughts today?"

    try:
        # Split output using defined section blocks
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
        # Ignore split errors and keep default messages
        pass

    return sentiment, areas, distortions, reflection
