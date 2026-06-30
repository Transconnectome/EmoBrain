"""Horikawa dataset adapter for D2 fMRI-LM pipeline.

Reads Horikawa ROI time-series csvs (Schaefer-400 cortical + Tian-S3 50 subcortical
= 450 ROI) per subject and per stimulus, concatenates them, pads/truncates to a
fixed T, applies per-subject per-ROI robust z-score, and writes the official
fMRI-LM HDF5 schema (see project/dir2_fmri_lm/adapters/_template.py).

Subject-pooled design: 5 subjects x 2185 stimuli = 10925 trials, all in one HDF5.
Sample id format: "<subject>::<stimulus_num>" (e.g. "sub-01::stimulus_42").

Outputs (under --out-dir, default
  /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/data/horikawa_emotion/ROI_Schaefer400Tian50/):

  data_resampled.h5
    time_series/sample_{i}     (450, T_fixed) float32
    metadata/subjects          (N,) bytes, "sub-01" ...
    metadata/sessions          (N,) bytes, "stimulus_42" ...
    metadata/sample_ids        (N,) bytes, "sub-01::stimulus_42" (extension, not
                                used by official fMRI-LM but useful for joining)

  normalization_params.npz
    medians (450,) iqrs (450,)        # --norm robust  (cohort level over pooled trials)

  per_subject_norm.npz
    medians (5, 450) iqrs (5, 450)    # raw per-subject per-ROI stats applied
                                       # BEFORE concatenation. Kept for audit.

  splits/{train,val,test}.txt
    one sample_id per line, drawn from horikawa_split.csv

  descriptors_rewritten/
    va_descriptors.csv          sample_id, text  (continuous V/A natural language)
    va_binary_descriptors.csv   sample_id, text  (Q1/Q4 only)
    cat_top1_descriptors.csv    sample_id, text  (Cowen-Keltner top-1)
    cat_topk_descriptors.csv    sample_id, text  (Cowen-Keltner top-k, threshold 0.10)
    mixed_descriptors.csv       sample_id, text  (V/A + cat combined)

CLI:
    python -m project.dir2_fmri_lm.adapters.horikawa --out-dir <path> [--norm robust]
                                                     [--max-samples N] [--smoke]
                                                     [--cat-threshold 0.10] [--t-fixed 16]
"""
from __future__ import annotations

import argparse
import gzip
import logging
import sys
import time
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

# Reuse helpers from sibling modules. Support both "python -m" and direct execution.
try:
    from ._template import write_h5, write_normalization_params
    from .generate_descriptors import (
        VA_TEMPLATE,
        VA_BINARY_TEMPLATE,
        CAT_TEMPLATE_TOP1,
        CAT_TEMPLATE_TOPK,
        MIXED_TEMPLATE,
        make_va,
        make_va_binary,
        make_cat_top1,
        make_cat_topk,
    )
except ImportError:  # direct script execution fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _template import write_h5, write_normalization_params  # type: ignore
    from generate_descriptors import (  # type: ignore
        VA_TEMPLATE,
        VA_BINARY_TEMPLATE,
        CAT_TEMPLATE_TOP1,
        CAT_TEMPLATE_TOPK,
        MIXED_TEMPLATE,
        make_va,
        make_va_binary,
        make_cat_top1,
        make_cat_topk,
    )


# ----------------------------------------------------------------------------
# Paths and constants
# ----------------------------------------------------------------------------

HORIKAWA_TS_ROOT = Path(
    "/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series"
)
LABELS_CSV = Path(
    "/pscratch/sd/s/sjmoon/EmoBrain/project/shared/data/cowen_horikawa_labels.csv"
)
SPLIT_CSV = Path(
    "/pscratch/sd/s/sjmoon/EmoBrain/project/shared/data/horikawa_split.csv"
)

SUBJECTS = [f"sub-{i:02d}" for i in range(1, 6)]
N_STIM = 2185                                # canonical Horikawa stimulus count
SCHAEFER_FILENAME = "fMRI.Schaefer17n400p.csv.gz"
TIAN_FILENAME = "fMRI.Tian_Subcortex_S3_3T.csv.gz"
N_SCHAEFER = 400
N_TIAN = 50
N_ROIS = N_SCHAEFER + N_TIAN                 # 450
T_FIXED_DEFAULT = 16

