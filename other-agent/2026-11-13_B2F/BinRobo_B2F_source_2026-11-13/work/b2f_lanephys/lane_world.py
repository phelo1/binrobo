#!/usr/bin/env python3
"""B2-F full-lane MuJoCo world (digital twin of Brian's lane from OSM + EU-DEM). Imports revG/sim/cg/h2/simB2h.py UNCHANGED and
replaces only its ground plane (wrapper of build_xml, the runX.py pattern) with:
  heightfield (EU-DEM profile along the OSM centreline, flat cross-section, 0.25 m cells, whole-lane bbox),
  pooled hedge collision boxes near the robot, feature beds with sharp box tiles (step / trench / pothole), leaf friction zones.
All lane features are ASSUMED (no survey); see FEAT / LEAVES / G12 below and PROGRESS_B2F_lane_phys.md."""
import os, sys, json, math, numpy as np
P = '/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c'
for k, v in dict(B2_DOCK='front', H2_HULL='new', CGB_F9='1').items(): os.environ.setdefault(k, v)
sys.path[:0] = [P + '/revG/sim/cg/h2', P + '/revG/sim/cg/b2', P + '/revG/sim/cg', P + '/revG/sim/g6']
from scipy.interpolate import PchipInterpolator
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ centreline
ROUTE = json.load(open(P + '/sitl/data/route.json'))
XY = np.array(ROUTE['xy'], float)
SV = np.r_[0, np.cumsum(np.linalg.norm(np.diff(XY, axis=0), axis=1))]; LEN = float(SV[-1])
ZDEM = np.array(ROUTE['elev']['eudem25m'], float)
Z0 = 29.0                                   # datum (m above sea level) subtracted from every height
DSTEP = 0.05
DS = np.arange(0.0, LEN + 1e-9, DSTEP)
CX = np.interp(DS, SV, XY[:, 0]); CY = np.interp(DS, SV, XY[:, 1])
def _seg_heading():
    i = np.clip(np.searchsorted(SV, DS, side='right') - 1, 0, len(SV) - 2)
    d = XY[i + 1] - XY[i]; return np.arctan2(d[:, 1], d[:, 0])
CH = _seg_heading()                          # polyline segment heading at each dense station (for lateral sign)
TREE = cKDTree(np.c_[CX, CY])
def xy_at(s): return np.array([np.interp(s, DS, CX), np.interp(s, DS, CY)])
def heading(s):   # smoothed over +-4 m (as sitl world.Lane.heading)
    a = xy_at(max(s - 4, 0)); b = xy_at(min(s + 4, LEN)); return math.atan2(b[1] - a[1], b[0] - a[0])
def seg_heading(s): return float(CH[int(np.clip(round(s / DSTEP), 0, len(DS) - 1))])
def point(s, lat=0.0, h=None):
    h = heading(s) if h is None else h; c = xy_at(np.clip(s, 0, LEN))
    return c + lat * np.array([-math.sin(h), math.cos(h)])
def project(pts):
    """pts (N,2) -> s (N,), lat (N,) (+ = left of house->road)"""
    pts = np.atleast_2d(pts); _, i = TREE.query(pts); h = CH[i]
    dx = pts[:, 0] - CX[i]; dy = pts[:, 1] - CY[i]
    return DS[i] + dx * np.cos(h) + dy * np.sin(h), -dx * np.sin(h) + dy * np.cos(h)

# ------------------------------------------------------------------ assumed features (chainage s from the house, m)
G12 = (138.0, 152.0)                         # 12 % pitch overlay (ASSUMED; EU-DEM max 7.9 %)
FEAT = dict(step=dict(s=290.0, h=0.040), trench=dict(s=455.0, w=0.20, dep=0.040),
            pothole=dict(s=550.0, L=0.40, W=0.25, lat=0.40, dep=0.060))
