"""Phase 1 / A1-2, A1-3. Participant and stimulus crosswalk by content hash.

Scientific question
-------------------
Do the stimulus identifiers used by the video files, the annotation table, the
fMRI arrays and the caption table all refer to the same clips, and what exactly
accounts for the difference between the number of video files, the number of
brain presentations, the number of annotated stimuli, and the 2,180 / 2,181
figures the design documents state?

What this excludes
------------------
A raw file hash alone cannot distinguish a re-encoded copy of the same clip
from a genuinely different clip, so it cannot by itself rule out that a
train/test split separates two files that a model would see as the same
stimulus. A1-3 therefore requires a hash over decoded frames as well. Without
both, every downstream split inherits an unchecked leakage assumption.

Method notes
------------
The system ffmpeg has no h264 decoder, so decoding uses the one binary on this
machine that does. Each clip is decoded to 32x32 grayscale. Two signatures are
derived. `decoded_sha256` is a hash over every decoded frame and detects an
exact re-encode. `clip_dhash` is a 56 bit difference hash of the temporally
averaged frame and supports a near-duplicate search by Hamming distance, which
catches re-encodes that differ by a compression artifact.

Outputs
-------
manifests/stimuli.tsv             one row per video file, raw and decoded hashes
manifests/stimulus_crosswalk.tsv  canonical stimulus id joined across sources
manifests/duplicate_report.tsv    duplicate and near-duplicate groups
manifests/participants.tsv        one row per participant with brain key summary
manifests/crosswalk_audit.json    counts and verdicts
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

from _assets import (  # noqa: E402
    ASSETS,
    DOC_CLAIMS,
    FFMPEG_DECODE,
    FFPROBE,
    MANIFESTS,
    provenance,
    read_tsv,
    write_json,
    write_tsv,
)

SCRIPT = "prereg_v2/code/p1_stimulus_crosswalk.py"
DECODE_SIDE = 32          # decoded frame is DECODE_SIDE x DECODE_SIDE grayscale
NEAR_DUP_MAX_HAMMING = 4  # reported, not acted on, so the threshold is auditable
SIG_FRAMES = 16           # temporal resampling length of the clip signature
NEAR_DUP_MIN_R = 0.95     # candidate threshold on the clip-signature correlation
NEAR_DUP_CONFIRM_R = 0.98 # at or above this a pair is treated as one split unit
N_WORKERS = 8


# ------------------------------------------------------------ media probe ---
def probe_one(path_str: str) -> dict:
    """Container and stream properties, plus decoded-frame signatures."""
    out: dict = {"path": path_str}
    try:
        r = subprocess.run(
            [FFPROBE, "-v", "error", "-print_format", "json",
             "-show_streams", "-show_format", path_str],
            capture_output=True, text=True, timeout=60)
        meta = json.loads(r.stdout)
        vs = [s for s in meta.get("streams", []) if s.get("codec_type") == "video"]
        aus = [s for s in meta.get("streams", []) if s.get("codec_type") == "audio"]
        v = vs[0] if vs else {}
        num, _, den = (v.get("r_frame_rate") or "0/1").partition("/")
        out.update(
            container_duration_s=float(meta.get("format", {}).get("duration", "nan")),
            video_codec=v.get("codec_name"),
            width=int(v.get("width", 0) or 0),
            height=int(v.get("height", 0) or 0),
            frame_rate=(float(num) / float(den)) if float(den or 0) else float("nan"),
            nb_frames_declared=int(v.get("nb_frames", 0) or 0),
            n_audio_streams=len(aus),
            has_audio=bool(aus),
            probe_ok=True,
        )
        # The repository README describes this stimulus set as silent and
        # treats the silence as a control that removes soundtrack and dialogue
        # as an explanation. Whether an audio track exists, and whether it
        # actually carries signal, is therefore checked rather than assumed.
        out["audio_mean_volume_db"] = float("nan")
        out["audio_max_volume_db"] = float("nan")
        if aus:
            rv = subprocess.run(
                [FFMPEG_DECODE, "-nostdin", "-v", "info", "-i", path_str,
                 "-map", "0:a:0", "-af", "volumedetect", "-f", "null", "-"],
                capture_output=True, text=True, timeout=120)
            for line in rv.stderr.splitlines():
                if "mean_volume:" in line:
                    out["audio_mean_volume_db"] = float(line.split("mean_volume:")[1].split("dB")[0])
                if "max_volume:" in line:
                    out["audio_max_volume_db"] = float(line.split("max_volume:")[1].split("dB")[0])
    except Exception as e:
        out.update(probe_ok=False, probe_error=f"{type(e).__name__}: {e}")

    try:
        r = subprocess.run(
            [FFMPEG_DECODE, "-v", "error", "-i", path_str,
             "-vf", f"scale={DECODE_SIDE}:{DECODE_SIDE},format=gray",
             "-c:v", "rawvideo", "-f", "rawvideo", "-"],
            capture_output=True, timeout=300)
        buf = np.frombuffer(r.stdout, dtype=np.uint8)
        px = DECODE_SIDE * DECODE_SIDE
        if buf.size == 0 or buf.size % px:
            raise ValueError(f"decoded {buf.size} bytes, not a multiple of {px}")
        frames = buf.reshape(-1, DECODE_SIDE, DECODE_SIDE)
        # 8x8 block means per frame, quantized, hashed over the whole clip
        blocks = frames.reshape(-1, 8, 4, 8, 4).mean(axis=(2, 4))
        q = np.round(blocks).astype(np.uint8)
        import hashlib
        out["decoded_sha256"] = hashlib.sha256(q.tobytes()).hexdigest()
        out["n_decoded_frames"] = int(frames.shape[0])
        # 56 bit difference hash of the temporally averaged frame
        mean_block = blocks.mean(axis=0)
        bits = (mean_block[:, :-1] > mean_block[:, 1:]).ravel()
        out["clip_dhash"] = int("".join("1" if b else "0" for b in bits), 2)
        # Fixed-length clip signature. Decoding to a common spatial grid and
        # resampling to a common frame count makes the signature invariant to
        # resolution, frame rate and clip length, which a difference hash of a
        # single averaged frame is not. Two clips that are the same scene at
        # different resolutions score near 1 here and are missed by both hashes.
        idxs = np.linspace(0, blocks.shape[0] - 1, SIG_FRAMES)
        sig = blocks[np.round(idxs).astype(int)].ravel().astype(np.float32)
        sig = sig - sig.mean()
        nrm = float(np.linalg.norm(sig))
        out["clip_signature"] = (sig / nrm) if nrm > 0 else sig
        out["decode_ok"] = True
    except Exception as e:
        out.update(decode_ok=False, decode_error=f"{type(e).__name__}: {e}",
                   decoded_sha256="", n_decoded_frames=0, clip_dhash=-1,
                   clip_signature=np.zeros(SIG_FRAMES * 64, dtype=np.float32))
    return out


def popcount64(x: np.ndarray) -> np.ndarray:
    x = x.astype(np.uint64)
    m1 = np.uint64(0x5555555555555555)
    m2 = np.uint64(0x3333333333333333)
    m4 = np.uint64(0x0F0F0F0F0F0F0F0F)
    x = x - ((x >> np.uint64(1)) & m1)
    x = (x & m2) + ((x >> np.uint64(2)) & m2)
    x = (x + (x >> np.uint64(4))) & m4
    return ((x * np.uint64(0x0101010101010101)) >> np.uint64(56)).astype(np.int64)


# -------------------------------------------------------------- loaders -----
def load_video_rows() -> pd.DataFrame:
    """Raw-file hashes come from p0; they are not recomputed here."""
    inv = read_tsv(MANIFESTS / "file_inventory.tsv")
    v = inv[inv.asset == "stimulus_videos"].copy()
    v["video_number"] = v.filename.str.replace(".mp4", "", regex=False).astype(int)
    return v.sort_values("video_number").reset_index(drop=True)


def load_brain_keys() -> tuple[pd.DataFrame, dict]:
    spec = ASSETS["brain_roi_timeseries"]
    rows, detail = [], {}
    for pt in sorted(Path(spec["path"]).glob(spec["glob"])):
        d = torch.load(pt, map_location="cpu", weights_only=False)
        stim = np.asarray(d["stim_num"]).astype(int)
        ot = np.asarray(d["original_T"]).astype(int)
        rows.append({
            "participant_id": pt.stem,
            "cohort": "horikawa_2020",
            "source_file": str(pt),
            "n_stimuli": len(stim),
            "n_unique_stimuli": len(np.unique(stim)),
            "n_repeated_stimuli": int(len(stim) - len(np.unique(stim))),
            "stim_min": int(stim.min()),
            "stim_max": int(stim.max()),
            "roi_mean_shape": str(tuple(d["roi_mean"].shape)),
            "roi_timeseries_shape": str(tuple(d["roi_timeseries"].shape)),
            "n_roi": int(d["n_roi"]),
            "T_max": int(d["T_max"]),
            "original_T_min": int(ot.min()),
            "original_T_max": int(ot.max()),
            "original_T_mean": float(ot.mean()),
            "n_missing_stim": int(np.asarray(d["missing_stim"]).size),
        })
        detail[pt.stem] = stim
    return pd.DataFrame(rows), detail


# ----------------------------------------------------------------- main -----
def main() -> None:
    prov = provenance(SCRIPT, {"decode_side": DECODE_SIDE,
                               "ffmpeg_decode": FFMPEG_DECODE,
                               "ffprobe": FFPROBE})
    audit: dict = {"provenance": prov}

    vids = load_video_rows()
    print(f"  probing {len(vids)} video files with {N_WORKERS} workers")
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        probes = list(ex.map(probe_one, vids.path.tolist(), chunksize=16))
    vids = vids.merge(pd.DataFrame(probes), on="path", how="left")

    n_bad = int((~vids.decode_ok.fillna(False)).sum())
    print(f"  decode failures: {n_bad}")

    # ---- duplicate structure ------------------------------------------------
    def groups(col: str) -> dict:
        g: dict = defaultdict(list)
        for _, r in vids.iterrows():
            if isinstance(r[col], str) and not r[col]:
                continue
            g[r[col]].append(int(r.video_number))
        return {k: sorted(v) for k, v in g.items() if len(v) > 1}

    raw_dups = groups("sha256")
    dec_dups = groups("decoded_sha256")

    # canonical stimulus id: lowest video number sharing decoded content
    canon = {int(n): int(n) for n in vids.video_number}
    for nums in dec_dups.values():
        for n in nums:
            canon[n] = min(nums)
    vids["canonical_video_number"] = vids.video_number.map(canon)
    vids["is_exact_duplicate_file"] = vids.video_number != vids.canonical_video_number

    # Near duplicates by correlation of the resolution-invariant clip
    # signature. The difference hash is kept as a second, weaker view so the
    # two can be compared, but the signature is what the split acts on.
    sig = np.vstack(vids.clip_signature.to_numpy())
    nums = vids.video_number.to_numpy()
    R = sig @ sig.T
    np.fill_diagonal(R, -1.0)
    ia, ib = np.nonzero(np.triu(R >= NEAR_DUP_MIN_R, k=1))
    h = vids.clip_dhash.to_numpy(dtype=np.uint64)
    near_rows = []
    for i, j in zip(ia, ib):
        a, b = int(nums[i]), int(nums[j])
        near_rows.append({
            "video_a": a, "video_b": b,
            "signature_r": float(R[i, j]),
            "dhash_hamming": int(popcount64(np.array([h[i] ^ h[j]]))[0]),
            "same_decoded_sha256": canon[a] == canon[b],
            "confirmed_same_content": bool(R[i, j] >= NEAR_DUP_CONFIRM_R),
        })
    near_rows.sort(key=lambda r: -r["signature_r"])

    # Confirmed near duplicates that are NOT byte or decoded-content identical
    # are merged into the canonical id as well: a split that separated them
    # would put the same scene in train and in test.
    extra_merges = [(r["video_a"], r["video_b"]) for r in near_rows
                    if r["confirmed_same_content"] and not r["same_decoded_sha256"]]
    for a, b in extra_merges:
        lo, hi = min(canon[a], canon[b]), max(canon[a], canon[b])
        for k_, v_ in list(canon.items()):
            if v_ == hi:
                canon[k_] = lo
    vids["canonical_video_number"] = vids.video_number.map(canon)
    vids["is_exact_duplicate_file"] = vids.video_number != vids.canonical_video_number

    dup_rows = (
        [{"group_type": "raw_file_sha256", "key": k, "n_files": len(v),
          "video_numbers": ",".join(map(str, v)), "canonical_video_number": min(v)}
         for k, v in raw_dups.items()]
        + [{"group_type": "decoded_frame_sha256", "key": k, "n_files": len(v),
            "video_numbers": ",".join(map(str, v)), "canonical_video_number": min(v)}
           for k, v in dec_dups.items()]
    )

    audit["videos"] = {
        "n_video_files": int(len(vids)),
        "n_unique_raw_sha256": int(vids.sha256.nunique()),
        "n_unique_decoded_sha256": int(vids.decoded_sha256.replace("", np.nan).nunique()),
        "n_raw_duplicate_groups": len(raw_dups),
        "n_decoded_duplicate_groups": len(dec_dups),
        "n_exact_duplicate_files": int(vids.is_exact_duplicate_file.sum()),
        "n_canonical_stimuli": int(vids.canonical_video_number.nunique()),
        "n_near_duplicate_candidate_pairs": len(near_rows),
        "n_near_duplicate_confirmed_pairs": int(sum(
            r["confirmed_same_content"] for r in near_rows)),
        "n_confirmed_near_duplicates_missed_by_both_hashes": len(extra_merges),
        "confirmed_near_duplicate_pairs_missed_by_hashes": extra_merges,
        "near_duplicate_candidate_threshold_signature_r": NEAR_DUP_MIN_R,
        "near_duplicate_confirm_threshold_signature_r": NEAR_DUP_CONFIRM_R,
        "n_decode_failures": n_bad,
        "video_number_min": int(vids.video_number.min()),
        "video_number_max": int(vids.video_number.max()),
        "any_audio_stream": bool(vids.has_audio.fillna(False).any()),
        "n_with_audio": int(vids.has_audio.fillna(False).sum()),
        "audio_clips": [
            {"video_number": int(r.video_number),
             "mean_volume_db": float(r.audio_mean_volume_db),
             "max_volume_db": float(r.audio_max_volume_db)}
            for _, r in vids[vids.has_audio.fillna(False)].iterrows()],
        "container_duration_s_min": float(vids.container_duration_s.min()),
        "container_duration_s_max": float(vids.container_duration_s.max()),
        "container_duration_s_mean": float(vids.container_duration_s.mean()),
        "distinct_resolutions": sorted(
            {f"{int(w)}x{int(h_)}" for w, h_ in zip(vids.width, vids.height)}),
        "distinct_frame_rates": sorted({round(float(x), 4)
                                        for x in vids.frame_rate.dropna()}),
        "distinct_video_codecs": sorted(set(vids.video_codec.dropna())),
    }

    # ---- annotations --------------------------------------------------------
    lab = pd.read_csv(ASSETS["labels_emobrain"]["path"])
    lab_alt = pd.read_csv(ASSETS["labels_emovis"]["path"])
    audit["labels"] = {
        "n_rows": int(len(lab)),
        "n_columns": int(lab.shape[1]),
        "stim_num_int_min": int(lab.stim_num_int.min()),
        "stim_num_int_max": int(lab.stim_num_int.max()),
        "n_unique_stim_num_int": int(lab.stim_num_int.nunique()),
        "n_duplicate_stim_num_int": int(lab.stim_num_int.duplicated().sum()),
        "emovis_copy_identical": bool(lab.equals(lab_alt)),
        "video_path_column_example": str(lab.video_path.iloc[0]),
        "video_path_column_root_exists": bool(
            Path(str(lab.video_path.iloc[0])).parent.exists()),
    }

    cap = pd.read_csv(ASSETS["captions_human"]["path"])
    cap.columns = [c.lstrip("﻿") for c in cap.columns]
    cc = cap.groupby("video_id").size()
    audit["captions"] = {
        "n_rows": int(len(cap)),
        "n_unique_video_id": int(cap.video_id.nunique()),
        "video_id_min": int(cap.video_id.min()),
        "video_id_max": int(cap.video_id.max()),
        "captions_per_video_min": int(cc.min()),
        "captions_per_video_max": int(cc.max()),
        "captions_per_video_modal": int(cc.mode().iloc[0]),
        "n_videos_with_nonmodal_count": int((cc != cc.mode().iloc[0]).sum()),
        "n_empty_descriptions": int(
            cap.description.isna().sum()
            + (cap.description.astype(str).str.strip() == "").sum()),
    }

    # ---- brain --------------------------------------------------------------
    parts, brain_keys = load_brain_keys()
    fmri = np.load(ASSETS["brain_roi_matrix"]["path"], mmap_mode="r")
    msi = np.load(ASSETS["main_stim_indices"]["path"])
    ref = parts.participant_id.iloc[0]
    audit["brain"] = {
        "n_participants": int(len(parts)),
        "participant_ids": parts.participant_id.tolist(),
        "roi_key_sets_identical_across_participants": bool(
            all(np.array_equal(brain_keys[k], brain_keys[ref]) for k in brain_keys)),
        "fmri_raw_shape": list(fmri.shape),
        "fmri_raw_n_presentations": int(fmri.shape[1]),
        "roi_timeseries_n_stimuli": int(parts.n_stimuli.iloc[0]),
        "n_presentations_without_roi_timeseries_row": int(
            fmri.shape[1] - parts.n_stimuli.iloc[0]),
        "main_stim_indices_len": int(msi.size),
        "main_stim_indices_min": int(msi.min()),
        "main_stim_indices_max": int(msi.max()),
        "main_stim_indices_is_plain_arange": bool(
            np.array_equal(msi, np.arange(msi.size))),
    }

    # Does fmri_raw row j hold the roi_mean of stimulus j+1? Verified, not assumed.
    d0 = torch.load(Path(ASSETS["brain_roi_timeseries"]["path"]) / f"{ref}.pt",
                    map_location="cpu", weights_only=False)
    rm = np.asarray(d0["roi_mean"], dtype=np.float64)
    order = np.argsort(np.asarray(d0["stim_num"]))
    head = np.asarray(fmri[0, :rm.shape[0]], dtype=np.float64)
    audit["brain"]["fmri_raw_row_j_equals_roi_mean_of_stim_j_plus_1"] = {
        "max_abs_diff": float(np.abs(head - rm[order]).max()),
        "verdict": bool(np.abs(head - rm[order]).max() < 1e-5),
    }

    # ---- canonical crosswalk ------------------------------------------------
    brain_stims = {int(x) for x in brain_keys[ref]}
    label_stims = {int(x) for x in lab.stim_num_int}
    caption_ids = {int(x) for x in cap.video_id.unique()}
    video_nums = {int(x) for x in vids.video_number}
    # every video number 1..2196 has a presentation row in fmri_raw
    fmri_stims = set(range(1, int(fmri.shape[1]) + 1))

    idx = vids.set_index("video_number")
    cw = pd.DataFrame([{
        "video_number": n,
        "video_filename": f"{n:04d}.mp4",
        "canonical_stimulus_id": canon[n],
        "raw_sha256": idx.at[n, "sha256"],
        "decoded_sha256": idx.at[n, "decoded_sha256"],
        "is_exact_duplicate_file": n != canon[n],
        "in_labels": n in label_stims,
        "in_brain_roi_timeseries": n in brain_stims,
        "in_fmri_raw_presentations": n in fmri_stims,
        "in_captions": n in caption_ids,
    } for n in sorted(video_nums)])
    cw["usable_for_modeling"] = (cw.in_labels & cw.in_brain_roi_timeseries
                                 & cw.in_captions)

    audit["crosswalk"] = {
        "n_video_numbers": len(video_nums),
        "n_in_labels": int(cw.in_labels.sum()),
        "n_in_brain_roi_timeseries": int(cw.in_brain_roi_timeseries.sum()),
        "n_in_fmri_raw_presentations": int(cw.in_fmri_raw_presentations.sum()),
        "n_in_captions": int(cw.in_captions.sum()),
        "n_usable_for_modeling": int(cw.usable_for_modeling.sum()),
        "n_canonical_usable_stimuli": int(
            cw[cw.usable_for_modeling].canonical_stimulus_id.nunique()),
        "video_numbers_without_labels": sorted(video_nums - label_stims),
        "video_numbers_without_brain_roi": sorted(video_nums - brain_stims),
        "video_numbers_without_captions": sorted(video_nums - caption_ids),
        "labels_not_in_videos": sorted(label_stims - video_nums),
        "brain_roi_not_in_videos": sorted(brain_stims - video_nums),
        "captions_not_in_videos": sorted(caption_ids - video_nums),
    }

    # ---- reconciliation against document claims -----------------------------
    can_counts = cw.groupby("canonical_stimulus_id").size()
    can_counts_annotated = (cw[cw.usable_for_modeling]
                            .groupby("canonical_stimulus_id").size())
    measured = {
        "video_files": int(len(vids)),
        "canonical_stimuli_all_files": int(vids.canonical_video_number.nunique()),
        "annotated_stimuli": int(len(lab)),
        "brain_roi_stimuli_per_participant": int(parts.n_stimuli.iloc[0]),
        "fmri_raw_presentations": int(fmri.shape[1]),
        "participants": int(len(parts)),
        "usable_for_modeling": int(cw.usable_for_modeling.sum()),
        "canonical_usable_stimuli": int(
            cw[cw.usable_for_modeling].canonical_stimulus_id.nunique()),
        # A canonical stimulus shown twice is a repeated presentation even when
        # the two presentations carry different file numbers. This is the only
        # source of repeat reliability in this dataset.
        "canonical_stimuli_with_more_than_one_presentation": int((can_counts > 1).sum()),
        "canonical_stimuli_with_more_than_one_annotated_presentation": int(
            (can_counts_annotated > 1).sum()),
        "max_presentations_of_any_canonical_stimulus": int(can_counts.max()),
    }
    audit["repeat_structure"] = {
        "canonical_stimuli_with_2_presentations": sorted(
            int(x) for x in can_counts[can_counts > 1].index),
        "canonical_stimuli_with_2_annotated_presentations": sorted(
            int(x) for x in can_counts_annotated[can_counts_annotated > 1].index),
        "note": ("prereg_v2 D7 and B9 reserve 72 repeated stimuli for "
                 "reliability, noise ceiling and final held-out evaluation, "
                 "and action_items A4-2 selects the response estimator by "
                 "repeated-test reliability. The measured count sets the "
                 "ceiling on all of those."),
    }
    audit["document_claim_reconciliation"] = {
        "claims": DOC_CLAIMS,
        "measured": measured,
        "resolution": {
            "2196_video_files": "presentations; every one has an fmri_raw row and a caption",
            "2185_annotated": "2196 minus videos 2186-2196, which have no annotation row "
                              "and no roi_timeseries entry",
            "2181_unique_by_content_hash": "2196 minus 15 files whose decoded frames are "
                                           "byte identical to an earlier file; equals the "
                                           "figure in prereg_v2 D5 replication and in README",
            "2180_unique_after_near_duplicate_merge": "2181 minus the pair (1349, 1363), "
                                                      "the same scene at two resolutions, "
                                                      "which both hashes miss; equals the "
                                                      "figure in prereg_v2 D5 primary",
            "verdict": "the 2180 and 2181 figures differ by exactly one rescaled copy "
                       "and both are reachable from this one stimulus set",
        },
        "residual_gaps": {
            "prereg_v2_D5_replication_unique_2181_minus_measured_canonical": (
                DOC_CLAIMS["prereg_v2_D5_replication_unique_stimuli"]
                - measured["canonical_usable_stimuli"]),
            "prereg_v2_D5_primary_unique_2180_minus_measured_canonical": (
                DOC_CLAIMS["prereg_v2_D5_primary_unique_stimuli"]
                - measured["canonical_usable_stimuli"]),
            "prereg_v2_D7_repeated_test_72_minus_measured_canonical_repeats": (
                DOC_CLAIMS["prereg_v2_D7_repeated_test_stimuli"]
                - measured["canonical_stimuli_with_more_than_one_presentation"]),
        },
    }

    np.save(MANIFESTS / "clip_signatures.npy", sig)
    np.save(MANIFESTS / "clip_signature_video_numbers.npy", nums)
    write_tsv(MANIFESTS / "stimuli.tsv", vids.drop(columns=["clip_signature"]), prov)
    write_tsv(MANIFESTS / "stimulus_crosswalk.tsv", cw, prov)
    write_tsv(MANIFESTS / "duplicate_report.tsv",
              pd.DataFrame(dup_rows) if dup_rows else
              pd.DataFrame(columns=["group_type", "key", "n_files",
                                    "video_numbers", "canonical_video_number"]), prov)
    write_tsv(MANIFESTS / "near_duplicate_pairs.tsv",
              pd.DataFrame(near_rows) if near_rows else
              pd.DataFrame(columns=["video_a", "video_b", "signature_r",
                                    "dhash_hamming", "same_decoded_sha256",
                                    "confirmed_same_content"]), prov)
    write_tsv(MANIFESTS / "participants.tsv", parts, prov)
    write_json(MANIFESTS / "crosswalk_audit.json", audit)

    print("\n  ---- measured ----")
    for k, v in measured.items():
        print(f"    {k}: {v}")
    print("  ---- duplicates ----")
    for k in ["n_unique_raw_sha256", "n_unique_decoded_sha256",
              "n_decoded_duplicate_groups", "n_canonical_stimuli",
              "n_near_duplicate_candidate_pairs", "n_near_duplicate_confirmed_pairs",
              "n_confirmed_near_duplicates_missed_by_both_hashes",
              "n_decode_failures", "n_with_audio"]:
        print(f"    {k}: {audit['videos'][k]}")


if __name__ == "__main__":
    main()
