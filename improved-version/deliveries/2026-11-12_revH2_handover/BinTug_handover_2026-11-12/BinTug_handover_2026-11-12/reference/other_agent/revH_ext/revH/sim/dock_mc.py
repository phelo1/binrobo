#!/usr/bin/env python3
"""Rev H docking and lift engagement: tolerance Monte Carlo over the seven data-sheet bins. Writes ../results/dock_mc.json.

THIS IS A TOLERANCE STACK, NOT CONTACT PHYSICS. It answers: with the approach and perception errors the Rev G study
already assumed, how often does the bin end up inside the mechanical capture envelope of the Rev H carriage, on the
first approach and after one re-approach? The numbers are only as good as the error assumptions listed in ASSUME.
The physical check is cheap: lift Brian's real bins by the lip with a plywood/steel mock-up of the comb.
"""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import params as P
R = P.ROBOT
OUT = os.path.join(HERE, '..', 'results'); os.makedirs(OUT, exist_ok=True)

ASSUME = dict(
    raw_lateral_mm=80.0, raw_yaw_deg=6.0,          # uniform +/-, at 1.5 m out: same raw errors as the G5 screen
    steer_res_mm=5.0, steer_res_deg=0.5,           # steering residual (1 sigma)
    engaged_len_m=0.63,                            # pad face to the bin's wheel axle: lever for yaw -> sideways sweep at the wheels
    guide_tol_mm=10.0,                             # a brush of this much on the UHMW guide strips slides without stopping
    retry_gain=0.7,                                # second look is taken from 0.8 m instead of 1.5 m: errors scale by this
    comb_tol_mm=5.0,                               # data-sheet comb height tolerance (1 sigma 2.5 mm)
    ground_step_mm=25.0,                           # bin standing higher/lower than the robot's wheels, uniform +/-
    bin_roll_deg=2.0,                              # uneven ground under the bin, uniform +/-
    min_lift_mm=60.0,                              # carry height that still clears the test obstacles
    blade_wall_tol_mm=7.0,                         # blade may sit this far off its nominal distance from the bin wall and still enter the lip channel
    wall_follow_sigma_mm=2.0,                      # sprung face under the blade follows the wall
    pad_switch_force_N=6.0,                        # total force to close both squaring switches
    body_halfwidth_frac=0.44,                      # bin body half-width at rail height as a fraction of W (tapered body)
)
CASES = {
    'baseline (camera 8 mm, 1.0 deg)':            dict(s_lat=8.0, s_yaw=1.0, side_sensors=False),
    'stress (camera 20 mm, 2.5 deg)':             dict(s_lat=20.0, s_yaw=2.5, side_sensors=False),
    'stress + leg-tip gap sensors (4 mm)':        dict(s_lat=20.0, s_yaw=2.5, side_sensors=True),
}


