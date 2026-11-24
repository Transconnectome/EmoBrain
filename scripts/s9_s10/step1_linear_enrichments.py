#!/usr/bin/env python3
"""Step 1 Whole-Brain Linear Enrichments (Zero src/ Modifications).

Runs immediately after authentic Glasser HCP360 + PickAtlas S2 roi_voxels sync
and Step 1 S5 linear re-run, producing three reviewer-critical analyses:

1. K1 Non-Circularity & Alternative Visual Backbone Check
   (`step1_k1_noncircularity_and_clip.tsv`):
   - Decodes emotion-word-stripped captions (`deberta_no_emotion_words/target.npy`, 4,096d;
     181 emotion words removed) and CLIP visual features (`clip/image.npy`, 512d) from
     whole-brain fMRI via canonical `s5_common.main_version` dual ridge.
   - Evaluates frozen `S4 noemo` (`noemo/fold{k}/model.pt`) and `S4 clip`
     (`baseline/clip_fold{k}/model.pt`) heads (uncalibrated + H2 validation N8 calibrated)
     against direct `S5 Ridge` (`emotion_main`) with 10,000-iteration `canonical_id`
     cluster bootstrap CIs and two-sided Hall-Wilson p-values.

2. Out-of-Zone Generalization of Linear Semantic Mediation
   (`step1_k1_zone_generalization.tsv`, replacing 60-split neural S8 6-2):
   - Across all 5 content zones x 6 folds x 2 modes (`excluded`, `control`) x 5 subjects,
     decodes `(V-JEPA2 5,632d, DeBERTa 4,096d)` strictly on zone-allowed training/val rows
     and applies the frozen `S4 zone` head (`zone/block{b}_fold{k}_{kind}/model.pt`).
   - Compares `K1_zone` (`excluded - control`) directly against `S5 Ridge zone`.

3. Confound-Free 13-Network Whole-Brain Ridge Leave-One-Network-Out & Single-Network-Only
   (`step1_cabnp13_lono_ridge.tsv`, replacing architectural-confound 6-4b & S8 6-4a):
   - Uses `manifests/s2/roi_table.tsv` + `manifests/s2/cabnp_groups.tsv` (12 cortical
     CAB-NP networks + `Subcortex` anatomical group).
   - Computes both Leave-One-Network-Out (`LONO`: drop group g's unique voxels, `r_full - r_drop`)
     and Single-Network-Only (`SNO`: fit dual ridge on group g's unique voxels alone)
     for 34 emotions and 14 affective dimensions (`B4`), reporting raw `Delta r`,
     per-1,000-voxel normalized `Delta r`, 10,000-iter `canonical_id` bootstrap CIs,
     Holm-13 adjusted p-values, and 5-participant random-effects t_4 tests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

_LOCAL_SRC = Path(__file__).resolve().parents[2] / "src"
REPO_SRC = _LOCAL_SRC if _LOCAL_SRC.is_dir() else Path("/scratch/emobrain/code/src")
sys.path.insert(0, str(REPO_SRC))

import numpy as np
import pandas as pd
from scipy import stats
import torch

import paths as P
import s4_common as c
from s4_feature_model import FeatureModel
import s5_common as d5

BOOT_SEED_TAG = b"EmoBrain/O4/video_canonical_bootstrap"
N_BOOT = 10_000
PARTICIPANTS = [f"sub-{s}" for s in d5.HK]


def build_boot_weights(split: pd.DataFrame, n_boot: int = N_BOOT) -> np.ndarray:
    """Exact O4(3) canonical_id cluster bootstrap weights (B, 2109)."""
    seed_int = int.from_bytes(hashlib.sha256(BOOT_SEED_TAG).digest()[:8], "big")
    rng = np.random.default_rng(seed_int)
    unique_cids = np.sort(split["canonical_id"].unique().astype(np.int64))
    assert len(unique_cids) == 2108
    cid_to_idx = {int(cid): i for i, cid in enumerate(unique_cids.tolist())}
    row_cluster = np.array([cid_to_idx[int(cid)] for cid in split["canonical_id"].tolist()], dtype=np.int64)
    draws = rng.integers(0, len(unique_cids), size=(n_boot, len(unique_cids)), dtype=np.int64)
    M_c = np.zeros((n_boot, len(unique_cids)), dtype=np.float64)
    row_grid = np.broadcast_to(np.arange(n_boot)[:, None], draws.shape)
    np.add.at(M_c, (row_grid, draws), 1.0)
    return M_c[:, row_cluster]


def weighted_boot_mean_r(W: np.ndarray, X: np.ndarray, Y: np.ndarray) -> Tuple[float, np.ndarray]:
    """Observed mean Pearson r and weighted bootstrap mean Pearson r (B,) across columns."""
    Y64 = np.asarray(Y, dtype=np.float64)
    X64 = np.asarray(X, dtype=np.float64)
    obs = float(np.nanmean(c.pearson(Y64, X64)))

    W_sum = W.sum(axis=1, keepdims=True)
    Yc = Y64 - Y64.mean(axis=0, keepdims=True)
    Xc = X64 - X64.mean(axis=0, keepdims=True)
    Sw_Y = W @ Yc
    Sw_Y2 = W @ (Yc * Yc)
    Sw_X = W @ Xc
    Sw_X2 = W @ (Xc * Xc)
    Sw_XY = W @ (Xc * Yc)

    cov = Sw_XY - (Sw_X * Sw_Y) / W_sum
    vx = Sw_X2 - (Sw_X * Sw_X) / W_sum
    vy = Sw_Y2 - (Sw_Y * Sw_Y) / W_sum
    den = np.sqrt(np.maximum(vx, 0.0) * np.maximum(vy, 0.0))
    valid = den > 1e-28
    r_mat = np.full_like(cov, np.nan)
    np.divide(cov, np.where(valid, den, 1.0), out=r_mat, where=valid)
    return obs, np.nanmean(r_mat, axis=1)


def basic_ci(obs: float, boot: np.ndarray, alpha: float = 0.05) -> Tuple[float, float]:
    v = boot[np.isfinite(boot)]
    if not np.isfinite(obs) or len(v) == 0:
        return float("nan"), float("nan")
    ql, qh = float(np.quantile(v, alpha / 2.0)), float(np.quantile(v, 1.0 - alpha / 2.0))
    return 2.0 * obs - qh, 2.0 * obs - ql


def hall_wilson_p(delta_obs: float, delta_boot: np.ndarray) -> float:
    v = delta_boot[np.isfinite(delta_boot)]
    if not np.isfinite(delta_obs) or len(v) == 0:
        return float("nan")
    exceed = int(np.sum(np.abs(v - delta_obs) >= np.abs(delta_obs)))
    return float((1 + exceed) / (len(v) + 1))


def holm_adjust(pvals: np.ndarray) -> np.ndarray:
    p = np.asarray(pvals, dtype=np.float64)
    out = np.full_like(p, np.nan)
    idx = np.flatnonzero(np.isfinite(p))
    m = len(idx)
    if m == 0:
        return out
    pv = p[idx]
    order = np.argsort(pv, kind="mergesort")
    adj = np.maximum.accumulate(np.minimum(1.0, pv[order] * (m - np.arange(m))))
    inv = np.empty_like(order)
    inv[order] = np.arange(m)
    out[idx] = adj[inv]
    return out


def n8_calibrate(x_val_hat: np.ndarray, x_val_true: np.ndarray, x_te_hat: np.ndarray) -> np.ndarray:
    """N8 / O35 mean-SD calibration fit strictly on validation fold."""
    mu_h = x_val_hat.mean(axis=0)
    sd_h = x_val_hat.std(axis=0, ddof=0)
    mu_t = x_val_true.mean(axis=0)
    sd_t = x_val_true.std(axis=0, ddof=0)
    med = float(np.median(sd_h))
    small = (sd_h < 0.01 * med) | (sd_h <= 0.0)
    scale = np.where(small, 1.0, sd_t / np.where(small, 1.0, sd_h))
    out = mu_t + scale * (x_te_hat - mu_h)
    if small.any():
        out[:, small] = x_te_hat[:, small] - mu_h[small] + mu_t[small]
    return out


def load_select_predict_head(pt_path: Path, n_v: int, n_c: int, n_out: int = 34):
    """Load saved S4 task_select_predict model.pt (includes vm, vs, cm, cs)."""
    saved = torch.load(pt_path, map_location="cpu", weights_only=True)
    r = int(saved["r"])
    model = FeatureModel(n_v, n_c, n_out, r)
    model.load_state_dict(saved["state_dict"])
    model.eval()
    coord = {k: saved[k].cpu().numpy().astype(np.float64) for k in ("vm", "vs", "cm", "cs")}
    return model, coord


def eval_head_prob(model: FeatureModel, coord: dict, v_raw: np.ndarray, c_raw: np.ndarray) -> np.ndarray:
    vz = (v_raw - coord["vm"]) / coord["vs"]
    cz = (c_raw - coord["cm"]) / coord["cs"]
    with torch.no_grad():
        vt = torch.as_tensor(vz.astype(np.float32))
        ct = torch.as_tensor(cz.astype(np.float32))
        prob = torch.sigmoid(model(vt, ct)).cpu().numpy().astype(np.float64)
    return prob


def decode_train_val_test(x_gpu: torch.Tensor, y_gpu: torch.Tensor, tr: np.ndarray, va: np.ndarray, te: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Fit s5_common dual ridge on tr, select lambda on va, return both va_hat (from tr->va) and te_hat (from dk->te)."""
    va_paths = d5.ridge_fit(x_gpu, y_gpu, tr, va, d5.LAMBDAS)
    scores = torch.stack([d5.r_selection(y_gpu[va], p) for p in va_paths])
    pick = d5.pick_per_target(scores)
    va_hat = va_paths.gather(0, pick[None, None, :].expand(1, len(va), y_gpu.shape[1]))[0]
    dk = np.concatenate([tr, va])
    te_paths = d5.ridge_fit(x_gpu, y_gpu, dk, te, d5.LAMBDAS)
    te_hat = te_paths.gather(0, pick[None, None, :].expand(1, len(te), y_gpu.shape[1]))[0]
    return va_hat.cpu().numpy().astype(np.float64), te_hat.cpu().numpy().astype(np.float64)


