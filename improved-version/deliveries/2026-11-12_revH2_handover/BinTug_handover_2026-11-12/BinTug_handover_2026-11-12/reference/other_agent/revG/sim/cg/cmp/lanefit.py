#!/usr/bin/env python3
"""Kinematic lane-fit comparison for straddle carriers (no MuJoCo). Same lane geometry as the G6 SITL (sitl/scripts_g6):
OSM lane (633 m), surveyed hedge line at +/-(3.6/2+0.25) m, TRUTH hedge faces (irregularity + overgrown narrowings incl.
s=500-516 both sides 0.60 m in = 2.9 m face to face), hedge gaps, yard s 0-25 (half 6 m), bell-mouth last 12 m (half 4.5 m),
private boundary 6.0 m from the road centre-line (footprint >= 0.3 m inside, SITL fp_ok), pads A/M/F, home spots, dock.
Strict scoring: any footprint point past a truth hedge face = FAIL; legal margin < 0.3 m = FAIL; bin-bin gap < 0.05 m = FAIL.
usage: lanefit.py <design.json> [<design.json> ...]  -> res/lanefit_<name>.json
design json: name, outline [[x,y],..] (tug, empty, tug frame: origin drive-axle centre, +x nose), bin [[x,y],..] (carried bin
in the tug frame), handle_dir (+1 handle toward robot +x, -1 toward -x), withdraw (+1 robot drives +x to leave the bin),
approach (-1 robot moves -x onto the bin), carry_dir (+1 normal travel is +x), half_w (m), pivot_D_sim (optional, m)."""
import os, sys, json, math, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); SITL = os.path.join(H, '..', '..', '..', '..', 'sitl', 'scripts_g6')
sys.path.insert(0, SITL)
import scenarios as SC, g6_features as G6
S = SC.site('real'); L = S.L; LANE = S.lane; HLN = G6.HL_NOM; M0 = LANE.mouth[0]
BINWD = (0.58, 0.74)                      # standing bin footprint w x d (SITL BIN)
EST_P95, EST_MAX = 0.124, 0.364           # SITL G6 s25a corridor-down lateral estimate error (truth), p95 / max |m|
LEGAL = 0.30; BINGAP = 0.05

def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
def tf(pts, x, y, yaw):
    c, s = math.cos(yaw), math.sin(yaw); P = np.asarray(pts, float)
    return np.c_[x + c * P[:, 0] - s * P[:, 1], y + s * P[:, 0] + c * P[:, 1]]
def densify(poly, step=0.05):
    out = []; P = np.asarray(poly, float)
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]; n = max(1, int(np.linalg.norm(b - a) / step))
        out += [a + (b - a) * k / n for k in range(n)]
    return np.array(out)

def region_margin(p):
    """signed margin (m) of a world point inside the drivable region (+ inside). Lane: truth hedge face; yard: half 6 m;
    mouth: half 4.5 m and private boundary - LEGAL. Returns (margin, kind)."""
    s, lat = LANE.project(np.asarray(p, float)); side = 1 if lat >= 0 else -1
    if s < -3: return -1.0, 'yard end'
    if s <= LANE.yard[1]: return 6.0 - abs(lat), 'yard'
    if s >= M0: return min(S.mouth_half - abs(lat), S.boundary_dist(p) - LEGAL), 'mouth/legal'
    face = HLN - (0.0 if G6.in_gap(s, side) else G6.hedge_offset(s, side))   # in a gap the surveyed line is kept (gate posts)
    m = face - abs(lat)
    if s > M0 - 12: m = min(m, S.boundary_dist(p) - LEGAL)
    return m, 'hedge'

def box_pts(x, y, yaw, w=BINWD[0], d=BINWD[1]):
    return tf([[d / 2, w / 2], [d / 2, -w / 2], [-d / 2, -w / 2], [-d / 2, w / 2]], x, y, yaw)
def pt_box_dist(p, x, y, yaw, w=BINWD[0], d=BINWD[1]):
    c, s = math.cos(yaw), math.sin(yaw); q = np.asarray(p) - [x, y]; lx = c * q[..., 0] + s * q[..., 1]; ly = -s * q[..., 0] + c * q[..., 1]
    dx = np.maximum(np.abs(lx) - d / 2, 0); dy = np.maximum(np.abs(ly) - w / 2, 0)
    inside = (np.abs(lx) <= d / 2) & (np.abs(ly) <= w / 2)
    return np.where(inside, -np.minimum(d / 2 - np.abs(lx), w / 2 - np.abs(ly)), np.hypot(dx, dy))

