"""Rev G4 feature modules for the bin-tug SITL (used by companion.py / scenarios.py / scene.py of scripts_g4).
 - BinCalendar   : alternate-week bin rotation from an anchor date, drop / pickup times, which bins (config_g4/bin_calendar.json)
 - DropLayout    : programmable drop layout per spot (position, heading, spacing, hedge clearance) + validator (config_g4/drop_layout*.json)
 - RouteFile     : teach-and-repeat route file (taught route + exact home / drop poses) + validator (out/G4/routes/*.json)
 - Radar24       : front + rear 24 GHz FMCW radar model (range, radial speed, SNR, FOV, hedge occlusion)
 - Car           : moving vehicle with a simple driver model (oncoming / from behind, pass or follow, turn off)
 - edge helpers  : keep-left geometry (gap between the tug's left side and the left lane edge)
Everything here is SIMULATION / stand-in logic; numbers marked ASSUMED are not measured.
"""
import json, math, os, datetime as dt, numpy as np
from world import TUG, BIN, wrap, box_segs

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
CFG = os.path.join(ROOT, 'config_g6'); ROUTES = os.path.join(ROOT, 'out', 'G6', 'routes')   # G6: own config + outputs (G4 untouched)

# ---------------------------------------------------------------- keep-left (Ireland drives on the left)
KL_GAP = 0.40                  # target gap between the tug's left side and the left lane edge (spec 0.3-0.5 m)
KL_ZONE = (25.0, 24.0)         # keep-left between s = 25 m (end of the yard / hairpin) and L - 24 m (junction wait area)
def kl_lat(lane_width, sgn):
    """Centre-line lateral offset for keep-left. sgn=+1 driving down (house->road: left = +lat), -1 driving up."""
    return sgn * (lane_width / 2 - KL_GAP - TUG['half_w'])
def left_gap(lane_width, lat, sgn, half=TUG['half_w']):
    """Gap (m) between a body of half-width `half` centred at `lat` and the left lane edge for travel direction sgn."""
    return lane_width / 2 - (sgn * lat + half)


# ---------------------------------------------------------------- bin calendar
WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
class BinCalendar:
    def __init__(self, path=None, data=None):
        self.path = path or os.path.join(CFG, 'bin_calendar.json')
        self.d = data if data is not None else json.load(open(self.path))
        self.anchor = dt.date.fromisoformat(self.d['anchor_date'])
        self.wd = WEEKDAYS.index(self.d['collection_weekday'])
        if self.anchor.weekday() != self.wd: raise ValueError('anchor_date must be a collection day (%s)' % self.d['collection_weekday'])

    def week_of(self, coll_date):
        n = (coll_date - self.anchor).days // 7
        names = sorted(self.d['weeks'].keys()); a = names.index(self.d.get('anchor_week', names[0]))
        return names[(a + n) % len(names)]

    def collection_for_evening(self, date):
        """The evening `date` (drop evening = D-1) -> the collection the tug should prepare, or None."""
        cd = date + dt.timedelta(days=-int(self.d['drop']['day_offset']))
        return self.collection(cd)

    def collection(self, cd):
        if cd.weekday() != self.wd: return None
        if cd.isoformat() in self.d.get('skip_dates', []): return dict(date=cd.isoformat(), skipped=True, bins=[])
        moved = self.d.get('moved_dates', {}).get(cd.isoformat())
        wk = self.week_of(cd); bins = list(self.d['weeks'][wk])
        return dict(date=cd.isoformat(), weekday=WEEKDAYS[cd.weekday()], week=wk, bins=bins, moved_to=moved,
                    drop_at='D%+d %s' % (self.d['drop']['day_offset'], self.d['drop']['time']), drop_earliest=self.d['drop']['earliest'],
                    pickup_at='D%+d %s' % (self.d['pickup']['day_offset'], self.d['pickup']['time']), pickup_deadline=self.d['pickup']['deadline'])

    def table(self, start, n_weeks=8):
        out = []; d0 = start + dt.timedelta(days=(self.wd - start.weekday()) % 7)
        for k in range(n_weeks): out.append(self.collection(d0 + dt.timedelta(days=7 * k)))
        return out


