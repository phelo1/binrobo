#!/usr/bin/env python3
"""Lane-physics video renderer (software rasteriser work/revB2F/raster.py, no OpenGL). B2-F CAD meshes posed from the recorded
MuJoCo body poses (scene.py), lane environment from lane_world.py, PIL HUD + inset lane map, ffmpeg H.264 1280x720 25 fps.
Chunked: render_lane.py <video> [budget_s]  -> renders the next block of frames into segments seg_NNN.mp4; re-call until DONE,
then render_lane.py <video> --final  (concat + caption check). Videos are defined in VIDEOS (shots = run, sim t0..t1, speed, camera)."""
import os, sys, json, math, time, glob, subprocess, pickle, numpy as np
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); P = '/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c'
sys.path.insert(0, HERE); sys.path.insert(0, P + '/work/revB2F')
import lane_world as LW
import scene as SC, raster as RA
from PIL import Image, ImageDraw, ImageFont
OUT = '/workspace/work/out/b2f_lane/phys'; os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1280, 720, 25
RS = 0.75   # 3D raster scale (upscaled to 1280x720 with Lanczos; HUD/caption drawn at full resolution)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; FONTB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FONTM = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
F = lambda n, b=False: ImageFont.truetype(FONTB if b else FONT, n); FM = lambda n: ImageFont.truetype(FONTM, n)
CAPTION = 'Digital twin simulation - not field footage. B2-F provisional pending bin check B0'
HUDN = ['s', 'lat', 'grade', 'v', 'liftF', 'clear', 'hedge', 'tip', 'Wh', 'leaf', 'roll', 'pitch', 'binkg', 'carry', 'gap']

# ------------------------------------------------------------------ data
class Rec:
    def __init__(R, rid):
        R.rid = rid; d = os.path.join(HERE, 'runs', rid); fs = sorted(glob.glob(os.path.join(d, 'rec_*.npz')))
        T, Q, Hh, O, PH = [], [], [], [], []
        for f in fs:
            r = np.load(f); T.append(r['t']); Q.append(r['q']); Hh.append(r['hud']); O.append(r['ob']); PH += list(r['ph'])
        R.t = np.concatenate(T); R.q = np.concatenate(Q); R.h = np.concatenate(Hh); R.ob = np.concatenate(O); R.ph = PH
        R.res = json.load(open(os.path.join(d, 'result.json'))); R.cfg = R.res['cfg']
        # running criteria state (for the live status light)
        car = R.h[:, 13] > 0.5
        R.bad = np.zeros(len(R.t), bool)
        R.warn = car & (R.h[:, 5] < 0.030); R.bad |= R.h[:, 6] < 0.0; R.bad |= R.h[:, 7] < 0.0; R.bad |= R.h[:, 14] <= 0.0
        R.badcum = np.maximum.accumulate(R.bad)
    def idx(R, t): return int(np.clip(np.searchsorted(R.t, t), 0, len(R.t) - 1))
_REC = {}
def rec(rid):
    if rid not in _REC: _REC[rid] = Rec(rid)
    return _REC[rid]

# ------------------------------------------------------------------ static environment geometry near s
COL = dict(tar=np.array([0.36, 0.37, 0.39]), tar2=np.array([0.40, 0.41, 0.43]), verge=np.array([0.36, 0.52, 0.26]), verge2=np.array([0.33, 0.48, 0.24]),
           leaf=np.array([0.55, 0.37, 0.16]), hedge=np.array([0.17, 0.36, 0.15]), hedge2=np.array([0.20, 0.42, 0.17]), tile=np.array([0.42, 0.42, 0.40]),
           padA=np.array([0.95, 0.80, 0.15]), home=np.array([0.25, 0.55, 0.95]), road=np.array([0.25, 0.25, 0.27]), dark=np.array([0.12, 0.12, 0.12]))