class Design:
    def __init__(s, D):
        s.D = D; s.name = D['name']
        # footprint = perimeters of the part rectangles (NOT a convex hull: the open U must not be filled in)
        s.outline = np.vstack([densify([[a, c], [b_, c], [b_, d_], [a, d_]], 0.04) for a, b_, c, d_, *_ in D['parts']])
        s.binp = densify(D['bin'], 0.04) if D.get('bin') else np.zeros((0, 2))
        s.hd = D['handle_dir']; s.wd = D['withdraw']; s.cd = D.get('carry_dir', 1)
        s.r_empty = float(np.max(np.linalg.norm(s.outline, axis=1)))
        s.r_load = float(max(s.r_empty, np.max(np.linalg.norm(s.binp, axis=1)) if len(s.binp) else 0))
        if D.get('pivot_D_sim'): s.r_load = max(s.r_load, D['pivot_D_sim'] / 2)
        s.bin_c = s.binp.mean(axis=0) if len(s.binp) else np.zeros(2)
        s.half_w = D['half_w']
    def fp(s, x, y, yaw, loaded): return tf(np.vstack([s.outline, s.binp]) if loaded else s.outline, x, y, yaw)

# ---------------------------------------------------------------- 1. swept path along the lane
def lane_target(s, sgn, hw):
    """SITL G4/G6 rule: keep-left (0.40 m gap to the 3.6 m lane edge) in the KL zone; centring between the truth faces where
    face-to-face < 3.2 m (ramp to full centring at 2.9 m)."""
    kl = sgn * (LANE.width / 2 - 0.40 - hw)
    fl = HLN - (0.0 if G6.in_gap(s, 1) else G6.hedge_offset(s, 1)); fr = HLN - (0.0 if G6.in_gap(s, -1) else G6.hedge_offset(s, -1))
    wff = fl + fr; mid = (fl - fr) / 2
    a = float(np.clip((3.2 - wff) / 0.3, 0, 1)); tgt = (1 - a) * kl + a * mid
    # never closer than the body half-width + 0.25 m to a face on the keep-left side (SITL corridor guard)
    return float(np.clip(tgt, -fr + hw + 0.25, fl - hw - 0.25)) if wff > 2 * hw + 0.5 else mid
def lane_sweep(d, loaded, sgn, v=0.5, dt=0.05, s0=26.0, s1=None):
    s1 = s1 or (M0 - 1.0); hw = d.half_w
    if sgn < 0: s0, s1 = s1, s0
    x, y = LANE.point(s0, lane_target(s0, sgn, hw)); yaw = LANE.heading(s0) + (0 if sgn > 0 else math.pi)
    prof = []; worst = (9, None); n = 0
    while True:
        s, lat = LANE.project(np.array([x, y]))
        if (sgn > 0 and s >= s1) or (sgn < 0 and s <= s1) or n > 40000: break
        la = 1.5; st = s + sgn * la; tp = LANE.point(st, lane_target(st, sgn, hw))
        a = wrap(math.atan2(tp[1] - y, tp[0] - x) - yaw); w = 2 * v * math.sin(a) / la
        x += v * math.cos(yaw) * dt; y += v * math.sin(yaw) * dt; yaw = wrap(yaw + w * dt); n += 1
        if n % 4: continue
        P = d.fp(x, y, yaw, loaded); best = 9
        for p in P[::2]:
            m, k = region_margin(p)
            if k == 'hedge': best = min(best, m)
        prof.append((round(s, 1), round(best, 3)))
        if best < worst[0]: worst = (round(best, 3), round(s, 1))
    return dict(min_clear_m=worst[0], at_s=worst[1], prof=prof[::5])

# ---------------------------------------------------------------- 2. pivot (180 deg) fit
def disc_ok(c, r, obst):
    """margin of a swept disc (centre c, radius r) inside the region and clear of standing bins (box list)."""
    m = 9.0
    for a in np.linspace(0, 2 * math.pi, 48, endpoint=False):
        p = c + r * np.array([math.cos(a), math.sin(a)]); mm, _ = region_margin(p); m = min(m, mm)
    for (bx, by, byaw) in obst: m = min(m, float(pt_box_dist(np.array(c), bx, by, byaw)) - r - BINGAP)   # gap to bin must exceed BINGAP
    return m
def pivot_search(r, zone, obst, step=0.2):
    """best pivot centre in zone (s0,s1,lat0,lat1): returns margin (m, >0 = fits) and where."""
    best = (-9, None)
    for s in np.arange(zone[0], zone[1] + 1e-6, step):
        for lat in np.arange(zone[2], zone[3] + 1e-6, step):
            c = LANE.point(s, lat); m = disc_ok(c, r, obst)
            if m > best[0]: best = (round(m, 3), (round(float(s), 1), round(float(lat), 2)))
    return best
