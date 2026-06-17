"""Build per-task result tables for Phase 1 method+result PDF.

Layout (rev 3, per user direction):
  - Pooled mode only.
  - Video features excluded.
  - Binary: AUROC + balanced accuracy (per head).
  - Regression: Pearson r + MAE + MSE (per head).
  - Cat34_multilabel: macro AUROC + macro F1.
  - Cat34_soft: Pearson r + top1 accuracy.
  - Best value per column bolded (max for AUROC / bAcc / Pearson r / top1 acc / F1, min for MAE / MSE).
  - Chance rows excluded from best-of comparison.
"""
from pathlib import Path
import pandas as pd
import numpy as np

P = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/shared/results/phase1")
OUT = Path("/pscratch/sd/s/sjmoon/EmoBrain/docs/reports/phase1_audit_20260604/_pdf")
OUT.mkdir(parents=True, exist_ok=True)

DISPLAY = {
    "ROI_Schaefer400Tian50": "ROI (Schaefer400+Tian50)",
    "Brain-JEPA": "Brain-JEPA",
    "NeuroSTORM": "NeuroSTORM",
    "SwiFT_NewE96": "SwiFT NewE96",
    "SwiFT_NewE36": "SwiFT NewE36",
    "SwiFT_NewE192": "SwiFT NewE192",
    "SwiFT_UAH_5M": "SwiFT UAH-5M",
    "SwiFT_UAH_51M": "SwiFT UAH-51M",
    "SwiFT_UAH_202M": "SwiFT UAH-202M",
}
ROW_ORDER = [
    ("ROI_Schaefer400Tian50", "n/a"),
    ("Brain-JEPA", "resting"), ("Brain-JEPA", "scratch"),
    ("NeuroSTORM", "resting"), ("NeuroSTORM", "scratch"),
    ("SwiFT_NewE36", "resting"), ("SwiFT_NewE36", "scratch"),
    ("SwiFT_NewE96", "resting"), ("SwiFT_NewE96", "scratch"),
    ("SwiFT_NewE192", "resting"), ("SwiFT_NewE192", "scratch"),
    ("SwiFT_UAH_5M", "resting"), ("SwiFT_UAH_5M", "scratch"),
    ("SwiFT_UAH_51M", "resting"), ("SwiFT_UAH_51M", "scratch"),
    ("SwiFT_UAH_202M", "resting"), ("SwiFT_UAH_202M", "scratch"),
]

# Bold-comparison subset: only BFM rows (exclude ROI baseline and chance).
# Phase 1 user direction: bold marks the best model among the foundation models,
# not the floor baseline.
BFM_ROWS = [(feat, init) for feat, init in ROW_ORDER
            if feat != "ROI_Schaefer400Tian50"]


def best_padding_row(df, feat, init, head):
    sub = df[(df["feature"] == feat) & (df["head"] == head) & (df["mode"] == "pooled")]
    if init != "n/a":
        sub = sub[sub["init"] == init]
    if len(sub) == 0:
        return None
    pads = sub["padding"].unique().tolist()
    for preferred in ["zero", "time_mean", "mean"]:
        if preferred in pads:
            cand = sub[sub["padding"] == preferred]
            return cand.sort_values("rank").iloc[0]
    return sub.sort_values("rank").iloc[0]


def fmt(m, s, digits=3, bold=False):
    if m is None or pd.isna(m):
        return "--"
    if s is None or pd.isna(s):
        base = f"{m:.{digits}f}"
    else:
        base = f"{m:.{digits}f} $\\pm$ {s:.{digits}f}"
    if bold:
        return r"\textbf{" + base + "}"
    return base


def _val(row, mean_col):
    """Return mean value or None if row missing / NaN."""
    if row is None:
        return None
    v = row[mean_col]
    return None if pd.isna(v) else float(v)


