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
HERE = os.path.dirname(os.path.abspath(__file__))
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
def mesh(w, tol=0.4, ang=0.10):
    v, t = w.tessellate(tol, ang); return np.array([[p.x, p.y, p.z] for p in v], np.float64) / 1000.0, np.array(t, np.int32)

# ------------------------------------------------------------------ item numbers, plain names, explode offsets
# (item, plain name, qty, [name prefixes], explode group, parts-list reference, note)
ITEMS = [
 (1, 'Side rail, 50 x 50 x 4 box section', 2, ['FR Side rail'], 'core', 'FAB-B2 (S12)', 'S12 section: 4 mm wall in place of 2 mm'),
 (2, 'Mast-base cross-member, 50 x 50 x 2', 1, ['FR Mast-base'], 'core', 'FAB-B2', ''),
 (3, 'Nose cross-member, raised to rail height', 1, ['FR Nose cross-member'], 'core', 'FAB-B2', 'raised 117 mm to clear the castor beam'),
 (4, 'Drive / motor plate, 6 mm', 2, ['FR Drive/motor plate'], 'drive', 'FAB-B2', ''),
 (5, 'Gearmotor 320 W with spring brake', 2, ['DR Gearmotor'], 'drive', 'DRV-M8 or donor chair', ''),
 (6, 'Chain case, 3.5:1 chain stage', 2, ['DR Chain case'], 'drive', 'DRV-W8', ''),
 (7, 'Axle stub, 25 mm', 2, ['DR Axle stub'], 'drive', 'DRV-W8', ''),
 (8, 'Wheel encoder and speed sensor', 2, ['SN Wheel encoder'], 'drive', 'G9, SPD-S8', 'on the outer face of the motor plate, clear of the wheel'),
 (9, 'Drive wheel 330 mm with hub', 2, ['DR Drive wheel'], 'wheel', 'DRV-W8', ''),
 (10, 'Castor cross-beam, pivots at its centre', 1, ['RK Castor cross-beam', 'RK Castor mounting plate'], 'rocker', 'not in the BOM', 'pivot pin 200 mm above the ground; stops at 2 degrees each way'),
 (11, 'Pivot pin M16 with bushed hanger plates', 1, ['RK Pivot'], 'pivot', 'not in the BOM', 'one bush in each hanger plate, 70 mm apart'),
 (12, 'Bump stop, rubber', 2, ['RK Bump stop'], 'rocker', 'not in the BOM', 'about 10 mm of travel at each castor'),
 (13, 'Castor 200 mm: fork, wheel, hub', 2, ['CA Castor'], 'castor', 'DRV-C7', ''),
 (14, 'Side guard, UHMW plastic', 2, ['GU UHMW guard'], 'guard', 'FAB-B2', ''),
 (15, 'Mouth flare, UHMW plastic', 2, ['GU Mouth flare'], 'guard', 'FAB-B2', ''),
 (16, 'Leg-tip gap sensor (distance sensor)', 2, ['SN Leg-tip gap sensor'], 'guard', 'B2-GAP', ''),
 (17, 'Anti-tip bracket and roller', 2, ['AT Anti-tip'], 'antitip', 'G12', ''),
 (18, 'Rear bumper with safety switch', 2, ['SF Rear bumper'], 'rearbump', 'BMP-L8, G22', ''),
 (19, 'Rear red marker', 2, ['LT Rear red marker'], 'rearbump', 'L2', ''),
 (20, 'Front bumper with safety switches', 1, ['SF Front bumper', 'SF Bumper corner'], 'frontbump', 'BMP-L8, G22', 'moved 65 mm forward: 15 mm clear of a castor swivelled forward'),
 (21, 'Dock charge contact', 2, ['DK Dock charge contact'], 'contacts', 'D2', 'moved with the bumper'),
 (22, 'Headlight, dipped', 2, ['LT Headlight'], 'headl', 'L1', ''),
 (23, 'Mast upright 80 x 40 x 4', 2, ['LM Mast upright'], 'mast', 'FAB-B2 (S12)', 'S12 section; top at 1,370 mm'),
 (24, 'Mast gusset', 2, ['LM Mast gusset'], 'mast', 'FAB-B2', 'moved to the new upright face'),
 (25, 'Mast top tie', 1, ['LM Mast top tie'], 'mast', 'FAB-B2', ''),
 (26, 'Linear rail HGR15, 1 m', 2, ['LM Linear rail'], 'rail', 'B-1', 'mounted 60 mm higher, on backing flats'),
 (27, 'Lift actuator 24 V 4 kN, 400 mm IP65 unit', 1, ['LA Lift actuator'], 'act', 'B-0 (now 300 mm)', 'base pin 60 mm lower; stops at 340 mm; BOM line B-0 to change to the 400 mm unit'),
 (28, 'Carriage plate with actuator bracket', 1, ['LC Carriage plate', 'LC Actuator bracket'], 'carriage', 'FAB-B2', 'plate 80 mm deeper; bracket longer to reach the actuator'),
 (29, 'Rail carriage block', 4, ['LC Rail carriage'], 'carriage', 'B-1', '200 mm apart (S12)'),
 (30, 'Comb face plate, sprung', 1, ['LC Comb face plate'], 'face', 'FAB-B2', 'one cable hole added'),
 (31, 'Comb pivot block with centring springs', 1, ['LC Comb pivot block'], 'face', 'FAB-B2', ''),
 (32, 'Comb plate 700 mm with lifting nib', 1, ['LC Comb plate', 'LC Nib'], 'comb', 'FAB-B2 (S12)', '60 mm wider than B2-F; 8 mm plate'),
 (33, 'Nib seat switch', 1, ['SW Nib seat switch'], 'nibsw', 'B-4', 'flush in the comb plate'),
 (34, 'Comb contact switch', 1, ['SW Comb contact switch'], 'face', 'G13', ''),
 (35, 'Comb distance sensor', 2, ['SN Comb ToF'], 'face', 'B1-TOF2, B-4', ''),
 (37, 'Pad arm and guide block, fixed', 1, ['PD Pad arm', 'PD Pad guide block'], 'pad', 'FAB-B2', 'pad no longer retracts'),
 (38, 'Pad slide rods, spring cup plate and springs', 1, ['PD Pad slide rods', 'PD Pad die springs', 'PD Pad springs'], 'padrods', 'B-3', '45 mm sprung stroke'),
 (39, 'Pad face, UHMW plastic 300 x 100', 1, ['PD Pad UHMW face'], 'padface', 'B-3', '11 mm behind the nib tip'),
 (40, 'Pad contact switch', 1, ['SW Pad contact switch'], 'padface', 'G13', ''),
 (41, 'Bay floor, HDPE 10 mm', 1, ['BY HDPE bay floor'], 'bayfloor', 'FAB-B2', 'front corners cut back: in the B2-F CAD the floor passes through the castors'),
 (42, 'Bay side walls, HDPE', 2, ['BY HDPE side walls'], 'baywall', 'FAB-B2', 'end 140 mm earlier, to clear the castors'),
 (43, 'Rear cover, fixed', 1, ['BY HDPE rear cover'], 'coverR', 'FAB-B2', ''),
 (44, 'Front cover, removable', 1, ['BY HDPE front cover'], 'coverF', 'FAB-B2', 'shortened to clear the castor beam; not drawn in the assembled views'),
 (45, 'Battery 24 V 20 Ah with BMS', 1, ['PW Battery'], 'bat', 'G14', 'moved 58 mm back to clear the castor beam and its pin'),
 (46, 'Ballast plate 5 kg', 1, ['BL Ballast'], 'ballast', 'none matches', 'narrower and thicker to clear the castors; BOM lines BT-01 and B-6 describe other ballast'),
 (47, 'Electronics pod', 1, ['EL Electronics pod'], 'pod', 'G26', 'contents listed on the parts-list sheet; not drawn individually'),
 (48, 'Power box: two contactors, lift driver, charge fuse', 1, ['EL Power box'], 'pbox', 'KM-L8, G16', 'the lift driver has no BOM line yet'),
 (49, 'Battery isolator key switch', 1, ['EL Battery isolator'], 'pbox', 'S3', ''),
 (50, 'E-stop button', 1, ['SF E-stop'], 'coverR', 'S8', ''),
 (51, 'Reset button', 1, ['SF Reset button'], 'coverR', 'RST-G7', ''),
 (52, 'Sensor post on foot plate', 1, ['SN Sensor post'], 'post', 'FAB-B2', 'foot moved onto the raised cross-member'),
 (53, '2D lidar with bracket and window', 1, ['SN Lidar bracket', 'SN 2D lidar', 'SN Lidar window'], 'post', 'G21', ''),
 (54, 'Front camera', 1, ['SN Front camera'], 'post', '', 'in their CAD; no line found in the parts list'),
 (55, 'GNSS antenna (RTK)', 1, ['SN GNSS antenna'], 'post', 'RTK-L8', ''),
 (56, 'LTE antenna', 1, ['CM LTE antenna'], 'post', 'G25', ''),
 (57, 'Radar, front', 1, ['SN Radar, front'], 'post', 'RD-G6', ''),
 (58, 'Horn speaker', 1, ['AU Horn speaker'], 'post', 'AU-L8', ''),
 (59, 'Rear camera with infra-red light', 1, ['SN Rear camera'], 'masttop', 'G23', ''),
 (60, 'Amber beacon', 1, ['SF Amber beacon'], 'masttop', 'L3', ''),
 (61, 'Rear work lamp', 1, ['LT Rear work lamp'], 'masttop', 'L4', ''),
 (62, 'Mast-top red marker', 1, ['LT Mast-top red marker'], 'masttop', 'L2', ''),
 (63, 'Radar, rear', 1, ['SN Radar, rear'], 'masttop', 'RD-G6', ''),
 (64, 'Microphone', 1, ['AU USB microphone'], 'masttop', 'AU-L8', ''),
 (65, 'Main fuse 50 A at the battery', 1, ['EL Main fuse'], 'bat', 'S1', 'at the battery positive, as the BOM says'),
 (66, 'Bumper bracket plate', 2, ['SF Bumper bracket'], 'frontbump', 'not in the BOM', 'carries the bumper 65 mm further forward, between the castors'),
 (67, 'Lift hard stop at 345 mm', 2, ['LM Lift hard stop'], 'rail', 'not in the BOM', 'clamped on the rail; keeps 25 mm under the top tie if the switch fails'),
 (68, 'Lift top limit switch', 1, ['SW Lift top limit'], 'mast', 'not in the BOM', 'in the up feed of the lift driver; trips at 340 mm'),
 (69, 'Rail backing flat 30 x 10', 2, ['LM Rail backing flat'], 'rail', 'S12', ''),
 (70, 'Mast foot plate with crush tubes', 2, ['LM Mast foot plate'], 'mast', 'S12', ''),
 (71, 'Actuator base bracket', 1, ['LA Actuator base bracket'], 'act', 'not in the BOM', 'on the front face of the mast-base cross-member'),
 (101, '240 L bin body', 1, ['BIN 240 L body', 'BIN Plain rim', 'BIN EN 840'], 'bin', '', "catalogue model, not Brian's measured bin"),
 (102, 'Bin lid', 1, ['BIN Lid'], 'binlid', '', ''),
 (103, 'Bin handle bar and brackets', 1, ['BIN Handle'], 'binhandle', '', ''),
 (104, 'Bin wheels and axle', 1, ['BIN Axle', 'BIN Wheel'], 'binwheel', '', ''),
]
# explode offsets (m) in the robot frame; 'side' groups move outward in +/-y by the second number
EX = dict(core=(0, 0, 0), drive=(0, .30, 0), wheel=(0, .58, 0), rocker=(.42, 0, -.16), pivot=(.26, 0, 0), castor=(.42, 0, -.46), guard=(0, 0, -.42), antitip=(-.30, 0, -.16),
          rearbump=(-.42, 0, 0), frontbump=(.80, 0, 0), contacts=(.95, 0, 0), headl=(.34, 0, .06), mast=(0, 0, .44), rail=(-.14, 0, .44), act=(.22, 0, .72), carriage=(-.44, 0, .44),
          face=(-.66, 0, .44), comb=(-.90, 0, .44), nibsw=(-.90, 0, .56), keeper=(-.66, 0, .72), pad=(-.52, 0, .10), padrods=(-.66, 0, .10), padface=(-.82, 0, .10), bayfloor=(0, 0, -.44), baywall=(0, .20, -.26),
          coverR=(-.10, -1.25, .10), coverF=(.10, 1.25, .10), bat=(0, 0, .30), ballast=(0, 0, -.32), pod=(0, 0, .34), pbox=(0, 0, .30), post=(.34, 0, .40), masttop=(0, 0, .70),
          bin=(-1.30, 0, .16), binlid=(-1.30, 0, .52), binhandle=(-1.62, 0, .16), binwheel=(-1.30, 0, -.22), loom=(0, 0, 0))