def lane_pivot_profile(r, ds=1.0):
    """at each station: can the swept disc fit anywhere across the lane (margin to truth faces)?"""
    out = []
    for s in np.arange(26.0, M0 - 1.0, ds):
        fl = HLN - (0.0 if G6.in_gap(s, 1) else G6.hedge_offset(s, 1)); fr = HLN - (0.0 if G6.in_gap(s, -1) else G6.hedge_offset(s, -1))
        out.append((round(float(s), 1), round((fl + fr) / 2 - r, 3)))
    return out

# ---------------------------------------------------------------- 3. pad / home sequences
def pads(n): return ['A', 'M', 'F'][:n]          # sitl/config_g6/drop_layout_default.json: drop order A, M, F; pickup F, M, A
def pad_pose(name, handle_to):
    """standing bin pose at a pad: handle facing 'lane' (up-lane, toward the house) or 'road' (down-lane)."""
    sp = SC.DROP_SPOTS(S)[name]; x, y, h = S.pose(sp['s'], sp['lat'], 0.0)
    byaw = h + (math.pi if handle_to == 'lane' else 0.0)      # byaw = direction the handle points
    return float(x), float(y), wrap(byaw), float(sp['s']), sp['lat']
def robot_at_bin(d, bx, by, byaw):
    """robot pose when the bin (handle pointing byaw) is carried: robot +x points along the handle if handle_dir=+1."""
    yaw = byaw if d.hd > 0 else wrap(byaw + math.pi); c, s_ = math.cos(yaw), math.sin(yaw)
    x = bx - (c * d.bin_c[0] - s_ * d.bin_c[1]); y = by - (s_ * d.bin_c[0] + c * d.bin_c[1]); return x, y, yaw
def sweep_ok(d, x, y, yaw, loaded, obst, dx_list):
    """straight move along robot x by each dx in dx_list: min region / bin margin of the footprint."""
    m = 9.0
    for dx in dx_list:
        P = d.fp(x + dx * math.cos(yaw), y + dx * math.sin(yaw), yaw, loaded)
        for p in P[::2]: m = min(m, region_margin(p)[0])
        for (bx, by, byaw) in obst: m = min(m, float(np.min(pt_box_dist(P, bx, by, byaw))) - BINGAP)
    return round(m, 3)
def line_pivot(d, x, y, yaw, r, dlist, loaded, obst, skip_last=False):
    """pivot centre constrained to the robot's own x-axis through (x, y, yaw), at signed distance dd in dlist; the straight
    move from the pose to the pivot point is swept too. Returns (best margin, dd)."""
    best = (-9.0, None)
    for dd in dlist:
        c = np.array([x + dd * math.cos(yaw), y + dd * math.sin(yaw)])
        m = disc_ok(c, r, obst)
        if m <= best[0]: continue
        mv = sweep_ok(d, x, y, yaw, loaded, obst, list(np.linspace(0, dd, max(2, int(abs(dd) / 0.1) + 1))))
        m = min(m, mv)
        if m > best[0]: best = (round(m, 3), round(float(dd), 2))
    return best
def zone_pivot(d, x, y, yaw, r, loaded, obst, s_rng=(-5.0, 5.0), lat_rng=(-2.2, 2.2), step=0.2):
    """180 deg pivot anywhere in a zone around the target pose (x, y, yaw), then a straight (crab-approximated S-curve) move at the
    final heading from the pivot centre to the target pose; both swept. Returns (margin, (ds, lat) of the pivot centre)."""
    s0, _ = LANE.project(np.array([x, y])); best = (-9.0, None)
    for ds in np.arange(s_rng[0], s_rng[1] + 1e-6, step):
        for lat in np.arange(lat_rng[0], lat_rng[1] + 1e-6, step):
            c = LANE.point(s0 + ds, lat); m = disc_ok(c, r, obst)
            if m <= best[0]: continue
            L_ = float(np.linalg.norm(c - [x, y])); n = max(2, int(L_ / 0.15) + 1); mv = 9.0
            for t in np.linspace(0, 1, n):
                P = d.fp(c[0] + t * (x - c[0]), c[1] + t * (y - c[1]), yaw, loaded)
                for p in P[::3]: mv = min(mv, region_margin(p)[0])
                for (bx, by, byaw) in obst: mv = min(mv, float(np.min(pt_box_dist(P, bx, by, byaw))) - BINGAP)
                if mv <= best[0]: break
            m = min(m, mv)
            if m > best[0]: best = (round(m, 3), (round(float(ds), 1), round(float(lat), 1)))
    return best
