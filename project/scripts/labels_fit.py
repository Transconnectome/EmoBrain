"""Fit Cowen34Normalizer on the train split and save mu/std.

Reads.
    project/shared/data/cowen_horikawa_labels.csv   (34D scores per stimulus)
    project/shared/data/horikawa_split.csv          (train/val/test membership)

Writes.
    project/shared/data/norm_stats/cowen34_train.pt  (mu, std)

Sanity output.
    - Fitted mu should be near 0 after transform on train.
    - Fitted std should be near 1 after transform on train.
    - Per-emotion mu/std of raw train reported for inspection.

Run.
    bash project/scripts/labels_fit.sh
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Absolute-import so this script can also be invoked as a plain python file.
import sys
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from project.data.labels import Cowen34Normalizer  # noqa: E402


DATA_DIR = REPO_ROOT / "project" / "shared" / "data"
LABELS_CSV = DATA_DIR / "cowen_horikawa_labels.csv"
SPLIT_CSV = DATA_DIR / "horikawa_split.csv"
NORM_OUT = DATA_DIR / "norm_stats" / "cowen34_train.pt"

SCORE_COLS = [f"score_{k}" for k in range(34)]


def main() -> None:
    print(f"[read] {LABELS_CSV}")
    labels = pd.read_csv(LABELS_CSV)
    print(f"       rows = {len(labels)}, cols = {len(labels.columns)}")

    print(f"[read] {SPLIT_CSV}")
    split = pd.read_csv(SPLIT_CSV)
    print(f"       rows = {len(split)}, cols = {list(split.columns)}")

    # Split file is (subject, stimulus) level. Pick stimuli that appear in train
    # for any subject, then filter labels by stimulus number.
    train_stims = set(split.loc[split["split"] == "train", "stimulus_num"].unique())
    train_mask = labels["stim_num_int"].isin(train_stims)
    train_labels = labels.loc[train_mask, SCORE_COLS].values.astype(np.float32)
    print(f"[train] unique train stimuli = {train_mask.sum()}")
    print(f"        val stimuli   = {labels['stim_num_int'].isin(set(split.loc[split['split'] == 'val', 'stimulus_num'].unique())).sum()}")
    print(f"        test stimuli  = {labels['stim_num_int'].isin(set(split.loc[split['split'] == 'test', 'stimulus_num'].unique())).sum()}")

    # Fit
    norm = Cowen34Normalizer()
    train_z = norm.fit_transform(train_labels)

    # Sanity: post-transform train should be mean ~ 0, std ~ 1 per emotion.
    post_mu = train_z.mean(dim=0)
    post_std = train_z.std(dim=0, unbiased=False)
    print("")
    print("[sanity] after z-score on train:")
    print(f"         mu   range [{post_mu.min().item():+.2e}, {post_mu.max().item():+.2e}]")
    print(f"         std  range [{post_std.min().item():+.4f}, {post_std.max().item():+.4f}]")
    assert post_mu.abs().max() < 1e-4, "post-transform mean not ~ 0"
    assert (post_std - 1).abs().max() < 1e-4, "post-transform std not ~ 1"

    # Save
    norm.save(NORM_OUT)
    print("")
    print(f"[save] {NORM_OUT}")
    print(f"       mu  shape = {tuple(norm.mu.shape)}")
    print(f"       std shape = {tuple(norm.std.shape)}")


if __name__ == "__main__":
    main()
