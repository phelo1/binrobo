import sys, numpy as np, mujoco, pickle, glob, os
import lanerun as LR, lane_world as LW
cfg = LR.RUNS['P5h_pothole'] if sys.argv[1]=='ph' else LR.RUNS['P5c_drop_ramp14']
S, R, L = LR.build(cfg); ck = LR.init_run('diag', cfg, S, R, L)
a = cfg['steps'][0][1]; D = LR.Drive(L, a); R.ctrl_fn = D.ctl
m = S.m; d = S.d; f = np.zeros(6); worst = {}
for k in range(60000):
    R.step()
    if k % 20 == 0:
        for i in range(d.ncon):
            c = d.contact[i]; b1 = m.geom_bodyid[c.geom1]; b2 = m.geom_bodyid[c.geom2]
            if (b1 == 0 and b2 in L.binbodies) or (b2 == 0 and b1 in L.binbodies):
                mujoco.mj_contactForce(m, d, i, f); n = (mujoco.mj_id2name(m, 5, c.geom1), mujoco.mj_id2name(m, 5, c.geom2))
                if f[0] > worst.get(n, (0,))[0]: worst[n] = (round(f[0]), round(L.s, 2), round(R.t, 2), round(L.wheel_clear()*1000,1))
    if D.remaining() < 0.02: break
print(worst); print('end s', L.s, 'clear min', L.M['clear_min'], 'liftF', L.M['liftF_max'])