# ---------------------------------------------------------------- programmable drop layout
class DropLayout:
    """Spots in lane coordinates: s_from_end (m from the lane end), lat (m, + = left of house->road) or 'auto' (from the
    hedge clearance), heading_deg (handle direction relative to the up-lane direction, + = CCW), spacing_m (min clear gap
    bin-to-bin to every other spot), hedge_clear_m (min clear gap bin-to-hedge line). `order` = spots used for 1, 2, 3 bins
    (the last one in the list is filled last and emptied last)."""
    def __init__(self, path=None, data=None):
        self.path = path or os.path.join(CFG, 'drop_layout_default.json')
        self.d = data if data is not None else json.load(open(self.path)); self.name = self.d.get('name', os.path.basename(self.path))

    def spot(self, S, k):
        sp = self.d['spots'][k]; s = S.L - sp['s_from_end']; lat = sp['lat']
        if lat == 'auto':      # as far left as the hedge clearance allows (left verge strip)
            hl = S.lane.width / 2 + 0.25; h = math.radians(sp.get('heading_deg', 0.0))
            half = 0.5 * (BIN['w'] * abs(math.cos(h)) + BIN['d'] * abs(math.sin(h)))
            lat = hl - sp['hedge_clear_m'] - half
        return dict(s=s, lat=float(lat), heading_deg=float(sp.get('heading_deg', 0.0)), spacing_m=sp.get('spacing_m', 0.5),
                    hedge_clear_m=sp.get('hedge_clear_m', 0.3), name=k)

    def spots(self, S): return {k: self.spot(S, k) for k in self.d['spots']}

    def pads_for(self, bins):
        """bins in drop order -> {bin: spot}; the last-dropped bin gets the last spot of `order` (the mouth)."""
        if self.d.get('order_semantics') == 'drop_first':      # Rev G6 handles-out: first-dropped bin -> first spot (A, the mouth)
            return {b: k for b, k in zip(bins, self.d['order'][:len(bins)])}
        order = self.d['order'][-len(bins):]
        return {b: k for b, k in zip(bins, order)}

    def bin_pose(self, S, k):
        sp = self.spot(S, k); x, y = S.lane.point(sp['s'], sp['lat'])
        yaw = wrap(S.lane.heading(sp['s']) + math.pi + math.radians(sp['heading_deg']))      # handle faces up-lane (+ offset)
        return float(x), float(y), yaw

    def validate(self, S, room_fn=None):
        """Checks per spot: legal boundary (bin footprint >= 0.45 m inside), inside the tug geofence, hedge clearance >= the
        programmed value, spacing to every other spot >= the programmed value, a 2.6 m dock corridor in front of the handle,
        and (lane spots) a pass corridor >= 1.36 m on the far side. Returns (ok, rows)."""
        rows = []; polys = {}
        for k in self.d['spots']:
            x, y, yaw = self.bin_pose(S, k); _, poly = box_segs(x, y, yaw, BIN['d'], BIN['w']); polys[k] = (np.array(poly), (x, y, yaw))
        allok = True
        for k, (poly, (x, y, yaw)) in polys.items():
            sp = self.spot(S, k); why = []
            legal = min(S.boundary_dist(p) for p in poly)
            if legal < 0.45: why.append('bin %.2f m from the private boundary (< 0.45)' % legal)
            hd = min(S.hedge_dist(p) for p in poly)
            if hd < sp['hedge_clear_m'] - 0.02: why.append('hedge clearance %.2f < %.2f m' % (hd, sp['hedge_clear_m']))
            if not S.in_fence((x, y), margin=-S.FENCE_IN - 0.2): why.append('bin centre outside the geofence')
            gaps = []
            for k2, (p2, _) in polys.items():
                if k2 == k: continue
                g = poly_gap(poly, p2); gaps.append((k2, g))
                if g < sp['spacing_m'] - 0.02: why.append('only %.2f m to spot %s (< %.2f)' % (g, k2, sp['spacing_m']))
            dock_ok = True
            if room_fn is not None:
                h = np.array([math.cos(yaw), math.sin(yaw)]); D = np.array([x, y]) + h * (0.30 - TUG['hook_x'])
                order = self.d['order']      # pickup order = drop order: spots later in `order` are still occupied when k is picked up
                later = order[order.index(k) + 1:] if k in order else [k2 for k2 in polys if k2 != k]
                if self.d.get('order_semantics') == 'drop_first' and k in order: later = order[:order.index(k)]   # G6: picked up in reverse
                others = [np.array(polys[k2][1][:2]) for k2 in later]
                dock_ok = room_fn(D, yaw, others)
                if not dock_ok: why.append('no 2.6 m dock corridor in front of the handle')
            s, lat = S.lane.project(np.array([x, y])); passc = None
            if s < S.lane.mouth[0]:
                lo = min(S.lane.project(p)[1] for p in poly)
                passc = lo - (-S.lane.width / 2)
                if passc < 2 * TUG['half_w'] + 0.6: why.append('pass corridor %.2f m < 1.36 m' % passc)
            rows.append(dict(spot=k, s_from_end=round(S.L - s, 2), lat=round(lat, 2), heading_deg=sp['heading_deg'], legal_m=round(legal, 2),
                             hedge_m=round(hd, 2), hedge_req=sp['hedge_clear_m'], min_gap_m=round(min(g for _, g in gaps), 2) if gaps else None,
                             spacing_req=sp['spacing_m'], pass_corridor_m=None if passc is None else round(passc, 2), dock_corridor=dock_ok,
                             ok=not why, why='; '.join(why)))
            allok &= not why
        return allok, rows


