#!/usr/bin/env python3
"""Rev H2 general arrangement: side, plan and front views with the main dimensions, the bin-interface explainer, and the cut list.
Writes ../fig/ga_revH2.png, ../fig/bin_interface.png, ../results/cut_list_revH2.csv, ../results/plate_list_revH2.csv and
../reference_out/RevH2_lanefit_design.json (footprint in the format of the other agent's cmp/lanefit.py).
Dimensions are read from params.py. Concept stage: not a drawing to build from."""
import os, sys, csv, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle, FancyArrowPatch
import params as P
import make_iso as MI
R = P.ROBOT; SURF, INK, INK2 = MI.SURF, MI.INK, MI.INK2
FIG = os.path.join(HERE, '..', 'fig'); RES = os.path.join(HERE, '..', 'results'); REF = os.path.join(HERE, '..', 'reference_out')
for d in (FIG, RES, REF): os.makedirs(d, exist_ok=True)
MX, NOSE, TIP, GI, PX, HT = R['mast_x'], R['nose_tip_x'], R['leg_tip_x'], R['leg_inner_gap'] / 2, R['pad_x'], R['height']


def D(ax, v, p0, p1, text, off=(0, 0), ha='center', va='center', ext=()):
    for e0, e1 in ext:
        a = v.px(e0); b = v.px(e1); ax.plot([a[0], b[0]], [a[1], b[1]], color=INK2, lw=0.5, zorder=5)
    a = v.px(p0); b = v.px(p1)
    ax.annotate('', xy=a, xytext=b, arrowprops=dict(arrowstyle='<->', color=INK, lw=0.8, shrinkA=0, shrinkB=0, mutation_scale=8), zorder=6)
    ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], text, fontsize=8.5, color=INK, ha=ha, va=va, zorder=7, bbox=dict(fc=SURF, ec='none', pad=1.2, alpha=0.9))


