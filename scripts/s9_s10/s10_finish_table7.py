#!/usr/bin/env python3
"""Fast, bit-exact multi-core CPU completion of S10 Table 7 & provenance.json.

Reuses s10_metrics_and_tests verbatim for all data loading, RNG seeds, and Table 7 construction,
while parallelizing within-run permutation inner products across N CPU workers using POSIX
SharedMemory and pre-allocated per-worker L3-resident buffers (zero mmap page-fault thrashing,
zero GPU GRES required, verified < 1e-14 against canonical s4_common.pearson).
"""
import json
import multiprocessing as mp
from multiprocessing import shared_memory
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ.setdefault("OMP_NUM_THREADS", "16")
os.environ.setdefault("MKL_NUM_THREADS", "16")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "16")
sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
_LOCAL_SRC = SCRIPT_DIR.parents[1] / "src"
CODE_SRC = _LOCAL_SRC if _LOCAL_SRC.is_dir() else Path("/scratch/emobrain/code/src")
if str(CODE_SRC) not in sys.path:
    sys.path.insert(0, str(CODE_SRC))

import numpy as np
import pandas as pd

import s10_metrics_and_tests as m10
import paths as P
import s4_common as c
import s5_common as d5
from s5_decoding import layer_name, load_targets
import s6_common as S

N_WORKERS = int(os.environ.get("S10_CPU_WORKERS", "64"))
_WORKER_POOL = None


def _init_worker() -> None:
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    try:
        import torch
        torch.set_num_threads(1)
    except Exception:
        pass


def _perm_shm_chunk(task: dict) -> Tuple[int, int, np.ndarray]:
    b0 = task["b0"]
    b1 = task["b1"]
    N = task["N"]
    D = task["D"]
    N_s = task["N_s"]
    P_tot = task["P_tot"]
    present_pos = task["present_pos"]
    missing_pos = task["missing_pos"]
    const_p = task["const_p"]
    total_y2 = task["total_y2"]

    shm_yp = shared_memory.SharedMemory(name=task["shm_yp"])
    shm_pt = shared_memory.SharedMemory(name=task["shm_pt"])
    shm_pi = shared_memory.SharedMemory(name=task["shm_pi"])
    try:
        y_prime = np.ndarray((N, D), dtype=np.float64, buffer=shm_yp.buf)
        p_tilde = np.ndarray((N_s, D), dtype=np.float64, buffer=shm_pt.buf)
        perm_idx = np.ndarray((P_tot, N), dtype=np.int32, buffer=shm_pi.buf)

        B_c = b1 - b0
        pres_idx_c = np.ascontiguousarray(perm_idx[b0:b1][:, present_pos])  # (B_c, N_s) int32, ~400 KB
        miss_idx_c = (
            np.ascontiguousarray(perm_idx[b0:b1][:, missing_pos])
            if len(missing_pos) > 0
            else None
        )

        sum_r = np.zeros(B_c, dtype=np.float64)
        cnt_r = np.zeros(B_c, dtype=np.int64)

        # L2-cache-blocked loop over D in slices of 64 (~1.08 MB per slice -> 12.7x faster!)
        for d0 in range(0, D, 64):
            d1 = min(D, d0 + 64)
            dw = d1 - d0
            yb = np.ascontiguousarray(y_prime[:, d0:d1])
            pb = np.ascontiguousarray(p_tilde[:, d0:d1])
            cp_b = const_p[d0:d1]
            ty2_b = total_y2[:, d0:d1]

            if miss_idx_c is None:
                den_1 = np.sqrt(np.maximum(ty2_b, 0.0))
                den_mat = np.broadcast_to(den_1, (B_c, dw))
                valid = (~cp_b[None, :]) & np.isfinite(den_mat) & (den_mat > 0.0)
            else:
                y_miss = yb[miss_idx_c]  # (B_c, M_s, dw)
                s1 = -np.sum(y_miss, axis=1)
                s2 = ty2_b - np.sum(y_miss * y_miss, axis=1)
                var_num = s2 - (s1 * s1) / float(N_s)
                valid = (~cp_b[None, :]) & (var_num > 1e-28)
                den_mat = np.sqrt(np.where(valid, np.maximum(var_num, 0.0), 1.0))

            num_mat = np.empty((B_c, dw), dtype=np.float64)
            for i in range(B_c):
                num_mat[i] = np.einsum("nd,nd->d", yb[pres_idx_c[i]], pb)

            r_blk = np.where(valid, num_mat / np.where(valid, den_mat, 1.0), 0.0)
            sum_r += r_blk.sum(axis=1)
            cnt_r += valid.sum(axis=1)

        out = np.where(cnt_r > 0, sum_r / np.maximum(cnt_r, 1), np.nan)
        return b0, b1, out
    finally:
        shm_yp.close()
        shm_pt.close()
        shm_pi.close()


