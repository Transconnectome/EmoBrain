"""
EmoBrain Phase 1 — benchmark table (per task, comprehensive).

각 task 마다 모든 (feature × init × padding × head × mode) cell 의
main metric + secondary metric (mean ± std across 5 fold × subjects) 표 생성.

Output (per task):
  results/phase1/_benchmark_<task>.csv   — full machine-readable
  results/phase1/_benchmark_<task>.md    — paper-ready markdown
  results/phase1/_benchmark_ALL.md       — 4 task concat single doc
"""
from pathlib import Path
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

EmoBrain = Path("/pscratch/sd/s/sjmoon/EmoBrain")
RESULTS = EmoBrain / "project/shared/results/phase1"

TASKS = ["V_binary", "A_binary", "V_reg", "A_reg"]
TASK_TITLE = {
    "V_binary": "Valence binary (extreme Q4 vs Q1 of self-rating)",
    "A_binary": "Arousal binary (extreme Q4 vs Q1 of self-rating)",
    "V_reg":    "Valence continuous regression (self-rating)",
    "A_reg":    "Arousal continuous regression (self-rating)",
}
# Task type → ordered metric list for display
TASK_METRICS = {
    "binary":      ["test_auroc", "test_auprc", "test_bal_acc"],
    "regression":  ["test_pearson_r", "test_mae", "test_mse", "test_rmse"],
}
TASK_TYPE = {"V_binary": "binary", "A_binary": "binary",
             "V_reg": "regression", "A_reg": "regression"}
TASK_MAIN = {"V_binary": "test_auroc", "A_binary": "test_auroc",
             "V_reg": "test_pearson_r", "A_reg": "test_pearson_r"}

# Brain (fMRI 입력) vs Video (자극 feature 입력) 분리
BRAIN_FEATURES = {
    "chance", "ROI_Schaefer400Tian50",
    "SwiFT_NewE96", "Brain-JEPA", "NeuroSTORM",
    # SwiFT 5 variants (Phase 1 Appendix)
    "SwiFT_NewE36", "SwiFT_NewE192",
    "SwiFT_UAH_5M", "SwiFT_UAH_51M", "SwiFT_UAH_202M",
}
VIDEO_FEATURES_PREFIX = ("V-JEPA2", "CLIP", "DINOv2", "VideoMAE", "Qwen-VL")


def categorize(feature: str) -> str:
    """Return 'brain' or 'video' or 'other'."""
    if feature in BRAIN_FEATURES:
        return "brain"
    if feature.startswith("SwiFT_"):
        return "brain"
    if any(feature.startswith(p) for p in VIDEO_FEATURES_PREFIX):
        return "video"
    return "other"

# Source CSV (raw per-row). Use combined where available, per-task otherwise.
SOURCE_FILES = [
    # chance
    "chance_baseline.csv",
    # Tier 1
    "bfm_probe_ROI_Schaefer400Tian50.csv",
    # Tier 2 BFM (main + cyclic + padding ablation)
    "bfm_probe_SwiFT_NewE96.csv",
    "bfm_probe_Brain-JEPA_V_binary.csv",
    "bfm_probe_Brain-JEPA_A_binary.csv",
    "bfm_probe_Brain-JEPA_V_reg.csv",
    "bfm_probe_Brain-JEPA_A_reg.csv",
    "bfm_probe_NeuroSTORM.csv",
    "swift_padding_ablation_V_binary.csv",
    "swift_padding_ablation_A_binary.csv",
    "swift_padding_ablation_V_reg.csv",
    "swift_padding_ablation_A_reg.csv",
    "swift_padding_cyclic_only_V_binary.csv",
    "swift_padding_cyclic_only_A_binary.csv",
    "swift_padding_cyclic_only_V_reg.csv",
    "swift_padding_cyclic_only_A_reg.csv",
    # SwiFT 5 variants (zero padding) per-task
    "bfm_probe_SwiFT_NewE36_zero_V_binary.csv",
    "bfm_probe_SwiFT_NewE36_zero_A_binary.csv",
    "bfm_probe_SwiFT_NewE36_zero_V_reg.csv",
    "bfm_probe_SwiFT_NewE36_zero_A_reg.csv",
    "bfm_probe_SwiFT_NewE192_zero_V_binary.csv",
    "bfm_probe_SwiFT_NewE192_zero_A_binary.csv",
    "bfm_probe_SwiFT_NewE192_zero_V_reg.csv",
    "bfm_probe_SwiFT_NewE192_zero_A_reg.csv",
    "bfm_probe_SwiFT_UAH_5M_zero_V_binary.csv",
    "bfm_probe_SwiFT_UAH_5M_zero_A_binary.csv",
    "bfm_probe_SwiFT_UAH_5M_zero_V_reg.csv",
    "bfm_probe_SwiFT_UAH_5M_zero_A_reg.csv",
    "bfm_probe_SwiFT_UAH_51M_zero_V_binary.csv",
    "bfm_probe_SwiFT_UAH_51M_zero_A_binary.csv",
    "bfm_probe_SwiFT_UAH_51M_zero_V_reg.csv",
    "bfm_probe_SwiFT_UAH_51M_zero_A_reg.csv",
    "bfm_probe_SwiFT_UAH_202M_zero_V_binary.csv",
    "bfm_probe_SwiFT_UAH_202M_zero_A_binary.csv",
    "bfm_probe_SwiFT_UAH_202M_zero_V_reg.csv",
    "bfm_probe_SwiFT_UAH_202M_zero_A_reg.csv",
    # Tier 3 video
    "video_probe_V-JEPA2.csv",
    "video_probe_CLIP.csv",
    "video_probe_DINOv2.csv",
    "video_probe_VideoMAE.csv",
    "video_probe_Qwen-VL_caption.csv",
]


