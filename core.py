"""
InnerSpace Core API Facade.
Provides a unified entry point for Gradio UI interactions.

This file serves as a facade to maintain backward compatibility while delegating
responsibilities to specialized modules according to SOLID principles:
- `inference.py` handles model lazy-loading, caching, and inference.
- `parser.py` handles file text extraction and output segment splitting.
- `heuristics.py` handles keyword-based offline backup interpretations.
- `analyzer.py` handles prompt formatting and orchestrates the pipeline.
"""

from __future__ import annotations

# Re-export key analytical components to maintain interface contracts
from analyzer import (
    JournalReport,
    analyze_journal,
    analyze_journal_ui,
)

__all__ = [
    "JournalReport",
    "analyze_journal",
    "analyze_journal_ui",
]
