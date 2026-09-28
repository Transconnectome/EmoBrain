"""Preprocessing census q1. Every step7 segment and every filtered frame.

Scientific question
-------------------
Is each step7 segment a faithful, untouched slice of one run-level z-scored
BOLD series, do the segments of a run tile that run without gaps, overlaps or
per-segment renormalisation, and is every filtered frame the transform of its
segment that the sample check found?

What this excludes
------------------
1. Header drift. One file with a different affine, shape or voxel size would
   silently map to the wrong parcels.
2. Broken tiling. If segments overlap, leave gaps, or were renormalised one by
   one, the run cannot be reconstructed and any lag-shifted window or GLM
   built on the reconstruction would be wrong. Two independent signatures
   test this. Voxelwise mean and sd over the reconstructed run should be 0
   and 1 if step6 z-scored the whole run and step7 only cut it. The change
   between the last volume of one segment and the first volume of the next
   (DVARS at a boundary) should look like any other TR-to-TR change.
3. Unverified derivatives. The frame transform was recovered from one file;
   it is checked here on all 66,755 frames.

The ROI values are recomputed in two forms. `ROI_ALL` averages every voxel in
the parcel, including voxels that are exactly zero because they fall outside
the brain; this is what NiftiLabelsMasker without a mask does. `ROI_BRAIN`
averages only non-zero voxels. The gap between them measures how much of each
parcel is diluted by out-of-brain zeros.

Outputs
-------
qc/segments_qc.tsv     one row per segment (11,285)
qc/boundaries_qc.tsv   one row per segment boundary inside a run
qc/runs_qc.tsv         one row per run (305)
qc/roi_runs/sub-XX.npz reconstructed ROI run series, both forms (gitignored)
qc/masks/sub-XX_*.nii.gz  union and intersection of non-constant voxels
qc/parcel_coverage.tsv per parcel and participant
qc/voxel_census.json   summary verdicts
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nibabel as nib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from _assets import MANIFESTS, provenance, read_tsv, write_json, write_tsv  # noqa: E402
from _qc import (FRAME_CROP, FRAMES, GRID_SHAPE, QC, QC_ATLAS, QC_MASKS,  # noqa: E402
                 QC_ROI, SUBJECTS)

SCRIPT = "prereg_v2/code/q1_voxel_census.py"
N_WORKERS = 16
CHECK_FRAMES = True

_LAB = {}


def _init():
    import numpy as _np
    for name in ("schaefer", "tian"):
        L = _np.load(QC_ATLAS / f"{name}_on_fmri_grid.npy").ravel().astype(_np.int64)
        sel = _np.nonzero(L > 0)[0]
        _LAB[name] = (sel, L[sel] - 1, int(L.max()))


def roi_means(vol_flat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(450,) means over all parcel voxels and over non-zero parcel voxels."""
    all_, brain = [], []
    for name in ("schaefer", "tian"):
        sel, lab, n = _LAB[name]
        x = vol_flat[sel].astype(np.float64)
        s = np.bincount(lab, weights=x, minlength=n)
        c = np.bincount(lab, minlength=n)
        nz = x != 0
        cz = np.bincount(lab[nz], minlength=n)
        all_.append(s / c)
        with np.errstate(invalid="ignore", divide="ignore"):
            brain.append(np.where(cz > 0, s / np.maximum(cz, 1), np.nan))
    return np.concatenate(all_), np.concatenate(brain)


