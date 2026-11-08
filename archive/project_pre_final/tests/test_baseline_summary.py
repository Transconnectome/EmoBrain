"""Synthetic checks for project/baseline/brain_decoding/summarize.py (W04, issue #8).

No real data: each test writes a small run folder (metadata.json, predictions.tsv,
codebook contract) in a temporary directory.

Run: python -B -m unittest project.tests.test_baseline_summary -v
"""
import csv
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from project.baseline.brain_decoding import summarize as sm

N_OBS, N_DIM = 4, 34
HEADER = ["observation_id", "content_id", "participant_id", "target_dimension",
          "valid", "target", "prediction", "training_mean_prediction"]


def cells(target=lambda i, j: 0.1 * i + 0.01 * j, pred=lambda i, j: 0.1 * i + 0.01 * j + 0.05 * ((i + j) % 3 - 1),
          base=lambda i, j: 0.2, valid=lambda i, j: True):
    return [[f"o{i}", f"c{i}", "horikawa/sub-01", j, valid(i, j),
             target(i, j) if valid(i, j) else "", pred(i, j), base(i, j)]
            for i in range(N_OBS) for j in range(N_DIM)]


class RunFixture(unittest.TestCase):
    def setUp(self):
        self._resamples, sm.N_RESAMPLES = sm.N_RESAMPLES, 50  # speed; references are not under test
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.run = self.root / "runs" / "prep" / "exp"
        self.run.mkdir(parents=True)
        (self.root / "codebook").mkdir()
        self.codebook = self.root / "codebook" / "cat34.json"
        self.codebook.write_text(json.dumps({"target": "cat34", "columns": [f"dim{j}" for j in range(N_DIM)]}))
        import pandas as pd
        (self.root / "audits" / "audit_x").mkdir(parents=True)
        self.manifest = self.root / "audits" / "audit_x" / "manifest_horikawa.tsv.gz"
        pd.DataFrame({"row_id": [f"o{i}" for i in range(N_OBS)] + ["other"],
                      "participant_id": ["horikawa/sub-01"] * (N_OBS + 1),
                      "content_id": [f"c{i}" for i in range(N_OBS)] + ["c9"]}).to_csv(self.manifest, sep="\t", index=False)

    def tearDown(self):
        sm.N_RESAMPLES = self._resamples
        self._tmp.cleanup()

    def write(self, rows, meta_overrides=None, mse=None, mse0=None):
        with (self.run / "predictions.tsv").open("w") as fh:
            w = csv.writer(fh, delimiter="\t")
            w.writerow(HEADER)
            w.writerows(rows)
        valid = [r for r in rows if r[4] is True]
        if mse is None:
            mse = float(np.mean([(r[6] - r[5]) ** 2 for r in valid]))
        if mse0 is None:
            mse0 = float(np.mean([(r[7] - r[5]) ** 2 for r in valid]))
        meta = dict(target="cat34", participant="horikawa/sub-01", preprocessing_id="synthetic",
                    scope_roles=dict(fit=["f0", "f1"], tune=["t0"], evaluate=[f"o{i}" for i in range(N_OBS)]),
                    config=dict(alphas=[1.0, 10.0]), alpha=10.0, tuning_mse=[0.2, 0.1],
                    mse=mse, training_mean_mse=mse0, seconds=0.1, code=dict(commit="test", dirty=""),
                    sources={str(self.codebook): hashlib.sha256(self.codebook.read_bytes()).hexdigest(),
                             str(self.manifest): hashlib.sha256(self.manifest.read_bytes()).hexdigest()})
        meta.update(meta_overrides or {})
        (self.run / "metadata.json").write_text(json.dumps(meta))
        return meta


class ConsistentRunTests(RunFixture):
    def test_metrics_recomputed_and_levels_agree(self):
        rows = cells()
        self.write(rows)
        out = sm.summarize(self.run)
        valid = [r for r in rows if r[4]]
        self.assertAlmostEqual(out["mse"], np.mean([(r[6] - r[5]) ** 2 for r in valid]), places=12)
        weighted = sum(d["n"] * d["mse"] for d in out["per_dimension"]) / sum(d["n"] for d in out["per_dimension"])
        self.assertAlmostEqual(out["mse"], weighted, places=12)
        self.assertEqual([d["dimension"] for d in out["per_dimension"]], [f"dim{j}" for j in range(N_DIM)])
        json.loads((self.run / "summary.json").read_text())  # strict JSON, no NaN

    def test_out_dir_leaves_existing_summary_untouched(self):
        self.write(cells())
        (self.run / "summary.json").write_text("original")
        sm.summarize(self.run, out_dir=self.root / "verify")
        self.assertEqual((self.run / "summary.json").read_text(), "original")
        self.assertTrue((self.root / "verify" / "summary.json").is_file())

    def test_masked_cells_are_excluded_not_zero(self):
        rows = cells(valid=lambda i, j: not (i == 0 and j < 5))
        self.write(rows)
        out = sm.summarize(self.run)
        self.assertEqual(out["n_valid_cells"], N_OBS * N_DIM - 5)
        self.assertEqual(out["per_dimension"][0]["n"], N_OBS - 1)

    def test_zero_denominator_reports_undefined_reduction(self):
        same = lambda i, j: 0.5  # training-mean prediction equals every target
        rows = cells(target=same, base=same)
        self.write(rows)
        out = sm.summarize(self.run)
        self.assertIsNone(out["mse_reduction"])
        self.assertEqual(len(out["undefined_reduction_dimensions"]), N_DIM)
        self.assertEqual(len(out["undefined_r_dimensions"]), N_DIM)  # constant targets: r undefined
        self.assertIn("null", (self.run / "summary.json").read_text())


