"""
Phase 2 Direction 4 — Subject-conditioned variability (analysis only, no new training).

For each (arch, task), the trained model produces predictions on the test fold for each
(subject, stimulus) pair. Since the SAME stim appears 5 times (once per subject) with
DIFFERENT brain activity, the prediction should vary across subjects if the brain
encoder is using subject-specific information.

We compute:
  - Per-stimulus subject variance of the prediction (averaged across stim)
  - Compared against (a) chance baseline (shuffled brain → subject), (b) prediction
    spread for ROI baseline (proxy for "how much subject-level variance exists")

This is analysis-only — we re-run the trained models in inference mode on test data.

Output: results/phase2/subject_variability/<arch>_<task>.csv
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

sys.path.insert(0, "/pscratch/sd/s/sjmoon/EmoBrain/project/dir2_multimodal/code/legacy_phase2")
sys.path.insert(0, "/pscratch/sd/s/sjmoon/EmoBrain/project/dir2_multimodal/code/legacy_phase2/architectures")

from _lib import (TASKS, load_brain_embeddings, load_video_feature, load_task_labels,
                  get_fold_split, fit_standardizer, apply_standardizer,
                  DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD, DEFAULT_VIDEO,
                  ALL_SUBJECTS)
from arch_D_late_fusion import LateFusion
from arch_A_token_transformer import TokenTransformer
from arch_B_cross_attention import CrossAttention

EmoBrain = Path("/pscratch/sd/s/sjmoon/EmoBrain")
OUT_DIR = EmoBrain / "project/shared/results/phase2/subject_variability"


def collect_predictions(model, brain_dict, video_feat, vstim, label_df, test_stim,
                         task_type, device, b_mu, b_std, v_mu, v_std):
    """For each (subject, stim) pair in test_stim, get model prediction.
    Returns a long DataFrame with cols: stim, subject, pred, label."""
    stim_to_vidx = {int(s): i for i, s in enumerate(vstim)}
    label_map = dict(zip(label_df["stimulus_num"], label_df["label"]))
    rows = []
    model.eval()
    with torch.no_grad():
        for subj, (emb, stim_arr) in brain_dict.items():
            s2b = {int(s): i for i, s in enumerate(stim_arr)}
            for stim in test_stim:
                if stim not in s2b or stim not in stim_to_vidx or stim not in label_map:
                    continue
                bx = (emb[s2b[stim]] - b_mu.squeeze()) / b_std.squeeze()
                vx = (video_feat[stim_to_vidx[stim]] - v_mu.squeeze()) / v_std.squeeze()
                bx_t = torch.from_numpy(bx.astype(np.float32)).unsqueeze(0).to(device)
                vx_t = torch.from_numpy(vx.astype(np.float32)).unsqueeze(0).to(device)
                out = model(bx_t, vx_t)
                if task_type == "binary":
                    pred = float(F.softmax(out, dim=-1)[0, 1].item())
                else:
                    pred = float(out.squeeze().item())
                rows.append({"stim": int(stim), "subject": subj,
                             "pred": pred, "label": float(label_map[stim])})
    return pd.DataFrame(rows)


def variability_metrics(df):
    """For each stim, compute std of pred across subjects. Return distribution stats."""
    by_stim = df.groupby("stim").agg(
        pred_mean=("pred", "mean"),
        pred_std=("pred", "std"),
        label=("label", "first"),
    ).reset_index()
    overall_pred_std = float(df["pred"].std())
    return {
        "mean_within_stim_subject_std": float(by_stim["pred_std"].mean()),
        "median_within_stim_subject_std": float(by_stim["pred_std"].median()),
        "overall_pred_std": overall_pred_std,
        "n_stim_evaluated": int(len(by_stim)),
        # Fraction of total variance that is across-stim (between) vs within-stim (across-subject)
        "between_stim_var": float(by_stim["pred_mean"].var()),
        "within_stim_var_mean": float((by_stim["pred_std"] ** 2).mean()),
    }


def main():
    """Loads the saved trained model from results/phase2/<arch>/<task>.csv setup.
    Since we don't currently save model weights from train_supervised, this script
    is a placeholder; it re-trains a single fold/seed model in-memory for analysis.
    For full pipeline, train_supervised could be extended to save .pt; we provide
    this script as the analysis spec to be wired up after the main runs complete.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", required=True, choices=["D", "A", "B"])
    ap.add_argument("--task", required=True, choices=list(TASKS.keys()))
    ap.add_argument("--fold", type=int, default=1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--brain_model", default=DEFAULT_BRAIN)
    ap.add_argument("--brain_init", default=DEFAULT_BRAIN_INIT)
    ap.add_argument("--brain_padding", default=DEFAULT_BRAIN_PAD)
    ap.add_argument("--video", default=DEFAULT_VIDEO)
    ap.add_argument("--out_csv", default=None)
    args = ap.parse_args()

    out_csv = args.out_csv or str(OUT_DIR / f"{args.arch}_{args.task}_fold{args.fold}_seed{args.seed}.csv")
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Re-train model (matching train_supervised.py logic)
    print(f"=== Phase 2 D4: subject variability (arch={args.arch} task={args.task} "
          f"fold={args.fold} seed={args.seed}) ===")
    print("  Re-training model in memory (analysis-only; main results already in results/phase2/<arch>/)")

    from train_supervised import train_one_run, ARCHS
    brain = load_brain_embeddings(args.brain_model, args.brain_init, args.brain_padding)
    video, vstim = load_video_feature(args.video)
    label_df, ttype = load_task_labels(args.task)
    split = get_fold_split(args.fold)
    data = __import__("_lib").build_pooled_data(brain, video, vstim, label_df, split, ttype)
    arch_cls = ARCHS[args.arch]
    n_out = TASKS[args.task]["n_out"]

    # We need access to the trained model (not just the result). Replicate training inline.
    res = train_one_run(
        arch_cls,
        data["train"]["brain"], data["train"]["video"], data["train"]["label"],
        data["val"]["brain"],   data["val"]["video"],   data["val"]["label"],
        data["test"]["brain"],  data["test"]["video"],  data["test"]["label"],
        ttype, n_out, args.seed, device,
    )
    print(f"  retrain test_main={res['test_main']:.4f}")
    print("  Note: standalone variability analysis requires saving the trained model state.")
    print("  This script is a spec for the analysis; production version should hook into")
    print("  train_supervised's best_state for each (arch, task, fold, seed).")

    # Skeleton output
    df = pd.DataFrame([{
        "arch": args.arch, "task": args.task, "fold": args.fold, "seed": args.seed,
        "status": "placeholder",
        "note": "Re-train trained model inline; use train_supervised+save_model patch to enable full analysis.",
    }])
    df.to_csv(out_csv, index=False)
    print(f"  skeleton row written to {out_csv}")


if __name__ == "__main__":
    main()
