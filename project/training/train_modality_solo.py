"""B2 baseline. Single-modality ridge to 34D emotion (NO LLM, NO fusion).

Implementation of `docs/notes/implementation_spec_20260702.md` §7-2.

Runs a per-modality ridge (brain / video / caption) to the 34D z-space label,
using the SAME split, label normalization (log1p_z default), and metrics as B1.

Purpose. VA-binary work showed video dominates brain (probe AUROC 0.97 vs
0.72). Does that dominance persist for the 34D task? If video-only >> brain-only
here too, it justifies the framework's video-leakage safeguards (Track B
distillation so the student never sees raw video).

Sample alignment. Brain is subject-specific (5 per stimulus). Video / caption
are stimulus-level (1 per stimulus). To compare on the SAME pooled sample grid
(8740 train / 1100 test), the stimulus-level embedding is replicated across the
5 subjects. This keeps the metric denominator identical across modalities.

Output.
    project/shared/results/baseline/b2_modality_solo.json

Run.
    bash project/scripts/train_modality_solo.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from project.data.fmri_adapter import FmriAdapter, SUBJECTS
from project.data.labels import Cowen34Normalizer
from project.evaluation.metrics import compute_metrics

DATA_DIR = REPO_ROOT / "project" / "shared" / "data"
LABELS_CSV = DATA_DIR / "cowen_horikawa_labels.csv"
SPLIT_CSV = DATA_DIR / "horikawa_split.csv"
NORM = DATA_DIR / "norm_stats" / "cowen34_train.pt"
FEAT_DIR = DATA_DIR / "stimulus_features"
OUT_DIR = REPO_ROOT / "project" / "shared" / "results" / "baseline"

SCORE_COLS = [f"score_{k}" for k in range(34)]
ALPHAS = [1.0, 10.0, 100.0, 1000.0, 10000.0]

# stimulus-level embeddings. row index = stim_idx (0-based) = stim_num - 1.
MODALITIES = {
    "video_vjepa2": "vjepa2_pretrained.npy",
    "video_clip": "clip_pretrained.npy",
    "caption": "caption_embed.npy",
}


def split_stims():
    split = pd.read_csv(SPLIT_CSV)
    out = {}
    for sp in ("train", "val", "test"):
        # (subject, stim) sample list, pooled order = subject-major then stim
        rows = split[split["split"] == sp]
        samples = [(r["subject"], int(r["stimulus_num"])) for _, r in rows.iterrows()]
        out[sp] = samples
    return out


def labels_for(samples, norm, labels_df):
    raw = np.stack([labels_df.loc[sn, SCORE_COLS].values.astype(np.float64) for _, sn in samples], 0)
    return norm.transform(raw).numpy()


def brain_features(samples, adapter):
    return np.stack([adapter.get(subj, sn, "mean").numpy() for subj, sn in samples], 0).astype(np.float64)


def stim_features(samples, emb):
    # emb row = stim_idx = stim_num - 1. Replicate per (subject, stim) sample.
    return np.stack([emb[sn - 1] for _, sn in samples], 0).astype(np.float64)


def tune_fit_eval(Xtr, Ytr, Xva, Yva, Xte, Yte, rare_idx, norm):
    best_alpha, best_val = None, -np.inf
    for a in ALPHAS:
        m = Ridge(alpha=a).fit(Xtr, Ytr)
        v = compute_metrics(m.predict(Xva), Yva, which=["profile"])["profile"]["pearson_mean"]
        if v > best_val:
            best_val, best_alpha = v, a
    model = Ridge(alpha=best_alpha).fit(Xtr, Ytr)
    pred = model.predict(Xte)
    m = compute_metrics(pred, Yte, rare_idx=rare_idx, normalizer=norm)
    return best_alpha, m


def rare_idx():
    labels = pd.read_csv(LABELS_CSV)
    marginal = labels[SCORE_COLS].mean(axis=0).values
    return list(np.argsort(marginal)[:10])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    adapter = FmriAdapter()
    norm = Cowen34Normalizer.load(NORM)
    labels_df = pd.read_csv(LABELS_CSV).set_index("stim_num_int")
    stims = split_stims()
    ri = rare_idx()

    Y = {sp: labels_for(stims[sp], norm, labels_df) for sp in ("train", "val", "test")}

    results = {}

    # brain-only (= B1, recomputed here for a same-run comparison)
    Xb = {sp: brain_features(stims[sp], adapter) for sp in ("train", "val", "test")}
    a, m = tune_fit_eval(Xb["train"], Y["train"], Xb["val"], Y["val"], Xb["test"], Y["test"], ri, norm)
    results["brain_roi_mean"] = {"alpha": a, "metrics": m}
    print(f"[brain]  profile={m['profile']['pearson_mean']:+.4f} rsa={m['rsa']['rsa_pearson']:+.4f} p@1={m['sparse']['precision@1']:.3f}")

    # stimulus-level modalities
    for name, fname in MODALITIES.items():
        emb = np.load(FEAT_DIR / fname)
        Xf = {sp: stim_features(stims[sp], emb) for sp in ("train", "val", "test")}
        a, m = tune_fit_eval(Xf["train"], Y["train"], Xf["val"], Y["val"], Xf["test"], Y["test"], ri, norm)
        results[name] = {"alpha": a, "metrics": m, "dim": int(emb.shape[1])}
        print(f"[{name}]  profile={m['profile']['pearson_mean']:+.4f} rsa={m['rsa']['rsa_pearson']:+.4f} p@1={m['sparse']['precision@1']:.3f}")

    (OUT_DIR / "b2_modality_solo.json").write_text(json.dumps(results, indent=2))

    print("\n" + "=" * 72)
    print("B2 MODALITY SOLO — TEST (profile pearson / CCC / rsa / sparse p@1)")
    print("=" * 72)
    for name, r in results.items():
        m = r["metrics"]
        print(f"  {name:16s}  pearson={m['profile']['pearson_mean']:+.4f}  "
              f"CCC={m['profile']['ccc_mean']:+.4f}  "
              f"rsa={m['rsa']['rsa_pearson']:+.4f}  p@1={m['sparse']['precision@1']:.3f}")
    print(f"\n[save] {OUT_DIR / 'b2_modality_solo.json'}")


if __name__ == "__main__":
    main()
