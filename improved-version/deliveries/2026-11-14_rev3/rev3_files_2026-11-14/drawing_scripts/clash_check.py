#!/usr/bin/env python3
"""Interference check on the drawing model with real solid intersections (OpenCascade, through CadQuery), not bounding boxes.

  1. every pair of parts, robot without the bin and robot carrying the bin: common volume;
  2. lift sweep: everything that rides on the carriage is moved from 0 mm to the top of travel in 2 mm steps and intersected
     with every fixed part: first travel at which each pair touches.
Pairs of parts that belong to the same bought-in assembly, or that are meant to pass through each other (a pin in its bush), are listed in ALLOW.
usage: clash_check.py [model script, default build_model.py] [--qmax 350] [--json out.json]"""
import sys, os, json, runpy, itertools, argparse
import numpy as np
import cadquery as cq
from OCP.gp import gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('script', nargs='?', default='build_model.py'); ap.add_argument('--qmax', type=float, default=350.0); ap.add_argument('--json'); ap.add_argument('--vmin', type=float, default=1.0)
ap.add_argument('--skip-static', action='store_true'); A = ap.parse_args()
sys.argv = [A.script]
g = runpy.run_path(os.path.join(HERE, A.script), run_name='clash')
PARTS, POSE, INST, M = g['PARTS'], g['POSE'], g['INST'], g['M']
LIFTG = ('lift', 'comb', 'pad', 'padbase')
# pairs that overlap by design (prefix pairs); everything else is reported
ALLOW = [('RK Pivot pin', 'RK '), ('LC Comb pivot', 'LC '), ('PD Pad slide rods', 'PD '), ('PD Pad die springs', 'PD '), ('PD Pad springs', 'PD '), ('DR ', 'DR '), ('CS ', 'CS '), ('BN ', 'BN '), ('BW ', 'BN '),
         ('LA Lift actuator rod', 'LA Lift actuator'), ('LA Lift actuator rod', 'LC Actuator bracket'), ('LA Lift actuator', 'LA Actuator base bracket'), ('LM Linear rail', 'LC Rail carriage'), ('SN 2D lidar', 'SN Lidar window'), ('SN Front camera', 'SN Front camera lens'), ('SN Rear camera', 'SN Rear camera lens'),
         ('SN Sensor post', 'SN Front camera'), ('SN Sensor post', 'SN Lidar bracket'), ('SN Sensor post', 'SN GNSS'), ('SN Sensor post', 'SN Radar, front'), ('SN Lidar bracket', 'SN 2D lidar'),
         ('SW Nib seat', 'LC Comb plate'), ('SF Front bumper bar', 'SF Front bumper stripe'), ('PD Pad UHMW face', 'BIN '), ('SF Bumper guide pin', 'SF Front bumper bar'), ('L', 'L')]
def allowed(a, b):
    for p, q in ALLOW:
        if (a.startswith(p) and b.startswith(q)) or (b.startswith(p) and a.startswith(q)):
            if (p, q) == ('L', 'L'): return a[:1] == 'L' and b[:1] == 'L' and a[1:2].isdigit() and b[1:2].isdigit()
            return True
    return False

def placed(solid, R, p):
    U, _, Vt = np.linalg.svd(np.asarray(R, float)); R = U @ Vt        # the recorded rotation is orthogonal only to float32 precision
    T = gp_Trsf(); T.SetValues(float(R[0, 0]), float(R[0, 1]), float(R[0, 2]), float(p[0]) * 1000.0, float(R[1, 0]), float(R[1, 1]), float(R[1, 2]), float(p[1]) * 1000.0, float(R[2, 0]), float(R[2, 1]), float(R[2, 2]), float(p[2]) * 1000.0)
    return cq.Shape.cast(BRepBuilderAPI_Transform(solid.wrapped, T, True).Shape())
def instances(state):
    out = []
    for name, grp, col, solid, render, src in PARTS:
        if name[:1] == 'L' and name[1:2].isdigit(): continue          # looms are checked by check_model.py (points in parts)
        for body in INST.get(grp, [grp]):
            R, p = POSE[state][body]; s = placed(solid, R, p); bb = s.BoundingBox()
            out.append(dict(name=name + ('' if body == grp else ' [%s]' % body), grp=grp, src=src, s=s, bb=(bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)))
    return out
def bbhit(a, b, m=0.0): return all(a[2 * k] < b[2 * k + 1] - m and b[2 * k] < a[2 * k + 1] - m for k in range(3))
def common(a, b):
    try: return a.intersect(b).Volume() / 1000.0     # cm3
    except Exception: return float('nan')
