"""Rev G6 feature modules for the bin-tug SITL (scripts_g6).
 - World side (truth): tree-canopy RTK multipath model (RtkMultipath), hedge gaps / gateways / overgrown narrowings
   (HEDGE_GAPS, HEDGE_BULGES, hedge_offset), wheel odometry with a scale error.
 - Pi side (companion): CorridorFit (2D-lidar hedge / verge line fit in the tug frame, no map, no pose),
   LaneFusion (corridor-primary lateral, RTK + odometry along-lane, dead-reckoning blend in gaps), hitch governor.
Everything here is SIMULATION / stand-in logic. Numbers marked ASSUMED are not measured on Brian's lane.
"""
import math, os, numpy as np
from world import TUG, BIN, wrap, HITCH_CAP_DEG
def M_TUG_KG(): return float(os.environ.get('BT_MASS', '95'))

# ------------------------------------------------------------------ truth: lane furniture (ASSUMED - no lane survey yet)
# Tree canopy over the lane (s ranges, m from the house end). RTK degrades only under canopy; the yard (s < 25) and the
# bell-mouth (s > L-12) are open sky.
CANOPY = [(45.0, 110.0), (180.0, 260.0), (300.0, 380.0), (470.0, 540.0), (575.0, 600.0)]
# Hedge gaps: (s0, s1, side) side +1 = left of house->road travel (+lat), -1 = right, 0 = both.
HEDGE_GAPS = [(60.0, 64.0, +1, 'field gate'), (140.0, 145.0, -1, 'gateway'), (230.0, 242.0, +1, 'open field (wire fence, lidar-transparent)'),
              (330.0, 334.5, 0, 'farm crossing (both sides)'), (455.0, 460.0, -1, 'neighbour driveway'), (560.0, 563.5, +1, 'field gate')]
# Overgrown narrowings: (s0, s1, side, inward m). The hedge face stands this much further into the lane than the survey line.
HEDGE_BULGES = [(395.0, 420.0, -1, 0.55, 'overgrown right hedge'), (500.0, 516.0, 0, 0.60, 'both hedges overgrown (2.9 m between faces)')]
W_NARROW = (3.2, 2.9)          # hedge-to-hedge (m): below 3.2 m no car can pass the tug anyway -> ramp from keep-left to centring
_HR = np.random.default_rng(2026)
_HK = [(_HR.uniform(0.02, 0.05), _HR.uniform(12, 60), _HR.uniform(0, 6.28)) for _ in range(4)]


def in_gap(s, side):
    for a, b, sd, _ in HEDGE_GAPS:
        if a <= s <= b and (sd == 0 or sd == side): return True
    return False


def hedge_offset(s, side):
    """Truth hedge-face offset INTO the lane (m) relative to the surveyed hedge line at station s on `side` (+1 left / -1 right):
    smooth irregularity (+/- ~0.12 m, fixed for the world) + overgrown narrowings (ramped over 3 m)."""
    o = sum(a * math.sin(2 * math.pi * s / lam + ph + (0.9 if side < 0 else 0.0)) for a, lam, ph in _HK)
    for a, b, sd, d, _ in HEDGE_BULGES:
        if sd == 0 or sd == side:
            o += d * float(np.clip(min(s - a, b - s) / 3.0, 0.0, 1.0))
    return o


def canopy_at(s):
    return any(a <= s <= b for a, b in CANOPY)


