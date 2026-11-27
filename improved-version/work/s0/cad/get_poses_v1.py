#!/usr/bin/env python3
"""Gets the geometry numbers and body positions for the improved-version CAD from the gate simulation itself:
one straight grab of a full 240 L bin (ESE 240 SL), improved-version switches. Writes rec_B2F.json / rec_B2F.npz in the
layout the other agent's CAD script reads (geo, bin parameters, hull, body list, poses at 'start' and 'carrying')."""
import os, sys, json
os.environ.update(CGB_F9='1', CMP_SIM='simB2hx', X_LIFT_RANGE='0.35', X_ROCKER='1', B2F_PAD_IN='-0.005', CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}', B2_DOCK='front')
import numpy as np, mujoco
CG = '/home/claude/b2f_run/revG/sim/cg'
for p in (os.path.join(CG, '..', 'it1'), os.path.join(CG, '..', '..', 'g6'), CG, os.path.join(CG, 'b2'), os.path.join(CG, 'h2')): sys.path.insert(0, p)
os.chdir(CG)
import importlib; B = importlib.import_module('simB2hx'); import hull_h2 as HH
from bins_g5 import BINS
OUT = '/home/claude/s0/cad'
binkey = 'ESE240SL'; p = B.bin_params(binkey); p['fill'] = BINS[binkey]['fill_full']
S = B.SimB(binkey, p, tug_pose=B.start_pose(p)); R = B.RunnerB(S); m, d = S.m, S.d
BODIES = ['tug', 'wheelL', 'wheelR', 'cforkL', 'cforkR', 'cwheelL', 'cwheelR', 'lift', 'comb', 'keeper', 'padbase', 'pad', 'bin', 'bwL', 'bwR', 'lid']
def snap(tidy=True):
    q0 = d.qpos.copy()
    if tidy:   # drawing only: castors straight, rocker level (the reversing approach leaves the castors swivelled)
        for jn in ('swivelL', 'swivelR', 'rock'):
            j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jn)
            if j >= 0: d.qpos[m.jnt_qposadr[j]] = 0.0
        mujoco.mj_forward(m, d)
    q = np.full((len(BODIES), 7), np.nan)
    for k, n in enumerate(BODIES):
        b = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
        if b >= 0: q[k, :3] = d.xpos[b]; q[k, 3:] = d.xquat[b]
    d.qpos[:] = q0; mujoco.mj_forward(m, d); return q
mujoco.mj_forward(m, d); R.run_for(0.5); q_start = snap()
g = B.grab(R); R.hold(); R.run_for(2.0); q_carry = snap()
jl = m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, 'lift')]
print('grab', g.get('result'), 'captured', S.captured(), 'dock offset', g.get('dock_dy_mm'), 'wheel clear', g.get('wheel_clear_mm'), 'lift q', round(float(d.qpos[jl]), 4))
hull = HH.geom_params(binkey, p)
json.dump(dict(geo=B.GEO, p=p, hull=hull, bodies=BODIES, frames=dict(start=0, carrying=1), lift_q_carry=float(d.qpos[jl]), grab=dict(result=g.get('result'), wheel_clear_mm=g.get('wheel_clear_mm'), dock_dy_mm=g.get('dock_dy_mm'))),
          open(os.path.join(OUT, 'rec_B2F.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
np.savez(os.path.join(OUT, 'rec_B2F.npz'), q=np.array([q_start, q_carry]))
print('hull keys', sorted(hull.keys())); print('geo keys', sorted(B.GEO.keys()))
