"""Ω11 adversarial synthetic geometry tests. No physical or browser claims."""
import importlib.util
import math
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parent.parent/'scripts'/'world-clearance-omega11.py'
SPEC = importlib.util.spec_from_file_location('world_clearance_omega11', SOURCE)
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)
LO=(0,0,0)
HI=(1,1,1)

class Static3DOracle(unittest.TestCase):
    def test_axis_clear(self):
        x=G.classify_clearance((2,.5,.5),(3,.5,.5),LO,HI,radius=.2,unit='m')
        self.assertEqual((x['state'],x['distance']),('CLEAR',1))

    def test_degenerate_segment(self):
        self.assertAlmostEqual(G.segment_aabb_min_distance((2,2,2),(2,2,2),LO,HI),math.sqrt(3))

    def test_centerline_crosses_box(self):
        x=G.classify_clearance((-2,.5,.5),(2,.5,.5),LO,HI,radius=.1,unit='m')
        self.assertEqual((x['state'],x['distance']),('INTERSECTS',0))

    def test_diagonal_corner_stationary_point(self):
        d=G.segment_aabb_min_distance((2,1.5,.5),(1.5,2,.5),LO,HI)
        self.assertAlmostEqual(d,math.sqrt(1.125))

    def test_tangency_is_inconclusive(self):
        self.assertEqual(G.classify_clearance((2,.5,.5),(3,.5,.5),LO,HI,radius=1,unit='m')['state'],'INCONCLUSIVE')

    def test_float_border_is_inconclusive(self):
        self.assertEqual(G.classify_clearance((1.1,.5,.5),(2,.5,.5),LO,HI,radius=.1,epsilon=1e-8,unit='m')['state'],'INCONCLUSIVE')

    def test_uncertainty_blocks_false_clear(self):
        self.assertEqual(G.classify_clearance((1.11,.5,.5),(2,.5,.5),LO,HI,radius=.1,uncertainty=.02,unit='m')['state'],'INCONCLUSIVE')

    def test_invalid_input_blocks(self):
        for opts in (dict(radius=-1,unit='m'),dict(radius=0,unit='km'),
                     dict(radius=0,epsilon=0,unit='m')):
            with self.assertRaises(ValueError):
                G.classify_clearance((2,0,0),(3,0,0),LO,HI,**opts)
        with self.assertRaises(ValueError):
            G.segment_aabb_min_distance((math.nan,0,0),(2,0,0),LO,HI)
        with self.assertRaises(ValueError):
            G.segment_aabb_min_distance((0,0,0),(2,0,0),(2,0,0),(1,1,1))

    def test_port_center_only(self):
        self.assertEqual(G.classify_port((0,0,0),(0,0,0),tolerance=.1,unit='mm')['state'],'WITHIN')
        self.assertEqual(G.classify_port((1,0,0),(0,0,0),tolerance=.1,unit='mm')['state'],'OUTSIDE')
        self.assertEqual(G.classify_port((.1,0,0),(0,0,0),tolerance=.1,unit='mm')['state'],'INCONCLUSIVE')

    def test_motion_bound_not_inferred(self):
        s=[(0,(3,.5,.5),(4,.5,.5)),(1,(3,.5,.5),(4,.5,.5))]
        self.assertEqual(G.classify_sampled_motion(s,LO,HI,radius=.1,endpoint_speed_bound=None,unit='m')['state'],'INCONCLUSIVE')
        self.assertEqual(G.classify_sampled_motion(s,LO,HI,radius=.1,endpoint_speed_bound=.1,unit='m')['state'],'CLEAR')
        self.assertEqual(G.classify_sampled_motion(s,LO,HI,radius=.1,endpoint_speed_bound=5,unit='m')['state'],'INCONCLUSIVE')

    def test_sampled_intersection_detected(self):
        s=[(0,(2,.5,.5),(3,.5,.5)),(1,(.5,.5,.5),(2,.5,.5))]
        self.assertEqual(G.classify_sampled_motion(s,LO,HI,radius=.1,endpoint_speed_bound=None,unit='m')['state'],'INTERSECTS')

    def test_sample_order_fail_closed(self):
        s=[(0,(2,0,0),(3,0,0)),(0,(2,0,0),(3,0,0))]
        with self.assertRaises(ValueError):
            G.classify_sampled_motion(s,LO,HI,radius=.1,endpoint_speed_bound=.1,unit='m')

if __name__=='__main__':
    unittest.main()