def run_bin(key, case, n, rng):
    b = P.BINS[key]; A = ASSUME; c = CASES[case]
    half_gap = R['leg_inner_gap'] / 2
    clear_wheels = half_gap - b['track'] / 2                      # free clearance at the bin wheels (the tightest point)
    clear_body = half_gap - A['body_halfwidth_frac'] * b['W']
    mouth = R['funnel_mouth'] / 2 - A['body_halfwidth_frac'] * b['W']

    def look(scale):
        s_lat = c['s_lat'] * scale; s_yaw = c['s_yaw'] * scale
        e = rng.normal(0, math.hypot(s_lat, A['steer_res_mm']), n) / 1000.0
        psi = np.radians(rng.normal(0, math.hypot(s_yaw, A['steer_res_deg']), n))
        if c['side_sensors']:                                     # gaps measured at the leg tips as the bin enters: lateral closed-loop to 4 mm,
            e = rng.normal(0, math.hypot(4.0, A['steer_res_mm']), n) / 1000.0     # yaw from two readings 0.30 m apart
            psi = np.radians(rng.normal(0, math.hypot(math.degrees(math.atan(4.0 * math.sqrt(2) / 300.0)), A['steer_res_deg']), n))
        return e, psi

    def lateral_ok(e, psi):
        sweep = np.abs(e) + A['engaged_len_m'] * np.tan(np.abs(psi))
        free = sweep <= clear_wheels
        guided = (~free) & (sweep <= clear_wheels + A['guide_tol_mm'] / 1000.0)
        in_mouth = np.abs(e) + 0.05 * np.abs(psi) <= mouth
        return free & in_mouth, guided & in_mouth, sweep

    # ---- vertical / fore-aft engagement (independent of the lateral result)
    comb = (b['comb'] if b['comb'] else rng.uniform(*P.COMB_UNKNOWN_BAND, n)) + rng.normal(0, A['comb_tol_mm'] / 2000.0, n)
    comb = comb + rng.uniform(-A['ground_step_mm'], A['ground_step_mm'], n) / 1000.0
    roll = np.radians(rng.uniform(-A['bin_roll_deg'], A['bin_roll_deg'], n))
    lip_lo = comb - 0.20 * np.tan(np.abs(roll)); lip_hi = comb + 0.20 * np.tan(np.abs(roll))    # lip height at the two switches (y = +/-0.20)
    reach = (lip_lo >= R['comb_z_min']) & (lip_hi <= R['comb_z_max'])
    lift_avail = R['comb_z_max'] - lip_hi
    lift_ok = lift_avail >= A['min_lift_mm'] / 1000.0
    blade_ok = np.abs(rng.normal(0, A['wall_follow_sigma_mm'], n)) <= A['blade_wall_tol_mm']
    vertical = reach & lift_ok & blade_ok
    # ---- empty bin pushed over by the squaring switches? (force at lip height vs tipping an empty bin about its wheels)
    tip_force = b['empty'] * P.G * 0.30 / comb                    # N at lip height to start tipping an empty bin backwards
    push_margin = float(np.min(tip_force) / A['pad_switch_force_N'])

    e1, p1 = look(1.0); free1, guided1, sw1 = lateral_ok(e1, p1)
    first = (free1 | guided1) & vertical
    e2, p2 = look(A['retry_gain']); free2, guided2, sw2 = lateral_ok(e2, p2)
    second = (~first) & (free2 | guided2) & vertical
    miss = ~(first | second)
    reasons = dict(lateral=int(np.sum(miss & vertical)), lip_out_of_travel=int(np.sum(miss & ~reach)),
                   lift_short=int(np.sum(miss & reach & ~lift_ok)), blade_missed_channel=int(np.sum(miss & reach & lift_ok & ~blade_ok)))
    return dict(bin=b['name'], n=n, clear_wheels_mm=round(clear_wheels * 1000, 1), clear_body_mm=round(clear_body * 1000, 1),
                first_try_pct=round(100 * float(np.mean(first)), 2), guide_contact_pct=round(100 * float(np.mean(guided1 & vertical)), 2),
                with_one_retry_pct=round(100 * float(np.mean(first | second)), 3), safe_miss_pct=round(100 * float(np.mean(miss)), 3),
                miss_reasons=reasons, sweep_p95_mm=round(float(np.percentile(sw1, 95)) * 1000, 1),
                lift_available_min_mm=round(float(np.min(lift_avail)) * 1000), empty_bin_push_margin=round(push_margin, 1))


def envelope():
    """Deterministic capture envelope per bin (no statistics)."""
    rows = []
    for key, b in P.BINS.items():
        half_gap = R['leg_inner_gap'] / 2
        cw = half_gap - b['track'] / 2
        comb = b['comb'] if b['comb'] else P.COMB_UNKNOWN_BAND[1]
        rows.append(dict(bin=b['name'], lateral_at_wheels_mm=round(cw * 1000), yaw_alone_deg=round(math.degrees(math.atan(cw / ASSUME['engaged_len_m'])), 1),
                         mouth_capture_mm=round((R['funnel_mouth'] / 2 - ASSUME['body_halfwidth_frac'] * b['W']) * 1000),
                         comb_mm=round(comb * 1000), travel_below_mm=round((comb - R['comb_z_min']) * 1000), lift_reserve_mm=round((R['comb_z_max'] - comb) * 1000),
                         comb_cover_pct=round(100 * min(1.0, R['comb_width'] / b['W']))))
    return rows


if __name__ == '__main__':
    n = 20000; rng = np.random.default_rng(20261111)
    res = dict(assumptions=ASSUME, cases={}, envelope=envelope(), n_per_bin=n,
               note='Tolerance Monte Carlo, not contact physics. "Safe miss" = robot backs out and alerts; nothing is lifted, nothing tips.')
    for case in CASES:
        rows = [run_bin(k, case, n, rng) for k in P.BINS]
        tot_first = np.mean([r['first_try_pct'] for r in rows]); tot_retry = np.mean([r['with_one_retry_pct'] for r in rows])
        res['cases'][case] = dict(rows=rows, mean_first_try_pct=round(float(tot_first), 2), mean_with_retry_pct=round(float(tot_retry), 3))
        print('==', case, '| mean first try %.2f %%, with one retry %.3f %%' % (tot_first, tot_retry))
        for r in rows: print('   %-30s clear %5.1f mm  first %6.2f %%  (guide %5.2f %%)  retry-> %7.3f %%  miss %s  lift>= %d mm' % (
            r['bin'], r['clear_wheels_mm'], r['first_try_pct'], r['guide_contact_pct'], r['with_one_retry_pct'], r['miss_reasons'], r['lift_available_min_mm']))
    for r in res['envelope']: print('  env', r)
    json.dump(res, open(os.path.join(OUT, 'dock_mc.json'), 'w'), indent=1)
