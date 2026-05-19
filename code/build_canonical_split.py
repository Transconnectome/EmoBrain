#!/usr/bin/env python3
"""
FEELIN canonical stimulus list + V/A quartile multilabel stratified split.

Canonical:
  - stimulus_1 ~ stimulus_2185 (2,185 total)
  - stimulus_0 (16 TR resting fMRI) 제외
  - 반복 11개 (stimulus_2186~2196) 제외

Stratification:
  - V quartile (Q1-Q4) × A quartile (Q1-Q4) = 8 multilabel categories
  - iterative-stratification으로 train/val/test 분포 균형
  - 같은 stimulus는 모든 5 subjects에서 동일 split (stimulus-stratified)

L0 Binary task subset:
  - V_binary: V Q4 (top 25%) vs V Q1 (bottom 25%), middle Q2+Q3 제외
  - A_binary: A Q4 vs A Q1, middle 제외

Outputs:
  data/feelin_canonical_stimuli.csv
  data/horikawa_split.csv               (모든 자극, train/val/test)
  data/horikawa_binary_subset.csv       (L0 task용 extreme group)
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/pscratch/sd/s/sjmoon/FEELIN")
OUT_DIR = ROOT / "setup" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

METADATA = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")

N_CANONICAL = 2185
N_SUBJECTS = 5
SUBJECTS = [f"sub-{i:02d}" for i in range(1, N_SUBJECTS + 1)]

# Split ratio
TRAIN_RATIO, VAL_RATIO, TEST_RATIO = 0.8, 0.1, 0.1


def load_canonical_metadata():
    df = pd.read_csv(METADATA)
    df["stim_num_int"] = df["stimulus_num"].str.replace("stimulus_", "").astype(int)
    df = df[df["stim_num_int"] <= N_CANONICAL].copy()
    df = df.sort_values("stim_num_int").reset_index(drop=True)
    assert len(df) == N_CANONICAL, f"expected {N_CANONICAL}, got {len(df)}"
    return df


def quartile_bins(values: np.ndarray) -> np.ndarray:
    """Assign Q1, Q2, Q3, Q4 (0-3) by quartile."""
    q = np.quantile(values, [0.25, 0.5, 0.75])
    bins = np.digitize(values, q)  # 0,1,2,3
    return bins.astype(int)


def multilabel_stratified_split(stim_ids, v_q, a_q, train, val, test, seed=42):
    """
    Multilabel stratified split using iterative-stratification.
    Each stimulus has 2 labels: V quartile (4-class) + A quartile (4-class).
    """
    try:
        from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit
    except ImportError:
        print("[WARN] iterstrat not installed. Using sklearn stratified split with combined 16-class label.")
        return _fallback_split(stim_ids, v_q, a_q, train, val, test, seed)

    n = len(stim_ids)
    # one-hot encode V quartile + A quartile → 8 labels per stimulus
    labels = np.zeros((n, 8), dtype=int)
    for i in range(n):
        labels[i, v_q[i]] = 1            # V quartile slot (0-3)
        labels[i, 4 + a_q[i]] = 1        # A quartile slot (4-7)

    # First split: train vs (val+test)
    msss = MultilabelStratifiedShuffleSplit(n_splits=1, test_size=(val + test), random_state=seed)
    train_idx, rest_idx = next(msss.split(stim_ids, labels))

    # Second split: val vs test
    rest_labels = labels[rest_idx]
    msss2 = MultilabelStratifiedShuffleSplit(n_splits=1, test_size=test / (val + test), random_state=seed)
    val_idx_local, test_idx_local = next(msss2.split(rest_idx, rest_labels))
    val_idx = rest_idx[val_idx_local]
    test_idx = rest_idx[test_idx_local]

    return train_idx, val_idx, test_idx


def _fallback_split(stim_ids, v_q, a_q, train, val, test, seed):
    """Fallback: combine V_q × A_q → 16-class single label, sklearn stratified."""
    from sklearn.model_selection import train_test_split
    combined = v_q * 4 + a_q  # 0-15
    idx = np.arange(len(stim_ids))
    train_idx, rest_idx = train_test_split(idx, test_size=(val + test), stratify=combined, random_state=seed)
    rest_combined = combined[rest_idx]
    val_idx_local, test_idx_local = train_test_split(np.arange(len(rest_idx)), test_size=test / (val + test), stratify=rest_combined, random_state=seed)
    val_idx = rest_idx[val_idx_local]
    test_idx = rest_idx[test_idx_local]
    return train_idx, val_idx, test_idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    print("=" * 70)
    print("FEELIN canonical stimuli + quartile multilabel stratified split")
    print("=" * 70)

    df = load_canonical_metadata()
    v_vals = df["valence_score"].values
    a_vals = df["arousal_score"].values

    v_q = quartile_bins(v_vals)
    a_q = quartile_bins(a_vals)

    # Boundaries
    v_bounds = np.quantile(v_vals, [0.25, 0.5, 0.75])
    a_bounds = np.quantile(a_vals, [0.25, 0.5, 0.75])
    print(f"\n[V quartile bounds] {v_bounds}")
    print(f"[A quartile bounds] {a_bounds}")
    print(f"\n[V quartile counts] {np.bincount(v_q)}")
    print(f"[A quartile counts] {np.bincount(a_q)}")

    # Save canonical
    canonical = pd.DataFrame({
        "stim_idx": range(len(df)),
        "stimulus_num": df["stim_num_int"].values,
        "stimulus_name": [f"stimulus_{s}" for s in df["stim_num_int"].values],
        "valence_score": v_vals,
        "arousal_score": a_vals,
        "v_quartile": v_q,  # 0-3 (Q1-Q4)
        "a_quartile": a_q,
    })
    canonical_path = OUT_DIR / "feelin_canonical_stimuli.csv"
    canonical.to_csv(canonical_path, index=False)
    print(f"\n[Canonical] {len(canonical)} stimuli → {canonical_path}")

    # Multilabel stratified split
    print(f"\n[Split] target {TRAIN_RATIO}/{VAL_RATIO}/{TEST_RATIO}, seed={args.seed}")
    train_idx, val_idx, test_idx = multilabel_stratified_split(
        canonical["stimulus_num"].values, v_q, a_q,
        TRAIN_RATIO, VAL_RATIO, TEST_RATIO, args.seed,
    )

    print(f"  train: {len(train_idx)} stimuli ({100*len(train_idx)/N_CANONICAL:.1f}%)")
    print(f"  val:   {len(val_idx)} stimuli ({100*len(val_idx)/N_CANONICAL:.1f}%)")
    print(f"  test:  {len(test_idx)} stimuli ({100*len(test_idx)/N_CANONICAL:.1f}%)")

    # Per-split V/A quartile distribution check
    for name, idx in [("train", train_idx), ("val", val_idx), ("test", test_idx)]:
        v_dist = np.bincount(v_q[idx], minlength=4) / len(idx)
        a_dist = np.bincount(a_q[idx], minlength=4) / len(idx)
        print(f"  {name:5} V_q ratio: {[f'{x:.3f}' for x in v_dist]}, A_q ratio: {[f'{x:.3f}' for x in a_dist]}")

    # Build per-subject × stimulus split (모든 subject가 같은 stimulus split 공유)
    split_label = np.zeros(N_CANONICAL, dtype=object)
    split_label[train_idx] = "train"
    split_label[val_idx] = "val"
    split_label[test_idx] = "test"

    rows = []
    for sub in SUBJECTS:
        for i in range(N_CANONICAL):
            rows.append({
                "subject": sub,
                "stimulus_num": canonical["stimulus_num"].iloc[i],
                "stimulus_name": canonical["stimulus_name"].iloc[i],
                "v_quartile": v_q[i],
                "a_quartile": a_q[i],
                "split": split_label[i],
            })
    split_df = pd.DataFrame(rows)
    split_path = OUT_DIR / "horikawa_split.csv"
    split_df.to_csv(split_path, index=False)
    print(f"\n[Split saved] {split_path}  ({len(split_df)} total samples)")

    # L0 binary subset (extreme quartile groups)
    v_binary_subset = canonical[canonical["v_quartile"].isin([0, 3])].copy()
    v_binary_subset["v_label"] = (v_binary_subset["v_quartile"] == 3).astype(int)
    a_binary_subset = canonical[canonical["a_quartile"].isin([0, 3])].copy()
    a_binary_subset["a_label"] = (a_binary_subset["a_quartile"] == 3).astype(int)

    v_binary_subset.to_csv(OUT_DIR / "horikawa_L0_V_binary_subset.csv", index=False)
    a_binary_subset.to_csv(OUT_DIR / "horikawa_L0_A_binary_subset.csv", index=False)
    print(f"\n[L0 binary subset]")
    print(f"  V binary: {len(v_binary_subset)} stimuli (Q1+Q4, ~{100*len(v_binary_subset)/N_CANONICAL:.0f}%)")
    print(f"  A binary: {len(a_binary_subset)} stimuli (Q1+Q4)")


if __name__ == "__main__":
    main()
