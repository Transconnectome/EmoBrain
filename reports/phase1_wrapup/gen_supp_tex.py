"""
Generate supplementary.tex with full benchmark tables (all cells) per task,
plus padding ablation detail breakdowns.
"""
from pathlib import Path
import pandas as pd

REPORT_DIR = Path("/pscratch/sd/s/sjmoon/FEELIN/reports/phase1_wrapup")
RESULTS = Path("/pscratch/sd/s/sjmoon/FEELIN/results/phase1")

TASKS = ["V_binary", "A_binary", "V_reg", "A_reg"]
TASK_TITLE = {
    "V_binary": "Valence binary classification (extreme Q4 vs Q1)",
    "A_binary": "Arousal binary classification (extreme Q4 vs Q1)",
    "V_reg":    "Valence continuous regression",
    "A_reg":    "Arousal continuous regression",
}
TASK_TYPE = {"V_binary": "binary", "A_binary": "binary",
             "V_reg": "regression", "A_reg": "regression"}
MAIN_METRIC = {"V_binary": "AUROC", "A_binary": "AUROC",
               "V_reg": "Pearson r", "A_reg": "Pearson r"}
TASK_METRICS = {
    "binary":     [("test_auroc", "AUROC"), ("test_auprc", "AUPRC"), ("test_bal_acc", "balAcc")],
    "regression": [("test_pearson_r", "r"), ("test_mae", "MAE"),
                   ("test_mse", "MSE"), ("test_rmse", "RMSE")],
}


def fmt(x):
    return f"{x:.4f}" if pd.notna(x) else "--"


def latex_escape(s):
    return str(s).replace("_", r"\_").replace("&", r"\&").replace("#", r"\#")


def longtable_for_task(task: str) -> str:
    df = pd.read_csv(RESULTS / f"_benchmark_{task}.csv", keep_default_na=False, na_values=[""])
    ttype = TASK_TYPE[task]
    mets = TASK_METRICS[ttype]
    mets = [(m, sh) for (m, sh) in mets if f"{m}_mean" in df.columns]

    # Column spec: rank, feature, init, padding, head, mode, then [mu, sigma] per metric, count
    n_metric_cols = 2 * len(mets)
    # Tighter siunitx for narrower columns; use r l l l l l + S cols + r
    col_spec = "r l l l l l " + ("S[table-format=1.4,table-column-width=1.05cm] " * n_metric_cols) + "r"

    header_top = (f"\\# & Feature & Init & Padding & Head & Mode "
                  + "".join([f"& \\multicolumn{{2}}{{c}}{{{sh}}} " for (_, sh) in mets])
                  + "& n")
    header_sub = ("  &         &      &         &      &      "
                  + "".join([" & {$\\mu$} & {$\\sigma$}" for _ in mets])
                  + " &  ")

    lines = []
    lines.append(r"\scriptsize")
    lines.append(r"\setlength{\tabcolsep}{3pt}")
    lines.append(r"\begin{longtable}{" + col_spec + r"}")
    lines.append(r"\caption{" + f"Full benchmark for {latex_escape(task)} ({TASK_TITLE[task]}). "
                 + f"Main metric: {MAIN_METRIC[task]}. Cells sorted by main metric within category."
                 + r"} \label{tab:supp-" + task.replace("_", "-") + r"}\\")
    lines.append(r"\toprule")
    lines.append(header_top + r" \\")
    lines.append(header_sub + r" \\")
    lines.append(r"\midrule")
    lines.append(r"\endfirsthead")
    lines.append(r"\multicolumn{" + str(7 + n_metric_cols) + "}{l}{\\small\\itshape continued from previous page} \\\\")
    lines.append(r"\toprule")
    lines.append(header_top + r" \\")
    lines.append(header_sub + r" \\")
    lines.append(r"\midrule")
    lines.append(r"\endhead")
    lines.append(r"\midrule \multicolumn{" + str(7 + n_metric_cols) + "}{r}{\\small\\itshape continued on next page} \\\\")
    lines.append(r"\endfoot")
    lines.append(r"\bottomrule")
    lines.append(r"\endlastfoot")

    # group by category, emit subsection header rows
    for category in ("brain", "video"):
        sub = df[df["category"] == category]
        if len(sub) == 0:
            continue
        label = "Brain models (fMRI input)" if category == "brain" else "Video models (stimulus features)"
        lines.append(r"\multicolumn{" + str(7 + n_metric_cols) + r"}{l}{\textit{" + label + r"}} \\")
        for _, row in sub.iterrows():
            cells = [
                str(int(row["rank"])),
                latex_escape(row["feature"]),
                latex_escape(row["init"]),
                latex_escape(row["padding"]),
                latex_escape(row["head"]),
                latex_escape(row["mode"]),
            ]
            for (m, _) in mets:
                cells.append(fmt(row[f"{m}_mean"]))
                cells.append(fmt(row[f"{m}_std"]))
            cells.append(str(int(row["n_eval"])))
            lines.append(" & ".join(cells) + r" \\")
        lines.append(r"\midrule")
    # Replace last \midrule with bottomrule via removing it (longtable adds bottomrule via endlastfoot)
    if lines[-1] == r"\midrule":
        lines.pop()
    lines.append(r"\end{longtable}")
    lines.append(r"\normalsize")
    return "\n".join(lines)


