# drive-wheel normal load from carried-state snapshots (P2c 13 kg, P1 110 kg) - for the P2c_pf root cause
import sys, numpy as np, mujoco, pickle, glob
import lanerun as LR, lane_world as LW
for run, snap in (('P2c', 'runs/P2c/snaps/s556.0.pkl'), ('P1', 'runs/P1/snaps/s144.0.pkl'), ('P1', 'runs/P1/snaps/s556.0.pkl')):
    cfg = LR.RUNS[run]; S, R, L = LR.build(cfg); sp = pickle.load(open(snap, 'rb')); LR.set_state(S, sp['state'])
    m, d = S.m, S.d; f = np.zeros(6); acc = {}
    for k in range(400):
        mujoco.mj_step(m, d)
    for i in range(d.ncon):
        c = d.contact[i]; mujoco.mj_contactForce(m, d, i, f)
        n = [mujoco.mj_id2name(m, 5, g) or 'g%d' % g for g in (c.geom1, c.geom2)]
        if m.geom_bodyid[c.geom1] == 0 or m.geom_bodyid[c.geom2] == 0:
            key = n[1] if m.geom_bodyid[c.geom1] == 0 else n[0]; acc[key] = acc.get(key, 0) + f[0]
    tot = sum(acc.values()); print(run, snap, {k: round(v) for k, v in acc.items()}, 'total %.0f N' % tot, 'grade %.1f' % (100 * LW.grade(L.s)))