class RtkMultipath:
    """ASSUMED RTK behaviour under tree canopy (LC29H-class dual-band receiver, typical hedgerow/tree lane):
    - Fixed under canopy drops to Float at ~1/25 s; Float episodes last 4-30 s and start with a position JUMP of 0.5-1.5 m
      (random direction), the bias then wanders (random walk 0.05 m/sqrt(s)).
    - Total dropouts (no fix) at ~1/90 s under canopy, 2-8 s long, then Float.
    - Rare wrong fix: fix type 6 with a 0.3-0.5 m bias for 3-8 s (~1/400 s under canopy) - the nasty case.
    - Leaving the canopy: re-convergence 3-10 s in Float with a decaying bias, then Fixed.
    Scenario gps_zones / gps_hold (s7, wake) still override this."""
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed + 991); self.state = 'fixed'; self.bias = np.zeros(2); self.until = 0.0
        self.events = []; self.enabled = os.environ.get('BT_MULTIPATH', '1') != '0'

    def step(self, t, s, dt):
        """Returns (quality 'rtk'|'float'|'none'|'wrongfix', bias_xy)."""
        if not self.enabled: return 'rtk', np.zeros(2)
        r = self.rng; cano = canopy_at(s)
        def ev(k): self.events.append(dict(t=round(t, 1), s=round(s, 1), kind=k, bias=round(float(np.linalg.norm(self.bias)), 2)))
        if self.state == 'fixed':
            if cano:
                u = r.random()
                if u < dt / 25.0:
                    a = r.uniform(0, 2 * math.pi); m = r.uniform(0.5, 1.5); self.bias = m * np.array([math.cos(a), math.sin(a)])
                    self.state = 'float'; self.until = t + r.uniform(4, 30); ev('float_jump')
                elif u < dt / 25.0 + dt / 90.0:
                    self.state = 'none'; self.until = t + r.uniform(2, 8); ev('dropout')
                elif u < dt / 25.0 + dt / 90.0 + dt / 400.0:
                    a = r.uniform(0, 2 * math.pi); m = r.uniform(0.3, 0.5); self.bias = m * np.array([math.cos(a), math.sin(a)])
                    self.state = 'wrongfix'; self.until = t + r.uniform(3, 8); ev('wrong_fix')
        elif self.state == 'float':
            self.bias += r.normal(0, 0.05 * math.sqrt(dt), 2)
            if not cano and self.until > t + 10: self.until = t + r.uniform(3, 10)
            if not cano: self.bias *= math.exp(-dt / 4.0)
            if t >= self.until:
                if cano and r.random() < 0.3: self.until = t + r.uniform(4, 15)      # stays float a while longer
                else: self.state = 'fixed'; self.bias[:] = 0; ev('refix')
        elif self.state == 'none':
            if t >= self.until:
                a = r.uniform(0, 2 * math.pi); m = r.uniform(0.5, 1.5) if cano else r.uniform(0.2, 0.6)
                self.bias = m * np.array([math.cos(a), math.sin(a)]); self.state = 'float'; self.until = t + r.uniform(4, 20); ev('float_after_dropout')
        elif self.state == 'wrongfix':
            if t >= self.until: self.state = 'fixed'; self.bias[:] = 0; ev('wrongfix_end')
        q = {'fixed': 'rtk', 'float': 'float', 'none': 'none', 'wrongfix': 'wrongfix'}[self.state]
        return q, self.bias.copy()


# ------------------------------------------------------------------ Pi side: 2D-lidar corridor (hedge / verge) fit
HL_NOM = 3.6 / 2 + 0.25          # surveyed hedge line, m from the lane centre-line
CORR_Y = (0.45, 3.2)             # lateral band (m, tug frame) searched for a hedge face on each side
CORR_X = (-0.6, 6.5)             # along band (m ahead of the drive axle); the rear arc |bearing| > 115 deg is body-occluded


def _ransac_quad(x, y, rng, it=40, thr=0.07):
    n = len(x); best = None
    if n < 12: return None
    for _ in range(it):
        idx = rng.choice(n, 3, replace=False)
        try: c = np.polyfit(x[idx], y[idx], 2)
        except Exception: continue
        if abs(c[0]) > 0.08: continue                       # hedge curvature radius > ~6 m at this scale
        res = np.abs(np.polyval(c, x) - y); inl = res < thr; k = int(inl.sum())
        if best is None or k > best[0]: best = (k, inl)
    if best is None or best[0] < 12: return None
    inl = best[1]
    if np.ptp(x[inl]) < 2.5: return None                  # must span >= 2.5 m along (a car door / a bin is not a hedge)
    c = np.polyfit(x[inl], y[inl], 2 if np.ptp(x[inl]) > 4 else 1)
    if len(c) == 2: c = np.r_[0.0, c]
    return c, inl


