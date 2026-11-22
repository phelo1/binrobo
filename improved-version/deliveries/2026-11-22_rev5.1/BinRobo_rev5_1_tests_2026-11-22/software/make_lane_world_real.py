#!/usr/bin/env python3
"""Writes work/b2f_lanephys/lane_world_real.py = the other agent's lane_world.py with the ASSUMED 12 % pitch overlay (G12) switched off, so the
lane profile is the EU-DEM profile as fetched (steepest 7.9 % over 10 m, 145-155 m from the house). Everything else is unchanged: the assumed
step, trench, pothole and leaf zones stay. The height-field cache gets its own file name.
Used by lanerun_x.py when X_LANE_WORLD=lane_world_real.   usage: make_lane_world_real.py <b2f_lanephys_dir>"""
import sys, os
d = sys.argv[1]; s = open(os.path.join(d, 'lane_world.py')).read()
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a); return s.replace(a, b)
s = rep(s, "w = smooth_win(G12[0], G12[1], 2.0); g1 = g0 * (1 - w) + (-0.12) * w", "w = 0.0 * smooth_win(G12[0], G12[1], 2.0); g1 = g0 * (1 - w) + (-0.12) * w   # [real profile] overlay off")
s = rep(s, "def hfield_grid(cache=os.path.join(HERE, 'hfield_cache.npz')):", "def hfield_grid(cache=os.path.join(HERE, 'hfield_cache_real.npz')):")
open(os.path.join(d, 'lane_world_real.py'), 'w').write(s); print('wrote lane_world_real.py')