BED = {k: (v['s'] - 3.0, v['s'] + 3.5) for k, v in FEAT.items()}   # heightfield lowered 0.15 m here; box tiles form the surface
LEAVES = [(128.0, 165.0), (200.0, 215.0), (470.0, 490.0), (575.0, 590.0)]
MU_GROUND, MU_LEAF = 0.6, 0.35
YARD_END, MOUTH0 = 25.0, LEN - 12.0          # no hedges in the yard (s<25) or the bell-mouth (s>621.06), as lanefit/LANE
HOME = dict(s=10.0, lat=-1.4); PAD_A = dict(s=LEN - 11.1, lat=1.35)   # scenarios.HOME_SPOTS['black'] / DROP_SPOTS['A']

def _profile():
    z0 = PchipInterpolator(SV, ZDEM)(DS); g0 = np.gradient(z0, DS)
    def smooth_win(a, b, bl):
        w = np.zeros_like(DS)
        w[(DS >= a) & (DS <= b)] = 1.0
        for e0, e1, up in ((a - bl, a, True), (b, b + bl, False)):
            m = (DS > e0) & (DS < e1); x = (DS[m] - e0) / bl; w[m] = 0.5 - 0.5 * np.cos(math.pi * (x if up else 1 - x))
        return w
    w = smooth_win(G12[0], G12[1], 2.0); g1 = g0 * (1 - w) + (-0.12) * w
    extra = float(np.sum(g1 - g0) * DSTEP)
    c = smooth_win(158.0, 190.0, 4.0); c /= np.sum(c) * DSTEP; g2 = g1 - extra * c
    z = z0[0] + np.r_[0, np.cumsum(0.5 * (g2[1:] + g2[:-1]) * DSTEP)]
    for k, (a, b) in BED.items():             # linearise the profile over each feature bed (+1 m) so planar tiles fit exactly
        a -= 1.0; b += 1.0; m = (DS >= a) & (DS <= b); za, zb = np.interp([a, b], DS, z); z[m] = za + (zb - za) * (DS[m] - a) / (b - a)
    return z - Z0, np.gradient(z, DS)
ZP, GP = _profile()
def zbase(s):                                # surface height without the step (datum Z0)
    return np.interp(s, DS, ZP)
def zprof(s):                                # surface height incl. the 40 mm step down at FEAT step s
    s = np.asarray(s, float); return np.interp(s, DS, ZP) - FEAT['step']['h'] * (s > FEAT['step']['s'])
def grade(s): return float(np.interp(s, DS, GP))

# ------------------------------------------------------------------ hedges (truth face = surveyed line 2.05 m - hedge_offset)
_HR = np.random.default_rng(2026)            # g6_features.py, copied (same seed -> same truth hedge)
_HK = [(_HR.uniform(0.02, 0.05), _HR.uniform(12, 60), _HR.uniform(0, 6.28)) for _ in range(4)]
HEDGE_GAPS = [(60.0, 64.0, +1), (140.0, 145.0, -1), (230.0, 242.0, +1), (330.0, 334.5, 0), (455.0, 460.0, -1), (560.0, 563.5, +1)]
HEDGE_BULGES = [(395.0, 420.0, -1, 0.55), (500.0, 516.0, 0, 0.60)]
def hedge_offset(s, side):
    o = sum(a * math.sin(2 * math.pi * s / lam + ph + (0.9 if side < 0 else 0.0)) for a, lam, ph in _HK)
    for a, b, sd, d in HEDGE_BULGES:
        if sd == 0 or sd == side: o += d * float(np.clip(min(s - a, b - s) / 3.0, 0.0, 1.0))
    return o
def hedge_face(s, side):
    """lateral of the hedge face (m, >0) on `side` for the 1 m segment containing s; None where there is no hedge"""
    if s < YARD_END or s > MOUTH0: return None
    k = math.floor(s); sm = k + 0.5
    for a, b, sd in HEDGE_GAPS:
        if a <= sm <= b and (sd == 0 or sd == side): return None
    return 2.05 - hedge_offset(sm, side)
