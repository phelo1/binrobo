#!/usr/bin/env python3
"""Revision 4 tests that are not in the other agent's runners (written 20 Nov 2026 by the reviewer/tester agent).
Uses their simulator module (env CMP_SIM, with my switches) and their drive/brake model unchanged. Run from revG/sim/cg.
Results: <RES>/<PREFIX>Y_<name><TAG>.json (env H2_RES, CMP_PREFIX, IT1_TAG as in their runX.py).

  runY.py pstop <v> <grade> <mu> <bin_kg|0> <t_react> [rev]
        Person stop. The robot drives at v (m/s; 'rev' = bin end leading) on a slope 'grade' in its travel direction (-0.12 = 12 % downhill),
        grip mu. At a mark the bumper is taken as touched; the robot keeps driving for t_react seconds (switch, safety controller,
        contactors, spring brakes), then the brakes go on (their brake model). Output: distance travelled from the touch to standstill
        = the bumper travel needed to stop within the bumper.
  runY.py lower <obst_mm> <L|both> <bin_kg> <margin_mm> [nocheck]
        Lowering guard. After the pick-up a block of height obst_mm is put under the left bin wheel (or a bar under both). The comb
        lowers at the real actuator speed (6 mm/s). Guard: if the load on the lift falls by more than max(80 N, 10 % of the carried
        load) while the comb is still more than margin_mm above the height where the bin wheels left the ground at the pick-up, stop and raise 30 mm.
        Output: peak force on the block, whether the guard tripped, and at what height.
  runY.py lat <bin_kg>
        Sideways tyre force on the drive wheels: pivot 180 deg on the spot, a tight turn at 0.5 m/s, a slalom, and a drive along a
        12 % cross slope, with the bin on board. Output: the largest sideways force on one drive tyre in each phase (for the motor plate).
  runY.py liftpeak <step|kerb> <one|both|nose> <v>
        Lift shock load: their step / kerb drive with the lift force cap as set in CGB_GEO act_N (use a high cap to see the true peak).
"""
import os, sys, json, time, math
H = os.path.join(os.getcwd(), 'h2'); sys.path.insert(0, H); sys.path.insert(0, os.path.join(H, '..', '..', 'g6'))
import numpy as np, mujoco, importlib
B = importlib.import_module(os.environ.get('CMP_SIM', 'simB2hx'))
from bins_g5 import BINS
RES = os.environ.get('H2_RES', os.path.join(H, 'res')); TAG = os.environ.get('IT1_TAG', ''); PFX = os.environ.get('CMP_PREFIX', 'B2F_'); T0 = time.time()
PM = float(os.environ.get('PERT_M', '1.0'))

def dump(name, o):
    o['cpu_s'] = round(time.time() - T0); o['geo'] = dict(B.GEO); o['env'] = {k: v for k, v in os.environ.items() if k.startswith(('H2_', 'CGB_', 'B2_', 'PERT', 'CMP_', 'SIM_', 'X_'))}
    f = os.path.join(RES, PFX + 'Y_' + name + TAG + '.json'); json.dump(o, open(f, 'w'), indent=1, default=str)
    print(name, json.dumps({k: v for k, v in o.items() if k not in ('events', 'geo', 'env', 'trace')}, default=str)[:900], flush=True)

# an extra world block (parked under the ground) that a test can move: wraps their build_xml
OBST = [0.06, 0.05, 0.03]   # half-sizes of the block (m); set by the test before the model is built. The block sits on a movable (mocap) body
_bx = B.build_xml
def build_xml2(*a, **k):
    xml, tm, bm = _bx(*a, **k)
    xml = xml.replace('</worldbody>', '<body name="obstb" mocap="true" pos="0 0 -1"><geom name="obst" type="box" size="%g %g %g" friction="0.6 0.005 0.0001" condim="3" contype="1" conaffinity="0" rgba="0.8 0.2 0.2 1"/></body></worldbody>' % tuple(OBST))
    return xml, tm, bm
B.build_xml = build_xml2

def scale_mass(S):
    if PM != 1.0:
        S.m.body_mass[:] *= PM; S.m.body_inertia[:] *= PM; mujoco.mj_setConst(S.m, S.d); S.lift_mass *= PM; mujoco.mj_forward(S.m, S.d)