def env_mesh(s_c, variant, back=12.0, fwd=26.0, dirn=1, ds=0.5, cut=0):
    """terrain strip, hedges, feature tiles, pads around chainage s_c (camera looks toward dirn)"""
    T, C = [], []
    s0, s1 = (s_c - back, s_c + fwd) if dirn > 0 else (s_c - fwd, s_c + back)
    s0 = max(s0, -6.0); s1 = min(s1, LW.LEN + 14.0)
    ss = np.arange(math.floor(s0 / ds) * ds, s1 + 1e-6, ds)
    lats = np.array([-7.0, -5.0, -3.5, -2.6, -1.8, -0.9, 0.0, 0.9, 1.8, 2.6, 3.5, 5.0, 7.0])
    def pt(s, l):
        sc = min(max(s, 0.0), LW.LEN); p = LW.point(sc, l)
        if s < 0 or s > LW.LEN:   # straight extension beyond the ends
            h = LW.heading(sc); p = p + (s - sc) * np.array([math.cos(h), math.sin(h)])
        z = float(LW.zprof(sc))
        for k, (a, b) in LW.BED.items():
            if a + 0.3 <= sc <= b - 0.3 and abs(l) <= 3.0: z -= 0.15
        return np.array([p[0], p[1], z])
    G = np.array([[pt(s, l) for l in lats] for s in ss])
    for i in range(len(ss) - 1):
        sm = 0.5 * (ss[i] + ss[i + 1]); leaf = LW.leaf_at(sm); mouth = sm > LW.MOUTH0; yard = sm < LW.YARD_END
        for j in range(len(lats) - 1):
            lm = 0.5 * (lats[j] + lats[j + 1]); a, b, c, d = G[i, j], G[i + 1, j], G[i + 1, j + 1], G[i, j + 1]
            surf = abs(lm) < 1.8 or (mouth and abs(lm) < 4.5) or (yard and abs(lm) < 5.0) or sm > LW.LEN
            if sm > LW.LEN + 0.5 and abs(lm) < 7: col = COL['road']
            elif surf: col = COL['leaf'] if (leaf and abs(lm) < 1.8) else (COL['tar'] if (i + j) % 2 else COL['tar2'])
            else: col = COL['verge'] if (i + j) % 2 else COL['verge2']
            T += [[a, b, c], [a, c, d]]; C += [col, col]
    # feature tiles (as in physics)
    for name, c, R, hs in LW.tiles(variant):
        sc_, _ = LW.project(c[:2][None])
        if not (s0 - 2 <= sc_[0] <= s1 + 2): continue
        hx, hy, hz = hs; v = np.array([[x, y, z] for x in (-hx, hx) for y in (-hy, hy) for z in (-hz, hz)]) @ R.T + c
        col = COL['dark'] if ('Bot' in name) else (np.array([0.62, 0.55, 0.30]) if 'Ramp' in name else COL['tile'])
        for f in [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]:
            q = v[list(f)]; T += [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]; C += [col, col]
    # hedges: 1 m boxes, face at the truth line
    for k in range(int(math.floor(s0)), int(math.ceil(s1))):
        sm = k + 0.5
        for side in (1, -1):
            f = LW.hedge_face(sm, side)
            if f is None or side == cut: continue   # cut: near-side hedge removed for side-camera views
            h = LW.seg_heading(sm); hgt = 1.7 + 0.25 * math.sin(sm * 1.7 + side) + 0.1 * math.sin(sm * 5.1)
            z0 = float(LW.zprof(sm)) - 0.2; t_ = np.array([math.cos(h), math.sin(h), 0]); n_ = np.array([-math.sin(h), math.cos(h), 0])
            c2 = LW.point(sm, side * (f + 0.45), h=h); ctr = np.array([c2[0], c2[1], z0 + hgt / 2])
            v = np.array([ctr + t_ * x + n_ * y + np.array([0, 0, z]) for x in (-0.52, 0.52) for y in (-0.45, 0.45) for z in (-hgt / 2, hgt / 2)])
            col = COL['hedge'] if k % 2 else COL['hedge2']
            for fc in [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]:
                q = v[list(fc)]; T += [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]; C += [col, col]
    # pads (outline strips 4 cm above the surface)
    for spot, col, (ls, ll) in ((LW.PAD_A, COL['padA'], (1.2, 0.9)), (LW.HOME, COL['home'], (1.2, 0.9))):
        if not (s0 - 3 <= spot['s'] <= s1 + 3): continue
        for (sa, la, sb, lb) in ((-ls, -ll, ls, -ll), (-ls, ll, ls, ll), (-ls, -ll, -ls, ll), (ls, -ll, ls, ll)):
            for w in (0.04,):
                pa = pt(spot['s'] + sa, spot['lat'] + la); pb = pt(spot['s'] + sb, spot['lat'] + lb); e = pb - pa; n = np.array([-e[1], e[0], 0]); n = n / (np.linalg.norm(n) + 1e-9) * w
                a, b, c, d = pa - n, pb - n, pb + n, pa + n
                for q in (a, b, c, d): q[2] += 0.012
                T += [[a, b, c], [a, c, d]]; C += [col, col]
    return np.array(T), np.array(C)
_ENV = {}
def env_cached(s_c, variant, dirn, cut=0):
    key = (round(s_c / 2.0), dirn, json.dumps(variant, sort_keys=True), cut)
    if key not in _ENV:
        if len(_ENV) > 6: _ENV.clear()
        _ENV[key] = env_mesh(key[0] * 2.0, variant, dirn=dirn, cut=cut)
    return _ENV[key]

# ------------------------------------------------------------------ robot + bin meshes
_BINSCALE = None
def robot_mesh(q, with_bin, binkey):
    Pz = SC.frame_poses(np.nan_to_num(q))
    if not with_bin: Pz = {k: v for k, v in Pz.items()}
    tris, cols, oid = SC.posed(Pz, with_bin=with_bin)
    if with_bin and binkey == 'WEB140':   # 140 L drawn as the 240 L CAD bin scaled to the Weber 140 envelope (D 545, W 475, H ~ -6 %)
        g = SC.posed.groups; m = np.isin(g, ['bin', 'bw', 'lid'])
        Rb, pb = Pz['bin']; L_ = (tris[m] - pb) @ Rb; L_ *= np.array([0.545 / 0.737, 0.475 / 0.583, 0.94]); tris[m] = L_ @ Rb.T + pb
    return tris, cols, oid
