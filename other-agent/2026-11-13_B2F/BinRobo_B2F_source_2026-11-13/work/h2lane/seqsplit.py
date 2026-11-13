import math, numpy as np
import lanefit_b2 as L2
LF=L2.LF
from lanefit import *
def sequence_k(d, n, handle_to, mission, kk):
    """drop (carry bin k to its pad and leave) or pickup (fetch bin k from its pad). Forward plan: the robot drives the lane
    nose-first both ways (carry_dir). Every pivot is on the robot's own axis line through the pad pose (it may drive or reverse
    straight up to 4 m to a spot where the pivot fits); every straight move is swept. Margins in m (>0 = clear)."""
    order = LF.pads(n) if mission == 'drop' else LF.pads(n)[::-1]; steps = []; ok = True
    for k, pn in enumerate(order):
        if k != kk: continue
        standing = [LF.pad_pose(q, handle_to)[:3] for q in order[:k]] if mission == 'drop' else [LF.pad_pose(q, handle_to)[:3] for q in order[k + 1:]]
        bx, by, byaw, bs, blat = LF.pad_pose(pn, handle_to); rx, ry, ryaw = LF.robot_at_bin(d, bx, by, byaw)
        down = math.cos(wrap(ryaw - LANE.heading(bs))) > 0          # robot +x points down-lane when it holds this bin
        nose_down = down if d.cd > 0 else not down
        tgt = [(bx, by, byaw)]
        if mission == 'drop':
            if not nose_down:      # arrives nose-down loaded, must hold the bin nose-up: one loaded pivot on the axis line
                m = LF.zone_pivot(d, rx, ry, ryaw, d.r_load, True, standing); steps.append(('%s loaded pivot 180 near the pad, then straight to it (margin, pivot ds,lat)' % pn, m[0], m[1]))
            else: steps.append(('%s arrives straight, no pivot' % pn, None))
            wd_dir = d.wd                                           # withdraw = robot drives along +x*withdraw, the bin leaves through the open end
            m = LF.sweep_ok(d, rx, ry, ryaw, False, standing, [wd_dir * t for t in np.linspace(0.2, 0.9, 8)])   # the placed bin itself: MuJoCo G6
            to_road = (wd_dir > 0) == down
            steps.append(('%s withdraw 0.9 m %s' % (pn, 'toward the road' if to_road else 'up-lane'), m))
            if to_road:
                m = LF.line_pivot(d, rx + wd_dir * 0.9 * math.cos(ryaw), ry + wd_dir * 0.9 * math.sin(ryaw), ryaw, d.r_empty,
                               [wd_dir * t for t in np.arange(0.0, 3.01, 0.1)], False, standing + tgt)
                steps.append(('%s empty pivot beyond the placed bin (margin, extra run m)' % pn, m[0], m[1]))
                steps.append(('%s pass the placed bin going home' % pn, LF.pass_bin(d, bs, standing + tgt)))
        else:
            ap = -d.wd                                              # approach = robot moves along -x*withdraw onto the bin
            if nose_down:          # holds the bin nose-down: drive past, reverse up onto it; then a loaded pivot to go home
                steps.append(('%s pass the bin on the way down' % pn, LF.pass_bin(d, bs, standing + tgt)))
                m = LF.sweep_ok(d, rx, ry, ryaw, False, standing, [-ap * t for t in np.linspace(0.2, 1.5, 14)])
                steps.append(('%s run-in 1.5 m onto the bin' % pn, m))
                m = LF.zone_pivot(d, rx, ry, ryaw, d.r_load, True, standing); steps.append(('%s loaded pivot 180 near the pad (margin, pivot ds,lat)' % pn, m[0], m[1]))
            else:                  # holds the bin nose-up: empty pivot on the axis line up-lane of the bin, then reverse onto it
                sx, sy = rx - ap * 1.5 * math.cos(ryaw), ry - ap * 1.5 * math.sin(ryaw)
                m = LF.zone_pivot(d, sx, sy, ryaw, d.r_empty, False, standing + tgt)
                steps.append(('%s empty pivot up-lane, then reverse to the approach start (margin, pivot ds,lat)' % pn, m[0], m[1]))
                m = LF.sweep_ok(d, rx, ry, ryaw, False, standing, [-ap * t for t in np.linspace(0.2, 1.5, 14)])
                steps.append(('%s run-in 1.5 m onto the bin' % pn, m))
    return steps
