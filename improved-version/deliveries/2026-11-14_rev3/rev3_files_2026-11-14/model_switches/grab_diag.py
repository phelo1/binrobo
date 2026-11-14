#!/usr/bin/env python3
"""Re-run chosen pick-up samples of a frozen batch and print why the scorer's truth test "seated" is true or false.
Same sampling as b2/runB2.py grab (their sampler g6/mc_g5.py, same seed arithmetic). Nothing is written.
usage (from revG/sim/cg, with the gate environment):  grab_diag.py <BIN> <n> <seed> <i,i,...>"""
import os, sys, json, numpy as np
CG = os.getcwd(); sys.path[:0] = [os.path.join(CG, 'h2'), os.path.join(CG, 'b2'), os.path.join(CG, '..', 'g6')]
import importlib, mc_g5
B = importlib.import_module(os.environ.get('CMP_SIM', 'simB2h')); from bins_g5 import BINS
b, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); want = [int(x) for x in sys.argv[4].split(',')]
rng = np.random.default_rng(seed); PS = [mc_g5.sample(BINS[b], i, rng) for i in range(n)]; CD = [float(rng.uniform(-0.010, 0.010)) for i in range(n)]
for i in want:
    p = dict(PS[i]); p['comb_d'] = CD[i]; pp = B.bin_params(b, p)
    S = B.SimB(b, pp, mu=p['mu'], tug_pose=B.start_pose(pp, p['dy'], p['dyaw'])); R = B.RunnerB(S); o = B.grab(R, seed=seed * 1000 + i)
    q = S.nib_in_bin(); P = S.p; G = B.GEO; xbt = P['xlip']; zL = P['zL_abs'] - P['wheel_r']; nh = G['nib_h']; nl = G['nib_l']; top = q[2] + nh / 2 + 0.005
    print(json.dumps(dict(i=i, result=o['result'], claim=o.get('claim'), seated=S.seated(), dock_dy_mm=o.get('dock_dy_mm'), tilt=o.get('bin_tilt_abs'), clear_mm=o.get('wheel_clear_mm'),
          nib_x_from_body_face_mm=round((q[0] - nl / 2 - xbt) * 1000, 1), channel_mm=[-4.0, round((0.022 + 0.004 - nl) * 1000, 1)], inx=bool((xbt - 0.004 < q[0] - nl / 2) and (q[0] + nl / 2 < xbt + 0.022 + 0.004)),
          nib_top_below_lip_mm=round((zL - top) * 1000, 1), inz_window_mm=[-6.0, 15.0], inz=bool((top > zL - 0.025 + 0.010) and (top < zL + 0.006)),
          nib_y_mm=round(q[1] * 1000, 1), iny=bool(abs(q[1]) <= abs(G['tooth_hw'] - P['lip_w'] / 2) + 0.02), nib_l_mm=nl * 1000, nib_h_mm=nh * 1000)), flush=True)
