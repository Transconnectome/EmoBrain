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
NORM_DIR = DATA_DIR / "norm_stats"

# Default = log1p_z (2026-07-07). Both modes are fitted and saved so experiments
# can select either; log1p_z is the project default.
MODES = ["log1p_z", "zscore"]
DEFAULT_MODE = "log1p_z"

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

    # Fit both modes, save to separate files. Default = log1p_z.
    NORM_DIR.mkdir(parents=True, exist_ok=True)
    for mode in MODES:
        norm = Cowen34Normalizer(mode=mode)
        train_z = norm.fit_transform(train_labels)
        post_mu = train_z.mean(dim=0)
        post_std = train_z.std(dim=0, unbiased=False)
        assert post_mu.abs().max() < 1e-4, f"[{mode}] post-transform mean not ~ 0"
        assert (post_std - 1).abs().max() < 1e-4, f"[{mode}] post-transform std not ~ 1"

        out = NORM_DIR / f"cowen34_train_{mode}.pt"
        norm.save(out)
        default_tag = "  (DEFAULT)" if mode == DEFAULT_MODE else ""
        print(f"[{mode}] post mu range [{post_mu.min():+.1e}, {post_mu.max():+.1e}], "
              f"std [{post_std.min():.4f}, {post_std.max():.4f}] -> {out.name}{default_tag}")

    # Also write the default under the legacy name for backward compat.
    Cowen34Normalizer(mode=DEFAULT_MODE).fit(train_labels).save(NORM_DIR / "cowen34_train.pt")
    print(f"[default] cowen34_train.pt = {DEFAULT_MODE}")


if __name__ == "__main__":
    main()
