#!/usr/bin/env python3
"""Rev G4 figures -> out/G4/report/: fences + keep-outs + allowed drop areas + slots + alternates (2 panels), keep-left gap
plot, vehicle-stop timelines. Usage: figures_g4.py"""
import json, os, sys, math, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, '..'); G4 = os.path.join(ROOT, 'out', 'G4'); OUT = os.path.join(G4, 'report'); os.makedirs(OUT, exist_ok=True)
import scenarios as SC
from g4_features import DropAreas, DropLayout, CFG, BIN, box_segs, left_gap
from world import TUG
S = SC.site('real'); L = S.L
areas = DropAreas(S).install(); lay = DropLayout()

def fence_mask(ax, X, Y):
    Z = np.array([[1.0 if S.in_fence((x, y), ko=False) else 0.0 for x in X] for y in Y])
    ax.contourf(X, Y, Z, levels=[0.5, 1.5], colors=['#d8f0d8'], alpha=0.6)
    Zb = np.array([[S.boundary_dist((x, y)) for x in X] for y in Y]); ax.contour(X, Y, Zb, levels=[0.0], colors='red', linewidths=1.5)

def draw(ax, s_rng, frame_end, title):
    ss = np.arange(*s_rng, 0.5)
    P = np.array([S.lane.point(s, 0) for s in ss]); allp = np.vstack([np.array([S.lane.point(s, l) for s in ss]) for l in (-6, 6)])
    x0, y0 = allp.min(0) - 2; x1, y1 = allp.max(0) + 2
    X = np.linspace(x0, x1, 120); Y = np.linspace(y0, y1, 120); fence_mask(ax, X, Y)
    H = S.hedge; m = [(min(h[0], h[2]) > x0 and max(h[0], h[2]) < x1 and min(h[1], h[3]) > y0 and max(h[1], h[3]) < y1) for h in H]
    for h in H[np.array(m)]: ax.plot([h[0], h[2]], [h[1], h[3]], color='darkgreen', lw=2.5)
    R = S.road; ax.plot(R[:, 0], R[:, 1], color='grey', lw=14, alpha=0.4, solid_capstyle='butt')
    ax.plot(P[:, 0], P[:, 1], 'k--', lw=0.6)
    for k, A in areas.areas.items():
        ax.fill(A[:, 0], A[:, 1], facecolor='none', edgecolor='blue', hatch='..', lw=1.2, label='allowed drop area' if k == 'pad_lane' else None)
    for kk, ko in enumerate(areas.keepouts):
        ax.fill(ko['P'][:, 0], ko['P'][:, 1], facecolor='#ff9999', edgecolor='red', hatch='xx', lw=1.2, label='keep-out (user)' if kk == 0 else None)
    def binp(x, y, yaw, col, lw=1.5, ls='-'):
        _, poly = box_segs(x, y, yaw, BIN['d'], BIN['w']); poly = np.array(poly + [poly[0]]); ax.plot(poly[:, 0], poly[:, 1], color=col, lw=lw, ls=ls)
        ax.plot([x, x + 0.45 * math.cos(yaw)], [y, y + 0.45 * math.sin(yaw)], color=col, lw=1)
    if frame_end:
        others_all = [S.pose(h['s'], h['lat'], 0.0) for h in SC.HOME_SPOTS.values()]
        for k in lay.d['spots']:
            p = lay.bin_pose(S, k); binp(*p, 'black', 2); ax.annotate(k, p[:2], fontsize=9, weight='bold')
            sp = lay.spot(S, k)
            room = lambda xx, yy, yw: True
            alts = areas.alternates(k, p, sp['hedge_clear_m'], [lay.bin_pose(S, q) for q in lay.d['spots'] if q != k] + others_all, sp['spacing_m'])
            for i, a in enumerate(alts): binp(*a, 'orange', 0.8, '--')
    else:
        for c, h in SC.HOME_SPOTS.items():
            p = S.pose(h['s'], h['lat'], 0.0); binp(*p, 'black', 2); ax.annotate(c, p[:2], fontsize=8)
        p = S.pose(SC.HOME_SPOTS['black']['s'], SC.HOME_SPOTS['black']['lat'], 0.0)
        oth = [S.pose(h['s'], h['lat'], 0.0) for c, h in SC.HOME_SPOTS.items() if c != 'black'] + [lay.bin_pose(S, q) for q in lay.d['spots']]
        for a in areas.alternates('home', p, 0.3, oth, 1.0): binp(*a, 'orange', 0.8, '--')
        d = S.pose(SC.DOCK['s'], SC.DOCK['lat'], 0); ax.plot(d[0], d[1], 's', color='purple', ms=8, label='charging dock')
    ax.plot([], [], color='red', label='assumed private boundary (6 m from road c/l)'); ax.plot([], [], color='black', label='programmed slot')
    ax.plot([], [], color='orange', ls='--', label='auto alternates (black bin / per spot)'); ax.fill([], [], color='#d8f0d8', label='tug geofence (axle)')
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.set_title(title, fontsize=10); ax.legend(fontsize=6.5, loc='lower left')
    ax.set_xlabel('x east (m)'); ax.set_ylabel('y north (m)')

