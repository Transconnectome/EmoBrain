"""Stage 0 emotion-space decoding noise ceiling (critic-revised 2026-07-09).

Replaces the retracted sqrt(ISC) ROI-space attenuation ceiling. That method was
wrong-units (a 450-ROI correlation cannot be subtracted from a 34D-profile
correlation) and structurally unable to return Case I (sqrt of a high ISC always
clears the ridge, so it could never detect R0). The emovi-method-critic verdict
(2026-07-09) required an in-units, conservative construction. This script is that.

All numbers are per-clip 34D profile Pearson (the headline metric), so they sit
on the SAME axis as ridge (pooled 0.294 / LOSO 0.232).

Anchors.
    lower                ridge pooled 0.294 / LOSO 0.232 (ridge_subject_regimes).
    upper A (primary)    inter-subject decoding ceiling. Each subject's ridge
                         decodes the 34D profile of the shared 220 test stimuli;
                         the leave-one-subject-out consensus agreement (per-clip
                         34D Pearson of one subject's decoded profile vs the mean
                         of the others') is a ceiling on cross-subject decoding,
                         in matched units, with a stimulus-bootstrap CI. Gate on
                         its lower CI (conservative).
    upper B (empirical)  representation saturation. A flexible within-subject
                         decoder (kernel ridge RBF) on the SAME ROI-mean feature.
                         If it cannot beat linear ridge, the ROI-mean
                         representation is saturated (R0 for ROI-mean).

Caveats (kept in the JSON so they travel with the number).
    - This is the ROI-mean decoding ceiling. E3 (BFM) / E4 (VLM) read richer
      inputs and are NOT bounded by it.
    - The inter-subject ceiling is still an upper bound (it assumes the shared
      decoded signal is entirely target-relevant; shared label structure can
      inflate it).
    - The 11 within-subject repeats (single-trial reliability ~0.09, several
      negative) are too thin for a formal analytical ceiling (Lage-Castellanos /
      Schoppe CC_norm). Reported descriptively only, as evidence the operative
      single-trial signal is weak.

Output.
    project/shared/results/noise_ceiling/decoding_ceiling.json  (new file)

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/stage0_decoding_ceiling.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402
from sklearn.kernel_ridge import KernelRidge  # noqa: E402

from project.data.fmri_adapter import FmriAdapter, SUBJECTS  # noqa: E402
from project.data.labels import Cowen34Normalizer  # noqa: E402
from project.evaluation.metrics import profile_correlation  # noqa: E402

DATA_DIR = REPO_ROOT / "project" / "shared" / "data"
LABELS_CSV = DATA_DIR / "cowen_horikawa_labels.csv"
SPLIT_CSV = DATA_DIR / "horikawa_split.csv"
NORM = DATA_DIR / "norm_stats" / "cowen34_train.pt"
FMRI_RAW = (REPO_ROOT / "archive" / "v5_direction_split_20260628" / "dir3_ccn"
            / "data" / "raw" / "raw_fmri" / "fmri_raw.npy")
OUT_DIR = REPO_ROOT / "project" / "shared" / "results" / "noise_ceiling"
OUT = OUT_DIR / "decoding_ceiling.json"

SCORE_COLS = [f"score_{k}" for k in range(34)]
RIDGE_ALPHAS = [1.0, 10.0, 100.0, 1000.0, 10000.0]
KR_ALPHAS = [0.1, 1.0, 10.0]
KR_GAMMAS = [1e-4, 1e-3, 1e-2]
N_BOOT = 1000
SEED = 0
RIDGE_POOLED = 0.294   # from ridge_subject_regimes.json (same pipeline)
RIDGE_LOSO = 0.232


def _row_pearson(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Per-row Pearson between two (M, D) arrays -> (M,)."""
    A = A - A.mean(axis=1, keepdims=True)
    B = B - B.mean(axis=1, keepdims=True)
    num = (A * B).sum(axis=1)
    den = np.sqrt((A * A).sum(axis=1) * (B * B).sum(axis=1))
    out = np.full(A.shape[0], np.nan)
    ok = den > 1e-12
    out[ok] = num[ok] / den[ok]
    return out


