"""
Shared summary aggregation for EmoBrain probe results.

Takes a per-row CSV (one row per fold × seed × subject × condition) and writes
a wide-format summary CSV with mean + std + count for ALL test_* numeric metrics.

User requirement (2026-05-26):
  - Per-fold split-level columns 필요 없음 (raw CSV 에 이미 있음)
  - Summary 는 모든 metric (test_auroc, test_pearson_r, test_mae, test_mse 등) 의
    mean + std across folds/seeds 가 한 row 에 다 보여야 함.

Output schema:
  - group cols: feature, init, padding, task, task_type, main_metric, head, mode, subject
  - per metric: {metric}_mean, {metric}_std
  - count column at the end (= number of fold×seed combinations averaged)
"""
import numpy as np
import pandas as pd

# Group axis = 결과 condition. fold + seed 만 평균 dimension.
GROUP_COLS = [
    "feature", "init", "padding", "task", "task_type", "main_metric",
    "head", "mode", "subject",
]

# Skipped: list-encoded strings (per_dim 같은 array) 와 non-numeric meta
SKIP_METRIC_COLS = {
    "test_pearson_r_per_dim",   # list 형태로 string 저장됨
    "test_main",                # 어차피 task 별 main metric 이라 redundant. keep mean separately.
}


def summarize_probe_csv(raw_csv_path: str, summary_csv_path: str):
    # keep_default_na=False: "n/a" / "NA" / "" 같은 string 을 NaN 으로 자동변환 안 함.
    # 그래야 init="n/a" 같은 ROI/video/chance row 가 groupby 에서 살아남음.
    df = pd.read_csv(raw_csv_path, keep_default_na=False, na_values=[""])

    # Group cols 중 실제 존재하는 것만 사용
    grp = [c for c in GROUP_COLS if c in df.columns]

    # 모든 test_* 컬럼 중 numeric 인 것
    metric_cols = []
    for c in df.columns:
        if not c.startswith("test_"):
            continue
        if c in SKIP_METRIC_COLS:
            continue
        # numeric check
        if pd.api.types.is_numeric_dtype(df[c]):
            metric_cols.append(c)

    # test_main 은 그대로 mean/std/count 포함시켜야 main_metric 빠르게 보기 좋음
    if "test_main" in df.columns and "test_main" not in metric_cols:
        metric_cols.insert(0, "test_main")

    # Aggregate: 각 metric 별로 mean, std (NaN ok if all-NaN column)
    agg_dict = {c: ["mean", "std"] for c in metric_cols}
    summary = df.groupby(grp).agg(agg_dict)
    # Flatten MultiIndex columns: ("test_auroc", "mean") → "test_auroc_mean"
    summary.columns = [f"{m}_{stat}" for (m, stat) in summary.columns]
    summary = summary.reset_index()

    # count 추가 (fold × seed 조합 수)
    count = df.groupby(grp).size().reset_index(name="count")
    summary = summary.merge(count, on=grp, how="left")

    summary.to_csv(summary_csv_path, index=False)
    return summary
