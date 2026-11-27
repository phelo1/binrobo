#!/usr/bin/env python3
"""Revision 4 structure check (my own calculation, 20 Nov 2026).

Load model and allowables follow the B2-F author's S12 (h2/s12_struct.py) and the reviewer's s12_rev2 so the numbers are comparable:
  wheel "edge"  = largest drive-tyre force in the pothole and compliant-tyre kerb runs
  wheel "carry" = largest on smooth ground (climbs, e-stop, pivot, statics)
  comb "all"    = largest comb force (nib + lip rim) in any run except the open trench (which the site must keep covered)
  yield SF = yield / stress; target 2.0. S235 235 MPa, S355 355 MPa, 8.8 bolts 640 MPa, 12.9 1080 MPa, bronze bush 60 MPa (all nominal, ASSUMED as theirs).
Peak forces are read from the result files of MY runs of the same tests on the revision 3 model (tag given on the command line).

usage: struct_r4.py <res_dir> <tag> [--rail HxBxT] [--xm BxHxT] [--nose BxHxT] [--json out.json]"""
import json, glob, os, sys, math, argparse
ap = argparse.ArgumentParser(); ap.add_argument('res'); ap.add_argument('tag'); ap.add_argument('--rail', default='60x60x4'); ap.add_argument('--xm', default='50x50x5'); ap.add_argument('--nose', default='50x50x4'); ap.add_argument('--xdir', default=None, help='folder with my extra runs (runY liftpeak / lat results)')
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


# ---------------------------------------------------------------- extra loads from my own tests (runY): stiff solid tyre on the kerb, lift shock, sideways tyre force
XD = {}
if A.xdir:
    for f in glob.glob(os.path.join(A.xdir, 'B2F_Y_liftpeak_*.json')):
        d = json.load(open(f)); k = os.path.basename(f).replace('B2F_Y_liftpeak_', '').replace('.json', '')
        if d.get('reached') and 'cap12' in k:
            ty = 'rigid' if d['tyre'] == 'rigid' else d['tyre'].split(',')[0]
            XD.setdefault('wheel_' + ty, (0.0, '')); XD.setdefault('lift', (0.0, ''))
            if d['wheel_peak_N'] > XD['wheel_' + ty][0]: XD['wheel_' + ty] = (float(d['wheel_peak_N']), k)
            if d['lift_peak_N'] > XD['lift'][0]: XD['lift'] = (float(d['lift_peak_N']), k)
    for f in glob.glob(os.path.join(A.xdir, 'B2F_Y_lat_*.json')):
        d = json.load(open(f)); XD['lat'] = max(XD.get('lat', (0.0, '')), (float(d['max_lat_N']), os.path.basename(f)))
loads['extra'] = XD
W_stiff = XD.get('wheel_0.020', (0.0, '-')); LIFT_SHOCK = max(XD.get('lift', (0.0, '-')), LIFT); LAT = XD.get('lat', (1000.0, 'ASSUMED 1 kN'))

# ---------------------------------------------------------------- geometry of revision 4 (mm unless stated)
X_MAST = 0.490; E_MAST = 0.450; BLOCK_PITCH = 0.200; RW = 0.165; T_PEAK = 150.0
H_STRUT = 0.360          # m, mast foot (z 410) to the strut pin on the upright (z 770)
A_STRUT = math.atan2(770 - 462, 955 - 592)   # strut angle below horizontal
F_ACT = 6800.0; F_CLUTCH = 1.4 * F_ACT       # actuator rated push; largest push if its own end-stop switches fail (slip clutch at up to 1.4 x, data sheet)
FY6082 = 250.0
rows = []
def row(item, case, load, stress, allow, note='', info=False):
    sf = allow / stress if stress > 0 else float('inf'); rows.append(dict(item=item, case=case, load=load, stress=round(stress, 1), SF=round(sf, 2), ok=(sf >= 2.0), note=note, info=info)); return sf

