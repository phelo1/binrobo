#!/usr/bin/env python3
"""Render one scenario trace to an MP4 clip (960x540, 10 fps): heading-up chase map with lidar, lane overview,
rear camera inset (re-rendered from the logged state, real ArUco detection drawn), elevation strip, telemetry, title card.
Long cruise stretches are time-compressed (factor shown on screen).
Usage: render.py <scenario> <target_seconds> [out.mp4]"""
import json, math, os, subprocess, sys, numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from world import TUG, BIN, box_segs, wrap
from scene import detect
import scenarios as SC

W, H, FPS = 960, 540, 10
BIN_COL = {0: (45, 45, 45), 4: (40, 140, 40), 30: (30, 70, 120), 10: (40, 110, 200)}     # Rev G3: black / green / brown / neighbour
BIN_NAME = {0: 'black', 4: 'green', 30: 'brown', 10: 'neighbour'}
FONT = cv2.FONT_HERSHEY_SIMPLEX
FIXNAME = {6: 'RTK FIXED', 5: 'RTK FLOAT', 1: 'NO FIX', 3: '3D', 0: '-'}


def put(img, txt, xy, sc=0.45, col=(255, 255, 255), th=1):
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):     # same-thickness shadow (a thicker stroke widens the glyph advance -> ghost letters)
        cv2.putText(img, txt, (xy[0] + dx, xy[1] + dy), FONT, sc, (0, 0, 0), th, cv2.LINE_AA)
    cv2.putText(img, txt, xy, FONT, sc, col, th, cv2.LINE_AA)


