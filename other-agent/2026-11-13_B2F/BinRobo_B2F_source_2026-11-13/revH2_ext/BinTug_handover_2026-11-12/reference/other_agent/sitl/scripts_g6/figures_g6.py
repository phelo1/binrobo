#!/usr/bin/env python3
"""Rev G6 figures -> out/G6/report/*.png (matplotlib). Usage: figures_g6.py [outdir_name=G6]
 fig_lateral_s25.png  : s25a/s25b/s25c truth lateral vs the commanded line along the lane + truth hedge faces (keep-left legs)
 fig_lateral_zoom.png : s25a zooms: the s=56-92 bends and the s=495-520 narrowing
 fig_drop_A.png       : s1 handles-out drop at spot A (x-y): tug path, bin, pads, private boundary, geofence
 fig_pickup_flip.png  : s10b / s20b pickup flips at the pads (x-y): tug path, bin track
 fig_yard_s24a.png    : s24a yard: parked car, planned U-turn swept area, tug path, bin final pose
 fig_hitch.png        : hitch angle histograms (towing) for the key runs
 fig_energy.png       : energy replay SOC (from out/G6/energy_*.json)"""
import json, os, sys, math, glob, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, '..'); TAG = sys.argv[1] if len(sys.argv) > 1 else 'G6'; G = os.path.join(ROOT, 'out', TAG)
OUT = os.path.join(G, 'report'); os.makedirs(OUT, exist_ok=True)
import scenarios as SC, g6_features as G6
from g4_features import DropLayout, box_segs
from world import TUG, BIN
S = SC.site('real'); L = S.L; lay = DropLayout()


def load(sc):
    p = os.path.join(G, sc)
    try: return json.load(open(os.path.join(p, 'result.json'))), json.load(open(os.path.join(p, 'trace.json')))['trace']
    except Exception: return None, None


def hedge_faces(ss):
    out = {}
    for side in (1, -1):
        v = np.array([side * (G6.HL_NOM - G6.hedge_offset(s, side)) if not G6.in_gap(s, side) else np.nan for s in ss]); out[side] = v
    return out


