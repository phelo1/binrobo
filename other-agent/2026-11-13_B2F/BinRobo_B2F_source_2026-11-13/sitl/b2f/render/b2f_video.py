#!/usr/bin/env python3
"""B2-F SITL scenario videos (post-processing only; reads trace.json / result.json / score.json, never the simulator).
1280x720, 25 fps, libx264 via ffmpeg. Left: robot-centred top-down view (north up) with truth hedge faces, lane, pads, road
boundary, robot footprint, bins, actors, lidar returns. Right: whole-lane minimap + status (mode, EKF / GNSS state, clock, speed,
hedge clearance, SOC, PASS/FAIL). Bottom: fixed caption on every frame.
usage: b2f_video.py scenario <runs_dir> <key> <out.mp4>
       b2f_video.py reel <runs_dir> <out.mp4>"""
import json, math, os, subprocess, sys, bisect
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'scripts_base'))
import b2f_scen as SC
from b2f_world import ROB, BIN_T

W, H, FPS = 1280, 720, 25
CAPTION = 'ArduPilot SITL simulation - not field footage. B2-F provisional pending bin check B0'
FD = '/usr/share/fonts/truetype/dejavu/' if os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf') else '/usr/share/fonts/truetype/'
def font(sz, bold=False, mono=False):
    n = 'DejaVuSansMono%s.ttf' % ('-Bold' if bold else '') if mono else 'DejaVuSans%s.ttf' % ('-Bold' if bold else '')
    for d in (FD, '/usr/share/fonts/truetype/', '/usr/share/fonts/truetype/dejavu/'):
        if os.path.exists(d + n): return ImageFont.truetype(d + n, sz)
    return ImageFont.load_default()
F_CAP, F_T, F_S, F_M, F_BIG = font(17, True), font(20, True), font(15), font(15, mono=True), font(34, True)
S = SC.S; HED = S.hedge_truth; HMID = 0.5 * (HED[:, :2] + HED[:, 2:])
VW, VH = 820, 640; SCALE = 38.0          # local view px, px per m
LANE_PTS = np.array([S.lane.point(q, 0.0) for q in np.arange(0, S.L + 0.5, 0.5)])
LANE_L = np.array([S.lane.point(q, 1.95) for q in np.arange(0, S.L + 0.5, 0.5)]); LANE_R = np.array([S.lane.point(q, -1.95) for q in np.arange(0, S.L + 0.5, 0.5)])
ROAD = np.array(S.road)

def boundary_pts():
    """private boundary = 6.0 m from the road centre-line: sample points near the mouth at that distance."""
    P = []
    for q in np.arange(S.L - 30, S.L + 12, 0.25):
        for l in np.arange(-14, 14.01, 0.25):
            p = S.lane.point(min(q, S.L), l) if q <= S.L else S.lane.point(S.L, l) + (q - S.L) * np.array([math.cos(S.lane.heading(S.L)), math.sin(S.lane.heading(S.L))])
            if abs(S.road_dist(p) - S.boundary) < 0.13: P.append(p)
    return np.array(P) if P else np.zeros((0, 2))
BND = boundary_pts()

STATE_NAMES = {'BOOT': 'boot / EKF init', 'DOCKED': 'docked', 'PIVOT': 'pivot', 'PIVOT_LOADED': 'pivot (loaded)', 'GRAB_APPROACH': 'grab approach',
               'GRAB_DOCK': 'reverse onto bin', 'LIFT': 'lift', 'PLACE': 'placing', 'SETDOWN': 'set-down', 'WITHDRAW': 'withdraw',
               'VERIFY': 'lidar bin check', 'DOCKING': 'docking', 'CRASHED': 'Pi frozen (injected)', 'BYPASS': 'Pi fence check bypassed'}


def rect(cx, cy, yaw, x0, x1, hw):
    c, s = math.cos(yaw), math.sin(yaw)
    return [(cx + a * c - b * s, cy + a * s + b * c) for a, b in ((x0, -hw), (x1, -hw), (x1, hw), (x0, hw))]