class CorridorFit:
    """Fits the hedge faces in the TUG frame from one 2D-lidar scan (pose-free, no map), per side in two windows:
    near (x -0.6..3.5 m from the drive axle: localisation) and far (x 2.5..7.0 m: what is coming - narrowings, bulges).
    Per side and window: dist (m, perpendicular from the axle line at x=0 for near / at x=4 m for far), rel_yaw (wall tangent vs
    tug heading), n inliers, span, poly. A face is 'hedge-like' if it is long (>= 2.5 m), roughly parallel (< 25 deg) and beside
    the tug (0.55-3.2 m): only those are used, everything else stays an obstacle candidate."""
    WIN = dict(near=(-0.6, 3.5, 0.0), far=(2.5, 7.0, 4.0))

    def __init__(self, seed=0): self.rng = np.random.default_rng(seed + 5)

    def fit(self, r):
        self.last_ahead = {}
        if r is None: return {}
        ang = np.radians(np.arange(len(r))); ok = np.isfinite(r)
        x = TUG['lidar_x'] + r[ok] * np.cos(ang[ok]); y = r[ok] * np.sin(ang[ok])
        out = {}
        for side in (+1, -1):     # G6 v3 look-ahead: nearest face intrusion 2-6.5 m ahead (10th percentile), no straight-line fit needed
            m = (x > 2.0) & (x < 7.5) & (side * y > 0.45) & (side * y < 4.2)          # (bulge ramps are not lines; wide band: a bend shifts both sides, a narrowing closes both)
            if m.sum() >= 8: self.last_ahead[side] = float(np.percentile(side * y[m], 10))
        for side in (+1, -1):
            for win, (x0, x1, xe) in self.WIN.items():
                m = (x > x0) & (x < x1) & (side * y > CORR_Y[0]) & (side * y < CORR_Y[1])
                res = _ransac_quad(x[m], y[m], self.rng)
                if res is None: continue
                c, inl = res; b = float(np.polyval(np.polyder(c), xe)); a = float(np.polyval(c, xe))
                d = abs(a) / math.sqrt(1 + b * b); ry = -math.atan(b)
                if abs(ry) > math.radians(25) or not (0.55 < d < 3.2): continue
                out.setdefault(side, {})[win] = dict(dist=d, rel_yaw=ry, n=int(inl.sum()), poly=c, span=float(np.ptp(x[m][inl])), xe=xe)
        return out

    @staticmethod
    def on_wall(px, py, walls, tol=0.2):
        """Mask of tug-frame points lying on a fitted hedge-like face (dropped from the obstacle check: bends, bulges)."""
        mask = np.zeros(len(px), bool)
        for side, ws in walls.items():
            for win, wv in ws.items():
                x0, x1, _ = CorridorFit.WIN[win]
                mask |= (np.abs(np.polyval(wv['poly'], px) - py) < tol) & (px > x0 - 0.3) & (px < x1 + 0.5) & (side * py > 0.3)
        return mask



# ------------------------------------------------------------------ G6 session 3: lane-frame face clearance (narrowing clamp)
FACE_CLR = TUG['half_w'] + 0.50     # axle-to-face lateral clearance the clamp keeps (body 0.38 + 0.35 obstacle band + 0.15 margin)
FACE_ZONE = 1.10                     # only returns with |lat| > this are hedge-face candidates (pad bins / people mid-lane excluded)