class RejectionTests(RunFixture):
    def assertRejects(self, pattern):
        with self.assertRaisesRegex(sm.SummaryError, pattern):
            sm.summarize(self.run)
        self.assertFalse((self.run / "summary.json").exists())

    def test_audit_counterexample_metadata_mse_0_tsv_mse_100(self):
        # Issue #8: target i, prediction i + 10, training mean 0; metadata claims mse 0.
        rows = cells(target=lambda i, j: float(i), pred=lambda i, j: float(i + 10), base=lambda i, j: 0.0)
        self.write(rows, mse=0.0, mse0=1.0)
        self.assertRejects("mse: metadata 0.0 disagrees")

    def test_training_mean_mse_mismatch(self):
        rows = cells()
        self.write(rows, mse0=123.0)
        self.assertRejects("training_mean_mse")

    def test_duplicate_cell(self):
        rows = cells()
        self.write(rows + [rows[3]])
        self.assertRejects("Duplicate cell")

    def test_missing_cell(self):
        self.write(cells()[:-1])
        self.assertRejects("missing cells")

    def test_out_of_range_and_non_integer_dimension(self):
        rows = cells()
        rows[0][3] = N_DIM
        self.write(rows)
        self.assertRejects("outside 0")
        rows[0][3] = "1.5"
        self.write(rows)
        self.assertRejects("Non-integer")

    def test_non_finite_values(self):
        for column, value in ((5, math.nan), (6, math.inf), (7, -math.inf)):
            rows = cells()
            rows[2][column] = value
            self.write(rows, mse=0.1, mse0=0.1)
            self.assertRejects("Non-finite")

    def test_invalid_cell_must_be_empty_and_flag_strict(self):
        rows = cells()
        rows[1][4], rows[1][5] = False, 0.3
        self.write(rows, mse=0.1, mse0=0.1)
        self.assertRejects("Invalid cell")
        rows = cells()
        rows[1][4] = "yes"
        self.write(rows, mse=0.1, mse0=0.1)
        self.assertRejects("Invalid cell")

    def test_observation_scope_mismatch(self):
        rows = cells()
        self.write(rows, meta_overrides=dict(scope_roles=dict(fit=["f0"], tune=["t0"], evaluate=["o0", "o1", "o2"])))
        self.assertRejects("outside the evaluate scope")
        self.write(rows, meta_overrides=dict(scope_roles=dict(fit=["f0"], tune=["t0"],
                                                              evaluate=[f"o{i}" for i in range(N_OBS + 1)])))
        self.assertRejects("missing cells")

    def test_codebook_changed_or_not_pinned(self):
        self.write(cells())
        self.codebook.write_text(json.dumps({"target": "cat34", "columns": [f"renamed{j}" for j in range(N_DIM)]}))
        self.assertRejects("changed since the run")
        self.write(cells(), meta_overrides=dict(sources={}))
        self.assertRejects("pins 0 codebook")

    def test_alpha_outside_declared_grid(self):
        self.write(cells(), meta_overrides=dict(alpha=3.0))
        self.assertRejects("declared grid")

    def test_alpha_not_tuning_minimum(self):
        # Codex review (2026-10-21): alpha 1.0 is in the grid [1, 10] but tuning MSE [0.2, 0.1] selects 10.
        self.write(cells(), meta_overrides=dict(alpha=1.0))
        self.assertRejects("not the tuning-MSE minimum")

    def test_participant_and_content_ids_checked_against_pinned_manifest(self):
        # Codex review (2026-10-21): every participant and content ID replaced.
        rows = cells()
        for r in rows:
            r[2], r[1] = "mindcaptioning/sub-99", "incorrect-content"
        self.write(rows)
        self.assertRejects("not the run participant")
        rows = cells()
        rows[5][1] = "c3"  # one cell of observation o0 carries another content
        self.write(rows)
        self.assertRejects("disagrees with the pinned manifest")

    def test_manifest_pin_missing_changed_or_moved(self):
        self.write(cells(), meta_overrides=dict(sources={str(self.codebook): hashlib.sha256(self.codebook.read_bytes()).hexdigest()}))
        self.assertRejects("pins 0 sources matching manifest")
        self.write(cells())
        moved = self.root / "audits" / "superseded" / "audit_x"
        moved.mkdir(parents=True)
        self.manifest.rename(moved / self.manifest.name)
        sm.summarize(self.run)  # an audit moved to superseded/ is followed
        (self.run / "summary.json").unlink()
        (moved / self.manifest.name).write_bytes(b"changed")
        self.assertRejects("changed since the run")


if __name__ == "__main__":
    unittest.main()