def set_mu(S, mu):
    for n in ('ground', 'bump', 'driveL', 'driveR', 'casterL', 'casterR', 'binwheelL', 'binwheelR'):
        g = mujoco.mj_name2id(S.m, mujoco.mjtObj.mjOBJ_GEOM, n)
        if g >= 0: S.m.geom_friction[g][0] = mu
def nominal(binkey, kg, **kw):
    p = B.bin_params(binkey); Bn = BINS[binkey]; p['fill'] = kg - Bn['empty']
    S = B.SimB(binkey, p, tug_pose=B.start_pose(p), **kw); scale_mass(S); R = B.RunnerB(S); g = B.grab(R)
    return S, R, g
def nobin(binkey='ESE240SL'):
    p = B.bin_params(binkey); S = B.SimB(binkey, p, with_bin=False); scale_mass(S); R = B.RunnerB(S); R.run_for(0.5)
    return S, R, dict(result='no bin')
def obst_force(S):
    g = mujoco.mj_name2id(S.m, mujoco.mjtObj.mjOBJ_GEOM, 'obst'); f = np.zeros(6); F = 0.0
    for i in range(S.d.ncon):
        c = S.d.contact[i]
        if c.geom1 == g or c.geom2 == g: mujoco.mj_contactForce(S.m, S.d, i, f); F += f[0]
    return F

cmd = sys.argv[1]
if cmd == 'pstop':
    v, grade, mu, kg, tr = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]); rev = len(sys.argv) > 7 and sys.argv[7] == 'rev'
    S, R, g = nominal('ESE240SL', kg) if kg > 0 else nobin()
    psi0 = S.rpy()[2]; sg = -1 if rev else 1
    set_mu(S, mu); R.phase = 'onto the slope'; R.ramp_grade(grade * sg, 0, 2.0); R.run_for(0.5)      # grade is along the travel direction
    x0 = S.d.xpos[S.bid['tug']].copy(); R.phase = 'driving'; R.ctrl_fn = B.heading_hold(R, sg * v, psi0)
    R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2] - x0[:2]) >= 2.0, 20.0); v0 = S.fwd_speed(); xc = S.d.xpos[S.bid['tug']].copy(); tc = R.t
    R.phase = 'bumper touched: still driving for the reaction time'; R.run_for(tr); vb = S.fwd_speed(); xb = S.d.xpos[S.bid['tug']].copy()
    R.ctrl_fn = None; R.phase = 'brakes on'; R.hold(); R.until(lambda: abs(S.fwd_speed()) < 0.01, 8.0); ts = R.t - tc
    d = float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2] - xc[:2])); dr = float(np.linalg.norm(xb[:2] - xc[:2]))
    R.run_for(3.0); slide = float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2] - xc[:2])) - d
    o = dict(test='person_stop', v_cmd=v, v_at_touch=round(abs(v0), 3), v_at_brake=round(abs(vb), 3), grade=grade, mu=mu, bin_kg=kg, t_react=tr, rev=rev, grab=g['result'], robot_kg=round(S.tug_mass * PM, 1),
             travel_after_touch_m=round(d, 3), of_which_reaction_m=round(dr, 3), braking_m=round(d - dr, 3), time_to_stop_s=round(ts, 2), slide_after_stop_m=round(slide, 3),
             captured_end=(S.captured() if kg > 0 else None), roll=round(abs(S.rpy()[0]), 1), pitch=round(abs(S.rpy()[1]), 1))
    dump('pstop_v%02d_g%+04d_m%02d_k%d_t%02d%s' % (round(v * 100), round(grade * 1000), round(mu * 100), round(kg), round(tr * 100), '_rev' if rev else ''), o)   # [24 Nov] slope in tenths of a per cent in the name (8.5 % was written as -08)
