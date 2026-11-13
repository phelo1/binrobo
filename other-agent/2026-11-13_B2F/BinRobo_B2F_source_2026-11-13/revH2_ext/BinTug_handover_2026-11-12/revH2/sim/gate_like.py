#!/usr/bin/env python3
"""Rev H2 against the other agent's FROZEN GATE (revG/sim/cg/CRITERIA_FROZEN.md), as far as this reduced-order model can go.
Writes ../results/gate_like.json.

Run here with the gate's thresholds: G2 climb, G3 step, G4 e-stop, G8 static loads and tip angles, G9 mass.
NOT run here, because they need contact and yaw physics (MuJoCo): G1 grab Monte Carlo, G5 carry and pivot, G6 set-down, G7 dt repeat.
These are indications, not gate results: this model welds the bin to the robot and has no yaw (see dyn.py)."""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import params as P
from dyn import Sim, Ground, settle, G
from models import make_revh
R = P.ROBOT
CRR_GATE = 0.06                                                    # gate: tug tyre and castor rolling resistance 0.06
ACC = 0.6                                                          # gate: accel ramp 0.6 m/s^2


def robot(mu, fill=1.0, binkey='ESE240SL'):
    b = make_revh(binkey, fill, mu=mu)
    for w in b.wheels: w.crr = CRR_GATE
    return b


def g2_climb(mu, nose_uphill=True):
    """Full 240 L, 5 m at 0.5 m/s up 12 %: 5 m in <= 25 s, then 3 s brake hold with creep < 0.05 m."""
    b = robot(mu); sgn = 1.0 if nose_uphill else -1.0
    s = Sim([b], Ground.flat(), grade=0.12 * sgn); settle(s, 1.2); x0 = b.x; t5 = None
    while s.t < 30.0:
        s.v_cmd = sgn * min(0.5, ACC * s.t + 0.02); s.step()
        if abs(b.x - x0) >= 5.0: t5 = s.t; break
    xh = b.x; s.braked = True; t_b = s.t; x_stop = None
    while s.t < t_b + 5.0:
        s.step()
        if x_stop is None and abs(b.vx) < 0.005: x_stop = b.x; t_stop = s.t
    creep = abs(b.x - x_stop) if x_stop is not None else float('nan')
    ok = t5 is not None and t5 <= 25.0 and creep < 0.05
    return dict(test='G2 climb 12 %', mu=mu, leading='nose' if nose_uphill else 'tail', t_5m_s=round(t5, 1) if t5 else None, hold_creep_m=round(creep, 3), ok=bool(ok))


def g3_step(h, onesided, drive_first=False, mu=0.6, v=0.5):
    """Full 240 L, 0.5 m/s, sharp step: reach 4.5 m in <= 25 s, roll and pitch < 15 deg."""
    b = robot(mu); x_o = 1.8
    if not drive_first:
        g = Ground.step(x_o, h); gR = Ground.flat() if onesided else g; s = Sim([b], g, gR); sgn = 1.0
    else:                                                          # tail leading: a drop for +x travel is a step up for -x travel
        g = Ground.step(x_o, -h); gR = Ground.flat() if onesided else g
        b = make_revh('ESE240SL', 1.0, mu=mu, x0=2 * x_o)
        for w in b.wheels: w.crr = CRR_GATE
        s = Sim([b], g, gR); sgn = -1.0
    settle(s, 1.2); x0 = b.x; pitch = roll = 0.0; t45 = None
    while s.t < 25.0:
        s.v_cmd = sgn * min(v, ACC * s.t + 0.02); s.step()
        pitch = max(pitch, abs(b.th)); roll = max(roll, abs(b.ph))
        if abs(b.x - x0) >= 4.5: t45 = s.t; break
    ok = t45 is not None and math.degrees(pitch) < 15 and math.degrees(roll) < 15
    return dict(test='G3 step', h_mm=round(h * 1000), where='one side' if onesided else 'full width', leading='drive wheels (tail first)' if drive_first else 'nose castors',
                reached_m=round(abs(b.x - x0), 2), t_s=round(s.t, 1), pitch_deg=round(math.degrees(pitch), 1), roll_deg=round(math.degrees(roll), 1), ok=bool(ok))


