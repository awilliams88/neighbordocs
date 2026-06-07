from __future__ import annotations

from pathlib import Path
import re
from env.config import SUPPORTED_SUFFIXES


# Match explicit report markers even when the model emits them inline.
_EXPLICIT_MARKER_PATTERN = re.compile(
    r"(?i)(={2,}[ \t]*"
    r"(?:dominant emotions?|emotions?|"
    r"affected life areas?|life areas?|areas|"
    r"cognitive distortions?|distortions?|"
    r"balanced reframe|cognitive reframe|reframe|"
    r"tiny next steps?|small next steps?|next steps?|"
    r"reflection)"
    r"[ \t]*={2,})"
)

# Match the section heading variants the local model commonly emits.
_SECTION_MARKER_PATTERN = re.compile(
    r"(?im)^[ \t]*(?:[-*][ \t]*)?(?:#{1,6}[ \t]*)?"
    r"(?:\*\*)?(?:={2,}[ \t]*)?"
    r"(?P<label>"
    r"dominant emotions?|emotions?|"
    r"affected life areas?|life areas?|areas|"
    r"cognitive distortions?|distortions?|"
    r"balanced reframe|cognitive reframe|reframe|"
    r"tiny next steps?|small next steps?|next steps?|"
    r"reflection"
    r")"
    r"\b"
    r"(?:[ \t]*={2,})?(?:\*\*)?[ \t]*(?::|-)?[ \t]*"
    r"(?P<trailing>[^\n]*)$"
)

# Fixed output order expected by the analysis cards.
_SECTION_ORDER = (
    "emotions",
    "areas",
    "distortions",
    "reframe",
    "next_step",
    "reflection",
)

# Defaults keep the UI stable when a section is genuinely absent.
_SECTION_DEFAULTS = {
    "emotions": "- Emotions not resolved.",
    "areas": "- Life areas not resolved.",
    "distortions": "- Distortions not resolved.",
    "reframe": "- Balanced reframe not resolved.",
    "next_step": "- Tiny next step not resolved.",
    "reflection": "How are you feeling about these thoughts today?",
}


def _resolve_file_path(file_input: object) -> Path | None:
    """Normalizes Gradio file payload variants into a local path."""
    # Empty or cleared file components should let the textbox drive analysis.
    if not file_input:
        return None

    # Gradio may return a single-item list when file mode changes.
    if isinstance(file_input, (list, tuple)):
        for item in file_input:
            path = _resolve_file_path(item)
            if path:
                return path
        return None

    # Newer Gradio payloads can be dictionaries with path-like fields.
    if isinstance(file_input, dict):
        for key in ("path", "name", "orig_name"):
            value = file_input.get(key)
            if value:
                return Path(str(value))
        return None

    # Local runs usually pass a string path from the upload component.
    return Path(str(file_input))


def extract_journal_text(file_path: object | None) -> str:
    """Reads journal entry from a text or markdown file, catching any disk or format errors."""
    # Empty file inputs fall back to the text box.
    path = _resolve_file_path(file_path)
    if not path:
        return ""
    try:
        # Accept only the supported private text formats.
        suffix = path.suffix.lower()
        if suffix in SUPPORTED_SUFFIXES:
            return path.read_text(encoding="utf-8", errors="ignore").strip()
        return f"Unsupported file: {suffix}. Try a text or markdown file."
    except Exception as e:
        return f"Error reading diary file: {e}"


def _canonical_section(label: str) -> str:
    """Maps a model heading variant onto the app's fixed output slots."""
    normalized = re.sub(r"[^a-z]+", " ", label.lower()).strip()
    if "emotion" in normalized:
        return "emotions"
    if "life area" in normalized or normalized == "areas":
        return "areas"
    if "distortion" in normalized:
        return "distortions"
    if "reframe" in normalized:
        return "reframe"
    if "next step" in normalized:
        return "next_step"
    return "reflection"


def _normalize_report_markers(response: str) -> str:
    """Places explicit section markers on their own lines before parsing."""
    return _EXPLICIT_MARKER_PATTERN.sub(r"\n\1\n", response)


def _clean_section_value(value: str) -> str:
    """Removes empty lines and leftover bracket-only prompt placeholders."""
    cleaned = value.strip()
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if lines and all(
        re.fullmatch(r"(?:[-*][ \t]*)?\[[^\]]+\]\.?", line) for line in lines
    ):
        return ""
    return cleaned


def parse_sections(response: str) -> tuple[str, str, str, str, str, str]:
    """Extracts CBT elements from the model's structured text response using section markers."""
    # Normalize explicit markers so merged sections still split cleanly.
    response = _normalize_report_markers(response)

    # Find candidate headings before assigning text to output cards.
    matches = list(_SECTION_MARKER_PATTERN.finditer(response))
    sections = dict(_SECTION_DEFAULTS)

    # If no section markers are found, return the default values.
    if not matches:
        return (
            sections["emotions"],
            sections["areas"],
            sections["distortions"],
            sections["reframe"],
            sections["next_step"],
            sections["reflection"],
        )

    # Attempt to find a single contiguous block of ordered sections.
    best_values: dict[str, str] = {}
    best_count = -1

    # Iterate through all matches as possible starting points.
    for start_index, match in enumerate(matches):
        values: dict[str, str] = {}
        last_order_index = -1

        # Check each subsequent match for ascending order.
        for current_index in range(start_index, len(matches)):
            current = matches[current_index]
            section = _canonical_section(current.group("label"))
            section_order_index = _SECTION_ORDER.index(section)

            # Stop if sections are out of order.
            if section_order_index <= last_order_index:
                break

            # Capture heading text plus content until the next heading.
            next_start = (
                matches[current_index + 1].start()
                if current_index + 1 < len(matches)
                else len(response)
            )

            # Clean up heading and capture section value.
            value = _clean_section_value(
                "\n".join(
                    [current.group("trailing"), response[current.end() : next_start]]
                )
            )

            # Store the value if it's not empty.
            if value:
                values[section] = value
            last_order_index = section_order_index

            # Stop if we've found a complete-looking ordered section block.
            if len(values) == len(_SECTION_ORDER):
                break

        # Prefer the last complete-looking ordered section block.
        if len(values) >= best_count:
            best_values = values
            best_count = len(values)

    # Assign extracted sections to the default dictionary.
    for section, value in best_values.items():
        sections[section] = value

    # Return extracted sections in the expected order.
    return (
        sections["emotions"],
        sections["areas"],
        sections["distortions"],
        sections["reframe"],
        sections["next_step"],
        sections["reflection"],
    )