def fig_lateral():
    runs = [('s25a_corridor_down', 'down (full bin), corridor lateral'), ('s25b_rtk_only_down', 'down, RTK-only baseline'), ('s25c_corridor_up', 'up (empty bin), corridor lateral')]
    fig, axs = plt.subplots(len(runs), 1, figsize=(11, 8.5), sharex=True)
    for ax, (sc, lab) in zip(axs, runs):
        r, T = load(sc)
        ss = np.arange(25, L - 20, 0.5); hf = hedge_faces(ss)
        ax.plot(ss, hf[1], color='darkgreen', lw=1); ax.plot(ss, hf[-1], color='darkgreen', lw=1)
        ax.fill_between(ss, hf[1], 2.6, color='darkgreen', alpha=0.15); ax.fill_between(ss, -2.6, hf[-1], color='darkgreen', alpha=0.15)
        if T:
            rows = [x for x in T if 'tl' in x and abs(x['v']) > 0.05 and 25 < x['ts'] < L - 20]
            s_ = np.array([x['ts'] for x in rows]); tl = np.array([x['tl'] for x in rows])
            ax.plot(s_, tl + TUG['half_w'], color='tab:blue', lw=0.6, alpha=0.6); ax.plot(s_, tl - TUG['half_w'], color='tab:blue', lw=0.6, alpha=0.6)
            ax.plot(s_, tl, color='tab:blue', lw=1.0, label='tug axle (truth) +/- half-width')
            lt = [(x['ts'], x['ltg']) for x in rows if x.get('ltg') is not None]
            if lt: ax.plot(*zip(*lt), color='orange', lw=0.8, ls='--', label='commanded line')
            la = r['lateral']; x_ = la.get('xte') or {}
            ax.set_title('%s: %s | %s | XTE SD %.2f m, P95 %.2f m | hedge clearance min %s m | hitch max %.1f deg, stop frames %d'
                         % (sc[:4], lab, r['result'], x_.get('sd', float('nan')), x_.get('p95_abs', float('nan')), la.get('hedge_clear_min_m'),
                            r['hitch_max_deg'], r['hitch_limit_hits']), fontsize=8)
        else: ax.set_title('%s: no result' % sc, fontsize=8)
        ax.set_ylim(-2.6, 2.6); ax.set_ylabel('lateral (m)'); ax.grid(alpha=0.3)
    axs[0].legend(fontsize=7, loc='lower right'); axs[-1].set_xlabel('lane station s (m from the house)')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_lateral_s25.png'), dpi=110); plt.close(fig)
    r, T = load('s25a_corridor_down')
    if not T: return
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    for ax, (a, b) in zip(axs, ((52, 95), (490, 522))):
        ss = np.arange(a, b, 0.25); hf = hedge_faces(ss)
        ax.plot(ss, hf[1], color='darkgreen'); ax.plot(ss, hf[-1], color='darkgreen')
        rows = [x for x in T if 'tl' in x and a < x['ts'] < b and abs(x['v']) > 0.05]
        s_ = np.array([x['ts'] for x in rows]); tl = np.array([x['tl'] for x in rows]); hi = np.array([x['hitch'] or 0 for x in rows])
        ax.plot(s_, tl, color='tab:blue', label='axle (truth)'); ax.plot(s_, tl + TUG['half_w'], 'tab:blue', lw=0.5); ax.plot(s_, tl - TUG['half_w'], 'tab:blue', lw=0.5)
        lt = [(x['ts'], x['ltg']) for x in rows if x.get('ltg') is not None]
        if lt: ax.plot(*zip(*lt), color='orange', ls='--', lw=0.8, label='commanded line')
        ax2 = ax.twinx(); ax2.plot(s_, hi, color='tab:red', lw=0.6, alpha=0.7); ax2.set_ylim(-30, 30); ax2.set_ylabel('hitch (deg)', color='tab:red', fontsize=8)
        ax.set_ylim(-2.3, 2.3); ax.set_title('s25a s=%d-%d m: %s' % (a, b, 'bends (survey kinks 25-46 deg)' if a < 100 else 'overgrown narrowing (2.9 m)'), fontsize=9)
        ax.set_xlabel('s (m)'); ax.set_ylabel('lateral (m)'); ax.grid(alpha=0.3)
    axs[0].legend(fontsize=7); fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_lateral_zoom.png'), dpi=110); plt.close(fig)


def xy_base(ax, s_rng, lat_rng=(-5, 5)):
    ss = np.arange(*s_rng, 0.5); allp = np.vstack([np.array([S.lane.point(s, l) for s in ss]) for l in lat_rng])
    x0, y0 = allp.min(0) - 1.5; x1, y1 = allp.max(0) + 1.5
    X = np.linspace(x0, x1, 110); Y = np.linspace(y0, y1, 110)
    Z = np.array([[1.0 if S.in_fence((x, y), ko=False) else 0.0 for x in X] for y in Y]); ax.contourf(X, Y, Z, levels=[0.5, 1.5], colors=['#e3f3e3'])
    Zb = np.array([[S.boundary_dist((x, y)) for x in X] for y in Y]); ax.contour(X, Y, Zb, levels=[0.0], colors='red', linewidths=1.2)
    H = S.hedge
    m = [(min(h[0], h[2]) > x0 and max(h[0], h[2]) < x1 and min(h[1], h[3]) > y0 and max(h[1], h[3]) < y1) for h in H]
    for h in H[np.array(m)]: ax.plot([h[0], h[2]], [h[1], h[3]], color='darkgreen', lw=2.2)
    R = S.road; ax.plot(R[:, 0], R[:, 1], color='grey', lw=12, alpha=0.35, solid_capstyle='butt')
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.grid(alpha=0.25)


def box(ax, x, y, yaw, Lx, Wx, col, lw=1.5, ls='-', fill=None):
    _, poly = box_segs(x, y, yaw, Lx, Wx); poly = np.array(poly + [poly[0]])
    if fill: ax.fill(poly[:, 0], poly[:, 1], color=fill, alpha=0.5)
    ax.plot(poly[:, 0], poly[:, 1], color=col, lw=lw, ls=ls)