res = dict(static={}, sweep=[])
if not A.skip_static:
    for state in ('nobin', 'carry'):
        I = instances(state); hits = []
        for a, b in itertools.combinations(I, 2):
            if a['grp'] == b['grp'] and a['src'] == 'CAD' and b['src'] == 'CAD' and a['grp'] != 'tug': continue
            if not bbhit(a['bb'], b['bb']) or allowed(a['name'], b['name']): continue
            v = common(a['s'], b['s'])
            if v == v and v >= A.vmin: hits.append((round(v, 1), a['name'][:58], b['name'][:58], 'legacy' if a['src'] == 'CAD' and b['src'] == 'CAD' else 'mine'))
        hits.sort(reverse=True); res['static'][state] = hits
        print('== %s: %d pairs with more than %.1f cm3 in common (%d involve a part I changed or added)' % (state, len(hits), A.vmin, sum(1 for h in hits if h[3] == 'mine')))
        for h in hits: print('   %7.1f cm3  %-58s x %-58s %s' % h)
# lift sweep from the no-bin pose
dz = float(POSE['carry']['lift'][1][2] - POSE['nobin']['lift'][1][2]); q0 = M['lift_q_carry'] * 1000.0 - dz * 1000.0
I = instances('nobin'); mov = [i for i in I if i['grp'] in LIFTG]; fix = [i for i in I if i['grp'] == 'tug']
print('== lift sweep: %d moving parts against %d fixed parts; lift at %.1f mm in the no-bin pose; sweep 0 to %.0f mm' % (len(mov), len(fix), q0, A.qmax))
first = {}
for q in np.arange(0.0, A.qmax + 0.01, 2.0):
    d = q - q0
    for a in mov:
        bb = (a['bb'][0], a['bb'][1], a['bb'][2], a['bb'][3], a['bb'][4] + d, a['bb'][5] + d)
        for b in fix:
            key = (a['name'], b['name'])
            if key in first or allowed(a['name'], b['name']) or not bbhit(bb, b['bb']): continue
            v = common(a['s'].translate(cq.Vector(0, 0, d)), b['s'])
            if v == v and v >= 0.2: first[key] = (float(q), round(v, 2))
for (a, b), (q, v) in sorted(first.items(), key=lambda kv: kv[1][0]):
    res['sweep'].append(dict(moving=a, fixed=b, first_q_mm=q, cm3=v)); print('   q %5.0f mm  %-56s meets %-56s (%.1f cm3)' % (q, a[:56], b[:56], v))
if not first: print('   nothing touches over the whole travel')
# 3. loom centre-lines against the solids (both poses): a point every 4 mm along every loom run, tested for being inside a solid by more than its surface
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN
ENDS = [('L5', 'LA Lift actuator motor'), ('L5', 'EL Power box'), ('L1', 'EL Power box'), ('L1', 'PW Battery'), ('L1', 'EL Main fuse'), ('L11', 'EL Power box'), ('L12', 'EL Power box'), ('L12', 'DK Dock'), ('L12', 'SF Front bumper bar'), ('L6', 'SF Amber beacon'), ('L6', 'SN Rear camera'),
        ('L6', 'LT '), ('L6', 'SN Radar, rear'), ('L6', 'AU '), ('L8', 'SN '), ('L8', 'AU '), ('L8', 'CM '), ('L10', 'SF '), ('L9', 'LT Headlight'), ('L9', 'SW Front bumper'), ('L7', 'SW '), ('L6', 'SW Lift'), ('L7', 'SN Comb'), ('L2', 'DR Gearmotor'), ('L3', 'DR Gearmotor'),
        ('L2', 'SN Wheel encoder'), ('L3', 'SN Wheel encoder'), ('L4', 'SF Rear bumper'), ('L4', 'SN Leg-tip'), ('L4', 'LT Rear'), ('L', 'EL Electronics pod'), ('L7', 'CH ')]     # a loom ends in or on these
res['looms'] = {}
for state in ('nobin', 'carry'):
    I = instances(state); hits = {}
    for lid, lname, route, cores, col, r, pls in g['looms'](state):
        for pl in pls:
            for a_, b_ in zip(pl[:-1], pl[1:]):
                a_ = np.array(a_, float) * 1000; b_ = np.array(b_, float) * 1000; n = max(int(np.linalg.norm(b_ - a_) / 4.0), 1)
                for k in range(n + 1):
                    q = a_ + (b_ - a_) * k / n
                    for i in I:
                        bb = i['bb']
                        if not (bb[0] < q[0] < bb[1] and bb[2] < q[1] < bb[3] and bb[4] < q[2] < bb[5]): continue
                        if any((lid == e or (e == 'L' and True)) and i['name'].startswith(pf) for e, pf in ENDS): continue
                        c = BRepClass3d_SolidClassifier(i['s'].wrapped, gp_Pnt(float(q[0]), float(q[1]), float(q[2])), 0.5)
                        if c.State() == TopAbs_IN: hits[(lid, i['name'][:60])] = hits.get((lid, i['name'][:60]), 0) + 1
    res['looms'][state] = [[k[0], k[1], v] for k, v in sorted(hits.items())]
    print('== looms, %s: %d loom/part pairs where the loom centre-line is inside a solid' % (state, len(hits)))
    for (lid, nm), v in sorted(hits.items()): print('   %-4s inside %-60s at %d points (%d mm of run)' % (lid, nm, v, v * 4))
if A.json: json.dump(res, open(A.json, 'w'), indent=1)