class Clip:
    def __init__(self, runs, key):
        self.key = key; d = os.path.join(runs, key)
        self.res = json.load(open(os.path.join(d, 'result.json'))); tr = json.load(open(os.path.join(d, 'trace.json')))
        self.T = tr['trace']; self.meta = tr['meta']; self.tt = [x['t'] for x in self.T]
        sc = json.load(open(os.path.join(os.path.dirname(runs.rstrip('/')), 'score.json'))) if os.path.exists(os.path.join(os.path.dirname(runs.rstrip('/')), 'score.json')) else []
        row = [q for q in sc if q['key'] == key]; self.score = row[0] if row else None
        self.verdict = self.score['verdict'] if self.score else '?'
        self.mini_bg, self.mini_tf = self.minimap_bg()

    def at(self, t):
        i = bisect.bisect_left(self.tt, t); i = min(max(i, 0), len(self.T) - 1); return self.T[i]

    def minimap_bg(self):
        mw, mh = 440, 260; pts = np.r_[LANE_PTS, ROAD]; lo = pts.min(0) - 8; hi = pts.max(0) + 8
        k = min(mw / (hi[0] - lo[0]), mh / (hi[1] - lo[1]))
        def tf(p): return (10 + (p[0] - lo[0]) * k, 10 + mh - (p[1] - lo[1]) * k)
        im = Image.new('RGB', (mw + 20, mh + 20), (22, 26, 30)); dr = ImageDraw.Draw(im)
        dr.line([tf(p) for p in ROAD], fill=(90, 90, 96), width=5)
        dr.line([tf(p) for p in LANE_PTS], fill=(150, 140, 110), width=3)
        for kk, pd in SC.PADS.items():
            p = S.lane.point(pd['s'], pd['lat']); q = tf(p); dr.ellipse([q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3], fill=(240, 200, 60))
        q = tf(S.lane.point(SC.DOCK['s'], 0.0)); dr.rectangle([q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3], fill=(90, 200, 255))
        dr.text(tf(S.lane.point(0, 0)), ' house', fill=(180, 180, 180), font=F_S); dr.text(tf(S.lane.point(S.L, 0)), ' road', fill=(180, 180, 180), font=F_S)
        return im, tf

    # -------------------------------------------------------------- frame
    def frame(self, t, title=None):
        x = self.at(t); im = Image.new('RGB', (W, H), (16, 18, 20)); dr = ImageDraw.Draw(im)
        cx, cy = x['x'], x['y']
        def P(px, py): return (VW / 2 + (px - cx) * SCALE, VH / 2 - (py - cy) * SCALE)
        # ground / lane band
        dr.rectangle([0, 0, VW, VH], fill=(34, 44, 30))
        i0 = max(0, int((x['s'] - 20) / 0.5)); i1 = min(len(LANE_PTS), int((x['s'] + 20) / 0.5) + 1)
        if i1 - i0 > 1:
            poly = [P(*p) for p in LANE_L[i0:i1]] + [P(*p) for p in LANE_R[i0:i1][::-1]]
            dr.polygon(poly, fill=(92, 84, 70))
            dr.line([P(*p) for p in LANE_PTS[i0:i1]], fill=(120, 110, 92), width=1)
        if x['s'] > S.L - 30:
            dr.line([P(*p) for p in ROAD], fill=(70, 70, 76), width=int(6.5 * SCALE))
            dr.line([P(*p) for p in ROAD], fill=(220, 220, 220), width=2)
            lab = None
            for p in BND[::2]:
                q = P(*p)
                if 0 <= q[0] <= VW and 0 <= q[1] <= VH:
                    dr.ellipse([q[0] - 1.6, q[1] - 1.6, q[0] + 1.6, q[1] + 1.6], fill=(255, 90, 200)); lab = lab or q
            if lab: dr.text((lab[0] + 6, lab[1] - 18), 'private boundary (fence C4)', fill=(255, 90, 200), font=F_S)
        # pads + home spots
        for kk, pd in self.res_pads().items():
            p = S.lane.point(pd['s'], pd['lat']); h = S.lane.heading(pd['s']); q = P(*p)
            if -50 < q[0] < VW + 50 and -50 < q[1] < VH + 50:
                dr.polygon([P(*v) for v in rect(p[0], p[1], h, -0.42, 0.42, 0.34)], outline=(240, 200, 60))
                dr.text((q[0] + 14, q[1] - 8), 'pad ' + kk, fill=(240, 200, 60), font=F_S)
        # hedges (truth faces)
        near = HED[np.linalg.norm(HMID - np.array([cx, cy]), axis=1) < 16]
        for sgm in near: dr.line([P(sgm[0], sgm[1]), P(sgm[2], sgm[3])], fill=(60, 190, 70), width=4)
        # standing bins, obstacles, cars, movers
        for name, b in (x.get('bins') or {}).items():
            bx, by, byaw, st, size = b
            if st in ('gone', 'carried'): continue
            T = BIN_T[size]
            if st == 'tipped': poly = rect(bx, by, byaw, -T['H'] / 2, T['H'] / 2, T['W'] / 2)
            else: poly = rect(bx, by, byaw, -T['D'] / 2, T['D'] / 2, T['W'] / 2)
            dr.polygon([P(*v) for v in poly], fill=(60, 60, 64) if name == 'black' else ((50, 120, 60) if name == 'green' else (120, 80, 40)), outline=(230, 230, 230))
        for o in x.get('obst') or []:
            dr.polygon([P(*v) for v in rect(o[0], o[1], o[2], -o[3] / 2, o[3] / 2, o[4] / 2)], fill=(150, 130, 90), outline=(255, 255, 255))
        for c in x.get('cars') or []:
            dr.polygon([P(*v) for v in rect(c[0], c[1], c[2], -c[3] / 2, c[3] / 2, c[4] / 2)], fill=(70, 90, 160), outline=(255, 255, 255))
        for mx, my, r, kind in x.get('mv') or []:
            q = P(mx, my); rr = r * SCALE
            dr.ellipse([q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr], fill=(230, 120, 40) if kind == 'person' else (200, 170, 60), outline=(255, 255, 255))
            dr.text((q[0] + rr + 3, q[1] - 8), kind, fill=(255, 255, 255), font=F_S)
        # lidar returns
        if x.get('lid'):
            lx = cx + ROB['lidar_x'] * math.cos(x['yaw']); ly = cy + ROB['lidar_x'] * math.sin(x['yaw'])
            for k, r in enumerate(x['lid']):
                if r is None: continue
                a = x['yaw'] + math.radians(3 * k); q = P(lx + r * math.cos(a), ly + r * math.sin(a))
                dr.ellipse([q[0] - 2, q[1] - 2, q[0] + 2, q[1] + 2], fill=(255, 60, 60))
        # robot + carried bin
        fp = rect(cx, cy, x['yaw'], ROB['x0'], ROB['x1'], ROB['hw'])
        dr.polygon([P(*v) for v in fp], fill=(200, 205, 215), outline=(20, 20, 20))
        nose = (cx + ROB['x1'] * math.cos(x['yaw']), cy + ROB['x1'] * math.sin(x['yaw']))
        dr.line([P(cx, cy), P(*nose)], fill=(220, 40, 40), width=3)
        if x.get('cb'):
            bx, by, byaw = x['cb']; size = (x.get('bins') or {}).get(x.get('carry'), [0, 0, 0, '', '240'])[4]; T = BIN_T[size]
            dr.polygon([P(*v) for v in rect(bx, by, byaw, -T['D'] / 2, T['D'] / 2, T['W'] / 2)], fill=(45, 45, 50), outline=(255, 210, 0))
        if x.get('ekf'):
            q = P(*x['ekf']); dr.line([q[0] - 6, q[1], q[0] + 6, q[1]], fill=(0, 220, 255), width=2); dr.line([q[0], q[1] - 6, q[0], q[1] + 6], fill=(0, 220, 255), width=2)
        # scale bar + legend
        dr.line([20, VH - 22, 20 + 2 * SCALE, VH - 22], fill=(255, 255, 255), width=3); dr.text((22, VH - 44), '2 m', fill=(255, 255, 255), font=F_S)
        dr.text((110, VH - 44), 'green: truth hedge face   red: lidar returns   cyan +: EKF position   pink: legal boundary   N up', fill=(220, 220, 220), font=F_S)
        # ---------------- right panel
        dr.rectangle([VW, 0, W, VH], fill=(22, 26, 30))
        im.paste(self.mini_bg, (VW + 0, 54))
        q = self.mini_tf((cx, cy)); q = (q[0] + VW, q[1] + 54); dr.ellipse([q[0] - 5, q[1] - 5, q[0] + 5, q[1] + 5], fill=(255, 60, 60), outline=(255, 255, 255))
        ttl = '%s  seed %d' % (self.res['scenario'], self.res['seed'])
        dr.text((VW + 12, 8), ttl, fill=(255, 255, 255), font=F_T)
        tt_ = self.res['title']
        while dr.textlength(tt_, font=F_S) > W - VW - 150 and len(tt_) > 10: tt_ = tt_[:-2]
        if tt_ != self.res['title']: tt_ = tt_.rstrip() + '...'
        dr.text((VW + 12, 32), tt_, fill=(200, 200, 200), font=F_S)
        fixn = {6: 'RTK fixed', 5: 'RTK float', 1: 'no fix'}.get(x.get('rq') and {'rtk': 6, 'wrongfix': 6, 'float': 5, 'none': 1}[x['rq']], '?')
        rawq = {'rtk': 'RTK fixed', 'wrongfix': 'RTK fixed*', 'float': 'RTK float', 'none': 'NO FIX'}.get(x.get('rq'), '?')
        sent = 'GPS_INPUT fix' if x.get('fix') == 6 else ('GPS_INPUT none' if x.get('fix') == 1 else 'GPS_INPUT %s' % x.get('fix'))
        ekf_err = math.hypot(x['ekf'][0] - cx, x['ekf'][1] - cy) if x.get('ekf') else None
        st = x.get('state') or ''
        lines = [('Mode (ArduPilot)', x.get('mode')), ('Pi state', STATE_NAMES.get(st, st.replace('_', ' ').lower())),
                 ('Clock', x.get('clk') or 'scenario t+%.0f s' % t), ('Sim time', '%.1f s' % t),
                 ('Receiver', rawq), ('Pi -> EKF', sent + (' (dead reckoning)' if x.get('rq') == 'none' and x.get('fix') == 6 else '')),
                 ('EKF pos error', '%.2f m (truth)' % ekf_err if ekf_err is not None else '-'),
                 ('Speed', '%.2f m/s (cmd %.2f)' % (x['v'], x.get('spd') or 0)), ('Station s', '%.1f m  lat %+.2f m' % (x['s'], x['lat'])),
                 ('Hedge clr min', '%.3f m (run so far)' % x['hc'] if x.get('hc') is not None and x['hc'] < 9 else '-'),
                 ('Battery', 'SOC %.1f %%  used %.1f Wh' % (100 * x['soc'], x['wh'])), ('Carrying', x.get('carry') or '-')]
        yy = 54 + 285
        for a, b in lines:
            dr.text((VW + 12, yy), a, fill=(150, 160, 170), font=F_S); dr.text((VW + 150, yy), str(b)[:36], fill=(240, 240, 240), font=F_M); yy += 20
        if x.get('alert'):
            dr.rectangle([VW + 6, VH - 30, W - 6, VH - 4], fill=(120, 30, 30)); dr.text((VW + 12, VH - 27), ('ALERT: ' + x['alert'])[:60], fill=(255, 255, 255), font=F_S)
        # verdict badge
        col = (30, 150, 60) if self.verdict == 'PASS' else ((180, 40, 40) if self.verdict == 'FAIL' else (90, 90, 90))
        dr.rectangle([W - 128, 6, W - 8, 46], fill=col); dr.text((W - 116, 9), self.verdict, fill=(255, 255, 255), font=F_BIG if len(self.verdict) <= 4 else F_T)
        if title:
            tw = dr.textlength(title, font=F_T); dr.rectangle([8, 8, 20 + tw, 38], fill=(0, 0, 0)); dr.text((14, 11), title, fill=(255, 230, 120), font=F_T)
        # caption bar (every frame)
        dr.rectangle([0, VH, W, H], fill=(0, 0, 0))
        tw = dr.textlength(CAPTION, font=F_CAP); dr.text(((W - tw) / 2, VH + 12), CAPTION, fill=(255, 215, 0), font=F_CAP)
        sub = 'Truth view of the digital-twin lane; robot driven by ArduPilot Rover 4.6.2 SITL + companion (Pi) code. Strict score vs frozen criteria.'
        tw = dr.textlength(sub, font=F_S); dr.text(((W - tw) / 2, VH + 46), sub, fill=(170, 170, 170), font=F_S)
        return im

    def res_pads(self):
        return SC.PADS


