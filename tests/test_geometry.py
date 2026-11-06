import unittest,sys,csv
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from extract import geometry_metrics
class GeometryTests(unittest.TestCase):
    def test_identical_grid(self):
        g=geometry_metrics([[0,0,0],[9,9,9]],np.eye(4),np.eye(4),[10]*3,[1]*3)
        self.assertEqual(g,{'max_bbox_excursion_mm':0.,'foreground_inside_pct':100.})
    def test_displaced_mask(self):
        a=np.eye(4);a[0,3]=20
        g=geometry_metrics([[0,0,0],[9,9,9]],a,np.eye(4),[10]*3,[1]*3)
        self.assertEqual(g,{'max_bbox_excursion_mm':20.,'foreground_inside_pct':0.})
    def test_source_data(self):
        with (ROOT/'data/geometry_comparison.csv').open() as f:r=list(csv.DictReader(f))
        self.assertEqual(len(r),130)
        self.assertEqual(sum(float(x['before_max_bbox_excursion_mm'])>0 for x in r),110)
        self.assertTrue(all(float(x['after_max_bbox_excursion_mm'])==0 and float(x['after_foreground_inside_pct'])==100 for x in r))
if __name__=='__main__':unittest.main()
