"""
5-fold stim-stratified split 생성.

각 stimulus 가 fold 1..5 중 하나에 배정.
Stratification: V quartile × A quartile joint label (16 cell).
같은 stimulus 는 모든 subject 에서 같은 fold (stim-level leakage 없음).

For each outer fold k in 1..5:
  test = stim where fold == k
  val  = stim where fold == (k % 5) + 1   (rotational, 다음 fold)
  train = 나머지 3 fold

Output: data/horikawa_5fold.csv (stimulus_num, fold)
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

DATA = Path("/pscratch/sd/s/sjmoon/FEELIN/data")
SEED = 0

def main():
    canon = pd.read_csv(DATA / "feelin_canonical_stimuli.csv")
    canon["joint_label"] = canon["v_quartile"].astype(str) + "_" + canon["a_quartile"].astype(str)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    fold_arr = np.zeros(len(canon), dtype=np.int64)
    for fold_idx, (_, test_idx) in enumerate(skf.split(canon, canon["joint_label"])):
        fold_arr[test_idx] = fold_idx + 1  # 1-indexed

    canon["fold"] = fold_arr
    out = canon[["stimulus_num", "fold"]].copy()
    out_path = DATA / "horikawa_5fold.csv"
    out.to_csv(out_path, index=False)
    print(f"Saved {out_path}")
    print(f"\nFold distribution:")
    print(canon["fold"].value_counts().sort_index().to_string())
    print(f"\nV quartile per fold:")
    print(pd.crosstab(canon["v_quartile"], canon["fold"], normalize="columns").round(3).to_string())
    print(f"\nA quartile per fold:")
    print(pd.crosstab(canon["a_quartile"], canon["fold"], normalize="columns").round(3).to_string())


if __name__ == "__main__":
    main()