def schedule(clip, t0=None, t1=None, fast=8.0, slow=2.0, max_frames=1900):
    """frame times: slow (x4) during manoeuvres / events, fast during lane legs, boot, waits. Scaled to <= max_frames."""
    T = clip.T; t0 = T[0]['t'] if t0 is None else t0; t1 = T[-1]['t'] if t1 is None else t1
    def sp(x):
        st = x['state'] or ''
        if st == 'BOOT': return max(fast, 25.0)
        if st.startswith('LANE') or st in ('BOOT', 'DOCKED', 'LIFT', 'SETDOWN'):
            return fast if abs(x['v']) > 0.05 or st in ('BOOT', 'DOCKED', 'LIFT', 'SETDOWN') else fast / 2
        return slow
    for _ in range(20):
        ts = []; t = t0
        while t <= t1: ts.append(t); t += sp(clip.at(t)) / FPS
        if len(ts) < 250: return list(np.linspace(t0, t1, 250))     # short runs: at least 10 s of video
        if len(ts) <= max_frames: return ts
        fast *= 1.35; slow *= 1.2
    return ts[:max_frames]


def encode(frames_iter, out):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24', '-pix_fmt', 'yuv420p', '-r', str(FPS), out], stdin=subprocess.PIPE)
    n = 0
    for im in frames_iter: p.stdin.write(im.tobytes()); n += 1
    p.stdin.close(); p.wait(); return n


