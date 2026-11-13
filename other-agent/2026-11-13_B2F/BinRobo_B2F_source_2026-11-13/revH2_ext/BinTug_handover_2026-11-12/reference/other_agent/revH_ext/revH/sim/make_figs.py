#!/usr/bin/env python3
"""Rev H figures: concept general arrangement (side + plan) and turning-space comparison. Writes ../fig/*.png.
Drawn from params.py, so the pictures follow the numbers."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch, Wedge, FancyBboxPatch
import params as P
R = P.ROBOT
FIG = os.path.join(HERE, '..', 'fig'); os.makedirs(FIG, exist_ok=True)

SURF = '#fcfcfb'; INK = '#0b0b0b'; INK2 = '#52514e'; GRID = '#d9d8d2'
ROBOT_C = '#2a78d6'; ROBOT_F = '#dbe8f8'; BIN_C = '#eb6834'; BIN_F = '#fbe3d8'; GREY = '#8d8c85'; GREY_F = '#e9e8e3'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': GRID, 'text.color': INK})


def label(ax, text, xy, xytext, ha='left', va='center', color=INK2):
    ax.annotate(text, xy=xy, xytext=xytext, ha=ha, va=va, fontsize=8.5, color=INK,
                arrowprops=dict(arrowstyle='-', color=color, lw=0.7, shrinkA=1, shrinkB=1))


def dim(ax, p0, p1, text, off=(0, 0), ha='center', va='bottom'):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle='<->', mutation_scale=8, color=INK2, lw=0.8))
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], text, ha=ha, va=va, fontsize=8.5, color=INK2)


def concept():
    b = P.BINS['ESE240SL']; lift = R['lift']; pad = R['pad_x']
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.0, 6.2), gridspec_kw=dict(width_ratios=[1.0, 1.0]))
    fig.patch.set_facecolor(SURF)
    # ------------------------------------------------------------------ side elevation (nose to the right)
    ax = a1; ax.set_facecolor(SURF); ax.set_aspect('equal'); ax.axis('off')
    ax.plot([-0.85, 1.25], [0, 0], color=GREY, lw=1.2)
    # bin (lifted): body, lid, handle, wheel
    body_d = b['D'] - 0.105; rim = b['comb'] + 0.02 + lift
    binpoly = [(pad, rim), (pad - 0.06, lift + 0.0), (pad - body_d + 0.07, lift), (pad - body_d, lift + 0.16), (pad - body_d, rim)]
    ax.add_patch(Polygon(binpoly, closed=True, fc=BIN_F, ec=BIN_C, lw=1.6, zorder=2))
    ax.add_patch(Polygon([(pad + 0.045, rim), (pad + 0.045, rim - 0.035), (pad + 0.02, rim - 0.035), (pad + 0.02, rim)], closed=True, fc=BIN_F, ec=BIN_C, lw=1.4, zorder=3))  # front lip
    ax.plot([pad + 0.05, pad - body_d - 0.02], [rim + 0.012, rim + 0.045], color=BIN_C, lw=3, solid_capstyle='round', zorder=3)                                              # lid
    ax.plot([pad - body_d, pad - body_d - 0.10, pad - body_d - 0.10], [rim - 0.02, rim - 0.02, rim - 0.07], color=BIN_C, lw=2.2, zorder=3)                                     # handle
    ax.add_patch(Circle((pad - body_d + 0.03, lift + 0.10), 0.10, fc=SURF, ec=BIN_C, lw=1.6, zorder=3))                                                                       # bin wheel
    # robot: rail, mast, carriage + comb, actuator, e-box, battery, motor, wheels, lidar, camera
    ax.add_patch(Rectangle((R['leg_tip_x'], 0.26), R['nose_tip_x'] - R['leg_tip_x'], 0.05, fc=ROBOT_F, ec=ROBOT_C, lw=1.4, zorder=4))
    ax.add_patch(Rectangle((R['mast_x'] - 0.025, 0.31), 0.05, R['height'] - 0.31, fc=ROBOT_F, ec=ROBOT_C, lw=1.4, zorder=4))
    cz = b['comb'] + lift
    ax.add_patch(Rectangle((pad, cz - R['pad_drop'] - 0.03), R['mast_x'] - 0.025 - pad, R['pad_drop'] + 0.05, fc=ROBOT_C, ec=ROBOT_C, lw=1.0, alpha=0.85, zorder=5))
    ax.add_patch(Rectangle((pad + 0.02, cz - 0.005), 0.012, 0.03, fc=INK, ec=INK, zorder=6))                                                                                  # comb blade under the lip
    ax.add_patch(Rectangle((R['mast_x'] + 0.04, 0.33), 0.035, 0.62, fc=SURF, ec=ROBOT_C, lw=1.2, zorder=4))                                                                   # actuator
    ax.add_patch(Rectangle((R['mast_x'] + 0.09, 0.45), 0.15, 0.26, fc=ROBOT_F, ec=ROBOT_C, lw=1.2, zorder=4))                                                                 # electronics
    ax.add_patch(Rectangle((-0.33, 0.31), 0.18, 0.17, fc=ROBOT_F, ec=ROBOT_C, lw=1.2, zorder=6))                                                                               # battery
    ax.add_patch(Rectangle((-0.30, 0.10), 0.25, 0.11, fc=SURF, ec=ROBOT_C, lw=1.0, ls='--', zorder=6))                                                                         # motor
    ax.add_patch(Circle((0.0, R['drive_r']), R['drive_r'], fc=SURF, ec=ROBOT_C, lw=2.0, zorder=7)); ax.add_patch(Circle((0.0, R['drive_r']), 0.03, fc=ROBOT_C, ec=ROBOT_C, zorder=8))
    ax.add_patch(Circle((R['nose_x'], R['nose_r']), R['nose_r'], fc=SURF, ec=ROBOT_C, lw=1.6, zorder=7))
    ax.plot([R['nose_x'], R['nose_x'] + 0.04, R['nose_x'] + 0.04], [R['nose_r'], R['nose_r'] + 0.10, 0.26], color=ROBOT_C, lw=1.4, zorder=6)
    ax.add_patch(Circle((R['tail_x'], R['tail_r'] + R['tail_gap']), R['tail_r'], fc=SURF, ec=ROBOT_C, lw=1.4, zorder=7))
    ax.plot([R['tail_x'], R['tail_x']], [R['tail_r'] + R['tail_gap'], 0.26], color=ROBOT_C, lw=1.2, zorder=6)
    ax.add_patch(Rectangle((R['nose_tip_x'] - 0.03, 0.31), 0.05, 0.06, fc=ROBOT_C, ec=ROBOT_C, zorder=6))                                                                      # lidar
    ax.add_patch(Rectangle((R['mast_x'] - 0.04, R['height']), 0.08, 0.05, fc=ROBOT_C, ec=ROBOT_C, zorder=6))                                                                   # camera
    # labels
    label(ax, 'Comb under the front lip', (pad + 0.026, cz + 0.02), (0.62, 1.22))
    label(ax, 'Carriage on rollers,\nrest pad below', (pad + 0.03, cz - 0.30), (0.70, 0.98))
    label(ax, 'Lift actuator\n3 kN, 300 mm', (R['mast_x'] + 0.058, 0.80), (0.74, 0.80))
    label(ax, 'Electronics', (R['mast_x'] + 0.2, 0.60), (0.80, 0.62))
    label(ax, 'Lidar', (R['nose_tip_x'], 0.34), (1.02, 0.44))
    label(ax, '260 mm caster', (R['nose_x'] + 0.10, 0.08), (0.98, 0.20))
    label(ax, 'Donor drive wheel\n(motor under the rail)', (0.0, 0.03), (-0.20, -0.16), ha='center')
    label(ax, 'Anti-tip wheel,\n75 mm clear', (R['tail_x'] - 0.04, 0.10), (-0.84, 0.22), ha='left')
    label(ax, 'Battery on\neach rail', (-0.30, 0.44), (-0.84, 0.50), ha='left')
    label(ax, 'Rear camera', (R['mast_x'] - 0.04, R['height'] + 0.03), (0.02, 1.42), ha='center')
    label(ax, 'Handle', (pad - body_d - 0.10, rim - 0.04), (-0.84, 1.02), ha='left')
    ax.text(0.03, 0.72, '240 L bin\ncarried upright', ha='center', va='center', fontsize=9.5, color=BIN_C, zorder=9)
    dim(ax, (0.20, 0.0), (0.20, lift), ' 100 mm', off=(0.005, 0), ha='left', va='center')
    dim(ax, (R['leg_tip_x'], -0.30), (R['nose_tip_x'], -0.30), '1.31 m', off=(0, 0.01))
    dim(ax, (1.30, 0.0), (1.30, R['height']), '1.30 m', off=(0.015, 0), ha='left', va='center')
    ax.set_xlim(-0.88, 1.52); ax.set_ylim(-0.40, 1.50)
    # ------------------------------------------------------------------ plan view
    ax = a2; ax.set_facecolor(SURF); ax.set_aspect('equal'); ax.axis('off')
    ax.add_patch(Circle((0, 0), 0.97, fc='none', ec=GREY, lw=1.0, ls=(0, (4, 3)), zorder=1))
    hw = b['W'] / 2
    ax.add_patch(FancyBboxPatch((pad - body_d, -hw), body_d, 2 * hw, boxstyle='round,pad=0,rounding_size=0.05', fc=BIN_F, ec=BIN_C, lw=1.6, zorder=2))
    ax.plot([pad - body_d - 0.09, pad - body_d - 0.09], [-0.20, 0.20], color=BIN_C, lw=3, solid_capstyle='round', zorder=3)
    for sg in (1, -1):
        ax.plot([pad - body_d, pad - body_d - 0.09], [sg * 0.20, sg * 0.20], color=BIN_C, lw=1.8, zorder=3)
        ax.add_patch(Rectangle((pad - body_d - 0.07, sg * (b['track'] / 2) - (0.04 if sg > 0 else 0)), 0.20, 0.04, fc=SURF, ec=BIN_C, lw=1.4, zorder=3))                      # bin wheels
        gi = R['leg_inner_gap'] / 2; mo = R['funnel_mouth'] / 2; xk = R['leg_tip_x'] + R['funnel_len']
        rail = [(R['nose_tip_x'], sg * gi), (xk, sg * gi), (R['leg_tip_x'], sg * mo), (R['leg_tip_x'], sg * (mo + 0.05)), (xk, sg * (gi + 0.05)), (R['nose_tip_x'], sg * (gi + 0.05))]
        ax.add_patch(Polygon(rail, closed=True, fc=ROBOT_F, ec=ROBOT_C, lw=1.4, zorder=4))                                                                       # rail with flared tip
        yw = sg * R['drive_track'] / 2
        ax.add_patch(Rectangle((-R['drive_r'], yw - 0.035), 2 * R['drive_r'], 0.07, fc=ROBOT_C, ec=ROBOT_C, lw=1.0, zorder=5))                                                 # drive wheel
        ax.add_patch(Rectangle((-0.06, min(sg * 0.38, yw - sg * 0.035)), 0.12, abs(yw - sg * 0.035 - sg * 0.38), fc=ROBOT_F, ec=ROBOT_C, lw=1.0, zorder=4))                    # gearbox
        ax.add_patch(Rectangle((-0.33, min(sg * 0.32, sg * 0.40)), 0.18, 0.08, fc=SURF, ec=ROBOT_C, lw=1.2, zorder=6))                                                         # battery
        ax.add_patch(Rectangle((R['nose_x'] - 0.13, sg * R['nose_track'] / 2 - 0.035), 0.26, 0.07, fc=SURF, ec=ROBOT_C, lw=1.4, zorder=5))                                     # caster
        ax.add_patch(Rectangle((R['tail_x'] - 0.05, sg * R['tail_track'] / 2 - 0.015), 0.10, 0.03, fc=SURF, ec=ROBOT_C, lw=1.2, zorder=7))                                     # tail wheel
        ax.add_patch(Circle((R['leg_tip_x'] + 0.07, sg * 0.362), 0.012, fc=INK, ec=INK, zorder=8))                                                                             # gap sensor
    ax.add_patch(Rectangle((R['mast_x'] - 0.025, -0.38), 0.05, 0.76, fc=ROBOT_F, ec=ROBOT_C, lw=1.4, zorder=4))                                                                # mast cross-member
    ax.add_patch(Rectangle((R['nose_tip_x'] - 0.05, -0.38), 0.05, 0.76, fc=ROBOT_F, ec=ROBOT_C, lw=1.4, zorder=4))                                                             # nose cross-member
    ax.add_patch(Rectangle((pad, -R['comb_width'] / 2), 0.03, R['comb_width'], fc=ROBOT_C, ec=ROBOT_C, zorder=6))                                                              # comb
    ax.add_patch(Rectangle((R['mast_x'] + 0.09, -0.14), 0.15, 0.28, fc=ROBOT_F, ec=ROBOT_C, lw=1.2, zorder=5))                                                                 # electronics
    ax.add_patch(Circle((R['nose_tip_x'] - 0.01, 0), 0.035, fc=ROBOT_C, ec=ROBOT_C, zorder=6))                                                                                 # lidar
    label(ax, 'Comb, 600 mm wide', (pad + 0.015, 0.24), (0.78, 1.08))
    label(ax, 'Pivot circle, 1.9 m', (0.97 * math.cos(math.radians(132)), 0.97 * math.sin(math.radians(132))), (-1.36, 1.04), ha='left')
    label(ax, 'Gap sensor in\neach rail tip', (R['leg_tip_x'] + 0.07, 0.362), (-1.36, 0.62), ha='left')
    label(ax, 'Flared rail tips\nguide the bin in', (R['leg_tip_x'] + 0.02, -0.40), (-1.36, -0.62), ha='left')
    label(ax, 'Anti-tip wheel\nunder each tip', (R['tail_x'], -R['tail_track'] / 2 - 0.015), (-1.36, -1.04), ha='left')
    label(ax, 'Drive wheels beside the bin:\n166 of 196 kg rides on them', (0.05, -R['drive_track'] / 2 - 0.035), (0.42, -1.12))
    label(ax, 'Battery', (-0.24, 0.40), (-0.42, 0.72), ha='center')
    ax.text(pad - body_d / 2, 0.0, 'Bin', ha='center', va='center', fontsize=10, color=BIN_C, zorder=9)
    dim(ax, (-0.66, -0.33), (-0.66, 0.33), '660 mm\nclear', off=(-0.02, 0), ha='right', va='center')
    dim(ax, (1.10, -R['width'] / 2), (1.10, R['width'] / 2), '1.04 m', off=(0.02, 0), ha='left', va='center')
    ax.set_xlim(-1.40, 1.45); ax.set_ylim(-1.28, 1.22)
    fig.text(0.02, 0.945, 'Side view: nose and direction of travel to the right', fontsize=10.5, color=INK, ha='left', weight='bold')
    fig.text(0.52, 0.945, 'Plan view', fontsize=10.5, color=INK, ha='left', weight='bold')
    # legend
    fig.text(0.5, 0.025, 'Blue: robot      Orange: bin      Dimensions from sim/params.py; concept stage, not a drawing to build from', ha='center', fontsize=8.5, color=INK2)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.06, wspace=0.02)
    fig.savefig(os.path.join(FIG, 'revH_concept.png'), dpi=170, facecolor=SURF); plt.close(fig)


def turning():
    """Swept area of a 180 degree turn in the 3.6 m lane the SITL assumes. Rev G numbers are mission.turning()'s: tug axle radius
    Lt / sin(cap), outer front corner radius hypot(R + half width, front overhang). Rev H pivots about its drive-axle centre."""
    Lt, cap, hw, front = 0.67, 28.0, 0.38, 0.762 + 0.195
    Rr = Lt / math.sin(math.radians(cap)); r_out = math.hypot(Rr + hw, front); need = (Rr + hw) + r_out
    r_in = math.sqrt(Rr ** 2 - Lt ** 2) - 0.29                    # inside edge of the towed bin (0.58 m wide) in the steady turn
    rp = max(math.hypot(x, y) for x, y in [(R['nose_tip_x'], 0.40), (R['leg_tip_x'], R['width'] / 2), (0.0, R['width'] / 2)])
    lane = 3.6
    fig, ax = plt.subplots(figsize=(11.0, 5.0)); fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF); ax.set_aspect('equal'); ax.axis('off')
    gx = 8.4                                                        # x offset of the Rev H panel
    for x0, x1 in ((-3.3, 3.3), (gx - 2.6, gx + 2.6)):
        for y0 in (-lane / 2 - 0.40, lane / 2):
            ax.add_patch(Rectangle((x0, y0), x1 - x0, 0.40, fc=GREY_F, ec='none', zorder=1))
        for y0 in (-lane / 2, lane / 2):
            ax.plot([x0, x1], [y0, y0], color=GREY, lw=1.2, zorder=2)
    # Rev G: enters along the lower edge (tug side on the lane edge), turns left through 180 degrees, leaves along the upper edge
    cx = -0.4; cy = -lane / 2 + hw + Rr; xs = cx - 2.7
    a0 = math.atan2(-(Rr + hw), front); pts = [(xs, cy - Rr - hw), (cx + front, cy - Rr - hw)]
    pts += [(cx + r_out * math.cos(a0 + math.pi * i / 80), cy + r_out * math.sin(a0 + math.pi * i / 80)) for i in range(81)]
    pts += [(xs, cy + Rr + hw), (xs, cy + Rr - hw), (cx, cy + Rr - hw)]
    pts += [(cx + r_in * math.cos(math.pi / 2 - math.pi * i / 80), cy + r_in * math.sin(math.pi / 2 - math.pi * i / 80)) for i in range(81)]
    pts += [(cx, cy - Rr + hw), (xs, cy - Rr + hw)]
    ax.add_patch(Polygon(pts, closed=True, fc=BIN_F, ec=BIN_C, lw=1.4, zorder=3))
    ax.add_patch(FancyArrowPatch((xs + 0.25, cy - Rr), (xs + 1.25, cy - Rr), arrowstyle='->', mutation_scale=10, color=BIN_C, lw=1.2, zorder=4))
    ax.add_patch(FancyArrowPatch((xs + 1.25, cy + Rr), (xs + 0.25, cy + Rr), arrowstyle='->', mutation_scale=10, color=BIN_C, lw=1.2, zorder=4))
    top = cy + r_out; xd = cx + r_out + 0.30
    ax.add_patch(FancyArrowPatch((xd, -lane / 2), (xd, top), arrowstyle='<->', mutation_scale=8, color=INK, lw=0.9, zorder=5))
    ax.plot([cx, xd + 0.08], [top, top], color=INK2, lw=0.6, ls=(0, (2, 2)), zorder=5)
    ax.text(xd + 0.08, 0.0, 'needs\n%.2f m' % need, fontsize=9.5, color=INK, va='center', ha='left')
    ax.annotate('%.2f m past the lane edge,\nwith the tug hard against the other side' % (top - lane / 2), xy=(cx + 0.35, top - 0.02), xytext=(cx - 2.6, lane / 2 + 0.62),
                fontsize=8.5, color=INK, ha='left', va='center', arrowprops=dict(arrowstyle='-', color=INK2, lw=0.7))
    ax.text(-3.3, lane / 2 + 1.12, 'Rev G: U-turn with the bin in tow, 28 deg hitch limit', fontsize=10.5, weight='bold', color=INK, ha='left')
    # Rev H
    ax.add_patch(Circle((gx, 0.0), rp, fc=ROBOT_F, ec=ROBOT_C, lw=1.4, zorder=3))
    ax.add_patch(FancyArrowPatch((gx, -rp), (gx, rp), arrowstyle='<->', mutation_scale=8, color=INK, lw=0.9, zorder=5))
    ax.text(gx + 0.08, 0.0, 'needs\n%.2f m' % (2 * rp), fontsize=9.5, color=INK, va='center', ha='left', zorder=6)
    ax.add_patch(FancyArrowPatch((gx + 1.9, -lane / 2), (gx + 1.9, lane / 2), arrowstyle='<->', mutation_scale=8, color=INK2, lw=0.8, zorder=5))
    ax.text(gx + 1.98, 0.0, 'lane\n%.1f m' % lane, fontsize=9, color=INK2, va='center', ha='left')
    ax.text(gx - 2.6, lane / 2 + 1.12, 'Rev H: pivot on the spot, bin on board', fontsize=10.5, weight='bold', color=INK, ha='left')
    ax.text(-3.3, -lane / 2 - 0.85, 'Area swept in a 180 degree turn, to scale. Lane width 3.6 m as assumed in the project\'s SITL world; hedges shaded. Rev G is a kinematic estimate from its CAD limits\n'
            '(bin axle 0.67 m behind the kingpin, hitch stop at 28 deg). Source: results/mission.json, turning.', fontsize=8.5, color=INK2, ha='left', va='top')
    ax.set_xlim(-3.5, gx + 3.0); ax.set_ylim(-lane / 2 - 1.45, lane / 2 + 1.40)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig(os.path.join(FIG, 'turning_space.png'), dpi=170, facecolor=SURF); plt.close(fig)
    return dict(revg_need=round(need, 2), revh_need=round(2 * rp, 2), over=round(top - lane / 2, 2))


if __name__ == '__main__':
    concept(); print(turning()); print('figures written to', os.path.abspath(FIG))
