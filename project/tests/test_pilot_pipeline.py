"""Synthetic behavioral checks for T005; no real arrays, downloads or jobs."""
from dataclasses import replace
import copy
import inspect
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np
import torch

from project.code.pilot_contracts import Observation
from project.code.pilot.baseline import checked_arrays, run_linear, LinearBenchmark
from project.code.pilot.analysis import commonality_scores, retrieval, linear_cka, perturb_tokens, fit_content_probe
from project.code.pilot.models import BrainStudent, JointTeacher, ModelConfig, supervised, student_objective
from project.code.pilot.scopes import nested_plan, oof_cache_key, require_cache, validate_bridge
from project.code.pilot.training import (TensorData, FitConfig, TargetScale, run_nested,
    fit_model, predict, save_fit, load_fit, state_hash, paired_content_permutation)
from project.code.pilot.artifacts import file_hash, save_linear_run
from project.scripts.run_pilot import verify_codebook


def fixture(target="cat34"):
    rng = np.random.default_rng(18)
    n, d = 20, 34 if target == "cat34" else 14
    rows = [Observation(f"o{i}", f"c{i}", f"mc/p1/s1/r{i // 4}", f"g{i // 4}", "synthetic-sdc-none-hash") for i in range(n)]
    x = rng.normal(size=(n, 12)).astype("float32")
    y = x @ rng.normal(size=(12, d)).astype("float32")
    if target == "cat34":
        y = 1 / (1 + np.exp(-y))
    ids = tuple(r.row_id for r in rows)
    batch = SimpleNamespace(observation_ids=ids, content_ids=tuple(r.content_id for r in rows),
                            preprocessing_id=rows[0].preprocessing_id, participant_id="mc/p1", brain_variant="synthetic",
                            brain=x, brain_valid=np.ones_like(x, dtype=bool), targets={target:y},
                            target_masks={target:np.ones_like(y, dtype=bool)})
    split = dict(fit=list(ids[:8]), tune=list(ids[8:12]), evaluate=list(ids[12:16]))
    data = TensorData(ids, batch.content_ids, x.reshape(n, 3, 4), np.ones((n, 3, 4), dtype=bool),
                      np.zeros(n, dtype=int), y, np.ones_like(y, dtype=bool),
                      rng.normal(size=(n, 6)).astype("float32"), rng.normal(size=(n, 5)).astype("float32"),
                      np.ones((n, 2), dtype=bool))
    cfg = ModelConfig(target, 3, 4, width=8, heads=2)
    provenance = dict(code_commit="synthetic", input_manifest_hash="manifest", split_hash="split",
                      target=target, target_transform_hash="identity", feature_hash="features",
                      config_hash="config", seed=0)
    return rows, batch, split, data, cfg, provenance


