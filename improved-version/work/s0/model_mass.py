#!/usr/bin/env python3
"""Print the mass of the robot in the MuJoCo model actually built (all bodies except the bin), for the environment it is run in.
usage (from revG/sim/cg, with the same environment variables as a gate run): python3 model_mass.py [bin key]"""
import os, sys, importlib
sys.path.insert(0, os.path.join(os.getcwd(), 'h2')); sys.path.insert(0, os.path.join(os.getcwd(), 'b2'))
import mujoco, numpy as np
B = importlib.import_module(os.environ.get('CMP_SIM', 'simB2h')); S = B.SimB(sys.argv[1] if len(sys.argv) > 1 else 'ESE240SL')
m = S.m; names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(m.nbody)]
binb = [i for i, n in enumerate(names) if n and n.startswith(('bin', 'bw', 'lid'))]; rob = [i for i in range(1, m.nbody) if i not in binb]
tot = float(m.body_mass[rob].sum()); com = (m.body_mass[rob, None] * S.d.xipos[rob]).sum(0) / tot if hasattr(S, 'd') else None
mujoco.mj_forward(m, S.d); com = (m.body_mass[rob, None] * S.d.xipos[rob]).sum(0) / tot; tug = S.d.xpos[names.index('tug')]
print('robot mass %.2f kg; CG relative to the axle centre x %.3f y %.3f z %.3f m; bin %.2f kg' % (tot, com[0] - tug[0], com[1] - tug[1], com[2], float(m.body_mass[binb].sum())))
print({n: round(float(m.body_mass[i]), 2) for i, n in enumerate(names) if i in rob and m.body_mass[i] > 0.05})
