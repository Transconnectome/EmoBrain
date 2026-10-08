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
    d = root / cohort_dir / sub / "v2"
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
            crosswalk_tsv=self.tmp / "crosswalk.tsv")
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
        d = self.paths.cohort_roots["horikawa"] / "sub-01" / "v2"
        cfg = json.loads((d / "preprocessing_config.json").read_text())
        cfg["sdc_existing"] = "syn-sdc-candidate"
        (d / "preprocessing_config.json").write_text(json.dumps(cfg))
        after = self.manifest(("horikawa",))[0].preprocessing_id.iloc[0]
        self.assertNotEqual(before, after)
        self.assertIn("sdc=syn-sdc-candidate", after)


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
        with self.assertRaisesRegex(ValueError, "non-reserved components"):
            pa.select_dev_subset(m, "mindcaptioning/sub-01", {"fit": 4, "tune": 1, "evaluate": 1})
        with self.assertRaisesRegex(ValueError, "three independent"):
            pa.select_dev_subset(m, "mindcaptioning/sub-01", {"fit": 1, "evaluate": 1})


if __name__ == "__main__":
    unittest.main()