class LinearTests(unittest.TestCase):
    def test_shuffle_rows_keeps_id_join_predictions(self):
        rows, b, s, *_ = fixture()
        a = run_linear(rows, b, s, "cat34")
        p = np.random.default_rng(2).permutation(len(b.brain))
        c = copy.deepcopy(b)
        c.observation_ids = tuple(b.observation_ids[i] for i in p)
        c.content_ids = tuple(b.content_ids[i] for i in p)
        c.brain, c.brain_valid = b.brain[p], b.brain_valid[p]
        c.targets = {k:v[p] for k,v in b.targets.items()}
        c.target_masks = {k:v[p] for k,v in b.target_masks.items()}
        z = run_linear(rows, c, s, "cat34")
        np.testing.assert_allclose(a["predictions"], z["predictions"])

    def test_final_label_poison_does_not_change_fit_or_selection(self):
        rows, b, s, *_ = fixture()
        first = run_linear(rows, b, s, "cat34")
        b.targets["cat34"][12:] = 1 - b.targets["cat34"][12:]
        second = run_linear(rows, b, s, "cat34")
        self.assertEqual(first["selected_alpha"], second["selected_alpha"])
        np.testing.assert_array_equal(first["model"].weights, second["model"].weights)

    def test_scaler_uses_training_only_and_reload(self):
        rows, b, s, *_ = fixture("affect14")
        result = run_linear(rows, b, s, "affect14")
        np.testing.assert_allclose(result["model"].scaler.mean, b.brain[:12].mean(0), atol=1e-7)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "linear.npz"
            result["model"].save(path)
            reloaded = LinearBenchmark.load(path)
            np.testing.assert_array_equal(result["predictions"], reloaded.predict(b.brain[12:16], b.brain_valid[12:16]))
            with self.assertRaises(FileExistsError):
                result["model"].save(path)

    def test_missing_target_values_are_not_zero_labels(self):
        rows, b, s, *_ = fixture()
        b.target_masks["cat34"][0, 0] = False
        b.targets["cat34"][0, 0] = np.nan
        a = run_linear(rows, b, s, "cat34")
        b.targets["cat34"][0, 0] = 999999
        z = run_linear(rows, b, s, "cat34")
        np.testing.assert_array_equal(a["predictions"], z["predictions"])

    def test_missing_brain_mask_and_labels_fail(self):
        rows, b, s, *_ = fixture()
        b.brain_valid = np.ones((1, 1), dtype=bool)
        with self.assertRaises(ValueError):
            checked_arrays(b, "cat34")
        b.brain_valid = np.ones_like(b.brain, dtype=bool)
        b.target_masks["cat34"][:, 0] = False
        with self.assertRaisesRegex(ValueError, "no training labels"):
            run_linear(rows, b, s, "cat34")

    def test_reserved_unselected_repeat_blocks_training(self):
        rows, b, s, *_ = fixture()
        rows.append(replace(rows[0], row_id="unselected-test", reserved=True))
        with self.assertRaisesRegex(ValueError, "Reserved"):
            run_linear(rows, b, s, "cat34")

    def test_content_and_preprocessing_mismatch_rejected(self):
        rows, b, s, *_ = fixture()
        b.content_ids = ("wrong",) + b.content_ids[1:]
        with self.assertRaisesRegex(ValueError, "content identity"):
            run_linear(rows, b, s, "cat34")
        b.content_ids = tuple(r.content_id for r in rows)
        b.preprocessing_id = "new-sdc"
        with self.assertRaisesRegex(ValueError, "preprocessing"):
            run_linear(rows, b, s, "cat34")


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)

    def test_all_content_masked_residual_has_finite_gradients(self):
        *_, data, cfg, _ = fixture()
        model = JointTeacher(cfg)
        b = torch.tensor(data.brain, requires_grad=True)
        out = model(b, torch.tensor(data.brain_valid), torch.tensor(data.participants),
                    torch.full((20, 6), float("nan")), torch.full((20, 5), float("nan")),
                    torch.zeros((20, 2), dtype=torch.bool))
        self.assertTrue(torch.isfinite(out["logits"]).all())
        out["logits"].sum().backward()
        self.assertTrue(torch.isfinite(b.grad).all())
        self.assertGreater(float(b.grad.abs().sum()), 0)

    def test_teacher_guidance_stop_gradient_and_nan_mask(self):
        for target, d in (("cat34", 34), ("affect14", 14)):
            with self.subTest(target=target):
                s = torch.zeros(2, d, requires_grad=True)
                g = torch.full((2, d), .4, requires_grad=True)
                y, mask = torch.full((2, d), .5), torch.ones(2, d, dtype=torch.bool)
                mask[0, 0], y[0, 0] = False, float("nan")
                terms = student_objective(s, y, mask, target, g, torch.ones_like(mask), .5)
                terms["total"].backward()
                self.assertIsNone(g.grad)
                self.assertTrue(torch.isfinite(s.grad).all())
                self.assertGreater(float(terms["distillation"].detach()), 0)

    def test_student_inference_needs_no_content_or_label_files(self):
        *_, data, cfg, _ = fixture()
        model = BrainStudent(cfg)
        self.assertEqual(list(inspect.signature(model.forward).parameters), ["brain", "brain_valid", "participant"])
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(list(Path(empty).iterdir()), [])
            out = model(torch.tensor(data.brain), torch.tensor(data.brain_valid), torch.tensor(data.participants))
        self.assertEqual(out["logits"].shape, (20, 34))

    def test_missing_brain_or_target_rejected(self):
        *_, data, cfg, _ = fixture()
        with self.assertRaisesRegex(ValueError, "All brain"):
            BrainStudent(cfg)(torch.tensor(data.brain), torch.zeros_like(torch.tensor(data.brain_valid)), torch.tensor(data.participants))
        with self.assertRaisesRegex(ValueError, "No valid"):
            supervised(torch.zeros(2,34), torch.zeros(2,34), torch.zeros(2,34,dtype=torch.bool), "cat34")

    def test_checkpoint_reload_matches_both_target_paths(self):
        for target in ("cat34", "affect14"):
            rows, _, split, data, cfg, _ = fixture(target)
            fit = fit_model(rows, data, cfg, FitConfig(), split["fit"], split["tune"], split["evaluate"])
            pred, _ = predict(fit, data, split["tune"])
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "student"
                save_fit(fit, path)
                reloaded = load_fit(path)
                np.testing.assert_array_equal(pred, predict(reloaded, data, split["tune"])[0])
                self.assertEqual(state_hash(fit.model), state_hash(reloaded.model))

    def test_continuous_oof_scalers_roundtrip_original_units(self):
        a = TargetScale.fit(np.array([[1.,10.],[3.,14.]]), np.ones((2,2),bool), "affect14")
        b = TargetScale.fit(np.array([[4.,0.],[8.,2.]]), np.ones((2,2),bool), "affect14")
        raw = np.array([[2.,12.]])
        np.testing.assert_allclose(b.transform(a.inverse(a.transform(raw))), b.transform(raw))
        self.assertFalse(np.allclose(a.transform(raw), b.transform(raw)))

    def test_nested_oof_exclusion_and_final_label_poisoning(self):
        for target in ("cat34", "affect14"):
            rows, _, split, data, cfg, prov = fixture(target)
            a = run_nested(rows, data, cfg, FitConfig(steps=2), split, prov, weights=(.2,.5))
            data.targets[12:] = 1 - data.targets[12:]
            b = run_nested(rows, data, cfg, FitConfig(steps=2), split, prov, weights=(.2,.5))
            self.assertEqual(state_hash(a["guided"].model), state_hash(b["guided"].model))
            self.assertEqual(a["selected_weight"], b["selected_weight"])
            for phase in ("inner_oof", "final_oof"):
                for entry in a[phase]:
                    used = set(entry["scope"]["fit"])
                    self.assertFalse(used & set(entry["scope"]["evaluate"]))
                    self.assertFalse(used & set(split["evaluate"]))
                    if phase == "inner_oof":
                        self.assertFalse(used & set(split["tune"]))
            np.testing.assert_array_equal(a["predictions"], b["predictions"])

    def test_shuffle_content_together_only_within_fit(self):
        _, _, split, data, _, _ = fixture()
        used = np.arange(8)
        p = paired_content_permutation(data, used, 1)
        self.assertEqual(set(p), set(used))
        self.assertTrue(np.all(p != used))
        # Actual shuffled OOF path must execute with the same boundaries.
        rows, _, split, data, cfg, prov = fixture()
        out = run_nested(rows, data, cfg, FitConfig(steps=1), split, prov, shuffled=True)
        self.assertTrue(np.isfinite(out["predictions"]).all())


