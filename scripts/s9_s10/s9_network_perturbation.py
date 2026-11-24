#!/usr/bin/env python3
"""S9-4: Network-Unit Input Perturbation (네트워크 단위 입력 교란, 6-4b, 2-4, O3, O4(3)).

Strict Operational Rules:
- CPU ONLY: CUDA_VISIBLE_DEVICES="", OMP/MKL/torch threads = 16, device = "cpu".
- Read-only access to /scratch/emobrain/code/ (never modifies tracked repo files).
- Outputs written atomically to /scratch/emobrain/outputs/s9_analysis/network_perturbation/.
"""
import os
import sys as _sys

_USE_SLURM_GPU = "--slurm-gpu" in _sys.argv
if _USE_SLURM_GPU:
    if not os.environ.get("SLURM_JOB_ID"):
        raise RuntimeError("--slurm-gpu is ONLY permitted inside a sanctioned Slurm job (sbatch/srun)!")
else:
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

os.environ.setdefault("OMP_NUM_THREADS", "16")
os.environ.setdefault("MKL_NUM_THREADS", "16")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "16")

import concurrent.futures
import copy as _copy
import hashlib
import json
import multiprocessing as mp
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch

torch.set_num_threads(16)
if _USE_SLURM_GPU:
    assert torch.cuda.is_available(), "Expected Slurm-allocated GPU!"
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    RUN_DEVICE = "cuda"
else:
    if torch.cuda.is_available():
        raise RuntimeError("CUDA must NOT be visible outside Slurm! Set CUDA_VISIBLE_DEVICES=''")
    RUN_DEVICE = "cpu"

_LOCAL_SRC = Path(__file__).resolve().parents[2] / "src"
CODE_SRC = _LOCAL_SRC if _LOCAL_SRC.is_dir() else Path("/scratch/emobrain/code/src")
sys.path.insert(0, str(CODE_SRC))

import paths as P
import s4_common as c
import s5_common as d5
import s6_common as S
import s6_model as M

OUT_DIR = Path("/scratch/emobrain/outputs/s9_analysis/network_perturbation")
CONDITIONS = ("brain_only", "brain_decoded")  # A-1, C-1 (interaction head)
SEEDS = (0, 1, 2)
N_FOLDS = 6
N_REPEATS = 20
N_BOOT = 10000
ALPHA = 0.05
VAR_EPS = 1e-24


def log(msg: str) -> None:
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{now}] {msg}", flush=True)


