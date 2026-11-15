#!/usr/bin/env python3
"""S10 Primary/Auxiliary Metrics, Baselines, Selection & Statistical Tests for EmoBrain.

Strict Operational Guarantees:
1. ZERO GPU USAGE: Forces CUDA_VISIBLE_DEVICES="" before any imports and runs strictly on CPU (16 threads).
2. ZERO REPO WRITES: Sets sys.dont_write_bytecode = True and writes ONLY to
   /scratch/emobrain/outputs/s10_tables_figures/tables/.
3. SCIENTIFIC RIGOR:
   - Rule G14: Computes every metric per seed (0, 1, 2), never averaging predictions across seeds.
   - Rule N11/N12: Evaluates on identical participant-video rows; pools 6 outer folds per participant
     before computing Pearson r once per emotion; never replaces undefined r with 0.
   - Rule O4(1)/(6): 10,000-iteration within-(fold, run_index) permutation tests keeping same-content
     pair (1349, 1363) fixed (+ sensitivity check permuting freely within run).
   - Rule O4(3): 10,000-iteration canonical_id cluster bootstrap (2,108 clusters) with basic 95% CIs
     and Hall & Wilson (1991) centered two-sided p-values.
"""
import os
import sys

USE_SLURM_GPU = "--slurm-gpu" in sys.argv
if USE_SLURM_GPU:
    if not os.environ.get("SLURM_JOB_ID"):
        raise RuntimeError("FATAL: --slurm-gpu requires running inside a sanctioned Slurm job (SLURM_JOB_ID missing)!")
else:
    # Default CPU-only mode: MUST precede all numerical / torch imports to guarantee zero GPU touch
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ.setdefault("OMP_NUM_THREADS", "16")
os.environ.setdefault("MKL_NUM_THREADS", "16")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "16")
sys.dont_write_bytecode = True

from pathlib import Path

_LOCAL_SRC = Path(__file__).resolve().parents[2] / "src"
CODE_SRC = _LOCAL_SRC if _LOCAL_SRC.is_dir() else Path("/scratch/emobrain/code/src")
if str(CODE_SRC) not in sys.path:
    sys.path.insert(0, str(CODE_SRC))

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(16)
if USE_SLURM_GPU:
    if not torch.cuda.is_available():
        raise RuntimeError("FATAL: --slurm-gpu requested inside Slurm job, but torch.cuda.is_available() is False!")
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    SLURM_DEVICE = torch.device("cuda:0")
else:
    if torch.cuda.is_available():
        raise RuntimeError("FATAL: CUDA is visible in CPU mode! S10 CPU mode must run with CUDA_VISIBLE_DEVICES=''.")
    SLURM_DEVICE = torch.device("cpu")

import paths as P
import s4_common as c
import s5_collect
import s5_common as d5
from s5_decoding import layer_name, load_targets
import s6_common as S

OUT_DIR = Path("/scratch/emobrain/outputs/s10_tables_figures/tables")
PARTICIPANTS = [f"sub-{s}" for s in d5.HK]  # ['sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05']
N_FOLDS = c.N_FOLDS  # 6
N_EMOTIONS = 34
N_BOOT = 10_000
N_PERM = 10_000

PERM_SEED_BYTES = b"EmoBrain/O4/within_run_permutation"
BOOT_SEED_BYTES = b"EmoBrain/O4/video_canonical_bootstrap"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def save_tsv_csv(df: pd.DataFrame, stem: str, out_dir: Path = OUT_DIR) -> Tuple[str, str]:
    tsv_path = out_dir / f"{stem}.tsv"
    csv_path = out_dir / f"{stem}.csv"
    df.to_csv(tsv_path, sep="\t", index=False)
    df.to_csv(csv_path, index=False)
    return str(tsv_path), str(csv_path)


def fisher_z_mean_1d(r: np.ndarray) -> float:
    valid = r[np.isfinite(r)]
    if len(valid) == 0:
        return float("nan")
    clipped = np.clip(valid, -0.999999, 0.999999)
    return float(np.tanh(np.mean(np.arctanh(clipped))))


def fisher_z_mean_2d(r_2d: np.ndarray) -> np.ndarray:
    """r_2d: (..., E). Returns Fisher-z mean along last axis."""
    clipped = np.clip(r_2d, -0.999999, 0.999999)
    with np.errstate(invalid="ignore"):
        z = np.arctanh(clipped)
        zm = np.nanmean(z, axis=-1)
    return np.tanh(zm)


def basic_ci(obs: float, boot: np.ndarray, alpha: float = 0.05) -> Tuple[float, float]:
    valid = boot[np.isfinite(boot)]
    if not np.isfinite(obs) or len(valid) == 0:
        return float("nan"), float("nan")
    q_low = float(np.quantile(valid, alpha / 2.0))
    q_high = float(np.quantile(valid, 1.0 - alpha / 2.0))
    return float(2.0 * obs - q_high), float(2.0 * obs - q_low)