def scenario_video(runs, key, out, part=None, nparts=1):
    c = Clip(runs, key); ts = schedule(c)
    if part is not None:     # chunked rendering (shell time limit): frames [part] of nparts -> out.partK.mp4
        k = len(ts); a = k * part // nparts; b = k * (part + 1) // nparts; ts = ts[a:b]
    def gen():
        for t in ts: yield c.frame(t)
        if part is None or part == nparts - 1:
            last = c.frame(c.T[-1]['t'])
            for _ in range(3 * FPS): yield last          # 3 s hold on the final state (outcome / alert banner)
    n = encode(gen(), out); return n


REEL = [  # (key, t-window start offset label, title) - windows found from the event times in the trace
    ('s1a__s7', 'grab', 'One-bin drop: grab at home, lift'),
    ('s1a__s7', 'lane', 'Loaded run down the lane (keep-left on the hedge face)'),
    ('s1a__s7', 'place', 'Set-down at pad A (tightest spot)'),
    ('s5a__s7', 'stop', 'Lidar: person crossing ahead - slow to 0.25 m/s'),
    ('s5b__s7', 'wait', 'Car in the bell-mouth - wait, then place'),
    ('s4b__s7', 'nofix', 'RTK loss under the hedge - odometry bridge'),
    ('s6a__s7', 'crash', 'Companion freeze - firmware HOLD'),
    ('s12b__s7', 'fence', 'Pi fence check bypassed - firmware fence HOLD'),
    ('s10a__s7', 'verify', 'Tipped bin - lidar check, no grab'),
    ('s3a__s7', 'end', 'FAIL: 140 L from the far home spot - hedge at s 25.7, fence HOLD'),
]


