#!/usr/bin/env python3
"""Improved-version model for the drawing set.

Starts from the other agent's CAD part definitions (cad_B2F_src.py is an unchanged copy of their work/revB2F/cad_B2F.py, run here
with the improved version's geometry numbers and body positions taken from the gate simulation by get_poses.py), then:
  1. applies the three tested mechanical changes (fixed pad, 350 mm lift travel with a 60 mm taller mast, castor cross-beam on a centre pivot);
  2. adds the electrical devices from the parts list that their CAD does not draw (positions PROPOSED here);
  3. adds a PROPOSED routing for ten wiring looms.
Writes model.pkl: one entry per drawn piece with its triangles in the robot frame (metres) for the two states
'nobin' (robot alone, comb down) and 'carry' (full 240 L bin on the comb at carrying height), its item number and its explode offset.
Robot frame: origin on the ground under the drive-axle centre, +x toward the castors (nose), +y left, z up."""
import sys, os, json, math, pickle, runpy
import numpy as np
import cadquery as cq
HERE = '/workspace/work/coldeye_rev2'
sys.argv = ['cad_B2F_src.py', 'nomesh', 'nostep']
g = runpy.run_path(os.path.join(HERE, 'cad_B2F_src.py'), run_name='cadsrc')
PARTS = [list(p) + ['CAD'] for p in g['PARTS']]; COL = dict(g['COL']); box, cylx, cyly, cylz = g['box'], g['cylx'], g['cyly'], g['cylz']; G = g['G']
M = json.load(open(os.path.join(HERE, 'rec_B2F.json'))); Q = np.load(os.path.join(HERE, 'rec_B2F.npz'))['q']; BODIES = M['bodies']
val = lambda w: w.val() if isinstance(w, cq.Workplane) else w

def find(prefix):
    r = [p for p in PARTS if p[0].startswith(prefix)]; assert r, prefix; return r
def remove(prefix):
    n = len(PARTS); PARTS[:] = [p for p in PARTS if not p[0].startswith(prefix)]; assert len(PARTS) < n, prefix
def replace(prefix, solid, name=None):
    r = find(prefix); assert len(r) == 1, (prefix, len(r)); r[0][3] = val(solid); r[0][5] = 'changed'
    if name: r[0][0] = name
def add(name, grp, col, solid, src='new', render=True): PARTS.append([name, grp, col, val(solid), render, src])

COL.update(red=(0.80, 0.10, 0.10), blue=(0.15, 0.35, 0.85), white=(0.96, 0.96, 0.96), lamp=(0.98, 0.95, 0.75), pbox=(0.30, 0.33, 0.38), rk=(0.36, 0.48, 0.62))
# ------------------------------------------------------------------ 1. the three tested mechanical changes
# (a) 350 mm lift travel: rails and mast 60 mm higher; the mast-top devices move up with it
for s, n in ((1, 'L'), (-1, 'R')):
    replace('LM Mast upright %s' % n, box(480, 560, s * 200 - 20, s * 200 + 20, 418, 1370).faces('<Z or >Z').shell(-4), 'LM Mast upright %s 80x40x4 (S12), 60 mm taller' % n)
    add('LM Rail backing flat %s 30x10 (S12)' % n, 'tug', 'steel', box(470, 480, s * 200 - 15, s * 200 + 15, 418, 1360))
    add('LM Mast foot plate %s 10 mm with crush tubes (S12)' % n, 'tug', 'steel', box(470, 565, s * 200 - 45, s * 200 + 45, 410, 418))
    add('LM Lift hard stop %s at 345 mm, clamped on the rail' % n, 'tug', 'red', box(446, 470, s * 200 - 16, s * 200 + 16, 1336, 1354))
    replace('LM Linear rail %s' % n, box(452, 470, s * 200 - 10, s * 200 + 10, 360, 1360), 'LM Linear rail %s HGR15 1 m, mounted 60 mm higher' % n)
