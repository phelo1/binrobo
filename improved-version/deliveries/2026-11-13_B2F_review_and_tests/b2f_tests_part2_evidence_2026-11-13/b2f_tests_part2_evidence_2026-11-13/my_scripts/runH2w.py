#!/usr/bin/env python3
"""Wrapper round the other agent's gate runner (h2/runH2.py), used only for grab trials with a wider start envelope.
It leaves their files untouched: it imports their trial sampler (g6/mc_g5.py), scales the lateral and yaw start
offsets of every sampled trial AFTER sampling (so the bins, friction, fill and lid of each trial are identical to
the frozen run with the same seed), then hands over to runH2.py unchanged.
  env X_DY_SCALE   (default 1.0)  multiplies the lateral start offset (frozen range +-0.08 m)
  env X_DYAW_SCALE (default 1.0)  multiplies the yaw start offset     (frozen range +-6 deg)
usage (from revG/sim/cg):  python3 <this file> grab <BIN> <n> <seed>
"""
import os, sys, runpy
CG = os.getcwd()
sys.path.insert(0, os.path.join(CG, '..', 'g6'))
import mc_g5
KY = float(os.environ.get('X_DY_SCALE', '1')); KA = float(os.environ.get('X_DYAW_SCALE', '1'))
_sample = mc_g5.sample
def sample(B, i, rng):
    p = _sample(B, i, rng)
    p['dy'] = round(p['dy'] * KY, 4); p['dyaw'] = round(p['dyaw'] * KA, 3)
    return p
mc_g5.sample = sample
target = os.path.join(CG, 'h2', 'runH2.py')
sys.argv = [target] + sys.argv[1:]
runpy.run_path(target, run_name='__main__')
