"""
Diagnostic: why does Phase 2 D (CLIP+BJ concat, pooled) = 0.67
when Phase 1 CLIP-alone (linear, stim_level) = 0.98 ?

Tests:
  (a) Phase 2 pipeline + CLIP only (brain zeroed) + pooled       — isolate concat effect
  (b) Phase 2 pipeline + CLIP only (brain zeroed) + stim_level   — isolate pooled effect
  (c) Phase 2 pipeline + CLIP only + stim_level (single stim)    — should ≈ Phase 1 result
  (d) Phase 2 pipeline + CLIP + BJ concat + stim_level           — concat effect with same data structure as Phase 1

Each on V_binary fold 1 only.
"""
import sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/code/dir2_multimodal/legacy_phase2")
from _lib import (load_brain_embeddings, load_video_feature, load_task_labels,
                  get_fold_split, ALL_SUBJECTS,
                  DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD, DEFAULT_VIDEO)


def build_pooled(brain, video, vstim, label_df, split):
    """Each stim × each subj → 1 row. Same as Phase 2 D."""
    s2v = {int(s): i for i, s in enumerate(vstim)}
    rows = []
    for subj, (emb, sarr) in brain.items():
        s2b = {int(s): i for i, s in enumerate(sarr)}
        for _, r in label_df.merge(split, on="stimulus_num", how="inner").iterrows():
            stim, sp, lab = int(r["stimulus_num"]), r["split"], r["label"]
            if stim not in s2b or stim not in s2v: continue
            rows.append((sp, emb[s2b[stim]], video[s2v[stim]], lab))
    return rows


def build_stim_level(video, vstim, label_df, split):
    """1 row per stim. Same as Phase 1 video probe."""
    s2v = {int(s): i for i, s in enumerate(vstim)}
    rows = []
    for _, r in label_df.merge(split, on="stimulus_num", how="inner").iterrows():
        stim, sp, lab = int(r["stimulus_num"]), r["split"], r["label"]
        if stim not in s2v: continue
        rows.append((sp, video[s2v[stim]], lab))
    return rows


def linear_probe(Xtr, ytr, Xva, yva, Xte, yte, name):
    sc = StandardScaler().fit(Xtr)
    Xtr, Xva, Xte = sc.transform(Xtr), sc.transform(Xva), sc.transform(Xte)
    best_val, best_C = -np.inf, None
    for C in [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]:
        clf = LogisticRegression(C=C, max_iter=2000, random_state=0)
        clf.fit(Xtr, ytr)
        prob_v = clf.predict_proba(Xva)[:, 1]
        vs = roc_auc_score(yva, prob_v)
        if vs > best_val:
            best_val, best_C = vs, C
            clf_te = LogisticRegression(C=C, max_iter=2000, random_state=0).fit(Xtr, ytr)
            prob_te = clf_te.predict_proba(Xte)[:, 1]
            test_auroc = roc_auc_score(yte, prob_te)
    print(f"  [{name:50s}] N_tr={Xtr.shape[0]:5d} D={Xtr.shape[1]:5d} "
          f"test_AUROC={test_auroc:.4f} (val={best_val:.4f} C={best_C})")


def main():
    print("=== Phase 2 D diagnostic on V_binary fold 1 ===\n")
    brain = load_brain_embeddings(DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD)
    video, vstim = load_video_feature(DEFAULT_VIDEO)
    label_df, ttype = load_task_labels("V_binary")
    split = get_fold_split(1)

    # ---- pooled rows ----
    pooled = build_pooled(brain, video, vstim, label_df, split)
    tr = [r for r in pooled if r[0] == "train"]
    va = [r for r in pooled if r[0] == "val"]
    te = [r for r in pooled if r[0] == "test"]

    Btr = np.stack([r[1] for r in tr]); Vtr = np.stack([r[2] for r in tr]); ytr = np.array([r[3] for r in tr])
    Bva = np.stack([r[1] for r in va]); Vva = np.stack([r[2] for r in va]); yva = np.array([r[3] for r in va])
    Bte = np.stack([r[1] for r in te]); Vte = np.stack([r[2] for r in te]); yte = np.array([r[3] for r in te])

    print("--- Pooled mode (Phase 2 D's data structure) ---")
    # (a) video only, pooled
    linear_probe(Vtr, ytr, Vva, yva, Vte, yte, "(a) CLIP only, pooled (5x dup)")
    # (d) concat brain+video, pooled
    linear_probe(np.concatenate([Btr, Vtr], -1), ytr,
                 np.concatenate([Bva, Vva], -1), yva,
                 np.concatenate([Bte, Vte], -1), yte,
                 "(d) BJ + CLIP concat, pooled")

    # ---- stim_level rows ----
    stim_level = build_stim_level(video, vstim, label_df, split)
    tr = [r for r in stim_level if r[0] == "train"]
    va = [r for r in stim_level if r[0] == "val"]
    te = [r for r in stim_level if r[0] == "test"]
    Vtr = np.stack([r[1] for r in tr]); ytr = np.array([r[2] for r in tr])
    Vva = np.stack([r[1] for r in va]); yva = np.array([r[2] for r in va])
    Vte = np.stack([r[1] for r in te]); yte = np.array([r[2] for r in te])

    print("\n--- Stim-level mode (Phase 1 video probe's data structure) ---")
    # (b/c) CLIP only stim_level
    linear_probe(Vtr, ytr, Vva, yva, Vte, yte, "(c) CLIP only, stim_level (Phase 1 setup)")


if __name__ == "__main__":
    main()