# Cowen-Keltner 34D columns in labels CSV.
CAT34_COLS = [f"score_{i}" for i in range(34)]
# Human-readable names for descriptor text. Order matches Cowen & Keltner (2017).
CAT34_NAMES = [
    "admiration", "adoration", "aesthetic_appreciation", "amusement",
    "anger", "anxiety", "awe", "awkwardness",
    "boredom", "calmness", "confusion", "contempt",
    "craving", "disgust", "empathic_pain", "entrancement",
    "envy", "excitement", "fear", "guilt",
    "horror", "interest", "joy", "nostalgia",
    "pride", "relief", "romance", "sadness",
    "satisfaction", "sexual_desire", "surprise", "sympathy",
    "triumph", "shame",
]
assert len(CAT34_NAMES) == 34

logger = logging.getLogger("horikawa_adapter")


# ----------------------------------------------------------------------------
# IO helpers
# ----------------------------------------------------------------------------

def _read_roi_csv(path: Path, expected_rois: int) -> np.ndarray:
    """Read a ROI csv.gz file. Returns (n_rois, T) float32 array.

    Schema: column 0 is label_name, columns 1..T are timepoints T1..Tn.
    """
    # pandas can read gzipped csv directly.
    df = pd.read_csv(path)
    if df.shape[0] != expected_rois:
        raise ValueError(f"{path}: expected {expected_rois} ROIs, got {df.shape[0]}")
    # Drop label_name column, keep time columns in original order.
    ts = df.iloc[:, 1:].to_numpy(dtype=np.float32)
    return ts


def _pad_or_truncate(ts: np.ndarray, t_fixed: int) -> np.ndarray:
    """ts: (n_rois, T). Pad with zeros along time axis or truncate to t_fixed."""
    n_rois, t = ts.shape
    if t == t_fixed:
        return ts
    if t > t_fixed:
        return ts[:, :t_fixed]
    out = np.zeros((n_rois, t_fixed), dtype=np.float32)
    out[:, :t] = ts
    return out


def _load_one_trial(subject: str, stim_num: int, t_fixed: int) -> np.ndarray:
    """Return (450, t_fixed) float32 raw concatenated ROI signal for one trial."""
    stim_dir = HORIKAWA_TS_ROOT / subject / f"stimulus_{stim_num}"
    schaefer = _read_roi_csv(stim_dir / SCHAEFER_FILENAME, N_SCHAEFER)
    tian = _read_roi_csv(stim_dir / TIAN_FILENAME, N_TIAN)
    if schaefer.shape[1] != tian.shape[1]:
        raise ValueError(
            f"{stim_dir}: Schaefer T={schaefer.shape[1]} vs Tian T={tian.shape[1]}"
        )
    cat = np.concatenate([schaefer, tian], axis=0)   # (450, T)
    return _pad_or_truncate(cat, t_fixed)


# ----------------------------------------------------------------------------
# Per-subject per-ROI z-score
# ----------------------------------------------------------------------------

def _per_subject_robust_zscore(
    trials_by_subject: dict[str, list[np.ndarray]],
) -> tuple[dict[str, list[np.ndarray]], dict[str, tuple[np.ndarray, np.ndarray]]]:
    """For each subject, compute per-ROI median/IQR over time across all trials,
    then z-score every trial. Matches D1 BrainVLM recording="Horikawa_ROI_zscore".

    Returns
        normalized: same shape as input
        stats: subject -> (medians (450,), iqrs (450,))
    """
    normalized: dict[str, list[np.ndarray]] = {}
    stats: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for subject, trials in trials_by_subject.items():
        # Concatenate along time axis: (450, sum_T)
        cat = np.concatenate(trials, axis=1)
        medians = np.median(cat, axis=1).astype(np.float32)             # (450,)
        q75 = np.percentile(cat, 75, axis=1).astype(np.float32)
        q25 = np.percentile(cat, 25, axis=1).astype(np.float32)
        iqrs = q75 - q25
        # Guard against zero IQR (constant ROI). Set to 1.0 -> z stays at 0.
        iqrs_safe = np.where(iqrs <= 1e-8, 1.0, iqrs).astype(np.float32)
        med_b = medians[:, None]
        iqr_b = iqrs_safe[:, None]
        normalized[subject] = [((t - med_b) / iqr_b).astype(np.float32) for t in trials]
        stats[subject] = (medians, iqrs)
        logger.info(
            "[norm] %s: %d trials, median range [%.3f, %.3f], iqr range [%.3f, %.3f]",
            subject,
            len(trials),
            float(medians.min()),
            float(medians.max()),
            float(iqrs.min()),
            float(iqrs.max()),
        )
    return normalized, stats


