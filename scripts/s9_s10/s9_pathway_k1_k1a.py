#!/usr/bin/env python3
"""S9-3 & S10 Pathway Evaluation: K1 (34 Emotions) & K1a + B4 (14 Dimensions).

Specifications implemented:
- docs/final/04_claude_code_workorder.md: S9 (lines 929-972), S10 (lines 980-1031, 1065-1079)
- docs/final/01_integrated_document.md: B4, B7, G14, K1, K1a, N3, N6, N8, N11, N12, O4(3), O17, O20, O21, O34, O35

Operational guarantees:
1. ZERO GPU usage: CUDA_VISIBLE_DEVICES="", torch.set_num_threads(8), device="cpu".
2. Read-only access to /scratch/emobrain/code and S2/S3/S4/S5/S6 outputs.
3. Outputs written exclusively to /scratch/emobrain/outputs/s9_analysis/pathway_k1_k1a/.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Enforce CPU-only execution BEFORE importing torch or any repo modules
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ.setdefault("OMP_NUM_THREADS", "8")
os.environ.setdefault("MKL_NUM_THREADS", "8")

_LOCAL_SRC = Path(__file__).resolve().parents[2] / "src"
REPO_SRC = _LOCAL_SRC if _LOCAL_SRC.is_dir() else Path("/scratch/emobrain/code/src")
sys.path.insert(0, str(REPO_SRC))

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(8)
if torch.cuda.is_available():
    raise RuntimeError("CUDA must NOT be available! Enforce CUDA_VISIBLE_DEVICES=''.")

import paths as P
import s4_common as c
from s4_feature_model import FeatureModel
import s5_common as d5
import s6_common as S

DEVICE = "cpu"
OUT_DIR = P.OUT / "s9_analysis" / "pathway_k1_k1a"
SCRIPT_PATH = Path(__file__).resolve()

BOOTSTRAP_SEED_TAG = b"EmoBrain/O4/video_canonical_bootstrap"
N_BOOT = 10_000
SEEDS = ("0", "1", "2")
HEADS = ("additive", "interaction")
CALIBRATIONS = ("uncalibrated", "calibrated")

VISION_LAYERS_S5 = ("vjepa2_10", "vjepa2_20", "vjepa2_30", "vjepa2_40")
CAPTION_LAYERS_S5 = ("deberta_06", "deberta_12", "deberta_18", "deberta_24")

# 01_integrated_document.md line 18: 7 categories noted in Cowen & Keltner (2017) main text
COWEN_EXCLUDED_7 = frozenset({
    "pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy"
})


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_array(arr: np.ndarray) -> str:
    a = np.ascontiguousarray(arr)
    h = hashlib.sha256()
    h.update(str(a.shape).encode())
    h.update(str(a.dtype).encode())
    h.update(a.tobytes())
    return h.hexdigest()


def check_repo_untouched() -> dict:
    """Verify tracked directories in /scratch/emobrain/code have zero modifications."""
    res_tracked = subprocess.run(
        ["git", "-C", str(P.REPO), "status", "--porcelain", "--", "src", "manifests", "splits", "configs"],
        capture_output=True,
        text=True,
        check=True,
    )
    if res_tracked.stdout.strip() != "":
        raise RuntimeError(f"Tracked repo directories are dirty:\n{res_tracked.stdout}")
    res_head = subprocess.run(
        ["git", "-C", str(P.REPO), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return {
        "repo": str(P.REPO),
        "head_commit": res_head.stdout.strip(),
        "tracked_dirs_clean": True,
    }


@dataclass(frozen=True)
class ModalityCalibrator:
    """N8 / O34 / O35 variance calibrator fit strictly on H2 validation fold in D_k D9 coordinates."""
    mu_hat: np.ndarray
    sd_hat: np.ndarray
    mu_true: np.ndarray
    sd_true: np.ndarray
    med_sd_hat: float
    threshold: float
    small_mask: np.ndarray

    @property
    def n_dims(self) -> int:
        return int(self.sd_hat.shape[0])

    @property
    def n_small(self) -> int:
        return int(self.small_mask.sum())


def fit_n8_calibrator(x_hat_val_dk: np.ndarray, x_true_val_dk: np.ndarray) -> ModalityCalibrator:
    """Fit N8 mean/SD calibration on H2 validation fold ONLY (zero test features, zero human ratings)."""
    xh = np.asarray(x_hat_val_dk, dtype=np.float64)
    xt = np.asarray(x_true_val_dk, dtype=np.float64)
    if xh.shape != xt.shape or xh.ndim != 2:
        raise ValueError(f"Shape mismatch in N8 calibration: {xh.shape} vs {xt.shape}")
    if not (np.isfinite(xh).all() and np.isfinite(xt).all()):
        raise ValueError("Non-finite values in H2 validation features during N8 calibration")

    mu_hat = xh.mean(axis=0)
    sd_hat = xh.std(axis=0, ddof=0)  # Matches c.fit_standardizer (ddof=0)
    mu_true = xt.mean(axis=0)
    sd_true = xt.std(axis=0, ddof=0)

    med_sd_hat = float(np.median(sd_hat))
    if med_sd_hat <= 0.0:
        raise ValueError(f"Median validation decoded SD is non-positive: {med_sd_hat}")
    threshold = 0.01 * med_sd_hat
    small_mask = (sd_hat < threshold) | (sd_hat <= 0.0)
    return ModalityCalibrator(
        mu_hat=mu_hat,
        sd_hat=sd_hat,
        mu_true=mu_true,
        sd_true=sd_true,
        med_sd_hat=med_sd_hat,
        threshold=threshold,
        small_mask=small_mask,
    )


def apply_n8_calibrator(cal: ModalityCalibrator, x_hat_test_dk: np.ndarray) -> np.ndarray:
    """Apply frozen H2 validation N8 statistics to test decoded features (O35 small-SD handling)."""
    xt = np.asarray(x_hat_test_dk, dtype=np.float64)
    if xt.ndim != 2 or xt.shape[1] != cal.n_dims:
        raise ValueError(f"Unexpected test feature shape {xt.shape} for calibrator ({cal.n_dims}d)")
    if not np.isfinite(xt).all():
        raise ValueError("Non-finite test decoded features before N8 calibration")

    safe_sd_hat = np.where(cal.small_mask, 1.0, cal.sd_hat)
    scale = np.where(cal.small_mask, 1.0, cal.sd_true / safe_sd_hat)
    out = cal.mu_true + scale * (xt - cal.mu_hat)
    # Explicit exact check on small_mask columns: mean-shift only (O35)
    if cal.small_mask.any():
        out[:, cal.small_mask] = xt[:, cal.small_mask] - cal.mu_hat[cal.small_mask] + cal.mu_true[cal.small_mask]
    if not np.isfinite(out).all():
        raise ValueError("Non-finite test decoded features after N8 calibration")
    return out


def load_s4_head(pt_path: Path, n_out: int, expected_coord: dict, head_kind: str) -> tuple[FeatureModel, dict]:
    saved = torch.load(pt_path, map_location="cpu", weights_only=True)
    r = int(saved["r"])
    if head_kind == "additive" and r != 0:
        raise ValueError(f"{pt_path}: additive head must have r=0, got {r}")
    if head_kind == "interaction" and r not in (1, 2, 4, 8):
        raise ValueError(f"{pt_path}: interaction head must have r in {{1,2,4,8}}, got {r}")
    for k in expected_coord:
        if not np.array_equal(saved[k].cpu().numpy(), expected_coord[k]):
            raise ValueError(f"{pt_path}: saved coordinate {k} differs from coordinates.npz")
    model = FeatureModel(5632, 4096, n_out, r)
    model.load_state_dict(saved["state_dict"])
    model.to(DEVICE).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    meta = {k: float(saved[k]) if k in ("weight_decay", "lr") else int(saved[k]) for k in ("r", "weight_decay", "lr", "epochs")}
    return model, meta


def forward_k1_head(model: FeatureModel, v_dk: np.ndarray, c_dk: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    vt = torch.as_tensor(np.asarray(v_dk, dtype=np.float32), dtype=torch.float32, device=DEVICE)
    ct = torch.as_tensor(np.asarray(c_dk, dtype=np.float32), dtype=torch.float32, device=DEVICE)
    with torch.no_grad():
        out = model(vt, ct)
        logit = c.finite(out.cpu().numpy().astype(np.float32), "K1 logit")
        prob = c.finite(torch.sigmoid(out).cpu().numpy().astype(np.float32), "K1 prob")
    return logit, prob


def forward_k1a_head(
    model: FeatureModel, v_dk: np.ndarray, c_dk: np.ndarray, target_mean: np.ndarray, target_std: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    vt = torch.as_tensor(np.asarray(v_dk, dtype=np.float32), dtype=torch.float32, device=DEVICE)
    ct = torch.as_tensor(np.asarray(c_dk, dtype=np.float32), dtype=torch.float32, device=DEVICE)
    with torch.no_grad():
        out = model(vt, ct)
        z = c.finite(out.cpu().numpy().astype(np.float32), "K1a z")
    # Rescale per fold to 1-9 scale before pooling (K1a, O20, s4_feature_model.py line 282)
    score = c.finite(z * target_std + target_mean, "K1a score")
    return z, score


def align_by_video_id(video_ids_src: np.ndarray, target_ids: np.ndarray, *arrays: np.ndarray, context: str = "") -> list[np.ndarray]:
    src_list = np.asarray(video_ids_src, dtype=np.int64).tolist()
    tgt_list = np.asarray(target_ids, dtype=np.int64).tolist()
    if len(src_list) != len(set(src_list)):
        raise ValueError(f"{context}: duplicate video_ids in source")
    if set(src_list) != set(tgt_list):
        raise ValueError(f"{context}: video_id mismatch (got {len(src_list)}, expected {len(tgt_list)})")
    pos = {v: i for i, v in enumerate(src_list)}
    idx = np.array([pos[v] for v in tgt_list], dtype=np.int64)
    return [arr[idx] for arr in arrays]


def build_canonical_bootstrap_weights(split: pd.DataFrame, n_boot: int = N_BOOT) -> dict:
    """Generate B=10,000 deterministic bootstrap draws of the 2,108 canonical_id clusters (O4(3))."""
    digest = hashlib.sha256(BOOTSTRAP_SEED_TAG).digest()
    seed_u64 = int.from_bytes(digest[:8], "big")
    rng = np.random.default_rng(seed_u64)

    canonical_ids_unique = np.sort(split["canonical_id"].unique().astype(np.int64))
    n_clusters = len(canonical_ids_unique)
    if n_clusters != 2108:
        raise ValueError(f"Expected 2,108 unique canonical_id clusters, got {n_clusters}")

    can_to_idx = {int(cid): i for i, cid in enumerate(canonical_ids_unique.tolist())}
    video_to_can_idx = np.array([can_to_idx[int(cid)] for cid in split["canonical_id"].tolist()], dtype=np.int64)

    draws = rng.integers(0, n_clusters, size=(n_boot, n_clusters), dtype=np.int64)
    offsets = (np.arange(n_boot, dtype=np.int64)[:, None]) * n_clusters
    flat_counts = np.bincount((draws + offsets).ravel(), minlength=n_boot * n_clusters)
    cluster_counts = flat_counts.reshape(n_boot, n_clusters)
    if not np.all(cluster_counts.sum(axis=1) == n_clusters):
        raise RuntimeError("Bootstrap cluster count row sums do not equal 2,108")
    if cluster_counts.max() > 255:
        raise RuntimeError("Cluster multiplicity exceeded uint8 capacity")
    cluster_counts_u8 = cluster_counts.astype(np.uint8)
    video_weights_u8 = cluster_counts_u8[:, video_to_can_idx]

    return {
        "seed_tag": BOOTSTRAP_SEED_TAG.decode("ascii"),
        "seed_sha256": digest.hex(),
        "random_seed_u64": seed_u64,
        "n_boot": n_boot,
        "canonical_ids": canonical_ids_unique,
        "video_ids": split["video_id"].to_numpy(dtype=np.int64),
        "video_to_canonical_idx": video_to_can_idx,
        "cluster_counts": cluster_counts_u8,
        "video_weights": video_weights_u8,
    }


def weighted_pearson_boot(y: np.ndarray, p: np.ndarray, weights_f64: np.ndarray, w_sums: np.ndarray) -> np.ndarray:
    """Exact vectorized weighted Pearson r across B bootstrap draws.

    y: (N, K) float64, p: (N, K) float64, weights_f64: (B, N) float64, w_sums: (B, 1) float64.
    Pre-centers y and p by unweighted means to prevent catastrophic cancellation in float64.
    """
    y64 = np.asarray(y, dtype=np.float64)
    p64 = np.asarray(p, dtype=np.float64)
    y0 = y64 - y64.mean(axis=0, keepdims=True)
    p0 = p64 - p64.mean(axis=0, keepdims=True)

    my = (weights_f64 @ y0) / w_sums
    mp = (weights_f64 @ p0) / w_sums

    cov = (weights_f64 @ (y0 * p0)) - w_sums * my * mp
    vy = (weights_f64 @ (y0 * y0)) - w_sums * my * my
    vp = (weights_f64 @ (p0 * p0)) - w_sums * mp * mp

    # Guard against tiny negative roundoff on genuinely constant resampled vectors
    scale_y = weights_f64 @ (y0 * y0)
    scale_p = weights_f64 @ (p0 * p0)
    valid = (vy > 1e-24 * np.maximum(scale_y, 1e-300)) & (vp > 1e-24 * np.maximum(scale_p, 1e-300))

    den = np.sqrt(np.maximum(vy, 0.0) * np.maximum(vp, 0.0))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.where(valid & (den > 0.0), cov / den, np.nan)

    # Exact fallback check if any entry failed the fast variance threshold
    if not valid.all():
        bad_b, bad_k = np.where(~valid)
        for b_idx, k_idx in zip(bad_b.tolist(), bad_k.tolist()):
            wb = weights_f64[b_idx] > 0
            ys = y64[wb, k_idx]
            ps = p64[wb, k_idx]
            if ys.size == 0 or np.all(ys == ys[0]) or np.all(ps == ps[0]):
                r[b_idx, k_idx] = np.nan
            else:
                rep_w = weights_f64[b_idx, wb].astype(np.int64)
                r[b_idx, k_idx] = float(c.pearson(np.repeat(ys, rep_w)[:, None], np.repeat(ps, rep_w)[:, None])[0])
    return r


def verify_weighted_pearson_equivalence(
    y_em: np.ndarray, p_em: np.ndarray, y_dim: np.ndarray, p_dim: np.ndarray,
    video_weights_u8: np.ndarray, elig_mask: np.ndarray, video_to_can_idx: np.ndarray, split: pd.DataFrame
) -> dict:
    """Verify weighted Pearson matches explicit row duplication to < 1e-12 across diverse draws."""
    dup_cid = 1349
    dup_cluster_idx = int(video_to_can_idx[split["video_id"].to_numpy() == dup_cid][0])
    # Pick first 5 draws + draws where canonical_id 1349 has multiplicity 0, 1, 2, 3+
    chosen_draws = list(range(5))
    for mult in (0, 1, 2, 3):
        matches = np.flatnonzero(video_weights_u8[:, split["video_id"].to_numpy() == dup_cid][:, 0] == mult)
        if len(matches):
            chosen_draws.extend(matches[:3].tolist())
    chosen_draws = sorted(set(chosen_draws))

    w_sub = video_weights_u8[chosen_draws][:, elig_mask].astype(np.float64)
    w_sums = w_sub.sum(axis=1, keepdims=True)

    ye = y_em[elig_mask]
    pe = p_em[elig_mask]
    yd = y_dim[elig_mask]
    pd_ = p_dim[elig_mask]

    fast_em = weighted_pearson_boot(ye, pe, w_sub, w_sums)
    fast_dim = weighted_pearson_boot(yd, pd_, w_sub, w_sums)

    max_diff_em = 0.0
    max_diff_dim = 0.0
    for i, b_idx in enumerate(chosen_draws):
        counts = video_weights_u8[b_idx, elig_mask].astype(np.int64)
        rep_ye = np.repeat(ye, counts, axis=0)
        rep_pe = np.repeat(pe, counts, axis=0)
        explicit_em = c.pearson(rep_ye, rep_pe)
        diff_em = float(np.nanmax(np.abs(fast_em[i] - explicit_em)))
        max_diff_em = max(max_diff_em, diff_em)

        rep_yd = np.repeat(yd, counts, axis=0)
        rep_pd = np.repeat(pd_, counts, axis=0)
        explicit_dim = c.pearson(rep_yd, rep_pd)
        diff_dim = float(np.nanmax(np.abs(fast_dim[i] - explicit_dim)))
        max_diff_dim = max(max_diff_dim, diff_dim)

    if max_diff_em >= 1e-12 or max_diff_dim >= 1e-12:
        raise RuntimeError(f"Weighted Pearson check failed: em={max_diff_em}, dim={max_diff_dim}")

    return {
        "n_draws_checked": len(chosen_draws),
        "draw_indices": chosen_draws,
        "canonical_1349_cluster_idx": dup_cluster_idx,
        "max_abs_diff_34_emotions": max_diff_em,
        "max_abs_diff_14_dimensions": max_diff_dim,
        "threshold": 1e-12,
        "passed": True,
    }


def basic_ci95(theta: float, boot: np.ndarray) -> tuple[float, float]:
    """O4(3): Basic 95% bootstrap CI [2*theta - q(0.975), 2*theta - q(0.025)]."""
    if not np.isfinite(theta):
        return float("nan"), float("nan")
    valid = boot[np.isfinite(boot)]
    if len(valid) == 0:
        return float("nan"), float("nan")
    q025, q975 = np.quantile(valid, [0.025, 0.975])
    return float(2.0 * theta - q975), float(2.0 * theta - q025)


def basic_ci95_vec(theta: np.ndarray, boot: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Vectorized basic 95% CI for theta (K,) and boot (B, K)."""
    low = np.full_like(theta, np.nan, dtype=np.float64)
    high = np.full_like(theta, np.nan, dtype=np.float64)
    for k in range(len(theta)):
        if np.isfinite(theta[k]):
            low[k], high[k] = basic_ci95(float(theta[k]), boot[:, k])
    return low, high