def scan_lane(lane, p, yaw, r):
    """Raw lidar scan -> lane frame (s, lat) of every return, using the pose (p, yaw). Vectorised over the nearby survey segments."""
    if r is None or p is None or yaw is None: return None
    ok = np.isfinite(r)
    if not ok.any(): return None
    ox = p[0] + TUG['lidar_x'] * math.cos(yaw); oy = p[1] + TUG['lidar_x'] * math.sin(yaw)
    ang = yaw + np.radians(np.arange(len(r)))[ok]; rr = r[ok]
    P = np.c_[ox + rr * np.cos(ang), oy + rr * np.sin(ang)]
    s0, lat0 = lane.project(np.asarray(p, float))
    i0 = max(0, int(np.searchsorted(lane.s, s0 - 14.0)) - 1); i1 = min(len(lane.P) - 1, int(np.searchsorted(lane.s, s0 + 14.0)) + 1)
    A = lane.P[i0:i1]; B = lane.P[i0 + 1:i1 + 1]
    if len(A) == 0: return None
    AB = B - A; L2 = np.maximum((AB * AB).sum(1), 1e-9)
    D = P[:, None, :] - A[None, :, :]
    t = np.clip((D * AB[None]).sum(2) / L2[None], 0, 1)
    Q = A[None] + t[..., None] * AB[None]; dd = np.linalg.norm(P[:, None, :] - Q, axis=2)
    k = np.argmin(dd, axis=1); n = np.arange(len(P))
    cr = AB[k, 0] * D[n, k, 1] - AB[k, 1] * D[n, k, 0]
    ss = lane.s[i0 + k] + t[n, k] * np.sqrt(L2[k]); ll = np.sign(cr) * dd[n, k]
    return ss, ll, float(s0), float(lat0), P


def lane_faces(lane, p, yaw, r, sgn, look=(-0.5, 8.0)):
    """Nearest hedge face on each lane side (lane frame lateral, in the frame of the pose estimate p) from the RAW lidar scan,
    over the stretch the tug is about to occupy (look m along the travel direction sgn). Bends are removed by projecting onto
    the surveyed centre-line, so a bend no longer looks like a narrowing. Returns ({+1: lat_left_face, -1: lat_right_face}, s, lat)."""
    q_ = scan_lane(lane, p, yaw, r)
    if q_ is None: return None
    ss, ll, s0, lat0, _ = q_
    m = (sgn * (ss - s0) > look[0]) & (sgn * (ss - s0) < look[1]) & (np.abs(ll) > FACE_ZONE) & (np.abs(ll) < 3.2)
    out = {}
    for side in (+1, -1):
        q = m & (side * ll > 0) & (side * (ll - lat0) > TUG['half_w'])
        if q.sum() >= 3: out[side] = float(side * np.percentile(side * ll[q], 5))
    return out, float(s0), float(lat0)

