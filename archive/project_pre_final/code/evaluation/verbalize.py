"""alpha layer. Verbalize a 34D emotion prediction as a sentence.

This is a CONVENIENCE, not a decoder and not a contribution. The 34D regression
is the result; this only re-expresses those 34 numbers as readable text for
inspection, demos and slides. It adds no information and must never be framed as
"natural-language decoding" (that would be the beta / EmoMind path, deliberately
not taken here). Pure post-processing, no training.

Pipeline. z-space prediction -> inverse_transform (expm1) -> raw crowd proportion
-> pick the emotions above a threshold, ordered by strength -> template. Emotion
co-occurrence (bittersweet) is preserved: several emotions can be named together.

Usage.
    from project.code.evaluation.verbalize import verbalize
    verbalize(pred_z[i], normalizer)   # -> "This clip most strongly evokes ..."
"""

from __future__ import annotations

import numpy as np
import torch

from project.code.fusion.prompt import emotion_order

_NAMES = emotion_order()


def _to_raw(pred_z, normalizer):
    z = pred_z if isinstance(pred_z, torch.Tensor) else torch.as_tensor(pred_z)
    raw = normalizer.inverse_transform(z.float().reshape(1, -1)).reshape(-1)
    return raw.clamp_min(0).cpu().numpy()               # crowd proportion >= 0


def verbalize(pred_z, normalizer, top_k: int = 3, floor: float = 0.05) -> str:
    """One clip's 34D prediction -> a sentence naming its strongest emotions."""
    raw = _to_raw(pred_z, normalizer)
    order = np.argsort(raw)[::-1]
    picked = [(int(i), float(raw[i])) for i in order[:top_k] if raw[i] >= floor]
    if not picked:
        return "This clip does not evoke any emotion strongly."
    names = [_NAMES[i] for i, _ in picked]
    if len(names) == 1:
        return f"This clip most strongly evokes {names[0]}."
    head, rest = names[0], names[1:]
    tail = rest[0] if len(rest) == 1 else ", ".join(rest[:-1]) + f" and {rest[-1]}"
    return f"This clip most strongly evokes {head}, with notable {tail}."


def verbalize_batch(pred_z, normalizer, **kw) -> list[str]:
    P = pred_z if isinstance(pred_z, torch.Tensor) else torch.as_tensor(pred_z)
    return [verbalize(P[i], normalizer, **kw) for i in range(P.shape[0])]