def poly_gap(A, B):
    """Min distance between two convex polygons (0 if they overlap)."""
    from matplotlib.path import Path
    if Path(A).contains_points(B).any() or Path(B).contains_points(A).any(): return 0.0
    def segd(P, a, b):
        ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab + 1e-12), 0, 1); return np.linalg.norm(P - (a + t[:, None] * ab), axis=1).min()
    d = 9e9
    for i in range(len(A)): d = min(d, segd(B, A[i], A[(i + 1) % len(A)]))
    for i in range(len(B)): d = min(d, segd(A, B[i], B[(i + 1) % len(B)]))
    return float(d)


# ---------------------------------------------------------------- teach-and-repeat route file
class RouteFile:
    @staticmethod
    def save(path, d):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(d, open(path, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else (o.tolist() if hasattr(o, 'tolist') else str(o)))

    @staticmethod
    def load(path): return json.load(open(path))

    @staticmethod
    def resample(pts, step=4.0, turn_deg=12.0):
        """Taught polyline [[x,y,yaw,v],...] -> waypoints every `step` m or whenever the heading turned `turn_deg`."""
        P = np.array([p[:2] for p in pts]); out = [P[0]]; acc = 0.0; h0 = pts[0][2]
        for i in range(1, len(P)):
            acc += np.linalg.norm(P[i] - P[i - 1])
            if acc >= step or abs(wrap(pts[i][2] - h0)) > math.radians(turn_deg): out.append(P[i]); acc = 0.0; h0 = pts[i][2]
        if np.linalg.norm(out[-1] - P[-1]) > 0.3: out.append(P[-1])
        return [tuple(map(float, p)) for p in out]

    @staticmethod
    def validate(S, d):
        """Every taught point inside the geofence, tug body clear of the hedge lines, footprint on private ground; drop and home
        poses inside the fence with a dock corridor. Returns dict of checks (route is rejected if any 'ok' is False)."""
        res = {}
        for key in ('route_down', 'route_up'):
            pts = np.array([p[:2] for p in d[key]]); bad = [i for i, p in enumerate(pts) if not S.in_fence(p, margin=-0.1)]
            hed = []
            for p in d[key][::3]:
                c, s_ = math.cos(p[2]), math.sin(p[2])
                for fx in (TUG['front'], -TUG['rear']):
                    for fy in (-TUG['half_w'], TUG['half_w']):
                        q = (p[0] + c * fx - s_ * fy, p[1] + s_ * fx + c * fy); sq, lq = S.lane.project(np.array(q))
                        if sq < S.lane.mouth[0] and not (S.lane.yard[0] <= sq <= S.lane.yard[1]): hed.append(S.lane.width / 2 + 0.25 - abs(lq))
            res[key] = dict(n=len(pts), length_m=round(float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum()), 1), outside_fence=len(bad),
                            min_hedge_clear_m=round(min(hed), 2) if hed else None, ok=(len(bad) == 0 and (not hed or min(hed) > 0.05)))
        for key in ('home_pose', 'drop_pose'):
            p = d[key]; ok = S.in_fence((p['x'], p['y']), margin=-S.FENCE_IN - 0.3) and S.boundary_dist((p['x'], p['y'])) > 0.45
            res[key] = dict(ok=bool(ok), boundary_m=round(S.boundary_dist((p['x'], p['y'])), 2))
        res['ok'] = all(v['ok'] for v in res.values() if isinstance(v, dict))
        return res