# 1 side rail: wheel force carried in bending to the mast-base joint (their model), net section at the bolt holes of the corner plates (one 9 mm hole in each flange)
h, b, t = sec(A.rail); S = rhs(h, b, t); Inet = S['I'] - 2 * (9 * t * (h / 2 - t / 2) ** 2); Znet = Inet / (h / 2)
for case, F in (('carry', W_carry[0]), ('edge', W_edge[0])):
    row('Side rail %s S355, net section at the joint' % A.rail, case, 'wheel %.0f N' % F, F * X_MAST * 1e3 / Znet, A.fy_rail, 'M = %.0f N m' % (F * X_MAST))
if W_stiff[0] > 0: row('Side rail %s S355, net section at the joint' % A.rail, 'sharp 40 mm kerb at 0.8 m/s on a stiff solid tyre (650 N/mm)', 'wheel %.0f N' % W_stiff[0], W_stiff[0] * X_MAST * 1e3 / Znet, A.fy_rail, 'my run ' + W_stiff[1])
Wr = max(g('step_rigid', 'wheel'), g('kerb_rigid', 'wheel'), XD.get('wheel_rigid', (0.0, '')))
row('Side rail %s S355, net section at the joint' % A.rail, 'the same kerb on a perfectly rigid tyre (not a real tyre; shown for the limit)', 'wheel %.0f N' % Wr[0], Wr[0] * X_MAST * 1e3 / Znet, A.fy_rail, 'against yield: %.2f' % (A.fy_rail / (Wr[0] * X_MAST * 1e3 / Znet)), info=True)
# 1b fatigue at the joint (the reviewer's rough spectrum: static wheel load with a full bin +/-50 % per bump, 2.0 million cycles in 10 years; ASSUMED)
Wst = g('static', 'wheel')[0] or 900.0; dS = Wst * X_MAST * 1e3 / Znet; FAT = 90.0 / 1.35
rows.append(dict(item='Side rail %s at the joint, fatigue: bolted plates (holes, detail category 90, partial factor 1.35)' % A.rail, case='ASSUMED spectrum: wheel %.0f N +/-50 %%, 2 million cycles' % Wst, load='range %.0f N' % Wst, stress=round(dS, 1), SF=round(FAT / dS, 2), ok=FAT / dS >= 1.0, note='allowable range %.1f MPa; needs 1.0' % FAT, info=True))
# 2 mast: the tipping moment of one upright (comb load x 0.45 m / 2) is taken by the strut. Upright bending at the strut pin; strut; pins; lugs; cleats
U = rhs(80, 40, 4); ST = rhs(30, 30, 2)
for case, C in (('carry', C_carry[0]), ('comb_all', C_all[0])):
    Mu = C * E_MAST / 2; H = Mu / H_STRUT; N = H / math.cos(A_STRUT); V = N * math.sin(A_STRUT)
    row('Mast upright 80x40x4 S235 at the strut pin', case, 'moment %.0f N m' % Mu, Mu * 1e3 / U['Z'], FY235)
    if case == 'comb_all':
        Pcr = math.pi ** 2 * 210000.0 * ST['I'] / 476.0 ** 2
        row('Mast strut 30x30x2 S235, axial', case, 'strut %.0f N' % N, N / ST['A'], FY235, 'Euler load %.0f kN' % (Pcr / 1000))
        row('Strut pins M10 8.8, double shear', case, 'strut %.0f N' % N, N / (2 * AS['M10']), 0.577 * FY88)
        row('Strut lug plates 2 x 5 mm S355, bearing on the pin', case, 'strut %.0f N' % N, N / (2 * 10 * 5.0), 1.5 * FY355, 'bearing limit 1.5 fy')
        Vb = math.hypot(N / 4, N * 52 / 40.0 / 2)
        row('Lug bolts 2 x M8 8.8 through the upright (2 shear planes each; pin 52 mm in front of the bolts)', case, 'per plane %.0f N' % Vb, Vb / AS['M8'], 0.577 * FY88)
        row('Strut foot cleats 2 x angle 40x40x4 S355, leg in its own plane, pin 52 mm above the member', case, 'push %.0f N' % H, (H / 2) * 52 / (4 * 40 ** 2 / 6.0), FY355)
        row('Mast foot cleats: 2 x M8 8.8 through the upright (2 shear planes each)', case, 'foot %.0f N' % H, H / (4 * AS['M8']), 0.577 * FY88)
        row('Mast foot cleats: 2 x M12 8.8 down through the cross-member, shear', case, 'foot %.0f N' % H, H / (2 * AS['M12']), 0.577 * FY88)
        # 3 cross-members under the mast loads
        xb, xh, xt = sec(A.xm); X = rhs(xh, xb, xt); nb, nh, nt = sec(A.nose); Nn = rhs(nh, nb, nt)
        Mh = H * 0.195; s_xm_h = Mh * 1e3 / X['Z']
        row('Mast-base cross-member %s S355: two foot forces sideways to the member (195 mm from each rail)' % A.xm, case, '2 x %.0f N' % H, s_xm_h, FY355)
        s_n_h = H * 0.195 * 1e3 / Nn['Z']; s_n_v = V * 0.195 * 1e3 / Nn['Z']; Fv = 3 * CAST[0]; s_n_c = Fv * 0.79 / 4 * 1e3 / Nn['Z']
        row('Nose cross-member %s S355: strut forces (both axes) + 3 x the static castor load at mid-span, summed at one corner' % A.nose, case + ' + castors x3', 'strut %.0f N, castors %.0f N' % (N, Fv), s_n_h + s_n_v + s_n_c, FY355, 'parts: %.0f + %.0f + %.0f MPa' % (s_n_h, s_n_v, s_n_c))