def basic_ci_vec(obs: np.ndarray, boot: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """obs: (D,), boot: (B, D)."""
    q_low = np.nanquantile(boot, alpha / 2.0, axis=0)
    q_high = np.nanquantile(boot, 1.0 - alpha / 2.0, axis=0)
    return 2.0 * obs - q_high, 2.0 * obs - q_low


def hall_wilson_p(delta_obs: float, delta_boot: np.ndarray) -> float:
    valid = delta_boot[np.isfinite(delta_boot)]
    if not np.isfinite(delta_obs) or len(valid) == 0:
        return float("nan")
    exceed = int(np.sum(np.abs(valid - delta_obs) >= np.abs(delta_obs)))
    return float((1 + exceed) / (len(valid) + 1))


def hall_wilson_p_vec(delta_obs: np.ndarray, delta_boot: np.ndarray) -> np.ndarray:
    """delta_obs: (D,), delta_boot: (B, D)."""
    B = delta_boot.shape[0]
    out = np.full(delta_obs.shape, np.nan, dtype=np.float64)
    for d in range(delta_obs.shape[0]):
        if np.isfinite(delta_obs[d]):
            v = delta_boot[:, d]
            v = v[np.isfinite(v)]
            if len(v) > 0:
                out[d] = (1 + np.sum(np.abs(v - delta_obs[d]) >= np.abs(delta_obs[d]))) / (B + 1)
    return out


def holm_adjust(pvals: np.ndarray) -> np.ndarray:
    """Holm-Bonferroni step-down adjustment preserving NaN positions."""
    p = np.asarray(pvals, dtype=np.float64)
    out = np.full_like(p, np.nan)
    valid_idx = np.flatnonzero(np.isfinite(p))
    m = len(valid_idx)
    if m == 0:
        return out
    pv = p[valid_idx]
    order = np.argsort(pv, kind="mergesort")
    ranked = pv[order]
    adj = np.minimum(1.0, ranked * (m - np.arange(m)))
    adj = np.maximum.accumulate(adj)
    inv = np.empty_like(order)
    inv[order] = np.arange(m)
    out[valid_idx] = adj[inv]
    return out


def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg step-up FDR q-values preserving NaN positions."""
    p = np.asarray(pvals, dtype=np.float64)
    out = np.full_like(p, np.nan)
    valid_idx = np.flatnonzero(np.isfinite(p))
    m = len(valid_idx)
    if m == 0:
        return out
    pv = p[valid_idx]
    order = np.argsort(pv, kind="mergesort")
    ranked = pv[order]
    q = ranked * (m / (np.arange(m) + 1.0))
    q = np.minimum(1.0, np.minimum.accumulate(q[::-1])[::-1])
    inv = np.empty_like(order)
    inv[order] = np.arange(m)
    out[valid_idx] = q[inv]
    return out


def weighted_boot_pearson_2d(
    W: np.ndarray,
    X: np.ndarray,
    Y_c: np.ndarray,
    Sw_Y: np.ndarray,
    Sw_Y2: np.ndarray,
    W_sum: np.ndarray,
) -> np.ndarray:
    """Exact multiplicity-weighted Pearson correlation across B bootstrap resamples."""
    X_c = X - X.mean(axis=0, keepdims=True)
    if USE_SLURM_GPU and X.shape[1] >= 64:
        with torch.no_grad():
            Wg = torch.as_tensor(W, dtype=torch.float64, device=SLURM_DEVICE)
            Xcg = torch.as_tensor(X_c, dtype=torch.float64, device=SLURM_DEVICE)
            Ycg = torch.as_tensor(Y_c, dtype=torch.float64, device=SLURM_DEVICE)
            Sw_X = (Wg @ Xcg).cpu().numpy()
            Sw_X2 = (Wg @ (Xcg * Xcg)).cpu().numpy()
            Sw_XY = (Wg @ (Xcg * Ycg)).cpu().numpy()
    else:
        Sw_X = W @ X_c
        Sw_X2 = W @ (X_c * X_c)
        Sw_XY = W @ (X_c * Y_c)

    cov_num = Sw_XY - (Sw_X * Sw_Y) / W_sum
    var_x = Sw_X2 - (Sw_X * Sw_X) / W_sum
    var_y = Sw_Y2 - (Sw_Y * Sw_Y) / W_sum

    # Guard tiny float rounding around zero variance (exact constant vector has X_c == 0 -> var_x == 0)
    const_x = np.all(X == X[:1], axis=0, keepdims=True)
    const_y = np.all(Y_c == Y_c[:1], axis=0, keepdims=True)
    denom2 = var_x * var_y
    valid = (~const_x) & (~const_y) & (var_x > 1e-28) & (var_y > 1e-28) & (denom2 > 0.0)

    out = np.full(Sw_XY.shape, np.nan, dtype=np.float64)
    np.divide(cov_num, np.sqrt(np.where(valid, denom2, 1.0)), out=out, where=valid)
    return out


def safe_identification_scores(pred: np.ndarray, true: np.ndarray) -> np.ndarray:
    """O19 pairwise identification accuracy per video, matching s5_collect.identification_scores."""
    a = pred.astype(np.float64) - pred.astype(np.float64).mean(1, keepdims=True)
    b = true.astype(np.float64) - true.astype(np.float64).mean(1, keepdims=True)
    na = np.linalg.norm(a, axis=1, keepdims=True)
    nb = np.linalg.norm(b, axis=1, keepdims=True)
    if len(pred) < 2 or not ((na > 0).all() and (nb > 0).all()):
        return np.full(len(pred), np.nan, dtype=np.float64)
    a = a / na
    b = b / nb
    s = a @ b.T
    d = np.diag(s)
    wins = (d[:, None] > s).sum(1)
    return wins / (len(s) - 1)


def fast_exact_perm_mean_r(
    p_sub: np.ndarray,
    y_all: np.ndarray,
    present_mask: np.ndarray,
    perm_idx: np.ndarray,
    chunk_size: int = 100,
) -> Tuple[float, np.ndarray]:
    """Exact Pearson r(p_sub, y_all[perm_idx][:, present_mask]) averaged over computable dims.

    Exploits zero-mean unit-norm standardization of p_sub on present_mask and exact missing-row
    subtraction for denominator norms. In --slurm-gpu mode, executes IEEE-754 float64 contractions on GPU.
    """
    N_s = int(present_mask.sum())
    assert p_sub.shape[0] == N_s
    D = p_sub.shape[1]
    P_total = perm_idx.shape[0]

    # Observed r via canonical c.pearson
    r_obs_vec = c.pearson(y_all[present_mask].astype(np.float64), p_sub.astype(np.float64))
    obs_mean = float(np.nanmean(r_obs_vec))

    p64 = p_sub.astype(np.float64)
    p_c = p64 - p64.mean(axis=0, keepdims=True)
    p_norm = np.linalg.norm(p_c, axis=0, keepdims=True)
    const_p = np.all(p64 == p64[:1], axis=0) | (p_norm[0] <= 1e-28)
    p_tilde = np.where(~const_p[None, :], p_c / np.where(p_norm > 0, p_norm, 1.0), 0.0)

    y64 = y_all.astype(np.float64)
    y_prime = y64 - y64.mean(axis=0, keepdims=True)  # sum over all 2109 rows == 0
    total_y2 = np.sum(y_prime * y_prime, axis=0, keepdims=True)  # (1, D)
    missing_pos = np.flatnonzero(~present_mask)
    present_pos = np.flatnonzero(present_mask)

    if USE_SLURM_GPU:
        with torch.no_grad():
            yp_g = torch.as_tensor(y_prime, dtype=torch.float64, device=SLURM_DEVICE)
            pt_g = torch.as_tensor(p_tilde, dtype=torch.float64, device=SLURM_DEVICE)
            ty2_g = torch.as_tensor(total_y2, dtype=torch.float64, device=SLURM_DEVICE)
            cp_g = torch.as_tensor(const_p, dtype=torch.bool, device=SLURM_DEVICE)
            pres_pos_g = torch.as_tensor(present_pos, dtype=torch.long, device=SLURM_DEVICE)
            miss_pos_g = torch.as_tensor(missing_pos, dtype=torch.long, device=SLURM_DEVICE)
            perm_g = torch.as_tensor(perm_idx, dtype=torch.long, device=SLURM_DEVICE)

            g_chunk = 500 if D >= 1024 else 2500
            null_g = torch.empty(P_total, dtype=torch.float64, device=SLURM_DEVICE)
            for b0 in range(0, P_total, g_chunk):
                b1 = min(P_total, b0 + g_chunk)
                pi_c = perm_g[b0:b1]
                if len(missing_pos) == 0:
                    den = torch.sqrt(torch.clamp(ty2_g, min=0.0)).expand(b1 - b0, D)
                else:
                    y_miss = yp_g[pi_c[:, miss_pos_g]]  # (B, M_s, D)
                    s1 = -y_miss.sum(dim=1)
                    s2 = ty2_g - (y_miss * y_miss).sum(dim=1)
                    var_num = s2 - (s1 * s1) / float(N_s)
                    den = torch.where(
                        var_num > 1e-28,
                        torch.sqrt(torch.clamp(var_num, min=0.0)),
                        torch.full_like(var_num, float("nan")),
                    )
                y_pres = yp_g[pi_c[:, pres_pos_g]]  # (B, N_s, D)
                num = torch.einsum("bnd,nd->bd", y_pres, pt_g)
                valid = (~cp_g[None, :]) & torch.isfinite(den) & (den > 0.0)
                r_mat = torch.where(
                    valid,
                    num / torch.where(valid, den, torch.ones_like(den)),
                    torch.full_like(num, float("nan")),
                )
                null_g[b0:b1] = torch.nanmean(r_mat, dim=1)
            return obs_mean, null_g.cpu().numpy()

    null_means = np.empty(P_total, dtype=np.float64)
    for b0 in range(0, P_total, chunk_size):
        b1 = min(P_total, b0 + chunk_size)
        pi_chunk = perm_idx[b0:b1]  # (B, 2109)

        # Denominator norm of y_prime[pi_chunk][:, present_pos] via missing complement (<=108 rows!)
        if len(missing_pos) == 0:
            den = np.sqrt(np.maximum(total_y2, 0.0))  # (1, D)
            den = np.broadcast_to(den, (b1 - b0, D))
        else:
            miss_idx = pi_chunk[:, missing_pos]  # (B, M_s)
            y_miss = y_prime[miss_idx]  # (B, M_s, D)
            s1 = -np.sum(y_miss, axis=1)  # sum over present = 0 - sum over missing
            s2 = total_y2 - np.sum(y_miss * y_miss, axis=1)
            var_num = s2 - (s1 * s1) / float(N_s)
            den = np.where(var_num > 1e-28, np.sqrt(np.maximum(var_num, 0.0)), np.nan)

        pres_idx = pi_chunk[:, present_pos]  # (B, N_s)
        y_pres = y_prime[pres_idx]  # (B, N_s, D)
        num = np.einsum("bnd,nd->bd", y_pres, p_tilde, optimize=True)

        valid = (~const_p[None, :]) & np.isfinite(den) & (den > 0.0)
        r_mat = np.full((b1 - b0, D), np.nan, dtype=np.float64)
        np.divide(num, np.where(valid, den, 1.0), out=r_mat, where=valid)
        null_means[b0:b1] = np.nanmean(r_mat, axis=1)

    return obs_mean, null_means


# S6 display codes & names (following 01_integrated_document.md & 04_claude_code_workorder.md)
S6_META: List[Tuple[str, str, str]] = [
    ("brain_only", "A-1", "A-1: Brain → Emotion"),
    ("brain_only_distill", "A-2", "A-2: Brain → Emotion [distillation]"),
    ("brain_only_featdec", "B-1", "B-1: Brain → Emotion + Vision + Caption"),
    ("brain_decoded", "C-1", "C-1: Brain + Decoded Feature → Emotion"),
    ("brain_decoded_additive", "C-1_additive", "C-1 (더하기 head): Brain + Decoded Feature → Emotion"),
    ("brain_decoded_grad", "C-1_grad", "C-1 (손실 흐름 허용판): Brain + Decoded Feature → Emotion"),
    ("brain_decoded_distill", "C-2", "C-2: Brain + Decoded Feature → Emotion [distillation]"),
    ("brain_decoded_sep", "D-1", "D-1: Brain + Decoded Feature → Emotion (별도 encoder)"),
    ("brain_decoded_sep_distill", "D-2", "D-2: Brain + Decoded Feature → Emotion [distillation] (별도 encoder)"),
    ("brain_features_only", "D-3", "D-3: Decoded Feature → Emotion (OOF)"),
    ("brain_features_only_paired", "D-3_paired", "D-3 (짝 앙상블): Decoded Feature → Emotion"),
    ("brain_frozen_feature_encoder", "D-4", "D-4 (짝 앙상블): 고정 encoder 2 + 정서 head"),
    ("brain_only_repr_frozen", "E-고정", "E-고정: Brain → Emotion [표현 전달, 고정]"),
    ("brain_only_repr_trained", "E-학습", "E-학습: Brain → Emotion [표현 전달, 함께 학습]"),
    ("multimodal", "Multimodal_ref", "Multimodal Model [참고: 실제 Vision+Caption 시험 입력 포함, G16]"),
    ("control_label_smoothing", "ctrl_label_smoothing", "대조군: Brain → Emotion [label smoothing]"),
    ("control_stimulus_shuffle", "ctrl_stimulus_shuffle", "대조군: Brain → Emotion [섞은 예측 평정]"),
    ("control_feature_shuffle", "ctrl_feature_shuffle", "대조군: Brain → Emotion + Vision + Caption [섞은 특징]"),
    ("brain_only_pool", "A-1_pool", "A-1 (평균 pooling판): Brain → Emotion"),
    ("brain_decoded_pool", "C-1_pool", "C-1 (평균 pooling판): Brain + Decoded Feature → Emotion"),
]


@dataclass
class EmotionModelData:
    model_id: str
    family: str
    code: str
    display_name: str
    status: str = "ok"
    is_multiseed: bool = False
    is_video_level: bool = False
    is_single_pair_avg: bool = False
    # participant -> (n_seeds, 2109, 34) for normal models; or (n_seeds, 4, 2109, 34) for single-pair avg
    preds_sub: Dict[str, np.ndarray] = field(default_factory=dict)
    # (1, 2109, 34) for video-level models evaluated on all 2,109 dev videos
    preds_all: Optional[np.ndarray] = None


def run_unit_assertions(
    split: pd.DataFrame,
    y_em: np.ndarray,
    present_masks: Dict[str, np.ndarray],
    W_all: np.ndarray,
    boot_draws: np.ndarray,
    unique_cids: np.ndarray,
    perm_idx: np.ndarray,
) -> Dict[str, float]:
    """Run mathematical unit tests verifying BLAS bootstrap, permutation, Holm, and BH-FDR."""
    # 1. Holm & BH-FDR sanity checks
    p_test = np.array([0.001, 0.02, 0.01, 0.20, np.nan])
    h_test = holm_adjust(p_test)
    assert np.allclose(h_test[:4], [0.004, 0.04, 0.03, 0.20], atol=1e-12) and np.isnan(h_test[4])
    q_test = bh_fdr(p_test)
    assert np.allclose(q_test[:4], [0.004, 0.026666666667, 0.02, 0.20], atol=1e-9) and np.isnan(q_test[4])

    # 2. Weighted bootstrap Pearson vs explicit cluster row-expansion c.pearson
    rng_u = np.random.default_rng(20261114)
    fake_pred = rng_u.uniform(0.0, 1.0, size=(len(split), 34))
    sub = "sub-05"  # most missing blocks (2,001 videos)
    pmask = present_masks[sub]
    W_sub = W_all[:25, pmask]
    W_sum = W_sub.sum(axis=1, keepdims=True)
    Y_sub = y_em[pmask]
    Y_c = Y_sub - Y_sub.mean(axis=0, keepdims=True)
    r_fast = weighted_boot_pearson_2d(W_sub, fake_pred[pmask], Y_c, W_sub @ Y_c, W_sub @ (Y_c * Y_c), W_sum)

    cid_to_rows = {int(cid): np.flatnonzero((split["canonical_id"].to_numpy() == cid) & pmask) for cid in unique_cids}
    max_boot_diff = 0.0
    for b in range(25):
        rows_exp = np.concatenate([cid_to_rows[int(unique_cids[c_i])] for c_i in boot_draws[b]])
        r_ref = c.pearson(y_em[rows_exp], fake_pred[rows_exp])
        diff = float(np.nanmax(np.abs(r_fast[b] - r_ref)))
        max_boot_diff = max(max_boot_diff, diff)
    if max_boot_diff > 1e-12:
        raise AssertionError(f"Weighted bootstrap Pearson mismatch: {max_boot_diff}")

    # 3. Fast exact permutation Pearson vs explicit c.pearson
    obs_m, null_m = fast_exact_perm_mean_r(fake_pred[pmask], y_em, pmask, perm_idx[:20], chunk_size=7)
    ref_obs = float(np.nanmean(c.pearson(y_em[pmask], fake_pred[pmask])))
    max_perm_diff = abs(obs_m - ref_obs)
    for b in range(20):
        ref_b = float(np.nanmean(c.pearson(y_em[perm_idx[b]][pmask], fake_pred[pmask])))
        max_perm_diff = max(max_perm_diff, abs(float(null_m[b]) - ref_b))
    if max_perm_diff > 1e-12:
        raise AssertionError(f"Fast permutation Pearson mismatch: {max_perm_diff}")

    return {
        "unit_weighted_boot_pearson_max_abs_diff": max_boot_diff,
        "unit_fast_perm_pearson_max_abs_diff": max_perm_diff,
    }


def build_bootstrap_and_permutations(split: pd.DataFrame) -> Tuple[
    np.ndarray, np.ndarray, np.ndarray, int, np.ndarray, np.ndarray, int
]:
    """Build exact O4(3) canonical_id bootstrap weights and O4(1) within-run permutations."""
    n_dev = len(split)
    unique_cids = np.sort(split["canonical_id"].unique())
    assert len(unique_cids) == 2108, f"Expected 2108 canonical_id clusters, got {len(unique_cids)}"
    cid_to_idx = {int(cid): i for i, cid in enumerate(unique_cids.tolist())}
    row_cluster = np.array([cid_to_idx[int(cid)] for cid in split["canonical_id"].tolist()], dtype=np.int64)

    vid_to_row = {int(v): i for i, v in enumerate(split["video_id"].tolist())}
    assert row_cluster[vid_to_row[1349]] == row_cluster[vid_to_row[1363]]

    boot_seed_int = int.from_bytes(hashlib.sha256(BOOT_SEED_BYTES).digest()[:8], "big")
    rng_boot = np.random.default_rng(boot_seed_int)
    boot_draws = rng_boot.integers(0, len(unique_cids), size=(N_BOOT, len(unique_cids)))

    M_cluster = np.zeros((N_BOOT, len(unique_cids)), dtype=np.float64)
    row_grid = np.broadcast_to(np.arange(N_BOOT)[:, None], boot_draws.shape)
    np.add.at(M_cluster, (row_grid, boot_draws), 1.0)
    assert np.all(M_cluster.sum(axis=1) == len(unique_cids))
    W_all = M_cluster[:, row_cluster]  # (10000, 2109), 1349 and 1363 get identical draw counts!
    assert np.array_equal(W_all[:, vid_to_row[1349]], W_all[:, vid_to_row[1363]])

    # O4(1): Within-(fold, run_index) permutations
    perm_seed_int = int.from_bytes(hashlib.sha256(PERM_SEED_BYTES).digest()[:8], "big")
    rng_perm = np.random.default_rng(perm_seed_int)

    dup_cids = set(split["canonical_id"].value_counts().loc[lambda s: s > 1].index.tolist())
    assert dup_cids == {1349}
    dup_rows = set(np.flatnonzero(split["canonical_id"].isin(dup_cids)).tolist())
    assert dup_rows == {vid_to_row[1349], vid_to_row[1363]}

    perm_idx = np.broadcast_to(np.arange(n_dev, dtype=np.int32)[None, :], (N_PERM, n_dev)).copy()
    blocks = split.groupby(["fold", "run_index"], sort=True).indices
    assert len(blocks) == 61
    for (_, _), idx_arr in blocks.items():
        movable = np.array([i for i in idx_arr if int(i) not in dup_rows], dtype=np.int32)
        if len(movable) > 1:
            rnd = rng_perm.random((N_PERM, len(movable)))
            order = np.argsort(rnd, axis=1)
            perm_idx[:, movable] = movable[order]

    # Sensitivity check: free within-run permutation of (1349, 1363)
    rng_perm_free = np.random.default_rng(perm_seed_int)
    perm_idx_free = np.broadcast_to(np.arange(n_dev, dtype=np.int32)[None, :], (N_PERM, n_dev)).copy()
    for (_, _), idx_arr in blocks.items():
        movable = np.asarray(idx_arr, dtype=np.int32)
        if len(movable) > 1:
            rnd = rng_perm_free.random((N_PERM, len(movable)))
            order = np.argsort(rnd, axis=1)
            perm_idx_free[:, movable] = movable[order]

    fold_arr = split["fold"].to_numpy()
    run_arr = split["run_index"].to_numpy()
    assert np.all(fold_arr[perm_idx] == fold_arr[None, :])
    assert np.all(run_arr[perm_idx] == run_arr[None, :])
    assert np.all(perm_idx[:, vid_to_row[1349]] == vid_to_row[1349])
    assert np.all(perm_idx[:, vid_to_row[1363]] == vid_to_row[1363])

    return unique_cids, boot_draws, W_all, boot_seed_int, perm_idx, perm_idx_free, perm_seed_int


def collect_all_emotion_models(
    split: pd.DataFrame,
    y_em: np.ndarray,
    present_masks: Dict[str, np.ndarray],
) -> Tuple[Dict[str, EmotionModelData], Dict[str, np.ndarray], np.ndarray, Dict[str, object]]:
    """Load and verify all S6, S5, and S4 emotion predictions aligned to split (2,109 rows)."""
    n_dev = len(split)
    vid_to_row = {int(v): i for i, v in enumerate(split["video_id"].tolist())}
    fold_arr = split["fold"].to_numpy()
    models: Dict[str, EmotionModelData] = {}
    checks: Dict[str, object] = {}

    # 1. S6 Brain Models (20 emotion conditions + 2 single-pair average variants)
    single_pair_models: Dict[str, EmotionModelData] = {}
    for cond, code, disp in S6_META:
        cfg = S.CONDITIONS[cond]
        em = EmotionModelData(
            model_id=f"s6_{cond}",
            family="S6_brain",
            code=code,
            display_name=disp,
            status="ok",
            is_multiseed=True,
            is_video_level=False,
            is_single_pair_avg=False,
            preds_sub={sub: np.full((3, n_dev, N_EMOTIONS), np.nan, dtype=np.float64) for sub in PARTICIPANTS},
        )
        sp_em: Optional[EmotionModelData] = None
        if cfg.paired:
            sp_code = f"{code}_single_pair"
            sp_disp = disp.replace("짝 앙상블", "짝 단일 평균, 5-A")
            sp_em = EmotionModelData(
                model_id=f"s6_{cond}_single_pair",
                family="S6_brain",
                code=sp_code,
                display_name=sp_disp,
                status="ok",
                is_multiseed=True,
                is_video_level=False,
                is_single_pair_avg=True,
                preds_sub={sub: np.full((3, 4, n_dev, N_EMOTIONS), np.nan, dtype=np.float64) for sub in PARTICIPANTS},
            )

        for k in range(1, N_FOLDS + 1):
            fdir = S.OUT / f"outer_fold{k}"
            sel = json.loads((fdir / cond / "selected.json").read_text())
            for s_idx, s_key in enumerate(("0", "1", "2")):
                rel = sel["seeds"][s_key]
                pred_path = fdir / rel / ("ensemble/test_pred.npz" if cfg.paired else "test_pred.npz")
                z = np.load(pred_path)
                p_part = z["participant"].astype(str)
                p_vid = z["video_id"].astype(np.int64)
                p_val = z["p"].astype(np.float64)
                p_pairs = z["p_pairs"].astype(np.float64) if cfg.paired else None

                for sub in PARTICIPANTS:
                    at = np.flatnonzero(p_part == sub)
                    expected_rows = np.flatnonzero((fold_arr == k) & present_masks[sub])
                    dest = np.array([vid_to_row[int(v)] for v in p_vid[at]], dtype=np.int64)
                    if not np.array_equal(np.sort(dest), expected_rows):
                        raise ValueError(f"Row mismatch in {pred_path} for {sub} fold {k}")
                    em.preds_sub[sub][s_idx, dest, :] = p_val[at]
                    if cfg.paired and sp_em is not None and p_pairs is not None:
                        for j_pair in range(4):
                            sp_em.preds_sub[sub][s_idx, j_pair, dest, :] = p_pairs[j_pair, at, :]

        for sub in PARTICIPANTS:
            pmask = present_masks[sub]
            if not np.isfinite(em.preds_sub[sub][:, pmask, :]).all():
                raise ValueError(f"Non-finite predictions in {cond} for {sub}")
            if sp_em is not None and not np.isfinite(sp_em.preds_sub[sub][:, :, pmask, :]).all():
                raise ValueError(f"Non-finite single-pair predictions in {cond} for {sub}")

        models[em.model_id] = em
        if sp_em is not None:
            single_pair_models[sp_em.model_id] = sp_em

    # Insert single-pair variants right after their paired ensemble counterparts
    ordered_models: Dict[str, EmotionModelData] = {}
    for mid, mobj in models.items():
        ordered_models[mid] = mobj
        if f"{mid}_single_pair" in single_pair_models:
            ordered_models[f"{mid}_single_pair"] = single_pair_models[f"{mid}_single_pair"]
    models = ordered_models

    # Verify cross-fold pair-slot invariance for D-4 single-pair average
    rng_slot = np.random.default_rng(42)
    d4_sp = models["s6_brain_frozen_feature_encoder_single_pair"]
    slot_vals = []
    for _ in range(100):
        # Randomly permute pair slots 0..3 independently within each fold k=1..6 on seed 0
        acc = 0.0
        for sub in PARTICIPANTS:
            pmask = present_masks[sub]
            mixed = np.empty((4, n_dev, N_EMOTIONS), dtype=np.float64)
            mixed[:] = np.nan
            for k in range(1, N_FOLDS + 1):
                frows = np.flatnonzero((fold_arr == k) & pmask)
                perm4 = rng_slot.permutation(4)
                mixed[:, frows, :] = d4_sp.preds_sub[sub][0, perm4][:, frows, :]
            pair_rs = [float(np.nanmean(c.pearson(y_em[pmask], mixed[j, pmask, :]))) for j in range(4)]
            acc += float(np.mean(pair_rs)) / len(PARTICIPANTS)
        slot_vals.append(acc)
    checks["d4_single_pair_seed0_slot_permutation_sd"] = float(np.std(slot_vals, ddof=1))
    checks["d4_single_pair_seed0_slot_permutation_range"] = float(np.max(slot_vals) - np.min(slot_vals))

    # 2. S5 Participant-Specific Baselines + D_k training mean
    m_dk_sub = {sub: np.full((n_dev, N_EMOTIONS), np.nan, dtype=np.float64) for sub in PARTICIPANTS}
    m_dk_all = np.full((n_dev, N_EMOTIONS), np.nan, dtype=np.float64)
    for k in range(1, N_FOLDS + 1):
        m_dk_all[fold_arr == k] = y_em[fold_arr != k].mean(axis=0)

    def make_s5_det(mid: str, code: str, disp: str) -> EmotionModelData:
        return EmotionModelData(
            model_id=mid,
            family="S5_baseline",
            code=code,
            display_name=disp,
            status="ok",
            is_multiseed=False,
            is_video_level=False,
            preds_sub={sub: np.full((1, n_dev, N_EMOTIONS), np.nan, dtype=np.float64) for sub in PARTICIPANTS},
        )

    def make_s5_3seed(mid: str, code: str, disp: str) -> EmotionModelData:
        return EmotionModelData(
            model_id=mid,
            family="S5_baseline",
            code=code,
            display_name=disp,
            status="ok",
            is_multiseed=True,
            is_video_level=False,
            preds_sub={sub: np.full((3, n_dev, N_EMOTIONS), np.nan, dtype=np.float64) for sub in PARTICIPANTS},
        )

    em_ridge_main = make_s5_det("s5_ridge_main", "ridge_main", "S5 Ridge (주 비교판, emotion_main)")
    em_ridge_lit = make_s5_det("s5_ridge_literature", "ridge_literature", "S5 Ridge (선행연구 안쪽 5겹판, emotion_literature)")
    em_dk_mean = make_s5_det("s5_dk_mean", "dk_mean", "S5 D_k 평균 프로필 기준선 (mean_prediction)")
    em_soft_bce = make_s5_det("s5_soft_bce", "soft_bce", "S5 Linear + Soft BCE")
    em_h2020 = make_s5_det("s5_h2020", "h2020", "S5 Horikawa et al. (2020) ROI Ensemble Ridge")
    em_signal = make_s5_det("s5_signal", "signal", "S5 블록 신호 평균·표준편차 기준선 (signal, I7)")
    em_mlp = make_s5_3seed("s5_mlp", "mlp", "S5 얕은 MLP 기준선 (3 seeds)")
    em_ged = make_s5_3seed("s5_ged", "ged", "S5 외부 기준선: GED (3 seeds)")
    em_emogrowth = make_s5_3seed("s5_emogrowth", "emogrowth", "S5 외부 기준선: EmoGrowth (3 seeds)")

    max_mdk_diff = 0.0
    for s_tag in d5.HK:
        sub = f"sub-{s_tag}"
        pmask = present_masks[sub]
        for k in range(1, N_FOLDS + 1):
            expected_rows = np.flatnonzero((fold_arr == k) & pmask)

            def load_align(path: Path) -> Tuple[dict, np.ndarray]:
                z = np.load(path)
                dest = np.array([vid_to_row[int(v)] for v in z["video_id"].tolist()], dtype=np.int64)
                if not np.array_equal(np.sort(dest), expected_rows):
                    raise ValueError(f"Row mismatch in {path}")
                return z, dest

            zr, dest = load_align(d5.OUT / f"ridge/sub-{s_tag}_fold{k}/pred.npz")
            em_ridge_main.preds_sub[sub][0, dest, :] = zr["emotion_main"].astype(np.float64)
            em_ridge_lit.preds_sub[sub][0, dest, :] = zr["emotion_literature"].astype(np.float64)
            mp = zr["mean_prediction"].astype(np.float64)
            em_dk_mean.preds_sub[sub][0, dest, :] = mp[None, :]
            m_dk_sub[sub][dest, :] = mp[None, :]
            ref_mp = y_em[(fold_arr != k) & pmask].mean(axis=0)
            max_mdk_diff = max(max_mdk_diff, float(np.max(np.abs(mp - ref_mp))))

            zb, dest = load_align(d5.OUT / f"soft_bce/sub-{s_tag}_fold{k}/pred.npz")
            em_soft_bce.preds_sub[sub][0, dest, :] = zb["pred"].astype(np.float64)

            zh, dest = load_align(d5.OUT / f"h2020/sub-{s_tag}_fold{k}/pred.npz")
            em_h2020.preds_sub[sub][0, dest, :] = zh["pred"].astype(np.float64)

            zs, dest = load_align(d5.OUT / f"signal/sub-{s_tag}_fold{k}/pred.npz")
            em_signal.preds_sub[sub][0, dest, :] = zs["pred"].astype(np.float64)

            zm, dest = load_align(d5.OUT / f"mlp/sub-{s_tag}_fold{k}/pred.npz")
            em_mlp.preds_sub[sub][:, dest, :] = zm["emotion_seeds"].astype(np.float64)

            zg, dest = load_align(d5.OUT / f"ged/sub-{s_tag}_fold{k}/pred.npz")
            em_ged.preds_sub[sub][:, dest, :] = zg["emotion_seeds"].astype(np.float64)

            ze, dest = load_align(d5.OUT / f"emogrowth/sub-{s_tag}_fold{k}/pred.npz")
            em_emogrowth.preds_sub[sub][:, dest, :] = ze["emotion_seeds"].astype(np.float64)

    if max_mdk_diff > 1e-6:
        raise AssertionError(f"D_k mean_prediction mismatch: {max_mdk_diff}")
    checks["s5_dk_mean_prediction_max_abs_diff"] = max_mdk_diff

    for obj in (
        em_ridge_main,
        em_ridge_lit,
        em_dk_mean,
        em_soft_bce,
        em_h2020,
        em_mlp,
        em_ged,
        em_emogrowth,
        em_signal,
    ):
        models[obj.model_id] = obj

    # Check optional / missing mlbvae
    mlbvae_dir = d5.OUT / "mlbvae"
    if mlbvae_dir.exists() and (mlbvae_dir / "sub-01_fold1/pred.npz").exists():
        z_probe = np.load(mlbvae_dir / "sub-01_fold1/pred.npz")
        has_seeds = "emotion_seeds" in z_probe.files
        em_mlb = (
            make_s5_3seed("s5_mlbvae", "mlbvae", "S5 외부 기준선: ML-BVAE")
            if has_seeds
            else make_s5_det("s5_mlbvae", "mlbvae", "S5 외부 기준선: ML-BVAE")
        )
        for s_tag in d5.HK:
            sub = f"sub-{s_tag}"
            for k in range(1, N_FOLDS + 1):
                zv = np.load(mlbvae_dir / f"sub-{s_tag}_fold{k}/pred.npz")
                dest = np.array([vid_to_row[int(v)] for v in zv["video_id"].tolist()], dtype=np.int64)
                if has_seeds:
                    em_mlb.preds_sub[sub][:, dest, :] = zv["emotion_seeds"].astype(np.float64)
                else:
                    em_mlb.preds_sub[sub][0, dest, :] = zv["pred"].astype(np.float64)
        models["s5_mlbvae"] = em_mlb
        checks["s5_mlbvae_status"] = "loaded"
    else:
        models["s5_mlbvae"] = EmotionModelData(
            model_id="s5_mlbvae",
            family="S5_baseline",
            code="mlbvae",
            display_name="S5 외부 기준선: ML-BVAE [미실행/중단: 산출물 없음]",
            status="not_run_missing_artifact",
            is_multiseed=True,
            is_video_level=False,
        )
        checks["s5_mlbvae_status"] = "missing_artifact_in_s5_ridge"

    # 3. Video-Level S5 Baselines & S4 No-Brain Feature Models (evaluated on both N11 participant-matched & all 2,109)
    def load_video_model(
        mid: str,
        family: str,
        code: str,
        disp: str,
        fold_path_fn,
        key: str,
    ) -> EmotionModelData:
        p_all = np.full((1, n_dev, N_EMOTIONS), np.nan, dtype=np.float64)
        for k in range(1, N_FOLDS + 1):
            path = fold_path_fn(k)
            z = np.load(path)
            dest = np.array([vid_to_row[int(v)] for v in z["video_id"].tolist()], dtype=np.int64)
            expected = np.flatnonzero(fold_arr == k)
            if not np.array_equal(np.sort(dest), expected):
                raise ValueError(f"Video fold mismatch in {path}")
            p_all[0, dest, :] = z[key].astype(np.float64)
        assert np.isfinite(p_all).all()
        p_sub = {}
        for sub in PARTICIPANTS:
            arr = np.full((1, n_dev, N_EMOTIONS), np.nan, dtype=np.float64)
            pmask = present_masks[sub]
            arr[0, pmask, :] = p_all[0, pmask, :]
            p_sub[sub] = arr
        return EmotionModelData(
            model_id=mid,
            family=family,
            code=code,
            display_name=disp,
            status="ok",
            is_multiseed=False,
            is_video_level=True,
            preds_sub=p_sub,
            preds_all=p_all,
        )

    models["s5_video_length"] = load_video_model(
        "s5_video_length", "S5_video", "video_length", "S5 영상 길이 기준선 (log duration ridge, N21/O23)",
        lambda k: d5.OUT / f"video/length_fold{k}/pred.npz", "pred",
    )
    models["s5_video_lowlevel"] = load_video_model(
        "s5_video_lowlevel", "S5_video", "video_lowlevel", "S5 저수준 시각·음향 12차원 기준선 (lowlevel ridge, O23)",
        lambda k: d5.OUT / f"video/lowlevel_fold{k}/pred.npz", "pred",
    )
    models["s4_stimulus"] = load_video_model(
        "s4_stimulus", "S4_nobrain", "stimulus_model", "S4 Stimulus Model (선택된 주 모델, V-JEPA2 + DeBERTa)",
        lambda k: c.OUT / f"stimulus/fold{k}/test_pred.npz", "p",
    )
    models["s4_stimulus_additive"] = load_video_model(
        "s4_stimulus_additive", "S4_nobrain", "stimulus_additive", "S4 Stimulus Model (더하기판, additive_p)",
        lambda k: c.OUT / f"stimulus/fold{k}/test_pred.npz", "additive_p",
    )
    models["s4_stimulus_interaction"] = load_video_model(
        "s4_stimulus_interaction", "S4_nobrain", "stimulus_interaction", "S4 Stimulus Model (상호작용판, interaction_p)",
        lambda k: c.OUT / f"stimulus/fold{k}/test_pred.npz", "interaction_p",
    )
    models["s4_noemo"] = load_video_model(
        "s4_noemo", "S4_nobrain", "stimulus_noemo", "S4 Stimulus Model (정서어 제거 캡션판, 3-4)",
        lambda k: c.OUT / f"noemo/fold{k}/test_pred.npz", "p",
    )
    for bname, bdisp in [
        ("videomae", "S4 대체 특징 기준선: VideoMAE + DeBERTa"),
        ("timesformer", "S4 대체 특징 기준선: TimeSformer + DeBERTa"),
        ("clip", "S4 대체 특징 기준선: CLIP + DeBERTa"),
        ("mpnet", "S4 대체 특징 기준선: V-JEPA2 + MPNet"),
    ]:
        models[f"s4_{bname}"] = load_video_model(
            f"s4_{bname}", "S4_nobrain", f"s4_{bname}", bdisp,
            lambda k, bn=bname: c.OUT / f"baseline/{bn}_fold{k}/test_pred.npz", "p",
        )

    # Cross-check S4 Stimulus Model all-dev r against precomputed s4_no_brain/summary/feature_model_test_r.tsv
    s4_ref = pd.read_csv(c.OUT / "summary/feature_model_test_r.tsv", sep="\t")
    stim_r_check = c.pearson(y_em, models["s4_stimulus"].preds_all[0])
    s4_max_diff = float(np.max(np.abs(stim_r_check - s4_ref["r"].to_numpy())))
    if s4_max_diff > 1e-5:
        raise AssertionError(f"S4 Stimulus Model cross-check failed: {s4_max_diff}")
    checks["s4_stimulus_vs_summary_tsv_max_abs_diff"] = s4_max_diff

    return models, m_dk_sub, m_dk_all, checks


def compute_subset_primary_stats(
    em: EmotionModelData,
    y_em: np.ndarray,
    present_masks: Dict[str, np.ndarray],
    subset_mask: np.ndarray,
    W_all: Optional[np.ndarray] = None,
) -> dict:
    """Compute pooled Pearson r, Fisher-z mean, n_not_computable, and optional 10k bootstrap CI on subset_mask."""
    if em.status != "ok":
        return {"status": em.status}

    n_seeds = 3 if em.is_multiseed else 1
    out: dict = {"status": "ok"}

    # Per-participant observed per-seed emotion r: shape (5, n_seeds, 34)
    obs_em = np.full((len(PARTICIPANTS), n_seeds, N_EMOTIONS), np.nan, dtype=np.float64)
    obs_mean34 = np.full((len(PARTICIPANTS), n_seeds), np.nan, dtype=np.float64)
    obs_fz = np.full((len(PARTICIPANTS), n_seeds), np.nan, dtype=np.float64)
    n_nc = np.zeros((len(PARTICIPANTS), n_seeds), dtype=np.int64)
    n_vids = np.zeros(len(PARTICIPANTS), dtype=np.int64)

    boot_mean34 = (
        np.full((len(PARTICIPANTS), n_seeds, W_all.shape[0]), np.nan, dtype=np.float64)
        if W_all is not None
        else None
    )

    for p_i, sub in enumerate(PARTICIPANTS):
        mask = present_masks[sub] & subset_mask
        n_vids[p_i] = int(mask.sum())
        y_s = y_em[mask]

        if W_all is not None:
            W_s = W_all[:, mask]
            W_sum = W_s.sum(axis=1, keepdims=True)
            Y_c = y_s - y_s.mean(axis=0, keepdims=True)
            Sw_Y = W_s @ Y_c
            Sw_Y2 = W_s @ (Y_c * Y_c)

        for s_i in range(n_seeds):
            if not em.is_single_pair_avg:
                x_s = em.preds_sub[sub][s_i, mask, :]
                r_vec = c.pearson(y_s, x_s)
                obs_em[p_i, s_i] = r_vec
                obs_mean34[p_i, s_i] = float(np.nanmean(r_vec))
                obs_fz[p_i, s_i] = fisher_z_mean_1d(r_vec)
                n_nc[p_i, s_i] = int(np.isnan(r_vec).sum())
                if W_all is not None and boot_mean34 is not None:
                    rb = weighted_boot_pearson_2d(W_s, x_s, Y_c, Sw_Y, Sw_Y2, W_sum)
                    boot_mean34[p_i, s_i] = np.nanmean(rb, axis=1)
            else:
                pair_r_vecs = []
                pair_means = []
                pair_fzs = []
                pair_ncs = []
                pair_boots = []
                for j in range(4):
                    x_sj = em.preds_sub[sub][s_i, j, mask, :]
                    rj = c.pearson(y_s, x_sj)
                    pair_r_vecs.append(rj)
                    pair_means.append(float(np.nanmean(rj)))
                    pair_fzs.append(fisher_z_mean_1d(rj))
                    pair_ncs.append(int(np.isnan(rj).sum()))
                    if W_all is not None:
                        rbj = weighted_boot_pearson_2d(W_s, x_sj, Y_c, Sw_Y, Sw_Y2, W_sum)
                        pair_boots.append(np.nanmean(rbj, axis=1))
                obs_em[p_i, s_i] = np.nanmean(np.stack(pair_r_vecs, axis=0), axis=0)
                obs_mean34[p_i, s_i] = float(np.mean(pair_means))
                obs_fz[p_i, s_i] = float(np.mean(pair_fzs))
                n_nc[p_i, s_i] = int(np.max(pair_ncs))
                if W_all is not None and boot_mean34 is not None:
                    boot_mean34[p_i, s_i] = np.mean(np.stack(pair_boots, axis=0), axis=0)

    # 5-participant mean per seed, then across seeds (Rule G14)
    m5_seeds = obs_mean34.mean(axis=0)  # (n_seeds,)
    m5_fz_seeds = obs_fz.mean(axis=0)
    out["n_videos_mean5sub"] = float(n_vids.mean())
    out["mean_5sub"] = float(m5_seeds.mean())
    out["mean_5sub_fisher_z"] = float(m5_fz_seeds.mean())
    out["mean_5sub_n_not_computable_max"] = int(n_nc.max())
    if em.is_multiseed:
        for s_i in range(3):
            out[f"mean_5sub_seed{s_i}"] = float(m5_seeds[s_i])
        out["mean_5sub_seed_sd"] = float(np.std(m5_seeds, ddof=1))
    else:
        out["mean_5sub_seed0"] = float(m5_seeds[0])
        out["mean_5sub_seed1"] = float("nan")
        out["mean_5sub_seed2"] = float("nan")
        out["mean_5sub_seed_sd"] = float("nan")

    if boot_mean34 is not None:
        # Average over seeds (per G14 score mean) and over 5 participants per bootstrap draw
        boot_sub = boot_mean34.mean(axis=1)  # (5, B)
        boot_m5 = boot_sub.mean(axis=0)  # (B,)
        ci_l, ci_h = basic_ci(out["mean_5sub"], boot_m5)
        out["mean_5sub_ci_low"] = ci_l
        out["mean_5sub_ci_high"] = ci_h
        out["_boot_sub"] = boot_sub  # (5, B)
        out["_boot_m5"] = boot_m5  # (B,)

    for p_i, sub in enumerate(PARTICIPANTS):
        s_vals = obs_mean34[p_i]
        out[f"{sub}_n_videos"] = int(n_vids[p_i])
        out[sub] = float(s_vals.mean())
        out[f"{sub}_fisher_z"] = float(obs_fz[p_i].mean())
        out[f"{sub}_n_not_computable"] = int(n_nc[p_i].max())
        if em.is_multiseed:
            for s_i in range(3):
                out[f"{sub}_seed{s_i}"] = float(s_vals[s_i])
            out[f"{sub}_seed_sd"] = float(np.std(s_vals, ddof=1))
        else:
            out[f"{sub}_seed0"] = float(s_vals[0])
            out[f"{sub}_seed1"] = float("nan")
            out[f"{sub}_seed2"] = float("nan")
            out[f"{sub}_seed_sd"] = float("nan")
        if boot_mean34 is not None:
            cl, ch = basic_ci(out[sub], boot_mean34[p_i].mean(axis=0))
            out[f"{sub}_ci_low"] = cl
            out[f"{sub}_ci_high"] = ch

    # All-dev (2,109) evaluation for video-only / S4 models
    if em.is_video_level and em.preds_all is not None:
        mask_all = subset_mask
        y_a = y_em[mask_all]
        x_a = em.preds_all[0, mask_all, :]
        r_a = c.pearson(y_a, x_a)
        out["all_dev_n_videos"] = int(mask_all.sum())
        out["all_dev_r"] = float(np.nanmean(r_a))
        out["all_dev_fisher_z"] = fisher_z_mean_1d(r_a)
        out["all_dev_n_not_computable"] = int(np.isnan(r_a).sum())
        if W_all is not None:
            W_a = W_all[:, mask_all]
            W_sum_a = W_a.sum(axis=1, keepdims=True)
            Y_ca = y_a - y_a.mean(axis=0, keepdims=True)
            rb_a = weighted_boot_pearson_2d(W_a, x_a, Y_ca, W_a @ Y_ca, W_a @ (Y_ca * Y_ca), W_sum_a)
            boot_a = np.nanmean(rb_a, axis=1)
            cl_a, ch_a = basic_ci(out["all_dev_r"], boot_a)
            out["all_dev_ci_low"] = cl_a
            out["all_dev_ci_high"] = ch_a
    else:
        out["all_dev_n_videos"] = np.nan
        out["all_dev_r"] = np.nan
        out["all_dev_fisher_z"] = np.nan
        out["all_dev_n_not_computable"] = np.nan
        if W_all is not None:
            out["all_dev_ci_low"] = np.nan
            out["all_dev_ci_high"] = np.nan

    return out


def build_table1_and_table2(
    models: Dict[str, EmotionModelData],
    split: pd.DataFrame,
    y_em: np.ndarray,
    present_masks: Dict[str, np.ndarray],
    dur_s: np.ndarray,
    multi_window_ids: set,
    W_all: np.ndarray,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, dict]]:
    """Build s10_table1_primary_metrics and s10_table2_subsets_and_duration."""
    n_dev = len(split)
    all_mask = np.ones(n_dev, dtype=bool)
    t1_rows = []
    full_cache: Dict[str, dict] = {}

    for mid, em in models.items():
        base = {
            "model_id": em.model_id,
            "family": em.family,
            "code": em.code,
            "display_name": em.display_name,
            "status": em.status,
            "is_multiseed": em.is_multiseed,
            "is_video_level": em.is_video_level,
        }
        st = compute_subset_primary_stats(em, y_em, present_masks, all_mask, W_all=W_all)
        full_cache[mid] = st
        row = {**base, **{k: v for k, v in st.items() if not k.startswith("_")}}
        t1_rows.append(row)

    df_t1 = pd.DataFrame(t1_rows)

    # Subsets for Table 2
    in_all_5_mask = split["in_all_5"].to_numpy(dtype=bool)
    mw_mask = split["video_id"].isin(multi_window_ids).to_numpy(dtype=bool)
    sw_mask = ~mw_mask
    dur_le_8 = dur_s <= 8.0
    dur_8_16 = (dur_s > 8.0) & (dur_s <= 16.0)
    dur_gt_16 = dur_s > 16.0
    q33, q67 = np.quantile(dur_s, [1.0 / 3.0, 2.0 / 3.0])
    tert1 = dur_s <= q33
    tert2 = (dur_s > q33) & (dur_s <= q67)
    tert3 = dur_s > q67

    subsets = [
        ("all_dev_2109", "전체 개발 영상 (2,109개)", all_mask),
        ("in_all_5_1969", "5명 공통 영상 (in_all_5 == True, 1,969개, B7)", in_all_5_mask),
        ("window_excluded_2029", "단일 창 영상만 (다중 창 80개 제외, 2,029개, 3-2)", sw_mask),
        ("multi_window_only_80", "다중 창 영상만 (80개, 진단용)", mw_mask),
        ("dur_le_8s_1503", "영상 길이 <= 8초 (반복 제시 구간, 1,503개, 3-2)", dur_le_8),
        ("dur_gt8_le16s_521", "영상 길이 (8초, 16초] (521개, 3-2)", dur_8_16),
        ("dur_gt_16s_85", "영상 길이 > 16초 (85개, 3-2)", dur_gt_16),
        ("dur_tertile1_le3.00s", f"영상 길이 1삼분위 (<= {q33:.3f}초, {int(tert1.sum())}개)", tert1),
        ("dur_tertile2_3.00_to_6.85s", f"영상 길이 2삼분위 (({q33:.3f}, {q67:.3f}]초, {int(tert2.sum())}개)", tert2),
        ("dur_tertile3_gt6.85s", f"영상 길이 3삼분위 (> {q67:.3f}초, {int(tert3.sum())}개)", tert3),
    ]

    t2_rows = []
    for sub_id, sub_label, smask in subsets:
        for mid, em in models.items():
            if em.status != "ok":
                continue
            st = (
                full_cache[mid]
                if sub_id == "all_dev_2109"
                else compute_subset_primary_stats(em, y_em, present_masks, smask, W_all=W_all)
            )
            row = {
                "subset_id": sub_id,
                "subset_description": sub_label,
                "n_dev_videos_in_subset": int(smask.sum()),
                "model_id": em.model_id,
                "family": em.family,
                "code": em.code,
                "display_name": em.display_name,
                "is_multiseed": em.is_multiseed,
                **{k: v for k, v in st.items() if not k.startswith("_") and k != "status"},
            }
            t2_rows.append(row)

    df_t2 = pd.DataFrame(t2_rows)
    return df_t1, df_t2, full_cache


def eval_aux_single_pred(
    p: np.ndarray,
    y: np.ndarray,
    m_dk: np.ndarray,
    fold_vec: np.ndarray,
    Q_len: np.ndarray,
) -> Dict[str, float]:
    """Compute all 2-4 / N19 / O19 / O25 / N21 auxiliary metrics on one (N, 34) prediction matrix."""
    r_vec = c.pearson(y, p)
    primary_r = float(np.nanmean(r_vec))
    n_r_nc = int(np.isnan(r_vec).sum())

    # O25: error reduction vs D_k training mean
    sq_err = (y - p) ** 2
    sq_dk = (y - m_dk) ** 2
    sse_m = sq_err.sum(axis=0)
    sse_dk = sq_dk.sum(axis=0)
    er_vec = np.where(sse_dk > 0, 1.0 - sse_m / sse_dk, np.nan)
    err_red_dk = float(np.nanmean(er_vec))

    # 2-4: within-video profile correlation across 34 emotions + D_k mean profile baseline
    prof_r_vec = c.pearson(y.T, p.T)
    prof_dk_vec = c.pearson(y.T, m_dk.T)
    profile_r = float(np.nanmean(prof_r_vec))
    profile_r_dk = float(np.nanmean(prof_dk_vec))
    n_prof_nc = int(np.isnan(prof_r_vec).sum())

    # N19: zero vs positive rating errors, MAE sum over 34 emotions, R^2
    abs_err = np.abs(y - p)
    zero_mask = y == 0.0
    pos_mask = y > 0.0
    mae_zero = float(abs_err[zero_mask].mean())
    mae_pos = float(abs_err[pos_mask].mean())
    rmse_zero = float(np.sqrt(sq_err[zero_mask].mean()))
    rmse_pos = float(np.sqrt(sq_err[pos_mask].mean()))
    mae_sum_34 = float(abs_err.mean(axis=0).sum())

    sst_test = np.sum((y - y.mean(axis=0, keepdims=True)) ** 2, axis=0)
    r2_vec = np.where(sst_test > 0, 1.0 - sse_m / sst_test, np.nan)
    r2_mean = float(np.nanmean(r2_vec))

    # O19: within-fold pairwise identification accuracy on 34-dim emotion vectors
    fold_idents = []
    all_ident_scores = []
    for k in range(1, N_FOLDS + 1):
        fk = fold_vec == k
        sc = safe_identification_scores(p[fk], y[fk])
        fold_idents.append(float(np.nanmean(sc)))
        all_ident_scores.append(sc)
    ident_fold_mean = float(np.nanmean(fold_idents))
    ident_vid_mean = float(np.nanmean(np.concatenate(all_ident_scores)))

    # N21 / O25: partial Pearson r controlling for [1, log_duration]
    y_res = y - Q_len @ (Q_len.T @ y)
    p_res = p - Q_len @ (Q_len.T @ p)
    part_r_vec = c.pearson(y_res, p_res)
    partial_r_len = float(np.nanmean(part_r_vec))

    return {
        "primary_r": primary_r,
        "error_reduction_vs_dk_mean": err_red_dk,
        "profile_r": profile_r,
        "profile_r_dk_mean": profile_r_dk,
        "mae_zero_y": mae_zero,
        "mae_pos_y": mae_pos,
        "rmse_zero_y": rmse_zero,
        "rmse_pos_y": rmse_pos,
        "mae_sum_34": mae_sum_34,
        "r2_mean": r2_mean,
        "emotion_identification": ident_fold_mean,
        "emotion_identification_video_weighted": ident_vid_mean,
        "partial_r_controlling_log_length": partial_r_len,
        "n_r_not_computable": float(n_r_nc),
        "n_profile_not_computable": float(n_prof_nc),
    }


AUX_METRIC_NAMES = [
    "primary_r",
    "error_reduction_vs_dk_mean",
    "profile_r",
    "profile_r_dk_mean",
    "mae_zero_y",
    "mae_pos_y",
    "rmse_zero_y",
    "rmse_pos_y",
    "mae_sum_34",
    "r2_mean",
    "emotion_identification",
    "emotion_identification_video_weighted",
    "partial_r_controlling_log_length",
]


def build_table3_auxiliary(
    models: Dict[str, EmotionModelData],
    split: pd.DataFrame,
    y_em: np.ndarray,
    present_masks: Dict[str, np.ndarray],
    m_dk_sub: Dict[str, np.ndarray],
    m_dk_all: np.ndarray,
    log_dur: np.ndarray,
) -> pd.DataFrame:
    """Build s10_table3_auxiliary_metrics across all S6, S5, and S4 models."""
    fold_arr = split["fold"].to_numpy()
    Q_sub = {}
    for sub in PARTICIPANTS:
        pmask = present_masks[sub]
        X = np.column_stack([np.ones(int(pmask.sum()), dtype=np.float64), log_dur[pmask]])
        Q, _ = np.linalg.qr(X)
        Q_sub[sub] = Q
    X_all = np.column_stack([np.ones(len(split), dtype=np.float64), log_dur])
    Q_all, _ = np.linalg.qr(X_all)

    rows = []
    for mid, em in models.items():
        if em.status != "ok":
            rows.append({
                "model_id": em.model_id,
                "family": em.family,
                "code": em.code,
                "display_name": em.display_name,
                "status": em.status,
                "participant": "mean_5sub",
            })
            continue

        n_seeds = 3 if em.is_multiseed else 1
        # Store per-participant, per-seed dict
        sub_seed_vals: Dict[str, List[Dict[str, float]]] = {sub: [] for sub in PARTICIPANTS}
        for sub in PARTICIPANTS:
            pmask = present_masks[sub]
            y_s = y_em[pmask]
            mdk_s = m_dk_sub[sub][pmask]
            f_s = fold_arr[pmask]
            q_s = Q_sub[sub]

            for s_i in range(n_seeds):
                if not em.is_single_pair_avg:
                    d_val = eval_aux_single_pred(em.preds_sub[sub][s_i, pmask, :], y_s, mdk_s, f_s, q_s)
                else:
                    pair_dicts = [
                        eval_aux_single_pred(em.preds_sub[sub][s_i, j, pmask, :], y_s, mdk_s, f_s, q_s)
                        for j in range(4)
                    ]
                    d_val = {
                        k: float(np.mean([pd_j[k] for pd_j in pair_dicts]))
                        for k in pair_dicts[0].keys()
                    }
                sub_seed_vals[sub].append(d_val)

        # Emit mean_5sub row first, then sub-01..05
        m5_row = {
            "model_id": em.model_id,
            "family": em.family,
            "code": em.code,
            "display_name": em.display_name,
            "status": "ok",
            "is_multiseed": em.is_multiseed,
            "participant": "mean_5sub",
            "n_videos": float(np.mean([int(present_masks[s].sum()) for s in PARTICIPANTS])),
        }
        for mname in AUX_METRIC_NAMES:
            seed_m5 = [float(np.mean([sub_seed_vals[sub][s_i][mname] for sub in PARTICIPANTS])) for s_i in range(n_seeds)]
            m5_row[mname] = float(np.mean(seed_m5))
            if em.is_multiseed:
                m5_row[f"{mname}_seed_sd"] = float(np.std(seed_m5, ddof=1))
                for s_i in range(3):
                    m5_row[f"{mname}_seed{s_i}"] = seed_m5[s_i]
            else:
                m5_row[f"{mname}_seed_sd"] = np.nan
        m5_row["n_r_not_computable_max"] = int(max(sub_seed_vals[sub][s_i]["n_r_not_computable"] for sub in PARTICIPANTS for s_i in range(n_seeds)))
        m5_row["n_profile_not_computable_max"] = int(max(sub_seed_vals[sub][s_i]["n_profile_not_computable"] for sub in PARTICIPANTS for s_i in range(n_seeds)))
        rows.append(m5_row)

        for sub in PARTICIPANTS:
            s_row = {
                "model_id": em.model_id,
                "family": em.family,
                "code": em.code,
                "display_name": em.display_name,
                "status": "ok",
                "is_multiseed": em.is_multiseed,
                "participant": sub,
                "n_videos": int(present_masks[sub].sum()),
            }
            for mname in AUX_METRIC_NAMES:
                s_vals = [sub_seed_vals[sub][s_i][mname] for s_i in range(n_seeds)]
                s_row[mname] = float(np.mean(s_vals))
                if em.is_multiseed:
                    s_row[f"{mname}_seed_sd"] = float(np.std(s_vals, ddof=1))
                    for s_i in range(3):
                        s_row[f"{mname}_seed{s_i}"] = s_vals[s_i]
                else:
                    s_row[f"{mname}_seed_sd"] = np.nan
            s_row["n_r_not_computable_max"] = int(max(sub_seed_vals[sub][s_i]["n_r_not_computable"] for s_i in range(n_seeds)))
            s_row["n_profile_not_computable_max"] = int(max(sub_seed_vals[sub][s_i]["n_profile_not_computable"] for s_i in range(n_seeds)))
            rows.append(s_row)

        if em.is_video_level and em.preds_all is not None:
            d_all = eval_aux_single_pred(em.preds_all[0], y_em, m_dk_all, fold_arr, Q_all)
            a_row = {
                "model_id": em.model_id,
                "family": em.family,
                "code": em.code,
                "display_name": em.display_name,
                "status": "ok",
                "is_multiseed": False,
                "participant": "all_dev_2109",
                "n_videos": len(split),
            }
            for mname in AUX_METRIC_NAMES:
                a_row[mname] = d_all[mname]
                a_row[f"{mname}_seed_sd"] = np.nan
            a_row["n_r_not_computable_max"] = int(d_all["n_r_not_computable"])
            a_row["n_profile_not_computable_max"] = int(d_all["n_profile_not_computable"])
            rows.append(a_row)

    return pd.DataFrame(rows)


def fmt_r_or_nc(val: float) -> object:
    return "계산 불가" if not np.isfinite(val) else float(val)


def build_table4_per_emotion(
    models: Dict[str, EmotionModelData],
    label_map: pd.DataFrame,
    y_em: np.ndarray,
    present_masks: Dict[str, np.ndarray],
    W_all: np.ndarray,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Build s10_table4_per_emotion_34 (wide 34-row) and s10_table4b_per_emotion_long."""
    t4_specs = [
        ("s6_brain_only", "A-1"),
        ("s6_brain_only_distill", "A-2"),
        ("s6_brain_only_featdec", "B-1"),
        ("s6_brain_decoded", "C-1"),
        ("s6_brain_decoded_distill", "C-2"),
        ("s6_brain_decoded_additive", "C-1_additive"),
        ("s6_brain_decoded_sep", "D-1"),
        ("s6_brain_features_only", "D-3"),
        ("s6_brain_frozen_feature_encoder", "D-4"),
        ("s5_ridge_main", "ridge_main"),
        ("s5_h2020", "h2020"),
        ("s4_stimulus", "Stimulus_Model"),
    ]

    B = W_all.shape[0]
    # Precompute participant Y bootstrap stats
    W_sub_cache = {}
    for sub in PARTICIPANTS:
        pm = present_masks[sub]
        Ws = W_all[:, pm]
        Ws_sum = Ws.sum(axis=1, keepdims=True)
        Ys = y_em[pm]
        Yc = Ys - Ys.mean(axis=0, keepdims=True)
        W_sub_cache[sub] = (pm, Ws, Ws_sum, Ys, Yc, Ws @ Yc, Ws @ (Yc * Yc))

    # Compute per-emotion obs & boot distributions:
    # obs_sub[tag] -> (5, 34), seed_sd_sub[tag] -> (5, 34), boot_sub[tag] -> (5, B, 34)
    obs_sub_map: Dict[str, np.ndarray] = {}
    sd_sub_map: Dict[str, np.ndarray] = {}
    sd_m5_map: Dict[str, np.ndarray] = {}
    boot_sub_map: Dict[str, np.ndarray] = {}

    for mid, tag in t4_specs:
        em = models[mid]
        n_seeds = 3 if em.is_multiseed else 1
        obs_ps = np.full((len(PARTICIPANTS), n_seeds, N_EMOTIONS), np.nan, dtype=np.float64)
        boot_ps = np.full((len(PARTICIPANTS), n_seeds, B, N_EMOTIONS), np.nan, dtype=np.float64)

        for p_i, sub in enumerate(PARTICIPANTS):
            pm, Ws, Ws_sum, Ys, Yc, Sw_Y, Sw_Y2 = W_sub_cache[sub]
            for s_i in range(n_seeds):
                Xs = em.preds_sub[sub][s_i, pm, :]
                obs_ps[p_i, s_i] = c.pearson(Ys, Xs)
                boot_ps[p_i, s_i] = weighted_boot_pearson_2d(Ws, Xs, Yc, Sw_Y, Sw_Y2, Ws_sum)

        obs_sub_map[tag] = obs_ps.mean(axis=1)  # (5, 34)
        boot_sub_map[tag] = boot_ps.mean(axis=1)  # (5, B, 34)
        if em.is_multiseed:
            sd_sub_map[tag] = np.std(obs_ps, axis=1, ddof=1)
            sd_m5_map[tag] = np.std(obs_ps.mean(axis=0), axis=0, ddof=1)
        else:
            sd_sub_map[tag] = np.full((len(PARTICIPANTS), N_EMOTIONS), np.nan)
            sd_m5_map[tag] = np.full(N_EMOTIONS, np.nan)

    # Also Stimulus Model on all 2,109 dev videos
    stim_em = models["s4_stimulus"]
    W_sum_all = W_all.sum(axis=1, keepdims=True)
    Yc_all = y_em - y_em.mean(axis=0, keepdims=True)
    stim_all_obs = c.pearson(y_em, stim_em.preds_all[0])  # (34,)
    stim_all_boot = weighted_boot_pearson_2d(
        W_all, stim_em.preds_all[0], Yc_all, W_all @ Yc_all, W_all @ (Yc_all * Yc_all), W_sum_all
    )  # (B, 34)
    stim_all_cil, stim_all_cih = basic_ci_vec(stim_all_obs, stim_all_boot)

    # 1-2(가): C-1 - C-1_additive per emotion (mean_5sub and per participant, with BH-FDR across 34 emotions!)
    diff_sub_obs = obs_sub_map["C-1"] - obs_sub_map["C-1_additive"]  # (5, 34)
    diff_sub_boot = boot_sub_map["C-1"] - boot_sub_map["C-1_additive"]  # (5, B, 34)
    diff_m5_obs = diff_sub_obs.mean(axis=0)  # (34,)
    diff_m5_boot = diff_sub_boot.mean(axis=0)  # (B, 34)
    diff_m5_cil, diff_m5_cih = basic_ci_vec(diff_m5_obs, diff_m5_boot)
    diff_m5_p = hall_wilson_p_vec(diff_m5_obs, diff_m5_boot)
    diff_m5_q = bh_fdr(diff_m5_p)

    diff_sub_cil = np.empty_like(diff_sub_obs)
    diff_sub_cih = np.empty_like(diff_sub_obs)
    diff_sub_p = np.empty_like(diff_sub_obs)
    diff_sub_q = np.empty_like(diff_sub_obs)
    for p_i in range(len(PARTICIPANTS)):
        diff_sub_cil[p_i], diff_sub_cih[p_i] = basic_ci_vec(diff_sub_obs[p_i], diff_sub_boot[p_i])
        diff_sub_p[p_i] = hall_wilson_p_vec(diff_sub_obs[p_i], diff_sub_boot[p_i])
        diff_sub_q[p_i] = bh_fdr(diff_sub_p[p_i])

    # Precompute CIs for each model tag
    m5_obs_map = {tag: obs_sub_map[tag].mean(axis=0) for _, tag in t4_specs}
    m5_boot_map = {tag: boot_sub_map[tag].mean(axis=0) for _, tag in t4_specs}
    m5_ci_map = {tag: basic_ci_vec(m5_obs_map[tag], m5_boot_map[tag]) for _, tag in t4_specs}
    sub_ci_map = {
        tag: [basic_ci_vec(obs_sub_map[tag][p_i], boot_sub_map[tag][p_i]) for p_i in range(len(PARTICIPANTS))]
        for _, tag in t4_specs
    }

    wide_rows = []
    long_rows = []
    for e_i in range(N_EMOTIONS):
        sc_col = f"score_{e_i}"
        emo_name = str(label_map.loc[e_i, "name"])
        assert str(label_map.loc[e_i, "score_col"]) == sc_col
        y_col = y_em[:, e_i]
        n_nz = int(np.sum(y_col > 0.0))
        r_mean = float(np.mean(y_col))
        r_var = float(np.var(y_col, ddof=1))
        r_sd = float(np.std(y_col, ddof=1))

        wrow: dict = {
            "emotion_index": e_i,
            "score_col": sc_col,
            "emotion": emo_name,
            "n_nonzero_dev2109": n_nz,
            "rating_mean": r_mean,
            "rating_var": r_var,
            "rating_sd": r_sd,
        }

        for mid, tag in t4_specs:
            val_m5 = m5_obs_map[tag][e_i]
            cil_m5, cih_m5 = m5_ci_map[tag][0][e_i], m5_ci_map[tag][1][e_i]
            wrow[f"{tag}_mean_5sub_r"] = fmt_r_or_nc(val_m5)
            wrow[f"{tag}_mean_5sub_seed_sd"] = sd_m5_map[tag][e_i]
            wrow[f"{tag}_mean_5sub_ci_low"] = cil_m5
            wrow[f"{tag}_mean_5sub_ci_high"] = cih_m5
            long_rows.append({
                "emotion_index": e_i,
                "score_col": sc_col,
                "emotion": emo_name,
                "n_nonzero_dev2109": n_nz,
                "rating_var": r_var,
                "model_tag": tag,
                "participant": "mean_5sub",
                "r": fmt_r_or_nc(val_m5),
                "seed_sd": sd_m5_map[tag][e_i],
                "ci_low": cil_m5,
                "ci_high": cih_m5,
            })
            for p_i, sub in enumerate(PARTICIPANTS):
                v_s = obs_sub_map[tag][p_i, e_i]
                cl_s, ch_s = sub_ci_map[tag][p_i][0][e_i], sub_ci_map[tag][p_i][1][e_i]
                wrow[f"{tag}_{sub}_r"] = fmt_r_or_nc(v_s)
                wrow[f"{tag}_{sub}_ci_low"] = cl_s
                wrow[f"{tag}_{sub}_ci_high"] = ch_s
                long_rows.append({
                    "emotion_index": e_i,
                    "score_col": sc_col,
                    "emotion": emo_name,
                    "n_nonzero_dev2109": n_nz,
                    "rating_var": r_var,
                    "model_tag": tag,
                    "participant": sub,
                    "r": fmt_r_or_nc(v_s),
                    "seed_sd": sd_sub_map[tag][p_i, e_i],
                    "ci_low": cl_s,
                    "ci_high": ch_s,
                })

        # Stimulus Model on all 2,109 dev videos
        wrow["Stimulus_Model_all_dev2109_r"] = fmt_r_or_nc(stim_all_obs[e_i])
        wrow["Stimulus_Model_all_dev2109_ci_low"] = stim_all_cil[e_i]
        wrow["Stimulus_Model_all_dev2109_ci_high"] = stim_all_cih[e_i]

        # 1-2(가): C-1 - C-1_additive
        wrow["diff_C1_minus_C1add_mean_5sub"] = diff_m5_obs[e_i]
        wrow["diff_C1_minus_C1add_mean_5sub_ci_low"] = diff_m5_cil[e_i]
        wrow["diff_C1_minus_C1add_mean_5sub_ci_high"] = diff_m5_cih[e_i]
        wrow["diff_C1_minus_C1add_mean_5sub_p_boot"] = diff_m5_p[e_i]
        wrow["diff_C1_minus_C1add_mean_5sub_q_fdr34"] = diff_m5_q[e_i]
        for p_i, sub in enumerate(PARTICIPANTS):
            wrow[f"diff_C1_minus_C1add_{sub}"] = diff_sub_obs[p_i, e_i]
            wrow[f"diff_C1_minus_C1add_{sub}_ci_low"] = diff_sub_cil[p_i, e_i]
            wrow[f"diff_C1_minus_C1add_{sub}_ci_high"] = diff_sub_cih[p_i, e_i]
            wrow[f"diff_C1_minus_C1add_{sub}_p_boot"] = diff_sub_p[p_i, e_i]
            wrow[f"diff_C1_minus_C1add_{sub}_q_fdr34"] = diff_sub_q[p_i, e_i]

        wide_rows.append(wrow)

    return pd.DataFrame(wide_rows), pd.DataFrame(long_rows)


def compute_feat_boot_ci(
    pred_sub: Dict[str, np.ndarray],
    true_all: np.ndarray,
    present_masks: Dict[str, np.ndarray],
    W_all: np.ndarray,
) -> Dict[str, Tuple[float, float]]:
    """Compute 10,000-iteration canonical_id basic 95% CI on O20 mean_dim_r for 5,632d / 4,096d features.

    pred_sub[sub]: (n_seeds, N_s, D) in original feature scale.
    """
    B = W_all.shape[0]
    boot_sub = np.empty((len(PARTICIPANTS), B), dtype=np.float64)
    obs_sub = np.empty(len(PARTICIPANTS), dtype=np.float64)

    for p_i, sub in enumerate(PARTICIPANTS):
        pm = present_masks[sub]
        Ws = W_all[:, pm]
        Ws_sum = Ws.sum(axis=1, keepdims=True)
        Ys = true_all[pm].astype(np.float64)
        Yc = Ys - Ys.mean(axis=0, keepdims=True)
        Sw_Y = Ws @ Yc
        Sw_Y2 = Ws @ (Yc * Yc)

        n_seeds = pred_sub[sub].shape[0]
        s_obs = []
        s_boot = np.zeros(B, dtype=np.float64)
        for s_i in range(n_seeds):
            Xs = pred_sub[sub][s_i].astype(np.float64)
            s_obs.append(float(np.nanmean(c.pearson(Ys, Xs))))
            # Chunk dimensions in blocks of 1024 to keep peak RAM tiny (<200 MB)
            D = Xs.shape[1]
            valid_counts = np.zeros(B, dtype=np.float64)
            r_sums = np.zeros(B, dtype=np.float64)
            for d0 in range(0, D, 1024):
                d1 = min(D, d0 + 1024)
                rb = weighted_boot_pearson_2d(
                    Ws, Xs[:, d0:d1], Yc[:, d0:d1], Sw_Y[:, d0:d1], Sw_Y2[:, d0:d1], Ws_sum
                )
                fin = np.isfinite(rb)
                r_sums += np.where(fin, rb, 0.0).sum(axis=1)
                valid_counts += fin.sum(axis=1)
            s_boot += (r_sums / np.maximum(valid_counts, 1.0)) / float(n_seeds)
        obs_sub[p_i] = float(np.mean(s_obs))
        boot_sub[p_i] = s_boot

    ci_out: Dict[str, Tuple[float, float]] = {}
    ci_out["mean_5sub"] = basic_ci(float(obs_sub.mean()), boot_sub.mean(axis=0))
    for p_i, sub in enumerate(PARTICIPANTS):
        ci_out[sub] = basic_ci(float(obs_sub[p_i]), boot_sub[p_i])
    return ci_out


def build_table5_feature_decoding(
    split: pd.DataFrame,
    present_masks: Dict[str, np.ndarray],
    W_all: np.ndarray,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Dict[str, np.ndarray]], Dict[str, object]]:
    """Build s10_table5_feature_decoding + s10_table5b_s5_64layers_full, returning decoded preds for Table 7."""
    vid_to_row = {int(v): i for i, v in enumerate(split["video_id"].tolist())}
    fold_arr = split["fold"].to_numpy()
    checks: Dict[str, object] = {}

    # True primary targets (2109, 5632) and (2109, 4096) in original scale
    v_true = c.load_rows("vjepa2/target", split["video_id"], split).astype(np.float64)
    c_true = c.load_rows("deberta/target", split["video_id"], split).astype(np.float64)
    assert v_true.shape == (len(split), 5632) and c_true.shape == (len(split), 4096)

    # Verify S5 64-layer decoding_layer_metrics.tsv and verify primary layer concatenation == target.npy
    layers_dict = load_targets(split)
    v_cat_true = np.concatenate([layers_dict[("vjepa2", l)] for l in (10, 20, 30, 40)], axis=1).astype(np.float64)
    c_cat_true = np.concatenate([layers_dict[("deberta", l)] for l in (6, 12, 18, 24)], axis=1).astype(np.float64)
    v_cat_diff = float(np.max(np.abs(v_cat_true - v_true)))
    c_cat_diff = float(np.max(np.abs(c_cat_true - c_true)))
    assert v_cat_diff < 1e-6 and c_cat_diff < 1e-6
    checks["vjepa2_primary_concat_vs_target_max_diff"] = v_cat_diff
    checks["deberta_primary_concat_vs_target_max_diff"] = c_cat_diff

    s5_layer_df = pd.read_csv(P.OUT / "s5_collect/decoding_layer_metrics.tsv", sep="\t")
    # Build 64-layer full table with 5-sub means
    m5_layer = (
        s5_layer_df.groupby(["model", "layer"], as_index=False)
        .agg(
            mean_r=("mean_r", "mean"),
            n_dim_not_computable=("n_dim_not_computable", "max"),
            identification=("identification", "mean"),
        )
    )
    m5_layer.insert(0, "participant", "mean_5sub")
    df_64layers = pd.concat([m5_layer, s5_layer_df], ignore_index=True)

    # Load S6 outer_fold standardization stats (4-train-fold D9 stats)
    std_by_fold = {
        k: np.load(S.OUT / f"outer_fold{k}/plan/standardization.npz")
        for k in range(1, N_FOLDS + 1)
    }

    # Evaluate S5 concatenated primary targets (Vision 5,632d & Caption 4,096d)
    s5_vis_preds: Dict[str, np.ndarray] = {}
    s5_cap_preds: Dict[str, np.ndarray] = {}
    s5_summary_rows = []

    v_layer_keys = [layer_name(("vjepa2", l)) for l in (10, 20, 30, 40)]
    c_layer_keys = [layer_name(("deberta", l)) for l in (6, 12, 18, 24)]

    s5_metrics_by_target: Dict[str, Dict[str, dict]] = {"vision_5632d": {}, "caption_4096d": {}}
    for s_tag in d5.HK:
        sub = f"sub-{s_tag}"
        pmask = present_masks[sub]
        N_s = int(pmask.sum())
        sub_row_idx = np.flatnonzero(pmask)
        global_to_local = {int(r): idx for idx, r in enumerate(sub_row_idx.tolist())}

        vp_full = np.full((1, N_s, 5632), np.nan, dtype=np.float64)
        cp_full = np.full((1, N_s, 4096), np.nan, dtype=np.float64)
        v_id_dk, v_id_d9, c_id_dk, c_id_d9 = [], [], [], []

        for k in range(1, N_FOLDS + 1):
            z = np.load(d5.OUT / f"decoding/sub-{s_tag}_fold{k}/test_pred.npz")
            g_rows = np.array([vid_to_row[int(v)] for v in z["video_id"].tolist()], dtype=np.int64)
            l_rows = np.array([global_to_local[int(r)] for r in g_rows], dtype=np.int64)

            vk = np.concatenate([z[lk].astype(np.float64) for lk in v_layer_keys], axis=1)
            ck = np.concatenate([z[lk].astype(np.float64) for lk in c_layer_keys], axis=1)
            vp_full[0, l_rows, :] = vk
            cp_full[0, l_rows, :] = ck

            # O19 identification in participant D_k coordinates (matching s5_collect.py) AND fold D9 coordinates
            dk_mask = (fold_arr != k) & pmask
            vm_dk, vs_dk = v_true[dk_mask].mean(0), v_true[dk_mask].std(0)
            cm_dk, cs_dk = c_true[dk_mask].mean(0), c_true[dk_mask].std(0)
            v_id_dk.append(safe_identification_scores((vk - vm_dk) / vs_dk, (v_true[g_rows] - vm_dk) / vs_dk))
            c_id_dk.append(safe_identification_scores((ck - cm_dk) / cs_dk, (c_true[g_rows] - cm_dk) / cs_dk))

            st_k = std_by_fold[k]
            vm_d9, vs_d9 = st_k["visual_mean"].astype(np.float64), st_k["visual_std"].astype(np.float64)
            cm_d9, cs_d9 = st_k["caption_mean"].astype(np.float64), st_k["caption_std"].astype(np.float64)
            v_id_d9.append(safe_identification_scores((vk - vm_d9) / vs_d9, (v_true[g_rows] - vm_d9) / vs_d9))
            c_id_d9.append(safe_identification_scores((ck - cm_d9) / cs_d9, (c_true[g_rows] - cm_d9) / cs_d9))

        assert np.isfinite(vp_full).all() and np.isfinite(cp_full).all()
        s5_vis_preds[sub] = vp_full
        s5_cap_preds[sub] = cp_full

        rv = c.pearson(v_true[pmask], vp_full[0])
        rc = c.pearson(c_true[pmask], cp_full[0])
        s5_metrics_by_target["vision_5632d"][sub] = {
            "mean_dim_r": float(np.nanmean(rv)),
            "n_dim_not_computable": int(np.isnan(rv).sum()),
            "identification_d9": float(np.concatenate(v_id_d9).mean()),
            "identification_dk": float(np.concatenate(v_id_dk).mean()),
        }
        s5_metrics_by_target["caption_4096d"][sub] = {
            "mean_dim_r": float(np.nanmean(rc)),
            "n_dim_not_computable": int(np.isnan(rc).sum()),
            "identification_d9": float(np.concatenate(c_id_d9).mean()),
            "identification_dk": float(np.concatenate(c_id_dk).mean()),
        }

    # Bootstrap CIs on [사전] 2-1 S5 Ridge primary targets
    s5_vis_ci = compute_feat_boot_ci(s5_vis_preds, v_true, present_masks, W_all)
    s5_cap_ci = compute_feat_boot_ci(s5_cap_preds, c_true, present_masks, W_all)

    for tkey, tlabel, ci_dict in [
        ("vision_5632d", "Vision (V-JEPA2 10,20,30,40; 5,632d)", s5_vis_ci),
        ("caption_4096d", "Caption (DeBERTa 6,12,18,24; 4,096d)", s5_cap_ci),
    ]:
        md = s5_metrics_by_target[tkey]
        row = {
            "model_id": "s5_ridge_decoding",
            "family": "S5_decoding",
            "code": "ridge_decoding",
            "display_name": "S5 Ridge Feature Decoder (2-1 주 검정 대상)",
            "decoder_source": "ridge_primary_concat",
            "target": tkey,
            "target_label": tlabel,
            "is_multiseed": False,
            "n_folds_evaluated": 6,
            "folds_note": "all 6 folds evaluated",
            "mean_5sub_r": float(np.mean([md[s]["mean_dim_r"] for s in PARTICIPANTS])),
            "mean_5sub_seed_sd": np.nan,
            "mean_5sub_seed0": float(np.mean([md[s]["mean_dim_r"] for s in PARTICIPANTS])),
            "mean_5sub_seed1": np.nan,
            "mean_5sub_seed2": np.nan,
            "mean_5sub_ci_low": ci_dict["mean_5sub"][0],
            "mean_5sub_ci_high": ci_dict["mean_5sub"][1],
            "mean_5sub_ident_d9": float(np.mean([md[s]["identification_d9"] for s in PARTICIPANTS])),
            "mean_5sub_ident_dk": float(np.mean([md[s]["identification_dk"] for s in PARTICIPANTS])),
            "n_dim_not_computable_max": int(max(md[s]["n_dim_not_computable"] for s in PARTICIPANTS)),
        }
        for sub in PARTICIPANTS:
            row[f"{sub}_r"] = md[sub]["mean_dim_r"]
            row[f"{sub}_seed_sd"] = np.nan
            row[f"{sub}_ci_low"] = ci_dict[sub][0]
            row[f"{sub}_ci_high"] = ci_dict[sub][1]
            row[f"{sub}_ident_d9"] = md[sub]["identification_d9"]
            row[f"{sub}_ident_dk"] = md[sub]["identification_dk"]
        s5_summary_rows.append(row)

    # Also summarize S5 64-layer averages (mean across 40 V-JEPA2 layers and mean across 24 DeBERTa layers, plus best layer)
    for m_name, n_lay, t_lbl in [
        ("vjepa2", 40, "V-JEPA2 40개 층 평균 (요약)"),
        ("deberta", 24, "DeBERTa 24개 층 평균 (요약)"),
    ]:
        sub_df = s5_layer_df[s5_layer_df["model"] == m_name]
        by_sub_r = sub_df.groupby("participant")["mean_r"].mean().to_dict()
        by_sub_id = sub_df.groupby("participant")["identification"].mean().to_dict()
        row = {
            "model_id": f"s5_ridge_{m_name}_all{n_lay}_avg",
            "family": "S5_decoding_64layer_summary",
            "code": f"ridge_{m_name}_all{n_lay}",
            "display_name": f"S5 Ridge ({t_lbl})",
            "decoder_source": f"all_{n_lay}_layers_mean",
            "target": f"{m_name}_all{n_lay}",
            "target_label": t_lbl,
            "is_multiseed": False,
            "n_folds_evaluated": 6,
            "folds_note": "all 6 folds evaluated",
            "mean_5sub_r": float(np.mean([by_sub_r[s] for s in PARTICIPANTS])),
            "mean_5sub_seed_sd": np.nan,
            "mean_5sub_seed0": float(np.mean([by_sub_r[s] for s in PARTICIPANTS])),
            "mean_5sub_seed1": np.nan,
            "mean_5sub_seed2": np.nan,
            "mean_5sub_ci_low": np.nan,
            "mean_5sub_ci_high": np.nan,
            "mean_5sub_ident_d9": np.nan,
            "mean_5sub_ident_dk": float(np.mean([by_sub_id[s] for s in PARTICIPANTS])),
            "n_dim_not_computable_max": int(sub_df["n_dim_not_computable"].max()),
        }
        for sub in PARTICIPANTS:
            row[f"{sub}_r"] = float(by_sub_r[sub])
            row[f"{sub}_seed_sd"] = np.nan
            row[f"{sub}_ci_low"] = np.nan
            row[f"{sub}_ci_high"] = np.nan
            row[f"{sub}_ident_d9"] = np.nan
            row[f"{sub}_ident_dk"] = float(by_sub_id[sub])
        s5_summary_rows.append(row)

    # S6 conditions with decoded_test.npz / aux_decoded_test.npz
    s6_dec_specs = [
        ("brain_only_featdec", "B-1", "B-1: Brain → Emotion + Vision + Caption", "outputs/decoded_test.npz", "shared_encoder", True),
        ("brain_decoded", "C-1", "C-1: Brain + Decoded Feature → Emotion", "outputs/decoded_test.npz", "shared_encoder", True),
        ("brain_decoded_additive", "C-1_additive", "C-1 (더하기 head)", "outputs/decoded_test.npz", "shared_encoder", False),
        ("brain_decoded_grad", "C-1_grad", "C-1 (손실 흐름 허용판)", "outputs/decoded_test.npz", "shared_encoder", False),
        ("brain_decoded_distill", "C-2", "C-2: Brain + Decoded Feature → Emotion [distillation]", "outputs/decoded_test.npz", "shared_encoder", True),
        ("feature_encoder", "encoder_2", "Feature Encoder 단독 (Brain → Vision + Caption, encoder 2)", "outputs/decoded_test.npz", "encoder_2", True),
        ("brain_decoded_sep", "D-1_enc2", "D-1 (별도 encoder: encoder 2 decoded_test)", "outputs/decoded_test.npz", "encoder_2", True),
        ("brain_decoded_sep", "D-1_aux_enc1", "D-1 (별도 encoder: 보조 encoder 1 aux_decoded_test)", "outputs/aux_decoded_test.npz", "aux_encoder_1", False),
        ("brain_decoded_sep_distill", "D-2_enc2", "D-2 [distillation] (별도 encoder: encoder 2 decoded_test)", "outputs/decoded_test.npz", "encoder_2", False),
        ("brain_decoded_sep_distill", "D-2_aux_enc1", "D-2 [distillation] (별도 encoder: 보조 encoder 1 aux_decoded_test)", "outputs/aux_decoded_test.npz", "aux_encoder_1", False),
        ("brain_decoded_pool", "C-1_pool", "C-1 (평균 pooling판)", "outputs/decoded_test.npz", "shared_encoder", False),
        ("control_feature_shuffle", "ctrl_feature_shuffle", "대조군: Brain → Emotion + Vision + Caption [섞은 특징]", "outputs/decoded_test.npz", "shared_encoder", False),
    ]

    c1_decoded_cache: Dict[str, Dict[str, np.ndarray]] = {}

    for cond, code, disp, rel_npz, dec_src, with_ci in s6_dec_specs:
        vis_preds_2109 = {sub: np.full((3, len(split), 5632), np.nan, dtype=np.float64) for sub in PARTICIPANTS}
        cap_preds_2109 = {sub: np.full((3, len(split), 4096), np.nan, dtype=np.float64) for sub in PARTICIPANTS}
        vis_preds_d9mean6 = {sub: np.full((3, len(split), 5632), np.nan, dtype=np.float64) for sub in PARTICIPANTS}
        cap_preds_d9mean6 = {sub: np.full((3, len(split), 4096), np.nan, dtype=np.float64) for sub in PARTICIPANTS}

        vis_id_d9 = {sub: [[] for _ in range(3)] for sub in PARTICIPANTS}
        cap_id_d9 = {sub: [[] for _ in range(3)] for sub in PARTICIPANTS}
        vis_id_dk = {sub: [[] for _ in range(3)] for sub in PARTICIPANTS}
        cap_id_dk = {sub: [[] for _ in range(3)] for sub in PARTICIPANTS}

        active_folds: List[int] = []
        skipped_zero_folds: List[int] = []

        for k in range(1, N_FOLDS + 1):
            fdir = S.OUT / f"outer_fold{k}"
            sel = json.loads((fdir / cond / "selected.json").read_text())
            st_k = std_by_fold[k]
            vm_d9, vs_d9 = st_k["visual_mean"].astype(np.float64), st_k["visual_std"].astype(np.float64)
            cm_d9, cs_d9 = st_k["caption_mean"].astype(np.float64), st_k["caption_std"].astype(np.float64)

            probe_npz = fdir / sel["seeds"]["0"] / rel_npz
            if not probe_npz.exists():
                if not (sel.get("zero_selected") and sel.get("source_condition") == "brain_only"):
                    raise FileNotFoundError(f"Unexpected missing decoded file: {probe_npz}")
                skipped_zero_folds.append(k)
                for sub in PARTICIPANTS:
                    frows = np.flatnonzero((fold_arr == k) & present_masks[sub])
                    vis_preds_d9mean6[sub][:, frows, :] = vm_d9[None, None, :]
                    cap_preds_d9mean6[sub][:, frows, :] = cm_d9[None, None, :]
                continue

            active_folds.append(k)
            for s_i, s_key in enumerate(("0", "1", "2")):
                z = np.load(fdir / sel["seeds"][s_key] / rel_npz)
                p_part = z["participant"].astype(str)
                p_vid = z["video_id"].astype(np.int64)
                vh = z["v_hat"].astype(np.float64)
                ch = z["c_hat"].astype(np.float64)

                for sub in PARTICIPANTS:
                    pmask = present_masks[sub]
                    at = np.flatnonzero(p_part == sub)
                    g_rows = np.array([vid_to_row[int(v)] for v in p_vid[at]], dtype=np.int64)

                    vh_sub = vh[at]  # in D9 standardized coordinates
                    ch_sub = ch[at]
                    v_orig = vh_sub * vs_d9 + vm_d9
                    c_orig = ch_sub * cs_d9 + cm_d9
                    vis_preds_2109[sub][s_i, g_rows, :] = v_orig
                    cap_preds_2109[sub][s_i, g_rows, :] = c_orig
                    vis_preds_d9mean6[sub][s_i, g_rows, :] = v_orig
                    cap_preds_d9mean6[sub][s_i, g_rows, :] = c_orig

                    # O19 in fold D9 coordinates
                    vt_d9 = (v_true[g_rows] - vm_d9) / vs_d9
                    ct_d9 = (c_true[g_rows] - cm_d9) / cs_d9
                    vis_id_d9[sub][s_i].append(safe_identification_scores(vh_sub, vt_d9))
                    cap_id_d9[sub][s_i].append(safe_identification_scores(ch_sub, ct_d9))

                    # Also O19 in participant D_k coordinates
                    dk_mask = (fold_arr != k) & pmask
                    vm_dk, vs_dk = v_true[dk_mask].mean(0), v_true[dk_mask].std(0)
                    cm_dk, cs_dk = c_true[dk_mask].mean(0), c_true[dk_mask].std(0)
                    vis_id_dk[sub][s_i].append(safe_identification_scores((v_orig - vm_dk) / vs_dk, (v_true[g_rows] - vm_dk) / vs_dk))
                    cap_id_dk[sub][s_i].append(safe_identification_scores((c_orig - cm_dk) / cs_dk, (c_true[g_rows] - cm_dk) / cs_dk))

        eval_masks = {
            sub: present_masks[sub] & np.isin(fold_arr, active_folds)
            for sub in PARTICIPANTS
        }
        vis_preds = {sub: vis_preds_2109[sub][:, eval_masks[sub], :] for sub in PARTICIPANTS}
        cap_preds = {sub: cap_preds_2109[sub][:, eval_masks[sub], :] for sub in PARTICIPANTS}

        if code == "C-1":
            assert len(active_folds) == 6
            c1_decoded_cache["vision_5632d"] = vis_preds
            c1_decoded_cache["caption_4096d"] = cap_preds

        vis_ci = compute_feat_boot_ci(vis_preds, v_true, eval_masks, W_all) if with_ci else None
        cap_ci = compute_feat_boot_ci(cap_preds, c_true, eval_masks, W_all) if with_ci else None

        fold_note = (
            f"all 6 folds evaluated"
            if not skipped_zero_folds
            else f"folds {active_folds} evaluated; fold {skipped_zero_folds} zero_selected=True (src=brain_only, no feature head, G10)"
        )

        for tkey, tlabel, preds_d, true_arr, id_d9_d, id_dk_d, ci_d in [
            ("vision_5632d", "Vision (V-JEPA2 10,20,30,40; 5,632d)", vis_preds, v_true, vis_id_d9, vis_id_dk, vis_ci),
            ("caption_4096d", "Caption (DeBERTa 6,12,18,24; 4,096d)", cap_preds, c_true, cap_id_d9, cap_id_dk, cap_ci),
        ]:
            r_ps = np.empty((len(PARTICIPANTS), 3), dtype=np.float64)
            id9_ps = np.empty((len(PARTICIPANTS), 3), dtype=np.float64)
            idk_ps = np.empty((len(PARTICIPANTS), 3), dtype=np.float64)
            nc_max = 0
            for p_i, sub in enumerate(PARTICIPANTS):
                emask = eval_masks[sub]
                for s_i in range(3):
                    rv = c.pearson(true_arr[emask], preds_d[sub][s_i])
                    r_ps[p_i, s_i] = float(np.nanmean(rv))
                    nc_max = max(nc_max, int(np.isnan(rv).sum()))
                    id9_ps[p_i, s_i] = float(np.nanmean(np.concatenate(id_d9_d[sub][s_i])))
                    idk_ps[p_i, s_i] = float(np.nanmean(np.concatenate(id_dk_d[sub][s_i])))

            m5_seeds = r_ps.mean(axis=0)
            row = {
                "model_id": f"s6_{cond}_{dec_src}",
                "family": "S6_decoded_features",
                "code": code,
                "display_name": disp,
                "decoder_source": dec_src,
                "target": tkey,
                "target_label": tlabel,
                "is_multiseed": True,
                "n_folds_evaluated": len(active_folds),
                "folds_note": fold_note,
                "mean_5sub_r": float(m5_seeds.mean()),
                "mean_5sub_seed_sd": float(np.std(m5_seeds, ddof=1)),
                "mean_5sub_seed0": float(m5_seeds[0]),
                "mean_5sub_seed1": float(m5_seeds[1]),
                "mean_5sub_seed2": float(m5_seeds[2]),
                "mean_5sub_ci_low": ci_d["mean_5sub"][0] if ci_d is not None else np.nan,
                "mean_5sub_ci_high": ci_d["mean_5sub"][1] if ci_d is not None else np.nan,
                "mean_5sub_ident_d9": float(id9_ps.mean()),
                "mean_5sub_ident_dk": float(idk_ps.mean()),
                "n_dim_not_computable_max": nc_max,
            }
            for p_i, sub in enumerate(PARTICIPANTS):
                row[f"{sub}_r"] = float(r_ps[p_i].mean())
                row[f"{sub}_seed_sd"] = float(np.std(r_ps[p_i], ddof=1))
                row[f"{sub}_ci_low"] = ci_d[sub][0] if ci_d is not None else np.nan
                row[f"{sub}_ci_high"] = ci_d[sub][1] if ci_d is not None else np.nan
                row[f"{sub}_ident_d9"] = float(id9_ps[p_i].mean())
                row[f"{sub}_ident_dk"] = float(idk_ps[p_i].mean())
            s5_summary_rows.append(row)

        # If a fold had zero_selected=True (B-1 fold 3), ALSO emit a 6-fold sensitivity row imputing D9 mean (v_hat=0, c_hat=0)
        if skipped_zero_folds:
            checks[f"{cond}_zero_selected_no_decoder_folds"] = skipped_zero_folds
            vis6 = {sub: vis_preds_d9mean6[sub][:, present_masks[sub], :] for sub in PARTICIPANTS}
            cap6 = {sub: cap_preds_d9mean6[sub][:, present_masks[sub], :] for sub in PARTICIPANTS}
            vis6_ci = compute_feat_boot_ci(vis6, v_true, present_masks, W_all) if with_ci else None
            cap6_ci = compute_feat_boot_ci(cap6, c_true, present_masks, W_all) if with_ci else None
            for tkey, tlabel, preds6_d, true_arr, ci6_d in [
                ("vision_5632d", "Vision (V-JEPA2 10,20,30,40; 5,632d)", vis6, v_true, vis6_ci),
                ("caption_4096d", "Caption (DeBERTa 6,12,18,24; 4,096d)", cap6, c_true, cap6_ci),
            ]:
                r6_ps = np.empty((len(PARTICIPANTS), 3), dtype=np.float64)
                nc6_max = 0
                for p_i, sub in enumerate(PARTICIPANTS):
                    pmask = present_masks[sub]
                    for s_i in range(3):
                        rv = c.pearson(true_arr[pmask], preds6_d[sub][s_i])
                        r6_ps[p_i, s_i] = float(np.nanmean(rv))
                        nc6_max = max(nc6_max, int(np.isnan(rv).sum()))
                m5_s6 = r6_ps.mean(axis=0)
                row6 = {
                    "model_id": f"s6_{cond}_{dec_src}_6fold_d9mean",
                    "family": "S6_decoded_features_sensitivity",
                    "code": f"{code}_6fold_d9mean",
                    "display_name": f"{disp} [6-fold 민감도: fold {skipped_zero_folds} zero_selected=True를 D9 평균 예측으로 포함]",
                    "decoder_source": f"{dec_src}_d9mean_imputed_zero_fold",
                    "target": tkey,
                    "target_label": tlabel,
                    "is_multiseed": True,
                    "n_folds_evaluated": 6,
                    "folds_note": f"all 6 folds (fold {skipped_zero_folds} zero_selected=True filled with D9 train mean)",
                    "mean_5sub_r": float(m5_s6.mean()),
                    "mean_5sub_seed_sd": float(np.std(m5_s6, ddof=1)),
                    "mean_5sub_seed0": float(m5_s6[0]),
                    "mean_5sub_seed1": float(m5_s6[1]),
                    "mean_5sub_seed2": float(m5_s6[2]),
                    "mean_5sub_ci_low": ci6_d["mean_5sub"][0] if ci6_d is not None else np.nan,
                    "mean_5sub_ci_high": ci6_d["mean_5sub"][1] if ci6_d is not None else np.nan,
                    "mean_5sub_ident_d9": np.nan,
                    "mean_5sub_ident_dk": np.nan,
                    "n_dim_not_computable_max": nc6_max,
                }
                for p_i, sub in enumerate(PARTICIPANTS):
                    row6[f"{sub}_r"] = float(r6_ps[p_i].mean())
                    row6[f"{sub}_seed_sd"] = float(np.std(r6_ps[p_i], ddof=1))
                    row6[f"{sub}_ci_low"] = ci6_d[sub][0] if ci6_d is not None else np.nan
                    row6[f"{sub}_ci_high"] = ci6_d[sub][1] if ci6_d is not None else np.nan
                    row6[f"{sub}_ident_d9"] = np.nan
                    row6[f"{sub}_ident_dk"] = np.nan
                s5_summary_rows.append(row6)

    decoded_for_perm = {
        "s5_vision": s5_vis_preds,
        "s5_caption": s5_cap_preds,
        "c1_vision": c1_decoded_cache["vision_5632d"],
        "c1_caption": c1_decoded_cache["caption_4096d"],
        "v_true": v_true,
        "c_true": c_true,
        "s5_vis_ci": s5_vis_ci,
        "s5_cap_ci": s5_cap_ci,
    }
    return pd.DataFrame(s5_summary_rows), df_64layers, decoded_for_perm, checks


