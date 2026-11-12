#!/usr/bin/env python3
"""Rev H hand calculations in code: lift force, structure, stability, drive demand. Writes ../results/statics.json.
Every result is a first-order estimate with the stated assumptions; nothing here replaces a load test."""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import params as P
G = P.G; R = P.ROBOT
OUT = os.path.join(HERE, '..', 'results'); os.makedirs(OUT, exist_ok=True)


def rhs(b, h, t):
    """Second moment (about the axis bending the h dimension), section modulus and mass per metre of a rectangular hollow section (mm)."""
    I = (b * h ** 3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12.0
    A = b * h - (b - 2 * t) * (h - 2 * t)
    return dict(I=I, Z=I / (h / 2.0), A=A, kg_m=A * 7.85e-3)


def lift():
    rows = []
    for key, b in P.BINS.items():
        c = P.bin_cg(b, 1.0); W = c['m'] * G
        e = c['xf'] + (R['mast_x'] - R['pad_x'])                  # bin CG to the mast guide axis
        M = W * e                                                  # moment the carriage puts into the mast
        H = W * c['xf'] / R['pad_drop']                            # comb pull = pad push
        roll_sp = 0.30                                             # vertical spacing of the carriage rollers
        Rr = M / roll_sp
        f_roll = 2 * Rr * 0.03; f_slide = 2 * Rr * 0.20
        carriage = 4.5 * G
        comb = b['comb'] if b['comb'] else sum(P.COMB_UNKNOWN_BAND) / 2
        rows.append(dict(bin=b['name'], gross_kg=round(c['m'], 1), comb_mm=round(comb * 1000),
                         carriage_travel_needed_mm=round((comb + R['lift'] - R['comb_z_min']) * 1000),
                         mast_moment_Nm=round(M), comb_pull_N=round(H), roller_reaction_N=round(Rr),
                         lift_force_rollers_N=round(W + carriage + f_roll), lift_force_slides_N=round(W + carriage + f_slide),
                         actuator_margin_rollers=round(4000 / (W + carriage + f_roll), 2), actuator_margin_rollers_3kN=round(3000 / (W + carriage + f_roll), 2), actuator_margin_slides=round(4000 / (W + carriage + f_slide), 2)))
    stroke = dict(stroke_mm=400, comb_z_min_mm=round(R['comb_z_min'] * 1000), comb_z_max_mm=round(R['comb_z_max'] * 1000),
                  bins_comb_range_mm=[938, 1030], en840_band_mm=[round(v * 1000) for v in P.EN840_COMB_BAND],
                  start_below_lowest_mm=round((P.EN840_COMB_BAND[0] - R['comb_z_min']) * 1000),
                  top_reserve_above_highest_plus_lift_mm=round((R['comb_z_max'] - (P.EN840_COMB_BAND[1] + R['lift'])) * 1000),
                  lift_time_s_at_5mm_s=round(R['lift'] * 1000 / 5), full_stroke_time_s=60)
    return dict(per_bin=rows, stroke=stroke)


def structure():
    worst = max(P.bin_cg(b, 1.0)['m'] * G * (P.bin_cg(b, 1.0)['xf'] + R['mast_x'] - R['pad_x']) for b in P.BINS.values())
    out = {}
    for name, sec in (('2 x 40x40x3', rhs(40, 40, 3)), ('2 x 50x50x3 (chosen)', rhs(50, 50, 3))):
        Z = 2 * sec['Z']
        out['mast ' + name] = dict(Z_mm3=round(Z), stress_static_MPa=round(worst * 1e3 / Z, 1), stress_3g_MPa=round(3 * worst * 1e3 / Z, 1),
                                   sf_3g_S235=round(235 / (3 * worst * 1e3 / Z), 2), kg_per_m_each=round(sec['kg_m'], 2))
    # side rail: simply supported between the drive wheel (x = 0) and the nose caster, bin + mast load applied at the mast foot
    c = P.combined('ESE240SL', 1.0); drive_N = 0.5 * c['m'] * G * (1 - c['x'] / R['nose_x'])
    Mrail = drive_N * R['mast_x']
    sec = rhs(50, 50, 3)
    out['side rail 50x50x3'] = dict(drive_wheel_load_N=round(drive_N), moment_Nm=round(Mrail), stress_static_MPa=round(Mrail * 1e3 / sec['Z'], 1),
                                    stress_3g_MPa=round(3 * Mrail * 1e3 / sec['Z'], 1), sf_3g_S235=round(235 / (3 * Mrail * 1e3 / sec['Z']), 2))
    W = 110 * G
    out['comb blade on lip'] = dict(note='10 mm rounded edge bearing on 390 mm of lip (narrowest receiver assumed)',
                                    bearing_static_MPa=round(W / (390 * 10), 2), bearing_3g_MPa=round(3 * W / (390 * 10), 2), hdpe_yield_MPa='20-25')
    return out


def stability():
    rows = []
    for lab, key, fill in (('unladen', None, 0), ('empty 240 L', 'ESE240SL', 0.0), ('full 240 L', 'ESE240SL', 1.0), ('full 140 L', 'ESE140CL', 1.0)):
        c = P.combined(key, fill) if key else P.combined(None)
        tr = R['drive_track'] / 2
        lat = math.degrees(math.atan(tr / c['z']))
        row = dict(load=lab, mass_kg=round(c['m'], 1), cg_x=round(c['x'], 3), cg_z=round(c['z'], 3),
                   lateral_tip_deg=round(lat, 1), cross_slope_30pct_margin=round(math.tan(math.radians(lat)) / 0.30, 2),
                   tip_back_grade_pct=round(100 * c['x'] / c['z'], 1),
                   tip_forward_decel_g=round((R['nose_x'] - c['x']) / c['z'], 2),
                   nose_share_flat_pct=round(100 * c['x'] / R['nose_x'], 1),
                   nose_share_12pct_climb_pct=round(100 * (c['x'] - 0.12 * c['z']) / R['nose_x'], 1),
                   accel_limit_12pct_climb_ms2=round(G * (c['x'] / c['z'] - 0.12), 2))
        # side wind 25 m/s on the bin side (0.62 m2, Cd 1.2) acting at 0.65 m
        if key:
            Fw = 0.5 * 1.225 * 25 ** 2 * 0.62 * 1.2
            row['wind25_overturn_margin'] = round(c['m'] * G * tr / (Fw * 0.65), 1)
        rows.append(row)
    # bin swinging off the pad: needs the inertial force at the CG to beat gravity's moment about the comb
    c = P.bin_cg(P.BINS['ESE240SL'], 1.0)
    swing = dict(note='acceleration (nose-forward) needed to swing a hanging bin off the pad = g * xf / (comb height - CG height)',
                 accel_g=round(c['xf'] / (1.005 - c['z']), 2))
    return dict(rows=rows, bin_swing_out=swing)


def drive_demand():
    """Wheel torque and motor current. Motor constant from a 24 V / ~4300 rpm no-load chair motor, 32:1 box at 80 %."""
    kt = 24.0 / (4300 * 2 * math.pi / 60); ratio, eta = 32.0, 0.80
    rows = []
    for lab, key, fill in (('unladen', None, 0), ('empty 240 L', 'ESE240SL', 0.0), ('full 240 L', 'ESE240SL', 1.0)):
        c = P.combined(key, fill) if key else P.combined(None)
        for grade in (0.022, 0.075, 0.12):
            F = c['m'] * G * (grade + P.DRIVE['crr'])
            Tw = F * R['drive_r'] / 2
            rows.append(dict(load=lab, grade_pct=round(grade * 100, 1), force_N=round(F), wheel_torque_Nm=round(Tw, 1),
                             motor_current_A=round(Tw / (ratio * eta * kt) + 1.5, 1), mech_power_W_at_0p8=round(F * 0.8)))
    return dict(kt=round(kt, 4), ratio=ratio, eta=eta, rows=rows,
                t_lim_60Nm_equals_A=round(60 / (ratio * eta * kt), 0), t_lim_80Nm_equals_A=round(80 / (ratio * eta * kt), 0))


def bin_on_slope():
    """Does a bin set down on a slope stay put? It stands on its two (free-rolling) wheels and its front base edge."""
    out = []
    for fill, lab in ((0.0, 'empty'), (1.0, 'full')):
        b = P.BINS['ESE240SL']; c = P.bin_cg(b, fill)
        axle_from_front = 0.63                                      # wheel axle behind the front wall
        base_front = 0.10                                           # base contact edge behind the front wall (tapered front)
        share = (axle_from_front - c['xf']) / (axle_from_front - base_front)   # share of weight on the front base edge, level ground
        for grade in (0.05, 0.08, 0.12):
            for facing in ('wheels downhill', 'wheels uphill'):
                sg = 1 if facing == 'wheels downhill' else -1
                sh = share - sg * grade * c['z'] / (axle_from_front - base_front)
                mu_need = grade / max(sh, 1e-6)
                out.append(dict(fill=lab, grade_pct=round(grade * 100), facing=facing, front_edge_share=round(sh, 2), mu_needed_at_base=round(mu_need, 2),
                                holds_at_mu_0p35=bool(mu_need <= 0.35)))
    return dict(rows=out, rule='Across the slope the wheels cannot roll, so any pad steeper than about 5 % gets bins placed cross-slope or wheels-uphill.')


def step_energy():
    """Hand check of the full-width square-step results, independent of dyn.py.
    A driven wheel of radius r meets a step of height h. Its hub then moves on an arc about the step corner, from the angle
    a0 = acos((r - h) / r) (measured from the vertical) down to 0. Along the arc the tyre is pushed by friction at the corner,
    at most mu * N with N = W * cos(theta) and never more than the torque limit, and held back by W * sin(theta).
    Where friction cannot carry the weight (tan(theta) > mu) the shortfall has to come from kinetic energy.
    Kinetic energy left after the wheels strike the corner: KE' = KE / (1 + f * tan(a0)^2), f = share of the mass on the drive axle
    (the arc forces a vertical velocity on that share). Rigid tyre, no wheel spin, nose casters already up: a deliberately simple check."""
    r = R['drive_r']; rows = []
    loads = (('unladen', None, 0.0), ('empty 240 L', 'ESE240SL', 0.0), ('full 240 L (110 kg)', 'ESE240SL', 1.0), ('full 140 L (70 kg)', 'ESE140CL', 1.0))  # same labels as tests_mech.LOADS
    for lab, key, fill in loads:
        c = P.combined(key, fill) if key else P.combined(None)
        f = 1.0 - c['x'] / R['nose_x']; W = f * c['m'] * G
        for mu in (0.6, 0.45, 0.3):
            for h in (0.03, 0.04, 0.05, 0.06, 0.08):
                a0 = math.acos((r - h) / r); need = 0.0; n = 400
                for i in range(n):                                   # integrate the shortfall along the arc
                    th = a0 * (i + 0.5) / n
                    push = min(mu * W * math.cos(th), 2 * P.DRIVE['t_lim'] / r)
                    need += max(W * math.sin(th) - push, 0.0) * r * a0 / n
                for v in (0.5, 0.8):
                    ke = 0.5 * c['m'] * v * v / (1.0 + f * math.tan(a0) ** 2)
                    rows.append(dict(load=lab, mu=mu, h_mm=round(h * 1000), v=v, corner_angle_deg=round(math.degrees(a0), 1),
                                     energy_short_J=round(need, 1), kinetic_after_impact_J=round(ke, 1), passes=bool(ke >= need)))
    # nose casters: pushed up the step by the drive wheels' traction (static check)
    c = P.combined('ESE240SL', 1.0); rn = R['nose_r']; Wn = c['m'] * G * c['x'] / R['nose_x']; nose = []
    for h in (0.04, 0.05, 0.06, 0.08):
        a = math.acos((rn - h) / rn)
        nose.append(dict(h_mm=round(h * 1000), push_needed_N=round(Wn * math.tan(a)), push_available_N_at_60Nm=round(2 * P.DRIVE['t_lim'] / r)))
    return dict(rows=rows, nose_casters_full_240L=nose)


if __name__ == '__main__':
    res = dict(lift=lift(), structure=structure(), stability=stability(), drive=drive_demand(), bin_on_slope=bin_on_slope(), step_energy=step_energy())
    json.dump(res, open(os.path.join(OUT, 'statics.json'), 'w'), indent=1)
    for k, v in res.items():
        print('==', k)
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, list):
                    for r in vv: print('   ', r)
                else: print('  ', kk, vv)
