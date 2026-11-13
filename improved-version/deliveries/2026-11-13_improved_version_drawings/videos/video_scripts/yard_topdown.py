#!/usr/bin/env python3
"""Video 3: top-down replay of the three-bin drop leaving the yard (seed 7), from the saved driving-test traces.
Left: the other agent's code unmodified. Right: with the planned yard-exit path. Nothing is re-simulated.
Hedges, lane centre-line, bins and footprints come from the same world model the tests used."""
import sys, os, json, math, subprocess
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
SC = '/home/claude/b2f_run/sitl/b2f/scripts'
sys.path.insert(0, SC); sys.path.insert(0, os.path.join(SC, '..', 'scripts_base'))
import b2f_world as BW, b2f_scen as SCN
from scene import seg_dist
S = SCN.S; ROB = BW.ROB; BIN_T = BW.BIN_T
OUT = '/home/claude/s0/video/out'; os.makedirs(OUT, exist_ok=True)
RUNS = [('Their code: slides sideways while driving on', '/home/claude/sitl_out/base472/runs/s3a__s7', 169.0),
        ('Fix: a planned curve to the lane centre', '/home/claude/sitl_out/fix4/runs/s3a__s7', 172.0)]
SPEED = 3.0; FPS = 25; LEAD = 3.0; SPAN = 68.0      # seconds of mission time shown per panel, measured from the start of the move
XL, YL = (-17.5, -2.0), (-9.0, 8.5)
BINCOL = dict(black=(0.25, 0.25, 0.27), green=(0.20, 0.55, 0.25), brown=(0.55, 0.36, 0.18))

def rect(cx, cy, yaw, x0, x1, hw):
    c, s = math.cos(yaw), math.sin(yaw); P = np.array([[x0, -hw], [x1, -hw], [x1, hw], [x0, hw]])
    return np.c_[cx + P[:, 0] * c - P[:, 1] * s, cy + P[:, 0] * s + P[:, 1] * c]

H = np.array(S.hedge_truth); mH = (H[:, [0, 2]].min(1) < XL[1] + 2) & (H[:, [0, 2]].max(1) > XL[0] - 2) & (H[:, [1, 3]].min(1) < YL[1] + 2) & (H[:, [1, 3]].max(1) > YL[0] - 2); H = H[mH]
CL = np.array([S.lane.point(s, 0.0) for s in np.arange(0.0, 45.0, 0.5)])
MARK = {s: S.lane.point(float(s), 0.0) for s in (10, 20, 30)}

def clearance(q):
    """smallest distance from the robot + carried bin outline to the truth hedge (m)"""
    P = BW.rect_pts(q['x'], q['y'], q['yaw'], ROB['x0'], ROB['x1'], ROB['hw'], 8)
    if q.get('cb'):
        T = BIN_T[q['bins'][q['carry']][4]]; P = np.r_[P, rect(q['cb'][0], q['cb'][1], q['cb'][2], -T['D'] / 2, T['D'] / 2, T['W'] / 2)]
    return float(np.min(seg_dist(P[:, None, :], H[None, :, :2], H[None, :, 2:])))

data = []
for title, d, t_move in RUNS:
    tr = json.load(open(os.path.join(d, 'trace.json')))['trace']; res = json.load(open(os.path.join(d, 'result.json')))
    tr = [q for q in tr if t_move - LEAD - 0.5 <= q['t'] <= t_move + SPAN + 0.5]
    data.append(dict(title=title, tr=tr, t=np.array([q['t'] for q in tr]), t0=t_move - LEAD, res=res, cmin=9.0))

fig = plt.figure(figsize=(12.8, 7.2), dpi=100); fig.patch.set_facecolor('#12141a')
axs = [fig.add_axes([0.012 + k * 0.494, 0.095, 0.482, 0.785]) for k in range(2)]
fig.text(0.012, 0.955, 'Three-bin evening, first trip: leaving the yard with the 140 L bin that is kept furthest to the side', color='white', fontsize=15.5, fontweight='bold', va='center')
fig.text(0.012, 0.066, 'Blue: robot (white bar = nose).  Brown: the 140 L bin being carried.  Grey and green boxes: the other two bins at home.  Yellow: path driven.  Green lines: hedges.  Dashed: lane centre.',
         color='#dddddd', fontsize=9, va='center')