def binp(ax, x, y, yaw, col, lw=1.5, ls='-'):
    box(ax, x, y, yaw, BIN['d'], BIN['w'], col, lw, ls); ax.plot([x, x + 0.45 * math.cos(yaw)], [y, y + 0.45 * math.sin(yaw)], color=col, lw=1.2)


def path(ax, T, t0=None, t1=None, col='tab:blue', lab='tug path', binc='tab:purple'):
    rows = [x for x in T if (t0 is None or x['t'] >= t0) and (t1 is None or x['t'] <= t1)]
    ax.plot([x['x'] for x in rows], [x['y'] for x in rows], color=col, lw=1, label=lab)
    bt = [(x['bin'][0], x['bin'][1]) for x in rows if x.get('bin')]
    if bt: ax.plot(*zip(*bt), color=binc, lw=0.6, ls=':', label='bin centre track')


def fig_drop():
    r, T = load('s1_morning')
    if not T: return
    fig, ax = plt.subplots(figsize=(8, 6.5)); xy_base(ax, (L - 26, L - 4))
    for k in lay.d['spots']:
        p = lay.bin_pose(S, k); binp(ax, *p, 'black', 1, '--'); ax.annotate(k, (p[0] + 0.3, p[1] + 0.3), fontsize=10, weight='bold')
    ev = [e for e in r['events'] if 'bin released' in e['text']]
    t_rel = ev[0]['t'] if ev else None
    path(ax, [x for x in T if L - 30 < x.get('ts', 0) or (x.get('ts') is None)], lab='tug axle path')
    last = T[-1]
    if last.get('bin'): binp(ax, *last['bin'][:3], 'tab:purple', 2.2)
    pl = (r['metrics'].get('placement') or [{}])[0]
    ax.set_title('s1 handles-out drop at spot A (%s): placement %.2f m / %+.0f deg, solo pivot %s' % (r['result'], pl.get('err_m', float('nan')), pl.get('yaw_err_deg', float('nan')),
                 (r['metrics'].get('solo_turn') or [{}])[0].get('at')), fontsize=9)
    ax.legend(fontsize=7, loc='upper left'); fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_drop_A.png'), dpi=110); plt.close(fig)


def fig_flip():
    fig, axs = plt.subplots(1, 2, figsize=(12, 5.5))
    for ax, sc in zip(axs, ('s10b_two_bin_pickup', 's20b_three_bin_pickup')):
        r, T = load(sc); xy_base(ax, (L - 26, L - 6))
        if not T: ax.set_title('%s: no result' % sc); continue
        for k in lay.d['spots']:
            p = lay.bin_pose(S, k); binp(ax, *p, 'black', 1, '--'); ax.annotate(k, (p[0] + 0.3, p[1] + 0.3), fontsize=10, weight='bold')
        rows = [x for x in T if x.get('ts', 0) > L - 28]
        ax.plot([x['x'] for x in rows], [x['y'] for x in rows], color='tab:blue', lw=0.7, label='tug axle path (near the pads)')
        for x in rows[::400]:
            if x.get('bin'): binp(ax, *x['bin'][:3], 'tab:purple', 0.5)
        fl = r['metrics'].get('flips') or []
        ax.set_title('%s (%s): %d flip(s) by orbit-nudge %s' % (sc[:4], r['result'], len(fl), [f['rot_deg'] for f in fl]), fontsize=9)
        ax.legend(fontsize=7, loc='upper left')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_pickup_flip.png'), dpi=110); plt.close(fig)


