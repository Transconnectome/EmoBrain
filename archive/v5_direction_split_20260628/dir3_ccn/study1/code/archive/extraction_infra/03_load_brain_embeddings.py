"""
Step 3: Load Brain-JEPA embeddings for all 5 subjects into a single numpy array.

Input:  /pscratch/sd/s/sjmoon/Horikawa_embedding/extract_embedding/jepa/jepa-ep300/embeddings/all/
        sub-{01..05}_stimulus_{1..2196}/frame0.pt   → torch.Tensor shape (768,)

Output: /pscratch/sd/s/sjmoon/EmoFM/brain_embeddings/brain_jepa_embeddings.npy
        shape: (5, 2196, 768)
        axis 0: subject index (0=sub-01, ..., 4=sub-05)
        axis 1: stimulus index (0=stimulus_1, ..., 2195=stimulus_2196)
        axis 2: embedding dim
"""

import numpy as np
import torch
from pathlib import Path

EMBED_DIR  = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/extract_embedding/jepa/jepa-ep300/embeddings/all")
OUTPUT_DIR = Path("/pscratch/sd/s/sjmoon/EmoFM/brain_embeddings")
OUTPUT_FILE = OUTPUT_DIR / "brain_jepa_embeddings.npy"
OUTPUT_DIR.mkdir(exist_ok=True)

SUBJECTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]
N_STIM   = 2196
EMBED_DIM = 768

embeddings = np.zeros((len(SUBJECTS), N_STIM, EMBED_DIM), dtype=np.float32)

for si, sub in enumerate(SUBJECTS):
    n_missing = 0
    for stim_idx in range(N_STIM):
        stim_num = stim_idx + 1   # stimulus_1 .. stimulus_2196
        pt_path  = EMBED_DIR / f"{sub}_stimulus_{stim_num}" / "frame0.pt"
        if not pt_path.exists():
            n_missing += 1
            continue
        emb = torch.load(pt_path, map_location="cpu", weights_only=True)
        embeddings[si, stim_idx] = emb.float().numpy()

    n_loaded = N_STIM - n_missing
    print(f"{sub}: loaded {n_loaded}/{N_STIM}  (missing={n_missing})")

np.save(OUTPUT_FILE, embeddings)
print(f"\nSaved: {OUTPUT_FILE}")
print(f"Shape: {embeddings.shape}")
print(f"Non-zero rows per subject: {[int(np.sum(np.any(embeddings[s] != 0, axis=1))) for s in range(5)]}")