xb, xh, xt = sec(A.xm); X = rhs(xh, xb, xt)
for case, F in (('lift shock, largest in my runs', LIFT_SHOCK[0]), ('actuator at its rated push', F_ACT), ('actuator against a stop, slip clutch at 1.4 x (its own end stops failed)', F_CLUTCH)):
    row('Mast-base cross-member %s S355, bending under the actuator at mid-span' % A.xm, case, '%.0f N' % F, F * 0.79 / 4 * 1e3 / X['Z'], FY355)
    row('Actuator base bracket: angle 100x100x12 S355, 120 wide, pin 40 mm from the upright leg', case, '%.0f N' % F, F * 40 / (120 * 12 ** 2 / 6.0), FY355)
    row('Base bracket bolts 2 x M12 8.8 through the cross-member (shear + prying)', case, '%.0f N' % F, math.hypot(F / 2, F * 50 / 70.0 / 2) / AS['M12'], FY88)
    row('Lug angles on the bracket: 2 x M8 8.8 each', case, 'per lug %.0f N' % (F / 2), (F / 2) / (2 * AS['M8']), 0.577 * FY88)
    row('Frame joint at the mast base: top and bottom plates 6 mm S355, 90 wide, 30 mm from bolt to rail edge (half the actuator load per joint, shared by two plates)', case, 'joint %.0f N' % (F / 2), (F / 4) * 30 / (90 * 6 ** 2 / 6.0), FY355)
# lift self-locking and the stops
rows.append(dict(item='Lift actuator holding (LINAK LA36 6.8 kN type: self-lock at least 8,800 N, data sheet)', case='lift shock, largest in my runs', load='%.0f N' % LIFT_SHOCK[0], stress=None, SF=round(8800.0 / max(LIFT_SHOCK[0], 1), 2), ok=8800.0 / max(LIFT_SHOCK[0], 1) >= 2, note=LIFT_SHOCK[1], info=False))
Ps = F_CLUTCH / 2; Vb = math.hypot(Ps / 2, Ps * 25 / 30.0)
row('Lift stop blocks: 2 x M10 8.8 through the upright, 30 mm apart, load 25 mm off the face', 'slip clutch 1.4 x', 'block %.0f N' % Ps, Vb / AS['M10'], 0.577 * FY88)
row('Upright wall 4 mm S235 in bearing under a stop bolt', 'slip clutch 1.4 x', 'bolt %.0f N' % Vb, Vb / (2 * 10 * 4.0), 1.5 * FY235, 'two walls; bearing limit 1.5 fy; crush tube inside')
row('Carriage cross-beam end on the aluminium stop block, 26 x 46 mm', 'slip clutch 1.4 x', 'block %.0f N' % Ps, Ps / (26 * 46.0), FY6082)
# 5 rail blocks, screws, carriage (as revision 3)
CBm = rhs(50, 50, 4)
for case, F in (('carry', C_carry[0]), ('comb_all', C_all[0])):
    Pb = max(F, 1.0) * E_MAST / BLOCK_PITCH / 2
    rows.append(dict(item='HGH15CA block, C0 23.47 kN, pitch 200 mm', case=case, load='block %.0f N' % Pb, stress=None, SF=round(23470.0 / Pb, 2), ok=23470.0 / Pb >= 2, note='', info=False))
    row('Rail screws M4 12.9 into the 10 mm flat (2 per block length)', case, 'screw %.0f N' % (Pb / 2), Pb / 2 / AS['M4'], FY129)
    row('Carriage cross-beam 50x50x4 S355 (block force x 170 mm)', case, 'block %.0f N' % Pb, Pb * 170 / CBm['Z'], FY355)
    row('Carriage plate strip between beam end and block, 50 x 16 aluminium, 30 mm', case, 'block %.0f N' % Pb, Pb * 30 / (50 * 16 ** 2 / 6.0), FY6082, '6082-T6, 250 MPa ASSUMED')