elif cmd == 'lower':
    hmm, where, kg, margin = float(sys.argv[2]), sys.argv[3], float(sys.argv[4]), float(sys.argv[5]) / 1000.0; chk = not (len(sys.argv) > 6 and sys.argv[6] == 'nocheck')
    h = hmm / 1000.0; OBST[:] = [0.06, 0.36 if where == 'both' else 0.05, max(h, 0.002) / 2]
    VL = float(os.environ.get('X_LOWER_V', '0.006')); vt = '' if abs(VL - 0.006) < 1e-9 else '_v%02d' % round(VL * 1000)   # lowering speed (default: 6 mm/s)
    tn = ('_n%02d' % round(float(os.environ['X_TRIP_N']))) if os.environ.get('X_TRIP_N') else ''
    S, R, g = nominal('ESE240SL', kg); o = dict(test='lowering_guard', obst_mm=hmm, where=where, bin_kg=kg, margin_mm=margin * 1000, lower_mm_s=VL * 1000, check=chk, grab=g['result'])
    if g['result'] != 'success': dump('lower_h%03d_%s_k%d_m%02d%s' % (hmm, where, kg, margin * 1000, '' if chk else '_nocheck') + vt + tn, o); sys.exit()
    R.run_for(1.0); S.contacts(); Fc = abs(S.lift_force()); zc = R.zc; q0 = S.lift_q(); wc0 = S.wheel_clear()
    wl = S.d.geom_xpos[S.gid['binwheelL']].copy(); wr = S.d.geom_xpos[S.gid['binwheelR']].copy()
    if hmm > 0: S.d.mocap_pos[0] = [(wl[0] + wr[0]) / 2, (wl[1] + wr[1]) / 2, h / 2] if where == 'both' else [wl[0], wl[1], h / 2]
    mujoco.mj_forward(S.m, S.d)
    # [revision 5] ground-looking ToF sensor on each leg (at the inner face of the leg guard, robot frame y +/-0.357, 150 mm up, level with the bin wheel; the robot's own parts are left out of the ray): it looks down and inwards at
    # the spot where the wheel will land. "short" = how much shorter the reading is than the bare-ground distance. Read before lowering starts.
    yaw_ = math.radians(S.rpy()[2]); nlat = np.array([-math.sin(yaw_), math.cos(yaw_)]); txy = S.d.xpos[S.bid['tug']][:2]; tof = {}
    for nm_, w_ in (('L', wl), ('R', wr)):
        yw_ = float(np.dot(w_[:2] - txy, nlat)); sg_ = 1.0 if yw_ > 0 else -1.0; sp_ = np.array([*(w_[:2] + nlat * (sg_ * 0.357 - yw_)), 0.150]); tg_ = np.array([w_[0], w_[1], 0.0])
        L0_ = float(np.linalg.norm(tg_ - sp_)); gid_ = np.zeros(1, dtype=np.int32); dist_ = mujoco.mj_ray(S.m, S.d, sp_, (tg_ - sp_) / L0_, None, 1, S.bid['tug'], gid_)
        tof[nm_] = dict(bare_mm=round(L0_ * 1000, 1), read_mm=round(dist_ * 1000, 1), short_mm=round((L0_ - dist_) * 1000, 1), hit=(S.m.geom(int(gid_[0])).name if gid_[0] >= 0 else None))
    o['tof'] = tof; o['tof_blocks_lowering'] = bool(max(t_['short_mm'] for t_ in tof.values()) > 15.0)
    # expected touchdown: the lift height at which the bin wheels left the ground at the pick-up. The firmware gets it from the load cell
    # (the height where the lift load stopped rising); here it is taken from the model, with a 5 mm allowance
    q_exp = q0 - wc0 + 0.005
    Fcar = S.lift_mass * 9.81; TRIPN = float(os.environ.get('X_TRIP_N', '80')); drop = max(TRIPN, 0.10 * (Fc - Fcar)); st = dict(peak=0.0, trip=None, t=[], k=0, first=None)
    def cond():
        F = abs(S.lift_force()); Fo = obst_force(S); st['peak'] = max(st['peak'], Fo); q = S.lift_q()
        st['k'] += 1
        if st['k'] % 20 == 0: st['t'].append((round(R.t, 2), round(q * 1000, 1), round(F), round(Fo)))
        if st['first'] is None and Fc - F > drop: st['first'] = round(q * 1000, 1)
        if chk and st['trip'] is None and q > q_exp + margin and Fc - F > drop: st['trip'] = dict(q_mm=round(q * 1000, 1), above_pickup_mm=round((q - zc) * 1000, 1), lift_N=round(F), block_N=round(Fo), t=round(R.t, 2)); return True
        return False
    R.phase = 'lowering at %.0f mm/s' % (VL * 1000); R.ramp_lift(zc, VL, cond=cond, Tmax=80)
    if st['trip']:
        R.phase = 'guard tripped: raise 30 mm'; qt = S.lift_q(); R.ramp_lift(min(qt + 0.03, B.GEO['lift_range'] - 0.002), VL, cond=lambda: (st.__setitem__('peak', max(st['peak'], obst_force(S))) or False), Tmax=12); R.run_for(1.0)
        o.update(result='stopped and raised', block_N_after=round(obst_force(S)), captured_end=S.captured())
    else:
        R.run_for(1.0); F1 = obst_force(S)
        R.phase = 'comb on down to release'; R.ramp_lift(max(0.0, zc - 0.050), VL, cond=lambda: (st.__setitem__('peak', max(st['peak'], obst_force(S))) or False), Tmax=30); R.run_for(1.0)
        o.update(result='set down on the block' if obst_force(S) > 20 else 'set down', block_N_at_pickup_height=round(F1), block_N_after=round(obst_force(S)), bin_tilt_end=round(S.bin_tilt_abs(), 1))
    o.update(carried_load_N=round(Fc - Fcar), carriage_weight_N=round(Fcar), trip_drop_N=round(drop), q_carry_mm=round(q0 * 1000, 1), q_pickup_mm=round(zc * 1000, 1), wheel_clear_carry_mm=round(wc0 * 1000, 1),
             q_expected_touchdown_mm=round(q_exp * 1000, 1), q_first_load_drop_mm=st['first'], tripped=st['trip'], peak_block_N=round(st['peak']), trace=st['t'][-60:])
    dump('lower_h%03d_%s_k%d_m%02d%s' % (hmm, where, kg, margin * 1000, '' if chk else '_nocheck') + vt + tn, o)
