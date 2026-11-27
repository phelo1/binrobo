#!/usr/bin/env python3
"""Command lists for revision 3 (other agent's runners, my model switches). usage: mk_r3_lists.py <kind> <tag> <mass json> [extra env] > list.txt
kinds: ballast (statics, tip, nose-light, climbs, e-stops, kerb, pivot), loads (S5 retention + S6 kerb, their structural load cases), gate (full frozen gate + clip-lid seeds), pert"""
import sys, json
kind, tag, massf = sys.argv[1:4]; extra = sys.argv[4] if len(sys.argv) > 4 else ''
GEO = dict(pad_ret=0.0, lift_extra1=0.15, pad_stroke=0.045)
def env(geo=None, more=''):
    g = dict(GEO); g.update(geo or {})
    return ("env CGB_F9=1 CMP_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=5.71 X_NOSE_DX=0.065 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 "
            "CGB_MASSF=%s B2F_PAD_IN=-0.015 CGB_GEO='%s' B2_DOCK=front CMP_PREFIX=B2F_ %s%s" % (massf, json.dumps(g, separators=(',', ':')), extra + ' ' if extra else '', more))
def H(args, t='', geo=None, more=''): return '%sIT1_TAG=%s%s python3 h2/runH2.py %s' % (env(geo, more), t, tag, args)
def X(args, t='', geo=None, more=''): return '%sIT1_TAG=%s%s python3 h2/runX.py %s' % (env(geo, more), t, tag, args)
T15 = "0.065,0.5;0.5,0.95,0.02"; T20 = "0.045,0.5;0.5,0.95,0.02"
out = []
STAT = [H('static %s %d' % (p, k)) for p in ('up', 'dn', 'crL', 'crR') for k in (110, 60)]
CLIMB = [H('climb %s %s' % (m, c)) for m in ('0.22', '0.25', '0.30') for c in ('0.06', '0.09')]
REL = ['WEB140 up12 full', 'WEB140 dn12 empty', 'WEB140 flat full', 'ESE240CL flat empty', 'ESE240CL up12 full', 'ESE240CL dn12 empty', 'ESE240SL250 dn12 full', 'ESE240SL250 up12 empty', 'ESE240SL250 flat full']
if kind == 'ballast':
    out += [H('step one'), H('step both'), H('step both ramp')] + STAT + [X('tipcalc')] + CLIMB + [H('estop fwd'), H('estop rev'), H('towstab')]
    out += [X('climbn %s 0.06' % m, '_cg60', more='H2_S7F=1 H2_BINCG_DZ=0.06 ') for m in ('0.22', '0.25', '0.30')] + [X('climbn 0.22 0.06', '_cg0', more='H2_S7F=1 ')]
    out += [H('static %s 110' % p, '_cg60', more='H2_BINCG_DZ=0.06 ') for p in ('up', 'dn', 'crL', 'crR')] + [X('tipcalc', '_cg60', more='H2_BINCG_DZ=0.06 ')]
elif kind == 'loads':
    for b in ('ESE240SL', 'WEB140'):
        for f in ('step', 'pothole', 'trench'):
            for v in ('0.5', '0.8'): out.append(X('ret %s %s %s' % (b, f, v), more='H2_S5V=2 ' if f == 'step' else ''))
    out += [X('tyrecal', '_t20', more="H2_TYRE_POST='%s' " % T20), X('kerb 0.5 nose', '_r'), X('kerb 0.8 nose', '_r'), X('kerb 0.5 tail', '_r'), X('kerb 0.5 nose ramp', '_r'),
            X('kerb 0.5 nose', '_t15', more="H2_TYRE_POST='%s' " % T15), X('kerb 0.8 nose', '_t15', more="H2_TYRE_POST='%s' " % T15), X('kerb 0.5 tail', '_t15', more="H2_TYRE_POST='%s' " % T15),
            X('kerb 0.5 nose', '_t20', more="H2_TYRE_POST='%s' " % T20), X('kerb 0.5 nose', '_r80', geo=dict(tcap=80)), X('kerb 0.5 nose', '_t15_80', geo=dict(tcap=80), more="H2_TYRE_POST='%s' " % T15)]
print('\n'.join(out))