def sequence(d, n, handle_to, mission):
    """drop (carry bin k to its pad and leave) or pickup (fetch bin k from its pad). Forward plan: the robot drives the lane
    nose-first both ways (carry_dir). Every pivot is on the robot's own axis line through the pad pose (it may drive or reverse
    straight up to 4 m to a spot where the pivot fits); every straight move is swept. Margins in m (>0 = clear)."""
    order = pads(n) if mission == 'drop' else pads(n)[::-1]; steps = []; ok = True
    for k, pn in enumerate(order):
        standing = [pad_pose(q, handle_to)[:3] for q in order[:k]] if mission == 'drop' else [pad_pose(q, handle_to)[:3] for q in order[k + 1:]]
        bx, by, byaw, bs, blat = pad_pose(pn, handle_to); rx, ry, ryaw = robot_at_bin(d, bx, by, byaw)
        down = math.cos(wrap(ryaw - LANE.heading(bs))) > 0          # robot +x points down-lane when it holds this bin
        nose_down = down if d.cd > 0 else not down
        tgt = [(bx, by, byaw)]
        if mission == 'drop':
            if not nose_down:      # arrives nose-down loaded, must hold the bin nose-up: one loaded pivot on the axis line
                m = zone_pivot(d, rx, ry, ryaw, d.r_load, True, standing); steps.append(('%s loaded pivot 180 near the pad, then straight to it (margin, pivot ds,lat)' % pn, m[0], m[1]))
            else: steps.append(('%s arrives straight, no pivot' % pn, None))
            wd_dir = d.wd                                           # withdraw = robot drives along +x*withdraw, the bin leaves through the open end
            m = sweep_ok(d, rx, ry, ryaw, False, standing, [wd_dir * t for t in np.linspace(0.2, 0.9, 8)])   # the placed bin itself: MuJoCo G6
            to_road = (wd_dir > 0) == down
            steps.append(('%s withdraw 0.9 m %s' % (pn, 'toward the road' if to_road else 'up-lane'), m))
            if to_road:
                m = line_pivot(d, rx + wd_dir * 0.9 * math.cos(ryaw), ry + wd_dir * 0.9 * math.sin(ryaw), ryaw, d.r_empty,
                               [wd_dir * t for t in np.arange(0.0, 3.01, 0.1)], False, standing + tgt)
                steps.append(('%s empty pivot beyond the placed bin (margin, extra run m)' % pn, m[0], m[1]))
                steps.append(('%s pass the placed bin going home' % pn, pass_bin(d, bs, standing + tgt)))
        else:
            ap = -d.wd                                              # approach = robot moves along -x*withdraw onto the bin
            if nose_down:          # holds the bin nose-down: drive past, reverse up onto it; then a loaded pivot to go home
                steps.append(('%s pass the bin on the way down' % pn, pass_bin(d, bs, standing + tgt)))
                m = sweep_ok(d, rx, ry, ryaw, False, standing, [-ap * t for t in np.linspace(0.2, 1.5, 14)])
                steps.append(('%s run-in 1.5 m onto the bin' % pn, m))
                m = zone_pivot(d, rx, ry, ryaw, d.r_load, True, standing); steps.append(('%s loaded pivot 180 near the pad (margin, pivot ds,lat)' % pn, m[0], m[1]))
            else:                  # holds the bin nose-up: empty pivot on the axis line up-lane of the bin, then reverse onto it
                sx, sy = rx - ap * 1.5 * math.cos(ryaw), ry - ap * 1.5 * math.sin(ryaw)
                m = zone_pivot(d, sx, sy, ryaw, d.r_empty, False, standing + tgt)
                steps.append(('%s empty pivot up-lane, then reverse to the approach start (margin, pivot ds,lat)' % pn, m[0], m[1]))
                m = sweep_ok(d, rx, ry, ryaw, False, standing, [-ap * t for t in np.linspace(0.2, 1.5, 14)])
                steps.append(('%s run-in 1.5 m onto the bin' % pn, m))
    for st in steps:
        if st[1] is not None and st[1] <= 0: ok = False
    return dict(ok=ok, steps=steps)