elif cmd == 'stepempty':
    # the robot without a bin over the 40 mm step (their step geometry): more than half its weight is on the castors, which are not driven
    side, v = sys.argv[2], float(sys.argv[3]); STEP_AT = float(os.environ.get('X_STEP_AT', '3.0')); bp = (30.0, float(os.environ.get('X_STEP_H', '0.040')), 0.40 if side == 'one' else 0.0, 0.25 if side == 'one' else 2.0)
    p = B.bin_params('ESE240SL'); S = B.SimB('ESE240SL', p, with_bin=False, terrain='bump', bump=bp); scale_mass(S); R = B.RunnerB(S); R.run_for(0.5)
    gb = S.gid['bump']; S.m.geom_pos[gb][0] = float(S.d.xpos[S.bid['tug']][0]) + STEP_AT; mujoco.mj_forward(S.m, S.d); psi0 = S.rpy()[2]
    xs = S.d.xpos[S.bid['tug']].copy(); dist = lambda: float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2] - xs[:2])); MX = dict(wheel=0.0)
    def mon():
        if R.i % 4: return
        C = S.contacts(); MX['wheel'] = max(MX['wheel'], C['driveL'], C['driveR'])
    YAW = float(os.environ.get('X_STEP_YAW', '0'))
    R.mon = mon; R.ctrl_fn = B.heading_hold(R, v, psi0 + YAW); ok = R.until(lambda: dist() >= STEP_AT + 2.9, 40.0); R.ctrl_fn = None; B.soft_stop(R); R.run_for(1.0)
    dump('stepempty_%s_v%02d%s' % (side, round(v * 10), ('_yaw%02d' % round(YAW) if YAW else '') + ('_h%02d' % round(float(os.environ['X_STEP_H']) * 1000) if os.environ.get('X_STEP_H') else '')), dict(test='step_empty', step_h_mm=float(os.environ.get('X_STEP_H', '0.040')) * 1000, yaw_deg=YAW, side=side, v=v, step_at_m=STEP_AT, reached=bool(ok), dist_m=round(dist(), 2), tcap=B.GEO['tcap'], wheel_peak_N=round(MX['wheel']),
         yaw_end_deg=round(S.rpy()[2] - psi0, 1), boost=getattr(R, '_bst', None), events=R.events[-6:]))