def obstacle_mesh(p, kind):
    if not np.isfinite(p).all(): return None
    if kind == 'person':
        parts = [((0, 0, 0.45), (0.13, 0.2, 0.45), (0.2, 0.25, 0.45)), ((0, 0, 1.2), (0.14, 0.24, 0.32), (0.8, 0.2, 0.15)), ((0, 0, 1.62), (0.1, 0.1, 0.11), (0.9, 0.75, 0.6))]
    else:
        parts = [((0, 0, 0.32), (0.38, 0.13, 0.13), (0.55, 0.38, 0.2)), ((0.36, 0, 0.47), (0.1, 0.08, 0.09), (0.5, 0.33, 0.18)), ((-0.25, 0.08, 0.12), (0.03, 0.03, 0.12), (0.5, 0.33, 0.18)),
                 ((0.25, 0.08, 0.12), (0.03, 0.03, 0.12), (0.5, 0.33, 0.18)), ((-0.25, -0.08, 0.12), (0.03, 0.03, 0.12), (0.5, 0.33, 0.18)), ((0.25, -0.08, 0.12), (0.03, 0.03, 0.12), (0.5, 0.33, 0.18))]
    T, C = [], []
    for c, h, col in parts:
        if kind == 'dog':   # dog runs across the lane: body along the lateral axis
            s_, _ = LW.project(p[None, :2]); hd = LW.heading(float(s_[0])) + math.pi / 2
            Rz = np.array([[math.cos(hd), -math.sin(hd), 0], [math.sin(hd), math.cos(hd), 0], [0, 0, 1]])
        else: Rz = np.eye(3)
        v = np.array([[x, y, z] for x in (-h[0], h[0]) for y in (-h[1], h[1]) for z in (-h[2], h[2])]) @ Rz.T + Rz @ np.array(c) + p
        for f in [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]:
            qq = v[list(f)]; T += [[qq[0], qq[1], qq[2]], [qq[0], qq[2], qq[3]]]; C += [np.array(col), np.array(col)]
    return np.array(T), np.array(C)

# ------------------------------------------------------------------ inset map
def build_map(w=230, h=420):
    pad = 14; x0, x1 = LW.CX.min(), LW.CX.max(); y0, y1 = LW.CY.min(), LW.CY.max()
    k = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0)); ox = (w - k * (x1 - x0)) / 2; oy = (h - k * (y1 - y0)) / 2
    tf = lambda x, y: (ox + k * (x - x0), h - (oy + k * (y - y0)))
    im = Image.new('RGBA', (w, h), (255, 255, 255, 215)); dr = ImageDraw.Draw(im)
    pts = [tf(x, y) for x, y in zip(LW.CX[::40], LW.CY[::40])]; dr.line(pts, fill=(70, 75, 85), width=5)
    for a, b in LW.LEAVES:
        m = (LW.DS >= a) & (LW.DS <= b); dr.line([tf(x, y) for x, y in zip(LW.CX[m][::20], LW.CY[m][::20])], fill=(170, 110, 40), width=7)
    m = (LW.DS >= LW.G12[0]) & (LW.DS <= LW.G12[1]); dr.line([tf(x, y) for x, y in zip(LW.CX[m][::10], LW.CY[m][::10])], fill=(200, 40, 40), width=3)
    for nm, f in LW.FEAT.items():
        p = tf(*LW.point(f['s'])); dr.rectangle([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(40, 40, 40))
    for spot, col, lab in ((LW.HOME, (60, 130, 240), 'home'), (LW.PAD_A, (230, 180, 20), 'pad A')):
        p = tf(*LW.point(spot['s'], spot['lat'])); dr.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=col, outline=(0, 0, 0))
        dr.text((p[0] + 9, p[1] - 8), lab, font=F(13, True), fill=(20, 20, 20))
    dr.text((8, 4), 'Lane 633 m (OSM)', font=F(13, True), fill=(20, 20, 20))
    dr.text((8, h - 52), 'leaves', font=F(12), fill=(170, 110, 40)); dr.text((8, h - 36), '12 % pitch', font=F(12), fill=(200, 40, 40)); dr.text((8, h - 20), 'step / trench / pothole', font=F(12), fill=(40, 40, 40))
    dr.rectangle([0, 0, w - 1, h - 1], outline=(120, 120, 120))
    return im, tf
MAP, MAPTF = build_map()

# ------------------------------------------------------------------ frame
def camera(q, s, dirn, mode):
    p = q[0, :3].astype(float); w, x, y, z = q[0, 3:]; yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    if mode == 'chase':
        h = LW.heading(min(max(s, 4), LW.LEN - 4)) + (0 if dirn > 0 else math.pi)
        d = np.array([math.cos(h), math.sin(h), 0.0]); n = np.array([-d[1], d[0], 0])
        eye = p - 5.2 * d + 0.9 * n + np.array([0, 0, 2.7]); tgt = p + 2.2 * d + np.array([0, 0, 0.45]); fov = 52
    elif mode == 'orbit':      # 3/4 rear-left of the robot (sees the comb/receiver and the bin)
        c, s_ = math.cos(yaw), math.sin(yaw); off = np.array([-2.8, 2.9, 1.9]); eye = p + np.array([c * off[0] - s_ * off[1], s_ * off[0] + c * off[1], off[2]]); tgt = p + np.array([0, 0, 0.55]); fov = 45
    elif mode == 'side':       # side view, robot's left (step / pothole crossings)
        c, s_ = math.cos(yaw), math.sin(yaw); off = np.array([0.6, 4.6, 1.0]); eye = p + np.array([c * off[0] - s_ * off[1], s_ * off[0] + c * off[1], off[2]]); tgt = p + np.array([0.3 * c, 0.3 * s_, 0.45]); fov = 42
    return eye, tgt, fov