def load_all() -> pd.DataFrame:
    dfs = []
    for f in SOURCE_FILES:
        p = RESULTS / f
        if not p.exists():
            print(f"  [WARN] missing {p.name}")
            continue
        d = pd.read_csv(p, keep_default_na=False, na_values=[""])
        d["source_file"] = f
        dfs.append(d)
    return pd.concat(dfs, ignore_index=True)


def make_task_table(df: pd.DataFrame, task: str) -> pd.DataFrame:
    """Per-task benchmark: one row per (feature, init, padding, head, mode);
    aggregate mean+std for all metrics across fold + seed + subject.
    카테고리 (brain/video) 컬럼 추가."""
    sub = df[df["task"] == task].copy()
    ttype = TASK_TYPE[task]
    metrics = TASK_METRICS[ttype]

    # 존재하는 metric col 만
    metrics = [m for m in metrics if m in sub.columns]

    grp = ["feature", "init", "padding", "head", "mode"]
    agg_dict = {m: ["mean", "std"] for m in metrics}
    g = sub.groupby(grp, dropna=False).agg(agg_dict)
    g.columns = [f"{m}_{stat}" for (m, stat) in g.columns]
    g = g.reset_index()
    # count
    cnt = sub.groupby(grp, dropna=False).size().reset_index(name="n_eval")
    g = g.merge(cnt, on=grp, how="left")

    # Category
    g["category"] = g["feature"].apply(categorize)

    # Sort by main metric mean desc within each category
    main_mean = f"{TASK_MAIN[task]}_mean"
    if main_mean in g.columns:
        g = g.sort_values(["category", main_mean], ascending=[True, False]).reset_index(drop=True)
    # rank within category
    g["rank"] = g.groupby("category").cumcount() + 1
    # reorder columns
    cols_front = ["category", "rank", "feature", "init", "padding", "head", "mode"]
    rest = [c for c in g.columns if c not in cols_front]
    g = g[cols_front + rest]
    return g


def _format_section(df: pd.DataFrame, task: str, metrics: list, section_title: str) -> str:
    """One category section (brain or video) as markdown table."""
    metric_short = {"test_auroc": "AUROC", "test_auprc": "AUPRC", "test_bal_acc": "balAcc",
                    "test_pearson_r": "r", "test_mae": "MAE", "test_mse": "MSE", "test_rmse": "RMSE"}
    d = df.copy()
    fmt = lambda x: f"{x:.4f}" if pd.notna(x) else "—"
    for c in d.columns:
        if c.startswith("test_"):
            d[c] = d[c].map(fmt)
    d["n_eval"] = d["n_eval"].astype(int)

    headers = ["#", "feature", "init", "padding", "head", "mode"]
    for m in metrics:
        headers.append(f"{metric_short[m]} μ")
        headers.append(f"{metric_short[m]} σ")
    headers.append("n")

    lines = []
    lines.append(f"#### {section_title} ({len(d)} cells)")
    lines.append("")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for _, row in d.iterrows():
        cells = [str(row["rank"]), str(row["feature"]), str(row["init"]),
                 str(row["padding"]), str(row["head"]), str(row["mode"])]
        for m in metrics:
            cells.append(str(row[f"{m}_mean"]))
            cells.append(str(row[f"{m}_std"]))
        cells.append(str(row["n_eval"]))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def to_markdown(df: pd.DataFrame, task: str) -> str:
    """Per-task markdown with BRAIN section + VIDEO section."""
    ttype = TASK_TYPE[task]
    metrics = [m for m in TASK_METRICS[ttype] if f"{m}_mean" in df.columns]

    lines = []
    lines.append(f"### {task} — {TASK_TITLE[task]}")
    lines.append("")
    # BRAIN section
    brain = df[df["category"] == "brain"]
    if len(brain):
        lines.append(_format_section(brain, task, metrics,
                                     "🧠 Brain models (fMRI input: chance + ROI floor + BFM)"))
    # VIDEO section
    video = df[df["category"] == "video"]
    if len(video):
        lines.append(_format_section(video, task, metrics,
                                     "🎬 Video models (stimulus feature input)"))
    return "\n".join(lines)


def main():
    print("=== Loading all raw CSVs ===")
    df = load_all()
    df = df[df["task"].isin(TASKS)].copy()
    print(f"  rows after task filter: {len(df)}")

    all_md_lines = [
        "# EmoBrain Phase 1 — Benchmark Tables (per task)",
        "",
        "**Protocol**: 5-fold stim-stratified CV × 1 seed (linear deterministic, MLP also 1 seed). "
        "Cells aggregated across fold × seed × subject (for per_subject mode 5 subj averaged).",
        "",
        "**Group cols**: feature × init × padding × head × mode.",
        "",
        "**Per task** sorted by main metric mean (AUROC for binary, Pearson r for regression).",
        "",
        f"**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
    ]

    for task in TASKS:
        print(f"\n=== {task} ===")
        t = make_task_table(df, task)
        out_csv = RESULTS / f"_benchmark_{task}.csv"
        t.to_csv(out_csv, index=False)
        out_md = RESULTS / f"_benchmark_{task}.md"
        md_full = to_markdown(t, task)
        out_md.write_text(md_full)
        print(f"  saved {out_csv.name}  ({len(t)} cells)")
        print(f"  saved {out_md.name}")
        all_md_lines.append(md_full)
        all_md_lines.append("\n---\n")

    out_all = RESULTS / "_benchmark_ALL.md"
    out_all.write_text("\n".join(all_md_lines))
    print(f"\n[done] combined: {out_all}")
    print(f"        ({out_all.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
