"""Prompt assembly. Fixed Question field for Track A (implementation_spec 8-3).

The Question is a fixed instruction, identical for every stimulus, so it is not
a learning shortcut. The shortcut risk is the variable caption, which is a
separate field and teacher-only. Caption is never merged into the Question.

    student prompt = brain tokens + Question field.
    teacher prompt = video tokens + Caption field + brain tokens + Question field.

This module provides only the Question text (Track A / student). Caption field
and full teacher sequence assembly come with the teacher (Step 6).
"""
from __future__ import annotations

from pathlib import Path

_ORDER = Path(__file__).resolve().parents[1] / "shared/data/cowen34_order.txt"


def emotion_names() -> list[str]:
    """34 Cowen-Keltner emotion names in canonical order."""
    return [ln.strip() for ln in _ORDER.read_text().splitlines() if ln.strip()]


def track_a_question() -> str:
    """Fixed Question field (implementation_spec 8-3), full 34-emotion list."""
    names = ", ".join(emotion_names())
    return (
        "Question 1: You are an affective neuroscientist. You are analyzing a "
        "subject's fMRI response evoked while watching a video. Analyze the "
        "response and identify which emotions it reflects.\n"
        "Question 2: Based on the above, give a score from 0 to 1 for each of "
        f"the 34 emotion categories ({names})."
    )


TRACK_A_QUESTION = track_a_question()
