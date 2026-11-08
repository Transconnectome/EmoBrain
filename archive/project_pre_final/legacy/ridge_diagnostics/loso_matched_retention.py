"""Fair cross-subject retention. Match the training set size.

The first LOSO comparison used within (n=1748, one subject) against LOSO
(n=6992, four subjects). Four times the training data. Weak representations then
scored retention > 1.0, which is impossible as a transfer statistic and exposed
the confound: the ratio was partly measuring training volume, not subject
invariance.

Here every regime trains on the SAME number of samples and is tested on the SAME
220 held-out stimuli of the SAME subject. Only the SOURCE of the training data
changes.

    within        train on subject s            (n = n_within)
    loso_matched  train on the other 4 subjects, subsampled to n_within
    loso_full     train on the other 4 subjects, all of it  (reference only,
                  this is the confounded number from the previous run)

    retention_fair = loso_matched / within

Reading. retention_fair near 1 means the representation transfers across
subjects almost for free. Low means it is subject specific. Because n_train is
now equal, a value above 1 is no longer manufacturable by data volume.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/loso_matched_retention.sh
    bash .../loso_matched_retention.sh all
    bash .../loso_matched_retention.sh roi_schaefer400tian50_mean brain_jepa_resting_pad-zero
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
from project.evaluation.metrics import profile_correlation  # noqa: E402

DATA = REPO_ROOT / "project" / "shared" / "data"
EMB_ROOT = REPO_ROOT / "project" / "shared" / "output" / "embeddings"
OUT = REPO_ROOT / "project" / "shared" / "results" / "loso_matched_retention.json"
SCORE_COLS = [f"score_{k}" for k in range(34)]
ALPHAS = [1.0, 10.0, 100.0, 1000.0, 10000.0]
ROI_BASELINE = "roi_schaefer400tian50_mean"
N_DRAWS = 5
SEED = 0

# informative subset: the ROI baseline, the strongest BFM family, the
# retention>1 anomalies (they must collapse once n_train is matched), and the
# best SwiFT / NeuroSTORM.
DEFAULT = [
    ROI_BASELINE,
    "brain_jepa_resting_pad-zero",
    "brain_jepa_resting_pad-mean",
    "brain_jepa_scratch_pad-zero",
    "brain_jepa_scratch_pad-mean",
    "neurostorm_resting_pad-zero",
    "swift_NewE96_SL20_resting_pad-spatial_only",
    "swift_NewE96_SL20_scratch_pad-replicate",
]


def tune_fit(Xtr, Ytr, Xva, Yva, Xte, Yte) -> float:
    best_a, best_v = ALPHAS[0], -np.inf
    for a in ALPHAS:
        v = profile_correlation(Ridge(alpha=a).fit(Xtr, Ytr).predict(Xva), Yva)["pearson_mean"]
        if v > best_v:
            best_v, best_a = v, a
    pred = Ridge(alpha=best_a).fit(Xtr, Ytr).predict(Xte)
    return float(profile_correlation(pred, Yte)["pearson_mean"])


def load_rep(variant, parts, labels, norm):
    src = BFMSource(variant, root=EMB_ROOT)
    d = {}
    for s in SUBJECTS:
        d[s] = {}
        for sp, stims in parts[s].items():
            X = np.stack([np.asarray(src.get(s, n)).ravel() for n in stims]).astype(np.float64)
            raw = np.stack([labels.loc[n, SCORE_COLS].to_numpy(np.float64) for n in stims])
            d[s][sp] = (X, np.asarray(norm.transform(raw), dtype=np.float64))
    return d


def run_variant(d) -> dict:
    rng = np.random.default_rng(SEED)
    within, matched, full = [], [], []
    for s in SUBJECTS:
        Xtr, Ytr = d[s]["train"]
        Xva, Yva = d[s]["val"]
        Xte, Yte = d[s]["test"]
        n_tr, n_va = len(Xtr), len(Xva)
        within.append(tune_fit(Xtr, Ytr, Xva, Yva, Xte, Yte))

        others = [o for o in SUBJECTS if o != s]
        OXtr = np.concatenate([d[o]["train"][0] for o in others])
        OYtr = np.concatenate([d[o]["train"][1] for o in others])
        OXva = np.concatenate([d[o]["val"][0] for o in others])
        OYva = np.concatenate([d[o]["val"][1] for o in others])
        # reference: the confounded full-data LOSO
        full.append(tune_fit(OXtr, OYtr, OXva, OYva, Xte, Yte))
        # matched: same n_train (and same n_val) as the within regime
        draws = []
        for _ in range(N_DRAWS):
            i = rng.choice(len(OXtr), n_tr, replace=False)
            j = rng.choice(len(OXva), min(n_va, len(OXva)), replace=False)
            draws.append(tune_fit(OXtr[i], OYtr[i], OXva[j], OYva[j], Xte, Yte))
        matched.append(float(np.mean(draws)))

    w, m, f = float(np.mean(within)), float(np.mean(matched)), float(np.mean(full))
    return {"within": w, "loso_matched": m, "loso_full": f,
            "retention_fair": m / w if w > 1e-9 else float("nan"),
            "retention_confounded": f / w if w > 1e-9 else float("nan"),
            "data_volume_effect": f - m,
            "within_per_subject": within, "matched_per_subject": matched}


def main() -> None:
    args = sys.argv[1:]
    if args == ["all"]:
        variants = sorted(p.name for p in EMB_ROOT.iterdir() if p.is_dir())
    else:
        variants = args or DEFAULT
    if ROI_BASELINE not in variants:
        variants = [ROI_BASELINE] + variants

    split = pd.read_csv(DATA / "horikawa_split.csv")
    labels = pd.read_csv(DATA / "cowen_horikawa_labels.csv").set_index("stim_num_int")
    norm = Cowen34Normalizer.load(DATA / "norm_stats" / "cowen34_train.pt")
    parts = {s: {sp: sorted(split.loc[(split["subject"] == s) & (split["split"] == sp),
                                      "stimulus_num"].astype(int))
                 for sp in ("train", "val", "test")} for s in SUBJECTS}

    n_tr = len(parts[SUBJECTS[0]]["train"])
    print(f"{len(variants)} representations. matched n_train = {n_tr} in every regime, "
          f"{N_DRAWS} subsample draws, same 220 test stimuli of the same subject.\n")

    res = {}
    for i, v in enumerate(variants, 1):
        t0 = time.time()
        try:
            r = run_variant(load_rep(v, parts, labels, norm))
        except Exception as e:  # noqa: BLE001
            print(f"[{i:2d}/{len(variants)}] {v:46s} SKIP ({type(e).__name__}: {e})")
            continue
        res[v] = r
        print(f"[{i:2d}/{len(variants)}] {v:46s} within {r['within']:+.3f}  "
              f"LOSO-matched {r['loso_matched']:+.3f}  retention {r['retention_fair']:.3f}  "
              f"(full-LOSO {r['loso_full']:+.3f}, volume effect {r['data_volume_effect']:+.3f})  "
              f"{time.time()-t0:.0f}s", flush=True)

    base = res.get(ROI_BASELINE)
    print("\n" + "=" * 108)
    print("FAIR CROSS-SUBJECT RETENTION (matched n_train). sorted by retention_fair")
    print("=" * 108)
    print(f"{'representation':46s} {'within':>7s} {'matched':>8s} {'reten':>6s} "
          f"{'conf.ret':>9s} {'volume':>7s}")
    for v, r in sorted(res.items(), key=lambda kv: -kv[1]["retention_fair"]):
        tag = "  <= ROI baseline" if v == ROI_BASELINE else ""
        print(f"{v:46s} {r['within']:+7.3f} {r['loso_matched']:+8.3f} "
              f"{r['retention_fair']:6.3f} {r['retention_confounded']:9.3f} "
              f"{r['data_volume_effect']:+7.3f}{tag}")

    if base:
        print("\n" + "=" * 108)
        print(f"ROI baseline. within {base['within']:+.3f}  matched-LOSO "
              f"{base['loso_matched']:+.3f}  fair retention {base['retention_fair']:.3f}")
        higher = {v: r for v, r in res.items() if v != ROI_BASELINE
                  and r["retention_fair"] > base["retention_fair"] + 0.05}
        beats = {v: r for v, r in res.items() if v != ROI_BASELINE
                 and r["loso_matched"] > base["loso_matched"] + 0.02}
        print(f"higher fair retention than ROI (+0.05) : {len(higher)} "
              f"{sorted(higher, key=lambda v: -res[v]['retention_fair'])[:3]}")
        print(f"higher matched-LOSO than ROI (+0.02)   : {len(beats)} "
              f"{sorted(beats, key=lambda v: -res[v]['loso_matched'])[:3]}")
        if beats:
            print("=> A BFM transfers to a NEW SUBJECT better than ROI mean at equal "
                  "training size. That is a reason ridge cannot supply.")
        elif higher:
            print("=> No BFM wins on absolute transfer, but some lose less. Subject "
                  "invariance is real yet not enough to overcome the lower base.")
        else:
            print("=> Cross-subject transfer does NOT justify a BFM even with the "
                  "confound removed. Move to data efficiency / structure / fusion.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2))
    print(f"[save] {OUT}")


if __name__ == "__main__":
    main()
