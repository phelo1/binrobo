# 2.5D world for the bin-tug SITL: real lane (OSM) + real terrain (EU-DEM 25 m), tug + towed bin,
# obstacles, ray-cast LD06 lidar, synthetic rear docking camera (rendered image -> real OpenCV ArUco).
import json, math, os, numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
LAT0, LON0 = 53.000000, -8.000000          # Brian's map pin = local origin (x east, y north)
MX = 111320 * math.cos(math.radians(LAT0)); MY = 111132.0
def ll2xy(lat, lon): return ((lon - LON0) * MX, (lat - LAT0) * MY)
def xy2ll(x, y): return (LAT0 + y / MY, LON0 + x / MX)
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi

# ---------------- tug / bin geometry (from cad/revF mass_revF.json, drive-axle centre = origin) ----------------
TUG = dict(mass=105.6, front=1.432 - 0.670 + 0.195,   # G6: CAD front is 195 mm longer than revF (HANDOVER 4.3)
           rear=0.670 - 0.0 + 0.21, half_w=0.38, track=0.69,
           lidar_x=1.402 - 0.670, lidar_z=0.307, cam_x=0.245 - 0.670, cam_z=1.255, hook_x=0.055 - 0.670)
BIN = dict(w=0.58, d=0.74, h=1.07, tilt_deg=48.0, L=1.35)   # L: turntable (drive axle) -> bin axle when hooked & tilted
VMAX = 1.0           # m/s at full throttle (wheelchair gearmotors, 24 V)
# G6: tug-bin articulation hard stop. CAD (Rev G kingpin yaw stops) = 28 deg (was 60 in G1-G4). g6-mech may open the
# kingpin to about +/-42 deg -> about 40 deg usable. Parameter: env BT_HITCH_CAP (deg), default 28.
HITCH_CAP_DEG = float(os.environ.get('BT_HITCH_CAP', '28'))
HITCH_CAP = math.radians(HITCH_CAP_DEG)
ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
MARKS = {i: cv2.aruco.generateImageMarker(ARUCO_DICT, i, 120, borderBits=1) for i in range(6)}


class Lane:
    def __init__(self, xy, width=3.6, yard=(0, 25), mouth=None):
        self.P = np.asarray(xy, float)
        d = np.linalg.norm(np.diff(self.P, axis=0), axis=1)
        self.s = np.r_[0, np.cumsum(d)]; self.length = self.s[-1]; self.width = width
        self.yard = yard; self.mouth = mouth if mouth else (self.length - 7, self.length + 50)
        self._hedges()

    def point(self, s, lat=0.0):
        s = np.clip(s, 0, self.length)
        x = np.interp(s, self.s, self.P[:, 0]); y = np.interp(s, self.s, self.P[:, 1])
        h = self.heading(s)
        return np.array([x + lat * math.cos(h + math.pi / 2), y + lat * math.sin(h + math.pi / 2)])

    def heading(self, s):  # ENU heading (rad from east, CCW) of increasing s, smoothed over +-4 m
        a = self._xy(max(s - 4, 0)); b = self._xy(min(s + 4, self.length))
        return math.atan2(b[1] - a[1], b[0] - a[0])

    def _xy(self, s): return np.array([np.interp(s, self.s, self.P[:, 0]), np.interp(s, self.s, self.P[:, 1])])

    def project(self, p):
        best = (1e9, 0, 0)
        for i in range(len(self.P) - 1):
            a, b = self.P[i], self.P[i + 1]; ab = b - a; L2 = ab @ ab
            t = np.clip((p - a) @ ab / L2, 0, 1); q = a + t * ab; dd = np.linalg.norm(p - q)
            if dd < best[0]:
                side = np.sign(ab[0] * (p - a)[1] - ab[1] * (p - a)[0])
                best = (dd, self.s[i] + t * math.sqrt(L2), side * dd)
        return best[1], best[2]       # s, lateral (+ = left of travel direction house->road)

    def _hedges(self):
        segs = []; ss = np.arange(0, self.length, 2.0)
        for side in (+1, -1):
            pts = []
            for s in ss:
                if self.yard[0] <= s <= self.yard[1] or s >= self.mouth[0]:
                    if len(pts) > 1: segs += [np.r_[pts[k], pts[k + 1]] for k in range(len(pts) - 1)]
                    pts = []; continue
                pts.append(self.point(s, side * (self.width / 2 + 0.25)))
            if len(pts) > 1: segs += [np.r_[pts[k], pts[k + 1]] for k in range(len(pts) - 1)]
        self.hedge = np.array(segs)


