"""V/A quartile (Q1 vs Q4) split helper.

Phase 1 의 binary classification task 와 동일 정의. valence (또는 arousal) 의
z-score 분포에서 25 percentile 미만 = Q1 (label 0), 75 percentile 이상 = Q4 (label 1),
가운데 (Q2 + Q3) = OTHER (학습/평가에서 mask 처리).

D1, D2 의 binary head + V_binary / A_binary metric 의 ground truth.

권장 사용. train fold 의 sample 분포로 q25, q75 를 계산하고, 동일 threshold 를
train + val + test 에 적용 (fold-internal split 의 robust evaluation).

Output columns appended to va_targets_csv:
  valence_quartile : {Q1, Q4, OTHER}
  arousal_quartile : {Q1, Q4, OTHER}
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def label_quartile(values: np.ndarray, q25: float, q75: float) -> np.ndarray:
    out = np.full(values.shape, "OTHER", dtype="<U5")
    out[values <= q25] = "Q1"
    out[values >= q75] = "Q4"
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--va-csv", required=True, help="input csv with columns stim_id, valence_z, arousal_z")
    p.add_argument("--manifest-csv", required=False, help="fold manifest (with fold{F}_split=='train' rows) for fitting q25/q75")
    p.add_argument("--fold", type=int, default=1)
    p.add_argument("--out-csv", required=True)
    args = p.parse_args()

    df = pd.read_csv(args.va_csv)
    if args.manifest_csv:
        manifest = pd.read_csv(args.manifest_csv)
        train_ids = set(manifest.loc[manifest[f"fold{args.fold}_split"] == "train", "stim_id"])
        fit = df[df["stim_id"].isin(train_ids)]
    else:
        fit = df

    v_q25, v_q75 = float(np.percentile(fit["valence_z"], 25)), float(np.percentile(fit["valence_z"], 75))
    a_q25, a_q75 = float(np.percentile(fit["arousal_z"], 25)), float(np.percentile(fit["arousal_z"], 75))

    df["valence_quartile"] = label_quartile(df["valence_z"].to_numpy(), v_q25, v_q75)
    df["arousal_quartile"] = label_quartile(df["arousal_z"].to_numpy(), a_q25, a_q75)

    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_csv, index=False)
    print(
        f"[quartile-split] v: q25={v_q25:.3f} q75={v_q75:.3f} | a: q25={a_q25:.3f} q75={a_q75:.3f}\n"
        f"  fitted on {len(fit)} train stim. assigned to {len(df)} total stim.\n"
        f"  valence  Q1={(df.valence_quartile=='Q1').sum()} Q4={(df.valence_quartile=='Q4').sum()} OTHER={(df.valence_quartile=='OTHER').sum()}\n"
        f"  arousal  Q1={(df.arousal_quartile=='Q1').sum()} Q4={(df.arousal_quartile=='Q4').sum()} OTHER={(df.arousal_quartile=='OTHER').sum()}\n"
        f"  -> {args.out_csv}"
    )


if __name__ == "__main__":
    main()