def ga():
    comb = P.BINS['ESE240SL']['comb']; sc = MI.Scene(); MI.add_robot(sc, comb)      # comb drawn at a 240 L bin's lip height, no bin
    fig = plt.figure(figsize=(16.5, 11.0)); fig.patch.set_facecolor(SURF)
    S = 520.0                                                                        # px per metre, same in every view
    # ---------------- side elevation (seen from the robot's right, nose to the right)
    szs = (1400, 1000); axs = fig.add_axes([0.01, 0.40, 0.56, 0.55]); vs = MI.View(-90, S, (0, 0), szs, el=0.0)
    vs = MI.View(-90, S, (430, 860), szs, el=0.0); img, _ = MI.raster(sc, vs)
    axs.imshow(img, interpolation='nearest'); axs.set_xlim(0, szs[0]); axs.set_ylim(szs[1], 0); axs.axis('off')
    g0 = vs.px((-0.75, 0, 0)); g1 = vs.px((1.45, 0, 0)); axs.plot([g0[0], g1[0]], [g0[1], g1[1]], color=INK2, lw=1.0, zorder=4)
    y = -0.6
    D(axs, vs, (TIP, y, -0.14), (NOSE, y, -0.14), '%.0f overall' % ((NOSE - TIP) * 1000), off=(0, 12), ext=[((TIP, y, 0), (TIP, y, -0.17)), ((NOSE, y, 0), (NOSE, y, -0.17))])
    D(axs, vs, (0, y, -0.07), (R['nose_x'], y, -0.07), '%.0f axle to castor' % (R['nose_x'] * 1000), off=(0, -10), ext=[((0, y, 0), (0, y, -0.10)), ((R['nose_x'], y, 0), (R['nose_x'], y, -0.10))])
    D(axs, vs, (TIP, y, -0.07), (0, y, -0.07), '%.0f' % (-TIP * 1000), off=(0, -10))
    D(axs, vs, (0, y, 1.47), (PX, y, 1.47), '%.0f to the bin\'s front wall' % (PX * 1000), off=(-70, -12), ext=[((0, y, 0.33), (0, y, 1.50)), ((PX, y, 1.10), (PX, y, 1.50))])
    D(axs, vs, (0, y, 1.56), (MX, y, 1.56), '%.0f to the mast centre' % (MX * 1000), off=(60, -12), ext=[((MX, y, HT), (MX, y, 1.59)), ((0, y, 1.50), (0, y, 1.59))])
    D(axs, vs, (1.12, y, 0), (1.12, y, HT), '%.0f mast' % (HT * 1000), off=(42, 0), ext=[((MX, y, HT), (1.15, y, HT))])
    D(axs, vs, (1.30, y, 0), (1.30, y, 0.31), '310 rail top', off=(52, 0), ext=[((NOSE, y, 0.31), (1.33, y, 0.31))])
    D(axs, vs, (-0.60, y, R['comb_z_min']), (-0.60, y, R['comb_z_max']), 'comb travel\n%.0f to %.0f' % (R['comb_z_min'] * 1000, R['comb_z_max'] * 1000), off=(-58, 0),
      ext=[((PX, y, R['comb_z_min']), (-0.63, y, R['comb_z_min'])), ((PX, y, R['comb_z_max']), (-0.63, y, R['comb_z_max']))])
    D(axs, vs, (0.20, y, comb), (0.20, y, comb - R['pad_drop']), 'pad %.0f\nbelow comb' % (R['pad_drop'] * 1000), off=(-50, 0), ext=[((PX, y, comb), (0.17, y, comb)), ((PX, y, comb - R['pad_drop']), (0.17, y, comb - R['pad_drop']))])
    for txt, pt, dx, dy in (('drive wheel dia %.0f' % (R['drive_r'] * 2000), (0.0, y, R['drive_r']), -150, 80), ('castor dia %.0f' % (R['nose_r'] * 2000), (R['nose_x'], y, R['nose_r']), 70, 95),
                            ('anti-tip wheel,\n%.0f off the ground' % (R['tail_gap'] * 1000), (R['tail_x'], y, R['tail_gap'] + R['tail_r']), -40, -150)):
        p = vs.px(pt); axs.annotate(txt, xy=p, xytext=(p[0] + dx, p[1] + dy), fontsize=8.5, color=INK, ha='center', va='center', zorder=7,
                                    bbox=dict(fc=SURF, ec='none', pad=1.2, alpha=0.9), arrowprops=dict(arrowstyle='-', color=INK2, lw=0.6))
    axs.text(0.02, 1.0, 'Side elevation (nose to the right)', transform=axs.transAxes, fontsize=11, weight='bold', color=INK, va='top')
    # ---------------- plan
    szp = (1400, 760); axp = fig.add_axes([0.01, 0.03, 0.56, 0.36]); vp = MI.View(-90, S, (430, 380), szp, el=90.0); img, _ = MI.raster(sc, vp)
    axp.imshow(img, interpolation='nearest'); axp.set_xlim(0, szp[0]); axp.set_ylim(szp[1], 0); axp.axis('off'); z = 1.5
    hw = R['width'] / 2
    D(axp, vp, (1.18, -hw, z), (1.18, hw, z), '%.0f overall width' % (R['width'] * 1000), off=(62, 0), ext=[((0.0, -hw, z), (1.21, -hw, z)), ((0.0, hw, z), (1.21, hw, z))])
    D(axp, vp, (-0.12, -GI, z), (-0.12, GI, z), '%.0f clear' % (2 * GI * 1000), off=(0, 0))
    D(axp, vp, (TIP - 0.10, -R['funnel_mouth'] / 2, z), (TIP - 0.10, R['funnel_mouth'] / 2, z), '%.0f mouth' % (R['funnel_mouth'] * 1000), off=(-44, 0),
      ext=[((TIP, -R['funnel_mouth'] / 2, z), (TIP - 0.13, -R['funnel_mouth'] / 2, z)), ((TIP, R['funnel_mouth'] / 2, z), (TIP - 0.13, R['funnel_mouth'] / 2, z))])
    D(axp, vp, (0.30, -R['comb_width'] / 2, z), (0.30, R['comb_width'] / 2, z), '%.0f comb' % (R['comb_width'] * 1000), off=(0, 0),
      ext=[((PX + 0.02, -R['comb_width'] / 2, z), (0.27, -R['comb_width'] / 2, z)), ((PX + 0.02, R['comb_width'] / 2, z), (0.27, R['comb_width'] / 2, z))])
    D(axp, vp, (R['nose_x'], -R['nose_track'] / 2, z), (R['nose_x'], R['nose_track'] / 2, z), '%.0f\ncastor track' % (R['nose_track'] * 1000), off=(0, 0))
    D(axp, vp, (0.0, -R['drive_track'] / 2, z), (0.0, R['drive_track'] / 2, z), '%.0f drive track' % (R['drive_track'] * 1000), off=(0, -40))
    axp.text(0.02, 0.985, 'Plan', transform=axp.transAxes, fontsize=11, weight='bold', color=INK, va='top')
    # ---------------- front elevation
    szf = (900, 1000); axf = fig.add_axes([0.58, 0.40, 0.40, 0.55]); vf = MI.View(0, S, (450, 860), szf, el=0.0); img, _ = MI.raster(sc, vf)
    axf.imshow(img, interpolation='nearest'); axf.set_xlim(0, szf[0]); axf.set_ylim(szf[1], 0); axf.axis('off'); x = 1.2
    g0 = vf.px((x, -0.8, 0)); g1 = vf.px((x, 0.8, 0)); axf.plot([g0[0], g1[0]], [g0[1], g1[1]], color=INK2, lw=1.0, zorder=4)
    D(axf, vf, (x, -hw, -0.09), (x, hw, -0.09), '%.0f' % (R['width'] * 1000), off=(0, 12), ext=[((x, -hw, 0.0), (x, -hw, -0.12)), ((x, hw, 0.0), (x, hw, -0.12))])
    hs = R['mast_half_span']
    D(axf, vf, (x, -hs, HT + 0.14), (x, hs, HT + 0.14), '%.0f mast uprights, centre to centre' % (2 * hs * 1000), off=(0, -12), ext=[((x, -hs, HT), (x, -hs, HT + 0.17)), ((x, hs, HT), (x, hs, HT + 0.17))])
    D(axf, vf, (x, -(GI + 0.05), 0.20), (x, GI + 0.05, 0.20), '%.0f over the rails' % ((2 * GI + 0.10) * 1000), off=(0, 12))
    axf.text(0.02, 0.985, 'Front elevation', transform=axf.transAxes, fontsize=11, weight='bold', color=INK, va='top')
    # ---------------- data block
    r = P.robot_mass(); full = P.combined('ESE240SL', 1.0)
    rows = [('Mass, 2 x 18 Ah AGM', '%.0f kg (donor AGM pair %.0f kg, LiFePO4 %.0f kg)' % (r['m'], r['m'] + 11.2, r['m'] - 7.0)),
            ('With a full 240 L bin', '%.0f kg' % full['m']),
            ('Robot centre of gravity', '%.0f mm ahead of the drive axle, %.0f mm high' % (r['x'] * 1000, r['z'] * 1000)),
            ('Frame', '50 x 50 x 3 S235 box section, bolted through flat laser-cut plates'),
            ('Lift', '24 V actuator, 4 kN, 400 mm stroke; roller carriage on the two uprights'),
            ('Comb', '640 mm plate, self-aligning: yaw +/-4 deg, roll +/-3 deg'),
            ('Rest pad', '400 x 120 mm rubber, %.0f mm below the comb, depth slots +/-%.0f mm' % (R['pad_drop'] * 1000, R['pad_adjust'] * 1000)),
            ('Bins', '120 to 240 L to EN 840-1, held by the frontal receiver (860 to 1,030 mm)'),
            ('Pivot circle', '%.2f m diameter (castor swivel circles)' % (2 * (math.hypot(R['nose_x'] + 0.055, R['nose_track'] / 2) + 0.055 + R['nose_r']))),
            ('Drive', 'two 24 V powerchair gearmotors with spring brakes, 318 mm wheels')]
    axd = fig.add_axes([0.59, 0.03, 0.40, 0.34]); axd.axis('off')
    axd.text(0, 1.0, 'Bin Tug Rev H2: general arrangement', fontsize=13, weight='bold', color=INK, va='top')
    for i, (k, vtxt) in enumerate(rows):
        axd.text(0.0, 0.88 - i * 0.078, k, fontsize=9, color=INK2, va='top'); axd.text(0.26, 0.88 - i * 0.078, vtxt, fontsize=8.8, color=INK, va='top')
    axd.text(0, 0.06, 'Dimensions in mm, from sim/params.py, 12 Nov 2026. Comb drawn at a 240 L bin\'s lip height.\nConcept stage: not a drawing to build from. Brackets and forks are indicative.', fontsize=8.5, color=INK2, va='top')
    fig.savefig(os.path.join(FIG, 'ga_revH2.png'), dpi=150, facecolor=SURF); plt.close(fig); print('wrote ga_revH2.png')