SIDE = {'drive', 'wheel', 'baywall'}
def item_of(name):
    hit = [it for it in ITEMS if any(name.startswith(p) for p in it[3])]; assert len(hit) == 1, (name, [h[0] for h in hit]); return hit[0]

OUT = []
for name, grp, col, w, render, src in PARTS:
    it = item_of(name); V, T = mesh(w)
    for b in INST.get(grp, [grp]):
        e = dict(name=name + ('' if b == grp else ' ' + b[-1]), item=it[0], grp=grp, body=b, col=tuple(COL[col]), T=T, src=src, render=render, kind='part', exgroup=it[4],
                 with_bin_only=grp in ('bin', 'bw', 'lid'))
        for st in ('nobin', 'carry'):
            R, p = POSE[st][b]; e['V_' + st] = (V @ R.T + p).astype(np.float32)
        cy = float(e['V_nobin'][:, 1].mean()); ex = EX[it[4]]
        e['explode'] = (ex[0], (1 if cy >= 0 else -1) * ex[1], ex[2]) if it[4] in SIDE else tuple(ex)
        OUT.append(e)

# ------------------------------------------------------------------ 3. wiring looms (PROPOSED routing; there is no B2-F wiring table yet)
def tube(pts, r, n=10):
    """triangles of a round tube along a polyline, with a ball at every joint so the bends are closed"""
    V = []; T = []
    def add_mesh(v, t):
        o = sum(len(a) for a in V); V.append(v); T.append(t + o)
    for a, b in zip(pts[:-1], pts[1:]):
        a = np.array(a, float); b = np.array(b, float); d = b - a; L = np.linalg.norm(d)
        if L < 1e-6: continue
        d /= L; u = np.cross(d, [0, 0, 1.0]); u = np.cross(d, [0, 1.0, 0]) if np.linalg.norm(u) < 1e-3 else u; u /= np.linalg.norm(u); w = np.cross(d, u)
        ang = np.linspace(0, 2 * math.pi, n, endpoint=False); ring = np.array([r * (math.cos(t) * u + math.sin(t) * w) for t in ang])
        v = np.r_[a + ring, b + ring, [a], [b]]; t = []
        for i in range(n):
            j = (i + 1) % n; t += [[i, j, n + j], [i, n + j, n + i], [2 * n, j, i], [2 * n + 1, n + i, n + j]]
        add_mesh(v, np.array(t, np.int32))
    for p in pts:   # joint balls (octahedron subdivided once is round enough at this size)
        p = np.array(p, float); lat = [(-1, 1), (0, 6), (1, 1)]; v = [p + [0, 0, -r]]
        ring = [p + r * np.array([math.cos(t), math.sin(t), 0]) for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)]; v += ring; v.append(p + [0, 0, r]); t = []
        for i in range(8):
            j = (i + 1) % 8; t += [[0, 1 + j, 1 + i], [9, 1 + i, 1 + j]]
        add_mesh(np.array(v), np.array(t, np.int32))
    return np.vstack(V).astype(np.float32), np.vstack(T).astype(np.int32)
