#!/usr/bin/env python3
"""The other agent's S7 nose-uphill climb (h2/runX.py climbn), re-run with a time trace of heading, wheel speeds and castor loads.
Their helper functions are taken from their file unchanged (everything above the command dispatch). Nothing is written to their result folder.
usage (from revG/sim/cg, with the model environment): s7_trace.py <mu> <crr> <out.json>"""
import os, sys, json, math
src = open(os.path.join(os.getcwd(), 'h2', 'runX.py')).read(); head = src[:src.index("\ncmd=sys.argv[1]")]
mu, cb, outp = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
sys.argv = ['runX.py', 'climbn']; ns = {'__name__': 'trace', '__file__': os.path.join(os.getcwd(), 'h2', 'runX.py')}; exec(compile(head, 'runX_head', 'exec'), ns)
B, np, mujoco, nominal, MX0, mon_full = ns['B'], ns['np'], ns['mujoco'], ns['nominal'], ns['MX0'], ns['mon_full']
S, R, g = nominal('ESE240SL', 110, crr_bin=cb)
for n in ('ground', 'bump', 'driveL', 'driveR', 'casterL', 'casterR', 'binwheelL', 'binwheelR'):
    gg = mujoco.mj_name2id(S.m, mujoco.mjtObj.mjOBJ_GEOM, n)
    if gg >= 0: S.m.geom_friction[gg][0] = mu
psi0 = S.rpy()[2]; tr = []
JN = [mujoco.mj_id2name(S.m, mujoco.mjtObj.mjOBJ_JOINT, j) for j in range(S.m.njnt)]
SW = [j for j, n in enumerate(JN) if n and ('swiv' in n.lower() or 'cfork' in n.lower() or 'caster' in n.lower() and 'spin' not in n.lower())]
WH = [j for j, n in enumerate(JN) if n and n.lower() in ('wheell', 'wheelr', 'drivel', 'driver', 'jwl', 'jwr')]
print('joints:', JN); print('swivel joints', [JN[j] for j in SW], 'wheel joints', [JN[j] for j in WH])
fine = []
def log():
    C = S.contacts() or {}
    try: C = S.loads()
    except Exception: pass
    tr.append([round(R.t, 2), R.phase[:14], round(S.rpy()[2] - psi0, 3), round(float(S.bin_in_tug()[1]) * 1000, 1), round(float(S.rpy('bin')[2] - S.rpy()[2]), 2)])
def run(fn, T):
    t0 = R.t; n = 0
    while R.t - t0 < T:
        if fn(): return True
        R.run_for(0.1); log()
        if R.phase.startswith('7 climb') and R.t - t0 < 4.0:
            fine.append([round(R.t - t0, 2), round(S.rpy()[2] - psi0, 2)] + [round(math.degrees(float(S.d.qpos[S.m.jnt_qposadr[j]])), 0) for j in SW] + [round(float(S.d.qvel[S.m.jnt_dofadr[j]]), 2) for j in WH] + [round(float(getattr(R, 'w', 0)), 2), round(float(getattr(R, 'wd', 0)), 3)])
    return False
R.phase = '7a onto 12 %'; R.ramp_grade(0.12, 0, 2.0); log(); R.run_for(1.0); log()
x0 = S.d.xpos[S.bid['tug']].copy(); dist = lambda: float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2] - x0[:2]))
R.phase = '7 climbing'; R.ctrl_fn = B.heading_hold(R, 0.5, psi0); ok = run(lambda: dist() >= 5.0, 25.0); R.ctrl_fn = None
R.phase = '8 brake hold'; R.hold(); run(lambda: False, 3.0)
dev = [abs(r[2]) for r in tr]; k = int(np.argmax(dev))
json.dump(dict(psi0=psi0, reached=bool(ok), max_dev=max(dev), at=tr[k], trace=tr, grab=g['result'], dock_dy=g.get('dock_dy_mm')), open(outp, 'w'))
print('psi0 %.3f deg; reached %s; largest heading deviation %.2f deg at t %.1f s in phase "%s"; bin sideways offset %.1f mm, bin yaw to robot %.2f deg' % (psi0, ok, max(dev), tr[k][0], tr[k][1], tr[k][3], tr[k][4]))
for r in fine[::2]: print('   ', r)
for r in tr[::20]: print('   t %6.1f  %-14s heading %+6.2f deg  bin dy %+6.1f mm  bin yaw %+5.2f' % tuple(r))
