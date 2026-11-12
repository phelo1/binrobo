# Scene extensions for the lane SITL: road + geofence, junction bell-mouth, several bins (ours + neighbour's),
# bin mass / load, rear docking-funnel capture, bumper orbit-nudge model, night camera with IR illuminator +
# retro-reflective tags and auto-exposure, ArUco detection + PnP, energy model. Builds on world.py.
import json, math, os, numpy as np, cv2
import g6_features as G6
from world import (World, Lane, Terrain, TUG, BIN, VMAX, HITCH_CAP, ARUCO_DICT, box_segs, _inside, wrap,
                   ll2xy, xy2ll, LAT0, LON0, load_real_lane, make_generic_lane, DATA)

M_TUG = float(os.environ.get('BT_MASS', '95'))   # G6: operating mass (kg) is a parameter: 95 (current) or 105 (g6-mech option). G1-G4 used 105.6
M_BIN_FULL, M_BIN_EMPTY = 55.0, 13.0          # 240 L wheelie bin: full general waste (assumed) / empty
DOCK_OFF = 0.30 - TUG['hook_x']              # tug drive-axle centre ahead of bin centre when seated (0.915 m)
MARK_SIDE = 0.22                             # printed tag side incl. black border (m)
# Rev G3 (ported from revG_alt, re-mapped to the master tag plan): one 4-tag set per bin, 4x4 ArUco. Brian's bins: black 0-3,
# green 4-7, brown 30-33; neighbour 10-13; 20 = charging dock tag (Rev G). Ownership is by ID range, never by "< 10".
BIN_ID0 = dict(black=0, green=4, brown=30, neighbour=10)
OUR_ID0 = (0, 4, 30)
_all_ids = list(range(0, 8)) + list(range(10, 14)) + list(range(20, 24)) + list(range(30, 34))
def id0_of(tag): return tag - tag % 4 if tag < 20 else (30 if 30 <= tag < 34 else 20)
def owner_of(tag):
    i0 = id0_of(tag); return {v: k for k, v in BIN_ID0.items()}.get(i0, 'dock' if i0 == 20 else '?')
def face_of(tag): return tag - id0_of(tag)
CROSSBEAM_HALF = 0.33        # Rev G3 (F7): rear centre gap between the corner bump strips = the bin's wheel-stop crossbeam
PACK_WH_NOM = 25.6 * float(os.environ.get('BT_PACK_AH', '20'))   # G6: parts pick 8S LFP 20 Ah = 512 Wh (G3/G4: 12 Ah = 307 Wh); env BT_PACK_AH
def pack_cold_factor(t_c):   # deliverable fraction of nominal capacity vs cell temperature (ASSUMED, typical LFP datasheet shape)
    return float(np.interp(t_c, [-20, -10, 0, 10, 25], [0.60, 0.75, 0.88, 0.95, 1.0]))
WORK_LAMP_GAIN = 160.0       # Rev G3: 3 W rear white work lamp, 0.15 m beside the lens (revG_alt model scaled from 2 x 5 W)
LAMP_OFFSET = 0.15
MARKS = {i: cv2.aruco.generateImageMarker(ARUCO_DICT, i, 120, borderBits=1) for i in _all_ids}
DET = cv2.aruco.ArucoDetector(ARUCO_DICT, cv2.aruco.DetectorParameters())


def road_polyline():
    H = {w['id']: w for w in json.load(open(os.path.join(DATA, 'osm_highways.json')))}
    return np.array([ll2xy(*p) for p in H['614523014']['geom']])


def seg_dist(p, A, B):
    ab = B - A; t = np.clip(((p - A) * ab).sum(-1) / ((ab * ab).sum(-1) + 1e-12), 0, 1)
    return np.linalg.norm(p - (A + t[..., None] * ab), axis=-1)


def _project_fast(self, p):
    p = np.asarray(p, float); A = self.P[:-1]; B = self.P[1:]; ab = B - A; L2 = (ab * ab).sum(1)
    t = np.clip(((p - A) * ab).sum(1) / L2, 0, 1); q = A + ab * t[:, None]; d = np.linalg.norm(p - q, axis=1)
    i = int(np.argmin(d)); side = np.sign(ab[i, 0] * (p - A[i])[1] - ab[i, 1] * (p - A[i])[0])
    return self.s[i] + t[i] * math.sqrt(L2[i]), side * d[i]
Lane.project = _project_fast


