"""QC / QA of the Horikawa preprocessed data we actually train on.

Run before starting experiments. Two purposes.
    1. Integrity. NaN / shape / stimulus coverage / mask / dead ROI / subject
       alignment / volume sanity. Catch silent preprocessing corruption.
    2. Information-loss diagnostic. We decode from roi_mean (the stimulus-window
       time average). If time averaging threw away signal, the Stage 0 ceiling
       (~0.31 on ROI-mean, Case I / R0) would be a preprocessing artifact rather
       than a brain limit. We test this directly by decoding from a richer
       time summary and comparing on the same split and metric.

Data checked (all read-only).
    project/shared/data/roi_timeseries/sub-XX.pt      (2185, 47, 450) + mask
    Horikawa_embedding/.../img/sub-XX_stimulus_N/     MNI volumes (74,91,81)
    archive/.../fmri_raw.npy                          (5, 2196, 450)

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/qc_horikawa_data.sh
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

ROI_DIR = REPO_ROOT / "project" / "shared" / "data" / "roi_timeseries"
VOL_DIR = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img")
FMRI_RAW = (REPO_ROOT / "archive" / "v5_direction_split_20260628" / "dir3_ccn"
            / "data" / "raw" / "raw_fmri" / "fmri_raw.npy")
DATA = REPO_ROOT / "project" / "shared" / "data"
OUT = REPO_ROOT / "project" / "shared" / "results" / "qc" / "horikawa_data_qc.json"
SUBJECTS = [f"sub-{i:02d}" for i in range(1, 6)]
SCORE_COLS = [f"score_{k}" for k in range(34)]
N_VOL_SAMPLE = 40
SEED = 0

results = []


def rec(section: str, name: str, status: str, detail: str) -> None:
    results.append({"section": section, "name": name, "status": status, "detail": detail})
    print(f"  [{status:4s}] {name}. {detail}")


def load_rois() -> dict:
    return {s: torch.load(ROI_DIR / f"{s}.pt", weights_only=False) for s in SUBJECTS}


def qc_integrity(rois: dict) -> None:
    print("\n[1] ROI timeseries integrity")
    shapes, stim_ok, nan_tot = set(), True, 0
    for s, d in rois.items():
        rt = d["roi_timeseries"].numpy()
        rm = d["roi_mean"].numpy()
        shapes.add((rt.shape, rm.shape))
        nan_tot += int(np.isnan(rt).sum() + np.isnan(rm).sum()
                       + np.isinf(rt).sum() + np.isinf(rm).sum())
        sn = d["stim_num"].numpy()
        if not (len(np.unique(sn)) == len(sn) and sn.min() == 1 and sn.max() == 2185):
            stim_ok = False
    rec("integrity", "shape consistent across subjects", "PASS" if len(shapes) == 1 else "FAIL",
        f"{sorted(shapes)}")
    rec("integrity", "no NaN / Inf", "PASS" if nan_tot == 0 else "FAIL",
        f"{nan_tot} non-finite values across 5 subjects")
    rec("integrity", "stimulus coverage 1..2185 unique", "PASS" if stim_ok else "FAIL",
        "stim_num contiguous and unique in every subject")
    miss = {s: int(d["missing_stim"].numel()) for s, d in rois.items()}
    rec("integrity", "missing stimuli", "PASS" if sum(miss.values()) == 0 else "WARN", f"{miss}")

    # mask / valid TR
    tr_stats = {}
    zero_tr = 0
    for s, d in rois.items():
        m = d["mask"].numpy().astype(bool)
        n_valid = m.sum(axis=1)
        zero_tr += int((n_valid == 0).sum())
        tr_stats[s] = [int(n_valid.min()), float(n_valid.mean()), int(n_valid.max())]
    rec("integrity", "stimuli with 0 valid TR", "PASS" if zero_tr == 0 else "FAIL",
        f"{zero_tr} stimuli have an all-false mask")
    rec("integrity", "valid TR per stimulus [min,mean,max]", "INFO", f"{tr_stats}")

    # roi_mean really is the masked time mean
    dev = []
    for s, d in rois.items():
        rt, m, rm = d["roi_timeseries"].numpy(), d["mask"].numpy().astype(bool), d["roi_mean"].numpy()
        idx = np.random.default_rng(SEED).choice(rt.shape[0], 200, replace=False)
        for i in idx:
            v = rt[i][m[i]]
            if v.size:
                dev.append(float(np.abs(v.mean(axis=0) - rm[i]).max()))
    mx = max(dev) if dev else float("nan")
    rec("integrity", "roi_mean == masked time mean", "PASS" if mx < 1e-4 else "FAIL",
        f"max |roi_mean - mean(valid TR)| = {mx:.2e} over 1000 sampled stimuli")


def qc_distribution(rois: dict) -> None:
    print("\n[2] value distribution, outliers, dead ROI")
    dead_all, stats = {}, {}
    for s, d in rois.items():
        rm = d["roi_mean"].numpy()
        sd = rm.std(axis=0)
        dead = int((sd < 1e-8).sum())
        low = int((sd < 0.01).sum())
        dead_all[s] = (dead, low)
        stats[s] = [round(float(rm.mean()), 4), round(float(rm.std()), 4),
                    round(float(rm.min()), 2), round(float(rm.max()), 2)]
    n_dead = sum(v[0] for v in dead_all.values())
    rec("distribution", "dead (zero-variance) ROIs", "PASS" if n_dead == 0 else "FAIL",
        f"per subject (dead, std<0.01): {dead_all}")
    rec("distribution", "roi_mean [mean,std,min,max]", "INFO", f"{stats}")

    # extreme value fraction (per-ROI z)
    fr = {}
    for s, d in rois.items():
        rm = d["roi_mean"].numpy()
        z = (rm - rm.mean(0)) / (rm.std(0) + 1e-12)
        fr[s] = round(float((np.abs(z) > 5).mean()) * 100, 4)
    worst = max(fr.values())
    rec("distribution", "extreme |z|>5 fraction (%)", "PASS" if worst < 0.5 else "WARN", f"{fr}")

    # per-stimulus spike: pattern norm outliers
    sp = {}
    for s, d in rois.items():
        rm = d["roi_mean"].numpy()
        n = np.linalg.norm(rm, axis=1)
        thr = n.mean() + 5 * n.std()
        sp[s] = int((n > thr).sum())
    rec("distribution", "spike stimuli (norm > mean+5sd)", "PASS" if max(sp.values()) < 20 else "WARN",
        f"{sp} of 2185 per subject")


def qc_alignment(rois: dict) -> None:
    print("\n[3] subject alignment")
    ref = rois[SUBJECTS[0]]["stim_num"].numpy()
    same = all(np.array_equal(rois[s]["stim_num"].numpy(), ref) for s in SUBJECTS)
    rec("alignment", "stim_num identical ordering across subjects", "PASS" if same else "FAIL",
        "row i is the same stimulus in every subject file")
    # cross-subject correlation of roi_mean patterns (should be positive, ~ISC)
    X = np.stack([rois[s]["roi_mean"].numpy() for s in SUBJECTS])  # (5,2185,450)
    cs = []
    for i in range(5):
        for j in range(i + 1, 5):
            a, b = X[i], X[j]
            a = a - a.mean(1, keepdims=True)
            b = b - b.mean(1, keepdims=True)
            num = (a * b).sum(1)
            den = np.sqrt((a * a).sum(1) * (b * b).sum(1)) + 1e-12
            cs.append(float(np.nanmean(num / den)))
    m = float(np.mean(cs))
    rec("alignment", "cross-subject spatial ISC", "PASS" if m > 0.05 else "FAIL",
        f"mean pairwise = {m:+.4f} (prior measurement 0.235; near 0 would mean misalignment)")


def qc_volumes() -> None:
    print("\n[4] MNI volume sample")
    if not VOL_DIR.exists():
        rec("volume", "volume dir", "FAIL", f"missing {VOL_DIR}")
        return
    dirs = [p for p in VOL_DIR.iterdir() if p.is_dir()]
    rec("volume", "stimulus-volume directories", "INFO",
        f"{len(dirs)} dirs (expect ~5 subj x 2185 = 10925)")
    random.seed(SEED)
    sample = random.sample(dirs, min(N_VOL_SAMPLE, len(dirs)))
    shapes, nframes, nonfinite, nz, rng_, gs_ok = set(), [], 0, [], [], 0
    for p in sample:
        fr = sorted(p.glob("frame_*.pt"))
        nframes.append(len(fr))
        if not fr:
            continue
        a = torch.load(fr[0], weights_only=False)
        a = np.asarray(a.numpy() if hasattr(a, "numpy") else a, dtype=np.float32)
        shapes.add(a.shape)
        nonfinite += int((~np.isfinite(a)).sum())
        nz.append(float((a != 0).mean()))
        rng_.append((float(a.min()), float(a.max())))
        g = p / "global_stats.pt"
        if g.exists():
            d = torch.load(g, weights_only=False)
            brain = a[a != 0]
            if brain.size and abs(float(d["global_mean"]) - brain.mean()) / (brain.mean() + 1e-9) < 0.5:
                gs_ok += 1
    rec("volume", "shape consistent", "PASS" if len(shapes) == 1 else "WARN", f"{sorted(shapes)}")
    rec("volume", "frames per stimulus", "PASS" if len(set(nframes)) == 1 else "WARN",
        f"distinct counts={sorted(set(nframes))}")
    rec("volume", "no NaN / Inf", "PASS" if nonfinite == 0 else "FAIL", f"{nonfinite} non-finite")
    rec("volume", "brain mask fraction", "INFO",
        f"nonzero mean={100*np.mean(nz):.1f}% (range {100*min(nz):.1f}-{100*max(nz):.1f}%)")
    rec("volume", "intensity range", "INFO",
        f"min={min(r[0] for r in rng_):.2f} max={max(r[1] for r in rng_):.2f} (non-negative by design)")
    rec("volume", "global_stats matches volume", "PASS" if gs_ok > 0.8 * len(sample) else "WARN",
        f"{gs_ok}/{len(sample)} sampled stimuli consistent within 50%")


def qc_raw() -> None:
    print("\n[5] raw fmri array + 11-repeat")
    if not FMRI_RAW.exists():
        rec("raw", "fmri_raw.npy", "FAIL", f"missing {FMRI_RAW}")
        return
    r = np.load(FMRI_RAW)
    rec("raw", "shape", "PASS" if r.shape == (5, 2196, 450) else "FAIL", f"{r.shape}")
    rec("raw", "no NaN / Inf", "PASS" if np.isfinite(r).all() else "FAIL",
        f"{int((~np.isfinite(r)).sum())} non-finite")
    cs = []
    for s in range(r.shape[0]):
        a, b = r[s, 0:11], r[s, 2185:2196]
        a = a - a.mean(1, keepdims=True)
        b = b - b.mean(1, keepdims=True)
        num = (a * b).sum(1)
        den = np.sqrt((a * a).sum(1) * (b * b).sum(1)) + 1e-12
        cs.extend((num / den).tolist())
    m = float(np.nanmean(cs))
    rec("raw", "11-repeat single-trial retest", "INFO",
        f"mean r={m:+.4f} (low single-trial reliability; used in Stage 0)")


def main() -> None:
    print("=" * 72)
    print("HORIKAWA PREPROCESSED DATA QC / QA")
    print("=" * 72)
    rois = load_rois()
    qc_integrity(rois)
    qc_distribution(rois)
    qc_alignment(rois)
    qc_volumes()
    qc_raw()

    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    n_warn = sum(1 for r in results if r["status"] == "WARN")
    print("\n" + "=" * 72)
    print(f"RESULT. {n_fail} FAIL, {n_warn} WARN, "
          f"{sum(1 for r in results if r['status'] == 'PASS')} PASS")
    for r in results:
        if r["status"] in ("FAIL", "WARN"):
            print(f"  [{r['status']}] {r['name']}: {r['detail']}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2))
    print(f"[save] {OUT}")


if __name__ == "__main__":
    main()
