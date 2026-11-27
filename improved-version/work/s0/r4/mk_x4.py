#!/usr/bin/env python3
"""Command lists for the exploration runs of 20 Nov (revision 3 model at 152.2 kg, results in h2/res_x4)."""
import json
E = "CGB_F9=1 CMP_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.065 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r3s.json B2F_PAD_IN=-0.015 B2_DOCK=front CMP_PREFIX=B2F_ H2_RES=/home/claude/b2f_run/revG/sim/cg/h2/res_x4"
G0 = dict(pad_ret=0.0, lift_extra1=0.15, pad_stroke=0.045)
Y = '/home/claude/s0/r4/runY.py'
def line(tag, cmd, geo=None, **env):
    g = dict(G0); g.update(geo or {})
    return "env %s %s CGB_GEO='%s' IT1_TAG=%s python3 %s" % (E, ' '.join("%s=%s" % kv for kv in env.items()), json.dumps(g, separators=(',', ':')), tag, cmd)
L = {}
# X1 person stop
a = []
for kg in (0,):
    for v in (0.2, 0.3, 0.4, 0.5):
        for gr in (0, -0.06, -0.12):
            for mu in (0.6, 0.3, 0.22): a.append(line('_x4', '%s pstop %g %g %g %g 0.15' % (Y, v, gr, mu, kg)))
for tr in (0.10, 0.20):
    for v in (0.3, 0.5):
        for gr, mu in ((0, 0.6), (0, 0.3), (-0.12, 0.3)): a.append(line('_x4', '%s pstop %g %g %g 0 %g' % (Y, v, gr, mu, tr)))
for v in (0.3, 0.4, 0.5):
    for gr in (0, -0.06, -0.12):
        for mu in (0.6, 0.3): a.append(line('_x4', '%s pstop %g %g %g 110 0.15' % (Y, v, gr, mu)))
for v in (0.1, 0.2):
    for gr, mu in ((0, 0.6), (0, 0.3), (-0.12, 0.3)):
        for kg in (0, 110): a.append(line('_x4', '%s pstop %g %g %g %g 0.15 rev' % (Y, v, gr, mu, kg)))
for v, gr, mu, kg in ((0.5, 0, 0.3, 110), (0.3, -0.12, 0.3, 110), (0.5, 0, 0.3, 0), (0.3, -0.12, 0.3, 0)): a.append(line('_x4pm110', '%s pstop %g %g %g %g 0.15' % (Y, v, gr, mu, kg), PERT_M=1.1))
L['pstop'] = a
# X2 step map: castor contact strip x torque mode
W = (0.008, 0.010, 0.012, 0.015, 0.018, 0.020, 0.022, 0.025)
MODES = dict(t60={}, b100=dict(X_BOOST=100), t80=dict(geo=dict(tcap=80.0)))
a = []
for side, modes in (('both', ('t60', 'b100', 't80')), ('one', ('t60', 'b100'))):
    for w in W:
        for m in modes:
            kw = dict(MODES[m]); geo = kw.pop('geo', None); a.append(line('_x4w%02d%s' % (round(w * 2000), m), 'h2/runH2.py step %s' % side, geo=geo, X_CAST_W=w, **kw))
for w, tr in ((0.012, 0.035), (0.025, 0.065), (0.012, 0.065), (0.025, 0.035)):
    for m in ('t60', 'b100'): a.append(line('_x4w%02dtr%02d%s' % (round(w * 2000), round(tr * 1000), m), 'h2/runH2.py step both', X_CAST_W=w, X_CAST_TRAIL=tr, **MODES[m]))
L['step'] = a
# X3 slippery hill start map
a = []
for w in W:
    for m in ('t60', 'b100'): a.append(line('_x4w%02d%s' % (round(w * 2000), m), 'h2/runX.py climbn 0.22 0.06', X_CAST_W=w, H2_BINCG_DZ=0.06, **MODES[m]))
L['s7'] = a
# X4 lift shock load with and without the 3 kN cap; X5 tyre stiffness
a = []
for cap in (3000.0, 12000.0):
    for kind, side, v in (('step', 'one', 0.5), ('step', 'both', 0.5), ('kerb', 'nose', 0.5), ('kerb', 'nose', 0.8), ('kerb', 'tail', 0.5)):
        a.append(line('_x4cap%d' % (cap / 1000), '%s liftpeak %s %s %g' % (Y, kind, side, v), geo=dict(act_N=cap), X_BOOST=100))
TY = dict(t20='0.020,0.5;0.5,0.95,0.02', t30='0.030,0.5;0.5,0.95,0.02', t45='0.045,0.5;0.5,0.95,0.02', t65='0.065,0.5;0.5,0.95,0.02')
for k, t in TY.items():
    for v in (0.5, 0.8): a.append(line('_x4cap12%s' % k, '%s liftpeak kerb nose %g' % (Y, v), geo=dict(act_N=12000.0), X_BOOST=100, H2_TYRE_POST="'%s'" % t))
    a.append(line('_x4%s' % k, 'h2/runX.py tyrecal', H2_TYRE_POST="'%s'" % t))
a.append(line('_x4rigid', 'h2/runX.py tyrecal'))
L['lift'] = a
# X8 seating check at large docking offsets (camera error sigma 40 mm instead of 8 mm), with and without the check
a = [line('_x4cam40', 'h2/runH2.py grab ESE240CL 30 303', B2_CAMSIG=0.04), line('_x4cam40noph', 'h2/runH2.py grab ESE240CL 30 303', B2_CAMSIG=0.04, X_POSTHOLD=0),
     line('_x4cam25', 'h2/runH2.py grab ESE240CL 30 303', B2_CAMSIG=0.025), line('_x4cam25noph', 'h2/runH2.py grab ESE240CL 30 303', B2_CAMSIG=0.025, X_POSTHOLD=0)]
L['seat'] = a
# X6 softer pad (0.6 kN at full stroke): pick-ups and retention
soft = dict(pad_k=6667.0)
a = [line('_x4soft', 'h2/runH2.py grab %s 30 %d' % (b, s), geo=soft) for b, s in (('WEB140', 201), ('ESE240SL', 202), ('ESE240CL', 203))]
for b, f, v in (('ESE240SL', 'step', 0.5), ('ESE240SL', 'step', 0.8), ('ESE240SL', 'trench', 0.8), ('WEB140', 'step', 0.8)): a.append(line('_x4soft', 'h2/runX.py ret %s %s %g' % (b, f, v), geo=soft, H2_S5V=2))
for c in ('estop fwd', 'estop rev', 'climb 0.22 0.06', 'step one', 'step both'): a.append(line('_x4soft', 'h2/runH2.py ' + c, geo=soft))
a.append(line('_x4soft', 'h2/runX.py climbn 0.22 0.06', geo=soft, H2_BINCG_DZ=0.06))
L['soft'] = a
# X7 one docking try only
L['tries1'] = [line('_x4try1', 'h2/runH2.py grab %s 30 %d' % (b, s), X_DOCK_TRIES=1) for b, s in (('WEB140', 201), ('ESE240SL', 202), ('ESE240CL', 203))]
for k, v in L.items():
    open('/home/claude/s0/r4/q_x4_%s.txt' % k, 'w').write('\n'.join(v) + '\n'); print(k, len(v))
