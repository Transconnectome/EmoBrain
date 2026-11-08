"""Preprocessing census q2. Every derived ROI file against the recomputation.

Scientific question
-------------------
Do the ROI CSVs, the roi_timeseries .pt files and fmri_raw.npy contain exactly
what the step7 segments and the atlas imply, for every stimulus and every
participant?

What this excludes
------------------
q1 recomputes the ROI series directly from step7. If a derived file matches
that recomputation to float precision, it inherits every property q1 verified
and needs no separate trust. If it does not, the stage that introduced the
difference is identified by which file first departs: CSV, then .pt, then
fmri_raw.

Outputs
-------
qc/derivation_chain.tsv   one row per participant, stimulus and file type
qc/derivation_chain.json  summary verdicts
"""
from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

from _assets import provenance, write_json, write_tsv  # noqa: E402
from _qc import FMRI_RAW, PT_DIR, QC, QC_ROI, ROI_CSV, SUBJECTS  # noqa: E402

SCRIPT = "prereg_v2/code/q2_derivation_chain.py"


def load_recomputed(subj: str) -> dict:
    """stimulus_number -> (roi_all (T,450), roi_brain (T,450))."""
    z = np.load(QC_ROI / f"{subj}.npz", allow_pickle=True)
    out = {}
    for i in range(len(z["run_keys"])):
        ra, rb, st = z[f"roi_all__{i}"], z[f"roi_brain__{i}"], z[f"segtable__{i}"]
        for r in st:
            if r["is_baseline"]:
                continue
            a, d = int(r["onset_tr"]), int(r["duration_tr"])
            out[int(r["stimulus_number"])] = (ra[a:a + d], rb[a:a + d])
    return out


def read_csv_pair(args):
    subj, stim = args
    d = ROI_CSV / subj / f"stimulus_{stim}"
    c = pd.read_csv(d / "fMRI.Schaefer17n400p.csv.gz")
    s = pd.read_csv(d / "fMRI.Tian_Subcortex_S3_3T.csv.gz")
    order_ok = (c.label_name.tolist() == [f"ROI_{i}" for i in range(1, 401)]
                and s.label_name.tolist() == [f"ROI_{i}" for i in range(1, 51)])
    x = np.concatenate([c.iloc[:, 1:].to_numpy(np.float64), s.iloc[:, 1:].to_numpy(np.float64)], 0).T
    return subj, stim, x, order_ok


def main() -> None:
    prov = provenance(SCRIPT)
    rows = []
    fmri = np.load(FMRI_RAW)
    summary = {"provenance": prov, "per_participant": {}}
    for si, subj in enumerate(SUBJECTS):
        rec = load_recomputed(subj)
        stims = sorted(rec)
        csv_dirs = sorted(int(p.name.split("_")[1]) for p in (ROI_CSV / subj).glob("stimulus_*"))
        with ProcessPoolExecutor(max_workers=16) as ex:
            csvs = list(ex.map(read_csv_pair, [(subj, s) for s in csv_dirs], chunksize=32))
        csv_map = {s: (x, ok) for _, s, x, ok in csvs}
        pt = torch.load(PT_DIR / f"{subj}.pt", map_location="cpu", weights_only=False)
        pts = np.asarray(pt["roi_timeseries"], np.float64)
        ptm = np.asarray(pt["roi_mean"], np.float64)
        pt_T = np.asarray(pt["original_T"]); pt_s = np.asarray(pt["stim_num"])
        for s in stims:
            a, b = rec[s]
            r = {"participant_id": subj, "stimulus_number": s, "T": a.shape[0],
                 "roi_brain_minus_all_mean_abs": float(np.nanmean(np.abs(b - a)))}
            if s in csv_map:
                x, ok = csv_map[s]
                r["csv_present"] = True
                r["csv_label_order_ok"] = bool(ok)
                r["csv_shape_ok"] = bool(x.shape == a.shape)
                r["csv_max_abs_diff"] = float(np.abs(x - a).max()) if x.shape == a.shape else float("nan")
            else:
                r["csv_present"] = False
            idx = np.where(pt_s == s)[0]
            if idx.size:
                i = idx[0]; T = int(pt_T[i])
                r["pt_present"] = True
                r["pt_T_ok"] = bool(T == a.shape[0])
                r["pt_ts_max_abs_diff"] = float(np.abs(pts[i, :T] - a).max()) if T == a.shape[0] else float("nan")
                r["pt_padding_all_zero"] = bool(np.all(pts[i, T:] == 0))
                r["pt_mean_max_abs_diff"] = float(np.abs(ptm[i] - a.mean(0)).max())
            else:
                r["pt_present"] = False
            if s <= fmri.shape[1]:
                r["fmri_raw_max_abs_diff"] = float(np.abs(fmri[si, s - 1].astype(np.float64) - a.mean(0)).max())
            rows.append(r)
        df = pd.DataFrame([r for r in rows if r["participant_id"] == subj])
        summary["per_participant"][subj] = {
            "n_recomputed_stimuli": len(stims),
            "n_csv_dirs": len(csv_dirs),
            "csv_dirs_not_in_step7": sorted(set(csv_dirs) - set(stims)),
            "step7_stimuli_without_csv": sorted(set(stims) - set(csv_dirs))[:20],
            "csv_max_abs_diff": float(df.csv_max_abs_diff.max()),
            "csv_all_label_order_ok": bool(df.loc[df.csv_present, "csv_label_order_ok"].all()),
            "pt_n_present": int(df.pt_present.sum()),
            "pt_ts_max_abs_diff": float(df.pt_ts_max_abs_diff.max()),
            "pt_mean_max_abs_diff": float(df.pt_mean_max_abs_diff.max()),
            "pt_padding_all_zero": bool(df.loc[df.pt_present, "pt_padding_all_zero"].all()),
            "fmri_raw_max_abs_diff": float(df.fmri_raw_max_abs_diff.max()),
            "roi_brain_minus_all_mean_abs_median": float(df.roi_brain_minus_all_mean_abs.median()),
        }
        print(f"  {subj}: {summary['per_participant'][subj]}")
    all_ = pd.DataFrame(rows)
    tol = 1e-4
    summary["verdict"] = {
        "csv_reproduced": bool(all_.csv_max_abs_diff.max() < tol),
        "pt_reproduced": bool(all_.pt_ts_max_abs_diff.max() < tol and all_.pt_mean_max_abs_diff.max() < tol),
        "fmri_raw_reproduced": bool(all_.fmri_raw_max_abs_diff.max() < tol),
        "tolerance": tol,
        "fmri_raw_participant_order": "row s of fmri_raw is compared with SUBJECTS[s]",
    }
    print(summary["verdict"])
    write_tsv(QC / "derivation_chain.tsv", all_, prov)
    write_json(QC / "derivation_chain.json", summary)


if __name__ == "__main__":
    main()
