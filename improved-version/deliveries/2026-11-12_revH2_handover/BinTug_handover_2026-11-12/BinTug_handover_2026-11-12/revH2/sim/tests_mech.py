#!/usr/bin/env python3
"""Rev H mechanical test bench (reduced-order dynamics). Writes ../results/mech.json.

Tests mirror the Rev G MuJoCo list where they still apply:
  loads      static wheel loads for every data-sheet bin, empty and full
  layout     the layout iteration that fixed the nose-heavy first sketch (documented, because it changed the design)
  obstacles  full-width square steps up/down, one-sided bump (Rev G test geometry), potholes
  grades     climb, descent, brake hold and emergency stop on 7.5 / 12 / 20 % at mu 0.3 (wet leaves) and above
  retention  does the bin stay seated on the comb over the worst obstacle runs
  revg_ref   the Rev G tug + bin in the same model, next to the project's published MuJoCo results

usage: python3 tests_mech.py [quick]
"""
import sys, os, json, math, time, copy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import params as P
from models import make_revh, make_revg
from dyn import Sim, Ground, settle, G

OUT = os.path.join(HERE, '..', 'results'); os.makedirs(OUT, exist_ok=True)
QUICK = len(sys.argv) > 1 and sys.argv[1] == 'quick'
LOADS = [('unladen', None, 0.0), ('empty 240 L', 'ESE240SL', 0.0), ('full 240 L (110 kg)', 'ESE240SL', 1.0), ('full 140 L (70 kg)', 'ESE140CL', 1.0)]


# ------------------------------------------------------------------------------------------------ helpers
def comb_local(b):
    """Comb point in body (CG-relative) coordinates."""
    return (P.ROBOT['pad_x'] - b.meta['cgx'], 1.0 + P.ROBOT['lift'] - b.meta['cgz'])


class Retention:
    """1-D check: a bin resting on the comb separates when the comb accelerates downwards faster than gravity."""
    def __init__(self, b, gz):
        self.b, self.gz = b, gz; self.l = comb_local(b)
        _, z, _, vz = b.point(*self.l); self.zb, self.vb, self.contact = z, vz, True
        self.max_gap = 0.0; self.vprev = vz; self.az_min = 0.0; self.az_max = 0.0

    def update(self, dt):
        _, z, _, vz = self.b.point(*self.l)
        a = (vz - self.vprev) / dt; self.vprev = vz
        if self.contact:
            self.zb, self.vb = z, vz
            if a < self.gz: self.contact = False
        else:
            self.vb += self.gz * dt; self.zb += self.vb * dt
            if self.zb <= z: self.contact = True; self.zb, self.vb = z, vz
        self.max_gap = max(self.max_gap, self.zb - z)