def find_best(values, direction="max"):
    """Find best value among (id, value) pairs. None values skipped. Returns set of ids tied for best."""
    items = [(i, v) for i, v in values if v is not None]
    if not items:
        return set()
    if direction == "max":
        best = max(v for _, v in items)
    else:
        best = min(v for _, v in items)
    # Use small tolerance for equality (3 decimal places)
    return {i for i, v in items if abs(v - best) < 5e-4}


def build_binary(task):
    df = pd.read_csv(P / f"_benchmark_{task}.csv")
    df["init"] = df["init"].fillna("n/a")
    df["padding"] = df["padding"].fillna("n/a")

    # Collect all (id, row) for each column: id = (feat, init), col = (head, metric)
    cells = {}  # cells[(feat, init, head)] = row
    for feat, init in ROW_ORDER:
        for head in ["linear", "mlp"]:
            cells[(feat, init, head)] = best_padding_row(df, feat, init, head)

    # Best per column
    cols = {
        "lin_auroc": ("linear", "test_auroc_mean", "max"),
        "lin_bacc":  ("linear", "test_bal_acc_mean", "max"),
        "mlp_auroc": ("mlp", "test_auroc_mean", "max"),
        "mlp_bacc":  ("mlp", "test_bal_acc_mean", "max"),
    }
    best = {}
    for key, (head, mcol, direction) in cols.items():
        # Compare among BFM rows only (exclude ROI baseline and chance).
        vals = [((feat, init), _val(cells[(feat, init, head)], mcol)) for feat, init in BFM_ROWS]
        best[key] = find_best(vals, direction)

    L = []
    L.append(r"\begin{table}[H]\centering")
    task_esc = task.replace('_', r'\_')
    L.append(rf"\caption{{Task {task_esc} (Q1 vs Q4 binary). Pooled mode, 5-fold CV (1 seed). bAcc = balanced accuracy. Best value per column \textbf{{among BFM rows}} in bold (ROI baseline and chance excluded from comparison). Padding = zero for BFM, time\_mean for ROI, mean for NeuroSTORM (as launched).}}")
    L.append(r"\resizebox{\textwidth}{!}{%")
    L.append(r"\begin{tabular}{llcccc}")
    L.append(r"\toprule")
    L.append(r" & & \multicolumn{2}{c}{Linear} & \multicolumn{2}{c}{MLP} \\")
    L.append(r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}")
    L.append(r"Model & Init & AUROC & bAcc & AUROC & bAcc \\")
    L.append(r"\midrule")
    eol = r" \\"
    for feat, init in ROW_ORDER:
        lin = cells[(feat, init, "linear")]
        mlp = cells[(feat, init, "mlp")]
        if lin is None and mlp is None:
            continue
        key = (feat, init)
        parts = [
            DISPLAY[feat] if init != "scratch" else "",
            init if init != "n/a" else "--",
            fmt(_val(lin, "test_auroc_mean"),  lin["test_auroc_std"]   if lin is not None else None, bold=key in best["lin_auroc"]),
            fmt(_val(lin, "test_bal_acc_mean"), lin["test_bal_acc_std"] if lin is not None else None, bold=key in best["lin_bacc"]),
            fmt(_val(mlp, "test_auroc_mean"),  mlp["test_auroc_std"]   if mlp is not None else None, bold=key in best["mlp_auroc"]),
            fmt(_val(mlp, "test_bal_acc_mean"), mlp["test_bal_acc_std"] if mlp is not None else None, bold=key in best["mlp_bacc"]),
        ]
        L.append(" & ".join(parts) + eol)
    # chance
    L.append(r"\midrule")
    chance = df[df["feature"] == "chance"]
    eol = r" \\"
    for head in ["stratified", "most_frequent"]:
        ch = chance[chance["head"] == head]
        if len(ch) == 0:
            continue
        r = ch.iloc[0]
        head_esc = head.replace("_", r"\_")
        a = fmt(r['test_auroc_mean'], r['test_auroc_std'])
        b = fmt(r['test_bal_acc_mean'], r['test_bal_acc_std'])
        L.append(f"Chance & {head_esc} & {a} & {b} & -- & --" + eol)
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}%")
    L.append(r"}")
    L.append(r"\end{table}")
    return "\n".join(L)