def draw_hud(img, R, i, shot, vid, night):
    dr = ImageDraw.Draw(img, 'RGBA'); h = R.h[i]; t = float(R.t[i])
    # top banner: caption watermark + title
    dr.rectangle([0, 0, W, 34], fill=(10, 14, 22, 200)); dr.text((12, 7), CAPTION, font=F(17, True), fill=(255, 210, 80))
    tt = 'SCENARIO  ' + (shot.get('label') or R.res['title']); tt = tt if len(tt) < 100 else tt[:97] + '...'
    dr.rounded_rectangle([8, 64, 16 + dr.textlength(tt, font=F(16, True)), 90], 6, fill=(10, 14, 22, 190)); dr.text((12, 67), tt, font=F(16, True), fill=(255, 255, 255))
    # phase line
    ph = R.ph[i] if i < len(R.ph) else ''; ph = ph if len(ph) < 110 else ph[:107] + '...'
    sp = shot.get('speed', 1.0); tl = ('TIME-LAPSE x%g' % sp) if sp > 1.01 else ('real time' if sp > 0.99 else 'slow motion x%g' % sp)
    dr.rectangle([0, 34, W, 60], fill=(10, 14, 22, 150)); dr.text((12, 38), ph, font=F(15), fill=(220, 225, 230))
    dr.text((W - 12 - dr.textlength(tl, font=F(16, True)), 37), tl, font=F(16, True), fill=(120, 220, 255) if sp > 1.01 else (200, 255, 200))
    # bottom HUD panel
    y0 = H - 112; dr.rectangle([0, y0, W, H], fill=(10, 14, 22, 205))
    carry = h[13] > 0.5; clr = h[5]
    cells = [('CHAINAGE', '%.1f m' % h[0]), ('GRADE', '%+.1f %%' % (h[2])), ('SPEED', '%.2f m/s' % abs(h[3])), ('BIN MASS', ('%.0f kg' % h[12]) if h[12] > 0 else 'no bin'),
             ('LIFT ACTUATOR', '%.0f N' % h[4]), ('BIN-WHEEL CLEAR', ('%.0f mm' % (1000 * clr)) if (np.isfinite(clr) and h[12] > 0) else '-'),
             ('HEDGE CLEAR', ('%.2f m' % h[6]) if h[6] < 8 else 'no hedge'), ('TIP MARGIN', '%.1f deg' % h[7]), ('ENERGY', '%.1f Wh' % h[8]), ('SIM TIME', '%d:%04.1f' % (t // 60, t % 60))]
    cw = (W - 24) / 5
    for k, (lab, val) in enumerate(cells):
        cx = 12 + (k % 5) * cw; cy = y0 + 8 + (k // 5) * 50
        dr.text((cx, cy), lab, font=F(12, True), fill=(150, 160, 175))
        col = (255, 255, 255)
        if lab == 'BIN-WHEEL CLEAR' and carry and clr < 0.030: col = (255, 90, 80)
        if lab == 'HEDGE CLEAR' and h[6] < 0: col = (255, 90, 80)
        if lab == 'LIFT ACTUATOR' and h[4] > 2950: col = (255, 170, 60)
        dr.text((cx, cy + 15), val, font=FM(22), fill=col)
    if h[9] > 0.5: dr.rounded_rectangle([12, y0 - 34, 210, y0 - 6], 6, fill=(150, 90, 30, 220)); dr.text((22, y0 - 31), 'WET LEAVES  mu 0.35', font=F(15, True), fill=(255, 255, 255))
    # live status + run verdict
    ok = not R.badcum[i]; wn = bool(R.warn[i]); st = 'CRITERIA OK SO FAR' if (ok and not wn) else ('BIN WHEELS < 30 mm (dip)' if ok else 'CRITERION BREACHED')
    bx = W - 330; dr.rounded_rectangle([bx, y0 - 76, W - 12, y0 - 8], 8, fill=(20, 120, 60, 225) if (ok and not wn) else ((190, 120, 20, 230) if ok else (170, 40, 40, 225)))
    dr.text((bx + 12, y0 - 72), st, font=F(17, True), fill=(255, 255, 255))
    v = R.res['verdict']; dr.text((bx + 12, y0 - 46), 'RUN RESULT (frozen criteria): ' + v, font=F(15, True), fill=(255, 255, 255) if v == 'PASS' else (255, 220, 120))
    if night: dr.text((12, 96), 'NIGHT RUN (scene darkened, headlights; lights 17 W in the energy)', font=F(15, True), fill=(255, 230, 150))
    # inset map
    m = MAP.copy(); md = ImageDraw.Draw(m); px, py = MAPTF(*R.q[i, 0, :2]); md.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(230, 30, 30), outline=(255, 255, 255), width=2)
    img.paste(m, (W - m.width - 12, 70), m)
def frame(R, t, shot, vid):
    i = R.idx(t); q = R.q[i]; h = R.h[i]; cfg = R.cfg; s = float(h[0])
    w, x, y, z = q[0, 3:]; yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z)); hd = LW.heading(min(max(s, 4), LW.LEN - 4))
    dirn = 1 if math.cos(yaw - hd) >= 0 else -1
    tris, cols, oid = robot_mesh(q, cfg['with_bin'], cfg['binkey'])
    eye, tgt, fov = camera(q, s, dirn, shot.get('cam', 'chase')); cut = 0
    se, le = LW.project(np.array([eye[:2]])); se, le = float(se[0]), float(le[0])
    if shot.get('cam') == 'side': cut = 1 if le > 0 else -1
    elif shot.get('cam') == 'orbit':   # orbit eye inside/behind a hedge (pad A, P7 pothole) -> cut that side away
        sd = 1 if le > 0 else -1; fh = LW.hedge_face(min(max(se, 0.5), LW.LEN - 0.5), sd)
        if fh is None: fh = LW.hedge_face(min(max(se, 0.5), 620.5), sd) if se > 600 else None
        if fh is not None and abs(le) > fh - 0.3: cut = sd
    Te, Ce = env_cached(s, cfg['variant'], dirn, cut)
    Ts = [tris, Te]; Cs = [cols, Ce]; Os = [oid, np.full(len(Te), oid.max() + 1)]
    for k, o in enumerate(cfg.get('obstacles', [])[:2]):
        om = obstacle_mesh(R.ob[i, k].astype(float), o['kind'])
        if om is not None: Ts.append(om[0]); Cs.append(om[1]); Os.append(np.full(len(om[0]), Os[-1].max() + 1 + k))
    T = np.concatenate(Ts); C = np.concatenate(Cs); O = np.concatenate(Os)
    night = cfg.get('night', False)
    Wr, Hr = int(W * RS), int(H * RS)
    img = RA.render(T, C, O, eye, tgt, Wr, Hr, fov=fov, ss=1, sh_ext=14.0, sh_ctr=q[0, :3], bg=(0.80, 0.86, 0.93), bg2=(0.55, 0.70, 0.88), amb=0.45, kd=0.6,
                    outline=True, edge_alpha=0.35)
    if night:
        a = img.astype(np.float32) / 255.0; a = a * np.array([0.16, 0.18, 0.26])
        Rq = SC.qmat(q[0, 3:]); ahead = q[0, :3] + Rq @ np.array([3.0, 0, 0])
        c2 = RA.project([ahead], eye, tgt, Wr, Hr, fov=fov)[0]; c3 = RA.project([q[0, :3] + Rq @ np.array([1.1, 0, 0])], eye, tgt, Wr, Hr, fov=fov)[0]
        yy, xx = np.mgrid[0:Hr, 0:Wr]; g = np.exp(-(((xx - c2[0]) / (260.0 * RS)) ** 2 + ((yy - c2[1]) / (110.0 * RS)) ** 2))
        g2 = np.exp(-(((xx - c3[0]) / (160.0 * RS)) ** 2 + ((yy - c3[1]) / (120.0 * RS)) ** 2))
        lit = np.clip(g + 0.6 * g2, 0, 1)[..., None]; a = a * (1 - lit) + (img.astype(np.float32) / 255.0) * 0.95 * lit
        img = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(img).resize((W, H), Image.LANCZOS); draw_hud(im, R, i, shot, vid, night)
    if cut: ImageDraw.Draw(im).text((12, 118 if night else 96), 'Near-side hedge cut away for the camera view', font=F(14), fill=(255, 255, 255))
    return im
def title_card(vid, sub=None, secs=4.0):
    im = Image.new('RGB', (W, H), (14, 20, 30)); dr = ImageDraw.Draw(im)
    dr.text((80, 200), CAPTION, font=F(30, True), fill=(255, 210, 80))
    dr.text((80, 270), vid['title'], font=F(34, True), fill=(255, 255, 255))
    y = 340
    for ln in (sub or vid.get('sub', [])):
        dr.text((80, y), ln, font=F(22), fill=(200, 210, 225)); y += 36
    dr.text((80, H - 70), 'BinRobo B2-F (front-wall EN 840 receiver dock)  |  MuJoCo 3.x, dt 0.5 ms, frozen gate model simB2h.py  |  renders: software rasteriser', font=F(16), fill=(140, 150, 165))
    return [im] * int(secs * FPS)
def end_card(vid):
    im = Image.new('RGB', (W, H), (14, 20, 30)); dr = ImageDraw.Draw(im); y = 110
    dr.text((80, 50), 'Results (frozen criteria) - ' + vid['title'], font=F(28, True), fill=(255, 255, 255))
    for rid in dict.fromkeys(vid['runs']):
        r = rec(rid).res; M = r['metrics']; col = (120, 230, 140) if r['verdict'] == 'PASS' else (255, 120, 100)
        dr.text((80, y), '%s  %s' % (r['verdict'], r['title']), font=F(20, True), fill=col); y += 30
        ln = 'sim %.0f s | %.1f Wh | bin-wheel clear min %s | hedge min %s | tip margin min %.1f deg | lift peak %.0f N' % (
            r['sim_time_s'], r['energy_Wh'], ('%.0f mm' % (1000 * M['clear_min'])) if M['clear_min'] < 8 else '-', ('%.2f m' % M['hedge_min']) if M['hedge_min'] < 8 else '-', M['tip_min'], M['liftF_max'])
        dr.text((100, y), ln, font=F(16), fill=(210, 215, 225)); y += 24
        for f in r['fails'][:3]: dr.text((100, y), '- ' + f[:120], font=F(16), fill=(255, 190, 150)); y += 22
        y += 10
        if y > H - 80: break
    dr.text((80, H - 50), CAPTION, font=F(18, True), fill=(255, 210, 80))
    return [im] * int(5 * FPS)

# ------------------------------------------------------------------ videos
def shots_transit(rid, t_grab_end=None, speed=40.0, ends=6.0):
    R = rec(rid); ph = R.ph; t = R.t
    def first(pred):
        for k, p in enumerate(ph):
            if pred(p): return float(t[k])
        return None
    out = []
    tg = first(lambda p: p.startswith('Transit') or p.startswith('Pivot') or p.startswith('Pull')); td = first(lambda p: p.startswith('10 SD2'))
    t_end = float(t[-1])
    if any(str(p).startswith(('0', '1')) or 'Approach' in str(p) for p in ph[:200]):
        out.append(dict(run=rid, t0=float(t[0]), t1=tg if tg else t_end, speed=ends, cam='orbit'))
    if tg is not None:
        tr_end = td if td else t_end
        out.append(dict(run=rid, t0=tg, t1=tr_end, speed=speed, cam='chase'))
    if td is not None: out.append(dict(run=rid, t0=td - 2.0, t1=t_end, speed=ends, cam='orbit'))
    return out
HL_SHOTS = [('P1', 0.0, 45.52, 8.0, 'orbit', 'P1 grab of the full 240 L bin (110 kg) at home - PASS'), ('P1', 302.0, 339.24, 6.0, 'chase', 'P1 down the 12 % wet-leaf pitch with 110 kg - PASS'), ('P5c_drop_ramp14', 614.1, 623.1, 1.5, 'side', 'P5c 40 mm step down on the 1:4 ramp - PASS (bin wheels dip to 14 mm)'), ('P5d_up_sharp_3kN', 666.38, 693.22, 3.0, 'side', 'P5d sharp 40 mm up-step - FAIL: drive wheels cannot climb (needs mu 0.86)'), ('P5g_trench_open', 949.06, 975.22, 2.0, 'side', 'P5g open 200 mm trench - FAIL: drive wheels wedge, stall'), ('P6a_person_estop', 321.21, 335.21, 1.25, 'chase', 'P6a person steps out on the 12 % wet descent - E-STOP, PASS'), ('P2c_pf', 1008.0, 1046.0, 5.0, 'chase', 'P2c-pf light 13 kg bin, 12 % wet climb - FAIL: drive wheel unloads, slip, lane departure'), ('P7', 1138.0, 1190.0, 8.0, 'chase', 'P7 night, mu x0.8 - FAIL: drive wheel trapped in the 60 mm pothole'), ('P1', 1297.44, 1323.04, 6.0, 'orbit', 'P1 set-down at pad A - PASS')]
def vid_def(name):
    V = {
     'P1': dict(title='P1 - full 240 L bin (110 kg): home -> pad A', runs=['P1'], sub=['Grab at home (x4), transit 633 m (time-lapse x30), set-down at pad A (x4).',
                'ESE 240 SL at 110 kg, front wall to the mast. Prepared lane: 1:4 ramp on the 40 mm step, trench covered.']),
     'P2': dict(title='P2 - return empty / collect the emptied 240 L at pad A', runs=['P2a', 'P2c', 'P2a_pf', 'P2c_pf'], sub=['P2a: pad A -> home without a bin. P2c: grab the empty bin (13 kg) at pad A, carry home.',
                'Both stall at the as-is 60 mm pothole (s 550). Supplementary *_pf runs: pothole filled.', 'Trim: the empty outbound leg home -> pad A is not simulated.']),
     'P3': dict(title='P3 - full 140 L bin (Weber 140, 66 kg): home -> pad A', runs=['P3'], sub=['Same mission as P1 with the 140 L bin (480 mm receiver).', '140 L drawn as a scaled 240 L CAD bin.']),
     'P4': dict(title='P4 - 12 % pitch, 110 kg, wet leaves (mu 0.35), stop and hold', runs=['P4a', 'P4b'], sub=['P4a downhill, P4b uphill (after a pivot on the slope).',
                'Spring-brake hold 10 s; frozen limit: creep < 0.05 m over 3 s.', 'The 12 % pitch is an ASSUMED overlay on the EU-DEM profile (DEM max 7.9 %).']),
     'P5': dict(title='P5 - 40 mm step (sharp / 1:4 ramp), trench, pothole, 110 kg', runs=['P5a_drop_sharp_3kN', 'P5b_drop_sharp_4kN', 'P5c_drop_ramp14', 'P5d_up_sharp_3kN', 'P5e_up_sharp_4kN', 'P5f_up_ramp14', 'P5g_trench_open', 'P5i_trench_open_4kN', 'P5h_pothole'],
                sub=['Real time. Step DOWN (outbound) and UP (bin carried back), 3 kN model cap and 4 kN (BOM FDI 4 kN).', 'Feature chainages are ASSUMED (no survey).']),
     'P6': dict(title='P6 - person and dog step into the path', runs=['P6a_person_estop', 'P6b_dog_crossing'], sub=['P6a: person steps out 1-2 m ahead on the 12 % wet descent -> E-STOP (spring brakes).',
                'P6b: dog runs across -> controlled stop, wait 2 s clear, resume. Real time.']),
     'P7': dict(title='P7 - night run, bin CG +60 mm, mass x1.1, mu x0.8', runs=['P7'], sub=['P1 mission with perturbations; all friction x0.8 (leaves 0.28).', 'Night: render darkened, lights 17 W added to the energy.']),
    }
    V['HL'] = dict(title='B2-F lane digital twin - highlights', runs=[h[0] for h in HL_SHOTS], titlesec=3, subsec=1.0,
                   sub=['Brian\'s 633 m lane, MuJoCo digital twin. Frozen pass/fail criteria.', 'Grab, the 12 % wet-leaf pitch, step/trench/pothole, a person stepping out,', 'and the failures found (light-load slip, pothole trap, sharp up-step, open trench).'])
    v = V[name]; v['name'] = name; shots = []
    if name == 'HL':
        v['shots'] = [dict(run=r, t0=a, t1=b, speed=sp, cam=cam, label=lab) for (r, a, b, sp, cam, lab) in HL_SHOTS]; return v
    for rid in v['runs']:
        R = rec(rid)
        if name in ('P1', 'P3', 'P7', 'P2'):
            sh = shots_transit(rid, speed=60.0 if rid.endswith('_pf') else 40.0)
            if name == 'P2':
                for x in sh: x['label'] = R.res['title']
            if name == 'P7':   # split the transit: x30 to the pothole trap, x100 while circling until the drive timeout
                out = []
                for x in sh:
                    if x['cam'] == 'chase' and x['t0'] < 1150.0 < x['t1']:
                        out += [dict(x, t1=1150.0), dict(x, t0=1150.0, speed=150.0)]
                    else: out.append(x)
                sh = out
            shots += sh
        elif name == 'HL': pass
        elif name == 'P5':
            fs = 290.0 if ('drop' in rid or 'up' in rid) else (455.0 if 'trench' in rid else 550.0)
            k = np.where(np.abs(R.h[:, 0] - fs) < 1.2)[0]; t0 = max(float(R.t[0]), float(R.t[k[0]]) - 4.0) if len(k) else float(R.t[0])
            shots.append(dict(run=rid, t0=t0, t1=float(R.t[-1]), speed=2.0, cam='side', label=R.res['title']))
        elif name == 'P4': shots.append(dict(run=rid, t0=float(R.t[0]), t1=float(R.t[-1]), speed=4.0, cam='chase', label=R.res['title']))
        elif name == 'P6':
            te = [e[0] for e in R.res['events'] if 'starts moving' in str(e[1])]
            t0 = max(float(R.t[0]), te[0] - 7.0) if te else float(R.t[0])
            shots.append(dict(run=rid, t0=t0, t1=float(R.t[-1]), speed=1.0, cam='chase', label=R.res['title']))
    v['shots'] = shots; return v
def frame_list(v):
    """[(kind, payload)] - kind 'card' (PIL image list index) or ('sim', shot index, t)"""
    L = [('title', k) for k in range(int(v.get('titlesec', 4) * FPS))]
    for j, sh in enumerate(v['shots']):
        if sh.get('label') and (j == 0 or v['shots'][j - 1]['run'] != sh['run']) and len(v['runs']) > 1: L += [('sub', j, k) for k in range(int(v.get('subsec', 1.6) * FPS))]
        n = max(1, int((sh['t1'] - sh['t0']) / sh['speed'] * FPS))
        L += [('sim', j, sh['t0'] + k * sh['speed'] / FPS) for k in range(n)]
    L += [('end', k) for k in range(5 * FPS)]
    return L
def sub_card(sh, k):
    R = rec(sh['run']); im = Image.new('RGB', (W, H), (14, 20, 30)); dr = ImageDraw.Draw(im)
    dr.text((80, 280), R.res['title'], font=F(32, True), fill=(255, 255, 255)); col = (120, 230, 140) if R.res['verdict'] == 'PASS' else (255, 120, 100)
    dr.text((80, 340), 'Result: ' + R.res['verdict'] + ('' if R.res['verdict'] == 'PASS' else ' - ' + '; '.join(R.res['fails'])[:120]), font=F(20, True), fill=col)
    dr.text((80, H - 60), CAPTION, font=F(18, True), fill=(255, 210, 80)); return im
def render_video(name, budget):
    v = vid_def(name); L = frame_list(v); d = os.path.join(HERE, 'vid', name); os.makedirs(d, exist_ok=True)
    stf = os.path.join(d, 'state.json'); st = json.load(open(stf)) if os.path.exists(stf) else dict(next=0, seg=0, n=len(L))
    if st['next'] >= len(L): print('DONE frames', name, len(L)); return True
    title = None; endc = None
    seg = os.path.join(d, 'seg_%03d.mp4' % st['seg'])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', seg], stdin=subprocess.PIPE)
    k = st['next']; n0 = k
    while k < len(L) and time.time() - T0 < budget:
        it = L[k]
        if it[0] == 'title':
            title = title or title_card(v)[0]; im = title
        elif it[0] == 'end':
            endc = endc or end_card(v)[0]; im = endc
        elif it[0] == 'sub': im = sub_card(v['shots'][it[1]], it[2])
        else:
            sh = v['shots'][it[1]]; im = frame(rec(sh['run']), it[2], sh, v)
        ff.stdin.write(np.asarray(im.convert('RGB')).tobytes()); k += 1
        if k in (n0 + 5, n0 + 120) or k % 150 == 0: im.save(os.path.join(d, 'sample_%05d.jpg' % k), quality=88)
    ff.stdin.close(); ff.wait()
    st['next'] = k; st['seg'] += 1; json.dump(st, open(stf, 'w'))
    print('frames %d..%d of %d (%.2f s/frame)' % (n0, k, len(L), (time.time() - T0) / max(1, k - n0)), flush=True)
    return k >= len(L)
def finalize(name):
    d = os.path.join(HERE, 'vid', name); segs = sorted(glob.glob(os.path.join(d, 'seg_*.mp4')))
    lst = os.path.join(d, 'list.txt'); open(lst, 'w').write(''.join("file '%s'\n" % s for s in segs))
    out = os.path.join(OUT, 'B2F_lane_%s.mp4' % name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out], check=True)
    pr = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,r_frame_rate', '-of', 'json', out], capture_output=True, text=True).stdout
    print('FINAL', out, pr.replace('\n', ' '))
