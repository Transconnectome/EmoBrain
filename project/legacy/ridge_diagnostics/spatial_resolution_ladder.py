"""Spatial resolution ladder. Does finer spatial detail beat the ROI-mean ceiling?

Stage 0 found the 450-ROI representation saturates at ~0.31 (Case I / R0), and
the QC showed time averaging is not the culprit. The remaining suspect is
SPATIAL compression: 450 ROIs average away ~245k brain voxels (a 500x squeeze).

This decodes the same 34D labels from the same stimuli at four spatial scales
built from the SAME volumes, so nothing differs but resolution.

    block 8 (16mm)  ~   479 features   (comparable to the 450 ROI dimensionality)
    block 4 ( 8mm)  ~ 3,837
    block 2 ( 4mm)  ~30,702
    block 1 ( 2mm)  ~245,618           (native)

Reading.
    flat ladder      -> spatial compression is NOT the bottleneck. R0 holds
                        beyond ROI-mean, and the framework must lean on fusion.
    rising ladder    -> the 450-ROI ceiling understates the brain. Encoder
                        candidates that read finer detail (E3/E4) are justified.

Also a built-in alignment check: if tylee's stimulus-N did not correspond to our
stim_num, decoding would collapse to ~0 at every rung.

Source volumes.
    /pscratch/sd/t/tylee/Horikawa_Haka/img/sub-XX/sub-XX_stimulus-N.nii.gz
    (97,115,97,T) 2mm MNI, z-scored, T variable. We time-average to match the
    roi_mean protocol.

Ridge note. n << p here, so we solve ridge in the DUAL (Gram) form. Forming the
p x p covariance would be 245k^2 and is never attempted.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/spatial_resolution_ladder.sh [subjects...]
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import nibabel as nib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from project.data.labels import Cowen34Normalizer  # noqa: E402
from project.evaluation.metrics import profile_correlation  # noqa: E402

TYLEE = Path("/pscratch/sd/t/tylee/Horikawa_Haka/img")
DATA = REPO_ROOT / "project" / "shared" / "data"
OUT = REPO_ROOT / "project" / "shared" / "results" / "spatial_resolution_ladder.json"
SCORE_COLS = [f"score_{k}" for k in range(34)]
BLOCKS = [8, 4, 2, 1]                      # 16mm, 8mm, 4mm, 2mm
ALPHAS = [1e2, 1e3, 1e4, 1e5, 1e6]
RIDGE_ROI450 = {"within": 0.307, "kernel_within": 0.313, "pooled": 0.294}


def block_reduce(vol: np.ndarray, mask: np.ndarray, b: int):
    """Brain-weighted block average. Returns (values, block_mask)."""
    if b == 1:
        return vol, mask
    pad = [(0, (-s) % b) for s in vol.shape]
    v = np.pad(vol * mask, pad)
    m = np.pad(mask.astype(np.float32), pad)
    sh = (v.shape[0] // b, b, v.shape[1] // b, b, v.shape[2] // b, b)
    vs = v.reshape(sh).sum(axis=(1, 3, 5))
    ms = m.reshape(sh).sum(axis=(1, 3, 5))
    out = np.zeros_like(vs)
    ok = ms > 0
    out[ok] = vs[ok] / ms[ok]
    return out, ok


def _timemean(f: Path) -> np.ndarray:
    a = nib.load(f).get_fdata(dtype=np.float32)
    return a.mean(axis=3) if a.ndim > 3 else a


def brain_mask(subj: str, stims: list[int], n: int = 120) -> np.ndarray:
    """Voxels non-zero in every sampled volume. One cheap pre-pass."""
    d = TYLEE / subj
    mask = None
    for s in stims[:: max(1, len(stims) // n)][:n]:
        f = d / f"{subj}_stimulus-{s}.nii.gz"
        if not f.exists():
            continue
        v = _timemean(f) != 0
        mask = v if mask is None else (mask & v)
    return mask


def extract_rungs(subj: str, stims: list[int], mask: np.ndarray, blocks: list[int]):
    """Load each volume ONCE and reduce it to every rung immediately.

    Never stacks full 3D volumes; that is 9.5 GB for 2185 stimuli and gets the
    process OOM-killed. Only the reduced features are kept.
    """
    d = TYLEE / subj
    dims = {}
    for b in blocks:
        _, bm = block_reduce(np.zeros_like(mask, dtype=np.float32), mask, b)
        dims[b] = (bm, int(bm.sum()))
    X = {b: np.zeros((len(stims), dims[b][1]), np.float32) for b in blocks}
    missing, t0 = [], time.time()
    for i, s in enumerate(stims):
        f = d / f"{subj}_stimulus-{s}.nii.gz"
        if not f.exists():
            missing.append(s)
            continue
        vol = _timemean(f)
        for b in blocks:
            v, _ = block_reduce(vol, mask, b)
            X[b][i] = v[dims[b][0]]
        if (i + 1) % 500 == 0:
            print(f"    {subj} {i+1}/{len(stims)} ({time.time()-t0:.0f}s)", flush=True)
    return X, missing


def dual_ridge_eval(Xtr, Ytr, Xva, Yva, Xte, Yte):
    """Ridge in dual form (n << p). Returns best test profile pearson.

    Centering is done IN PLACE. The caller frees these arrays right after, and a
    copy of the 2mm rung would add ~1.7 GB of peak memory for nothing.
    """
    mu = Xtr.mean(0, keepdims=True)
    Xtr -= mu
    Xva -= mu
    Xte -= mu
    K = Xtr @ Xtr.T
    Kva, Kte = Xva @ Xtr.T, Xte @ Xtr.T
    n = K.shape[0]
    best_v, best_a = -9.0, None
    for a in ALPHAS:
        coef = np.linalg.solve(K + a * np.eye(n, dtype=K.dtype), Ytr)
        v = profile_correlation(Kva @ coef, Yva)["pearson_mean"]
        if v > best_v:
            best_v, best_a = v, a
    coef = np.linalg.solve(K + best_a * np.eye(n, dtype=K.dtype), Ytr)
    return profile_correlation(Kte @ coef, Yte)["pearson_mean"], best_a


def main() -> None:
    subjects = sys.argv[1:] or ["sub-01", "sub-02"]
    split = pd.read_csv(DATA / "horikawa_split.csv")
    labels = pd.read_csv(DATA / "cowen_horikawa_labels.csv").set_index("stim_num_int")
    norm = Cowen34Normalizer.load(DATA / "norm_stats" / "cowen34_train.pt")

    out = {"ridge_roi450_reference": RIDGE_ROI450, "subjects": {}}
    for subj in subjects:
        rows = split[split["subject"] == subj]
        parts = {sp: sorted(rows.loc[rows["split"] == sp, "stimulus_num"].astype(int))
                 for sp in ("train", "val", "test")}
        stims = parts["train"] + parts["val"] + parts["test"]
        print(f"\n=== {subj}. {len(stims)} volumes ===", flush=True)
        mask = brain_mask(subj, stims)
        print(f"  brain mask {int(mask.sum()):,} voxels", flush=True)
        X, missing = extract_rungs(subj, stims, mask, BLOCKS)
        print(f"  reduced. missing {len(missing)}, "
              f"dims={{{', '.join(f'{2*b}mm:{X[b].shape[1]:,}' for b in BLOCKS)}}}", flush=True)

        ntr, nva = len(parts["train"]), len(parts["val"])
        Y = {}
        for sp in ("train", "val", "test"):
            raw = np.stack([labels.loc[s, SCORE_COLS].to_numpy(np.float64) for s in parts[sp]])
            Y[sp] = np.asarray(norm.transform(raw), dtype=np.float32)

        res = {}
        for b in BLOCKS:
            t0 = time.time()
            Xb = X[b]
            r, a = dual_ridge_eval(Xb[:ntr], Y["train"], Xb[ntr:ntr+nva], Y["val"],
                                   Xb[ntr+nva:], Y["test"])
            res[f"block{b}_{2*b}mm"] = {"n_features": int(Xb.shape[1]),
                                        "test_profile_pearson": float(r), "alpha": a}
            print(f"  {2*b:>2}mm  dim={Xb.shape[1]:>7,}  test profile pearson = {r:+.4f}  "
                  f"(alpha {a:.0e}, {time.time()-t0:.0f}s)", flush=True)
            X[b] = None                      # free as we go
        out["subjects"][subj] = res
        del X

    # verdict
    print("\n" + "=" * 66)
    print("SPATIAL RESOLUTION LADDER (test profile Pearson, within subject)")
    print("=" * 66)
    print(f"  reference: 450-ROI ridge within={RIDGE_ROI450['within']:+.3f} "
          f"kernel={RIDGE_ROI450['kernel_within']:+.3f}")
    rungs = [f"block{b}_{2*b}mm" for b in BLOCKS]
    means = {}
    for k in rungs:
        vals = [out["subjects"][s][k]["test_profile_pearson"] for s in subjects]
        means[k] = float(np.mean(vals))
        print(f"  {k:>16}  dim={out['subjects'][subjects[0]][k]['n_features']:>7,}  "
              f"mean={means[k]:+.4f}  per-subject={[round(v,4) for v in vals]}")
    gain = means[rungs[-1]] - means[rungs[0]]
    best = max(means.values())
    out["summary"] = {"means": means, "finest_minus_coarsest": gain,
                      "best_rung": max(means, key=means.get), "best": best,
                      "beats_roi450_kernel": bool(best > RIDGE_ROI450["kernel_within"] + 0.02)}
    print(f"\n  finest - coarsest = {gain:+.4f}")
    if best > RIDGE_ROI450["kernel_within"] + 0.02:
        print("  => RISING. Finer spatial detail beats the ROI-mean ceiling. "
              "Spatial compression WAS a bottleneck; encoders reading finer "
              "detail (E3/E4) are justified.")
    else:
        print("  => FLAT. Finer spatial detail does not beat the ROI-mean ceiling. "
              "R0 extends beyond ROI-mean; the framework must lean on the fusion "
              "axis rather than on brain-encoder resolution.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"[save] {OUT}")


if __name__ == "__main__":
    main()