def build_regression(task):
    df = pd.read_csv(P / f"_benchmark_{task}.csv")
    df["init"] = df["init"].fillna("n/a")
    df["padding"] = df["padding"].fillna("n/a")

    cells = {}
    for feat, init in ROW_ORDER:
        for head in ["linear", "mlp"]:
            cells[(feat, init, head)] = best_padding_row(df, feat, init, head)

    cols = {
        "lin_r":   ("linear", "test_pearson_r_mean", "max"),
        "lin_mae": ("linear", "test_mae_mean",       "min"),
        "lin_mse": ("linear", "test_mse_mean",       "min"),
        "mlp_r":   ("mlp",    "test_pearson_r_mean", "max"),
        "mlp_mae": ("mlp",    "test_mae_mean",       "min"),
        "mlp_mse": ("mlp",    "test_mse_mean",       "min"),
    }
    best = {}
    for key, (head, mcol, direction) in cols.items():
        # Compare among BFM rows only (exclude ROI baseline and chance).
        vals = [((feat, init), _val(cells[(feat, init, head)], mcol)) for feat, init in BFM_ROWS]
        best[key] = find_best(vals, direction)

    L = []
    L.append(r"\begin{table}[H]\centering")
    task_esc = task.replace('_', r'\_')
    L.append(rf"\caption{{Task {task_esc} (continuous regression). Pooled mode, 5-fold CV (1 seed). Best value per column \textbf{{among BFM rows}} in bold (ROI baseline and chance excluded; MAE / MSE bold = minimum, Pearson r bold = maximum).}}")
    L.append(r"\resizebox{\textwidth}{!}{%")
    L.append(r"\begin{tabular}{llcccccc}")
    L.append(r"\toprule")
    L.append(r" & & \multicolumn{3}{c}{Linear} & \multicolumn{3}{c}{MLP} \\")
    L.append(r"\cmidrule(lr){3-5}\cmidrule(lr){6-8}")
    L.append(r"Model & Init & Pearson r & MAE & MSE & Pearson r & MAE & MSE \\")
    L.append(r"\midrule")
    eol = r" \\"
    for feat, init in ROW_ORDER:
        lin = cells[(feat, init, "linear")]
        mlp = cells[(feat, init, "mlp")]
        if lin is None and mlp is None:
            continue
        key = (feat, init)
        parts = [
            DISPLAY[feat] if init != "scratch" else "",
            init if init != "n/a" else "--",
            fmt(_val(lin, "test_pearson_r_mean"), lin["test_pearson_r_std"] if lin is not None else None, bold=key in best["lin_r"]),
            fmt(_val(lin, "test_mae_mean"),       lin["test_mae_std"]       if lin is not None else None, bold=key in best["lin_mae"]),
            fmt(_val(lin, "test_mse_mean"),       lin["test_mse_std"]       if lin is not None else None, bold=key in best["lin_mse"]),
            fmt(_val(mlp, "test_pearson_r_mean"), mlp["test_pearson_r_std"] if mlp is not None else None, bold=key in best["mlp_r"]),
            fmt(_val(mlp, "test_mae_mean"),       mlp["test_mae_std"]       if mlp is not None else None, bold=key in best["mlp_mae"]),
            fmt(_val(mlp, "test_mse_mean"),       mlp["test_mse_std"]       if mlp is not None else None, bold=key in best["mlp_mse"]),
        ]
        L.append(" & ".join(parts) + eol)
    L.append(r"\midrule")
    chance = df[df["feature"] == "chance"]
    for head in ["mean", "median"]:
        ch = chance[chance["head"] == head]
        if len(ch) == 0:
            continue
        r = ch.iloc[0]
        parts = [
            "Chance", head,
            fmt(r["test_pearson_r_mean"], r["test_pearson_r_std"]),
            fmt(r["test_mae_mean"], r["test_mae_std"]),
            fmt(r["test_mse_mean"], r["test_mse_std"]),
            "--", "--", "--",
        ]
        L.append(" & ".join(parts) + eol)
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}%")
    L.append(r"}")
    L.append(r"\end{table}")
    return "\n".join(L)