def build_table6_bundle(
    split: pd.DataFrame,
    y_em: np.ndarray,
    present_masks: Dict[str, np.ndarray],
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, object]]:
    """Build Table 6 bundle: S6 selected hyperparams + F8 weights, S5 O18 boundaries, S4 O16 at_cap, and 6-2 zone summaries."""
    vid_to_row = {int(v): i for i, v in enumerate(split["video_id"].tolist())}
    fold_arr = split["fold"].to_numpy()
    checks: Dict[str, object] = {}

    # 1. S6 selected hyperparameters + F8 weight counts + zero_selected summary
    wc_df = pd.read_csv(P.MANIFESTS / "s6/weight_counts.tsv", sep="\t")
    wc_lookup = {}
    for _, wr in wc_df.iterrows():
        rk = -1 if pd.isna(wr["rank"]) else int(wr["rank"])
        wc_lookup[(str(wr["condition"]), int(wr["d"]), rk)] = wr

    code_map = {cond: (code, disp) for cond, code, disp in S6_META}
    code_map["feature_encoder"] = ("encoder_2", "Feature Encoder 단독 (Brain → Vision + Caption, encoder 2)")

    s6_sel_rows = []
    for cond in S.CONDITIONS.keys():
        code, disp = code_map.get(cond, (cond, S.DISPLAY.get(cond, cond)))
        for k in range(1, N_FOLDS + 1):
            sel = json.loads((S.OUT / f"outer_fold{k}/{cond}/selected.json").read_text())
            cand = sel["candidate"]
            d_val = int(cand["d"])
            rk_val = -1 if cand.get("rank") is None else int(cand["rank"])
            w_match = wc_lookup.get((cond, d_val, rk_val))
            # Best candidate val_score from rows
            cand_id = S.candidate_id(cand)
            val_scores = [r["val_score"] for r in sel.get("rows", []) if r.get("candidate_id") == cand_id]
            val_score = float(val_scores[0]) if val_scores else float("nan")
            lam_val = cand.get("lam")
            alpha_val = cand.get("alpha")
            s6_sel_rows.append({
                "fold": k,
                "condition": cond,
                "code": code,
                "display_name": disp,
                "d": d_val,
                "input_wd": cand.get("input_wd"),
                "lr": cand.get("lr"),
                "lam": lam_val,
                "alpha": alpha_val,
                "rank": cand.get("rank"),
                "feature_wd": cand.get("feature_wd"),
                "zero_selected": bool(sel.get("zero_selected", False)),
                "lam_is_zero": (lam_val is not None and float(lam_val) == 0.0),
                "alpha_is_zero": (alpha_val is not None and float(alpha_val) == 0.0),
                "source_condition": sel.get("source_condition"),
                "val_score": val_score,
                "trainable_params_F8": int(w_match["trainable"]) if w_match is not None else np.nan,
                "shared_params_F8": int(w_match["shared"]) if w_match is not None else np.nan,
                "frozen_params_F8": int(w_match["frozen"]) if w_match is not None else np.nan,
                "input_weight_params_F8": int(w_match["input_weight"]) if w_match is not None else np.nan,
            })
    df_s6_sel = pd.DataFrame(s6_sel_rows)

    zero_rows = []
    for cond in S.CONDITIONS.keys():
        sub_df = df_s6_sel[df_s6_sel["condition"] == cond]
        code, disp = code_map.get(cond, (cond, cond))
        zs_folds = sub_df.loc[sub_df["zero_selected"], "fold"].tolist()
        l0_folds = sub_df.loc[sub_df["lam_is_zero"], "fold"].tolist()
        a0_folds = sub_df.loc[sub_df["alpha_is_zero"], "fold"].tolist()
        zero_rows.append({
            "condition": cond,
            "code": code,
            "display_name": disp,
            "n_folds_total": len(sub_df),
            "n_zero_selected_G10": int(sub_df["zero_selected"].sum()),
            "zero_selected_folds": ",".join(map(str, zs_folds)) if zs_folds else "none",
            "n_lam_zero": int(sub_df["lam_is_zero"].sum()),
            "lam_zero_folds": ",".join(map(str, l0_folds)) if l0_folds else "none",
            "n_alpha_zero": int(sub_df["alpha_is_zero"].sum()),
            "alpha_zero_folds": ",".join(map(str, a0_folds)) if a0_folds else "none",
            "d_32_count": int((sub_df["d"] == 32).sum()),
            "d_64_count": int((sub_df["d"] == 64).sum()),
            "trainable_params_min_F8": int(sub_df["trainable_params_F8"].min()),
            "trainable_params_max_F8": int(sub_df["trainable_params_F8"].max()),
        })
    df_s6_zero = pd.DataFrame(zero_rows)

    # 2. S5 O18 boundary-lambda counts
    b_rows = []

    def add_boundary_row(task: str, sub_group: str, idx_arr: np.ndarray, max_idx: int, grid_desc: str) -> None:
        flat = idx_arr.reshape(-1)
        low = int(np.sum(flat == 0))
        high = int(np.sum(flat == max_idx))
        tot = int(flat.size)
        b_rows.append({
            "stage_task": task,
            "subgroup": sub_group,
            "lambda_grid": grid_desc,
            "at_low_end": low,
            "at_high_end": high,
            "at_either_end": low + high,
            "total": tot,
            "frac_low_end": low / tot if tot else np.nan,
            "frac_high_end": high / tot if tot else np.nan,
            "frac_either_end": (low + high) / tot if tot else np.nan,
        })

    dec_lam_df = pd.read_csv(P.OUT / "s5_collect/decoding_lambda.tsv", sep="\t")
    add_boundary_row("s5_decoding", "all_64layers_5sub_6fold", dec_lam_df["lambda_index"].to_numpy(), 9, "logspace(1,6,10)")
    for m_name in ("vjepa2", "deberta"):
        add_boundary_row("s5_decoding", m_name, dec_lam_df.loc[dec_lam_df["model"] == m_name, "lambda_index"].to_numpy(), 9, "logspace(1,6,10)")

    # ridge, h2020, signal, video, zone
    rm_em, rm_dim, rl_em, rl_dim = [], [], [], []
    h20_idx, sig_idx, z_exc_idx, z_ctl_idx = [], [], [], []
    for s_tag in d5.HK:
        for k in range(1, N_FOLDS + 1):
            zr = np.load(d5.OUT / f"ridge/sub-{s_tag}_fold{k}/pred.npz")
            rm_em.append(zr["lambda_main"][:34])
            rm_dim.append(zr["lambda_main"][34:])
            rl_em.append(zr["lambda_literature"][:34])
            rl_dim.append(zr["lambda_literature"][34:])
            zh = np.load(d5.OUT / f"h2020/sub-{s_tag}_fold{k}/pred.npz")
            h20_idx.append(zh["lambda_index"])
            zs = np.load(d5.OUT / f"signal/sub-{s_tag}_fold{k}/pred.npz")
            sig_idx.append(zs["lambda_index"])
            for b in range(1, 6):
                z_exc_idx.append(np.load(d5.OUT / f"zone/sub-{s_tag}_block{b}_fold{k}_excluded/pred.npz")["lambda_index"])
                z_ctl_idx.append(np.load(d5.OUT / f"zone/sub-{s_tag}_block{b}_fold{k}_control/pred.npz")["lambda_index"])

    add_boundary_row("s5_ridge", "emotion_main_34", np.concatenate(rm_em), 9, "logspace(1,6,10)")
    add_boundary_row("s5_ridge", "dimension_main_14", np.concatenate(rm_dim), 9, "logspace(1,6,10)")
    add_boundary_row("s5_ridge", "emotion_literature_34", np.concatenate(rl_em), 9, "logspace(1,6,10)")
    add_boundary_row("s5_ridge", "dimension_literature_14", np.concatenate(rl_dim), 9, "logspace(1,6,10)")
    add_boundary_row("s5_h2020", "370roi_x_34emotions", np.stack(h20_idx), 19, "logspace(1,4,20)")
    add_boundary_row("s5_signal", "34emotions", np.concatenate(sig_idx), 9, "logspace(1,6,10)")
    add_boundary_row("s5_zone", "excluded_5blocks", np.concatenate(z_exc_idx), 9, "logspace(1,6,10)")
    add_boundary_row("s5_zone", "control_5blocks", np.concatenate(z_ctl_idx), 9, "logspace(1,6,10)")

    for vname in ("length", "lowlevel"):
        v_idx = [np.load(d5.OUT / f"video/{vname}_fold{k}/pred.npz")["lambda_index"] for k in range(1, N_FOLDS + 1)]
        add_boundary_row("s5_video", vname, np.concatenate(v_idx), 9, "logspace(1,6,10)")

    # S4 ridge_d12 & ridge_noemo boundary checks
    d12_df = pd.read_csv(c.OUT / "ridge_d12/d12.tsv", sep="\t")
    d12_idx = np.array([int(x) for s in d12_df["lambda_index"] for x in str(s).split(",")], dtype=np.int64)
    add_boundary_row("s4_ridge_d12", "vjepa2_40blocks_caption_and_lowlevel", d12_idx, 7, "8-point ridge grid (S4)")

    noemo_df = pd.read_csv(c.OUT / "ridge_noemo/noemo_ridge.tsv", sep="\t")
    b_rows.append({
        "stage_task": "s4_ridge_noemo",
        "subgroup": "original_and_no_emotion_words_34emotions",
        "lambda_grid": "8-point ridge grid (S4)",
        "at_low_end": 0 if float(noemo_df["frac_lambda_at_ends"].max()) == 0.0 else np.nan,
        "at_high_end": 0 if float(noemo_df["frac_lambda_at_ends"].max()) == 0.0 else np.nan,
        "at_either_end": int(round(float(noemo_df["frac_lambda_at_ends"].sum()) * 6)),
        "total": len(noemo_df) * 6,
        "frac_low_end": 0.0 if float(noemo_df["frac_lambda_at_ends"].max()) == 0.0 else np.nan,
        "frac_high_end": 0.0 if float(noemo_df["frac_lambda_at_ends"].max()) == 0.0 else np.nan,
        "frac_either_end": float(noemo_df["frac_lambda_at_ends"].mean()),
    })
    df_s5_bound = pd.DataFrame(b_rows)

    # 3. S4 selection & at_cap (O16) + ridge_noemo + ridge_d12 + window_change summaries
    s4_sel_raw = pd.read_csv(P.OUT / "s4_collect/feature_model_selection.tsv", sep="\t")
    s4_cap_summary = (
        s4_sel_raw.groupby(["model", "version", "lr"], dropna=False, as_index=False)
        .agg(
            n_runs=("at_cap", "count"),
            n_at_cap=("at_cap", lambda s: int(np.sum(s.astype(bool)))),
            mean_epochs=("epochs", "mean"),
            max_epochs=("epochs", "max"),
            mean_val_r=("val_r", "mean"),
        )
    )
    s4_cap_summary["frac_at_cap"] = s4_cap_summary["n_at_cap"] / s4_cap_summary["n_runs"]

    # Build clean S4 auxiliary summary table (ridge_noemo, ridge_d12, window_change)
    wc_win_df = pd.read_csv(c.OUT / "window_change/window_change_summary.tsv", sep="\t")
    s4_aux_rows = []
    for cap_kind, grp in noemo_df.groupby("caption"):
        s4_aux_rows.append({
            "analysis": "s4_ridge_noemo",
            "key": str(cap_kind),
            "metric_primary": float(grp["r"].mean()),
            "metric_secondary": float(grp["r"].median()),
            "n_items": int(len(grp)),
            "detail": f"mean_34emo_r={grp['r'].mean():.6f}, max_frac_lambda_at_ends={grp['frac_lambda_at_ends'].max():.4f}",
        })
    orig_r = noemo_df.set_index(["caption", "emotion"]).loc["original", "r"]
    noem_r = noemo_df.set_index(["caption", "emotion"]).loc["no_emotion_words", "r"]
    diff_ne = (noem_r - orig_r).to_numpy()
    s4_aux_rows.append({
        "analysis": "s4_ridge_noemo_diff",
        "key": "no_emotion_words_minus_original",
        "metric_primary": float(np.mean(diff_ne)),
        "metric_secondary": float(np.median(diff_ne)),
        "n_items": int(len(diff_ne)),
        "detail": f"min_diff={np.min(diff_ne):.6f}, max_diff={np.max(diff_ne):.6f}",
    })
    for tgt, grp in d12_df.groupby("target"):
        pk_idx = grp["mean_r2"].idxmax()
        b10_40 = grp[grp["block"].isin([10, 20, 30, 40])]["mean_r2"].mean()
        s4_aux_rows.append({
            "analysis": "s4_ridge_d12",
            "key": str(tgt),
            "metric_primary": float(grp.loc[pk_idx, "mean_r2"]),
            "metric_secondary": float(b10_40),
            "n_items": int(len(grp)),
            "detail": f"peak_block={int(grp.loc[pk_idx, 'block'])}, min_mean_r2={grp['mean_r2'].min():.6f} (block {int(grp.loc[grp['mean_r2'].idxmin(), 'block'])}), mean_r2_blocks_10_20_30_40={b10_40:.6f}",
        })
    for _, wr in wc_win_df.iterrows():
        s4_aux_rows.append({
            "analysis": "s4_window_change_80videos",
            "key": f"vjepa2_block_{int(wr['block'])}",
            "metric_primary": float(wr["ratio"]),
            "metric_secondary": float(wr["within"]),
            "n_items": int(wr["n_valid"]),
            "detail": f"to_mean={wr['to_mean']:.6f}, other_video={wr['other_video']:.6f}, n_not_computable={int(wr['n_not_computable'])}",
        })
    df_s4_aux = pd.DataFrame(s4_aux_rows)

    checks["s4_ridge_noemo_mean_r"] = {
        k: float(g["r"].mean()) for k, g in noemo_df.groupby("caption")
    }
    checks["s4_ridge_d12_peak"] = {
        k: {
            "max_mean_r2": float(g["mean_r2"].max()),
            "peak_block": int(g.loc[g["mean_r2"].idxmax(), "block"]),
        }
        for k, g in d12_df.groupby("target")
    }
    checks["s4_window_change_summary"] = wc_win_df.to_dict(orient="records")

    # 4. Zone summary (6-2 pooling rules for S4 Stimulus and S5 Ridge)
    blocks_df = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t")
    block_arr = np.zeros(len(split), dtype=np.int64)
    for _, br in blocks_df.iterrows():
        v = int(br["video_id"])
        if v in vid_to_row:
            block_arr[vid_to_row[v]] = int(br["block"])
    assert (block_arr >= 1).all() and (block_arr <= 5).all()

    zone_block_rows = []
    zone_summary_rows = []

    # Load S4 zone pooled predictions per block & kind (on all block dev videos)
    s4_zone_preds: Dict[Tuple[int, str], np.ndarray] = {}
    for b in range(1, 6):
        b_mask = block_arr == b
        for kind in ("excluded", "control"):
            arr = np.full((len(split), N_EMOTIONS), np.nan, dtype=np.float64)
            for k in range(1, N_FOLDS + 1):
                z = np.load(c.OUT / f"zone/block{b}_fold{k}_{kind}/test_pred.npz")
                dest = np.array([vid_to_row[int(v)] for v in z["video_id"].tolist()], dtype=np.int64)
                expected = np.flatnonzero(b_mask & (fold_arr == k))
                if not np.array_equal(np.sort(dest), expected):
                    raise ValueError(f"S4 zone mismatch block {b} fold {k} {kind}")
                arr[dest, :] = z["p"].astype(np.float64)
            s4_zone_preds[(b, kind)] = arr

    # Cross-check S4 zone against precomputed s4_no_brain/summary/zone_test_r.tsv
    s4_zone_ref = pd.read_csv(c.OUT / "summary/zone_test_r.tsv", sep="\t")
    r_b1_exc = c.pearson(y_em[block_arr == 1], s4_zone_preds[(1, "excluded")][block_arr == 1])
    ref_b1_exc = s4_zone_ref[(s4_zone_ref["block"] == 1) & (s4_zone_ref["kind"] == "excluded")]["r"].to_numpy()
    z_diff = float(np.nanmax(np.abs(r_b1_exc - ref_b1_exc)))
    assert z_diff < 1e-5, f"S4 zone cross-check diff: {z_diff}"
    checks["s4_zone_vs_summary_tsv_max_abs_diff"] = z_diff

    # Load S5 ridge zone pooled predictions per participant, block & kind
    s5_zone_preds: Dict[Tuple[str, int, str], np.ndarray] = {}
    for s_tag in d5.HK:
        sub = f"sub-{s_tag}"
        pmask = present_masks[sub]
        for b in range(1, 6):
            b_mask = (block_arr == b) & pmask
            for kind in ("excluded", "control"):
                arr = np.full((len(split), N_EMOTIONS), np.nan, dtype=np.float64)
                for k in range(1, N_FOLDS + 1):
                    z = np.load(d5.OUT / f"zone/sub-{s_tag}_block{b}_fold{k}_{kind}/pred.npz")
                    dest = np.array([vid_to_row[int(v)] for v in z["video_id"].tolist()], dtype=np.int64)
                    expected = np.flatnonzero(b_mask & (fold_arr == k))
                    if not np.array_equal(np.sort(dest), expected):
                        raise ValueError(f"S5 zone mismatch {sub} block {b} fold {k} {kind}")
                    arr[dest, :] = z["pred"].astype(np.float64)
                s5_zone_preds[(sub, b, kind)] = arr

    def eval_zone_entity(
        model_id: str,
        disp: str,
        entity: str,
        get_mask_fn,
        get_pred_fn,
    ) -> dict:
        blk_exc, blk_ctl, blk_drop = [], [], []
        for b in range(1, 6):
            m = get_mask_fn(b)
            yb = y_em[m]
            p_exc = get_pred_fn(b, "excluded")[m]
            p_ctl = get_pred_fn(b, "control")[m]

            const_y = np.all(yb == yb[:1], axis=0)
            const_p_exc = np.all(p_exc == p_exc[:1], axis=0)
            const_p_ctl = np.all(p_ctl == p_ctl[:1], axis=0)
            # Rule 6-2: exclude constant-y emotions AND exclude any emotion constant in either setting from BOTH settings
            eval_em = (~const_y) & (~const_p_exc) & (~const_p_ctl)
            r_exc = c.pearson(yb[:, eval_em], p_exc[:, eval_em])
            r_ctl = c.pearson(yb[:, eval_em], p_ctl[:, eval_em])
            me = float(np.nanmean(r_exc))
            mc = float(np.nanmean(r_ctl))
            blk_exc.append(me)
            blk_ctl.append(mc)
            blk_drop.append(me - mc)

            zone_block_rows.append({
                "model_id": model_id,
                "display_name": disp,
                "participant": entity,
                "block": b,
                "n_test_videos": int(m.sum()),
                "n_emotions_included": int(eval_em.sum()),
                "n_const_y_emotions": int(const_y.sum()),
                "n_const_pred_excluded": int(const_p_exc.sum()),
                "n_const_pred_control": int(const_p_ctl.sum()),
                "r_excluded": me,
                "r_control": mc,
                "diff_excluded_minus_control": me - mc,
            })

        return {
            "model_id": model_id,
            "display_name": disp,
            "participant": entity,
            "five_block_mean_excluded": float(np.mean(blk_exc)),
            "five_block_mean_control": float(np.mean(blk_ctl)),
            "five_block_mean_diff_excluded_minus_control": float(np.mean(blk_drop)),
            **{f"block{b}_excluded": blk_exc[b - 1] for b in range(1, 6)},
            **{f"block{b}_control": blk_ctl[b - 1] for b in range(1, 6)},
            **{f"block{b}_diff": blk_drop[b - 1] for b in range(1, 6)},
        }

    # S4 Stimulus on all_dev_2109 and restricted to each participant (N11)
    zone_summary_rows.append(
        eval_zone_entity(
            "s4_stimulus_zone",
            "S4 Stimulus Model (5개 내용 구역 제외 vs 대조)",
            "all_dev_2109",
            lambda b: block_arr == b,
            lambda b, kd: s4_zone_preds[(b, kd)],
        )
    )
    s4_sub_z = [
        eval_zone_entity(
            "s4_stimulus_zone",
            "S4 Stimulus Model (참가자 영상 정합, N11)",
            sub,
            lambda b, s=sub: (block_arr == b) & present_masks[s],
            lambda b, kd: s4_zone_preds[(b, kd)],
        )
        for sub in PARTICIPANTS
    ]
    s4_m5 = {
        "model_id": "s4_stimulus_zone",
        "display_name": "S4 Stimulus Model (참가자 영상 정합, N11)",
        "participant": "mean_5sub",
    }
    for k_col in [k for k in s4_sub_z[0].keys() if k not in ("model_id", "display_name", "participant")]:
        s4_m5[k_col] = float(np.mean([d[k_col] for d in s4_sub_z]))
    zone_summary_rows.append(s4_m5)
    zone_summary_rows.extend(s4_sub_z)

    # S5 Ridge zone per participant + 5-sub mean
    s5_sub_z = [
        eval_zone_entity(
            "s5_ridge_zone",
            "S5 Ridge (5개 내용 구역 제외 vs 대조)",
            sub,
            lambda b, s=sub: (block_arr == b) & present_masks[s],
            lambda b, kd, s=sub: s5_zone_preds[(s, b, kd)],
        )
        for sub in PARTICIPANTS
    ]
    s5_m5 = {
        "model_id": "s5_ridge_zone",
        "display_name": "S5 Ridge (5개 내용 구역 제외 vs 대조)",
        "participant": "mean_5sub",
    }
    for k_col in [k for k in s5_sub_z[0].keys() if k not in ("model_id", "display_name", "participant")]:
        s5_m5[k_col] = float(np.mean([d[k_col] for d in s5_sub_z]))
    zone_summary_rows.append(s5_m5)
    zone_summary_rows.extend(s5_sub_z)

    df_zone_summary = pd.DataFrame(zone_summary_rows)
    df_zone_by_block = pd.DataFrame(zone_block_rows)

    # Master combined overview table s10_table6_selection_and_boundaries
    master_rows = []
    for _, zr in df_s6_zero.iterrows():
        master_rows.append({
            "section": "S6_zero_selected_and_weights",
            "item": zr["condition"],
            "label": zr["display_name"],
            "metric_1_name": "n_zero_selected_of_6",
            "metric_1_value": zr["n_zero_selected_G10"],
            "metric_2_name": "n_lam_or_alpha_zero_of_6",
            "metric_2_value": int(zr["n_lam_zero"] + zr["n_alpha_zero"]),
            "metric_3_name": "trainable_params_max_F8",
            "metric_3_value": zr["trainable_params_max_F8"],
            "detail": f"zero_folds={zr['zero_selected_folds']}; lam0_folds={zr['lam_zero_folds']}; d32={zr['d_32_count']},d64={zr['d_64_count']}",
        })
    for _, br in df_s5_bound.iterrows():
        master_rows.append({
            "section": "O18_lambda_boundary_counts",
            "item": f"{br['stage_task']}:{br['subgroup']}",
            "label": br["lambda_grid"],
            "metric_1_name": "at_low_end",
            "metric_1_value": br["at_low_end"],
            "metric_2_name": "at_high_end",
            "metric_2_value": br["at_high_end"],
            "metric_3_name": "total",
            "metric_3_value": br["total"],
            "detail": f"frac_either_end={br['frac_either_end']:.6f}",
        })
    for _, cr in s4_cap_summary.iterrows():
        master_rows.append({
            "section": "S4_O16_at_cap_counts",
            "item": f"{cr['model']}:{cr['version']}:lr={cr['lr']}",
            "label": f"{cr['model']} ({cr['version']})",
            "metric_1_name": "n_at_cap",
            "metric_1_value": cr["n_at_cap"],
            "metric_2_name": "n_runs",
            "metric_2_value": cr["n_runs"],
            "metric_3_name": "mean_val_r",
            "metric_3_value": cr["mean_val_r"],
            "detail": f"mean_epochs={cr['mean_epochs']:.1f}, max_epochs={cr['max_epochs']}",
        })
    for _, zsr in df_zone_summary[df_zone_summary["participant"].isin(["all_dev_2109", "mean_5sub"])].iterrows():
        master_rows.append({
            "section": "Zone_5block_summary_6_2",
            "item": f"{zsr['model_id']}:{zsr['participant']}",
            "label": zsr["display_name"],
            "metric_1_name": "five_block_mean_excluded",
            "metric_1_value": zsr["five_block_mean_excluded"],
            "metric_2_name": "five_block_mean_control",
            "metric_2_value": zsr["five_block_mean_control"],
            "metric_3_name": "diff_excluded_minus_control",
            "metric_3_value": zsr["five_block_mean_diff_excluded_minus_control"],
            "detail": "equal-weight mean across 5 content blocks",
        })
    for _, axr in df_s4_aux.iterrows():
        master_rows.append({
            "section": "S4_auxiliary_summaries",
            "item": f"{axr['analysis']}:{axr['key']}",
            "label": axr["analysis"],
            "metric_1_name": "metric_primary",
            "metric_1_value": axr["metric_primary"],
            "metric_2_name": "metric_secondary",
            "metric_2_value": axr["metric_secondary"],
            "metric_3_name": "n_items",
            "metric_3_value": axr["n_items"],
            "detail": axr["detail"],
        })
    df_t6_master = pd.DataFrame(master_rows)

    tables = {
        "s10_table6_selection_and_boundaries": df_t6_master,
        "s10_s6_selected_hyperparams": df_s6_sel,
        "s10_s6_zero_selected_summary": df_s6_zero,
        "s10_s6_weight_counts": wc_df,
        "s10_s5_lambda_boundary_counts": df_s5_bound,
        "s10_s4_selection_and_at_cap": s4_cap_summary,
        "s10_s4_auxiliary_summaries": df_s4_aux,
        "s10_s4_s5_zone_summary": df_zone_summary,
        "s10_s4_s5_zone_by_block": df_zone_by_block,
    }
    return tables, checks