def process_run(task: dict) -> dict:
    t0 = time.time()
    segs = sorted(task["segments"], key=lambda r: r["onset_tr"])
    P = int(np.prod(GRID_SHAPE))
    ssum = np.zeros(P); ssq = np.zeros(P); nonconst = np.zeros(P, bool)
    first_vals = None
    prev_last = None
    seg_rows, bnd_rows, dvars, dv_is_boundary, gsig = [], [], [], [], []
    roi_all, roi_brain = [], []
    ref_aff = None
    n_tr = 0

    for k, s in enumerate(segs):
        nii = s["meta_path"].replace("_meta.txt", ".nii.gz")
        row = {"participant_id": task["participant_id"], "session": task["session"],
               "run": task["run"], "stimulus_name": s["stimulus_name"],
               "stimulus_number": s["stimulus_number"], "onset_tr": s["onset_tr"],
               "duration_tr": s["duration_tr"], "nifti": nii}
        img = nib.load(nii)
        hdr = img.header
        row.update(shape=str(img.shape), dtype=str(img.get_data_dtype()),
                   zooms=str(tuple(float(z) for z in hdr.get_zooms())),
                   qform_code=int(hdr["qform_code"]), sform_code=int(hdr["sform_code"]))
        if ref_aff is None:
            ref_aff = img.affine
        row["affine_matches_run_reference"] = bool(np.allclose(img.affine, ref_aff))
        row["affine_matches_census_reference"] = bool(np.allclose(img.affine, task["ref_affine"]))
        d = np.asarray(img.dataobj, dtype=np.float32)
        if d.ndim == 3:
            d = d[..., None]
        T = d.shape[3]
        row["n_tr_file"] = int(T)
        row["n_tr_matches_meta"] = bool(T == s["duration_tr"])
        row["grid_ok"] = bool(d.shape[:3] == GRID_SHAPE)
        row["n_nan"] = int(np.isnan(d).sum())
        row["n_inf"] = int(np.isinf(d).sum())
        flat = d.reshape(P, T)
        row["n_all_zero_volumes"] = int((~flat.any(axis=0)).sum())
        row["nonzero_voxels_min_over_tr"] = int((flat != 0).sum(axis=0).min())
        row["mean"] = float(flat[flat != 0].mean()) if (flat != 0).any() else float("nan")
        row["sd"] = float(flat[flat != 0].std()) if (flat != 0).any() else float("nan")

        # voxelwise run accumulators
        f64 = flat.astype(np.float64)
        ssum += f64.sum(1); ssq += (f64 ** 2).sum(1)
        if first_vals is None:
            first_vals = flat[:, 0].copy()
        nonconst |= (flat != first_vals[:, None]).any(axis=1)

        # DVARS across every consecutive pair, including the segment boundary
        within = []
        for t in range(T):
            v = flat[:, t]
            nz = v != 0
            gsig.append(float(v[nz].mean()) if nz.any() else float("nan"))
            if prev_last is not None:
                m = (v != 0) | (prev_last != 0)
                dv = float(np.sqrt(np.mean((v[m] - prev_last[m]) ** 2)))
                dvars.append(dv)
                is_b = (t == 0)
                dv_is_boundary.append(is_b)
                if is_b:
                    bnd = {"participant_id": task["participant_id"], "session": task["session"],
                           "run": task["run"], "boundary_index": k,
                           "prev_stimulus": segs[k - 1]["stimulus_name"],
                           "next_stimulus": s["stimulus_name"],
                           "tr_gap": int(s["onset_tr"] - (segs[k - 1]["onset_tr"] + segs[k - 1]["duration_tr"])),
                           "boundary_dvars": dv}
                    bnd_rows.append(bnd)
                else:
                    within.append(dv)
            prev_last = v.copy()
            a, b = roi_means(v)
            roi_all.append(a); roi_brain.append(b)
        row["within_segment_dvars_mean"] = float(np.mean(within)) if within else float("nan")
        n_tr += T

        # filtered frames
        if CHECK_FRAMES and s["stimulus_number"] == s["stimulus_number"] and s["stimulus_number"] is not None \
                and not s["is_baseline"]:
            fdir = FRAMES / f"{task['participant_id']}_stimulus_{int(s['stimulus_number'])}"
            maxdiff, nfr, ok = 0.0, 0, True
            try:
                import torch
                expect = np.maximum(d[FRAME_CROP], 0)
                for t in range(T):
                    fp = fdir / f"frame_{t}.pt"
                    fr = np.asarray(torch.load(fp, map_location="cpu", weights_only=False))[..., 0]
                    maxdiff = max(maxdiff, float(np.abs(fr - expect[..., t]).max()))
                    nfr += 1
                extra = fdir / f"frame_{T}.pt"
                ok = not extra.exists()
            except Exception as e:  # missing frame or unreadable
                row["frame_error"] = f"{type(e).__name__}: {e}"
                ok = False
            row["n_frames_checked"] = nfr
            row["frame_max_abs_diff_vs_relu_crop"] = maxdiff
            row["frame_count_exact"] = ok
            brain_in = np.abs(d).sum(axis=3) != 0
            crop_mask = np.zeros(GRID_SHAPE, bool); crop_mask[FRAME_CROP] = True
            row["brain_voxels_outside_frame_crop"] = int((brain_in & ~crop_mask).sum())
            row["frac_brain_values_negative_zeroed"] = float((d[brain_in] < 0).mean())
        seg_rows.append(row)

    mean = ssum / n_tr
    sd = np.sqrt(np.maximum(ssq / n_tr - mean ** 2, 0))
    mv, sv = mean[nonconst], sd[nonconst]
    dv = np.array(dvars); isb = np.array(dv_is_boundary, bool)
    gs = np.array(gsig)
    run_row = {
        "participant_id": task["participant_id"], "session": task["session"], "run": task["run"],
        "n_segments": len(segs), "n_tr": n_tr,
        "first_onset_tr": int(segs[0]["onset_tr"]),
        "tiling_contiguous": bool(all(segs[i]["onset_tr"] + segs[i]["duration_tr"] == segs[i + 1]["onset_tr"]
                                      for i in range(len(segs) - 1))),
        "n_nonconstant_voxels": int(nonconst.sum()),
        "voxel_mean_abs_median": float(np.median(np.abs(mv))),
        "voxel_mean_abs_p99": float(np.quantile(np.abs(mv), .99)),
        "voxel_sd_median": float(np.median(sv)),
        "voxel_sd_p01": float(np.quantile(sv, .01)),
        "voxel_sd_p99": float(np.quantile(sv, .99)),
        "frac_voxels_zscored_within_0.02": float(np.mean((np.abs(mv) < .02) & (np.abs(sv - 1) < .02))),
        "dvars_within_median": float(np.median(dv[~isb])) if (~isb).any() else float("nan"),
        "dvars_boundary_median": float(np.median(dv[isb])) if isb.any() else float("nan"),
        "dvars_boundary_over_within": float(np.median(dv[isb]) / np.median(dv[~isb])) if isb.any() else float("nan"),
        "n_tr_dvars_gt_3mad": int(np.sum(dv > np.median(dv) + 3 * 1.4826 * np.median(np.abs(dv - np.median(dv))))),
        "global_signal_sd": float(np.nanstd(gs)),
        "seconds": round(time.time() - t0, 1),
    }
    seg_table = [{"segment": i, "stimulus_name": s["stimulus_name"],
                  "stimulus_number": s["stimulus_number"], "onset_tr": s["onset_tr"],
                  "duration_tr": s["duration_tr"], "is_baseline": s["is_baseline"]}
                 for i, s in enumerate(segs)]
    return {"key": (task["participant_id"], task["session"], task["run"]),
            "segments": seg_rows, "boundaries": bnd_rows, "run": run_row,
            "roi_all": np.asarray(roi_all, np.float32), "roi_brain": np.asarray(roi_brain, np.float32),
            "seg_table": seg_table, "dvars": dv.astype(np.float32), "dvars_is_boundary": isb,
            "nonconst": np.packbits(nonconst)}


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", default=",".join(SUBJECTS))
    ap.add_argument("--max-runs", type=int, default=0, help="smoke test: runs per subject")
    ap.add_argument("--workers", type=int, default=N_WORKERS)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    subs = args.subjects.split(",")

    prov = provenance(SCRIPT, {"frame_crop": str(FRAME_CROP), "workers": args.workers,
                               "max_runs": args.max_runs, "subjects": subs})
    ev = read_tsv(MANIFESTS / "events_audited.tsv")
    ev = ev[ev.participant_id.isin(subs)]
    ev["stimulus_number"] = ev.stimulus_number.astype("float")
    ref_aff = nib.load(ev.meta_path.iloc[0].replace("_meta.txt", ".nii.gz")).affine

    tasks = []
    for (p, ses, run), g in ev.groupby(["participant_id", "session", "run"]):
        tasks.append({"participant_id": p, "session": ses, "run": run, "ref_affine": ref_aff,
                      "segments": [{"meta_path": r.meta_path, "stimulus_name": r.stimulus_name,
                                    "stimulus_number": (None if pd.isna(r.stimulus_number) else int(r.stimulus_number)),
                                    "onset_tr": int(r.onset_tr), "duration_tr": int(r.duration_tr),
                                    "is_baseline": bool(r.is_baseline)} for r in g.itertuples()]})
    if args.max_runs:
        keep = []
        for s in subs:
            keep += [t for t in tasks if t["participant_id"] == s][: args.max_runs]
        tasks = keep
    print(f"  {len(tasks)} runs, {sum(len(t['segments']) for t in tasks)} segments, {args.workers} workers")

    results = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init) as ex:
        futs = [ex.submit(process_run, t) for t in tasks]
        for i, f in enumerate(as_completed(futs), 1):
            results.append(f.result())
            if i % 20 == 0 or i == len(futs):
                print(f"    {i}/{len(futs)} runs, {time.time() - t0:.0f}s", flush=True)
    results.sort(key=lambda r: r["key"])

    tag = f".{args.tag}" if args.tag else ""
    segs = pd.DataFrame([s for r in results for s in r["segments"]])
    bnds = pd.DataFrame([b for r in results for b in r["boundaries"]])
    runs = pd.DataFrame([r["run"] for r in results])

    # subject masks, parcel coverage, reconstructed ROI runs
    QC_MASKS.mkdir(parents=True, exist_ok=True); QC_ROI.mkdir(parents=True, exist_ok=True)
    P = int(np.prod(GRID_SHAPE))
    L = {n: np.load(QC_ATLAS / f"{n}_on_fmri_grid.npy").ravel() for n in ("schaefer", "tian")}
    cov_rows = []
    for s in subs:
        rs = [r for r in results if r["key"][0] == s]
        if not rs:
            continue
        m = np.stack([np.unpackbits(r["nonconst"])[:P].astype(bool) for r in rs])
        union, inter = m.any(0), m.all(0)
        for nm, mk in (("union", union), ("intersection", inter)):
            nib.save(nib.Nifti1Image(mk.reshape(GRID_SHAPE).astype(np.uint8), ref_aff),
                     QC_MASKS / f"{s}_nonconstant_{nm}{tag}.nii.gz")
        for atlas, off in (("schaefer", 0), ("tian", 400)):
            lab = L[atlas]
            n = int(lab.max())
            tot = np.bincount(lab, minlength=n + 1)[1:]
            ci = np.bincount(lab[inter], minlength=n + 1)[1:]
            cu = np.bincount(lab[union], minlength=n + 1)[1:]
            for j in range(n):
                cov_rows.append({"participant_id": s, "atlas": atlas, "label": j + 1, "roi_index": off + j,
                                 "n_voxels": int(tot[j]), "n_in_all_runs": int(ci[j]),
                                 "n_in_any_run": int(cu[j]),
                                 "frac_covered_all_runs": float(ci[j] / tot[j])})
        np.savez_compressed(
            QC_ROI / f"{s}{tag}.npz",
            run_keys=np.array(["|".join(r["key"]) for r in rs]),
            **{f"roi_all__{i}": r["roi_all"] for i, r in enumerate(rs)},
            **{f"roi_brain__{i}": r["roi_brain"] for i, r in enumerate(rs)},
            **{f"segtable__{i}": pd.DataFrame(r["seg_table"]).to_records(index=False) for i, r in enumerate(rs)},
            **{f"dvars__{i}": r["dvars"] for i, r in enumerate(rs)},
            **{f"dvarsb__{i}": r["dvars_is_boundary"] for i, r in enumerate(rs)})
        print(f"  {s}: union {union.sum()} voxels, intersection {inter.sum()} voxels")
    cov = pd.DataFrame(cov_rows)

    st = segs[segs.stimulus_name != "baseline"]
    summ = {
        "provenance": prov,
        "n_runs": int(len(runs)), "n_segments": int(len(segs)),
        "n_boundaries": int(len(bnds)),
        "header": {
            "all_grid_97x115x97": bool(segs.grid_ok.all()),
            "all_affine_identical": bool(segs.affine_matches_census_reference.all()),
            "distinct_zooms": sorted(segs.zooms.unique()),
            "distinct_dtypes": sorted(segs.dtype.unique()),
            "distinct_qform_sform": sorted({f"{a}/{b}" for a, b in zip(segs.qform_code, segs.sform_code)}),
            "all_tr_counts_match_meta": bool(segs.n_tr_matches_meta.all()),
            "n_nan_total": int(segs.n_nan.sum()), "n_inf_total": int(segs.n_inf.sum()),
            "n_all_zero_volumes_total": int(segs.n_all_zero_volumes.sum()),
        },
        "tiling": {
            "all_runs_contiguous": bool(runs.tiling_contiguous.all()),
            "all_runs_start_at_tr0": bool((runs.first_onset_tr == 0).all()),
            "n_boundaries_with_gap_or_overlap": int((bnds.tr_gap != 0).sum()) if len(bnds) else 0,
            "run_length_tr_min": int(runs.n_tr.min()), "run_length_tr_max": int(runs.n_tr.max()),
        },
        "run_zscore": {
            "median_over_runs_of_median_abs_voxel_mean": float(runs.voxel_mean_abs_median.median()),
            "median_over_runs_of_median_voxel_sd": float(runs.voxel_sd_median.median()),
            "min_over_runs_frac_voxels_zscored": float(runs["frac_voxels_zscored_within_0.02"].min()),
            "median_over_runs_frac_voxels_zscored": float(runs["frac_voxels_zscored_within_0.02"].median()),
        },
        "boundary_continuity": {
            "median_boundary_over_within_dvars": float(runs.dvars_boundary_over_within.median()),
            "max_boundary_over_within_dvars": float(runs.dvars_boundary_over_within.max()),
        },
        "frames": ({
            "n_segments_checked": int(st.n_frames_checked.notna().sum()),
            "n_frames_checked": int(st.n_frames_checked.sum()),
            "max_abs_diff_vs_relu_crop": float(st.frame_max_abs_diff_vs_relu_crop.max()),
            "all_frame_counts_exact": bool(st.frame_count_exact.all()),
            "n_frame_errors": int(st["frame_error"].notna().sum()) if "frame_error" in st else 0,
            "brain_voxels_outside_crop_max": int(st.brain_voxels_outside_frame_crop.max()),
            "frac_brain_values_zeroed_by_relu_median": float(st.frac_brain_values_negative_zeroed.median()),
        } if CHECK_FRAMES and "n_frames_checked" in st else {}),
        "coverage": {
            "n_parcels_with_coverage_below_0.5_any_participant": int(
                cov[cov.frac_covered_all_runs < .5].roi_index.nunique()) if len(cov) else None,
            "n_parcels_with_zero_coverage_any_participant": int(
                cov[cov.n_in_all_runs == 0].roi_index.nunique()) if len(cov) else None,
        },
    }
    write_tsv(QC / f"segments_qc{tag}.tsv", segs, prov)
    write_tsv(QC / f"boundaries_qc{tag}.tsv", bnds, prov)
    write_tsv(QC / f"runs_qc{tag}.tsv", runs, prov)
    write_tsv(QC / f"parcel_coverage{tag}.tsv", cov, prov)
    write_json(QC / f"voxel_census{tag}.json", summ)
    import json
    print(json.dumps({k: v for k, v in summ.items() if k != "provenance"}, indent=1, default=str))


if __name__ == "__main__":
    main()