def patch_ranges(name):
    """frame ranges of orbit shots away from the yard (pad A / P7 pothole) - re-rendered with the hedge cut-away"""
    v = vid_def(name); L = frame_list(v); out = []; cur = None
    for k, it in enumerate(L):
        hit = False
        if it[0] == 'sim':
            sh = v['shots'][it[1]]
            if sh.get('cam') == 'orbit':
                R = rec(sh['run']); hit = float(R.h[R.idx(it[2]), 0]) > 30.0
        if hit and cur is None: cur = [k, k + 1]
        elif hit: cur[1] = k + 1
        elif cur is not None: out.append(tuple(cur)); cur = None
    if cur is not None: out.append(tuple(cur))
    return v, L, out
def patch(name, budget):
    """re-render the patch ranges into vid/<name>/patch_<a>.mp4 (resumable); then --splice"""
    v, L, rngs = patch_ranges(name); d = os.path.join(HERE, 'vid', name)
    for a, b in rngs:
        f = os.path.join(d, 'patch_%05d_%05d.mp4' % (a, b))
        if os.path.exists(f): continue
        if time.time() - T0 + (b - a) * 0.4 > budget: print('PATCH budget, next', a, b); return False
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', f + '.tmp.mp4'], stdin=subprocess.PIPE)
        for k in range(a, b):
            it = L[k]; sh = v['shots'][it[1]]; im = frame(rec(sh['run']), it[2], sh, v); ff.stdin.write(np.asarray(im.convert('RGB')).tobytes())
            if k == (a + b) // 2: im.save(os.path.join(d, 'patchsample_%05d.jpg' % k), quality=88)
        ff.stdin.close(); ff.wait(); os.replace(f + '.tmp.mp4', f); print('patched', name, a, b, flush=True)
    print('PATCH DONE', name, rngs); return True
