"""
Module containing keyword-based fallback heuristics.
Analyzes text patterns to extract mood, areas of concern, distortions, and questions.
"""

from __future__ import annotations


def build_sentiment_fallback(text: str) -> str:
    """Detects simple emotion keywords to build a fallback mood classification."""
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


def build_areas_fallback(text: str) -> str:
    """Maps daily concerns to specific life areas based on vocabulary patterns."""
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


def build_distortions_fallback(text: str) -> str:
    """Detects common cognitive distortions by analyzing linguistic patterns (should, catastrophizing, etc.)."""
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


def build_reflection_fallback(text: str) -> str:
    """Generates a simple, comforting CBT reflection question matching dominant keywords."""
    lowered = text.lower()

    if "work" in lowered or "job" in lowered:
        return "What would a small, manageable step towards easing this work pressure look like today?"
    if "always" in lowered or "never" in lowered:
        return "You mentioned things 'always' or 'never' going this way. Can you think of a single exception?"

    return "What is one kind thing you can say to yourself about these thoughts today?"
