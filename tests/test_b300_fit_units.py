"""CPU-only operational tests; synthetic files do not prove GPU behavior."""
import importlib.util
import json
import pathlib
import tempfile
import unittest

P = pathlib.Path(__file__).resolve().parents[1] / 'scripts/b300/fit_units.py'

def load():
    s = importlib.util.spec_from_file_location('fit_units', P)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

class Contracts(unittest.TestCase):
    def setUp(self):
        self.f = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def manifest(self):
        return {'schema': 'emobrain-fit-units-v1', 'scope': 'bounded_measurement',
                'units': [{'id':'a','dependencies':[],'condition':'brain_only','candidate':{},'seed':0,'artifact_rel':'a','required':['model.pt','done.json','history.tsv']}],
                'groups': [{'id':'g','units':['a']}], 'expected_units':['a'], 'restart_policy':'restart_from_seed'}
    def test_valid_dag(self):
        self.f.validate_manifest(self.manifest())
    def test_duplicate_unit(self):
        m=self.manifest();m['units']*=2
        with self.assertRaises(ValueError):self.f.validate_manifest(m)
    def test_missing_dependency(self):
        m=self.manifest();m['units'][0]['dependencies']=['x']
        with self.assertRaises(ValueError):self.f.validate_manifest(m)
    def test_cycle(self):
        m=self.manifest();m['units'][0]['dependencies']=['a']
        with self.assertRaises(ValueError):self.f.validate_manifest(m)
    def test_declared_universe_mismatch(self):
        m=self.manifest();m['expected_units']+=['b']
        with self.assertRaises(ValueError):self.f.validate_manifest(m)
    def test_path_escape(self):
        m=self.manifest();m['units'][0]['artifact_rel']='../a'
        with self.assertRaises(ValueError):self.f.validate_manifest(m)
    def test_atomic_immutable(self):
        p=self.root/'r.json';self.f.publish_json(p,{'x':1})
        with self.assertRaises(FileExistsError):self.f.publish_json(p,{'x':2})
        self.assertEqual(json.loads(p.read_text()),{'x':1})
    def test_corrupt_artifact_rejected(self):
        d=self.root/'a';d.mkdir();(d/'model.pt').write_bytes(b'a')
        hashes=self.f.hash_tree(d);(d/'model.pt').write_bytes(b'b')
        with self.assertRaises(ValueError):self.f.verify_hashes(d,hashes)
    def test_missing_artifact_rejected(self):
        with self.assertRaises(ValueError):self.f.verify_hashes(self.root,{'a':'0'*64})
    def test_incomplete_selection_rejected(self):
        with self.assertRaises(ValueError):self.f.verify_group(self.manifest(),'g',self.root)

class ReceiptImports(unittest.TestCase):
    def test_exact_dependency_import_and_corruption_detection(self):
        f=load()
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)/'source';target=pathlib.Path(d)/'comparison'
            a=dict(id='a',dependencies=[],condition='brain_only',candidate={'d':4},seed=0,artifact_rel='a',required=['model.pt','done.json','history.tsv'])
            b=dict(a,id='b',dependencies=['a'],artifact_rel='b')
            m=dict(schema=f.SCHEMA,scope='synthetic_cpu_fixture',restart_policy='restart_from_seed',units=[a,b],expected_units=['a','b'],groups=[dict(id='g',units=['a','b'])])
            folder=root/'science/a';folder.mkdir(parents=True)
            (folder/'model.pt').write_bytes(b'synthetic fixture bytes')
            (folder/'history.tsv').write_text('epoch\n1\n')
            (folder/'done.json').write_text(json.dumps(dict(run_key='fixture',candidate=a['candidate'],seed=0)))
            attempt=root/'attempts/a/original';attempt.mkdir(parents=True);(attempt/'telemetry.json').write_text('{}')
            receipt=dict(status='complete',manifest_sha256=f.identity(m),unit=a,run_key='fixture',artifacts=f.hash_tree(folder),dependencies={},attempt='attempts/a/original',telemetry_sha256=f.digest(attempt/'telemetry.json'),slurm_job_id='synthetic-not-a-job')
            f.publish_json(f.receipt_path(root,'a'),receipt)
            f.clone_dependencies(m,root,target,['b'])
            self.assertEqual(f.digest(f.receipt_path(root,'a')),f.digest(f.receipt_path(target,'a')))
            self.assertFalse(f.receipt_path(target,'b').exists())
            self.assertEqual(f.read_json(target/'imported_dependencies.json')['new_fit_count'],0)
            (target/'science/a/model.pt').write_bytes(b'corrupted')
            with self.assertRaises(ValueError):f.verify_unit(m,'a',target)
    def test_writer_lock_rejects_second_writer(self):
        f=load()
        with tempfile.TemporaryDirectory() as d:
            with f.writer_lock(d,'u'):
                with self.assertRaises(ValueError):
                    with f.writer_lock(d,'u'):pass

