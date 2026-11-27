#!/usr/bin/env python3
"""Revision 4, list C: person-stop map, lowering guard, castor / step maps, lift shock (results in h2/res_r4x)."""
import json
E = "CGB_F9=1 CMP_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.34 X_LIFT_V=0.013 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r4.json B2F_PAD_IN=-0.015 B2_DOCK=front CMP_PREFIX=B2F_ H2_RES=/home/claude/b2f_run/revG/sim/cg/h2/res_r4x"
G0 = dict(pad_ret=0.0, lift_extra1=0.15, pad_stroke=0.045, act_N=6800.0); Y = '/home/claude/s0/r4/runY.py'
def line(tag, cmd, geo=None, **env):
    g = dict(G0); g.update(geo or {})
    return "env %s %s CGB_GEO='%s' IT1_TAG=%s python3 %s" % (E, ' '.join("%s=%s" % kv for kv in env.items()), json.dumps(g, separators=(',', ':')), tag, cmd)
a = []
for kg in (0, 110):
    for gr in (0, -0.03, -0.06, -0.09, -0.12):
        for mu in (0.6, 0.3):
            for v in (0.15, 0.2, 0.3, 0.4, 0.5): a.append(line('_r4', '%s pstop %g %g %g %g 0.15' % (Y, v, gr, mu, kg)))
for gr in (0, -0.06, -0.08, -0.12):
    for v in (0.2, 0.3):
        for kg in (0, 110): a.append(line('_r4', '%s pstop %g %g 0.22 %g 0.15' % (Y, v, gr, kg)))
for kg in (0, 110):
    for gr in (0, -0.06, -0.12):
        for mu in (0.3, 0.22):
            for v in (0.3, 0.5): a.append(line('_r4cb', '%s pstop %g %g %g %g 0.15' % (Y, v, gr, mu, kg), X_CBRAKE=30))
for gr in (-0.09, -0.12):
    for v in (0.2, 0.3):
        for mu in (0.3, 0.22): a.append(line('_r4', '%s pstop %g %g %g 0 0.15 rev' % (Y, v, gr, mu)))
for v, gr, mu, kg in ((0.5, 0, 0.3, 110), (0.3, -0.12, 0.3, 110), (0.5, 0, 0.3, 0), (0.15, -0.12, 0.3, 0), (0.4, 0, 0.3, 0)): a.append(line('_r4pm110', '%s pstop %g %g %g %g 0.15' % (Y, v, gr, mu, kg), PERT_M=1.1))
for tr in (0.10, 0.20):
    for v, gr, mu, kg in ((0.5, 0, 0.3, 110), (0.5, 0, 0.3, 0), (0.4, 0, 0.3, 0)): a.append(line('_r4', '%s pstop %g %g %g %g %g' % (Y, v, gr, mu, kg, tr)))
# lowering guard
for h, w, kg, m, extra in ((60, 'L', 110, 15, ''), (40, 'L', 110, 15, ''), (25, 'L', 110, 15, ''), (15, 'L', 110, 15, ''), (100, 'both', 110, 15, ''), (60, 'both', 110, 15, ''), (60, 'L', 25, 15, ''), (0, 'L', 110, 15, ''), (0, 'L', 25, 15, ''), (0, 'L', 60, 15, ''), (60, 'L', 110, 15, ' nocheck'), (60, 'L', 60, 15, '')):
    a.append(line('_r4', '%s lower %g %s %g %g%s' % (Y, h, w, kg, m, extra)))
# step and hill-start maps: castor contact strip, torque mode, distance of the step
MODES = dict(t60={}, b100=dict(X_BOOST=100))
for w in (0.008, 0.012, 0.016, 0.018, 0.020, 0.022, 0.025):
    for m in ('t60', 'b100'):
        for at in (1.6, 3.0):
            for side in ('both', 'one'): a.append(line('_r4w%02d%s' % (round(w * 2000), m), '%s liftpeak step %s 0.5' % (Y, side), X_CAST_W=w, X_STEP_AT=at, **MODES[m]))
for w in (0.008, 0.012, 0.016, 0.018, 0.020, 0.022, 0.025): a.append(line('_r4w%02dt60' % round(w * 2000), 'h2/runX.py climbn 0.22 0.06', X_CAST_W=w, H2_BINCG_DZ=0.06, H2_S7F=1))
# lift shock and wheel load with the cap far above the loads; tyre stiffness
TY = dict(t20='0.020,0.5;0.5,0.95,0.02', t30='0.030,0.5;0.5,0.95,0.02', t65='0.065,0.5;0.5,0.95,0.02')
for kind, side, v in (('kerb', 'nose', 0.5), ('kerb', 'nose', 0.8)):
    a.append(line('_r4cap12', '%s liftpeak %s %s %g' % (Y, kind, side, v), geo=dict(act_N=12000.0)))
    for k, t in TY.items(): a.append(line('_r4cap12%s' % k, '%s liftpeak %s %s %g' % (Y, kind, side, v), geo=dict(act_N=12000.0), H2_TYRE_POST="'%s'" % t))
for k, t in TY.items(): a.append(line('_r4%s' % k, 'h2/runX.py tyrecal', H2_TYRE_POST="'%s'" % t))
open('/home/claude/s0/r4/q_r4_c.txt', 'w').write('\n'.join(a) + '\n'); print(len(a))
