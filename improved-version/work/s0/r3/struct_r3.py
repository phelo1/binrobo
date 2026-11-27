#!/usr/bin/env python3
"""Revision 3 structure check (my own calculation, 14 Nov 2026).

Load model and allowables follow the B2-F author's S12 (h2/s12_struct.py) and the reviewer's s12_rev2 so the numbers are comparable:
  wheel "edge"  = largest drive-tyre force in the pothole and compliant-tyre kerb runs
  wheel "carry" = largest on smooth ground (climbs, e-stop, pivot, statics)
  comb "all"    = largest comb force (nib + lip rim) in any run except the open trench (which the site must keep covered)
  yield SF = yield / stress; target 2.0. S235 235 MPa, S355 355 MPa, 8.8 bolts 640 MPa, 12.9 1080 MPa, bronze bush 60 MPa (all nominal, ASSUMED as theirs).
Peak forces are read from the result files of MY runs of the same tests on the revision 3 model (tag given on the command line).

usage: struct_r3.py <res_dir> <tag> [--rail HxBxT] [--xm BxHxT] [--nose BxHxT] [--json out.json]"""
import json, glob, os, sys, math, argparse
ap = argparse.ArgumentParser(); ap.add_argument('res'); ap.add_argument('tag'); ap.add_argument('--rail', default='50x50x4'); ap.add_argument('--xm', default='50x50x5'); ap.add_argument('--nose', default='50x50x3')
ap.add_argument('--also', action='append', default=[], help='further result tags whose peaks are merged in'); ap.add_argument('--exclude', action='append', default=[], help='result file names (without B2F_ and .json) left out of the sizing loads and listed separately'); ap.add_argument('--json'); ap.add_argument('--fy_rail', type=float, default=355.0); ap.add_argument('--quiet', action='store_true'); A = ap.parse_args()
FY235, FY355, FY88, FY129, BUSH = 235.0, 355.0, 640.0, 1080.0, 60.0
AS = {'M4': 8.78, 'M8': 36.6, 'M10': 58.0, 'M12': 84.3}