def g4_estop(nose_downhill=True, mu=0.30, v=0.5):
    """Full 240 L, 12 % down, mu 0.30, 0.5 m/s, spring brakes: stop <= 0.5 m, slide after the stop < 0.05 m, no tip."""
    b = robot(mu); sgn = 1.0 if nose_downhill else -1.0
    s = Sim([b], Ground.flat(), grade=-0.12 * sgn); settle(s, 1.2); pitch = 0.0
    while s.t < 5.0:
        s.v_cmd = sgn * min(v, ACC * s.t + 0.02); s.step()
    xb, vb = b.x, b.vx; s.braked = True; x_stop = None
    while s.t < 12.0:
        s.step(); pitch = max(pitch, abs(b.th))
        if x_stop is None and abs(b.vx) < 0.005: x_stop = b.x; t_stop = s.t
        if x_stop is not None and s.t > t_stop + 3.0: break
    stop = abs(x_stop - xb) if x_stop is not None else float('nan'); slide = abs(b.x - x_stop) if x_stop is not None else float('nan')
    ok = stop <= 0.5 and slide < 0.05 and math.degrees(pitch) < 15
    return dict(test='G4 e-stop 12 % down', leading='nose castors' if nose_downhill else 'bin (tail first)', v_at_brake=round(abs(vb), 2), stop_m=round(stop, 3),
                slide_after_stop_m=round(slide, 3), pitch_deg=round(math.degrees(pitch), 1), ok=bool(ok))


def cg(bin_model, kg):
    """Robot + bin CG in the robot frame. bin_model: 'gate' (the other agent's frozen bin model) or 'mine' (params.bin_cg)."""
    r = P.robot_mass()
    if kg == 0: return r['m'], r['x'], r['z']
    if bin_model == 'gate':
        c = P.GATE_BIN_CG['ESE240SL_110' if kg > 80 else 'ESE240SL_60']; xf, zb = c['xf'], c['z']
    else:
        b = P.BINS['ESE240SL']; c = P.bin_cg(b, (kg - b['empty']) / b['fill_full']); xf, zb = c['xf'], c['z']
    xb = R['pad_x'] - xf; zb += R['lift']; M = r['m'] + kg
    return M, (r['m'] * r['x'] + kg * xb) / M, (r['m'] * r['z'] + kg * zb) / M


