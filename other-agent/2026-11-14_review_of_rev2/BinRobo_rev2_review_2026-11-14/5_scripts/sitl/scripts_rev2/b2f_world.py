"""B2-F carrier physics world for the ArduPilot JSON SITL (lock-step). Truth side only.
 - Lane / truth hedges / terrain / road / private boundary: scene.Site from the G6 copy (scripts_base), unchanged.
 - Body: rigid skid-steer carrier (drive axle origin, +x = nose). Wheels from SERVO1/SERVO3 PWM (ThrottleLeft/Right),
   first-order motor lag + traction limit; castors at the nose. NO hitch / kingpin.
 - Carried bin is rigid on the comb (front wall at x = +0.269 m): adds mass + CG and joins the footprint.
 - LD06 lidar (nose, 0.30 m high): 360 rays, 12 m, body self-occlusion behind the mast; hedges, bins, boxes, cars, people/dogs.
 - GPS truth quality: scenario zones override the G6 canopy multipath model.
 - Energy: traction + rolling + grade + accel + turning scrub + hotel + lights + lift actuator; LFP pack model.
 Everything here is picklable (checkpointing across SITL restarts)."""
import math, os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'scripts_base'))
from scene import Site, seg_dist
from world import wrap
import g6_features as G6

P_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DIMS = json.load(open(os.path.join(P_ROOT, 'work', 'revB2F', 'dims_B2F.json')))
_b = DIMS['robot_no_bin']
ROB = dict(x0=_b[0][0] / 1000.0, x1=_b[1][0] / 1000.0, hw=_b[1][1] / 1000.0,       # -0.397 .. 1.106, half width 0.465
           track=DIMS['track_mm'] / 1000.0, vmax=0.80, mass=92.3, lidar_x=1.00, tau=0.15, a_trac=1.2,
           comb_x=0.2692, castor_x=0.95)
BIN_T = {'240': dict(D=0.772, W=0.583, H=1.07, empty=13.0, full=55.0), '140': dict(D=0.62, W=0.48, H=1.0, empty=9.0, full=32.0)}
PACK = dict(v_nom=25.6, ah=20.0, wh=512.0)
SITE = {}
def site():
    if 'real' not in SITE: SITE['real'] = Site('real')
    return SITE['real']