def run_analysis_1_noncircularity(
    brains: Dict[str, d5.BrainSet],
    split: pd.DataFrame,
    y_em: np.ndarray,
    present_masks: Dict[str, np.ndarray],
    W_all: np.ndarray,
    device: str,
) -> pd.DataFrame:
    """1. K1 with emotion-word-stripped DeBERTa (`noemo`) and CLIP visual features."""
    vid_to_row = {int(v): i for i, v in enumerate(split["video_id"].tolist())}
    ids_dev = split["video_id"].to_numpy()
    v_vjepa = c.load_rows(c.VISUAL_TARGET, ids_dev, split).astype(np.float64)
    c_deb = c.load_rows(c.CAPTION_TARGET, ids_dev, split).astype(np.float64)
    c_noemo = c.load_rows(c.CAPTION_NO_EMOTION, ids_dev, split).astype(np.float64)
    v_clip = c.load_rows(c.BASELINE_FEATURES["clip"][1], ids_dev, split).astype(np.float64)

    variants = [
        "s5_ridge_direct",
        "k1_canonical_uncal",
        "k1_canonical_cal",
        "k1_noemo_uncal",
        "k1_noemo_cal",
        "k1_clip_uncal",
        "k1_clip_cal",
    ]
    preds = {
        var: {sub: np.full((len(split), 34), np.nan, dtype=np.float64) for sub in PARTICIPANTS}
        for var in variants
    }

    # Preload S4 fold heads
    s4_stim_heads = {}
    s4_noemo_heads = {}
    s4_clip_heads = {}
    for k in range(1, c.N_FOLDS + 1):
        st_coord_npz = np.load(c.OUT / f"stimulus/fold{k}/coordinates.npz")
        st_coord = {key: st_coord_npz[key].astype(np.float64) for key in ("vm", "vs", "cm", "cs")}
        st_saved = torch.load(c.OUT / f"stimulus/fold{k}/head_additive.pt", map_location="cpu", weights_only=True)
        st_m = FeatureModel(5632, 4096, 34, int(st_saved["r"]))
        st_m.load_state_dict(st_saved["state_dict"])
        st_m.eval()
        s4_stim_heads[k] = (st_m, st_coord)
        s4_noemo_heads[k] = load_select_predict_head(c.OUT / f"noemo/fold{k}/model.pt", 5632, 4096, 34)
        s4_clip_heads[k] = load_select_predict_head(c.OUT / f"baseline/clip_fold{k}/model.pt", 512, 4096, 34)

    for s_tag in d5.HK:
        sub = f"sub-{s_tag}"
        brain = brains[sub]
        b_rows_in_dev = np.array([vid_to_row[int(v)] for v in brain.video_id.tolist()], dtype=np.int64)
        x_gpu = d5.as_tensor(brain.X, device)

        # Pack all feature targets needed in a single tensor per participant for fast kernel reuse!
        # [5632 vjepa | 4096 deberta | 4096 noemo | 512 clip] = 14,336 dims
        y_feat_all = np.concatenate(
            [v_vjepa[b_rows_in_dev], c_deb[b_rows_in_dev], c_noemo[b_rows_in_dev], v_clip[b_rows_in_dev]],
            axis=1,
        )
        yf_gpu = d5.as_tensor(y_feat_all, device)

        for k in range(1, c.N_FOLDS + 1):
            roles = c.roles(k)
            tr = np.flatnonzero(np.isin(brain.fold, roles["train"]))
            va = np.flatnonzero(brain.fold == roles["val"])
            te = np.flatnonzero(brain.fold == k)
            dest = b_rows_in_dev[te]
            va_dev = b_rows_in_dev[va]

            # Direct S5 ridge emotion_main
            zr = np.load(d5.OUT / f"ridge/sub-{s_tag}_fold{k}/pred.npz")
            zr_dest = np.array([vid_to_row[int(v)] for v in zr["video_id"].tolist()], dtype=np.int64)
            preds["s5_ridge_direct"][sub][zr_dest] = zr["emotion_main"].astype(np.float64)

            va_hat, te_hat = decode_train_val_test(x_gpu, yf_gpu, tr, va, te)
            vj_va, vj_te = va_hat[:, :5632], te_hat[:, :5632]
            db_va, db_te = va_hat[:, 5632:9728], te_hat[:, 5632:9728]
            ne_va, ne_te = va_hat[:, 9728:13824], te_hat[:, 9728:13824]
            cl_va, cl_te = va_hat[:, 13824:], te_hat[:, 13824:]

            vj_te_cal = n8_calibrate(vj_va, v_vjepa[va_dev], vj_te)
            db_te_cal = n8_calibrate(db_va, c_deb[va_dev], db_te)
            ne_te_cal = n8_calibrate(ne_va, c_noemo[va_dev], ne_te)
            cl_te_cal = n8_calibrate(cl_va, v_clip[va_dev], cl_te)

            m_st, cd_st = s4_stim_heads[k]
            m_ne, cd_ne = s4_noemo_heads[k]
            m_cl, cd_cl = s4_clip_heads[k]

            preds["k1_canonical_uncal"][sub][dest] = eval_head_prob(m_st, cd_st, vj_te, db_te)
            preds["k1_canonical_cal"][sub][dest] = eval_head_prob(m_st, cd_st, vj_te_cal, db_te_cal)
            preds["k1_noemo_uncal"][sub][dest] = eval_head_prob(m_ne, cd_ne, vj_te, ne_te)
            preds["k1_noemo_cal"][sub][dest] = eval_head_prob(m_ne, cd_ne, vj_te_cal, ne_te_cal)
            preds["k1_clip_uncal"][sub][dest] = eval_head_prob(m_cl, cd_cl, cl_te, db_te)
            preds["k1_clip_cal"][sub][dest] = eval_head_prob(m_cl, cd_cl, cl_te_cal, db_te_cal)

    # Summarize with 10k bootstrap CIs and comparisons vs s5_ridge_direct and k1_canonical
    obs_m = {}
    boot_m = {}
    for var in variants:
        obs_s, boot_s = [], []
        for sub in PARTICIPANTS:
            pm = present_masks[sub]
            o, b = weighted_boot_mean_r(W_all[:, pm], preds[var][sub][pm], y_em[pm])
            obs_s.append(o)
            boot_s.append(b)
        obs_m[var] = np.array(obs_s)
        boot_m[var] = np.stack(boot_s, axis=0)  # (5, B)

    rows = []
    for var in variants:
        m5_obs = float(obs_m[var].mean())
        m5_boot = boot_m[var].mean(axis=0)
        cil, cih = basic_ci(m5_obs, m5_boot)
        d_ridge_obs = m5_obs - float(obs_m["s5_ridge_direct"].mean())
        d_ridge_boot = m5_boot - boot_m["s5_ridge_direct"].mean(axis=0)
        dr_l, dr_h = basic_ci(d_ridge_obs, d_ridge_boot)
        dr_p = hall_wilson_p(d_ridge_obs, d_ridge_boot)
        row = {
            "variant": var,
            "mean_5sub_r": m5_obs,
            "ci95_low": cil,
            "ci95_high": cih,
            "diff_vs_s5_ridge_direct": d_ridge_obs,
            "diff_vs_ridge_ci95_low": dr_l,
            "diff_vs_ridge_ci95_high": dr_h,
            "p_vs_s5_ridge_direct": dr_p,
            "n_sub_gt_ridge_of_5": int(np.sum(obs_m[var] > obs_m["s5_ridge_direct"])),
        }
        for i, sub in enumerate(PARTICIPANTS):
            row[f"{sub}_r"] = float(obs_m[var][i])
        rows.append(row)
    return pd.DataFrame(rows)