def bin_profile(front_taper, rear_taper, bd=0.632, zr=1.025):
    """Side profile of a 240 L bin, x = distance behind the front wall at rim height (so the front is at the right when x is flipped)."""
    return [(0.0, zr), (front_taper, 0.0), (bd - rear_taper, 0.0), (bd - rear_taper * 0.25, 0.42), (bd, zr)]


def interface():
    H = json.load(open(os.path.join(RES, 'hang.json')))
    real = [r for r in H['as_designed'] if 'SL' in r['bin'] and '250' not in r['bin'] and '240' in r['bin']][0]; oth = H['other_agent_revH_model']
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 7.4)); fig.patch.set_facecolor(SURF)
    BIN_C, BIN_F, ROB_C, ROB_F = '#eb6834', '#fbe3d8', '#2a78d6', '#dbe8f8'
    seat = P.COMB_SEAT_OFFSET
    # title, front taper, rear taper, wall-to-pad gap e, pad drop, pad face x in the picture, wheel drop, real?
    cases = [('What the manufacturers\' drawings show, and how Rev H2 holds it', 0.035, 0.125, (real['wall_setback_mm'] - real['pad_setback_mm']) / 1000.0, R['pad_drop'],
              seat - R['pad_setback'], real['wheel_drop_mm'] / 1000.0, True),
             ('How the other agent\'s test of Rev H modelled the same bin', 0.170, 0.030, oth['swing_at_pad_mm'] / 1000.0, 0.45, seat - 0.004, oth['wheel_drop_mm'] / 1000.0, False)]
    for ax, (title, ft, rt, e, pdrop, pf, drop, isreal) in zip(axes, cases):
        ax.set_facecolor(SURF); ax.set_aspect('equal'); ax.axis('off')
        zr = 1.025; comb = 1.005; lift = 0.10
        th = math.atan(e / pdrop); piv = np.array((-seat, comb))                # seat line in bin coordinates (x behind the front wall at the rim)
        def T(p):                                                              # bin point -> picture (front to the right), hanging by th about the seat line
            d = np.array(p) - piv; c, s_ = math.cos(th), math.sin(th)
            q = piv + np.array((d[0] * c + d[1] * s_, -d[0] * s_ + d[1] * c)); return (-q[0], q[1] + lift)
        prof = bin_profile(ft, rt)
        ax.add_patch(Polygon([T(p) for p in prof], closed=True, fc=BIN_F, ec=BIN_C, lw=1.8, zorder=2))
        ax.add_patch(Polygon([T(p) for p in [(0.0, zr), (-0.038, zr), (-0.038, zr - 0.05), (-0.030, zr - 0.05), (-0.030, zr - 0.02), (0.0, zr - 0.02)]], closed=True, fc=BIN_C, ec=BIN_C, lw=1.0, zorder=3))
        l0, l1 = T((-0.034, zr + 0.012)), T((0.66, zr + 0.05)); ax.plot([l0[0], l1[0]], [l0[1], l1[1]], color=BIN_C, lw=3.5, solid_capstyle='round', zorder=3)
        h0, h1, h2 = T((0.632, zr - 0.02)), T((0.72, zr - 0.02)), T((0.72, zr - 0.06)); ax.plot([h0[0], h1[0], h2[0]], [h0[1], h1[1], h2[1]], color=BIN_C, lw=2.5, zorder=3)
        wc = (T((0.5515, 0.10))[0], 0.10 + lift - drop); ax.add_patch(Circle(wc, 0.10, fc=SURF, ec=BIN_C, lw=1.8, zorder=4))
        ax.plot([-1.0, 0.45], [0, 0], color='#8d8c85', lw=1.2)
        ax.add_patch(Rectangle((0.075, 0.30), 0.05, 1.10, fc=ROB_F, ec=ROB_C, lw=1.4, zorder=1))                       # mast upright
        ax.add_patch(Rectangle((seat - 0.004, comb + lift - 0.06), 0.008, 0.06, fc=ROB_C, ec=ROB_C, zorder=5))         # comb tooth
        ax.add_patch(Rectangle((seat + 0.004, comb + lift - 0.10), 0.071, 0.05, fc=ROB_C, ec=ROB_C, alpha=0.85, zorder=4))
        ax.add_patch(Rectangle((pf, comb + lift - pdrop - 0.06), 0.014, 0.12, fc='#0b0b0b', ec='#0b0b0b', zorder=5))   # rest pad
        ax.add_patch(Rectangle((pf + 0.014, comb + lift - pdrop - 0.03), 0.075 - pf - 0.014, 0.06, fc=ROB_C, ec=ROB_C, alpha=0.85, zorder=4))
        clear = lift - drop
        ax.annotate('', xy=(wc[0] - 0.16, 0.0), xytext=(wc[0] - 0.16, max(clear, 0.001)), arrowprops=dict(arrowstyle='<->', color='#0b0b0b', lw=0.8, shrinkA=0, shrinkB=0, mutation_scale=7))
        ax.text(wc[0] - 0.18, max(clear / 2, 0.035), '%.0f mm clear' % (clear * 1000), fontsize=9, color='#0b0b0b', ha='right', va='center')
        def lab(text, xy, xytext, ha='left'):
            ax.annotate(text, xy=xy, xytext=xytext, fontsize=9, color='#0b0b0b', ha=ha, va='center', arrowprops=dict(arrowstyle='-', color='#52514e', lw=0.7))
        lab('Comb tooth under the\nfrontal receiver (front lip)', (seat, comb + lift - 0.01), (0.20, 1.28))
        lab('Rest pad, %.0f mm\nbelow the comb' % (pdrop * 1000), (pf + 0.007, comb + lift - pdrop), (0.20, comb + lift - pdrop))
        lab('Handle and lid hinge:\nrear of the bin', T((0.72, zr - 0.04)), (-1.02, 1.32), ha='left')
        lab('Wheels: rear of the bin', (wc[0] - 0.05, wc[1] + 0.08), (-1.02, 0.52), ha='left')
        lab('Front wall', T((ft * 0.55, zr * 0.45)), (0.20, 0.42))
        ax.text(-1.02, 1.56, title, fontsize=11.5, weight='bold', color='#0b0b0b', ha='left')
        if isreal:
            txt = ('Front wall tapers about 35 mm over its height (Craemer 240 side elevation, scaled).\n'
                   'Pad face set %.0f mm behind the comb seat line, adjustable +/-%.0f mm: the bin hangs %.1f deg.\n'
                   'Wheels drop %.0f mm, so a 100 mm lift leaves %.0f mm clear (target: %.0f mm or more).'
                   % (R['pad_setback'] * 1000, R['pad_adjust'] * 1000, real['hang_deg'], drop * 1000, clear * 1000, R['wheel_clear_min'] * 1000))
        else:
            txt = ('Bin hull with a 170 mm taper on the FRONT wall (cmp/simH.py line 132) and a pad flush with the comb\n'
                   'face, 450 mm below it: the base swings %.0f mm and the bin hangs %.0f deg (their MuJoCo run: 11-12 deg).\n'
                   'Wheels drop %.0f mm, so a 100 mm lift leaves %.0f mm, or none on a 250 mm-wheel bin: their "false holds".'
                   % (e * 1000, oth['hang_deg'], drop * 1000, clear * 1000))
        ax.text(-1.02, -0.16, txt, fontsize=9, color='#52514e', ha='left', va='top')
        ax.set_xlim(-1.06, 0.80); ax.set_ylim(-0.42, 1.64)
    fig.text(0.5, 0.012, 'Schematic side views of a 240 L bin, nose of the robot to the right. Receiver position: EN 840-1 "frontal receiver"; GGAWB guidelines 03/2025 s.3.5;\n'
             'ESE manual; SULO, Craemer and Weber drawings (reference/other_agent/web/downloads/g5bins). See docs/EVIDENCE_receiver_side.md.', ha='center', fontsize=8.5, color='#52514e')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.07, wspace=0.02)
    fig.savefig(os.path.join(FIG, 'bin_interface.png'), dpi=150, facecolor=SURF); plt.close(fig); print('wrote bin_interface.png')


