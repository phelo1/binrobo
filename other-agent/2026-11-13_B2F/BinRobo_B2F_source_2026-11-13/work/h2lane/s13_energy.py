#!/usr/bin/env python3
"""S13 energy and heat: three-bin evening at 0 C on the lane profile, three packs (Rev H2 new AGM 2x18 Ah, Rev H2 donor AGM pair,
B2-F 24 V 20 Ah LFP); motor current on the 12 % grade against the controller's continuous rating.
Sources: carrier SITL s20a / s20b (air 0.5 C, night, cold rolling factor 1.15, lights) = drive + hotel + lift energy of the
three-bin drop and pickup evenings; an independent cross-check on sitl/data/route.json (EU-DEM 25 m) with the mission.py
leg model; mass scaling for the heavier donor pack. Output res/s13_energy.json."""
import json, math, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.abspath(os.path.join(H, '..', '..'))
G = 9.81
def sitl(d, s): return json.load(open(os.path.join(H, 'sitl_out', '%s__%s.json' % (d, s))))
route = json.load(open(os.path.join(P, 'sitl', 'data', 'route.json'))); S_ = np.array(route['s']); Z = np.array(route['elev']['eudem25m']); L = float(S_[-1])
def lfp_cold(t): return float(np.interp(t, [-20, -10, 0, 10, 25], [0.60, 0.75, 0.88, 0.95, 1.0]))   # sitl scene.pack_cold_factor (assumed)
PACKS = {
 'RevH2 new AGM 2x12V 18Ah': dict(design='RevH2', robot_kg=91.0, V=24.0, Ah=18.0, chem='AGM', cold=0.85, rate=0.85, plan=0.50, maxdod=0.80, age=1.0),
 'RevH2 donor AGM pair (40 Ah assumed, 80 % health)': dict(design='RevH2', robot_kg=102.2, V=24.0, Ah=40.0, chem='AGM', cold=0.85, rate=0.85, plan=0.50, maxdod=0.80, age=0.80),
 'B2-F LFP 24V 20Ah (8S, 25.6 V)': dict(design='B2F', robot_kg=92.3, V=25.6, Ah=20.0, chem='LFP', cold=lfp_cold(0.0), rate=1.0, plan=0.80, maxdod=0.90, age=1.0),
}
SITL_MASS = {'RevH2': 91.0, 'B2F': 92.3}
def leg_wh(s0, s1, m, v=0.5, crr=0.03 * 1.15, eta=0.60, hotel=9 + 17):
    n = max(2, int(abs(s1 - s0))); ss = np.linspace(s0, s1, n); zz = np.interp(ss, S_, Z); e = 0.0; t = 0.0
    for i in range(n - 1):
        ds = abs(ss[i + 1] - ss[i]); g = (zz[i + 1] - zz[i]) / ds; vv = 0.4 if (ss[i] < 25 or ss[i] > L - 24) else v
        p = max(0.0, m * G * (crr + g) * vv) / eta + hotel; e += p * ds / vv / 3600; t += ds / vv
    return e, t