NPOOL = 26                                   # segments per side kept as collision boxes (s-8 .. s+17 around the robot)
BODY_HALF = 0.49                             # B2-F half width incl. arms/guards (CORNERS y max 0.465 + guard)

# ------------------------------------------------------------------ heightfield
HRES = 0.25
def hfield_grid(cache=os.path.join(HERE, 'hfield_cache.npz')):
    if os.path.exists(cache):
        d = np.load(cache); return d['H'], tuple(d['geo'])
    x0, x1 = CX.min() - 12, CX.max() + 12; y0, y1 = CY.min() - 12, CY.max() + 12
    nc = int(math.ceil((x1 - x0) / HRES)) + 1; nr = int(math.ceil((y1 - y0) / HRES)) + 1
    xs = x0 + HRES * np.arange(nc); ys = y0 + HRES * np.arange(nr)
    H = np.empty((nr, nc), np.float32)
    for r0 in range(0, nr, 200):
        gx, gy = np.meshgrid(xs, ys[r0:r0 + 200]); pts = np.c_[gx.ravel(), gy.ravel()]
        s, lat = project(pts); s = np.clip(s, 0, LEN); z = zprof(s)
        for k, (a, b) in BED.items(): z = z - 0.15 * ((s >= a) & (s <= b) & (np.abs(lat) <= 2.8))
        H[r0:r0 + 200] = z.reshape(gx.shape)
    geo = (x0, x1, y0, y1, nr, nc)
    np.savez_compressed(cache, H=H, geo=np.array(geo)); return H, geo

# ------------------------------------------------------------------ feature tiles (sharp edges)
def _frame(s):
    h = seg_heading(s); g = grade(s); t = np.array([math.cos(h), math.sin(h), g]); t /= np.linalg.norm(t)
    n = np.array([-math.sin(h), math.cos(h), 0.0]); u = np.cross(t, n); return np.c_[t, n, u]
def _quat(R):
    import mujoco; q = np.zeros(4); mujoco.mju_mat2Quat(q, R.ravel()); return q
def tiles(variant):
    """variant: dict(step='ramp'|'sharp', trench='covered'|'open'). Returns list of (name, center, R, half sizes) boxes;
    top faces on the lane surface. Local axes: t along s, n lateral, u up."""
    out = []
    L0, L1 = -3.0, 3.0
    f = FEAT['step']; a, b = BED['step']; ss = f['s']
    def box2(name, fs, s0, s1, l0, l1, zlevel_fn, th=0.10):
        R = _frame(fs); sm = 0.5 * (s0 + s1); lm = 0.5 * (l0 + l1); c2 = point(sm, lm, h=seg_heading(fs))
        c = np.array([c2[0], c2[1], zlevel_fn(sm)]) - R[:, 2] * th / 2
        out.append((name, c, R, ((s1 - s0) / 2 * math.sqrt(1 + grade(fs) ** 2), (l1 - l0) / 2, th / 2)))
    up = lambda s: float(zbase(s)); lo = lambda s: float(zbase(s)) - f['h']
    box2('stepU', ss, a - 0.4, ss, L0, L1, up); box2('stepL', ss, ss, b + 0.4, L0, L1, lo)
    if variant.get('step', 'ramp') == 'ramp':   # 1:4 ramp on the lower side: 160 mm long, from the lower level up to the edge
        Lr = 4 * f['h']; th = math.atan(f['h'] / Lr); R0 = _frame(ss)
        Rr = R0 @ np.array([[math.cos(th), 0, math.sin(th)], [0, 1, 0], [-math.sin(th), 0, math.cos(th)]])   # Ry(+th): top falls along +s
        tt = 0.02; sm = ss + Lr / 2; c2 = point(sm, 0.0, h=seg_heading(ss))
        zc = float(zbase(sm)) - f['h'] / 2
        c = np.array([c2[0], c2[1], zc]) - Rr[:, 2] * tt / 2
        out.append(('stepRamp', c, Rr, (Lr / 2 / math.cos(th) + 0.004, (L1 - L0) / 2, tt / 2)))
    f = FEAT['trench']; a, b = BED['trench']; ts = f['s']; lev = lambda s: float(zbase(s)) - FEAT['step']['h']
    box2('trA', ts, a - 0.4, ts, L0, L1, lev); box2('trB', ts, ts + f['w'], b + 0.4, L0, L1, lev)
    box2('trBot', ts, ts - 0.05, ts + f['w'] + 0.05, L0, L1, lambda s: lev(s) - f['dep'])
    if variant.get('trench', 'covered') == 'covered': box2('trCover', ts, ts, ts + f['w'], L0, L1, lev)
    f = FEAT['pothole']; a, b = BED['pothole']; ps = f['s']; pl0, pl1 = f['lat'] - f['W'] / 2, f['lat'] + f['W'] / 2
    box2('phA', ps, a - 0.4, ps, L0, L1, lev); box2('phB', ps, ps + f['L'], b + 0.4, L0, L1, lev)
    box2('phR', ps, ps, ps + f['L'], L0, pl0, lev); box2('phL', ps, ps, ps + f['L'], pl1, L1, lev)
    box2('phBot', ps, ps - 0.05, ps + f['L'] + 0.05, pl0 - 0.05, pl1 + 0.05, lambda s: lev(s) - f['dep'])
    if variant.get('pothole', 'asis') == 'filled': box2('phCover', ps, ps, ps + f['L'], pl0, pl1, lev)
    return out

