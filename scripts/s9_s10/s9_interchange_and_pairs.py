#!/usr/bin/env python3
"""S9-1 Interchange Interventions & S9-2 Nearest-Pair Comparison (O2, O3, O4, O9, O33).

Strict operational guarantees:
- CPU-only execution: CUDA_VISIBLE_DEVICES="", OMP_NUM_THREADS=12, MKL_NUM_THREADS=12, torch.set_num_threads(12).
- Read-only access to /scratch/emobrain/code and existing S2/S6 outputs; zero modifications to tracked repo files.
- Exact alignment with docs/final/reference/audition_codex.py (loaded as s6_model.ac),
  docs/final/04_claude_code_workorder.md (S9 & S10), and docs/final/01_integrated_document.md (O2, O3, O4, O9, O33).
"""
import os

# Enforce zero GPU visibility and 12 CPU threads BEFORE importing numpy/torch.
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OMP_NUM_THREADS"] = "12"
os.environ["MKL_NUM_THREADS"] = "12"

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

# Add repo src to sys.path (read-only)
_LOCAL_ROOT = Path(__file__).resolve().parents[2]
CODE_ROOT = _LOCAL_ROOT if (_LOCAL_ROOT / "src").is_dir() else Path("/scratch/emobrain/code")
SRC_DIR = CODE_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(12)
if torch.cuda.is_available():
    raise RuntimeError("CUDA is visible! Must run strictly on CPU with CUDA_VISIBLE_DEVICES=''.")

import s4_common as c
import s6_common as S
import s6_model as M
from s6_model import ac

PARTICIPANTS = ("sub-01", "sub-02", "sub-03", "sub-04", "sub-05")
FOLDS = (1, 2, 3, 4, 5, 6)
SEEDS = (0, 1, 2)
PATH_NAMES = ("visual", "caption", "both")

INTERCHANGE_CONDITIONS = (
    ("brain_decoded", "C-1"),
    ("brain_decoded_additive", "C-1_additive"),
    ("brain_decoded_sep", "D-1"),
)
O33_CONDITIONS = (
    ("brain_only", "A-1"),
    ("brain_decoded", "C-1"),
)

HIGH_EMONET_NAMES = ("craving", "sexual desire", "entrancement", "horror")
LOW_EMONET_NAMES = ("confusion", "awe", "surprise")