# ------------------------------------------------------------------ Pi side: lane fusion -> position forwarded to the autopilot
class LaneFusion:
    """Corridor-primary lateral, RTK + wheel-odometry along-lane (Rev G6, third-party review item 'lidar-primary lateral').
    State: position p (x, y) in the lane map frame + 1-sigma along / lateral uncertainty. Heading from the autopilot attitude.
      predict : wheel odometry (scale error ~1 %, ASSUMED) along the IMU/compass heading
      RTK     : Fixed -> full update along-lane; laterally weak if the corridor is valid. Float -> 2 % gain with a 0.8 m gate
                (the 0.5-1.5 m jumps are rejected). No fix -> nothing. A persistent Fixed innovation > 0.35 m is accepted after 2 s.
      corridor: lateral update (gain 0.35, gate 0.5 m + 4 % of the distance since the last corridor update) from the hedge-face
                fit; rejected per side if the face is > 0.4 m off its expected place (parked car, bin, person against the hedge).
    The forwarded position is rate-limited (<= 0.2 m/s of correction) so the autopilot EKF sees no glitches."""
    KL_TARGET_D = None

    def __init__(self, site):
        self.S = site; self.p = None; self.sig_s = 9.0; self.sig_l = 9.0; self.last_corr_odo = -1e9; self.odo = 0.0
        self.fixed_odo = 0.0; self.out = None; self.walls = {}; self.corr_valid = False; self.corr_lat = None
        self.narrow = False; self.width_meas = None; self._pending = None; self.stats = dict(corr_upd=0, corr_rej=0, rtk_fix_upd=0, float_rej=0, float_upd=0, wrongfix_hits=0)
        self.lat_offset = 0.0; self.lat_offset_tgt = 0.0; self.mode = 'rtk'; self.side_off = 0.0; self.side_seen = -1e9

    def lane_zone(self, s):
        return self.S.lane.yard[1] <= s <= self.S.lane.mouth[0] - 0.5

    def predict(self, v_odo, yaw, dt):
        if self.p is None or yaw is None: return
        mv = v_odo * dt * np.array([math.cos(yaw), math.sin(yaw)]); self.p = self.p + mv; d = abs(v_odo * dt); self.odo += d
        if self.out is not None: self.out = self.out + mv
        self.sig_s = min(9.0, self.sig_s + 0.015 * d); self.sig_l = min(9.0, self.sig_l + 0.03 * d)

    def rtk(self, fix, xy, t):
        xy = np.asarray(xy, float)
        if self.p is None:
            if fix == 6: self.p = xy.copy(); self.sig_s = self.sig_l = 0.03
            return
        s, _ = self.S.lane.project(self.p); h = self.S.lane.heading(s); u = np.array([math.cos(h), math.sin(h)]); n = np.array([-u[1], u[0]])
        e = xy - self.p; ea = e @ u; el = e @ n; corr = self.corr_valid and self.lane_zone(s)
        if fix == 6:
            if math.hypot(ea, el if not corr else 0.0) > 0.35:
                if self._pending is None: self._pending = t
                if t - self._pending < 2.0: self.stats['wrongfix_hits'] += 1; return
            else: self._pending = None
            ka = 0.3; kl = 0.03 if corr else 0.3
            self.p = self.p + ka * ea * u + kl * el * n; self.sig_s = min(self.sig_s, 0.05)
            if not corr: self.sig_l = min(self.sig_l, 0.05)
            self.fixed_odo = self.odo; self.stats['rtk_fix_upd'] += 1
        elif fix == 5:
            if abs(ea) < 0.8: self.p = self.p + 0.02 * ea * u; self.sig_s = min(self.sig_s, 1.5); self.stats['float_upd'] += 1
            else: self.stats['float_rej'] += 1
            if not corr:
                if abs(el) < 0.8: self.p = self.p + 0.02 * el * n; self.sig_l = min(self.sig_l, 1.5)

    def corridor(self, walls, yaw, kl_target, ahead=None, faces=None):
        """walls from CorridorFit (tug frame). kl_target: (travel-left lane side, keep-left lateral) or None.
        Localisation uses the NEAR faces that sit within 0.4 m of where the surveyed hedge line should be. Each side's face is
        referenced to the keep-left side through a learned side-to-side offset (hedges are not exactly where the survey says), so
        losing one side in a gateway does not step the estimate. Narrowings (incl. what the FAR window sees ahead) switch the
        reference to the measured corridor centre (W_NARROW)."""
        self.walls = walls; self.corr_valid = False; self.narrow = False; self.width_meas = None
        if self.p is None or yaw is None: self.lat_offset = 0.0; return None
        s, lat = self.S.lane.project(self.p)
        if not self.lane_zone(s) or kl_target is None:          # G6 fix: decay (<= 0.2 m/s), never step, when leaving the lane zone
            self.lat_offset_tgt = 0.0; self.c_lat_f = None
            r_ = 0.02 if not self.lane_zone(s) else 0.005     # keep-left paused (hold, guard, leg end): ease off slowly
            self.lat_offset += float(np.clip(-self.lat_offset, -r_, r_))
            if not self.lane_zone(s): return None
        h = self.S.lane.heading(s); dpsi = wrap(yaw - h); fwd = math.cos(dpsi) >= 0
        est = {}; loose = {}
        for side, ws in walls.items():          # side in the TUG frame (+1 = tug left); lane side flips when driving up-lane
            lane_side = side if fwd else -side
            for win, wv in ws.items(): loose.setdefault(lane_side, {})[win] = wv['dist']
            wv = ws.get('near')
            if wv is None: continue
            exp_d = (HL_NOM - lane_side * lat)
            if abs(wv['dist'] - exp_d) > 0.4 + max(0.0, self.sig_l - 0.1): self.stats['corr_rej'] += 1; continue
            est[lane_side] = lane_side * (HL_NOM - wv['dist'])        # lateral of the axle in the lane frame from that face
        # ---- narrowing (near or ahead): hedge-to-hedge width from the loose faces (survey line where a side is not seen)
        def dside(ls, win):
            v = loose.get(ls, {}).get(win)
            return v if v is not None else (HL_NOM - ls * lat)
        for side, d_ in (ahead or {}).items():
            loose.setdefault(side if fwd else -side, {})['ahead'] = d_
        wn = dside(1, 'near') + dside(-1, 'near'); wf = dside(1, 'far') + dside(-1, 'far'); wa = dside(1, 'ahead') + dside(-1, 'ahead')
        self.width_meas = min(wn, wf, wa)
        # G6 session 3: CLEARANCE CLAMP in the lane frame (replaces the width ramp 3.2 -> 2.9 m, which started too late and only
        # half-centred: s2/s3/s1n/s10a/s20a/s22a stopped at the s=500-516 narrowing with the bulge 'ahead' as an obstacle).
        # The commanded lateral is the keep-left/planned line clipped to [right face + CLR, left face - CLR] (faces from the raw
        # scan projected on the surveyed centre-line, so bends cancel); infeasible -> the midpoint.
        if faces is not None and kl_target is not None:
            fl = faces.get(+1, HL_NOM); fr = faces.get(-1, -HL_NOM)
            self.width_meas = fl - fr          # lane-frame face-to-face width (bends removed)
            lo, hi = fr + FACE_CLR, fl - FACE_CLR
            T = kl_target[1] if lo <= hi else 0.5 * (lo + hi)
            if lo <= hi: T = float(np.clip(T, lo, hi))
            bind = abs(T - kl_target[1]) > 0.04
            if bind: self.nar_until = self.odo + 3.0
            if bind:
                self.T_f = T if getattr(self, 'T_f', None) is None else self.T_f + 0.25 * (T - self.T_f)
            elif self.odo < getattr(self, 'nar_until', -1.0) and getattr(self, 'T_f', None) is not None:
                self.T_f += 0.02 * (T - self.T_f)            # latched 3 m past the last binding reading: ease back slowly
            else: self.T_f = None
            if self.T_f is not None:
                self.lat_offset_tgt = kl_target[1] - self.T_f
                self.narrow = abs(self.lat_offset_tgt) > 0.15     # a real narrowing (not hedge irregularity): no corridor update from bulged faces
            else: self.lat_offset_tgt = 0.0
            # face-to-face width is independent of the estimate error: < 3.6 m (survey 4.1 m) = bulged faces in view -> no corridor
            # update from them (dev s2: an accepted one-sided update off a 0.6 m bulge moved the estimate ~0.5 m -> AUTO swerve)
            if fl - fr < 3.6: self.narrow = True
            rl = 0.04 if abs(self.lat_offset_tgt) >= abs(self.lat_offset) else 0.012     # in at <= 0.4 m/s, back out at <= 0.12 m/s
            self.lat_offset += float(np.clip(self.lat_offset_tgt - self.lat_offset, -rl, rl))  # (dev: solo AUTO overshot the re-merge, s=496 touch)
        else:
            f = float(np.clip((W_NARROW[0] - self.width_meas) / (W_NARROW[0] - W_NARROW[1]), 0.0, 1.0)) if kl_target is not None else 0.0
            if kl_target is None: f = -1.0
            if f > 0: self.nar_until = self.odo + 4.0
            elif f == 0 and self.odo < getattr(self, 'nar_until', -1.0) and getattr(self, 'c_lat_f', None) is not None:
                f = -2.0; self.narrow = True
            if f > 0:
                win = min((('near', wn), ('far', wf), ('ahead', wa)), key=lambda q: q[1])[0]
                c_lat = lat - 0.5 * (dside(-1, win) - dside(1, win))
                self.c_lat_f = c_lat if getattr(self, 'c_lat_f', None) is None else self.c_lat_f + 0.05 * (c_lat - self.c_lat_f)
                self.narrow = True; self.lat_offset_tgt = f * (kl_target[1] - self.c_lat_f)
            elif f == 0: self.lat_offset_tgt = 0.0; self.c_lat_f = None
            if f >= 0 or f == -2.0: self.lat_offset += float(np.clip(self.lat_offset_tgt - self.lat_offset, -0.04, 0.04))
        if not est: return None
        if self.narrow:          # G6 v3: inside a narrowing the faces are NOT where the survey says (bulges) -> no lateral update from
            self.stats['corr_narrow_skip'] = self.stats.get('corr_narrow_skip', 0) + 1     # them (and no side-offset learning);
            return None          # centring there is relative (c_off), so it does not need the absolute estimate
        if len(est) == 2:
            self.side_off += 0.1 * ((est[+1] - est[-1]) - self.side_off)    # learned (left-derived - right-derived), low-pass
            self.side_seen = self.odo
        elif self.odo - self.side_seen > 30.0: self.side_off *= 0.9
        ref = kl_target[0] if kl_target is not None else 0
        def from_side(k):
            if ref == 0: return est[k] - k * 0.5 * self.side_off
            return est[k] if k == ref else est[k] + ref * self.side_off
        lat_m = (from_side(+1) + from_side(-1)) / 2 if len(est) == 2 else from_side(list(est)[0])
        gate = 0.5 + 0.04 * max(0.0, self.odo - self.last_corr_odo)
        if abs(lat_m - lat) > min(gate, 1.5): self.stats['corr_rej'] += 1; return None
        n = np.array([-math.sin(h), math.cos(h)])
        k = 0.35 if len(est) == 2 else 0.2          # G6 v2: one side only (gateway edge, partial hedge) -> lower gain
        self.p = self.p + k * (lat_m - lat) * n; self.sig_l = 0.1; self.last_corr_odo = self.odo
        self.corr_valid = True; self.corr_lat = lat_m; self.stats['corr_upd'] += 1
        return lat_m

    def quality(self):
        if self.p is None: return 'none'
        if self.sig_s < 1.0 and self.sig_l < 0.25: return 'good'
        if self.sig_s < 2.5 and self.sig_l < 0.6: return 'degraded'
        return 'lost'

    def output(self, dt):
        """Position forwarded to the autopilot as GPS_INPUT. Motion (odometry prediction) passes straight through; corrections
        (RTK / corridor / the narrowing reference offset) reach the output at <= 0.25 m/s so the autopilot EKF sees no glitch."""
        if self.p is None: return None
        tgt = self.p.copy()
        if self.out is None: self.out = tgt.copy()
        d = tgt - self.out; m = float(np.linalg.norm(d)); lim = 0.15 * dt     # G6 v2: estimate corrections reach the EKF at <= 0.15 m/s
        self.out = tgt.copy() if m <= lim else self.out + d * (lim / m)
        o = self.out.copy()
        if self.lat_offset:      # G6 v3: the narrowing reference shift is added after the limiter (its own rate limit is 0.4 m/s)
            s, _ = self.S.lane.project(self.p); h = self.S.lane.heading(s); o = o + self.lat_offset * np.array([-math.sin(h), math.cos(h)])
        return o


def hitch_gov(w_cmd, v, phi, cap_deg=None, margin_deg=3.0, k=2.0):
    """Rev G6 hitch governor (needs a kingpin angle sensor - ASSUMED, magnetic encoder on the kingpin).
    phi = tug yaw - bin yaw (rad). The bin's yaw rate is v/L sin(phi); keep |phi| <= cap - margin by bounding the tug yaw rate."""
    lim = math.radians((HITCH_CAP_DEG if cap_deg is None else cap_deg) - margin_deg)
    wb = v / BIN['L'] * math.sin(phi)
    return float(np.clip(w_cmd, wb - k * (lim + phi), wb + k * (lim - phi)))