def surface_z(x, y, variant=None):
    """analytic surface height (datum) at world x,y incl. sharp features (for clearance metrics)"""
    variant = variant or {}
    s, lat = project(np.c_[np.atleast_1d(x), np.atleast_1d(y)]); s = np.clip(s, 0, LEN); z = zprof(s)
    f = FEAT['step']; ramp = variant.get('step', 'ramp') == 'ramp'
    if ramp:
        m = (s > f['s']) & (s < f['s'] + 4 * f['h']); z = np.where(m, z + f['h'] * (1 - (s - f['s']) / (4 * f['h'])), z)
    f = FEAT['trench']
    if variant.get('trench', 'covered') != 'covered':
        m = (s > f['s']) & (s < f['s'] + f['w']); z = np.where(m, z - f['dep'], z)
    f = FEAT['pothole']
    m = (s > f['s']) & (variant.get('pothole', 'asis') != 'filled') & (s < f['s'] + f['L']) & (lat > f['lat'] - f['W'] / 2) & (lat < f['lat'] + f['W'] / 2); z = np.where(m, z - f['dep'], z)
    return z

def leaf_at(s): return any(a <= s <= b for a, b in LEAVES)

# ------------------------------------------------------------------ XML injection
def world_xml(variant, mu=MU_GROUND, obstacles=()):
    H, (x0, x1, y0, y1, nr, nc) = hfield_grid()
    zmin = float(H.min()) - 0.05; zmax = float(H.max()) + 0.05
    asset = f'<hfield name="lane" nrow="{int(nr)}" ncol="{int(nc)}" size="{(x1 - x0) / 2:.4f} {(y1 - y0) / 2:.4f} {zmax - zmin:.4f} 1.0"/>'
    fr = f'{mu} 0.005 0.0001'
    g = [f'<geom name="ground" type="hfield" hfield="lane" pos="{(x0 + x1) / 2:.4f} {(y0 + y1) / 2:.4f} {zmin:.4f}" friction="{fr}" condim="3" priority="1" rgba="0.5 0.5 0.45 1"/>']
    for t in tiles(variant):
        name, c, R, hs = t; q = _quat(R)
        g.append(f'<geom name="t_{name}" type="box" pos="{c[0]:.5f} {c[1]:.5f} {c[2]:.5f}" quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}" '
                 f'size="{hs[0]:.5f} {hs[1]:.5f} {hs[2]:.5f}" friction="{fr}" condim="3" priority="1" rgba="0.45 0.45 0.42 1"/>')
    for side in (1, -1):
        for k in range(NPOOL):
            g.append(f'<geom name="hedge{"L" if side > 0 else "R"}{k}" type="box" pos="0 0 -500" size="0.52 0.4 1.1" friction="0.8" condim="3" rgba="0.2 0.45 0.2 1"/>')
    for o in obstacles:   # mocap moving obstacles (person/dog)
        g.append(f'<body name="{o["name"]}" mocap="true" pos="0 0 -400"><geom name="g_{o["name"]}" type="capsule" fromto="0 0 {o["r"]} 0 0 {o["h"] - o["r"]}" size="{o["r"]}" contype="1" conaffinity="1" rgba="0.8 0.3 0.2 1"/></body>')
    return asset, ''.join(g), (H, zmin, zmax)

