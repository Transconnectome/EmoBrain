"""Sanity check for HorikawaDataset with real fMRI via FmriAdapter.

Verifies (mean mode).
    - Split sample counts (train 8740, val 1085, test 1100).
    - Same-stim label is subject-invariant.
    - Same-stim fMRI is subject-VARIANT (brain differs even when label is same).
    - fMRI value range is non-trivial (not zeros).
    - Sample structure keys.

Verifies (timeseries mode).
    - fMRI shape (T_max=47, 450).
    - mask shape (T_max,) bool, valid_T count matches original_T.
    - Padding zone (indices >= original_T) is exactly zero in raw fmri.
    - Padding-invariance under mean-with-mask.

Run.
    bash project/scripts/datasets_smoke.sh
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402
from project.data.datasets import HorikawaDataset, C, N_ROI  # noqa: E402


EXPECTED = {"train": 8740, "val": 1085, "test": 1100}


def check_split_counts() -> None:
    for split, expected_n in EXPECTED.items():
        ds = HorikawaDataset(split=split, fmri_mode="mean")
        assert len(ds) == expected_n, f"[{split}] len={len(ds)} expected {expected_n}"
        print(f"  [{split}] len = {len(ds)}")


def check_mean_mode() -> None:
    print("")
    print("[mean mode]")
    ds = HorikawaDataset(split="train", fmri_mode="mean")
    s0 = ds[0]
    print(f"  sample keys: {sorted(s0.keys())}")
    print(f"  subject_id  = {s0['subject_id']}")
    print(f"  stim_num    = {s0['stim_num']}")
    print(f"  label       shape={tuple(s0['label'].shape)}  range [{s0['label'].min():+.3f}, {s0['label'].max():+.3f}]")
    print(f"  fmri        shape={tuple(s0['fmri'].shape)}   range [{s0['fmri'].min():+.3f}, {s0['fmri'].max():+.3f}]")

    assert s0["fmri"].shape == (N_ROI,)
    assert s0["fmri"].abs().sum() > 0, "fmri is all-zero (adapter not connected?)"

    # Same-stim label invariance, same-stim fMRI variance.
    stim_pick = s0["stim_num"]
    matching_idx = [i for i in range(len(ds)) if ds._samples[i].stim_num == stim_pick]
    assert len(matching_idx) == 5, f"expected 5 subjects for stim {stim_pick}"
    label_ref = ds[matching_idx[0]]["label"]
    fmri_stack = []
    for i in matching_idx:
        s = ds[i]
        assert torch.allclose(s["label"], label_ref), "label not invariant across subjects"
        fmri_stack.append(s["fmri"])
    fmri_stack = torch.stack(fmri_stack, dim=0)  # (5, 450)
    subj_std = fmri_stack.std(dim=0).mean().item()
    print(f"  [invariance] stim {stim_pick} label identical across 5 subjects")
    print(f"  [variance]   stim {stim_pick} fMRI std across 5 subjects (mean over ROI) = {subj_std:+.4f}")
    assert subj_std > 0, "fMRI is identical across subjects (should differ)"


def check_timeseries_mode() -> None:
    print("")
    print("[timeseries mode]")
    ds = HorikawaDataset(split="train", fmri_mode="timeseries")
    s0 = ds[0]
    print(f"  sample keys: {sorted(s0.keys())}")
    ts = s0["fmri"]
    mask = s0["mask"]
    T_actual = int(s0["original_T"])
    T_max = ts.shape[0]
    print(f"  fmri shape={tuple(ts.shape)}  original_T={T_actual}  T_max={T_max}")
    print(f"  mask shape={tuple(mask.shape)}  dtype={mask.dtype}  valid_count={int(mask.sum())}")

    assert ts.shape == (T_max, N_ROI)
    assert mask.shape == (T_max,)
    assert mask.dtype == torch.bool
    assert int(mask.sum()) == T_actual, "mask valid count != original_T"

    # Padding zone is exact zero on disk.
    if T_actual < T_max:
        pad_slice = ts[T_actual:]
        assert (pad_slice == 0).all(), "padding zone is not zero"
        print(f"  padding zone [T={T_actual}..{T_max - 1}] is exact zero: OK")

    # Padding-invariance. Replace pad with random noise, masked mean unchanged.
    ts_noised = ts.clone()
    if T_actual < T_max:
        ts_noised[T_actual:] = torch.randn_like(ts_noised[T_actual:]) * 1e3
    mask_f = mask.unsqueeze(-1).to(ts.dtype)
    mean_original = (ts * mask_f).sum(dim=0) / max(T_actual, 1)
    mean_noised = (ts_noised * mask_f).sum(dim=0) / max(T_actual, 1)
    diff = (mean_original - mean_noised).abs().max().item()
    print(f"  [invariance] padding-invariance max abs diff = {diff:.2e}")
    assert diff < 1e-4, "padding leaked through mask"


def check_caption_mode() -> None:
    print("")
    print("[caption mode]")
    train = HorikawaDataset(split="train", fmri_mode="mean", caption_mode="human")
    val = HorikawaDataset(split="val", fmri_mode="mean", caption_mode="human")
    train.set_epoch(0)

    s = train[0]
    assert "caption" in s, "caption not attached to sample"
    print(f"  train[0] caption (epoch=0): {s['caption'][:100]}")
    assert isinstance(s["caption"], str) and len(s["caption"]) > 0

    # Deterministic within (stim, epoch).
    s_again = train[0]
    assert s["caption"] == s_again["caption"], "same (stim,epoch) yielded different rater"
    print(f"  train[0] deterministic within epoch 0: OK")

    # Cross-epoch variation. Different epoch should (usually) pick a different rater.
    train.set_epoch(1)
    s_ep1 = train[0]
    train.set_epoch(2)
    s_ep2 = train[0]
    train.set_epoch(0)
    seen = {s["caption"], s_ep1["caption"], s_ep2["caption"]}
    print(f"  train[0] across epochs {{0,1,2}}: {len(seen)} distinct captions")
    print(f"    ep0: {s['caption'][:80]}")
    print(f"    ep1: {s_ep1['caption'][:80]}")
    print(f"    ep2: {s_ep2['caption'][:80]}")

    # Val is deterministic, epoch-invariant.
    v0 = val[0]
    val.set_epoch(99)  # should be ignored
    v99 = val[0]
    assert v0["caption"] == v99["caption"], "val caption depends on epoch (should not)"
    print(f"  val[0] epoch-invariant: OK")
    print(f"    val[0]: {v0['caption'][:80]}")


def main() -> None:
    print("[split counts]")
    check_split_counts()
    check_mean_mode()
    check_timeseries_mode()
    check_caption_mode()
    print("")
    print("all checks OK")


if __name__ == "__main__":
    main()