def build_cat34():
    # threshold 0.10 results (re-measured 2026-06-07; was 0.15)
    df_bfm = pd.read_csv(P / "cat34_probe_linear_t010.csv")
    df_bfm = df_bfm[(df_bfm["padding"] == "zero") & (df_bfm["mode"] == "pooled")]
    df_roi = pd.read_csv(P / "cat34_probe_ROI_linear_t010.csv")
    df_roi = df_roi[df_roi["mode"] == "pooled"]
    df_ch = pd.read_csv(P / "chance_cat34_t010.csv")
    all_df = pd.concat([df_bfm, df_roi, df_ch], ignore_index=True)

    rows = []
    for (feat, init, head, task), g in all_df.groupby(["feature", "init", "head", "task"], dropna=False):
        row = {"feature": feat, "init": str(init), "head": str(head), "task": task,
               "main_mean": g["test_main"].mean(), "main_std": g["test_main"].std()}
        if task == "Cat34_multilabel":
            row["sec_mean"] = g["test_macro_f1"].mean()
            row["sec_std"]  = g["test_macro_f1"].std()
        else:
            row["sec_mean"] = g["test_top1_acc"].mean()
            row["sec_std"]  = g["test_top1_acc"].std()
        rows.append(row)
    agg = pd.DataFrame(rows)

    def lookup(feat, init, head, task):
        sub = agg[(agg["feature"] == feat) & (agg["task"] == task)]
        if init is not None:
            sub = sub[sub["init"] == str(init)]
        if head is not None:
            sub = sub[sub["head"] == str(head)]
        return sub.iloc[0] if len(sub) else None

    # Real-model rows (ROI + BFM)
    model_rows = [("ROI_Schaefer400Tian50", "n/a", "linear")]
    for feat in ["Brain-JEPA", "NeuroSTORM", "SwiFT_NewE96"]:
        for init in ["resting", "scratch"]:
            model_rows.append((feat, init, "linear"))
    # Bold comparison subset: BFM rows only (exclude ROI baseline).
    bfm_rows_cat34 = [r for r in model_rows if r[0] != "ROI_Schaefer400Tian50"]

    # Compute best per column among BFM rows only.
    cols = {
        "ml_auroc": ("Cat34_multilabel", "main_mean", "max"),
        "ml_f1":    ("Cat34_multilabel", "sec_mean",  "max"),
        "sf_r":     ("Cat34_soft",       "main_mean", "max"),
        "sf_top1":  ("Cat34_soft",       "sec_mean",  "max"),
    }
    best = {}
    for k, (task, mcol, direction) in cols.items():
        vals = []
        for feat, init, head in bfm_rows_cat34:
            r = lookup(feat, init, head, task)
            vals.append(((feat, init), None if r is None or pd.isna(r[mcol]) else float(r[mcol])))
        best[k] = find_best(vals, direction)

    def cell(r, key_mean, key_std, bold=False):
        if r is None:
            return "--"
        m = r[key_mean]; s = r[key_std]
        return fmt(None if pd.isna(m) else float(m),
                   None if pd.isna(s) else float(s),
                   bold=bold)

    L = []
    L.append(r"\begin{table}[H]\centering")
    L.append(r"\caption{Task Cat34\_multilabel (threshold 0.10 = 1/10 raters, natural unit) and Cat34\_soft. Pooled mode, linear probe only (Cat34 launched with --skip\_mlp). multilabel: macro AUROC over 34 categories + macro F1. soft: per-category Pearson r averaged over 34 categories + top1 accuracy (argmax of predicted distribution vs true argmax). mean $\pm$ std over 5 folds. Best value per column \textbf{among BFM rows} in bold (ROI baseline and chance excluded from comparison).}")
    L.append(r"\resizebox{\textwidth}{!}{%")
    L.append(r"\begin{tabular}{llcccc}")
    L.append(r"\toprule")
    L.append(r" & & \multicolumn{2}{c}{Cat34\_multilabel} & \multicolumn{2}{c}{Cat34\_soft} \\")
    L.append(r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}")
    L.append(r"Model & Init / Head & macro AUROC & macro F1 & Pearson r & top1 acc \\")
    L.append(r"\midrule")

    L.append(r"\multicolumn{6}{l}{\textit{Tier 1 baseline}} \\")
    r_ml = lookup("ROI_Schaefer400Tian50", "n/a", "linear", "Cat34_multilabel")
    r_sf = lookup("ROI_Schaefer400Tian50", "n/a", "linear", "Cat34_soft")
    key = ("ROI_Schaefer400Tian50", "n/a")
    eol = r" \\"
    roi_parts = [
        "ROI (Schaefer400+Tian50)", "linear",
        cell(r_ml, "main_mean", "main_std", bold=key in best["ml_auroc"]),
        cell(r_ml, "sec_mean",  "sec_std",  bold=key in best["ml_f1"]),
        cell(r_sf, "main_mean", "main_std", bold=key in best["sf_r"]),
        cell(r_sf, "sec_mean",  "sec_std",  bold=key in best["sf_top1"]),
    ]
    L.append(" & ".join(roi_parts) + eol)

    L.append(r"\midrule")
    L.append(r"\multicolumn{6}{l}{\textit{Tier 2 BFM (frozen)}} \\")
    for feat in ["Brain-JEPA", "NeuroSTORM", "SwiFT_NewE96"]:
        for init in ["resting", "scratch"]:
            ml = lookup(feat, init, "linear", "Cat34_multilabel")
            sf = lookup(feat, init, "linear", "Cat34_soft")
            key = (feat, init)
            feat_disp = DISPLAY[feat] if init == "resting" else ""
            bfm_parts = [
                feat_disp, init,
                cell(ml, "main_mean", "main_std", bold=key in best["ml_auroc"]),
                cell(ml, "sec_mean",  "sec_std",  bold=key in best["ml_f1"]),
                cell(sf, "main_mean", "main_std", bold=key in best["sf_r"]),
                cell(sf, "sec_mean",  "sec_std",  bold=key in best["sf_top1"]),
            ]
            L.append(" & ".join(bfm_parts) + eol)

    L.append(r"\midrule")
    L.append(r"\multicolumn{6}{l}{\textit{Chance}} \\")
    eol = r" \\"
    for head in ["stratified", "most_frequent"]:
        ml = lookup("chance", "n/a", head, "Cat34_multilabel")
        head_esc = head.replace("_", r"\_")
        a = cell(ml, 'main_mean', 'main_std')
        b = cell(ml, 'sec_mean', 'sec_std')
        L.append(f"Chance & {head_esc} & {a} & {b} & -- & --" + eol)
    for head in ["shuffled", "mean", "uniform"]:
        sf = lookup("chance", "n/a", head, "Cat34_soft")
        a = cell(sf, 'main_mean', 'main_std')
        b = cell(sf, 'sec_mean', 'sec_std')
        L.append(f"Chance & {head} & -- & -- & {a} & {b}" + eol)
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}%")
    L.append(r"}")
    L.append(r"\end{table}")
    return "\n".join(L)


tables = {
    "V_binary": build_binary("V_binary"),
    "A_binary": build_binary("A_binary"),
    "V_reg":    build_regression("V_reg"),
    "A_reg":    build_regression("A_reg"),
    "Cat34":    build_cat34(),
}
for k, v in tables.items():
    (OUT / f"table_{k}.tex").write_text(v)
    print(f"wrote {OUT / f'table_{k}.tex'} ({len(v.splitlines())} lines)")
