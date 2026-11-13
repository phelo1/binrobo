#!/usr/bin/env python3
"""Figures for COMPARE_B1_vs_RevH: fig1 plan footprints + pivot circles, fig2 lane swept clearance, fig3 Rev H hang / grab outcome.
Writes docs/reviews/fig_cmp_*.png"""
import os, sys, json, math, glob
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
H = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(H, 'res'); OUT = os.path.join(H, '..', '..', '..', '..', 'docs', 'reviews')

def fig1():
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.6))
    for ax, nm in zip(axs, ('B1', 'RevH')):
        D = json.load(open(os.path.join(H, 'designs', nm + '.json'))); LF = json.load(open(os.path.join(RES, 'lanefit_%s.json' % nm)))
        for x0, x1, y0, y1, lab in D['parts']:
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='#9db8de' if 'envelope' not in lab else 'none', ec='#2c4a75', lw=0.8,
                                   ls='-' if 'envelope' not in lab else ':'))
        ax.add_patch(Polygon(D['bin'], closed=True, fc='#f6c9b3', ec='#d4582a', lw=1.0, alpha=0.8))
        ax.add_patch(Circle((0, 0), LF['r_load'], fc='none', ec='k', ls='--', lw=0.8))
        ax.plot(0, 0, 'k+')
        ax.set_aspect('equal'); ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.3, 1.3); ax.grid(alpha=0.3)
        ttl = {'B1': 'B1 (comb on the handle-side receiver)', 'RevH': 'Rev H (comb on the bin front wall)'}[nm]
        ax.set_title('%s\nwidth %.2f m, pivot dia. %.2f m loaded' % (ttl, 2 * D['half_w'], LF['pivot_D_load']), fontsize=9)
        ax.set_xlabel('x (m), + = nose / castor end'); ax.set_ylabel('y (m)')
        ax.annotate('handle', xy=(0.34 if nm == 'B1' else -0.25, 0.0), fontsize=7, color='#d4582a', ha='center')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_cmp_1_plan.png'), dpi=150); plt.close(fig)

def fig2():
    fig, ax = plt.subplots(figsize=(10, 3.6))
    for nm, col in (('B1', '#2c4a75'), ('RevH', '#d4582a')):
        LF = json.load(open(os.path.join(RES, 'lanefit_%s.json' % nm)))
        for k, ls in (('down loaded', '-'), ('up loaded', ':')):
            pr = LF['sweep'][k]['prof']; ax.plot([p[0] for p in pr], [p[1] for p in pr], ls, color=col, lw=0.9, label='%s %s' % (nm, k))
    ax.axhline(0, color='k', lw=0.8); ax.axhline(0.124, color='grey', lw=0.6, ls='--'); ax.text(30, 0.135, 'SITL lateral estimate error p95 0.124 m', fontsize=7, color='grey')
    ax.axvspan(500, 516, color='#f2d0d0', alpha=0.6); ax.text(502, 1.1, 's 500-516\n2.9 m between faces', fontsize=7)
    ax.set_xlabel('lane station s (m from the house)'); ax.set_ylabel('min clearance to the truth hedge face (m)')
    ax.set_ylim(-0.1, 1.4); ax.grid(alpha=0.3); ax.legend(fontsize=7, ncol=4, loc='upper left')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_cmp_2_lane.png'), dpi=150); plt.close(fig)

def fig3():
    """G1 outcome per bin type: B1 final, B1 full-width comb, Rev H raw, Rev H FH1+FH2"""
    sets = [('B1 final (160 mm comb)', os.path.join(H, '..', 'it1', 'res'), 'B1_', '_f9'), ('B1 640 mm self-aligning comb', RES, 'B1_', '_f9_fwp32'),
            ('Rev H raw (as designed)', RES, 'H_', '_raw'), ('Rev H + FH1 + FH2', RES, 'H_', '_fx')]
    bins = ['WEB140', 'ESE240SL', 'ESE240CL', 'ESE240SL250', 'ESE140CL']
    fig, ax = plt.subplots(figsize=(10, 4.2)); w = 0.2
    for j, (lab, rd, pf, tg) in enumerate(sets):
        cap, fh = [], []
        for b in bins:
            f = os.path.join(rd, '%sgrab_%s%s.json' % (pf, b, tg))
            if os.path.exists(f): d = json.load(open(f)); cap.append(d['captured']); fh.append(d['false_holds'])
            else: cap.append(0); fh.append(0)
        xs = [i + (j - 1.5) * w for i in range(len(bins))]
        ax.bar(xs, cap, w, label=lab)
        for x, c_, f_ in zip(xs, cap, fh):
            if f_: ax.text(x, c_ + 0.6, '%d\nFH' % f_, ha='center', va='bottom', fontsize=7, color='red', fontweight='bold')
    ax.axhline(28, color='k', ls='--', lw=0.7); ax.text(4.45, 28.4, 'pass 28/30', fontsize=7)
    ax.set_xticks(range(len(bins))); ax.set_xticklabels(['Weber 140', 'ESE 240 SL', 'ESE 240 CL', 'SL 250 mm (extra)', 'ESE 140 CL (extra)'], fontsize=8)
    ax.set_ylabel('captured of 30'); ax.set_ylim(0, 34); ax.legend(fontsize=7, ncol=4, loc='upper center', bbox_to_anchor=(0.5, -0.1)); ax.grid(axis='y', alpha=0.3)
    ax.set_title('G1 grab Monte Carlo (FH = false hold: claimed but not lifted)', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_cmp_3_grab.png'), dpi=150); plt.close(fig)

if __name__ == '__main__':
    for f in sys.argv[1:] or ('fig1', 'fig2', 'fig3'): globals()[f]()