def mir(pl): return [(x, -y, z) for x, y, z in pl]
def uloop(xa, xb, y, zl, n=9):
    """hanging U-shaped loop of cable in the plane y: down at xa, round the bottom at height zl, up at xb"""
    r = abs(xa - xb) / 2; xc = (xa + xb) / 2; sg = 1 if xa > xb else -1
    return [(xc + sg * r * math.cos(math.pi * k / n), y, zl + r - r * math.sin(math.pi * k / n)) for k in range(n + 1)]
def lift_pts(st, pl):
    R, p = POSE[st]['lift']; return [tuple(R @ np.array(q, float) + p) for q in pl]
pz = (G['nib_h'] - G['pad_dz'])   # pad centre height in the lift frame (m)
def uloop_y(ya, yb, x, zl, n=9):
    """hanging U-shaped loop in the plane x: down at ya, round the bottom at height zl, up at yb"""
    r = abs(ya - yb) / 2; yc = (ya + yb) / 2; sg = 1 if ya > yb else -1
    return [(x, yc + sg * r * math.cos(math.pi * k / n), zl + r - r * math.sin(math.pi * k / n)) for k in range(n + 1)]
def looms(st):
    R, p = POSE[st]['lift']; Mv = R @ np.array([0.060, 0.07, 0.10]) + p; A = (0.475, 0.172, 1.10); zl = min(A[2], float(Mv[2])) - 0.22   # A: chain anchor on the mast, Mv: moving end on the carriage
    drvL = [(0.585, 0.125, 0.25), (0.585, 0.36, 0.25), (0.56, 0.36, 0.25), (0.56, 0.36, 0.425), (0.53, 0.398, 0.425), (-0.05, 0.398, 0.425), (-0.05, 0.42, 0.452)]
    encL = [(0.065, 0.398, 0.425), (0.065, 0.458, 0.425), (0.065, 0.458, 0.186)]   # over the rail and down the OUTER face of the motor plate, clear of the wheel
    rearL = [(0.572, 0.125, 0.232), (0.572, 0.346, 0.232), (0.546, 0.346, 0.232), (0.546, 0.346, 0.432), (0.53, 0.398, 0.432), (0.44, 0.398, 0.432), (0.42, 0.398, 0.385), (-0.33, 0.398, 0.385), (-0.372, 0.43, 0.40)]   # along the inner face of the rail, under the gearmotor
    rearL2 = [(-0.33, 0.398, 0.385), (-0.33, 0.398, 0.36), (-0.362, 0.40, 0.215)]
    return [
     ('L1', 'Battery power trunk', 'battery positive through the main fuse to the isolator key and the contactors in the power box; switched feed on to the pod', '2 x 10 mm2', (0.80, 0.10, 0.10), 0.008,
      [[(0.76, -0.022, 0.290), (0.76, 0.13, 0.290), (0.74, 0.20, 0.262), (0.74, 0.20, 0.25)], [(0.66, 0.17, 0.19), (0.66, 0.122, 0.19)]]),
     ('L2', 'Left drive loom', 'pod to left gearmotor and brake; sensor drop over the rail and down the outside of the motor plate', 'motor pair 6 mm2, brake pair, 2 signal cables', (1.00, 0.55, 0.00), 0.006, [drvL, encL]),
     ('L3', 'Right drive loom', 'as L2, mirrored', 'as L2', (1.00, 0.55, 0.00), 0.006, [mir(drvL), mir(encL)]),
     ('L4', 'Rear loom, left and right', 'pod along the inner face of each side rail, under the gearmotor, to rear bumper switches, leg-tip gap sensors, rear markers', 'stop-loop pair, sensor cable, lamp pair each side', (0.95, 0.82, 0.10), 0.006,
      [rearL, rearL2, mir(rearL), mir(rearL2)]),
     ('L5', 'Lift actuator loom', 'lift driver in the power box, up through the rear cover, to the actuator motor', 'motor pair 2.5 mm2', (0.55, 0.35, 0.20), 0.007,
      [[(0.66, 0.17, 0.24), (0.66, 0.145, 0.27), (0.66, 0.145, 0.325), (0.64, 0.03, 0.36)]]),
     ('L6', 'Mast-top loom', 'pod up the front of the right upright to rear camera, beacon, work lamp, marker, rear radar, microphone', 'USB cable, 4 lamp pairs, radar cable', (0.10, 0.70, 0.85), 0.007,
      [[(0.58, -0.06, 0.29), (0.58, -0.06, 0.325), (0.573, -0.185, 0.325), (0.573, -0.185, 1.385), (0.529, -0.17, 1.395), (0.529, 0.15, 1.395), (0.50, 0.15, 1.427)], [(0.529, 0.0, 1.395), (0.50, 0.0, 1.428), (0.46, 0.0, 1.437)],
       [(0.529, -0.11, 1.395), (0.529, -0.11, 1.428), (0.47, -0.11, 1.428), (0.458, -0.11, 1.41)], [(0.529, -0.15, 1.395), (0.50, -0.15, 1.427)], [(0.529, 0.082, 1.395), (0.529, 0.082, 1.428), (0.474, 0.082, 1.428), (0.462, 0.082, 1.418)]]),
     ('L7', 'Carriage loom', 'pod up the front of the left upright to a cable chain anchored on the mast; one hand-off on the carriage, then to the 2 comb distance sensors, comb, nib and pad switches. Also the lift top limit switch', '3 sensor cables, 4 switch pairs', (0.15, 0.35, 0.90), 0.006,
      [[(0.58, 0.06, 0.29), (0.58, 0.06, 0.325), (0.573, 0.185, 0.325), (0.573, 0.185, 1.10), (0.573, 0.172, 1.10), A], [(0.573, 0.185, 1.10), (0.573, 0.185, 1.313), (0.573, 0.231, 1.313), (0.482, 0.231, 1.313)],
       [A] + uloop_y(A[1], 0.07, A[0], zl) + [tuple(Mv)],
       lift_pts(st, [(0.060, 0.07, 0.10), (0.047, 0.07, 0.10), (0.047, 0.07, -0.08), (-0.006, 0.07, -0.08), (-0.006, 0.18, -0.08), (-0.006, 0.18, -0.022)]), lift_pts(st, [(-0.006, 0.07, -0.08), (-0.006, -0.18, -0.08), (-0.006, -0.18, -0.022)]),
       lift_pts(st, [(0.047, 0.07, 0.10), (0.047, 0.115, 0.025), (0.002, 0.115, 0.025)]), lift_pts(st, [(-0.006, 0.07, -0.08), (-0.06, 0.06, -0.04), (-0.122, 0.06, -0.04), (-0.122, 0.02, -0.018)]),
       lift_pts(st, [(-0.006, 0.13, -0.08), (-0.006, 0.13, pz + 0.05), (-0.10, 0.16, pz + 0.05), (-0.115, 0.16, pz + 0.02)])]),
     ('L8', 'Sensor-post loom', 'pod along the bay floor and up the post to lidar, front camera, GNSS, LTE antenna, front radar, horn', 'lidar cable, USB cable, 2 coax, radar cable, speaker pair', (0.60, 0.25, 0.80), 0.007,
      [[(0.72, 0.10, 0.24), (0.905, 0.10, 0.24), (0.905, 0.10, 0.425), (0.955, 0.06, 0.425), (1.0, 0.028, 0.45), (1.0, 0.028, 1.05)], [(1.0, 0.028, 0.815), (1.03, 0.02, 0.815)], [(1.0, 0.028, 0.725), (1.02, 0.03, 0.725)],
       [(1.0, 0.028, 0.58), (1.02, 0.02, 0.58)], [(1.0, 0.028, 0.47), (1.025, 0.024, 0.47)]]),
     ('L9', 'Nose loom', 'pod up behind the castor beam, along the nose cross-member to the headlights, down between the castors and under the bumper to its switches and the charge contacts. The charge pair runs back to the 10 A fuse in the power box', 'stop-loop pair, 2 lamp pairs, charge pair 2.5 mm2', (0.10, 0.62, 0.28), 0.007,
      [[(0.72, -0.10, 0.24), (0.905, -0.10, 0.24), (0.905, -0.10, 0.425), (0.955, -0.10, 0.425), (1.003, -0.10, 0.385)], [(1.003, -0.30, 0.385), (1.003, 0.30, 0.385)],
       [(1.003, 0.12, 0.385), (1.105, 0.12, 0.30), (1.105, 0.12, 0.118), (1.158, 0.12, 0.118), (1.158, 0.12, 0.142)], [(1.003, -0.12, 0.385), (1.105, -0.12, 0.30), (1.105, -0.12, 0.118), (1.158, -0.12, 0.118), (1.158, -0.12, 0.142)]]),
     ('L10', 'Operator-controls loom', 'pod to E-stop and reset button', '2 stop-loop pairs, lamp and button pairs', (0.90, 0.20, 0.60), 0.006,
      [[(0.64, -0.12, 0.275), (0.64, -0.30, 0.275), (0.64, -0.30, 0.302)], [(0.60, -0.12, 0.275), (0.60, -0.23, 0.275), (0.60, -0.23, 0.302)]]),
     ('L11', 'Safety and control loom', 'pod to power box: the two contactor coils from the safety relay, the contactor feedback contacts, switched-feed voltage sense, lift up and down commands', '2 coil pairs, feedback pair, sense pair, 2 command pairs', (0.95, 0.40, 0.70), 0.006,
      [[(0.70, 0.122, 0.215), (0.70, 0.17, 0.215)]]),
    ]