def obstacle(kind, h, v, binkey, fill, mu=0.6, t_lim=None, onesided=False, length=0.40, t_end=12.0, ramp=0.5):
    b = make_revh(binkey, fill, mu=mu, t_lim=t_lim)
    x_o = 1.8
    if kind == 'step': g = Ground.step(x_o, h); x_end = x_o
    elif kind == 'bump': g = Ground.bump(x_o, length, h); x_end = x_o + length
    else: g = Ground.pothole(x_o, length, h); x_end = x_o + length
    gR = Ground.flat() if onesided else g
    s = Sim([b], g, gR); settle(s, 1.2)
    cgx = b.meta['cgx']; x_goal = x_end + 0.45 + 0.5 + cgx
    ret = Retention(b, -G) if binkey else None
    pk = dict(pitch=0.0, roll=0.0, vmin=9.0, tq=0.0, drive_min=1e9)
    lc = comb_local(b) if binkey else (P.ROBOT['pad_x'] - cgx, 1.1 - b.meta['cgz'])
    az_hi = 0.0; vz_prev = b.point(*lc)[3]; k = 0
    while s.t < t_end and b.x < x_goal:
        s.v_cmd = min(v, ramp * s.t + 0.05)
        s.step(); k += 1
        if ret: ret.update(s.dt)
        pk['pitch'] = max(pk['pitch'], abs(b.th)); pk['roll'] = max(pk['roll'], abs(b.ph))
        if s.t > v / ramp + 0.3: pk['vmin'] = min(pk['vmin'], b.vx)
        if k % 50 == 0:                                          # 10 ms average upward acceleration at the comb
            vzc = b.point(*lc)[3]; a = (vzc - vz_prev) / (50 * s.dt); vz_prev = vzc
            az_hi = max(az_hi, a)
    ok = b.x >= x_goal
    where = None
    if not ok:
        ax = b.x - cgx - x_o
        where = 'nose casters' if ax < -P.ROBOT['nose_x'] + 0.25 else ('drive wheels' if ax < 0.25 else 'tail wheels')
    return dict(kind=kind, h_mm=round(h * 1000), v=v, mu=mu, t_lim=t_lim or P.DRIVE['t_lim'], onesided=onesided, ok=bool(ok),
                stalled_at=where, t=round(s.t, 2), vmin=round(pk['vmin'], 2), pitch_deg=round(math.degrees(pk['pitch']), 1),
                roll_deg=round(math.degrees(pk['roll']), 1), comb_load_factor=round(1.0 + az_hi / G, 2),
                lip_gap_mm=round(ret.max_gap * 1000, 1) if ret else None)


def grade_run(mode, grade, binkey, fill, mu, v=0.8, ramp=0.4, t_lim=None):
    """mode: 'climb' (+x is uphill), 'descend' (+x is downhill), 'estop' (descend then brakes), 'hold' (parked, brakes on)."""
    b = make_revh(binkey, fill, mu=mu, t_lim=t_lim)
    gr = grade if mode == 'climb' else -grade
    s = Sim([b], Ground.flat(), grade=gr); settle(s, 1.2)
    cgx = b.meta['cgx']; x0 = b.x
    nose_min = 1e9; tail_max = 0.0; slip_max = 0.0; pitch = 0.0
    if mode == 'hold':
        s.braked = True
        while s.t < 8.0: s.step()
        return dict(mode=mode, grade_pct=round(grade * 100, 1), mu=mu, creep_m=round(abs(b.x - x0), 3), ok=bool(abs(b.x - x0) < 0.05))
    t_brake = 5.0; x_brake = None; stop_t = None
    t_end = 8.0 if mode != 'estop' else 12.0
    v_end = None
    while s.t < t_end:
        if mode == 'estop' and s.t >= t_brake:
            if x_brake is None: x_brake = b.x; v_brake = b.vx
            s.braked = True
            if abs(b.vx) < 0.005 and stop_t is None: stop_t = s.t - t_brake; x_stop = b.x
            if stop_t is not None and s.t > t_brake + stop_t + 1.0: break
        else:
            s.v_cmd = min(v, ramp * s.t + 0.02)
        s.step()
        if s.t > 0.2:
            nose_min = min(nose_min, sum(w.fn for w in b.wheels if w.name.startswith('nose')))
            tail_max = max(tail_max, sum(w.fn for w in b.wheels if w.name.startswith('tail')))
            pitch = max(pitch, abs(b.th))
            for w in b.wheels:
                if w.driven: slip_max = max(slip_max, abs(w.w * w.r - b.vx))
    out = dict(mode=mode, grade_pct=round(grade * 100, 1), mu=mu, v_cmd=v, v_end=round(b.vx, 2), nose_min_N=round(nose_min),
               tail_max_N=round(tail_max), slip_max=round(slip_max, 2), pitch_deg=round(math.degrees(pitch), 1))
    if mode == 'estop':
        out.update(stop_dist_m=round((x_stop - x_brake) if stop_t is not None else float('nan'), 2), stop_t_s=round(stop_t, 2) if stop_t is not None else None,
                   v_at_brake=round(v_brake, 2), ok=bool(stop_t is not None and (x_stop - x_brake) < 1.0 and tail_max >= 0))
    elif mode == 'climb':
        out['ok'] = bool(b.vx > 0.85 * v)
    else:
        out['ok'] = bool(abs(b.vx - v) < 0.1 * v + 0.05)
    return out


