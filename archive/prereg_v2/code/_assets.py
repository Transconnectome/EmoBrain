"""Asset registry for EmoBrain prereg_v2 Phase 0-3 audit.

Single source of truth for which files the audit touches. Every path listed
here is read-only. Nothing in this project writes outside PREREG_ROOT.

`declared` records what the project documents claim about an asset. `verified`
status is produced by the audit scripts and is never written back into this
file, so that a document claim and a measurement can never be confused.

Design documents this registry is checked against, in the reading order the
project specifies:
  design_docs/AGENTS.md
  design_docs/action_items_v1.md   Phase 0-3 = A0-*, A1-*, A2-*, A3-*
  design_docs/paper_v15.md
  design_docs/prereg_v2.md         D1-D8, L1-L11, B1-B10
  design_docs/implementation_v2.md 3.1 participant/stimulus manifest
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

SCRATCH = Path("/pscratch/sd/s/sjmoon")
PREREG_ROOT = SCRATCH / "EmoBrain" / "prereg_v2"
DESIGN_DOCS = PREREG_ROOT / "design_docs"
MANIFESTS = PREREG_ROOT / "manifests"
SPLITS = PREREG_ROOT / "splits"
CONFIGS = PREREG_ROOT / "configs"
TESTS = PREREG_ROOT / "tests"
LOGS = PREREG_ROOT / "logs"
SUPERSEDED = MANIFESTS / "superseded"

# The system ffmpeg at /usr/bin has no h264 decoder, so decoded-frame work
# (A1-3 perceptual hash) uses the one binary on this machine that does.
PYTHON = "/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python"
FFPROBE = "/usr/bin/ffprobe"
FFMPEG_DECODE = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffmpeg"

# ---------------------------------------------------------------- assets ----
# kind:
#   file          single file, content hashed
#   dir_files     glob inside a directory, each file content hashed
#   dir_summary   too large to content hash; size and file count only
#   absence_check declared by a document; recorded as absent unless found
ASSETS = {
    # ---- stimuli -----------------------------------------------------------
    "stimulus_videos": dict(
        kind="dir_files",
        path=SCRATCH / "EmoViS/data/raw/CowenEmotionVideos",
        glob="*.mp4",
        declared="Cowen-Keltner emotional video clips presented in Horikawa fMRI",
        hash_contents=True,
    ),
    # ---- annotations -------------------------------------------------------
    "labels_emobrain": dict(
        kind="file",
        path=SCRATCH / "EmoBrain/project/shared/data/cowen_horikawa_labels.csv",
        declared="34 category proportions + 14 affective dimensions per stimulus",
        hash_contents=True,
    ),
    "labels_emovis": dict(
        kind="file",
        path=SCRATCH / "EmoViS/study1/data/master_stimulus_index.csv",
        declared="same table, EmoViS copy",
        hash_contents=True,
    ),
    "captions_human": dict(
        kind="file",
        path=SCRATCH / "EmoBrain/project/shared/data/caption_ck20.csv",
        declared="MindCaptioning-style human captions, reported as 20 raters per clip",
        hash_contents=True,
    ),
    # ---- brain: ROI level --------------------------------------------------
    "brain_roi_timeseries": dict(
        kind="dir_files",
        path=SCRATCH / "EmoBrain/project/shared/data/roi_timeseries",
        glob="sub-*.pt",
        declared="per-subject ROI time series and per-stimulus ROI mean, 450 parcels",
        hash_contents=True,
    ),
    "brain_roi_matrix": dict(
        kind="file",
        path=SCRATCH / "EmoViS/data/raw/fmri_raw.npy",
        declared="(n_subject, n_presentation, 450) ROI matrix",
        hash_contents=True,
    ),
    "main_stim_indices": dict(
        kind="file",
        path=SCRATCH / "EmoViS/study1/data/main_stim_indices.npy",
        declared="index selecting unique stimuli out of presentations",
        hash_contents=True,
    ),
    # ---- brain: voxel level and event metadata -----------------------------
    "brain_voxel_step7": dict(
        kind="dir_summary",
        path=SCRATCH / "EmoViS/data/raw/step7_voxel",
        declared="per-stimulus NIfTI in MNI plus per-stimulus and per-run metadata",
        hash_contents=False,
    ),
    "horikawa_embedding_root": dict(
        kind="dir_summary",
        path=SCRATCH / "Horikawa_embedding",
        declared="raw MNI volumes per TR and derived embeddings",
        hash_contents=False,
    ),
    # ---- datasets declared in prereg_v2 but not yet confirmed locally -------
    "mindcaptioning_ds005191": dict(
        kind="absence_check",
        path=SCRATCH / "ds005191",
        declared="prereg_v2 D1 PRIMARY cohort, 6 participants, unique stimuli 2180",
        hash_contents=False,
    ),
    "emofilm_ds004872": dict(
        kind="dir_summary",
        path=SCRATCH / "ds004872",
        declared="Emo-FilM; no role in prereg_v2 D1-D8",
        hash_contents=False,
    ),
    "emofilm_local": dict(
        kind="dir_summary",
        path=SCRATCH / "Emo-FilM",
        declared="second local copy of Emo-FilM; role undeclared",
        hash_contents=False,
    ),
}

# Per-subject event metadata inside brain_voxel_step7. Handled separately from
# ASSETS because it is parsed, not hashed as an opaque blob.
EVENT_META_ROOT = SCRATCH / "EmoViS/data/raw/step7_voxel"
EVENT_META_GLOB = "*_meta.txt"
RUN_SUMMARY_GLOB = "*_stimulus_summary.txt"

# Paths that project documents or data files reference but that may not exist.
DECLARED_PATHS_TO_VERIFY = {
    "labels_video_path_column_root": SCRATCH / "EmoFM/videos/CowenEmotionVideos",
    "step7_source_preprocessing_root": Path("/storage/bigdata/Horikawa/preprocessing_output"),
    "step7_source_events_root": Path("/storage/bigdata/Horikawa/raw"),
}

# Numeric claims made by the design documents, to be reconciled, never assumed.
DOC_CLAIMS = {
    "prereg_v2_D1_primary_cohort_n_participants": 6,
    "prereg_v2_D2_replication_cohort_n_participants": 5,
    "prereg_v2_D5_primary_unique_stimuli": 2180,
    "prereg_v2_D5_primary_modeling_train": 2108,
    "prereg_v2_D5_primary_repeated_test": 72,
    "prereg_v2_D5_replication_unique_stimuli": 2181,
    "prereg_v2_D6_stimulus_pairs_not_independent": 2556,
    "prereg_v2_D7_repeated_test_stimuli": 72,
    "readme_horikawa_unique_stimuli": 2181,
    "context_emobrain_unique_stimuli": 2185,
    "context_emobrain_presentations": 2196,
    "captions_raters_per_clip": 20,
}


# ------------------------------------------------------------- utilities ----
def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def git_commit(repo: Path = SCRATCH / "EmoBrain") -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=20,
        ).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def provenance(script: str, extra: dict | None = None) -> dict:
    """Provenance block stamped into every artifact this project writes."""
    p = {
        "generated_by": script,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_commit": git_commit(),
        "python": PYTHON,
        "asset_registry": str(Path(__file__).resolve()),
        "asset_registry_sha256": sha256_file(Path(__file__).resolve()),
    }
    if extra:
        p.update(extra)
    return p


def _preserve(path: Path) -> None:
    """Move an existing artifact aside instead of destroying it.

    The instruction is not to overwrite existing files. A re-run therefore
    archives the previous artifact under its own modification time, so that a
    number quoted from an earlier run can always be traced to the file that
    produced it.
    """
    if not path.exists():
        return
    SUPERSEDED.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(path.stat().st_mtime))
    dest = SUPERSEDED / f"{path.stem}.{stamp}{path.suffix}"
    i = 0
    while dest.exists():
        i += 1
        dest = SUPERSEDED / f"{path.stem}.{stamp}.{i}{path.suffix}"
    shutil.move(str(path), str(dest))
    print(f"  preserved previous artifact -> {dest}")


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _preserve(path)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, default=str)
    print(f"  wrote {path}")


def write_tsv(path: Path, df, provenance_block: dict) -> None:
    """Write a TSV with a commented provenance header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    _preserve(path)
    with open(path, "w") as fh:
        for k, v in provenance_block.items():
            fh.write(f"# {k}\t{v}\n")
        df.to_csv(fh, sep="\t", index=False)
    print(f"  wrote {path}  ({len(df)} rows)")


def read_tsv(path: Path):
    import pandas as pd
    return pd.read_csv(path, sep="\t", comment="#")