row('Comb pivot pin D20 8.8', 'comb_all', 'comb %.0f N' % C_all[0], C_all[0] * 20 / (math.pi * 20 ** 3 / 32), FY88)
# 8 castor pivot: pin, bushes, clamp plates and their bolts
for T in (100.0, T_PEAK):
    Fh = 2 * T / RW; Fb = Fh / 2
    row('Rocker bushes D20 x 12 bronze (2, 70 mm apart)', 'kerb strike, %d N m per wheel' % T, 'bush %.0f N' % Fb, Fb / (20 * 12), BUSH)
    row('Rocker pin D20 8.8 (12 mm arm)', 'kerb strike, %d N m per wheel' % T, 'bush %.0f N' % Fb, Fb * 12 / (math.pi * 20 ** 3 / 32), FY88)
    row('Pivot clamp plates 10 x 90 S355, weak axis, 185 mm from the pin to the member', 'kerb strike, %d N m per wheel' % T, 'plate %.0f N' % Fb, Fb * 185 / (90 * 10 ** 2 / 6.0), FY355)
    row('Clamp bolts 4 x M10 8.8 through the nose member (plate root moment over a 35 mm lever, 2 bolts)', 'kerb strike, %d N m per wheel' % T, 'plate %.0f N' % Fb, (Fb * 185 / 35.0 / 2) / AS['M10'], FY88)
    nb, nh, nt = sec(A.nose); Nn = rhs(nh, nb, nt)
    row('Nose cross-member %s S355, torsion (kerb strike)' % A.nose, 'kerb strike, %d N m per wheel' % T, 'push %.0f N' % Fh, Fh * 0.21 * 1e3 / Nn['Wt'], 0.577 * FY355)
CB = rhs(50, 40, 3); row('Castor beam 50x40x3 S235 at the pivot (3 x the static load on one castor)', 'static x3', 'castor %.0f N' % (1.5 * CAST[0]), 1.5 * CAST[0] * 280 / CB['Z'], FY235)
# 11 bumper carrier: folded 5 mm brackets (leg = angle 40x40x5, W 1.91 cm3), backing beam 40x40x2
BB = rhs(40, 40, 2)
for Fk in (500.0, 1000.0): row('Bumper side brackets: folded leg, angle 40x40x5 S355, 185 mm', 'side knock %.0f N at the bumper' % Fk, 'per leg %.0f N' % (Fk / 2), (Fk / 2) * 185 / 1910.0, FY355)
row('Bumper side brackets: leg in its own plane 40 x 5 S355, 185 mm', 'bumper pressed to 600 N (the maker\'s largest reference force)', 'per leg 300 N', 300 * 185 / (5 * 40 ** 2 / 6.0), FY355)
row('Bumper backing beam 40x40x2 S235 between the legs (300 mm span) with 175 mm overhangs', 'bumper pressed to 600 N on one end', '600 N at the tip', 600 * 175 / BB['Z'], FY235)
# 12 drive / motor plate 8 mm S355, 200 wide: sideways tyre force at the ground, 354 mm below the flange
for case, F in (('largest sideways tyre force in my runs', LAT[0]), ('1.0 kN (the reviewer\'s figure)', 1000.0)):
    row('Drive / motor plate 8 x 200 S355, weak axis at the flange', case, '%.0f N at the ground' % F, F * 354 / (200 * 8 ** 2 / 6.0), FY355, LAT[1] if 'my runs' in case else '')