def run_analysis_2_k1_zone(
    brains: Dict[str, d5.BrainSet],
    split: pd.DataFrame,
    y_em: np.ndarray,
    device: str,
) -> pd.DataFrame:
    """2. Out-of-zone generalization (`5 blocks x 6 folds x {excluded, control}`) for K1_zone vs S5 Ridge zone."""
    vid_to_row = {int(v): i for i, v in enumerate(split["video_id"].tolist())}
    ids_dev = split["video_id"].to_numpy()
    fold_of = dict(zip(split["video_id"].tolist(), split["fold"].tolist()))
    v_vjepa = c.load_rows(c.VISUAL_TARGET, ids_dev, split).astype(np.float64)
    c_deb = c.load_rows(c.CAPTION_TARGET, ids_dev, split).astype(np.float64)
    blocks_df = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t")
    control_df = pd.read_csv(c.S2 / "content_block_control_samples.tsv", sep="\t")

    # Preload 60 S4 zone heads
    zone_heads = {}
    for b in range(1, 6):
        for k in range(1, c.N_FOLDS + 1):
            for kind in ("excluded", "control"):
                zone_heads[(b, k, kind)] = load_select_predict_head(
                    c.OUT / f"zone/block{b}_fold{k}_{kind}/model.pt", 5632, 4096, 34
                )

    rows = []
    for s_tag in d5.HK:
        sub = f"sub-{s_tag}"
        brain = brains[sub]
        b_rows_in_dev = np.array([vid_to_row[int(v)] for v in brain.video_id.tolist()], dtype=np.int64)
        x_gpu = d5.as_tensor(brain.X, device)
        yf_gpu = d5.as_tensor(np.concatenate([v_vjepa[b_rows_in_dev], c_deb[b_rows_in_dev]], axis=1), device)

        for b in range(1, 6):
            # Pool across 6 outer folds inside content block b (matching S10 Table 6 zone evaluation)
            pooled = {
                m_key: {kind: [] for kind in ("excluded", "control")}
                for m_key in ("s5_ridge_zone", "k1_zone_uncal", "k1_zone_cal")
            }
            y_true_pooled = {"excluded": [], "control": []}

            for k in range(1, c.N_FOLDS + 1):
                roles = c.roles(k)
                for kind in ("excluded", "control"):
                    train_ids, test_ids = c.zone_sets(split, b, k, kind, blocks_df, control_df)
                    tr_ids = [v for v in train_ids if fold_of[v] in roles["train"]]
                    va_ids = [v for v in train_ids if fold_of[v] == roles["val"]]
                    tr = brain.rows(tr_ids)
                    va = brain.rows(va_ids)
                    te = brain.rows(test_ids)
                    if len(te) == 0:
                        continue

                    va_hat, te_hat = decode_train_val_test(x_gpu, yf_gpu, tr, va, te)
                    vj_va, vj_te = va_hat[:, :5632], te_hat[:, :5632]
                    db_va, db_te = va_hat[:, 5632:], te_hat[:, 5632:]
                    va_dev = b_rows_in_dev[va]
                    te_dev = b_rows_in_dev[te]
                    vj_cal = n8_calibrate(vj_va, v_vjepa[va_dev], vj_te)
                    db_cal = n8_calibrate(db_va, c_deb[va_dev], db_te)

                    m_z, cd_z = zone_heads[(b, k, kind)]
                    p_uncal = eval_head_prob(m_z, cd_z, vj_te, db_te)
                    p_cal = eval_head_prob(m_z, cd_z, vj_cal, db_cal)

                    zz = np.load(d5.OUT / f"zone/sub-{s_tag}_block{b}_fold{k}_{kind}/pred.npz")
                    # Align S5 ridge zone pred to brain.video_id[te]
                    zz_pos = {int(v): idx for idx, v in enumerate(zz["video_id"].tolist())}
                    p_ridge = np.stack([zz["pred"][zz_pos[int(v)]] for v in brain.video_id[te].tolist()], axis=0)

                    pooled["s5_ridge_zone"][kind].append(p_ridge)
                    pooled["k1_zone_uncal"][kind].append(p_uncal)
                    pooled["k1_zone_cal"][kind].append(p_cal)
                    y_true_pooled[kind].append(y_em[te_dev])

            y_exc = np.concatenate(y_true_pooled["excluded"], axis=0)
            y_ctl = np.concatenate(y_true_pooled["control"], axis=0)
            for m_key in ("s5_ridge_zone", "k1_zone_uncal", "k1_zone_cal"):
                r_exc = float(np.nanmean(c.pearson(y_exc, np.concatenate(pooled[m_key]["excluded"], axis=0))))
                r_ctl = float(np.nanmean(c.pearson(y_ctl, np.concatenate(pooled[m_key]["control"], axis=0))))
                rows.append({
                    "model": m_key,
                    "participant": sub,
                    "block": b,
                    "r_excluded": r_exc,
                    "r_control": r_ctl,
                    "diff_excluded_minus_control": r_exc - r_ctl,
                })

    df_sub_blocks = pd.DataFrame(rows)
    # Add 5-block mean per participant and 5-participant summary with t_4 test
    summary_rows = []
    for m_key, grp in df_sub_blocks.groupby("model", sort=False):
        by_sub = grp.groupby("participant", as_index=False).agg(
            r_excluded=("r_excluded", "mean"),
            r_control=("r_control", "mean"),
            diff_excluded_minus_control=("diff_excluded_minus_control", "mean"),
        )
        for _, sr in by_sub.iterrows():
            summary_rows.append({
                "model": m_key,
                "participant": sr["participant"],
                "block": "five_block_mean",
                "r_excluded": float(sr["r_excluded"]),
                "r_control": float(sr["r_control"]),
                "diff_excluded_minus_control": float(sr["diff_excluded_minus_control"]),
                "t4_stat": np.nan,
                "p_t4_two_sided": np.nan,
            })
        diffs = by_sub["diff_excluded_minus_control"].to_numpy(dtype=np.float64)
        t_res = stats.ttest_1samp(diffs, 0.0)
        summary_rows.append({
            "model": m_key,
            "participant": "mean_5sub",
            "block": "five_block_mean",
            "r_excluded": float(by_sub["r_excluded"].mean()),
            "r_control": float(by_sub["r_control"].mean()),
            "diff_excluded_minus_control": float(diffs.mean()),
            "t4_stat": float(t_res.statistic),
            "p_t4_two_sided": float(t_res.pvalue),
        })
    return pd.concat([df_sub_blocks, pd.DataFrame(summary_rows)], ignore_index=True)