class ScopeAndAnalysisTests(unittest.TestCase):
    def test_artifacts_are_row_aligned_reloadable_and_never_overwritten(self):
        rows, batch, split, *_ = fixture()
        result = run_linear(rows,batch,split,"cat34")
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/"input.txt"
            source.write_text("synthetic source")
            out = save_linear_run(tmp,"one-run",rows,batch,split,"cat34",result,{"seed":0},
                                  {str(source):file_hash(source)}, {"commit":"test","source_hashes":{}},.01)
            metadata = json.loads((out/"metadata.json").read_text())
            self.assertEqual(metadata["scope_roles"],split)
            self.assertEqual(len((out/"predictions.tsv").read_text().splitlines()), 1+4*34)
            model = LinearBenchmark.load(out/"linear_model.npz")
            np.testing.assert_array_equal(model.predict(batch.brain[12:16],batch.brain_valid[12:16]),result["predictions"])
            with self.assertRaises(FileExistsError):
                save_linear_run(tmp,"one-run",rows,batch,split,"cat34",result,{"seed":0},
                                {str(source):file_hash(source)},{"commit":"test","source_hashes":{}},.01)

    def test_codebook_execution_gate_checks_target_order_and_source_hash(self):
        audit = {"codebook":{"cat34_order":[f"c{i}" for i in range(34)]}}
        with self.assertRaisesRegex(ValueError,"verification"):
            verify_codebook(None,"cat34",audit)
        with tempfile.TemporaryDirectory() as tmp:
            source, contract = Path(tmp)/"codebook.txt", Path(tmp)/"contract.json"
            source.write_text("synthetic evidence")
            record=dict(target="cat34",columns=audit["codebook"]["cat34_order"],reference_path=str(source),
                        reference_sha256=file_hash(source),reviewed_by="synthetic test",scale_description="proportions")
            contract.write_text(json.dumps(record))
            self.assertEqual(len(verify_codebook(contract,"cat34",audit)),2)
            source.write_text("changed")
            with self.assertRaisesRegex(ValueError,"checksum"):
                verify_codebook(contract,"cat34",audit)

    def test_oof_cache_target_preprocessing_and_weights_separate(self):
        rows, _, s, _, _, prov = fixture()
        scope = nested_plan(rows, s)["inner"][0]
        prov.update(teacher_checkpoint_hash="weights", transform_hash="transform")
        key = oof_cache_key(rows, scope, prov)
        for p in (dict(prov,target="affect14"), dict(prov,teacher_checkpoint_hash="different")):
            with self.assertRaises(ValueError):
                require_cache(key, oof_cache_key(rows, scope, p))
        with self.assertRaises(ValueError):
            require_cache(key, oof_cache_key([replace(r, preprocessing_id="new-sdc") for r in rows], scope, prov))
        del prov["transform_hash"]
        with self.assertRaises(ValueError):
            oof_cache_key(rows, scope, prov)

    def test_too_few_oof_groups_fail(self):
        rows, _, s, *_ = fixture()
        s["fit"] = s["fit"][:4]
        with self.assertRaisesRegex(ValueError, "two independent"):
            nested_plan(rows, s)

    def test_common_denominator_and_signed_negative_component(self):
        y = np.array([[1.,2.],[3.,4.]])
        pred = dict(G=np.zeros_like(y), GC=y*.5, GE=y*.5, GCE=y*0)
        out = commonality_scores(y, np.ones_like(y,bool), np.zeros(2), pred)
        self.assertEqual(out["denominator"], 30.)
        self.assertLess(out["content_given_affect"], 0.)
        self.assertAlmostEqual(out["content_given_affect"], -.75)
        pred = dict(G=np.zeros_like(y), GC=np.zeros_like(y), GE=np.zeros_like(y), GCE=y)
        self.assertLess(commonality_scores(y,np.ones_like(y,bool),np.zeros(2),pred)["shared_predictive_component"], 0)
        with self.assertRaises(ValueError):
            commonality_scores(y,np.ones_like(y,bool),y,pred)

    def test_retrieval_deduplicates_content_and_conservative_ties(self):
        ref = np.array([[1.,0.],[0.,1.],[1.,0.]])
        result = retrieval(ref,ref,["a","b","a"])
        self.assertEqual(result["candidate_count"],2)
        self.assertEqual(result["chance"],.5)
        self.assertEqual(result["accuracy"],1.)
        tied = np.ones((2,2))
        self.assertEqual(retrieval(tied,tied,["a","b"])["accuracy"],0.)

    def test_probe_cka_alignment_and_matched_perturbation(self):
        rows, b, split, data, _, _ = fixture()
        probe, predicted = fit_content_probe(rows,b.observation_ids,b.brain,data.video,split["fit"],split["evaluate"])
        self.assertEqual(predicted.shape,(4,6))
        np.testing.assert_allclose(probe.scaler.mean,b.brain[:8].mean(0),atol=1e-7)
        self.assertAlmostEqual(linear_cka(b.brain,b.brain,b.observation_ids,b.observation_ids,"one-fit"),1.,places=6)
        with self.assertRaises(ValueError):
            linear_cka(b.brain,b.brain,b.observation_ids,b.observation_ids[::-1],"one-fit")
        p = perturb_tokens(data.brain,data.brain_valid,[0],[1])
        np.testing.assert_array_equal(p["selected"]["brain"][:,1:],data.brain[:,1:])
        np.testing.assert_array_equal(p["null"]["brain"][:,0],data.brain[:,0])
        data.brain_valid[:,0,0] = False
        with self.assertRaises(ValueError):
            perturb_tokens(data.brain,data.brain_valid,[0],[1])

    def test_bridge_forbids_common_test_content_in_discovery(self):
        rows, _, s, *_ = fixture()
        validate_bridge(rows,s["fit"],s["fit"],s["evaluate"])
        with self.assertRaises(ValueError):
            validate_bridge(rows,s["fit"]+s["evaluate"],s["tune"],s["evaluate"])


if __name__ == "__main__":
    unittest.main()