replace('LM Mast top tie', box(470, 520, -230, 230, 1370, 1420))
replace('SN Rear camera (lip', box(410, 460, -35, 35, 1420, 1455)); replace('SN Rear camera lens', cylx(404, 410, 0, 1438, 12))
replace('SF Amber beacon', cylz(1420, 1478, 495, 150, 32).union(cq.Workplane().sphere(32).translate((495, 150, 1478))))
for r_ in find('LM Mast gusset'): r_[3] = r_[3].translate(cq.Vector(40, 0, 8)); r_[5] = 'changed'   # gussets follow the new upright face
add('SW Lift top limit switch (in the up feed of the lift driver)', 'tug', 'switch', box(452, 476, 222, 240, 1300, 1326))
# lift actuator: 400 mm IP65 unit, 620 mm closed. Base pin 60 mm lower (z 350) on a bracket on the front face of the mast-base cross-member, so the unit stands in front of that member (axis x 555)
replace('LA Lift actuator QC', cylz(350, 910, 555, 0, 34).union(cylz(326, 350, 555, 0, 16)), 'LA Lift actuator FDI 24 V 4 kN, 400 mm IP65 unit, 620 mm closed (340 mm used)')
replace('LA Lift actuator motor', box(589, 660, -40, 40, 352, 452))
replace('LA Lift actuator rod', cylz(-300, 135, 140, 0, 15)); replace('LC Actuator bracket', box(40, 165, -45, 45, 120, 150))
add('LA Actuator base bracket on the mast-base cross-member', 'tug', 'steel', box(515, 523, -50, 50, 318, 410).union(box(515, 600, -50, 50, 318, 328)))
# carriage: rail blocks 200 mm apart (S12) by moving the lower pair down 80 mm; plate 80 mm deeper, with two grommet holes for the carriage loom
for r_ in find('LC Rail carriage'):
    if r_[3].BoundingBox().zmin < 0: r_[3] = r_[3].translate(cq.Vector(0, 0, -80)); r_[5] = 'changed'
replace('LC Carriage plate', box(10, 40, -230, 230, -110, 165).cut(box(10, 40, 60, 80, -90, -70)).cut(box(10, 40, 105, 125, 15, 35)))
replace('LC Comb face plate', box(0, 10, -200, 200, -50, 150).cut(box(0, 10, 105, 125, 15, 35)))
find('LC Comb plate')[0][0] = 'LC Comb plate 700 mm, 8 mm S355 (S12), self-aligning'; find('LC Comb plate')[0][5] = 'changed'; find('LC Nib')[0][0] = 'LC Nib 8 long x 20 high, 700 mm'; find('LC Nib')[0][5] = 'changed'
remove('KP Keeper')   # the front dock has no handle bar to keep: in the firmware model the keeper is forced OK and its contacts are off
# (b) fixed pad: the retract drive goes (the sprung face, slide rods and contact switch stay; pad set 5 mm further back via the geometry numbers)
for pfx in ('PD Toggle actuator TRU', 'PD Toggle actuator rod', 'PD Knee toggle', 'SW Pad toggle-lock switch'): remove(pfx)
for pfx in ('PD Pad arm', 'PD Pad UHMW face'): find(pfx)[0][5] = 'changed'
replace('PD Pad guide block', box(g['pfx'] + 82, 14, -120, 120, g['pz'] - 35, g['pz'] + 35).cut(cylx(g['pfx'], 20, -90, g['pz'], 9)).cut(cylx(g['pfx'], 20, 90, g['pz'], 9)))
replace('PD Pad slide rods', cylx(20, 150, -90, 0, 8).union(cylx(20, 150, 90, 0, 8)).union(box(66, 76, -130, 130, -30, 30)), 'PD Pad slide rods + spring cup plate, 46 mm clear stroke')
replace('PD Pad die springs', cylx(20, 66, -60, 0, 14).union(cylx(20, 66, 60, 0, 14)), 'PD Pad springs 30 kN/m, long enough for the 45 mm stroke')
# (c) castor cross-beam on a centre pivot. The nose cross-member is raised to rail height to make room; drop plates and fixed castor plates go.
for pfx in ('FR Rail drop plate', 'FR Castor plate'): remove(pfx)
for r_ in find('FR Side rail'): r_[5] = 'changed'
replace('FR Nose cross-member', box(930, 980, -405, 405, 360, 410).faces('<Y or >Y').shell(-2), 'FR Nose cross-member 50x50x2, raised to rail height')
add('RK Castor cross-beam 50x40x3 RHS, pivots at its centre', 'tug', 'rk', box(935, 975, -360, 360, 266, 316).faces('<Y or >Y').shell(-3))
for s, n in ((1, 'L'), (-1, 'R')):
    add('RK Castor mounting plate %s 6 mm' % n, 'tug', 'rk', box(890, 1010, s * 280 - 70, s * 280 + 70, 260, 266))
    add('RK Bump stop %s (rubber, +/-2 deg, about 10 mm at the castor)' % n, 'tug', 'rubber', cylz(316, 349, 955, s * 300, 16))