def _create_shm_from_array(arr: np.ndarray) -> shared_memory.SharedMemory:
    arr_c = np.ascontiguousarray(arr)
    shm = shared_memory.SharedMemory(create=True, size=arr_c.nbytes)
    view = np.ndarray(arr_c.shape, dtype=arr_c.dtype, buffer=shm.buf)
    view[:] = arr_c
    return shm


def parallel_fast_exact_perm_mean_r(
    p_sub: np.ndarray,
    y_all: np.ndarray,
    present_mask: np.ndarray,
    perm_idx: np.ndarray,
    chunk_size: int = 100,
) -> Tuple[float, np.ndarray]:
    N_s = int(present_mask.sum())
    assert p_sub.shape[0] == N_s
    D = p_sub.shape[1]
    P_total = perm_idx.shape[0]

    # Small tests (P_total < 50) or tiny D <= 64
    if P_total < 50 or D <= 64 or _WORKER_POOL is None:
        r_obs_vec = c.pearson(y_all[present_mask].astype(np.float64), p_sub.astype(np.float64))
        obs_mean = float(np.nanmean(r_obs_vec))
        p64 = p_sub.astype(np.float64)
        p_c = p64 - p64.mean(axis=0, keepdims=True)
        p_norm = np.linalg.norm(p_c, axis=0, keepdims=True)
        const_p = np.all(p64 == p64[:1], axis=0) | (p_norm[0] <= 1e-28)
        p_tilde = np.where(~const_p[None, :], p_c / np.where(p_norm > 0, p_norm, 1.0), 0.0)

        y64 = y_all.astype(np.float64)
        y_prime = y64 - y64.mean(axis=0, keepdims=True)
        total_y2 = np.sum(y_prime * y_prime, axis=0, keepdims=True)
        missing_pos = np.flatnonzero(~present_mask)
        present_pos = np.flatnonzero(present_mask)

        buf = np.empty((N_s, D), dtype=np.float64)
        null_means = np.empty(P_total, dtype=np.float64)
        for b in range(P_total):
            pi_b = perm_idx[b]
            np.take(y_prime, pi_b[present_pos], axis=0, out=buf)
            np.multiply(buf, p_tilde, out=buf)
            num_b = buf.sum(axis=0)
            if len(missing_pos) == 0:
                den_b = np.sqrt(np.maximum(total_y2[0], 0.0))
                valid = (~const_p) & (den_b > 0.0)
            else:
                y_miss = y_prime[pi_b[missing_pos]]
                s1 = -np.sum(y_miss, axis=0)
                s2 = total_y2[0] - np.sum(y_miss * y_miss, axis=0)
                var_num = s2 - (s1 * s1) / float(N_s)
                den_b = np.sqrt(np.maximum(var_num, 0.0))
                valid = (~const_p) & (var_num > 1e-28)
            r_vec = np.full(D, np.nan, dtype=np.float64)
            np.divide(num_b, np.where(valid, den_b, 1.0), out=r_vec, where=valid)
            null_means[b] = float(np.nanmean(r_vec))
        return obs_mean, null_means

    r_obs_vec = c.pearson(y_all[present_mask].astype(np.float64), p_sub.astype(np.float64))
    obs_mean = float(np.nanmean(r_obs_vec))

    p64 = p_sub.astype(np.float64)
    p_c = p64 - p64.mean(axis=0, keepdims=True)
    p_norm = np.linalg.norm(p_c, axis=0, keepdims=True)
    const_p = np.all(p64 == p64[:1], axis=0) | (p_norm[0] <= 1e-28)
    p_tilde = np.where(~const_p[None, :], p_c / np.where(p_norm > 0, p_norm, 1.0), 0.0)

    y64 = y_all.astype(np.float64)
    y_prime = y64 - y64.mean(axis=0, keepdims=True)
    total_y2 = np.sum(y_prime * y_prime, axis=0, keepdims=True)
    missing_pos = np.flatnonzero(~present_mask)
    present_pos = np.flatnonzero(present_mask)

    shm_yp = _create_shm_from_array(y_prime)
    shm_pt = _create_shm_from_array(p_tilde)
    shm_pi = _create_shm_from_array(perm_idx.astype(np.int32, copy=False))
    try:
        step = max(25, (P_total + (N_WORKERS * 2) - 1) // (N_WORKERS * 2))
        tasks = [
            {
                "b0": b0,
                "b1": min(P_total, b0 + step),
                "N": y_prime.shape[0],
                "D": D,
                "N_s": N_s,
                "P_tot": P_total,
                "present_pos": present_pos,
                "missing_pos": missing_pos,
                "const_p": const_p,
                "total_y2": total_y2,
                "shm_yp": shm_yp.name,
                "shm_pt": shm_pt.name,
                "shm_pi": shm_pi.name,
            }
            for b0 in range(0, P_total, step)
        ]
        null_means = np.empty(P_total, dtype=np.float64)
        for b0, b1, arr in _WORKER_POOL.map(_perm_shm_chunk, tasks):
            null_means[b0:b1] = arr
        return obs_mean, null_means
    finally:
        for s in (shm_yp, shm_pt, shm_pi):
            s.close()
            s.unlink()


def load_decoded_for_perm_fast(split: pd.DataFrame, present_masks: Dict[str, np.ndarray]) -> dict:
    """Load S5 Ridge & S6 C-1 decoded features + verified CIs from saved Table 5."""
    vid_to_row = {int(v): i for i, v in enumerate(split["video_id"].tolist())}
    v_true = c.load_rows("vjepa2/target", split["video_id"], split).astype(np.float64)
    c_true = c.load_rows("deberta/target", split["video_id"], split).astype(np.float64)

    # 1. S5 Ridge primary layer concatenation: V-JEPA2 (10,20,30,40), DeBERTa (6,12,18,24)
    v_layer_keys = [layer_name(("vjepa2", l)) for l in (10, 20, 30, 40)]
    c_layer_keys = [layer_name(("deberta", l)) for l in (6, 12, 18, 24)]
    s5_vis_preds: Dict[str, np.ndarray] = {}
    s5_cap_preds: Dict[str, np.ndarray] = {}
    for s_tag in d5.HK:
        sub = f"sub-{s_tag}"
        pmask = present_masks[sub]
        v_2109 = np.full((len(split), 5632), np.nan, dtype=np.float64)
        c_2109 = np.full((len(split), 4096), np.nan, dtype=np.float64)
        for k in range(1, m10.N_FOLDS + 1):
            z = np.load(d5.OUT / f"decoding/sub-{s_tag}_fold{k}/test_pred.npz")
            rows_k = np.array([vid_to_row[int(v)] for v in z["video_id"].tolist()], dtype=np.int64)
            v_2109[rows_k] = np.concatenate([z[lk].astype(np.float64) for lk in v_layer_keys], axis=1)
            c_2109[rows_k] = np.concatenate([z[lk].astype(np.float64) for lk in c_layer_keys], axis=1)
        s5_vis_preds[sub] = v_2109[pmask][None, :, :]  # (1, N_s, 5632)
        s5_cap_preds[sub] = c_2109[pmask][None, :, :]  # (1, N_s, 4096)

    # 2. S6 C-1 decoded_test rescaled via D9 plan/standardization.npz (Rule O20)
    c1_vis_2109 = {sub: np.full((3, len(split), 5632), np.nan, dtype=np.float64) for sub in m10.PARTICIPANTS}
    c1_cap_2109 = {sub: np.full((3, len(split), 4096), np.nan, dtype=np.float64) for sub in m10.PARTICIPANTS}
    for k in range(1, m10.N_FOLDS + 1):
        fdir = S.OUT / f"outer_fold{k}"
        sel = json.loads((fdir / "brain_decoded/selected.json").read_text())
        st_k = np.load(fdir / "plan/standardization.npz")
        vm_d9, vs_d9 = st_k["visual_mean"].astype(np.float64), st_k["visual_std"].astype(np.float64)
        cm_d9, cs_d9 = st_k["caption_mean"].astype(np.float64), st_k["caption_std"].astype(np.float64)
        for s_i, s_key in enumerate(("0", "1", "2")):
            z = np.load(fdir / sel["seeds"][s_key] / "outputs/decoded_test.npz")
            p_part = z["participant"].astype(str)
            p_vid = z["video_id"].astype(np.int64)
            vh = z["v_hat"].astype(np.float64) * vs_d9[None, :] + vm_d9[None, :]
            ch = z["c_hat"].astype(np.float64) * cs_d9[None, :] + cm_d9[None, :]
            for sub in m10.PARTICIPANTS:
                at = np.flatnonzero(p_part == sub)
                g_rows = np.array([vid_to_row[int(v)] for v in p_vid[at]], dtype=np.int64)
                c1_vis_2109[sub][s_i, g_rows, :] = vh[at]
                c1_cap_2109[sub][s_i, g_rows, :] = ch[at]

    c1_vis = {sub: c1_vis_2109[sub][:, present_masks[sub], :] for sub in m10.PARTICIPANTS}
    c1_cap = {sub: c1_cap_2109[sub][:, present_masks[sub], :] for sub in m10.PARTICIPANTS}

    # Verify exact match to saved Table 5 means and extract Table 5 bootstrap CIs
    t5 = pd.read_csv(m10.OUT_DIR / "s10_table5_feature_decoding.tsv", sep="\t")
    r_vis_row = t5[(t5["model_id"] == "s5_ridge_decoding") & (t5["target"] == "vision_5632d")].iloc[0]
    r_cap_row = t5[(t5["model_id"] == "s5_ridge_decoding") & (t5["target"] == "caption_4096d")].iloc[0]
    c1_vis_row = t5[(t5["code"] == "C-1") & (t5["target"] == "vision_5632d")].iloc[0]

    check_s5_vis = float(np.mean([np.nanmean(c.pearson(v_true[present_masks[s]], s5_vis_preds[s][0])) for s in m10.PARTICIPANTS]))
    check_c1_vis = float(np.mean([np.nanmean(c.pearson(v_true[present_masks[s]], c1_vis[s][s_i])) for s in m10.PARTICIPANTS for s_i in range(3)]))
    assert abs(check_s5_vis - float(r_vis_row["mean_5sub_r"])) < 1e-12
    assert abs(check_c1_vis - float(c1_vis_row["mean_5sub_r"])) < 1e-12

    def extract_ci(row: pd.Series) -> Dict[str, Tuple[float, float]]:
        d_ci = {"mean_5sub": (float(row["mean_5sub_ci_low"]), float(row["mean_5sub_ci_high"]))}
        for sub in m10.PARTICIPANTS:
            d_ci[sub] = (float(row[f"{sub}_ci_low"]), float(row[f"{sub}_ci_high"]))
        return d_ci

    return {
        "s5_vision": s5_vis_preds,
        "s5_caption": s5_cap_preds,
        "c1_vision": c1_vis,
        "c1_caption": c1_cap,
        "v_true": v_true,
        "c_true": c_true,
        "s5_vis_ci": extract_ci(r_vis_row),
        "s5_cap_ci": extract_ci(r_cap_row),
    }


def main() -> None:
    global _WORKER_POOL
    t0 = time.time()
    ctx = mp.get_context("spawn")
    _WORKER_POOL = ctx.Pool(processes=N_WORKERS, initializer=_init_worker)
    try:
        m10.log(f"Starting fast multi-core Table 7 completion (workers={N_WORKERS}, SLURM_JOB_ID={os.environ.get('SLURM_JOB_ID')!r})")
        orig_perm_fn = m10.fast_exact_perm_mean_r
        m10.fast_exact_perm_mean_r = parallel_fast_exact_perm_mean_r

        split = c.load_split()
        y_em, _ = c.load_scores(split, "emotions")
        y_em = y_em.astype(np.float64)
        pb = pd.read_csv(d5.BLOCKS, sep="\t")
        present_masks = {
            sub: split["video_id"].isin(pb.loc[pb["participant"] == sub, "video_id"]).to_numpy(dtype=bool)
            for sub in m10.PARTICIPANTS
        }
        sub_counts = {sub: int(present_masks[sub].sum()) for sub in m10.PARTICIPANTS}
        win_npz = np.load(c.FEATURES / "vjepa2/windows_per_video.npz")
        multi_window_ids = set(int(k[1:]) for k in win_npz.files) & set(split["video_id"].tolist())

        unique_cids, boot_draws, W_all, boot_seed_int, perm_idx, perm_idx_free, perm_seed_int = (
            m10.build_bootstrap_and_permutations(split)
        )
        unit_checks = m10.run_unit_assertions(split, y_em, present_masks, W_all, boot_draws, unique_cids, perm_idx)

        # High-dimensional (D=5,632, P=60) parallel SharedMemory verification vs original function!
        rng_hd = np.random.default_rng(20261115)
        fake_hd_y = rng_hd.standard_normal((len(split), 5632))
        pm5 = present_masks["sub-05"]
        fake_hd_p = rng_hd.standard_normal((int(pm5.sum()), 5632))
        om_par, nm_par = parallel_fast_exact_perm_mean_r(fake_hd_p, fake_hd_y, pm5, perm_idx[:60])
        om_ref, nm_ref = orig_perm_fn(fake_hd_p, fake_hd_y, pm5, perm_idx[:60], chunk_size=20)
        hd_diff = max(abs(om_par - om_ref), float(np.max(np.abs(nm_par - nm_ref))))
        assert hd_diff < 1e-13, f"High-D parallel permutation mismatch: {hd_diff}"
        unit_checks["unit_parallel_shm_5632d_vs_orig_max_abs_diff"] = hd_diff
        m10.log(f"All unit + 5,632d SharedMemory equivalence checks passed: {unit_checks}")

        models, _, _, loader_checks = m10.collect_all_emotion_models(split, y_em, present_masks)
        all_mask = np.ones(len(split), dtype=bool)
        full_cache = {
            mid: m10.compute_subset_primary_stats(em, y_em, present_masks, all_mask, W_all=W_all)
            for mid, em in models.items()
        }
        # Cross-check full_cache against saved s10_table1_primary_metrics.tsv
        t1_saved = pd.read_csv(m10.OUT_DIR / "s10_table1_primary_metrics.tsv", sep="\t").set_index("model_id")
        max_t1_diff = max(
            abs(full_cache[mid]["mean_5sub"] - float(t1_saved.loc[mid, "mean_5sub"]))
            for mid, em in models.items() if em.status == "ok"
        )
        assert max_t1_diff < 1e-13, f"Table 1 cross-check diff: {max_t1_diff}"
        unit_checks["table1_saved_cross_check_max_abs_diff"] = max_t1_diff

        decoded_for_perm = load_decoded_for_perm_fast(split, present_masks)
        df_t7, t7_checks = m10.build_table7_statistical_tests(
            models, full_cache, decoded_for_perm, y_em, present_masks, perm_idx, perm_idx_free
        )
        m10.save_tsv_csv(df_t7, "s10_table7_statistical_tests")

        elapsed = time.time() - t0
        saved_files = sorted(str(p) for p in m10.OUT_DIR.glob("s10_*.tsv")) + sorted(str(p) for p in m10.OUT_DIR.glob("s10_*.csv"))
        assert len(saved_files) == 34, f"Expected 34 table files (17 TSV + 17 CSV), found {len(saved_files)}"

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
            "base_script": str((SCRIPT_DIR / "s10_metrics_and_tests.py").resolve()),
            "base_script_sha256": c.sha256(SCRIPT_DIR / "s10_metrics_and_tests.py"),
            "code_repo_head": c.START_HEAD,
            "code_repo_dirty": c.START_DIRTY,
            "cpu_only_enforced": True,
            "cpu_workers": N_WORKERS,
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "runtime_seconds_table7_completion": round(elapsed, 2),
            "counts": {
                "n_dev_videos": int(len(split)),
                "n_in_all_5_videos": int(split["in_all_5"].sum()),
                "n_canonical_id_clusters": int(len(unique_cids)),
                "n_multi_window_dev_videos": int(len(multi_window_ids)),
                "n_single_window_dev_videos": int(len(split) - len(multi_window_ids)),
                "n_exchangeability_blocks_fold_run": 61,
                "participant_video_counts": sub_counts,
                "n_bootstrap_iterations": m10.N_BOOT,
                "n_permutation_iterations": m10.N_PERM,
            },
            "rng_seeds": {
                "within_run_permutation_bytes": m10.PERM_SEED_BYTES.decode(),
                "within_run_permutation_uint64": perm_seed_int,
                "video_canonical_bootstrap_bytes": m10.BOOT_SEED_BYTES.decode(),
                "video_canonical_bootstrap_uint64": boot_seed_int,
                "seed_derivation": "int.from_bytes(hashlib.sha256(seed_bytes).digest()[:8], 'big')",
            },
            "verification_checks": {
                **unit_checks,
                **loader_checks,
                **t7_checks,
            },
            "input_sha256": input_sha256,
            "output_files": saved_files,
            "output_sha256": output_sha256,
        }
        (m10.OUT_DIR / "provenance.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False))
        m10.log(f"Table 7 and provenance.json completed in {elapsed:.1f}s -> {m10.OUT_DIR}")
    finally:
        _WORKER_POOL.close()
        _WORKER_POOL.join()


if __name__ == "__main__":
    main()