# in the exploded view a loom travels with the part it is tied to: L5 with the actuator, L6 and the fixed run of L7 with the mast, the carriage branches of L7 with the carriage, L8 with the sensor post
LEX = dict(L5=['act'], L6=['mast'] * 5, L7=['mast', 'mast', 'mast'] + ['carriage'] * 5, L8=['post'] * 5, L11=['pod'])
LN = {}
for st in ('nobin', 'carry'):
    for k, (lid, lname, route, cores, col, r, pls) in enumerate(looms(st)):
        exg = LEX.get(lid, ['loom'] * len(pls)); assert len(exg) == len(pls), lid
        for g in dict.fromkeys(exg):
            Vs = []; Ts = []; o = 0
            for pl, pg in zip(pls, exg):
                if pg != g: continue
                v, t = tube(pl, r); Vs.append(v); Ts.append(t + o); o += len(v)
            LN.setdefault((lid, g), dict(name=lname + ' (proposed route)', item=200 + k + 1, loom=lid, grp='tug', body='tug', col=col, src='new', render=True, kind='loom', exgroup=g, with_bin_only=False,
                                         explode=tuple(EX[g]), route=route, cores=cores, T=np.vstack(Ts)))['V_' + st] = np.vstack(Vs)
OUT += list(LN.values())
ITEMS_OUT = [dict(item=i, name=n, qty=q, ref=ref, note=note, exgroup=eg) for i, n, q, pf, eg, ref, note in ITEMS]
ITEMS_OUT += [dict(item=e['item'], name='%s  %s' % (e['loom'], e['name'].replace(' (proposed route)', '')), qty=1, ref='HX-G6, PWR-G8, H1', note=e['route'] + '. ' + e['cores'], exgroup='loom', loom=e['loom'])
              for e in {e['item']: e for e in reversed(list(LN.values()))}.values()]