def splice(name):
    v, L, rngs = patch_ranges(name); d = os.path.join(HERE, 'vid', name); src = os.path.join(OUT, 'B2F_lane_%s.mp4' % name)
    orig = os.path.join(d, 'orig_unpatched.mp4')
    if not os.path.exists(orig): os.replace(src, orig)
    pieces = []; k = 0; n = len(L)
    for a, b in rngs + [(n, n)]:
        if a > k:
            p = os.path.join(d, 'piece_%05d_%05d.mp4' % (k, a))
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', orig, '-vf', 'select=between(n\\,%d\\,%d),setpts=N/%d/TB' % (k, a - 1, FPS), '-r', str(FPS),
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', p], check=True); pieces.append(p)
        if b > a: pieces.append(os.path.join(d, 'patch_%05d_%05d.mp4' % (a, b)))
        k = b
    lst = os.path.join(d, 'plist.txt'); open(lst, 'w').write(''.join("file '%s'\n" % p for p in pieces))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', src], check=True)
    pr = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries', 'format=duration:stream=nb_read_frames,width,height', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout
    print('SPLICED', src, pr.replace('\n', ' '), 'expected frames', n)
if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[2] == '--patch': patch(sys.argv[1], float(sys.argv[3]) if len(sys.argv) > 3 else 95.0); sys.exit()
    if len(sys.argv) > 2 and sys.argv[2] == '--splice': splice(sys.argv[1]); sys.exit()
    if len(sys.argv) > 2 and sys.argv[2] == '--ranges': print(patch_ranges(sys.argv[1])[2]); sys.exit()
    if len(sys.argv) > 2 and sys.argv[2] == '--final': finalize(sys.argv[1])
    elif len(sys.argv) > 2 and sys.argv[2] == '--count':
        v = vid_def(sys.argv[1]); L = frame_list(v); print(sys.argv[1], len(L), 'frames', len(L) / FPS, 's', [(s['run'], round(s['t0'], 1), round(s['t1'], 1), s['speed']) for s in v['shots']])
    else: render_video(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 95.0)