def reel_window(c, tag):
    T = c.T
    def first(pred):
        for x in T:
            if pred(x): return x['t']
        return T[0]['t']
    if tag == 'grab': t = first(lambda x: x['state'] == 'GRAB_DOCK'); return t - 4, t + 50, 6.0
    if tag == 'lane': t = first(lambda x: x['state'] == 'LANE_DOWN_LOADED' and x['s'] > 260); return t, t + 120, 15.0
    if tag == 'place': t = first(lambda x: x['state'] == 'PLACE'); return t - 5, t + 70, 8.0
    if tag == 'stop': t = first(lambda x: x['mv'] and any(m[3] == 'person' for m in x['mv'])); return t - 3, t + 20, 2.5
    if tag == 'wait': t = first(lambda x: x['cars'] and x['s'] > 612); return t - 3, t + 90, 10.0
    if tag == 'nofix': t = first(lambda x: x['rq'] == 'none'); return t - 5, t + 50, 6.0
    if tag == 'crash': t = first(lambda x: x['state'] == 'CRASHED'); return t - 6, t + 10, 1.2
    if tag == 'fence': t = first(lambda x: x['mode'] == 'HOLD' and x['t'] > 50); return t - 25, t + 6, 2.5
    if tag == 'verify': t = first(lambda x: x['state'] == 'VERIFY'); return t - 20, t + 25, 3.5
    if tag == 'end': return T[-1]['t'] - 40, T[-1]['t'], 4.5
    return T[0]['t'], T[-1]['t'], 20.0


def reel_frames(runs, items):
    for key, tag, title in items:
        c = Clip(runs, key); a, b, spd = reel_window(c, tag)
        a = max(a, c.T[0]['t']); b = min(b, c.T[-1]['t']); t = a; n = 0
        while t <= b and n < 9 * FPS: yield c.frame(t, title=title); t += spd / FPS; n += 1


if __name__ == '__main__':
    if sys.argv[1] == 'scenario':
        part = int(sys.argv[5]) if len(sys.argv) > 5 else None; nparts = int(sys.argv[6]) if len(sys.argv) > 6 else 1
        print('frames', scenario_video(sys.argv[2], sys.argv[3], sys.argv[4], part, nparts))
    elif sys.argv[1] == 'frames':     # count frames only
        c = Clip(sys.argv[2], sys.argv[3]); print(len(schedule(c)))
    elif sys.argv[1] == 'still':      # one PNG at time t
        c = Clip(sys.argv[2], sys.argv[3]); c.frame(float(sys.argv[4])).save(sys.argv[5])
    elif sys.argv[1] == 'reel':
        a = int(sys.argv[4]) if len(sys.argv) > 4 else 0; b = int(sys.argv[5]) if len(sys.argv) > 5 else len(REEL)
        print('frames', encode(reel_frames(sys.argv[2], REEL[a:b]), sys.argv[3]))