ITEMS_OUT.sort(key=lambda d: d['item'])
src_of = {}
for e in OUT: src_of.setdefault(e['item'], set()).add(e['src'])
for it in ITEMS_OUT: it['src'] = 'new' if src_of[it['item']] == {'new'} else ('changed' if 'changed' in src_of[it['item']] or 'new' in src_of[it['item']] else 'CAD')
pickle.dump(dict(parts=OUT, items=ITEMS_OUT, geo=G, lift_q_carry=M['lift_q_carry'], grab=M['grab']), open(os.path.join(HERE, 'model.pkl'), 'wb'))
print('pieces', len(OUT), 'items', len(ITEMS_OUT), 'triangles', sum(len(e['T']) for e in OUT))
print('by source:', {s: sum(1 for it in ITEMS_OUT if it['src'] == s) for s in ('CAD', 'changed', 'new')})
used = {e['item'] for e in OUT}; print('items without geometry:', [it['item'] for it in ITEMS_OUT if it['item'] not in used])
A = np.vstack([e['V_nobin'] for e in OUT if not e['with_bin_only']]); print('robot envelope nobin (mm): x %.0f..%.0f  y %.0f..%.0f  z %.0f..%.0f' % tuple(1000 * v for v in (A[:, 0].min(), A[:, 0].max(), A[:, 1].min(), A[:, 1].max(), A[:, 2].min(), A[:, 2].max())))
