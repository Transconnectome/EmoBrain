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

if __name__=='__main__':unittest.main()