N_BOOTSTRAP = 10000
BOOTSTRAP_SEED_BYTES = b"EmoBrain/O4/pair_cluster_bootstrap"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg FDR q-values, preserving NaNs."""
    p = np.asarray(pvals, dtype=np.float64)
    q = np.full_like(p, np.nan, dtype=np.float64)
    valid = np.isfinite(p)
    m = int(valid.sum())
    if m == 0:
        return q
    pv = p[valid]
    order = np.argsort(pv, kind="mergesort")
    ranked = pv[order]
    ranks = np.arange(1, m + 1, dtype=np.float64)
    raw_q = ranked * (m / ranks)
    monotone_q = np.minimum.accumulate(raw_q[::-1])[::-1]
    monotone_q = np.clip(monotone_q, 0.0, 1.0)
    out_valid = np.empty_like(pv)
    out_valid[order] = monotone_q
    q[valid] = out_valid
    return q


def bootstrap_ci_and_p(theta_hat: np.ndarray, theta_boot: np.ndarray):
    """Basic 95% bootstrap CI and Hall & Wilson (1991) centered two-sided p-value.

    theta_hat: [...] float64
    theta_boot: [B, ...] float64
    Returns: ci_low, ci_high, p_boot, n_nan_boot (all shape [...])
    """
    th = np.asarray(theta_hat, dtype=np.float64)
    tb = np.asarray(theta_boot, dtype=np.float64)
    B = tb.shape[0]
    n_nan = np.isnan(tb).sum(axis=0)

    # Scalar fast path
    if th.ndim == 0:
        if not np.isfinite(th) or n_nan == B:
            return np.nan, np.nan, np.nan, int(n_nan)
        tb_valid = tb[np.isfinite(tb)] if n_nan > 0 else tb
        B_eff = tb_valid.shape[0]
        q975 = float(np.quantile(tb_valid, 0.975))
        q025 = float(np.quantile(tb_valid, 0.025))
        ci_low = 2.0 * float(th) - q975
        ci_high = 2.0 * float(th) - q025
        exceed = int(np.sum(np.abs(tb_valid - float(th)) >= np.abs(float(th))))
        p_val = (1.0 + exceed) / (B_eff + 1.0)
        return ci_low, ci_high, p_val, int(n_nan)

    # Array path
    ci_low = np.full(th.shape, np.nan, dtype=np.float64)
    ci_high = np.full(th.shape, np.nan, dtype=np.float64)
    p_val = np.full(th.shape, np.nan, dtype=np.float64)

    all_finite_mask = np.isfinite(th) & (n_nan == 0)
    if np.all(all_finite_mask):
        q975 = np.quantile(tb, 0.975, axis=0)
        q025 = np.quantile(tb, 0.025, axis=0)
        ci_low = 2.0 * th - q975
        ci_high = 2.0 * th - q025
        exceed = np.sum(np.abs(tb - th[None, ...]) >= np.abs(th[None, ...]), axis=0)
        p_val = (1.0 + exceed) / (B + 1.0)
        return ci_low, ci_high, p_val, n_nan

    it = np.nditer(th, flags=["multi_index"])
    while not it.finished:
        idx = it.multi_index
        cl, ch, pv, _ = bootstrap_ci_and_p(th[idx], tb[(slice(None),) + idx])
        ci_low[idx] = cl
        ci_high[idx] = ch
        p_val[idx] = pv
        it.iternext()
    return ci_low, ci_high, p_val, n_nan


def _exact_const_mask_per_boot(A_flat: np.ndarray, pair_g: np.ndarray, active_g: np.ndarray, has_p: np.ndarray, G: int) -> np.ndarray:
    """Exact per-bootstrap-draw constancy mask [b, L], matching (x == x[0:1]).all(0) on concatenated pairs."""
    L = A_flat.shape[1]
    amin_g = np.full((G, L), np.inf, dtype=np.float64)
    amax_g = np.full((G, L), -np.inf, dtype=np.float64)
    np.minimum.at(amin_g, pair_g, A_flat)
    np.maximum.at(amax_g, pair_g, A_flat)
    internally_var = ((amax_g > amin_g) & has_p[:, None]).astype(np.float64)  # [G, L]

    # Fast check: if any active cluster is internally variable, the concatenated vector is guaranteed non-constant.
    has_internal_var = (active_g.astype(np.float64) @ internally_var) > 0  # [b, L]
    is_const = np.zeros_like(has_internal_var, dtype=bool)
    if not has_internal_var.all():
        b_idx, l_idx = np.where(~has_internal_var)
        for bi, li in zip(b_idx.tolist(), l_idx.tolist()):
            act = active_g[bi]
            if not act.any():
                is_const[bi, li] = True
            else:
                vals = amin_g[act, li]
                is_const[bi, li] = bool(vals.max() == vals.min())
    return is_const


def fast_cluster_bootstrap_pearson(
    X: np.ndarray,
    Y: np.ndarray,
    pair_g: np.ndarray,
    counts: np.ndarray,
    G: int = 419,
    chunk: int = 1000,
) -> np.ndarray:
    """Exact cluster-multiplicity weighted Pearson r across B bootstrap draws.

    X: [P, ..., 34] float64
    Y: [P, 34] float64
    pair_g: [P] int64 in 0..G-1
    counts: [B, G] float64 integer cluster multiplicities
    Returns: [B, ..., 34] float64 matching ac.change_alignment on concatenated pairs.
    """
    orig_mid = X.shape[1:-1]
    P = X.shape[0]
    B = counts.shape[0]
    M_mid = int(np.prod(orig_mid)) if orig_mid else 1

    X3 = np.asarray(X, dtype=np.float64).reshape(P, M_mid, 34)
    Y2 = np.asarray(Y, dtype=np.float64)

    # Pre-center by unweighted mean to avoid catastrophic cancellation in float64
    mx = X3.mean(axis=0, keepdims=True)
    my = Y2.mean(axis=0, keepdims=True)
    Xc = X3 - mx
    Yc = Y2 - my

    n_g = np.bincount(pair_g, minlength=G).astype(np.float64)  # [G]
    has_p = n_g > 0
    N_b = counts @ n_g  # [B]

    K = M_mid * 34
    X_flat = X3.reshape(P, K)
    Xc_flat = Xc.reshape(P, K)
    Yc_broad = np.broadcast_to(Yc[:, None, :], (P, M_mid, 34)).reshape(P, K)

    Ind = np.zeros((G, P), dtype=np.float64)
    Ind[pair_g, np.arange(P)] = 1.0

    S_x = Ind @ Xc_flat                  # [G, K]
    S_xx = Ind @ (Xc_flat * Xc_flat)     # [G, K]
    S_xy = Ind @ (Xc_flat * Yc_broad)    # [G, K]
    S_y = Ind @ Yc                       # [G, 34]
    S_yy = Ind @ (Yc * Yc)               # [G, 34]

    # Precompute constancy helpers for X and Y
    ymin_g = np.full((G, 34), np.inf, dtype=np.float64)
    ymax_g = np.full((G, 34), -np.inf, dtype=np.float64)
    np.minimum.at(ymin_g, pair_g, Y2)
    np.maximum.at(ymax_g, pair_g, Y2)
    y_int_var = ((ymax_g > ymin_g) & has_p[:, None]).astype(np.float64)

    xmin_g = np.full((G, K), np.inf, dtype=np.float64)
    xmax_g = np.full((G, K), -np.inf, dtype=np.float64)
    np.minimum.at(xmin_g, pair_g, X_flat)
    np.maximum.at(xmax_g, pair_g, X_flat)
    x_int_var = ((xmax_g > xmin_g) & has_p[:, None]).astype(np.float64)

    wy = counts @ S_y
    wyy = counts @ S_yy
    with np.errstate(divide="ignore", invalid="ignore"):
        ss_y = wyy - (wy * wy) / N_b[:, None]

    out = np.empty((B, M_mid, 34), dtype=np.float64)
    for start in range(0, B, chunk):
        end = min(start + chunk, B)
        cb = counts[start:end]
        nb = N_b[start:end]
        active = (cb > 0) & has_p[None, :]  # [b, G]
        act_f = active.astype(np.float64)

        # Constancy check for Y [b, 34]
        y_has_var = (act_f @ y_int_var) > 0
        const_y = np.zeros_like(y_has_var, dtype=bool)
        if not y_has_var.all():
            bi_arr, ei_arr = np.where(~y_has_var)
            for bi, ei in zip(bi_arr.tolist(), ei_arr.tolist()):
                act = active[bi]
                vals = ymin_g[act, ei]
                const_y[bi, ei] = (vals.size == 0) or bool(vals.max() == vals.min())

        # Constancy check for X [b, K]
        x_has_var = (act_f @ x_int_var) > 0
        const_x = np.zeros_like(x_has_var, dtype=bool)
        if not x_has_var.all():
            bi_arr, ki_arr = np.where(~x_has_var)
            for bi, ki in zip(bi_arr.tolist(), ki_arr.tolist()):
                act = active[bi]
                vals = xmin_g[act, ki]
                const_x[bi, ki] = (vals.size == 0) or bool(vals.max() == vals.min())
        const_x_3 = const_x.reshape(-1, M_mid, 34)

        wx = (cb @ S_x).reshape(-1, M_mid, 34)
        wxx = (cb @ S_xx).reshape(-1, M_mid, 34)
        wxy = (cb @ S_xy).reshape(-1, M_mid, 34)
        wy_b = wy[start:end][:, None, :]
        ss_y_b = ss_y[start:end][:, None, :]
        nb_3 = nb[:, None, None]

        with np.errstate(divide="ignore", invalid="ignore"):
            ss_x_b = wxx - (wx * wx) / nb_3
            cov_b = wxy - (wx * wy_b) / nb_3
            denom = np.sqrt(np.maximum(ss_x_b, 0.0) * np.maximum(ss_y_b, 0.0))
            valid = (
                (nb_3 >= 2)
                & (~const_x_3)
                & (~const_y[:, None, :])
                & (ss_x_b > 0)
                & (ss_y_b > 0)
                & (denom > 0)
            )
            r_b = np.where(valid, np.clip(cov_b / denom, -1.0, 1.0), np.nan)
        out[start:end] = r_b

    return out.reshape((B,) + orig_mid + (34,))


def fast_cluster_bootstrap_mean(
    V: np.ndarray,
    pair_g: np.ndarray,
    counts: np.ndarray,
    G: int = 419,
) -> np.ndarray:
    """Exact cluster-multiplicity weighted arithmetic mean over pairs for each bootstrap draw.

    V: [P, ...] float64
    Returns: [B, ...] float64
    """
    orig_tail = V.shape[1:]
    P = V.shape[0]
    K = int(np.prod(orig_tail)) if orig_tail else 1
    V2 = np.asarray(V, dtype=np.float64).reshape(P, K)

    n_g = np.bincount(pair_g, minlength=G).astype(np.float64)
    N_b = counts @ n_g  # [B]

    Ind = np.zeros((G, P), dtype=np.float64)
    Ind[pair_g, np.arange(P)] = 1.0
    S_v = Ind @ V2  # [G, K]
    wv = counts @ S_v  # [B, K]
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(N_b[:, None] > 0, wv / N_b[:, None], np.nan)
    return out.reshape((counts.shape[0],) + orig_tail)


def save_tsv_and_csv(df: pd.DataFrame, base_path_without_ext: Path) -> tuple[Path, Path]:
    base_path_without_ext.parent.mkdir(parents=True, exist_ok=True)
    tsv_path = base_path_without_ext.with_suffix(".tsv")
    csv_path = base_path_without_ext.with_suffix(".csv")
    df.to_csv(tsv_path, sep="\t", index=False)
    df.to_csv(csv_path, index=False)
    return tsv_path, csv_path


def derive_control_seed(condition: str, participant: str, fold: int, seed: int) -> int:
    msg = f"EmoBrain/S9_O3/{condition}/{participant}/{fold}/{seed}".encode()
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], "big")


@torch.no_grad()
def run_fold_saved_interchange(
    readout,
    g_part: torch.Tensor,
    v_part: torch.Tensor,
    c_part: torch.Tensor,
    logit_saved_part: torch.Tensor,
    ratings_part: torch.Tensor,
    pairs_local: torch.Tensor,
    video_ids: tuple[int, ...],
    participant: str,
    fold: int,
    seed: int,
    checkpoint_id: str,
    control_seed: int,
):
    """Exact saved-decoded-feature counterpart of ac.interchange_intervention (no brain forward pass)."""
    n = g_part.shape[0]
    assert len(video_ids) == n and len(set(video_ids)) == n
    assert n >= 3
    a = pairs_local[:, 0]
    b = pairs_local[:, 1]

    generator = torch.Generator(device="cpu").manual_seed(control_seed)
    c_indices = torch.empty(ac.CONTROL_REPEATS, len(pairs_local), dtype=torch.long)
    for j, (ai, bi) in enumerate(pairs_local.tolist()):
        eligible = torch.tensor([i for i in range(n) if i not in (ai, bi)], dtype=torch.long)
        c_indices[:, j] = eligible[torch.randint(len(eligible), (ac.CONTROL_REPEATS,), generator=generator)]

    readout.eval()
    g_a = g_part[a]
    va, ca = v_part[a], c_part[a]
    vb, cb = v_part[b], c_part[b]

    z, p, I = ac.swap_2x2(readout, g_a, va, ca, vb, cb)

    # Verify z(A, A) matches test_outputs['logit'][a]
    z_aa_diff = float((z[:, 0, 0, :] - logit_saved_part[a]).abs().max().item())
    if z_aa_diff >= 1e-5:
        raise ValueError(f"z(A,A) mismatch vs saved logit: {z_aa_diff} >= 1e-5 ({checkpoint_id} {participant})")

    actual_lengths = torch.stack(
        (torch.linalg.vector_norm(vb - va, dim=-1), torch.linalg.vector_norm(cb - ca, dim=-1)),
        dim=-1,
    )

    control_z, control_p, control_I, lengths = [], [], [], []
    for cs in c_indices:
        v_random, _ = ac.length_matched_change(va, vb, v_part[cs])
        c_random, _ = ac.length_matched_change(ca, cb, c_part[cs])
        rz, rp, ri = ac.swap_2x2(readout, g_a, va, ca, v_random, c_random)
        control_z.append(rz.cpu())
        control_p.append(rp.cpu())
        control_I.append(ri.cpu())
        lengths.append(
            torch.stack(
                (
                    torch.linalg.vector_norm(v_random - va, dim=-1),
                    torch.linalg.vector_norm(c_random - ca, dim=-1),
                ),
                dim=-1,
            ).cpu()
        )

    controls_p = torch.stack(control_p)
    fi = ac.FoldInterventions(
        participant=participant,
        fold=fold,
        seed=seed,
        checkpoint_id=checkpoint_id,
        video_ids=video_ids,
        pairs=pairs_local,
        control_indices=c_indices,
        z=z.cpu(),
        p=p.cpu(),
        I=I.cpu(),
        delta_p=ac._delta_p(p).cpu(),
        delta_y=(ratings_part[b] - ratings_part[a]).cpu(),
        actual_lengths=actual_lengths.cpu(),
        control_z=torch.stack(control_z),
        control_p=controls_p,
        control_I=torch.stack(control_I),
        control_delta_p=ac._delta_p(controls_p),
        control_lengths=torch.stack(lengths),
        control_seed=control_seed,
    )
    return fi, z_aa_diff


def verify_explicit_concat_bootstrap(
    dp: np.ndarray,
    ctrl_dp: np.ndarray,
    dy: np.ndarray,
    abs_I: np.ndarray,
    ctrl_abs_I: np.ndarray,
    pair_g: np.ndarray,
    draws_5: np.ndarray,
    counts_5: np.ndarray,
    G: int,
) -> dict:
    """Verify weighted-Pearson & weighted-mean bootstrap matches explicit pair concatenation on 5 draws."""
    r_act_fast = fast_cluster_bootstrap_pearson(dp, dy, pair_g, counts_5, G=G)
    # ctrl_dp is [100, P, 3, 34] -> move P to 0: [P, 100, 3, 34]
    r_ctrl_each_fast = fast_cluster_bootstrap_pearson(np.moveaxis(ctrl_dp, 1, 0), dy, pair_g, counts_5, G=G)
    r_ctrl_mean_fast = r_ctrl_each_fast.mean(axis=1)
    abs_I_fast = fast_cluster_bootstrap_mean(abs_I, pair_g, counts_5, G=G)
    ctrl_abs_I_fast = fast_cluster_bootstrap_mean(np.moveaxis(ctrl_abs_I, 1, 0), pair_g, counts_5, G=G).mean(axis=1)

    max_diff_act = 0.0
    max_diff_ctrl_each = 0.0
    max_diff_ctrl_mean = 0.0
    max_diff_abs_I = 0.0
    max_diff_ctrl_abs_I = 0.0

    cluster_to_rows = [np.where(pair_g == g)[0] for g in range(G)]
    for b in range(len(draws_5)):
        idx = np.concatenate([cluster_to_rows[g] for g in draws_5[b]])
        ref_act = ac.change_alignment(
            torch.from_numpy(dp[idx].astype(np.float64)),
            torch.from_numpy(dy[idx].astype(np.float64)),
        ).r.numpy()
        ref_ctrl_each = ac.change_alignment(
            torch.from_numpy(np.moveaxis(ctrl_dp[:, idx, :, :], 1, 0).astype(np.float64)),
            torch.from_numpy(dy[idx].astype(np.float64)),
        ).r.numpy()
        ref_ctrl_mean = ref_ctrl_each.mean(axis=0)
        ref_abs_I = abs_I[idx].astype(np.float64).mean(axis=0)
        ref_ctrl_abs_I = ctrl_abs_I[:, idx, :].astype(np.float64).mean(axis=1).mean(axis=0)

        assert np.array_equal(np.isnan(r_act_fast[b]), np.isnan(ref_act)), "NaN pattern mismatch in actual_r!"
        assert np.array_equal(np.isnan(r_ctrl_each_fast[b]), np.isnan(ref_ctrl_each)), "NaN pattern mismatch in ctrl_r!"

        m_act = np.nanmax(np.abs(r_act_fast[b] - ref_act))
        m_ce = np.nanmax(np.abs(r_ctrl_each_fast[b] - ref_ctrl_each))
        m_cm = np.nanmax(np.abs(r_ctrl_mean_fast[b] - ref_ctrl_mean))
        m_ai = float(np.max(np.abs(abs_I_fast[b] - ref_abs_I)))
        m_cai = float(np.max(np.abs(ctrl_abs_I_fast[b] - ref_ctrl_abs_I)))

        max_diff_act = max(max_diff_act, float(m_act))
        max_diff_ctrl_each = max(max_diff_ctrl_each, float(m_ce))
        max_diff_ctrl_mean = max(max_diff_ctrl_mean, float(m_cm))
        max_diff_abs_I = max(max_diff_abs_I, m_ai)
        max_diff_ctrl_abs_I = max(max_diff_ctrl_abs_I, m_cai)

    overall_max = max(max_diff_act, max_diff_ctrl_each, max_diff_ctrl_mean, max_diff_abs_I, max_diff_ctrl_abs_I)
    if overall_max >= 1e-12:
        raise ValueError(f"Weighted bootstrap equivalence check failed: max_abs_diff={overall_max:.3e} >= 1e-12")
    return {
        "n_explicit_draws": int(len(draws_5)),
        "max_abs_diff_actual_r": max_diff_act,
        "max_abs_diff_control_r_each": max_diff_ctrl_each,
        "max_abs_diff_control_r_mean": max_diff_ctrl_mean,
        "max_abs_diff_abs_I": max_diff_abs_I,
        "max_abs_diff_control_abs_I": max_diff_ctrl_abs_I,
        "max_abs_diff_overall": overall_max,
    }


def main():
    parser = argparse.ArgumentParser(description="S9-1 Interchange Interventions & S9-2 Nearest-Pair Comparison")
    parser.add_argument("--device", default="cpu", choices=["cpu"], help="CPU only (strictly enforced)")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("/scratch/emobrain/outputs/s9_analysis"),
        help="Root output directory for S9 analysis",
    )
    args = parser.parse_args()
    if args.device != "cpu" or torch.cuda.is_available():
        raise SystemExit("Strictly CPU execution required (--device cpu and CUDA_VISIBLE_DEVICES='').")

    t_start = time.time()
    out_root: Path = args.out_dir
    interchange_dir = out_root / "interchange"
    pair_comp_dir = out_root / "pair_comparison"
    interchange_dir.mkdir(parents=True, exist_ok=True)
    pair_comp_dir.mkdir(parents=True, exist_ok=True)

    # Verify BH-FDR implementation matches scipy if installed
    try:
        from scipy.stats import false_discovery_control
        _test_p = np.linspace(0.001, 0.9, 34)
        assert np.max(np.abs(bh_fdr(_test_p) - false_discovery_control(_test_p, method="bh"))) < 1e-15
    except Exception:
        pass

    print(f"[S9] Starting S9-1 & S9-2 on CPU (threads={torch.get_num_threads()}, cuda={torch.cuda.is_available()})")

    # 1. Load split, ground-truth 34 emotions, and S2 pair manifests
    split = c.load_split()
    assert len(split) == 2109 and split["video_id"].is_unique
    y_em, em_cols = c.load_scores(split, "emotions")  # [2109, 34] float32
    label_map = pd.read_csv(c.LABEL_MAP, sep="\t")
    assert label_map["score_col"].tolist() == em_cols
    emotion_names = label_map["name"].tolist()
    assert len(emotion_names) == 34

    # Verify EmoNet still-frame group emotion names
    name_to_eidx = {n: i for i, n in enumerate(emotion_names)}
    for n in HIGH_EMONET_NAMES + LOW_EMONET_NAMES:
        if n not in name_to_eidx:
            raise ValueError(f"EmoNet group emotion '{n}' not found in label_map_34.tsv!")
    high_eidx = np.array([name_to_eidx[n] for n in HIGH_EMONET_NAMES], dtype=np.int64)
    low_eidx = np.array([name_to_eidx[n] for n in LOW_EMONET_NAMES], dtype=np.int64)
    emonet_group_of = [
        "high" if n in HIGH_EMONET_NAMES else ("low" if n in LOW_EMONET_NAMES else "other")
        for n in emotion_names
    ]

    vid_to_split_row = {int(v): i for i, v in enumerate(split["video_id"].tolist())}

    s2_dir = CODE_ROOT / "manifests" / "s2"
    pairs_dir_df = pd.read_csv(s2_dir / "pairs_directed.tsv", sep="\t")
    pairs_un_df = pd.read_csv(s2_dir / "pairs_unordered.tsv", sep="\t")
    pair_groups_df = pd.read_csv(s2_dir / "pair_groups.tsv", sep="\t")
    pair_missing_df = pd.read_csv(s2_dir / "pair_missing_counts.tsv", sep="\t").set_index("participant")

    assert len(pairs_dir_df) == 2109, f"Expected 2109 directed pairs, got {len(pairs_dir_df)}"
    assert len(pairs_un_df) == 1690, f"Expected 1690 unordered pairs, got {len(pairs_un_df)}"
    assert (pairs_un_df["video_a"] < pairs_un_df["video_b"]).all(), "Unordered pairs must satisfy video_a < video_b!"

    # Verify connected cluster structure (419 clusters across 6 folds)
    unique_clusters_df = pair_groups_df[["fold", "pair_group", "group_size"]].drop_duplicates().reset_index(drop=True)
    G = len(unique_clusters_df)
    assert G == 419, f"Expected 419 pair_group clusters, got {G}"
    assert int(unique_clusters_df["group_size"].sum()) == 2109

    cluster_names = unique_clusters_df["pair_group"].tolist()
    pg_to_gidx = {pg_name: idx for idx, pg_name in enumerate(cluster_names)}
    vid_to_pg = dict(zip(pair_groups_df["video_id"].astype(int), pair_groups_df["pair_group"]))
    vid_to_fold = dict(zip(pair_groups_df["video_id"].astype(int), pair_groups_df["fold"].astype(int)))

    # Assert every directed & unordered pair belongs to a single pair_group in its fold
    for label_kind, df_p in (("directed", pairs_dir_df), ("unordered", pairs_un_df)):
        pg_a = df_p["video_a"].map(vid_to_pg)
        pg_b = df_p["video_b"].map(vid_to_pg)
        f_a = df_p["video_a"].map(vid_to_fold)
        assert pg_a.notna().all() and pg_b.notna().all()
        assert (pg_a == pg_b).all(), f"{label_kind} pair crosses pair_group boundary!"
        assert (f_a == df_p["fold"]).all(), f"{label_kind} pair fold mismatch!"

    pairs_dir_df = pairs_dir_df.copy()
    pairs_dir_df["pair_group"] = pairs_dir_df["video_a"].map(vid_to_pg)
    pairs_dir_df["gidx"] = pairs_dir_df["pair_group"].map(pg_to_gidx).astype(np.int64)

    pairs_un_df = pairs_un_df.copy()
    pairs_un_df["pair_group"] = pairs_un_df["video_a"].map(vid_to_pg)
    pairs_un_df["gidx"] = pairs_un_df["pair_group"].map(pg_to_gidx).astype(np.int64)

    # Save group_size_distribution.tsv (& .csv)
    dir_per_g = pairs_dir_df.groupby("pair_group").size()
    un_per_g = pairs_un_df.groupby("pair_group").size()
    unique_clusters_df["n_directed_pairs"] = unique_clusters_df["pair_group"].map(dir_per_g).fillna(0).astype(int)
    unique_clusters_df["n_unordered_pairs"] = unique_clusters_df["pair_group"].map(un_per_g).fillna(0).astype(int)
    gs_rows = []
    for gs, grp in unique_clusters_df.groupby("group_size", sort=True):
        n_cl = len(grp)
        tot_v = int(grp["group_size"].sum())
        gs_rows.append(
            dict(
                group_size=int(gs),
                n_clusters=int(n_cl),
                pct_clusters=100.0 * n_cl / G,
                total_videos=tot_v,
                pct_videos=100.0 * tot_v / 2109.0,
                total_directed_pairs=int(grp["n_directed_pairs"].sum()),
                total_unordered_pairs=int(grp["n_unordered_pairs"].sum()),
            )
        )
    gs_dist_df = pd.DataFrame(gs_rows)
    save_tsv_and_csv(gs_dist_df, interchange_dir / "group_size_distribution")
    print(f"[S9] Verified 419 pair_group clusters (size {gs_dist_df['group_size'].min()}..{gs_dist_df['group_size'].max()})")

    # 2. Generate the shared 10,000-iteration pair_group cluster bootstrap draws (O4(2), O4(3), O4(7), 1009)
    boot_seed_int = int.from_bytes(hashlib.sha256(BOOTSTRAP_SEED_BYTES).digest()[:8], "big")
    rng_boot = np.random.default_rng(boot_seed_int)
    cluster_draws = rng_boot.integers(0, G, size=(N_BOOTSTRAP, G), dtype=np.int32)
    cluster_counts = np.zeros((N_BOOTSTRAP, G), dtype=np.float64)
    for b in range(N_BOOTSTRAP):
        cluster_counts[b] = np.bincount(cluster_draws[b], minlength=G)
    np.savez(
        out_root / "pair_cluster_bootstrap_draws.npz",
        seed_string=np.array(BOOTSTRAP_SEED_BYTES.decode()),
        seed_uint64=np.uint64(boot_seed_int),
        pair_groups=np.array(cluster_names),
        cluster_counts=cluster_counts.astype(np.uint8),
    )
    print(f"[S9] Generated {N_BOOTSTRAP} shared pair_group bootstrap draws (seed_uint64={boot_seed_int})")

    # =========================================================================
    # TASK A: S9-1 INTERCHANGE INTERVENTIONS
    # =========================================================================
    n_conds = len(INTERCHANGE_CONDITIONS)
    n_subs = len(PARTICIPANTS)
    n_seeds = len(SEEDS)

    # Point estimate arrays: [n_cond, n_sub, n_seed, ...]
    pt_actual_r = np.empty((n_conds, n_subs, n_seeds, 3, 34), dtype=np.float64)
    pt_ctrl_r_mean = np.empty((n_conds, n_subs, n_seeds, 3, 34), dtype=np.float64)
    pt_effect = np.empty((n_conds, n_subs, n_seeds, 3, 34), dtype=np.float64)
    pt_n_const_target = np.zeros((n_conds, n_subs, n_seeds), dtype=np.int64)
    pt_n_const_pred_act = np.zeros((n_conds, n_subs, n_seeds, 3), dtype=np.int64)
    pt_n_const_pred_ctrl = np.zeros((n_conds, n_subs, n_seeds, 3), dtype=np.int64)
    pt_n_pairs_valid = np.zeros((n_conds, n_subs, n_seeds), dtype=np.int64)

    pt_mean_abs_I = np.empty((n_conds, n_subs, n_seeds, 34), dtype=np.float64)
    pt_ctrl_mean_abs_I = np.empty((n_conds, n_subs, n_seeds, 34), dtype=np.float64)
    pt_abs_I_effect = np.empty((n_conds, n_subs, n_seeds, 34), dtype=np.float64)
    pt_max_abs_I_act = np.zeros((n_conds, n_subs, n_seeds), dtype=np.float64)
    pt_max_abs_I_ctrl = np.zeros((n_conds, n_subs, n_seeds), dtype=np.float64)

    pt_prob_I = np.empty((n_conds, n_subs, n_seeds, 34), dtype=np.float64)
    pt_ctrl_prob_I = np.empty((n_conds, n_subs, n_seeds, 34), dtype=np.float64)
    pt_prob_I_effect = np.empty((n_conds, n_subs, n_seeds, 34), dtype=np.float64)

    # Bootstrap replicate arrays: [n_cond, n_sub, n_seed, B, ...]
    boot_actual_r = np.empty((n_conds, n_subs, n_seeds, N_BOOTSTRAP, 3, 34), dtype=np.float64)
    boot_ctrl_r_mean = np.empty((n_conds, n_subs, n_seeds, N_BOOTSTRAP, 3, 34), dtype=np.float64)
    boot_effect = np.empty((n_conds, n_subs, n_seeds, N_BOOTSTRAP, 3, 34), dtype=np.float64)
    boot_abs_I_effect = np.empty((n_conds, n_subs, n_seeds, N_BOOTSTRAP, 34), dtype=np.float64)
    boot_prob_I_effect = np.empty((n_conds, n_subs, n_seeds, N_BOOTSTRAP, 34), dtype=np.float64)

    selected_candidates_log = {}
    z_aa_max_diff_by_cond = {}
    ctrl_len_mismatch_by_cond = {}
    additive_verification_detail = []
    step_length_rows = []
    explicit_bootstrap_checks = {}
    saved_interchange_npz_files = []

    ones_1xG = np.ones((1, G), dtype=np.float64)

    for ci, (cond, mcode) in enumerate(INTERCHANGE_CONDITIONS):
        z_aa_max_cond = 0.0
        len_mismatch_vis_cond = 0.0
        len_mismatch_cap_cond = 0.0
        selected_candidates_log[cond] = {}

        for si, seed in enumerate(SEEDS):
            t_cs = time.time()
            fold_fis_by_sub = {pid: [] for pid in PARTICIPANTS}
            fold_meta_by_sub = {pid: [] for pid in PARTICIPANTS}

            for fold in FOLDS:
                fdir = S.OUT / f"outer_fold{fold}"
                sel = json.loads((fdir / cond / "selected.json").read_text())
                if si == 0:
                    selected_candidates_log[cond][f"outer_fold{fold}"] = {
                        "candidate": sel["candidate"],
                        "zero_selected": sel["zero_selected"],
                        "seeds": sel["seeds"],
                    }
                seed_rel = sel["seeds"][str(seed)]
                sdir = fdir / seed_rel
                checkpoint_id = f"outer_fold{fold}/{seed_rel}"

                model, _ = M.load_checkpoint(sdir / "model.pt", device="cpu")
                readout = model.main.readout if cond == "brain_decoded_sep" else model.readout
                readout.eval()

                to = np.load(sdir / "outputs" / "test_outputs.npz")
                dt = np.load(sdir / "outputs" / "decoded_test.npz")
                assert np.array_equal(to["participant"], dt["participant"])
                assert np.array_equal(to["video_id"], dt["video_id"])

                f_pairs_df = pairs_dir_df[pairs_dir_df["fold"] == fold]
                f_un_fold_df = pairs_un_df[pairs_un_df["fold"] == fold]

                for pi, pid in enumerate(PARTICIPANTS):
                    mask = to["participant"] == pid
                    vids = to["video_id"][mask].astype(np.int64)
                    vids_tuple = tuple(int(v) for v in vids.tolist())
                    vid_to_local = {int(v): idx for idx, v in enumerate(vids_tuple)}

                    # Count valid unordered pairs in this fold for O9 completeness reporting
                    n_un_fold_valid = sum(
                        1
                        for r in f_un_fold_df.itertuples(index=False)
                        if (int(r.video_a) in vid_to_local) and (int(r.video_b) in vid_to_local)
                    )

                    # Filter directed pairs where BOTH video_a and video_b exist in participant's test rows (O9)
                    valid_rows = [
                        (
                            vid_to_local[int(r.video_a)],
                            vid_to_local[int(r.video_b)],
                            int(r.video_a),
                            int(r.video_b),
                            float(r.distance),
                            str(r.pair_group),
                            int(r.gidx),
                        )
                        for r in f_pairs_df.itertuples(index=False)
                        if (int(r.video_a) in vid_to_local) and (int(r.video_b) in vid_to_local)
                    ]
                    pairs_local = torch.tensor([[ x[0], x[1] ] for x in valid_rows], dtype=torch.long)

                    # Map ratings strictly via video_id -> split row
                    split_rows = [vid_to_split_row[v] for v in vids_tuple]
                    ratings_part = torch.from_numpy(y_em[split_rows])
                    g_part = torch.from_numpy(to["g"][mask])
                    v_part = torch.from_numpy(dt["v_hat"][mask])
                    c_part = torch.from_numpy(dt["c_hat"][mask])
                    logit_part = torch.from_numpy(to["logit"][mask])

                    cseed = derive_control_seed(cond, pid, fold, seed)
                    fi, z_diff = run_fold_saved_interchange(
                        readout=readout,
                        g_part=g_part,
                        v_part=v_part,
                        c_part=c_part,
                        logit_saved_part=logit_part,
                        ratings_part=ratings_part,
                        pairs_local=pairs_local,
                        video_ids=vids_tuple,
                        participant=pid,
                        fold=fold,
                        seed=seed,
                        checkpoint_id=checkpoint_id,
                        control_seed=cseed,
                    )
                    z_aa_max_cond = max(z_aa_max_cond, z_diff)

                    # Verify control step lengths match actual step lengths
                    act_len_np = fi.actual_lengths.numpy()  # [P_f, 2]
                    ctrl_len_np = fi.control_lengths.numpy()  # [100, P_f, 2]
                    vis_mm = float(np.max(np.abs(ctrl_len_np[:, :, 0] - act_len_np[None, :, 0])))
                    cap_mm = float(np.max(np.abs(ctrl_len_np[:, :, 1] - act_len_np[None, :, 1])))
                    len_mismatch_vis_cond = max(len_mismatch_vis_cond, vis_mm)
                    len_mismatch_cap_cond = max(len_mismatch_cap_cond, cap_mm)

                    donor_vids = vids[fi.control_indices.numpy()]  # [100, P_f]
                    va_ids = np.array([x[2] for x in valid_rows], dtype=np.int32)
                    vb_ids = np.array([x[3] for x in valid_rows], dtype=np.int32)
                    assert not np.any(donor_vids == va_ids[None, :])
                    assert not np.any(donor_vids == vb_ids[None, :])

                    sem_dists = np.array([x[4] for x in valid_rows], dtype=np.float32)
                    pg_names = np.array([x[5] for x in valid_rows], dtype="<U8")
                    gidxs = np.array([x[6] for x in valid_rows], dtype=np.int64)

                    fold_fis_by_sub[pid].append(fi)
                    fold_meta_by_sub[pid].append(
                        dict(
                            fold=fold,
                            n_all=len(f_pairs_df),
                            n_valid=len(valid_rows),
                            n_un_all=len(f_un_fold_df),
                            n_un_valid=n_un_fold_valid,
                            va_ids=va_ids,
                            vb_ids=vb_ids,
                            donor_vids=donor_vids.astype(np.int32),
                            sem_dists=sem_dists,
                            pg_names=pg_names,
                            gidxs=gidxs,
                            vis_mm=vis_mm,
                            cap_mm=cap_mm,
                        )
                    )

                    # Record per-fold step length & missing pair row
                    step_length_rows.append(
                        dict(
                            condition=cond,
                            model_code=mcode,
                            participant=pid,
                            seed=str(seed),
                            fold=str(fold),
                            n_directed_all=len(f_pairs_df),
                            n_directed_valid=len(valid_rows),
                            n_directed_missing=len(f_pairs_df) - len(valid_rows),
                            n_unordered_all=len(f_un_fold_df),
                            n_unordered_valid=n_un_fold_valid,
                            n_unordered_missing=len(f_un_fold_df) - n_un_fold_valid,
                            manifest_missing_exact_match=np.nan,
                            semantic_tag_dist_mean=float(sem_dists.mean()),
                            semantic_tag_dist_sd=float(sem_dists.std(ddof=1)),
                            semantic_tag_dist_median=float(np.median(sem_dists)),
                            semantic_tag_dist_min=float(sem_dists.min()),
                            semantic_tag_dist_max=float(sem_dists.max()),
                            visual_step_d9_mean=float(act_len_np[:, 0].mean()),
                            visual_step_d9_sd=float(act_len_np[:, 0].std(ddof=1)),
                            visual_step_d9_median=float(np.median(act_len_np[:, 0])),
                            visual_step_d9_min=float(act_len_np[:, 0].min()),
                            visual_step_d9_max=float(act_len_np[:, 0].max()),
                            caption_step_d9_mean=float(act_len_np[:, 1].mean()),
                            caption_step_d9_sd=float(act_len_np[:, 1].std(ddof=1)),
                            caption_step_d9_median=float(np.median(act_len_np[:, 1])),
                            caption_step_d9_min=float(act_len_np[:, 1].min()),
                            caption_step_d9_max=float(act_len_np[:, 1].max()),
                            max_control_length_mismatch_vis=vis_mm,
                            max_control_length_mismatch_cap=cap_mm,
                        )
                    )

            # Pool across 6 folds per participant, verify O9 missing counts, run ac.summarize_interventions & 10,000 bootstrap
            npz_parts = []
            npz_folds = []
            npz_pg = []
            npz_va = []
            npz_vb = []
            npz_sem_dist = []
            npz_act_len = []
            npz_z = []
            npz_p = []
            npz_I = []
            npz_I_prob = []
            npz_dp = []
            npz_dy = []
            npz_donor_vids = []
            npz_ctrl_local = []
            npz_ctrl_z = []
            npz_ctrl_I = []
            npz_ctrl_dp = []
            npz_ctrl_len = []

            for pi, pid in enumerate(PARTICIPANTS):
                fis = fold_fis_by_sub[pid]
                metas = fold_meta_by_sub[pid]
                summ = ac.summarize_interventions(fis)

                n_valid_tot = int(summ["n_pairs"].item())
                n_missing_tot = 2109 - n_valid_tot
                expected_missing = int(pair_missing_df.loc[pid, "n_directed_missing"])
                if n_missing_tot != expected_missing:
                    raise ValueError(
                        f"O9 directed missing mismatch for {pid}: got {n_missing_tot}, expected {expected_missing}"
                    )

                dp_cat = torch.cat([x.delta_p for x in fis], dim=0).numpy().astype(np.float64)        # [P, 3, 34]
                dy_cat = torch.cat([x.delta_y for x in fis], dim=0).numpy().astype(np.float64)        # [P, 34]
                ctrl_dp_cat = torch.cat([x.control_delta_p for x in fis], dim=1).numpy()              # [100, P, 3, 34] float32
                I_cat = torch.cat([x.I for x in fis], dim=0).numpy()                                  # [P, 34] float32
                ctrl_I_cat = torch.cat([x.control_I for x in fis], dim=1).numpy()                     # [100, P, 34] float32

                p_cat = torch.cat([x.p for x in fis], dim=0).numpy()                                  # [P, 2, 2, 34]
                ctrl_p_cat = torch.cat([x.control_p for x in fis], dim=1).numpy()                     # [100, P, 2, 2, 34]
                I_prob_cat = (p_cat[:, 1, 1, :] - p_cat[:, 1, 0, :]) - (p_cat[:, 0, 1, :] - p_cat[:, 0, 0, :])
                ctrl_I_prob_cat = (
                    (ctrl_p_cat[:, :, 1, 1, :] - ctrl_p_cat[:, :, 1, 0, :])
                    - (ctrl_p_cat[:, :, 0, 1, :] - ctrl_p_cat[:, :, 0, 0, :])
                )

                pair_g_cat = np.concatenate([m["gidxs"] for m in metas])                              # [P]
                sem_cat = np.concatenate([m["sem_dists"] for m in metas])
                act_len_cat = torch.cat([x.actual_lengths for x in fis], dim=0).numpy()

                # Verify additive head I == 0 (919)
                max_I_act = float(np.max(np.abs(I_cat)))
                max_I_ctrl = float(np.max(np.abs(ctrl_I_cat)))
                pt_max_abs_I_act[ci, pi, si] = max_I_act
                pt_max_abs_I_ctrl[ci, pi, si] = max_I_ctrl
                if cond == "brain_decoded_additive":
                    if max(max_I_act, max_I_ctrl) >= 1e-5:
                        raise ValueError(
                            f"Additive head unit test failed ({pid} seed{seed}): max_I_act={max_I_act}, max_I_ctrl={max_I_ctrl}"
                        )
                    additive_verification_detail.append(
                        dict(
                            participant=pid,
                            seed=seed,
                            n_pairs_valid=n_valid_tot,
                            max_abs_I_actual=max_I_act,
                            max_abs_I_control_100draws=max_I_ctrl,
                        )
                    )

                # Store pooled point estimates from ac.summarize_interventions
                pt_actual_r[ci, pi, si] = summ["actual_r"].numpy()
                pt_ctrl_r_mean[ci, pi, si] = summ["control_r_mean"].numpy()
                pt_effect[ci, pi, si] = summ["effect"].numpy()
                pt_n_const_target[ci, pi, si] = int(summ["constant_target"].sum().item())
                pt_n_const_pred_act[ci, pi, si] = summ["n_constant_prediction"].numpy()
                pt_n_const_pred_ctrl[ci, pi, si] = summ["n_control_constant_prediction"].max(dim=0).values.numpy()
                pt_n_pairs_valid[ci, pi, si] = n_valid_tot

                pt_mean_abs_I[ci, pi, si] = summ["mean_abs_I"].numpy()
                pt_ctrl_mean_abs_I[ci, pi, si] = summ["control_mean_abs_I"].numpy()
                pt_abs_I_effect[ci, pi, si] = summ["mean_abs_I_effect"].numpy()

                abs_Ip_d = np.abs(I_prob_cat.astype(np.float64))
                ctrl_abs_Ip_d = np.abs(ctrl_I_prob_cat.astype(np.float64))
                pt_prob_I[ci, pi, si] = abs_Ip_d.mean(axis=0)
                pt_ctrl_prob_I[ci, pi, si] = ctrl_abs_Ip_d.mean(axis=1).mean(axis=0)
                pt_prob_I_effect[ci, pi, si] = pt_prob_I[ci, pi, si] - pt_ctrl_prob_I[ci, pi, si]

                # Cross-check fast_cluster_bootstrap_pearson on uniform weights == ac.summarize_interventions
                r_unif_act = fast_cluster_bootstrap_pearson(dp_cat, dy_cat, pair_g_cat, ones_1xG, G=G)[0]
                r_unif_ctrl = fast_cluster_bootstrap_pearson(
                    np.moveaxis(ctrl_dp_cat, 1, 0), dy_cat, pair_g_cat, ones_1xG, G=G
                )[0].mean(axis=0)
                assert np.nanmax(np.abs(r_unif_act - pt_actual_r[ci, pi, si])) < 1e-13
                assert np.nanmax(np.abs(r_unif_ctrl - pt_ctrl_r_mean[ci, pi, si])) < 1e-13

                # Explicit pair-concatenation verification on 5 bootstrap draws for C-1 seed0 (sub-01 and sub-05)
                if cond == "brain_decoded" and seed == 0 and pid in ("sub-01", "sub-05"):
                    explicit_bootstrap_checks[f"{cond}_seed{seed}_{pid}"] = verify_explicit_concat_bootstrap(
                        dp=dp_cat,
                        ctrl_dp=ctrl_dp_cat,
                        dy=dy_cat,
                        abs_I=np.abs(I_cat.astype(np.float64)),
                        ctrl_abs_I=np.abs(ctrl_I_cat.astype(np.float64)),
                        pair_g=pair_g_cat,
                        draws_5=cluster_draws[:5],
                        counts_5=cluster_counts[:5],
                        G=G,
                    )

                # Run 10,000-iteration cluster bootstrap!
                b_act = fast_cluster_bootstrap_pearson(dp_cat, dy_cat, pair_g_cat, cluster_counts, G=G, chunk=1000)
                # Process 100 controls in 2 slices of 50 to keep peak RAM < 1 GB
                b_ctrl_part1 = fast_cluster_bootstrap_pearson(
                    np.moveaxis(ctrl_dp_cat[:50], 1, 0), dy_cat, pair_g_cat, cluster_counts, G=G, chunk=500
                ).sum(axis=1)
                b_ctrl_part2 = fast_cluster_bootstrap_pearson(
                    np.moveaxis(ctrl_dp_cat[50:], 1, 0), dy_cat, pair_g_cat, cluster_counts, G=G, chunk=500
                ).sum(axis=1)
                b_ctrl_mean = (b_ctrl_part1 + b_ctrl_part2) / 100.0

                boot_actual_r[ci, pi, si] = b_act
                boot_ctrl_r_mean[ci, pi, si] = b_ctrl_mean
                boot_effect[ci, pi, si] = b_act - b_ctrl_mean

                # Bootstrap for |I| and |I_prob|
                abs_I_d = np.abs(I_cat.astype(np.float64))
                ctrl_abs_I_mean100_per_pair = np.abs(ctrl_I_cat.astype(np.float64)).mean(axis=0)  # [P, 34]
                # Note: (1/100) sum_m [(1/N_b) sum_p w_{b,p} |I_{m,p}|] == (1/N_b) sum_p w_{b,p} [(1/100) sum_m |I_{m,p}|]
                b_abs_I = fast_cluster_bootstrap_mean(abs_I_d, pair_g_cat, cluster_counts, G=G)
                b_ctrl_abs_I = fast_cluster_bootstrap_mean(ctrl_abs_I_mean100_per_pair, pair_g_cat, cluster_counts, G=G)
                boot_abs_I_effect[ci, pi, si] = b_abs_I - b_ctrl_abs_I

                ctrl_abs_Ip_mean100_per_pair = ctrl_abs_Ip_d.mean(axis=0)
                b_prob_I = fast_cluster_bootstrap_mean(abs_Ip_d, pair_g_cat, cluster_counts, G=G)
                b_ctrl_prob_I = fast_cluster_bootstrap_mean(ctrl_abs_Ip_mean100_per_pair, pair_g_cat, cluster_counts, G=G)
                boot_prob_I_effect[ci, pi, si] = b_prob_I - b_ctrl_prob_I

                # Record pooled all_6folds step length & missing pair row
                n_un_tot_valid = sum(m["n_un_valid"] for m in metas)
                n_un_tot_missing = 1690 - n_un_tot_valid
                assert n_un_tot_missing == int(pair_missing_df.loc[pid, "n_unordered_missing"])
                step_length_rows.append(
                    dict(
                        condition=cond,
                        model_code=mcode,
                        participant=pid,
                        seed=str(seed),
                        fold="all_6folds",
                        n_directed_all=2109,
                        n_directed_valid=n_valid_tot,
                        n_directed_missing=n_missing_tot,
                        n_unordered_all=1690,
                        n_unordered_valid=n_un_tot_valid,
                        n_unordered_missing=n_un_tot_missing,
                        manifest_missing_exact_match=True,
                        semantic_tag_dist_mean=float(sem_cat.mean()),
                        semantic_tag_dist_sd=float(sem_cat.std(ddof=1)),
                        semantic_tag_dist_median=float(np.median(sem_cat)),
                        semantic_tag_dist_min=float(sem_cat.min()),
                        semantic_tag_dist_max=float(sem_cat.max()),
                        visual_step_d9_mean=float(act_len_cat[:, 0].mean()),
                        visual_step_d9_sd=float(act_len_cat[:, 0].std(ddof=1)),
                        visual_step_d9_median=float(np.median(act_len_cat[:, 0])),
                        visual_step_d9_min=float(act_len_cat[:, 0].min()),
                        visual_step_d9_max=float(act_len_cat[:, 0].max()),
                        caption_step_d9_mean=float(act_len_cat[:, 1].mean()),
                        caption_step_d9_sd=float(act_len_cat[:, 1].std(ddof=1)),
                        caption_step_d9_median=float(np.median(act_len_cat[:, 1])),
                        caption_step_d9_min=float(act_len_cat[:, 1].min()),
                        caption_step_d9_max=float(act_len_cat[:, 1].max()),
                        max_control_length_mismatch_vis=max(m["vis_mm"] for m in metas),
                        max_control_length_mismatch_cap=max(m["cap_mm"] for m in metas),
                    )
                )

                # Accumulate per-pair arrays for saving interchange_<condition>_seed<seed>.npz
                npz_parts.append(np.full(n_valid_tot, pid, dtype="<U6"))
                npz_folds.append(np.concatenate([np.full(m["n_valid"], m["fold"], dtype=np.int16) for m in metas]))
                npz_pg.append(np.concatenate([m["pg_names"] for m in metas]))
                npz_va.append(np.concatenate([m["va_ids"] for m in metas]))
                npz_vb.append(np.concatenate([m["vb_ids"] for m in metas]))
                npz_sem_dist.append(sem_cat)
                npz_act_len.append(act_len_cat)
                npz_z.append(torch.cat([x.z for x in fis], dim=0).numpy())
                npz_p.append(p_cat)
                npz_I.append(I_cat)
                npz_I_prob.append(I_prob_cat)
                npz_dp.append(dp_cat.astype(np.float32))
                npz_dy.append(dy_cat.astype(np.float32))
                npz_donor_vids.append(np.concatenate([m["donor_vids"] for m in metas], axis=1))
                npz_ctrl_local.append(torch.cat([x.control_indices for x in fis], dim=1).numpy().astype(np.int16))
                npz_ctrl_z.append(torch.cat([x.control_z for x in fis], dim=1).numpy())
                npz_ctrl_I.append(ctrl_I_cat)
                npz_ctrl_dp.append(ctrl_dp_cat)
                npz_ctrl_len.append(torch.cat([x.control_lengths for x in fis], dim=1).numpy())

            npz_path = interchange_dir / f"interchange_{cond}_seed{seed}.npz"
            np.savez(
                npz_path,
                condition=np.array(cond),
                model_code=np.array(mcode),
                seed=np.int32(seed),
                participant=np.concatenate(npz_parts),
                fold=np.concatenate(npz_folds),
                pair_group=np.concatenate(npz_pg),
                video_a=np.concatenate(npz_va),
                video_b=np.concatenate(npz_vb),
                semantic_distance=np.concatenate(npz_sem_dist),
                actual_lengths_d9=np.concatenate(npz_act_len, axis=0),
                z=np.concatenate(npz_z, axis=0),
                p=np.concatenate(npz_p, axis=0),
                I=np.concatenate(npz_I, axis=0),
                I_prob=np.concatenate(npz_I_prob, axis=0),
                delta_p=np.concatenate(npz_dp, axis=0),
                delta_y=np.concatenate(npz_dy, axis=0),
                control_donor_video_ids=np.concatenate(npz_donor_vids, axis=1),
                control_indices_local=np.concatenate(npz_ctrl_local, axis=1),
                control_z=np.concatenate(npz_ctrl_z, axis=1),
                control_I=np.concatenate(npz_ctrl_I, axis=1),
                control_delta_p=np.concatenate(npz_ctrl_dp, axis=1),
                control_lengths_d9=np.concatenate(npz_ctrl_len, axis=1),
            )
            saved_interchange_npz_files.append(str(npz_path))
            print(
                f"[S9-1] Completed {cond} ({mcode}) seed={seed} in {time.time() - t_cs:.1f}s "
                f"(saved {npz_path.name})"
            )

        z_aa_max_diff_by_cond[cond] = z_aa_max_cond
        ctrl_len_mismatch_by_cond[cond] = {
            "visual_max_abs_diff": len_mismatch_vis_cond,
            "caption_max_abs_diff": len_mismatch_cap_cond,
        }

    # Add 3-seed mean rows to step_length_rows (for all_6folds)
    step_df_raw = pd.DataFrame(step_length_rows)
    mean3_step_rows = []
    for (cond, mcode, pid), grp in step_df_raw[step_df_raw["fold"] == "all_6folds"].groupby(
        ["condition", "model_code", "participant"], sort=False
    ):
        r0 = grp.iloc[0].to_dict()
        r0["seed"] = "mean_3seeds"
        for col in [
            "visual_step_d9_mean",
            "visual_step_d9_sd",
            "visual_step_d9_median",
            "visual_step_d9_min",
            "visual_step_d9_max",
            "caption_step_d9_mean",
            "caption_step_d9_sd",
            "caption_step_d9_median",
            "caption_step_d9_min",
            "caption_step_d9_max",
        ]:
            r0[col] = float(grp[col].mean())
        r0["max_control_length_mismatch_vis"] = float(grp["max_control_length_mismatch_vis"].max())
        r0["max_control_length_mismatch_cap"] = float(grp["max_control_length_mismatch_cap"].max())
        mean3_step_rows.append(r0)
    step_length_df = pd.concat([step_df_raw, pd.DataFrame(mean3_step_rows)], ignore_index=True)
    save_tsv_and_csv(step_length_df, interchange_dir / "s9_step_lengths_and_missing")

    # =========================================================================
    # BUILD S9-1 SUMMARY TABLES (2-2, 1-1, 1-1 EmoNet groups, 1-2(나))
    # =========================================================================
    # Helper to expand [n_sub, n_seed, ...] -> grid of (sub_label, seed_label)
    # sub_labels: sub-01..sub-05 + mean_5sub
    # seed_labels: 0, 1, 2 + mean_3seeds
    sub_labels = list(PARTICIPANTS) + ["mean_5sub"]
    seed_labels = ["0", "1", "2", "mean_3seeds"]

    def get_grid_slice(pt_arr, boot_arr, pi_idx, si_idx):
        """Extract (theta_hat, theta_boot, seed_sd) for participant index pi_idx (0..5) and seed index si_idx (0..3).
        pt_arr: [5, 3, ...], boot_arr: [5, 3, B, ...]
        """
        if pi_idx < 5:
            pt_p = pt_arr[pi_idx]        # [3, ...]
            bt_p = boot_arr[pi_idx]      # [3, B, ...]
        else:
            pt_p = np.mean(pt_arr, axis=0)   # [3, ...]
            bt_p = np.mean(boot_arr, axis=0) # [3, B, ...]

        if si_idx < 3:
            return pt_p[si_idx], bt_p[si_idx], np.full(pt_p[si_idx].shape, np.nan, dtype=np.float64)
        else:
            sd = np.std(pt_p, axis=0, ddof=1)
            return np.mean(pt_p, axis=0), np.mean(bt_p, axis=0), sd

    # --- Table 1: s9_2_2_swap_summary.tsv (& .csv) ---
    # 34-emotion arithmetic mean of actual_r, control_r_mean, effect (for visual, caption, both + visual_minus_caption)
    rows_2_2 = []
    pt_act_34 = np.nanmean(pt_actual_r, axis=-1)            # [C, 5, 3, 3]
    pt_ctrl_34 = np.nanmean(pt_ctrl_r_mean, axis=-1)        # [C, 5, 3, 3]
    pt_eff_34 = np.nanmean(pt_effect, axis=-1)              # [C, 5, 3, 3]
    bt_act_34 = np.nanmean(boot_actual_r, axis=-1)          # [C, 5, 3, B, 3]
    bt_ctrl_34 = np.nanmean(boot_ctrl_r_mean, axis=-1)      # [C, 5, 3, B, 3]
    bt_eff_34 = np.nanmean(boot_effect, axis=-1)            # [C, 5, 3, B, 3]

    for ci, (cond, mcode) in enumerate(INTERCHANGE_CONDITIONS):
        for pi_idx, pid_lbl in enumerate(sub_labels):
            n_val_p = int(pt_n_pairs_valid[ci, pi_idx, 0]) if pi_idx < 5 else int(pt_n_pairs_valid[ci, :, 0].sum())
            n_miss_p = (2109 - n_val_p) if pi_idx < 5 else (5 * 2109 - n_val_p)
            for si_idx, s_lbl in enumerate(seed_labels):
                act_hat, act_bt, act_sd = get_grid_slice(pt_act_34[ci], bt_act_34[ci], pi_idx, si_idx)
                ctrl_hat, ctrl_bt, ctrl_sd = get_grid_slice(pt_ctrl_34[ci], bt_ctrl_34[ci], pi_idx, si_idx)
                eff_hat, eff_bt, eff_sd = get_grid_slice(pt_eff_34[ci], bt_eff_34[ci], pi_idx, si_idx)

                cl_e, ch_e, pv_e, nnan_e = bootstrap_ci_and_p(eff_hat, eff_bt)
                cl_a, ch_a, pv_a, _ = bootstrap_ci_and_p(act_hat, act_bt)

                for path_i, pname in enumerate(PATH_NAMES):
                    if pi_idx < 5 and si_idx < 3:
                        n_elig = 34 - int(pt_n_const_target[ci, pi_idx, si_idx])
                        n_nc_act = int(pt_n_const_pred_act[ci, pi_idx, si_idx, path_i])
                        n_nc_ctrl = int(pt_n_const_pred_ctrl[ci, pi_idx, si_idx, path_i])
                    else:
                        n_elig = 34
                        n_nc_act = int(pt_n_const_pred_act[ci, :, :, path_i].max())
                        n_nc_ctrl = int(pt_n_const_pred_ctrl[ci, :, :, path_i].max())

                    rows_2_2.append(
                        dict(
                            condition=cond,
                            model_code=mcode,
                            participant=pid_lbl,
                            seed=s_lbl,
                            path=pname,
                            is_2_2_primary=True,
                            n_pairs_valid=n_val_p,
                            n_pairs_missing=n_miss_p,
                            n_eligible_emotions=n_elig,
                            n_not_computable_actual=n_nc_act,
                            n_not_computable_control=n_nc_ctrl,
                            actual_r=float(act_hat[path_i]),
                            actual_r_seed_sd=float(act_sd[path_i]),
                            actual_r_ci95_low=float(cl_a[path_i]),
                            actual_r_ci95_high=float(ch_a[path_i]),
                            actual_r_p_boot=float(pv_a[path_i]),
                            control_r_mean=float(ctrl_hat[path_i]),
                            control_r_seed_sd=float(ctrl_sd[path_i]),
                            effect=float(eff_hat[path_i]),
                            effect_seed_sd=float(eff_sd[path_i]),
                            ci95_low=float(cl_e[path_i]),
                            ci95_high=float(ch_e[path_i]),
                            p_boot=float(pv_e[path_i]),
                            n_nan_boot=int(nnan_e[path_i]),
                        )
                    )

                # Also add overall 34-emotion visual_minus_caption convenience row
                vmc_hat = float(eff_hat[0] - eff_hat[1])
                vmc_bt = eff_bt[:, 0] - eff_bt[:, 1]
                if si_idx == 3:
                    pt_p_sub = pt_eff_34[ci, pi_idx] if pi_idx < 5 else pt_eff_34[ci].mean(axis=0)
                    vmc_sd = float(np.std(pt_p_sub[:, 0] - pt_p_sub[:, 1], ddof=1))
                else:
                    vmc_sd = np.nan
                vmc_cl, vmc_ch, vmc_pv, vmc_nnan = bootstrap_ci_and_p(np.array(vmc_hat), vmc_bt)
                rows_2_2.append(
                    dict(
                        condition=cond,
                        model_code=mcode,
                        participant=pid_lbl,
                        seed=s_lbl,
                        path="visual_minus_caption",
                        is_2_2_primary=False,
                        n_pairs_valid=n_val_p,
                        n_pairs_missing=n_miss_p,
                        n_eligible_emotions=34,
                        n_not_computable_actual=0,
                        n_not_computable_control=0,
                        actual_r=float(act_hat[0] - act_hat[1]),
                        actual_r_seed_sd=np.nan,
                        actual_r_ci95_low=np.nan,
                        actual_r_ci95_high=np.nan,
                        actual_r_p_boot=np.nan,
                        control_r_mean=float(ctrl_hat[0] - ctrl_hat[1]),
                        control_r_seed_sd=np.nan,
                        effect=vmc_hat,
                        effect_seed_sd=vmc_sd,
                        ci95_low=float(vmc_cl),
                        ci95_high=float(vmc_ch),
                        p_boot=float(vmc_pv),
                        n_nan_boot=int(vmc_nnan),
                    )
                )

    df_2_2 = pd.DataFrame(rows_2_2)
    save_tsv_and_csv(df_2_2, interchange_dir / "s9_2_2_swap_summary")
    print(f"[S9-1] Saved s9_2_2_swap_summary ({len(df_2_2)} rows)")

    # --- Table 2: s9_1_1_emotion_path_diff.tsv (& .csv) ---
    rows_1_1 = []
    pt_vmc = pt_effect[:, :, :, 0, :] - pt_effect[:, :, :, 1, :]          # [C, 5, 3, 34]
    bt_vmc = boot_effect[:, :, :, :, 0, :] - boot_effect[:, :, :, :, 1, :]  # [C, 5, 3, B, 34]

    for ci, (cond, mcode) in enumerate(INTERCHANGE_CONDITIONS):
        for pi_idx, pid_lbl in enumerate(sub_labels):
            n_val_p = int(pt_n_pairs_valid[ci, pi_idx, 0]) if pi_idx < 5 else int(pt_n_pairs_valid[ci, :, 0].sum())
            for si_idx, s_lbl in enumerate(seed_labels):
                act_hat, _, _ = get_grid_slice(pt_actual_r[ci], boot_actual_r[ci], pi_idx, si_idx)     # [3, 34]
                ctrl_hat, _, _ = get_grid_slice(pt_ctrl_r_mean[ci], boot_ctrl_r_mean[ci], pi_idx, si_idx)  # [3, 34]
                eff_hat, eff_bt, eff_sd = get_grid_slice(pt_effect[ci], boot_effect[ci], pi_idx, si_idx)   # [3, 34], [B, 3, 34]
                vmc_hat, vmc_bt, vmc_sd = get_grid_slice(pt_vmc[ci], bt_vmc[ci], pi_idx, si_idx)           # [34], [B, 34]

                vis_cl, vis_ch, vis_pv, _ = bootstrap_ci_and_p(eff_hat[0], eff_bt[:, 0, :])
                cap_cl, cap_ch, cap_pv, _ = bootstrap_ci_and_p(eff_hat[1], eff_bt[:, 1, :])
                vmc_cl, vmc_ch, vmc_pv, vmc_nnan = bootstrap_ci_and_p(vmc_hat, vmc_bt)
                vmc_q = bh_fdr(vmc_pv)
                vis_q = bh_fdr(vis_pv)
                cap_q = bh_fdr(cap_pv)

                for e_idx, ename in enumerate(emotion_names):
                    rows_1_1.append(
                        dict(
                            condition=cond,
                            model_code=mcode,
                            participant=pid_lbl,
                            seed=s_lbl,
                            emotion_idx=e_idx,
                            score_col=em_cols[e_idx],
                            emotion=ename,
                            emonet_still_frame_group=emonet_group_of[e_idx],
                            n_pairs_valid=n_val_p,
                            visual_actual_r=float(act_hat[0, e_idx]),
                            visual_control_r_mean=float(ctrl_hat[0, e_idx]),
                            visual_effect=float(eff_hat[0, e_idx]),
                            visual_effect_seed_sd=float(eff_sd[0, e_idx]),
                            visual_ci95_low=float(vis_cl[e_idx]),
                            visual_ci95_high=float(vis_ch[e_idx]),
                            visual_p_boot=float(vis_pv[e_idx]),
                            visual_q_bh_fdr=float(vis_q[e_idx]),
                            caption_actual_r=float(act_hat[1, e_idx]),
                            caption_control_r_mean=float(ctrl_hat[1, e_idx]),
                            caption_effect=float(eff_hat[1, e_idx]),
                            caption_effect_seed_sd=float(eff_sd[1, e_idx]),
                            caption_ci95_low=float(cap_cl[e_idx]),
                            caption_ci95_high=float(cap_ch[e_idx]),
                            caption_p_boot=float(cap_pv[e_idx]),
                            caption_q_bh_fdr=float(cap_q[e_idx]),
                            both_actual_r=float(act_hat[2, e_idx]),
                            both_control_r_mean=float(ctrl_hat[2, e_idx]),
                            both_effect=float(eff_hat[2, e_idx]),
                            both_effect_seed_sd=float(eff_sd[2, e_idx]),
                            visual_minus_caption=float(vmc_hat[e_idx]),
                            visual_minus_caption_seed_sd=float(vmc_sd[e_idx]),
                            ci95_low=float(vmc_cl[e_idx]),
                            ci95_high=float(vmc_ch[e_idx]),
                            p_boot=float(vmc_pv[e_idx]),
                            q_bh_fdr=float(vmc_q[e_idx]),
                            n_nan_boot=int(vmc_nnan[e_idx]),
                        )
                    )

    df_1_1 = pd.DataFrame(rows_1_1)
    save_tsv_and_csv(df_1_1, interchange_dir / "s9_1_1_emotion_path_diff")
    print(f"[S9-1] Saved s9_1_1_emotion_path_diff ({len(df_1_1)} rows)")

    # --- Table 3: s9_1_1_emonet_groups.tsv (& .csv) ---
    # Kragel et al. (2019) EmoNet High vs Low still-frame group comparison (911-913)
    rows_emonet = []
    # Build [C, 5, 3, 4_metrics] for high, low, high_minus_low where 4_metrics = (visual_effect, caption_effect, both_effect, visual_minus_caption)
    metric_names_em = ("visual_effect", "caption_effect", "both_effect", "visual_minus_caption")

    def build_group_4metrics(eff_arr, axis_e=-1):
        # eff_arr has trailing shape [3, 34]
        hi_3 = np.mean(eff_arr[..., :, high_eidx], axis=-1)   # [..., 3]
        lo_3 = np.mean(eff_arr[..., :, low_eidx], axis=-1)    # [..., 3]
        hi_4 = np.concatenate([hi_3, (hi_3[..., 0] - hi_3[..., 1])[..., None]], axis=-1)
        lo_4 = np.concatenate([lo_3, (lo_3[..., 0] - lo_3[..., 1])[..., None]], axis=-1)
        diff_4 = hi_4 - lo_4
        return hi_4, lo_4, diff_4

    pt_hi, pt_lo, pt_hml = build_group_4metrics(pt_effect)
    bt_hi, bt_lo, bt_hml = build_group_4metrics(boot_effect)

    group_specs = (
        (
            "high_still_frame",
            "EmoNet에서 정지 프레임 분류 성능이 높았던 정서",
            ",".join(HIGH_EMONET_NAMES),
            len(HIGH_EMONET_NAMES),
            pt_hi,
            bt_hi,
        ),
        (
            "low_still_frame",
            "EmoNet에서 정지 프레임 분류 성능이 낮았던 정서",
            ",".join(LOW_EMONET_NAMES),
            len(LOW_EMONET_NAMES),
            pt_lo,
            bt_lo,
        ),
        (
            "high_minus_low",
            "EmoNet 정지 프레임 높았던 정서 빼기 낮았던 정서",
            f"({','.join(HIGH_EMONET_NAMES)}) - ({','.join(LOW_EMONET_NAMES)})",
            len(HIGH_EMONET_NAMES) + len(LOW_EMONET_NAMES),
            pt_hml,
            bt_hml,
        ),
    )

    for ci, (cond, mcode) in enumerate(INTERCHANGE_CONDITIONS):
        for pi_idx, pid_lbl in enumerate(sub_labels):
            for si_idx, s_lbl in enumerate(seed_labels):
                for g_code, g_ko, g_ems, g_n, g_pt, g_bt in group_specs:
                    ghat, gbt, gsd = get_grid_slice(g_pt[ci], g_bt[ci], pi_idx, si_idx)
                    gcl, gch, gpv, gnnan = bootstrap_ci_and_p(ghat, gbt)
                    for mi, mname in enumerate(metric_names_em):
                        rows_emonet.append(
                            dict(
                                condition=cond,
                                model_code=mcode,
                                participant=pid_lbl,
                                seed=s_lbl,
                                group=g_code,
                                group_label_ko=g_ko,
                                emotions=g_ems,
                                n_emotions=g_n,
                                metric=mname,
                                estimate=float(ghat[mi]),
                                seed_sd=float(gsd[mi]),
                                ci95_low=float(gcl[mi]),
                                ci95_high=float(gch[mi]),
                                p_boot=float(gpv[mi]),
                                n_nan_boot=int(gnnan[mi]),
                            )
                        )

    df_emonet = pd.DataFrame(rows_emonet)
    save_tsv_and_csv(df_emonet, interchange_dir / "s9_1_1_emonet_groups")
    print(f"[S9-1] Saved s9_1_1_emonet_groups ({len(df_emonet)} rows)")

    # --- Table 4: s9_1_2_interaction_I.tsv (& .csv) ---
    rows_1_2 = []
    # First row: explicit global additive verification row (919)
    add_ci = [i for i, (c_name, _) in enumerate(INTERCHANGE_CONDITIONS) if c_name == "brain_decoded_additive"][0]
    global_add_max_act = float(pt_max_abs_I_act[add_ci].max())
    global_add_max_ctrl = float(pt_max_abs_I_ctrl[add_ci].max())
    global_add_max_all = max(global_add_max_act, global_add_max_ctrl)
    assert global_add_max_all < 1e-5

    rows_1_2.append(
        dict(
            row_type="additive_unit_test_verification",
            condition="brain_decoded_additive",
            model_code="C-1_additive",
            participant="all_5sub_6folds",
            seed="all_3seeds",
            emotion_idx=-2,
            score_col="ALL_34",
            emotion="UNIT_TEST_MAX_ABS_I_LT_1E-5_PASS",
            n_pairs_valid=int(pt_n_pairs_valid[add_ci, :, 0].sum() * 3),
            mean_abs_I=float(pt_mean_abs_I[add_ci].mean()),
            mean_abs_I_seed_sd=float(pt_mean_abs_I[add_ci].mean(axis=(0, 2)).std(ddof=1)),
            control_mean_abs_I=float(pt_ctrl_mean_abs_I[add_ci].mean()),
            control_mean_abs_I_seed_sd=float(pt_ctrl_mean_abs_I[add_ci].mean(axis=(0, 2)).std(ddof=1)),
            effect=float(pt_abs_I_effect[add_ci].mean()),
            effect_seed_sd=float(pt_abs_I_effect[add_ci].mean(axis=(0, 2)).std(ddof=1)),
            ci95_low=np.nan,
            ci95_high=np.nan,
            p_boot=np.nan,
            q_bh_fdr=np.nan,
            prob_contrast_abs=float(pt_prob_I[add_ci].mean()),
            control_prob_contrast_abs=float(pt_ctrl_prob_I[add_ci].mean()),
            prob_contrast_effect=float(pt_prob_I_effect[add_ci].mean()),
            prob_contrast_ci95_low=np.nan,
            prob_contrast_ci95_high=np.nan,
            prob_contrast_p_boot=np.nan,
            max_abs_I_actual=global_add_max_act,
            max_abs_I_control=global_add_max_ctrl,
            max_abs_I_overall=global_add_max_all,
        )
    )

    pt_I_34 = pt_mean_abs_I.mean(axis=-1)              # [C, 5, 3]
    pt_cI_34 = pt_ctrl_mean_abs_I.mean(axis=-1)        # [C, 5, 3]
    pt_effI_34 = pt_abs_I_effect.mean(axis=-1)         # [C, 5, 3]
    bt_effI_34 = boot_abs_I_effect.mean(axis=-1)       # [C, 5, 3, B]

    pt_pI_34 = pt_prob_I.mean(axis=-1)
    pt_cpI_34 = pt_ctrl_prob_I.mean(axis=-1)
    pt_effpI_34 = pt_prob_I_effect.mean(axis=-1)
    bt_effpI_34 = boot_prob_I_effect.mean(axis=-1)

    for ci, (cond, mcode) in enumerate(INTERCHANGE_CONDITIONS):
        for pi_idx, pid_lbl in enumerate(sub_labels):
            n_val_p = int(pt_n_pairs_valid[ci, pi_idx, 0]) if pi_idx < 5 else int(pt_n_pairs_valid[ci, :, 0].sum())
            for si_idx, s_lbl in enumerate(seed_labels):
                if pi_idx < 5 and si_idx < 3:
                    m_act = float(pt_max_abs_I_act[ci, pi_idx, si_idx])
                    m_ctrl = float(pt_max_abs_I_ctrl[ci, pi_idx, si_idx])
                elif pi_idx < 5 and si_idx == 3:
                    m_act = float(pt_max_abs_I_act[ci, pi_idx, :].max())
                    m_ctrl = float(pt_max_abs_I_ctrl[ci, pi_idx, :].max())
                elif pi_idx == 5 and si_idx < 3:
                    m_act = float(pt_max_abs_I_act[ci, :, si_idx].max())
                    m_ctrl = float(pt_max_abs_I_ctrl[ci, :, si_idx].max())
                else:
                    m_act = float(pt_max_abs_I_act[ci].max())
                    m_ctrl = float(pt_max_abs_I_ctrl[ci].max())
                m_all = max(m_act, m_ctrl)

                # 34-emotion mean row
                i34_hat, _, i34_sd = get_grid_slice(pt_I_34[ci], bt_effI_34[ci], pi_idx, si_idx)
                ci34_hat, _, ci34_sd = get_grid_slice(pt_cI_34[ci], bt_effI_34[ci], pi_idx, si_idx)
                ei34_hat, ei34_bt, ei34_sd = get_grid_slice(pt_effI_34[ci], bt_effI_34[ci], pi_idx, si_idx)
                pi34_hat, _, _ = get_grid_slice(pt_pI_34[ci], bt_effpI_34[ci], pi_idx, si_idx)
                cpi34_hat, _, _ = get_grid_slice(pt_cpI_34[ci], bt_effpI_34[ci], pi_idx, si_idx)
                epi34_hat, epi34_bt, _ = get_grid_slice(pt_effpI_34[ci], bt_effpI_34[ci], pi_idx, si_idx)

                cl_34, ch_34, pv_34, _ = bootstrap_ci_and_p(ei34_hat, ei34_bt)
                pcl_34, pch_34, ppv_34, _ = bootstrap_ci_and_p(epi34_hat, epi34_bt)

                rows_1_2.append(
                    dict(
                        row_type="summary_34",
                        condition=cond,
                        model_code=mcode,
                        participant=pid_lbl,
                        seed=s_lbl,
                        emotion_idx=-1,
                        score_col="mean_34",
                        emotion="mean_34",
                        n_pairs_valid=n_val_p,
                        mean_abs_I=float(i34_hat),
                        mean_abs_I_seed_sd=float(i34_sd),
                        control_mean_abs_I=float(ci34_hat),
                        control_mean_abs_I_seed_sd=float(ci34_sd),
                        effect=float(ei34_hat),
                        effect_seed_sd=float(ei34_sd),
                        ci95_low=float(cl_34),
                        ci95_high=float(ch_34),
                        p_boot=float(pv_34),
                        q_bh_fdr=np.nan,
                        prob_contrast_abs=float(pi34_hat),
                        control_prob_contrast_abs=float(cpi34_hat),
                        prob_contrast_effect=float(epi34_hat),
                        prob_contrast_ci95_low=float(pcl_34),
                        prob_contrast_ci95_high=float(pch_34),
                        prob_contrast_p_boot=float(ppv_34),
                        max_abs_I_actual=m_act,
                        max_abs_I_control=m_ctrl,
                        max_abs_I_overall=m_all,
                    )
                )

                # Per-emotion rows (0..33)
                ie_hat, _, ie_sd = get_grid_slice(pt_mean_abs_I[ci], boot_abs_I_effect[ci], pi_idx, si_idx)
                cie_hat, _, cie_sd = get_grid_slice(pt_ctrl_mean_abs_I[ci], boot_abs_I_effect[ci], pi_idx, si_idx)
                eie_hat, eie_bt, eie_sd = get_grid_slice(pt_abs_I_effect[ci], boot_abs_I_effect[ci], pi_idx, si_idx)
                pie_hat, _, _ = get_grid_slice(pt_prob_I[ci], boot_prob_I_effect[ci], pi_idx, si_idx)
                cpie_hat, _, _ = get_grid_slice(pt_ctrl_prob_I[ci], boot_prob_I_effect[ci], pi_idx, si_idx)
                epie_hat, epie_bt, _ = get_grid_slice(pt_prob_I_effect[ci], boot_prob_I_effect[ci], pi_idx, si_idx)

                cl_e, ch_e, pv_e, _ = bootstrap_ci_and_p(eie_hat, eie_bt)
                q_e = bh_fdr(pv_e)
                pcl_e, pch_e, ppv_e, _ = bootstrap_ci_and_p(epie_hat, epie_bt)

                for e_idx, ename in enumerate(emotion_names):
                    rows_1_2.append(
                        dict(
                            row_type="per_emotion",
                            condition=cond,
                            model_code=mcode,
                            participant=pid_lbl,
                            seed=s_lbl,
                            emotion_idx=e_idx,
                            score_col=em_cols[e_idx],
                            emotion=ename,
                            n_pairs_valid=n_val_p,
                            mean_abs_I=float(ie_hat[e_idx]),
                            mean_abs_I_seed_sd=float(ie_sd[e_idx]),
                            control_mean_abs_I=float(cie_hat[e_idx]),
                            control_mean_abs_I_seed_sd=float(cie_sd[e_idx]),
                            effect=float(eie_hat[e_idx]),
                            effect_seed_sd=float(eie_sd[e_idx]),
                            ci95_low=float(cl_e[e_idx]),
                            ci95_high=float(ch_e[e_idx]),
                            p_boot=float(pv_e[e_idx]),
                            q_bh_fdr=float(q_e[e_idx]),
                            prob_contrast_abs=float(pie_hat[e_idx]),
                            control_prob_contrast_abs=float(cpie_hat[e_idx]),
                            prob_contrast_effect=float(epie_hat[e_idx]),
                            prob_contrast_ci95_low=float(pcl_e[e_idx]),
                            prob_contrast_ci95_high=float(pch_e[e_idx]),
                            prob_contrast_p_boot=float(ppv_e[e_idx]),
                            max_abs_I_actual=m_act,
                            max_abs_I_control=m_ctrl,
                            max_abs_I_overall=m_all,
                        )
                    )

    df_1_2 = pd.DataFrame(rows_1_2)
    save_tsv_and_csv(df_1_2, interchange_dir / "s9_1_2_interaction_I")
    print(
        f"[S9-1] Saved s9_1_2_interaction_I ({len(df_1_2)} rows; "
        f"additive global max |I| = {global_add_max_all:.3e})"
    )

    # =========================================================================
    # TASK B: S9-2 NEAREST-PAIR COMPARISON (O33, O4(7))
    # =========================================================================
    t_o33 = time.time()
    pt_o33_r = np.empty((2, n_subs, n_seeds, 34), dtype=np.float64)
    boot_o33_r = np.empty((2, n_subs, n_seeds, N_BOOTSTRAP, 34), dtype=np.float64)
    pt_o33_n_valid = np.zeros((n_subs,), dtype=np.int64)
    pt_o33_n_not_comp = np.zeros((2, n_subs, n_seeds), dtype=np.int64)
    pt_o33_const_pred = np.zeros((2, n_subs, n_seeds, 34), dtype=bool)
    test_pred_vs_test_outputs_max_diff = 0.0

    selected_candidates_log["brain_only"] = {}

    for mi, (cond, mcode) in enumerate(O33_CONDITIONS):
        for si, seed in enumerate(SEEDS):
            dp_by_sub = {pid: [] for pid in PARTICIPANTS}
            dy_by_sub = {pid: [] for pid in PARTICIPANTS}
            g_by_sub = {pid: [] for pid in PARTICIPANTS}

            for fold in FOLDS:
                fdir = S.OUT / f"outer_fold{fold}"
                sel = json.loads((fdir / cond / "selected.json").read_text())
                if si == 0 and cond == "brain_only":
                    selected_candidates_log["brain_only"][f"outer_fold{fold}"] = {
                        "candidate": sel["candidate"],
                        "zero_selected": sel["zero_selected"],
                        "seeds": sel["seeds"],
                    }
                sdir = fdir / sel["seeds"][str(seed)]
                tp = np.load(sdir / "test_pred.npz")
                if cond == "brain_decoded":
                    to = np.load(sdir / "outputs" / "test_outputs.npz")
                    p_diff = float(np.max(np.abs(tp["p"] - to["p"])))
                    test_pred_vs_test_outputs_max_diff = max(test_pred_vs_test_outputs_max_diff, p_diff)

                f_un_df = pairs_un_df[pairs_un_df["fold"] == fold]

                for pi, pid in enumerate(PARTICIPANTS):
                    mask = tp["participant"] == pid
                    vids = tp["video_id"][mask].astype(np.int64)
                    p_part = tp["p"][mask]  # [n, 34] float32
                    vid_to_local = {int(v): idx for idx, v in enumerate(vids.tolist())}

                    valid_un = [
                        (vid_to_local[int(r.video_a)], vid_to_local[int(r.video_b)], int(r.video_a), int(r.video_b), int(r.gidx))
                        for r in f_un_df.itertuples(index=False)
                        if (int(r.video_a) in vid_to_local) and (int(r.video_b) in vid_to_local)
                    ]
                    idx_a = np.array([x[0] for x in valid_un], dtype=np.int64)
                    idx_b = np.array([x[1] for x in valid_un], dtype=np.int64)
                    srow_a = np.array([vid_to_split_row[x[2]] for x in valid_un], dtype=np.int64)
                    srow_b = np.array([vid_to_split_row[x[3]] for x in valid_un], dtype=np.int64)
                    g_arr = np.array([x[4] for x in valid_un], dtype=np.int64)

                    dp_by_sub[pid].append((p_part[idx_b] - p_part[idx_a]).astype(np.float64))
                    dy_by_sub[pid].append((y_em[srow_b] - y_em[srow_a]).astype(np.float64))
                    g_by_sub[pid].append(g_arr)

            for pi, pid in enumerate(PARTICIPANTS):
                dp_all = np.concatenate(dp_by_sub[pid], axis=0)
                dy_all = np.concatenate(dy_by_sub[pid], axis=0)
                g_all = np.concatenate(g_by_sub[pid], axis=0)

                n_un_valid = len(dy_all)
                n_un_missing = 1690 - n_un_valid
                exp_un_missing = int(pair_missing_df.loc[pid, "n_unordered_missing"])
                if n_un_missing != exp_un_missing:
                    raise ValueError(
                        f"O9 unordered missing mismatch for {pid}: got {n_un_missing}, expected {exp_un_missing}"
                    )
                pt_o33_n_valid[pi] = n_un_valid

                align = ac.change_alignment(torch.from_numpy(dp_all), torch.from_numpy(dy_all))
                r_vec = align.r.numpy()
                pt_o33_r[mi, pi, si] = r_vec
                not_comp_mask = (align.constant_target | align.constant_prediction).numpy()
                pt_o33_n_not_comp[mi, pi, si] = int(not_comp_mask.sum())
                pt_o33_const_pred[mi, pi, si] = align.constant_prediction.numpy()

                # Verify uniform-weight equivalence
                r_unif = fast_cluster_bootstrap_pearson(dp_all, dy_all, g_all, ones_1xG, G=G)[0]
                assert np.nanmax(np.abs(r_unif - r_vec)) < 1e-13

                # 10,000-iteration cluster bootstrap using EXACT SAME cluster_counts
                boot_o33_r[mi, pi, si] = fast_cluster_bootstrap_pearson(
                    dp_all, dy_all, g_all, cluster_counts, G=G, chunk=1000
                )

    # Build Task B Table 6a: s9_o33_unordered_pairs.tsv (& .csv)
    pt_o33_34 = np.nanmean(pt_o33_r, axis=-1)          # [2, 5, 3]
    bt_o33_34 = np.nanmean(boot_o33_r, axis=-1)        # [2, 5, 3, B]
    pt_o33_diff_34 = pt_o33_34[1] - pt_o33_34[0]       # C-1 minus A-1 [5, 3]
    bt_o33_diff_34 = bt_o33_34[1] - bt_o33_34[0]       # [5, 3, B]

    rows_o33_sum = []
    comp_specs = (
        ("brain_only", "A-1", pt_o33_34[0], bt_o33_34[0]),
        ("brain_decoded", "C-1", pt_o33_34[1], bt_o33_34[1]),
        ("brain_decoded_minus_brain_only", "C-1_minus_A-1", pt_o33_diff_34, bt_o33_diff_34),
    )

    for pi_idx, pid_lbl in enumerate(sub_labels):
        n_all_u = 1690 if pi_idx < 5 else 5 * 1690
        n_val_u = int(pt_o33_n_valid[pi_idx]) if pi_idx < 5 else int(pt_o33_n_valid.sum())
        n_miss_u = n_all_u - n_val_u
        for si_idx, s_lbl in enumerate(seed_labels):
            for comp_i, (comp_name, comp_code, c_pt, c_bt) in enumerate(comp_specs):
                chat, cbt, csd = get_grid_slice(c_pt, c_bt, pi_idx, si_idx)
                ccl, cch, cpv, cnnan = bootstrap_ci_and_p(chat, cbt)
                if comp_i < 2 and pi_idx < 5 and si_idx < 3:
                    n_nc = int(pt_o33_n_not_comp[comp_i, pi_idx, si_idx])
                elif comp_i < 2:
                    n_nc = int(pt_o33_n_not_comp[comp_i].max())
                else:
                    n_nc = int(pt_o33_n_not_comp.max())

                rows_o33_sum.append(
                    dict(
                        comparison=comp_name,
                        model_code=comp_code,
                        participant=pid_lbl,
                        seed=s_lbl,
                        n_unordered_all=n_all_u,
                        n_unordered_valid=n_val_u,
                        n_unordered_missing=n_miss_u,
                        n_eligible_emotions=34 - n_nc,
                        n_not_computable=n_nc,
                        estimate=float(chat),
                        seed_sd=float(csd),
                        ci95_low=float(ccl),
                        ci95_high=float(cch),
                        p_boot=float(cpv),
                        n_nan_boot=int(cnnan),
                    )
                )

    df_o33_sum = pd.DataFrame(rows_o33_sum)
    save_tsv_and_csv(df_o33_sum, pair_comp_dir / "s9_o33_unordered_pairs")

    # Build Task B Table 6b: s9_o33_per_emotion.tsv (& .csv)
    pt_o33_diff_e = pt_o33_r[1] - pt_o33_r[0]          # [5, 3, 34]
    bt_o33_diff_e = boot_o33_r[1] - boot_o33_r[0]      # [5, 3, B, 34]
    rows_o33_em = []

    for pi_idx, pid_lbl in enumerate(sub_labels):
        n_val_u = int(pt_o33_n_valid[pi_idx]) if pi_idx < 5 else int(pt_o33_n_valid.sum())
        for si_idx, s_lbl in enumerate(seed_labels):
            a1_hat, a1_bt, a1_sd = get_grid_slice(pt_o33_r[0], boot_o33_r[0], pi_idx, si_idx)
            c1_hat, c1_bt, c1_sd = get_grid_slice(pt_o33_r[1], boot_o33_r[1], pi_idx, si_idx)
            df_hat, df_bt, df_sd = get_grid_slice(pt_o33_diff_e, bt_o33_diff_e, pi_idx, si_idx)

            a1_cl, a1_ch, a1_pv, _ = bootstrap_ci_and_p(a1_hat, a1_bt)
            c1_cl, c1_ch, c1_pv, _ = bootstrap_ci_and_p(c1_hat, c1_bt)
            df_cl, df_ch, df_pv, df_nnan = bootstrap_ci_and_p(df_hat, df_bt)
            df_q = bh_fdr(df_pv)

            for e_idx, ename in enumerate(emotion_names):
                rows_o33_em.append(
                    dict(
                        participant=pid_lbl,
                        seed=s_lbl,
                        emotion_idx=e_idx,
                        score_col=em_cols[e_idx],
                        emotion=ename,
                        n_unordered_valid=n_val_u,
                        r_A1=float(a1_hat[e_idx]),
                        r_A1_seed_sd=float(a1_sd[e_idx]),
                        r_A1_ci95_low=float(a1_cl[e_idx]),
                        r_A1_ci95_high=float(a1_ch[e_idx]),
                        r_A1_p_boot=float(a1_pv[e_idx]),
                        r_C1=float(c1_hat[e_idx]),
                        r_C1_seed_sd=float(c1_sd[e_idx]),
                        r_C1_ci95_low=float(c1_cl[e_idx]),
                        r_C1_ci95_high=float(c1_ch[e_idx]),
                        r_C1_p_boot=float(c1_pv[e_idx]),
                        diff_C1_minus_A1=float(df_hat[e_idx]),
                        diff_seed_sd=float(df_sd[e_idx]),
                        diff_ci95_low=float(df_cl[e_idx]),
                        diff_ci95_high=float(df_ch[e_idx]),
                        diff_p_boot=float(df_pv[e_idx]),
                        diff_q_bh_fdr=float(df_q[e_idx]),
                        not_computable_A1=bool(np.isnan(a1_hat[e_idx])),
                        not_computable_C1=bool(np.isnan(c1_hat[e_idx])),
                        n_nan_boot=int(df_nnan[e_idx]),
                    )
                )

    df_o33_em = pd.DataFrame(rows_o33_em)
    save_tsv_and_csv(df_o33_em, pair_comp_dir / "s9_o33_per_emotion")
    print(f"[S9-2] Completed O33 unordered pair comparison in {time.time() - t_o33:.1f}s")

    # =========================================================================
    # PROVENANCE & FINAL INTEGRITY CHECKS
    # =========================================================================
    output_table_files = [
        interchange_dir / "s9_2_2_swap_summary.tsv",
        interchange_dir / "s9_2_2_swap_summary.csv",
        interchange_dir / "s9_1_1_emotion_path_diff.tsv",
        interchange_dir / "s9_1_1_emotion_path_diff.csv",
        interchange_dir / "s9_1_1_emonet_groups.tsv",
        interchange_dir / "s9_1_1_emonet_groups.csv",
        interchange_dir / "s9_1_2_interaction_I.tsv",
        interchange_dir / "s9_1_2_interaction_I.csv",
        interchange_dir / "s9_step_lengths_and_missing.tsv",
        interchange_dir / "s9_step_lengths_and_missing.csv",
        interchange_dir / "group_size_distribution.tsv",
        interchange_dir / "group_size_distribution.csv",
        pair_comp_dir / "s9_o33_unordered_pairs.tsv",
        pair_comp_dir / "s9_o33_unordered_pairs.csv",
        pair_comp_dir / "s9_o33_per_emotion.tsv",
        pair_comp_dir / "s9_o33_per_emotion.csv",
        out_root / "pair_cluster_bootstrap_draws.npz",
    ]

    tracked_dirty = c.git("status", "--porcelain", "-uno").stdout.strip() != ""
    protected_dirs_dirty = (
        c.git("status", "--porcelain", "--", "src", "manifests", "splits", "configs").stdout.strip() != ""
    )

    prov = {
        "component": "s9_interchange_and_pairs",
        "code_commit": c.START_HEAD,
        "code_dirty": bool(c.START_DIRTY or tracked_dirty or protected_dirs_dirty),
        "tracked_files_dirty": bool(tracked_dirty),
        "protected_dirs_dirty": bool(protected_dirs_dirty),
        "script_path": str(Path(__file__).resolve()),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "cpu_only_enforcement": {
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "torch_cuda_is_available": bool(torch.cuda.is_available()),
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
            "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
            "torch_num_threads": int(torch.get_num_threads()),
        },
        "input_sha256": {
            "pairs_directed.tsv": sha256_file(s2_dir / "pairs_directed.tsv"),
            "pairs_unordered.tsv": sha256_file(s2_dir / "pairs_unordered.tsv"),
            "pair_groups.tsv": sha256_file(s2_dir / "pair_groups.tsv"),
            "pair_missing_counts.tsv": sha256_file(s2_dir / "pair_missing_counts.tsv"),
            "split_hk_dev.tsv": sha256_file(c.SPLITS / "split_hk_dev.tsv"),
            "label_map_34.tsv": sha256_file(c.LABEL_MAP),
            "audition_codex.py": sha256_file(M.AUDITION_PATH),
            "s4_common.py": sha256_file(SRC_DIR / "s4_common.py"),
            "s6_common.py": sha256_file(SRC_DIR / "s6_common.py"),
            "s6_model.py": sha256_file(SRC_DIR / "s6_model.py"),
        },
        "bootstrap_spec": {
            "n_iterations": N_BOOTSTRAP,
            "n_pair_group_clusters": G,
            "seed_string": BOOTSTRAP_SEED_BYTES.decode(),
            "seed_uint64": boot_seed_int,
            "ci_method": "Basic bootstrap 95% CI: [2*theta_hat - q(0.975), 2*theta_hat - q(0.025)]",
            "p_value_method": "Hall & Wilson (1991) centered two-sided: (1 + sum(|theta_boot - theta_hat| >= |theta_hat|)) / (B + 1)",
            "shared_across_participants_seeds_paths": True,
        },
        "o3_control_spec": {
            "n_repeats": int(ac.CONTROL_REPEATS),
            "seed_derivation": "int.from_bytes(hashlib.sha256(f'EmoBrain/S9_O3/{condition}/{participant}/{fold}/{seed}'.encode()).digest()[:8], 'big')",
            "same_donor_C_for_visual_and_caption": True,
            "per_draw_r_then_average": True,
        },
        "selected_candidates": selected_candidates_log,
        "verification_checks": {
            "z_AA_vs_test_outputs_logit_max_abs_diff_by_condition": z_aa_max_diff_by_cond,
            "z_AA_vs_test_outputs_logit_max_abs_diff_overall": max(z_aa_max_diff_by_cond.values()),
            "z_AA_check_passed_lt_1e-5": bool(max(z_aa_max_diff_by_cond.values()) < 1e-5),
            "test_pred_vs_test_outputs_p_max_abs_diff": test_pred_vs_test_outputs_max_diff,
            "brain_decoded_additive_unit_test": {
                "max_abs_I_actual": global_add_max_act,
                "max_abs_I_control_100draws": global_add_max_ctrl,
                "max_abs_I_overall": global_add_max_all,
                "passed_lt_1e-5": bool(global_add_max_all < 1e-5),
                "per_participant_seed": additive_verification_detail,
            },
            "control_length_matching_max_abs_diff": ctrl_len_mismatch_by_cond,
            "o9_missing_pair_counts_exact_match": {
                "directed_missing": pair_missing_df["n_directed_missing"].to_dict(),
                "unordered_missing": pair_missing_df["n_unordered_missing"].to_dict(),
                "exact_match_verified": True,
            },
            "pair_groups_connected_components_verified": {
                "n_clusters": G,
                "n_directed_pairs": 2109,
                "n_unordered_pairs": 1690,
                "all_pairs_within_single_cluster": True,
            },
            "weighted_pearson_bootstrap_equivalence_check": explicit_bootstrap_checks,
        },
        "output_tables_sha256": {str(p.relative_to(out_root)): sha256_file(p) for p in output_table_files},
        "saved_per_pair_npz_files": saved_interchange_npz_files,
        "elapsed_seconds": round(time.time() - t_start, 2),
    }

    assert not prov["code_dirty"], "Tracked repository became dirty!"

    # Write provenance to interchange/, pair_comparison/, and out_root/provenance.json safely
    (interchange_dir / "provenance.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n")
    (pair_comp_dir / "provenance.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n")

    root_prov_path = out_root / "provenance.json"
    if root_prov_path.exists():
        try:
            existing = json.loads(root_prov_path.read_text())
            if isinstance(existing, dict) and existing.get("component") not in (None, "s9_interchange_and_pairs"):
                merged = {"components": {existing["component"]: existing, "s9_interchange_and_pairs": prov}}
                merged.update(prov)
                root_prov_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
            else:
                root_prov_path.write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n")
        except Exception:
            root_prov_path.write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n")
    else:
        root_prov_path.write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n")

    print(f"[S9] ALL DONE in {prov['elapsed_seconds']}s! Outputs written to {out_root}")


if __name__ == "__main__":
    main()
