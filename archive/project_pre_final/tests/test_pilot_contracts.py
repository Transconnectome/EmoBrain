import unittest
from dataclasses import replace

from project.code.pilot_contracts import Observation, artifact_key, validate_scopes


class PilotContractsTests(unittest.TestCase):
    def setUp(self):
        self.rows = [Observation(str(i), f"c{i}", f"mc/p1/s1/r{i}", f"g{i}", "v2")
                     for i in range(4)]
        self.provenance = dict(code_commit="abc", input_manifest_hash="m",
                               split_hash="s", target="cat34",
                               target_transform_hash="identity", feature_hash="f",
                               config_hash="cfg", seed=0)
        self.scopes = dict(fit=["0", "1"], evaluate=["2"], forbidden=["3"])

    def key(self, rows=None, scopes=None):
        return artifact_key(self.rows if rows is None else rows,
                            self.scopes if scopes is None else scopes, self.provenance)

    def test_valid(self):
        self.assertEqual(validate_scopes(self.rows, ["0", "1"], ["2"], ["3"]),
                         dict(fit=2, evaluate=1, forbidden=1))

    def test_canonical_repeat_across_participants(self):
        rows = self.rows + [Observation("copy", "c0", "mc/p2/s1/r0", "g0", "v2")]
        with self.assertRaisesRegex(ValueError, "content_id leakage"):
            validate_scopes(rows, ["0"], ["copy"])

    def test_connected_run_leak(self):
        rows = [replace(r, run_group="g0") if r.row_id == "2" else r for r in self.rows]
        with self.assertRaisesRegex(ValueError, "run_group leakage"):
            validate_scopes(rows, ["0"], ["2"])

    def test_reserved_content_in_unselected_repeat(self):
        rows = self.rows + [Observation("test-repeat", "c0", "mc/p1/test/r1",
                                       "g0", "v2", True)]
        with self.assertRaisesRegex(ValueError, "Reserved content"):
            validate_scopes(rows, ["0"], ["2"])

    def test_reserved_evaluation(self):
        rows = [replace(r, reserved=True) if r.row_id == "2" else r for r in self.rows]
        with self.assertRaisesRegex(ValueError, "Reserved content"):
            validate_scopes(rows, ["0"], ["2"])

    def test_forbidden_outer_or_inner_dependency(self):
        with self.assertRaisesRegex(ValueError, "leakage"):
            validate_scopes(self.rows, ["0", "3"], ["2"], ["3"])

    def test_bad_manifest(self):
        cases = [[], self.rows + [self.rows[0]],
                 self.rows + [replace(self.rows[0], row_id="x", run_group="wrong")],
                 [replace(self.rows[0], reserved="false")],
                 [replace(self.rows[0], preprocessing_id="")]]
        for rows in cases:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                validate_scopes(rows, ["0"], ["2"])

    def test_unknown_or_empty_scope(self):
        for fit, evaluate in [(["unknown"], ["2"]), ([], ["2"]), (["0"], [])]:
            with self.subTest(fit=fit), self.assertRaises(ValueError):
                validate_scopes(self.rows, fit, evaluate)

    def test_cache_order_invariant(self):
        self.assertEqual(self.key(), self.key(list(reversed(self.rows)),
                         dict(fit=["1", "0"], evaluate=["2"], forbidden=["3"])))

    def test_cache_changes_with_preprocessing_roles_and_target(self):
        old = self.key()
        self.assertNotEqual(old, self.key([replace(r, preprocessing_id="sdc-new")
                                          for r in self.rows]))
        self.assertNotEqual(old, self.key(scopes=dict(fit=["2"], evaluate=["0", "1"],
                                                     forbidden=["3"])))
        self.provenance["target"] = "affect14"
        self.assertNotEqual(old, self.key())

    def test_incomplete_cache_provenance(self):
        del self.provenance["input_manifest_hash"]
        with self.assertRaises(ValueError):
            self.key()


if __name__ == "__main__":
    unittest.main()