class PairEnsemble(unittest.TestCase):
    def test_mean_probabilities_and_exact_rows(self):
        import numpy as np
        f=load()
        with tempfile.TemporaryDirectory() as d:
            paths=[]
            for j,value in enumerate((.1,.9)):
                p=pathlib.Path(d)/f'{j}.npz';np.savez(p,participant=np.array(['p','p']),video_id=np.array([1,2]),p=np.full((2,34),value,dtype=np.float32));paths.append(p)
            out=f.paired_predictions(paths)
            self.assertTrue(np.array_equal(out['p'],np.full((2,34),.5,dtype=np.float32)))
            self.assertEqual(out['p_pairs'].shape,(2,2,34))
            np.savez(paths[1],participant=np.array(['p','p']),video_id=np.array([2,1]),p=np.full((2,34),.9))
            with self.assertRaisesRegex(ValueError,'row order'):f.paired_predictions(paths)

class RuntimePathBinding(unittest.TestCase):
    def test_swapped_config_rejected_while_frozen_original_intact(self):
        import os
        from unittest.mock import patch
        f=load()
        with tempfile.TemporaryDirectory() as d:
            a=pathlib.Path(d)/'a.yaml';b=pathlib.Path(d)/'b.yaml';a.write_text('original');b.write_text('different')
            with patch.dict(os.environ,{'EMOBRAIN_PATHS':str(b)},clear=True):
                with self.assertRaisesRegex(ValueError,'EMOBRAIN_PATHS'):f.check_runtime_paths({'paths_config':str(a)})
            self.assertEqual(a.read_text(),'original')
            with patch.dict(os.environ,{'EMOBRAIN_PATHS':str(a)},clear=True):f.check_runtime_paths({'paths_config':str(a)})

class TelemetryFailure(unittest.TestCase):
    def test_failed_enter_stops_sampler_restores_signal_and_preserves_receipt(self):
        import signal,sys,types
        from unittest.mock import patch
        path=P.parent/'measure_fit_units.py'
        spec=importlib.util.spec_from_file_location('meter_test',path);meter=importlib.util.module_from_spec(spec);spec.loader.exec_module(meter)
        def fail():raise RuntimeError('injected CUDA init failure')
        fake=types.SimpleNamespace(cuda=types.SimpleNamespace(synchronize=fail))
        old=signal.getsignal(signal.SIGTERM)
        with tempfile.TemporaryDirectory() as d,patch.dict(sys.modules,{'torch':fake,'fit_units':load()}),patch.object(meter,'query',side_effect=lambda fields,kind='gpu':[['GPU-TEST','0','0']] if kind=='gpu' else []):
            obj=meter.UnitTelemetry(d,'failure')
            with self.assertRaisesRegex(RuntimeError,'injected CUDA'):
                with obj:pass
            self.assertFalse(obj.thread.is_alive())
            self.assertEqual(signal.getsignal(signal.SIGTERM),old)
            self.assertEqual(json.loads((pathlib.Path(d)/'telemetry.json').read_text())['status'],'entry_failed')

if __name__=='__main__':unittest.main()
