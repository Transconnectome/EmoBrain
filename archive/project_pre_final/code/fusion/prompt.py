"""Prompt fields and token order (spec §6-5, §7.2, §8-3).

Two text fields, kept separate so ablation is possible (spec §14).
    Question field   fixed instruction, identical for every clip, so it can never
                     be a shortcut. Includes the 34-category inventory.
    Caption field    per-clip human-written visual description (teacher only).
                     Affect neutrality is not assumed, so this segment remains
                     independently droppable for shortcut analysis.

Token order (spec §7.2).
    teacher   video, caption, brain, question
    student   brain, question
Vector tokens (brain, video) enter through their projector; text (caption,
question) enters through the tokenizer only, never a projector.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_ORDER = REPO_ROOT / "project" / "shared" / "data" / "cowen34_order.txt"


def emotion_order() -> list[str]:
    return [l.strip() for l in _ORDER.read_text().splitlines() if l.strip()]


def question_text() -> str:
    """The fixed Question field (spec §8-3, verbatim)."""
    inv = ", ".join(emotion_order())
    return (
        "Question 1: You are an affective neuroscientist. You are analyzing a "
        "subject's fMRI response evoked while watching a video. Analyze the "
        "response and identify which emotions it reflects.\n"
        "Question 2: Based on the above, give a score from 0 to 1 for each of the "
        f"34 emotion categories ({inv})."
    )


def caption_field(caption: str) -> str:
    return f"Caption: {caption}"


# segment order given active modalities. "brain"/"video" are vector segments
# (projector), "caption"/"question" are text segments (tokenizer).
def token_order(modalities: dict) -> list[str]:
    if modalities.get("video") or modalities.get("caption"):     # teacher form
        seq = []
        if modalities.get("video"):
            seq.append("video")
        if modalities.get("caption"):
            seq.append("caption")
        seq += ["brain", "question"]
        return seq
    return ["brain", "question"]                                 # student form