# ---------------------------------------------------------------- 24 GHz radar (front + rear)
# HLK-LD2451 (Hi-Link): 24-24.25 GHz FMCW, 1T2R, up to 100 m for vehicles, azimuth +-15..20 deg (sources differ), 5 V > 300 mA
# (107 mA average), UART 115200, a frame every 100 ms, reports only targets moving faster than a set speed (0-120 km/h).
# Model: FOV +-20 deg, 30 m, min |radial speed| 2 km/h; noise, Pd and 'SNR' are ASSUMED (the module outputs no SNR -
# in hardware the vehicle/person split would come from the lidar extent + the module's own vehicle detection).
RADAR = dict(fov_deg=20.0, rmax_vehicle=30.0, rmax_person=8.0, sig_r=0.10, sig_v=0.10, pd_vehicle=0.95, pd_person=0.6, v_min=0.55,
             snr_vehicle=26.0, snr_person=11.0, snr_static_box=22.0, min_r_rear_towing=2.2, rate_hz=10.0)
class Radar24:
    """Two 24 GHz FMCW modules: front (bumper, facing forward) and rear (top of the mast, 1.3 m, looking back over the bin).
    Each reports targets: range (nearest reflecting point), radial speed (+ = receding), azimuth, SNR. It cannot tell vehicles
    from other things on its own; the companion uses SNR + lidar extent + ego-motion compensation. Hedges block line of sight."""
    def __init__(self, rng): self.rng = rng; self.prev = {}

    def _los_clear(self, H, a, b):
        if not len(H): return True
        A = H[:, :2]; B = H[:, 2:]; d = b - a; e = B - A
        den = d[0] * e[:, 1] - d[1] * e[:, 0]; q = A - a
        with np.errstate(divide='ignore', invalid='ignore'):
            t = (q[:, 0] * e[:, 1] - q[:, 1] * e[:, 0]) / den; u = (q[:, 0] * d[1] - q[:, 1] * d[0]) / den
        return not np.any((np.abs(den) > 1e-9) & (t > 0.02) & (t < 0.98) & (u >= 0) & (u <= 1))

    def scan(self, w):
        out = []
        c, s_ = math.cos(w.yaw), math.sin(w.yaw)
        mounts = {'front': (np.array([w.x + TUG['front'] * c, w.y + TUG['front'] * s_]), w.yaw),
                  'rear': (np.array([w.x - 0.30 * c, w.y - 0.30 * s_]), wrap(w.yaw + math.pi))}
        H = w.site.hedges_near((w.x, w.y), 35.0)
        targets = []
        for vh in getattr(w, 'vehicles', []):
            if not vh.on: continue
            _, poly = box_segs(vh.x, vh.y, vh.yaw, vh.L, vh.W)
            targets.append(('veh:%s' % vh.name, np.array(poly), np.array([vh.vx, vh.vy]), RADAR['snr_vehicle'], RADAR['rmax_vehicle'], RADAR['pd_vehicle']))
        for m in w.movers:
            p = np.array(m['pos'](w.t)); pp = np.array(m['pos'](w.t - 0.1)); vel = (p - pp) / 0.1
            if np.linalg.norm(p - np.array([w.x, w.y])) > 40: continue
            targets.append(('mov:%s' % m['kind'], p[None], vel, RADAR['snr_person'], RADAR['rmax_person'], RADAR['pd_person']))
        for o in w.obst:      # parked cars / static boxes: real radar reflectors with zero ground speed
            if o.get('H', 1) < 0.3: continue
            _, poly = box_segs(o['x'], o['y'], o['yaw'], o['L'], o['W'])
            targets.append(('static:%s' % o['kind'], np.array(poly), np.zeros(2), RADAR['snr_static_box'], RADAR['rmax_vehicle'], 0.9))
        ego = np.array([w.v * c, w.v * s_])
        for side, (pos, look) in mounts.items():
            for name, poly, vel, snr, rmax, pd in targets:
                if len(poly) > 1:      # nearest point of the outline (edges sampled)
                    pts = np.concatenate([poly[i] + np.linspace(0, 1, 6)[:, None] * (poly[(i + 1) % len(poly)] - poly[i]) for i in range(len(poly))])
                else: pts = poly
                d = np.linalg.norm(pts - pos, axis=1); i = int(np.argmin(d)); p = pts[i]; r = float(d[i])
                if r > rmax or r < 0.3: continue
                az = wrap(math.atan2(p[1] - pos[1], p[0] - pos[0]) - look)
                if abs(az) > math.radians(RADAR['fov_deg']): continue
                if side == 'rear' and w.attached and r < RADAR['min_r_rear_towing']: continue     # own bin (zero Doppler) gated out
                if not self._los_clear(H, pos, p): continue
                if self.rng.random() > pd: continue
                u = (p - pos) / max(r, 1e-6); vr = float((vel - ego) @ u)          # + = receding
                if abs(vr) < RADAR['v_min']: continue                              # module's minimum-speed gate (2 km/h)
                out.append(dict(side=side, name=name, r=round(r + float(self.rng.normal(0, RADAR['sig_r'])), 2),
                                vr=round(vr + float(self.rng.normal(0, RADAR['sig_v'])), 2), az=round(math.degrees(az), 1),
                                snr=round(snr + float(self.rng.normal(0, 2.0)), 1), ego_los=round(float(-ego @ u), 2)))
        return out


