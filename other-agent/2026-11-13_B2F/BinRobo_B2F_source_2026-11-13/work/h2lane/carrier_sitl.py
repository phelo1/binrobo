#!/usr/bin/env python3
"""S9 carrier lane SITL (kinematic, Python, NO ArduPilot binary in the loop).

Re-models the G6 lane SITL for a straddle CARRIER: one rigid differential-drive body that carries the bin (no hitch, no
relay flip), pivots on the spot about the drive-axle centre. Same site as sitl/scripts_g6 (OSM lane 633 m, truth hedge faces
with irregularity, overgrown narrowings and gaps, yard, bell-mouth, private boundary, pads A/M/F, home spots, dock) and the
G6 scenario definitions (positions, zones, obstacles copied from scenarios.py). Footprints = the S8 lane-fit designs.

What is simulated: pure-pursuit path following on the ESTIMATED pose (truth = estimate - error), speed / accel / yaw-rate
limits, pivots, localisation error by GPS zone (RTK fix / float / none) with the G6 corridor (lidar hedge fit) lateral aid in
the lane, dead reckoning with along-lane uncertainty growth and the G6 hold rule, obstacle detection (LD06 12 m, front
sector) with stop / resume and a lateral by-pass of static objects, the G4 home-slot alternate rule, energy (traction on the
DEM grade + rolling + accel + pivot + hotel + lights + lift) and motor current. Fixed manoeuvre times (lift, set-down,
junction wait, dock) are taken from revH2/sim/mission.py so the comparison with mission.json is like for like.

Strict scoring (declared in S9_THRESHOLDS before any run): truth hedge clearance < 0 = FAIL; region (yard edge / mouth /
legal 0.3 m) margin < 0 = FAIL; footprint overlapping a standing bin, car, branch or person = FAIL; bin-bin gap < 0.05 m =
FAIL; placement error > 0.6 m or handle direction off by > 20 deg = FAIL; outcome must equal the declared expectation.

Chunked + resumable: state is pickled after every chunk (python carrier_sitl.py <design> <scenario> <budget_s>)."""
import os, sys, json, math, time, pickle, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.abspath(os.path.join(H, '..', '..'))
sys.path.insert(0, os.path.join(P, 'revG', 'sim', 'cg', 'b2')); sys.path.insert(0, os.path.join(P, 'revG', 'sim', 'cg', 'cmp'))
import lanefit_b2 as L2
LF = L2.LF; SC = LF.SC; S = LF.S; LANE = LF.LANE; G6 = LF.G6; L = LF.L; M0 = LF.M0
OUT = os.path.join(H, 'sitl_out'); os.makedirs(OUT, exist_ok=True)
G = 9.81
S9_THRESHOLDS = dict(hedge_strict_m=0.0, region_m=0.0, obstacle_overlap_m=0.0, bin_gap_m=0.05, placement_m=0.6, handle_deg=20.0,
                     person_gap_m=0.3, review_hedge_m=0.10, est_p95_ref_m=0.124, declared='2026-11-12 before the first S9 run')
# ------------------------------------------------------------------------------------------------ designs
DESIGNS = {
 'RevH2': dict(json='RevH2_b2r.json', mass=91.0, mass_donor=102.2, track=0.97, r_wheel=0.159, kt_wheel=1.0, kt_wheel_phys=1.5,
               ctrl_cont_A=30.0, ctrl_peak_A=60.0, ctrl='RoboClaw 2x30A', batt={'AGM 2x18Ah (new)': (24.0, 18.0, 'AGM', 102.2 - 11.2),
                                                                                   'donor AGM pair 40Ah': (24.0, 40.0, 'AGM', 102.2)}),
 'B2F': dict(json='B2F_b2r.json', mass=92.3, mass_donor=105.5, track=0.80, r_wheel=0.165, kt_wheel=52.7 / 25.8, kt_wheel_phys=52.7 / 25.8,
             ctrl_cont_A=30.0, ctrl_peak_A=60.0, ctrl='RoboClaw 2x30A', batt={'LFP 24V 20Ah': (25.6, 20.0, 'LFP', 92.3)}),
}
A = dict(v_cruise=0.5, v_slow=0.4, v_manoeuvre=0.25, v_rev=0.20, acc=0.25, w_max=0.6, w_pivot=0.40, look=1.5, look_m=0.6,
         crr=0.03, eta=0.60, hotel_w=9.0, lights_w=17.0, lift_w=50.0,
         t_lift=30, t_warn=3, t_setdown=26, t_pull=5, t_photo=3, t_junction=10, t_dock=35, t_seek=15, t_undock=10,
         gps_fix_sd=0.02, gps_float_sd=0.25, corridor_sd=0.063, dr_growth=0.03, dr_hold_m=2.5, tau_fix=10.0, tau_float=30.0,
         lidar_range=12.0, stop_margin=1.0, resume_clear_s=2.0, dt=0.1, chk_dt=0.5)
YARD_S1 = LANE.yard[1]

def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
def box_pts(x, y, yaw, Lx, Wy, n=6):
    pts = []
    for i in range(n):
        f = -0.5 + i / (n - 1)
        pts += [(f * Lx, Wy / 2), (f * Lx, -Wy / 2), (Lx / 2, f * Wy), (-Lx / 2, f * Wy)]
    return LF.tf(pts, x, y, yaw)
def pt_box(p, b):   # signed distance of points to a box dict(x,y,yaw,L,W)
    return LF.pt_box_dist(p, b['x'], b['y'], b['yaw'], w=b['W'], d=b['L'])

class Body:
    def __init__(s, dname):
        s.dn = dname; s.cfg = DESIGNS[dname]; D = json.load(open(os.path.join(H, s.cfg['json'])))
        L2.KL = D.get('kl_gap'); L2.SRUN = D.get('pivot_strategy') == 'srun'; L2.GUARD = D.get('guard', 0.25)
        s.d = LF.Design(D); s.D = D
        s.out_empty = s.d.outline[::2]; s.binp = s.d.binp[::2]
    def fp(s, x, y, yaw, loaded):
        return LF.tf(np.vstack([s.out_empty, s.binp]) if loaded else s.out_empty, x, y, yaw)