class Renderer:
    def __init__(self, name):
        self.name = name
        d = json.load(open(os.path.join(ROOT, 'out', 'G4', name, 'trace.json'))); self.meta = d['meta']; self.T = d['trace']
        self.res = json.load(open(os.path.join(ROOT, 'out', 'G4', name, 'result.json')))
        self.sc = SC.get(name); self.S = self.sc['site']; self.w = self.sc['world']; self.night = self.meta['night']
        self.static = self.meta['static']
        S = self.S
        self.lane_xy = S.lane.P; self.L = S.L
        # overview panel transform
        P = np.vstack([S.lane.P, S.road[np.linalg.norm(S.road - S.lane.P[-1], axis=1) < 120]])
        self.ov_min = P.min(0) - 15; self.ov_max = P.max(0) + 15
        self.ov_w, self.ov_h = 420, 180
        sc = min(self.ov_w / (self.ov_max[0] - self.ov_min[0]), self.ov_h / (self.ov_max[1] - self.ov_min[1])); self.ov_sc = sc
        self.ov_bg = self._overview_bg()
        self.el_bg, self.el_s, self.el_z = self._elev_bg()
        self.trail = []

    # ---------- static panels ----------
    def ov_px(self, p):
        c = (self.ov_min + self.ov_max) / 2
        return (int(self.ov_w / 2 + (p[0] - c[0]) * self.ov_sc), int(self.ov_h / 2 - (p[1] - c[1]) * self.ov_sc))

    def _overview_bg(self):
        img = np.zeros((self.ov_h, self.ov_w, 3), np.uint8); img[:] = (40, 60, 40) if not self.night else (35, 30, 25)
        R = self.S.road
        cv2.polylines(img, [np.array([self.ov_px(p) for p in R], np.int32)], False, (90, 90, 90), 3)
        z = np.array([self.S.ter.z(*p) for p in self.S.lane.P]); zn = (z - z.min()) / (np.ptp(z) + 1e-6)
        for i in range(len(self.S.lane.P) - 1):
            col = (int(255 * (1 - zn[i])), int(160 + 60 * zn[i]), int(255 * zn[i]))
            cv2.line(img, self.ov_px(self.S.lane.P[i]), self.ov_px(self.S.lane.P[i + 1]), col, 2, cv2.LINE_AA)
        put(img, 'house', self.ov_px(self.S.lane.P[0] + np.array([4, 4])), 0.38)
        put(img, 'the public road', self.ov_px(self.S.lane.P[-1] + np.array([-60, -18])), 0.38) if self.S.variant == 'real' else None
        put(img, 'lane overview (colour = height)', (6, 14), 0.38, (200, 200, 200))
        return img

    def _elev_bg(self):
        s = np.linspace(0, self.L, 200); z = np.array([self.S.ter.z(*self.S.lane.point(q)) for q in s])
        img = np.zeros((110, 420, 3), np.uint8); img[:] = (30, 30, 30)
        zmin, zmax = z.min() - 1, z.max() + 1
        pts = np.array([[int(10 + 400 * q / self.L), int(100 - 80 * (zz - zmin) / (zmax - zmin))] for q, zz in zip(s, z)], np.int32)
        cv2.polylines(img, [pts], False, (120, 200, 255), 2, cv2.LINE_AA)
        put(img, 'elevation %.0f-%.0f m  (house left, road right)' % (z.min(), z.max()), (8, 14), 0.38, (200, 200, 200))
        return img, s, (zmin, zmax)

    # ---------- chase view ----------
    def chase(self, r, scan):
        img = np.zeros((H, 540, 3), np.uint8)
        img[:] = (55, 95, 55) if not self.night else (22, 20, 18)
        x0, y0, yaw = r['x'], r['y'], r['yaw']; sc = 26.0
        c, s = math.cos(-yaw + math.pi / 2), math.sin(-yaw + math.pi / 2)
        cx, cy = 270, 330
        def px(p):
            dx, dy = p[0] - x0, p[1] - y0
            u = c * dx - s * dy; v = s * dx + c * dy
            return (int(cx + u * sc), int(cy - v * sc))
        S = self.S
        # road, lane surface, mouth
        Rd = S.road[np.linalg.norm(S.road - np.array([x0, y0]), axis=1) < 200]
        if len(Rd) > 1: cv2.polylines(img, [np.array([px(p) for p in Rd], np.int32)], False, (70, 70, 75) if not self.night else (40, 40, 45), int(2 * S.road_half * sc))
        sl, _ = S.lane.project(np.array([x0, y0]))
        ss = np.arange(max(0, sl - 25), min(self.L, sl + 25), 0.5)
        if len(ss) > 1:
            lp = np.array([px(S.lane.point(q)) for q in ss], np.int32)
            cv2.polylines(img, [lp], False, (95, 100, 100) if not self.night else (45, 45, 48), int(S.lane.width * sc))
            if sl > self.L - 30:
                mp = [px(S.lane.point(q, S.mouth_half)) for q in np.arange(S.lane.mouth[0], self.L, 0.5)] + \
                     [px(S.lane.point(q, -S.mouth_half)) for q in np.arange(self.L, S.lane.mouth[0], -0.5)]
                cv2.fillPoly(img, [np.array(mp, np.int32)], (90, 98, 98) if not self.night else (42, 42, 46))
            if sl < 30:
                yp = [px(S.lane.point(q, 6)) for q in np.arange(0, 25, 0.5)] + [px(S.lane.point(q, -6)) for q in np.arange(25, 0, -0.5)]
                cv2.fillPoly(img, [np.array(yp, np.int32)], (90, 98, 98) if not self.night else (42, 42, 46))
        Hh = S.hedges_near((x0, y0), 25)
        for h in Hh: cv2.line(img, px(h[:2]), px(h[2:]), (30, 70, 30) if not self.night else (20, 40, 20), 9)
        # Rev G3: private boundary (assumed 6 m from the road centre-line) and the junction wait point / drop pad
        if sl > self.L - 45 and getattr(S, 'boundary', None):
            for side in (1, -1):
                R_ = S.road; bl = []
                for i in range(len(R_) - 1):
                    a_, b_ = R_[i], R_[i + 1]; d_ = b_ - a_; Ld = np.linalg.norm(d_)
                    if Ld < 1e-6: continue
                    n_ = np.array([-d_[1], d_[0]]) / Ld
                    for t_ in np.arange(0, Ld, 1.0):
                        q = a_ + d_ * t_ / Ld + n_ * side * S.boundary
                        if np.linalg.norm(q - np.array([x0, y0])) < 30: bl.append(px(q))
                if len(bl) > 1: cv2.polylines(img, [np.array(bl, np.int32)], False, (0, 0, 200), 2, cv2.LINE_AA)
            jw = S.lane.point(self.L - SC.JUNCTION_WAIT, 0)
            cv2.line(img, px(S.lane.point(self.L - SC.JUNCTION_WAIT, -1.8)), px(S.lane.point(self.L - SC.JUNCTION_WAIT, 1.8)), (0, 220, 255), 2)
            put(img, 'wait pt', px(S.lane.point(self.L - SC.JUNCTION_WAIT, 2.0)), 0.38, (0, 220, 255))
            for k_, sp in SC.DROP_SPOTS(S).items():
                _, poly = box_segs(*S.lane.point(sp['s'], sp['lat']), S.lane.heading(sp['s']), 0.95, 0.75)
                cv2.polylines(img, [np.array([px(p) for p in poly], np.int32)], True, (180, 180, 180), 1)
            rp = px(S.road[np.argmin(np.linalg.norm(S.road - np.array([x0, y0]), axis=1))])
            put(img, 'public road / verge', (min(max(rp[0], 10), 380), min(max(rp[1], 60), 470)), 0.4, (120, 120, 255))
        if not hasattr(self, '_ko'):          # Rev G4: user keep-out zones (red hatch outline)
            from g4_features import DropAreas
            self._ko = DropAreas(S, self.sc.get('drop_areas'), self.sc.get('keepouts_extra', ())).keepouts
        for k_ in self._ko:
            if np.min(np.linalg.norm(k_['P'] - np.array([x0, y0]), axis=1)) < 30:
                pp = np.array([px(p) for p in k_['P']], np.int32); cv2.polylines(img, [pp], True, (60, 60, 255), 2, cv2.LINE_AA)
                put(img, 'keep-out', tuple(pp.mean(0).astype(int)), 0.38, (60, 60, 255))
        lt = r.get('lights') or ''
        if self.night:      # Rev G3: the lights actually on (B beacon, H head lamps, T red markers, I IR, W rear work lamp)
            ov = img.copy()
            cones = []
            if 'H' in lt: cones.append((0, 9, (90, 110, 120), 0.5))
            if 'I' in lt: cones.append((math.pi, 4, (70, 40, 70), 0.6))
            if 'W' in lt: cones.append((math.pi, 3.5, (120, 120, 120), 0.9))
            for ang0, rng_, col, wd in cones:
                pts = [px((x0, y0))] + [px((x0 + rng_ * math.cos(yaw + ang0 + a), y0 + rng_ * math.sin(yaw + ang0 + a))) for a in np.linspace(-wd, wd, 9)]
                cv2.fillPoly(ov, [np.array(pts, np.int32)], col)
            img = cv2.addWeighted(ov, 0.5, img, 0.5, 0)
        # trail
        if len(self.trail) > 1:
            cv2.polylines(img, [np.array([px(p) for p in self.trail[-400:]], np.int32)], False, (0, 200, 255), 1, cv2.LINE_AA)
        # static obstacles
        for o in self.static:
            _, poly = box_segs(o['x'], o['y'], o['yaw'], o['L'], o['W'])
            col = (40, 40, 160) if o['kind'] == 'car' else (30, 80, 120)
            cv2.fillPoly(img, [np.array([px(p) for p in poly], np.int32)], col)
            put(img, o['kind'], px((o['x'], o['y'])), 0.4)
        # bins
        def draw_bin(b, col, ours=True, state='up'):
            Lb, Wb = (BIN['h'], BIN['w']) if state == 'tipped' else (BIN['d'], BIN['w'])
            _, poly = box_segs(b[0], b[1], b[2], Lb, Wb)
            cv2.fillPoly(img, [np.array([px(p) for p in poly], np.int32)], col)
            cv2.polylines(img, [np.array([px(p) for p in poly], np.int32)], True, (200, 200, 200), 1)
            hp = [px(poly[0]), px(poly[3])]                  # +x face = handle side
            cv2.line(img, hp[0], hp[1], (0, 165, 255), 3)
        if r['bin'] is not None:
            draw_bin(r['bin'], BIN_COL.get(r.get('bin_id', 0), (40, 120, 40)), True, r['bin'][3])
            if r.get('bin_id', 0) != 0 or r.get('others_id'): put(img, BIN_NAME.get(r.get('bin_id', 0), ''), px((r['bin'][0] + 0.5, r['bin'][1] + 0.5)), 0.38)
        for o, i0 in zip(r.get('others', []), r.get('others_id') or [10] * 9):
            draw_bin(o, BIN_COL.get(i0, (120, 80, 40))); put(img, BIN_NAME.get(i0, ''), px((o[0] + 0.5, o[1] + 0.5)), 0.38, (200, 200, 200))
        # lidar hits
        if scan is not None:
            ox = x0 + TUG['lidar_x'] * math.cos(yaw); oy = y0 + TUG['lidar_x'] * math.sin(yaw)
            ang = yaw + np.radians(np.arange(360)); ok = np.isfinite(scan)
            for a, d in zip(ang[ok][::2], scan[ok][::2]):
                cv2.circle(img, px((ox + d * math.cos(a), oy + d * math.sin(a))), 2, (60, 60, 255), -1)
        # tug
        _, poly = box_segs(x0 + (TUG['front'] - TUG['rear']) / 2 * math.cos(yaw), y0 + (TUG['front'] - TUG['rear']) / 2 * math.sin(yaw), yaw,
                           TUG['front'] + TUG['rear'], 2 * TUG['half_w'])
        cv2.fillPoly(img, [np.array([px(p) for p in poly], np.int32)], (0, 140, 255))
        cv2.polylines(img, [np.array([px(p) for p in poly], np.int32)], True, (0, 0, 0), 1)
        for v in r.get('veh', []) or []:      # Rev G4: moving vehicles
            _, poly = box_segs(v[0], v[1], v[2], v[3], v[4])
            cv2.fillPoly(img, [np.array([px(p) for p in poly], np.int32)], (60, 60, 200)); cv2.polylines(img, [np.array([px(p) for p in poly], np.int32)], True, (255, 255, 255), 1)
            fp_ = (v[0] + 0.5 * v[3] * math.cos(v[2]), v[1] + 0.5 * v[3] * math.sin(v[2])); cv2.circle(img, px(fp_), 4, (0, 255, 255), -1)
            put(img, v[5], px((v[0] + 0.6, v[1] + 0.6)), 0.45, (255, 220, 220))
        for q in r.get('rad', []) or []:      # Rev G4: radar targets (vehicle-like SNR): arc at the reported range
            ang0 = yaw if q[0] == 'f' else yaw + math.pi
            pts_ = [px((x0 + q[1] * math.cos(ang0 + a), y0 + q[1] * math.sin(ang0 + a))) for a in np.linspace(-0.35, 0.35, 8)]
            cv2.polylines(img, [np.array(pts_, np.int32)], False, (0, 255, 255) if q[2] < -0.3 else (0, 180, 0), 2, cv2.LINE_AA)
        for m in r.get('movers', []):      # people / dogs / vehicles drawn on top so a child behind the tug is visible
            cv2.circle(img, px(m[:2]), max(4, int(m[2] * sc)), (200, 120, 255), -1); cv2.circle(img, px(m[:2]), max(4, int(m[2] * sc)), (255, 255, 255), 1)
            put(img, m[3], px((m[0] + 0.5, m[1] + 0.5)), 0.42, (230, 180, 255))
        if 'T' in lt:        # red markers: mast top + rear frame corners
            for fx_, fy_ in ((-TUG['rear'], TUG['half_w']), (-TUG['rear'], -TUG['half_w']), (0.0, 0.0)):
                cv2.circle(img, px((x0 + fx_ * math.cos(yaw) - fy_ * math.sin(yaw), y0 + fx_ * math.sin(yaw) + fy_ * math.cos(yaw))), 4, (0, 0, 255), -1)
        if 'B' in lt and int(r['t'] * 2) % 2 == 0:      # amber beacon, flashing 1 Hz
            cv2.circle(img, px((x0, y0)), 9, (0, 190, 255), -1); cv2.circle(img, px((x0, y0)), 14, (0, 190, 255), 1)
        if not r.get('chain', True): put(img, 'STOP CHAIN OPEN', (cx - 80, cy + 60), 0.6, (0, 0, 255), 2)
        if r.get('xb') and not r.get('seat'): put(img, 'CROSSBEAM CONTACT', (cx - 85, cy + 85), 0.6, (0, 0, 255), 2)
        cv2.circle(img, px((x0 + TUG['lidar_x'] * math.cos(yaw), y0 + TUG['lidar_x'] * math.sin(yaw))), 4, (255, 255, 255), -1)
        cv2.arrowedLine(img, (cx, cy), (cx, cy - 35), (255, 255, 255), 2, tipLength=0.3)
        put(img, '5 m', (470, 528), 0.4); cv2.line(img, (470, 515), (470 + int(5 * sc), 515), (255, 255, 255), 2)
        return img

    def camera(self, r):
        w = self.w; w.x, w.y, w.yaw = r['x'], r['y'], r['yaw']
        if r['bin'] is not None: w.bin = dict(x=r['bin'][0], y=r['bin'][1], yaw=r['bin'][2], state=r['bin'][3], id0=r.get('bin_id', 0))
        w.attached = r['att']
        w.others = [dict(x=lo[0], y=lo[1], yaw=lo[2], state='up', id0=i0) for lo, i0 in zip(r.get('others', []), r.get('others_id') or [10] * 9)]
        img, _ = w.render_cam(seed=int(r['t'] * 10) % 100000, lamp='W' in (r.get('lights') or ''))
        dets = detect(img) if not r['att'] else []
        for q in dets:
            col = (0, 255, 0) if q[0] - q[0] % 4 == r.get('bin_id', 0) or (q[0] >= 30 and r.get('bin_id') == 30) else (0, 0, 255)
            put(img, 'id%d %.1fm' % (q[0], q[1]), (8, 230 - 16 * dets.index(q)), 0.42, col)
        if dets:
            g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            from scene import DET
            corners, ids, _ = DET.detectMarkers(g)
            if ids is not None: cv2.aruco.drawDetectedMarkers(img, corners, ids)
        if r['att']: put(img, 'bin hooked (camera looks at the bin lid)', (8, 120), 0.4, (200, 200, 200))
        put(img, 'rear dock camera %s' % ('NIGHT IR + retro tags' if self.night else 'day'), (6, 14), 0.4, (255, 255, 0))
        return img, dets

    def lidar_scan(self, r):
        w = self.w; w.x, w.y, w.yaw = r['x'], r['y'], r['yaw']; w.attached = r['att']
        if r['bin'] is not None: w.bin = dict(x=r['bin'][0], y=r['bin'][1], yaw=r['bin'][2], state=r['bin'][3])
        w.movers = [dict(kind=m[3], r=m[2], pos=(lambda t, p=(m[0], m[1]): p)) for m in r.get('movers', [])]
        saved = list(w.obst); w.obst = saved + [dict(kind='car', x=v[0], y=v[1], yaw=v[2], L=v[3], W=v[4], H=1.5) for v in (r.get('veh') or [])]
        w.vehicles = []
        out = w.lidar(); w.obst = saved
        return out

    def frame(self, r, factor):
        scan = self.lidar_scan(r)
        out = np.zeros((H, W, 3), np.uint8)
        out[:, :540] = self.chase(r, scan)
        ov = self.ov_bg.copy()
        cv2.circle(ov, self.ov_px((r['x'], r['y'])), 5, (0, 140, 255), -1); cv2.circle(ov, self.ov_px((r['x'], r['y'])), 6, (0, 0, 0), 1)
        out[0:180, 540:960] = ov
        cam, dets = self.camera(r)
        out[182:422, 540:860] = cam
        el = self.el_bg.copy(); s_now, _ = self.S.lane.project(np.array([r['x'], r['y']]))
        zmin, zmax = self.el_z; z = self.S.ter.z(r['x'], r['y'])
        cv2.circle(el, (int(10 + 400 * s_now / self.L), int(100 - 80 * (z - zmin) / (zmax - zmin))), 5, (0, 140, 255), -1)
        out[430:540, 540:960] = el
        # right of camera: status chips
        x = 866
        fx = r['fix']; ch = [('GPS', FIXNAME.get(fx, str(fx)), (0, 255, 0) if fx == 6 else ((0, 200, 255) if fx == 5 else (0, 0, 255))),
              ('LIGHT', ('NIGHT ' + (r.get('lights') or '')) if self.night else 'DAY', (255, 200, 100) if self.night else (0, 255, 255)),
              ('HOOK', 'LATCHED' if r['att'] else ('%.0f deg' % r['hook']), (0, 255, 0) if r['att'] else (255, 255, 255)),
              ('SEAT', 'ON' if r['seat'] else 'off', (0, 255, 0) if r['seat'] else (180, 180, 180)),
              ('CHAIN', 'OK' if r.get('chain', True) else 'OPEN', (0, 255, 0) if r.get('chain', True) else (0, 0, 255)),
              ('XBEAM', 'contact' if r.get('xb') else 'clear', (0, 200, 255) if r.get('xb') else (180, 180, 180))]
        if r.get('soc') is not None: ch.append(('SOC', '%.0f%%%s' % (100 * r['soc'], (' %.0fA' % r['chg']) if r.get('chg') else ''), (0, 255, 0) if r['soc'] > 0.3 else (0, 0, 255)))
        for i, (k_, v_, c_) in enumerate(ch):
            put(out, k_, (x, 197 + 32 * i), 0.38, (200, 200, 200)); put(out, v_, (x, 212 + 32 * i), 0.4, c_)
        # telemetry box on chase view
        box = out[6:186, 6:300].copy(); out[6:186, 6:300] = (box * 0.35).astype(np.uint8)
        b = r['bin']; bs = '-'
        if b is not None:
            sb, lb = self.S.lane.project(np.array(b[:2])); rel = math.degrees(wrap(b[2] - self.S.lane.heading(sb)))
            bs = 's=%.1f lat=%+.1f hdl %+.0f%s' % (sb, lb, rel, ' TIPPED' if b[3] == 'tipped' else '')
        lines = [('MODE  %s' % r['mode'], (0, 255, 255)), ('STATE %s' % r['state'], (255, 255, 0)),
                 ('speed %.2f m/s   hitch %+.0f deg' % (r['v'], r['hitch']), (255, 255, 255)),
                 ('lidar nearest %s' % ('%.2f m' % r['lidar'] if r['lidar'] is not None else '-'), (255, 255, 255)),
                 ('lane s=%.0f m of %.0f   %s' % (s_now, self.L, 'NIGHT' if self.night else 'DAY'), (255, 255, 255)),
                 ('bin %s' % bs, (150, 255, 150)), ('energy %.1f Wh   t=%s' % (r['wh'], self.clock(r['t'])), (255, 255, 255))]
        if r.get('clk') is not None:
            from companion import clock_str
            lines[4] = ('lane s=%.0f m   clock %s   %s' % (s_now, clock_str(r['clk']), 'NIGHT' if self.night else 'DAY'), (255, 255, 255))
        if r.get('slp'): put(out, 'SLEEPING - RTC alarm set (4G/RTK/Pi off)', (60, 300), 0.7, (255, 200, 100), 2)
        if r.get('vstop'): put(out, 'VEHICLE STOP - HOLD + BEACON', (110, 260), 0.7, (0, 220, 255), 2)
        if r.get('aud') in ('announce', 'call', 'ringing'): put(out, {'announce': 'SPEAKER: canned clip', 'call': 'OWNER ON 2-WAY AUDIO', 'ringing': 'owner calling...'}[r['aud']], (110, 235), 0.6, (255, 180, 255), 2)
        if r.get('kl'):
            sl_, ll_ = self.S.lane.project(np.array([r['x'], r['y']])); h_ = self.S.lane.heading(sl_); sg_ = 1 if math.cos(wrap(r['yaw'] - h_)) > 0 else -1
            put(out, 'KEEP LEFT: gap to left edge %.2f m' % (self.S.lane.width / 2 - (sg_ * ll_ + TUG['half_w'])), (300, 470), 0.5, (150, 255, 150))
        for i, (t, col) in enumerate(lines): put(out, t, (12, 26 + 22 * i), 0.47, col)
        if r.get('alert'): put(out, '4G ALERT: ' + r['alert'][:52], (8, 520), 0.47, (0, 0, 255), 1)
        put(out, self.res['title'][:44], (8, 205), 0.5, (255, 255, 255))
        put(out, 'x%d' % factor if factor > 1 else 'x1 real time', (440, 30), 0.7, (0, 255, 255) if factor > 1 else (200, 200, 200), 2)
        return out

    @staticmethod
    def clock(t): return '%d:%02d' % (int(t // 60), int(t % 60))

    def title_card(self, sub, n=22):
        img = np.zeros((H, W, 3), np.uint8); img[:] = (30, 25, 20)
        put(img, self.res['title'], (40, 200), 0.85, (255, 255, 255), 2)
        put(img, 'Real ArduPilot Rover 4.6.2 SITL (JSON backend) on Brian\'s lane - %s' % ('NIGHT' if self.night else 'day'), (40, 245), 0.55, (200, 200, 200))
        for i, l in enumerate(sub): put(img, l, (40, 300 + 32 * i), 0.6, (0, 255, 255) if i == 0 else (220, 220, 220), 1)
        return [img] * n

    def segments(self, target):
        """Choose a time-compression factor per trace sample: cruise (AUTO, nothing happening) vs manoeuvre."""
        T = self.T; dt = np.diff([r['t'] for r in T] + [T[-1]['t'] + 0.1])
        boot = np.array([r['state'] in ('BOOT', 'SLEEP', 'WAKE') or r.get('slp') for r in T])
        cruise = np.array([(r['state'].startswith('AUTO_') and r['state'] not in ('AUTO_DETOUR', 'AUTO_FLOAT_SLOW')) or r['state'] in ('DOCKED', 'RELEASE_HOLD', 'DOCK_HOLD') for r in T])
        tb, tc = dt[boot].sum(), dt[cruise & ~boot].sum(); tm = dt[~cruise & ~boot].sum()
        fm = 2
        avail = target - 2.0 - tm / fm
        while avail < target * 0.35 and fm < 16: fm *= 2; avail = target - 2.0 - tm / fm
        fc = 8
        for f in (8, 16, 32, 64, 128, 256, 512):
            fc = f
            if tc / f <= max(avail, 1): break
        fb = max(32, fc)
        return [(fb if boot[i] else (fc if cruise[i] else fm)) for i in range(len(T))]

    def render(self, target, out_path):
        fac = self.segments(target)
        sub = ['Result: %s - %s' % (self.res['result'].upper(), self.res['outcome'])]
        if self.res['alerts']: sub.append('Alert sent: ' + self.res['alerts'][0]['text'][:80])
        sub.append('sim time %s, energy %.1f Wh' % (self.clock(self.res['sim_time_s']), self.res['energy_wh']))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H), '-r', str(FPS),
                              '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '26', '-pix_fmt', 'yuv420p', out_path], stdin=subprocess.PIPE)
        for f in self.title_card(sub): p.stdin.write(f.tobytes())
        acc = 0.0; n = 0
        for i, r in enumerate(self.T):
            self.trail.append((r['x'], r['y']))
            acc += 0.1 / fac[i]                 # each trace sample is 0.1 s of sim time
            if acc >= 1.0 / FPS or i == len(self.T) - 1:
                acc -= 1.0 / FPS
                p.stdin.write(self.frame(r, fac[i]).tobytes()); n += 1
        last = self.frame(self.T[-1], 1)
        put(last, 'END: %s' % self.res['outcome'][:50], (8, 495), 0.6, (0, 255, 0) if self.res['result'] == 'pass' else (0, 200, 255), 2)
        for k in range(15): p.stdin.write(last.tobytes())
        p.stdin.close(); p.wait()
        return n


if __name__ == '__main__':
    name = sys.argv[1]; target = float(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'out', 'G4', 'clips', name + '.mp4')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    n = Renderer(name).render(target, out)
    print('rendered', name, n, 'frames ->', out)