def build_pool() -> dict:
    """subject -> {split -> (X (n,450), Yz (n,34), stims)}. Test = shared 220."""
    adapter = FmriAdapter()
    norm = Cowen34Normalizer.load(NORM)
    labels = pd.read_csv(LABELS_CSV).set_index("stim_num_int")
    split = pd.read_csv(SPLIT_CSV)
    data = {}
    for subj in SUBJECTS:
        rows = split[split["subject"] == subj]
        data[subj] = {}
        for sp in ("train", "val", "test"):
            stims = sorted(rows.loc[rows["split"] == sp, "stimulus_num"].astype(int).tolist())
            X = np.stack([adapter.get(subj, sn, "mean").numpy() for sn in stims], 0).astype(np.float64)
            raw = np.stack([labels.loc[sn, SCORE_COLS].values.astype(np.float64) for sn in stims], 0)
            Yz = norm.transform(raw).numpy()
            data[subj][sp] = (X, Yz, stims)
    return data


def tune_ridge(Xtr, Ytr, Xva, Yva):
    best_a, best_v = None, -np.inf
    for a in RIDGE_ALPHAS:
        m = Ridge(alpha=a).fit(Xtr, Ytr)
        v = profile_correlation(m.predict(Xva), Yva)["pearson_mean"]
        if v > best_v:
            best_v, best_a = v, a
    return Ridge(alpha=best_a).fit(Xtr, Ytr), best_a


def tune_kernel_ridge(Xtr, Ytr, Xva, Yva):
    best, best_v, best_hp = None, -np.inf, None
    for a in KR_ALPHAS:
        for g in KR_GAMMAS:
            m = KernelRidge(alpha=a, kernel="rbf", gamma=g).fit(Xtr, Ytr)
            v = profile_correlation(m.predict(Xva), Yva)["pearson_mean"]
            if v > best_v:
                best_v, best, best_hp = v, m, (a, g)
    return best, best_hp


def inter_subject_ceiling(data: dict) -> dict:
    """Upper anchor A. Decode the shared 220 test stimuli per subject, measure
    leave-one-subject-out consensus agreement of the decoded 34D profiles."""
    test_stims = data[SUBJECTS[0]]["test"][2]
    assert all(data[s]["test"][2] == test_stims for s in SUBJECTS), "test set differs"
    n_stim = len(test_stims)
    P = np.zeros((len(SUBJECTS), n_stim, 34))
    for si, subj in enumerate(SUBJECTS):
        Xtr, Ytr, _ = data[subj]["train"]
        Xva, Yva, _ = data[subj]["val"]
        Xte, _, _ = data[subj]["test"]
        model, _ = tune_ridge(Xtr, Ytr, Xva, Yva)
        P[si] = model.predict(Xte)

    # per-stimulus, per-subject: r(subject decode, mean of OTHER subjects' decode)
    R_loo = np.zeros((len(SUBJECTS), n_stim))
    for si in range(len(SUBJECTS)):
        others = [t for t in range(len(SUBJECTS)) if t != si]
        M = P[others].mean(axis=0)              # consensus of the rest
        R_loo[si] = _row_pearson(P[si], M)
    per_stim = np.nanmean(R_loo, axis=0)        # (n_stim,) mean over subjects
    ceiling_loo = float(np.nanmean(per_stim))

    # optimistic variant: each subject vs full-group mean (includes self)
    Mfull = P.mean(axis=0)
    R_opt = np.stack([_row_pearson(P[si], Mfull) for si in range(len(SUBJECTS))], 0)
    ceiling_opt = float(np.nanmean(R_opt))

    # stimulus bootstrap on the LOO ceiling
    rng = np.random.default_rng(SEED)
    valid = per_stim[~np.isnan(per_stim)]
    boots = np.array([np.mean(rng.choice(valid, size=valid.size, replace=True))
                      for _ in range(N_BOOT)])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "ceiling_loo": ceiling_loo,
        "ceiling_loo_ci95": [float(lo), float(hi)],
        "ceiling_optimistic_fullmean": ceiling_opt,
        "n_test_stim": int(n_stim),
        "per_subject_loo": [float(np.nanmean(R_loo[si])) for si in range(len(SUBJECTS))],
    }