def pass_bin(d, bs, obst):
    """best lateral position to pass standing bins near station bs (empty, along the lane, +/-2 m of track)."""
    best = -9
    for lat in np.arange(-2.0, 2.01, 0.05):
        m = 9.0
        for ds in np.arange(-2.0, 2.01, 0.25):
            s = bs + ds; x, y = LANE.point(s, lat); yaw = LANE.heading(s); P = d.fp(x, y, yaw, False)
            for p in P[::2]: m = min(m, region_margin(p)[0])
            for (bx, by, byaw) in obst: m = min(m, float(np.min(pt_box_dist(P, bx, by, byaw))) - BINGAP)
        best = max(best, m)
    return round(best, 3)

def yard_dock(d):
    """dock: robot parked at DOCK (s 4, lat 0) facing down-lane; charging dock box behind it. Home spots s 10 lat -1.4/-3.0/-4.6.
    180 deg pivot within 2 m of the dock pose with 0-3 bins at home (empty and loaded)."""
    dx, dy, dyaw = S.pose(SC.DOCK['s'], SC.DOCK['lat'], 0.0)
    dock_box = (dx - 0.8 * math.cos(dyaw), dy - 0.8 * math.sin(dyaw), dyaw)         # 0.74 x 0.58 fake-bin dock (ASSUMED position)
    homes = [S.pose(v['s'], v['lat'], math.pi) for v in SC.HOME_SPOTS.values()]       # handles face down-lane
    out = {}
    for nh in (0, 1, 2, 3):
        obst = [dock_box] + [h[:3] for h in homes[:nh]]
        for lab, r in (('empty', d.r_empty), ('loaded', d.r_load)):
            out['dock %s, %d bins home' % (lab, nh)] = pivot_search(r, (2.0, 6.5, -2.0, 2.0), obst)
            out['yard %s, %d bins home' % (lab, nh)] = pivot_search(r, (6.0, 24.0, -5.5, 5.5), obst, step=0.5)
    return out
def mouth(d):
    out = {}
    for n in (0, 1, 2, 3):
        for ht in ('lane', 'road'):
            obst = [pad_pose(q, ht)[:3] for q in pads(n)] if n else []
            for lab, r in (('empty', d.r_empty), ('loaded', d.r_load)):
                out['mouth %s, %d bins at road (handles to %s)' % (lab, n, ht)] = pivot_search(r, (M0 - 2.0, L - 6.0, -4.0, 4.0), obst)
    return out

if __name__ == '__main__':
    for f in sys.argv[1:]:
        D = json.load(open(f)); d = Design(D); R = dict(design=d.name, r_empty=round(d.r_empty, 3), r_load=round(d.r_load, 3),
                                                        pivot_D_empty=round(2 * d.r_empty, 2), pivot_D_load=round(2 * d.r_load, 2), half_w=d.half_w)
        R['sweep'] = {('%s %s' % ('down' if sg > 0 else 'up', 'loaded' if ld else 'empty')): lane_sweep(d, ld, sg) for sg in (1, -1) for ld in (True, False)}
        mins = [v['min_clear_m'] for v in R['sweep'].values()]
        R['sweep_min'] = min(mins); R['sweep_PASS_strict'] = R['sweep_min'] > 0; R['sweep_margin_vs_p95'] = round(R['sweep_min'] - EST_P95, 3)
        R['lane_pivot'] = lane_pivot_profile(d.r_empty); R['lane_pivot_loaded'] = lane_pivot_profile(d.r_load)
        R['lane_pivot_frac_empty'] = round(np.mean([m > 0 for _, m in R['lane_pivot']]), 3)
        R['lane_pivot_frac_loaded'] = round(np.mean([m > 0 for _, m in R['lane_pivot_loaded']]), 3)
        R['yard_dock'] = yard_dock(d); R['mouth'] = mouth(d)
        R['sequences'] = {'%s n%d handle-to-%s' % (ms, n, ht): sequence(d, n, ht, ms) for ms in ('drop', 'pickup') for n in (1, 2, 3) for ht in ('lane', 'road')}
        json.dump(R, open(os.path.join(H, 'res', 'lanefit_%s.json' % d.name), 'w'), indent=1, default=float)
        print(d.name, 'pivot D empty/loaded', R['pivot_D_empty'], R['pivot_D_load'], 'sweep min', R['sweep_min'], {k: v['min_clear_m'] for k, v in R['sweep'].items()})
        print(' lane pivot fraction empty/loaded', R['lane_pivot_frac_empty'], R['lane_pivot_frac_loaded'])
        for k, v in list(R['yard_dock'].items()) + list(R['mouth'].items()): print('  ', k, v)
        for k, v in R['sequences'].items(): print('  ', k, 'OK' if v['ok'] else 'FAIL', v['steps'])
