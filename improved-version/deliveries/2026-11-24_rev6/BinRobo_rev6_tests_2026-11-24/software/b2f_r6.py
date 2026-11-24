"""Revision 6 additions to the mission software (24 Nov 2026, reviewer/tester agent). Mixed into Companion in b2f_companion_x.py;
everything here is OFF unless X_R6=1.

Why: the re-test of revision 5.1 (and my own reproduction) showed a person who walks out from the far hedge and crosses about 1 m in
front of the nose is touched in 2 of 3 runs. The lidar saw the person for 2.5 s; the software only reacted to returns already inside
the robot's own path, and the person was outside the camera's +-55 degree view until the last 0.3 s.

What this adds
  lane watch      anything compact standing or moving INSIDE the lane, anywhere the lidars see, is an "object" - found from the scan
                  itself (local hedge-face fit), with the map as a second opinion under an RTK fix only. Not limited to the robot's path.
  rear lidars     two more lidars on the rear leg tips (modelled here from truth, like the front one): all-round view at 0.30 m.
  near zone       an object within X_R6_NEAR (3.0 m) of the robot's body, in any direction: stop and wait.
  first sight     ONE camera detection (not two in a row) already slows the robot to the touch-safe speed.
  pause           camera-confirmed person or animal within 5 m: pause as in 5.1. A camera "person" further than 2.5 m away that no lidar
                  can find is not paused for (false detections), only slowed for.
  restart         only when nothing has been inside the zones for 3 s on ALL sensors; first 3 m at 0.2 m/s.
  static things   an object that no camera calls a person, that has not moved for 20 s and is 0.5 m clear of the path: pass at 0.2 m/s.
  hold timer      15 minutes of pausing within any 20 minutes: hold and alert (was: 15 minutes in one unbroken pause).
  fast cruise     X_VFAST="g:v_bin:v_empty,..." clear-lane speed by downhill slope; used only under an RTK fix, between two hedge faces,
                  with nothing in the lane within the slow zone and no camera sighting. Zones and the protective field grow with speed.
Test switches: X_PHANTOM=<false camera persons per minute>.
"""
import os, math, json
import numpy as np
from scene import seg_dist
from world import wrap
import b2f_world as BW
from b2f_world import ROB

R6 = os.environ.get('X_R6') == '1'
NEAR = float(os.environ.get('X_R6_NEAR', '3.0'))          # m from the body: stop and wait
REAR = os.environ.get('X_R6_REAR', '1') == '1'            # rear corner lidars fitted
STATIC_T = float(os.environ.get('X_R6_STATIC_T', '20'))   # s without movement before a non-person object may be passed
V_CRAWL = 0.20
CAM_R = float(os.environ.get('X_PPL_PAUSE_R', '5.0'))     # camera pause radius (same setting as 5.1)
HOLD_SUM = float(os.environ.get('X_PPL_PAUSE_MAX', '900')); HOLD_WIN = 1200.0
PHANTOM = float(os.environ.get('X_PHANTOM', '0'))
DEBUG = os.environ.get('X_R6_DEBUG') == '1'
V_QUICK = float(os.environ.get('X_R6_VQUICK', '0.45'))    # a pause entered faster than this brakes at once (firmware HOLD)
VFAST = sorted(tuple(float(v) for v in t.split(':')) for t in os.environ.get('X_VFAST', '').split(',') if t)
VTOP = float(os.environ.get('X_VTOP', '0.5'))             # firmware WP_SPEED: full thrust command = this speed
V_TOUCH = 0.45                                            # speeds up to here are "touch-safe" commands (the slope rule sets the actual value)
FLOAT_V = float(os.environ.get('X_R6_FLOAT_V', '0'))        # clear-lane speed cap under RTK Float with both hedge faces in view (0 = stay at 0.3 m/s as before)
FAST_GAP = float(os.environ.get('X_R6_FAST_GAP', '0.0'))  # extra distance from the left hedge when faster than touch-safe (m)