# ------------------------------------------------------------------------------------------------ test groups
def static_loads():
    rows = []
    for key in [None] + list(P.BINS):
        for fill in ((0.0,) if key is None else (0.0, 0.5, 1.0)):
            b = make_revh(key, fill); s = Sim([b], Ground.flat()); settle(s, 1.5)
            d = {w.name: w.fn / G for w in b.wheels}
            drive = d['driveL'] + d['driveR']; nose = d['noseL'] + d['noseR']
            c = b.meta
            # tip-back grade (CG over the drive axle), lateral tip angle, traction demand on 12 %
            nx = P.ROBOT['nose_x']; tx = abs(P.ROBOT['tail_x'])
            def drive_share(g_signed):                             # g_signed > 0: nose downhill
                xe = c['x'] + c['z'] * g_signed                    # where the weight vector meets the ground, ahead of the axle
                return 1.0 - (xe / nx if xe >= 0 else -xe / tx)
            rows.append(dict(bin=P.BINS[key]['name'] if key else 'none (unladen)', fill=fill, mass_kg=round(b.m, 1), cg_x=round(c['x'], 3), cg_z=round(c['z'], 3),
                             drive_kg=round(drive, 1), nose_kg=round(nose, 1), nose_share_pct=round(100 * nose / (drive + nose), 1),
                             tipback_grade_pct=round(100 * c['x'] / c['z'], 1),
                             lateral_tip_deg=round(math.degrees(math.atan((P.ROBOT['drive_track'] / 2) / c['z'])), 1),
                             mu_hold_12pct_nose_down=round(0.12 / drive_share(0.12), 3), mu_hold_12pct_nose_up=round(0.12 / drive_share(-0.12), 3),
                             mu_hold_7p5pct_nose_down=round(0.075 / drive_share(0.075), 3)))
    return rows