def install(B, variant, obstacles=()):
    """monkeypatch simB2h.build_xml so SimB builds on the lane world. Returns a post-build hook setting the hfield data."""
    _bx = B._orig_build_xml if hasattr(B, '_orig_build_xml') else B.build_xml; B._orig_build_xml = _bx
    asset, geoms, (H, zmin, zmax) = world_xml(variant, obstacles=obstacles)
    def build_xml2(*a, **k):
        xml, tm, bm = _bx(*a, **k)
        i = xml.find('<geom name="ground"'); j = xml.find('/>', i) + 2; xml = xml[:i] + geoms + xml[j:]
        if '<asset>' in xml: xml = xml.replace('<asset>', '<asset>' + asset, 1)
        else: xml = xml.replace('<worldbody>', '<asset>' + asset + '</asset><worldbody>', 1)
        return xml, tm, bm
    B.build_xml = build_xml2
    def post(m):
        import mujoco
        hid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_HFIELD, 'lane')
        adr = m.hfield_adr[hid]; n = m.hfield_nrow[hid] * m.hfield_ncol[hid]
        m.hfield_data[adr:adr + n] = ((H.astype(np.float64) - zmin) / (zmax - zmin)).ravel()
    return post

class HedgePool:
    """moves the pooled hedge boxes to the 1 m segments around the robot (s-8 .. s+17)"""
    def __init__(s, m):
        import mujoco
        s.m = m; s.ids = {side: [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, 'hedge%s%d' % ('L' if side > 0 else 'R', k)) for k in range(NPOOL)] for side in (1, -1)}
        s.k0 = None
    def update(s, s_now, back=8):
        import mujoco
        k0 = int(math.floor(s_now)) - back
        if k0 == s.k0: return
        s.k0 = k0
        for side in (1, -1):
            for j, gid in enumerate(s.ids[side]):
                k = k0 + j; sm = k + 0.5; f = hedge_face(sm, side) if 0 <= sm <= LEN else None
                if f is None: s.m.geom_pos[gid] = (0, 0, -500); continue
                h = seg_heading(sm); c = point(sm, side * (f + 0.4), h=h); z = float(zprof(sm)) + 0.8
                s.m.geom_pos[gid] = (c[0], c[1], z); q = np.zeros(4); mujoco.mju_axisAngle2Quat(q, np.array([0, 0, 1.0]), h); s.m.geom_quat[gid] = q

if __name__ == '__main__':
    import time; t = time.time(); H, geo = hfield_grid(); print('hfield', H.shape, geo, round(time.time() - t, 1), 's')
    print('len', LEN, 'z house', zprof(0), 'z road', zprof(LEN), 'max |grade| %', round(100 * np.abs(GP).max(), 2), 'at', DS[np.argmax(np.abs(GP))])
    for s in (100, 136, 140, 145, 150, 155, 170, 190, 200): print(s, round(100 * grade(s), 2), end='; ')
    print(); print('pad A', PAD_A, point(PAD_A['s'], PAD_A['lat']), 'home', point(HOME['s'], HOME['lat']))
    for t_ in tiles(dict(step='ramp', trench='covered')): print(t_[0], np.round(t_[1], 3), np.round(t_[3], 3))