elif cmd == 'lat':
    kg = float(sys.argv[2]); S, R, g = nominal('ESE240SL', kg) if kg > 0 else nobin(); psi0 = S.rpy()[2]; PH = {}; cur = ['']
    gd = [S.gid['driveL'], S.gid['driveR']]; f6 = np.zeros(6)
    def mon():
        if R.i % 4: return
        Rt = S.d.xmat[S.bid['tug']].reshape(3, 3); lat = [0.0, 0.0]; nrm = [0.0, 0.0]
        for i in range(S.d.ncon):
            c = S.d.contact[i]
            for k, gg in enumerate(gd):
                if c.geom1 == gg or c.geom2 == gg:
                    mujoco.mj_contactForce(S.m, S.d, i, f6); fw = c.frame.reshape(3, 3).T @ f6[:3]; lat[k] += float(Rt[:, 1] @ fw); nrm[k] += float(f6[0])
        d_ = PH.setdefault(cur[0], dict(lat=0.0, normal=0.0, roll=0.0)); d_['lat'] = max(d_['lat'], abs(lat[0]), abs(lat[1])); d_['normal'] = max(d_['normal'], nrm[0], nrm[1]); d_['roll'] = max(d_['roll'], abs(S.rpy()[0]))
    R.mon = mon
    cur[0] = 'straight 0.5 m/s'; R.ctrl_fn = B.heading_hold(R, 0.5, psi0); R.run_for(4.0)
    cur[0] = 'turn 0.5 m/s, 0.5 rad/s'; R.ctrl_fn = None
    def turn(v, om):
        R.w = v / B.RW; R.wd = om * 2 * B.GEO['track'] / B.RW; R.brake = False
    turn(0.5, 0.5); R.run_for(4.0)
    cur[0] = 'slalom +/-25 deg'
    for sg in (1, -1, 1, -1): R.ctrl_fn = B.heading_hold(R, 0.5, S.rpy()[2] + sg * 25.0); R.run_for(2.5)
    R.ctrl_fn = None; B.soft_stop(R)
    cur[0] = 'pivot 180 deg on the spot'; turn(0.0, 0.5); R.run_for(6.5); R.hold(); R.run_for(1.0)
    cur[0] = 'e-stop from 0.5 m/s in a turn'; turn(0.5, 0.4); R.run_for(3.0); R.hold(); R.run_for(2.0)
    cur[0] = '12 % cross slope: ramp on'; psi1 = S.rpy()[2]; R.ramp_grade(0.0, 0.12, 2.0); R.run_for(1.0)
    cur[0] = '12 % cross slope: drive 0.5 m/s'; R.ctrl_fn = B.heading_hold(R, 0.5, psi1); R.run_for(5.0); R.ctrl_fn = None
    cur[0] = '12 % cross slope: e-stop'; R.hold(); R.run_for(2.0)
    o = dict(test='drive_tyre_sideways_force', bin_kg=kg, grab=g['result'], phases={k: {a: round(b, 1) for a, b in v.items()} for k, v in PH.items()}, max_lat_N=round(max(v['lat'] for v in PH.values())), captured_end=(S.captured() if kg > 0 else None))
    dump('lat_k%d' % kg, o)