class Site:
    """Lane + terrain + road + geofence. The last 12 m of the lane is an open bell mouth (no lane hedges)."""
    def __init__(self, variant='real'):
        self.variant = variant
        if variant == 'real':
            R = json.load(open(os.path.join(DATA, 'route.json'))); G = json.load(open(os.path.join(DATA, 'dem_grid.json')))
            P = np.asarray(R['xy']); Ltot = np.linalg.norm(np.diff(P, axis=0), axis=1).sum()
            self.lane = Lane(P, width=3.6, yard=(0, 25), mouth=(Ltot - 12, Ltot + 50)); self.ter = Terrain(G)
            self.road = road_polyline(); self.road_half = 3.0; self.mouth_half = 4.5
            # Rev G3 legal note: the road verge is likely a 'public place'. Private ground is taken to start BOUNDARY m from the
            # road centre-line (3.0 m half carriageway + 3.0 m verge - ASSUMED, to be confirmed on the folio map / site survey).
            self.boundary = 6.0
        else:   # generic steeper/narrower variant (12 %, 2.8 m), road across the far end
            self.lane, self.ter = make_generic_lane()
            Ltot = self.lane.length; e = self.lane.P[-1]; h = self.lane.heading(Ltot); n = np.array([-math.sin(h), math.cos(h)])
            self.road = np.array([e - 60 * n, e + 60 * n]); self.road_half = 3.0; self.mouth_half = 3.5; self.boundary = 6.0
            self.lane.mouth = (Ltot - 8, Ltot + 50); self.lane._hedges()
        self.L = self.lane.length
        self._extra_hedges()
        self.keepouts = []          # Rev G4: user keep-out polygons (list of dict(name, P=Nx2 xy)); inclusion fence = in_fence()
        self.KO_CLEAR = 0.5         # tug axle must stay >= 0.5 m outside a keep-out (body half-width 0.38 + 0.12)

    def _extra_hedges(self):
        segs = [self.lane.hedge] if len(self.lane.hedge) else []
        for side in (+1, -1):
            pts = []
            for s in np.arange(self.lane.mouth[0], self.L + 6, 1.0):
                p = self.lane.point(s, side * self.mouth_half)
                if self.road_dist(p) < self.road_half + 0.6: break
                pts.append(p)
            if len(pts) > 1: segs.append(np.array([np.r_[pts[k], pts[k + 1]] for k in range(len(pts) - 1)]))
            a = self.lane.point(self.lane.mouth[0], side * (self.lane.width / 2 + 0.25)); b = self.lane.point(self.lane.mouth[0], side * self.mouth_half)
            segs.append(np.array([np.r_[a, b]]))
        R = self.road; end = self.lane.P[-1]
        for off in (+1, -1):
            for i in range(len(R) - 1):
                a, b = R[i], R[i + 1]; d = b - a; L = np.linalg.norm(d)
                if L < 1e-6: continue
                n = np.array([-d[1], d[0]]) / L
                for t in np.arange(0, L, 2.0):
                    p = a + d * t / L + n * off * (self.road_half + 1.0); q = a + d * min(t + 2, L) / L + n * off * (self.road_half + 1.0)
                    m = 0.5 * (p + q)
                    if np.linalg.norm(m - end) > 70 or np.linalg.norm(m - end) < 9.5: continue
                    segs.append(np.array([np.r_[p, q]]))
        extra = [s for s in segs[1:] if len(s)] if len(self.lane.hedge) else [s for s in segs if len(s)]
        if self.variant == 'real':
            # Rev G6: lane hedges rebuilt with the surveyed gaps (gateways, open field, farm crossing). MAP = surveyed hedge line
            # (used by the Pi's map filter / planning); TRUTH = hedge face with irregularity + overgrown narrowings (lidar only).
            mp, tr = [], []
            for side in (+1, -1):
                ss = np.arange(self.lane.yard[1], self.lane.mouth[0] + 0.01, 1.0)
                for a, b in zip(ss[:-1], ss[1:]):
                    if G6.in_gap(0.5 * (a + b), side): continue
                    mp.append(np.r_[self.lane.point(a, side * G6.HL_NOM), self.lane.point(b, side * G6.HL_NOM)])
                    tr.append(np.r_[self.lane.point(a, side * (G6.HL_NOM - G6.hedge_offset(a, side))), self.lane.point(b, side * (G6.HL_NOM - G6.hedge_offset(b, side)))])
            self.hedge = np.concatenate([np.array(mp)] + extra); self.hedge_truth = np.concatenate([np.array(tr)] + extra)
        else:
            self.hedge = np.concatenate([s for s in segs if len(s)]); self.hedge_truth = self.hedge
        self.lane.hedge = self.hedge_truth    # lidar in world.py reads lane.hedge (G6: the truth hedge faces)

    def road_dist(self, p):
        p = np.asarray(p, float)
        return float(seg_dist(p[None], self.road[:-1], self.road[1:]).min())

    FENCE_IN = 1.2           # Rev G3: tug axle fence sits 1.2 m inside the private boundary (front overhang 0.76 m + 0.44 m)

    def boundary_dist(self, p):
        """Signed distance (m) of a point inside the private boundary (negative = on the public verge / road)."""
        return self.road_dist(p) - self.boundary

    def fp_ok(self, p, legal_margin=0.3):
        """Rev G3: a FOOTPRINT point (bumper, corner) is inside the lane corridor and >= legal_margin inside the private boundary."""
        return self.in_fence(p, margin=legal_margin - self.FENCE_IN)

    def keepout_depth(self, p):
        """Rev G4: signed distance of a point to the nearest keep-out polygon (+ = inside by that much, - = outside by that much)."""
        best = -99.0; p = np.asarray(p, float)
        for k in self.keepouts:
            P = k['P']; A = P; B = np.roll(P, -1, axis=0)
            d = float(seg_dist(p[None], A, B).min())
            x, y = p; inside = False; j = len(P) - 1
            for i in range(len(P)):
                if ((P[i, 1] > y) != (P[j, 1] > y)) and (x < (P[j, 0] - P[i, 0]) * (y - P[i, 1]) / (P[j, 1] - P[i, 1] + 1e-12) + P[i, 0]): inside = not inside
                j = i
            best = max(best, d if inside else -d)
        return best

    def in_fence(self, p, margin=0.0, ko=True):
        if ko and self.keepouts and self.keepout_depth(p) > -(self.KO_CLEAR + max(margin, 0.0)): return False
        return self._in_fence(p, margin)

    def _in_fence(self, p, margin=0.0):
        """Tug geofence: inside the lane corridor / yard / bell mouth and (Rev G3) on private ground, FENCE_IN m inside the
        assumed private boundary (was: >= road_half + 0.5 m from the road centre-line, i.e. on the verge)."""
        s, lat = self.lane.project(np.asarray(p, float))
        if s >= self.lane.mouth[0]: half = self.mouth_half - 0.2
        elif self.lane.yard[0] <= s <= self.lane.yard[1]: half = 6.0
        else: half = self.lane.width / 2 + 0.1
        if abs(lat) > half - margin: return False
        if s < -3: return False
        return self.road_dist(p) >= self.boundary + self.FENCE_IN + margin

    def fence_margin(self, p):
        """Rev G6: how far (m) a point (the tug axle) is inside the geofence (negative = outside). Same rules as _in_fence."""
        s, lat = self.lane.project(np.asarray(p, float))
        if s >= self.lane.mouth[0]: half = self.mouth_half - 0.2
        elif self.lane.yard[0] <= s <= self.lane.yard[1]: half = 6.0
        else: half = self.lane.width / 2 + 0.1
        return float(min(half - abs(lat), self.road_dist(p) - (self.boundary + self.FENCE_IN)))

    def hedge_dist(self, p):
        H = self.hedge; return float(seg_dist(np.asarray(p, float)[None], H[:, :2], H[:, 2:]).min())

    def hedges_near(self, p, r=16.0):
        H = self.hedge; m = 0.5 * (H[:, :2] + H[:, 2:]); return H[np.linalg.norm(m - np.asarray(p)[None], axis=1) < r]

    def pose(self, s, lat=0.0, rel_yaw=0.0):
        p = self.lane.point(s, lat); return float(p[0]), float(p[1]), wrap(self.lane.heading(s) + rel_yaw)