def rhs(h, b, t):
    """h = depth in the bending direction, b = width, t = wall (mm). Sharp-corner formulas, as S12."""
    I = (b * h ** 3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12.0
    return dict(I=I, Z=I / (h / 2.0), Wt=2 * (b - t) * (h - t) * t, A=2 * t * (b + h - 2 * t))
def sec(s): return [float(x) for x in s.split('x')]

# ---------------------------------------------------------------- peaks from the result files
def cat(b, d):
    if 'trench' in b: return 'trench'
    if '_S5_' in b and 'step' in b: return 'step_rigid'
    if '_S5_' in b: return 'pothole'
    if '_S6_' in b: return 'ramp' if d.get('ramp') else ('kerb_compliant' if str(d.get('tyre', '')).startswith('0.') else 'kerb_rigid')
    if 'step40' in b: return 'step_rigid'
    if 'static' in b: return 'static'
    return 'carry'
P = {}; nfiles = 0; EXCL = []
for tg_, f in [(t_, f_) for t_ in [A.tag] + A.also for f_ in glob.glob(os.path.join(A.res, 'B2F_*%s.json' % t_))]:
    b = os.path.basename(f)
    if 'grab_' in b or 'tipcalc' in b or 'tyrecal' in b or b.startswith('B2F_gate'): continue
    d = json.load(open(f))
    if not isinstance(d, dict): continue
    if b.replace('B2F_', '').replace('.json', '') in A.exclude:
        EXCL.append(dict(file=b, wheel=d.get('drive_tyre'), comb=d.get('lipF'), pad=d.get('padF'), yaw_dev=d.get('yaw_dev'), roll=d.get('roll'))); continue
    if 'peak' in d:
        pk = d['peak']; r = dict(wheel=pk.get('drive_tyre_N', [0])[0], comb=pk.get('nib_rim_N', [0])[0], pad=pk.get('pad_N', [0])[0], lift=pk.get('lift_N', [0])[0])
    elif 'lipF' in d: r = dict(wheel=d['drive_tyre'], comb=d['lipF'], pad=d['padF'], lift=d['liftF'])
    elif 'driveL' in d: r = dict(wheel=max(d['driveL'], d['driveR']), comb=0.0, pad=d.get('pad_N', 0), lift=d.get('lift_N', 0), castor=d['caster_sum'])
    else: continue
    nfiles += 1; c = cat(b, d)
    for k, v in r.items():
        if (c, k) not in P or v > P[(c, k)][0]: P[(c, k)] = (float(v), b.replace('B2F_', '').replace('.json', ''))
g = lambda c, k: P.get((c, k), (0.0, '-'))
W_carry = max(g('carry', 'wheel'), g('static', 'wheel')); W_edge = max(g('pothole', 'wheel'), g('kerb_compliant', 'wheel'))
cats = ('carry', 'pothole', 'step_rigid', 'kerb_compliant', 'kerb_rigid', 'ramp')
C_carry = g('carry', 'comb'); C_all = max(g(c, 'comb') for c in cats); C_static = (110 * 9.81, 'bin 110 kg')
PAD = max(g(c, 'pad') for c in cats); LIFT = max(g(c, 'lift') for c in cats); CAST = max((v for (c, k), v in P.items() if k == 'castor'), default=(0.0, '-'))
loads = dict(files=nfiles, wheel_carry=W_carry, wheel_edge=W_edge, wheel_edge_pothole=g('pothole', 'wheel'), wheel_edge_kerb=g('kerb_compliant', 'wheel'), wheel_rigid_step_info=g('step_rigid', 'wheel'), wheel_trench_info=g('trench', 'wheel'),
             comb_carry=C_carry, comb_all=C_all, comb_by_case={c: g(c, 'comb') for c in cats + ('trench',)}, pad=PAD, lift=LIFT, castor_static_sum=CAST)

# ---------------------------------------------------------------- geometry of revision 3 (mm unless stated)
X_MAST = 0.490          # m, drive axle to the centre of the mast-base cross-member (x 465-515)
E_MAST = 0.450          # m, comb load to the upright centre (reviewer's figure for the upright at x 520)
BLOCK_PITCH = 0.200     # m
FOOT_LEVER = 0.048      # m, rear bearing edge of the foot shoe (x 467) to the front leg on the member's front face (x 515)
RW = 0.165; T_CAP = 60.0; T_PEAK = 150.0     # drive wheel radius (m); torque cap (N m); largest wheel torque logged in my files (N m)
rows = []
def row(item, case, load, stress, allow, note=''):
    sf = allow / stress if stress > 0 else float('inf'); rows.append(dict(item=item, case=case, load=load, stress=round(stress, 1), SF=round(sf, 2), ok=sf >= 2.0, note=note)); return sf

# 1 side rail (their model: the wheel force is carried in bending to the mast foot, M = F * x_mast, one rail)
h, b, t = sec(A.rail); S = rhs(h, b, t)
for case, F in (('carry', W_carry[0]), ('edge', W_edge[0])):
    row('Side rail %s, fy %.0f' % (A.rail, A.fy_rail), case, 'wheel %.0f N' % F, F * X_MAST * 1e3 / S['Z'], A.fy_rail, 'M = %.0f N m' % (F * X_MAST))
# 1b side rail: the mast-base cross-member delivers one upright's foot moment as a moment at the joint (worst: all of it to one side of the joint)
Mu_all = C_all[0] * E_MAST / 2; Mu_carry = C_carry[0] * E_MAST / 2
row('Side rail %s at the mast-base joint' % A.rail, 'comb_all', 'moment %.0f N m' % Mu_all, Mu_all * 1e3 / S['Z'], A.fy_rail, 'all of the joint moment on one side of the joint')
# 2 uprights 80x40x4 S235 at the foot
U = rhs(80, 40, 4)
for case, M in (('carry', Mu_carry), ('comb_all', Mu_all)): row('Mast upright 80x40x4 S235 at the foot', case, 'moment %.0f N m' % M, M * 1e3 / U['Z'], FY235)
# 3 mast-base cross-member: torsion from one upright's foot moment; bending under the lift actuator reaction at mid-span (span 0.86 m, simply supported)
xb, xh, xt = sec(A.xm); X = rhs(xh, xb, xt)
for case, M in (('carry', Mu_carry), ('comb_all', Mu_all)): row('Mast-base cross-member %s S355, torsion' % A.xm, case, 'torque %.0f N m' % M, M * 1e3 / X['Wt'], 0.577 * FY355)
F_ACT = 4000.0
row('Mast-base cross-member %s S355, bending under the actuator' % A.xm, 'lift 4 kN', '4000 N at mid-span', F_ACT * 0.86 / 4 * 1e3 / X['Z'], FY355)
# 4 mast foot shoe: 2 x M12 8.8 through the front leg (shear, lever 48 mm to the rear bearing edge) + 2 x M12 8.8 down through the member (tension, lever 23 mm).
#   Stress shown = bolt stress if the moment is shared in proportion to the yield capacity of the two bolt rows.
MCAP = 2 * AS['M12'] * 0.577 * FY88 * FOOT_LEVER + 2 * AS['M12'] * FY88 * 0.023       # N m at bolt yield
for case, M in (('carry', Mu_carry), ('comb_all', Mu_all)):
    row('Mast foot shoe bolt group, 4 x M12 8.8', case, 'moment %.0f N m' % M, FY88 * M / MCAP, FY88, 'capacity at bolt yield %.0f N m' % MCAP)
    row('Upright to shoe weld: full-penetration on the two 40 mm faces = wall strength', case, 'moment %.0f N m' % M, M * 1e3 / U['Z'], FY235, 'as the upright section')
# 5 rail blocks and rail screws
for case, F in (('carry', C_carry[0]), ('comb_all', C_all[0])):
    Pb = max(F, 1.0) * E_MAST / BLOCK_PITCH / 2
    rows.append(dict(item='HGH15CA block, C0 23.47 kN, pitch 200 mm', case=case, load='block %.0f N' % Pb, stress=None, SF=round(23470.0 / Pb, 2), ok=23470.0 / Pb >= 2, note=''))
    row('Rail screws M4 12.9 into the 10 mm flat (2 per block length)', case, 'screw %.0f N' % (Pb / 2), Pb / 2 / AS['M4'], FY129)
# 6 comb pivot pin D20 8.8, 20 mm cantilever (their assumption)
row('Comb pivot pin D20 8.8', 'comb_all', 'comb %.0f N' % C_all[0], C_all[0] * 20 / (math.pi * 20 ** 3 / 32), FY88)
# 7 nose cross-member: castor loads through the hanger plates at mid-span (vertical 3 g on the static castor sum), kerb strike torque
nb, nh, nt = sec(A.nose); N = rhs(nh, nb, nt)
Fv = 3 * CAST[0]
row('Nose cross-member %s S235, bending (3 g on the castor pair, at mid-span)' % A.nose, 'static x3', 'castors %.0f N' % Fv, Fv * 0.86 / 4 * 1e3 / N['Z'], FY235)
for T in (80.0, T_PEAK):
    Fh = 2 * T / RW; Mk = Fh * 0.21      # both drive wheels push the castor pair against a kerb; pivot pin 210 mm below the member centre (pin z 200, member z 385... lever to the member centre)
    row('Nose cross-member %s S235, torsion (kerb strike, %d N m per wheel)' % (A.nose, T), 'kerb', 'push %.0f N' % Fh, Mk * 1e3 / N['Wt'], 0.577 * FY235, 'lever 0.21 m to the pin')
# 8 rocker pin D20 and bushes D20 x 12, 70 mm apart; hanger plates 10 x 90 S355, welded to both faces of the nose cross-member
for T in (80.0, T_PEAK):
    Fh = 2 * T / RW; Fb = Fh / 2
    row('Rocker bushes D20 x 12 bronze (2, 70 mm apart)', 'kerb %d N m' % T, 'bush %.0f N' % Fb, Fb / (20 * 12), BUSH)
    row('Rocker pin D20 8.8 (bending between bush and housing, 12 mm arm)', 'kerb %d N m' % T, 'bush %.0f N' % Fb, Fb * 12 / (math.pi * 20 ** 3 / 32), FY88)
    row('Hanger plates 10 x 90 S355, weak axis, 185 mm from pin to the member', 'kerb %d N m' % T, 'plate %.0f N' % Fb, Fb * 185 / (90 * 10 ** 2 / 6.0), FY355, 'each plate takes half')
# 8b castor beam 50x40x3: 3 g on one castor, 280 mm from the pivot
CB = rhs(50, 40, 3); row('Castor beam 50x40x3 S235 at the pivot (3 g on one castor)', 'static x3', 'castor %.0f N' % (1.5 * CAST[0]), 1.5 * CAST[0] * 280 / CB['Z'], FY235)
# 9 actuator base bracket: 10 mm S355 back plate 120 wide, load 40 mm off the member face (gussets not counted); stall force ASSUMED 1.5 x the 4 kN rating until the supplier states it
F_STALL = 1.5 * F_ACT
for case, F in (('lift 4 kN', F_ACT), ('stall 6 kN (ASSUMED)', F_STALL)): row('Actuator base bracket 10 x 120 S355 (gussets not counted)', case, '%.0f N at 40 mm' % F, F * 40 / (120 * 10 ** 2 / 6.0), FY355)
row('Mast-base cross-member %s S355, bending under a stalled actuator' % A.xm, 'stall 6 kN (ASSUMED)', '6000 N at mid-span', F_STALL * 0.81 / 4 * 1e3 / X['Z'], FY355)
# 10 lift top stops: one bracket each side, 2 x M10 8.8 through the upright 50 mm apart, the tongue 85 mm in front of the bolt group
Pst = F_STALL / 2; Vb = Pst / 2 + Pst * 85 / 50.0
row('Lift stop bracket bolts, 2 x M10 8.8 each side', 'stall 6 kN (ASSUMED)', 'bolt %.0f N' % Vb, Vb / AS['M10'], 0.577 * FY88)
row('Lift stop tongue on the carriage plate edge, bearing 40 x 16 mm, aluminium', 'stall 6 kN (ASSUMED)', '%.0f N per side' % Pst, Pst / (40 * 16.0), 250.0, '6082-T6, 250 MPa ASSUMED')
# 11 bumper carrier: sideways knock on the bumper end; two drop legs 40x40x2, 200 mm from the arm to the bar; two guide pins D12, 20 mm stick-out
B = rhs(40, 40, 2)
for Fk in (500.0, 1000.0):
    row('Bumper carrier drop legs 2 x 40x40x2 S235, 200 mm', 'side knock %.0f N' % Fk, 'per leg %.0f N' % (Fk / 2), (Fk / 2) * 200 / B['Z'], FY235)
    row('Bumper guide pins 2 x D12 8.8, 20 mm stick-out', 'side knock %.0f N' % Fk, 'per pin %.0f N' % (Fk / 2), (Fk / 2) * 20 / (math.pi * 12 ** 3 / 32), FY88)
# 12 carriage: the tipping moment of the bin goes from the centre of the plate to the four rail blocks through two cross-beams 50x50x4 S355 (one per block row)
CBm = rhs(50, 50, 4)
for case, F in (('carry', C_carry[0]), ('comb_all', C_all[0])):
    Pb = max(F, 1.0) * E_MAST / BLOCK_PITCH / 2
    row('Carriage cross-beam 50x50x4 S355 (block force x 170 mm)', case, 'block %.0f N' % Pb, Pb * 170 / CBm['Z'], FY355)
    row('Carriage plate strip between beam end and block, 50 x 16 aluminium, 30 mm', case, 'block %.0f N' % Pb, Pb * 30 / (50 * 16 ** 2 / 6.0), 250.0, '6082-T6, 250 MPa ASSUMED')
# 13 pad arm 80x40x3 (40 deep in the load direction) and the plate tongue 120 x 16 aluminium; pad force at 560 below the comb, bolts at 75 and 230 below
PA = rhs(40, 80, 3); Rl = PAD[0] * (560 - 75) / (230 - 75.0)
row('Pad arm 80x40x3 S235 at the lower bolt', 'pad peak', 'pad %.0f N' % PAD[0], PAD[0] * (560 - 230) / PA['Z'], FY235)
row('Carriage plate tongue 120 x 16 aluminium at its root', 'pad peak', 'lower bolt %.0f N' % Rl, Rl * 120 / (120 * 16 ** 2 / 6.0), 250.0, '6082-T6, 250 MPa ASSUMED')
# 13b pad springs at the full 45 mm stroke: 2 springs, wire 4.5, mean diameter 26.5, 15 N/mm, 10 mm preload (shear stress with the Wahl factor)
Fsp = 15.0 * 55; C = 26.5 / 4.5; Kw = (4 * C - 1) / (4 * C - 4) + 0.615 / C
rows.append(dict(item='Pad spring at the full 45 mm stroke (wire 4.5, 15 coils)', case='full stroke', load='%.0f N per spring' % Fsp, stress=round(Kw * 8 * Fsp * 26.5 / (math.pi * 4.5 ** 3), 1), SF=round(0.5 * 1850 / (Kw * 8 * Fsp * 26.5 / (math.pi * 4.5 ** 3)), 2), ok=True, spring=True, note='spring check, not a yield check: against 0.5 x 1850 MPa (chrome-silicon spring wire, ASSUMED); an occasional load'))
out = dict(excluded=EXCL, also=A.also, tag=A.tag, sections=dict(rail=A.rail, mast_base=A.xm, nose=A.nose), loads=loads, rows=rows, min_SF=min(r['SF'] for r in rows if not r.get('spring')), failing=[r['item'] + ' / ' + r['case'] for r in rows if not r['ok']])
if A.json: json.dump(out, open(A.json, 'w'), indent=1)
if not A.quiet:
    print('files read: %d (tag %s)' % (nfiles, A.tag))
    print('LOADS  wheel carry %.0f N (%s) | wheel edge %.0f N (%s) [pothole %.0f, kerb compliant %.0f] | rigid step, info only %.0f' % (W_carry[0], W_carry[1], W_edge[0], W_edge[1], g('pothole', 'wheel')[0], g('kerb_compliant', 'wheel')[0], g('step_rigid', 'wheel')[0]))
    print('       comb carry %.0f N (%s) | comb all %.0f N (%s) | by case %s' % (C_carry[0], C_carry[1], C_all[0], C_all[1], {c: round(g(c, 'comb')[0]) for c in cats + ('trench',)}))
    print('       pad %.0f N (%s) | lift %.0f N | static castor sum %.0f N' % (PAD[0], PAD[1], LIFT[0], CAST[0]))
    for r in rows: print('  %-74s %-18s %-22s %s SF %5.2f %s %s' % (r['item'][:74], r['case'][:18], r['load'][:22], ('%6.1f MPa' % r['stress']) if r['stress'] is not None else '     -    ', r['SF'], 'ok ' if r['ok'] else 'LOW', r['note']))
    print('lowest SF %.2f; below 2.0: %s' % (out['min_SF'], out['failing'] or 'none'))
    for e in EXCL: print('left out of the sizing loads:', e)
