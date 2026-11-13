#!/usr/bin/env python3
"""Rev H lane mission estimate on the project's real lane profile (sitl/data/route.json, 635 m, EU-DEM heights).
Writes ../results/mission.json.

Kinematic and energy bookkeeping only: time = distance / speed + fixed manoeuvre times; energy = traction against grade and
rolling resistance through one efficiency, plus hotel load. It is NOT an ArduPilot SITL run. The Rev G columns are read from the
project's own SITL result files (numbers copied below with their source), so the comparison is estimate-vs-SITL, not like-for-like.
"""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import params as P
G = P.G; R = P.ROBOT
OUT = os.path.join(HERE, '..', 'results'); os.makedirs(OUT, exist_ok=True)
route = json.load(open(os.path.join(HERE, '..', 'data', 'route.json')))
S = np.array(route['s']); Z = np.array(route['elev']['eudem25m']); L = float(S[-1])

# ------------------------------------------------------------------------------------------------ assumptions
A = dict(
    yard_len=25.0, junction_len=24.0, slow_v=0.4,          # slow zones at both ends (yard, and from the junction wait point to the pad)
    home_s=10.0, pad_from_end=15.0,                        # home slots ~10 m from the dock; drop pad ~15 m inside the lane end (project layout: 11-20 m)
    hotel_w=9.0, lights_w=17.0,                            # awake electronics (project figure) + night lights (2 head 4.8, markers 1, beacon 8, IR 3)
    eta=P.DRIVE['eta'], crr=P.DRIVE['crr'],
    lift_w=50.0,
    time_allowance=1.05,                                   # +5 % for obstacle holds and re-plans
    # fixed manoeuvre times (s)
    undock=10, to_home=25, dock_on_bin=25, lift=30, warn=3, junction_wait=10, pivot=8, reverse_place=10, set_down=26, pull_away=5,
    photo=3, dock_charge=35, seek=15,
    usable_frac_plan=0.50, usable_frac_max=0.80, batt_nominal_wh=2 * 12 * 18, rate_factor=0.85, cold_factor=0.85,
)
# Rev G figures from the project's SITL result files (seed 7): sitl/out/s1n_night_drop, sitl/out/s20a_three_bin_drop,
# sitl/out/G4/s20a_three_bin_drop, revG/RESULTS_G3_sitl.md
REVG_SITL = dict(one_bin_drop_min=2787.9 / 60, one_bin_drop_wh=42.6, three_bin_drop_G3_min=7601.8 / 60, three_bin_drop_G3_wh=107.1,
                 three_bin_drop_G4_min=8954.9 / 60, three_bin_drop_G4_wh=163.0, three_bin_pickup_G3_min=101.0, three_bin_pickup_G3_wh=82.7,
                 cruise=0.5, placement_error_m='0.45-0.65', placement_yaw_deg='11-17')


def leg(s0, s1, mass, v_cruise, night=True):
    """Drive from station s0 to s1 (m from the house). Returns (seconds, Wh)."""
    n = max(2, int(abs(s1 - s0) / 1.0)); ss = np.linspace(s0, s1, n); zz = np.interp(ss, S, Z)
    t = 0.0; e = 0.0
    for i in range(n - 1):
        ds = abs(ss[i + 1] - ss[i]);
        if ds < 1e-9: continue
        grade = (zz[i + 1] - zz[i]) / ds                    # along the direction of travel
        sm = 0.5 * (ss[i] + ss[i + 1])
        v = A['slow_v'] if (sm < A['yard_len'] or sm > L - A['junction_len']) else v_cruise
        dt = ds / v
        F = mass * G * (A['crr'] + grade)
        p = max(0.0, F * v) / A['eta'] + A['hotel_w'] + (A['lights_w'] if night else 0.0)
        t += dt; e += p * dt / 3600.0
    return t, e


def fixed(seconds, night=True, extra_w=0.0):
    return seconds, (A['hotel_w'] + (A['lights_w'] if night else 0.0) + extra_w) * seconds / 3600.0


