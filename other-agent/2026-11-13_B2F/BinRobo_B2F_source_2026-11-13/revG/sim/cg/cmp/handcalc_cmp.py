#!/usr/bin/env python3
"""Hand calcs, B1 vs Rev H, same method for both (it1/handcalc_it1.py method). Output res/handcalc_cmp.json.
 - drive torque and mu_req on 12 % (sim friction-loss terms as in the frozen model), drive/castor loads flat and on 12 %
 - tip angles (support polygon), castor lift-off
 - comb/lip contact: bearing pressure and ledge bending on the lip section of the gate model (30 x 8 mm ledge, rim at 26 mm),
   coverage of the EN 840 receiver width (EN 840-1:2004 Tables 2/3 dim. 2: 480 mm 140 L, 580 mm 240 L)
B1 numbers: it1/res/handcalc_it1.json (unchanged). Rev H: masses from cmp/mass_revH.json (= params.MASS_ITEMS), bin CG from the
gate bin model (bins_g5) carried by its front wall at pad_x 0.37, upright and at the hang tilt measured in MuJoCo."""
import json, math, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..', 'g6'))
from bins_g5 import BINS
g = 9.81; th = math.atan(0.12); s, c = math.sin(th), math.cos(th)
OUT = {}
OUT['B1'] = json.load(open(os.path.join(H, '..', 'it1', 'res', 'handcalc_it1.json')))['ITER1_B1']

def bin_cg_front(binkey, kg):
    """bin CG (x from the FRONT wall at rim height, + = toward the handle; z above the bin base) - gate bin model, mirrored"""
    B = BINS[binkey]; bx = B['bar_x'][0]; cb = B['cb'][0]; r = 0.0135; xbt = bx - cb; sc = B['D'] / 0.74; bh = B['bar_abs'][0] - B['wheel'] / 2
    xfront = bx + r - B['D'] + 0.02
    me = B['empty'] - 1.4 - 1.8; mf = kg - B['empty']; ce = (xbt - 0.32 * sc, 0.42 * bh / 0.93); cf = (xbt - 0.33 * sc, 0.38 * bh / 0.93)
    m = me + mf + 3.2; x = (me * ce[0] + mf * cf[0] + 3.2 * xbt) / m; z = (me * ce[1] + mf * cf[1] + 3.2 * bh) / m
    return x - xfront, z + B['wheel'] / 2, B, bh + B['wheel'] / 2     # dist behind the front wall, CG height (bin standing), rim height

def revh(kg, tilt_deg, lift=0.10, binkey='ESE240SL'):
    M_ = json.load(open(os.path.join(H, 'mass_revH.json'))); rws = M_['rows'] + M_['carriage']
    mt = sum(r['kg'] for r in rws); xt = sum(r['kg'] * r['p'][0] for r in rws) / mt; zt = sum(r['kg'] * r['p'][2] for r in rws) / mt
    xc, yc, yd, xtail, ytail, gap = 0.74, 0.30, 0.485, -0.40, 0.405, 0.075
    if kg:
        xf, zb, B, zr = bin_cg_front(binkey, kg)
        Xb, Zb = 0.374 - xf, zb + lift
        if tilt_deg:     # bin rotates about the lip (front wall, rim height) so its base swings toward the mast (measured hang tilt)
            p = (0.374, zr + lift); rx, rz = Xb - p[0], Zb - p[1]; a = math.radians(tilt_deg)
            Xb, Zb = p[0] + rx * math.cos(a) - rz * math.sin(a), p[1] + rx * math.sin(a) + rz * math.cos(a)
            Xb, Zb = p[0] + (Xb - p[0]), Zb
    else: Xb = Zb = 0.0
    M = mt + kg; X = (mt * xt + kg * Xb) / M; Z = (mt * zt + kg * Zb) / M
    def tip_side(px, py, qx, qy):
        L = math.hypot(qx - px, qy - py); d = abs((qx - px) * (py - 0) - (px - X) * (qy - py)) / L; return math.degrees(math.atan(d / Z))
    Nd = M * g * (xc - X) / xc
    Nd_up = M * g * (c * (xc - X) - s * Z) / xc               # nose uphill
    Nd_dn = M * g * (c * (xc - X) + s * Z) / xc
    rw = 0.159; resist = M * g * s + 2 * 0.06 * 300 * 0.165 / rw + 2 * 0.06 * 200 * 0.13 / 0.13
    return dict(bin_kg=kg, hang_tilt_deg=tilt_deg, M=round(M, 1), cg_x=round(X, 3), cg_z=round(Z, 3),
                tip_lateral_deg=round(tip_side(0, yd, xc, yc), 1), tip_lateral_drive_track_only_deg=round(math.degrees(math.atan(yd / Z)), 1),
                tip_forward_over_castors_deg=round(math.degrees(math.atan((xc - X) / Z)), 1),
                castor_liftoff_about_drive_axle_deg=round(math.degrees(math.atan(X / Z)), 1),
                tail_touch_pitch_deg=round(math.degrees(math.atan(gap / abs(xtail))), 1),
                rear_tip_on_tail_wheels_deg=round(math.degrees(math.atan((X - xtail) / Z)), 1),
                drive_N_flat=round(Nd), castor_N_flat=round(M * g - Nd), drive_N_12up=round(Nd_up), castor_N_12up=round(M * g * c - Nd_up),
                castor_N_12dn=round(M * g * c - Nd_dn), mu_req_12=round(resist / Nd_up, 3),
                torque_per_wheel_12_Nm=round(resist * rw / 2, 1), torque_x1p25=round(1.25 * resist * rw / 2, 1))