def lists():
    xk = TIP + R['funnel_len']
    tube = [('Side rail, straight part', 2, NOSE - 0.015 - xk, '50x50x3 RHS S235'), ('Side rail, flared tip (mitre to suit)', 2, math.hypot(R['funnel_len'], R['funnel_mouth'] / 2 - GI), '50x50x3 RHS S235'),
            ('Nose cross-member', 1, 2 * GI + 0.10, '50x50x3 RHS S235'), ('Mast base cross-member', 1, 2 * GI + 0.10, '50x50x3 RHS S235'),
            ('Mast upright', 2, HT - 0.31, '50x50x3 RHS S235'), ('Mast top tie', 1, 2 * R['mast_half_span'] + 0.05, '50x50x3 RHS S235'),
            ('Carriage top bar', 1, 0.54, '50x50x3 RHS S235'), ('Carriage lower bar', 1, 0.50, '50x50x3 RHS S235'), ('Carriage side member', 2, R['pad_drop'] - 0.02, '50x50x3 RHS S235'),
            ('Mast brace', 2, math.dist((MX + 0.03, R['mast_half_span'], 0.92), (NOSE - 0.10, GI + 0.025, 0.32)), '30x30x2 RHS S235')]
    with open(os.path.join(RES, 'cut_list_revH2.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['part', 'qty', 'length_mm', 'section', 'total_mm']); tot = {}
        for n, q, L_, sec in tube:
            w.writerow([n, q, round(L_ * 1000), sec, round(q * L_ * 1000)]); tot[sec] = tot.get(sec, 0) + q * L_
        for sec, t in tot.items(): w.writerow(['TOTAL ' + sec, '', '', sec, round(t * 1000)])
        w.writerow(['NOTE', '', '', '', 'Concept cut list from params.py. Check every length against the detail drawings before cutting.'])
    plates = [('Motor / gearbox plate', 2, '6 mm S355', '170 x 140', 'hangs the donor gearbox under the rail; hole pattern from the donor unit'),
              ('Mast foot gusset', 4, '5 mm S355', '150 x 150 triangle', 'upright to base cross-member'), ('Rail to cross-member joint plate', 4, '5 mm S355', '150 x 100', 'nose and mast-base cross-members'),
              ('Rail-tip splice plate', 2, '5 mm S355', '160 x 50', 'flared tip to rail'), ('Castor outrigger plate', 2, '8 mm S355', '170 x 150', 'on top of rail and nose cross-member'),
              ('Actuator base lug', 1, '6 mm S355', '80 x 60 pair', 'on the mast base cross-member'), ('Carriage horn', 1, '6 mm S355', '250 x 45 pair', 'actuator rod pin 130 mm above the comb line'),
              ('Carriage roller cheek', 4, '6 mm S355', '120 x 110', 'two per upright, carry 8 bearings'), ('Comb plate with teeth', 1, '6 mm S355', '640 x 75', 'tooth profile to EN 840-1 Annex B: buy the standard first'),
              ('Comb pivot block and stops', 1, '8 mm S355', '100 x 60', 'yaw +/-4 deg, roll +/-3 deg, 2 bushes, 2 springs'), ('Rest-pad bracket, slotted', 1, '5 mm S355', '400 x 100', '+/-25 mm depth slots'),
              ('Battery tray', 2, '4 mm S355', '190 x 90', 'on the rail beside the drive wheel'), ('Tail-wheel bracket', 2, '5 mm S355', '140 x 40', 'under the flared tip'),
              ('Mast top tie plate', 2, '5 mm S355', '100 x 50', '')]
    with open(os.path.join(RES, 'plate_list_revH2.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['part', 'qty', 'material', 'nominal_size_mm', 'note'])
        for p in plates: w.writerow(p)
        w.writerow(['TOTAL plates', sum(p[1] for p in plates), '', '', 'Sizes are placeholders for costing. No DXFs exist yet.'])
    # footprint for the other agent's lane-fit tool (rectangles x0, x1, y0, y1, label), same format as cmp/designs/RevH.json
    bx = R['batt_x']; cx = R['nose_x'] + 0.055; reach = 0.055 + R['nose_r']; yc = R['nose_track'] / 2
    parts = [[xk, NOSE - 0.015, GI, GI + 0.05, 'rail L'], [xk, NOSE - 0.015, -(GI + 0.05), -GI, 'rail R'], [TIP, xk, GI, R['funnel_mouth'] / 2 + 0.05, 'funnel flare L'],
             [TIP, xk, -(R['funnel_mouth'] / 2 + 0.05), -GI, 'funnel flare R'], [-R['drive_r'], R['drive_r'], 0.45, 0.52, 'drive wheel L'], [-R['drive_r'], R['drive_r'], -0.52, -0.45, 'drive wheel R'],
             [bx - 0.0925, bx + 0.0925, GI - 0.008, GI + 0.072, 'battery L'], [bx - 0.0925, bx + 0.0925, -(GI + 0.072), -(GI - 0.008), 'battery R'],
             [R['tail_x'] - 0.05, R['tail_x'] + 0.05, 0.385, 0.425, 'tail wheel L'], [R['tail_x'] - 0.05, R['tail_x'] + 0.05, -0.425, -0.385, 'tail wheel R'],
             [NOSE - 0.065, NOSE - 0.015, -(GI + 0.05), GI + 0.05, 'nose cross-member'], [NOSE - 0.015, NOSE, -(GI + 0.05 - R['nose_chamfer']), GI + 0.05 - R['nose_chamfer'], 'bumper (corners chamfered %.0f mm)' % (R['nose_chamfer'] * 1000)],
             [cx - reach, cx + reach, yc - reach, yc + reach, 'nose castor L swivel envelope as a box (true envelope is a circle r %.3f about %.3f, %.2f)' % (reach, cx, yc)],
             [cx - reach, cx + reach, -yc - reach, -yc + reach, 'nose castor R swivel envelope'], [MX - 0.025, MX + 0.025, -0.245, 0.245, 'mast + carriage']]
    hwb = P.BINS['ESE240SL']['W'] / 2; bd = P.BINS['ESE240SL']['D'] - 0.105
    design = dict(name='RevH2', parts=parts, bin=[[PX - bd - 0.10, hwb], [PX - bd - 0.10, -hwb], [PX + 0.04, -hwb], [PX + 0.04, hwb]], handle_dir=-1, withdraw=1, approach=-1, carry_dir=1, half_w=R['width'] / 2,
                  src='revH2/sim/params.py ROBOT (12 Nov 2026). Bin outline is the plumb ESE 240 SL incl. handle; replace with the MuJoCo pose after a grab (cmp/dump_fp.py).')
    json.dump(design, open(os.path.join(REF, 'RevH2_lanefit_design.json'), 'w'), indent=1)
    print('wrote cut list, plate list, lane-fit design; tube totals', {k: round(v, 2) for k, v in tot.items()})


if __name__ == '__main__':
    lists(); interface(); ga()
