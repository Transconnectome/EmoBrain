"""
Padding ablation probe (NewE96).

For each (init, padding, task, head, mode, subject_or_pool, seed):
  - init    : resting | scratch
  - padding : replicate | zero | mean
  - task    : V binary (Q4 vs Q1) | A binary (Q4 vs Q1)
  - head    : linear (logistic L2) | mlp (SwiFT vendored, configurable preset)
  - mode    : single | pooled | per_subject
              single       -> single subject train+test
              pooled       -> concat all subjects' samples into one train/val/test
              per_subject  -> train+test separately per subject, report each row
  - subject : sub-01..sub-05 (or "pool")
  - seed    : 0, 1, 2  (averaged)

MLP presets (--mlp_preset):
  swift  (default): SwiftMLP hidden=768, mlp_ratio=4.0, drop=0.3   ~9.4M params
  small            : SmallMLP hidden=256, mlp_ratio=2.0, drop=0.5  ~0.7M params

Other MLP hyperparams shared across presets:
  batch_size=8, epochs=40, patience=10, LR grid {1e-4,3e-4,1e-3,3e-3,1e-2}
  Adam wd=1e-4, balanced sampling, val AUROC early stop

Metrics on test: AUROC, AUPRC, balanced_accuracy.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, balanced_accuracy_score,
                             roc_auc_score)
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.heads import SwiftMLP, SmallMLP

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
EMB_ROOT = FEELIN / "project/shared/output/embeddings"
DATA = FEELIN / "data"
OUT_DIR = FEELIN / "project/shared/results/padding_ablation"

MODEL_TAG = "swift_NewE96_SL20"
ALL_SUBJECTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]
INITS = ["resting", "scratch"]
PADS = ["replicate", "zero", "mean"]
TASKS = ["V", "A"]
SEEDS = [0, 1, 2]

LINEAR_CS = [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]
MLP_LRS = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
MLP_BATCH = 8
MLP_EPOCHS = 40
MLP_PATIENCE = 10
MLP_WD = 1e-4

MLP_PRESETS = {
    "swift": dict(cls="SwiftMLP", hidden=768, mlp_ratio=4.0, drop=0.3, num_blocks=2),
    "small": dict(cls="SmallMLP", hidden=256, mlp_ratio=2.0, drop=0.5, num_blocks=2),
}


def load_subject_emb(init, pad, subject):
    p = EMB_ROOT / f"{MODEL_TAG}_{init}_pad-{pad}" / f"{subject}.pt"
    d = torch.load(p, map_location="cpu", weights_only=False)
    emb = d["embeddings"].numpy().astype(np.float32)
    stim = d["stim_num"].numpy() if hasattr(d["stim_num"], "numpy") else np.asarray(d["stim_num"])
    return emb, stim


def _task_label_df(task):
    if task == "V":
        return pd.read_csv(DATA / "horikawa_L0_V_binary_subset.csv"), "v_label"
    return pd.read_csv(DATA / "horikawa_L0_A_binary_subset.csv"), "a_label"


def build_task_data(init, pad, task, subjects):
    """
    Build one train/val/test dataset by pooling given subjects.
    Standardization fit on train only.
    """
    bin_df, label_col = _task_label_df(task)
    split = pd.read_csv(DATA / "horikawa_split.csv")

    X_parts = {"train": [], "val": [], "test": []}
    y_parts = {"train": [], "val": [], "test": []}

    for subj in subjects:
        emb, stim_num = load_subject_emb(init, pad, subj)
        split_s = split[split["subject"] == subj][["stimulus_num", "split"]]
        df = (bin_df[["stimulus_num", label_col]]
              .merge(split_s, on="stimulus_num", how="inner"))
        stim_to_idx = {int(s): i for i, s in enumerate(stim_num)}
        df["row"] = df["stimulus_num"].map(stim_to_idx)
        assert df["row"].notna().all(), f"stim_num mismatch for {subj}"
        for sp in ["train", "val", "test"]:
            sub = df[df["split"] == sp]
            rows = sub["row"].astype(int).values
            X_parts[sp].append(emb[rows])
            y_parts[sp].append(sub[label_col].astype(int).values)

    out = {}
    for sp in ["train", "val", "test"]:
        out[f"X_{sp}"] = np.concatenate(X_parts[sp], axis=0)
        out[f"y_{sp}"] = np.concatenate(y_parts[sp], axis=0)
    scaler = StandardScaler().fit(out["X_train"])
    for k in ["X_train", "X_val", "X_test"]:
        out[k] = scaler.transform(out[k])
    return out


def eval_metrics(y_true, prob, pred):
    return {
        "auroc": float(roc_auc_score(y_true, prob)),
        "auprc": float(average_precision_score(y_true, prob)),
        "bal_acc": float(balanced_accuracy_score(y_true, pred)),
    }


def linear_probe(data, seed):
    """L2 logistic with class_weight='balanced'. C tuned on val AUROC."""
    best_c, best_val_auc, best_model = None, -1, None
    for C in LINEAR_CS:
        clf = LogisticRegression(C=C, penalty="l2", solver="lbfgs",
                                 max_iter=5000, class_weight="balanced",
                                 random_state=seed, n_jobs=1)
        clf.fit(data["X_train"], data["y_train"])
        val_prob = clf.predict_proba(data["X_val"])[:, 1]
        val_auc = roc_auc_score(data["y_val"], val_prob)
        if val_auc > best_val_auc:
            best_val_auc, best_c, best_model = val_auc, C, clf
    test_prob = best_model.predict_proba(data["X_test"])[:, 1]
    test_pred = best_model.predict(data["X_test"])
    m = eval_metrics(data["y_test"], test_prob, test_pred)
    m["val_auroc"] = float(best_val_auc)
    m["best_hp"] = f"C={best_c}"
    return m


def _build_mlp(preset_cfg, in_dim):
    if preset_cfg["cls"] == "SwiftMLP":
        return SwiftMLP(num_classes=2, num_blocks=preset_cfg["num_blocks"],
                        hidden_dim=in_dim, mlp_ratio=preset_cfg["mlp_ratio"],
                        drop_rate=preset_cfg["drop"], already_pooled=True)
    elif preset_cfg["cls"] == "SmallMLP":
        return SmallMLP(in_dim=in_dim, num_classes=2,
                        hidden=preset_cfg["hidden"], num_blocks=preset_cfg["num_blocks"],
                        mlp_ratio=preset_cfg["mlp_ratio"], drop_rate=preset_cfg["drop"])
    raise ValueError(preset_cfg["cls"])


def _train_one_mlp(data, seed, lr, dev, preset_cfg):
    torch.manual_seed(seed)
    np.random.seed(seed)

    in_dim = data["X_train"].shape[1]
    Xtr = torch.from_numpy(data["X_train"]).float().to(dev)
    ytr = torch.from_numpy(data["y_train"]).long().to(dev)
    Xva = torch.from_numpy(data["X_val"]).float().to(dev)
    Xte = torch.from_numpy(data["X_test"]).float().to(dev)
    ytr_np = data["y_train"]
    n_train = len(ytr_np)

    class_count = np.bincount(ytr_np)
    sample_w = 1.0 / class_count[ytr_np]
    sample_w = sample_w / sample_w.sum()

    model = _build_mlp(preset_cfg, in_dim).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=MLP_WD)
    loss_fn = nn.CrossEntropyLoss()
    rng = np.random.default_rng(seed)

    best_val_auc, best_state, stale, best_epoch = -1, None, 0, 0
    for epoch in range(MLP_EPOCHS):
        model.train()
        idx_all = rng.choice(n_train, size=n_train, replace=True, p=sample_w)
        idx_all = torch.from_numpy(idx_all).long().to(dev)
        for s in range(0, n_train, MLP_BATCH):
            idx = idx_all[s:s + MLP_BATCH]
            opt.zero_grad()
            logits = model(Xtr[idx])
            loss = loss_fn(logits, ytr[idx])
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            val_prob = torch.softmax(model(Xva), dim=1)[:, 1].cpu().numpy()
        val_auc = roc_auc_score(data["y_val"], val_prob)
        if val_auc > best_val_auc:
            best_val_auc = val_auc
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            best_epoch = epoch + 1
            stale = 0
        else:
            stale += 1
            if stale >= MLP_PATIENCE:
                break

    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        test_prob = torch.softmax(model(Xte), dim=1)[:, 1].cpu().numpy()
    test_pred = (test_prob >= 0.5).astype(int)
    m = eval_metrics(data["y_test"], test_prob, test_pred)
    return best_val_auc, m, best_epoch


def mlp_probe(data, seed, preset_cfg, dev):
    best_lr, best_val_auc, best_test, best_epoch = None, -1, None, 0
    for lr in MLP_LRS:
        val_auc, test_m, ep = _train_one_mlp(data, seed, lr, dev, preset_cfg)
        if val_auc > best_val_auc:
            best_val_auc, best_lr, best_test, best_epoch = val_auc, lr, test_m, ep
    m = dict(best_test)
    m["val_auroc"] = float(best_val_auc)
    m["best_hp"] = f"lr={best_lr},ep={best_epoch},h={preset_cfg['hidden']},drop={preset_cfg['drop']}"
    return m


def run_one(init, pad, task, head_name, mode, subjects, mlp_preset_name, dev):
    """Returns list of result rows. One row per (mode-grouping, seed)."""
    preset_cfg = MLP_PRESETS[mlp_preset_name]
    rows = []

    if mode == "per_subject":
        groups = [(s, [s]) for s in subjects]
    elif mode == "pooled":
        groups = [("pool", list(subjects))]
    else:  # single
        assert len(subjects) == 1
        groups = [(subjects[0], list(subjects))]

    for subj_label, subj_list in groups:
        data = build_task_data(init, pad, task, subj_list)
        ntr, nva, nte = len(data["y_train"]), len(data["y_val"]), len(data["y_test"])
        for seed in SEEDS:
            if head_name == "linear":
                res = linear_probe(data, seed)
            else:
                res = mlp_probe(data, seed, preset_cfg, dev)
            row = {
                "init": init, "padding": pad, "task": task, "head": head_name,
                "mode": mode, "subject": subj_label,
                "mlp_preset": mlp_preset_name if head_name == "mlp" else "n/a",
                "seed": seed,
                "n_train": ntr, "n_val": nva, "n_test": nte,
                "best_hp": res["best_hp"],
                "val_auroc": res["val_auroc"],
                "test_auroc": res["auroc"],
                "test_auprc": res["auprc"],
                "test_bal_acc": res["bal_acc"],
            }
            rows.append(row)
            print(f"    [{head_name} mode={mode} {subj_label} s{seed}] "
                  f"val_AUC={res['val_auroc']:.3f} test_AUC={res['auroc']:.3f} "
                  f"test_AUPRC={res['auprc']:.3f} ({res['best_hp']})")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", default="sub-01",
                    help="Comma-separated subjects (e.g. sub-01,sub-02). "
                         "For mode=single, must be exactly one.")
    ap.add_argument("--mode", choices=["single", "pooled", "per_subject"],
                    default="single")
    ap.add_argument("--mlp_preset", choices=list(MLP_PRESETS.keys()), default="swift")
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--summary_csv", required=True)
    args = ap.parse_args()

    subjects = [s.strip() for s in args.subjects.split(",")]
    if args.mode == "single" and len(subjects) != 1:
        raise ValueError(f"mode=single requires exactly 1 subject, got {subjects}")

    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {dev}, mode={args.mode}, subjects={subjects}, mlp_preset={args.mlp_preset}")
    print(f"MLP preset config: {MLP_PRESETS[args.mlp_preset]}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for init in INITS:
        for pad in PADS:
            for task in TASKS:
                print(f"\n[cell] init={init} pad={pad} task={task}")
                for head_name in ["linear", "mlp"]:
                    rows.extend(run_one(init, pad, task, head_name,
                                        args.mode, subjects, args.mlp_preset, dev))

    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)
    print(f"\n[done] per-seed rows -> {args.out_csv}  ({len(df)} rows)")

    grp = ["init", "padding", "task", "head", "mode", "subject", "mlp_preset"]
    metrics = ["test_auroc", "test_auprc", "test_bal_acc"]
    agg = df.groupby(grp)[metrics].agg(["mean", "std"])
    agg.columns = [f"{m}_{stat}" for m, stat in agg.columns]
    agg = agg.reset_index()
    agg.to_csv(args.summary_csv, index=False)
    print(f"[done] summary -> {args.summary_csv}  ({len(agg)} cells)")

    print("\n=== Mean test_AUROC per padding (over all dims) ===")
    print(df.groupby("padding")["test_auroc"].agg(["mean", "std"]).round(4))


if __name__ == "__main__":
    main()
