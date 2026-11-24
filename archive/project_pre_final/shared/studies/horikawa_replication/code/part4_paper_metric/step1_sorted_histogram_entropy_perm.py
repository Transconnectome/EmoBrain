"""Stage B. Paper-style cluster quality metric (Horikawa et al. 2020, Figure 6 D/E).

For each (cluster labels, Cowen 34 emotion score),
  1. top-5% high-score samples per emotion (~109 samples if N=2185)
  2. distribution of those 109 samples across K clusters
  3. sort histogram descending -> "sorted cluster index"
  4. entropy of distribution (low entropy = clean cluster, high = scattered)
  5. permutation null: random assignment of 109 samples to K clusters, repeated 100k times.
     Compare observed entropy to null entropy distribution (p_perm).

Used together with silhouette/NMI to compare with paper. Paper uses K=27 main + K=15, 50 supp.

Output. results/clustering/paper_metric_<run_tag>.csv with one row per (source, setting, emotion).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/pscratch/sd/s/sjmoon/EmoBrain")
OUT_ROOT = REPO / "project" / "shared" / "studies" / "horikawa_replication" / "results"
LABELS_CSV = REPO / "project" / "shared" / "data" / "cowen_horikawa_labels.csv"

N_PERM = 100_000
TOP_PCT = 0.05


def load_cowen_labels() -> dict:
    df = pd.read_csv(LABELS_CSV)
    df = df.sort_values("stim_idx").reset_index(drop=True)
    cat34 = df[[f"score_{i}" for i in range(34)]].to_numpy(dtype=np.float32)
    return {"cat34_soft": cat34}


def entropy_of_hist(counts: np.ndarray) -> float:
    p = counts / max(counts.sum(), 1)
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))


def permutation_null_entropy(n_samples: int, k: int, n_perm: int = N_PERM, rng_seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(rng_seed)
    out = np.zeros(n_perm, dtype=np.float32)
    for i in range(n_perm):
        assign = rng.integers(0, k, size=n_samples)
        counts = np.bincount(assign, minlength=k)
        out[i] = entropy_of_hist(counts)
    return out


def paper_metric_one(labels: np.ndarray, cat34_soft: np.ndarray, perm_cache: dict) -> pd.DataFrame:
    """labels: (N,) cluster id, cat34_soft: (N, 34) soft emotion ratings."""
    N, K = len(labels), len(np.unique(labels[labels != -1]))
    if K < 2:
        return pd.DataFrame()
    top_n = max(1, int(round(N * TOP_PCT)))
    rows = []
    if K not in perm_cache:
        perm_cache[K] = permutation_null_entropy(top_n, K, rng_seed=0)
    null = perm_cache[K]
    for e in range(cat34_soft.shape[1]):
        order = np.argsort(-cat34_soft[:, e])[:top_n]
        sel_lab = labels[order]
        counts = np.bincount(sel_lab[sel_lab != -1], minlength=K)
        sorted_counts = np.sort(counts)[::-1]
        ent = entropy_of_hist(counts)
        p = float((null <= ent).mean())
        rows.append({
            "emotion_idx": e,
            "K": K,
            "top1_cluster_count": int(sorted_counts[0]),
            "top1_cluster_pct": float(sorted_counts[0] / top_n),
            "top3_cluster_pct": float(sorted_counts[:3].sum() / top_n),
            "entropy": ent,
            "null_mean": float(null.mean()),
            "p_perm": p,
        })
    return pd.DataFrame(rows)


def run_dir_iter(root: Path):
    """Yield (source_tag, setting_name, labels_path) for every labels.csv."""
    for src_dir in sorted(root.iterdir()):
        if not src_dir.is_dir() or src_dir.name.startswith("_") or src_dir.name == "figures" or src_dir.name == "per_subject":
            continue
        for setting_dir in sorted(src_dir.iterdir()):
            if not setting_dir.is_dir():
                continue
            lab = setting_dir / "labels.csv"
            if lab.exists():
                yield src_dir.name, setting_dir.name, lab


def per_subject_iter(root: Path):
    ps = root / "per_subject"
    if not ps.exists():
        return
    for tag_dir in sorted(ps.iterdir()):
        if not tag_dir.is_dir():
            continue
        for setting_dir in sorted(tag_dir.iterdir()):
            if not setting_dir.is_dir():
                continue
            lab = setting_dir / "labels.csv"
            if lab.exists():
                yield tag_dir.name, setting_dir.name, lab


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ks", nargs="+", type=int, default=[15, 27, 50],
                   help="K values to evaluate (paper default 15/27/50)")
    p.add_argument("--include-per-subject", action="store_true")
    p.add_argument("--out-csv", default=str(OUT_ROOT / "paper_metric.csv"))
    args = p.parse_args()

    cowen = load_cowen_labels()
    cat34 = cowen["cat34_soft"]

    perm_cache = {}
    all_rows = []
    iters = [run_dir_iter(OUT_ROOT)]
    if args.include_per_subject:
        iters.append(per_subject_iter(OUT_ROOT))
    for it in iters:
        for src, setting, lab_path in it:
            if setting.startswith("hdbscan"):
                continue
            try:
                k_in_setting = int(setting.split("_K")[-1])
            except ValueError:
                continue
            if k_in_setting not in args.ks:
                continue
            labels = pd.read_csv(lab_path)["cluster_id"].to_numpy()
            df_em = paper_metric_one(labels, cat34, perm_cache)
            df_em.insert(0, "setting", setting)
            df_em.insert(0, "source", src)
            all_rows.append(df_em)
            print(f"[paper-metric] {src}/{setting}: K={k_in_setting} "
                  f"mean_entropy={df_em['entropy'].mean():.3f} "
                  f"mean_p_perm={df_em['p_perm'].mean():.4f} "
                  f"n_emo_sig(p<0.01)={int((df_em['p_perm']<0.01).sum())}/34", flush=True)
    df = pd.concat(all_rows, ignore_index=True)
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_csv, index=False)
    print(f"[paper-metric] wrote {len(df)} rows to {args.out_csv}")


if __name__ == "__main__":
    main()