def trip(kind, binkey, v_cruise, night=True):
    """One bin: 'drop' (full bin down, unladen up) or 'pickup' (unladen down, empty bin up). Starts and ends on the dock."""
    m_r = P.robot_mass()['m']; b = P.BINS[binkey]
    m_full = m_r + b['empty'] + b['fill_full']; m_empty = m_r + b['empty']
    pad_s = L - A['pad_from_end']; home = A['home_s']
    steps = []
    def add(name, te): steps.append((name, te[0], te[1]))
    if kind == 'drop':
        add('undock + to home slot', fixed(A['undock'] + A['to_home'], night))
        add('pivot, reverse onto bin, square', fixed(A['pivot'] + A['dock_on_bin'], night))
        add('lift + pre-motion warning', fixed(A['lift'] + A['warn'], night, A['lift_w']))
        add('carry full bin down', leg(home, L - A['junction_len'], m_full, v_cruise, night))
        add('junction wait check', fixed(A['junction_wait'], night))
        add('to pad', leg(L - A['junction_len'], pad_s, m_full, v_cruise, night))
        add('pivot 180, reverse to slot', fixed(A['pivot'] + A['reverse_place'], night))
        add('set down, pull away, photo', fixed(A['set_down'] + A['pull_away'] + A['photo'], night, A['lift_w']))
        add('return unladen', leg(pad_s, 4.0, m_r, v_cruise, night))
        add('dock + charge check', fixed(A['dock_charge'], night))
    else:
        add('undock', fixed(A['undock'], night))
        add('drive down unladen', leg(4.0, L - A['junction_len'], m_r, v_cruise, night))
        add('junction wait check', fixed(A['junction_wait'], night))
        add('to pad, find bin', leg(L - A['junction_len'], pad_s, m_r, v_cruise, night))
        add('identify + pivot + reverse onto bin', fixed(A['seek'] + A['pivot'] + A['dock_on_bin'], night))
        add('lift + pre-motion warning', fixed(A['lift'] + A['warn'], night, A['lift_w']))
        add('carry empty bin up', leg(pad_s, home, m_empty, v_cruise, night))
        add('pivot, reverse to home slot, set down', fixed(A['pivot'] + A['reverse_place'] + A['set_down'] + A['pull_away'], night, A['lift_w']))
        add('dock + charge check', fixed(A['to_home'] + A['dock_charge'], night))
    t = sum(s[1] for s in steps) * A['time_allowance']; e = sum(s[2] for s in steps) * A['time_allowance']
    return dict(kind=kind, bin=b['name'], v_cruise=v_cruise, minutes=round(t / 60, 1), wh=round(e, 1),
                steps=[dict(step=n, s=round(tt), wh=round(ee, 2)) for n, tt, ee in steps])


