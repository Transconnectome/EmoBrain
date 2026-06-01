"""
SwiFT padding ablation 결과에서 best padding 을 자동 선정.

기본: per-task winner table + overall (test_main mean over task × init × head × mode × fold) winner.
출력: stdout (사람용) + simple key=value 행 (스크립트 파싱용).
"""
import argparse
from pathlib import Path
import pandas as pd

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default=str(FEELIN / "results/phase1/swift_padding_ablation*.csv"),
                    help="glob pattern. per-task split CSV 들 (swift_padding_ablation_V_binary.csv, ...) "
                         "을 자동 결합. _summary.csv 는 자동 제외.")
    ap.add_argument("--restrict_init", default=None,
                    help="resting | scratch | None (default both 평균).")
    args = ap.parse_args()

    # Per-task CSV 들 자동 결합 (_summary 제외)
    paths = sorted(p for p in Path("/").glob(args.glob.lstrip("/"))
                   if not p.stem.endswith("_summary"))
    if not paths:
        raise FileNotFoundError(f"No CSV found matching {args.glob}")
    dfs = [pd.read_csv(p, keep_default_na=False, na_values=[""]) for p in paths]
    df = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(df)} rows from {len(paths)} files:")
    for p in paths:
        print(f"  {p.name}")

    if args.restrict_init:
        df = df[df["init"] == args.restrict_init]

    print(f"\nPaddings present: {sorted(df['padding'].unique())}")
    print(f"Inits present:    {sorted(df['init'].unique())}")
    print(f"Tasks present:    {sorted(df['task'].unique())}")

    # Per-task per-padding mean test_main
    g = df.groupby(["task", "padding"])["test_main"].mean().reset_index()
    pivot = g.pivot(index="padding", columns="task", values="test_main")
    pivot["_OVERALL_MEAN"] = pivot.mean(axis=1)
    pivot = pivot.sort_values("_OVERALL_MEAN", ascending=False)
    print("\n=== Per-task mean test_main, by padding ===")
    print(pivot.to_string(float_format=lambda x: f"{x:.4f}"))

    best_padding = pivot.index[0]
    print(f"\n>>> BEST PADDING (overall mean): {best_padding}")
    print(f"    overall_mean = {pivot.loc[best_padding, '_OVERALL_MEAN']:.4f}")

    # Per-task winners
    print("\n=== Per-task winner padding ===")
    for task in sorted(df["task"].unique()):
        sub = g[g["task"] == task].sort_values("test_main", ascending=False)
        winner = sub.iloc[0]
        runners = sub.iloc[1] if len(sub) > 1 else None
        delta = (winner["test_main"] - runners["test_main"]) if runners is not None else float("nan")
        print(f"  {task:12s}: {winner['padding']:14s} {winner['test_main']:.4f}  (Δ vs 2nd = {delta:+.4f})")

    print(f"\n# Script-parseable line:")
    print(f"BEST_PADDING={best_padding}")


if __name__ == "__main__":
    main()
