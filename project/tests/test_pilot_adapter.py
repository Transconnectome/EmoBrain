"""Synthetic tests for the pilot data adapter (BOARD T004).

No real data are read. Each test builds a tiny fake cohort tree and checks one
failure mode the pilot handoff names: identity by array order, missing or
ambiguous annotation, all-masked content, reserved-content propagation,
connected run groups, constant-voxel validity, brain-only student inputs and
preprocessing identity.

Run from the repository root:
    python -m unittest project.tests.test_pilot_adapter -v
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from project.code.pilot_contracts import validate_scopes
from project.data import pilot_adapter as pa

N_VOX = 6


def _write_participant(root: Path, cohort_dir: str, sub: str, rows: list[dict],
                       constant_voxels: dict | None = None, config_extra: dict | None = None):
    d = root / cohort_dir / sub / {"MC": "v2", "HK": "v3"}[cohort_dir]  # pa.RESPONSE_VERSIONS
    (d / "qc").mkdir(parents=True)
    sm = pd.DataFrame(rows)
    sm.insert(0, "row", np.arange(len(sm)))
    sm.to_csv(d / f"{sub}_samples.tsv", sep="\t", index=False)
    rng = np.random.default_rng(len(rows))
    brain = rng.normal(size=(len(rows), N_VOX)).astype(np.float32)
    brain[:, 0] = sm["row"].to_numpy()          # column 0 encodes the array row
    np.save(d / f"{sub}_blocks_common36_runz.npy", brain)
    np.save(d / f"{sub}_blocks_common36.npy", brain * 2)
    (d / "STATUS.json").write_text(json.dumps({"state": "complete", "samples": len(rows)}))
    (d / f"{sub}_mask.nii.gz").write_bytes(f"synthetic mask {cohort_dir} {sub}".encode())  # hashed, not parsed
    cfg = {"policy": "test-policy", "sdc_existing": "none", "script_sha256": "abc"}
    cfg.update(config_extra or {})
    (d / "preprocessing_config.json").write_text(json.dumps(cfg))
    runs = []
    for (ses, run), g in sm.groupby(["session", "run"]):
        idx = (constant_voxels or {}).get((ses, run), [])
        runs.append({"run": f"{sub}_{ses}_task-x_{run}", "constant_voxels_after_trim": len(idx),
                     "constant_voxel_indices": idx})
    (d / "qc" / "runs.json").write_text(json.dumps(runs))
    return d


def _row(video, session, run, part="train", rep=1, content=None, **flags):
    r = {"video_id": video, "onset_sec": 0.0, "duration_sec": 10.0, "session": session,
         "run": run, "part": part, "rep": rep, "content_id": content or video}
    r.update(flags)
    return r


class AdapterFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        # Crosswalk: 1 and 9 are identical content; 3 and 7 are a near duplicate.
        cw = pd.DataFrame({"video_number": range(1, 11)})
        cw["canonical_stimulus_id"] = cw.video_number.replace({9: 1, 7: 3})
        cw["decoded_sha256"] = cw.video_number.replace({9: 1}).map(lambda v: f"h{v}")
        cw.to_csv(self.tmp / "crosswalk.tsv", sep="\t", index=False)
        # Annotation rows for 1..8; video 7 has its own row (ambiguous with 3
        # under the near-duplicate merge); video 10 has no row (missing).
        lab = pd.DataFrame({"stim_idx": range(8), "stim_num_int": range(1, 9)})
        for j in range(34):
            lab[f"score_{j}"] = (lab.stim_num_int * (j + 1) % 7) / 10
        for c in pa.AFFECT14:
            lab[c] = 1.0 + lab.stim_num_int
        lab.to_csv(self.tmp / "labels.csv", index=False)
        (self.tmp / "order.txt").write_text("\n".join(f"emo{j}" for j in range(34)))
        fdir = self.tmp / "features"
        fdir.mkdir()
        np.save(fdir / "video.npy", np.arange(8 * 3, dtype=np.float32).reshape(8, 3))
        np.save(fdir / "stim_idx.npy", np.arange(8, dtype=np.int32))
        self.paths = pa.DataPaths(
            cohort_roots={"mindcaptioning": self.tmp / "MC", "horikawa": self.tmp / "HK"},
            labels_csv=self.tmp / "labels.csv", order34=self.tmp / "order.txt",
            captions_csv=self.tmp / "labels.csv", video_features=fdir / "video.npy",
            crosswalk_tsv=self.tmp / "crosswalk.tsv",
            response_versions={"mindcaptioning": "v2", "horikawa": "v3"})  # base layout; QC layout in QcLayoutTests
        # MindCaptioning: two participants, identical runs; video 5 is final test.
        for sub in ("sub-01", "sub-02"):
            _write_participant(self.tmp, "MC", sub, [
                _row(1, "ses-train01", "run-01", test_video_in_train_session=False),
                _row(2, "ses-train01", "run-01", test_video_in_train_session=False),
                _row(3, "ses-train01", "run-02", test_video_in_train_session=False),
                _row(4, "ses-train01", "run-03", test_video_in_train_session=False),
                _row(6, "ses-train01", "run-04", test_video_in_train_session=False),
                _row(8, "ses-train01", "run-05", test_video_in_train_session=False),
                _row(5, "ses-train01", "run-06", test_video_in_train_session=True),
                _row(5, "ses-test01", "run-01", part="test", rep=1, test_video_in_train_session=False),
                _row(5, "ses-test01", "run-01", part="test", rep=2, test_video_in_train_session=False),
            ], constant_voxels={("ses-train01", "run-02"): [4]} if sub == "sub-02" else None)
        # Horikawa: 9 repeats 1 in another run (links run-01 and run-04); 7 is
        # a near duplicate of 3; 5 is MindCaptioning test content; 10 unannotated.
        _write_participant(self.tmp, "HK", "sub-01", [
            _row(1, "ses-01", "run-01", exclude_duplicate=False),
            _row(7, "ses-01", "run-02", exclude_duplicate=False),
            _row(5, "ses-01", "run-03", exclude_duplicate=False),
            _row(9, "ses-01", "run-04", exclude_duplicate=True),
            _row(10, "ses-01", "run-05", exclude_duplicate=False),
            _row(2, "ses-01", "run-06", exclude_duplicate=False),
        ], config_extra={"sdc_existing": "none"})

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def manifest(self, cohorts=("mindcaptioning", "horikawa"), policy="merge"):
        m, info = pa.build_manifest(self.paths, cohorts, near_duplicate_policy=policy)
        lab, _ = pa.load_labels(self.paths)
        join = pa.annotation_join(m, lab, info["canonical_map"])
        return pa.attach_annotation(m, join), info


class ManifestTests(AdapterFixture):
    def test_participant_ids_are_cohort_qualified(self):
        m, _ = self.manifest()
        self.assertEqual(m.participant_id.nunique(), 3)   # MC sub-01, MC sub-02, HK sub-01
        self.assertIn("mindcaptioning/sub-01", set(m.participant_id))
        self.assertIn("horikawa/sub-01", set(m.participant_id))
        self.assertTrue(all(r.startswith(p + "/") for r, p in zip(m.run_id, m.participant_id)))

    def test_run_names_repeat_across_sessions_so_run_id_is_qualified(self):
        m, _ = self.manifest(("mindcaptioning",))
        p1 = m[m.participant_id == "mindcaptioning/sub-01"]
        self.assertEqual(p1[p1.run == "run-01"].session.nunique(), 2)
        self.assertEqual(p1.groupby("run_id").session.nunique().max(), 1)

    def test_rows_identified_by_row_column_not_file_order(self):
        d = self.paths.cohort_roots["mindcaptioning"] / "sub-01" / "v2"
        sm = pd.read_csv(d / "sub-01_samples.tsv", sep="\t")
        sm.sample(frac=1.0, random_state=3).to_csv(d / "sub-01_samples.tsv", sep="\t", index=False)
        with self.assertRaisesRegex(ValueError, "samples.row is not 0..n-1"):
            self.manifest(("mindcaptioning",))

    def test_brain_rows_follow_array_row(self):
        m, _ = self.manifest(("mindcaptioning",))
        rows = m[(m.participant_id == "mindcaptioning/sub-01")].iloc[::-1]          # reversed request order
        b = pa.load_student_batch(rows, self.paths, target_spaces=("cat34",))
        np.testing.assert_array_equal(b.brain[:, 0], rows.array_row.to_numpy())
        self.assertEqual(b.observation_ids, tuple(rows.row_id))

    def test_reserved_content_propagates_across_participants_and_cohorts(self):
        m, _ = self.manifest()
        reserved = m[m.reserved]
        self.assertEqual(set(reserved.content_id), {pa.content_key(5)})
        self.assertIn("horikawa", set(reserved.cohort))
        self.assertTrue(reserved[reserved.part == "train"].flag_test_video_in_train_session.any())

    def test_reserved_marked_in_horikawa_only_manifest(self):
        m, info = self.manifest(("horikawa",))
        self.assertEqual(set(m.cohort), {"horikawa"})
        self.assertEqual(set(m.loc[m.reserved, "content_id"]), {pa.content_key(5)})
        self.assertEqual(info["n_reserved_contents"], 1)

    def test_run_groups_link_runs_through_shared_content(self):
        m, _ = self.manifest(("horikawa",))
        g = m.set_index("run")["run_group"]
        self.assertEqual(g["run-01"], g["run-04"])      # 1 and 9 are one content
        self.assertNotEqual(g["run-01"], g["run-05"])
        mc, _ = self.manifest(("mindcaptioning",))
        same_run = mc[(mc.session == "ses-train01") & (mc.run == "run-01")
                      ].groupby("participant_id").run_group.agg(set)
        self.assertTrue(all(len(x) == 1 for x in same_run))
        same_run = same_run.map(lambda x: next(iter(x)))
        self.assertEqual(same_run.nunique(), 1)         # same content across participants

    def test_near_duplicate_policy_changes_grouping(self):
        merged, _ = self.manifest(("horikawa",), policy="merge")
        hashed, _ = self.manifest(("horikawa",), policy="hash_only")
        v7 = lambda m: m.loc[m.video_id == 7, "content_id"].item()
        self.assertEqual(v7(merged), pa.content_key(3))
        self.assertEqual(v7(hashed), pa.content_key(7))

    def test_manifest_satisfies_contract_index_and_blocks_leaks(self):
        m, _ = self.manifest(("mindcaptioning",))
        obs = pa.to_observations(m)
        p1 = m[m.participant_id == "mindcaptioning/sub-01"]
        train01 = (m.session == "ses-train01") & (m.run == "run-01")
        fit = list(p1[train01[p1.index]].row_id)
        other_participant_same_content = list(m[(m.participant_id == "mindcaptioning/sub-02") & train01].row_id)
        with self.assertRaisesRegex(ValueError, "leakage"):
            validate_scopes(obs, fit, other_participant_same_content)
        with self.assertRaisesRegex(ValueError, "Reserved content"):
            validate_scopes(obs, fit, list(p1[p1.video_id == 5].row_id))

    def test_preprocessing_id_changes_with_config(self):
        m, _ = self.manifest(("horikawa",))
        before = m.preprocessing_id.iloc[0]
        d = self.paths.cohort_roots["horikawa"] / "sub-01" / "v3"
        cfg = json.loads((d / "preprocessing_config.json").read_text())
        cfg["sdc_existing"] = "syn-sdc-candidate"
        (d / "preprocessing_config.json").write_text(json.dumps(cfg))
        after = self.manifest(("horikawa",))[0].preprocessing_id.iloc[0]
        self.assertNotEqual(before, after)
        self.assertIn("sdc=syn-sdc-candidate", after)

    def test_sdc_field_overrides_legacy_sdc_existing(self):
        # Horikawa v3: legacy sdc_existing still "none", SyN-SDC described in sdc.
        d = self.paths.cohort_roots["horikawa"] / "sub-01" / "v3"
        cfg = json.loads((d / "preprocessing_config.json").read_text())
        cfg["sdc"] = "fMRIPrep fieldmap-less SyN SDC; phase-encoding axis A-P assumed"
        (d / "preprocessing_config.json").write_text(json.dumps(cfg))
        pid = self.manifest(("horikawa",))[0].preprocessing_id.iloc[0]
        self.assertIn("sdc=fieldmap-less-syn", pid)

    def test_response_versions_select_cohort_folders(self):
        self.assertEqual(pa.response_dir(self.paths, "horikawa", "sub-01").name, "v3")
        self.assertEqual(pa.response_dir(self.paths, "mindcaptioning", "sub-01").name, "v2")


class AnnotationTests(AdapterFixture):
    def test_status_uses_full_group_membership(self):
        hk, _ = self.manifest(("horikawa",))
        mc, _ = self.manifest(("mindcaptioning",))
        status = lambda m, v: m.loc[m.video_id == v, "annotation_status"].iloc[0]
        self.assertEqual(status(hk, 7), "ambiguous")     # 3 and 7 both have rows
        self.assertEqual(status(mc, 3), "ambiguous")     # same content, same status
        self.assertEqual(status(hk, 9), "ok")            # 9 has no row; 1 does
        self.assertEqual(status(hk, 10), "missing")

    def test_ambiguous_and_missing_are_masked_not_averaged(self):
        m, _ = self.manifest(("horikawa",))
        b = pa.load_student_batch(m, self.paths)
        bad = ~(m.annotation_status == "ok").to_numpy()
        self.assertTrue(bad.any())
        for space in ("cat34", "affect14"):
            self.assertFalse(b.target_masks[space][bad].any())
            self.assertTrue(np.isnan(b.targets[space][bad]).all())
            self.assertTrue(b.target_masks[space][~bad].all())

    def test_duplicate_without_own_row_uses_group_row(self):
        m, _ = self.manifest(("horikawa",))
        b = pa.load_student_batch(m, self.paths, target_spaces=("affect14",))
        i9 = list(m.video_id).index(9)
        i1 = list(m.video_id).index(1)
        np.testing.assert_array_equal(b.targets["affect14"][i9], b.targets["affect14"][i1])

    def test_all_masked_content_stays_in_manifest(self):
        m, _ = self.manifest(("horikawa",))
        ex = pa.exclusion_manifest(m)
        self.assertIn(pa.content_key(10), set(ex.content_id))
        self.assertTrue((ex.scope == "pilot_only_not_a_study_exclusion").all())
        self.assertIn(pa.content_key(10), set(m.content_id))


class BatchTests(AdapterFixture):
    def test_student_batch_has_no_content_fields(self):
        names = set(pa.StudentBatch.__dataclass_fields__)
        self.assertFalse(names & {"video", "caption", "content", "video_valid", "caption_valid"})

    def test_student_batch_builds_without_feature_files(self):
        Path(self.paths.video_features).unlink()
        m, _ = self.manifest(("mindcaptioning",))
        b = pa.load_student_batch(m[m.participant_id == "mindcaptioning/sub-01"], self.paths)
        self.assertEqual(b.brain.shape[1], N_VOX)

    def test_student_batch_rejects_mixed_participants(self):
        m, _ = self.manifest(("mindcaptioning",))
        with self.assertRaisesRegex(ValueError, "one participant"):
            pa.load_student_batch(m, self.paths)

    def test_constant_voxel_marked_invalid_only_in_its_run(self):
        m, _ = self.manifest(("mindcaptioning",))
        rows = m[m.participant_id == "mindcaptioning/sub-02"]
        b = pa.load_student_batch(rows, self.paths)
        in_run = (rows.run == "run-02").to_numpy()
        self.assertFalse(b.brain_valid[in_run, 4].any())
        self.assertTrue(b.brain_valid[~in_run, 4].all())

    def test_teacher_features_aligned_and_resolved_through_content(self):
        m, info = self.manifest(("horikawa",))
        s = pa.load_student_batch(m, self.paths)
        f = pa.load_content_features(m, self.paths, info["canonical_map"])
        t = pa.TeacherBatch(s, f)
        i9 = list(m.video_id).index(9)
        i1 = list(m.video_id).index(1)
        np.testing.assert_array_equal(t.content.video[i9], t.content.video[i1])
        self.assertFalse(f.video_valid[list(m.video_id).index(10)])
        self.assertIsNone(f.caption)
        self.assertIn("MISSING", f.caption_source)

    def test_teacher_batch_rejects_misaligned_features(self):
        m, info = self.manifest(("horikawa",))
        s = pa.load_student_batch(m, self.paths)
        f = pa.load_content_features(m.iloc[::-1], self.paths, info["canonical_map"])
        with self.assertRaisesRegex(ValueError, "row-aligned"):
            pa.TeacherBatch(s, f)


class SubsetTests(AdapterFixture):
    def test_subset_is_metadata_only_and_validates(self):
        m, _ = self.manifest(("mindcaptioning",))
        roles = {"fit": 2, "tune": 1, "evaluate": 1}
        a = pa.select_dev_subset(m, "mindcaptioning/sub-01", roles)
        b = pa.select_dev_subset(m.sample(frac=1.0, random_state=1), "mindcaptioning/sub-01", roles)
        self.assertEqual(a, b)
        obs = pa.to_observations(m)
        validate_scopes(obs, a["fit"] + a["tune"], a["evaluate"])
        validate_scopes(obs, a["fit"], a["tune"], a["evaluate"])
        chosen = m[m.row_id.isin(sum(a.values(), []))]
        self.assertFalse(chosen.reserved.any())

    def test_subset_refuses_too_few_components(self):
        m, _ = self.manifest(("mindcaptioning",))
        with self.assertRaisesRegex(ValueError, "non-reserved, QC-included components"):
            pa.select_dev_subset(m, "mindcaptioning/sub-01", {"fit": 4, "tune": 1, "evaluate": 1})
        with self.assertRaisesRegex(ValueError, "three independent"):
            pa.select_dev_subset(m, "mindcaptioning/sub-01", {"fit": 1, "evaluate": 1})

    def test_test_cohort_refused_for_development(self):
        # 2026-10-20 (D28): Horikawa trains and develops, MindCaptioning is the later validation cohort.
        self.assertEqual(pa.require_development_cohort("horikawa/sub-01"), "horikawa")
        with self.assertRaisesRegex(ValueError, "not 'development'"):
            pa.require_development_cohort("mindcaptioning/sub-01")
        with self.assertRaisesRegex(ValueError, "not 'development'"):
            pa.require_development_cohort("sub-01")  # cohort-unqualified IDs are refused too


class InputDigestTests(AdapterFixture):
    """Issue #7: inputs that change feature rows or brain validity must change the digest."""

    def audit_inventory(self):
        return pa.audit(self.tmp / f"audit_{len(list(self.tmp.glob('audit_*')))}", self.paths,
                        hash_arrays="all")["inventory"]

    def rows(self, cohort, participant):
        m, info = self.manifest((cohort,))
        return m[m.participant_id == participant], info

    def test_inventory_schema_records_stim_idx_and_qc(self):
        inv = self.audit_inventory()
        self.assertEqual(inv["schema"], pa.INVENTORY_SCHEMA)
        self.assertIn("sha256", inv["shared"]["stim_idx"])
        self.assertIn("shared/stim_idx", inv["shared"]["content_dependencies"]["files"])
        rec = inv["participants"]["mindcaptioning/sub-02"]
        self.assertIn("sha256", rec["qc/runs.json"])
        self.assertIn("mindcaptioning/sub-02/qc/runs.json", rec["dependencies"]["runz"]["files"])

    def test_unchanged_inputs_pass_and_match_batch_digests(self):
        inv = self.audit_inventory()
        rows, info = self.rows("horikawa", "horikawa/sub-01")
        digest = pa.check_inventory(inv, self.paths, "horikawa/sub-01")
        self.assertEqual(digest, pa.load_student_batch(rows, self.paths).input_digest)
        self.assertEqual(digest, inv["participants"]["horikawa/sub-01"]["dependencies"]["runz"]["digest"])
        pa.check_inventory(inv, self.paths, "horikawa/sub-01", content=True)
        self.assertEqual(pa.load_content_features(rows, self.paths, info["canonical_map"]).input_digest,
                         inv["shared"]["content_dependencies"]["digest"])

    def test_stim_idx_change_changes_digest_and_is_refused(self):
        inv = self.audit_inventory()
        rows, info = self.rows("horikawa", "horikawa/sub-01")
        before = pa.load_content_features(rows, self.paths, info["canonical_map"])
        si = Path(self.paths.video_features).parent / "stim_idx.npy"
        np.save(si, np.load(si)[::-1].copy())          # same bytes count, different row order
        after = pa.load_content_features(rows, self.paths, info["canonical_map"])
        self.assertFalse(np.array_equal(before.video, after.video))
        self.assertNotEqual(before.input_digest, after.input_digest)
        pa.check_inventory(inv, self.paths, "horikawa/sub-01")  # brain-only path does not read it
        with self.assertRaisesRegex(ValueError, r"shared/stim_idx"):
            pa.check_inventory(inv, self.paths, "horikawa/sub-01", content=True)
        self.assertNotEqual(self.audit_inventory()["shared"]["stim_idx"]["sha256"], inv["shared"]["stim_idx"]["sha256"])

    def test_constant_voxel_change_changes_validity_digest_and_is_refused(self):
        inv = self.audit_inventory()
        rows, _ = self.rows("mindcaptioning", "mindcaptioning/sub-02")
        before = pa.load_student_batch(rows, self.paths)
        q = self.tmp / "MC" / "sub-02" / "v2" / "qc" / "runs.json"
        runs = json.loads(q.read_text())
        runs[0]["constant_voxel_indices"] = [1, 2]
        q.write_text(json.dumps(runs))
        after = pa.load_student_batch(rows, self.paths)
        self.assertFalse(np.array_equal(before.brain_valid, after.brain_valid))
        np.testing.assert_array_equal(before.brain, after.brain)  # only validity changed
        self.assertNotEqual(before.input_digest, after.input_digest)
        with self.assertRaisesRegex(ValueError, r"mindcaptioning/sub-02/qc/runs.json"):
            pa.check_inventory(inv, self.paths, "mindcaptioning/sub-02")
        pa.check_inventory(inv, self.paths, "horikawa/sub-01")  # other participants unaffected

    def test_legacy_or_unhashed_inventory_is_refused(self):
        inv = self.audit_inventory()
        legacy = {k: v for k, v in inv.items() if k != "schema"}
        with self.assertRaisesRegex(ValueError, "legacy inventory"):
            pa.check_inventory(legacy, self.paths, "horikawa/sub-01")
        pilot = pa.audit(self.tmp / "audit_pilot", self.paths, hash_arrays="pilot")["inventory"]
        with self.assertRaisesRegex(ValueError, "no dependency record"):
            pa.check_inventory(pilot, self.paths, "mindcaptioning/sub-02")  # array not hashed