class Terrain:
    def __init__(self, grid=None, flat_z=0.0, grade_fn=None):
        self.g = grid; self.flat_z = flat_z; self.grade_fn = grade_fn
        if grid:
            self.xs = np.array(grid['xs']); self.ys = np.array(grid['ys']); self.Z = np.array(grid['z'])

    def z(self, x, y):
        if self.grade_fn: return self.grade_fn(x, y)
        if not self.g: return self.flat_z
        i = np.clip((x - self.xs[0]) / (self.xs[1] - self.xs[0]), 0, len(self.xs) - 1.001)
        j = np.clip((y - self.ys[0]) / (self.ys[1] - self.ys[0]), 0, len(self.ys) - 1.001)
        i0, j0 = int(i), int(j); fi, fj = i - i0, j - j0; Z = self.Z
        return (Z[j0, i0] * (1 - fi) * (1 - fj) + Z[j0, i0 + 1] * fi * (1 - fj) + Z[j0 + 1, i0] * (1 - fi) * fj + Z[j0 + 1, i0 + 1] * fi * fj)

    def grad(self, x, y, h=1.5):
        return ((self.z(x + h, y) - self.z(x - h, y)) / (2 * h), (self.z(x, y + h) - self.z(x, y - h)) / (2 * h))


def box_segs(cx, cy, yaw, L, W):
    c, s = math.cos(yaw), math.sin(yaw)
    pts = [(cx + c * dx - s * dy, cy + s * dx + c * dy) for dx, dy in ((L / 2, W / 2), (-L / 2, W / 2), (-L / 2, -W / 2), (L / 2, -W / 2))]
    return [np.r_[pts[k], pts[(k + 1) % 4]] for k in range(4)], pts