OUT['RevH_params'] = dict(note='Rev H own claim (params.combined, full 240 L): 195.5 kg, CG x 0.116 z 0.564, 166.2 kg drive / 29.5 kg nose')
OUT['RevH'] = dict(tug_kg=json.load(open(os.path.join(H, 'mass_revH.json')))['total'],
                   cases=[revh(110, 0.0), revh(110, 11.3), revh(60, 0.0), revh(60, 11.3), revh(0, 0.0)])

# ---------------------------------------------------------------- comb / lip
def lip(F, comb_w, recv_w, a=0.026, t=0.008):
    w = min(comb_w, recv_w)
    return dict(F_N=round(F), comb_mm=round(comb_w * 1000), receiver_mm=round(recv_w * 1000), coverage_pct=round(100 * w / recv_w),
                line_load_N_per_mm=round(F / (w * 1000), 2), bearing_MPa=round(F / (w * 1000 * t * 1000), 2),
                ledge_bending_MPa=round(6 * F * a / (w * t * t) / 1e6, 1))
OUT['lip_note'] = ('Lip section is the gate-model assumption (30 x 8 mm HDPE ledge, load at the 26 mm rim) - not measured. HDPE yield ~20-25 MPa '
                   '(Rev H statics uses the same). Ribbed real receivers are stronger; ratios between designs hold. EN 840-5 4.5 test load '
                   '0.4 kg/dm3 x V (96 kg for 240 L, net); GGAWB AR 03/2025 s3.5: whole receiving section supported over its full width.')
OUT['lip_inputs'] = json.load(open(os.path.join(H, 'res', 'lip_inputs.json'))) if os.path.exists(os.path.join(H, 'res', 'lip_inputs.json')) else {}
L = OUT['lip_inputs']
rows = {}
for name, F, cw, rw_ in (('B1 160 mm comb, ESE 240 SL full, static carry', L.get('B1_static', 1578), 0.160, 0.580),
                         ('B1 160 mm comb, ESE 240 SL full, peak carry (G3/G5 runs)', L.get('B1_peak', 2500), 0.160, 0.580),
                         ('B1 160 mm comb, Weber 140 full, static', L.get('B1_static_140', 986), 0.160, 0.480),
                         ('B1-FW 640 mm comb, ESE 240 SL full, static carry', L.get('FW_static', 1485), 0.640, 0.580),
                         ('B1-FW 640 mm comb, ESE 240 SL full, peak carry', L.get('FW_peak', 2500), 0.640, 0.580),
                         ('Rev H 600 mm comb on the FRONT rim, Weber 140 full, static', L.get('H_static_140', 611), 0.600, 0.480),
                         ('Rev H 600 mm comb on the FRONT rim, ESE 240 full (pad variant), static', L.get('H_static_240', 1300), 0.600, 0.580),
                         ('Rev H own claim (statics.json): 110 kg on 390 mm x 10 mm', 110 * g, 0.390, 0.390)):
    rows[name] = lip(F, cw, rw_)
OUT['lip'] = rows
json.dump(OUT, open(os.path.join(H, 'res', 'handcalc_cmp.json'), 'w'), indent=1)
if __name__ == '__main__':
    for c_ in OUT['RevH']['cases']: print('RevH', c_)
    for k, v in rows.items(): print(k, v)