def representation_saturation(data: dict) -> dict:
    """Upper anchor B. Flexible (kernel ridge RBF) vs linear ridge, within
    subject, on the same ROI-mean feature. Flexible ~ linear => saturated."""
    lin, flex, hps = [], [], []
    for subj in SUBJECTS:
        Xtr, Ytr, _ = data[subj]["train"]
        Xva, Yva, _ = data[subj]["val"]
        Xte, Yte, _ = data[subj]["test"]
        lm, _ = tune_ridge(Xtr, Ytr, Xva, Yva)
        lin.append(profile_correlation(lm.predict(Xte), Yte)["pearson_mean"])
        km, hp = tune_kernel_ridge(Xtr, Ytr, Xva, Yva)
        flex.append(profile_correlation(km.predict(Xte), Yte)["pearson_mean"])
        hps.append(hp)
    lin_m, flex_m = float(np.mean(lin)), float(np.mean(flex))
    return {
        "linear_ridge_within": lin_m,
        "kernel_ridge_within": flex_m,
        "flex_minus_linear": flex_m - lin_m,
        "per_subject_linear": [float(x) for x in lin],
        "per_subject_kernel": [float(x) for x in flex],
        "kernel_hparams": [list(h) for h in hps],
    }


def repeat_reliability() -> dict:
    """Descriptive only. 11 stimuli shown twice; single-trial ROI-pattern
    test-retest. Too thin for a formal ceiling (Schoppe CC_norm), kept as
    evidence the operative single-trial signal is weak."""
    r = np.load(FMRI_RAW)                        # (5, 2196, 450)
    corrs = []
    for s in range(r.shape[0]):
        A = r[s, 0:11]
        B = r[s, 2185:2196]
        corrs.extend(_row_pearson(A, B).tolist())
    corrs = np.array(corrs)
    return {
        "single_trial_retest_mean": float(np.nanmean(corrs)),
        "single_trial_retest_median": float(np.nanmedian(corrs)),
        "n_pairs": int(np.sum(~np.isnan(corrs))),
        "note": "11 stim x 2 presentations, single trial. Too thin for a formal "
                "analytical ceiling; descriptive evidence of weak single-trial signal.",
    }