def layout_study():
    """Design iteration: the first sketch (batteries and electronics in the nose, 200 mm donor casters, pad 0.30 m ahead of the axle)
    put 51 % of the unladen robot on the nose casters and stalled on every step when unladen."""
    base_R = copy.deepcopy(P.ROBOT); base_M = list(P.MASS_ITEMS)
    def setv(pad_x=0.30, nose_x=0.66, nose_r=0.10, batt_x=0.55, motor_x=0.08, ebox_x=0.58, nose_m=4.0, tail_gap=0.075):
        d = pad_x - 0.30
        P.ROBOT.update(pad_x=pad_x, nose_x=nose_x, nose_r=nose_r, tail_gap=tail_gap, tail_x=-0.47)
        P.MASS_ITEMS[:] = [('Legs', 11.1, 0.15 + d / 2, 0.285), ('Nose cross', 5.5 if batt_x < 0.3 else 6.5, nose_x - 0.06, 0.285), ('Mast uprights', 7.1, 0.38 + d, 0.80),
                           ('Mast ties', 3.0, 0.45 + d, 0.60), ('Carriage', 4.5, 0.33 + d, 0.90), ('Actuator', 2.0, 0.40 + d, 0.65), ('Drive units', 19.0, motor_x, 0.16),
                           ('Nose casters', nose_m, nose_x, nose_r + 0.02), ('Tail wheels', 0.8, -0.47, 0.07), ('Batteries', 10.8, batt_x, 0.36 if batt_x < 0.3 else 0.25),
                           ('E-box', 5.0, (0.44 + d) if ebox_x < 0.5 else ebox_x, 0.55 if ebox_x < 0.5 else 0.40), ('Sensors etc', 5.0, 0.50, 0.50), ('Brackets', 4.0, 0.15, 0.22)]
    variants = [
        ('A0 first sketch: batteries + electronics in the nose, 200 mm casters, tail gap 12 mm', dict(tail_gap=0.012)),
        ('A0b as A0, tail gap 75 mm', dict()),
        ('A1 batteries on the legs, motors aft, electronics on the mast', dict(batt_x=-0.24, motor_x=-0.08, ebox_x=0.44)),
        ('A2 = A1 + 260 mm nose casters', dict(batt_x=-0.24, motor_x=-0.08, ebox_x=0.44, nose_r=0.13, nose_m=5.0)),
        ('A3 = A2 + pad moved 70 mm forward', dict(batt_x=-0.24, motor_x=-0.08, ebox_x=0.44, nose_r=0.13, nose_m=5.0, pad_x=0.37)),
        ('A4 = A3 + nose casters 80 mm further forward (CHOSEN)', dict(batt_x=-0.24, motor_x=-0.08, ebox_x=0.44, nose_r=0.13, nose_m=5.0, pad_x=0.37, nose_x=0.74)),
        ('A5 = A1 + pad forward, donor 200 mm casters kept', dict(batt_x=-0.24, motor_x=-0.08, ebox_x=0.44, pad_x=0.37)),
    ]
    rows = []
    for name, kw in variants:
        setv(**kw)
        r = P.robot_mass(); cl = P.combined('ESE240SL', 1.0); wb = P.ROBOT['nose_x']
        row = dict(variant=name, unladen_nose_pct=round(100 * r['x'] / wb), full_nose_pct=round(100 * cl['x'] / wb), steps={})
        for lab, bk, fill in LOADS[:3]:
            res = {}
            for h in (0.04, 0.05, 0.06):
                for v in (0.5, 0.8):
                    res['%d@%.1f' % (h * 1000, v)] = obstacle('step', h, v, bk, fill)['ok']
            row['steps'][lab] = res
        row['passes'] = sum(sum(v.values()) for v in row['steps'].values()); row['of'] = 18
        g = grade_run('climb', 0.12, 'ESE240SL', 1.0, 0.3, v=0.5); row['full_climb12_tail_N'] = g['tail_max_N']
        rows.append(row); print('  layout', name, row['passes'], '/ 18', flush=True)
    P.ROBOT.clear(); P.ROBOT.update(base_R); P.MASS_ITEMS[:] = base_M
    return rows


def obstacles():
    rows = []
    hs = (0.04, 0.05, 0.06, 0.08)
    for lab, bk, fill in LOADS:
        for mu in (0.6, 0.45):
            for h in hs:
                for v in (0.5, 0.8):
                    r = obstacle('step', h, v, bk, fill, mu=mu); r['load'] = lab; rows.append(r)
        print('  steps', lab, flush=True)
    for h in (0.05, 0.06, 0.08):                                 # higher current limit (80 A class), full bin
        for v in (0.5, 0.8):
            r = obstacle('step', h, v, 'ESE240SL', 1.0, t_lim=P.DRIVE['t_lim_hi']); r['load'] = LOADS[2][0]; rows.append(r)
    for lab, bk, fill in LOADS:                                  # step down
        for h in (-0.06, -0.10):
            for v in (0.5, 0.8):
                r = obstacle('step', h, v, bk, fill); r['load'] = lab; rows.append(r)
    for lab, bk, fill in LOADS:                                  # one-sided bump, Rev G test geometry (300 mm long box under the left wheels)
        for h in (0.04, 0.05, 0.06):
            r = obstacle('bump', h, 0.5, bk, fill, onesided=True, length=0.30); r['load'] = lab; rows.append(r)
    for lab, bk, fill in LOADS:                                  # potholes: one-sided (Rev G test) and full-width
        for one in (True, False):
            for d in (0.04, 0.06, 0.10):
                for v in (0.5, 0.8):
                    r = obstacle('pothole', d, v, bk, fill, onesided=one, length=0.40); r['load'] = lab; rows.append(r)
    return rows


def wet_leaves_steps():
    """Small steps on wet leaf mulch (mu 0.3), the worst surface the cold-eye review names for this lane."""
    rows = []
    for lab, bk, fill in LOADS:
        for h in (0.03, 0.04):
            for v in (0.5, 0.8):
                r = obstacle('step', h, v, bk, fill, mu=0.3); r['load'] = lab; rows.append(r)
    return rows