def check_repo_clean() -> str:
    res = subprocess.run(
        ["git", "-C", str(P.REPO), "status", "--porcelain", "--", "src", "manifests", "splits", "configs"],
        capture_output=True,
        text=True,
        check=True,
    )
    if res.stdout.strip():
        raise RuntimeError(f"Tracked repo directories have modifications:\n{res.stdout}")
    head = subprocess.run(
        ["git", "-C", str(P.REPO), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return head


def holm_adjust(p_vals: np.ndarray) -> np.ndarray:
    """Exact Holm-Bonferroni step-down adjusted p-values across family of length m."""
    p = np.asarray(p_vals, dtype=np.float64)
    if p.ndim != 1 or not np.isfinite(p).all():
        raise ValueError("Holm input p-values must be finite 1D array")
    m = len(p)
    order = np.argsort(p, kind="mergesort")
    adj = p[order] * (m - np.arange(m, dtype=np.float64))
    adj = np.maximum.accumulate(adj)
    adj = np.clip(adj, 0.0, 1.0)
    out = np.empty(m, dtype=np.float64)
    out[order] = adj
    return out


def bh_fdr_adjust(p_vals: np.ndarray) -> np.ndarray:
    """Exact Benjamini-Hochberg FDR q-values, handling NaNs by adjusting over finite entries."""
    p = np.asarray(p_vals, dtype=np.float64)
    out = np.full(p.shape, np.nan, dtype=np.float64)
    valid = np.flatnonzero(np.isfinite(p))
    m = len(valid)
    if m == 0:
        return out
    pv = p[valid]
    order = np.argsort(pv, kind="mergesort")
    adj = pv[order] * (m / np.arange(1, m + 1, dtype=np.float64))
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.clip(adj, 0.0, 1.0)
    tmp = np.empty(m, dtype=np.float64)
    tmp[order] = adj
    out[valid] = tmp
    return out


def boot_ci_and_p(theta: float, theta_boot: np.ndarray) -> tuple[float, float, float]:
    """O4(3): Basic 95% CI [2*theta - q(0.975), 2*theta - q(0.025)] and centered two-sided Hall & Wilson p-value."""
    if not np.isfinite(theta):
        return np.nan, np.nan, np.nan
    tb = np.asarray(theta_boot, dtype=np.float64)
    finite = tb[np.isfinite(tb)]
    if len(finite) != len(tb):
        raise ValueError(f"Bootstrap replicates contain {len(tb) - len(finite)} non-finite values")
    q025, q975 = np.quantile(tb, [0.025, 0.975])
    ci_low = float(2.0 * theta - q975)
    ci_high = float(2.0 * theta - q025)
    b_count = len(tb)
    exceed = int(np.sum(np.abs(tb - theta) >= np.abs(theta)))
    p_val = float((1 + exceed) / (b_count + 1))
    return ci_low, ci_high, p_val


def boot_ci_and_p_vec(theta: np.ndarray, theta_boot: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized O4(3) Basic 95% CI and Hall & Wilson p-value for 1D theta (E,) and theta_boot (B, E)."""
    theta = np.asarray(theta, dtype=np.float64)
    tb = np.asarray(theta_boot, dtype=np.float64)
    b_count, m = tb.shape
    ci_low = np.full(m, np.nan, dtype=np.float64)
    ci_high = np.full(m, np.nan, dtype=np.float64)
    p_val = np.full(m, np.nan, dtype=np.float64)
    for j in range(m):
        if np.isfinite(theta[j]) and np.isfinite(tb[:, j]).all():
            ci_low[j], ci_high[j], p_val[j] = boot_ci_and_p(float(theta[j]), tb[:, j])
    return ci_low, ci_high, p_val


def weighted_pearson_blas(
    W: np.ndarray,
    W_sum: np.ndarray,
    Y0: np.ndarray,
    Sw_Y: np.ndarray,
    SYY: np.ndarray,
    P_mat: np.ndarray,
) -> np.ndarray:
    """Exact multiplicity-weighted Pearson r via shifted BLAS dgemm.

    W: (B, N) float64 multiplicity weights
    W_sum: (B, 1) float64 row sums of W
    Y0: (N, 34) centered Y
    Sw_Y: (B, 34) W @ Y0
    SYY: (B, 34) sum_i w_i (y_i - y_bar_w)^2
    P_mat: (N, K * 34) float64 predictions
    Returns: (B, K, 34) float64 correlations (NaN if constant y or constant p).
    """
    n_rows, total_cols = P_mat.shape
    if total_cols % 34 != 0:
        raise ValueError(f"P_mat columns {total_cols} not divisible by 34")
    k_blocks = total_cols // 34
    P0 = P_mat - P_mat.mean(axis=0, keepdims=True)
    Y0_rep = Y0 if k_blocks == 1 else np.tile(Y0, (1, k_blocks))

    # Concatenate [P0, P0^2, P0*Y0_rep] so MKL executes ONE large dgemm
    Z = np.concatenate([P0, P0 * P0, P0 * Y0_rep], axis=1)
    WZ = W @ Z  # (B, 3 * total_cols)
    Sw_P = WZ[:, :total_cols]
    Sw_P2 = WZ[:, total_cols : 2 * total_cols]
    Sw_PY = WZ[:, 2 * total_cols :]

    Sw_Y_rep = Sw_Y if k_blocks == 1 else np.tile(Sw_Y, (1, k_blocks))
    SYY_rep = SYY if k_blocks == 1 else np.tile(SYY, (1, k_blocks))

    SPP = Sw_P2 - (Sw_P * Sw_P) / W_sum
    SPY = Sw_PY - (Sw_P * Sw_Y_rep) / W_sum

    valid = (SPP > VAR_EPS) & (SYY_rep > VAR_EPS)
    den = np.sqrt(np.where(valid, SPP * SYY_rep, 1.0))
    r_flat = np.where(valid, SPY / den, np.nan)
    return r_flat.reshape(W.shape[0], k_blocks, 34)


def run_unit_self_tests() -> dict:
    """Verify Holm-13 and BH-FDR formulas on known reference cases."""
    p_test = np.array([0.001, 0.01, 0.04, 0.20, 0.50])
    h_exp = np.array([0.005, 0.04, 0.12, 0.40, 0.50])
    bh_exp = np.array([0.005, 0.025, 0.06666666666666667, 0.25, 0.50])
    assert np.max(np.abs(holm_adjust(p_test) - h_exp)) < 1e-15
    assert np.max(np.abs(bh_fdr_adjust(p_test) - bh_exp)) < 1e-15
    return {"holm_bh_unit_test": "passed"}


def _eval_single_checkpoint_worker(task: dict) -> dict:
    """Evaluate one (fold, cond, seed) checkpoint in IEEE-754 FP32."""
    dev = str(task.get("device", "cpu"))
    if dev == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        os.environ["OMP_NUM_THREADS"] = "6"
        os.environ["MKL_NUM_THREADS"] = "6"
        os.environ["OPENBLAS_NUM_THREADS"] = "6"
        torch.set_num_threads(6)

    k = int(task["k"])
    c_idx = int(task["c_idx"])
    cond = str(task["cond"])
    s_idx = int(task["s_idx"])
    seed = int(task["seed"])
    ckpt_path = Path(task["ckpt_path"])
    out_npz_path = Path(task["out_npz_path"])
    fold_cache_path = Path(task["fold_cache_path"])
    roi_indices_list = task["roi_indices_list"]
    default_g_idx = int(task["default_g_idx"])
    participants = task["participants"]

    t_start = time.time()
    fc = torch.load(fold_cache_path, map_location="cpu", weights_only=False)
    xs_dict = {kp: vp.to(dev) for kp, vp in fc["xs_dict"].items()}
    pos_dict = {kp: vp.to(dev) for kp, vp in fc["pos_dict"].items()}
    n_test_fold = int(fc["n_test_fold"])
    row_part = fc["row_part"]
    row_vid = fc["row_vid"]
    xs_vid_order = fc["xs_vid_order"]
    donor_batch_idx = fc["donor_batch_idx"].to(dev)
    part_fold_slices = fc["part_fold_slices"]
    donor_map_k = fc["donor_map_k"]

    test_batch = M.BrainBatch(xs_dict, pos_dict, n_test_fold)
    roi_idx_tensors = [torch.as_tensor(arr, dtype=torch.long, device=dev) for arr in roi_indices_list]

    ckpt_hashes = {
        f"outer_fold{k}/{task['rel']}/model.pt": c.sha256(ckpt_path),
        f"outer_fold{k}/{task['rel']}/outputs/test_outputs.npz": c.sha256(out_npz_path),
    }

    model, _ = M.load_checkpoint(ckpt_path, device=dev)
    model.eval()
    if model.spec.get("tokenizer", "linear") != "linear":
        raise RuntimeError(f"Unexpected tokenizer in {ckpt_path}: {model.spec.get('tokenizer')}")

    sanity2_res = None
    with torch.no_grad():
        T = model.input_layer(test_batch)  # (N_test_fold, 370, d)
        p_unpert = model.readout(model.encoder(T)).p.detach().cpu().numpy()

        saved_out = np.load(out_npz_path)
        saved_map = {
            (str(p), int(v)): row_p
            for p, v, row_p in zip(saved_out["participant"], saved_out["video_id"], saved_out["p"])
        }
        assert len(saved_map) == n_test_fold
        p_saved_aligned = np.stack([saved_map[(str(p), int(v))] for p, v in zip(row_part, row_vid)], axis=0)
        abs_d1 = np.abs(p_unpert - p_saved_aligned)
        diff1_max = float(np.max(abs_d1))
        diff1_mean = float(np.mean(abs_d1))
        diff1_p99 = float(np.quantile(abs_d1, 0.99))

        fp64_cpu_diff = None
        if k == 1 and seed == 0 and cond == "brain_only":
            m64 = _copy.deepcopy(model).double()
            xs64 = {kp: vp.double() for kp, vp in test_batch.xs.items()}
            p64 = m64(M.BrainBatch(xs64, test_batch.positions, test_batch.n)).p.detach().cpu().numpy()
            fp64_cpu_diff = float(np.max(np.abs(p_unpert - p64)))
            assert fp64_cpu_diff < 1e-6, f"IEEE FP32 vs FP64 diff too large: {fp64_cpu_diff}"
            del m64, xs64

        sanity1_res = {
            "max_abs_diff_gpu_tf32_vs_cpu_fp32": diff1_max,
            "mean_abs_diff": diff1_mean,
            "p99_abs_diff": diff1_p99,
            **({"cpu_fp32_vs_cpu_fp64_max_abs_diff": fp64_cpu_diff} if fp64_cpu_diff is not None else {}),
        }
        if diff1_mean >= 1e-5 or diff1_max >= 5e-4:
            raise AssertionError(
                f"Sanity Check 1 FAILED on fold{k} {cond} seed{seed}: mean={diff1_mean}, max={diff1_max}"
            )

        if k == 1 and seed == 0:
            r_def = roi_indices_list[default_g_idx]
            r_def_t = roi_idx_tensors[default_g_idx]
            bounds_01 = model.input_layer.bounds["sub-01"]
            vids_01_xs = xs_vid_order["sub-01"]
            vid_to_xs01 = {int(v): i for i, v in enumerate(vids_01_xs.tolist())}
            vids_sorted_01, donor_vids_01 = donor_map_k["sub-01"]
            rec_to_don_01 = {
                int(rv): int(dv) for rv, dv in zip(vids_sorted_01.tolist(), donor_vids_01[0].tolist())
            }
            donor_xs01_idx = torch.as_tensor(
                [vid_to_xs01[rec_to_don_01[int(v)]] for v in vids_01_xs.tolist()],
                dtype=torch.long,
                device=dev,
            )
            xs_raw_pert = {p: x.clone() for p, x in test_batch.xs.items()}
            for r_id in r_def.tolist():
                b0, b1 = bounds_01[r_id], bounds_01[r_id + 1]
                xs_raw_pert["sub-01"][:, b0:b1] = test_batch.xs["sub-01"][donor_xs01_idx, b0:b1]
            p_from_raw = model(M.BrainBatch(xs_raw_pert, test_batch.positions, test_batch.n)).p.detach().cpu().numpy()

            at_01 = torch.as_tensor(part_fold_slices["sub-01"][0], dtype=torch.long, device=dev)
            don_global_01 = donor_batch_idx[0, at_01]
            T_tok_pert = T.clone()
            T_tok_pert[at_01[:, None], r_def_t[None, :], :] = T[don_global_01[:, None], r_def_t[None, :], :]
            p_from_tok = model.readout(model.encoder(T_tok_pert)).p.detach().cpu().numpy()
            diff2_sub01 = float(np.max(np.abs(p_from_raw - p_from_tok)))

            xs_raw_all = {p: x.clone() for p, x in test_batch.xs.items()}
            for pid_c in participants:
                bounds_p = model.input_layer.bounds[pid_c]
                vids_px = xs_vid_order[pid_c]
                vid_to_px = {int(v): i for i, v in enumerate(vids_px.tolist())}
                vs_p, dv_p = donor_map_k[pid_c]
                r2d_p = {int(rv): int(dv) for rv, dv in zip(vs_p.tolist(), dv_p[0].tolist())}
                don_px = torch.as_tensor([vid_to_px[r2d_p[int(v)]] for v in vids_px.tolist()], dtype=torch.long, device=dev)
                for r_id in r_def.tolist():
                    b0, b1 = bounds_p[r_id], bounds_p[r_id + 1]
                    xs_raw_all[pid_c][:, b0:b1] = test_batch.xs[pid_c][don_px, b0:b1]
            p_raw_all = model(M.BrainBatch(xs_raw_all, test_batch.positions, test_batch.n)).p.detach().cpu().numpy()
            T_all_pert = T.clone()
            T_all_pert[:, r_def_t, :] = T.index_select(0, donor_batch_idx[0])[:, r_def_t, :]
            p_tok_all = model.readout(model.encoder(T_all_pert)).p.detach().cpu().numpy()
            diff2_all5 = float(np.max(np.abs(p_raw_all - p_tok_all)))

            sanity2_res = {
                "sub01_only_max_abs_diff": diff2_sub01,
                "all5_simultaneous_max_abs_diff": diff2_all5,
            }
            if diff2_sub01 >= 1e-6 or diff2_all5 >= 1e-6:
                raise AssertionError(
                    f"Sanity Check 2 FAILED on {cond}: sub01={diff2_sub01}, all5={diff2_all5}"
                )

        p_orig_by_pid = {}
        p_pert_by_pid = {
            pid: np.empty((len(roi_idx_tensors), N_REPEATS, len(part_fold_slices[pid][0]), 34), dtype=np.float32)
            for pid in participants
        }
        for pid in participants:
            at, _ = part_fold_slices[pid]
            p_orig_by_pid[pid] = p_unpert[at].astype(np.float32)

        T_pert = T.clone()
        for g_idx, r_idx_t in enumerate(roi_idx_tensors):
            orig_slice = T[:, r_idx_t, :].clone()
            for rep in range(N_REPEATS):
                T_pert[:, r_idx_t, :] = orig_slice.index_select(0, donor_batch_idx[rep])
                p_rep = model.readout(model.encoder(T_pert)).p.detach().cpu().numpy()
                for pid in participants:
                    at, _ = part_fold_slices[pid]
                    p_pert_by_pid[pid][g_idx, rep] = p_rep[at]
            T_pert[:, r_idx_t, :] = orig_slice
            if not torch.equal(T_pert, T):
                raise RuntimeError("T_pert restoration drift detected!")

    return {
        "k": k,
        "c_idx": c_idx,
        "cond": cond,
        "s_idx": s_idx,
        "seed": seed,
        "elapsed": round(time.time() - t_start, 2),
        "part_dest": {pid: part_fold_slices[pid][1] for pid in participants},
        "p_orig_by_pid": p_orig_by_pid,
        "p_pert_by_pid": p_pert_by_pid,
        "sanity1_key": f"fold{k}:{cond}:seed{seed}",
        "sanity1_res": sanity1_res,
        "sanity2_res": sanity2_res,
        "ckpt_hashes": ckpt_hashes,
    }


def main() -> None:
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    git_head = check_repo_clean()
    unit_checks = run_unit_self_tests()
    log(f"Starting S9-4 Network-Unit Input Perturbation on CPU (git HEAD={git_head})")

    # 1. Load manifests, splits, labels, and all 5 participants' brain sets
    cabnp_path = P.S2 / "cabnp_groups.tsv"
    roi_table_path = P.S2 / "roi_table.tsv"
    agree_path = P.S2 / "agreement_hk_13groups.tsv"
    label_map_path = P.S1 / "label_map_34.tsv"

    cabnp_df = pd.read_csv(cabnp_path, sep="\t")
    roi_df = pd.read_csv(roi_table_path, sep="\t")
    agree_df = pd.read_csv(agree_path, sep="\t")
    label_df = pd.read_csv(label_map_path, sep="\t")

    assert len(cabnp_df) == 13, f"Expected 13 CAB-NP groups, got {len(cabnp_df)}"
    assert len(roi_df) == 370 and np.array_equal(roi_df.roi_index.to_numpy(), np.arange(370))
    assert set(cabnp_df.group) == set(roi_df.group) == set(agree_df.group)

    # Merge agreement into cabnp_df preserving cabnp_groups.tsv canonical order
    groups_meta = cabnp_df.merge(
        agree_df[["group", "median", "min", "max", "count"]].rename(
            columns={
                "median": "median_agreement",
                "min": "min_agreement",
                "max": "max_agreement",
                "count": "agreement_roi_count",
            }
        ),
        on="group",
        how="left",
        validate="one_to_one",
    )
    assert (groups_meta["n_roi"] == groups_meta["agreement_roi_count"]).all()
    groups_meta["group_kind"] = np.where(
        groups_meta["group"] == "Subcortex",
        "anatomical_subcortex",
        "cortical_network",
    )

    group_names = groups_meta["group"].tolist()
    group_ko_map = dict(zip(groups_meta["group"], groups_meta["group_ko"]))
    roi_indices_by_group = {}
    for g in group_names:
        sub = roi_df[roi_df["group"] == g]
        idxs = np.sort(sub["roi_index"].to_numpy(dtype=np.int64))
        roi_indices_by_group[g] = idxs
    all_covered = np.sort(np.concatenate(list(roi_indices_by_group.values())))
    assert np.array_equal(all_covered, np.arange(370)), "13 groups must partition 0..369 exactly"

    split = c.load_split()
    y_all, emo_score_cols = c.load_scores(split, "emotions")
    assert emo_score_cols == label_df["score_col"].tolist()
    emotion_names = label_df["name"].tolist()
    vid_to_split_pos = {int(v): i for i, v in enumerate(split.video_id.tolist())}

    log("Loading 5 participants' allowed dev brain responses (CPU, read-only)...")
    brains_all = S.load_brains(split, split.video_id.tolist())
    participants = sorted(brains_all.keys())  # ['sub-01', ..., 'sub-05']
    assert participants == [f"sub-{s}" for s in d5.HK]

    # Verify ROI names match roi_table.tsv and compute voxel counts per participant x group
    voxels_by_part_group = {pid: {} for pid in participants}
    unique_voxels_by_part_group = {pid: {} for pid in participants}
    for s in d5.HK:
        pid = f"sub-{s}"
        with np.load(d5.roi_path(s)) as z:
            roi_names = z["roi"].tolist()
        assert roi_names == roi_df["roi"].tolist(), f"{pid} ROI order != roi_table.tsv"
        b = brains_all[pid]
        for g in group_names:
            r_idxs = roi_indices_by_group[g]
            pos_list = [b.roi_positions[int(r)] for r in r_idxs]
            voxels_by_part_group[pid][g] = int(sum(len(p) for p in pos_list))
            unique_voxels_by_part_group[pid][g] = int(len(np.unique(np.concatenate(pos_list))))

    # 2. Mandatory Sanity Check 0: standardization.npz vs S.prepare_fold & S.voxel_standardizer
    log("Running Sanity Check 0: verifying standardization.npz == S.prepare_fold to 0.0 exact equality...")
    plan1 = S.load_plan("outer_fold1", split)
    lin = np.linspace(-1.0, 1.0, len(split), dtype=np.float32)[:, None]
    fd1 = S.prepare_fold(
        brains_all,
        split,
        y_all,
        np.broadcast_to(lin, (len(split), M.VISUAL_DIM)).copy(),
        np.broadcast_to(lin, (len(split), M.CAPTION_DIM)).copy(),
        plan1,
        device="cpu",
    )
    batch_fd1 = fd1.batch(fd1.rows("test"))
    std1 = np.load(S.OUT / "outer_fold1/plan/standardization.npz")
    sanity0_fold1_diffs = {}
    for pid in participants:
        b = brains_all[pid]
        te_rows = b.rows(plan1.test)
        m, sd, cst = std1[f"voxel_mean:{pid}"], std1[f"voxel_std:{pid}"], std1[f"voxel_constant:{pid}"]
        z = (np.asarray(b.X[te_rows], np.float64) - m) / sd
        z[:, cst] = 0.0
        cols = np.concatenate(b.roi_positions)
        x_fast = z.astype(np.float32)[:, cols]
        diff = float(np.max(np.abs(x_fast - batch_fd1.xs[pid].numpy())))
        sanity0_fold1_diffs[pid] = diff
        if diff != 0.0:
            raise AssertionError(f"Sanity Check 0 failed on {pid}: max_abs_diff={diff}")
    del fd1, batch_fd1

    sanity0_all_folds_std_diff = 0.0
    for k in range(1, N_FOLDS + 1):
        pk = S.load_plan(f"outer_fold{k}", split)
        std_k = np.load(S.OUT / f"outer_fold{k}/plan/standardization.npz")
        for pid in participants:
            b = brains_all[pid]
            tr_rows = b.rows(pk.train)
            m, sd, cst = S.voxel_standardizer(b.X[tr_rows])
            d_m = float(np.max(np.abs(m - std_k[f"voxel_mean:{pid}"])))
            d_s = float(np.max(np.abs(sd - std_k[f"voxel_std:{pid}"])))
            sanity0_all_folds_std_diff = max(sanity0_all_folds_std_diff, d_m, d_s)
            assert d_m == 0.0 and d_s == 0.0 and np.array_equal(cst, std_k[f"voxel_constant:{pid}"])
    log(f"Sanity Check 0 PASSED: max_abs_diff = 0.0 across outer_fold1..6!")

    # 3. Build Shared 20-Repeat Donor Assignment Table (O3)
    log("Generating deterministic 20-repeat donor assignment table (O3)...")
    donor_seeds_meta = {}
    donor_rows_records = []
    donor_map = {}  # (k, pid) -> (sorted_vids, donor_vids_20_by_n)

    for k in range(1, N_FOLDS + 1):
        pk = S.load_plan(f"outer_fold{k}", split)
        for pid in participants:
            b = brains_all[pid]
            vids = np.sort(b.video_id[b.rows(pk.test)].astype(np.int64))
            n = len(vids)
            if n < 2:
                raise ValueError(f"Fold {k} {pid}: insufficient test videos ({n})")
            seed_label = f"EmoBrain/S9_6_4b/donor/{pid}/fold{k}"
            seed_int = int.from_bytes(hashlib.sha256(seed_label.encode()).digest()[:8], "big")
            donor_seeds_meta[f"fold{k}:{pid}"] = {
                "seed_string": seed_label,
                "seed_uint64": seed_int,
                "n_test_videos": int(n),
            }
            rng = np.random.default_rng(seed_int)
            raw = rng.integers(0, n - 1, size=(N_REPEATS, n))
            donor_local = np.where(raw >= np.arange(n)[None, :], raw + 1, raw)
            assert (donor_local != np.arange(n)[None, :]).all()
            assert (donor_local >= 0).all() and (donor_local < n).all()
            donor_vids = vids[donor_local]
            donor_map[(k, pid)] = (vids, donor_vids)

            # Append records for donor_assignments.tsv
            fold_col = np.full(N_REPEATS * n, k, dtype=np.int64)
            rep_col = np.repeat(np.arange(N_REPEATS, dtype=np.int64), n)
            rec_col = np.tile(vids, N_REPEATS)
            don_col = donor_vids.reshape(-1)
            donor_rows_records.append(
                pd.DataFrame(
                    {
                        "fold": fold_col,
                        "participant": pid,
                        "repeat": rep_col,
                        "recipient_video_id": rec_col,
                        "donor_video_id": don_col,
                    }
                )
            )

    donor_df = pd.concat(donor_rows_records, ignore_index=True)
    assert (donor_df["recipient_video_id"] != donor_df["donor_video_id"]).all()
    log(f"Donor table built: {len(donor_df)} rows ({N_REPEATS} repeats x {len(donor_df) // N_REPEATS} test rows).")

    # Prepare pooled storage per participant (sorted video_ids across all 6 folds)
    part_vids_sorted = {}
    part_vid_to_pos = {}
    part_Y = {}
    for pid in participants:
        vids_all = np.sort(brains_all[pid].video_id.astype(np.int64))
        # Verify union of 6 outer test folds equals vids_all
        from_folds = np.sort(np.concatenate([donor_map[(k, pid)][0] for k in range(1, N_FOLDS + 1)]))
        assert np.array_equal(vids_all, from_folds), f"{pid}: pooled fold test videos != allowed dev videos"
        part_vids_sorted[pid] = vids_all
        part_vid_to_pos[pid] = {int(v): idx for idx, v in enumerate(vids_all.tolist())}
        part_Y[pid] = np.asarray(y_all[[vid_to_split_pos[int(v)] for v in vids_all]], dtype=np.float64)

    # Pooled prediction arrays:
    # P_orig[pid]: (2, 3, N_s, 34) float32
    # P_pert[pid]: (2, 3, 13, 20, N_s, 34) float32
    P_orig = {
        pid: np.full((len(CONDITIONS), len(SEEDS), len(part_vids_sorted[pid]), 34), np.nan, dtype=np.float32)
        for pid in participants
    }
    P_pert = {
        pid: np.full(
            (len(CONDITIONS), len(SEEDS), len(group_names), N_REPEATS, len(part_vids_sorted[pid]), 34),
            np.nan,
            dtype=np.float32,
        )
        for pid in participants
    }

    # 4. Run Checkpoints Across All 6 Folds x 2 Conditions x 3 Seeds (with Sanity Checks 1 & 2)
    roi_idx_tensors = [torch.as_tensor(roi_indices_by_group[g], dtype=torch.long) for g in group_names]
    default_g_idx = group_names.index("Default")
    sanity1_diffs = {}
    sanity2_diffs = {}
    input_hashes = {
        "cabnp_groups.tsv": c.sha256(cabnp_path),
        "roi_table.tsv": c.sha256(roi_table_path),
        "agreement_hk_13groups.tsv": c.sha256(agree_path),
        "label_map_34.tsv": c.sha256(label_map_path),
        "split_hk_dev.tsv": c.sha256(P.SPLITS / "split_hk_dev.tsv"),
        "labels": c.sha256(c.LABELS),
    }
    selected_candidates_meta = {}

    log("Preparing 6 fold test batches and running 36 checkpoints across 18 CPU spawn workers (6 threads each, zero GPU)...")
    t_fwd = time.time()
    tmp_cache_dir = OUT_DIR / "_tmp_fold_batches"
    tmp_cache_dir.mkdir(parents=True, exist_ok=True)
    roi_indices_list = [roi_indices_by_group[g] for g in group_names]
    tasks = []

    try:
        for k in range(1, N_FOLDS + 1):
            std_k = np.load(S.OUT / f"outer_fold{k}/plan/standardization.npz")
            rows_npz = np.load(S.OUT / f"outer_fold{k}/plan/rows.npz")
            te_mask = rows_npz["role"] == 2
            row_part = rows_npz["participant"][te_mask].astype(str)
            row_vid = rows_npz["video_id"][te_mask].astype(np.int64)
            n_test_fold = len(row_vid)

            xs_dict, pos_dict = {}, {}
            xs_vid_order = {}
            for pid in participants:
                at = np.flatnonzero(row_part == pid)
                b = brains_all[pid]
                vid_to_b_row = {int(v): r_i for r_i, v in enumerate(b.video_id.tolist())}
                b_rows = np.array([vid_to_b_row[int(v)] for v in row_vid[at]], dtype=np.int64)
                m, sd, cst = std_k[f"voxel_mean:{pid}"], std_k[f"voxel_std:{pid}"], std_k[f"voxel_constant:{pid}"]
                z = (np.asarray(b.X[b_rows], np.float64) - m) / sd
                z[:, cst] = 0.0
                cols = np.concatenate(b.roi_positions)
                xs_dict[pid] = torch.as_tensor(z.astype(np.float32)[:, cols], device="cpu")
                pos_dict[pid] = torch.as_tensor(at, dtype=torch.long, device="cpu")
                xs_vid_order[pid] = row_vid[at]

            global_pos = {(str(p), int(v)): idx for idx, (p, v) in enumerate(zip(row_part, row_vid))}
            donor_batch_idx_np = np.empty((N_REPEATS, n_test_fold), dtype=np.int64)
            for pid in participants:
                vids_sorted, donor_vids = donor_map[(k, pid)]
                for local_i, v in enumerate(vids_sorted.tolist()):
                    g_rec = global_pos[(pid, int(v))]
                    for rep in range(N_REPEATS):
                        d_vid = int(donor_vids[rep, local_i])
                        donor_batch_idx_np[rep, g_rec] = global_pos[(pid, d_vid)]

            for rep in range(N_REPEATS):
                idx_rep = donor_batch_idx_np[rep]
                assert np.array_equal(row_part[idx_rep], row_part), "Donor crossed participant boundary!"
                assert (row_vid[idx_rep] != row_vid).all(), "Self-donor detected!"
            donor_batch_idx = torch.as_tensor(donor_batch_idx_np, dtype=torch.long, device="cpu")

            part_fold_slices = {}
            for pid in participants:
                at = np.flatnonzero(row_part == pid)
                dest = np.array([part_vid_to_pos[pid][int(v)] for v in row_vid[at]], dtype=np.int64)
                part_fold_slices[pid] = (at, dest)

            fold_cache_path = tmp_cache_dir / f"fold{k}_test_batch.pt"
            torch.save(
                {
                    "xs_dict": xs_dict,
                    "pos_dict": pos_dict,
                    "n_test_fold": n_test_fold,
                    "row_part": row_part,
                    "row_vid": row_vid,
                    "xs_vid_order": xs_vid_order,
                    "donor_batch_idx": donor_batch_idx,
                    "part_fold_slices": part_fold_slices,
                    "donor_map_k": {pid: donor_map[(k, pid)] for pid in participants},
                },
                fold_cache_path,
            )

            for c_idx, cond in enumerate(CONDITIONS):
                sel_path = S.OUT / f"outer_fold{k}/{cond}/selected.json"
                input_hashes[f"outer_fold{k}/{cond}/selected.json"] = c.sha256(sel_path)
                sel = json.loads(sel_path.read_text())
                selected_candidates_meta[f"outer_fold{k}:{cond}"] = sel["candidate"]
                for s_idx, seed in enumerate(SEEDS):
                    rel = sel["seeds"][str(seed)]
                    ckpt_path = S.OUT / f"outer_fold{k}/{rel}/model.pt"
                    out_npz_path = S.OUT / f"outer_fold{k}/{rel}/outputs/test_outputs.npz"
                    tasks.append(
                        {
                            "k": k,
                            "c_idx": c_idx,
                            "cond": cond,
                            "s_idx": s_idx,
                            "seed": seed,
                            "rel": rel,
                            "ckpt_path": str(ckpt_path),
                            "out_npz_path": str(out_npz_path),
                            "fold_cache_path": str(fold_cache_path),
                            "roi_indices_list": roi_indices_list,
                            "default_g_idx": default_g_idx,
                            "participants": participants,
                            "device": RUN_DEVICE,
                        }
                    )

        assert len(tasks) == 36
        done_cnt = 0

        def _ingest_result(res: dict) -> None:
            nonlocal done_cnt
            done_cnt += 1
            k_r = res["k"]
            c_i = res["c_idx"]
            s_i = res["s_idx"]
            cond_r = res["cond"]
            sanity1_diffs[res["sanity1_key"]] = res["sanity1_res"]
            if res["sanity2_res"] is not None:
                sanity2_diffs[cond_r] = res["sanity2_res"]
            input_hashes.update(res["ckpt_hashes"])
            for pid in participants:
                dest = res["part_dest"][pid]
                P_orig[pid][c_i, s_i, dest, :] = res["p_orig_by_pid"][pid]
                pert_arr = res["p_pert_by_pid"][pid]  # (13, 20, len(dest), 34)
                for g_ii in range(pert_arr.shape[0]):
                    for r_ii in range(pert_arr.shape[1]):
                        P_pert[pid][c_i, s_i, g_ii, r_ii, dest, :] = pert_arr[g_ii, r_ii]
            if done_cnt % 6 == 0 or done_cnt == 36:
                log(
                    f"  Completed {done_cnt}/36 checkpoints "
                    f"(latest: fold{k_r} {cond_r} seed{res['seed']} in {res['elapsed']}s; "
                    f"wall={time.time() - t_fwd:.1f}s)"
                )

        if RUN_DEVICE == "cuda":
            for t in tasks:
                _ingest_result(_eval_single_checkpoint_worker(t))
        else:
            ctx = mp.get_context("spawn")
            with concurrent.futures.ProcessPoolExecutor(max_workers=18, mp_context=ctx) as ex:
                futs = [ex.submit(_eval_single_checkpoint_worker, t) for t in tasks]
                for fut in concurrent.futures.as_completed(futs):
                    _ingest_result(fut.result())
    finally:
        shutil.rmtree(tmp_cache_dir, ignore_errors=True)

    # Verify complete coverage and finiteness of pooled predictions
    for pid in participants:
        if not np.isfinite(P_orig[pid]).all() or not np.isfinite(P_pert[pid]).all():
            raise RuntimeError(f"{pid}: Missing or non-finite pooled predictions!")
    max_s1 = max(v["max_abs_diff_gpu_tf32_vs_cpu_fp32"] for v in sanity1_diffs.values())
    mean_s1 = max(v["mean_abs_diff"] for v in sanity1_diffs.values())
    log(
        f"All 36 checkpoints done in {time.time() - t_fwd:.1f}s! "
        f"Sanity Check 1 max_abs_diff={max_s1:.2e} (mean_max={mean_s1:.2e}); "
        f"Sanity Check 2={sanity2_diffs}"
    )

    # 5. Compute Observed Drops & 10,000-Iteration Video-Cluster Bootstrap (O4(3))
    log("Preparing 10,000-iteration canonical_id video-cluster bootstrap weights...")
    unique_cids = np.sort(split["canonical_id"].unique())
    assert len(unique_cids) == 2108, f"Expected 2108 canonical_id clusters, got {len(unique_cids)}"
    cid_to_idx = {int(cid): i for i, cid in enumerate(unique_cids.tolist())}
    vid_to_cluster = {int(row.video_id): cid_to_idx[int(row.canonical_id)] for _, row in split.iterrows()}

    boot_seed_bytes = b"EmoBrain/O4/video_canonical_bootstrap"
    boot_seed_int = int.from_bytes(hashlib.sha256(boot_seed_bytes).digest()[:8], "big")
    rng_boot = np.random.default_rng(boot_seed_int)
    boot_draws = rng_boot.integers(0, len(unique_cids), size=(N_BOOT, len(unique_cids)))

    M_cluster = np.zeros((N_BOOT, len(unique_cids)), dtype=np.float64)
    row_grid = np.broadcast_to(np.arange(N_BOOT)[:, None], boot_draws.shape)
    np.add.at(M_cluster, (row_grid, boot_draws), 1.0)
    assert np.all(M_cluster.sum(axis=1) == len(unique_cids))

    # Verify duplicate canonical_id pair (1349, 1363) receives identical multiplicity weights
    assert vid_to_cluster[1349] == vid_to_cluster[1363]

    # Precompute participant bootstrap weight matrices and Y statistics
    W_part = {}
    W_sum_part = {}
    Y0_part = {}
    Sw_Y_part = {}
    SYY_part = {}
    for pid in participants:
        clusters_s = np.array([vid_to_cluster[int(v)] for v in part_vids_sorted[pid]], dtype=np.int64)
        W = np.ascontiguousarray(M_cluster[:, clusters_s], dtype=np.float64)
        W_sum = W.sum(axis=1, keepdims=True)
        assert (W_sum > 0).all()
        Y = part_Y[pid]
        Y0 = Y - Y.mean(axis=0, keepdims=True)
        Sw_Y = W @ Y0
        Sw_Y2 = W @ (Y0 * Y0)
        SYY = Sw_Y2 - (Sw_Y * Sw_Y) / W_sum
        W_part[pid] = W
        W_sum_part[pid] = W_sum
        Y0_part[pid] = Y0
        Sw_Y_part[pid] = Sw_Y
        SYY_part[pid] = SYY

    # Mandatory Sanity Check 3: compare weighted_pearson_blas vs explicit row expansion + s4_common.pearson
    sanity3_max_diff = 0.0
    pid0 = "sub-01"
    P_test_mat = P_pert[pid0][1, 0, 0].transpose(1, 0, 2).reshape(len(part_vids_sorted[pid0]), N_REPEATS * 34).astype(np.float64)
    r_blas_test = weighted_pearson_blas(
        W_part[pid0][:5], W_sum_part[pid0][:5], Y0_part[pid0], Sw_Y_part[pid0][:5], SYY_part[pid0][:5], P_test_mat
    )
    for b_i, draw_idx in enumerate([0, 1, 2, 3, 4]):
        counts_int = W_part[pid0][draw_idx].astype(np.int64)
        exp_rows = np.repeat(np.arange(len(counts_int)), counts_int)
        for rep_chk in (0, 7, 19):
            p_exp = P_pert[pid0][1, 0, 0, rep_chk][exp_rows]
            y_exp = part_Y[pid0][exp_rows]
            r_ref = c.pearson(p_exp, y_exp)
            d3 = float(np.nanmax(np.abs(r_blas_test[b_i, rep_chk] - r_ref)))
            sanity3_max_diff = max(sanity3_max_diff, d3)
    if sanity3_max_diff >= 1e-13:
        raise AssertionError(f"Sanity Check 3 FAILED: max_abs_diff={sanity3_max_diff}")
    log(f"Sanity Check 3 PASSED: BLAS weighted Pearson vs explicit expansion max_abs_diff={sanity3_max_diff:.2e}")

    # Arrays for observed & bootstrap statistics
    n_p, n_c, n_s, n_g = len(participants), len(CONDITIONS), len(SEEDS), len(group_names)
    r_orig_emo_obs = np.empty((n_p, n_c, n_s, 34), dtype=np.float64)
    r_orig_obs = np.empty((n_p, n_c, n_s), dtype=np.float64)
    r_pert_rep_obs = np.empty((n_p, n_c, n_s, n_g, N_REPEATS), dtype=np.float64)
    drop_rep_obs = np.empty((n_p, n_c, n_s, n_g, N_REPEATS), dtype=np.float64)
    drop_obs = np.empty((n_p, n_c, n_s, n_g), dtype=np.float64)
    drop_emo_obs = np.empty((n_p, n_c, n_s, n_g, 34), dtype=np.float64)

    n_const_y_obs = np.zeros(n_p, dtype=np.int64)
    n_const_p_orig_obs = np.zeros((n_p, n_c, n_s), dtype=np.int64)
    n_const_p_pert_obs = np.zeros((n_p, n_c, n_s, n_g), dtype=np.int64)  # max across 20 repeats

    r_orig_emo_boot = np.empty((N_BOOT, n_p, n_c, n_s, 34), dtype=np.float64)
    r_orig_boot = np.empty((N_BOOT, n_p, n_c, n_s), dtype=np.float64)
    drop_boot = np.empty((N_BOOT, n_p, n_c, n_s, n_g), dtype=np.float64)

    t_boot = time.time()
    log("Computing unperturbed observed & bootstrap correlations...")
    for p_i, pid in enumerate(participants):
        Y = part_Y[pid]
        y_var = Y.var(axis=0)
        n_const_y_obs[p_i] = int(np.sum(y_var <= VAR_EPS))

        # Stack all 6 (cond, seed) unperturbed predictions for single BLAS call
        orig_blocks = []
        for c_i in range(n_c):
            for s_i in range(n_s):
                po = P_orig[pid][c_i, s_i].astype(np.float64)
                n_const_p_orig_obs[p_i, c_i, s_i] = int(np.sum(po.var(axis=0) <= VAR_EPS))
                r_e = c.pearson(po, Y)
                r_orig_emo_obs[p_i, c_i, s_i] = r_e
                r_orig_obs[p_i, c_i, s_i] = float(np.nanmean(r_e))
                orig_blocks.append(po)

        P_orig_cat = np.concatenate(orig_blocks, axis=1)  # (N_s, 6 * 34)
        rb_orig = weighted_pearson_blas(
            W_part[pid], W_sum_part[pid], Y0_part[pid], Sw_Y_part[pid], SYY_part[pid], P_orig_cat
        )  # (B, 6, 34)
        idx = 0
        for c_i in range(n_c):
            for s_i in range(n_s):
                r_orig_emo_boot[:, p_i, c_i, s_i, :] = rb_orig[:, idx, :]
                r_orig_boot[:, p_i, c_i, s_i] = np.nanmean(rb_orig[:, idx, :], axis=-1)
                idx += 1

    # Loop over 13 groups, computing both 34-emotion mean bootstrap drops AND per-emotion exploratory table
    per_emotion_rows = []
    n_const_boot_any = 0

    log("Computing 13-group x 20-repeat bootstrap drops and per-emotion BH-FDR statistics...")
    for g_i, g_name in enumerate(group_names):
        g_ko = group_ko_map[g_name]
        g_kind = str(groups_meta.loc[g_i, "group_kind"])
        n_roi_g = int(groups_meta.loc[g_i, "n_roi"])
        med_agree = float(groups_meta.loc[g_i, "median_agreement"])

        # (B, 5, 2, 3, 34) for this group (~81.6 MB)
        drop_emo_boot_g = np.empty((N_BOOT, n_p, n_c, n_s, 34), dtype=np.float64)

        for p_i, pid in enumerate(participants):
            Y = part_Y[pid]
            n_vid_s = len(Y)
            # Stack 2 conditions x 3 seeds x 20 repeats = 120 blocks of 34 cols -> 4080 cols
            pert_blocks = []
            for c_i in range(n_c):
                for s_i in range(n_s):
                    r_pert_e_reps = np.empty((N_REPEATS, 34), dtype=np.float64)
                    max_const = 0
                    for rep in range(N_REPEATS):
                        pp = P_pert[pid][c_i, s_i, g_i, rep].astype(np.float64)
                        max_const = max(max_const, int(np.sum(pp.var(axis=0) <= VAR_EPS)))
                        re_rep = c.pearson(pp, Y)
                        r_pert_e_reps[rep] = re_rep
                        r_pert_rep_obs[p_i, c_i, s_i, g_i, rep] = float(np.nanmean(re_rep))
                        pert_blocks.append(pp)
                    n_const_p_pert_obs[p_i, c_i, s_i, g_i] = max_const
                    # O3: drop per repeat = r_orig - r_pert(repeat), then mean over 20 repeats
                    d_reps = r_orig_obs[p_i, c_i, s_i] - r_pert_rep_obs[p_i, c_i, s_i, g_i, :]
                    drop_rep_obs[p_i, c_i, s_i, g_i, :] = d_reps
                    drop_obs[p_i, c_i, s_i, g_i] = float(np.mean(d_reps))
                    drop_emo_obs[p_i, c_i, s_i, g_i, :] = np.nanmean(
                        r_orig_emo_obs[p_i, c_i, s_i, None, :] - r_pert_e_reps, axis=0
                    )

            P_pert_cat = np.concatenate(pert_blocks, axis=1)  # (N_s, 120 * 34)
            rb_pert = weighted_pearson_blas(
                W_part[pid], W_sum_part[pid], Y0_part[pid], Sw_Y_part[pid], SYY_part[pid], P_pert_cat
            )  # (B, 120, 34)
            if not np.isfinite(rb_pert).all():
                n_const_boot_any += int(np.sum(~np.isfinite(rb_pert)))

            blk = 0
            for c_i in range(n_c):
                for s_i in range(n_s):
                    rb_slice = rb_pert[:, blk : blk + N_REPEATS, :]  # (B, 20, 34)
                    blk += N_REPEATS
                    r_pert_mean34_b = np.nanmean(rb_slice, axis=-1)  # (B, 20)
                    drop_boot[:, p_i, c_i, s_i, g_i] = r_orig_boot[:, p_i, c_i, s_i] - np.mean(
                        r_pert_mean34_b, axis=1
                    )
                    drop_emo_boot_g[:, p_i, c_i, s_i, :] = np.nanmean(
                        r_orig_emo_boot[:, p_i, c_i, s_i, None, :] - rb_slice, axis=1
                    )

        # Summarize exploratory per-emotion results (3-seed mean) for sub-01..05 and mean_5
        # Observed: drop_emo_obs[:, :, :, g_i, :] has shape (5, 2, 3, 34)
        for p_label_idx in range(n_p + 1):
            if p_label_idx < n_p:
                p_label = participants[p_label_idx]
                Yp = part_Y[p_label]
                n_nonzero_vec = np.sum(Yp > 0, axis=0).astype(int)
                var_y_vec = Yp.var(axis=0, ddof=0)
                obs_s = drop_emo_obs[p_label_idx, :, :, g_i, :]  # (2, 3, 34)
                boot_s = drop_emo_boot_g[:, p_label_idx, :, :, :]  # (B, 2, 3, 34)
            else:
                p_label = "mean_5"
                n_nonzero_vec = np.sum(y_all > 0, axis=0).astype(int)
                var_y_vec = y_all.astype(np.float64).var(axis=0, ddof=0)
                obs_s = drop_emo_obs[:, :, :, g_i, :].mean(axis=0)  # (2, 3, 34)
                boot_s = drop_emo_boot_g.mean(axis=1)  # (B, 2, 3, 34)

            obs_A1 = obs_s[0].mean(axis=0)  # (34,)
            sd_A1 = obs_s[0].std(axis=0, ddof=1)
            obs_C1 = obs_s[1].mean(axis=0)  # (34,)
            sd_C1 = obs_s[1].std(axis=0, ddof=1)
            diff_seeds = obs_s[1] - obs_s[0]  # (3, 34)
            obs_diff = diff_seeds.mean(axis=0)
            sd_diff = diff_seeds.std(axis=0, ddof=1)

            boot_A1 = boot_s[:, 0, :, :].mean(axis=1)  # (B, 34)
            boot_C1 = boot_s[:, 1, :, :].mean(axis=1)  # (B, 34)
            boot_diff = boot_C1 - boot_A1  # (B, 34)

            ciL_A1, ciH_A1, p_A1 = boot_ci_and_p_vec(obs_A1, boot_A1)
            ciL_C1, ciH_C1, p_C1 = boot_ci_and_p_vec(obs_C1, boot_C1)
            ciL_df, ciH_df, p_df = boot_ci_and_p_vec(obs_diff, boot_diff)

            q_A1 = bh_fdr_adjust(p_A1)
            q_C1 = bh_fdr_adjust(p_C1)
            q_df = bh_fdr_adjust(p_df)

            for e_i, e_name in enumerate(emotion_names):
                per_emotion_rows.append(
                    {
                        "analysis_status": "[탐색]",
                        "fdr_family": f"{p_label}:{g_name}:34_emotions",
                        "participant": p_label,
                        "group": g_name,
                        "group_ko": g_ko,
                        "group_kind": g_kind,
                        "n_roi": n_roi_g,
                        "median_agreement": med_agree,
                        "emotion_index": e_i,
                        "score_col": emo_score_cols[e_i],
                        "emotion": e_name,
                        "n_nonzero_y": int(n_nonzero_vec[e_i]),
                        "var_y": float(var_y_vec[e_i]),
                        "drop_A1_mean": float(obs_A1[e_i]),
                        "drop_A1_sd": float(sd_A1[e_i]),
                        "drop_A1_ci_low": float(ciL_A1[e_i]),
                        "drop_A1_ci_high": float(ciH_A1[e_i]),
                        "drop_A1_p_boot": float(p_A1[e_i]),
                        "drop_A1_q_bh34": float(q_A1[e_i]),
                        "drop_C1_mean": float(obs_C1[e_i]),
                        "drop_C1_sd": float(sd_C1[e_i]),
                        "drop_C1_ci_low": float(ciL_C1[e_i]),
                        "drop_C1_ci_high": float(ciH_C1[e_i]),
                        "drop_C1_p_boot": float(p_C1[e_i]),
                        "drop_C1_q_bh34": float(q_C1[e_i]),
                        "diff_C1_minus_A1_mean": float(obs_diff[e_i]),
                        "diff_C1_minus_A1_sd": float(sd_diff[e_i]),
                        "diff_C1_minus_A1_seed0": float(diff_seeds[0, e_i]),
                        "diff_C1_minus_A1_seed1": float(diff_seeds[1, e_i]),
                        "diff_C1_minus_A1_seed2": float(diff_seeds[2, e_i]),
                        "diff_C1_minus_A1_ci_low": float(ciL_df[e_i]),
                        "diff_C1_minus_A1_ci_high": float(ciH_df[e_i]),
                        "diff_C1_minus_A1_p_boot": float(p_df[e_i]),
                        "diff_C1_minus_A1_q_bh34": float(q_df[e_i]),
                        "sig_bh34_diff": bool(q_df[e_i] < ALPHA) if np.isfinite(q_df[e_i]) else False,
                    }
                )

        log(f"  Group {g_i + 1:2d}/13 ({g_name:20s}, n_roi={n_roi_g:2d}) done ({time.time() - t_boot:.1f}s)")

    # 6. Build Primary Summary Table (s9_6_4b_network_perturbation_summary.tsv) & Per-Seed Table (s9_6_4b_by_seed.tsv)
    log("Assembling summary tables with Holm-13 multiple-comparison correction...")

    summary_rows = []
    for p_label_idx in range(n_p + 1):
        p_label = participants[p_label_idx] if p_label_idx < n_p else "mean_5"
        raw_p_diff_family = np.empty(n_g, dtype=np.float64)
        temp_family_rows = []

        for g_i, g_name in enumerate(group_names):
            g_row = groups_meta.iloc[g_i]
            if p_label_idx < n_p:
                pid = participants[p_label_idx]
                n_vox = float(voxels_by_part_group[pid][g_name])
                n_uvox = float(unique_voxels_by_part_group[pid][g_name])
                n_vid_eval = int(len(part_vids_sorted[pid]))
                ro_A1_s = r_orig_obs[p_label_idx, 0, :]  # (3,)
                ro_C1_s = r_orig_obs[p_label_idx, 1, :]  # (3,)
                d_A1_s = drop_obs[p_label_idx, 0, :, g_i]  # (3,)
                d_C1_s = drop_obs[p_label_idx, 1, :, g_i]  # (3,)
                b_A1_s = drop_boot[:, p_label_idx, 0, :, g_i]  # (B, 3)
                b_C1_s = drop_boot[:, p_label_idx, 1, :, g_i]  # (B, 3)
            else:
                n_vox = float(np.mean([voxels_by_part_group[p][g_name] for p in participants]))
                n_uvox = float(np.mean([unique_voxels_by_part_group[p][g_name] for p in participants]))
                n_vid_eval = int(len(split))
                ro_A1_s = r_orig_obs[:, 0, :].mean(axis=0)  # (3,)
                ro_C1_s = r_orig_obs[:, 1, :].mean(axis=0)  # (3,)
                d_A1_s = drop_obs[:, 0, :, g_i].mean(axis=0)  # (3,)
                d_C1_s = drop_obs[:, 1, :, g_i].mean(axis=0)  # (3,)
                b_A1_s = drop_boot[:, :, 0, :, g_i].mean(axis=1)  # (B, 3)
                b_C1_s = drop_boot[:, :, 1, :, g_i].mean(axis=1)  # (B, 3)

            diff_s = d_C1_s - d_A1_s  # (3,)
            d_A1_mean, d_A1_sd = float(d_A1_s.mean()), float(d_A1_s.std(ddof=1))
            d_C1_mean, d_C1_sd = float(d_C1_s.mean()), float(d_C1_s.std(ddof=1))
            diff_mean, diff_sd = float(diff_s.mean()), float(diff_s.std(ddof=1))

            b_A1_mean = b_A1_s.mean(axis=1)  # (B,)
            b_C1_mean = b_C1_s.mean(axis=1)  # (B,)
            b_diff_mean = b_C1_mean - b_A1_mean  # (B,)

            ciL_A1, ciH_A1, p_A1 = boot_ci_and_p(d_A1_mean, b_A1_mean)
            ciL_C1, ciH_C1, p_C1 = boot_ci_and_p(d_C1_mean, b_C1_mean)
            ciL_df, ciH_df, p_df = boot_ci_and_p(diff_mean, b_diff_mean)
            raw_p_diff_family[g_i] = p_df

            temp_family_rows.append(
                {
                    "participant": p_label,
                    "n_videos": n_vid_eval,
                    "group": g_name,
                    "group_ko": str(g_row["group_ko"]),
                    "group_kind": str(g_row["group_kind"]),
                    "n_roi": int(g_row["n_roi"]),
                    "n_voxels": n_vox,
                    "n_unique_voxels": n_uvox,
                    "median_agreement": float(g_row["median_agreement"]),
                    "min_agreement": float(g_row["min_agreement"]),
                    "max_agreement": float(g_row["max_agreement"]),
                    "r_orig_A1_mean": float(ro_A1_s.mean()),
                    "r_orig_A1_sd": float(ro_A1_s.std(ddof=1)),
                    "r_orig_C1_mean": float(ro_C1_s.mean()),
                    "r_orig_C1_sd": float(ro_C1_s.std(ddof=1)),
                    "drop_A1_mean": d_A1_mean,
                    "drop_A1_sd": d_A1_sd,
                    "drop_A1_seed0": float(d_A1_s[0]),
                    "drop_A1_seed1": float(d_A1_s[1]),
                    "drop_A1_seed2": float(d_A1_s[2]),
                    "drop_A1_ci_low": ciL_A1,
                    "drop_A1_ci_high": ciH_A1,
                    "drop_A1_p_boot": p_A1,
                    "drop_C1_mean": d_C1_mean,
                    "drop_C1_sd": d_C1_sd,
                    "drop_C1_seed0": float(d_C1_s[0]),
                    "drop_C1_seed1": float(d_C1_s[1]),
                    "drop_C1_seed2": float(d_C1_s[2]),
                    "drop_C1_ci_low": ciL_C1,
                    "drop_C1_ci_high": ciH_C1,
                    "drop_C1_p_boot": p_C1,
                    "diff_C1_minus_A1_mean": diff_mean,
                    "diff_C1_minus_A1_sd": diff_sd,
                    "diff_C1_minus_A1_seed0": float(diff_s[0]),
                    "diff_C1_minus_A1_seed1": float(diff_s[1]),
                    "diff_C1_minus_A1_seed2": float(diff_s[2]),
                    "diff_C1_minus_A1_ci_low": ciL_df,
                    "diff_C1_minus_A1_ci_high": ciH_df,
                    "p_boot": p_df,
                }
            )

        p_holm = holm_adjust(raw_p_diff_family)
        for g_i, r_dict in enumerate(temp_family_rows):
            r_dict["holm_family"] = f"{p_label}:13_groups"
            r_dict["p_holm13"] = float(p_holm[g_i])
            r_dict["confirmed_unadj"] = bool(r_dict["p_boot"] < ALPHA)
            r_dict["confirmed_holm13"] = bool(p_holm[g_i] < ALPHA)
            summary_rows.append(r_dict)

    summary_df = pd.DataFrame(summary_rows)

    # Annotate counts of confirmed individual participants (out of 5) per network (6-1 rule)
    indiv = summary_df[summary_df["participant"].isin(participants)]
    counts_by_g = {}
    for g_name in group_names:
        sub_g = indiv[indiv["group"] == g_name]
        counts_by_g[g_name] = {
            "n_confirmed_unadj_of_5": int(sub_g["confirmed_unadj"].sum()),
            "n_confirmed_holm13_of_5": int(sub_g["confirmed_holm13"].sum()),
            "n_pos_diff_of_5": int((sub_g["diff_C1_minus_A1_mean"] > 0).sum()),
            "n_neg_diff_of_5": int((sub_g["diff_C1_minus_A1_mean"] < 0).sum()),
        }
    for col in ("n_confirmed_unadj_of_5", "n_confirmed_holm13_of_5", "n_pos_diff_of_5", "n_neg_diff_of_5"):
        summary_df[col] = summary_df["group"].map(lambda g, c=col: counts_by_g[g][c])

    # Per-seed table (s9_6_4b_by_seed.tsv)
    by_seed_rows = []
    for s_i, seed in enumerate(SEEDS):
        for p_label_idx in range(n_p + 1):
            p_label = participants[p_label_idx] if p_label_idx < n_p else "mean_5"
            raw_p_seed_family = np.empty(n_g, dtype=np.float64)
            tmp_seed_rows = []
            for g_i, g_name in enumerate(group_names):
                g_row = groups_meta.iloc[g_i]
                if p_label_idx < n_p:
                    pid = participants[p_label_idx]
                    n_vox = float(voxels_by_part_group[pid][g_name])
                    ro_A1 = float(r_orig_obs[p_label_idx, 0, s_i])
                    ro_C1 = float(r_orig_obs[p_label_idx, 1, s_i])
                    d_A1 = float(drop_obs[p_label_idx, 0, s_i, g_i])
                    d_C1 = float(drop_obs[p_label_idx, 1, s_i, g_i])
                    rep_sd_A1 = float(drop_rep_obs[p_label_idx, 0, s_i, g_i, :].std(ddof=1))
                    rep_sd_C1 = float(drop_rep_obs[p_label_idx, 1, s_i, g_i, :].std(ddof=1))
                    b_A1 = drop_boot[:, p_label_idx, 0, s_i, g_i]
                    b_C1 = drop_boot[:, p_label_idx, 1, s_i, g_i]
                    nc_y = int(n_const_y_obs[p_label_idx])
                    nc_pA = int(n_const_p_pert_obs[p_label_idx, 0, s_i, g_i])
                    nc_pC = int(n_const_p_pert_obs[p_label_idx, 1, s_i, g_i])
                else:
                    n_vox = float(np.mean([voxels_by_part_group[p][g_name] for p in participants]))
                    ro_A1 = float(r_orig_obs[:, 0, s_i].mean())
                    ro_C1 = float(r_orig_obs[:, 1, s_i].mean())
                    d_A1 = float(drop_obs[:, 0, s_i, g_i].mean())
                    d_C1 = float(drop_obs[:, 1, s_i, g_i].mean())
                    rep_sd_A1 = float(drop_rep_obs[:, 0, s_i, g_i, :].mean(axis=0).std(ddof=1))
                    rep_sd_C1 = float(drop_rep_obs[:, 1, s_i, g_i, :].mean(axis=0).std(ddof=1))
                    b_A1 = drop_boot[:, :, 0, s_i, g_i].mean(axis=1)
                    b_C1 = drop_boot[:, :, 1, s_i, g_i].mean(axis=1)
                    nc_y = int(n_const_y_obs.sum())
                    nc_pA = int(n_const_p_pert_obs[:, 0, s_i, g_i].max())
                    nc_pC = int(n_const_p_pert_obs[:, 1, s_i, g_i].max())

                diff_val = d_C1 - d_A1
                b_diff = b_C1 - b_A1
                ciL_A1, ciH_A1, p_A1 = boot_ci_and_p(d_A1, b_A1)
                ciL_C1, ciH_C1, p_C1 = boot_ci_and_p(d_C1, b_C1)
                ciL_df, ciH_df, p_df = boot_ci_and_p(diff_val, b_diff)
                raw_p_seed_family[g_i] = p_df

                tmp_seed_rows.append(
                    {
                        "seed": seed,
                        "participant": p_label,
                        "group": g_name,
                        "group_ko": str(g_row["group_ko"]),
                        "group_kind": str(g_row["group_kind"]),
                        "n_roi": int(g_row["n_roi"]),
                        "n_voxels": n_vox,
                        "median_agreement": float(g_row["median_agreement"]),
                        "r_orig_A1": ro_A1,
                        "r_pert_A1_mean20": ro_A1 - d_A1,
                        "drop_A1": d_A1,
                        "drop_A1_sd_20rep": rep_sd_A1,
                        "drop_A1_ci_low": ciL_A1,
                        "drop_A1_ci_high": ciH_A1,
                        "drop_A1_p_boot": p_A1,
                        "r_orig_C1": ro_C1,
                        "r_pert_C1_mean20": ro_C1 - d_C1,
                        "drop_C1": d_C1,
                        "drop_C1_sd_20rep": rep_sd_C1,
                        "drop_C1_ci_low": ciL_C1,
                        "drop_C1_ci_high": ciH_C1,
                        "drop_C1_p_boot": p_C1,
                        "diff_C1_minus_A1": diff_val,
                        "diff_C1_minus_A1_ci_low": ciL_df,
                        "diff_C1_minus_A1_ci_high": ciH_df,
                        "p_boot": p_df,
                        "n_const_y": nc_y,
                        "n_const_p_A1_maxrep": nc_pA,
                        "n_const_p_C1_maxrep": nc_pC,
                    }
                )
            p_holm_s = holm_adjust(raw_p_seed_family)
            for g_i, r_dict in enumerate(tmp_seed_rows):
                r_dict["p_holm13"] = float(p_holm_s[g_i])
                r_dict["confirmed_unadj"] = bool(r_dict["p_boot"] < ALPHA)
                r_dict["confirmed_holm13"] = bool(p_holm_s[g_i] < ALPHA)
                by_seed_rows.append(r_dict)

    by_seed_df = pd.DataFrame(by_seed_rows)
    per_emotion_df = pd.DataFrame(per_emotion_rows)

    # 7. Write all output files atomically
    log("Writing output tables, donor assignments, and provenance.json...")
    summary_df.to_csv(OUT_DIR / "s9_6_4b_network_perturbation_summary.tsv", sep="\t", index=False)
    summary_df.to_csv(OUT_DIR / "s9_6_4b_network_perturbation_summary.csv", index=False)

    by_seed_df.to_csv(OUT_DIR / "s9_6_4b_by_seed.tsv", sep="\t", index=False)
    by_seed_df.to_csv(OUT_DIR / "s9_6_4b_by_seed.csv", index=False)

    per_emotion_df.to_csv(OUT_DIR / "s9_6_4b_per_emotion.tsv", sep="\t", index=False)

    donor_df.to_csv(OUT_DIR / "donor_assignments.tsv", sep="\t", index=False)
    np.savez_compressed(
        OUT_DIR / "donor_assignments.npz",
        fold=donor_df["fold"].to_numpy(np.int16),
        participant=donor_df["participant"].to_numpy(),
        repeat=donor_df["repeat"].to_numpy(np.int16),
        recipient_video_id=donor_df["recipient_video_id"].to_numpy(np.int32),
        donor_video_id=donor_df["donor_video_id"].to_numpy(np.int32),
    )

    # Final repo cleanliness verification
    git_head_after = check_repo_clean()
    assert git_head_after == git_head

    # Summary of Holm-13 confirmations across families
    family_summary = {}
    for p_label in ["mean_5"] + participants:
        sub = summary_df[summary_df["participant"] == p_label]
        family_summary[p_label] = {
            "n_confirmed_unadjusted": int(sub["confirmed_unadj"].sum()),
            "n_confirmed_holm13": int(sub["confirmed_holm13"].sum()),
            "confirmed_unadj_groups": sub.loc[sub["confirmed_unadj"], "group"].tolist(),
            "confirmed_holm13_groups": sub.loc[sub["confirmed_holm13"], "group"].tolist(),
        }

    provenance = {
        "analysis": "S9-4 Network-Unit Input Perturbation (6-4b, 2-4, O3, O4(3))",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.time() - t0, 3),
        "git_head": git_head,
        "tracked_repo_clean_before_and_after": True,
        "environment": {
            "python": sys.version,
            "torch": torch.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "cuda_is_available": torch.cuda.is_available(),
            "torch_num_threads": torch.get_num_threads(),
            "device": RUN_DEVICE,
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "tf32_allowed": bool(torch.backends.cuda.matmul.allow_tf32) if RUN_DEVICE == "cuda" else False,
        },
        "design_parameters": {
            "conditions": list(CONDITIONS),
            "display_names": {"brain_only": "A-1 (Brain -> Emotion)", "brain_decoded": "C-1 (Brain + Decoded Feature -> Emotion, interaction head)"},
            "outer_folds": list(range(1, N_FOLDS + 1)),
            "seeds": list(SEEDS),
            "seed_sd_ddof": 1,
            "n_cabnp_groups": 13,
            "subcortex_note": "10 subcortical ROIs form 1 anatomical group (Subcortex / 피질하 해부학적 묶음), not called a functional network (6-4).",
            "n_perturbation_repeats_O3": N_REPEATS,
            "n_bootstrap_draws_O4": N_BOOT,
            "bootstrap_unit": "video canonical_id cluster (2,108 clusters across 2,109 dev videos; 1349 & 1363 co-sampled)",
            "bootstrap_seed_string": boot_seed_bytes.decode(),
            "bootstrap_seed_uint64": boot_seed_int,
            "ci_method": "Basic bootstrap 95% CI: [2*theta - q(0.975), 2*theta - q(0.025)]",
            "p_value_method": "Centered two-sided Hall & Wilson (1991): (1 + sum(|Delta_boot - Delta| >= |Delta|)) / 10001",
            "multiple_comparisons_primary": "Holm-13 across 13 groups on diff_drop = drop(C-1) - drop(A-1), separately per family (mean_5 and each participant)",
            "multiple_comparisons_exploratory": "BH-FDR across 34 emotions within each (participant, group, comparison) family [탐색]",
        },
        "selected_candidates": selected_candidates_meta,
        "voxels_by_participant_and_group": voxels_by_part_group,
        "unique_voxels_by_participant_and_group": unique_voxels_by_part_group,
        "donor_seeds": donor_seeds_meta,
        "sanity_checks": {
            **unit_checks,
            "sanity0_fold1_standardization_vs_prepare_fold_max_abs_diff": sanity0_fold1_diffs,
            "sanity0_all6folds_voxel_standardizer_max_abs_diff": sanity0_all_folds_std_diff,
            "sanity1_unperturbed_vs_saved_test_outputs_max_abs_diff_overall": float(max(v["max_abs_diff_gpu_tf32_vs_cpu_fp32"] for v in sanity1_diffs.values())),
            "sanity1_unperturbed_vs_saved_test_outputs_max_mean_abs_diff": float(max(v["mean_abs_diff"] for v in sanity1_diffs.values())),
            "sanity1_note": "Saved test_outputs.npz ran on B300 GPU with TF32 Tensor Cores (10-bit mantissa); CPU runs IEEE-754 FP32 (matching FP64 within 2.43e-7). Both r_orig and r_pert in S9-4 are evaluated consistently in IEEE-754 FP32 on CPU.",
            "sanity1_per_checkpoint_max_abs_diff": sanity1_diffs,
            "sanity2_raw_voxel_vs_pre_self_attn_token_replacement_fold1_seed0_Default_rep0": sanity2_diffs,
            "sanity3_blas_weighted_pearson_vs_explicit_repeat_max_abs_diff": sanity3_max_diff,
            "sanity4_donor_no_self_replacement": True,
            "sanity4_donor_same_participant_and_fold": True,
            "n_const_y_observed": {p: int(n_const_y_obs[i]) for i, p in enumerate(participants)},
            "n_const_p_orig_max": int(n_const_p_orig_obs.max()),
            "n_const_p_pert_max": int(n_const_p_pert_obs.max()),
            "n_nonfinite_boot_correlations": int(n_const_boot_any),
        },
        "holm13_confirmation_summary": family_summary,
        "input_sha256": input_hashes,
        "output_files": [
            str(OUT_DIR / "s9_6_4b_network_perturbation_summary.tsv"),
            str(OUT_DIR / "s9_6_4b_network_perturbation_summary.csv"),
            str(OUT_DIR / "s9_6_4b_by_seed.tsv"),
            str(OUT_DIR / "s9_6_4b_by_seed.csv"),
            str(OUT_DIR / "s9_6_4b_per_emotion.tsv"),
            str(OUT_DIR / "donor_assignments.tsv"),
            str(OUT_DIR / "donor_assignments.npz"),
            str(OUT_DIR / "provenance.json"),
        ],
    }
    (OUT_DIR / "provenance.json").write_text(json.dumps(provenance, indent=2, ensure_ascii=False))

    # Print concise mean_5 table to stdout
    m5 = summary_df[summary_df["participant"] == "mean_5"].copy()
    log("=== 5-PARTICIPANT MEAN (mean_5) SUMMARY ACROSS 13 GROUPS ===")
    cols_show = [
        "group",
        "n_roi",
        "median_agreement",
        "drop_A1_mean",
        "drop_C1_mean",
        "diff_C1_minus_A1_mean",
        "diff_C1_minus_A1_ci_low",
        "diff_C1_minus_A1_ci_high",
        "p_boot",
        "p_holm13",
        "confirmed_holm13",
        "n_confirmed_unadj_of_5",
        "n_confirmed_holm13_of_5",
    ]
    print(m5[cols_show].to_string(index=False), flush=True)
    log(f"ALL DONE in {time.time() - t0:.2f}s!")


if __name__ == "__main__":
    main()
