"""Structural guards on S2 arrays; synthetic tests do not validate anatomy."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

spec = importlib.util.spec_from_file_location('roi_structure', Path(__file__).resolve().parents[1] / 'scripts/b300/verify_s2_roi_voxels.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class StructureTest(unittest.TestCase):
    def fixture(self):
        return dict(offsets=np.array([0,2,3]), columns=np.array([0,1,1]), n_columns=np.array(4), shape=np.array([2,2,2]), affine=np.eye(4))

    def test_integer_valued_floats_and_cross_roi_overlap_preserved(self):
        z=self.fixture()
        for key in ['offsets','columns','n_columns','shape']:z[key]=z[key].astype(float)
        off,cols,n=module.validated_geometry(z,2)
        self.assertEqual(cols.tolist(),[0,1,1]);self.assertEqual(n,4)

    def test_malformed_arrays_fail_before_coercion(self):
        cases=[('offsets',np.array([1,3,4])),('offsets',np.array([0.,1.5,3.])),('offsets',np.array([0,3,2])),('offsets',np.array([0,3])),('columns',np.array([[0,1,1]])),('columns',np.array([0.,1.5,1.])),('columns',np.array([0.,np.inf,1.])),('columns',np.array([0,2**63,1],dtype=np.uint64)),('n_columns',np.array(4.5)),('n_columns',np.array([4])),('shape',np.array([2,0,2])),('shape',np.array([2,2.5,2])),('shape',np.array([2,2])),('affine',np.eye(3)),('affine',np.full((4,4),np.nan))]
        for key,value in cases:
            with self.subTest(key=key,value=value):
                z=self.fixture();z[key]=value
                with self.assertRaises(ValueError):module.validated_geometry(z,2)

if __name__=='__main__':unittest.main(verbosity=2)