class World:
    """Holds truth state. Physics step driven by ArduPilot servo outputs (JSON SITL backend)."""
    def __init__(self, lane, terrain, home_xy, home_yaw):
        self.lane = lane; self.ter = terrain
        self.x, self.y = home_xy; self.yaw = home_yaw        # ENU yaw
        self.vl = self.vr = 0.0; self.v = 0.0; self.w = 0.0; self.t = 0.0
        self.attached = False; self.bin = None              # dict x,y,yaw,state('up','tipped'), marker faces
        self.obst = []                                      # static boxes: dict(kind, x,y,yaw,L,W,H)
        self.movers = []                                    # moving circles: dict(kind, r, fn(t)->(x,y))
        self.hook_pwm = 1100; self.hook_tilt = 0.0           # deg
        self.bumper = False; self.seat = False; self.hitch = 0.0; self.hitch_max = 0.0; self.hitch_limit_hits = 0
        self.gps_zones = []                                 # list (s0,s1,kind) kind in 'float','none'
        self.last_acc = np.zeros(3); self.prev_v = 0.0; self.odo = 0.0
        self.rng = np.random.default_rng(int(os.environ.get('BT_SEED', '7')))     # Rev G: BT_SEED for robustness sweeps

    # ---------- truth helpers ----------
    def zxy(self, x, y): return self.ter.z(x, y)

    def attitude(self):
        gx, gy = self.ter.grad(self.x, self.y)
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        slope_fwd = gx * c + gy * s; slope_left = -gx * s + gy * c
        pitch = math.atan(slope_fwd)        # nose-up positive
        roll = math.atan(slope_left)        # left side higher -> rolled right (positive)
        return roll, pitch

    def grade_here(self):
        gx, gy = self.ter.grad(self.x, self.y)
        return gx * math.cos(self.yaw) + gy * math.sin(self.yaw)

    # ---------- physics ----------
    def step(self, dt, pwm):
        thl = np.clip((pwm[0] - 1500) / 500.0, -1, 1); thr = np.clip((pwm[2] - 1500) / 500.0, -1, 1)
        if abs(thl) < 0.02: thl = 0
        if abs(thr) < 0.02: thr = 0
        grade = self.grade_here()
        load = 1.6 if self.attached else 1.0
        droop = 0.9 * grade * load                     # m/s lost per unit grade (motor speed droop under load)
        roll_res = 0.03 * load
        def tgt(th):
            if th == 0: return 0.0                     # spring brake holds
            v = th * VMAX - droop
            return v - math.copysign(roll_res, th) if abs(v) > roll_res else 0.0
        tau = 0.35 * load
        self.vl += (tgt(thl) - self.vl) * min(1, dt / tau); self.vr += (tgt(thr) - self.vr) * min(1, dt / tau)
        v = 0.5 * (self.vl + self.vr); w = (self.vr - self.vl) / (TUG['track'] * 1.25)   # skid scrub factor
        nx = self.x + v * math.cos(self.yaw) * dt; ny = self.y + v * math.sin(self.yaw) * dt
        if self.collides(nx, ny, self.yaw + w * dt, v):
            v = 0.0; self.vl = self.vr = 0.0; w = 0.0; self.bumper = True
        else:
            self.bumper = False
            self.x, self.y = nx, ny; self.yaw = wrap(self.yaw + w * dt)
        self.odo += abs(v) * dt
        if self.attached:
            b = self.bin; L = BIN['L']
            phi = wrap(self.yaw - b['yaw'])
            b['yaw'] = wrap(b['yaw'] + v / L * math.sin(phi) * dt)
            phi = wrap(self.yaw - b['yaw'])
            if abs(phi) > HITCH_CAP:                      # turntable hard stop: bin dragged round
                b['yaw'] = wrap(self.yaw - math.copysign(HITCH_CAP, phi)); self.hitch_limit_hits += 1
                phi = math.copysign(HITCH_CAP, phi)
            self.hitch = math.degrees(phi); self.hitch_max = max(self.hitch_max, abs(self.hitch))
            b['x'] = self.x - L * math.cos(b['yaw']); b['y'] = self.y - L * math.sin(b['yaw'])
        tgt_tilt = BIN['tilt_deg'] if pwm[4] > 1700 else 0.0
        self.hook_tilt += np.clip(tgt_tilt - self.hook_tilt, -12 * dt, 12 * dt)   # ~4 s full stroke
        self.seat = self._seat_check()
        acc = (v - self.prev_v) / dt; self.prev_v = v
        self.v, self.w = v, w; self.t += dt
        return acc

    def _seat_check(self):
        if self.bin is None or self.bin['state'] != 'up': return False
        if self.attached: return True
        lk = getattr(self, '_seat_lock', None)
        if lk is not None:
            # Rev G2 sim fix: once the handle is in the hook throat and the wheels bear on the crossbeam, the bin stays seated
            # until the tug drives FORWARD away from it (> 3 cm) or its body yaws > 15 deg off the bin axis. Reverse creep pushes the bin with it
            # (scene.py). Before this, the instantaneous 9 cm proxy could flicker off while the tug coasted to a stop.
            fwd = (self.x - lk[0]) * math.cos(lk[2]) + (self.y - lk[1]) * math.sin(lk[2])
            if fwd < 0.03 and abs(wrap(self.yaw - self.bin['yaw'])) < math.radians(15): return True   # hitch is yaw-free while docking
            self._seat_lock = None
        hx = self.x + TUG['hook_x'] * math.cos(self.yaw); hy = self.y + TUG['hook_x'] * math.sin(self.yaw)
        b = self.bin; hb = (b['x'] + 0.30 * math.cos(b['yaw']), b['y'] + 0.30 * math.sin(b['yaw']))   # handle face centre
        d = math.hypot(hx - hb[0], hy - hb[1]); yaw_err = abs(wrap(self.yaw - b['yaw']))
        ok = d < 0.09 and yaw_err < math.radians(15)
        if ok: self._seat_lock = (self.x, self.y, self.yaw)
        return ok

    def try_attach(self):
        if self.seat and self.hook_tilt > BIN['tilt_deg'] - 2 and not self.attached:
            self.attached = True; return True
        return False

    def release(self):
        if self.attached and self.hook_tilt < 2:
            self.attached = False; b = self.bin; self._seat_lock = None
            b['x'] = self.x + (TUG['hook_x'] - 0.30 - 0.07) * math.cos(b['yaw']); b['y'] = self.y + (TUG['hook_x'] - 0.30 - 0.07) * math.sin(b['yaw'])
            return True
        return False

    def collides(self, x, y, yaw, v):
        if v == 0: return False
        c, s = math.cos(yaw), math.sin(yaw)
        ex = TUG['front'] if v > 0 else -0.45
        pts = [(x + c * ex - s * dy, y + s * ex + c * dy) for dy in np.linspace(-TUG['half_w'], TUG['half_w'], 7)]
        for o in self.static_boxes(include_bin=not self.attached, for_collision=True):
            _, poly = box_segs(o['x'], o['y'], o['yaw'], o['L'], o['W'])
            for p in pts:
                if _inside(p, poly): return True
        for m in self.movers:
            mx, my = m['pos'](self.t)
            for p in pts:
                if math.hypot(p[0] - mx, p[1] - my) < m['r']: return True
        return False

    def static_boxes(self, include_bin=True, for_collision=False):
        out = list(self.obst)
        if include_bin and self.bin is not None:
            b = self.bin
            if b['state'] == 'tipped': out.append(dict(kind='bin', x=b['x'], y=b['y'], yaw=b['yaw'], L=BIN['h'], W=BIN['w'], H=0.6))
            else:
                if for_collision and self.seat_zone(): return out    # rear funnel engages bin: no collision
                out.append(dict(kind='bin', x=b['x'], y=b['y'], yaw=b['yaw'], L=BIN['d'], W=BIN['w'], H=BIN['h']))
        return out

    def seat_zone(self):
        b = self.bin
        hx = self.x + TUG['hook_x'] * math.cos(self.yaw); hy = self.y + TUG['hook_x'] * math.sin(self.yaw)
        hb = (b['x'] + 0.30 * math.cos(b['yaw']), b['y'] + 0.30 * math.sin(b['yaw']))
        return math.hypot(hx - hb[0], hy - hb[1]) < 0.35 and abs(wrap(self.yaw - b['yaw'])) < math.radians(25)

    # ---------- sensors ----------
    def lidar(self, nrays=360, rmax=12.0):
        """LD06 stand-in: 360 rays, 1 deg, 12 m, sigma 1.5 cm, beam at 0.31 m above ground.
        Rear arc |bearing|>115 deg is occluded by the tug body/rear frame/bin. Returns ranges from the lidar."""
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        ox = self.x + TUG['lidar_x'] * c; oy = self.y + TUG['lidar_x'] * s
        ang = np.radians(np.arange(nrays)) ; th = self.yaw + ang
        dx, dy = np.cos(th), np.sin(th)
        segs = []
        if len(self.lane.hedge):
            H = self.lane.hedge; mid = 0.5 * (H[:, :2] + H[:, 2:])
            segs.append(H[np.hypot(mid[:, 0] - ox, mid[:, 1] - oy) < rmax + 3])
        for o in self.static_boxes(include_bin=not self.attached):
            if o.get('H', 1) < 0.25: continue            # below the beam
            sg, _ = box_segs(o['x'], o['y'], o['yaw'], o['L'], o['W']); segs.append(np.array(sg))
        r = np.full(nrays, np.inf)
        segs = [g for g in segs if len(g)]
        if segs:
            S = np.concatenate(segs)
            ax, ay, bx, by = S[:, 0], S[:, 1], S[:, 2], S[:, 3]
            ex, ey = bx - ax, by - ay
            den = dx[:, None] * ey[None] - dy[:, None] * ex[None]
            qx, qy = ax[None] - ox, ay[None] - oy
            with np.errstate(divide='ignore', invalid='ignore'):
                t = (qx * ey[None] - qy * ex[None]) / den
                u = (qx * dy[:, None] - qy * dx[:, None]) / den
            ok = (np.abs(den) > 1e-9) & (t > 0.02) & (u >= 0) & (u <= 1)
            t = np.where(ok, t, np.inf); r = np.minimum(r, t.min(axis=1))
        for m in self.movers:
            mx, my = m['pos'](self.t); fx, fy = mx - ox, my - oy
            b = fx * dx + fy * dy; cc = fx * fx + fy * fy - m['r'] ** 2; disc = b * b - cc
            hit = (disc > 0) & (b > 0); tt = np.where(hit, b - np.sqrt(np.clip(disc, 0, None)), np.inf)
            r = np.minimum(r, tt)
        r = r + self.rng.normal(0, 0.015, nrays)
        r[r > rmax] = np.inf
        bearing = (np.degrees(ang) + 180) % 360 - 180
        r[np.abs(bearing) > 115] = np.nan               # occluded
        return r

    def gps_quality(self):
        s, lat = self.lane.project(np.array([self.x, self.y]))
        q = 'rtk'
        for s0, s1, k in self.gps_zones:
            if s0 <= s <= s1:
                if k == 'none': return 'none'
                q = 'float'
        return q

    # ---------- rear docking camera (renders an image; ArUco detection is real OpenCV) ----------
    CAM_W, CAM_H, CAM_F = 320, 240, 230.0      # ~70 deg HFOV

    def cam_pose(self):
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        pos = np.array([self.x + TUG['cam_x'] * c, self.y + TUG['cam_x'] * s, self.zxy(self.x, self.y) + TUG['cam_z']])
        look_yaw = self.yaw + math.pi; pitch = math.radians(-30)
        fwd = np.array([math.cos(look_yaw) * math.cos(pitch), math.sin(look_yaw) * math.cos(pitch), math.sin(pitch)])
        right = np.array([math.sin(look_yaw), -math.cos(look_yaw), 0.0]); up = np.cross(right, fwd)
        return pos, np.array([right, -up, fwd])     # rows: camera x(right), y(down), z(forward)

    def bin_faces(self):
        """World 3D corners of the bin's marker faces. Marker ids: 0 handle/back face (dock side), 1 front, 2 left, 3 right, 4 lid."""
        b = self.bin; z0 = self.zxy(b['x'], b['y']); c, s = math.cos(b['yaw']), math.sin(b['yaw'])
        def W(px, py, pz):     # bin frame: x toward handle face, y left, z up
            if b['state'] == 'tipped':   # lying on its front face, lid pointing along yaw
                px, pz = pz - BIN['h'] / 2, BIN['d'] / 2 - px
            return np.array([b['x'] + c * px - s * py, b['y'] + s * px + c * py, z0 + pz])
        d2, w2, m = BIN['d'] / 2, BIN['w'] / 2, 0.11
        zc = 0.72
        faces = {0: [W(d2, m, zc + m), W(d2, -m, zc + m), W(d2, -m, zc - m), W(d2, m, zc - m)],
                 1: [W(-d2, -m, zc + m), W(-d2, m, zc + m), W(-d2, m, zc - m), W(-d2, -m, zc - m)],
                 2: [W(-m, w2, zc + m), W(m, w2, zc + m), W(m, w2, zc - m), W(-m, w2, zc - m)],
                 3: [W(m, -w2, zc + m), W(-m, -w2, zc + m), W(-m, -w2, zc - m), W(m, -w2, zc - m)]}
        body = [W(px, py, pz) for px in (-d2, d2) for py in (-w2, w2) for pz in (0.05, BIN['h'])]
        return faces, body

    def render_cam(self):
        img = np.zeros((self.CAM_H, self.CAM_W, 3), np.uint8); img[:] = (70, 110, 60)          # grass/gravel
        img[: self.CAM_H // 6] = (200, 180, 150)
        if self.bin is None or self.attached: return img, None
        pos, R = self.cam_pose()
        def proj(P):
            q = R @ (np.asarray(P) - pos)
            if q[2] < 0.1: return None
            return (self.CAM_F * q[0] / q[2] + self.CAM_W / 2, self.CAM_F * q[1] / q[2] + self.CAM_H / 2, q[2])
        faces, body = self.bin_faces()
        bp = [proj(p) for p in body]
        if all(p is not None for p in bp):
            hull = cv2.convexHull(np.array([[p[0], p[1]] for p in bp], np.float32)).astype(np.int32)
            cv2.fillConvexPoly(img, hull, (40, 70, 30))
        vis = []
        for fid, corners in faces.items():
            pc = [proj(p) for p in corners]
            if any(p is None for p in pc): continue
            n = np.cross(corners[1] - corners[0], corners[3] - corners[0])      # outward normal check
            if n @ (pos - corners[0]) <= 0: continue
            dst = np.array([[p[0], p[1]] for p in pc], np.float32)
            if dst[:, 0].max() < 0 or dst[:, 0].min() > self.CAM_W or dst[:, 1].max() < 0 or dst[:, 1].min() > self.CAM_H: continue
            mk = cv2.cvtColor(MARKS[fid], cv2.COLOR_GRAY2BGR)
            pad = cv2.copyMakeBorder(mk, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=(255, 255, 255))
            src = np.array([[159, 0], [0, 0], [0, 159], [159, 159]], np.float32)
            Hm = cv2.getPerspectiveTransform(src, dst + (dst - dst.mean(0)) * (1/3))
            warped = cv2.warpPerspective(pad, Hm, (self.CAM_W, self.CAM_H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0))
            mask = cv2.warpPerspective(np.full((160, 160), 255, np.uint8), Hm, (self.CAM_W, self.CAM_H))
            img[mask > 0] = warped[mask > 0]; vis.append(fid)
        noise = self.rng.normal(0, 6, img.shape)
        img = np.clip(img.astype(float) + noise, 0, 255).astype(np.uint8)
        return img, vis


def _inside(p, poly):
    x, y = p; n = len(poly); ins = False
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1: ins = not ins
    return ins


def load_real_lane():
    R = json.load(open(os.path.join(DATA, 'route.json')))
    G = json.load(open(os.path.join(DATA, 'dem_grid.json')))
    return Lane(R['xy']), Terrain(G), R


def make_generic_lane():
    """Variant: narrower (2.8 m) winding lane, 300 m, sustained 12 % climb from the road to the house."""
    s = np.arange(0, 301, 2.0); xs = s * 1.0; ys = 12 * np.sin(s / 35.0)
    P = np.c_[xs, ys]
    lane = Lane(P, width=2.8, yard=(0, 20))
    ter = Terrain(grade_fn=lambda x, y: 60.0 - 0.12 * x)      # house at x=0 is 36 m above road end
    return lane, ter