def hall_wilson_p(delta: float, delta_boot: np.ndarray) -> float:
    """O4(3): Two-sided centered bootstrap p-value (Hall & Wilson, 1991).
    p = (1 + sum(|Delta_boot - Delta| >= |Delta|)) / (B_valid + 1).
    """
    if not np.isfinite(delta):
        return float("nan")
    valid = delta_boot[np.isfinite(delta_boot)]
    if len(valid) == 0:
        return float("nan")
    exceed = int(np.sum(np.abs(valid - delta) >= np.abs(delta)))
    return float((1 + exceed) / (len(valid) + 1))


def hall_wilson_p_vec(delta: np.ndarray, delta_boot: np.ndarray) -> np.ndarray:
    out = np.full_like(delta, np.nan, dtype=np.float64)
    for k in range(len(delta)):
        if np.isfinite(delta[k]):
            out[k] = hall_wilson_p(float(delta[k]), delta_boot[:, k])
    return out


def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg (1995) step-up FDR q-values, ignoring NaNs."""
    p = np.asarray(pvals, dtype=np.float64)
    q = np.full_like(p, np.nan, dtype=np.float64)
    valid_idx = np.flatnonzero(np.isfinite(p))
    m = len(valid_idx)
    if m == 0:
        return q
    pv = p[valid_idx]
    order = np.argsort(pv, kind="mergesort")
    ranked = pv[order]
    ranks = np.arange(1, m + 1, dtype=np.float64)
    raw = ranked * (m / ranks)
    adj_sorted = np.minimum.accumulate(raw[::-1])[::-1]
    adj_sorted = np.clip(adj_sorted, 0.0, 1.0)
    unsorted = np.empty_like(adj_sorted)
    unsorted[order] = adj_sorted
    q[valid_idx] = unsorted
    return q


def sd_pair(vals: list[float] | np.ndarray) -> tuple[float, float]:
    a = np.asarray(vals, dtype=np.float64)
    if len(a) < 2 or not np.isfinite(a).all():
        return float("nan"), float("nan")
    return float(a.std(ddof=1)), float(a.std(ddof=0))


def main() -> None:
    t0 = time.time()
    repo_before = check_repo_untouched()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/7] Loading split, human scores, label map, and participant block masks...", flush=True)
    split = c.load_split()
    video_ids = split["video_id"].to_numpy(dtype=np.int64)
    folds = split["fold"].to_numpy(dtype=np.int64)
    in_all_5 = split["in_all_5"].to_numpy(dtype=bool)
    vid_to_pos = {int(v): i for i, v in enumerate(video_ids.tolist())}

    y_em, em_cols = c.load_scores(split, "emotions")
    y_dim, dim_cols = c.load_scores(split, "dimensions")
    y_em64 = np.asarray(y_em, dtype=np.float64)
    y_dim64 = np.asarray(y_dim, dtype=np.float64)

    label_map_df = pd.read_csv(c.LABEL_MAP, sep="\t")
    if label_map_df["score_col"].tolist() != em_cols:
        raise RuntimeError("label_map_34.tsv score_col order does not match c.load_scores")
    em_names = label_map_df["name"].tolist()
    keep_27_mask = np.array([name not in COWEN_EXCLUDED_7 for name in em_names], dtype=bool)
    if int(keep_27_mask.sum()) != 27:
        raise RuntimeError(f"Expected 27 Cowen & Keltner subset emotions, got {int(keep_27_mask.sum())}")
    dim_names = list(c.DIMENSIONS)

    participants = [f"sub-{s}" for s in d5.HK]
    blocks_table = pd.read_csv(d5.BLOCKS, sep="\t")
    elig_mask = np.zeros((len(participants), len(split)), dtype=bool)
    for pi, s in enumerate(d5.HK):
        allowed = d5.allowed_rows(s, blocks_table)
        for v in allowed["video_id"].tolist():
            elig_mask[pi, vid_to_pos[int(v)]] = True
    if not np.array_equal(elig_mask.all(axis=0), in_all_5):
        raise RuntimeError("Intersection of 5 participants' eligible videos does not match split.in_all_5")

    print("[2/7] Loading frozen S4 Stimulus heads (K1 & K1a) and running true-feature sanity checks...", flush=True)
    s4_k1_heads: dict[tuple[int, str], FeatureModel] = {}
    s4_k1a_heads: dict[tuple[int, str], FeatureModel] = {}
    s4_coords_k1: dict[int, dict[str, np.ndarray]] = {}
    s4_coords_k1a: dict[int, dict[str, np.ndarray]] = {}
    s4_sanity_records = []
    coord_identity_records = []

    s4_true_k1 = {h: np.full((len(split), 34), np.nan, dtype=np.float32) for h in ("selected", *HEADS)}
    s4_true_k1a = {h: np.full((len(split), 14), np.nan, dtype=np.float64) for h in HEADS}

    for k in range(1, c.N_FOLDS + 1):
        stim_dir = P.OUT / "s4_no_brain" / "stimulus" / f"fold{k}"
        k1a_dir = P.OUT / "s4_no_brain" / "k1a" / f"fold{k}"

        ck1_npz = np.load(stim_dir / "coordinates.npz")
        ck1a_npz = np.load(k1a_dir / "coordinates.npz")
        ck1 = {key: ck1_npz[key] for key in ("visual_mean", "visual_std", "caption_mean", "caption_std")}
        ck1a = {key: ck1a_npz[key] for key in ("visual_mean", "visual_std", "caption_mean", "caption_std", "target_mean", "target_std")}

        coord_diffs = {}
        for key in ("visual_mean", "visual_std", "caption_mean", "caption_std"):
            if not np.array_equal(ck1[key], ck1a[key]):
                raise RuntimeError(f"Fold {k}: K1 and K1a coordinates.npz differ on {key}")
            coord_diffs[key] = float(np.max(np.abs(ck1[key] - ck1a[key])))
        coord_identity_records.append({"fold": k, "bit_identical": True, "max_abs_diff": coord_diffs})

        s4_coords_k1[k] = ck1
        s4_coords_k1a[k] = ck1a

        meta_k1, meta_k1a = {}, {}
        for h in HEADS:
            s4_k1_heads[(k, h)], meta_k1[h] = load_s4_head(stim_dir / f"head_{h}.pt", 34, ck1, h)
            s4_k1a_heads[(k, h)], meta_k1a[h] = load_s4_head(k1a_dir / f"head_{h}.pt", 14, ck1a, h)

        # True-feature reproduction check (< 1e-5)
        te_mask = folds == k
        te_ids = video_ids[te_mask]
        v_raw_te = c.load_rows(c.VISUAL_TARGET, te_ids, split).astype(np.float64)
        c_raw_te = c.load_rows(c.CAPTION_TARGET, te_ids, split).astype(np.float64)
        v_te_dk = (v_raw_te - ck1["visual_mean"]) / ck1["visual_std"]
        c_te_dk = (c_raw_te - ck1["caption_mean"]) / ck1["caption_std"]

        stim_saved = np.load(stim_dir / "test_pred.npz")
        k1a_saved = np.load(k1a_dir / "test_pred.npz")
        if not np.array_equal(stim_saved["video_id"], te_ids) or not np.array_equal(k1a_saved["video_id"], te_ids):
            raise RuntimeError(f"Fold {k}: S4 test_pred.npz video_id order mismatch")

        s4_true_k1["selected"][te_mask] = stim_saved["p"]
        fold_check = {"fold": k, "k1_meta": meta_k1, "k1a_meta": meta_k1a}
        for h in HEADS:
            lg, pr = forward_k1_head(s4_k1_heads[(k, h)], v_te_dk, c_te_dk)
            saved_lg = stim_saved[f"{h}_logit"]
            saved_pr = stim_saved[f"{h}_p"]
            d_lg = float(np.max(np.abs(lg - saved_lg)))
            d_lg_rel = float(np.max(np.abs(lg - saved_lg) / np.maximum(np.abs(saved_lg), 1.0)))
            d_pr = float(np.max(np.abs(pr - saved_pr)))
            # Predictions p must match saved test_pred.npz to < 1e-5; raw unbounded logits (~ -10) allow CPU MKL vs GPU cuBLAS FP32 GEMM relative tolerance < 2e-5
            if d_pr >= 1e-5 or d_lg_rel >= 2e-5:
                raise RuntimeError(f"Fold {k} K1 {h} reproduction failed: p_diff={d_pr}, logit_abs={d_lg}, logit_rel={d_lg_rel}")
            fold_check[f"k1_{h}_logit_max_diff"] = d_lg
            fold_check[f"k1_{h}_logit_max_rel_diff"] = d_lg_rel
            fold_check[f"k1_{h}_p_max_diff"] = d_pr
            s4_true_k1[h][te_mask] = saved_pr

            zz, sc = forward_k1a_head(s4_k1a_heads[(k, h)], v_te_dk, c_te_dk, ck1a["target_mean"], ck1a["target_std"])
            d_zz = float(np.max(np.abs(zz - k1a_saved[f"{h}_z"])))
            d_sc = float(np.max(np.abs(sc - k1a_saved[f"{h}_score"])))
            if d_zz >= 1e-5 or d_sc >= 1e-5:
                raise RuntimeError(f"Fold {k} K1a {h} reproduction diff >= 1e-5: z={d_zz}, score={d_sc}")
            fold_check[f"k1a_{h}_z_max_diff"] = d_zz
            fold_check[f"k1a_{h}_score_max_diff"] = d_sc
            s4_true_k1a[h][te_mask] = k1a_saved[f"{h}_score"]
        s4_sanity_records.append(fold_check)

    for arr in [*s4_true_k1.values(), *s4_true_k1a.values()]:
        if not np.isfinite(arr).all():
            raise RuntimeError("Incomplete S4 true-feature pooled predictions")

    print("[3/7] Loading B4 direct ridge, S6 A-1 (brain_only), and S6 decoded features; running N8/O34/O35...", flush=True)
    b4_ridge_main = np.full((5, len(split), 14), np.nan, dtype=np.float64)
    b4_ridge_lit = np.full((5, len(split), 14), np.nan, dtype=np.float64)
    s5_em_ridge_main = np.full((5, len(split), 34), np.nan, dtype=np.float64)

    a1_preds = {sd: np.full((5, len(split), 34), np.nan, dtype=np.float32) for sd in SEEDS}
    c1_full_preds = {sd: np.full((5, len(split), 34), np.nan, dtype=np.float32) for sd in SEEDS}

    # Stream keys: ("ridge", "na"), ("brain_decoded", "0"|"1"|"2"), ("feature_encoder", "0"|"1"|"2")
    stream_specs = [("ridge", "na")] + [("brain_decoded", sd) for sd in SEEDS] + [("feature_encoder", sd) for sd in SEEDS]
    k1_preds = {
        (src, sd, h, cal): np.full((5, len(split), 34), np.nan, dtype=np.float32)
        for (src, sd) in stream_specs for h in HEADS for cal in CALIBRATIONS
    }
    k1a_preds = {
        (src, sd, h, cal): np.full((5, len(split), 14), np.nan, dtype=np.float64)
        for (src, sd) in stream_specs for h in HEADS for cal in CALIBRATIONS
    }

    o35_rows = []
    n8_leakage_checks = []
    k1_k1a_feature_identity_count = 0

    for k in range(1, c.N_FOLDS + 1):
        roles = c.roles(k)
        val_fold = int(roles["val"])
        test_fold = int(roles["test"])
        if test_fold != k or val_fold == test_fold:
            raise RuntimeError(f"Invalid fold roles for outer fold {k}: {roles}")

        ck1 = s4_coords_k1[k]
        ck1a = s4_coords_k1a[k]

        outer_s6 = P.OUT / "s6_brain" / f"outer_fold{k}"
        s6_std_npz = np.load(outer_s6 / "plan" / "standardization.npz")
        s6_feat_stats = {key: s6_std_npz[key] for key in ("visual_mean", "visual_std", "caption_mean", "caption_std")}

        # Load S6 A-1, C-1, and encoder 2 files once per outer fold
        sel_a1 = json.loads((outer_s6 / "brain_only" / "selected.json").read_text())
        sel_c1 = json.loads((outer_s6 / "brain_decoded" / "selected.json").read_text())
        sel_fe = json.loads((outer_s6 / "feature_encoder" / "selected.json").read_text())

        a1_fold_npz = {sd: np.load(outer_s6 / sel_a1["seeds"][sd] / "test_pred.npz") for sd in SEEDS}
        c1_full_fold_npz = {sd: np.load(outer_s6 / sel_c1["seeds"][sd] / "test_pred.npz") for sd in SEEDS}
        c1_dec_te = {sd: np.load(outer_s6 / sel_c1["seeds"][sd] / "outputs" / "decoded_test.npz") for sd in SEEDS}
        c1_dec_va = {sd: np.load(outer_s6 / sel_c1["seeds"][sd] / "outputs" / "decoded_val.npz") for sd in SEEDS}
        fe_dec_te = {sd: np.load(outer_s6 / sel_fe["seeds"][sd] / "outputs" / "decoded_test.npz") for sd in SEEDS}
        fe_dec_va = {sd: np.load(outer_s6 / sel_fe["seeds"][sd] / "outputs" / "decoded_val.npz") for sd in SEEDS}

        for pi, s in enumerate(d5.HK):
            pid = f"sub-{s}"
            va_split_pos = np.flatnonzero(elig_mask[pi] & (folds == val_fold))
            te_split_pos = np.flatnonzero(elig_mask[pi] & (folds == test_fold))
            val_ids_s = video_ids[va_split_pos]
            test_ids_s = video_ids[te_split_pos]

            if set(val_ids_s.tolist()) & set(test_ids_s.tolist()):
                raise RuntimeError(f"Leakage detected: {pid} fold {k} val and test video_ids overlap!")

            # True H2 validation features in D_k D9 coordinates (N8 calibration target ONLY)
            v_raw_val = c.load_rows(c.VISUAL_TARGET, val_ids_s, split).astype(np.float64)
            c_raw_val = c.load_rows(c.CAPTION_TARGET, val_ids_s, split).astype(np.float64)
            v_true_val_dk = (v_raw_val - ck1["visual_mean"]) / ck1["visual_std"]
            c_true_val_dk = (c_raw_val - ck1["caption_mean"]) / ck1["caption_std"]

            # B4 direct brain ridge predictions
            r_npz = np.load(P.OUT / "s5_ridge" / "ridge" / f"{pid}_fold{k}" / "pred.npz")
            dm_main, dm_lit, em_main = align_by_video_id(
                r_npz["video_id"], test_ids_s,
                r_npz["dimension_main"], r_npz["dimension_literature"], r_npz["emotion_main"],
                context=f"B4 ridge {pid} fold{k}",
            )
            b4_ridge_main[pi, te_split_pos] = dm_main
            b4_ridge_lit[pi, te_split_pos] = dm_lit
            s5_em_ridge_main[pi, te_split_pos] = em_main

            # A-1 & C-1 full predictions
            for sd in SEEDS:
                z_a1 = a1_fold_npz[sd]
                m_a1 = z_a1["participant"] == pid
                (p_a1,) = align_by_video_id(z_a1["video_id"][m_a1], test_ids_s, z_a1["p"][m_a1], context=f"A-1 {pid} fold{k} seed{sd}")
                a1_preds[sd][pi, te_split_pos] = p_a1

                z_c1 = c1_full_fold_npz[sd]
                m_c1 = z_c1["participant"] == pid
                (p_c1,) = align_by_video_id(z_c1["video_id"][m_c1], test_ids_s, z_c1["p"][m_c1], context=f"C-1 full {pid} fold{k} seed{sd}")
                c1_full_preds[sd][pi, te_split_pos] = p_c1

            # Build decoded feature streams in S4 fold<k> D_k D9 coordinates
            decoded_streams: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}

            # Source 1: S5 Ridge decoded features (O21, O34)
            s5_dec_dir = P.OUT / "s5_ridge" / "decoding" / f"{pid}_fold{k}"
            s5_te_npz = np.load(s5_dec_dir / "test_pred.npz")
            v_s5_te_raw = np.concatenate([s5_te_npz[ln] for ln in VISION_LAYERS_S5], axis=1).astype(np.float64)
            c_s5_te_raw = np.concatenate([s5_te_npz[ln] for ln in CAPTION_LAYERS_S5], axis=1).astype(np.float64)
            v_s5_te_raw, c_s5_te_raw = align_by_video_id(
                s5_te_npz["video_id"], test_ids_s, v_s5_te_raw, c_s5_te_raw, context=f"S5 decoding test {pid} fold{k}"
            )
            v_s5_te_dk = (v_s5_te_raw - ck1["visual_mean"]) / ck1["visual_std"]
            c_s5_te_dk = (c_s5_te_raw - ck1["caption_mean"]) / ck1["caption_std"]

            s5_oof_npz = np.load(s5_dec_dir / "inner_oof_target.npz")
            oof_val_mask = s5_oof_npz["inner_fold"] == val_fold
            if not oof_val_mask.any():
                raise RuntimeError(f"Empty O34 inner_oof slice for {pid} fold{k} val_fold={val_fold}")
            v_s5_va_raw = np.concatenate([s5_oof_npz[ln][oof_val_mask] for ln in VISION_LAYERS_S5], axis=1).astype(np.float64)
            c_s5_va_raw = np.concatenate([s5_oof_npz[ln][oof_val_mask] for ln in CAPTION_LAYERS_S5], axis=1).astype(np.float64)
            v_s5_va_raw, c_s5_va_raw = align_by_video_id(
                s5_oof_npz["video_id"][oof_val_mask], val_ids_s, v_s5_va_raw, c_s5_va_raw, context=f"S5 O34 inner_oof {pid} fold{k}"
            )
            v_s5_va_dk = (v_s5_va_raw - ck1["visual_mean"]) / ck1["visual_std"]
            c_s5_va_dk = (c_s5_va_raw - ck1["caption_mean"]) / ck1["caption_std"]
            decoded_streams[("ridge", "na")] = (v_s5_va_dk, c_s5_va_dk, v_s5_te_dk, c_s5_te_dk)

            # Source 2 (S6 brain_decoded C-1) & Source 3 (S6 feature_encoder encoder 2)
            for src_name, dec_va_dict, dec_te_dict in (
                ("brain_decoded", c1_dec_va, c1_dec_te),
                ("feature_encoder", fe_dec_va, fe_dec_te),
            ):
                for sd in SEEDS:
                    zva = dec_va_dict[sd]
                    mva = zva["participant"] == pid
                    v_va_s6, c_va_s6 = align_by_video_id(
                        zva["video_id"][mva], val_ids_s, zva["v_hat"][mva], zva["c_hat"][mva],
                        context=f"{src_name} decoded_val {pid} fold{k} seed{sd}",
                    )
                    v_va_dk, c_va_dk = S.to_k1_head(v_va_s6, c_va_s6, s6_feat_stats, ck1)

                    zte = dec_te_dict[sd]
                    mte = zte["participant"] == pid
                    v_te_s6, c_te_s6 = align_by_video_id(
                        zte["video_id"][mte], test_ids_s, zte["v_hat"][mte], zte["c_hat"][mte],
                        context=f"{src_name} decoded_test {pid} fold{k} seed{sd}",
                    )
                    v_te_dk, c_te_dk = S.to_k1_head(v_te_s6, c_te_s6, s6_feat_stats, ck1)
                    decoded_streams[(src_name, sd)] = (v_va_dk, c_va_dk, v_te_dk, c_te_dk)

            n8_leakage_checks.append({
                "participant": pid,
                "fold": k,
                "val_fold": val_fold,
                "n_val": int(len(val_ids_s)),
                "n_test": int(len(test_ids_s)),
                "val_test_overlap": int(len(set(val_ids_s.tolist()) & set(test_ids_s.tolist()))),
            })

            # Fit N8 calibrators on H2 val ONLY, calibrate test features, and run K1 & K1a heads on identical features
            src_display_map = {
                "ridge": "S5 Ridge",
                "brain_decoded": "C-1 (Brain + Decoded Feature -> Emotion)",
                "feature_encoder": "encoder 2 (Feature-only encoder, D-1 diagnostic)",
            }
            for (src_name, sd), (v_va_dk, c_va_dk, v_te_uncal, c_te_uncal) in decoded_streams.items():
                cal_v = fit_n8_calibrator(v_va_dk, v_true_val_dk)
                cal_c = fit_n8_calibrator(c_va_dk, c_true_val_dk)

                for mod_name, cal_obj in (("vision", cal_v), ("caption", cal_c)):
                    non_small = ~cal_obj.small_mask
                    mean_ratio = float(np.mean(cal_obj.sd_true[non_small] / cal_obj.sd_hat[non_small])) if non_small.any() else float("nan")
                    o35_rows.append({
                        "source": src_name,
                        "source_display": src_display_map[src_name],
                        "seed": sd,
                        "participant": pid,
                        "fold": k,
                        "val_fold": val_fold,
                        "n_val_videos": int(len(val_ids_s)),
                        "modality": mod_name,
                        "n_dims": cal_obj.n_dims,
                        "med_sd_hat": cal_obj.med_sd_hat,
                        "threshold_0p01_med": cal_obj.threshold,
                        "min_sd_hat": float(cal_obj.sd_hat.min()),
                        "max_sd_hat": float(cal_obj.sd_hat.max()),
                        "mean_sd_hat": float(cal_obj.sd_hat.mean()),
                        "mean_sd_true": float(cal_obj.sd_true.mean()),
                        "mean_sd_ratio_non_small": mean_ratio,
                        "n_small_sd": cal_obj.n_small,
                        "frac_small_sd": float(cal_obj.n_small / cal_obj.n_dims),
                    })

                v_te_cal = apply_n8_calibrator(cal_v, v_te_uncal)
                c_te_cal = apply_n8_calibrator(cal_c, c_te_uncal)

                for cal_label, (v_in, c_in) in (("uncalibrated", (v_te_uncal, c_te_uncal)), ("calibrated", (v_te_cal, c_te_cal))):
                    # Verify exact SHA-256 identity of input arrays fed to K1 and K1a (workorder line 970)
                    hv_before = sha256_array(v_in)
                    hc_before = sha256_array(c_in)
                    for h in HEADS:
                        _, p_k1 = forward_k1_head(s4_k1_heads[(k, h)], v_in, c_in)
                        _, sc_k1a = forward_k1a_head(s4_k1a_heads[(k, h)], v_in, c_in, ck1a["target_mean"], ck1a["target_std"])
                        k1_preds[(src_name, sd, h, cal_label)][pi, te_split_pos] = p_k1
                        k1a_preds[(src_name, sd, h, cal_label)][pi, te_split_pos] = sc_k1a
                    if sha256_array(v_in) != hv_before or sha256_array(c_in) != hc_before:
                        raise RuntimeError("Input array mutated during head evaluation!")
                    k1_k1a_feature_identity_count += 1

    # Verify every participant's eligible rows are 100% finite and non-eligible rows are NaN
    def assert_elig_completeness(arr3d: np.ndarray, label: str) -> None:
        for pi, pid in enumerate(participants):
            if not np.isfinite(arr3d[pi, elig_mask[pi]]).all():
                raise RuntimeError(f"{label} ({pid}): missing/NaN values on eligible rows")
            if not np.isnan(arr3d[pi, ~elig_mask[pi]]).all():
                raise RuntimeError(f"{label} ({pid}): unexpected non-NaN values on ineligible rows")

    assert_elig_completeness(b4_ridge_main, "b4_ridge_main")
    assert_elig_completeness(b4_ridge_lit, "b4_ridge_lit")
    for sd in SEEDS:
        assert_elig_completeness(a1_preds[sd], f"a1_seed{sd}")
        assert_elig_completeness(c1_full_preds[sd], f"c1_full_seed{sd}")
    for key, arr in k1_preds.items():
        assert_elig_completeness(arr, f"k1_{key}")
    for key, arr in k1a_preds.items():
        assert_elig_completeness(arr, f"k1a_{key}")

    o35_df = pd.DataFrame(o35_rows)
    o35_df.to_csv(OUT_DIR / "o35_small_sd_counts.tsv", sep="\t", index=False, float_format="%.8g")
    o35_df.to_csv(OUT_DIR / "o35_small_sd_counts.csv", index=False, float_format="%.8g")

    print("[4/7] Saving raw prediction archives (k1a_predictions.npz & k1_predictions.npz) and bootstrap weights...", flush=True)
    k1a_save = {
        "video_id": video_ids,
        "content_id": split["content_id"].to_numpy(dtype=np.int64),
        "canonical_id": split["canonical_id"].to_numpy(dtype=np.int64),
        "fold": folds,
        "in_all_5": in_all_5,
        "participants": np.array(participants),
        "eligible_mask": elig_mask,
        "dimensions": np.array(dim_names),
        "dimension_cols": np.array(dim_cols),
        "y_true_1to9": y_dim,
        "b4_ridge_main": b4_ridge_main,
        "b4_ridge_literature": b4_ridge_lit,
        "s4_true_additive": s4_true_k1a["additive"],
        "s4_true_interaction": s4_true_k1a["interaction"],
    }
    for (src, sd, h, cal), arr in k1a_preds.items():
        key_str = f"k1a_{src}_{h}_{cal}" if sd == "na" else f"k1a_{src}_seed{sd}_{h}_{cal}"
        k1a_save[key_str] = arr
    np.savez_compressed(OUT_DIR / "k1a_predictions.npz", **k1a_save)

    k1_save = {
        "video_id": video_ids,
        "content_id": split["content_id"].to_numpy(dtype=np.int64),
        "canonical_id": split["canonical_id"].to_numpy(dtype=np.int64),
        "fold": folds,
        "in_all_5": in_all_5,
        "participants": np.array(participants),
        "eligible_mask": elig_mask,
        "emotions": np.array(em_names),
        "emotion_cols": np.array(em_cols),
        "in_cowen27": keep_27_mask,
        "y_true_0to1": y_em,
        "s5_emotion_ridge_main": s5_em_ridge_main.astype(np.float32),
        "s4_true_selected": s4_true_k1["selected"],
        "s4_true_additive": s4_true_k1["additive"],
        "s4_true_interaction": s4_true_k1["interaction"],
    }
    for sd in SEEDS:
        k1_save[f"a1_brain_only_seed{sd}"] = a1_preds[sd]
        k1_save[f"c1_full_model_seed{sd}"] = c1_full_preds[sd]
    for (src, sd, h, cal), arr in k1_preds.items():
        key_str = f"k1_{src}_{h}_{cal}" if sd == "na" else f"k1_{src}_seed{sd}_{h}_{cal}"
        k1_save[key_str] = arr
    np.savez_compressed(OUT_DIR / "k1_predictions.npz", **k1_save)

    boot_info = build_canonical_bootstrap_weights(split, N_BOOT)
    np.savez_compressed(
        OUT_DIR / "bootstrap_canonical_weights.npz",
        seed_tag=np.array(boot_info["seed_tag"]),
        seed_sha256=np.array(boot_info["seed_sha256"]),
        random_seed_u64=np.array(boot_info["random_seed_u64"], dtype=np.uint64),
        canonical_ids=boot_info["canonical_ids"],
        video_ids=boot_info["video_ids"],
        video_to_canonical_idx=boot_info["video_to_canonical_idx"],
        cluster_counts=boot_info["cluster_counts"],
        video_weights=boot_info["video_weights"],
    )

    video_weights_u8 = boot_info["video_weights"]
    wp_check = verify_weighted_pearson_equivalence(
        y_em64,
        k1_preds[("ridge", "na", "interaction", "uncalibrated")][0].astype(np.float64),
        y_dim64,
        k1a_preds[("ridge", "na", "interaction", "uncalibrated")][0],
        video_weights_u8,
        elig_mask[0],
        boot_info["video_to_canonical_idx"],
        split,
    )
    print(f"    Weighted-Pearson sanity check passed: max_diff_em={wp_check['max_abs_diff_34_emotions']:.3e}, max_diff_dim={wp_check['max_abs_diff_14_dimensions']:.3e}", flush=True)

    print("[5/7] Computing 10,000-iteration canonical_id bootstrap correlations for all K1 & K1a/B4 conditions...", flush=True)
    # Precompute weight matrices per participant (eligible videos), common 5-participant videos (B7), and full 2,109 dev videos
    w_elig = []
    w_elig_sums = []
    for pi in range(5):
        wf = video_weights_u8[:, elig_mask[pi]].astype(np.float64)
        w_elig.append(wf)
        w_elig_sums.append(wf.sum(axis=1, keepdims=True))

    w_common = video_weights_u8[:, in_all_5].astype(np.float64)
    w_common_sums = w_common.sum(axis=1, keepdims=True)

    w_all = video_weights_u8.astype(np.float64)
    w_all_sums = w_all.sum(axis=1, keepdims=True)

    def eval_5subj(pred_5_2109_k: np.ndarray, y_2109_k: np.ndarray, sub_mask: np.ndarray | None = None) -> dict:
        """Compute point r and (10000, K) bootstrap r for each of 5 participants (eligible rows) + 5-subj mean + common_5subj_mean (B7).

        Per 04_claude_code_workorder.md line 1005: participant summary is nanmean across computable emotions/dimensions,
        and 5-participant overall summary is the equal-weight mean across the 5 participant summaries.
        """
        obs_list, boot_list = [], []
        obs_com_list, boot_com_list = [], []
        for pi in range(5):
            m = elig_mask[pi]
            yi, pri = y_2109_k[m], pred_5_2109_k[pi, m].astype(np.float64)
            obs_list.append(c.pearson(yi, pri))
            boot_list.append(weighted_pearson_boot(yi, pri, w_elig[pi], w_elig_sums[pi]))

            yc, prc = y_2109_k[in_all_5], pred_5_2109_k[pi, in_all_5].astype(np.float64)
            obs_com_list.append(c.pearson(yc, prc))
            boot_com_list.append(weighted_pearson_boot(yc, prc, w_common, w_common_sums))

        obs_arr = np.stack(obs_list, axis=0)      # (5, K)
        boot_arr = np.stack(boot_list, axis=0)    # (5, B, K)
        obs_com = np.stack(obs_com_list, axis=0)  # (5, K)
        boot_com = np.stack(boot_com_list, axis=0)  # (5, B, K)

        out = {}
        for pi, pid in enumerate(participants):
            d = {
                "obs_vec": obs_arr[pi],
                "boot_vec": boot_arr[pi],
                "obs_mean": float(np.nanmean(obs_arr[pi])),
                "boot_mean": np.nanmean(boot_arr[pi], axis=1),
                "obs_seeds": None,
                "seed_means": None,
            }
            if sub_mask is not None:
                d["obs_mean_sub"] = float(np.nanmean(obs_arr[pi, sub_mask]))
                d["boot_mean_sub"] = np.nanmean(boot_arr[pi, :, :][:, sub_mask], axis=1)
                d["seed_means_sub"] = None
            out[pid] = d

        for key_name, oa, ba in (("mean_5subj", obs_arr, boot_arr), ("common_5subj_mean", obs_com, boot_com)):
            d = {
                "obs_vec": np.nanmean(oa, axis=0),
                "boot_vec": np.nanmean(ba, axis=0),
                "obs_mean": float(np.mean(np.nanmean(oa, axis=1))),
                "boot_mean": np.mean(np.nanmean(ba, axis=2), axis=0),
                "obs_seeds": None,
                "seed_means": None,
            }
            if sub_mask is not None:
                d["obs_mean_sub"] = float(np.mean(np.nanmean(oa[:, sub_mask], axis=1)))
                d["boot_mean_sub"] = np.mean(np.nanmean(ba[:, :, sub_mask], axis=2), axis=0)
                d["seed_means_sub"] = None
            out[key_name] = d
        return out

    def eval_s4_ref(pred_2109_k: np.ndarray, y_2109_k: np.ndarray, sub_mask: np.ndarray | None = None) -> dict:
        """Evaluate S4 Stimulus Model on each participant's eligible rows (N11), 5-subj mean, common_5subj, AND all_2109_dev."""
        tiled = np.broadcast_to(pred_2109_k[None, :, :], (5, len(split), pred_2109_k.shape[1]))
        out = eval_5subj(tiled, y_2109_k, sub_mask=sub_mask)
        p64 = pred_2109_k.astype(np.float64)
        oa = c.pearson(y_2109_k, p64)
        ba = weighted_pearson_boot(y_2109_k, p64, w_all, w_all_sums)
        d = {
            "obs_vec": oa,
            "boot_vec": ba,
            "obs_mean": float(np.nanmean(oa)),
            "boot_mean": np.nanmean(ba, axis=1),
            "obs_seeds": None,
            "seed_means": None,
        }
        if sub_mask is not None:
            d["obs_mean_sub"] = float(np.nanmean(oa[sub_mask]))
            d["boot_mean_sub"] = np.nanmean(ba[:, sub_mask], axis=1)
            d["seed_means_sub"] = None
        out["all_2109_dev"] = d
        return out

    # Evaluate K1 conditions
    k1_eval_a1 = {sd: eval_5subj(a1_preds[sd], y_em64, sub_mask=keep_27_mask) for sd in SEEDS}
    k1_eval_c1_full = {sd: eval_5subj(c1_full_preds[sd], y_em64, sub_mask=keep_27_mask) for sd in SEEDS}
    k1_eval_s4 = {h: eval_s4_ref(s4_true_k1[h], y_em64, sub_mask=keep_27_mask) for h in HEADS}
    k1_eval_paths = {key: eval_5subj(arr, y_em64, sub_mask=keep_27_mask) for key, arr in k1_preds.items()}

    # Add 3-seed metric average (G14: average of per-seed r, NEVER ensemble of predictions!)
    def avg_3seeds_eval(eval_by_seed: dict[str, dict]) -> dict:
        out = {}
        for subj_key in eval_by_seed["0"]:
            obs_s = np.stack([eval_by_seed[sd][subj_key]["obs_vec"] for sd in SEEDS], axis=0)      # (3, K)
            boot_s = np.stack([eval_by_seed[sd][subj_key]["boot_vec"] for sd in SEEDS], axis=0)    # (3, B, K)
            seed_means = np.array([eval_by_seed[sd][subj_key]["obs_mean"] for sd in SEEDS], dtype=np.float64)
            seed_boots = np.stack([eval_by_seed[sd][subj_key]["boot_mean"] for sd in SEEDS], axis=0)  # (3, B)
            d = {
                "obs_vec": np.nanmean(obs_s, axis=0),
                "boot_vec": np.nanmean(boot_s, axis=0),
                "obs_mean": float(np.mean(seed_means)),
                "boot_mean": np.mean(seed_boots, axis=0),
                "obs_seeds": obs_s,
                "seed_means": seed_means,
            }
            if "obs_mean_sub" in eval_by_seed["0"][subj_key]:
                sm_sub = np.array([eval_by_seed[sd][subj_key]["obs_mean_sub"] for sd in SEEDS], dtype=np.float64)
                sb_sub = np.stack([eval_by_seed[sd][subj_key]["boot_mean_sub"] for sd in SEEDS], axis=0)
                d["obs_mean_sub"] = float(np.mean(sm_sub))
                d["boot_mean_sub"] = np.mean(sb_sub, axis=0)
                d["seed_means_sub"] = sm_sub
            out[subj_key] = d
        return out

    k1_eval_a1_mean3 = avg_3seeds_eval(k1_eval_a1)
    k1_eval_c1_full_mean3 = avg_3seeds_eval(k1_eval_c1_full)
    k1_eval_paths_mean3 = {}
    for src in ("brain_decoded", "feature_encoder"):
        for h in HEADS:
            for cal in CALIBRATIONS:
                k1_eval_paths_mean3[(src, h, cal)] = avg_3seeds_eval(
                    {sd: k1_eval_paths[(src, sd, h, cal)] for sd in SEEDS}
                )

    # Evaluate K1a & B4 14-dimension conditions
    b4_eval_main = eval_5subj(b4_ridge_main, y_dim64)
    b4_eval_lit = eval_5subj(b4_ridge_lit, y_dim64)
    s4_k1a_eval = {h: eval_s4_ref(s4_true_k1a[h], y_dim64) for h in HEADS}
    k1a_eval_paths = {key: eval_5subj(arr, y_dim64) for key, arr in k1a_preds.items()}
    k1a_eval_paths_mean3 = {}
    for src in ("brain_decoded", "feature_encoder"):
        for h in HEADS:
            for cal in CALIBRATIONS:
                k1a_eval_paths_mean3[(src, h, cal)] = avg_3seeds_eval(
                    {sd: k1a_eval_paths[(src, sd, h, cal)] for sd in SEEDS}
                )

    print("[6/7] Building K1 summary & per-emotion tables...", flush=True)
    n_vid_map = {participants[pi]: int(elig_mask[pi].sum()) for pi in range(5)}
    n_vid_map["mean_5subj"] = float(np.mean([elig_mask[pi].sum() for pi in range(5)]))
    n_vid_map["common_5subj_mean"] = int(in_all_5.sum())
    n_vid_map["all_2109_dev"] = int(len(split))

    # Y summary per participant for emotions & dimensions
    y_em_stats = {}
    y_dim_stats = {}
    for pi, pid in enumerate(participants):
        ye_p = y_em64[elig_mask[pi]]
        y_em_stats[pid] = ((ye_p > 0).sum(axis=0), ye_p.var(axis=0, ddof=0))
        yd_p = y_dim64[elig_mask[pi]]
        y_dim_stats[pid] = (yd_p.mean(axis=0), yd_p.var(axis=0, ddof=0))
    y_em_stats["mean_5subj"] = (
        np.mean([y_em_stats[p][0] for p in participants], axis=0),
        np.mean([y_em_stats[p][1] for p in participants], axis=0),
    )
    y_em_stats["common_5subj_mean"] = ((y_em64[in_all_5] > 0).sum(axis=0), y_em64[in_all_5].var(axis=0, ddof=0))
    y_em_stats["all_2109_dev"] = ((y_em64 > 0).sum(axis=0), y_em64.var(axis=0, ddof=0))
    y_dim_stats["mean_5subj"] = (
        np.mean([y_dim_stats[p][0] for p in participants], axis=0),
        np.mean([y_dim_stats[p][1] for p in participants], axis=0),
    )
    y_dim_stats["common_5subj_mean"] = (y_dim64[in_all_5].mean(axis=0), y_dim64[in_all_5].var(axis=0, ddof=0))
    y_dim_stats["all_2109_dev"] = (y_dim64.mean(axis=0), y_dim64.var(axis=0, ddof=0))

    k1_summary_rows = []
    k1_emotion_rows = []

    def emit_k1_spec(
        *,
        role: str,
        source: str,
        source_display: str,
        seed: str,
        head: str,
        calibration: str,
        eval_dict: dict,
        comparison_baseline: str,
        base_dict: dict | None,
        subj_keys: tuple[str, ...],
        mc_note: str,
    ) -> None:
        # First compute per-participant p-values/diffs so mean_5subj can report confirmed participant counts (6-1)
        per_subj_summary_p = {}
        per_subj_summary_d = {}
        per_subj_em_p = {}
        per_subj_em_q = {}
        per_subj_em_d = {}

        if base_dict is not None:
            for pid in participants:
                em_entry = eval_dict[pid]
                b_p_entry = base_dict[pid]

                d34 = float(em_entry["obs_mean"] - b_p_entry["obs_mean"])
                db34 = em_entry["boot_mean"] - b_p_entry["boot_mean"]
                per_subj_summary_d[pid] = d34
                per_subj_summary_p[pid] = hall_wilson_p(d34, db34)

                de = em_entry["obs_vec"] - b_p_entry["obs_vec"]
                dbe = em_entry["boot_vec"] - b_p_entry["boot_vec"]
                pe = hall_wilson_p_vec(de, dbe)
                qe = bh_fdr(pe)
                per_subj_em_d[pid] = de
                per_subj_em_p[pid] = pe
                per_subj_em_q[pid] = qe

        for sk in subj_keys:
            entry = eval_dict[sk]
            obs_r = entry["obs_vec"]        # (34,)
            boot_r = entry["boot_vec"]      # (B, 34)
            mean34 = entry["obs_mean"]
            boot_mean34 = entry["boot_mean"]
            mean27 = entry["obs_mean_sub"]
            boot_mean27 = entry["boot_mean_sub"]
            obs_seeds = entry["obs_seeds"]  # (3, 34) if mean_3seeds else None
            seed_means34 = entry["seed_means"]

            if seed_means34 is not None:
                sd1_r34, sd0_r34 = sd_pair(seed_means34)
            else:
                sd1_r34, sd0_r34 = float("nan"), float("nan")

            ci_l34, ci_h34 = basic_ci95(mean34, boot_mean34)
            n_not_comp34 = int(np.isnan(obs_r).sum())
            n_comp34 = 34 - n_not_comp34
            n_not_comp27 = int(np.isnan(obs_r[keep_27_mask]).sum())

            base_mean34 = float("nan")
            diff34 = float("nan")
            sd1_d34, sd0_d34 = float("nan"), float("nan")
            d_ci_l34, d_ci_h34 = float("nan"), float("nan")
            p_boot34 = float("nan")
            diff27 = float("nan")
            d_ci_l27, d_ci_h27 = float("nan"), float("nan")
            p_boot27 = float("nan")
            n_subj_unc, n_subj_pos_unc, n_subj_neg_unc = None, None, None

            if base_dict is not None and sk in base_dict:
                b_entry = base_dict[sk]
                base_mean34 = b_entry["obs_mean"]
                base_boot34 = b_entry["boot_mean"]
                base_mean27 = b_entry["obs_mean_sub"]
                base_boot27 = b_entry["boot_mean_sub"]
                b_seed_means34 = b_entry["seed_means"]

                diff34 = mean34 - base_mean34
                db34 = boot_mean34 - base_boot34
                d_ci_l34, d_ci_h34 = basic_ci95(diff34, db34)
                p_boot34 = hall_wilson_p(diff34, db34)

                diff27 = mean27 - base_mean27
                db27 = boot_mean27 - base_boot27
                d_ci_l27, d_ci_h27 = basic_ci95(diff27, db27)
                p_boot27 = hall_wilson_p(diff27, db27)

                if seed_means34 is not None and b_seed_means34 is not None:
                    # Paired seed differences (seed s vs A-1 seed s)
                    seed_diffs = seed_means34 - b_seed_means34
                    sd1_d34, sd0_d34 = sd_pair(seed_diffs)
                elif seed_means34 is None and b_seed_means34 is not None:
                    # Ridge vs 3 A-1 seeds
                    seed_diffs = mean34 - b_seed_means34
                    sd1_d34, sd0_d34 = sd_pair(seed_diffs)

                if sk == "mean_5subj":
                    n_subj_unc = sum(1 for p in participants if per_subj_summary_p[p] < 0.05)
                    n_subj_pos_unc = sum(1 for p in participants if per_subj_summary_d[p] > 0 and per_subj_summary_p[p] < 0.05)
                    n_subj_neg_unc = sum(1 for p in participants if per_subj_summary_d[p] < 0 and per_subj_summary_p[p] < 0.05)

            k1_summary_rows.append({
                "participant": sk,
                "n_videos": n_vid_map[sk],
                "role": role,
                "source": source,
                "source_display": source_display,
                "seed": seed,
                "head": head,
                "calibration": calibration,
                "mean_r_34": mean34,
                "seed_sd_r_34_ddof1": sd1_r34,
                "seed_sd_r_34_ddof0": sd0_r34,
                "ci95_low_r_34": ci_l34,
                "ci95_high_r_34": ci_h34,
                "n_computable_34": n_comp34,
                "n_not_computable_34": n_not_comp34,
                "mean_r_27_cowen": mean27,
                "n_not_computable_27": n_not_comp27,
                "comparison_baseline": comparison_baseline,
                "baseline_mean_r_34": base_mean34,
                "diff_vs_a1_34": diff34,
                "seed_sd_diff_34_ddof1": sd1_d34,
                "seed_sd_diff_34_ddof0": sd0_d34,
                "diff_ci95_low_34": d_ci_l34,
                "diff_ci95_high_34": d_ci_h34,
                "p_boot_two_sided_34": p_boot34,
                "diff_vs_a1_27_cowen": diff27,
                "diff_ci95_low_27": d_ci_l27,
                "diff_ci95_high_27": d_ci_h27,
                "p_boot_two_sided_27": p_boot27,
                "n_subj_confirmed_uncorrected": n_subj_unc,
                "n_subj_pos_uncorrected": n_subj_pos_unc,
                "n_subj_neg_uncorrected": n_subj_neg_unc,
                "multiple_comparison_note": mc_note,
            })

            # Per-emotion rows for sub-01..05, mean_5subj, and all_2109_dev (skip common_5subj_mean to keep per-emotion tidy)
            if sk in (*participants, "mean_5subj", "all_2109_dev"):
                ci_le, ci_he = basic_ci95_vec(obs_r, boot_r)
                sd1_re = obs_seeds.std(axis=0, ddof=1) if obs_seeds is not None else np.full(34, np.nan)
                n_nz, var_y = y_em_stats[sk]

                if base_dict is not None and sk in base_dict:
                    obs_b = base_dict[sk]["obs_vec"]
                    boot_b = base_dict[sk]["boot_vec"]
                    obs_b_seeds = base_dict[sk]["obs_seeds"]
                    de = obs_r - obs_b
                    dbe = boot_r - boot_b
                    d_le, d_he = basic_ci95_vec(de, dbe)
                    pe = hall_wilson_p_vec(de, dbe)
                    qe = bh_fdr(pe)
                    if obs_seeds is not None and obs_b_seeds is not None:
                        sd1_de = (obs_seeds - obs_b_seeds).std(axis=0, ddof=1)
                    elif obs_seeds is None and obs_b_seeds is not None:
                        sd1_de = (obs_r[None, :] - obs_b_seeds).std(axis=0, ddof=1)
                    else:
                        sd1_de = np.full(34, np.nan)
                    fam = f"{sk}:{source}:seed={seed}:{head}:{calibration}:vs_{comparison_baseline}:34emotions"
                    tier = "[탐색: BH-FDR 34개 정서]"
                else:
                    obs_b = np.full(34, np.nan)
                    de = np.full(34, np.nan)
                    d_le = np.full(34, np.nan)
                    d_he = np.full(34, np.nan)
                    pe = np.full(34, np.nan)
                    qe = np.full(34, np.nan)
                    sd1_de = np.full(34, np.nan)
                    fam = "none"
                    tier = mc_note

                for ei in range(34):
                    n_s_unc_e, n_s_fdr_e = None, None
                    if base_dict is not None and sk == "mean_5subj":
                        n_s_unc_e = sum(1 for p in participants if per_subj_em_p[p][ei] < 0.05)
                        n_s_fdr_e = sum(1 for p in participants if per_subj_em_q[p][ei] < 0.05)
                    k1_emotion_rows.append({
                        "participant": sk,
                        "n_videos": n_vid_map[sk],
                        "emotion_col": em_cols[ei],
                        "emotion": em_names[ei],
                        "in_cowen27": bool(keep_27_mask[ei]),
                        "n_nonzero_y": float(n_nz[ei]),
                        "var_y": float(var_y[ei]),
                        "role": role,
                        "source": source,
                        "source_display": source_display,
                        "seed": seed,
                        "head": head,
                        "calibration": calibration,
                        "computable": bool(np.isfinite(obs_r[ei])),
                        "r": float(obs_r[ei]),
                        "seed_sd_r_ddof1": float(sd1_re[ei]),
                        "ci95_low": float(ci_le[ei]),
                        "ci95_high": float(ci_he[ei]),
                        "comparison_baseline": comparison_baseline,
                        "r_baseline": float(obs_b[ei]),
                        "diff_vs_a1": float(de[ei]),
                        "seed_sd_diff_ddof1": float(sd1_de[ei]),
                        "diff_ci95_low": float(d_le[ei]),
                        "diff_ci95_high": float(d_he[ei]),
                        "p_boot_two_sided": float(pe[ei]),
                        "q_bh_fdr_34": float(qe[ei]),
                        "sig_uncorrected_0p05": bool(pe[ei] < 0.05) if np.isfinite(pe[ei]) else None,
                        "sig_bh_fdr_0p05": bool(qe[ei] < 0.05) if np.isfinite(qe[ei]) else None,
                        "n_subj_uncorrected_0p05": n_s_unc_e,
                        "n_subj_bh_fdr_0p05": n_s_fdr_e,
                        "analysis_tier": tier,
                        "fdr_family": fam,
                    })

    std_subjs = (*participants, "mean_5subj", "common_5subj_mean")

    # 1. Baseline A-1 (brain_only)
    for sd in SEEDS:
        emit_k1_spec(
            role="baseline_A1",
            source="brain_only",
            source_display="A-1 (Brain -> Emotion)",
            seed=sd,
            head="query_readout",
            calibration="na",
            eval_dict=k1_eval_a1[sd],
            comparison_baseline="none",
            base_dict=None,
            subj_keys=std_subjs,
            mc_note="기준 조건(A-1)",
        )
    emit_k1_spec(
        role="baseline_A1",
        source="brain_only",
        source_display="A-1 (Brain -> Emotion, 3-seed mean)",
        seed="mean_3seeds",
        head="query_readout",
        calibration="na",
        eval_dict=k1_eval_a1_mean3,
        comparison_baseline="none",
        base_dict=None,
        subj_keys=std_subjs,
        mc_note="기준 조건(A-1, G14 seed 점수 평균)",
    )

    # 2. Context: Full C-1 (with ROI token path g(H))
    for sd in SEEDS:
        emit_k1_spec(
            role="context_full_c1_with_roi_path",
            source="brain_decoded_full_model",
            source_display="C-1 Full Model (ROI+Decoded 참고)",
            seed=sd,
            head="interaction",
            calibration="na",
            eval_dict=k1_eval_c1_full[sd],
            comparison_baseline=f"A-1_seed{sd}",
            base_dict=k1_eval_a1[sd],
            subj_keys=std_subjs,
            mc_note="참고 맥락(C-1 전체 모델, ROI 경로 포함)",
        )
    emit_k1_spec(
        role="context_full_c1_with_roi_path",
        source="brain_decoded_full_model",
        source_display="C-1 Full Model (ROI+Decoded 참고, 3-seed mean)",
        seed="mean_3seeds",
        head="interaction",
        calibration="na",
        eval_dict=k1_eval_c1_full_mean3,
        comparison_baseline="A-1_mean_3seeds_paired",
        base_dict=k1_eval_a1_mean3,
        subj_keys=std_subjs,
        mc_note="참고 맥락(C-1 전체 모델, G14 seed 점수 평균)",
    )

    # 3. Reference S4 Stimulus Model (True Vision + Caption, NOT upper bound!)
    for h in HEADS:
        emit_k1_spec(
            role="reference_not_upper_bound",
            source="s4_true_features",
            source_display="S4 Stimulus Model (참고값, 상한 아님)",
            seed="na",
            head=h,
            calibration="na",
            eval_dict=k1_eval_s4[h],
            comparison_baseline="none",
            base_dict=None,
            subj_keys=(*std_subjs, "all_2109_dev"),
            mc_note="참고값(상한 아님, N10/N11)",
        )

    # 4. Primary K1: S5 Ridge decoded features -> Frozen K1 head (vs A-1 3-seed mean AND vs each A-1 seed 0,1,2)
    for h in HEADS:
        for cal in CALIBRATIONS:
            emit_k1_spec(
                role="primary_k1_pathway",
                source="ridge",
                source_display="S5 Ridge -> Frozen K1 Head",
                seed="na",
                head=h,
                calibration=cal,
                eval_dict=k1_eval_paths[("ridge", "na", h, cal)],
                comparison_baseline="A-1_mean_3seeds",
                base_dict=k1_eval_a1_mean3,
                subj_keys=std_subjs,
                mc_note="보조 분석(K1): [사전] 15개 Holm 묶음 밖, 비율 미사용(N6)",
            )
            for sd in SEEDS:
                emit_k1_spec(
                    role="primary_k1_pathway_per_a1_seed",
                    source="ridge",
                    source_display="S5 Ridge -> Frozen K1 Head",
                    seed="na",
                    head=h,
                    calibration=cal,
                    eval_dict=k1_eval_paths[("ridge", "na", h, cal)],
                    comparison_baseline=f"A-1_seed{sd}",
                    base_dict=k1_eval_a1[sd],
                    subj_keys=std_subjs,
                    mc_note=f"보조 분석(K1): A-1 seed {sd} 대조",
                )

    # 5. Primary K1: S6 C-1 (brain_decoded) decoded features -> Frozen K1 head (seed s matched vs A-1 seed s + 3-seed mean)
    for h in HEADS:
        for cal in CALIBRATIONS:
            for sd in SEEDS:
                emit_k1_spec(
                    role="primary_k1_pathway",
                    source="brain_decoded",
                    source_display="C-1 Decoded -> Frozen K1 Head",
                    seed=sd,
                    head=h,
                    calibration=cal,
                    eval_dict=k1_eval_paths[("brain_decoded", sd, h, cal)],
                    comparison_baseline=f"A-1_seed{sd}",
                    base_dict=k1_eval_a1[sd],
                    subj_keys=std_subjs,
                    mc_note="보조 분석(K1): 같은 seed의 A-1과 짝 비교(G14, N6)",
                )
            emit_k1_spec(
                role="primary_k1_pathway",
                source="brain_decoded",
                source_display="C-1 Decoded -> Frozen K1 Head (3-seed mean)",
                seed="mean_3seeds",
                head=h,
                calibration=cal,
                eval_dict=k1_eval_paths_mean3[("brain_decoded", h, cal)],
                comparison_baseline="A-1_mean_3seeds_paired",
                base_dict=k1_eval_a1_mean3,
                subj_keys=std_subjs,
                mc_note="보조 분석(K1): 3-seed 점수 평균 비교(G14, 예측 앙상블 아님)",
            )

    # 6. Bonus Diagnostic K1: S6 encoder 2 (feature_encoder) decoded features -> Frozen K1 head (01 5-A D-1)
    for h in HEADS:
        for cal in CALIBRATIONS:
            for sd in SEEDS:
                emit_k1_spec(
                    role="diagnostic_encoder2_D1",
                    source="feature_encoder",
                    source_display="encoder 2 Decoded -> Frozen K1 Head [보조 진단]",
                    seed=sd,
                    head=h,
                    calibration=cal,
                    eval_dict=k1_eval_paths[("feature_encoder", sd, h, cal)],
                    comparison_baseline=f"A-1_seed{sd}",
                    base_dict=k1_eval_a1[sd],
                    subj_keys=std_subjs,
                    mc_note="[보조 진단: 01 5-A D-1 encoder 2] 같은 seed의 A-1과 비교",
                )
            emit_k1_spec(
                role="diagnostic_encoder2_D1",
                source="feature_encoder",
                source_display="encoder 2 Decoded -> Frozen K1 Head [보조 진단, 3-seed mean]",
                seed="mean_3seeds",
                head=h,
                calibration=cal,
                eval_dict=k1_eval_paths_mean3[("feature_encoder", h, cal)],
                comparison_baseline="A-1_mean_3seeds_paired",
                base_dict=k1_eval_a1_mean3,
                subj_keys=std_subjs,
                mc_note="[보조 진단: 01 5-A D-1 encoder 2] 3-seed 점수 평균 비교(G14)",
            )

    k1_summary_df = pd.DataFrame(k1_summary_rows)
    k1_emotion_df = pd.DataFrame(k1_emotion_rows)
    k1_summary_df.to_csv(OUT_DIR / "s9_k1_pathway_summary.tsv", sep="\t", index=False, float_format="%.8g")
    k1_summary_df.to_csv(OUT_DIR / "s9_k1_pathway_summary.csv", index=False, float_format="%.8g")
    k1_emotion_df.to_csv(OUT_DIR / "s9_k1_per_emotion.tsv", sep="\t", index=False, float_format="%.8g")
    k1_emotion_df.to_csv(OUT_DIR / "s9_k1_per_emotion.csv", index=False, float_format="%.8g")

    print("[7/7] Building unified K1a & B4 14-dimension summary & per-dimension tables...", flush=True)
    k1a_summary_rows = []
    k1a_dim_rows = []

    def emit_k1a_spec(
        *,
        role: str,
        source: str,
        source_display: str,
        seed: str,
        head: str,
        calibration: str,
        eval_dict: dict,
        compare_to_b4_main: bool,
        subj_keys: tuple[str, ...],
        tier_summary: str,
    ) -> None:
        per_subj_sum_p = {}
        per_subj_sum_d = {}
        per_subj_dim_d = {}
        per_subj_dim_p = {}
        per_subj_dim_q = {}

        if compare_to_b4_main:
            for pid in participants:
                dm_entry = eval_dict[pid]
                b4_p_entry = b4_eval_main[pid]

                d14 = float(dm_entry["obs_mean"] - b4_p_entry["obs_mean"])
                db14 = dm_entry["boot_mean"] - b4_p_entry["boot_mean"]
                per_subj_sum_d[pid] = d14
                per_subj_sum_p[pid] = hall_wilson_p(d14, db14)

                dd = dm_entry["obs_vec"] - b4_p_entry["obs_vec"]
                dbd = dm_entry["boot_vec"] - b4_p_entry["boot_vec"]
                pd_p = hall_wilson_p_vec(dd, dbd)
                qd_p = bh_fdr(pd_p)
                per_subj_dim_d[pid] = dd
                per_subj_dim_p[pid] = pd_p
                per_subj_dim_q[pid] = qd_p

        for sk in subj_keys:
            entry = eval_dict[sk]
            obs_r = entry["obs_vec"]        # (14,)
            boot_r = entry["boot_vec"]      # (B, 14)
            mean14 = entry["obs_mean"]
            boot_mean14 = entry["boot_mean"]
            obs_seeds = entry["obs_seeds"]
            seed_means14 = entry["seed_means"]

            if seed_means14 is not None:
                sd1_r14, sd0_r14 = sd_pair(seed_means14)
            else:
                sd1_r14, sd0_r14 = float("nan"), float("nan")

            ci_l14, ci_h14 = basic_ci95(mean14, boot_mean14)
            n_not_comp14 = int(np.isnan(obs_r).sum())
            n_comp14 = 14 - n_not_comp14

            # Side-by-side (1) B4 ridge_main, B4 ridge_lit, and (2) S4 K1a reference (1067-1070)
            b4_main_14 = b4_eval_main[sk]["obs_mean"] if sk in b4_eval_main else float("nan")
            b4_lit_14 = b4_eval_lit[sk]["obs_mean"] if sk in b4_eval_lit else float("nan")
            s4_ref_14 = s4_k1a_eval[head][sk]["obs_mean"] if head in HEADS and sk in s4_k1a_eval[head] else float("nan")

            diff14 = float("nan")
            sd1_d14, sd0_d14 = float("nan"), float("nan")
            d_ci_l14, d_ci_h14 = float("nan"), float("nan")
            p_boot14 = float("nan")
            n_dims_pos = None
            n_dims_unc = None
            n_dims_fdr = None
            n_dims_pos_fdr = None
            n_dims_neg_fdr = None
            n_subj_unc, n_subj_pos_unc, n_subj_neg_unc = None, None, None

            if compare_to_b4_main and sk in b4_eval_main:
                b4_entry = b4_eval_main[sk]
                obs_b, boot_b = b4_entry["obs_vec"], b4_entry["boot_vec"]
                diff14 = mean14 - b4_entry["obs_mean"]
                db14 = boot_mean14 - b4_entry["boot_mean"]
                d_ci_l14, d_ci_h14 = basic_ci95(diff14, db14)
                p_boot14 = hall_wilson_p(diff14, db14)

                if seed_means14 is not None:
                    seed_diffs14 = seed_means14 - b4_entry["obs_mean"]
                    sd1_d14, sd0_d14 = sd_pair(seed_diffs14)

                dd_here = obs_r - obs_b
                pd_here = hall_wilson_p_vec(dd_here, boot_r - boot_b)
                qd_here = bh_fdr(pd_here)
                n_dims_pos = int(np.sum(dd_here > 0))
                n_dims_unc = int(np.sum(pd_here < 0.05))
                n_dims_fdr = int(np.sum(qd_here < 0.05))
                n_dims_pos_fdr = int(np.sum((dd_here > 0) & (qd_here < 0.05)))
                n_dims_neg_fdr = int(np.sum((dd_here < 0) & (qd_here < 0.05)))

                if sk == "mean_5subj":
                    n_subj_unc = sum(1 for p in participants if per_subj_sum_p[p] < 0.05)
                    n_subj_pos_unc = sum(1 for p in participants if per_subj_sum_d[p] > 0 and per_subj_sum_p[p] < 0.05)
                    n_subj_neg_unc = sum(1 for p in participants if per_subj_sum_d[p] < 0 and per_subj_sum_p[p] < 0.05)

            k1a_summary_rows.append({
                "participant": sk,
                "n_videos": n_vid_map[sk],
                "rater_reliability": "[미확인]",
                "role": role,
                "source": source,
                "source_display": source_display,
                "seed": seed,
                "head": head,
                "calibration": calibration,
                "mean_r_14": mean14,
                "seed_sd_r_14_ddof1": sd1_r14,
                "seed_sd_r_14_ddof0": sd0_r14,
                "ci95_low_r_14": ci_l14,
                "ci95_high_r_14": ci_h14,
                "n_computable_14": n_comp14,
                "n_not_computable_14": n_not_comp14,
                "col1_b4_ridge_main_mean_r_14": b4_main_14,
                "col1b_b4_ridge_lit_mean_r_14": b4_lit_14,
                "col2_s4_stim_ref_mean_r_14_not_upper_bound": s4_ref_14,
                "comparison_baseline": "B4_ridge_main" if compare_to_b4_main else "none",
                "diff_vs_b4_main_14": diff14,
                "seed_sd_diff_14_ddof1": sd1_d14,
                "seed_sd_diff_14_ddof0": sd0_d14,
                "diff_ci95_low_14": d_ci_l14,
                "diff_ci95_high_14": d_ci_h14,
                "p_boot_two_sided_14": p_boot14,
                "n_dims_pos_diff_of_14": n_dims_pos,
                "n_dims_p_lt_0p05_uncorrected": n_dims_unc,
                "n_dims_q_lt_0p05_bh_fdr": n_dims_fdr,
                "n_dims_pos_bh_fdr": n_dims_pos_fdr,
                "n_dims_neg_bh_fdr": n_dims_neg_fdr,
                "n_subj_confirmed_uncorrected": n_subj_unc,
                "n_subj_pos_uncorrected": n_subj_pos_unc,
                "n_subj_neg_uncorrected": n_subj_neg_unc,
                "analysis_tier": tier_summary,
            })

            # Per-dimension rows
            ci_ld, ci_hd = basic_ci95_vec(obs_r, boot_r)
            sd1_rd = obs_seeds.std(axis=0, ddof=1) if obs_seeds is not None else np.full(14, np.nan)
            sd0_rd = obs_seeds.std(axis=0, ddof=0) if obs_seeds is not None else np.full(14, np.nan)
            mean_y_d, var_y_d = y_dim_stats[sk]

            b4_m_vec = b4_eval_main[sk]["obs_vec"] if sk in b4_eval_main else np.full(14, np.nan)
            b4_l_vec = b4_eval_lit[sk]["obs_vec"] if sk in b4_eval_lit else np.full(14, np.nan)
            s4_r_vec = s4_k1a_eval[head][sk]["obs_vec"] if head in HEADS and sk in s4_k1a_eval[head] else np.full(14, np.nan)

            if compare_to_b4_main and sk in b4_eval_main:
                obs_b, boot_b = b4_eval_main[sk]["obs_vec"], b4_eval_main[sk]["boot_vec"]
                dd = obs_r - obs_b
                dbd = boot_r - boot_b
                d_ld, d_hd = basic_ci95_vec(dd, dbd)
                pd_v = hall_wilson_p_vec(dd, dbd)
                qd_v = bh_fdr(pd_v)
                sd1_dd = (obs_seeds - obs_b[None, :]).std(axis=0, ddof=1) if obs_seeds is not None else np.full(14, np.nan)
                sd0_dd = (obs_seeds - obs_b[None, :]).std(axis=0, ddof=0) if obs_seeds is not None else np.full(14, np.nan)
                fam = f"{sk}:{source}:seed={seed}:{head}:{calibration}:vs_B4_ridge_main:14dims"
                tier_dim = "[탐색: BH-FDR 14개 차원, Holm 15개 밖]"
            else:
                dd = np.full(14, np.nan)
                d_ld = np.full(14, np.nan)
                d_hd = np.full(14, np.nan)
                pd_v = np.full(14, np.nan)
                qd_v = np.full(14, np.nan)
                sd1_dd = np.full(14, np.nan)
                sd0_dd = np.full(14, np.nan)
                fam = "none"
                tier_dim = tier_summary

            for di in range(14):
                ns_unc, ns_pos_unc, ns_neg_unc = None, None, None
                ns_fdr, ns_pos_fdr, ns_neg_fdr = None, None, None
                if compare_to_b4_main and sk == "mean_5subj":
                    ns_unc = sum(1 for p in participants if per_subj_dim_p[p][di] < 0.05)
                    ns_pos_unc = sum(1 for p in participants if per_subj_dim_d[p][di] > 0 and per_subj_dim_p[p][di] < 0.05)
                    ns_neg_unc = sum(1 for p in participants if per_subj_dim_d[p][di] < 0 and per_subj_dim_p[p][di] < 0.05)
                    ns_fdr = sum(1 for p in participants if per_subj_dim_q[p][di] < 0.05)
                    ns_pos_fdr = sum(1 for p in participants if per_subj_dim_d[p][di] > 0 and per_subj_dim_q[p][di] < 0.05)
                    ns_neg_fdr = sum(1 for p in participants if per_subj_dim_d[p][di] < 0 and per_subj_dim_q[p][di] < 0.05)

                k1a_dim_rows.append({
                    "participant": sk,
                    "n_videos": n_vid_map[sk],
                    "dimension": dim_names[di],
                    "dimension_col": dim_cols[di],
                    "rater_reliability": "[미확인]",
                    "mean_y_1to9": float(mean_y_d[di]),
                    "var_y_1to9": float(var_y_d[di]),
                    "role": role,
                    "source": source,
                    "source_display": source_display,
                    "seed": seed,
                    "head": head,
                    "calibration": calibration,
                    "computable": bool(np.isfinite(obs_r[di])),
                    "r": float(obs_r[di]),
                    "seed_sd_r_ddof1": float(sd1_rd[di]),
                    "seed_sd_r_ddof0": float(sd0_rd[di]),
                    "ci95_low": float(ci_ld[di]),
                    "ci95_high": float(ci_hd[di]),
                    "col1_r_b4_ridge_main": float(b4_m_vec[di]),
                    "col1b_r_b4_ridge_literature": float(b4_l_vec[di]),
                    "col2_r_s4_stim_ref_not_upper_bound": float(s4_r_vec[di]),
                    "comparison_baseline": "B4_ridge_main" if compare_to_b4_main else "none",
                    "diff_vs_b4_main": float(dd[di]),
                    "seed_sd_diff_ddof1": float(sd1_dd[di]),
                    "seed_sd_diff_ddof0": float(sd0_dd[di]),
                    "diff_ci95_low": float(d_ld[di]),
                    "diff_ci95_high": float(d_hd[di]),
                    "p_boot_two_sided": float(pd_v[di]),
                    "q_bh_fdr_14": float(qd_v[di]),
                    "sig_uncorrected_0p05": bool(pd_v[di] < 0.05) if np.isfinite(pd_v[di]) else None,
                    "sig_bh_fdr_0p05": bool(qd_v[di] < 0.05) if np.isfinite(qd_v[di]) else None,
                    "n_subj_uncorrected_0p05": ns_unc,
                    "n_subj_pos_uncorrected_0p05": ns_pos_unc,
                    "n_subj_neg_uncorrected_0p05": ns_neg_unc,
                    "n_subj_bh_fdr_0p05": ns_fdr,
                    "n_subj_pos_bh_fdr_0p05": ns_pos_fdr,
                    "n_subj_neg_bh_fdr_0p05": ns_neg_fdr,
                    "analysis_tier": tier_dim,
                    "fdr_family": fam,
                })

    # (1) B4 Direct Brain Ridge (main = primary, literature = appendix)
    emit_k1a_spec(
        role="col1_baseline_b4_main",
        source="b4_ridge_main",
        source_display="(1) B4 Brain -> 14D Ridge (주 비교판)",
        seed="na",
        head="linear_ridge",
        calibration="na",
        eval_dict=b4_eval_main,
        compare_to_b4_main=False,
        subj_keys=std_subjs,
        tier_summary="[보조: B4 주 비교판(N15)]",
    )
    emit_k1a_spec(
        role="col1b_appendix_b4_literature",
        source="b4_ridge_literature",
        source_display="(1b) B4 Brain -> 14D Ridge (안쪽 5겹 문헌판, 부록)",
        seed="na",
        head="linear_ridge",
        calibration="na",
        eval_dict=b4_eval_lit,
        compare_to_b4_main=False,
        subj_keys=std_subjs,
        tier_summary="[보조 부록: B4 문헌판(H3)]",
    )

    # (2) S4 K1a Stimulus Model (True Vision + Caption -> 14D, reference, NOT upper bound)
    for h in HEADS:
        emit_k1a_spec(
            role="col2_reference_not_upper_bound",
            source="s4_k1a_true_features",
            source_display="(2) S4 K1a Stimulus Model (참고값, 상한 아님)",
            seed="na",
            head=h,
            calibration="na",
            eval_dict=s4_k1a_eval[h],
            compare_to_b4_main=False,
            subj_keys=(*std_subjs, "all_2109_dev"),
            tier_summary="참고값(상한 아님, K1a/N10/N11)",
        )

    # (3) Decoded Features -> Frozen K1a Stimulus Model: Ridge
    for h in HEADS:
        for cal in CALIBRATIONS:
            emit_k1a_spec(
                role="col3_primary_k1a_pathway",
                source="ridge",
                source_display="(3) S5 Ridge Decoded -> Frozen K1a Head",
                seed="na",
                head=h,
                calibration=cal,
                eval_dict=k1a_eval_paths[("ridge", "na", h, cal)],
                compare_to_b4_main=True,
                subj_keys=std_subjs,
                tier_summary="[보조/탐색: K1a 대 B4 주 비교판, 비율 미사용]",
            )

    # (3) Decoded Features -> Frozen K1a Stimulus Model: S6 C-1 (brain_decoded, seeds 0,1,2 & 3-seed mean)
    for h in HEADS:
        for cal in CALIBRATIONS:
            for sd in SEEDS:
                emit_k1a_spec(
                    role="col3_primary_k1a_pathway",
                    source="brain_decoded",
                    source_display="(3) C-1 Decoded -> Frozen K1a Head",
                    seed=sd,
                    head=h,
                    calibration=cal,
                    eval_dict=k1a_eval_paths[("brain_decoded", sd, h, cal)],
                    compare_to_b4_main=True,
                    subj_keys=std_subjs,
                    tier_summary="[보조/탐색: K1a 대 B4 주 비교판, G14 seed별]",
                )
            emit_k1a_spec(
                role="col3_primary_k1a_pathway",
                source="brain_decoded",
                source_display="(3) C-1 Decoded -> Frozen K1a Head (3-seed mean)",
                seed="mean_3seeds",
                head=h,
                calibration=cal,
                eval_dict=k1a_eval_paths_mean3[("brain_decoded", h, cal)],
                compare_to_b4_main=True,
                subj_keys=std_subjs,
                tier_summary="[보조/탐색: K1a 대 B4 주 비교판, G14 3-seed 점수 평균]",
            )

    # (3-bonus) S6 encoder 2 (feature_encoder, seeds 0,1,2 & 3-seed mean)
    for h in HEADS:
        for cal in CALIBRATIONS:
            for sd in SEEDS:
                emit_k1a_spec(
                    role="col3_diagnostic_encoder2_D1",
                    source="feature_encoder",
                    source_display="(3-진단) encoder 2 Decoded -> Frozen K1a Head [보조 진단]",
                    seed=sd,
                    head=h,
                    calibration=cal,
                    eval_dict=k1a_eval_paths[("feature_encoder", sd, h, cal)],
                    compare_to_b4_main=True,
                    subj_keys=std_subjs,
                    tier_summary="[보조 진단: encoder 2 (01 5-A D-1)]",
                )
            emit_k1a_spec(
                role="col3_diagnostic_encoder2_D1",
                source="feature_encoder",
                source_display="(3-진단) encoder 2 Decoded -> Frozen K1a Head [보조 진단, 3-seed mean]",
                seed="mean_3seeds",
                head=h,
                calibration=cal,
                eval_dict=k1a_eval_paths_mean3[("feature_encoder", h, cal)],
                compare_to_b4_main=True,
                subj_keys=std_subjs,
                tier_summary="[보조 진단: encoder 2 (01 5-A D-1), G14 3-seed 점수 평균]",
            )

    k1a_summary_df = pd.DataFrame(k1a_summary_rows)
    k1a_dim_df = pd.DataFrame(k1a_dim_rows)
    k1a_summary_df.to_csv(OUT_DIR / "s9_k1a_b4_14dimensions_summary.tsv", sep="\t", index=False, float_format="%.8g")
    k1a_summary_df.to_csv(OUT_DIR / "s9_k1a_b4_14dimensions_summary.csv", index=False, float_format="%.8g")
    k1a_dim_df.to_csv(OUT_DIR / "s9_k1a_b4_per_dimension.tsv", sep="\t", index=False, float_format="%.8g")
    k1a_dim_df.to_csv(OUT_DIR / "s9_k1a_b4_per_dimension.csv", index=False, float_format="%.8g")

    repo_after = check_repo_untouched()
    elapsed = round(time.time() - t0, 3)

    output_files = sorted(p.name for p in OUT_DIR.iterdir() if p.is_file() and p.name != "provenance.json")
    output_hashes = {fn: c.sha256(OUT_DIR / fn) for fn in output_files}

    provenance = {
        "task": "S9-3 & S10 Pathway Evaluation (K1 34 Emotions & K1a + B4 14 Dimensions)",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed,
        "script_path": str(SCRIPT_PATH),
        "script_sha256": c.sha256(SCRIPT_PATH) if SCRIPT_PATH.exists() else None,
        "output_dir": str(OUT_DIR),
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "torch": torch.__version__,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "cuda_is_available": bool(torch.cuda.is_available()),
            "torch_num_threads": int(torch.get_num_threads()),
            "device": DEVICE,
        },
        "repo_integrity": {
            "before": repo_before,
            "after": repo_after,
        },
        "bootstrap": {
            "seed_tag": boot_info["seed_tag"],
            "seed_sha256": boot_info["seed_sha256"],
            "random_seed_u64": boot_info["random_seed_u64"],
            "n_boot": N_BOOT,
            "n_dev_videos": int(len(split)),
            "n_unique_canonical_ids": int(len(boot_info["canonical_ids"])),
            "paired_canonical_id_1349_videos": [1349, 1363],
            "participant_eligible_video_counts": {participants[pi]: int(elig_mask[pi].sum()) for pi in range(5)},
            "common_5subj_video_count": int(in_all_5.sum()),
        },
        "sanity_checks": {
            "zero_test_leakage_in_n8_calibration": {
                "passed": True,
                "n_participant_fold_slices": len(n8_leakage_checks),
                "max_val_test_video_overlap": max(x["val_test_overlap"] for x in n8_leakage_checks),
                "human_ratings_used_in_n8": False,
                "test_features_used_in_n8": False,
                "s5_ridge_uses_o34_held_out_inner_oof": True,
            },
            "k1_vs_k1a_coordinates_npz_identity": {
                "passed": True,
                "bit_identical_all_6_folds": all(x["bit_identical"] for x in coord_identity_records),
                "per_fold": coord_identity_records,
            },
            "s4_true_feature_test_pred_reproduction": {
                "passed": True,
                "tolerance": 1e-5,
                "max_k1_logit_diff": max(max(x["k1_additive_logit_max_diff"], x["k1_interaction_logit_max_diff"]) for x in s4_sanity_records),
                "max_k1_prob_diff": max(max(x["k1_additive_p_max_diff"], x["k1_interaction_p_max_diff"]) for x in s4_sanity_records),
                "max_k1a_z_diff": max(max(x["k1a_additive_z_max_diff"], x["k1a_interaction_z_max_diff"]) for x in s4_sanity_records),
                "max_k1a_score_diff": max(max(x["k1a_additive_score_max_diff"], x["k1a_interaction_score_max_diff"]) for x in s4_sanity_records),
                "per_fold": s4_sanity_records,
            },
            "k1_and_k1a_identical_decoded_features_and_n8_stats": {
                "passed": True,
                "n_stream_participant_fold_cal_slices_verified": k1_k1a_feature_identity_count,
            },
            "weighted_pearson_vs_explicit_row_duplication": wp_check,
            "o35_small_sd_summary": {
                "total_rows": int(len(o35_df)),
                "total_small_sd_dims_across_all_slices": int(o35_df["n_small_sd"].sum()),
                "max_small_sd_dims_in_any_slice": int(o35_df["n_small_sd"].max()),
                "by_source_modality": (
                    o35_df.groupby(["source", "modality"])["n_small_sd"]
                    .agg(["count", "sum", "max"])
                    .reset_index()
                    .to_dict(orient="records")
                ),
            },
        },
        "output_files_sha256": output_hashes,
    }
    (OUT_DIR / "provenance.json").write_text(json.dumps(provenance, indent=2, ensure_ascii=False))
    print(f"DONE in {elapsed:.2f}s! Outputs written to {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
