"""Pilot data adapter and development audit (BOARD T004).

What this module answers
------------------------
Can every v2 block-response row be tied, without guessing from array order, to
one participant, one run, one canonical video content and at most one
annotation row, and can the full observation manifest be split by connected
run/content components without leaking reserved test content?

What it provides
----------------
- ``build_manifest``: the FULL observation manifest for one or both cohorts,
  with canonical content IDs, reserved final-test content propagated across
  every participant and cohort, connected run groups, annotation join status
  and an immutable preprocessing ID per participant.
- ``to_observations``: rows for ``project.code.pilot_contracts.Observation``.
- ``exclusion_manifest``: pilot-only quarantine of rows whose annotation join is
  missing or ambiguous. This is not a permanent study exclusion and never
  averages conflicting annotation rows (T003 is unresolved).
- ``select_dev_subset``: a deterministic, metadata-only development subset.
- ``load_student_batch`` / ``load_content_features``: the batch contract. A
  ``StudentBatch`` has no content-feature fields at all; a ``TeacherBatch``
  composes a student batch with ``ContentFeatures``. Student code therefore
  cannot receive video or caption inputs by accident.

What it does not do
-------------------
It does not choose a target policy for duplicate annotation rows (T003), decide
whether Horikawa keeps both 1349 and 1363 (T002), embed captions, extract
low-level features, fit any model or select preprocessing. Human-caption
sentence embeddings and low-level visual features are not on the server; the
adapter reports them as missing instead of substituting generated captions.

Run the audit with ``bash project/data/pilot_adapter.sh`` (see that file).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SCRATCH = Path("/pscratch/sd/s/sjmoon")

COHORT_DIRS = {"mindcaptioning": "MindCaptioning", "horikawa": "Horikawa"}
BRAIN_VARIANTS = {"runz": "blocks_common36_runz", "raw": "blocks_common36"}
TARGET_SPACES = ("cat34", "affect14")
AFFECT14 = (
    "arousal_score", "dominance_score", "valence_score", "approach_score",
    "attention_score", "certainty_score", "commitment_score", "control_score",
    "effort_score", "fairness_score", "identity_score", "obstruction_score",
    "safety_score", "upswing_score",
)
NEAR_DUPLICATE_POLICIES = ("merge", "hash_only")


@dataclass(frozen=True)
class DataPaths:
    cohort_roots: Mapping[str, Path]
    labels_csv: Path
    order34: Path
    captions_csv: Path
    video_features: Path
    crosswalk_tsv: Path


DEFAULT_PATHS = DataPaths(
    cohort_roots={k: SCRATCH / v for k, v in COHORT_DIRS.items()},
    labels_csv=REPO / "project/shared/data/cowen_horikawa_labels.csv",
    order34=REPO / "project/shared/data/cowen34_order.txt",
    captions_csv=REPO / "project/shared/data/caption_ck20.csv",
    video_features=REPO / "project/shared/data/stimulus_features/vjepa2_pretrained.npy",
    crosswalk_tsv=REPO / "prereg_v2/manifests/stimulus_crosswalk.tsv",
)


# --------------------------------------------------------------- utilities --
def sha256_file(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", comment="#")


def participant_dirs(paths: DataPaths, cohort: str) -> list[Path]:
    root = Path(paths.cohort_roots[cohort])
    return sorted(p / "v2" for p in root.glob("sub-*") if (p / "v2").is_dir())


def preprocessing_id(cohort: str, config: Mapping) -> str:
    """Immutable ID: cohort, policy, distortion-correction status, config hash.

    The config records mask, GM map, script and sample-table checksums, so any
    change in SDC, response estimator, mask or atlas reuse changes the ID.
    """
    blob = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    sdc = str(config.get("sdc_existing", "unknown")).replace(" ", "-")
    return f"{cohort}:{config.get('policy', 'unknown')}:sdc={sdc}:{hashlib.sha256(blob).hexdigest()[:12]}"


# ------------------------------------------------------- canonical content --
def load_canonical_map(crosswalk_tsv: Path, policy: str = "merge") -> dict[int, int]:
    """video_number -> canonical content number.

    ``merge`` also joins the verified rescaled copy (1349, 1363) found by
    decoded-frame signatures; ``hash_only`` uses byte-identical decoded content
    only. Whether Horikawa keeps both 1349 and 1363 is T002 and is not decided
    here; for split safety ``merge`` keeps them in one group either way.
    """
    if policy not in NEAR_DUPLICATE_POLICIES:
        raise ValueError(f"near_duplicate_policy must be one of {NEAR_DUPLICATE_POLICIES}")
    cw = _read_tsv(crosswalk_tsv)
    if policy == "merge":
        return {int(v): int(c) for v, c in zip(cw.video_number, cw.canonical_stimulus_id)}
    first = cw.groupby("decoded_sha256").video_number.transform("min")
    return {int(v): int(c) for v, c in zip(cw.video_number, first)}


def content_key(canonical_number: int) -> str:
    return f"c{int(canonical_number):04d}"


# ----------------------------------------------------------------- manifest --
def _read_participant(cohort: str, d: Path) -> tuple[pd.DataFrame, dict]:
    sub = d.parent.name
    sm = pd.read_csv(d / f"{sub}_samples.tsv", sep="\t")
    status = json.loads((d / "STATUS.json").read_text())
    config = json.loads((d / "preprocessing_config.json").read_text())
    if status.get("state") != "complete":
        raise ValueError(f"{cohort}/{sub}: STATUS is not complete")
    if not np.array_equal(sm["row"].to_numpy(), np.arange(len(sm))):
        raise ValueError(f"{cohort}/{sub}: samples.row is not 0..n-1; refusing to map array rows")
    if len(sm) != int(status["samples"]):
        raise ValueError(f"{cohort}/{sub}: samples.tsv rows != STATUS samples")
    info = {"participant_dir": str(d), "status": status, "config": config,
            "preprocessing_id": preprocessing_id(cohort, config)}
    return sm, info


def reserved_contents(paths: DataPaths, canon: Mapping[int, int]) -> set[str]:
    """Canonical content IDs of MindCaptioning final-test videos (part == test).

    Read from every MindCaptioning participant regardless of which cohorts or
    participants a manifest includes. Fails rather than returning an empty set.
    """
    reserved = set()
    for d in participant_dirs(paths, "mindcaptioning"):
        sm = pd.read_csv(d / f"{d.parent.name}_samples.tsv", sep="\t", usecols=["video_id", "part"])
        reserved |= {content_key(canon[int(v)]) for v in sm.loc[sm.part == "test", "video_id"]}
    if not reserved:
        raise ValueError("No MindCaptioning test content found; cannot mark reserved content")
    return reserved


def build_manifest(paths: DataPaths = DEFAULT_PATHS,
                   cohorts: Sequence[str] = ("mindcaptioning", "horikawa"),
                   near_duplicate_policy: str = "merge",
                   participants: Mapping[str, Sequence[str]] | None = None
                   ) -> tuple[pd.DataFrame, dict]:
    """Full observation manifest. Never trim it before scope validation."""
    canon = load_canonical_map(paths.crosswalk_tsv, near_duplicate_policy)
    frames, info = [], {}
    for cohort in cohorts:
        for d in participant_dirs(paths, cohort):
            sub = d.parent.name
            if participants and cohort in participants and sub not in participants[cohort]:
                continue
            sm, pinfo = _read_participant(cohort, d)
            info[f"{cohort}/{sub}"] = pinfo
            f = pd.DataFrame({
                "cohort": cohort,
                "participant_id": f"{cohort}/{sub}",   # cohort-qualified: MC sub-01 != HK sub-01
                "subject": sub,
                "session": sm["session"].astype(str),
                "run": sm["run"].astype(str),
                "array_row": sm["row"].astype(int),
                "video_id": sm["video_id"].astype(int),
                "source_content_id": sm["content_id"].astype(int),
                "part": sm["part"].astype(str),
                "rep": sm["rep"].astype(int),
                "onset_sec": sm["onset_sec"].astype(float),
                "duration_sec": sm["duration_sec"].astype(float),
                "flag_test_video_in_train_session": (
                    sm["test_video_in_train_session"].astype(bool)
                    if "test_video_in_train_session" in sm else False),
                "flag_later_duplicate": (
                    sm["exclude_duplicate"].astype(bool) if "exclude_duplicate" in sm else False),
                "preprocessing_id": pinfo["preprocessing_id"],
            })
            missing = sorted(set(f.video_id) - canon.keys())
            if missing:
                raise ValueError(f"{cohort}/{sub}: video IDs absent from crosswalk: {missing[:5]}")
            f["canonical_number"] = f.video_id.map(canon).astype(int)
            frames.append(f)
    if not frames:
        raise ValueError("No participant data found")
    m = pd.concat(frames, ignore_index=True)
    m["run_id"] = m.participant_id + "/" + m.session + "/" + m.run
    m["row_id"] = m.run_id + "/r" + m.array_row.astype(str).str.zfill(5)
    m["content_id"] = m.canonical_number.map(content_key)
    # Reserved = MindCaptioning final-test content, propagated to every row of
    # that content in every participant and cohort, also when MindCaptioning
    # rows are not part of this manifest (e.g. a Horikawa-only manifest).
    reserved = reserved_contents(paths, canon)
    m["reserved"] = m.content_id.isin(reserved)
    m["run_group"] = compute_run_groups(m)
    info["near_duplicate_policy"] = near_duplicate_policy
    info["canonical_map"] = canon
    info["n_reserved_contents"] = len(reserved)
    return m, info


def compute_run_groups(m: pd.DataFrame) -> pd.Series:
    """Connected components of the run <-> canonical content bipartite graph.

    Two runs share a group if any content links them, directly or through a
    chain, in any participant or cohort present in ``m``.
    """
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    for run, content in zip("run:" + m.run_id, "content:" + m.content_id):
        union(run, content)
    roots = ("run:" + m.run_id).map(find)
    order = {r: f"rg{i:04d}" for i, r in enumerate(sorted(roots.unique()))}
    return roots.map(order)


# --------------------------------------------------------------- annotation --
def load_labels(paths: DataPaths = DEFAULT_PATHS) -> tuple[pd.DataFrame, list[str]]:
    lab = pd.read_csv(paths.labels_csv)
    names = [ln.strip() for ln in Path(paths.order34).read_text().splitlines() if ln.strip()]
    cols = [c for c in lab.columns if c.startswith("score_")]
    if cols != [f"score_{j}" for j in range(34)] or len(names) != 34:
        raise ValueError("34-D columns or order file do not match score_0..score_33")
    missing = [c for c in AFFECT14 if c not in lab.columns]
    if missing:
        raise ValueError(f"affect14 columns missing: {missing}")
    if lab.stim_num_int.duplicated().any():
        raise ValueError("duplicate annotation rows for one video number")
    return lab, names


def annotation_join(m: pd.DataFrame, lab: pd.DataFrame,
                    canonical: Mapping[int, int]) -> pd.DataFrame:
    """Per canonical content: which annotation rows exist for its members.

    Membership comes from the full crosswalk, not from which videos a cohort
    happened to present, so a content has the same status in every manifest.

    ok        exactly one annotated video number in the content group
    missing   none
    ambiguous more than one, i.e. two different rating rows for one content
    """
    annotated = set(lab.stim_num_int.astype(int))
    members: dict[str, list[int]] = {}
    for v, c in canonical.items():
        members.setdefault(content_key(c), []).append(int(v))
    presented = m.groupby("content_id").video_id.apply(lambda s: sorted(set(int(v) for v in s)))
    rows = []
    for cid, pres in presented.items():
        allv = sorted(members.get(cid, pres))
        ann = [v for v in allv if v in annotated]
        status = "ok" if len(ann) == 1 else ("missing" if not ann else "ambiguous")
        rows.append({"content_id": cid, "member_videos": ",".join(map(str, allv)),
                     "presented_videos": ",".join(map(str, pres)),
                     "annotated_videos": ",".join(map(str, ann)),
                     "annotation_video": ann[0] if len(ann) == 1 else -1,
                     "annotation_status": status})
    return pd.DataFrame(rows)


def attach_annotation(m: pd.DataFrame, join: pd.DataFrame) -> pd.DataFrame:
    out = m.merge(join[["content_id", "annotation_video", "annotation_status"]],
                  on="content_id", how="left", validate="many_to_one")
    if out.annotation_status.isna().any():
        raise ValueError("annotation join left rows without status")
    return out


def exclusion_manifest(m: pd.DataFrame) -> pd.DataFrame:
    """Pilot-only quarantine. Rows stay in the manifest; only targets are masked."""
    q = m[m.annotation_status != "ok"].copy()
    q["reason"] = "annotation_" + q.annotation_status
    q["scope"] = "pilot_only_not_a_study_exclusion"
    return q[["row_id", "content_id", "cohort", "participant_id", "video_id",
              "annotation_status", "reason", "scope"]]


# ----------------------------------------------------------- contract rows --
def to_observations(m: pd.DataFrame):
    from project.code.pilot_contracts import Observation
    return [Observation(r.row_id, r.content_id, r.run_id, r.run_group,
                        r.preprocessing_id, bool(r.reserved))
            for r in m.itertuples(index=False)]


def component_sizes(m: pd.DataFrame) -> dict:
    g = m.groupby("run_group")
    sizes = pd.DataFrame({"n_runs": g.run_id.nunique(), "n_rows": g.size(),
                          "n_contents": g.content_id.nunique(),
                          "n_participants": g.participant_id.nunique(),
                          "has_reserved": g.reserved.any()})
    return {"n_components": int(len(sizes)),
            "n_components_without_reserved": int((~sizes.has_reserved).sum()),
            "largest_component_rows": int(sizes.n_rows.max()),
            "largest_component_runs": int(sizes.n_runs.max()),
            "rows_in_largest_component_fraction": float(sizes.n_rows.max() / len(m)),
            "runs_per_component_counts": {int(k): int(v) for k, v in
                                          sizes.n_runs.value_counts().sort_index().items()}}


# ----------------------------------------------------------- dev subset ----
def select_dev_subset(m: pd.DataFrame, participant: str,
                      roles: Mapping[str, int]) -> dict[str, list[str]]:
    """Deterministic, metadata-only subset of whole run groups for one participant.

    Components are taken in (session, run) order among those with no reserved
    content, then assigned to roles in the given order (for example fit, tune,
    evaluate). No score, target or brain value is read. Raises if fewer than
    three independent components are available. ``participant`` is the
    cohort-qualified ID, for example ``mindcaptioning/sub-01``.
    """
    p = m[m.participant_id == participant]
    if p.empty:
        raise ValueError(f"no rows for {participant}")
    ordered = (p.groupby("run_group").agg(first_session=("session", "min"),
                                          first_run=("run", "min"),
                                          reserved=("reserved", "any"))
               .reset_index())
    ordered = ordered[~ordered.reserved].sort_values(["first_session", "first_run", "run_group"])
    need = sum(roles.values())
    if len(roles) < 3 or need < 3:
        raise ValueError("need at least three independent components across fit/tune/evaluate")
    if len(ordered) < need:
        raise ValueError(f"only {len(ordered)} non-reserved components available, need {need}")
    picked = list(ordered.run_group[:need])
    out, i = {}, 0
    for role, n in roles.items():
        comps = picked[i:i + n]
        i += n
        out[role] = sorted(p.loc[p.run_group.isin(comps), "row_id"])
    return out


# ------------------------------------------------------------ batch contract --
@dataclass(frozen=True)
class StudentBatch:
    """Brain-only input for one participant. Contains no content features."""
    participant_id: str
    preprocessing_id: str
    brain_variant: str
    observation_ids: tuple[str, ...]
    content_ids: tuple[str, ...]
    brain: np.ndarray            # (n, v) float32 block response, participant voxel space
    brain_valid: np.ndarray      # (n, v) bool; False where a voxel was constant in that run
    targets: Mapping[str, np.ndarray] = field(default_factory=dict)       # (n, d) float32, NaN if invalid
    target_masks: Mapping[str, np.ndarray] = field(default_factory=dict)  # (n, d) bool


@dataclass(frozen=True)
class ContentFeatures:
    """Teacher-only content inputs, aligned to observation order."""
    observation_ids: tuple[str, ...]
    video: np.ndarray | None          # (n, dv) float32
    video_valid: np.ndarray | None    # (n,) bool
    video_source: str
    caption: np.ndarray | None        # (n, ds) float32
    caption_valid: np.ndarray | None
    caption_source: str


@dataclass(frozen=True)
class TeacherBatch:
    student: StudentBatch
    content: ContentFeatures

    def __post_init__(self):
        if self.student.observation_ids != self.content.observation_ids:
            raise ValueError("teacher content features are not row-aligned with brain rows")


def _constant_voxel_invalid(d: Path, sub: str) -> dict[tuple[str, str], np.ndarray]:
    """(session, run) -> voxel indices zero-filled because constant in that run."""
    out = {}
    for r in json.loads((d / "qc" / "runs.json").read_text()):
        idx = r.get("constant_voxel_indices") or []
        if idx:
            parts = r["run"].split("_")
            ses = next(x for x in parts if x.startswith("ses-"))
            run = next(x for x in parts if x.startswith("run-"))
            out[(ses, run)] = np.asarray(idx, dtype=np.int64)
    return out


def load_student_batch(m_rows: pd.DataFrame, paths: DataPaths = DEFAULT_PATHS,
                       brain_variant: str = "runz",
                       target_spaces: Sequence[str] = TARGET_SPACES) -> StudentBatch:
    """Load brain rows by their recorded array row, never by position in ``m_rows``."""
    if m_rows.participant_id.nunique() != 1 or m_rows.cohort.nunique() != 1:
        raise ValueError("a StudentBatch holds one participant (voxel spaces differ)")
    if "annotation_status" not in m_rows:
        raise ValueError("attach_annotation() before loading targets")
    cohort, sub = m_rows.cohort.iloc[0], m_rows.subject.iloc[0]
    d = Path(paths.cohort_roots[cohort]) / sub / "v2"
    arr = np.load(d / f"{sub}_{BRAIN_VARIANTS[brain_variant]}.npy", mmap_mode="r")
    rows = m_rows.array_row.to_numpy()
    if rows.max() >= arr.shape[0]:
        raise ValueError("array_row beyond brain array")
    brain = np.asarray(arr[rows], dtype=np.float32)
    valid = np.isfinite(brain)
    invalid = _constant_voxel_invalid(d, sub)
    for i, (ses, run) in enumerate(zip(m_rows.session, m_rows.run)):
        if (ses, run) in invalid:
            valid[i, invalid[(ses, run)]] = False
    lab, _ = load_labels(paths)
    lab = lab.set_index("stim_num_int")
    targets, masks = {}, {}
    ok = (m_rows.annotation_status == "ok").to_numpy()
    ann = m_rows.annotation_video.to_numpy()
    for space in target_spaces:
        cols = [f"score_{j}" for j in range(34)] if space == "cat34" else list(AFFECT14)
        y = np.full((len(m_rows), len(cols)), np.nan, dtype=np.float32)
        if ok.any():
            y[ok] = lab.loc[ann[ok], cols].to_numpy(dtype=np.float32)
        mk = np.isfinite(y)
        targets[space], masks[space] = y, mk
    return StudentBatch(m_rows.participant_id.iloc[0], m_rows.preprocessing_id.iloc[0], brain_variant,
                        tuple(m_rows.row_id), tuple(m_rows.content_id), brain, valid,
                        targets, masks)


def load_content_features(m_rows: pd.DataFrame, paths: DataPaths = DEFAULT_PATHS,
                          canonical: Mapping[int, int] | None = None) -> ContentFeatures:
    """Frozen V-JEPA 2 features by explicit stim_idx -> video number; captions missing.

    Feature rows are identified through the annotation table's (stim_idx,
    stim_num_int) columns. A presented video without its own feature row (for
    example Horikawa 2186) uses a member of the same canonical content group.
    """
    canonical = canonical or load_canonical_map(paths.crosswalk_tsv, "merge")
    lab = pd.read_csv(paths.labels_csv, usecols=["stim_idx", "stim_num_int"])
    feat = np.load(paths.video_features, mmap_mode="r")
    stim_idx = np.load(Path(paths.video_features).parent / "stim_idx.npy")
    row_of_idx = {int(s): r for r, s in enumerate(stim_idx)}
    video_row = {int(v): row_of_idx[int(s)] for s, v in zip(lab.stim_idx, lab.stim_num_int)
                 if int(s) in row_of_idx}
    by_content: dict[int, int] = {}
    for v, r in sorted(video_row.items()):
        by_content.setdefault(canonical[v], r)
    rows = [video_row.get(int(v), by_content.get(canonical[int(v)], -1)) for v in m_rows.video_id]
    rows = np.asarray(rows)
    vvalid = rows >= 0
    video = np.zeros((len(rows), feat.shape[1]), dtype=np.float32)
    if vvalid.any():
        video[vvalid] = np.asarray(feat[rows[vvalid]], dtype=np.float32)
    return ContentFeatures(tuple(m_rows.row_id), video, vvalid,
                           f"{paths.video_features} (provenance of checkpoint/layer/pooling unverified)",
                           None, None,
                           "MISSING: no human-caption sentence embeddings on server; generated captions not substituted")


def voxel_ijk(paths: DataPaths, cohort: str, sub: str) -> np.ndarray:
    """Column -> voxel coordinates (mask order is numpy C order per preprocessing record)."""
    import nibabel as nib
    d = Path(paths.cohort_roots[cohort]) / sub / "v2"
    mask = np.asarray(nib.load(d / f"{sub}_mask.nii.gz").dataobj) > 0
    return np.argwhere(mask)


# --------------------------------------------------------------------- audit --
def _git(*args: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True,
                           text=True, timeout=30)
    except Exception as e:  # pragma: no cover
        return f"unavailable: {e}"
    if r.returncode != 0:  # e.g. a copy outside the repository: never record "" as provenance
        return f"unavailable: {r.stderr.strip()}"
    return r.stdout.strip()


def _dev_subset(m: pd.DataFrame, participant: str, roles: Mapping[str, int], inventory: dict) -> dict:
    from project.code.pilot_contracts import validate_scopes
    subset = select_dev_subset(m, participant, roles)
    obs = to_observations(m)
    counts = validate_scopes(obs, subset["fit"] + subset["tune"], subset["evaluate"])
    counts_tune = validate_scopes(obs, subset["fit"], subset["tune"], subset["evaluate"])
    rows = m[m.row_id.isin(sum(subset.values(), []))]
    v = inventory["participants"][participant]["runz"]["shape"][1]
    return {"participant": participant, "roles": roles,
            "row_counts": {k: len(x) for k, x in subset.items()},
            "target_ok_counts": {k: int((rows[rows.row_id.isin(x)].annotation_status == "ok").sum())
                                 for k, x in subset.items()},
            "components": {k: sorted(m.loc[m.row_id.isin(x), "run_group"].unique())
                           for k, x in subset.items()},
            "runs": {k: sorted(m.loc[m.row_id.isin(x), "run_id"].unique()) for k, x in subset.items()},
            "validate_scopes_fit+tune_vs_evaluate": counts,
            "validate_scopes_fit_vs_tune_forbid_evaluate": counts_tune,
            "estimate": {"voxels": v, "rows": int(len(rows)),
                         "brain_bytes_float32": int(len(rows) * v * 4),
                         "note": "dual ridge on <=500 rows: about a minute of CPU"},
            "row_ids": subset}


def audit(out: Path, paths: DataPaths = DEFAULT_PATHS, hash_arrays: str = "pilot",
          pilot_participant: str = "sub-01",
          roles: Mapping[str, int] | None = None) -> dict:
    roles = dict(roles or {"fit": 8, "tune": 2, "evaluate": 2})
    t0 = time.time()
    out.mkdir(parents=True, exist_ok=False)
    report: dict = {"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "environment": {"python": sys.executable, "version": sys.version.split()[0],
                                    "numpy": np.__version__, "pandas": pd.__version__,
                                    "host": platform.node()},
                    "git": {"branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
                            "commit": _git("rev-parse", "HEAD"),
                            "dirty": _git("status", "--porcelain").splitlines()}}

    # inventory -------------------------------------------------------------
    inv = {"shared": {}, "participants": {}}
    for name in ("labels_csv", "order34", "captions_csv", "crosswalk_tsv"):
        p = Path(getattr(paths, name))
        inv["shared"][name] = {"path": str(p), "bytes": p.stat().st_size, "sha256": sha256_file(p)}
    vf = Path(paths.video_features)
    va = np.load(vf, mmap_mode="r")
    inv["shared"]["video_features"] = {"path": str(vf), "resolved": str(vf.resolve()),
                                       "shape": list(va.shape), "dtype": str(va.dtype),
                                       "sha256": sha256_file(vf.resolve())}
    inv["shared"]["missing_artifacts"] = {
        "human_caption_sentence_embeddings": "absent; caption_ck20.csv text exists (20 per video)",
        "low_level_visual_features": "absent (no luminance/colour/motion-energy features found)",
        "generated_caption_embedding": "stimulus_features/caption_embed.npy is from generated captions; not used",
    }
    for cohort in COHORT_DIRS:
        for d in participant_dirs(paths, cohort):
            sub = d.parent.name
            rec = {}
            for variant, stem in BRAIN_VARIANTS.items():
                p = d / f"{sub}_{stem}.npy"
                a = np.load(p, mmap_mode="r")
                rec[variant] = {"path": str(p), "shape": list(a.shape), "dtype": str(a.dtype),
                                "bytes": p.stat().st_size}
                if hash_arrays == "all" or (hash_arrays == "pilot" and sub == pilot_participant
                                            and variant == "runz"):
                    rec[variant]["sha256"] = sha256_file(p)
            for small in (f"{sub}_samples.tsv", f"{sub}_mask.nii.gz", "preprocessing_config.json",
                          "STATUS.json"):
                rec[small] = {"sha256": sha256_file(d / small)}
            inv["participants"][f"{cohort}/{sub}"] = rec
    report["inventory"] = inv

    # manifests, joins, components ------------------------------------------
    lab, names = load_labels(paths)
    report["codebook"] = {"cat34_order": names,
                          "cat34_order_basis": "cowen34_order.txt; caption-probe check 2026-09; "
                                               "original Cowen codebook not on server",
                          "affect14_columns": list(AFFECT14),
                          "affect14_scale": "1-9 means; polarity unverified (no codebook on server)"}
    manifests = {}
    for label, cohorts in (("mindcaptioning", ["mindcaptioning"]), ("horikawa", ["horikawa"]),
                           ("joint", ["mindcaptioning", "horikawa"])):
        m, minfo = build_manifest(paths, cohorts)
        join = annotation_join(m, lab, minfo["canonical_map"])
        m = attach_annotation(m, join)
        manifests[label] = m
        obs = to_observations(m)
        from project.code.pilot_contracts import _index
        _index(obs)  # raises on inconsistent run groups / duplicate IDs
        report[f"manifest_{label}"] = {
            "n_rows": int(len(m)), "n_participants": int(m.participant_id.nunique()),
            "n_runs": int(m.run_id.nunique()), "n_contents": int(m.content_id.nunique()),
            "n_reserved_rows": int(m.reserved.sum()),
            "n_reserved_contents": int(m.loc[m.reserved, "content_id"].nunique()),
            "annotation_status_rows": m.annotation_status.value_counts().to_dict(),
            "annotation_status_contents": join.annotation_status.value_counts().to_dict(),
            "ambiguous_contents": join.loc[join.annotation_status == "ambiguous",
                                           ["content_id", "annotated_videos"]].values.tolist(),
            "missing_contents": join.loc[join.annotation_status == "missing",
                                         "content_id"].tolist(),
            "flag_test_video_in_train_session_rows": int(m.flag_test_video_in_train_session.sum()),
            "flag_later_duplicate_rows": int(m.flag_later_duplicate.sum()),
            "contents_seen_by_all_participants": int(
                (m.groupby("content_id").participant_id.nunique()
                 == m.participant_id.nunique()).sum()),
            "near_duplicate_merges": sorted(
                int(v) for v in m.loc[m.source_content_id != m.canonical_number, "video_id"].unique()),
            "preprocessing_ids": sorted(m.preprocessing_id.unique()),
            "components": component_sizes(m),
        }
        m.to_csv(out / f"manifest_{label}.tsv.gz", sep="\t", index=False)
        exclusion_manifest(m).to_csv(out / f"pilot_exclusions_{label}.tsv", sep="\t", index=False)

    # development subsets (one per cohort, from that cohort's own manifest) ----
    report["dev_subsets"] = {}
    for cohort in COHORT_DIRS:
        participant = f"{cohort}/{pilot_participant}"
        try:
            report["dev_subsets"][participant] = _dev_subset(
                manifests[cohort], participant, roles, report["inventory"])
        except (ValueError, KeyError) as e:
            report["dev_subsets"][participant] = {"error": str(e)}
    report["seconds"] = round(time.time() - t0, 1)
    (out / "audit.json").write_text(json.dumps(report, indent=2, default=str, ensure_ascii=False))
    return report


def main(argv: Iterable[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit")
    a.add_argument("--out", required=True, type=Path)
    a.add_argument("--hash-arrays", choices=("none", "pilot", "all"), default="pilot")
    a.add_argument("--pilot-participant", default="sub-01")
    args = ap.parse_args(list(argv) if argv is not None else None)
    if args.cmd == "audit":
        rep = audit(args.out, hash_arrays=args.hash_arrays,
                    pilot_participant=args.pilot_participant)
        print(json.dumps({k: rep[k] for k in rep if k.startswith("manifest_")},
                         indent=1, default=str)[:6000])
        print(json.dumps({p: {k: v for k, v in d.items() if k != "row_ids"}
                          for p, d in rep["dev_subsets"].items()}, indent=1, default=str))


if __name__ == "__main__":
    main()
