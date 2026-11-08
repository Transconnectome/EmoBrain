"""Build semantic embeddings for the 34 Cowen-Keltner emotion names.

These become the INITIALISATION of the decoder's label queries. They must live in
the same space as the caption embeddings so that a query and a caption token are
comparable: EmoViS built `caption_embed.npy` with sentence-transformers
all-mpnet-base-v2, so we reproduce that encoder's pipeline exactly (mean-pool over
tokens with the attention mask, then L2-normalise) using plain transformers, since
sentence_transformers is not installed in this env.

Why this file matters. The whole held-out-emotion test rests on the queries being
SEMANTIC: an emotion the model never trained on is decoded by instantiating its
name embedding as a query. Random-init queries cannot do that by construction.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/build_emotion_query_embeddings.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

ENCODER = "sentence-transformers/all-mpnet-base-v2"   # same encoder as caption_embed.npy
ORDER = REPO_ROOT / "project" / "shared" / "data" / "cowen34_order.txt"
OUT_DIR = REPO_ROOT / "project" / "shared" / "data" / "emotion_query"
OUT_NPY = OUT_DIR / "emotion_query_mpnet.npy"
OUT_JSON = OUT_DIR / "emotion_query_mpnet.json"


def sbert_embed(texts, tok, mdl):
    """all-mpnet-base-v2 sentence embedding: mean pooling + L2 normalise."""
    batch = tok(list(texts), padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        hidden = mdl(**batch).last_hidden_state
    mask = batch["attention_mask"].unsqueeze(-1).float()
    pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
    return torch.nn.functional.normalize(pooled, p=2, dim=1)


def main():
    from transformers import AutoModel, AutoTokenizer

    names = [l.strip() for l in ORDER.read_text().splitlines() if l.strip()]
    assert len(names) == 34, f"expected 34 emotions, got {len(names)}"

    tok = AutoTokenizer.from_pretrained(ENCODER)
    mdl = AutoModel.from_pretrained(ENCODER).eval()
    emb = sbert_embed(names, tok, mdl).numpy().astype(np.float32)
    assert emb.shape == (34, mdl.config.hidden_size)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    np.save(OUT_NPY, emb)

    # Semantic neighbour structure, saved as provenance and used to build the
    # semantic-interpolation control baseline in the held-out-emotion test.
    sim = emb @ emb.T
    off = sim.copy()
    np.fill_diagonal(off, -9.0)
    neighbours = {names[i]: [names[j], float(sim[i, j])]
                  for i, j in enumerate(off.argmax(1))}

    OUT_JSON.write_text(json.dumps({
        "encoder": ENCODER,
        "pooling": "mean over tokens with attention mask, then L2 normalise",
        "note": "same encoder/pipeline as project/shared/data/stimulus_features/caption_embed.npy",
        "order_file": str(ORDER.relative_to(REPO_ROOT)),
        "emotions": names,
        "shape": list(emb.shape),
        "nearest_neighbour": neighbours,
    }, indent=2))

    print(f"[emotion-query] {emb.shape} -> {OUT_NPY}")
    for e in ("fear", "joy", "disgust", "nostalgia", "awe"):
        n, s = neighbours[e]
        print(f"  {e:24s} nearest: {n} ({s:.3f})")


if __name__ == "__main__":
    main()