# ---------------------------------------------------------------- moving vehicle with a simple driver model
class Car:
    """A car / van on the lane, in lane coordinates. dirn=-1 drives up-lane (toward the house, i.e. oncoming for a tug going
    down), +1 drives down-lane. mode: 'pass' (slows, moves over and passes the tug if there is room, else stops and waits),
    'follow' (closes up and follows at ~follow_gap m, never passes), and leaves the scene at s_off (turns into a gate).
    It appears when the tug passes lane station appear_s (or at t_on). Driver reaction: sees the tug at 30 m."""
    def __init__(self, name, s0, dirn, v_cruise=4.5, mode='pass', lat0=0.0, appear_s=None, t_on=None, s_off=None, follow_gap=4.0,
                 v_pass=1.5, L=4.3, W=1.8, H=1.45, wait_after_stop=0.0):
        self.name = name; self.s = s0; self.dirn = dirn; self.vc = v_cruise; self.mode = mode; self.lat = lat0; self.lat_cmd = lat0
        self.appear_s = appear_s; self.t_on = t_on; self.s_off = s_off; self.gap_f = follow_gap; self.v_pass = v_pass
        self.L, self.W, self.H = L, W, H; self.v = v_cruise; self.on = False; self.gone = False; self.x = self.y = 0.0; self.yaw = 0.0
        self.vx = self.vy = 0.0; self.passed = False; self.min_gap = 99.0; self.min_gap_bin = 99.0; self.stopped_t = 0.0; self.log = []
        self.wait_after_stop = wait_after_stop; self.kind = 'car'

    def _tug_extent(self, w):
        """Tug + towed bin in lane coordinates: (s_min, s_max, lat_min, lat_max)."""
        S = w.site; pts = w.footprint(); SL = np.array([S.lane.project(np.array(p)) for p in pts])
        return SL[:, 0].min(), SL[:, 0].max(), SL[:, 1].min(), SL[:, 1].max()

    def update(self, w, dt_):
        S = w.site
        if self.gone: return
        if not self.on:
            if (self.appear_s is not None and S.lane.project(np.array([w.x, w.y]))[0] > self.appear_s) or (self.t_on is not None and w.t >= self.t_on):
                self.on = True; self.t0 = w.t
            else: return
        smin, smax, lmin, lmax = self._tug_extent(w)
        front = self.s + self.dirn * self.L / 2
        gap = (smin - front) if self.dirn > 0 else (front - smax)          # along-lane gap to the tug (+ = tug ahead)
        hl = S.lane.width / 2 + 0.25
        room_r = (lmin - 0.5) - (-hl + 0.1)        # space to pass on the -lat side
        room_l = (hl - 0.1) - (lmax + 0.5)         # space on the +lat side
        v_t = self.vc
        if gap > -self.L and not self.passed:
            if self.mode == 'pass':
                if max(room_r, room_l) >= self.W:
                    side = -1 if room_r >= room_l else 1
                    self.lat_cmd = side * (hl - 0.1 - self.W / 2) if gap < 30 else self.lat_cmd
                    if gap < 12: v_t = self.v_pass
                    elif gap < 30: v_t = min(self.vc, 2.5)
                else:      # no room: stop 4 m short and wait
                    v_t = 0.0 if gap < 6 else (1.5 if gap < 15 else self.vc)
            else:          # follow: close up to follow_gap and keep it
                tug_v = w.v if abs(w.v) > 0.02 else 0.0
                v_t = max(0.0, min(self.vc, abs(tug_v) + 0.6 * (gap - self.gap_f))) if gap < 25 else self.vc
            if gap < -0.5 and self.mode == 'pass' and abs(self.lat - self.lat_cmd) < 0.3: pass
        if gap < -(self.L + 1.0) and not self.passed:
            self.passed = True
        if self.passed:
            self.lat_cmd = 0.0; v_t = self.vc
        # longitudinal dynamics (accel 1.5 m/s^2, brake 3 m/s^2)
        a = np.clip((v_t - self.v) / max(dt_, 1e-3), -3.0, 1.5); self.v = max(0.0, self.v + a * dt_)
        dl = np.clip(self.lat_cmd - self.lat, -0.6 * dt_, 0.6 * dt_); self.lat += dl
        self.s += self.dirn * self.v * dt_
        if self.v < 0.05: self.stopped_t += dt_
        if (self.s_off is not None and self.dirn * (self.s - self.s_off) > 0) or self.s < -5 or self.s > S.L + 5:
            self.gone = True; self.on = False; self.x = self.y = 1e4; self.vx = self.vy = 0.0; return
        h = S.lane.heading(self.s); p = S.lane.point(self.s, self.lat)
        self.yaw = wrap(h + (0 if self.dirn > 0 else math.pi)); nx, ny = float(p[0]), float(p[1])
        self.vx = (nx - self.x) / dt_ if self.x != 0 else 0.0; self.vy = (ny - self.y) / dt_ if self.y != 0 else 0.0
        self.x, self.y = nx, ny
        # truth gaps (evaluation only)
        _, cp = box_segs(self.x, self.y, self.yaw, self.L, self.W); cp = np.array(cp)
        c, s_ = math.cos(w.yaw), math.sin(w.yaw)
        tx = w.x + c * (TUG['front'] - TUG['rear']) / 2; ty = w.y + s_ * (TUG['front'] - TUG['rear']) / 2
        _, tp = box_segs(tx, ty, w.yaw, TUG['front'] + TUG['rear'], 2 * TUG['half_w'])
        self.min_gap = min(self.min_gap, poly_gap_fast(cp, np.array(tp)))
        if w.attached and w.bin is not None:
            _, bp = box_segs(w.bin['x'], w.bin['y'], w.bin['yaw'], BIN['d'], BIN['w'])
            self.min_gap_bin = min(self.min_gap_bin, poly_gap_fast(cp, np.array(bp)))

    def box(self):
        return dict(kind=self.kind, x=self.x, y=self.y, yaw=self.yaw, L=self.L, W=self.W, H=self.H)