def padding_ablation_detail() -> str:
    """Detailed padding ablation broken out by init, head, mode."""
    # Build from raw padding ablation CSVs
    dfs = []
    for t in TASKS:
        for src in [f"swift_padding_ablation_{t}.csv", f"swift_padding_cyclic_only_{t}.csv"]:
            p = RESULTS / src
            if p.exists():
                d = pd.read_csv(p, keep_default_na=False, na_values=[""])
                dfs.append(d)
    df = pd.concat(dfs, ignore_index=True)
    df = df[df["task"].isin(TASKS)]
    # group
    g = df.groupby(["task", "padding", "init", "head", "mode"], dropna=False).agg(
        mean=("test_main", "mean"), std=("test_main", "std")
    ).reset_index()

    pads = ["mean", "replicate", "zero", "spatial_only", "cyclic_replicate"]
    pads_disp = [p.replace("_", r"\_") for p in pads]
    out_lines = []
    out_lines.append(r"\scriptsize")
    out_lines.append(r"\setlength{\tabcolsep}{4pt}")
    out_lines.append(r"\begin{longtable}{l l l l " + "S[table-format=1.4] " * len(pads) + "}")
    out_lines.append(r"\caption{SwiFT NewE96 padding ablation, broken out by init, head, and mode. "
                     r"Each cell is the mean test\_main across 5 folds (and 5 subjects for per\_subject mode)."
                     r"} \label{tab:supp-padding-detail}\\")
    out_lines.append(r"\toprule")
    out_lines.append("Task & Init & Head & Mode "
                     + "".join([f"& {{{p}}} " for p in pads_disp]) + r"\\")
    out_lines.append(r"\midrule")
    out_lines.append(r"\endfirsthead")
    out_lines.append(r"\toprule")
    out_lines.append("Task & Init & Head & Mode "
                     + "".join([f"& {{{p}}} " for p in pads_disp]) + r"\\")
    out_lines.append(r"\midrule")
    out_lines.append(r"\endhead")
    out_lines.append(r"\bottomrule")
    out_lines.append(r"\endlastfoot")
    last_task = None
    for (task, init, head, mode), gg in g.groupby(["task", "init", "head", "mode"]):
        if task != last_task and last_task is not None:
            out_lines.append(r"\midrule")
        last_task = task
        cells = [latex_escape(task), latex_escape(init), latex_escape(head), latex_escape(mode)]
        for p in pads:
            row = gg[gg["padding"] == p]
            cells.append(fmt(row["mean"].values[0]) if len(row) else "--")
        out_lines.append(" & ".join(cells) + r"\\")
    out_lines.append(r"\end{longtable}")
    out_lines.append(r"\normalsize")
    return "\n".join(out_lines)


def chance_table() -> str:
    d = pd.read_csv(RESULTS / "chance_baseline_summary.csv", keep_default_na=False, na_values=[""])
    d = d[d["task"].isin(TASKS)]
    lines = []
    lines.append(r"\begin{table}[h]")
    lines.append(r"\centering")
    lines.append(r"\caption{Chance baselines per task, by dummy-predictor strategy. Stratified rows are averaged over 3 seeds.} \label{tab:chance}")
    lines.append(r"\small")
    lines.append(r"\begin{tabular}{l l S[table-format=1.4] S[table-format=1.4] r}")
    lines.append(r"\toprule")
    lines.append("Task & Head & {$\\mu$} & {$\\sigma$} & n \\\\")
    lines.append(r"\midrule")
    for _, row in d.iterrows():
        cells = [latex_escape(row["task"]), latex_escape(row["head"]),
                 fmt(row["test_main_mean"]), fmt(row["test_main_std"]), str(int(row["count"]))]
        lines.append(" & ".join(cells) + r"\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    return "\n".join(lines)


def main():
    parts = []
    parts.append(r"""\documentclass[10pt, a4paper, landscape]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=1.3cm]{geometry}
\usepackage{microtype}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{makecell}
\usepackage{caption}
\usepackage{xcolor}
\usepackage{siunitx}
\sisetup{detect-all, table-format=1.4}
\usepackage{fancyhdr}
\usepackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=black, citecolor=blue!50!black, urlcolor=blue!50!black}
\pagestyle{fancy}
\fancyhf{}
\rhead{\small FEELIN Phase 1 Supplementary Material}
\rfoot{\thepage}
\setlength{\parskip}{4pt}
\setlength{\parindent}{0pt}
\title{\vspace{-2em}\textbf{Supplementary Material}\\
       \large Full benchmark tables for FEELIN Phase 1 frozen-probe report}
\author{}
\date{2026-05-27}
\begin{document}
\maketitle
\thispagestyle{fancy}

\section{Chance baselines}
""")
    parts.append(chance_table())

    parts.append(r"""
\section{Per-task full benchmark}
All cells are reported. Within each category (brain, video) rows are sorted by the main
metric (AUROC for binary, Pearson $r$ for regression). The $n$ column shows the number of
underlying fold $\times$ seed (or, for per\_subject mode, fold $\times$ seed $\times$ subject)
fits that were averaged.
""")
    for task in TASKS:
        parts.append(r"\subsection{" + latex_escape(task) + r"}")
        parts.append(longtable_for_task(task))

    parts.append(r"""
\section{SwiFT padding ablation -- detailed breakdown}
The aggregate padding ablation in the main report averages across init, head, and mode.
Table~\ref{tab:supp-padding-detail} below shows the same data broken out by every
combination, in case patterns differ between subject-conditional and pooled modes or
between heads.
""")
    parts.append(padding_ablation_detail())

    parts.append(r"\end{document}")

    out = REPORT_DIR / "supplementary.tex"
    out.write_text("\n".join(parts))
    print(f"Wrote {out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
