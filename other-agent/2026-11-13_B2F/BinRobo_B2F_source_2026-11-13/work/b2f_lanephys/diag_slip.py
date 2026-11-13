# P2a_pf slip check: from the snapshot s166 drive through the leaf-patch entry, log wheel rim speed vs ground speed and axle torque
import numpy as np, mujoco, pickle, math
import lanerun as LR, lane_world as LW, simB2h as B
cfg = LR.RUNS['P2a_pf']; S, R, L = LR.build(cfg); sp = pickle.load(open('runs/P2a_pf/snaps/s166.0.pkl', 'rb'))
LR.set_state(S, sp['state']); LR.restore_attrs(S, R, sp['R'], sp['S']); L.carry = sp['carry']
a = cfg['steps'][2][1]; D = LR.Drive(L, a); R.ctrl_fn = D.ctl; d = S.d; m = S.m
jl, jr = L.dax; f = np.zeros(6)
for k in range(9000):
    R.step()
    if k % 200 == 0:
        v = S.fwd_speed(); wl, wr = d.qvel[jl] * B.RW, d.qvel[jr] * B.RW
        N = {}
        for i in range(d.ncon):
            c = d.contact[i]
            for g in (c.geom1, c.geom2):
                n = mujoco.mj_id2name(m, 5, g)
                if n in ('driveL', 'driveR'): mujoco.mj_contactForce(m, d, i, f); N[n] = N.get(n, 0) + f[0]
        print('t %.1f s %.2f mu %.2f v %.3f rimL %.3f rimR %.3f tqL %.1f tqR %.1f NL %.0f NR %.0f yaw-err %.0f' % (R.t, L.s, m.geom_friction[L.gground[0]][0], v, wl, wr, d.actuator_force[0], d.actuator_force[1], N.get('driveL', 0), N.get('driveR', 0),
              math.degrees(LR.wrap(L.tug_xy_yaw()[1] - LW.heading(L.s) - math.pi))))