def g8_static(bin_model='gate'):
    """12 % grade facing up, down and across, 110 and 60 kg bins: each drive wheel >= 100 N, castors (sum) >= 50 N;
    hand-calc tip angles >= 20 deg in every direction. Castor lift-off >= 20 deg is the other agent's extra design target."""
    th = math.atan(0.12); s, c = math.sin(th), math.cos(th); L = R['nose_x']; yd = R['drive_track'] / 2; yc = R['nose_track'] / 2; rows = []
    for kg in (110.0, 60.0, 0.0):
        M, X, Z = cg(bin_model, kg); W = M * G
        poses = {}
        for name, sx in (('nose uphill', 1.0), ('nose downhill', -1.0)):          # weight shifts towards the downhill end
            Nc = W * (c * X - sx * s * Z) / L; Nd = W * c - Nc; poses[name] = dict(drive_each_N=round(Nd / 2), castors_N=round(Nc))
        for name, sy in (('cross-slope, left side downhill', 1.0), ('cross-slope, right side downhill', -1.0)):
            Nc = W * c * X / L; Nd = W * c - Nc
            # lateral transfer taken by the drive axle and the castors in proportion to their vertical load (rigid frame)
            dN = W * s * Z / (2 * (Nd * yd + Nc * yc) / (Nd + Nc))
            poses[name] = dict(drive_low_N=round(Nd / 2 + dN * Nd / (Nd + Nc)), drive_high_N=round(Nd / 2 - dN * Nd / (Nd + Nc)), castors_N=round(Nc))
        okp = all(min(v.get('drive_each_N', 1e9), v.get('drive_high_N', 1e9)) >= 100 and v['castors_N'] >= 50 for v in poses.values())
        def tip_side(px, py, qx, qy):                                             # CG distance from the line drive wheel -> castor
            Ls = math.hypot(qx - px, qy - py); d = abs((qx - px) * (py - 0) - (px - X) * (qy - py)) / Ls; return math.degrees(math.atan(d / Z))
        tips = dict(lateral_deg=round(tip_side(0, yd, L, yc), 1), forward_over_castors_deg=round(math.degrees(math.atan((L - X) / Z)), 1),
                    rear_onto_antitip_wheels_deg=round(math.degrees(math.atan((X - R['tail_x']) / Z)), 1),
                    castor_liftoff_about_drive_axle_deg=round(math.degrees(math.atan(X / Z)), 1))
        # traction demand on 12 %, the other agent's hand-calc terms (their handcalc_cmp.py), worst orientation
        rw = R['drive_r']; resist = W * s + 2 * 0.06 * 300 * 0.165 / rw + 2 * 0.06 * 200 * 0.13 / 0.13
        Nd_worst = W * (c * (L - X) - s * Z) / L
        rows.append(dict(bin_kg=kg, bin_cg_model=bin_model, mass_kg=round(M, 1), cg_x=round(X, 3), cg_z=round(Z, 3), poses=poses, poses_ok=bool(okp), tips=tips,
                         tips_ok=bool(min(tips['lateral_deg'], tips['forward_over_castors_deg'], tips['rear_onto_antitip_wheels_deg']) >= 20),
                         castor_liftoff_target_met=bool(tips['castor_liftoff_about_drive_axle_deg'] >= 20) if kg else None,
                         mu_req_12pct_their_method=round(resist / Nd_worst, 3), torque_per_wheel_12pct_Nm=round(resist * rw / 2, 1)))
    return rows


def main():
    out = dict(note=__doc__, criteria='reference/other_agent/CRITERIA_FROZEN.md (frozen 2026-11-11 07:51 +03)')
    print('G2'); out['G2'] = [g2_climb(mu, n) for mu in (0.30, 0.25, 0.22) for n in (True, False)]
    print('G3'); out['G3'] = [g3_step(0.04, True), g3_step(0.04, False), g3_step(0.04, False, drive_first=True), g3_step(0.04, True, drive_first=True),
                              g3_step(0.05, False), g3_step(0.05, False, drive_first=True), g3_step(0.06, False), g3_step(0.06, False, drive_first=True),
                              g3_step(0.04, False, mu=0.45), g3_step(0.04, False, drive_first=True, mu=0.45)]
    out['G3'][8]['mu'] = out['G3'][9]['mu'] = 0.45
    print('G4'); out['G4'] = [g4_estop(True), g4_estop(False), g4_estop(True, v=0.8), g4_estop(False, v=0.8)]
    out['G8'] = g8_static('gate') + g8_static('mine')
    for label, kg in P.BATTERY_OPTIONS.items():                     # battery choice changes mass and, a little, the pitch margin
        pass
    r = P.robot_mass(); out['G9'] = dict(mass_kg=round(r['m'], 1), limit_kg=120, ok=bool(r['m'] <= 120),
                                         with_donor_agm_kg=round(r['m'] - 10.8 + 22.0, 1), with_lifepo4_kg=round(r['m'] - 10.8 + 3.8, 1))
    out['not_run_here'] = ['G1 grab Monte Carlo (contact)', 'G5 carry stability and 180 deg pivot (yaw)', 'G6 set-down, 18 cases (contact)', 'G7 time-step repeat']
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'gate_like.json'), 'w'), indent=1)
    for k in ('G2', 'G3', 'G4'):
        for r_ in out[k]: print(r_)
    for r_ in out['G8']: print({k: v for k, v in r_.items() if k != 'poses'}, r_['poses'])
    print(out['G9'])


if __name__ == '__main__':
    main()