# ------------------------------------------------------------------------------------------------ scenarios (G6 geometry)
def hold_pose(body, bx, by, byaw):        # robot pose holding a bin whose handle points byaw (front-wall carrier: handle_dir -1)
    return LF.robot_at_bin(body.d, bx, by, byaw)
def bin_pose_from_robot(body, x, y, yaw):
    c, s_ = math.cos(yaw), math.sin(yaw); bc = body.d.bin_c
    byaw = yaw if body.d.hd > 0 else wrap(yaw + math.pi)
    return x + c * bc[0] - s_ * bc[1], y + s_ * bc[0] + c * bc[1], byaw
def pad_bin(name, handle_to='road', jit=(0, 0, 0)):
    sp = SC.DROP_SPOTS(S)[name]; s0 = sp['s'] + jit[0]; lat = sp['lat'] + jit[1]
    x, y, h = S.pose(s0, lat, 0.0); byaw = wrap(h + (math.pi if handle_to == 'lane' else 0.0) + math.radians(jit[2]))
    return dict(x=float(x), y=float(y), yaw=byaw, L=0.74, W=0.58, kind='bin', name=name)
def home_bin(col):
    hs = SC.HOME_SPOTS[col]; x, y, h = S.pose(hs['s'], hs['lat'], 0.0)   # handles face down-lane
    return dict(x=float(x), y=float(y), yaw=float(h), L=0.74, W=0.58, kind='bin', name=col)
def dock_box():
    dx, dy, dyaw = S.pose(SC.DOCK['s'], SC.DOCK['lat'], 0.0)
    return dict(x=dx - 0.8 * math.cos(dyaw), y=dy - 0.8 * math.sin(dyaw), yaw=dyaw, L=0.74, W=0.58, kind='dock', name='dock')

def scenario(name):
    """returns dict: start pose, plan (list of ops), bins (dict), obstacles, movers, zones, night, air_c, expect, mass of bins."""
    dk = S.pose(SC.DOCK['s'], SC.DOCK['lat'], 0.0)
    if name == 's1_morning':
        return dict(start=dk, night=False, air=8.0, expect='pass', zones=[], movers=[], obst=[],
                    bins={'black': dict(home_bin('black'), kg=55.0)}, plan=[('drop', 'black', 'A')])
    if name == 's1n_night_drop':
        return dict(start=dk, night=True, air=4.0, expect='pass', zones=[], movers=[], obst=[],
                    bins={'black': dict(home_bin('black'), kg=55.0)}, plan=[('drop', 'black', 'A')])
    if name == 's3_night_pickup':
        dn = SC.drop_nominal(S); x, y, h = S.pose(dn['s'] - 0.8, dn['lat'] - 0.6, 0.0)
        b = dict(x=float(x), y=float(y), yaw=wrap(h + math.pi + math.radians(30)), L=0.74, W=0.58, kind='bin', name='black', kg=13.0)
        # G6 s3 bin: handle to the house, rotated 30 deg, ~1 m off pad A. Carrier: bin is fetched as found and set down at home.
        return dict(start=dk, night=True, air=5.0, expect='pass', zones=[], movers=[], obst=[], bins={'black': b},
                    plan=[('pickup', 'black', 'home:black')])
    if name == 's20a_three_bin_drop':
        bins = {c: dict(home_bin(c), kg=55.0) for c in ('black', 'green', 'brown')}
        return dict(start=dk, night=True, air=0.5, expect='pass', zones=[], movers=[], obst=[], bins=bins,
                    plan=[('drop', 'black', 'A'), ('drop', 'green', 'M'), ('drop', 'brown', 'F')])
    if name == 's20b_three_bin_pickup':
        jit = {'black': (0.2, 0.1, 6), 'green': (-0.3, -0.15, -9), 'brown': (0.25, -0.1, 12)}
        pads = {'brown': 'F', 'green': 'M', 'black': 'A'}
        bins = {c: dict(pad_bin(pads[c], 'road', jit[c]), name=c, kg=13.0) for c in pads}
        return dict(start=dk, night=True, air=0.5, expect='pass', zones=[], movers=[], obst=[], bins=bins,
                    plan=[('pickup', 'brown', 'home:brown'), ('pickup', 'green', 'home:green'), ('pickup', 'black', 'home:black')])
    if name == 's24a_home_slot_car':
        x, y, yaw = S.pose(9.0, -1.6, 0.03); car = dict(kind='car', x=float(x), y=float(y), yaw=float(yaw), L=4.3, W=1.8, name='car')
        # carrier version: arrives from s 60 carrying the empty black bin (handle to the road); black home slot blocked by a car
        hx, hy, hyaw = S.pose(60.0, 0.0, math.pi)
        return dict(start=(hx, hy, hyaw), night=True, air=5.0, expect='pass', zones=[], movers=[], obst=[car],
                    bins={'black': dict(kind='bin', x=0, y=0, yaw=0, L=0.74, W=0.58, name='black', kg=13.0, carried=True)},
                    plan=[('home_with', 'black', 'home:black')], carried='black')
    if name == 's7_rtk_dropout':
        hx, hy, hyaw = S.pose(120.0, 0.0, math.pi)
        return dict(start=(hx, hy, hyaw), night=False, air=8.0, expect='pass', movers=[], obst=[],
                    zones=[(60, 110, 'float'), (84, 90, 'none'), (20, 58, 'float'), (28, 52, 'none')],
                    bins={'black': dict(kind='bin', x=0, y=0, yaw=0, L=0.74, W=0.58, name='black', kg=13.0, carried=True)},
                    plan=[('lane', 12.0, -1)], carried='black')
    if name == 's7b_rtk_long_loss':
        hx, hy, hyaw = S.pose(330.0, 0.0, math.pi)
        return dict(start=(hx, hy, hyaw), night=False, air=8.0, expect='alert', movers=[], obst=[], zones=[(100, 300, 'none')],
                    bins={'black': dict(kind='bin', x=0, y=0, yaw=0, L=0.74, W=0.58, name='black', kg=13.0, carried=True)},
                    plan=[('lane', 30.0, -1)], carried='black')
    if name == 's5_person_dog':
        s0 = 300.0; hx, hy, hyaw = S.pose(s0, 0.0, 0.0)
        mv = [dict(kind='person', s_cross=s0 + 25, r=0.25, v=0.9, trig=4.2, lat0=-3.2, lat1=3.2, pause=4.0),
              dict(kind='dog', s_cross=s0 + 60, r=0.20, v=2.0, trig=4.0, lat0=3.0, lat1=-3.2, pause=4.0)]
        return dict(start=(hx, hy, hyaw), night=False, air=8.0, expect='pass', zones=[], movers=mv, obst=[],
                    bins={'black': dict(kind='bin', x=0, y=0, yaw=0, L=0.74, W=0.58, name='black', kg=55.0, carried=True)},
                    plan=[('lane', s0 + 90, 1)], carried='black')
    if name == 's6_branch':
        s0 = 420.0; x, y, yaw = S.pose(s0 + 22, -0.85, 0.25); hx, hy, hyaw = S.pose(s0, 0.0, 0.0)
        br = dict(kind='branch', x=float(x), y=float(y), yaw=float(yaw), L=2.2, W=0.5, name='branch')
        return dict(start=(hx, hy, hyaw), night=False, air=8.0, expect='pass', zones=[], movers=[], obst=[br],
                    bins={'black': dict(kind='bin', x=0, y=0, yaw=0, L=0.74, W=0.58, name='black', kg=55.0, carried=True)},
                    plan=[('lane', s0 + 50, 1)], carried='black')
    raise KeyError(name)