elif cmd == 'liftpeak':
    kind, side, v = sys.argv[2], sys.argv[3], float(sys.argv[4]); STEP_AT = float(os.environ.get('X_STEP_AT', '1.6'))    # their step test puts the edge 1.6 m ahead of the axle: the castors meet it 0.55 m after the robot has reversed onto the bin
    if kind == 'step':
        bp = (30.0, float(os.environ.get('X_STEP_H', '0.040')), 0.40 if side == 'one' else 0.0, 0.25 if side == 'one' else 2.0); S, R, g = nominal('ESE240SL', 110, terrain='bump', bump=bp)
        gb = S.gid['bump']; S.m.geom_pos[gb][0] = float(S.d.xpos[S.bid['tug']][0]) + STEP_AT; sg = 1
    else:
        bp = (30.0, 0.040, 0.0, 2.0); S, R, g = nominal('ESE240SL', 110, terrain='bump', bump=bp); gb = S.gid['bump']; sg = 1 if side == 'nose' else -1
        S.m.geom_pos[gb][0] = float(S.d.xpos[S.bid['tug']][0]) + sg * 1.6
    if os.environ.get('H2_TYRE_POST'):
        sr, _, si = os.environ['H2_TYRE_POST'].partition(';'); vv = [float(x) for x in sr.split(',')]
        for n in ('driveL', 'driveR'):
            gg = S.gid[n]; S.m.geom_solref[gg] = vv; S.m.geom_priority[gg] = 1
            if si: S.m.geom_solimp[gg][:3] = [float(x) for x in si.split(',')]
    mujoco.mj_forward(S.m, S.d); psi0 = S.rpy()[2]; MX = dict(lift=0.0, liftq_min=9.0, liftq_max=-9.0, wheel=0.0, comb=0.0, pad=0.0, seated=True, bin_ground=0.0, slip=0.0)
    qh = S.lift_q()
    def mon():
        if R.i % 4: return
        C = S.contacts(); F = abs(S.lift_force()); MX['lift'] = max(MX['lift'], F); q = S.lift_q(); MX['liftq_min'] = min(MX['liftq_min'], q); MX['liftq_max'] = max(MX['liftq_max'], q)
        MX['wheel'] = max(MX['wheel'], C['driveL'], C['driveR']); MX['comb'] = max(MX['comb'], S.pair('nib', 'ledge') + S.pair('tooth', 'rim') + S.pair('nib', 'rim') + S.pair('tooth', 'ledge')); MX['pad'] = max(MX['pad'], C['padg'])
        MX['seated'] = MX['seated'] and S.seated(); MX['bin_ground'] = max(MX['bin_ground'], S.bin_ground())
    R.mon = mon; xs = S.d.xpos[S.bid['tug']].copy(); dist = lambda: float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2] - xs[:2]))
    sw = {}
    def swiv(): return [round(math.degrees(float(S.d.qpos[S.jq('swivel' + c)])) % 360.0, 1) for c in 'LR']
    sw['start'] = swiv()
    _m0 = mon
    def mon2():
        _m0()
        if 'at_step' not in sw and kind == 'step' and dist() >= STEP_AT - B.GEO['cx'] - B.GEO['cr'] - 0.03: sw['at_step'] = swiv()
    R.mon = mon2
    YAW = float(os.environ.get('X_STEP_YAW', '0'))   # meet the edge at this angle (deg) instead of square on
    R.ctrl_fn = B.heading_hold(R, sg * v, psi0 + YAW); ok = R.until(lambda: dist() >= 4.5 + (STEP_AT - 1.6 if kind == 'step' else 0), 40.0); R.ctrl_fn = None; B.soft_stop(R); R.run_for(1.0)
    o = dict(test='lift_shock', step_at_m=STEP_AT, kind=kind, side=side, v=v, grab=g['result'], reached=bool(ok), dist_m=round(dist(), 2), act_cap_N=B.GEO['act_N'], tcap=B.GEO['tcap'], tyre=os.environ.get('H2_TYRE_POST', 'rigid'),
             lift_peak_N=round(MX['lift']), lift_static_N=round(abs(S.lift_force())), carriage_sag_mm=round((qh - MX['liftq_min']) * 1000, 2), wheel_peak_N=round(MX['wheel']), comb_peak_N=round(MX['comb']), pad_peak_N=round(MX['pad']),
             castor_swivel_deg=sw, seated_all=MX['seated'], bin_ground_N=round(MX['bin_ground']), captured_end=S.captured(), boost=getattr(R, '_bst', None), events=R.events[-6:])
    o['yaw_deg'] = YAW; o['heading_end_deg'] = round(S.rpy()[2] - psi0, 1)
    dump('liftpeak_%s_%s_v%02d%s%s' % (kind, side, round(v * 10), '' if STEP_AT == 1.6 else '_at%02d' % round(STEP_AT * 10), ('_yaw%02d' % round(YAW) if YAW else '') + ('_h%02d' % round(float(os.environ['X_STEP_H']) * 1000) if os.environ.get('X_STEP_H') else '')), o)