class ExtWorld(World):
    def __init__(self, site, home_xy, home_yaw, night=False):
        super().__init__(site.lane, site.ter, home_xy, home_yaw)
        self.site = site; self.night = night
        self.bin_mass = M_BIN_EMPTY; self.others = []
        self.nudge = 0; self.nudge_rot = 0.0; self.wedged = False; self.contact_bin = False; self.fence_breach = False
        # ---- Rev G3 (ported from revG_alt): hard-wired stop chain, E-stop, crossbeam contact, pack, faults, weather ----
        self.chain_ok = True; self.estop = False; self.chain_trips = []; self.chain_reason = None
        self.crossbeam = False; self.crossbeam_events = []; self.push_m = 0.0; self._hit_lat = 0.0
        self.air_c = 8.0; self.wind_gust = 5.0
        self.soc = self.soc0 = 0.90; self.pack_v = 26.4; self.pack_a = 0.0; self.pack_wh_out = 0.0
        self.contact_fault = 0; self.charge_fault = False; self.contact_tries = 0; self._was_seat = False
        self.dock_v = False; self.charge_a = 0.0
        self.pawl_stuck = 0; self.rel_tries = 0; self._rel_try = False
        self.lamp_work = False; self.lamp_dim = False
        self.legal_min = 1e9; self.legal_min_xy = None; self.rev_v_max = 0.0
        # ---- Rev G4: moving vehicles (driver model in g4_features.Car), pack temperature + dock pack heater, hedge-overlap metric ----
        self.ko_max = -99.0; self.ko_xy = None
        self.vehicles = []; self.pack_c = None; self.pack_heater = False; self.heater_w = 0.0; self.hedge_overlap = 0.0; self.hedge_overlap_xy = None
        self.hedge_clear_min = 9.0; self.hedge_clear_at = None; self.fence_clear_min = 9.0     # Rev G6 evaluation (truth)

    def update_vehicles(self, dt):
        for vh in self.vehicles: vh.update(self, dt)

    def pack_temp_step(self, dt):
        """Rev G4 (ASSUMED thermal model): 12 Ah 8S LFP pack in an insulated box, heat capacity 3300 J/K, loss 0.6 W/K to air.
        Optional 15 W pad heater powered by the dock supply (only while docked with dock voltage) holds it >= +5 C so the
        temperature-gated charger (>= +3 C) can charge. Off the dock the pack cools toward the air temperature."""
        if self.pack_c is None: self.pack_c = self.air_c
        q = -0.6 * (self.pack_c - self.air_c)
        self.heater_w = 15.0 if (self.pack_heater and self.dock_v and self.pack_c < 5.0) else 0.0
        self.pack_c += (q + self.heater_w) * dt / (3300.0 * PACK_WH_NOM / 307.2)     # G6: heat capacity scales with the pack

    def static_boxes(self, include_bin=True, for_collision=False):
        out = super().static_boxes(include_bin, for_collision)
        for o in self.others:
            out.append(dict(kind='bin2', x=o['x'], y=o['y'], yaw=o['yaw'], L=BIN['d'], W=BIN['w'], H=BIN['h']))
        for vh in self.vehicles:            # Rev G4: moving vehicles are boxes for the lidar and the bump strips
            if vh.on: out.append(vh.box())
        return out

    def step(self, dt, pwm):
        if self.vehicles: self.update_vehicles(dt)
        self.pack_temp_step(dt)
        thl = np.clip((pwm[0] - 1500) / 500.0, -1, 1); thr = np.clip((pwm[2] - 1500) / 500.0, -1, 1)
        if abs(thl) < 0.02: thl = 0
        if abs(thr) < 0.02: thr = 0
        if not self.chain_ok: thl = thr = 0.0          # Rev G3: hard-wired chain open -> motor-driver enable cut, spring brakes
        if self.pack_v < 22.0: thl = thr = 0.0          # BMS under-voltage cut-off
        grade = self.grade_here()
        load = 1.0 + 1.1 * self.bin_mass / M_TUG if self.attached else 1.0
        droop = 0.9 * grade * load; roll_res = 0.03 * load
        def tgt(th):
            if th == 0: return 0.0
            v = th * VMAX - droop
            return v - math.copysign(roll_res, th) if abs(v) > roll_res else 0.0
        tau = 0.35 * load
        self.vl += (tgt(thl) - self.vl) * min(1, dt / tau); self.vr += (tgt(thr) - self.vr) * min(1, dt / tau)
        v = 0.5 * (self.vl + self.vr); w = (self.vr - self.vl) / (TUG['track'] * 1.25)
        nx = self.x + v * math.cos(self.yaw) * dt; ny = self.y + v * math.sin(self.yaw) * dt; nyaw = wrap(self.yaw + w * dt)
        hit = self.collides(nx, ny, nyaw, v)
        self.contact_bin = False
        if hit:
            if v < 0 and abs(self._hit_lat) <= CROSSBEAM_HALF:
                # Rev G3 (F7): centre gap. Only the crossbeam is there (its contact switch is read by the Pi, it is NOT in the
                # hard-wired loop because the bin's wheels press it at every docking). A person is compliant: the tug keeps
                # pushing until the software stops it (push distance logged); rigid objects stop it.
                if not self.crossbeam_events or self.t - self.crossbeam_events[-1]['t'] > 1.0:
                    self.crossbeam_events.append(dict(t=round(self.t, 2), kind=hit, v=round(v, 3), lat=round(self._hit_lat, 3)))
                if hit == 'mover' and self.push_m < 0.3:
                    self.push_m += abs(v) * dt; hit = False
            elif not (self.nudge and v > 0 and hit == 'bin'):
                self.chain_trip('%s bump strip (%s)' % ('rear corner' if v < 0 else 'front', hit))
        if hit and self.nudge and v > 0 and hit == 'bin' and self.bin['state'] == 'up' and not self.attached:
            self.contact_bin = True
            if self._push_bin(v * dt):
                self.x, self.y, self.yaw = nx, ny, nyaw; self.bumper = True
            else:
                v = 0.0; self.vl = self.vr = 0.0; w = 0.0; self.bumper = True
        elif hit:
            v = 0.0; self.vl = self.vr = 0.0; w = 0.0; self.bumper = True
        else:
            self.bumper = False; self.x, self.y, self.yaw = nx, ny, nyaw
        self._fc = getattr(self, '_fc', 0) + 1
        if self._fc % 10 == 0 and not self.site.in_fence((self.x, self.y), margin=-0.6, ko=False):
            self.fence_breach = True
        if self._fc % 10 == 0 and getattr(self.site, 'boundary', None) is not None and self.site.variant == 'real':
            self._legal_check()
        if self._fc % 10 == 0: self._hedge_check()
        if self._fc % 10 == 0 and self.site.variant == 'real':      # Rev G6 evaluation: axle margin to the tug geofence (truth)
            fm = self.site.fence_margin((self.x, self.y))
            if fm < self.fence_clear_min: self.fence_clear_min = fm
        if self._fc % 10 == 0 and self.site.keepouts:      # Rev G4 evaluation: deepest footprint point inside a keep-out
            dk = max(self.site.keepout_depth(p) for p in self.footprint())
            if dk > self.ko_max: self.ko_max = dk; self.ko_xy = (round(self.x, 2), round(self.y, 2))
        if v < -0.005: self.rev_v_max = max(self.rev_v_max, -v)
        self.crossbeam = self._rear_contact()
        self.odo += abs(v) * dt
        if self.attached:
            b = self.bin; L = BIN['L']
            phi = wrap(self.yaw - b['yaw'])
            b['yaw'] = wrap(b['yaw'] + v / L * math.sin(phi) * dt)
            phi = wrap(self.yaw - b['yaw'])
            if abs(phi) > HITCH_CAP:
                b['yaw'] = wrap(self.yaw - math.copysign(HITCH_CAP, phi)); self.hitch_limit_hits += 1; phi = math.copysign(HITCH_CAP, phi)
            self.hitch = math.degrees(phi); self.hitch_max = max(self.hitch_max, abs(self.hitch))
            b['x'] = self.x - L * math.cos(b['yaw']); b['y'] = self.y - L * math.sin(b['yaw'])
        if not self.attached and v < 0 and self.bin is not None and self.bin['state'] == 'up' and self.seat_zone():
            self._funnel(abs(v) * dt)
        if not self.attached and v < 0 and self.seat and self.bin is not None:
            # Rev G sim fix: once seated, the wheel-stop crossbeam bears on the bin's wheels, so any further reverse travel
            # (the tug coasting to a stop) pushes the bin along instead of driving through it and losing the seat.
            self.bin['x'] += v * math.cos(self.yaw) * dt; self.bin['y'] += v * math.sin(self.yaw) * dt
        tgt_tilt = BIN['tilt_deg'] if pwm[4] > 1700 else 0.0
        self.hook_tilt += np.clip(tgt_tilt - self.hook_tilt, -12 * dt, 12 * dt)
        self.seat = self._seat_check()
        self.dock_seat = self._dock_check()
        if self.seat and self.hook_tilt > BIN['tilt_deg'] - 2 and not self.attached: self.attached = True
        if self.attached and self.hook_tilt < 2 and pwm[4] < 1300 and not self._rel_try:
            # Rev G3 (F2): the release cam lifts the gravity pawls when the mast is fully down. pawl_stuck = number of tries
            # that fail (mud / ice / bent cam; 99 = jammed until the manual lever is used).
            self._rel_try = True; self.rel_tries += 1
            if self.rel_tries > self.pawl_stuck: self.release()
        if self.hook_tilt > 5: self._rel_try = False
        self._dock_power()
        acc = (v - self.prev_v) / dt; self.prev_v = v
        self.v, self.w = v, w; self.t += dt
        return acc

    # ---------------- Rev G3 additions ----------------
    def chain_trip(self, reason):
        if self.chain_ok:
            self.chain_ok = False; self.chain_reason = reason
            self.chain_trips.append(dict(t=round(self.t, 2), reason=reason, v=round(self.v, 3), x=round(self.x, 3), y=round(self.y, 3)))

    def press_estop(self): self.estop = True; self.chain_trip('E-stop pressed')

    def chain_reset(self):
        """Reset request from the Pi to the safety relay; refused while the E-stop is latched (manual twist-reset only)."""
        if self.estop or self.chain_ok: return False
        self.chain_ok = True; self.chain_reason = None; return True

    def _rear_contact(self):
        """Crossbeam contact switch (centre gap |y| <= 0.33 m at the rear frame): a seated bin, or anything else touching it."""
        if self.seat and not self.attached: return True
        c, s_ = math.cos(self.yaw), math.sin(self.yaw); ex = -0.46
        pts = [(self.x + c * ex - s_ * dy, self.y + s_ * ex + c * dy) for dy in np.linspace(-CROSSBEAM_HALF, CROSSBEAM_HALF, 5)]
        for m in self.movers:
            mx, my = m['pos'](self.t)
            if any(math.hypot(p[0] - mx, p[1] - my) < m['r'] + 0.01 for p in pts): return True
        return False

    def footprint(self):
        c, s_ = math.cos(self.yaw), math.sin(self.yaw); hw = TUG['half_w']
        pts = [(self.x + c * fx - s_ * fy, self.y + s_ * fx + c * fy) for fx in (TUG['front'], -TUG['rear']) for fy in (-hw, hw)]
        if self.attached and self.bin is not None:
            b = self.bin; cb, sb = math.cos(b['yaw']), math.sin(b['yaw'])
            pts += [(b['x'] + cb * fx - sb * fy, b['y'] + sb * fx + cb * fy) for fx in (-BIN['d'] / 2, BIN['d'] / 2) for fy in (-BIN['w'] / 2, BIN['w'] / 2)]
        return pts

    def _legal_check(self):
        """Evaluation: closest approach of the tug footprint (and a towed bin) to the assumed private boundary."""
        d = min(self.site.boundary_dist(p) for p in self.footprint())
        if d < self.legal_min: self.legal_min = d; self.legal_min_xy = (round(self.x, 2), round(self.y, 2))

    def _hedge_check(self):
        """Rev G4 evaluation: how far the tug footprint (and a towed bin) reaches past a modelled lane hedge line (the hedges are
        lidar-only in this world - there is no collision with them - so an overlap would be a real hedge strike)."""
        S = self.site; hl = S.lane.width / 2 + 0.25
        for p in self.footprint():
            s, lat = S.lane.project(np.asarray(p, float))
            if s < S.lane.mouth[0] and not (S.lane.yard[0] <= s <= S.lane.yard[1]) and s > 0:
                o = abs(lat) - hl
                if o > self.hedge_overlap: self.hedge_overlap = o; self.hedge_overlap_xy = (round(float(p[0]), 2), round(float(p[1]), 2), round(float(S.L - s), 2))
                if S.variant == 'real':       # Rev G6: clearance to the TRUTH hedge face (irregular, overgrown), skipped in gaps
                    side = 1 if lat >= 0 else -1
                    if not G6.in_gap(s, side):
                        c = (hl - G6.hedge_offset(s, side)) - abs(lat)
                        if c < self.hedge_clear_min: self.hedge_clear_min = c; self.hedge_clear_at = (round(float(s), 1), side)

    def _dock_power(self):
        """Dock voltage on the crossbeam contacts and charge current (29.2 V CC/CV charger, 5 A). Faults for tests:
        contact_fault = n seatings with no dock voltage (leaves/corrosion; 99 = always); charge_fault = voltage but no current
        (charger tripped / high-resistance contact). Charging is inhibited below +3 C pack temperature (temp-gated charger,
        HANDOVER s.6.1 step 8); the dock still powers the bus."""
        ds = getattr(self, 'dock_seat', None) or {}
        seat = bool(ds.get('seat'))
        if seat and not self._was_seat: self.contact_tries += 1
        self._was_seat = seat
        self.dock_v = seat and self.contact_tries > self.contact_fault
        pc = self.air_c if self.pack_c is None else self.pack_c          # Rev G4: gate on the pack temperature (= air without the heater)
        self.charge_a = (5.0 if self.soc < 0.995 else 0.3) if (self.dock_v and pc >= 3.0 and not self.charge_fault) else 0.0

    def pack_step(self, p_load, dt):
        """8S LiFePO4 12 Ah pack. Usable energy = 307 Wh x cold factor (0.88 at 0 C, assumed). On the dock with voltage the
        dock supply carries the bus; charge current flows into the pack only if not inhibited."""
        usable = PACK_WH_NOM * pack_cold_factor(self.air_c)
        p_pack = -(self.charge_a * 28.8) if self.dock_v else p_load
        if p_pack > 0: self.pack_wh_out += p_pack * dt / 3600.0
        self.soc = float(np.clip(self.soc - p_pack * dt / 3600.0 / usable, 0.0, 1.0))
        ocv = float(np.interp(self.soc, [0.0, 0.03, 0.10, 0.20, 0.50, 0.90, 1.0], [20.0, 24.0, 25.0, 25.6, 26.0, 26.4, 26.8]))
        self.pack_a = p_pack / max(ocv, 1.0); self.pack_v = ocv - 0.06 * self.pack_a

    def tilt_current(self):
        """Tilt-actuator holding current at 48 deg (24 V screw actuator): idle + load term + noise (revG_alt model)."""
        return 1.4 + 0.095 * (self.bin_mass if self.bin is not None else 0.0) + float(self.rng.normal(0, 0.25))

    def collides(self, x, y, yaw, v):
        if v == 0: return False
        c, s = math.cos(yaw), math.sin(yaw)
        ex = TUG['front'] if v > 0 else -0.45
        dys = np.linspace(-TUG['half_w'], TUG['half_w'], 9)
        pts = [(x + c * ex - s * dy, y + s * ex + c * dy) for dy in dys]
        hits = []
        for o in self.static_boxes(include_bin=not self.attached, for_collision=True):
            _, poly = box_segs(o['x'], o['y'], o['yaw'], o['L'], o['W'])
            for p, dy in zip(pts, dys):
                if _inside(p, poly): hits.append((o['kind'], dy))
        for m in self.movers:
            mx, my = m['pos'](self.t)
            for p, dy in zip(pts, dys):
                if math.hypot(p[0] - mx, p[1] - my) < m['r']: hits.append(('mover', dy))
        if not hits: return False
        k = [h for h in hits if abs(h[1]) > CROSSBEAM_HALF]        # any contact on a bump-strip zone wins (hard-wired)
        kind, dy = (k[0] if k else hits[0]); self._hit_lat = float(dy)
        return kind

    def _dock_check(self):
        """Rev G charging dock. The dock's V-guide rails take the rear frame's crossbeam (yaw lock OFF while docking, so the
        rear frame swings to line up): captured if, when the crossbeam reaches the dock stop, the crossbeam centre is within
        +/-0.15 m laterally and the tug is within +/-15 deg of the dock axis. Returns dict(seat, lat, along, dyaw) (truth)."""
        d = getattr(self, 'dock', None)
        if d is None: return None
        hx = self.x + TUG['hook_x'] * math.cos(self.yaw); hy = self.y + TUG['hook_x'] * math.sin(self.yaw)
        fx, fy = d['x'] + 0.30 * math.cos(d['yaw']), d['y'] + 0.30 * math.sin(d['yaw'])        # dock contact face centre
        c, s_ = math.cos(d['yaw']), math.sin(d['yaw']); rx, ry = hx - fx, hy - fy
        along = rx * c + ry * s_; lat = -rx * s_ + ry * c; dyaw = wrap(self.yaw - d['yaw'])
        seat = along < 0.02 and abs(lat) < 0.15 and abs(dyaw) < math.radians(15)
        return dict(seat=bool(seat), lat=lat, along=along, dyaw=dyaw)

    def _funnel(self, ds):
        """Rear docking funnel (flared arms 0.65 m apart): once the handle face is inside the funnel mouth
        (|lateral| < 0.2 m, |yaw| < 20 deg) the bin is guided onto the hook centre-line over ~0.25 m of reverse travel."""
        b = self.bin; c, s = math.cos(self.yaw), math.sin(self.yaw)
        hb = np.array([b['x'] + 0.30 * math.cos(b['yaw']), b['y'] + 0.30 * math.sin(b['yaw'])])
        rel = hb - np.array([self.x, self.y]); lat = -s * rel[0] + c * rel[1]; dyaw = wrap(self.yaw - b['yaw'])
        if abs(lat) > 0.2 or abs(dyaw) > math.radians(20): return
        f = min(1.0, ds / 0.25)
        b['yaw'] = wrap(b['yaw'] + f * dyaw)
        b['x'] += -f * lat * -s; b['y'] += -f * lat * c

    def _push_bin(self, ds):
        """Bumper orbit-nudge of the empty bin (MuJoCo-calibrated: ~0.55 m roll toward the handle per 90 deg,
        wedges if a hedge is within ~0.8 m). Returns False if the bin will not move (wedged)."""
        b = self.bin
        if self.site.hedge_dist((b['x'], b['y'])) < 0.8:
            self.wedged = True; return False
        dth = self.nudge * ds / 0.55
        hx, hy = math.cos(b['yaw']), math.sin(b['yaw'])
        roll = 0.55 * abs(dth) / (math.pi / 2)
        b['x'] += hx * roll; b['y'] += hy * roll; b['yaw'] = wrap(b['yaw'] + dth); self.nudge_rot += abs(dth)
        return True

    # ---- camera: day / night (IR illuminator + retro-reflective tags) ----
    def render_cam(self, night=None, seed=None, lamp=None):
        """Rev G3: per-bin tag sets (bin['id0']); optional rear white work lamp (lamp=None -> the companion's current state,
        dimmed lamp = off for the camera)."""
        night = self.night if night is None else night
        lamp = (self.lamp_work and not self.lamp_dim) if lamp is None else lamp
        W_, H_, F = self.CAM_W, self.CAM_H, self.CAM_F
        rng = self.rng if seed is None else np.random.default_rng(seed)
        pos, R = self.cam_pose()
        bins = []
        if self.bin is not None and not self.attached: bins.append((self.bin, self.bin.get('id0', 0)))
        for o in self.others: bins.append((o, o.get('id0', 10)))
        if getattr(self, 'dock', None) is not None: bins.append((self.dock, 20))      # Rev G charging dock (tag 20 on its backboard)
        alb = np.zeros((H_, W_), np.float32); alb[:] = 0.22; alb[: H_ // 6] = 0.55
        rows = (np.arange(H_) - H_ / 2) / F; ang = math.radians(30) + np.arctan(rows)
        gr = np.where(ang > 0.02, TUG['cam_z'] / np.sin(np.clip(ang, 0.02, None)), 30.0)
        rng_img = np.repeat(gr[:, None], W_, axis=1).astype(np.float32)
        retro = np.zeros((H_, W_), bool); vis = []
        def proj(P):
            q = R @ (np.asarray(P) - pos)
            if q[2] < 0.1: return None
            return (F * q[0] / q[2] + W_ / 2, F * q[1] / q[2] + H_ / 2, q[2])
        for b, id0 in sorted(bins, key=lambda bb: -np.linalg.norm(np.array([bb[0]['x'], bb[0]['y']]) - pos[:2])):
            saved = self.bin; self.bin = b
            faces, body = self.bin_faces(); self.bin = saved
            bp = [proj(p) for p in body]
            if all(p is not None for p in bp):
                hull = cv2.convexHull(np.array([[p[0], p[1]] for p in bp], np.float32)).astype(np.int32)
                m = np.zeros((H_, W_), np.uint8); cv2.fillConvexPoly(m, hull, 1)
                alb[m > 0] = 0.12; rng_img[m > 0] = np.mean([p[2] for p in bp])
            for fid, corners in faces.items():
                if id0 == 20 and fid != 0: continue          # dock carries one tag only (facing the tug)
                pc = [proj(p) for p in corners]
                if any(p is None for p in pc): continue
                n = np.cross(corners[1] - corners[0], corners[3] - corners[0])
                if n @ (pos - corners[0]) <= 0: continue
                dst = np.array([[p[0], p[1]] for p in pc], np.float32)
                if dst[:, 0].max() < 0 or dst[:, 0].min() > W_ or dst[:, 1].max() < 0 or dst[:, 1].min() > H_: continue
                mk = MARKS[fid + id0].astype(np.float32) / 255.0
                pad = cv2.copyMakeBorder(mk, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=1.0)
                src = np.array([[159, 0], [0, 0], [0, 159], [159, 159]], np.float32)
                Hm = cv2.getPerspectiveTransform(src, dst + (dst - dst.mean(0)) * (1 / 3))
                wa = cv2.warpPerspective(pad, Hm, (W_, H_), flags=cv2.INTER_LINEAR, borderValue=0)
                msk = cv2.warpPerspective(np.ones((160, 160), np.float32), Hm, (W_, H_)) > 0.5
                alb[msk] = 0.05 + 0.85 * wa[msk]; retro |= msk; rng_img[msk] = np.mean([p[2] for p in pc]); vis.append(fid + id0)
        if not night:
            img = alb * 235.0 + 15.0 + rng.normal(0, 4, alb.shape)
        else:
            # moonless night: ambient ~0.5 % of day; 850 nm IR LED illuminator beside the camera (cos^6 beam, 1/r^2);
            # retro-reflective tag sheeting returns ~6x the diffuse level toward the co-located source;
            # auto-exposure / gain capped at x10, sensor noise grows with gain; slight blur (longer exposure).
            xs = (np.arange(W_) - W_ / 2) / F; ys = (np.arange(H_) - H_ / 2) / F
            off = np.sqrt(xs[None] ** 2 + ys[:, None] ** 2); beam = np.cos(np.arctan(off)) ** 6
            E = 230.0 * beam / np.maximum(rng_img, 0.5) ** 2
            gain = np.where(retro, 6.0, 1.0)
            raw = alb * (1.2 + E * gain)
            if lamp:
                # Rev G3 (ported from revG_alt): 3 W white rear work lamp, wide beam (cos^2), 0.15 m from the lens, so the
                # retro-reflective gain only applies at long range (observation angle 0.15/r rad; x6 below ~0.3 deg -> x1 beyond 2 deg).
                beam_w = np.cos(np.arctan(off)) ** 2
                obs = np.degrees(LAMP_OFFSET / np.maximum(rng_img, 0.3))
                g_w = np.where(retro, 1.0 + 5.0 * np.exp(-(obs / 1.0) ** 2), 1.0)
                raw = raw + alb * (WORK_LAMP_GAIN * beam_w / np.maximum(rng_img, 0.5) ** 2) * g_w
            g_ae = float(np.clip(200.0 / max(np.percentile(raw, 99.7), 1e-3), 1.0, 10.0))
            img = raw * g_ae + rng.normal(0, 3.0 * g_ae, raw.shape)
            img = cv2.GaussianBlur(img.astype(np.float32), (0, 0), 0.7)
        img = np.clip(img, 0, 255).astype(np.uint8)
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR), vis