SCEN = ['s1_morning', 's1n_night_drop', 's3_night_pickup', 's20a_three_bin_drop', 's20b_three_bin_pickup', 's24a_home_slot_car',
        's7_rtk_dropout', 's7b_rtk_long_loss', 's5_person_dog', 's6_branch']

# ------------------------------------------------------------------------------------------------ the simulator
class Sim:
    def __init__(s, dname, scname, seed=7, mass_key=None):
        s.body = Body(dname); s.dn = dname; s.sc = scname; s.cfg = s.body.cfg; sc = scenario(scname); s.spec = sc
        s.rng = np.random.default_rng(seed); s.t = 0.0
        s.x, s.y, s.yaw = map(float, sc['start']); s.v = 0.0; s.w = 0.0
        s.bins = {k: dict(v) for k, v in sc['bins'].items()}; s.carry = sc.get('carried'); s.obst = list(sc['obst']) + [dock_box()]
        s.movers = [dict(m, t0=None) for m in sc['movers']]; s.zones = sc['zones']; s.night = sc['night']; s.air = sc['air']
        s.m_robot = s.cfg['mass']
        s.err = np.zeros(2); s.dr_unc = 0.0; s.dr_mode = False; s.hold_t = 0.0
        s.ops = list(sc['plan']); s.queue = []; s.done = False; s.outcome = None; s.alerts = []; s.events = []
        s.E = dict(total_wh=0.0, drive_wh=0.0, hotel_wh=0.0, lift_wh=0.0); s.odo = 0.0
        s.metrics = dict(hedge_min=9.0, hedge_at=None, region_min=9.0, region_at=None, obst_min=9.0, obst_at=None, bin_min=9.0,
                         bin_at=None, person_min=9.0, stops=0, n_hedge_below_review=0, est_lat_abs=[], placements=[], pivots=0,
                         i_motor_max=0.0, i_motor_max_at=None, i_motor_max_12=0.0, lat_err_samples=0)
        s.engaged = set(); s.metrics['engaged_min'] = 9.0
        s.trace = []; s.last_chk = -9.0; s.stop_until = None; s.clear_since = None; s.bypass = 0.0
        s.wall = 0.0
    # ---------------------------------------------------------------- environment
    def zone(self, s_):
        z = 'fix'
        for a, b, k in self.zones:
            if a <= s_ <= b:
                if k == 'none': return 'none'
                z = 'float'
        return z
    def mover_pos(self, m):
        a = LANE.point(m['s_cross'], m['lat0']); b = LANE.point(m['s_cross'], m['lat1']); Lab = float(np.linalg.norm(b - a))
        if m['t0'] is None:
            if math.hypot(self.x - (a[0] + b[0]) / 2, self.y - (a[1] + b[1]) / 2) < m['trig']: m['t0'] = self.t
            else: return None
        d = (self.t - m['t0']) * m['v']; mid = Lab * 0.45
        if d > mid: d = mid + max(0.0, d - mid - m['pause'] * m['v'])
        if d >= Lab: return None
        return a + (b - a) * d / Lab
    def obstacles_now(self):
        ob = [o for o in self.obst]
        for k, b in self.bins.items():
            if k != self.carry: ob.append(b)
        return ob
    # ---------------------------------------------------------------- localisation
    def loc_step(self, dt):
        s_, lat = LANE.project(np.array([self.x, self.y])); z = self.zone(s_)
        in_lane = YARD_S1 + 1 < s_ < M0 - 1
        if z == 'fix': sd, tau = A['gps_fix_sd'], A['tau_fix']; self.dr_unc = 0.0; self.dr_mode = False
        elif z == 'float': sd, tau = A['gps_float_sd'], A['tau_float']; self.dr_unc = 0.0; self.dr_mode = False
        else:
            self.dr_mode = True; self.dr_unc += A['dr_growth'] * abs(self.v) * dt; sd, tau = None, None
        if sd is not None:
            a = math.exp(-dt / tau); self.err = a * self.err + math.sqrt(1 - a * a) * sd * self.rng.standard_normal(2)
        else:
            self.err[0] += 0.02 * abs(self.v) * dt * self.rng.standard_normal()        # along-lane DR drift
        if in_lane:   # corridor (lidar hedge fit) aid on the lateral component
            self.err[1] = float(np.clip(self.err[1], -2.5 * A['corridor_sd'], 2.5 * A['corridor_sd'])) if z != 'fix' else self.err[1]
            if z != 'fix': self.err[1] = 0.9 * self.err[1] + 0.1 * A['corridor_sd'] * self.rng.standard_normal()
        return s_, lat, z
    def est_pose(self):
        h = LANE.heading(LANE.project(np.array([self.x, self.y]))[0]); c, s_ = math.cos(h), math.sin(h)
        ex = c * self.err[0] - s_ * self.err[1]; ey = s_ * self.err[0] + c * self.err[1]
        return self.x + ex, self.y + ey, self.yaw
    # ---------------------------------------------------------------- energy / current
    def power(self, v, w, acc, extra_w=0.0):
        m = self.m_robot + (self.bins[self.carry]['kg'] if self.carry else 0.0)
        s_, _ = LANE.project(np.array([self.x, self.y]))
        z0 = S.ter.z(self.x, self.y); z1 = S.ter.z(self.x + 0.5 * math.cos(self.yaw), self.y + 0.5 * math.sin(self.yaw))
        grade = (z1 - z0) / 0.5 * (1 if v >= 0 else -1)
        crr = A['crr'] * (1.15 if self.air <= 2 else 1.0)                 # cold grease / tyre allowance at ~0 C (assumed)
        F = m * G * (crr + grade) + m * acc * (1 if v >= 0 else -1)
        Pw = max(0.0, F * abs(v)) + crr * m * G * abs(w) * 0.55            # pivot: wheels + castors roll on ~0.55 m mean radius
        Pd = Pw / A['eta']
        Pt = Pd + A['hotel_w'] + (A['lights_w'] if self.night else 0.0) + extra_w
        T_wheel = max(F, crr * m * G) * self.cfg['r_wheel'] / 2 + (crr * m * G * 0.55 * self.cfg['r_wheel'] / (self.cfg['track'] / 2) / 2 if abs(w) > 0.05 else 0.0)
        I = T_wheel / self.cfg['kt_wheel']
        return Pt, Pd, I, grade
    def account(self, dt, v, w, acc, extra_w=0.0):
        Pt, Pd, I, grade = self.power(v, w, acc, extra_w)
        self.E['total_wh'] += Pt * dt / 3600; self.E['drive_wh'] += Pd * dt / 3600
        self.E['hotel_wh'] += (A['hotel_w'] + (A['lights_w'] if self.night else 0.0)) * dt / 3600; self.E['lift_wh'] += extra_w * dt / 3600
        if I > self.metrics['i_motor_max']: self.metrics['i_motor_max'] = I; self.metrics['i_motor_max_at'] = (round(self.t), round(grade, 3))
        if grade > 0.10: self.metrics['i_motor_max_12'] = max(self.metrics['i_motor_max_12'], I)
    # ---------------------------------------------------------------- checks (truth)
    def check(self, force=False):
        if not force and self.t - self.last_chk < A['chk_dt']: return
        self.last_chk = self.t; loaded = self.carry is not None
        P = self.body.fp(self.x, self.y, self.yaw, loaded); M = self.metrics; s_, _ = LANE.project(np.array([self.x, self.y]))
        hmin = 9.0; rmin = 9.0
        for p in P[::2]:
            m, k = LF.region_margin(p)
            if k == 'hedge': hmin = min(hmin, m)
            rmin = min(rmin, m)
        if hmin < M['hedge_min']: M['hedge_min'] = round(hmin, 3); M['hedge_at'] = round(float(s_), 1)
        if rmin < M['region_min']: M['region_min'] = round(rmin, 3); M['region_at'] = round(float(s_), 1)
        if hmin < A.get('review', 0.10): M['n_hedge_below_review'] += 1
        for o in self.obstacles_now():
            dd = float(np.min(pt_box(P, o)))
            if o['name'] in self.engaged: M['engaged_min'] = min(M['engaged_min'], round(dd, 3)); continue
            if o['kind'] == 'bin':
                if dd < M['bin_min']: M['bin_min'] = round(dd, 3); M['bin_at'] = '%s t=%.0f s=%.1f' % (o['name'], self.t, s_)
            elif dd < M['obst_min']: M['obst_min'] = round(dd, 3); M['obst_at'] = o['name']
        for m in self.movers:
            p = self.mover_pos(m)
            if p is not None and abs(self.v) > 0.02: M['person_min'] = min(M['person_min'], round(float(np.min(np.linalg.norm(P - p, axis=1))) - m['r'], 3))
            if p is not None: M['person_min_any'] = min(M.get('person_min_any', 9.0), round(float(np.min(np.linalg.norm(P - p, axis=1))) - m['r'], 3))
        if len(self.trace) == 0 or self.t - self.trace[-1][0] >= 5.0:
            self.trace.append((round(self.t, 1), round(self.x, 2), round(self.y, 2), round(self.yaw, 3), round(float(s_), 1), round(self.E['total_wh'], 2)))
    # ---------------------------------------------------------------- obstacle reaction (lidar, front sector along travel)
    def blocked_ahead(self, dirn):
        """True if a mover or obstacle is inside the swept corridor ahead within stopping distance + margin."""
        loaded = self.carry is not None; c, s_ = math.cos(self.yaw), math.sin(self.yaw)
        look = abs(self.v) ** 2 / (2 * A['acc']) + A['stop_margin'] + 0.3
        P = self.body.fp(self.x + dirn * look * c, self.y + dirn * look * s_, self.yaw, loaded)
        Ps = [self.body.fp(self.x + dirn * f * look * c, self.y + dirn * f * look * s_, self.yaw, loaded)[::2] for f in (0.0, 0.33, 0.67, 1.0)]
        for m in self.movers:
            p = self.mover_pos(m)
            if p is None: continue
            if min(float(np.min(np.linalg.norm(Q - p, axis=1))) for Q in Ps) < m['r'] + 0.45: return 'mover'
        for o in self.obst:
            if o['kind'] in ('car', 'branch') and float(np.min(pt_box(P, o))) < 0.15: return o['name']
        return None
    # ---------------------------------------------------------------- motion primitives (each returns True when finished)
    def step_motion(self, v_cmd, w_cmd, dt):
        acc = float(np.clip((v_cmd - self.v) / dt, -A['acc'], A['acc'])); self.v += acc * dt
        self.w = float(np.clip(w_cmd, -A['w_max'], A['w_max']))
        self.x += self.v * math.cos(self.yaw) * dt; self.y += self.v * math.sin(self.yaw) * dt; self.yaw = wrap(self.yaw + self.w * dt)
        self.odo += abs(self.v) * dt; self.t += dt; self.account(dt, self.v, self.w, acc); self.loc_step(dt); self.check()
    def op_wait(self, secs, extra_w=0.0, label=''):
        n = int(round(secs / 1.0))
        for _ in range(n):
            self.t += 1.0; self.account(1.0, 0.0, 0.0, 0.0, extra_w)
        self.events.append((round(self.t), 'wait %s %ds' % (label, secs)))
    def op_pivot(self, yaw_t):
        self.metrics['pivots'] += 1; dt = A['dt']; n = 0
        while abs(wrap(yaw_t - self.yaw)) > 0.02 and n < 3000:
            e = wrap(yaw_t - self.yaw); w = math.copysign(min(A['w_pivot'], 1.5 * abs(e) + 0.05), e)
            self.v = 0.0; self.w = w; self.yaw = wrap(self.yaw + w * dt); self.t += dt; n += 1
            self.account(dt, 0.0, w, 0.0); self.loc_step(dt); self.check()
        self.check(force=True)
    def op_line(self, xt, yt, reverse=False, v_max=None):
        """drive (or reverse) to a point with pure pursuit on the estimate; heading is not forced at the end."""
        dt = A['dt']; v_max = v_max or (A['v_rev'] if reverse else A['v_manoeuvre']); n = 0; sg = -1 if reverse else 1
        while n < 6000:
            ex, ey, eyaw = self.est_pose(); dx, dy = xt - ex, yt - ey; dist = math.hypot(dx, dy)
            if dist < 0.04: break
            hd = math.atan2(dy, dx) if not reverse else wrap(math.atan2(dy, dx) + math.pi)
            e = wrap(hd - eyaw)
            if dist > 0.3 and abs(e) > math.radians(35):   # too far off: square up on the spot first
                self.op_pivot(wrap(self.yaw + e)); continue
            v = sg * min(v_max, 0.6 * dist + 0.05); w = 2.0 * e * abs(v) / max(0.5, min(A['look_m'], dist)) if dist > 0.15 else 0.0
            if not self.may_move(sg, 'manoeuvre'):
                n += 1
                if self.outcome: return
                continue
            self.step_motion(v, w, dt); n += 1
        self.v = 0.0; self.check(force=True)
    def may_move(self, dirn, why):
        """stop while blocked; resume only after the corridor has been clear for resume_clear_s."""
        if self.blocked_ahead(dirn): self.clear_since = None; self.hold_step(why); return False
        if self.stop_until is not None:
            if self.clear_since is None: self.clear_since = self.t
            if self.t - self.clear_since < A['resume_clear_s']: self.hold_step(why); return False
            self.events.append((round(self.t), 'resume after %.0f s' % (self.t - self.stop_until))); self.stop_until = None; self.clear_since = None
        return True
    def hold_step(self, why):
        self.v = 0.0; self.t += A['dt']; self.account(A['dt'], 0.0, 0.0, 0.0); self.loc_step(A['dt']); self.check()
        if self.stop_until is None: self.stop_until = self.t; self.metrics['stops'] += 1; self.events.append((round(self.t), 'STOP: %s' % why))
        if self.t - self.stop_until > 120:
            self.outcome = 'alert'; self.alerts.append('blocked > 120 s (%s): hold + alert' % why)
    def lane_target(self, s_, sgn):
        hw = self.body.d.half_w
        if getattr(self, 'lat_force', None) is not None: return self.lat_force
        return LF.lane_target(s_, sgn, hw) + self.bypass
    def pass_bin(self, b, s_goal):
        """drive past a standing bin on its free side (lateral chosen with the largest truth clearance to region and bins)
        before manoeuvring on its far side."""
        sb, lb = LANE.project(np.array([b['x'], b['y']])); hw = self.body.d.half_w; best = None
        for lat in np.arange(-4.0, 4.01, 0.1):
            m = 9.0
            for ds in np.arange(-2.0, 2.01, 0.5):
                x, y = LANE.point(sb + ds, lat); P = self.body.fp(x, y, LANE.heading(sb + ds), self.carry is not None)
                for p in P[::3]: m = min(m, LF.region_margin(p)[0])
                for o in self.obstacles_now(): m = min(m, float(np.min(pt_box(P, o))) - 0.05)
            if best is None or m > best[0]: best = (m, lat)
        self.events.append((round(self.t), 'pass bin %s at lat %.1f (planned margin %.2f m)' % (b['name'], best[1], best[0])))
        self.lat_force = float(best[1]); self.op_lane(s_goal, 1); self.lat_force = None
    def loaded_turn_home(self):
        """holding a bin nose-down after a pickup: find a pivot spot near here whose loaded disc is clear, go there, pivot up-lane."""
        s0, l0 = LANE.project(np.array([self.x, self.y])); r = self.body.d.r_load; obs = [(o['x'], o['y'], o['yaw']) for o in self.obstacles_now()]
        best = None
        for ds in np.arange(-6.0, 6.01, 0.5):
            for lat in np.arange(-4.0, 4.01, 0.25):
                c = LANE.point(s0 + ds, lat); m = LF.disc_ok(c, r, obs)
                if m > 0.05:
                    d = abs(ds) + abs(lat - l0)
                    if best is None or d < best[0]: best = (d, c, m)
        if best is None: self.events.append((round(self.t), 'no loaded pivot spot')); return
        self.op_line(best[1][0], best[1][1]); self.op_pivot(LANE.heading(LANE.project(best[1])[0]) + math.pi)
    def op_lane(self, s_goal, sgn, v_cruise=None):
        """follow the lane (keep-left / centring rule of the S8 lane fit, B2 route rules) to station s_goal."""
        dt = A['dt']; n = 0; v_cruise = v_cruise or A['v_cruise']
        while n < 40000:
            ex, ey, eyaw = self.est_pose(); s_, lat = LANE.project(np.array([ex, ey]))
            if (sgn > 0 and s_ >= s_goal) or (sgn < 0 and s_ <= s_goal): break
            if self.dr_mode and self.dr_unc > A['dr_hold_m']:
                self.outcome = 'alert'; self.alerts.append('no fix: along-lane uncertainty %.1f m > %.1f m -> hold + alert at s %.0f' % (self.dr_unc, A['dr_hold_m'], s_))
                self.events.append((round(self.t), 'HOLD no-fix')); return
            vlim = A['v_slow'] if (s_ < 25 or s_ > L - 24) else v_cruise
            if self.dr_mode: vlim = min(vlim, 0.25)
            elif self.zone(s_) == 'float': vlim = min(vlim, 0.3)          # G6 rule: RTK float -> 0.3 m/s
            self.update_bypass(s_, sgn)
            st = s_ + sgn * A['look']; tp = LANE.point(st, self.lane_target(st, sgn))
            a = wrap(math.atan2(tp[1] - ey, tp[0] - ex) - eyaw)
            if abs(a) > math.radians(60): self.op_pivot(wrap(self.yaw + a)); continue
            v = vlim; w = 2 * v * math.sin(a) / A['look']
            if not self.may_move(1, 'lane'):
                n += 1
                if self.outcome: return
                continue
            self.step_motion(v, w, dt); n += 1
            if n % 50 == 0: self.metrics['est_lat_abs'].append(round(abs(self.err[1]), 3))
        self.bypass = 0.0
    def update_bypass(self, s_, sgn):
        """static objects (car, branch) seen within 10 m ahead: shift the lane target sideways to clear them by 0.25 m if the
        shifted footprint keeps >= 0.05 m to the mapped hedge face; otherwise no shift (the stop rule then holds + alerts)."""
        self.bypass = 0.0
        for o in self.obst:
            if o['kind'] not in ('car', 'branch'): continue
            so, lo = LANE.project(np.array([o['x'], o['y']]))
            if not (0 < sgn * (so - s_) < 10 or abs(so - s_) < 2.5): continue
            pts = box_pts(o['x'], o['y'], o['yaw'], o['L'], o['W']); lats = [LANE.project(p)[1] for p in pts]
            hw = self.body.d.half_w; base = LF.lane_target(so, sgn, hw)
            fl = LF.HLN - G6.hedge_offset(so, 1); fr = LF.HLN - G6.hedge_offset(so, -1)
            cands = [max(lats) + 0.25 + hw, min(lats) - 0.25 - hw]
            ok = [c for c in cands if -fr + hw + 0.05 <= c <= fl - hw - 0.05]
            if ok:
                c = min(ok, key=lambda c: abs(c - base))
                if not (min(lats) - hw - 0.25 < base < max(lats) + hw + 0.25): c = base
                self.bypass = c - base
    # ---------------------------------------------------------------- higher-level operations
    def approach_and_lift(self, bkey):
        """front-wall carrier: get on the bin's axis 1.6 m out on the open (handle) side, facing the hold heading, then reverse
        onto the bin, square, lift. The pivot spot is searched on and beside the axis line (disc clear of everything)."""
        b = self.bins[bkey]; hx, hy, hyaw = hold_pose(self.body, b['x'], b['y'], b['yaw'])
        c, s_ = math.cos(hyaw), math.sin(hyaw); others = [o for o in self.obstacles_now() if o is not b]
        best = None
        for run in np.arange(1.6, 4.01, 0.2):
            for off in (0.0, 0.3, -0.3, 0.6, -0.6, 0.9, -0.9):
                px, py = hx + run * c - off * s_, hy + run * s_ + off * c
                m = LF.disc_ok(np.array([px, py]), self.body.d.r_empty, [(o['x'], o['y'], o['yaw']) for o in others + [b]])
                m2 = LF.disc_ok(np.array([px, py]), self.body.d.r_empty, [])   # region only
                if off != 0.0:   # the second pivot (at the approach start on the axis) must be clear too
                    qx, qy = hx + 1.6 * c, hy + 1.6 * s_
                    m2 = min(m2, LF.disc_ok(np.array([qx, qy]), self.body.d.r_empty, [(o['x'], o['y'], o['yaw']) for o in others + [b]]))
                if min(m, m2) > 0.05: best = (px, py, run, off); break
            if best: break
        if best is None: best = (hx + 1.6 * c, hy + 1.6 * s_, 1.6, 0.0); self.events.append((round(self.t), 'no clear pivot spot found for %s' % bkey))
        sr, _ = LANE.project(np.array([self.x, self.y])); sb, _ = LANE.project(np.array([b['x'], b['y']])); sp, _ = LANE.project(np.array(best[:2]))
        if sr < sb - 0.5 and sp > sb - 1.0: self.pass_bin(b, sp + 0.3)
        self.op_line(best[0], best[1]); self.op_pivot(hyaw)
        sx, sy = hx + 1.6 * c, hy + 1.6 * s_
        if math.hypot(sx - best[0], sy - best[1]) > 0.05: self.op_line(sx, sy, reverse=(best[2] > 1.6 + 1e-6))
        self.op_pivot(hyaw); self.engaged = {b['name']}; self.op_line(hx, hy, reverse=True); self.op_pivot(hyaw)
        self.op_wait(A['t_seek'] + 10, label='square on bin')
        self.op_wait(A['t_lift'] + A['t_warn'], A['lift_w'], 'lift'); self.carry = bkey; self.engaged = set()
    def set_down(self, target_pose, handle_ok_yaw=None):
        b = self.bins[self.carry]; bx, by, byaw = bin_pose_from_robot(self.body, self.x, self.y, self.yaw)
        self.op_wait(A['t_setdown'], A['lift_w'], 'set down'); b.update(x=bx, y=by, yaw=byaw)
        err = math.hypot(bx - target_pose[0], by - target_pose[1]); dyaw = abs(math.degrees(wrap(byaw - target_pose[2])))
        self.metrics['placements'].append(dict(bin=self.carry, err_m=round(err, 3), handle_err_deg=round(dyaw, 1)))
        self.engaged = {b['name']}; self.carry = None
        # withdraw: drive +x (bin leaves through the open tail) 1.3 m (tail clears the placed bin by > 0.05 m)
        self.op_line(self.x + 1.3 * math.cos(self.yaw), self.y + 1.3 * math.sin(self.yaw)); self.check(force=True); self.engaged = set(); self.check(force=True); self.op_wait(A['t_pull'] + A['t_photo'], label='photo')
    def goto_station(self, s_goal, lat_goal):
        s_, _ = LANE.project(np.array([self.x, self.y])); sgn = 1 if s_goal > s_ else -1
        h = LANE.heading(s_) + (0 if sgn > 0 else math.pi)
        if abs(wrap(h - self.yaw)) > math.radians(60): self.op_pivot(h)
        self.op_lane(s_goal, sgn)
    def do_drop(self, bkey, pad):
        b = self.bins[bkey]
        self.op_wait(A['t_undock'], label='undock')
        self.approach_and_lift(bkey)
        if self.outcome: return
        self.goto_station(L - 23.0, 0); self.op_wait(A['t_junction'], label='junction wait')
        if self.outcome: return
        tgt = pad_bin(pad, 'road'); hx, hy, hyaw = hold_pose(self.body, tgt['x'], tgt['y'], tgt['yaw'])
        pv = self.pivot_plan(hx, hy, hyaw, loaded=True)
        self.goto_station(LANE.project(np.array(pv[:2]))[0] - 1.5, 0)
        self.op_line(pv[0], pv[1]); self.op_pivot(hyaw); self.goto_pose(hx, hy, hyaw)
        self.set_down((tgt['x'], tgt['y'], tgt['yaw']))
        self.goto_station(SC.DOCK['s'] + 3.0, 0); self.dock()
    def pivot_plan(self, hx, hy, hyaw, loaded):
        """pivot centre for the final heading hyaw near the hold pose: on the hold axis line behind the target (robot -x side),
        lateral offsets allowed, disc (loaded radius) clear of region and standing bins; first fit from 1.0 m out."""
        r = self.body.d.r_load if loaded else self.body.d.r_empty; c, s_ = math.cos(hyaw), math.sin(hyaw)
        obs = [(o['x'], o['y'], o['yaw']) for o in self.obstacles_now()]
        for run in np.arange(1.0, 6.01, 0.25):
            for off in (0.0, 0.3, -0.3, 0.6, -0.6, 0.9, -0.9, 1.2, -1.2):
                px, py = hx - run * c - off * s_, hy - run * s_ + off * c
                if LF.disc_ok(np.array([px, py]), r, obs) > 0.05: return (px, py, run, off)
        self.events.append((round(self.t), 'pivot plan: no clear spot')); return (hx - 3.0 * c, hy - 3.0 * s_, 3.0, 0.0)
    def goto_pose(self, hx, hy, hyaw):
        """from a pivot spot already facing hyaw: drive forward to the hold pose (pure pursuit S if offset small, else line)."""
        self.op_line(hx, hy); self.op_pivot(hyaw)
    def dock(self):
        dx, dy, dyaw = S.pose(SC.DOCK['s'], SC.DOCK['lat'], 0.0)
        # dock facing down-lane: pivot spot 1.6 m down-lane of the dock pose, then reverse onto the dock
        c, s_ = math.cos(dyaw), math.sin(dyaw); px, py = dx + 1.6 * c, dy + 1.6 * s_
        self.op_line(px, py); self.op_pivot(dyaw); self.engaged = {'dock'}; self.op_line(dx, dy, reverse=True); self.op_wait(A['t_dock'], label='dock')
    def home_slot(self, col):
        """G4 g) rule: the bin's own home slot, or the nearest clear legal alternate in the yard (0.3 m from cars/bins/dock)."""
        hs = SC.HOME_SPOTS[col]; x, y, h = S.pose(hs['s'], hs['lat'], 0.0); cand = [(0.0, x, y, h, hs['s'], hs['lat'])]
        for s_ in np.arange(6.0, 22.01, 0.5):
            for lat in np.arange(-5.4, 5.41, 0.4):
                xx, yy, hh = S.pose(s_, lat, 0.0); cand.append((math.hypot(xx - x, yy - y), xx, yy, hh, s_, lat))
        cand.sort(key=lambda c: c[0]); obs = self.obstacles_now()
        for dist, xx, yy, hh, s_, lat in cand:
            P = box_pts(xx, yy, hh, 0.74, 0.58)
            if min(float(np.min(pt_box(P, o))) for o in obs) < 0.3: continue
            if min(LF.region_margin(p)[0] for p in P) < 0.3: continue
            # the carrier must reach it: hold pose and a pivot spot clear
            hx, hy, hyaw = hold_pose(self.body, xx, yy, hh)
            Pr = self.body.fp(hx, hy, hyaw, True)
            if min(float(np.min(pt_box(Pr, o))) for o in obs) < 0.1: continue
            if dist > 0: self.events.append((round(self.t), 'home slot %s blocked -> alternate at s %.1f lat %.1f (%.1f m away)' % (col, s_, lat, dist)))
            return (xx, yy, hh)
        return None
    def do_pickup(self, bkey, dest):
        self.op_wait(A['t_undock'], label='undock')
        b = self.bins[bkey]; sb, _ = LANE.project(np.array([b['x'], b['y']]))
        self.goto_station(min(sb - 3.0, L - 23.0), 0)
        if self.outcome: return
        self.op_wait(A['t_junction'], label='junction wait')
        self.approach_and_lift(bkey)
        if self.outcome: return
        self.home_with(bkey, dest)
    def home_with(self, bkey, dest):
        if math.cos(wrap(self.yaw - LANE.heading(LANE.project(np.array([self.x, self.y]))[0]))) > 0: self.loaded_turn_home()
        col = dest.split(':')[1]; slot = self.home_slot(col)
        if slot is None: self.outcome = 'alert'; self.alerts.append('no clear home slot'); return
        hx, hy, hyaw = hold_pose(self.body, *slot)
        pv = self.pivot_plan(hx, hy, hyaw, loaded=True)
        self.goto_station(max(LANE.project(np.array(pv[:2]))[0] + 2.0, 14.0), 0)
        if self.outcome: return
        self.op_line(pv[0], pv[1]); self.op_pivot(hyaw); self.goto_pose(hx, hy, hyaw)
        self.set_down(slot)
        self.dock()
    # ---------------------------------------------------------------- driver
    def run(self, budget):
        t0 = time.time()
        while self.ops and not self.outcome and time.time() - t0 < budget:
            op = self.ops.pop(0); self.events.append((round(self.t), 'OP %s' % (op,)))
            if op[0] == 'drop': self.do_drop(op[1], op[2])
            elif op[0] == 'pickup': self.do_pickup(op[1], op[2])
            elif op[0] == 'home_with': self.home_with(op[1], op[2])
            elif op[0] == 'lane': self.op_lane(op[1], op[2])
        self.wall += time.time() - t0
        if not self.ops and not self.outcome: self.outcome = 'completed'
        return self.outcome is not None
    def result(self):
        M = self.metrics; T = S9_THRESHOLDS; defects = []
        if M['hedge_min'] < T['hedge_strict_m']: defects.append('hedge %+.3f m at s %s' % (M['hedge_min'], M['hedge_at']))
        if M['region_min'] < T['region_m']: defects.append('region %+.3f m at s %s' % (M['region_min'], M['region_at']))
        if M['obst_min'] < T['obstacle_overlap_m']: defects.append('obstacle overlap %+.3f m (%s)' % (M['obst_min'], M['obst_at']))
        if M['bin_min'] < T['bin_gap_m']: defects.append('bin gap %.3f m (%s)' % (M['bin_min'], M['bin_at']))
        if M['person_min'] < T['person_gap_m']: defects.append('person/dog gap %.3f m' % M['person_min'])
        for p in M['placements']:
            if p['err_m'] > T['placement_m'] or p['handle_err_deg'] > T['handle_deg']: defects.append('placement %s %.2f m / %.0f deg' % (p['bin'], p['err_m'], p['handle_err_deg']))
        got = 'pass' if self.outcome == 'completed' else 'alert'
        ok = (got == self.spec['expect']) and not defects
        la = M['est_lat_abs']
        return dict(design=self.dn, scenario=self.sc, expect=self.spec['expect'], result=got, outcome=self.outcome, alerts=self.alerts,
                    strict_pass=ok, defects=defects, sim_min=round(self.t / 60, 2), energy_wh=round(self.E['total_wh'], 2),
                    E=dict((k, round(v, 2)) for k, v in self.E.items()), odo_m=round(self.odo, 1), hedge_min_m=M['hedge_min'], hedge_at_s=M['hedge_at'],
                    region_min_m=M['region_min'], region_at_s=M['region_at'], obst_min_m=M['obst_min'], bin_min_m=M['bin_min'], person_min_m=M['person_min'],
                    stops=M['stops'], pivots=M['pivots'], placements=M['placements'], i_motor_max_A=round(M['i_motor_max'], 1),
                    i_motor_max_at=M['i_motor_max_at'], i_motor_12pct_A=round(M['i_motor_max_12'], 1),
                    est_lat_p95_m=round(float(np.percentile(la, 95)), 3) if la else None, wall_s=round(self.wall, 1),
                    n_chk_below_0p10=M['n_hedge_below_review'], engaged_min_m=M['engaged_min'], person_min_any_m=M.get('person_min_any', 9.0), thresholds=T, events=self.events[-60:], trace=self.trace)

if __name__ == '__main__':
    dn, scn, bud = sys.argv[1], sys.argv[2], float(sys.argv[3])
    pk = os.path.join(OUT, '%s__%s.pkl' % (dn, scn)); rj = os.path.join(OUT, '%s__%s.json' % (dn, scn))
    if os.path.exists(rj): print('already done', rj); sys.exit(0)
    sim = pickle.load(open(pk, 'rb')) if os.path.exists(pk) else Sim(dn, scn)
    fin = sim.run(bud)
    if fin:
        R = sim.result(); json.dump(R, open(rj, 'w'), indent=1, default=float)
        if os.path.exists(pk): os.remove(pk)
        print('DONE', dn, scn, R['result'], 'strict', R['strict_pass'], R['defects'], 'min', R['sim_min'], 'Wh', R['energy_wh'], 'hedge', R['hedge_min_m'], 'I', R['i_motor_max_A'])
    else:
        pickle.dump(sim, open(pk, 'wb')); print('chunk', dn, scn, 't_sim %.0f s' % sim.t, 'ops left', len(sim.ops))