def rect_pts(cx, cy, yaw, x0, x1, hw, n=8):
    """outline points of a rectangle in a body frame [x0,x1] x [-hw,hw], placed at (cx,cy,yaw)."""
    xs = np.linspace(x0, x1, n); ys = np.linspace(-hw, hw, max(3, n // 2))
    loc = np.r_[np.c_[xs, np.full(n, hw)], np.c_[xs, np.full(n, -hw)], np.c_[np.full(len(ys), x0), ys], np.c_[np.full(len(ys), x1), ys]]
    c, s = math.cos(yaw), math.sin(yaw)
    return np.c_[cx + c * loc[:, 0] - s * loc[:, 1], cy + s * loc[:, 0] + c * loc[:, 1]]

def box_corners(cx, cy, yaw, L, W):
    c, s = math.cos(yaw), math.sin(yaw); out = []
    for a, b in ((L / 2, W / 2), (-L / 2, W / 2), (-L / 2, -W / 2), (L / 2, -W / 2)):
        out.append((cx + c * a - s * b, cy + s * a + c * b))
    return np.array(out)

def box_segs(cx, cy, yaw, L, W):
    C = box_corners(cx, cy, yaw, L, W); return np.array([np.r_[C[i], C[(i + 1) % 4]] for i in range(4)])

def pts_in_box(P, b):
    c, s = math.cos(b['yaw']), math.sin(b['yaw']); d = P - np.array([b['x'], b['y']])
    u = d[:, 0] * c + d[:, 1] * s; v = -d[:, 0] * s + d[:, 1] * c
    return (np.abs(u) <= b['L'] / 2) & (np.abs(v) <= b['W'] / 2)

def gap_pts_box(P, b):
    """min distance (m) from points P to box b (0 if inside)."""
    c, s = math.cos(b['yaw']), math.sin(b['yaw']); d = P - np.array([b['x'], b['y']])
    u = np.abs(d[:, 0] * c + d[:, 1] * s) - b['L'] / 2; v = np.abs(-d[:, 0] * s + d[:, 1] * c) - b['W'] / 2
    return float(np.min(np.hypot(np.maximum(u, 0), np.maximum(v, 0))))


class World:
    def __init__(self, x, y, yaw, seed=7, night=True):
        self.S = site(); self.t = 0.0; self.x = x; self.y = y; self.yaw = yaw; self.v = 0.0; self.w = 0.0
        self.vl = 0.0; self.vr = 0.0; self.night = night; self.seed = seed; self.rng = np.random.default_rng(seed)
        self.carry = None; self.bins = {}; self.obst = []; self.movers = []; self.cars = []; self.zones = []
        self.lift_q = 0.0; self.pad_on = False; self.lift_busy = 0.0
        self.estop = False; self.chain_ok = True; self.chain_trips = []; self.bump = False
        self.mp = G6.RtkMultipath(seed); self.odo = 0.0; self.odo_k = 1.0 + float(np.random.default_rng(seed + 77).normal(0, 0.01))
        self.soc = 0.90; self.air_c = 4.0; self.wind_gust = 5.0; self.frost = False
        self.pack_wh_out = 0.0; self.energy_wh = 0.0; self.p_now = 0.0; self.lights_w = 0.0; self.hotel_w = 9.0
        self.hedge_min = 99.0; self.hedge_min_at = None; self.legal_min = 99.0; self.legal_min_at = None
        self.contact_min = 99.0; self.contact_with = None; self.person_rest_min = 99.0; self.car_rest_min = 99.0
        self.collisions = []; self._chk_t = -1.0; self.placements = []

    # ------------------------------------------------------------------ geometry
    def mass(self):
        return ROB['mass'] + (self.bins[self.carry]['mass'] if self.carry else 0.0)
    def bin_pose_in_robot(self, b):
        """carried bin centre (x in robot frame) for a bin of type b['size']: front wall at the comb face."""
        return ROB['comb_x'] - BIN_T[b['size']]['D'] / 2
    def footprint(self, x=None, y=None, yaw=None, with_bin=True, n=10):
        x = self.x if x is None else x; y = self.y if y is None else y; yaw = self.yaw if yaw is None else yaw
        P = rect_pts(x, y, yaw, ROB['x0'], ROB['x1'], ROB['hw'], n)
        if with_bin and self.carry:
            b = self.bins[self.carry]; T = BIN_T[b['size']]; bx = self.bin_pose_in_robot(b)
            P = np.r_[P, rect_pts(x, y, yaw, bx - T['D'] / 2, bx + T['D'] / 2, T['W'] / 2, 6)]
        return P
    def carried_xy(self):
        b = self.bins[self.carry]; bx = self.bin_pose_in_robot(b)
        return self.x + bx * math.cos(self.yaw), self.y + bx * math.sin(self.yaw), wrap(self.yaw + math.pi)   # handle points to robot -x
    def s_lat(self, x=None, y=None):
        return self.S.lane.project(np.array([self.x if x is None else x, self.y if y is None else y]))

    # ------------------------------------------------------------------ actors (all data, no closures -> picklable)
    def mover_pos(self, m):
        if m['t0'] is None:
            if math.hypot(self.x - m['mid'][0], self.y - m['mid'][1]) < m['trigger_d']: m['t0'] = self.t + m.get('delay', 0.0)
            else: return None
        if self.t < m['t0']: return None
        a = np.array(m['a']); b = np.array(m['b']); Lab = float(np.linalg.norm(b - a)); d = (self.t - m['t0']) * m['speed']
        mid = Lab * m.get('pause_at', 0.5)
        if d > mid: d = mid + max(0.0, d - mid - m.get('pause', 0.0) * m['speed'])
        if d >= Lab: return None
        p = a + (b - a) * d / Lab; return (float(p[0]), float(p[1]))
    def car_box(self, c):
        if c['t0'] is None:
            if self.s_lat()[0] >= c['appear_s']: c['t0'] = self.t
            else: return None
        if self.t - c['t0'] > c['dwell']: return None
        return dict(x=c['x'], y=c['y'], yaw=c['yaw'], L=c['L'], W=c['W'], kind='car')
    def standing(self):
        """all standing objects as boxes (bins not carried, static obstacles, cars present)."""
        out = []
        for k, b in self.bins.items():
            if k == self.carry or b['state'] == 'gone': continue
            T = BIN_T[b['size']]
            if b['state'] == 'tipped': out.append(dict(x=b['x'], y=b['y'], yaw=b['yaw'], L=T['H'], W=T['W'], kind='bin_tipped', name=k, engaged=b.get('engaged', False)))
            else: out.append(dict(x=b['x'], y=b['y'], yaw=b['yaw'], L=T['D'], W=T['W'], kind='bin', name=k, engaged=b.get('engaged', False)))
        out += [dict(o) for o in self.obst]
        for c in self.cars:
            cb = self.car_box(c)
            if cb: out.append(cb)
        return out
    def movers_now(self):
        out = []
        for m in self.movers:
            p = self.mover_pos(m)
            if p: out.append((p[0], p[1], m['r'], m['kind']))
        return out

    # ------------------------------------------------------------------ dynamics
    def step(self, dt, pwm):
        self.t += dt
        tl = (pwm[0] - 1500) / 400.0; tr = (pwm[2] - 1500) / 400.0
        tl = float(np.clip(tl, -1, 1)); tr = float(np.clip(tr, -1, 1))
        if not self.chain_ok or self.lift_busy > 0: tl = tr = 0.0       # stop chain open / interlock while lifting = motor enable off
        al = ROB['a_trac'] * ROB['mass'] / self.mass()
        if not self.chain_ok:            # spring brakes: decel limited (ASSUMED 2.0 m/s^2 with load, friction-limited)
            dec = 2.0 * dt
            self.vl = math.copysign(max(0.0, abs(self.vl) - dec), self.vl); self.vr = math.copysign(max(0.0, abs(self.vr) - dec), self.vr)
        else:
            for side, tgt in (('vl', tl * ROB['vmax']), ('vr', tr * ROB['vmax'])):
                cur = getattr(self, side); d = (tgt - cur) * min(1.0, dt / ROB['tau']); d = float(np.clip(d, -al * dt, al * dt))
                setattr(self, side, cur + d)
        self.v = 0.5 * (self.vl + self.vr); self.w = (self.vr - self.vl) / (ROB['track'] * 1.05)    # 5 % turning scrub (castors)
        if self.lift_busy > 0: self.lift_busy = max(0.0, self.lift_busy - dt)
        nx = self.x + self.v * math.cos(self.yaw) * dt; ny = self.y + self.v * math.sin(self.yaw) * dt; nyaw = wrap(self.yaw + self.w * dt)
        # contact (bump strip / body) with standing objects or people: chain opens, robot does not move into it
        hit = self.contact(nx, ny, nyaw)
        if hit is not None and (abs(self.v) > 0.005 or abs(self.w) > 0.01):
            self.collisions.append(dict(t=round(self.t, 2), what=hit)); self.chain_trip('contact with %s' % hit)
        else:
            self.odo += abs(self.v) * dt; self.x, self.y, self.yaw = nx, ny, nyaw
        self.energy(dt)
        if self.t - self._chk_t >= 0.2: self._chk_t = self.t; self.checks()
    def contact(self, x, y, yaw):
        P = self.footprint(x, y, yaw, n=8)
        for o in self.standing():
            if o.get('engaged'): continue
            if pts_in_box(P, o).any(): return o.get('name', o['kind'])
        for (mx, my, r, k) in self.movers_now():
            if np.min(np.hypot(P[:, 0] - mx, P[:, 1] - my)) < r: return k
        return None
    def chain_trip(self, why):
        if self.chain_ok: self.chain_trips.append(dict(t=round(self.t, 2), why=why, v=round(self.v, 3)))
        self.chain_ok = False
    def checks(self):
        """truth clearance bookkeeping (5 Hz): hedge, legal boundary, objects."""
        P = self.footprint(n=10); S = self.S
        H = S.hedge_truth; m = 0.5 * (H[:, :2] + H[:, 2:]); near = H[np.linalg.norm(m - np.array([self.x, self.y]), axis=1) < 5.0]
        if len(near):
            d = float(np.min(seg_dist(P[:, None, :], near[None, :, :2], near[None, :, 2:])))
            if d < self.hedge_min: self.hedge_min = d; self.hedge_min_at = (round(self.t, 1), round(float(self.s_lat()[0]), 1))
        sl = float(self.s_lat()[0])
        if sl > S.L - 40:
            rd = float(np.min(seg_dist(P[:, None, :], S.road[None, :-1], S.road[None, 1:])) - S.boundary)
            if rd < self.legal_min: self.legal_min = rd; self.legal_min_at = (round(self.t, 1), round(sl, 1))
        for o in self.standing():
            if o.get('engaged'): continue
            g = gap_pts_box(P, o)
            if g < self.contact_min: self.contact_min = g; self.contact_with = o.get('name', o['kind'])
            if o['kind'] == 'car' and abs(self.v) < 0.01: self.car_rest_min = min(self.car_rest_min, g)
        for (mx, my, r, k) in self.movers_now():
            g = float(np.min(np.hypot(P[:, 0] - mx, P[:, 1] - my))) - r
            if g < self.contact_min: self.contact_min = g; self.contact_with = k
            if abs(self.v) < 0.01 and g < 3.0: self.person_rest_min = min(self.person_rest_min, g)

    # ------------------------------------------------------------------ sensors
    def lidar(self, rmax=12.0):
        """360 ranges (index = bearing deg CCW from the robot +x axis), inf = no return. Truth geometry."""
        ox = self.x + ROB['lidar_x'] * math.cos(self.yaw); oy = self.y + ROB['lidar_x'] * math.sin(self.yaw)
        ang = self.yaw + np.radians(np.arange(360)); D = np.c_[np.cos(ang), np.sin(ang)]
        H = self.S.hedge_truth; m = 0.5 * (H[:, :2] + H[:, 2:]); segs = [H[np.linalg.norm(m - np.array([ox, oy]), axis=1) < rmax + 3]]
        for o in self.standing():
            if o.get('engaged'): continue
            if math.hypot(o['x'] - ox, o['y'] - oy) < rmax + 3: segs.append(box_segs(o['x'], o['y'], o['yaw'], o['L'], o['W']))
        Sg = np.concatenate([s for s in segs if len(s)]) if any(len(s) for s in segs) else np.zeros((0, 4))
        r = np.full(360, np.inf)
        if len(Sg):
            A = Sg[:, :2] - np.array([ox, oy]); E = Sg[:, 2:] - Sg[:, :2]
            den = D[:, None, 0] * E[None, :, 1] - D[:, None, 1] * E[None, :, 0]
            with np.errstate(divide='ignore', invalid='ignore'):
                t = (A[None, :, 0] * E[None, :, 1] - A[None, :, 1] * E[None, :, 0]) / den
                u = (A[None, :, 0] * D[:, None, 1] - A[None, :, 1] * D[:, None, 0]) / den
            ok = (np.abs(den) > 1e-9) & (t > 0.02) & (u >= 0) & (u <= 1)
            t = np.where(ok, t, np.inf); r = np.min(t, axis=1)
        for (mx, my, rr, k) in self.movers_now():
            dx, dy = mx - ox, my - oy; b = D[:, 0] * dx + D[:, 1] * dy; c = dx * dx + dy * dy - rr * rr; disc = b * b - c
            hit = (disc > 0) & (b > 0); tt = np.where(hit, b - np.sqrt(np.maximum(disc, 0)), np.inf); r = np.minimum(r, tt)
        rel = (np.arange(360) + 360) % 360
        r[(rel > 105) & (rel < 255)] = np.inf          # mast / body / carried bin behind the nose lidar: rear sector blind
        r[r > rmax] = np.inf
        r = np.where(np.isfinite(r), r + self.rng.normal(0, 0.01, 360), r)
        return r
    def gps_quality(self):
        s = float(self.s_lat()[0])
        for a, b, q in self.zones:
            if a <= s <= b: return q, np.zeros(2)
        return self.mp.step(self.t, s, 0.2)

    # ------------------------------------------------------------------ energy
    def energy(self, dt):
        m = self.mass(); g = 9.81; v = self.v
        gx, gy = self.S.ter.grad(self.x, self.y); grade = gx * math.cos(self.yaw) + gy * math.sin(self.yaw)
        a = (v - getattr(self, '_vprev', 0.0)) / dt; self._vprev = v
        F = m * g * 0.03 * (1 if abs(v) > 0.01 else 0) + m * g * grade * (1 if v >= 0 else -1) * (1 if abs(v) > 0.01 else 0) + m * max(a, 0) * (1 if v >= 0 else -1)
        p_tr = max(0.0, F * abs(v)) / 0.60 + (0.08 * m * g * abs(self.w) * 0.40 / 0.60)    # scrub torque (ASSUMED mu_turn 0.08, arm 0.40 m)
        p = p_tr + self.hotel_w + self.lights_w + (50.0 if self.lift_busy > 0 else 0.0)
        self.p_now = p; e = p * dt / 3600.0; self.energy_wh += e; self.pack_wh_out += e
        cold = float(np.interp(self.air_c, [-20, -10, 0, 10, 25], [0.60, 0.75, 0.88, 0.95, 1.0]))
        self.soc = max(0.0, self.soc - e / (PACK['wh'] * cold))
    def pack_v(self):
        return 24.0 + 2.6 * self.soc - 0.04 * self.p_now / 25.0