def now_ok(c):
    """at most one mode request every 0.5 s"""
    return c.w.t - getattr(c, '_r6_mode_t', -9.0) > 0.5


def slow_range(v):
    """how far ahead an object in the lane already slows the robot to the touch-safe speed (m): 4 m at 0.4 m/s, 10 m at 1.0 m/s."""
    return 4.0 + 10.0 * max(0.0, v - 0.4)


def rect_dist(bx, by):
    """distance from robot-frame points to the robot's outline (0 inside)."""
    dx = np.maximum(np.maximum(ROB['x0'] - bx, bx - ROB['x1']), 0.0); dy = np.maximum(np.abs(by) - ROB['hw'], 0.0)
    return np.hypot(dx, dy)


class R6Mixin:
    # ------------------------------------------------------------ sensors
    def rear_scan(self):
        """the two rear-corner lidars (leg tips, 0.30 m above the ground): robot-frame points. Truth geometry, 10 mm noise, 1 degree steps,
        12 m range. Each sees 263 degrees: its own flank, the rear, and across the back of the robot."""
        w = self.w; c, s = math.cos(w.yaw), math.sin(w.yaw)
        if not hasattr(self, '_r6rng'): self._r6rng = np.random.default_rng(6060 + int(self.sc.get('seed', 0) or 0))
        H = w.S.hedge_truth; mid = 0.5 * (H[:, :2] + H[:, 2:]); segs = [H[np.linalg.norm(mid - np.array([w.x, w.y]), axis=1) < 16.0]]
        for o in w.standing():
            if o.get('engaged'): continue
            if math.hypot(o['x'] - w.x, o['y'] - w.y) < 16.0: segs.append(BW.box_segs(o['x'], o['y'], o['yaw'], o['L'], o['W']))
        segs = [q for q in segs if len(q)]; Sg = np.concatenate(segs) if segs else np.zeros((0, 4)); movers = w.movers_now(); out = []
        for side in (1.0, -1.0):
            lx, ly = ROB['x0'], side * (ROB['hw'] - 0.02); ox = w.x + lx * c - ly * s; oy = w.y + lx * s + ly * c
            rel = side * np.arange(4, 267); ang = w.yaw + np.radians(rel); D = np.c_[np.cos(ang), np.sin(ang)]; r = np.full(len(rel), np.inf)
            if len(Sg):
                A = Sg[:, :2] - np.array([ox, oy]); E = Sg[:, 2:] - Sg[:, :2]
                den = D[:, None, 0] * E[None, :, 1] - D[:, None, 1] * E[None, :, 0]
                with np.errstate(divide='ignore', invalid='ignore'):
                    t = (A[None, :, 0] * E[None, :, 1] - A[None, :, 1] * E[None, :, 0]) / den
                    u = (A[None, :, 0] * D[:, None, 1] - A[None, :, 1] * D[:, None, 0]) / den
                ok = (np.abs(den) > 1e-9) & (t > 0.02) & (u >= 0) & (u <= 1); r = np.min(np.where(ok, t, np.inf), axis=1)
            for (mx, my, rr, k) in movers:
                dx, dy = mx - ox, my - oy; b = D[:, 0] * dx + D[:, 1] * dy; cc = dx * dx + dy * dy - rr * rr; disc = b * b - cc
                hit = (disc > 0) & (b > 0); r = np.minimum(r, np.where(hit, b - np.sqrt(np.maximum(disc, 0)), np.inf))
            r[r > 12.0] = np.inf; ok = np.isfinite(r); r = r[ok] + self._r6rng.normal(0, 0.01, int(ok.sum())); a = np.radians(rel[ok])
            out.append(np.c_[lx + r * np.cos(a), ly + r * np.sin(a)])
        return np.concatenate(out) if out else np.zeros((0, 2))

    def r6_points(self):
        """all lidar points in the robot frame (front lidar scan + rear lidars)."""
        P = []
        if self.scan is not None:
            r = self.scan; ok = np.isfinite(r)
            if ok.any():
                a = np.radians(np.arange(360))[ok]; P.append(np.c_[ROB['lidar_x'] + r[ok] * np.cos(a), r[ok] * np.sin(a)])
        if REAR: P.append(self.rear_scan())
        P = [q for q in P if len(q)]
        return np.concatenate(P) if P else np.zeros((0, 2))

    def r6_objects(self, rng=12.0):
        """compact things standing free inside the lane, from the lidars. A return is HEDGE if it lies on or behind the local hedge face
        (face = median sideways distance of the returns 0.3 to 2 m before and after it on the same side), or - under an RTK fix only -
        within 0.40 m of the surveyed hedge line. Where no face can be fitted and there is no fix, the map with the old 1.2 m radius is
        used. What is left, less the known bins and the dock, is clustered (0.45 m). Returns a list of dicts (robot frame):
        x, y (centre), n, d (m to the robot's outline), w (world xy), conf (seen in two scans running), moved (m in the last second)."""
        now = self.w.t
        if getattr(self, '_r6_t', -9.0) == now: return self._r6_objs
        self._r6_t = now; self._r6_objs = []; self._r6_hedge = np.zeros((0, 2))
        p = self.pose(); B = self.r6_points()
        if p is None or len(B) == 0: return self._r6_objs
        x, y, yaw = p; c, s = math.cos(yaw), math.sin(yaw)
        B = B[(np.hypot(B[:, 0], B[:, 1]) < rng + 1.5) & (rect_dist(B[:, 0], B[:, 1]) > 0.03)]
        if len(B) == 0: return self._r6_objs
        W = np.c_[x + B[:, 0] * c - B[:, 1] * s, y + B[:, 0] * s + B[:, 1] * c]; fix = self.r.raw_fix == 6; N = len(B)
        # local face on each side. While the robot turns on the spot it stands across the lane, and a face fitted along its own axis is
        # meaningless (a person walking up beside it was taken for hedge). Then the fit is made in a frame turned to the lane direction.
        Bf = B
        if getattr(self, '_r6_piv', False):
            psi = yaw - float(self.S.lane.heading(float(self.w.s_lat()[0]))); cp_, sp_ = math.cos(psi), math.sin(psi)
            Bf = np.c_[B[:, 0] * cp_ - B[:, 1] * sp_, B[:, 0] * sp_ + B[:, 1] * cp_]
        face = np.full(N, np.nan); rr_ = np.hypot(B[:, 0], B[:, 1])
        for side in (1.0, -1.0):
            idx = np.where((Bf[:, 1] * side > 0.30))[0]
            if len(idx) < 4: continue
            xs = Bf[idx, 0]; ys = np.abs(Bf[idx, 1])
            # A face is long. It is fitted from 0.25 m bins along the lane (the median sideways distance in each bin), not from single
            # returns: a walker or a box fills two or three bins however many returns it gives; a hedge fills them all. Near the robot
            # (within 5 m) a face needs five filled bins among those 0.3 to 2 m before and after the return; farther off, three.
            # Before, at a gateway - no hedge beside the walker - their own returns outvoted the few hedge returns and made a 'face'
            # that they then lay on: the lidar took them for hedge.
            bi = np.floor(xs / 0.25).astype(int); ub, inv = np.unique(bi, return_inverse=True)
            bmed = np.array([np.median(ys[inv == k]) for k in range(len(ub))]); bx = (ub + 0.5) * 0.25
            dxm = np.abs(xs[:, None] - bx[None, :]); nb = (dxm > 0.30) & (dxm < 2.0)
            cnt = nb.sum(axis=1); Y = np.where(nb, bmed[None, :], np.nan)
            with np.errstate(all='ignore'): med = np.nanmedian(Y, axis=1)
            face[idx] = np.where(cnt >= np.where(rr_[idx] < 5.0, 5, 3), med, np.nan)
        known_face = np.isfinite(face); hedge = known_face & (np.abs(Bf[:, 1]) > face - 0.30)
        H = self.map_segs; mid = 0.5 * (H[:, :2] + H[:, 2:]); Hn = H[np.linalg.norm(mid - np.array([x, y]), axis=1) < rng + 8.0]
        dmap = np.min(seg_dist(W[:, None, :], Hn[None, :, :2], Hn[None, :, 2:]), axis=1) if len(Hn) else np.full(N, np.inf)
        if fix: hedge |= dmap < 0.40
        else: hedge |= (~known_face) & (dmap < 1.2)
        self._r6_hedge = B[hedge]      # for the gateway look-ahead (r6_gap_ahead)
        # outside the lane altogether (seen through a gap): lateral position on the map, generous when the fix is poor
        lat = np.array([self.S.lane.project(q)[1] for q in W[~hedge]]) if (~hedge).any() else np.zeros(0)
        keep = ~hedge; k_idx = np.where(keep)[0]
        if len(k_idx):
            out_lane = np.abs(lat) > HL_MAP + (0.10 if fix else 1.2); keep[k_idx[out_lane]] = False
        for k, b in self.st['known']:
            m = np.where(keep)[0]
            if len(m) == 0: break
            g = np.array([BW.gap_pts_box(W[i:i + 1], dict(b, L=b['L'] + (0.5 if fix else 2.4), W=b['W'] + (0.5 if fix else 2.4))) for i in m])
            keep[m[g <= 0.0]] = False
        for (ix, iy, ir, until) in self.st.get('r6_ignore', []):
            if until > now: keep &= np.hypot(W[:, 0] - ix, W[:, 1] - iy) > ir
        m = np.where(keep)[0]
        if len(m) == 0:
            self._r6_prev = []; self._r6_prev_t = now
            # an empty look is a record too: 'nothing was there a second ago' (for the arrival rule at a turn, r6_near_pivot)
            hist = self.st.setdefault('r6_hist', []); hist.append((now, []))
            while hist and now - hist[0][0] > 1.3: hist.pop(0)
            self._r6_hist_ok = any(now - h[0] >= 0.9 for h in hist)
            return self._r6_objs
        Bm = B[m]; Wm = W[m]; lab = -np.ones(len(m), int); nl = 0; Bh = B[hedge]
        for i in range(len(m)):
            if lab[i] >= 0: continue
            lab[i] = nl; stack = [i]
            while stack:
                j = stack.pop(); near = np.where((lab < 0) & (np.hypot(Bm[:, 0] - Bm[j, 0], Bm[:, 1] - Bm[j, 1]) < 0.45))[0]
                lab[near] = nl; stack += list(near)
            nl += 1
        prev = getattr(self, '_r6_prev', []) if now - getattr(self, '_r6_prev_t', -9.0) < 0.35 else []; hist = self.st.setdefault('r6_hist', []); objs = []
        for q in range(nl):
            Bq = Bm[lab == q]; Wq = Wm[lab == q]
            if len(Bq) < 2: continue
            cw = Wq.mean(axis=0); cb = Bq.mean(axis=0); d = float(np.min(rect_dist(Bq[:, 0], Bq[:, 1])))
            if len(Bh):   # joined to the hedge (a bulge, a post in the hedge line): nearest hedge return closer than the scan's own point spacing allows for a free-standing thing
                rq = float(np.min(np.hypot(Bq[:, 0] - (ROB['lidar_x'] if cb[0] > 0.5 else ROB['x0']), Bq[:, 1])))
                dh = float(np.min(np.hypot(Bh[:, 0][None, :] - Bq[:, 0][:, None], Bh[:, 1][None, :] - Bq[:, 1][:, None])))
                if dh < 0.20 + 0.05 * rq: continue
            conf = any(math.hypot(cw[0] - pw[0], cw[1] - pw[1]) < 0.6 for pw in prev)
            objs.append(dict(x=float(cb[0]), y=float(cb[1]), n=int(len(Bq)), d=d, w=(float(cw[0]), float(cw[1])), conf=conf,
                             ymin=float(np.min(np.abs(Bq[:, 1]))), xmin=float(np.min(Bq[:, 0])), xmax=float(np.max(Bq[:, 0]))))
        self._r6_prev = [o['w'] for o in objs]; self._r6_prev_t = now
        # movement over the last second (world frame): compare with the object positions logged about 1 s ago
        hist.append((now, [o['w'] for o in objs]));
        while hist and now - hist[0][0] > 1.3: hist.pop(0)
        old = [h for h in hist if now - h[0] >= 0.9]
        self._r6_hist_ok = bool(old)      # the watch has been running for a second: 'was not there a second ago' can be told from 'no record'
        for o in objs:
            o['moved'] = None
            if old:
                dd = [math.hypot(o['w'][0] - pw[0], o['w'][1] - pw[1]) for pw in old[-1][1]]
                o['moved'] = min(dd) if dd else None      # None = was not there a second ago
        self._r6_objs = objs
        if DEBUG and self.w.movers_now():      # test aid: what became of the returns that lie on a walker
            mv = self.w.movers_now()[0]; on = np.hypot(W[:, 0] - mv[0], W[:, 1] - mv[1]) < mv[2] + 0.08
            print('R6DBG t %.2f fix %s pts on walker %d | face known %d, hedge %d, kept %d | objects %s' % (now, fix, int(on.sum()), int((known_face & on).sum()), int((hedge & on).sum()), int((keep & on).sum()),
                  [(round(o['x'], 2), round(o['y'], 2), o['n'], round(o['d'], 2), o['conf']) for o in objs]), flush=True)
        return objs

    def cam_tracks(self):
        """camera tracks for revision 6: [(x ahead of the axle, y left, radius, kind, confirmed, age of last sighting s)]. Updates the 5.1 model."""
        self.cam_people(); now = self.w.t; out = []
        for kind, tr in self.st.get('cam_trk', {}).items():
            if 'pos' not in tr: continue
            out.append((tr['pos'][0], tr['pos'][1], tr['pos'][2], kind, tr.get('until', -9.0) > now, now - tr['last']))
        return out

    # ------------------------------------------------------------ decisions
    def r6_near(self, hyst=0.0, yard=False, mv=0.15):
        """what is near, on every sensor. Returns dict: d (m, nearest thing that calls for a stop, or None), person (a camera-confirmed
        person or animal is one of them), holders (list of ('cam'|'lid', world xy, distance, in_path, corroborated))."""
        objs = [o for o in self.r6_objects() if o['conf']]; holders = []; x, y, yaw = self.pose(); c, s = math.cos(yaw), math.sin(yaw)
        for (bx, by, r_, kind, confd, age) in self.cam_tracks():
            if not confd: continue
            rng_ = math.hypot(bx - 1.04, by) - r_
            cor = any(math.hypot(o['x'] - bx, o['y'] - by) < 0.8 for o in objs)
            if rng_ < 2.5 + hyst or (cor and rng_ < CAM_R + hyst):
                holders.append(('cam', (x + bx * c - by * s, y + bx * s + by * c), rng_, abs(by) - r_ < ROB['hw'] + 0.5 and bx > ROB['x1'] - 0.3, cor or rng_ < 2.5))
        for o in objs:
            if yard and not (o['moved'] is not None and o['moved'] > mv): continue      # in the yard only things that move count (bins, walls and clutter are for the yard logic)
            if o['d'] < NEAR + hyst:
                inp = o['ymin'] < ROB['hw'] + 0.5 and o['xmax'] > ROB['x1'] - 0.3
                sg_ = getattr(self, '_r6_sgn', None)
                if not yard and sg_ and not inp:      # the lane bends: also measure against the planned line at the thing's own station
                    so_, lo_ = self.S.lane.project(np.array(o['w'])); sr_ = float(self.w.s_lat()[0])
                    if (so_ - sr_) * sg_ > ROB['x1'] - 0.3 and abs(lo_ - self.lat_nominal(float(so_), sg_)) < ROB['hw'] + 0.5 + 0.2: inp = True
                holders.append(('lid', o['w'], o['d'], inp, False))
        if not holders: return dict(d=None, person=False, holders=[])
        return dict(d=min(h[2] for h in holders), person=any(h[0] == 'cam' and h[4] for h in holders), holders=holders)

    def r6_near_pivot(self, hyst=0.0, mv=0.15):
        """near, for a turn on the spot: a camera person, anything that moves within the stand-still zone, and anything unknown at all -
        moving or not - within 1.75 m of the axle, the circle the nose sweeps (+ hyst). The same test starts the turn, watches it and
        allows the restart: before, the restart used the first two only, so the robot turned on with a person standing in the circle."""
        nr = self.r6_near(hyst=hyst, yard=True, mv=mv)
        objs = [o for o in self.r6_objects() if o['conf']]
        sw = [o for o in objs if math.hypot(o['x'], o['y']) < 1.75 + 0.6 * hyst]
        # Outside the house yard a thing inside the stand-still zone that was not there a second ago has ARRIVED: it counts as moving at
        # once. Movement is judged against where a thing was a second ago, so a walker close to the hedge, who is only told from it at
        # 3 to 4 m, was not a 'mover' until a second later: the turn ran on for up to 1.4 s with them inside 3 m (pivot test b).
        # Not in the yard: there the turn itself brings walls and clutter into view.
        if getattr(self, '_r6_hist_ok', False) and float(self.w.s_lat()[0]) > 30.0:
            sw += [o for o in objs if o['moved'] is None and o['d'] < NEAR + hyst and not any(o is q for q in sw)]
        if not sw: return nr
        hs = list(nr['holders']) + [('lid', o['w'], o['d'], True, False) for o in sw]
        return dict(d=min(h[2] for h in hs), person=nr['person'], holders=hs)

    def r6_pause(self, near, where='lane'):
        """stop and stand still while anything is in the zones. Restart when every sensor has shown the zones empty for 3 s. Things that no
        camera calls a person, have not moved for STATIC_T and are clear of the path are then passed at a crawl. Owner message after 2
        minutes; hold after 15 minutes of pausing in any 20 minutes; a non-person thing in the path for 120 s is 'path blocked'."""
        st = self.st; t0 = self.w.t; clear = None; told = False; np0 = self.no_pause; self.no_pause = True
        h0 = min(near['holders'], key=lambda h: h[2])
        v_in_ = abs(self.w.v)
        rec = dict(t=round(t0, 1), v_in=round(v_in_, 2), range=round(near['d'], 2), s=round(float(self.w.s_lat()[0]), 1), by=h0[0], where=where); st['metrics'].setdefault('ppl_pauses', []).append(rec)
        rec['obj'] = [(round(o['x'], 2), round(o['y'], 2), o['n'], round(o['d'], 2), None if o['moved'] is None else round(o['moved'], 2)) for o in self.r6_objects() if o['conf'] and o['d'] < NEAR + 0.5][:4]
        self.r.ev('pi', '%s: %s %.1f m away -> stand still' % ('camera' if h0[0] == 'cam' else 'lidar', 'person or animal' if near['person'] else 'something', near['d']))
        seen_ = bool(near['person']); was_person = seen_ or t0 - st.get('r6_person_t', -999.0) < 60.0; ref = None; ref_t = t0; log = st.setdefault('r6_pauselog', []); last_ = t0; t_path = 0.0
        if seen_: st['r6_person_t'] = t0
        while True:
            # standing still means still: once stopped, the firmware goes to HOLD (drive outputs neutral, brakes on) - in GUIDED its heading and
            # turn-rate loops keep the wheels twitching (+-0.05 rad/s), and the nose corner must not move with someone 0.3 m from it
            # Entered above the touch-safe speed: brake at once. HOLD puts the drive in neutral with the brakes on, which is the stop the
            # physics tests measured (reply note, section 4.5); the firmware's own ramp (0.8 m/s2) would take 0.3 to 0.5 s longer.
            if v_in_ > V_QUICK or (abs(self.w.v) < 0.02 and abs(self.w.w) < 0.08):
                self._r6_hold = True
                if self.mode != 'HOLD' and now_ok(self): self.set_mode(4); self._r6_mode_t = self.w.t
            else: self.stop_cmd()
            yield
            now = self.w.t; nr = self.r6_near_pivot(hyst=0.5) if where == 'pivot' else self.r6_near(hyst=0.5, yard=(where != 'lane')); dt_ = now - last_; last_ = now
            if nr['person']: st['r6_person_t'] = now; seen_ = True
            # a person stays a person: once a camera has called it one during this pause it counts as one until the pause ends, and a thing
            # that turns up within a minute of the last sighting counts as one too
            was_person = seen_ or now - st.get('r6_person_t', -999.0) < 60.0
            if nr['d'] is None: clear = clear or now
            else: clear = None
            if clear and now - clear > 3.0: self.r.ev('pi', 'nothing near for 3 s on any sensor -> carry on, slowly at first'); break
            if nr['d'] is not None and not was_person:
                # a thing no camera has called a person. Still = no holder further than 0.4 m from where the holders were when the clock started
                # (a holder that drops out for a scan does not restart the clock).
                cur = [h[1] for h in nr['holders']]; inpath = any(h[3] for h in nr['holders'])
                if ref is None or any(min(math.hypot(a[0] - b[0], a[1] - b[1]) for b in ref) > 0.4 for a in cur): ref = cur; ref_t = now
                if inpath: t_path += dt_
                # it may be passed at a crawl only if it is clear of the path AND the front camera has had it in view all this time and never
                # called it a person. Something beside or behind the robot is outside that view: it is treated as a person and waited for.
                px_, py_, pyaw_ = self.pose(); c_, s_ = math.cos(pyaw_), math.sin(pyaw_)
                def in_view(w_):
                    bx_ = (w_[0] - px_) * c_ + (w_[1] - py_) * s_ - 1.04; by_ = -(w_[0] - px_) * s_ + (w_[1] - py_) * c_
                    return bx_ > 0.2 and math.hypot(bx_, by_) < 5.5 and abs(math.atan2(by_, bx_)) < math.radians(50.0)
                if now - ref_t > STATIC_T and not inpath and all(in_view(w_) for w_ in cur):
                    ig = st.setdefault('r6_ignore', [])
                    for h in nr['holders']: ig.append((h[1][0], h[1][1], 0.8, now + 120.0))
                    self.r.ev('pi', 'in the camera view, not called a person, has not moved for %.0f s and is clear of the path -> pass at 0.2 m/s' % STATIC_T); rec['passed_static'] = True; break
                if now - t0 > 120.0:
                    g_, hl_ = self.obstacle_ahead()
                    if t_path > 60.0 or (g_ is not None and g_ < 3.0 and not hl_):
                        self.alert('path blocked for 120 s (something %.1f m from the robot, in its path)' % nr['d']); self.finish('alert', 'path blocked')
                        while True: self.stop_cmd(); yield
            elif nr['d'] is not None or (clear and now - clear > 1.0): ref = None; ref_t = now      # a holder that drops out for less than a second does not restart the stillness clock
            if not told and now - t0 > 120.0:
                told = True; self.alert('waiting: %s has been near the robot for 2 minutes (it carries on by itself when the way is clear)' % ('someone' if was_person else 'something'))
            tot = sum(min(b, now) - max(a, now - HOLD_WIN) for a, b in log if b > now - HOLD_WIN) + (now - t0)
            if tot > HOLD_SUM:
                self.alert('someone or something has been near the robot for %d of the last %d minutes - holding' % (round(HOLD_SUM / 60.0), round(HOLD_WIN / 60.0))); self.finish('alert', 'path blocked')
                while True: self.stop_cmd(); yield
        rec['wait_s'] = round(self.w.t - t0, 1); rec['person'] = bool(was_person); log.append((t0, self.w.t)); self.no_pause = np0; st['nofix_t0'] = None
        if getattr(self, '_r6_hold', False):   # back to GUIDED before moving
            tm_ = self.w.t
            while self.mode != 'GUIDED' and self.w.t - tm_ < 5.0:
                if (self.w.t - tm_) % 1.0 < 0.11: self.set_mode(15)
                yield
            self._r6_hold = False; self._stop_yaw = None
        st['r6_crawl_odo'] = self.w.odo + 3.0

    def r6_gap_ahead(self, look=5.5, gap=1.8):
        """a gateway ahead: on either side the hedge returns stop for more than `gap` metres somewhere between 1 m behind the nose and
        `look` metres ahead of it. (No farther: beyond that the returns from the near hedge are too far apart to tell a gap from a hedge.)"""
        self.r6_objects(); H = getattr(self, '_r6_hedge', None)
        if H is None or len(H) == 0: return True
        x0 = ROB['x1'] - 1.0; x1 = ROB['x1'] + look
        for side in (1.0, -1.0):
            xs = np.sort(H[(H[:, 1] * side > 0.30) & (H[:, 0] > x0 - 1.0) & (H[:, 0] < x1 + 1.0), 0])
            if len(xs) == 0: return True
            if float(np.max(np.diff(np.r_[x0, np.clip(xs, x0, x1), x1]))) > gap: return True
        return False

    def r6_lane(self, v, in_lane, fast_ok, s, sgn, gdown, loaded, vcap=9.0):
        """lane loop hook: returns (action, v). action 'pause' (with self._r6_nr set) or None; v = the speed allowed."""
        self._r6_sgn = sgn if in_lane else None
        nr = self.r6_near(yard=not in_lane)
        if nr['d'] is not None: self._r6_nr = nr; return 'pause', 0.0
        v_touch = v; objs = [o for o in self.r6_objects() if o['conf']]
        seen = [t for t in self.cam_tracks() if t[5] < 1.0]                      # any camera sighting in the last second, confirmed or not
        ahead = [o for o in objs if o['xmax'] > ROB['x1'] - 0.5]
        d_ahead = min([math.hypot(max(o['xmin'] - ROB['x1'], 0.0), max(o['ymin'] - ROB['hw'], 0.0)) for o in ahead], default=None)
        if VFAST and fast_ok and in_lane:
            vf = v_touch
            for thr_, vb_, ve_ in VFAST:
                if gdown >= thr_: vf = vb_ if loaded else ve_
            vf = max(min(vf, vcap), v_touch)
            # bends: the heading command may change at HDG_RATE only; keep the turn rate the bend asks for under 80 % of that
            h0 = self.S.lane.heading(s); kap = max(abs(wrap(self.S.lane.heading(s + sgn * q) - h0)) / q for q in (2.0, 4.0, 6.0))
            fl_ = getattr(self, '_r6_fl', None)
            if kap > 1e-6 and 0.12 / kap < vf:
                vf = max(v_touch, 0.12 / kap)
                if fl_ is not None: fl_['bend'] = round(fl_.get('bend', 0.0) + 0.1, 1)
            if seen or (d_ahead is not None and d_ahead < slow_range(vf)):
                vf = v_touch
                if fl_ is not None: fl_['seen' if seen else 'object'] = round(fl_.get('seen' if seen else 'object', 0.0) + 0.1, 1)
            if vf > v_touch + 0.01 and self.r6_gap_ahead():      # a gateway or a gap in the hedge within 5.5 m ahead: touch-safe speed until it is passed
                vf = v_touch
                if fl_ is not None: fl_['gap'] = round(fl_.get('gap', 0.0) + 0.1, 1)
            if fl_ is not None and vf > v_touch + 0.01: fl_['fast'] = round(fl_.get('fast', 0.0) + 0.1, 1)
            v = vf
        if seen: v = min(v, v_touch)
        if d_ahead is not None and d_ahead < slow_range(v): v = min(v, v_touch)
        if self.w.odo < self.st.get('r6_crawl_odo', -1.0): v = min(v, V_CRAWL)
        if self.st.get('r6_ignore') and any(u > self.w.t and math.hypot(ix - self.w.x, iy - self.w.y) < 5.0 for ix, iy, ir, u in self.st['r6_ignore']): v = min(v, V_CRAWL)
        return None, v


HL_MAP = 3.6 / 2 + 0.25