def evenings():
    out = []
    bins3 = ['ESE240SL', 'SULO240', 'ESE140CL']            # black 240, green 240, brown 140
    usable_plan = A['batt_nominal_wh'] * A['rate_factor'] * A['cold_factor'] * A['usable_frac_plan']
    usable_max = A['batt_nominal_wh'] * A['rate_factor'] * A['cold_factor'] * A['usable_frac_max']
    for v in (0.5, 0.8):
        for nb in (1, 2, 3):
            for kind in ('drop', 'pickup'):
                trips = [trip(kind, bins3[i], v) for i in range(nb)]
                tm = sum(t['minutes'] for t in trips); wh = sum(t['wh'] for t in trips)
                row = dict(v_cruise=v, bins=nb, kind=kind, minutes=round(tm, 1), wh=round(wh, 1),
                           battery_plan_wh=round(usable_plan), battery_max_wh=round(usable_max), within_plan=bool(wh <= usable_plan))
                if kind == 'pickup':
                    row['finish_clock_if_start_1800'] = '%02d:%02d' % (18 + int(tm // 60), int(tm % 60))
                    row['margin_to_2100_min'] = round(180 - tm, 1)
                else:
                    row['finish_clock_if_start_1800'] = '%02d:%02d' % (18 + int(tm // 60), int(tm % 60))
                out.append(row)
    return out, trip('drop', 'ESE240SL', 0.5), trip('pickup', 'ESE240SL', 0.5)


def placement(n=100000, seed=7):
    """Where the bin ends up relative to its programmed slot when it is set down. Rigid carry: bin error = robot pose error."""
    rng = np.random.default_rng(seed); out = {}
    lever = R['mast_x'] - (R['pad_x'] - 0.345)              # RTK antenna (mast top) to the bin centre
    for name, sxy, shd in (('RTK fixed (25 mm, 1.5 deg)', 0.025, 1.5), ('RTK fixed, poor heading (25 mm, 4 deg)', 0.025, 4.0), ('RTK float (0.25 m, 2 deg)', 0.25, 2.0)):
        ex = rng.normal(0, sxy, n); ey = rng.normal(0, sxy, n); hd = np.radians(rng.normal(0, shd, n))
        bx = ex + lever * (np.cos(hd) - 1); by = ey + lever * np.sin(hd)
        r = np.hypot(bx, by)
        out[name] = dict(p50_mm=round(float(np.percentile(r, 50)) * 1000), p95_mm=round(float(np.percentile(r, 95)) * 1000),
                         p999_mm=round(float(np.percentile(r, 99.9)) * 1000), yaw_p95_deg=round(float(np.percentile(np.abs(np.degrees(hd)), 95)), 1),
                         over_0p6m_pct=round(100 * float(np.mean(r > 0.6)), 4))
    return dict(cases=out, lever_m=round(lever, 3), revg_g4_sitl='0.45-0.65 m and 11-17 deg off (sitl/out/G4/report/open_issues.md, PROGRESS.md)',
                rule='Set down only on RTK fixed; on float, hold 20 s for a fix, else use the pad tag or alert.')


def turning():
    """Space needed to turn round. Rev G: steady-state turn of a tractor with the hitch on its axle, hitch angle capped (kinematics only).
    Rev H: pivot about the drive-axle centre."""
    out = {}
    for name, Lt in (('Rev G, CAD hitch length 0.67 m', 0.67), ('Rev G, SITL trailer length 1.35 m', 1.35)):
        for cap in (28.0, 60.0):
            Rr = Lt / math.sin(math.radians(cap))                   # radius of the tug axle centre
            half_w, front = 0.38, 0.762 + 0.195                     # tug body half width (world.py); front overhang incl. the +195 mm CAD correction
            r_out = math.hypot(Rr + half_w, front)                  # radius swept by the tug's outer front corner
            width = (Rr + half_w) + r_out                           # 180 deg turn: outer side on entry + the corner's furthest reach
            out['%s, hitch cap %.0f deg' % (name, cap)] = dict(tug_axle_radius_m=round(Rr, 2), outer_swept_radius_m=round(r_out, 2),
                                                               u_turn_width_m=round(width, 2), fits_3p6m_lane=bool(width <= 3.6 - 0.2))
    # Rev H2: pivot about the drive-axle centre. Swept radius = the furthest of: chamfered nose corners, rail tips, drive wheels,
    # and the swivel circle of each nose castor (swivel axis 55 mm ahead of the wheel centre, reach = trail + wheel radius).
    ch = R.get('nose_chamfer', 0.0); hw_frame = R['leg_inner_gap'] / 2 + 0.05
    pts = [(R['nose_tip_x'], hw_frame - ch), (R['nose_tip_x'] - ch, hw_frame), (R['leg_tip_x'], R['funnel_mouth'] / 2 + 0.05), (R['drive_r'], R['width'] / 2)]
    r_frame = max(math.hypot(x, y) for x, y in pts)
    r_castor = math.hypot(R['nose_x'] + 0.055, R['nose_track'] / 2) + 0.055 + R['nose_r']
    rp = max(r_frame, r_castor); D = 2 * rp
    out['Rev H2 pivot'] = dict(swept_radius_m=round(rp, 2), u_turn_width_m=round(D, 2), set_by='castor swivel circle' if r_castor >= r_frame else 'frame corner',
                               frame_only_m=round(2 * r_frame, 2), fits_3p6m_lane=bool(D <= 3.6 - 0.2), free_side_margin_in_3p6m_lane_m=round((3.6 - D) / 2, 2),
                               fits_2p9m_narrowing=bool(D <= 2.9), margin_at_2p9m_narrowing_m=round((2.9 - D) / 2, 2))
    out['reference_other_agent_lanefit'] = dict(note='cmp/lanefit.py with truth hedge faces (2.9 m face to face at s 500-516). Pivot diameters, empty / loaded: Rev H 2.16 / 2.16, '
                                                     'B1 2.36 / 2.42, B2 2.28 / 2.39; all three pass every station and all 12 pad sequences. Rev H2 lies between Rev H and B2. '
                                                     'RE-RUN lanefit.py with reference/RevH2_lanefit_design.json before relying on this.')
    return out


def car_on_home_slot():
    """s24a geometry: a 4.5 x 1.8 m car is parked over the home slot. The bin goes to an alternate slot beside it.
    Rev H needs a clear patch for: pivot circle + 1.5 m straight reverse into the slot."""
    rp = turning()['Rev H2 pivot']['swept_radius_m']
    need_len = rp + 1.5 + 0.8; need_wid = 2 * rp
    return dict(rev_h_clear_patch_m=dict(length=round(need_len, 2), width=round(need_wid, 2)),
                closest_approach_to_car_m=0.5, note='Pivot centre is kept >= swept radius + 0.5 m from any lidar return; no swept arc crosses the slot row. '
                'Rev G needed a U-turn through the slot row (tug axle radius 1.43 m at the 28 deg CAD cap) and struck the car (open_issues.md).')


if __name__ == '__main__':
    ev, d1, p1 = evenings()
    res = dict(lane_m=round(L, 1), assumptions=A, revg_sitl=REVG_SITL, evenings=ev, one_bin_drop_detail=d1, one_bin_pickup_detail=p1,
               placement=placement(), turning=turning(), car_on_home_slot=car_on_home_slot(),
               note='Estimate, not SITL. Speeds: slow zones 0.4 m/s in the yard and from the junction wait point to the pad.')
    json.dump(res, open(os.path.join(OUT, 'mission.json'), 'w'), indent=1)
    print('lane %.0f m' % L)
    for r in ev: print('  v=%.1f bins=%d %-6s %6.1f min %6.1f Wh  finish %s %s plan-batt %s' % (r['v_cruise'], r['bins'], r['kind'], r['minutes'], r['wh'], r['finish_clock_if_start_1800'],
                                                                                                ('margin %.0f min' % r['margin_to_2100_min']) if 'margin_to_2100_min' in r else '', r['within_plan']))
    for s in d1['steps']: print('    drop  %-36s %5d s %6.2f Wh' % (s['step'], s['s'], s['wh']))
    for s in p1['steps']: print('    pick  %-36s %5d s %6.2f Wh' % (s['step'], s['s'], s['wh']))
    print(json.dumps(res['placement'], indent=1)); print(json.dumps(res['turning'], indent=1)); print(res['car_on_home_slot'])