CAM_K = np.array([[230.0, 0, 160], [0, 230.0, 120], [0, 0, 1]])
OBJ = np.array([[-MARK_SIDE / 2, MARK_SIDE / 2, 0], [MARK_SIDE / 2, MARK_SIDE / 2, 0], [MARK_SIDE / 2, -MARK_SIDE / 2, 0], [-MARK_SIDE / 2, -MARK_SIDE / 2, 0]], np.float32)


def detect(img):
    """Real OpenCV ArUco detection + PnP. Returns list of (id, range_m, bearing_rad_in_cam, tvec, rvec)."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = DET.detectMarkers(g)
    out = []
    if ids is None: return out
    for c, i in zip(corners, ids.ravel()):
        ok, rvec, tvec = cv2.solvePnP(OBJ, c.reshape(4, 2).astype(np.float32), CAM_K, None, flags=cv2.SOLVEPNP_IPPE_SQUARE)
        if not ok: continue
        t = tvec.ravel(); out.append((int(i), float(np.linalg.norm(t)), float(math.atan2(t[0], t[2])), t, rvec.ravel()))
    return out


def tag_to_world(det, tug_x, tug_y, tug_yaw, z_tug):
    """Camera-frame tag pose -> world xyz of the tag centre, the face's outward normal yaw, |normal z|."""
    i, r, brg, t, rv = det
    c, s = math.cos(tug_yaw), math.sin(tug_yaw)
    pos = np.array([tug_x + TUG['cam_x'] * c, tug_y + TUG['cam_x'] * s, z_tug + TUG['cam_z']])
    look = tug_yaw + math.pi; pitch = math.radians(-30)
    fwd = np.array([math.cos(look) * math.cos(pitch), math.sin(look) * math.cos(pitch), math.sin(pitch)])
    right = np.array([math.sin(look), -math.cos(look), 0.0]); up = np.cross(right, fwd)
    Rcw = np.array([right, -up, fwd])
    pw = pos + Rcw.T @ t
    Rm, _ = cv2.Rodrigues(rv); nz = Rcw.T @ (Rm @ np.array([0, 0, 1.0]))   # OpenCV tag z: out of the tag toward the viewer
    nyaw = math.atan2(nz[1], nz[0])
    return pw, nyaw, abs(nz[2])