class QcExclusionTests(AdapterFixture):
    """Lab-server QC may drop participants or runs; rows stay flagged in the manifest."""

    def with_exclusions(self, participants=(), runs=()):
        import dataclasses
        f = self.tmp / "qc_exclusions.json"
        entry = lambda cohort, sub, **kw: dict(cohort=cohort, participant=sub, reason="motion", source="qc test",
                                              decided="2026-10-21", **kw)
        f.write_text(json.dumps({"schema": 1, "status": "test",
                                 "participants": [entry(c, s) for c, s in participants],
                                 "runs": [entry(c, s, run=r) for c, s, r in runs]}))
        self.paths = dataclasses.replace(self.paths, qc_exclusions=f)
        return f

    def test_excluded_participant_flagged_and_blocked(self):
        self.with_exclusions(participants=[("mindcaptioning", "sub-02")])
        m, info = self.manifest(("mindcaptioning",))
        sub2 = m.participant_id == "mindcaptioning/sub-02"
        self.assertTrue(m.loc[sub2, "qc_excluded"].all())
        self.assertFalse(m.loc[~sub2, "qc_excluded"].any())
        self.assertEqual(info["qc_exclusions"]["participants"], ["mindcaptioning/sub-02"])
        with self.assertRaisesRegex(ValueError, "excluded by QC"):
            pa.select_dev_subset(m, "mindcaptioning/sub-02", {"fit": 1, "tune": 1, "evaluate": 1})
        with self.assertRaisesRegex(ValueError, "excluded by QC"):
            pa.load_student_batch(m[sub2], self.paths)
        ex = pa.exclusion_manifest(m)
        self.assertEqual(set(ex.loc[ex.scope == "study_exclusion_lab_server_qc", "row_id"]), set(m.loc[sub2, "row_id"]))
        validate_scopes(pa.to_observations(m), list(m.loc[~sub2 & ~m.reserved, "row_id"])[:2],
                        list(m.loc[~sub2 & ~m.reserved, "row_id"])[-1:])  # full manifest still checks leakage

    def test_excluded_run_drops_its_component(self):
        self.with_exclusions(runs=[("mindcaptioning", "sub-01", "ses-train01/run-02")])
        m, _ = self.manifest(("mindcaptioning",))
        bad = m.run_id == "mindcaptioning/sub-01/ses-train01/run-02"
        self.assertTrue(m.loc[bad, "qc_excluded"].all() and not m.loc[~bad, "qc_excluded"].any())
        picked = pa.select_dev_subset(m, "mindcaptioning/sub-01", {"fit": 2, "tune": 1, "evaluate": 1})
        used = set(sum(picked.values(), []))
        self.assertFalse(used & set(m.loc[bad, "row_id"]))
        self.assertEqual(m.loc[m.row_id.isin(used), "run_group"].nunique(), 4)

    def test_list_change_changes_digest_and_is_refused(self):
        f = self.with_exclusions()
        inv = pa.audit(self.tmp / "audit_qc", self.paths, hash_arrays="all")["inventory"]
        self.assertEqual(inv["shared"]["qc_exclusions"]["participants"], {})
        m, _ = self.manifest(("horikawa",))
        before = pa.load_student_batch(m, self.paths).input_digest
        pa.check_inventory(inv, self.paths, "horikawa/sub-01")
        self.with_exclusions(runs=[("horikawa", "sub-01", "ses-01/run-05")])
        self.assertEqual(f, self.paths.qc_exclusions)
        m, _ = self.manifest(("horikawa",))
        after = pa.load_student_batch(m[~m.qc_excluded], self.paths).input_digest
        self.assertNotEqual(before, after)
        with self.assertRaisesRegex(ValueError, "shared/qc_exclusions"):
            pa.check_inventory(inv, self.paths, "horikawa/sub-01")

    def test_malformed_or_missing_list_is_refused(self):
        import dataclasses
        f = self.with_exclusions()
        for bad in ({"schema": 2, "status": "x"},
                    {"schema": 1, "status": "x", "participants": [{"cohort": "horikawa", "participant": "sub-01"}]},
                    {"schema": 1, "status": "x", "participants": [dict(cohort="other", participant="sub-01", reason="r",
                                                                       source="s", decided="d")]},
                    {"schema": 1, "status": "x", "runs": [dict(cohort="horikawa", participant="sub-01", run="run-01",
                                                               reason="r", source="s", decided="d")]},
                    {"schema": 1, "status": "x", "participants": [dict(cohort="horikawa", participant="sub-01",
                                                                       reason="r", source="s", decided="d")] * 2}):
            f.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                pa.load_qc_exclusions(self.paths)
        self.paths = dataclasses.replace(self.paths, qc_exclusions=self.tmp / "absent.json")
        with self.assertRaises(FileNotFoundError):
            pa.load_qc_exclusions(self.paths)

    def test_repository_list_is_valid_and_currently_empty(self):
        import dataclasses
        qc = pa.load_qc_exclusions(dataclasses.replace(self.paths, qc_exclusions=pa.DEFAULT_PATHS.qc_exclusions))
        self.assertEqual((qc["participants"], qc["runs"]), ({}, {}))
        self.assertTrue(qc["status"].startswith("pending"))