fig, axs = plt.subplots(1, 2, figsize=(13, 6.2))
draw(axs[0], (L - 34, L + 4), True, 'Bell-mouth + drop pad: inclusion fence, private boundary, allowed areas, keep-outs')
draw(axs[1], (0, 26), False, 'Yard: home slots, allowed home area, keep-out, alternates (black bin)')
plt.tight_layout(); plt.savefig(os.path.join(OUT, 'g4_fences.png'), dpi=110); plt.close()

# keep-left gap along the lane (s10b, both directions)
p = os.path.join(G4, 's10b_two_bin_pickup', 'trace.json')
if os.path.exists(p):
    tr = json.load(open(p))['trace']; fig, ax = plt.subplots(figsize=(11, 3.4))
    for sgn, col, lab in ((1, 'tab:blue', 'down (house -> road)'), (-1, 'tab:orange', 'up (road -> house)')):
        ss = []; gg = []
        for r in tr[::5]:
            if not r.get('kl') or abs(r['v']) < 0.1: continue
            s, lat = S.lane.project(np.array([r['x'], r['y']])); h = S.lane.heading(s)
            if math.cos(r['yaw'] - h) * sgn < 0.5: continue
            ss.append(s); gg.append(left_gap(S.lane.width, lat, sgn))
        ax.plot(ss, gg, '.', ms=1.2, color=col, label=lab)
    ax.axhspan(0.3, 0.5, color='green', alpha=0.15, label='spec 0.3-0.5 m'); ax.axhline(0, color='red', lw=0.8)
    ax.set_xlabel('lane station s (m from the house)'); ax.set_ylabel('gap tug left side -> left lane edge (m)'); ax.legend(fontsize=7, ncol=3)
    ax.set_title('Keep-left tracking, s10b (two-bin pickup, both directions, truth pose)', fontsize=10); plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'g4_keepleft.png'), dpi=110); plt.close()

# vehicle stop timelines
fig, axs = plt.subplots(1, 3, figsize=(13, 3.2))
for ax, n in zip(axs, ['s23a_vehicle_oncoming', 's23b_vehicle_behind', 's23c_vehicle_passing']):
    p = os.path.join(G4, n, 'trace.json')
    if not os.path.exists(p): continue
    tr = json.load(open(p))['trace']; t = []; v = []; g = []; hold = []
    for r in tr[::3]:
        if not r.get('veh'): continue
        x, y = r['x'], r['y']; d = min(math.hypot(q[0] - x, q[1] - y) - q[3] / 2 for q in r['veh'])
        t.append(r['t']); v.append(r['v']); g.append(d); hold.append(1 if r.get('vstop') else 0)
    if not t: continue
    ax.plot(t, g, label='vehicle centre-dist - L/2 (m)'); ax.plot(t, np.array(v) * 10, label='tug speed x10 (m/s)')
    ax.fill_between(t, 0, np.array(hold) * max(g), color='orange', alpha=0.3, label='VEHICLE HOLD'); ax.set_ylim(-1, 20)
    ax.set_title(n, fontsize=9); ax.set_xlabel('sim t (s)'); ax.legend(fontsize=6)
plt.tight_layout(); plt.savefig(os.path.join(OUT, 'g4_vehicle.png'), dpi=110); plt.close()
print('figures ok')