def poly_gap_fast(A, B):
    if np.linalg.norm(A.mean(0) - B.mean(0)) > 8: return 8.0
    return poly_gap(A, B)


# ---------------------------------------------------------------- Rev G4 g) adaptive drop spot: allowed areas, keep-outs, alternates
def _pip(P, x, y):
    inside = False; j = len(P) - 1
    for i in range(len(P)):
        if ((P[i, 1] > y) != (P[j, 1] > y)) and (x < (P[j, 0] - P[i, 0]) * (y - P[i, 1]) / (P[j, 1] - P[i, 1] + 1e-12) + P[i, 0]): inside = not inside
        j = i
    return inside


class DropAreas:
    """User-drawn ALLOWED drop areas (inclusion polygons per slot family) and KEEP-OUT polygons (exclusion zones), plus the
    ordered alternate slots per programmed slot (taught list or 'auto' = generated inside the allowed area)."""
    def __init__(self, S, path=None, extra_keepouts=()):
        self.S = S; self.path = path or os.path.join(CFG, 'drop_areas.json'); self.d = json.load(open(self.path))
        self.areas = {k: self.to_xy(v) for k, v in self.d['allowed_areas'].items()}
        self.keepouts = [dict(name=k['name'], P=self.to_xy(k)) for k in list(self.d.get('keepouts', [])) + list(extra_keepouts)]

    def to_xy(self, a):
        S = self.S; f = a.get('frame', 'end'); Q = [tuple(q) for q in a['poly']]; out = []
        for i in range(len(Q)):            # densify each edge in lane coordinates (0.4 m) so a curved lane keeps the shape
            p0, p1 = np.array(Q[i], float), np.array(Q[(i + 1) % len(Q)], float); n = max(1, int(np.linalg.norm(p1 - p0) / 0.4))
            for k in range(n):
                q = p0 + (p1 - p0) * k / n; out.append(S.lane.point(S.L - q[0] if f == 'end' else q[0], q[1]))
        return np.array(out, float)

    def install(self):
        """Put the keep-outs into the site geofence (Site.in_fence rejects points within 0.5 m of a keep-out)."""
        self.S.keepouts = list(self.keepouts); return self

    def area_of(self, slot): return self.d['slot_area'].get('home' if slot.startswith('home') else slot)

    def bin_poly(self, x, y, yaw, infl=0.0):
        _, poly = box_segs(x, y, yaw, BIN['d'] + 2 * infl, BIN['w'] + 2 * infl); return np.array(poly)

    def legal(self, x, y, yaw, area, hedge_clear, others, spacing, room_fn=None):
        """Footprint inside the allowed area, outside every keep-out (>= 0.1 m), inside the private-ground fence (>= 0.45 m),
        hedge clearance, spacing to the other programmed slots, and a dock corridor (if room_fn given)."""
        S = self.S; poly = self.bin_poly(x, y, yaw)
        A = self.areas[area]
        if not all(_pip(A, *p) for p in poly): return False, 'outside allowed area'
        if self.keepouts and max(S.keepout_depth(p) for p in poly) > -0.1: return False, 'in/near keep-out'
        if min(S.boundary_dist(p) for p in poly) < 0.45: return False, 'not on private ground'
        if min(S.hedge_dist(p) for p in poly) < hedge_clear - 0.02: return False, 'hedge clearance'
        for o in others:
            if poly_gap(poly, self.bin_poly(*o)) < spacing - 0.02: return False, 'spacing'
        if room_fn is not None and not room_fn(x, y, yaw): return False, 'no dock corridor'
        return True, ''

    def alternates(self, slot, pose, hedge_clear, others, spacing, room_fn=None):
        """Ordered alternates for one programmed slot: the taught list if given, else a grid inside the allowed area,
        same handle heading as the primary (handles toward the lane), sorted by distance from the primary."""
        spec = self.d['alternates'].get('home' if slot.startswith('home') else slot, 'auto'); area = self.area_of(slot)
        x0, y0, yaw0 = pose; out = []
        if spec != 'auto':
            cands = [(self.S.lane.point(self.S.L - q[0] if self.d['allowed_areas'][area].get('frame') == 'end' else q[0], q[1]), yaw0 + math.radians(q[2] if len(q) > 2 else 0)) for q in spec]
        else:
            A = self.areas[area]; g = self.d.get('grid_m', 0.4); cands = []
            xs = np.arange(A[:, 0].min(), A[:, 0].max() + g, g); ys = np.arange(A[:, 1].min(), A[:, 1].max() + g, g)
            for x in xs:
                for y in ys:
                    if _pip(A, x, y): cands.append((np.array([x, y]), yaw0))
        for p, yaw in cands:
            if math.hypot(p[0] - x0, p[1] - y0) < 0.5: continue
            s_, _ = self.S.lane.project(np.asarray(p, float)); yaw = wrap(self.S.lane.heading(s_) + wrap(yaw0 - self.S.lane.heading(self.S.lane.project(np.array([x0, y0]))[0])))
            ok, why = self.legal(p[0], p[1], yaw, area, hedge_clear, others, spacing, room_fn)
            if ok: out.append((float(p[0]), float(p[1]), float(yaw)))
        out.sort(key=lambda q: math.hypot(q[0] - x0, q[1] - y0))
        sel = []
        for q in out:
            if all(math.hypot(q[0] - r[0], q[1] - r[1]) >= self.d.get('min_alt_separation_m', 0.6) for r in sel): sel.append(q)
            if len(sel) >= self.d.get('max_alternates', 6): break
        return sel