# 13 pad arm, tongue (as revision 3)
PA = rhs(40, 80, 3); Rl = PAD[0] * (560 - 75) / (230 - 75.0)
row('Pad arm 80x40x3 S235 below the tongue bolts', 'pad peak', 'pad %.0f N' % PAD[0], PAD[0] * (560 - 230) / PA['Z'], FY235)
row('Carriage plate tongue 120 x 16 aluminium at its root', 'pad peak', 'lower bolt %.0f N' % Rl, Rl * 120 / (120 * 16 ** 2 / 6.0), FY6082, '6082-T6, 250 MPa ASSUMED')
row('Tongue bolts 3 x M10 8.8 (lower pair reaction)', 'pad peak', 'reaction %.0f N' % Rl, Rl / (2 * AS['M10']), 0.577 * FY88)
# 14 pad springs: 2 x (wire 4.5, mean diameter 26.5, 14.5 active coils): 15 N/mm each; 145 mm free, 135 fitted, 90 at full stroke; solid 74.3 mm
d_, D_, n_ = 4.5, 26.5, 14.5; k_ = 15.0; c_ = D_ / d_; Kw = (4 * c_ - 1) / (4 * c_ - 4) + 0.615 / c_
for case, defl in (('fitted (pad just touching)', 10.0), ('largest pad force in my runs', PAD[0] / 2 / k_), ('full stroke 45 mm', 55.0)):
    F1 = k_ * defl; tau = Kw * 8 * F1 * D_ / (math.pi * d_ ** 3)
    rows.append(dict(item='Pad spring (2 x %.1f N/mm), shear stress with the Wahl factor' % k_, case=case, load='%.0f N each' % F1, stress=round(tau, 0), SF=round(925.0 / tau, 2), ok=tau <= 925.0, note='allowable 925 MPa for chrome-silicon wire (ASSUMED); spring check, needs 1.0', info=True))
Ls = (n_ + 2) * d_; Sa = n_ * (0.0015 * D_ ** 2 / d_ + 0.1 * d_)
rows.append(dict(item='Pad spring: length left before solid at full stroke', case='free 145, full stroke 90, solid %.1f mm' % Ls, load='-', stress=None, SF=round((90.0 - Ls) / Sa, 2), ok=(90.0 - Ls) >= Sa, note='%.1f mm left; EN 13906-1 asks %.1f mm' % (90.0 - Ls, Sa), info=True))
out = dict(loads=loads, rows=rows, sections=dict(rail=A.rail, xm=A.xm, nose=A.nose), fy_rail=A.fy_rail, excluded=EXCL, rail_Znet_mm3=round(Znet), rail_Z_mm3=round(S['Z']))
if A.json: json.dump(out, open(A.json, 'w'), indent=1)
print('loads from %d result files:' % nfiles)
for k, v in loads.items():
    if k not in ('files', 'comb_by_case', 'extra'): print('  %-26s %8.0f N   %s' % (k, v[0], v[1]))
print('  extra:', XD)
print('\n%-118s %-52s %-30s %8s %6s' % ('item', 'case', 'load', 'MPa', 'SF'))
for r in rows: print('%-118s %-52s %-30s %8s %6.2f %s %s' % (r['item'][:118], r['case'][:52], r['load'][:30], '-' if r['stress'] is None else r['stress'], r['SF'], '' if r['ok'] else ('(info)' if r.get('info') else '<< BELOW 2.0'), r['note'][:60]))
low = [r for r in rows if not r['ok'] and not r.get('info')]; print('\nrows below 2.0 (not counting information rows): %d of %d' % (len(low), sum(1 for r in rows if not r.get('info'))))
if EXCL: print('left out of the sizing loads:', EXCL)