class QcLayoutTests(AdapterFixture):
    """Lab-server QC folders (v3_qc): usable rows only, recomputed z, QC mask; record in base folder."""

    def write_qc(self, cohort_dir="HK", sub="sub-01", version="v3_qc", drop_rows=(4,), drop_voxels=(5,),
                 subject_qc="pass"):
        base = self.tmp / cohort_dir / sub / {"HK": "v3", "MC": "v2"}[cohort_dir]
        d = base.parent / version
        d.mkdir()
        sm = pd.read_csv(base / f"{sub}_samples.tsv", sep="\t")
        usable = sm[~sm.row.isin(drop_rows)].reset_index(drop=True)
        usable.insert(0, "qc_row", np.arange(len(usable)))
        usable["usable_flag"] = True
        usable.to_csv(d / f"{sub}_samples_qc_usable.tsv", sep="\t", index=False)
        keep = [v for v in range(N_VOX) if v not in drop_voxels]
        brain = np.random.default_rng(7).normal(size=(len(usable), len(keep))).astype(np.float32)
        brain[:, 0] = usable.qc_row.to_numpy()    # column 0 encodes the QC array row
        np.save(d / f"{sub}_blocks_common36_qc_runz.npy", brain)
        np.save(d / f"{sub}_blocks_common36_qc.npy", brain * 2)
        (d / f"{sub}_mask_qc.nii.gz").write_bytes(b"synthetic qc mask")
        (d / "SUCCESS.json").write_text(json.dumps({"state": "complete"}))
        (d / "QC_SUMMARY.json").write_text(json.dumps(dict(
            subject_qc=subject_qc, subject_exclusion_reason="" if subject_qc == "pass" else "mean FD",
            input_version=base.name, thresholds={"BLOCK_FD": 0.9}, code_sha256="c0de" * 16,
            voxels_qc=len(keep), output_shape=[len(usable), len(keep)])))
        import dataclasses
        self.paths = dataclasses.replace(self.paths, response_versions={"mindcaptioning": "v2", "horikawa": version})
        return d, usable

    def test_rows_keep_original_ids_and_load_by_qc_row(self):
        d, usable = self.write_qc()
        m, info = self.manifest(("horikawa",))
        self.assertEqual(len(m), len(usable))
        self.assertEqual(list(m.array_row), list(usable.qc_row))
        self.assertEqual(list(m.source_row), list(usable.row))
        self.assertTrue(all(r.endswith(f"/r{src:05d}") for r, src in zip(m.row_id, m.source_row)))
        self.assertIn("+qc-c0dec0de", m.preprocessing_id.iloc[0])
        b = pa.load_student_batch(m, self.paths)
        np.testing.assert_array_equal(b.brain[:, 0], m.array_row.to_numpy())
        self.assertEqual(b.brain.shape[1], N_VOX - 1)
        self.assertTrue(b.brain_valid.all())          # QC mask already dropped constant voxels

    def test_reserved_from_full_pre_qc_table_and_dependencies(self):
        self.write_qc()
        m, info = self.manifest(("horikawa",))
        self.assertEqual(set(m.loc[m.reserved, "content_id"]), {pa.content_key(5)})
        deps = pa.student_dependencies(self.paths, "horikawa", "sub-01")
        self.assertIn("horikawa/sub-01/QC_SUMMARY.json", deps)
        self.assertEqual(deps["horikawa/sub-01/preprocessing_config.json"].parent.name, "v3")
        self.assertEqual(deps["mindcaptioning/sub-01/reserved_source_samples.tsv"].parent.name, "v2")
        self.assertNotIn("horikawa/sub-01/qc/runs.json", deps)

    def test_failed_or_inconsistent_qc_is_refused(self):
        d, usable = self.write_qc(subject_qc="fail")
        with self.assertRaisesRegex(ValueError, "failed lab-server QC"):
            self.manifest(("horikawa",))
        q = json.loads((d / "QC_SUMMARY.json").read_text())
        q.update(subject_qc="pass", output_shape=[len(usable) + 1, N_VOX - 1])
        (d / "QC_SUMMARY.json").write_text(json.dumps(q))
        with self.assertRaisesRegex(ValueError, "QC output rows"):
            self.manifest(("horikawa",))

    def test_qc_audit_inventory_and_check(self):
        self.write_qc()
        inv = pa.audit(self.tmp / "audit_qclayout", self.paths, hash_arrays="all")["inventory"]
        rec = inv["participants"]["horikawa/sub-01"]
        self.assertEqual(rec["version"], "v3_qc")
        self.assertIn("QC_SUMMARY.json", rec)
        self.assertIn("base/preprocessing_config.json", rec)
        pa.check_inventory(inv, self.paths, "horikawa/sub-01")
        q = self.tmp / "HK" / "sub-01" / "v3_qc" / "QC_SUMMARY.json"
        q.write_text(q.read_text().replace('"BLOCK_FD": 0.9', '"BLOCK_FD": 0.5'))
        with self.assertRaisesRegex(ValueError, "QC_SUMMARY"):
            pa.check_inventory(inv, self.paths, "horikawa/sub-01")


if __name__ == "__main__":
    unittest.main()