def build_table7_statistical_tests(
    models: Dict[str, EmotionModelData],
    full_cache: Dict[str, dict],
    decoded_for_perm: Dict[str, object],
    y_em: np.ndarray,
    present_masks: Dict[str, np.ndarray],
    perm_idx: np.ndarray,
    perm_idx_free: np.ndarray,
) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """Build s10_table7_statistical_tests (10k within-run permutations + 10k canonical_id bootstraps)."""
    rows = []
    checks: Dict[str, object] = {}
    P_tot = perm_idx.shape[0]

    # =========================================================================
    # PART A: 10,000-Iteration Within-Run Permutation Tests (O4(1), O4(4), O4(6))
    # =========================================================================
    def run_emotion_perm_model(mid: str, perm_arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Returns obs_ps (5, n_seeds) and null_ps (5, n_seeds, P_tot)."""
        em = models[mid]
        n_seeds = 3 if em.is_multiseed else 1
        obs_ps = np.empty((len(PARTICIPANTS), n_seeds), dtype=np.float64)
        null_ps = np.empty((len(PARTICIPANTS), n_seeds, P_tot), dtype=np.float64)
        for p_i, sub in enumerate(PARTICIPANTS):
            pmask = present_masks[sub]
            for s_i in range(n_seeds):
                om, nm = fast_exact_perm_mean_r(
                    em.preds_sub[sub][s_i, pmask, :], y_em, pmask, perm_arr, chunk_size=250
                )
                obs_ps[p_i, s_i] = om
                null_ps[p_i, s_i] = nm
        return obs_ps, null_ps

    log("Running 10,000-iter within-run permutation tests for 0행 (A-1, C-1) + free-pair sensitivity check...")
    a1_obs, a1_null = run_emotion_perm_model("s6_brain_only", perm_idx)
    c1_obs, c1_null = run_emotion_perm_model("s6_brain_decoded", perm_idx)
    _, a1_null_free = run_emotion_perm_model("s6_brain_only", perm_idx_free)
    _, c1_null_free = run_emotion_perm_model("s6_brain_decoded", perm_idx_free)

    def one_sided_p(obs_v: float, null_v: np.ndarray) -> float:
        return float((1 + int(np.sum(null_v >= obs_v))) / (len(null_v) + 1))

    # Sensitivity diff between fixed-(1349,1363) and free within-run permutation
    p_a1_fixed = one_sided_p(float(a1_obs.mean()), a1_null.mean(axis=(0, 1)))
    p_a1_free = one_sided_p(float(a1_obs.mean()), a1_null_free.mean(axis=(0, 1)))
    p_c1_fixed = one_sided_p(float(c1_obs.mean()), c1_null.mean(axis=(0, 1)))
    p_c1_free = one_sided_p(float(c1_obs.mean()), c1_null_free.mean(axis=(0, 1)))
    null_mean_diff = max(
        abs(float(a1_null.mean()) - float(a1_null_free.mean())),
        abs(float(c1_null.mean()) - float(c1_null_free.mean())),
    )
    checks["perm_same_content_pair_sensitivity"] = {
        "a1_mean5sub_p_fixed": p_a1_fixed,
        "a1_mean5sub_p_free": p_a1_free,
        "c1_mean5sub_p_fixed": p_c1_fixed,
        "c1_mean5sub_p_free": p_c1_free,
        "max_abs_null_mean_diff": null_mean_diff,
        "max_abs_p_diff": max(abs(p_a1_fixed - p_a1_free), abs(p_c1_fixed - p_c1_free)),
    }

    # Holm-2 across (A-1, C-1) for 0행 prerequisite tests (separately on mean_5sub and each participant!)
    p_row0_m5 = holm_adjust(np.array([
        one_sided_p(float(a1_obs.mean()), a1_null.mean(axis=(0, 1))),
        one_sided_p(float(c1_obs.mean()), c1_null.mean(axis=(0, 1))),
    ]))
    p_row0_sub = np.empty((len(PARTICIPANTS), 2), dtype=np.float64)
    for p_i in range(len(PARTICIPANTS)):
        raw_pair = np.array([
            one_sided_p(float(a1_obs[p_i].mean()), a1_null[p_i].mean(axis=0)),
            one_sided_p(float(c1_obs[p_i].mean()), c1_null[p_i].mean(axis=0)),
        ])
        p_row0_sub[p_i] = holm_adjust(raw_pair)

    for idx_0, (mid, code, label, obs_ps, null_ps) in enumerate([
        ("s6_brain_only", "0행_A-1", "0행 전제 검정: A-1 (Brain → Emotion) vs 순열 귀무분포", a1_obs, a1_null),
        ("s6_brain_decoded", "0행_C-1", "0행 전제 검정: C-1 (Brain + Decoded Feature → Emotion) vs 순열 귀무분포", c1_obs, c1_null),
    ]):
        st_ci = full_cache[mid]
        null_m5 = null_ps.mean(axis=(0, 1))
        obs_m5_seeds = obs_ps.mean(axis=0)
        obs_m5 = float(obs_m5_seeds.mean())
        raw_p_m5 = one_sided_p(obs_m5, null_m5)
        sub_raw_ps = [one_sided_p(float(obs_ps[p_i].mean()), null_ps[p_i].mean(axis=0)) for p_i in range(len(PARTICIPANTS))]

        row = {
            "test_id": code,
            "family_group": "0행_전제검정_Holm2",
            "is_prereg_15": False,
            "method": "within_run_permutation_10000_one_sided",
            "comparison_label": label,
            "cond_a": mid,
            "cond_b": "permutation_null",
            "mean_5sub_effect": obs_m5,
            "mean_5sub_seed_sd": float(np.std(obs_m5_seeds, ddof=1)),
            "mean_5sub_seed0": float(obs_m5_seeds[0]),
            "mean_5sub_seed1": float(obs_m5_seeds[1]),
            "mean_5sub_seed2": float(obs_m5_seeds[2]),
            "mean_5sub_ci_low": st_ci["mean_5sub_ci_low"],
            "mean_5sub_ci_high": st_ci["mean_5sub_ci_high"],
            "null_mean_5sub": float(null_m5.mean()),
            "null_sd_5sub": float(np.std(null_m5, ddof=1)),
            "null_q95_5sub": float(np.quantile(null_m5, 0.95)),
            "mean_5sub_p_raw": raw_p_m5,
            "mean_5sub_p_holm_family": float(p_row0_m5[idx_0]),
            "holm_family_note": "Holm-2 (0행 전제 검정 2개 묶음)",
            "n_confirmed_pos_unadj": int(sum(p < 0.05 for p in sub_raw_ps)),
            "n_confirmed_neg_unadj": 0,
            "n_confirmed_pos_holm_family": int(sum(p_row0_sub[p_i, idx_0] < 0.05 for p_i in range(len(PARTICIPANTS)))),
        }
        # Also record per-seed permutation p-values on mean_5sub
        for s_i in range(3):
            row[f"mean_5sub_seed{s_i}_p_raw"] = one_sided_p(float(obs_m5_seeds[s_i]), null_ps[:, s_i, :].mean(axis=0))
        for p_i, sub in enumerate(PARTICIPANTS):
            row[f"{sub}_effect"] = float(obs_ps[p_i].mean())
            row[f"{sub}_seed_sd"] = float(np.std(obs_ps[p_i], ddof=1))
            row[f"{sub}_ci_low"] = st_ci[f"{sub}_ci_low"]
            row[f"{sub}_ci_high"] = st_ci[f"{sub}_ci_high"]
            row[f"{sub}_p_raw"] = sub_raw_ps[p_i]
            row[f"{sub}_p_holm_family"] = float(p_row0_sub[p_i, idx_0])
        rows.append(row)

    # [사전] 2-1 S5 Ridge Feature Decoding + Exploratory C-1 Decoded Feature Permutation Tests
    log("Running 10,000-iter within-run permutation tests for [사전] 2-1 Vision (5,632d) & Caption (4,096d) + C-1...")
    v_true = decoded_for_perm["v_true"]
    c_true = decoded_for_perm["c_true"]

    feat_perm_specs = [
        ("2-1_ridge_vision", "[사전]_15_중_2-1", True, "[사전] 2-1: S5 Ridge Vision (5,632d) vs 순열 귀무분포", decoded_for_perm["s5_vision"], v_true, decoded_for_perm["s5_vis_ci"], 50),
        ("2-1_ridge_caption", "[사전]_15_중_2-1", True, "[사전] 2-1: S5 Ridge Caption (4,096d) vs 순열 귀무분포", decoded_for_perm["s5_caption"], c_true, decoded_for_perm["s5_cap_ci"], 60),
        ("expl_C1_decoded_vision", "탐색_C1_feature_decoding", False, "탐색 참고: C-1 Decoded Vision (5,632d) vs 순열 귀무분포", decoded_for_perm["c1_vision"], v_true, None, 40),
        ("expl_C1_decoded_caption", "탐색_C1_feature_decoding", False, "탐색 참고: C-1 Decoded Caption (4,096d) vs 순열 귀무분포", decoded_for_perm["c1_caption"], c_true, None, 50),
    ]

    for tid, fgrp, is_pre, label, pred_dict, t_arr, ci_dict, csz in feat_perm_specs:
        n_seeds = pred_dict[PARTICIPANTS[0]].shape[0]
        obs_ps = np.empty((len(PARTICIPANTS), n_seeds), dtype=np.float64)
        null_ps = np.empty((len(PARTICIPANTS), n_seeds, P_tot), dtype=np.float64)
        for p_i, sub in enumerate(PARTICIPANTS):
            pmask = present_masks[sub]
            for s_i in range(n_seeds):
                om, nm = fast_exact_perm_mean_r(pred_dict[sub][s_i], t_arr, pmask, perm_idx, chunk_size=csz)
                obs_ps[p_i, s_i] = om
                null_ps[p_i, s_i] = nm

        null_m5 = null_ps.mean(axis=(0, 1))
        obs_m5_seeds = obs_ps.mean(axis=0)
        obs_m5 = float(obs_m5_seeds.mean())
        raw_p_m5 = one_sided_p(obs_m5, null_m5)
        sub_raw_ps = [one_sided_p(float(obs_ps[p_i].mean()), null_ps[p_i].mean(axis=0)) for p_i in range(len(PARTICIPANTS))]

        row = {
            "test_id": tid,
            "family_group": fgrp,
            "is_prereg_15": is_pre,
            "method": "within_run_permutation_10000_one_sided",
            "comparison_label": label,
            "cond_a": tid,
            "cond_b": "permutation_null",
            "mean_5sub_effect": obs_m5,
            "mean_5sub_seed_sd": float(np.std(obs_m5_seeds, ddof=1)) if n_seeds > 1 else np.nan,
            "mean_5sub_seed0": float(obs_m5_seeds[0]),
            "mean_5sub_seed1": float(obs_m5_seeds[1]) if n_seeds > 1 else np.nan,
            "mean_5sub_seed2": float(obs_m5_seeds[2]) if n_seeds > 1 else np.nan,
            "mean_5sub_ci_low": ci_dict["mean_5sub"][0] if ci_dict is not None else np.nan,
            "mean_5sub_ci_high": ci_dict["mean_5sub"][1] if ci_dict is not None else np.nan,
            "null_mean_5sub": float(null_m5.mean()),
            "null_sd_5sub": float(np.std(null_m5, ddof=1)),
            "null_q95_5sub": float(np.quantile(null_m5, 0.95)),
            "mean_5sub_p_raw": raw_p_m5,
            "mean_5sub_p_holm_family": np.nan,  # filled below for prereg S10-8
            "holm_family_note": "Holm-15 대상 (S10 내 8개 부분 묶음 보정값 병기)" if is_pre else "탐색 참고 (Holm-15 제외)",
            "n_confirmed_pos_unadj": int(sum(p < 0.05 for p in sub_raw_ps)),
            "n_confirmed_neg_unadj": 0,
            "n_confirmed_pos_holm_family": np.nan,
        }
        if n_seeds > 1:
            for s_i in range(3):
                row[f"mean_5sub_seed{s_i}_p_raw"] = one_sided_p(float(obs_m5_seeds[s_i]), null_ps[:, s_i, :].mean(axis=0))
        for p_i, sub in enumerate(PARTICIPANTS):
            row[f"{sub}_effect"] = float(obs_ps[p_i].mean())
            row[f"{sub}_seed_sd"] = float(np.std(obs_ps[p_i], ddof=1)) if n_seeds > 1 else np.nan
            row[f"{sub}_ci_low"] = ci_dict[sub][0] if ci_dict is not None else np.nan
            row[f"{sub}_ci_high"] = ci_dict[sub][1] if ci_dict is not None else np.nan
            row[f"{sub}_p_raw"] = sub_raw_ps[p_i]
            row[f"{sub}_p_holm_family"] = np.nan
        rows.append(row)

    # =========================================================================
    # PART B: 10,000-Iteration canonical_id Video-Unit Bootstrap Comparisons (O4(3))
    # =========================================================================
    log("Computing 10,000-iter canonical_id bootstrap CIs & Hall-Wilson p-values across all comparisons...")
    boot_comparisons = [
        # [사전] 2-3 (6 comparisons)
        ("2-3_가_B1_vs_A1", "[사전]_15_중_2-3", True, "[사전] 2-3(가): B-1 - A-1 (특징 보조손실 효과)", "s6_brain_only_featdec", "s6_brain_only"),
        ("2-3_나_C1_vs_B1", "[사전]_15_중_2-3", True, "[사전] 2-3(나): C-1 - B-1 (정서 head 특징 입력 효과)", "s6_brain_decoded", "s6_brain_only_featdec"),
        ("2-3_다_A2_vs_A1", "[사전]_15_중_2-3", True, "[사전] 2-3(다): A-2 - A-1 (예측 평정 증류 효과)", "s6_brain_only_distill", "s6_brain_only"),
        ("2-3_라_A2_vs_label_smoothing", "[사전]_15_중_2-3", True, "[사전] 2-3(라): A-2 - label_smoothing (평정 내용 vs 완화 정칙화)", "s6_brain_only_distill", "s6_control_label_smoothing"),
        ("2-3_마_B1_vs_A2", "[사전]_15_중_2-3", True, "[사전] 2-3(마): B-1 - A-2 (특징 보조손실 vs 예측 평정 증류)", "s6_brain_only_featdec", "s6_brain_only_distill"),
        ("2-3_바_C2_vs_C1", "[사전]_15_중_2-3", True, "[사전] 2-3(바): C-2 - C-1 (C-1 위 증류 추가 효과)", "s6_brain_decoded_distill", "s6_brain_decoded"),
        # G6 Shuffle Controls
        ("G6_B1_vs_feat_shuffle", "보조_G6_대응섞기대조", False, "보조 G6: B-1 - control_feature_shuffle (올바른 특징 vs 섞은 특징)", "s6_brain_only_featdec", "s6_control_feature_shuffle"),
        ("G6_A2_vs_stim_shuffle", "보조_G6_대응섞기대조", False, "보조 G6: A-2 - control_stimulus_shuffle (올바른 예측 평정 vs 섞은 평정)", "s6_brain_only_distill", "s6_control_stimulus_shuffle"),
        # F7 / N22 Mean Pooling Ablations
        ("F7_A1_vs_A1_pool", "보조_F7_N22_평균풀링", False, "보조 F7(N22): A-1 - A-1_pool (정서별 query vs 평균 pooling)", "s6_brain_only", "s6_brain_only_pool"),
        ("F7_C1_vs_C1_pool", "보조_F7_N22_평균풀링", False, "보조 F7(N22): C-1 - C-1_pool (정서별 query vs 평균 pooling)", "s6_brain_decoded", "s6_brain_decoded_pool"),
        # G8 Stop-gradient Ablation
        ("G8_C1_vs_C1_grad", "보조_G8_기울기차단", False, "보조 G8: C-1 - C-1_grad (stop-gradient vs 손실 흐름 허용판)", "s6_brain_decoded", "s6_brain_decoded_grad"),
        # 1-2(가) Interaction vs Additive Head
        ("1-2_가_C1_vs_C1_additive", "보조_1-2가_결합방식", False, "보조 1-2(가): C-1 - C-1_additive (상호작용 head vs 더하기 head)", "s6_brain_decoded", "s6_brain_decoded_additive"),
        # D Family (2-stage / Separate Encoder / Paired Frozen Encoder)
        ("D_D1_vs_C1", "보조_D묶음_2단계구조", False, "보조 D묶음: D-1 - C-1 (별도 encoder vs 공유 encoder)", "s6_brain_decoded_sep", "s6_brain_decoded"),
        ("D_D1_vs_B1", "보조_D묶음_2단계구조", False, "보조 D묶음: D-1 - B-1", "s6_brain_decoded_sep", "s6_brain_only_featdec"),
        ("D_D2_vs_C2", "보조_D묶음_2단계구조", False, "보조 D묶음: D-2 - C-2 (별도 encoder 증류 vs 공유 encoder 증류)", "s6_brain_decoded_sep_distill", "s6_brain_decoded_distill"),
        ("D_D2_vs_D1", "보조_D묶음_2단계구조", False, "보조 D묶음: D-2 - D-1 (별도 encoder 위 증류 효과)", "s6_brain_decoded_sep_distill", "s6_brain_decoded_sep"),
        ("D_D4_ens_vs_A1", "보조_D묶음_2단계구조", False, "보조 D묶음: D-4 (짝 앙상블) - A-1", "s6_brain_frozen_feature_encoder", "s6_brain_only"),
        ("D_D4_single_vs_A1", "보조_D묶음_2단계구조", False, "보조 D묶음 (5-A): D-4 (짝 단일 평균) - A-1 (앙상블 효과 제거 비교)", "s6_brain_frozen_feature_encoder_single_pair", "s6_brain_only"),
        ("D_D4_ens_vs_D3_paired_ens", "보조_D묶음_2단계구조", False, "보조 D묶음: D-4 (짝 앙상블) - D-3_paired (짝 앙상블)", "s6_brain_frozen_feature_encoder", "s6_brain_features_only_paired"),
        ("D_D4_single_vs_D3_paired_single", "보조_D묶음_2단계구조", False, "보조 D묶음 (5-A): D-4 (짝 단일 평균) - D-3_paired (짝 단일 평균)", "s6_brain_frozen_feature_encoder_single_pair", "s6_brain_features_only_paired_single_pair"),
        ("D_D3_vs_A1", "보조_D묶음_2단계구조", False, "보조 D묶음: D-3 (OOF Decoded Feature → Emotion) - A-1", "s6_brain_features_only", "s6_brain_only"),
        ("D_D3_vs_C1", "보조_D묶음_2단계구조", False, "보조 D묶음: D-3 (OOF Decoded Feature → Emotion) - C-1", "s6_brain_features_only", "s6_brain_decoded"),
        # E Family (G16 Multimodal Representation Transfer)
        ("E_frozen_vs_A1", "보조_E묶음_G16_표현전달", False, "보조 E묶음(G16): E-고정 - A-1", "s6_brain_only_repr_frozen", "s6_brain_only"),
        ("E_frozen_vs_C1", "보조_E묶음_G16_표현전달", False, "보조 E묶음(G16): E-고정 - C-1", "s6_brain_only_repr_frozen", "s6_brain_decoded"),
        ("E_trained_vs_A1", "보조_E묶음_G16_표현전달", False, "보조 E묶음(G16): E-학습 - A-1", "s6_brain_only_repr_trained", "s6_brain_only"),
        ("E_trained_vs_C1", "보조_E묶음_G16_표현전달", False, "보조 E묶음(G16): E-학습 - C-1", "s6_brain_only_repr_trained", "s6_brain_decoded"),
        ("E_trained_vs_E_frozen", "보조_E묶음_G16_표현전달", False, "보조 E묶음(G16): E-학습 - E-고정", "s6_brain_only_repr_trained", "s6_brain_only_repr_frozen"),
        # Baselines (N23)
        ("N23_A1_vs_ridge_main", "보조_N23_기준선비교", False, "보조 N23: A-1 - ridge_main", "s6_brain_only", "s5_ridge_main"),
        ("N23_C1_vs_ridge_main", "보조_N23_기준선비교", False, "보조 N23: C-1 - ridge_main", "s6_brain_decoded", "s5_ridge_main"),
        ("N23_C2_vs_ridge_main", "보조_N23_기준선비교", False, "보조 N23: C-2 - ridge_main", "s6_brain_decoded_distill", "s5_ridge_main"),
        ("N23_A1_vs_soft_bce", "보조_N23_기준선비교", False, "보조 N23: A-1 - soft_bce", "s6_brain_only", "s5_soft_bce"),
        ("N23_A1_vs_mlp", "보조_N23_기준선비교", False, "보조 N23: A-1 - mlp", "s6_brain_only", "s5_mlp"),
        ("N23_A1_vs_h2020", "보조_N23_기준선비교", False, "보조 N23: A-1 - h2020", "s6_brain_only", "s5_h2020"),
        ("N23_C1_vs_h2020", "보조_N23_기준선비교", False, "보조 N23: C-1 - h2020", "s6_brain_decoded", "s5_h2020"),
        ("N23_C2_vs_h2020", "보조_N23_기준선비교", False, "보조 N23: C-2 - h2020", "s6_brain_decoded_distill", "s5_h2020"),
        ("N23_A1_vs_ged", "보조_N23_기준선비교", False, "보조 N23: A-1 - ged", "s6_brain_only", "s5_ged"),
        ("N23_A1_vs_emogrowth", "보조_N23_기준선비교", False, "보조 N23: A-1 - emogrowth", "s6_brain_only", "s5_emogrowth"),
        ("N23_A1_vs_signal", "보조_N23_기준선비교", False, "보조 N23: A-1 - signal", "s6_brain_only", "s5_signal"),
    ]

    def per_emotion_vec(mid: str) -> np.ndarray:
        """Return 5-participant mean per-emotion r vector (34,) averaged across seeds."""
        em = models[mid]
        n_seeds = 3 if em.is_multiseed else 1
        mat = np.empty((len(PARTICIPANTS), n_seeds, N_EMOTIONS), dtype=np.float64)
        for p_i, sub in enumerate(PARTICIPANTS):
            pm = present_masks[sub]
            for s_i in range(n_seeds):
                if not em.is_single_pair_avg:
                    mat[p_i, s_i] = c.pearson(y_em[pm], em.preds_sub[sub][s_i, pm, :])
                else:
                    mat[p_i, s_i] = np.nanmean(
                        np.stack([c.pearson(y_em[pm], em.preds_sub[sub][s_i, j, pm, :]) for j in range(4)], axis=0),
                        axis=0,
                    )
        return mat.mean(axis=(0, 1))

    em_vec_cache: Dict[str, np.ndarray] = {}

    for tid, fgrp, is_pre, label, ma, mb in boot_comparisons:
        st_a = full_cache[ma]
        st_b = full_cache[mb]
        ema = models[ma]
        emb = models[mb]

        obs_m5 = st_a["mean_5sub"] - st_b["mean_5sub"]
        boot_m5 = st_a["_boot_m5"] - st_b["_boot_m5"]
        cil_m5, cih_m5 = basic_ci(obs_m5, boot_m5)
        p_m5 = hall_wilson_p(obs_m5, boot_m5)

        # Seed-level differences when applicable (Rule G14)
        if ema.is_multiseed and emb.is_multiseed:
            d_seeds = [st_a[f"mean_5sub_seed{s}"] - st_b[f"mean_5sub_seed{s}"] for s in range(3)]
            s0, s1, s2, ssd = d_seeds[0], d_seeds[1], d_seeds[2], float(np.std(d_seeds, ddof=1))
        elif ema.is_multiseed and not emb.is_multiseed:
            d_seeds = [st_a[f"mean_5sub_seed{s}"] - st_b["mean_5sub"] for s in range(3)]
            s0, s1, s2, ssd = d_seeds[0], d_seeds[1], d_seeds[2], float(np.std(d_seeds, ddof=1))
        elif not ema.is_multiseed and emb.is_multiseed:
            d_seeds = [st_a["mean_5sub"] - st_b[f"mean_5sub_seed{s}"] for s in range(3)]
            s0, s1, s2, ssd = d_seeds[0], d_seeds[1], d_seeds[2], float(np.std(d_seeds, ddof=1))
        else:
            s0, s1, s2, ssd = obs_m5, np.nan, np.nan, np.nan

        # Per-emotion summary (6-1 rule: how many of 34 emotions increased, median/min/max)
        if ma not in em_vec_cache:
            em_vec_cache[ma] = per_emotion_vec(ma)
        if mb not in em_vec_cache:
            em_vec_cache[mb] = per_emotion_vec(mb)
        em_diff = em_vec_cache[ma] - em_vec_cache[mb]

        sub_effs, sub_ps, sub_cils, sub_cihs, sub_sds = [], [], [], [], []
        for p_i, sub in enumerate(PARTICIPANTS):
            eff_s = st_a[sub] - st_b[sub]
            b_s = st_a["_boot_sub"][p_i] - st_b["_boot_sub"][p_i]
            cl_s, ch_s = basic_ci(eff_s, b_s)
            ps_val = hall_wilson_p(eff_s, b_s)
            if ema.is_multiseed and emb.is_multiseed:
                ds = [st_a[f"{sub}_seed{s}"] - st_b[f"{sub}_seed{s}"] for s in range(3)]
                sd_s = float(np.std(ds, ddof=1))
            elif ema.is_multiseed:
                ds = [st_a[f"{sub}_seed{s}"] - st_b[sub] for s in range(3)]
                sd_s = float(np.std(ds, ddof=1))
            else:
                sd_s = np.nan
            sub_effs.append(eff_s)
            sub_ps.append(ps_val)
            sub_cils.append(cl_s)
            sub_cihs.append(ch_s)
            sub_sds.append(sd_s)

        n_pos_unadj = int(sum((sub_ps[i] < 0.05) and (sub_effs[i] > 0) for i in range(len(PARTICIPANTS))))
        n_neg_unadj = int(sum((sub_ps[i] < 0.05) and (sub_effs[i] < 0) for i in range(len(PARTICIPANTS))))

        row = {
            "test_id": tid,
            "family_group": fgrp,
            "is_prereg_15": is_pre,
            "method": "canonical_id_bootstrap_10000_two_sided_Hall_Wilson",
            "comparison_label": label,
            "cond_a": ma,
            "cond_b": mb,
            "mean_5sub_effect": obs_m5,
            "mean_5sub_seed_sd": ssd,
            "mean_5sub_seed0": s0,
            "mean_5sub_seed1": s1,
            "mean_5sub_seed2": s2,
            "mean_5sub_ci_low": cil_m5,
            "mean_5sub_ci_high": cih_m5,
            "null_mean_5sub": 0.0,
            "null_sd_5sub": float(np.std(boot_m5 - obs_m5, ddof=1)),
            "null_q95_5sub": np.nan,
            "mean_5sub_p_raw": p_m5,
            "mean_5sub_p_holm_family": np.nan,
            "holm_family_note": "Holm-15 대상 (S10 내 8개 부분 묶음 보정값 병기)" if is_pre else "보조 비교 (Holm-15 제외, 개별 보고)",
            "n_confirmed_pos_unadj": n_pos_unadj,
            "n_confirmed_neg_unadj": n_neg_unadj,
            "n_confirmed_pos_holm_family": np.nan,
            "n_emotions_pos_of_34": int(np.sum(em_diff > 0)),
            "emotion_diff_median": float(np.nanmedian(em_diff)),
            "emotion_diff_min": float(np.nanmin(em_diff)),
            "emotion_diff_max": float(np.nanmax(em_diff)),
        }
        for p_i, sub in enumerate(PARTICIPANTS):
            row[f"{sub}_effect"] = sub_effs[p_i]
            row[f"{sub}_seed_sd"] = sub_sds[p_i]
            row[f"{sub}_ci_low"] = sub_cils[p_i]
            row[f"{sub}_ci_high"] = sub_cihs[p_i]
            row[f"{sub}_p_raw"] = sub_ps[p_i]
            row[f"{sub}_p_holm_family"] = np.nan
        rows.append(row)

    df_t7 = pd.DataFrame(rows)

    # Apply partial Holm-8 across the 8 [사전] tests computed here (2 from 2-1 + 6 from 2-3),
    # AND record worst-case Holm-15 upper bound min(1, 15 * p_raw) so coordinator has both!
    pre_mask = df_t7["is_prereg_15"].to_numpy(dtype=bool)
    assert int(pre_mask.sum()) == 8
    df_t7.loc[pre_mask, "mean_5sub_p_holm_family"] = holm_adjust(df_t7.loc[pre_mask, "mean_5sub_p_raw"].to_numpy())
    df_t7["mean_5sub_p_holm15_upper_bound"] = np.where(
        pre_mask, np.minimum(1.0, 15.0 * df_t7["mean_5sub_p_raw"].to_numpy()), np.nan
    )

    pre_indices = np.flatnonzero(pre_mask)
    sub_holm8 = {}
    for sub in PARTICIPANTS:
        adj_s = holm_adjust(df_t7.loc[pre_mask, f"{sub}_p_raw"].to_numpy())
        df_t7.loc[pre_mask, f"{sub}_p_holm_family"] = adj_s
        df_t7[f"{sub}_p_holm15_upper_bound"] = np.where(
            pre_mask, np.minimum(1.0, 15.0 * df_t7[f"{sub}_p_raw"].to_numpy()), np.nan
        )
        sub_holm8[sub] = adj_s

    for local_i, r_idx in enumerate(pre_indices):
        n_pos_h8 = sum(
            (sub_holm8[sub][local_i] < 0.05) and (float(df_t7.loc[r_idx, f"{sub}_effect"]) > 0)
            for sub in PARTICIPANTS
        )
        n_pos_h15_ub = sum(
            (float(df_t7.loc[r_idx, f"{sub}_p_holm15_upper_bound"]) < 0.05)
            and (float(df_t7.loc[r_idx, f"{sub}_effect"]) > 0)
            for sub in PARTICIPANTS
        )
        df_t7.loc[r_idx, "n_confirmed_pos_holm_family"] = int(n_pos_h8)
        df_t7.loc[r_idx, "n_confirmed_pos_holm15_upper_bound"] = int(n_pos_h15_ub)

    return df_t7, checks


def main() -> None:
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log(f"Starting S10 evaluation on CPU (threads={torch.get_num_threads()}, CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')!r})")

    # 1. Load split, labels, durations, multi-window IDs, participant blocks
    split = c.load_split()
    assert len(split) == 2109, f"Expected 2,109 dev videos, got {len(split)}"
    y_em, score_cols = c.load_scores(split, "emotions")
    y_em = y_em.astype(np.float64)
    assert y_em.shape == (2109, 34)

    label_map = pd.read_csv(c.LABEL_MAP, sep="\t")
    assert label_map["score_col"].tolist() == score_cols

    stimuli = pd.read_csv(d5.STIMULI, sep="\t", comment="#").set_index("video_number")
    dur_s = stimuli.loc[split["video_id"], "container_duration_s"].to_numpy(np.float64)
    log_dur = np.log(dur_s)

    win_npz = np.load(c.FEATURES / "vjepa2/windows_per_video.npz")
    multi_window_ids = set(int(k[1:]) for k in win_npz.files) & set(split["video_id"].tolist())
    assert len(multi_window_ids) == 80, f"Expected 80 multi-window dev videos, got {len(multi_window_ids)}"

    pb = pd.read_csv(d5.BLOCKS, sep="\t")
    present_masks = {
        sub: split["video_id"].isin(pb.loc[pb["participant"] == sub, "video_id"]).to_numpy(dtype=bool)
        for sub in PARTICIPANTS
    }
    sub_counts = {sub: int(present_masks[sub].sum()) for sub in PARTICIPANTS}
    assert sum(sub_counts.values()) == 10402

    # 2. Build RNG bootstrap & permutation structures + run mathematical unit assertions
    log("Building 10,000-iteration canonical_id bootstrap weights and (fold, run_index) permutations...")
    unique_cids, boot_draws, W_all, boot_seed_int, perm_idx, perm_idx_free, perm_seed_int = (
        build_bootstrap_and_permutations(split)
    )
    unit_checks = run_unit_assertions(split, y_em, present_masks, W_all, boot_draws, unique_cids, perm_idx)
    log(f"Unit assertions passed: {unit_checks}")

    # 3. Collect all S6, S5, and S4 emotion predictions
    log("Collecting S6 (20 conditions + 2 single-pair), S5 baselines, and S4 no-brain predictions...")
    models, m_dk_sub, m_dk_all, loader_checks = collect_all_emotion_models(split, y_em, present_masks)

    saved_files: List[str] = []

    # 4. Table 1 & Table 2
    log("Computing Table 1 (primary metrics + 10k bootstrap CIs) and Table 2 (subsets & duration bins)...")
    df_t1, df_t2, full_cache = build_table1_and_table2(
        models, split, y_em, present_masks, dur_s, multi_window_ids, W_all
    )
    saved_files.extend(save_tsv_csv(df_t1, "s10_table1_primary_metrics"))
    saved_files.extend(save_tsv_csv(df_t2, "s10_table2_subsets_and_duration"))

    # 5. Table 3
    log("Computing Table 3 (auxiliary metrics: O25 error reduction, profile r, MAE/RMSE zero vs pos, O19 ident, N21 partial r)...")
    df_t3 = build_table3_auxiliary(models, split, y_em, present_masks, m_dk_sub, m_dk_all, log_dur)
    saved_files.extend(save_tsv_csv(df_t3, "s10_table3_auxiliary_metrics"))

    # 6. Table 4
    log("Computing Table 4 (34 emotions + 10k bootstrap CIs + 1-2(가) C-1 vs C-1_additive BH-FDR)...")
    df_t4, df_t4_long = build_table4_per_emotion(models, label_map, y_em, present_masks, W_all)
    saved_files.extend(save_tsv_csv(df_t4, "s10_table4_per_emotion_34"))
    saved_files.extend(save_tsv_csv(df_t4_long, "s10_table4b_per_emotion_long"))

    # 7. Table 5
    log("Computing Table 5 (S5 64-layer + primary targets + S6 decoded_test O20 r & O19 D9 identification)...")
    df_t5, df_t5_64, decoded_for_perm, t5_checks = build_table5_feature_decoding(split, present_masks, W_all)
    saved_files.extend(save_tsv_csv(df_t5, "s10_table5_feature_decoding"))
    saved_files.extend(save_tsv_csv(df_t5_64, "s10_table5b_s5_64layers_full"))

    # 8. Table 6 Bundle
    log("Computing Table 6 bundle (S6 hyperparams & zero_selected & F8 weights, S5 O18 boundaries, S4 at_cap, 6-2 zone)...")
    t6_tables, t6_checks = build_table6_bundle(split, y_em, present_masks)
    for stem, df_sub in t6_tables.items():
        saved_files.extend(save_tsv_csv(df_sub, stem))

    # 9. Table 7
    log("Computing Table 7 (10,000-iter within-run permutation tests & 10,000-iter canonical_id bootstrap tests)...")
    df_t7, t7_checks = build_table7_statistical_tests(
        models, full_cache, decoded_for_perm, y_em, present_masks, perm_idx, perm_idx_free
    )
    saved_files.extend(save_tsv_csv(df_t7, "s10_table7_statistical_tests"))

    elapsed = time.time() - t0
    input_sha256 = {
        "split_hk_dev.tsv": c.sha256(P.SPLITS / "split_hk_dev.tsv"),
        "cowen_horikawa_labels.csv": c.sha256(c.LABELS),
        "label_map_34.tsv": c.sha256(c.LABEL_MAP),
        "stimuli.tsv": c.sha256(d5.STIMULI),
        "participant_blocks_hk.tsv": c.sha256(d5.BLOCKS),
        "content_blocks_assignment.tsv": c.sha256(c.S2 / "content_blocks_assignment.tsv"),
        "windows_per_video.npz": c.sha256(c.FEATURES / "vjepa2/windows_per_video.npz"),
        "vjepa2_target.npy": c.sha256(c.FEATURES / "vjepa2/target.npy"),
        "deberta_target.npy": c.sha256(c.FEATURES / "deberta/target.npy"),
        "weight_counts.tsv": c.sha256(P.MANIFESTS / "s6/weight_counts.tsv"),
        "s5_decoding_layer_metrics.tsv": c.sha256(P.OUT / "s5_collect/decoding_layer_metrics.tsv"),
        "s4_feature_model_selection.tsv": c.sha256(P.OUT / "s4_collect/feature_model_selection.tsv"),
    }
    output_sha256 = {Path(p).name: c.sha256(Path(p)) for p in saved_files}

    prov = {
        "script": str(Path(__file__).resolve()),
        "script_sha256": c.sha256(Path(__file__).resolve()),
        "code_repo_head": c.START_HEAD,
        "code_repo_dirty": c.START_DIRTY,
        "cpu_only_enforced": not USE_SLURM_GPU,
        "slurm_gpu_mode": USE_SLURM_GPU,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "cuda_available": bool(torch.cuda.is_available()),
        "torch_num_threads": int(torch.get_num_threads()),
        "runtime_seconds": round(elapsed, 2),
        "counts": {
            "n_dev_videos": int(len(split)),
            "n_in_all_5_videos": int(split["in_all_5"].sum()),
            "n_canonical_id_clusters": int(len(unique_cids)),
            "n_multi_window_dev_videos": int(len(multi_window_ids)),
            "n_single_window_dev_videos": int(len(split) - len(multi_window_ids)),
            "n_exchangeability_blocks_fold_run": 61,
            "participant_video_counts": sub_counts,
            "n_bootstrap_iterations": N_BOOT,
            "n_permutation_iterations": N_PERM,
        },
        "rng_seeds": {
            "within_run_permutation_bytes": PERM_SEED_BYTES.decode(),
            "within_run_permutation_uint64": perm_seed_int,
            "video_canonical_bootstrap_bytes": BOOT_SEED_BYTES.decode(),
            "video_canonical_bootstrap_uint64": boot_seed_int,
            "seed_derivation": "int.from_bytes(hashlib.sha256(seed_bytes).digest()[:8], 'big')",
        },
        "verification_checks": {
            **unit_checks,
            **loader_checks,
            **t5_checks,
            **t6_checks,
            **t7_checks,
        },
        "input_sha256": input_sha256,
        "output_files": saved_files,
        "output_sha256": output_sha256,
    }
    prov_path = OUT_DIR / "provenance.json"
    prov_path.write_text(json.dumps(prov, indent=2, ensure_ascii=False))
    log(f"All S10 tables and provenance.json saved in {elapsed:.1f}s -> {OUT_DIR}")


if __name__ == "__main__":
    main()