def fig_yard():
    r, T = load('s24a_home_slot_car')
    if not T: return
    import companion as C, types
    fig, ax = plt.subplots(figsize=(8, 7)); xy_base(ax, (0, 22), (-7, 7))
    sc = SC.get('s24a_home_slot_car')
    for o in sc['world'].obst: box(ax, o['x'], o['y'], o['yaw'], o['L'], o['W'], 'red', 2, fill='#ffaaaa')
    o_ = types.SimpleNamespace(S=S)
    for b, hs in SC.HOME_SPOTS.items():
        p = S.pose(hs['s'], hs['lat'], 0.0); binp(ax, *p, 'black', 1, '--')
    Q = C.Companion.yard_uturn_sweep(o_, SC.HOME_SPOTS['black']['s'], SC.HOME_SPOTS['black']['lat'])
    ax.scatter(Q[:, 0], Q[:, 1], s=2, color='orange', alpha=0.4, label='planned U-turn swept area (primary slot)')
    ht = r['metrics'].get('home_target') or None
    path(ax, [x for x in T if x.get('ts', 99) < 40], lab='tug axle path')
    last = T[-1]
    if last.get('bin'): binp(ax, *last['bin'][:3], 'tab:purple', 2.2)
    us = r['metrics'].get('uturn_stops') or []
    ax.set_title('s24a car on the home slot (%s): %s; U-turn runtime stops %d' % (r['result'], r['outcome'][:60], len(us)), fontsize=9)
    ax.legend(fontsize=7, loc='upper left'); fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_yard_s24a.png'), dpi=110); plt.close(fig)


def fig_hitch():
    fig, ax = plt.subplots(figsize=(8, 4)); bins = np.arange(-30, 31, 1)
    for sc in ('s25a_corridor_down', 's25c_corridor_up', 's1_morning', 's20a_three_bin_drop', 's20b_three_bin_pickup'):
        r, T = load(sc)
        if not T: continue
        h = [x['hitch'] for x in T if x.get('att') and x.get('hitch') is not None and abs(x['v']) > 0.05]
        if h: ax.hist(h, bins=bins, histtype='step', lw=1.2, density=True, label='%s (max %.1f)' % (sc[:4], max(abs(v) for v in h)))
    cap = G6.HITCH_CAP_DEG; ax.axvline(cap, color='red'); ax.axvline(-cap, color='red'); ax.axvline(cap - 3, color='red', ls=':'); ax.axvline(-cap + 3, color='red', ls=':')
    ax.set_xlabel('kingpin angle while towing (deg); red = 28 deg stop, dotted = governor limit'); ax.set_ylabel('density'); ax.legend(fontsize=7); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_hitch.png'), dpi=110); plt.close(fig)


def fig_energy():
    files = sorted(glob.glob(os.path.join(G, 'energy_*.json')))
    if not files: return
    fig, ax = plt.subplots(figsize=(10, 4.2)); labels = []; k = 0
    for f in files:
        d = json.load(open(f))
        for r in d['replay']:
            col = {12: 'tab:red', 20: 'tab:green', 25: 'tab:blue'}[r['pack_ah']]
            ax.bar(k, 100 * r['soc_end'], color=col, alpha=0.9 if r['case'] == 'A' else 0.45, edgecolor='black' if r['complete'] else 'red', lw=1.5)
            ax.text(k, 100 * r['soc_end'] + 1.5, '%d%%' % round(100 * r['soc_end']), ha='center', fontsize=7)
            labels.append('%s\n%s %dWh' % (d['label'], r['case'], r['pack_wh'])); k += 1
    ax.axhline(10, color='red', ls=':', label='10 % planning reserve'); ax.set_xticks(range(k)); ax.set_xticklabels(labels, fontsize=6)
    ax.set_ylabel('SOC at the end of s20b (%)'); ax.set_title('Energy replay: A = as designed (overnight heater recharge), B = 0 C derate, no charge at all; red edge = not all bins moved', fontsize=9)
    ax.legend(fontsize=7); ax.grid(alpha=0.3, axis='y'); fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_energy.png'), dpi=110); plt.close(fig)


if __name__ == '__main__':
    for f in (fig_lateral, fig_drop, fig_flip, fig_yard, fig_hitch, fig_energy):
        try: f(); print('ok', f.__name__)
        except Exception as e:
            import traceback; traceback.print_exc(); print('FAILED', f.__name__, e)