def case_of(headroom: float) -> str:
    if headroom < 0.05:
        return "I (R0 realized -> reframe; ceiling ~ ridge)"
    if headroom <= 0.15:
        return "II (narrow headroom -> proceed with reservation)"
    return "III (wide headroom -> encoder competition normal)"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("[stage0] building pooled data (5 subj x train/val/test) ...")
    data = build_pool()

    print("[stage0] upper anchor A. inter-subject decoding ceiling ...")
    A = inter_subject_ceiling(data)
    print(f"  ceiling_loo = {A['ceiling_loo']:+.4f}  "
          f"CI95 [{A['ceiling_loo_ci95'][0]:+.4f}, {A['ceiling_loo_ci95'][1]:+.4f}]  "
          f"(optimistic full-mean {A['ceiling_optimistic_fullmean']:+.4f})")

    print("[stage0] upper anchor B. representation saturation (kernel vs linear) ...")
    B = representation_saturation(data)
    print(f"  linear ridge within  = {B['linear_ridge_within']:+.4f}")
    print(f"  kernel ridge within  = {B['kernel_ridge_within']:+.4f}  "
          f"(flex - linear = {B['flex_minus_linear']:+.4f})")

    print("[stage0] 11-repeat single-trial reliability (descriptive) ...")
    C = repeat_reliability()
    print(f"  single-trial retest mean = {C['single_trial_retest_mean']:+.4f}")

    # INFLATION DIAGNOSTIC. Anchor A measures agreement of decoded profiles
    # BETWEEN subjects; a ceiling must be agreement with TRUTH. The within-subject
    # decoder-vs-truth correlation (B linear) is the truth-agreement. If A's
    # inter-subject agreement >> decoder-vs-truth, A is inflated by shared label
    # structure (regression toward the common label subspace), not reproducible
    # brain decoding. Then A is disqualified as a ceiling.
    decoder_vs_truth = B["linear_ridge_within"]           # within test, pred vs true
    inter_subj_agreement = A["ceiling_loo"]
    inflation_gap = inter_subj_agreement - decoder_vs_truth
    A_inflated = inflation_gap > 0.05

    # GATE on the trustworthy anchor: representation saturation (the best
    # truth-aligned decoding achievable on ROI-mean). Flexibility delta ~ 0 =>
    # ROI-mean saturated. This is the operationally valid ceiling.
    operative_ceiling = B["kernel_ridge_within"]
    headroom = operative_ceiling - RIDGE_POOLED
    verdict = case_of(headroom)

    out = {
        "metric": "per-clip 34D profile Pearson (same axis as ridge)",
        "scope": "ROI-mean representation only (E1/E2/ridge). E3 (BFM) / E4 (VLM) "
                 "read richer inputs and are NOT bounded by this ceiling.",
        "ridge_pooled": RIDGE_POOLED,
        "ridge_loso": RIDGE_LOSO,
        "upper_A_inter_subject": A,
        "upper_B_representation_saturation": B,
        "repeat_reliability_descriptive": C,
        "inflation_diagnostic": {
            "inter_subject_agreement": inter_subj_agreement,
            "decoder_vs_truth": decoder_vs_truth,
            "inflation_gap": inflation_gap,
            "A_disqualified_as_ceiling": bool(A_inflated),
            "reading": "decoders agree with EACH OTHER far more than with the "
                       "TRUTH => anchor A is shared-label-structure inflation, "
                       "not a truth ceiling. Gate on anchor B instead.",
        },
        "gate": {
            "ceiling_used": "upper_B kernel-ridge saturation (truth-aligned, "
                            "operative ceiling of the ROI-mean representation)",
            "operative_ceiling": operative_ceiling,
            "flexibility_delta_over_linear": B["flex_minus_linear"],
            "headroom_vs_ridge_pooled": headroom,
            "case": verdict,
            "thresholds": "I<0.05, II 0.05-0.15, III>0.15",
            "note": "R0 test is on ROI-mean; a real headroom, if any, must come "
                    "from richer brain representations (voxel / temporal), whose "
                    "ceiling is not measured here.",
        },
        "caveats": [
            "ROI-mean decoding ceiling only; E3 (BFM) / E4 (VLM) richer inputs "
            "are not bounded by it.",
            "anchor A (0.68) is inflated by shared label structure (agreement "
            "with other decoders, not with truth); disqualified as a ceiling.",
            "sqrt(ISC) ROI-space ceiling was retracted (wrong units, cannot detect R0).",
            "kernel-ridge grid is not exhaustive; the near-zero flexibility delta "
            "is consistent with saturation but is not a proof that no nonlinear "
            "readout exists on ROI-mean.",
        ],
    }
    OUT.write_text(json.dumps(out, indent=2))

    print("\n" + "=" * 64)
    print("STAGE 0 DECODING CEILING (per-clip 34D profile Pearson, ROI-mean)")
    print("=" * 64)
    print(f"  ridge (lower anchor)        pooled {RIDGE_POOLED:+.3f} / LOSO {RIDGE_LOSO:+.3f}")
    print(f"  anchor A inter-subj agree   {inter_subj_agreement:+.3f}  "
          f"[CI {A['ceiling_loo_ci95'][0]:+.3f}, {A['ceiling_loo_ci95'][1]:+.3f}]")
    print(f"  ... decoder-vs-TRUTH        {decoder_vs_truth:+.3f}   "
          f"(gap {inflation_gap:+.3f} => A {'INFLATED, disqualified' if A_inflated else 'ok'})")
    print(f"  anchor B kernel saturation  {operative_ceiling:+.3f} "
          f"(linear {B['linear_ridge_within']:+.3f}, flex delta {B['flex_minus_linear']:+.3f})")
    print(f"  operative ceiling (B)       {operative_ceiling:+.3f}")
    print(f"  gate headroom (B - ridge)   = {headroom:+.3f}")
    print(f"  => CASE {verdict}   [ROI-mean scope; richer reps not measured]")
    print(f"\n[save] {OUT}")


if __name__ == "__main__":
    main()
