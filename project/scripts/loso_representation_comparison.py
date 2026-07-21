"""Why use a BFM instead of ridge on ROI mean? Test the cross-subject axis.

Within subject, everything saturates at ~0.32 (Stage 0 R0, confirmed across time
resolution, spatial resolution and model nonlinearity). So the justification for
a brain foundation model cannot come from within-subject accuracy. It has to come
from something ridge on ROI mean structurally cannot do.

The first candidate is CROSS-SUBJECT GENERALISATION. Ridge on ROI mean memorises
one subject's 450-ROI to 34D mapping and collapses when transferred
(within 0.307 -> LOSO 0.232, retention 0.76). A foundation model pretrained over
many subjects may carry a subject-invariant representation. If its LOSO retention
is clearly higher, that IS the reason to use it, even at equal within-subject
accuracy.

Regimes (identical to project/scripts/ridge_subject_regimes.py so the numbers are
directly comparable).
    within   train on subject s, test on subject s.        mean over 5 subjects
    pooled   train on all 5, test on all 5.
    loso     train on 4 subjects, test on the held-out one. mean over 5 folds

Every representation is served through the same BFMSource interface, including
the ROI mean baseline (`roi_schaefer400tian50_mean`), so nothing differs but the
representation itself.

Headline. `retention = loso / within`. Also reports CCC, RSA and rare-emotion
recovery, because a representation can be worth using for structure preservation
even at equal profile correlation.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/loso_representation_comparison.sh
    bash .../loso_representation_comparison.sh roi_schaefer400tian50_mean swift_NewE96_SL20_resting_pad-zero
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402

from project.data.bfm_source import BFMSource  # noqa: E402
from project.data.fmri_adapter import SUBJECTS  # noqa: E402
from project.data.labels import Cowen34Normalizer  # noqa: E402
from project.evaluation.metrics import compute_metrics  # noqa: E402

DATA = REPO_ROOT / "project" / "shared" / "data"
EMB_ROOT = REPO_ROOT / "project" / "shared" / "output" / "embeddings"
OUT = REPO_ROOT / "project" / "shared" / "results" / "loso_representation_comparison.json"
SCORE_COLS = [f"score_{k}" for k in range(34)]
ALPHAS = [1.0, 10.0, 100.0, 1000.0, 10000.0]
ROI_BASELINE = "roi_schaefer400tian50_mean"
N_RARE = 10


def load_rep(variant: str, parts: dict, labels, norm):
    """variant -> {subject: {split: (X, Yz)}}. Same interface for every rep."""
    src = BFMSource(variant, root=EMB_ROOT)
    data = {}
    for subj in SUBJECTS:
        data[subj] = {}
        for sp, stims in parts[subj].items():
            X = np.stack([np.asarray(src.get(subj, s)).ravel() for s in stims]).astype(np.float64)
            raw = np.stack([labels.loc[s, SCORE_COLS].to_numpy(np.float64) for s in stims])
            data[subj][sp] = (X, np.asarray(norm.transform(raw), dtype=np.float64))
    return data


def fit_eval(Xtr, Ytr, Xva, Yva, Xte, Yte, rare_idx, full=False):
    best_a, best_v = None, -np.inf
    for a in ALPHAS:
        m = Ridge(alpha=a).fit(Xtr, Ytr)
        v = compute_metrics(m.predict(Xva), Yva, which=["profile"])["profile"]["pearson_mean"]
        if v > best_v:
            best_v, best_a = v, a
    pred = Ridge(alpha=best_a).fit(Xtr, Ytr).predict(Xte)
    which = ["profile", "per_emotion", "rsa"] if full else ["profile"]
    m = compute_metrics(pred, Yte, which=which, rare_idx=rare_idx)
    out = {"alpha": best_a,
           "pearson": float(m["profile"]["pearson_mean"]),
           "ccc": float(m["profile"]["ccc_mean"])}
    if full:
        pe = m.get("per_emotion", {})
        out["per_emotion_mean"] = float(pe.get("mean", np.nan))
        for k in ("rare_mean", "rare_pearson_mean"):
            if k in pe:
                out["rare_mean"] = float(pe[k])
                break
        rs = m.get("rsa", {})
        out["rsa"] = float(next((v for v in rs.values() if isinstance(v, (int, float))), np.nan))
    return out


def cat(data, subs, sp, i):
    return np.concatenate([data[s][sp][i] for s in subs], axis=0)


def run_variant(data, rare_idx) -> dict:
    # within
    within = [fit_eval(*data[s]["train"], *data[s]["val"], *data[s]["test"], rare_idx)
              for s in SUBJECTS]
    # pooled
    pooled = fit_eval(cat(data, SUBJECTS, "train", 0), cat(data, SUBJECTS, "train", 1),
                      cat(data, SUBJECTS, "val", 0), cat(data, SUBJECTS, "val", 1),
                      cat(data, SUBJECTS, "test", 0), cat(data, SUBJECTS, "test", 1),
                      rare_idx, full=True)
    # loso
    loso = []
    for held in SUBJECTS:
        others = [s for s in SUBJECTS if s != held]
        loso.append(fit_eval(cat(data, others, "train", 0), cat(data, others, "train", 1),
                             cat(data, others, "val", 0), cat(data, others, "val", 1),
                             *data[held]["test"], rare_idx, full=True))
    w = float(np.mean([r["pearson"] for r in within]))
    l = float(np.mean([r["pearson"] for r in loso]))
    return {
        "within": w, "within_per_subject": [r["pearson"] for r in within],
        "pooled": pooled["pearson"], "pooled_ccc": pooled["ccc"],
        "loso": l, "loso_per_fold": [r["pearson"] for r in loso],
        "loso_ccc": float(np.mean([r["ccc"] for r in loso])),
        "loso_rsa": float(np.nanmean([r.get("rsa", np.nan) for r in loso])),
        "loso_rare": float(np.nanmean([r.get("rare_mean", np.nan) for r in loso])),
        "retention": (l / w) if w > 1e-9 else float("nan"),
    }


def main() -> None:
    variants = sys.argv[1:] or sorted(p.name for p in EMB_ROOT.iterdir() if p.is_dir())
    if ROI_BASELINE not in variants:
        variants = [ROI_BASELINE] + variants

    split = pd.read_csv(DATA / "horikawa_split.csv")
    labels = pd.read_csv(DATA / "cowen_horikawa_labels.csv").set_index("stim_num_int")
    norm = Cowen34Normalizer.load(DATA / "norm_stats" / "cowen34_train.pt")
    parts = {s: {sp: sorted(split.loc[(split["subject"] == s) & (split["split"] == sp),
                                      "stimulus_num"].astype(int))
                 for sp in ("train", "val", "test")} for s in SUBJECTS}
    freq = labels[SCORE_COLS].to_numpy(np.float64).mean(0)
    rare_idx = list(np.argsort(freq)[:N_RARE])

    print(f"{len(variants)} representations, 3 regimes each "
          f"(within / pooled / LOSO), rare = {N_RARE} least frequent emotions\n")
    res = {}
    for i, v in enumerate(variants, 1):
        t0 = time.time()
        try:
            data = load_rep(v, parts, labels, norm)
            r = run_variant(data, rare_idx)
        except Exception as e:  # noqa: BLE001
            print(f"[{i:2d}/{len(variants)}] {v:52s} SKIP ({type(e).__name__}: {e})")
            continue
        res[v] = r
        print(f"[{i:2d}/{len(variants)}] {v:52s} within {r['within']:+.3f}  "
              f"pooled {r['pooled']:+.3f}  LOSO {r['loso']:+.3f}  "
              f"retention {r['retention']:.3f}  ({time.time()-t0:.0f}s)", flush=True)

    base = res.get(ROI_BASELINE)
    print("\n" + "=" * 104)
    print("CROSS-SUBJECT (LOSO) COMPARISON. sorted by LOSO profile Pearson")
    print("=" * 104)
    print(f"{'representation':52s} {'within':>7s} {'LOSO':>7s} {'reten':>6s} "
          f"{'dLOSO':>7s} {'CCC':>6s} {'RSA':>6s} {'rare':>6s}")
    for v, r in sorted(res.items(), key=lambda kv: -kv[1]["loso"]):
        d = r["loso"] - base["loso"] if base else float("nan")
        tag = "  <= ROI baseline" if v == ROI_BASELINE else ""
        print(f"{v:52s} {r['within']:+7.3f} {r['loso']:+7.3f} {r['retention']:6.3f} "
              f"{d:+7.3f} {r['loso_ccc']:+6.3f} {r['loso_rsa']:+6.3f} "
              f"{r['loso_rare']:+6.3f}{tag}")

    if base:
        winners = {v: r for v, r in res.items()
                   if v != ROI_BASELINE and r["loso"] > base["loso"] + 0.02}
        better_ret = {v: r for v, r in res.items()
                      if v != ROI_BASELINE and r["retention"] > base["retention"] + 0.05}
        print("\n" + "=" * 104)
        print(f"ROI baseline. within {base['within']:+.3f}  LOSO {base['loso']:+.3f}  "
              f"retention {base['retention']:.3f}")
        print(f"BFM beating ROI on LOSO by >0.02 : {len(winners)} "
              f"{sorted(winners, key=lambda v: -res[v]['loso'])[:3]}")
        print(f"BFM with retention >0.05 higher  : {len(better_ret)} "
              f"{sorted(better_ret, key=lambda v: -res[v]['retention'])[:3]}")
        if winners or better_ret:
            print("=> A pretrained brain representation transfers across subjects better "
                  "than ROI mean. THIS is a reason to use a BFM that ridge cannot supply.")
        else:
            print("=> No BFM transfers better than ROI mean. The cross-subject axis does "
                  "NOT justify a BFM either; look to structure, data efficiency or fusion.")
        res["_baseline"] = ROI_BASELINE

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2))
    print(f"[save] {OUT}")


if __name__ == "__main__":
    main()