def run_analysis_3_cabnp13_lono(
    brains: Dict[str, d5.BrainSet],
    split: pd.DataFrame,
    y_em: np.ndarray,
    y_dim: np.ndarray,
    present_masks: Dict[str, np.ndarray],
    W_all: np.ndarray,
    device: str,
) -> pd.DataFrame:
    """3. Confound-free 13-network whole-brain Ridge Leave-One-Network-Out (LONO) & Single-Network-Only (SNO)."""
    vid_to_row = {int(v): i for i, v in enumerate(split["video_id"].tolist())}
    roi_df = pd.read_csv(P.MANIFESTS / "s2/roi_table.tsv", sep="\t")
    cab_df = pd.read_csv(P.MANIFESTS / "s2/cabnp_groups.tsv", sep="\t")
    groups = cab_df["group"].tolist()
    group_ko_map = dict(zip(cab_df["group"].tolist(), cab_df["group_ko"].tolist()))
    roi_indices_by_group = {
        g: roi_df.loc[roi_df["group"] == g, "roi_index"].to_numpy(dtype=np.int64).tolist()
        for g in groups
    }

    # Store predictions: mode -> group -> sub -> (2109, 48) [34 emotions + 14 dimensions]
    full_preds = {sub: np.full((len(split), 48), np.nan, dtype=np.float64) for sub in PARTICIPANTS}
    lono_preds = {
        g: {sub: np.full((len(split), 48), np.nan, dtype=np.float64) for sub in PARTICIPANTS}
        for g in groups
    }
    sno_preds = {
        g: {sub: np.full((len(split), 48), np.nan, dtype=np.float64) for sub in PARTICIPANTS}
        for g in groups
    }
    group_vox_counts: Dict[str, Dict[str, int]] = {g: {} for g in groups}

    for s_tag in d5.HK:
        sub = f"sub-{s_tag}"
        brain = brains[sub]
        n_vox_total = brain.X.shape[1]
        b_rows_in_dev = np.array([vid_to_row[int(v)] for v in brain.video_id.tolist()], dtype=np.int64)
        y_all48 = np.concatenate([y_em[b_rows_in_dev], y_dim[b_rows_in_dev]], axis=1)
        y_gpu = d5.as_tensor(y_all48, device)
        x_full_gpu = d5.as_tensor(brain.X, device)

        for k in range(1, c.N_FOLDS + 1):
            roles = c.roles(k)
            tr = np.flatnonzero(np.isin(brain.fold, roles["train"]))
            va = np.flatnonzero(brain.fold == roles["val"])
            te = np.flatnonzero(brain.fold == k)
            dest = b_rows_in_dev[te]
            p_full, _ = d5.main_version(x_full_gpu, y_gpu, tr, va, te)
            full_preds[sub][dest] = p_full.cpu().numpy().astype(np.float64)

        for g in groups:
            g_pos = np.unique(np.concatenate([brain.roi_positions[r_i] for r_i in roi_indices_by_group[g]]))
            group_vox_counts[g][sub] = int(len(g_pos))
            keep_mask = np.ones(n_vox_total, dtype=bool)
            keep_mask[g_pos] = False
            x_lono_gpu = d5.as_tensor(brain.X[:, keep_mask], device)
            x_sno_gpu = d5.as_tensor(brain.X[:, g_pos], device)

            for k in range(1, c.N_FOLDS + 1):
                roles = c.roles(k)
                tr = np.flatnonzero(np.isin(brain.fold, roles["train"]))
                va = np.flatnonzero(brain.fold == roles["val"])
                te = np.flatnonzero(brain.fold == k)
                dest = b_rows_in_dev[te]
                p_lono, _ = d5.main_version(x_lono_gpu, y_gpu, tr, va, te)
                p_sno, _ = d5.main_version(x_sno_gpu, y_gpu, tr, va, te)
                lono_preds[g][sub][dest] = p_lono.cpu().numpy().astype(np.float64)
                sno_preds[g][sub][dest] = p_sno.cpu().numpy().astype(np.float64)

    # Compute bootstrap stats for 34 emotions and 14 dimensions
    full_em_obs, full_em_boot = {}, {}
    full_dm_obs, full_dm_boot = {}, {}
    for sub in PARTICIPANTS:
        pm = present_masks[sub]
        full_em_obs[sub], full_em_boot[sub] = weighted_boot_mean_r(W_all[:, pm], full_preds[sub][pm, :34], y_em[pm])
        full_dm_obs[sub], full_dm_boot[sub] = weighted_boot_mean_r(W_all[:, pm], full_preds[sub][pm, 34:], y_dim[pm])

    rows = []
    for g in groups:
        g_kind = "anatomical_subcortical_group" if g == "Subcortex" else "cortical_network"
        n_roi = len(roi_indices_by_group[g])
        mean_vox = float(np.mean([group_vox_counts[g][s] for s in PARTICIPANTS]))

        em_drop_subs, em_drop_boots = [], []
        em_sno_subs, em_sno_boots = [], []
        dm_drop_subs, dm_drop_boots = [], []
        dm_sno_subs = []

        for sub in PARTICIPANTS:
            pm = present_masks[sub]
            o_lono_em, b_lono_em = weighted_boot_mean_r(W_all[:, pm], lono_preds[g][sub][pm, :34], y_em[pm])
            o_sno_em, b_sno_em = weighted_boot_mean_r(W_all[:, pm], sno_preds[g][sub][pm, :34], y_em[pm])
            o_lono_dm, b_lono_dm = weighted_boot_mean_r(W_all[:, pm], lono_preds[g][sub][pm, 34:], y_dim[pm])
            o_sno_dm, _ = weighted_boot_mean_r(W_all[:, pm], sno_preds[g][sub][pm, 34:], y_dim[pm])

            em_drop_subs.append(full_em_obs[sub] - o_lono_em)
            em_drop_boots.append(full_em_boot[sub] - b_lono_em)
            em_sno_subs.append(o_sno_em)
            em_sno_boots.append(b_sno_em)
            dm_drop_subs.append(full_dm_obs[sub] - o_lono_dm)
            dm_drop_boots.append(full_dm_boot[sub] - b_lono_dm)
            dm_sno_subs.append(o_sno_dm)

        em_drop_arr = np.array(em_drop_subs)
        em_drop_m5 = float(em_drop_arr.mean())
        em_drop_b5 = np.mean(np.stack(em_drop_boots, axis=0), axis=0)
        cil_d, cih_d = basic_ci(em_drop_m5, em_drop_b5)
        p_boot_d = hall_wilson_p(em_drop_m5, em_drop_b5)
        t4_d = stats.ttest_1samp(em_drop_arr, 0.0)

        em_sno_arr = np.array(em_sno_subs)
        em_sno_m5 = float(em_sno_arr.mean())
        em_sno_b5 = np.mean(np.stack(em_sno_boots, axis=0), axis=0)
        cil_s, cih_s = basic_ci(em_sno_m5, em_sno_b5)

        dm_drop_m5 = float(np.mean(dm_drop_subs))
        dm_drop_b5 = np.mean(np.stack(dm_drop_boots, axis=0), axis=0)
        p_boot_dm = hall_wilson_p(dm_drop_m5, dm_drop_b5)

        row = {
            "group": g,
            "group_ko": group_ko_map[g],
            "group_kind": g_kind,
            "n_roi": n_roi,
            "mean_unique_voxels_5sub": mean_vox,
            "lono_drop_em34_mean5sub": em_drop_m5,
            "lono_drop_em34_per_1k_vox": em_drop_m5 / (mean_vox / 1000.0) if mean_vox > 0 else np.nan,
            "lono_drop_em34_ci95_low": cil_d,
            "lono_drop_em34_ci95_high": cih_d,
            "lono_drop_em34_p_boot": p_boot_d,
            "lono_drop_em34_t4": float(t4_d.statistic),
            "lono_drop_em34_p_t4": float(t4_d.pvalue),
            "sno_only_em34_mean5sub": em_sno_m5,
            "sno_only_em34_ci95_low": cil_s,
            "sno_only_em34_ci95_high": cih_s,
            "lono_drop_dim14_mean5sub": dm_drop_m5,
            "lono_drop_dim14_p_boot": p_boot_dm,
            "sno_only_dim14_mean5sub": float(np.mean(dm_sno_subs)),
        }
        for i, sub in enumerate(PARTICIPANTS):
            row[f"{sub}_lono_drop_em34"] = float(em_drop_arr[i])
            row[f"{sub}_sno_only_em34"] = float(em_sno_arr[i])
            row[f"{sub}_voxels"] = group_vox_counts[g][sub]
        rows.append(row)

    df = pd.DataFrame(rows)
    df["lono_drop_em34_p_holm13"] = holm_adjust(df["lono_drop_em34_p_boot"].to_numpy())
    df["lono_drop_dim14_p_holm13"] = holm_adjust(df["lono_drop_dim14_p_boot"].to_numpy())
    return df.sort_values("lono_drop_em34_mean5sub", ascending=False).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--out-dir", type=Path, default=P.OUT / "s9_analysis/step1_linear_enrichments")
    args = ap.parse_args()

    if args.device.startswith("cuda") and not os.environ.get("SLURM_JOB_ID"):
        raise SystemExit("ERROR: GPU execution on b300-01 MUST run inside Slurm (sbatch/srun).")

    t0 = time.time()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    split = c.load_split()
    y_em, _ = c.load_scores(split, "emotions")
    y_dim, _ = c.load_scores(split, "dimensions")
    y_em = y_em.astype(np.float64)
    y_dim = y_dim.astype(np.float64)

    pb = pd.read_csv(d5.BLOCKS, sep="\t")
    present_masks = {
        sub: split["video_id"].isin(pb.loc[pb["participant"] == sub, "video_id"]).to_numpy(dtype=bool)
        for sub in PARTICIPANTS
    }
    W_all = build_boot_weights(split, N_BOOT)

    print(f"[Step1-Enrich] Loading whole-brain BrainSet for 5 HK participants (device={args.device})...", flush=True)
    brains = {f"sub-{s_tag}": d5.load_brain(s_tag, split) for s_tag in d5.HK}

    print("[Step1-Enrich] 1/3 Running K1 non-circularity (noemo) & CLIP mediation check...", flush=True)
    df_a1 = run_analysis_1_noncircularity(brains, split, y_em, present_masks, W_all, args.device)
    df_a1.to_csv(out_dir / "step1_k1_noncircularity_and_clip.tsv", sep="\t", index=False, float_format="%.6f")

    print("[Step1-Enrich] 2/3 Running K1_zone out-of-zone generalization (60 splits x 5 subjects)...", flush=True)
    df_a2 = run_analysis_2_k1_zone(brains, split, y_em, args.device)
    df_a2.to_csv(out_dir / "step1_k1_zone_generalization.tsv", sep="\t", index=False, float_format="%.6f")

    print("[Step1-Enrich] 3/3 Running CAB-NP 13-network LONO & SNO whole-brain ridge...", flush=True)
    df_a3 = run_analysis_3_cabnp13_lono(brains, split, y_em, y_dim, present_masks, W_all, args.device)
    df_a3.to_csv(out_dir / "step1_cabnp13_lono_ridge.tsv", sep="\t", index=False, float_format="%.6f")

    prov = {
        "script": str(Path(__file__).resolve()),
        "script_sha256": c.sha256(Path(__file__).resolve()),
        "code_head": c.START_HEAD,
        "device": args.device,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "runtime_seconds": round(time.time() - t0, 2),
        "roi_voxels_sha256": {f"hk_sub-{s}.npz": c.sha256(d5.roi_path(s)) for s in d5.HK},
        "participant_unique_voxels": {sub: int(brains[sub].X.shape[1]) for sub in PARTICIPANTS},
        "outputs": [
            "step1_k1_noncircularity_and_clip.tsv",
            "step1_k1_zone_generalization.tsv",
            "step1_cabnp13_lono_ridge.tsv",
        ],
    }
    (out_dir / "provenance.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False))
    print(f"[Step1-Enrich] Completed in {prov['runtime_seconds']}s -> {out_dir}", flush=True)


if __name__ == "__main__":
    main()
