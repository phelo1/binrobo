# P5g / P5i trench: wheel positions and ground contacts at the end state
import sys, numpy as np, mujoco, pickle
import lanerun as LR, lane_world as LW
rid = sys.argv[1]; cfg = LR.RUNS[rid]; S, R, L = LR.build(cfg); ck = pickle.load(open('runs/%s/ckpt.pkl' % rid, 'rb')); LR.set_state(S, ck['state'])
m, d = S.m, S.d; f = np.zeros(6)
for w in ('wheelL', 'wheelR', 'cwheelL', 'cwheelR', 'bwL', 'bwR', 'tug', 'bin'):
    p = d.xpos[L.bid[w]]; s, l = LW.project(p[:2][None]); print(w, 's %.3f lat %.3f z-surf %.3f' % (s[0], l[0], p[2] - LW.surface_z(p[0], p[1], cfg['variant'])[0]))
for i in range(d.ncon):
    c = d.contact[i]; mujoco.mj_contactForce(m, d, i, f); print(mujoco.mj_id2name(m, 5, c.geom1), mujoco.mj_id2name(m, 5, c.geom2), round(f[0]))
r = __import__('json').load(open('runs/%s/result.json' % rid)); print(r['events'][-6:]); print(r['sim_time_s'], r['t_start'])