def grades():
    rows = []
    cases = [('unladen', None, 0.0), ('empty 240 L', 'ESE240SL', 0.0), ('full 240 L (110 kg)', 'ESE240SL', 1.0)]
    for lab, bk, fill in cases:
        for grade in (0.075, 0.12, 0.20):
            for mu in (0.3, 0.45):
                for mode in ('climb', 'descend', 'estop', 'hold'):
                    r = grade_run(mode, grade, bk, fill, mu); r['load'] = lab; rows.append(r)
        print('  grades', lab, flush=True)
    for mu in (0.10, 0.15, 0.20):                                # how slippery before a full bin slides on 12 %
        r = grade_run('hold', 0.12, 'ESE240SL', 1.0, mu); r['load'] = cases[2][0]; rows.append(r)
        r = grade_run('estop', 0.12, 'ESE240SL', 1.0, mu); r['load'] = cases[2][0]; rows.append(r)
    return rows


def revg_reference():
    """Rev G tug + tilted bin in this model, beside the project's MuJoCo results (RESULTS_G3_mech s.3, RESULTS_G5 s.5)."""
    def bump(h, onesided, v=0.5, mu=0.6, bin_m=108.3):
        tug, binb, joint, meta = make_revg(bin_m=bin_m, mu=mu)
        x_b = 1.6; gL = Ground.bump(x_b, 0.30, h); gR = Ground.flat() if onesided else gL
        s = Sim([tug, binb], gL, gR, joint=joint); settle(s, 2.0)
        x_goal = x_b + 0.30 + 0.5 + 0.67 + P.REVG['tug_cg'][0]; s.v_cmd = v; hook = 0.0
        while s.t < 14.0 and tug.x < x_goal:
            s.step(); hook = max(hook, math.hypot(*s.joint_force))
        return dict(h_mm=round(h * 1000), onesided=onesided, ok=bool(tug.x >= x_goal), hook_peak_N=round(hook))
    published = {40: 'PASS', 50: 'STALL', 60: 'STALL'}
    rows = []
    for h in (0.04, 0.05, 0.06):
        r = bump(h, True); r['mujoco_published'] = published[r['h_mm']]; rows.append(r)
    for h in (0.04, 0.05, 0.06):
        r = bump(h, False); r['mujoco_published'] = 'not tested'; rows.append(r)
    tug, binb, joint, meta = make_revg(); s = Sim([tug, binb], Ground.flat(), joint=joint); settle(s, 2.0)
    stat = dict(tug_drive_kg=round(sum(w.fn for w in tug.wheels if w.driven) / G, 1), tug_caster_kg=round(sum(w.fn for w in tug.wheels if not w.driven) / G, 1),
                bin_wheels_kg=round(sum(w.fn for w in binb.wheels) / G, 1), hook_vertical_N=round(abs(s.joint_force[1])),
                hook_share=round(meta['hook_static_share'], 3))
    return dict(static=stat, bumps=rows)


if __name__ == '__main__':
    t0 = time.time(); res = {}
    print('static loads'); res['loads'] = static_loads()
    print('Rev G reference'); res['revg_ref'] = revg_reference()
    if not QUICK:
        print('layout study'); res['layout'] = layout_study()
    print('obstacles'); res['obstacles'] = obstacles()
    print('wet leaves'); res['wet_leaves_steps'] = wet_leaves_steps()
    print('grades'); res['grades'] = grades()
    res['meta'] = dict(robot=P.robot_mass(), ROBOT=P.ROBOT, DRIVE=P.DRIVE, cpu_s=round(time.time() - t0), date='2026-11-12',
                       note='Reduced-order model (x, z, pitch, roll); no yaw. Not MuJoCo. See dyn.py header.')
    json.dump(res, open(os.path.join(OUT, 'mech.json'), 'w'), indent=1)
    print('wrote mech.json in %d s' % (time.time() - t0))