# pivot pin 200 mm above the ground = the height used in every passing test (a re-test at 287 mm, through the beam itself, docked less accurately), so the pin sits in a housing under the beam
add('RK Pivot hanger plate rear 8 mm, bushed', 'tug', 'steel', box(916, 924, -45, 45, 170, 410)); add('RK Pivot hanger plate front 8 mm, bushed', 'tug', 'steel', box(986, 994, -45, 45, 170, 410))
add('RK Castor cross-beam pivot housing (pin fixed in it, welded under the beam)', 'tug', 'rk', box(936, 974, -30, 30, 174, 266))
add('RK Pivot pin M16 shoulder bolt, one bush in each hanger plate (70 mm apart)', 'tug', 'hub', cylx(908, 1004, 0, 200, 9))
# consequences of (c) in the nose: battery 50 mm back, front cover shorter, sensor post stands on the raised cross-member
replace('PW Battery', box(722, 902, -90, 90, 130, 280), 'PW Battery 24 V 20 Ah LiFePO4 + BMS (moved 58 mm back)')
replace('BY HDPE front cover', box(720, 915, -386, 386, 300, 306), 'BY HDPE front cover (removable, shortened)')
# In the B2-F CAD the bay floor, the bay side walls and the ballast plate pass through the castors. Trimmed here to clear them (the front bumper clash is left as an open issue, see sheet 9).
replace('BY HDPE bay floor', box(500, 790, -380, 380, 120, 130).union(box(790, 980, -120, 120, 120, 130)), 'BY HDPE bay floor 10 mm, cut back at the front corners for the castors')
replace('BY HDPE side walls', box(500, 790, -386, -380, 130, 300).union(box(500, 790, 380, 386, 130, 300)), 'BY HDPE side walls, ending 140 mm earlier for the castors')
replace('BL Ballast plate', box(930, 1050, -115, 115, 130, 153), 'BL Ballast plate 5 kg, narrower and thicker to clear the castors')
for pfx in ('SF Front bumper (switch', 'SF Bumper corner', 'SF Front bumper stripe', 'DK Dock charge contact'):
    for r_ in find(pfx): r_[3] = r_[3].translate(cq.Vector(65, 0, 0)); r_[5] = 'changed'
for s, n in ((1, 'L'), (-1, 'R')):
    add('SF Bumper bracket %s 8 mm plate from the nose cross-member' % n, 'tug', 'steel', box(980, 1115, s * 70 - 4, s * 70 + 4, 300, 360).union(box(1085, 1115, s * 70 - 4, s * 70 + 4, 156, 300)))
replace('SN Sensor post D40', cylz(410, 1060, 1000, 0, 20).union(box(955, 1040, -45, 45, 410, 418)), 'SN Sensor post D40 on a foot plate on the nose cross-member')
# ------------------------------------------------------------------ 2. electrical devices in the parts list but not in their CAD (positions proposed)
add('EL Power box: 2 contactors, lift driver, charge fuse and ideal diode', 'tug', 'pbox', box(610, 770, 170, 360, 130, 250))
add('EL Main fuse 50 A in a holder on the battery positive', 'tug', 'red', box(734, 784, -62, -22, 280, 298))
add('EL Battery isolator key switch 100 A (on the power box, through the cover)', 'tug', 'red', cylz(250, 332, 690, 265, 18).union(box(682, 698, 245, 285, 332, 344)))
add('SF Reset button, blue illuminated', 'tug', 'blue', cylz(306, 324, 600, -230, 13))
for s, n in ((1, 'L'), (-1, 'R')):
    add('LT Headlight %s (dipped)' % n, 'tug', 'lamp', cylx(980, 1018, s * 300, 385, 27))
    add('LT Rear red marker %s' % n, 'tug', 'red', box(-401, -396, s * 430 - 22, s * 430 + 22, 404, 426))
    add('SN Wheel encoder + speed sensor %s' % n, 'tug', 'sensor', box(48, 82, min(s * 450, s * 465), max(s * 450, s * 465), 150, 182))
add('LT Mast-top red marker', 'tug', 'red', box(520, 526, -30, 30, 1384, 1406))
add('LT Rear work lamp 3 W', 'tug', 'lamp', cylx(444, 470, -110, 1395, 20))
add('SN Radar, rear', 'tug', 'sensor', box(455, 470, 60, 104, 1378, 1412)); add('SN Radar, front', 'tug', 'sensor', box(1018, 1042, -22, 22, 560, 604))
add('AU USB microphone', 'tug', 'sensor', cylz(1420, 1452, 495, -150, 8)); add('AU Horn speaker 15 W', 'tug', 'dark', cylx(1020, 1072, 0, 470, 40))
add('CM LTE antenna', 'tug', 'white', cylz(930, 1045, 1000, 46, 8).union(box(985, 1015, 18, 52, 922, 930)))
# ------------------------------------------------------------------ poses of the simulation bodies relative to the robot frame
def qmat(q):
    w, x, y, z = q; return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
def poses(frame):
    q = Q[frame]; Rt = qmat(q[0, 3:]); pt = q[0, :3]; return {n: (Rt.T @ qmat(q[k, 3:]), Rt.T @ (q[k, :3] - pt)) for k, n in enumerate(BODIES)}
POSE = dict(nobin=poses(M['frames']['start']), carry=poses(M['frames']['carrying']))
INST = {'wheel': ['wheelL', 'wheelR'], 'cfork': ['cforkL', 'cforkR'], 'cwheel': ['cwheelL', 'cwheelR'], 'bw': ['bwL', 'bwR']}
