#!/usr/bin/env python3
"""Command lists for the revision 4 test campaign. Takes the revision 2 lists (same runners, same arguments) and swaps in the revision 3 model switches.
usage: mk_r3_campaign.py <mass json> <tag> [extra env]   writes q_<tag>_gate.txt, q_<tag>_pert.txt, q_<tag>_loads.txt, q_<tag>_s7.txt in this folder"""
import sys, re, json, os
massf, tag = sys.argv[1], sys.argv[2]; extra = sys.argv[3] if len(sys.argv) > 3 else 'X_CAST_W=0.012 X_POSTHOLD=0.030'
HERE = os.path.dirname(os.path.abspath(__file__)); GEO = dict(pad_ret=0.0, lift_extra1=0.15, pad_stroke=0.045, act_N=6800.0)
def env(geo=None, more=''):
    g = dict(GEO); g.update(geo or {})
    return ("env CGB_F9=1 CMP_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.245 X_LIFT_V=0.013 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 %s "
            "CGB_MASSF=%s B2F_PAD_IN=-0.015 CGB_GEO='%s' B2_DOCK=front CMP_PREFIX=B2F_ %s" % (extra, massf, json.dumps(g, separators=(',', ':')), more))
def conv(line, oldtag):
    m = re.search(r"CMP_PREFIX=B2F_ (.*?)IT1_TAG=(\S+) (python3 .*)$", line.strip()); assert m, line
    more, t, cmd = m.groups(); geo = None
    g = re.search(r"CGB_GEO='(\{.*?\})' ", more)
    if g: geo = json.loads(g.group(1)); more = more.replace(g.group(0), '')
    assert oldtag in t, (t, oldtag)
    return '%sIT1_TAG=%s %s' % (env(geo, more), t.replace(oldtag, '_' + tag), cmd)
gate = [conv(l, '_r2b') for l in open('/home/claude/s0/var_r2b.txt') if l.strip()]
pert = [conv(l, '_r2') for l in open('/home/claude/s0/var_r2_pert.txt') if l.strip()]
loads = [conv(l, '_mj401') for l in open('/home/claude/s0/r3/q_b2f_loads.txt') if l.strip() and 'H2_KEEPER' not in l]
T15 = "0.065,0.5;0.5,0.95,0.02"; T20 = "0.045,0.5;0.5,0.95,0.02"
X = lambda args, t='', geo=None, more='': '%sIT1_TAG=%s_%s python3 h2/runX.py %s' % (env(geo, more), t, tag, args)
H = lambda args, t='', geo=None, more='': '%sIT1_TAG=%s_%s python3 h2/runH2.py %s' % (env(geo, more), t, tag, args)
loads += [X('kerb 0.8 nose', '_r'), X('kerb 0.5 tail', '_r'), X('kerb 0.8 nose', '_t15', more="H2_TYRE_POST='%s' " % T15), X('kerb 0.5 tail', '_t15', more="H2_TYRE_POST='%s' " % T15),
          X('kerb 0.5 nose', '_t20', more="H2_TYRE_POST='%s' " % T20), X('kerb 0.5 nose', '_t15_80', geo=dict(tcap=80), more="H2_TYRE_POST='%s' " % T15)]
s7 = [X('climbn %s 0.06' % m, '_cg60', more='H2_S7F=1 H2_BINCG_DZ=0.06 ') for m in ('0.22', '0.25', '0.30')] + [X('climbn 0.22 0.06', '_cg0', more='H2_S7F=1 ')]
s7 += [H('static %s 110' % p, '_cg60', more='H2_BINCG_DZ=0.06 ') for p in ('up', 'dn', 'crL', 'crR')] + [X('tipcalc', '_cg60', more='H2_BINCG_DZ=0.06 ')]
for name, L in (('gate', gate), ('pert', pert), ('loads', loads), ('s7', s7)):
    open(os.path.join(HERE, 'q_%s_%s.txt' % (tag, name)), 'w').write('\n'.join(L) + '\n'); print(name, len(L))