fig.text(0.012, 0.030, 'Top-down replay of the driving-software simulation (seed 7, ArduRover 4.7.2 SITL), 3x speed. Not field footage. The yard layout, hedges and bin positions are assumed, not surveyed.',
         color='#aaaaaa', fontsize=8.5, va='center')
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '1280x720', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                       '-pix_fmt', 'yuv420p', '-movflags', '+faststart', os.path.join(OUT, '3_three_bin_drop_yard_exit_before_after.mp4')], stdin=subprocess.PIPE)
nfr = int((LEAD + SPAN) / SPEED * FPS) + FPS * 2
for n in range(nfr):
    tl = min(n / FPS * SPEED, LEAD + SPAN)
    for k, (ax, D) in enumerate(zip(axs, data)):
        ax.clear(); ax.set_facecolor('#8f8a78'); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_color('#555555')
        ax.plot(CL[:, 0], CL[:, 1], color='#d8d4c4', lw=1.2, ls=(0, (6, 5)), zorder=1)
        for s_, p in MARK.items(): ax.text(p[0] + 0.25, p[1] + 0.1, '%d m' % s_, color='#e8e4d4', fontsize=8, zorder=2)
        for h in H: ax.plot([h[0], h[2]], [h[1], h[3]], color='#1f5a25', lw=7, solid_capstyle='round', zorder=3)
        i = int(np.clip(np.searchsorted(D['t'], D['t0'] + tl), 0, len(D['t']) - 1)); q = D['tr'][i]; ended = (D['t0'] + tl) > D['t'][-1] + 0.3
        P = np.array([[r['x'], r['y']] for r in D['tr'][:i + 1]]); ax.plot(P[:, 0], P[:, 1], color='#ffd23a', lw=2.0, zorder=4)
        for name, b in q['bins'].items():
            T = BIN_T[b[4]]
            if b[3] == 'carried' and q.get('cb'): bx, by, byaw = q['cb']
            else: bx, by, byaw = b[0], b[1], b[2]
            ax.add_patch(Polygon(rect(bx, by, byaw, -T['D'] / 2, T['D'] / 2, T['W'] / 2), closed=True, fc=BINCOL[name], ec='black', lw=0.8, zorder=7 if b[3] == 'carried' else 5))
        ax.add_patch(Polygon(rect(q['x'], q['y'], q['yaw'], ROB['x0'], ROB['x1'], ROB['hw']), closed=True, fc='#3c6fb0', ec='white', lw=1.2, alpha=0.92, zorder=6))
        c, s = math.cos(q['yaw']), math.sin(q['yaw']); ax.plot([q['x'] + 0.75 * c, q['x'] + 1.05 * c], [q['y'] + 0.75 * s, q['y'] + 1.05 * s], color='white', lw=3, zorder=8)
        cl = clearance(q); D['cmin'] = min(D['cmin'], cl)
        ax.set_title(D['title'], color='white', fontsize=13, fontweight='bold', loc='left', pad=6)
        stopped = (k == 0 and (ended or q['mode'] == 'HOLD'))
        ax.text(0.02, 0.97, ('Scored smallest hedge clearance in this run: %.2f m (limit 0.124 m)' % D['res']['hedge_min_m']) if stopped else ('Nearest hedge now: %.2f m (limit 0.124 m)' % cl),
                transform=ax.transAxes, color='white', fontsize=10.5, va='top', bbox=dict(fc='#12141a', ec='none', alpha=0.75, pad=4), zorder=10)
        if stopped:
            ax.text(0.02, 0.905, 'STOPPED: the firmware fence halts the robot at the hedge end', transform=ax.transAxes, color='#ff7b6b', fontsize=11.5, fontweight='bold',
                    va='top', bbox=dict(fc='#12141a', ec='none', alpha=0.8, pad=4), zorder=10)
        elif k == 1 and q['state'].startswith('LANE'):
            ax.text(0.02, 0.905, 'On the lane centre before the hedges begin; carries on to the road', transform=ax.transAxes, color='#8be29b', fontsize=11.5, fontweight='bold',
                    va='top', bbox=dict(fc='#12141a', ec='none', alpha=0.8, pad=4), zorder=10)
    fig.canvas.draw(); ff.stdin.write(np.asarray(fig.canvas.buffer_rgba()).tobytes())
    if n % 100 == 0: print('frame', n, 'of', nfr, 'tl %.1f' % tl, [round(D['cmin'], 3) for D in data], flush=True)
ff.stdin.close(); ff.wait(); print('WROTE video 3; smallest clearances (their code, fix):', [round(D['cmin'], 3) for D in data], '| result files say', [D['res']['hedge_min_m'] for D in data])