# ---------------- energy model ----------------
G = 9.81
def power_w(v, w, grade, attached, bin_mass, moving, night_dock, hook_moving, lights_w=None):
    """Electrical power from the 24 V pack. Driving: wheel power / 0.62 (motor+gearbox+driver), no regen (spring brakes).
    grade is along the direction of motion. Rolling: tug Crr 0.035; bin 65 % on its own wheels (Crr 0.05), 35 % on the tug.
    Skid-steer scrub: mu_lat 0.5 on a quarter track. Electronics 9 W, beacon 2 W moving, IR 5 W while docking at night,
    hook actuator 70 W while stroking."""
    m = M_TUG + (bin_mass if attached else 0.0)
    F = m * G * grade / math.sqrt(1 + grade ** 2) + M_TUG * G * 0.035 + ((0.65 * 0.05 + 0.35 * 0.035) * bin_mass * G if attached else 0)
    Pw = F * abs(v) if abs(v) > 0.01 else 0.0
    Pturn = 0.5 * M_TUG * G * abs(w) * TUG['track'] / 4 if abs(w) > 0.02 else 0.0
    Pd = max(0.0, Pw + Pturn) / 0.62
    if lights_w is not None:        # Rev G: companion reports the actual lighting load (beacon, head, tail, IR, work light)
        return Pd + 9.0 + lights_w + (70.0 if hook_moving else 0.0)
    return Pd + 9.0 + (2.0 if moving else 0.0) + (5.0 if night_dock else 0.0) + (70.0 if hook_moving else 0.0)
