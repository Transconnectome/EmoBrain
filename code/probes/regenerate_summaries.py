"""
이미 완성된 per-row CSV (results/phase1/*.csv) 들에 대해 풍부한 summary CSV 를
다시 생성한다. 기존 *_summary.csv 는 덮어쓰기.

새 schema (모든 test_* metric 의 mean + std + count):
  feature, init, padding, task, task_type, main_metric, head, mode, subject,
  test_main_mean, test_main_std,
  test_auroc_mean, test_auroc_std,    # binary 만 의미
  test_auprc_mean, test_auprc_std,
  test_bal_acc_mean, test_bal_acc_std,
  test_pearson_r_mean, test_pearson_r_std,   # regression
  test_mae_mean, test_mae_std,
  test_mse_mean, test_mse_std,
  test_rmse_mean, test_rmse_std,
  ... 등 raw CSV 에 있는 모든 test_* numeric column,
  count
"""
import sys
from pathlib import Path

from _summary_helper import summarize_probe_csv

RESULTS = Path("/pscratch/sd/s/sjmoon/FEELIN/results/phase1")


def main():
    # raw CSV 후보: *_summary.csv 가 아닌 모든 .csv
    raws = sorted([
        p for p in RESULTS.glob("*.csv")
        if not p.stem.endswith("_summary")
    ])
    print(f"Found {len(raws)} raw CSV files in {RESULTS}\n")

    for raw in raws:
        summary_path = raw.with_name(f"{raw.stem}_summary.csv")
        try:
            summary = summarize_probe_csv(str(raw), str(summary_path))
            print(f"  ✓ {raw.name:55s} → {summary_path.name}  ({len(summary)} cells, {len(summary.columns)} cols)")
        except Exception as e:
            print(f"  ✗ {raw.name:55s} FAILED: {e}")


if __name__ == "__main__":
    main()