out = dict(note='three-bin evening = s20a (3 drops) on collection eve and s20b (3 pickups) the next evening; each from a full charge unless stated', packs={})
for name, pk in PACKS.items():
    d = pk['design']; a = sitl(d, 's20a_three_bin_drop'); b = sitl(d, 's20b_three_bin_pickup')
    f_drop = (pk['robot_kg'] + 27.5) / (SITL_MASS[d] + 27.5); f_pick = (pk['robot_kg'] + 6.5) / (SITL_MASS[d] + 6.5)   # mean carried mass over the trip
    def scale(R, f): return R['E']['drive_wh'] * f + R['E']['hotel_wh'] + R['E']['lift_wh']
    e_drop = scale(a, f_drop); e_pick = scale(b, f_pick)
    nom = pk['V'] * pk['Ah']; usable_plan = nom * pk['cold'] * pk['rate'] * pk['age'] * pk['plan']; usable_max = nom * pk['cold'] * pk['rate'] * pk['age'] * pk['maxdod']
    # cross-check on the route profile: 3 trips loaded down (55 kg) + empty up (drop); empty down + 13 kg up (pickup)
    m = pk['robot_kg']; xd = sum(leg_wh(10, L - 15, m + 55)[0] + leg_wh(L - 15, 4, m)[0] for _ in range(3))
    xp = sum(leg_wh(4, L - 15, m)[0] + leg_wh(L - 15, 10, m + 13)[0] for _ in range(3))
    out['packs'][name] = dict(design=d, robot_kg=m, nominal_wh=round(nom), usable_plan_wh_0C=round(usable_plan), usable_max_wh_0C=round(usable_max),
        drop_evening_wh=round(e_drop, 1), pickup_evening_wh=round(e_pick, 1), drop_min=a['sim_min'], pickup_min=b['sim_min'],
        drop_within_plan=bool(e_drop <= usable_plan), pickup_within_plan=bool(e_pick <= usable_plan),
        both_evenings_no_recharge_wh=round(e_drop + e_pick, 1), both_within_max=bool(e_drop + e_pick <= usable_max),
        route_crosscheck_drop_wh_driving_only=round(xd, 1), route_crosscheck_pickup_wh_driving_only=round(xp, 1),
        charge_note=('LFP: no charging below 0 C cell temperature; needs the dock pack heater (G4) for an overnight recharge at 0 C' if pk['chem'] == 'LFP' else
                     'AGM: charges at 0 C with temperature compensation (slower); 50 % DoD planning limit for cycle life'))
# ---------------------------------------------------------------- motor current on the 12 % grade
CUR = []
CASES = [('Rev H2 new AGM', 91.0, 0.159, 1.0, 1.5, 'RoboClaw 2x30A', 30.0, 60.0),
         ('Rev H2 donor AGM', 102.2, 0.159, 1.0, 1.5, 'RoboClaw 2x30A', 30.0, 60.0),
         ('B2-F new drive LFP', 92.3, 0.165, 52.7 / 25.8, 52.7 / 25.8, 'RoboClaw 2x30A', 30.0, 60.0),
         ('B2-F donor (+2:1 chain)', 105.5, 0.159, 2.0, 3.0, 'RoboClaw 2x30A', 30.0, 60.0)]
for lab, mr, rw, kt, ktp, ctrl, icont, ipk in CASES:
    for bin_kg, bl in ((110.0, 'full 240 L at the EN 840 rating, 110 kg'), (55.0, 'SITL full bin 55 kg')):
        m = mr + bin_kg; th = math.atan(0.12); crr = 0.03 * 1.15
        F = m * G * (crr * math.cos(th) + math.sin(th)); T = F * rw / 2; Fa = F + m * 0.25; Ta = Fa * rw / 2
        CUR.append(dict(case=lab, load=bl, mass_kg=round(m, 1), wheel_torque_Nm=round(T, 1), motor_A_cont=round(T / kt, 1), motor_A_cont_phys=round(T / ktp, 1),
                        motor_A_start_0p25g=round(Ta / kt, 1), controller=ctrl, ctrl_cont_A=icont, ctrl_peak_A=ipk,
                        under_cont=bool(T / kt < icont), margin_A=round(icont - T / kt, 1), batt_A=round(2 * F * 0.5 / 0.6 / 24.0, 1)))
out['current_12pct'] = CUR
out['kt_note'] = ('wheel-referred torque per motor amp. Rev H2 donor: 1.0 N m/A is implied by params.py (t_lim 60 N m at the 60 A RoboClaw '
                  'peak; t_lim_hi 80 N m at the 80 A MDDS30 peak) - conservative; 1.5 N m/A from the 24 V / 1.67 m/s back-EMF and a 0.65 gearbox efficiency. '
                  'B2 new drive: 53 N m at 25.8 A (DESIGN_B2, PEWM82M + 3.5:1). B2 donor + 2:1 chain: 2x the donor value. Donor motors are unmeasured (test B5).')
out['lane_grade_note'] = 'Real lane (EU-DEM 25 m): steepest 7.9 % over 10 m at s 145; SRTM 30 m shows 12 % over 25 m at s 55. 12 % is the project design case.'
json.dump(out, open(os.path.join(H, 'res', 's13_energy.json'), 'w'), indent=1)
for k, v in out['packs'].items(): print(k, v)
for c in CUR: print(c)