# ----------------------------------------------------------------------------
# Main pipeline steps
# ----------------------------------------------------------------------------

def _enumerate_trials(
    subjects: list[str], stim_nums: list[int]
) -> list[tuple[str, int]]:
    """Deterministic order: subject outer, stimulus inner."""
    return [(s, k) for s in subjects for k in stim_nums]


def _build_descriptor_inputs(
    labels: pd.DataFrame, split_df: pd.DataFrame, sample_ids: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (va_df, cat_df) aligned to sample_ids order.

    va_df columns: sample_id, valence, arousal, valence_quartile, arousal_quartile
                   (quartiles encoded as "Q1".."Q4" to match make_va_binary contract)
    cat_df columns: sample_id, <CAT34_NAMES...>
    """
    # Stimulus-level lookup tables.
    labels_by_stim = labels.set_index("stimulus_num")
    split_indexed = split_df.set_index(["subject", "stimulus_name"])

    rows_va = []
    rows_cat = []
    for sid in sample_ids:
        subject, stim = sid.split("::")
        lbl = labels_by_stim.loc[stim]
        spl = split_indexed.loc[(subject, stim)]
        v_q_int = int(spl["v_quartile"])  # 0..3
        a_q_int = int(spl["a_quartile"])
        # Map 0..3 -> Q1..Q4.
        v_q = f"Q{v_q_int + 1}"
        a_q = f"Q{a_q_int + 1}"
        rows_va.append({
            "sample_id": sid,
            "valence": float(lbl["valence_score"]),
            "arousal": float(lbl["arousal_score"]),
            "valence_quartile": v_q,
            "arousal_quartile": a_q,
        })
        cat_row = {"sample_id": sid}
        for col, name in zip(CAT34_COLS, CAT34_NAMES):
            cat_row[name] = float(lbl[col])
        rows_cat.append(cat_row)
    return pd.DataFrame(rows_va), pd.DataFrame(rows_cat)


def _make_mixed_descriptor(
    va_df: pd.DataFrame, cat_df: pd.DataFrame, threshold: float
) -> pd.DataFrame:
    """Combine VA continuous + Cowen-Keltner topk into one text row per sample."""
    cat_arr = cat_df[CAT34_NAMES].to_numpy()
    rows = []
    for i, sid in enumerate(va_df["sample_id"]):
        v = va_df.iloc[i]["valence"]
        a = va_df.iloc[i]["arousal"]
        va_text = VA_TEMPLATE.format(v=f"{v:.2f}", a=f"{a:.2f}")
        active = [CAT34_NAMES[k] for k in range(34) if cat_arr[i, k] >= threshold]
        if not active:
            active = [CAT34_NAMES[int(cat_arr[i].argmax())]]
        cat_text = CAT_TEMPLATE_TOPK.format(tops=", ".join(active))
        rows.append({
            "sample_id": sid,
            "text": MIXED_TEMPLATE.format(va=va_text, cat=cat_text, caption="").strip(),
        })
    return pd.DataFrame(rows)


def _write_splits(
    out_dir: Path, split_df: pd.DataFrame, sample_ids: list[str]
) -> dict[str, int]:
    split_indexed = split_df.set_index(["subject", "stimulus_name"])
    by_split: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    for sid in sample_ids:
        subject, stim = sid.split("::")
        s = split_indexed.loc[(subject, stim), "split"]
        by_split.setdefault(s, []).append(sid)
    splits_dir = out_dir / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for split_name, ids in by_split.items():
        with open(splits_dir / f"{split_name}.txt", "w") as f:
            for sid in ids:
                f.write(sid + "\n")
        counts[split_name] = len(ids)
    return counts


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------

def run(
    out_dir: Path,
    norm: str = "robust",
    t_fixed: int = T_FIXED_DEFAULT,
    cat_threshold: float = 0.10,
    smoke: bool = False,
    max_samples: int | None = None,
) -> dict[str, object]:
    """Main pipeline. Returns a summary dict."""
    t0 = time.time()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load metadata
    if not LABELS_CSV.exists():
        raise FileNotFoundError(f"labels csv missing: {LABELS_CSV}")
    if not SPLIT_CSV.exists():
        raise FileNotFoundError(f"split csv missing: {SPLIT_CSV}")
    labels = pd.read_csv(LABELS_CSV)
    split_df = pd.read_csv(SPLIT_CSV)
    logger.info("loaded labels=%s split=%s", labels.shape, split_df.shape)

    # Validate the label columns we depend on.
    missing = [c for c in (["stimulus_num", "valence_score", "arousal_score"] + CAT34_COLS)
               if c not in labels.columns]
    if missing:
        raise ValueError(f"labels csv missing columns: {missing[:5]} ...")
    missing_split = [c for c in ("subject", "stimulus_name", "v_quartile", "a_quartile", "split")
                     if c not in split_df.columns]
    if missing_split:
        raise ValueError(f"split csv missing columns: {missing_split}")

    # Decide subject / stimulus iteration.
    if smoke:
        subjects = SUBJECTS[:2]
        stim_nums = list(range(1, 51))         # stimulus_1 .. stimulus_50
        logger.info("[SMOKE] %d subj x %d stim", len(subjects), len(stim_nums))
    else:
        subjects = SUBJECTS
        stim_nums = list(range(1, N_STIM + 1))

    plan = _enumerate_trials(subjects, stim_nums)
    if max_samples is not None:
        plan = plan[:max_samples]
    logger.info("planning %d trials", len(plan))

    # Load all trials, grouped by subject for normalization.
    trials_by_subject: dict[str, list[np.ndarray]] = {s: [] for s in subjects}
    order_per_subject: dict[str, list[int]] = {s: [] for s in subjects}
    sample_ids: list[str] = []
    subjects_meta: list[str] = []
    sessions_meta: list[str] = []
    n_loaded = 0
    n_total = len(plan)
    log_every = max(1, n_total // 20)

    for subject, stim_num in plan:
        ts = _load_one_trial(subject, stim_num, t_fixed)
        trials_by_subject[subject].append(ts)
        order_per_subject[subject].append(stim_num)
        sample_ids.append(f"{subject}::stimulus_{stim_num}")
        subjects_meta.append(subject)
        sessions_meta.append(f"stimulus_{stim_num}")
        n_loaded += 1
        if n_loaded % log_every == 0:
            logger.info("[load] %d/%d (%.1f%%)", n_loaded, n_total, 100.0 * n_loaded / n_total)

    logger.info("loaded %d trials in %.1fs", n_loaded, time.time() - t0)

    # Per-subject per-ROI robust z-score.
    normalized_by_subject, per_subj_stats = _per_subject_robust_zscore(trials_by_subject)

    # Rebuild trial list in the same order as sample_ids.
    # Use a per-subject cursor.
    cursors = {s: 0 for s in subjects}
    time_series_ordered: list[np.ndarray] = []
    for sid in sample_ids:
        subject = sid.split("::")[0]
        ts = normalized_by_subject[subject][cursors[subject]]
        cursors[subject] += 1
        time_series_ordered.append(ts)
    assert all(cursors[s] == len(trials_by_subject[s]) for s in subjects)

    # Write HDF5.
    h5_path = out_dir / "data_resampled.h5"
    logger.info("writing HDF5 -> %s", h5_path)
    write_h5(h5_path, time_series_ordered, subjects_meta, sessions_meta)
    # Append sample_ids dataset for downstream joins (official schema ignores it).
    import h5py
    with h5py.File(h5_path, "a") as f:
        f["metadata"].create_dataset(
            "sample_ids", data=np.array(sample_ids, dtype="S64")
        )

    # Cohort-level normalization params (matches template helper convention).
    norm_path = out_dir / "normalization_params.npz"
    logger.info("writing cohort norm -> %s", norm_path)
    write_normalization_params(norm_path, time_series_ordered, norm=norm)

    # Per-subject stats for audit / per-subject inference variants.
    per_subj_path = out_dir / "per_subject_norm.npz"
    subj_order = subjects
    medians_stack = np.stack([per_subj_stats[s][0] for s in subj_order], axis=0)
    iqrs_stack = np.stack([per_subj_stats[s][1] for s in subj_order], axis=0)
    np.savez(
        per_subj_path,
        subjects=np.array(subj_order, dtype="S16"),
        medians=medians_stack,
        iqrs=iqrs_stack,
    )

    # Descriptors.
    desc_dir = out_dir / "descriptors_rewritten"
    desc_dir.mkdir(parents=True, exist_ok=True)
    va_df, cat_df = _build_descriptor_inputs(labels, split_df, sample_ids)

    va_text = make_va(va_df, v_col="valence", a_col="arousal", sample_col="sample_id")
    va_text.to_csv(desc_dir / "va_descriptors.csv", index=False)

    va_bin = make_va_binary(
        va_df,
        v_q_col="valence_quartile",
        a_q_col="arousal_quartile",
        sample_col="sample_id",
    )
    va_bin.to_csv(desc_dir / "va_binary_descriptors.csv", index=False)

    cat_top1 = make_cat_top1(cat_df, label_cols=CAT34_NAMES, sample_col="sample_id")
    cat_top1.to_csv(desc_dir / "cat_top1_descriptors.csv", index=False)

    cat_topk = make_cat_topk(
        cat_df, label_cols=CAT34_NAMES, sample_col="sample_id", threshold=cat_threshold
    )
    cat_topk.to_csv(desc_dir / "cat_topk_descriptors.csv", index=False)

    mixed = _make_mixed_descriptor(va_df, cat_df, threshold=cat_threshold)
    mixed.to_csv(desc_dir / "mixed_descriptors.csv", index=False)

    # Splits.
    split_counts = _write_splits(out_dir, split_df, sample_ids)

    elapsed = time.time() - t0
    summary = {
        "n_samples": len(sample_ids),
        "n_subjects": len(subjects),
        "n_stim_per_subject": len(stim_nums),
        "h5_path": str(h5_path),
        "norm_path": str(norm_path),
        "per_subj_norm_path": str(per_subj_path),
        "desc_dir": str(desc_dir),
        "split_counts": split_counts,
        "elapsed_sec": elapsed,
        "t_fixed": t_fixed,
        "cat_threshold": cat_threshold,
        "smoke": smoke,
        "norm": norm,
    }
    return summary


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Convert Horikawa ROI csvs into fMRI-LM HDF5 + descriptors."
    )
    p.add_argument(
        "--out-dir",
        default="/pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/data/horikawa_emotion/ROI_Schaefer400Tian50",
        help="Output dir for data_resampled.h5 / normalization_params.npz / descriptors_rewritten/",
    )
    p.add_argument("--norm", choices=["robust", "std"], default="robust",
                   help="Cohort normalization params written next to the h5.")
    p.add_argument("--t-fixed", type=int, default=T_FIXED_DEFAULT,
                   help="Fixed time length per trial (zero-pad shorter, truncate longer).")
    p.add_argument("--cat-threshold", type=float, default=0.10,
                   help="Cowen-Keltner soft-label threshold for top-k descriptor.")
    p.add_argument("--smoke", action="store_true",
                   help="Smoke mode: only 2 subjects x 50 stimuli.")
    p.add_argument("--max-samples", type=int, default=None,
                   help="If set, truncate the trial plan to this many (after smoke filtering).")
    p.add_argument("--log-level", default="INFO",
                   help="Logging level. Default INFO.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    )
    out_dir = Path(args.out_dir)
    if args.smoke:
        out_dir = out_dir.parent / (out_dir.name + "__SMOKE")
    summary = run(
        out_dir=out_dir,
        norm=args.norm,
        t_fixed=args.t_fixed,
        cat_threshold=args.cat_threshold,
        smoke=args.smoke,
        max_samples=args.max_samples,
    )
    print()
    print("=" * 70)
    print("Horikawa adapter summary")
    print("=" * 70)
    for k, v in summary.items():
        print(f"  {k:>22s}  {v}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
