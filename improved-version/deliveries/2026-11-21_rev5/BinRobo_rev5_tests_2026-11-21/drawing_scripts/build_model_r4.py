#!/usr/bin/env python3
"""Improved-version model for the drawing set, revision 4 (20 Nov 2026). Sections 1 and 2 are revision 2; 2b is revision 3; 2c holds the changes made after the review of revision 3.

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

# ------------------------------------------------------------------ 2b. revision 3 (14 Nov 2026): the answers to the review of revision 2
def sy(sg, a, b): return (min(sg * a, sg * b), max(sg * a, sg * b))
def recut(prefix, tool):
    for r_ in find(prefix): r_[3] = r_[3].cut(val(tool)); r_[5] = 'changed'
# (a) frame drawn with its real walls; S355 for the rails and the mast-base cross-member
for s, n in ((1, 'L'), (-1, 'R')):
    replace('FR Side rail %s' % n, box(-370, 980, *sy(s, 405, 455), 360, 410).faces('<X or >X').shell(-4), 'FR Side rail %s 50x50x4 RHS S355' % n)
    add('FR Corner plate %s rear, 6 mm, welded over the rail / mast-base joint' % n, 'tug', 'steel', box(450, 530, *sy(s, 375, 455), 410, 416))
    add('FR Corner plate %s front, 6 mm, welded over the rail / nose joint' % n, 'tug', 'steel', box(915, 980, *sy(s, 375, 455), 410, 416))
    recut('DR Chain case %s' % n, box(-380, 990, *sy(s, 404, 456), 359, 411))          # the case is notched round the rail (it was drawn 5 mm into it)
    recut('GU UHMW guard %s' % n, cyly(*sy(s, 363, 369), 0, 165, 176))                 # 5 mm pocket behind the tyre: 2 mm clear of it
replace('FR Mast-base cross-member', box(465, 515, -405, 405, 360, 410).faces('<Y or >Y').shell(-5), 'FR Mast-base cross-member 50x50x5 RHS S355')
replace('FR Nose cross-member', box(930, 980, -405, 405, 360, 410).faces('<Y or >Y').shell(-3), 'FR Nose cross-member 50x50x3 RHS, at rail height')
# (b) mast foot: welded L-shoe (top plate + front leg) in place of the loose foot plate and the floating gussets; rails start above the cross-member
replace('LM Mast top tie', box(470, 520, -230, 230, 1370, 1420).faces('<Y or >Y').shell(-2), 'LM Mast top tie 50x50x2 RHS')
remove('LM Mast gusset'); remove('LM Mast foot plate'); remove('LM Lift hard stop'); remove('SW Lift top limit switch')
for s, n in ((1, 'L'), (-1, 'R')):
    replace('LM Mast upright %s' % n, box(480, 560, s * 200 - 20, s * 200 + 20, 420, 1370).faces('<Z or >Z').shell(-4), 'LM Mast upright %s 80x40x4 RHS, welded all round to its foot shoe' % n)
    replace('LM Rail backing flat %s' % n, box(470, 480, s * 200 - 15, s * 200 + 15, 420, 1360), 'LM Rail backing flat %s 30x10' % n)
    replace('LM Linear rail %s' % n, box(455, 470, s * 200 - 7.5, s * 200 + 7.5, 420, 1360), 'LM Linear rail %s HGR15, 940 mm' % n)
    add('LM Mast foot shoe %s: 10 mm S355 top plate and front leg' % n, 'tug', 'steel', box(465, 565, s * 200 - 45, s * 200 + 45, 410, 420).union(box(515, 525, s * 200 - 45, s * 200 + 45, 362, 410)))
    # (c) lift top and bottom ends: bolted stops with a tongue over the carriage plate edge, switches outboard of the plate
    add('LM Lift top stop %s: bolted 12 mm S355 bracket with tongue, 2 x M10 through the upright' % n, 'tug', 'red', box(427, 560, *sy(s, 220, 232), 1335, 1365).union(box(427, 445, *sy(s, 190, 220), 1335, 1365)))
    add('LM Lift bottom stop %s: bolted bracket with tongue, 2 x M10' % n, 'tug', 'red', box(427, 560, *sy(s, 220, 232), 690, 720).union(box(427, 445, *sy(s, 190, 220), 690, 720)))
    add('SW Lift top limit switch %s (channel %s), roller lever down to 1,327 mm' % (n, 'A' if s > 0 else 'B'), 'tug', 'switch', box(420, 450, *sy(s, 236, 258), 1338, 1368))
add('SW Lift down limit switch, roller lever up to 725 mm', 'tug', 'switch', box(420, 450, 236, 258, 684, 716))
# (d) carriage with real plate sizes. Plate 16 mm aluminium in front of the rail blocks (it was drawn 3 mm into the rails), striker tabs for the switches, tongue for the pad arm
remove('LC Rail carriage')
for s in (1, -1):
    for z0 in (-105, 95): add('LC Rail carriage block HGH15CA', 'lift', 'rail', box(26, 50, s * 200 - 23.5, s * 200 + 23.5, z0, z0 + 60), src='changed')
replace('LC Carriage plate', box(10, 26, -230, 230, -110, 165).union(box(10, 26, -60, 60, -260, -110)).union(box(10, 26, 230, 252, 140, 165)).union(box(10, 26, -252, -230, 140, 165)).union(box(10, 26, 230, 252, -110, -85))
        .cut(box(10, 26, 70, 165, -40, 90)).cut(box(10, 26, -165, -70, -40, 90)), 'LC Carriage plate 16 mm aluminium 6082, two windows, striker tabs, tongue for the pad arm')
for z0, nm in ((100, 'top'), (-100, 'bottom')): add('LC Carriage cross-beam 50x50x4 RHS S355 behind the plate, %s block row' % nm, 'lift', 'steel', box(26, 76, -170, 170, z0, z0 + 50).faces('<Y or >Y').shell(-4))
replace('LC Actuator bracket', box(76, 165, -45, 45, 140, 150).union(box(76, 165, -45, -39, 90, 140)).union(box(76, 165, 39, 45, 90, 140)), 'LC Actuator bracket: 10 mm S355 plate with two 6 mm cheeks, on the top cross-beam')
find('LC Comb face plate')[0][0] = 'LC Comb face plate (sprung, 10 mm UHMW)'
replace('LC Comb plate', box(0, 122, -350, 350, -8, 0), 'LC Comb plate 700 x 122 x 8 mm S355, self-aligning'); replace('LC Nib', box(-8, 0, -350, 350, -8, 20), 'LC Nib 8 long x 20 high, 700 mm')
# pad: arm is a box section hung from the plate tongue, below the comb pivot block (it was drawn through it); guide block clamped round the arm;
# rods move with the pad, two long springs give a real 45 mm stroke against a fixed cup plate behind the arm
pz_ = g['pz']
replace('PD Pad arm', box(-30, 10, -40, 40, -620, -52).faces('<Z or >Z').shell(-3), 'PD Pad arm 80x40x3 RHS, bolted to the carriage plate tongue (3 x M10)')
gb = box(-37, 14, -120, 120, pz_ - 35, pz_ + 35).cut(box(-30.5, 10.5, -40.5, 40.5, pz_ - 36, pz_ + 36))
for yy in (-90, 90): gb = gb.cut(cylx(-40, 20, yy, pz_, 9.5))
for yy in (-60, 60): gb = gb.cut(cylx(-40, 20, yy, pz_, 17))
replace('PD Pad guide block', gb, 'PD Pad guide block, aluminium, clamped round the arm, bushed for the rods')
remove('PD Pad slide rods')
add('PD Pad slide rods D16, fixed in the pad backing (move with the pad)', 'pad', 'steel', cylx(26, 119, -90, 0, 8).union(cylx(26, 119, 90, 0, 8)), src='changed')
add('PD Pad backing plate 6 mm aluminium', 'pad', 'steel', box(20, 26, -140, 140, -45, 45))
cup = box(150, 160, -130, 130, -30, 30)
for yy in (-90, 90): cup = cup.cut(cylx(149, 161, yy, 0, 9.5))
for yy in (-110, 110): cup = cup.union(cylx(133, 150, yy, 0, 6))
add('PD Pad spring cup plate 10 mm aluminium on two standoffs from the guide block (fixed)', 'padbase', 'steel', cup)
replace('PD Pad springs', cylx(26, 150, -60, 0, 15.5).union(cylx(26, 150, 60, 0, 15.5)), 'PD Pad springs 2 x 15 N/mm, outside diameter 31, wire 4.5, 134 mm free, 124 mm fitted')
# (e) actuator base bracket: real plate sizes
replace('LA Actuator base bracket', box(515, 525, -60, 60, 318, 410).union(box(525, 600, -60, 60, 318, 328)).union(box(525, 600, 54, 60, 328, 400)).union(box(525, 600, -60, -54, 328, 400))
        .union(box(540, 570, 18, 28, 328, 348)).union(box(540, 570, -28, -18, 328, 348)), 'LA Actuator base bracket: 10 mm S355 back plate and shelf, two gussets, clevis lugs; 2 x M12 through the mast-base cross-member')
# (f) castor-beam pivot: 10 mm S355 hanger plates welded to both faces of the nose cross-member, D20 pin
replace('RK Pivot hanger plate rear', box(920, 930, -45, 45, 170, 410), 'RK Pivot hanger plate rear 10 mm S355, welded to the nose cross-member')
replace('RK Pivot hanger plate front', box(980, 990, -45, 45, 170, 410), 'RK Pivot hanger plate front 10 mm S355, welded to the nose cross-member')
replace('RK Pivot pin', cylx(912, 998, 0, 200, 10), 'RK Pivot pin D20, bronze bushes in the beam housing, held in both hanger plates')
# (g) front bumper on a real carrier: two arms with drop legs between the castors, a fixed beam, the bumper bar sliding 15 mm on two sprung pins, a two-contact switch at each end
remove('SF Bumper bracket'); remove('BL Ballast plate')
for s, n in ((1, 'L'), (-1, 'R')):
    add('SF Bumper carrier arm %s 40x40x2 with drop leg, flange welded to the nose cross-member' % n, 'tug', 'steel',
        box(980, 988, s * 90 - 30, s * 90 + 30, 355, 415).union(box(988, 1090, s * 90 - 20, s * 90 + 20, 365, 405).faces('<X or >X').shell(-2)).union(box(1050, 1090, s * 90 - 20, s * 90 + 20, 165, 365).faces('<Z or >Z').shell(-2)))
    add('SF Bumper guide pin D12 with return spring %s' % n, 'tug', 'hub', cylx(1115, 1132, s * 150, 185, 6))
    add('SW Front bumper switch %s, two normally-closed contacts (one per channel)' % n, 'tug', 'switch', box(1117, 1129, *sy(s, 178, 202), 172, 198))
add('SF Bumper carrier beam 40x25x2, fixed to the drop legs', 'tug', 'steel', box(1090, 1115, -200, 200, 165, 205).faces('<Y or >Y').shell(-2))
replace('SF Front bumper (switch', box(1130, 1155, -330, 330, 130, 230), 'SF Front bumper bar: rubber strip on an aluminium backing, slides 15 mm on two pins')
# (h) drawing faults listed in the review: lidar clear of the post, cable holes in the covers, cable-chain brackets
replace('SN 2D lidar', cylz(830, 905, 1080, 0, 50)); replace('SN Lidar window', cylz(845, 885, 1080, 0, 51)); replace('SN Lidar bracket', box(1015, 1095, -15, 15, 818, 830), 'SN Lidar bracket, 80 mm arm from the post')
rc = box(520, 720, -386, 386, 300, 306).cut(cylz(299, 307, 690, 265, 20)).cut(cylz(299, 307, 640, -300, 11)).cut(cylz(299, 307, 600, -230, 11)).cut(cylz(299, 307, 660, 145, 9)).cut(cylz(299, 307, 580, 60, 9)).cut(cylz(299, 307, 580, -60, 9))
for s in (1, -1): rc = rc.cut(box(545, 565, *sy(s, 333, 364), 299, 307))
replace('BY HDPE rear cover', rc, 'BY HDPE rear cover (fixed), with cable grommets')
replace('BY HDPE front cover', box(720, 915, -386, 386, 300, 306).cut(cylz(299, 307, 905, 100, 9)).cut(cylz(299, 307, 905, -100, 9)).cut(cylz(299, 307, 905, 140, 9)), 'BY HDPE front cover (removable, shortened), with cable grommets')
add('CH Cable chain anchor bracket on the left upright', 'tug', 'steel', box(497, 513, 162, 180, 1085, 1115))
add('CH Cable chain bracket on the carriage', 'lift', 'steel', box(26, 98, 60, 80, 76, 100))
# (i) drive/motor plate: it was drawn up through the inside of the side rail. Now it stops under the rail, with a 6 mm top flange bolted up through the rail (4 x M8 in crush tubes)
for s, n in ((1, 'L'), (-1, 'R')):
    r_ = find('FR Drive/motor plate %s' % n)[0]; r_[3] = r_[3].cut(val(box(-101, 101, *sy(s, 404, 456), 360, 411))).fuse(val(box(-100, 100, *sy(s, 405, 450), 354, 360))); r_[5] = 'changed'
    r_[0] = 'FR Drive/motor plate %s 6 mm S355 with top flange bolted up through the rail' % n
# comb plate notched for the two distance sensors that look past it
for s in (1, -1): recut('LC Comb plate', box(109, 123, s * 180 - 16, s * 180 + 16, -9, 1))

# ------------------------------------------------------------------ 2c. revision 4 (20 Nov 2026): the answers to the review of revision 3
# (a) side rails 60x60x4 S355, bottom face level with the cross-members (top 10 mm higher). Cross-members butt against the rail's inner face.
for s, n in ((1, 'L'), (-1, 'R')):
    replace('FR Side rail %s' % n, box(-370, 980, *sy(s, 395, 455), 360, 420).faces('<X or >X').shell(-4), 'FR Side rail %s 60x60x4 RHS S355' % n)
    recut('DR Chain case %s' % n, box(-380, 990, *sy(s, 394, 456), 359, 421))
    for r_ in find('DR Gearmotor %s' % n): r_[3] = r_[3].translate(cq.Vector(0, 0, 10)); r_[5] = 'changed'
    # drive / motor plate 8 mm (was 6): for the sideways tyre load. It ends under the rail with a top flange bolted up through the rail (4 x M8 in crush tubes)
    replace('FR Drive/motor plate %s' % n, box(-100, 100, *sy(s, 442, 450), 120, 360).union(box(-100, 100, *sy(s, 395, 450), 354, 360)), 'FR Drive/motor plate %s 8 mm S355 with top flange bolted up through the rail' % n)
replace('FR Mast-base cross-member', box(465, 515, -395, 395, 360, 410).faces('<Y or >Y').shell(-5), 'FR Mast-base cross-member 50x50x5 RHS S355')
replace('FR Nose cross-member', box(930, 980, -395, 395, 360, 410).faces('<Y or >Y').shell(-4), 'FR Nose cross-member 50x50x4 RHS S355, at rail height')
# (a0) the last welds of the castor beam and the actuator bracket become bolted or screwed joints (names only; geometry unchanged)
find('RK Castor cross-beam pivot housing')[0][0] = 'RK Castor cross-beam pivot housing: steel block bolted up through the beam (2 x M8), pin fixed in it'
for n in ('L', 'R'): find('RK Castor mounting plate %s' % n)[0][0] = 'RK Castor mounting plate %s 6 mm, bolted up through the beam (2 x M8)' % n
# (b) frame joints bolted, no weld: a top and a bottom plate over each joint, bolts through crush tubes in rail and cross-member
remove('FR Corner plate')
for s, n in ((1, 'L'), (-1, 'R')):
    for x0, x1, w in ((440, 540, 'rear'), (895, 985, 'front')):
        add('FR Corner plate %s %s, top, 6 mm S355, bolted (packer on the cross-member)' % (n, w), 'tug', 'steel', box(x0 + 5, x1 - 5, *sy(s, 340, 450), 420, 426).union(box(465 if w == 'rear' else 930, 515 if w == 'rear' else 980, *sy(s, 340, 393), 410, 420)))
        add('FR Corner plate %s %s, bottom, 6 mm S355, bolted' % (n, w), 'tug', 'steel', box(x0 + 5, x1 - 5, *sy(s, 340, 450), 354, 360))
# (c) mast: uprights stand on the cross-member, held by two angle cleats each; a strut from each upright to the nose cross-member takes the
#     tipping moment of the hanging bin, so the foot joint and the cross-member no longer carry it
remove('LM Mast foot shoe'); remove('LM Lift top stop'); remove('LM Lift bottom stop'); remove('SW Lift down limit switch')
import math as _m
def strut(xa, za, xb, zb, y0, sec=30, wall=2, over=20):
    L = _m.hypot(xb - xa, zb - za) + 2 * over; ang = _m.degrees(_m.atan2(za - zb, xb - xa))
    t = cq.Workplane('XY').box(L, sec, sec).cut(cq.Workplane('XY').box(L + 2, sec - 2 * wall, sec - 2 * wall))
    return t.rotate((0, 0, 0), (0, 1, 0), ang).translate(((xa + xb) / 2.0, y0, (za + zb) / 2.0))
for s, n in ((1, 'L'), (-1, 'R')):
    replace('LM Mast upright %s' % n, box(480, 560, s * 200 - 20, s * 200 + 20, 410, 1370).faces('<Z or >Z').shell(-4), 'LM Mast upright %s 80x40x4 RHS, on two bolted angle cleats' % n)
    add('LM Mast foot cleat %s outer: angle 60x60x6, 50 long' % n, 'tug', 'steel', box(465, 515, *sy(s, 220, 226), 410, 470).union(box(465, 515, *sy(s, 220, 280), 410, 416)))
    add('LM Mast foot cleat %s inner: angle 60x60x6, 50 long' % n, 'tug', 'steel', box(465, 515, *sy(s, 174, 180), 410, 470).union(box(465, 515, *sy(s, 120, 180), 410, 416)))
    add('LM Mast strut %s 30x30x2 RHS, pinned at both ends (M10)' % n, 'tug', 'steel', strut(592, 770, 955, 462, s * 200))
    add('LM Mast strut lug plates %s on the upright, 5 mm, 2 x M8 through the upright' % n, 'tug', 'steel', box(520, 616, *sy(s, 220, 225), 740, 800).union(box(520, 616, *sy(s, 175, 180), 740, 800)))
    add('LM Mast strut foot cleats %s on the nose cross-member, two angles 40x40x4 S355' % n, 'tug', 'steel',
        box(935, 975, *sy(s, 176, 180), 410, 485).union(box(935, 975, *sy(s, 140, 180), 410, 414)).union(box(935, 975, *sy(s, 220, 224), 410, 485)).union(box(935, 975, *sy(s, 220, 260), 410, 414)))
    # (d) lift ends: a stop block on the inner face of each upright catches the end of the carriage cross-beam. No tongue, no weld.
    add('LM Lift top stop block %s: 30x50 aluminium bar on the inner face of the upright, 2 x M10 through it; the top tie is bolted down onto it' % n, 'tug', 'red', box(445, 540, *sy(s, 144, 174), 1320, 1370).union(box(480, 540, *sy(s, 174, 180), 1320, 1370)))
    add('LM Lift bottom stop block %s: 30x45 aluminium bar on the inner face of the upright, 2 x M10 through it' % n, 'tug', 'red', box(445, 540, *sy(s, 144, 174), 672, 717).union(box(480, 540, *sy(s, 174, 180), 672, 717)))
    add('SW Lift down limit switch %s (channel %s), roller lever up to 725 mm' % (n, 'A' if s > 0 else 'B'), 'tug', 'switch', box(420, 450, *sy(s, 236, 258), 669, 701))
replace('LM Mast top tie', box(470, 520, -230, 230, 1370, 1420).faces('<Y or >Y').shell(-2), 'LM Mast top tie 50x50x2 RHS')
# (e) lift actuator: an outdoor unit with published holding force and its own end-stop switches (drawn: LINAK LA36, 6.8 kN, 350 mm stroke,
#     600 mm between the pins when closed; outline ASSUMED from the catalogue). Base pin at z 335 so that its own stops come at -15 and +331 mm of
#     carriage travel: inside the bolted blocks (-18 and +335) and outside the limit switches (0 and +327).
remove('LA Lift actuator motor')
replace('LA Lift actuator FDI', box(533, 597, -42, 42, 352, 440).union(cylz(440, 905, 565, 0, 30)).union(box(553, 577, -12, 12, 320, 350)), 'LA Lift actuator, outdoor unit 24 V 6.8 kN, 350 mm stroke, own end stops (drawn: LINAK LA36)')
add('LA Lift actuator motor (across the unit)', 'tug', 'dark', cylx(597, 760, 0, 395, 33), src='changed')
replace('LA Lift actuator rod', cylz(-330, 100, 150, 0, 15).union(box(138, 162, -12, 12, 100, 130)), 'LA Lift actuator rod D30 with rod eye')
replace('LC Actuator bracket', box(76, 190, -45, 45, 140, 150).union(box(76, 190, -45, -39, 90, 140)).union(box(76, 190, 39, 45, 90, 140)), 'LC Actuator bracket: 10 mm S355 plate and two 6 mm cheeks screwed to its edges (M6), bolted on the top cross-beam')
replace('LA Actuator base bracket', box(515, 527, -60, 60, 295, 405).union(box(527, 615, -60, 60, 295, 307)).union(box(545, 585, 14, 20, 307, 350)).union(box(545, 585, -20, -14, 307, 350)).union(box(545, 585, 20, 50, 307, 313)).union(box(545, 585, -50, -20, 307, 313)),
        'LA Actuator base bracket: angle 100x100x12 S355, 120 long, 2 x M12 through the cross-member; two bolted lug angles on a shim pack')
# carriage plate: a second striker tab at the bottom, for the right-hand down switch
replace('LC Carriage plate', box(10, 26, -230, 230, -110, 165).union(box(10, 26, -60, 60, -260, -110)).union(box(10, 26, 230, 252, 140, 165)).union(box(10, 26, -252, -230, 140, 165)).union(box(10, 26, 230, 252, -110, -85)).union(box(10, 26, -252, -230, -110, -85))
        .cut(box(10, 26, 70, 165, -40, 90)).cut(box(10, 26, -165, -70, -40, 90)), 'LC Carriage plate 16 mm aluminium 6082, two windows, four striker tabs, tongue for the pad arm')
# (f) pad springs 145 mm free (was 134): 15.7 mm short of solid at full stroke. The springs run in bores through the guide block
replace('PD Pad springs', cylx(26, 161, -60, 0, 15.5).union(cylx(26, 161, 60, 0, 15.5)), 'PD Pad springs 2 x 15 N/mm, outside diameter 31, wire 4.5, 145 mm free, 135 mm fitted')
cup = box(156, 166, -130, 130, -30, 30)
for yy in (-90, 90): cup = cup.cut(cylx(155, 167, yy, 0, 9.5))
for yy in (-60, 60): cup = cup.cut(cylx(156, 161, yy, 0, 16.5))          # 5 mm pockets locate the spring ends
for yy in (-110, 110): cup = cup.union(cylx(133, 156, yy, 0, 6))
replace('PD Pad spring cup plate', cup, 'PD Pad spring cup plate 10 mm aluminium with spring pockets, on two standoffs from the guide block (fixed)')
# (g) castor-beam pivot: the two hanger plates are clamped on the nose cross-member by 4 x M10 through it (no weld)
replace('RK Pivot hanger plate rear', box(920, 930, -60, 60, 340, 410).union(box(920, 930, -45, 45, 170, 340)), 'RK Pivot hanger plate rear 10 mm S355, bolted through the nose cross-member')
replace('RK Pivot hanger plate front', box(980, 990, -60, 60, 340, 410).union(box(980, 990, -45, 45, 170, 340)), 'RK Pivot hanger plate front 10 mm S355, bolted through the nose cross-member')
# (h) front: a foam safety bumper 300 mm deep in place of the 15 mm sliding bar. Carrier: two laser-cut side plates (arm and drop leg in one piece)
#     on angle cleats, and a backing beam. Charge contacts move from the bumper face to pads under the nose.
for pfx in ('SF Front bumper bar', 'SF Bumper corner', 'SF Front bumper stripe', 'DK Dock charge contact', 'SF Bumper guide pin', 'SW Front bumper switch', 'SF Bumper carrier arm', 'SF Bumper carrier beam'): remove(pfx)
for s, n in ((1, 'L'), (-1, 'R')):
    add('SF Bumper carrier side bracket %s: 5 mm S355, laser-cut and folded (arm and drop leg in one piece, stiffening flanges)' % n, 'tug', 'steel',
        box(985, 1090, *sy(s, 150, 155), 365, 405).union(box(1050, 1090, *sy(s, 150, 155), 150, 365)).union(box(1085, 1090, *sy(s, 155, 190), 150, 365)).union(box(985, 1085, *sy(s, 155, 190), 400, 405)).union(box(980, 985, *sy(s, 100, 155), 360, 410)))
    add('DK Charge contact pad %s under the nose, on a 4 mm bracket' % n, 'tug', 'red', box(1085, 1125, *sy(s, 40, 80), 100, 106).union(box(1090, 1094, *sy(s, 40, 80), 106, 160)))
add('SF Bumper carrier backing beam 40x40x2 RHS, bolted to the drop legs', 'tug', 'steel', box(1090, 1130, -330, 330, 160, 200).faces('<Y or >Y').shell(-2))
add('SF Safety bumper: foam, 300 deep x 150 high x 700 wide, two-channel switching mat inside', 'tug', 'rubber',
    cq.Workplane('XY').polyline([(1130, -350), (1330, -350), (1430, -250), (1430, 250), (1330, 350), (1130, 350)]).close().extrude(150).translate((0, 0, 115)))
# (i) under the bin: two light beams across the mouth, 40 mm above the ground (sender on the left, receiver on the right)
for xb, w in ((-270, 'A'), (-195, 'B')):
    for s, n in ((1, 'sender'), (-1, 'receiver')):
        add('SF Under-bin light beam %s, %s' % (w, n), 'tug', 'switch', box(xb - 8, xb + 8, *sy(s, 372, 392), 32, 48))
# (j) rear cover: cut-out for the actuator base bracket, cable holes moved
rc = box(520, 720, -386, 386, 300, 306).cut(cylz(299, 307, 690, 265, 20)).cut(cylz(299, 307, 640, -300, 11)).cut(cylz(299, 307, 600, -230, 11)).cut(cylz(299, 307, 660, 145, 9)).cut(cylz(299, 307, 580, 78, 9)).cut(cylz(299, 307, 580, -78, 9)).cut(box(519, 625, -65, 65, 299, 307))
for s in (1, -1): rc = rc.cut(box(545, 565, *sy(s, 298, 334), 299, 307))
replace('BY HDPE rear cover', rc, 'BY HDPE rear cover (fixed), with cable grommets and a cut-out for the actuator base')
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
 (1, 'Side rail, 60 x 60 x 4 box section, S355', 2, ['FR Side rail'], 'core', 'S12-RAIL (to change)', '60 x 60 in place of 50 x 50: safety factor 2.1 on the largest wheel load of the load cases; S355'),
 (2, 'Mast-base cross-member, 50 x 50 x 5, S355', 1, ['FR Mast-base'], 'core', 'FAB-B2 (to change)', 'carries the mast feet and the actuator base; butts against the rails'),
 (3, 'Nose cross-member, 50 x 50 x 4, S355, at rail height', 1, ['FR Nose cross-member'], 'core', 'FAB-B2 (to change)', '4 mm wall, S355: carries the castor pivot plates, the mast strut feet and the bumper carrier. To become 60 x 60 x 4 (reply note, 3.6)'),
 (74, 'Corner plates 6 mm, bolted: top and bottom at each joint', 8, ['FR Corner plate'], 'core', 'new line needed', 'laser-cut S355; 4 x M8 8.8 per joint through crush tubes; 10 mm packer on the cross-member. No weld'),
 (4, 'Drive / motor plate, 8 mm, with top flange', 2, ['FR Drive/motor plate'], 'drive', 'FAB-B2 (to change)', '8 mm in place of 6 mm for the sideways tyre load; flange bolted up through the rail with 4 x M8'),
 (5, 'Gearmotor 320 W with spring brake', 2, ['DR Gearmotor'], 'drive', 'DRV-M8 or donor chair', ''),
 (6, 'Chain case, 3.5:1 chain stage', 2, ['DR Chain case'], 'drive', 'DRV-W8', ''),
 (7, 'Axle stub, 25 mm', 2, ['DR Axle stub'], 'drive', 'DRV-W8', ''),
 (8, 'Wheel encoder and speed sensor', 2, ['SN Wheel encoder'], 'drive', 'G9, SPD-S8', 'on the outer face of the motor plate, clear of the wheel'),
 (9, 'Drive wheel 330 mm with hub', 2, ['DR Drive wheel'], 'wheel', 'DRV-W8', ''),
 (10, 'Castor cross-beam, pivots at its centre', 1, ['RK Castor cross-beam', 'RK Castor mounting plate'], 'rocker', 'not in the BOM', 'pivot pin 200 mm above the ground; stops at 2 degrees each way'),
 (11, 'Pivot pin D20 with two 10 mm clamp plates', 1, ['RK Pivot'], 'pivot', 'S12-PIN; plates: new line', 'plates S355, clamped on the nose cross-member by 4 x M10 through it; bronze bushes in the beam housing'),
 (12, 'Bump stop, rubber', 2, ['RK Bump stop'], 'rocker', 'not in the BOM', 'about 10 mm of travel at each castor'),
 (13, 'Castor 200 mm: fork, wheel, hub', 2, ['CA Castor'], 'castor', 'DRV-C7 (to change)', 'round-profile tyre; swivel torque to be measured on the bench before ordering two (reply note, section 4)'),
 (14, 'Side guard, UHMW plastic', 2, ['GU UHMW guard'], 'guard', 'FAB-B2', ''),
 (15, 'Mouth flare, UHMW plastic', 2, ['GU Mouth flare'], 'guard', 'FAB-B2', ''),
 (16, 'Leg-tip gap sensor (distance sensor)', 2, ['SN Leg-tip gap sensor'], 'guard', 'B2-GAP', ''),
 (17, 'Anti-tip bracket and roller', 2, ['AT Anti-tip'], 'antitip', 'G12', ''),
 (18, 'Rear bumper with safety switch', 2, ['SF Rear bumper'], 'rearbump', 'BMP-L8, G22', ''),
 (19, 'Rear red marker', 2, ['LT Rear red marker'], 'rearbump', 'L2', ''),
 (20, 'Safety bumper, foam, 300 mm deep', 1, ['SF Safety bumper'], 'frontbump', 'BMP-L8 (to change)', 'pressure-sensitive bumper to EN ISO 13856-3 with its control unit; 150 mm of travel after it switches (maker to confirm)'),
 (21, 'Charge contact pad under the nose', 2, ['DK Charge contact'], 'contacts', 'D2 (to change)', 'the dock is a low floor shoe: docking no longer presses the bumper'),
 (22, 'Headlight, dipped', 2, ['LT Headlight'], 'headl', 'L1', ''),
 (23, 'Mast upright 80 x 40 x 4 with foot cleats', 2, ['LM Mast upright', 'LM Mast foot cleat'], 'mast', 'S12-MAST', 'stands on the cross-member; two angle cleats 60 x 60 x 6, bolted. No weld'),
 (25, 'Mast top tie 50 x 50 x 2', 1, ['LM Mast top tie'], 'mast', 'FAB-B2', 'bolted down onto the two top stop blocks'),
 (26, 'Linear rail HGR15, 940 mm', 2, ['LM Linear rail'], 'rail', 'B-1', 'starts above the cross-member, on a backing flat'),
 (27, 'Lift actuator 24 V, 6.8 kN, 350 mm, outdoor unit', 1, ['LA Lift actuator'], 'act', 'B-0 (to change)', 'needs: holding force at least 6 kN, IP66, own end-stop switches, 600 mm between pins closed. Drawn: LINAK LA36'),
 (28, 'Carriage: aluminium plate, two steel beams, bracket', 1, ['LC Carriage plate', 'LC Carriage cross-beam', 'LC Actuator bracket'], 'carriage', 'FAB-B2 (to change)', 'cross-beams 50 x 50 x 4 S355 carry the load to the rail blocks; their ends land on the stop blocks; bolted'),
 (29, 'Rail carriage block HGH15CA', 4, ['LC Rail carriage'], 'carriage', 'B-1', '200 mm apart'),
 (30, 'Comb face plate, sprung, UHMW plastic', 1, ['LC Comb face plate'], 'face', 'FAB-B2', ''),
 (31, 'Comb pivot block with D20 pin and centring springs', 1, ['LC Comb pivot block'], 'face', 'FAB-B2, S12-PIN', ''),
 (32, 'Comb plate 700 x 122 x 8 mm with lifting nib', 1, ['LC Comb plate', 'LC Nib'], 'comb', 'B2-COMB (to change)', '60 mm wider than B2-F; 8 mm S355 (BOM says 640 x 6)'),
 (33, 'Nib seat switch', 1, ['SW Nib seat switch'], 'nibsw', 'B-4', 'flush in the comb plate'),
 (34, 'Comb contact switch', 1, ['SW Comb contact switch'], 'face', 'G13', ''),
 (35, 'Comb distance sensor', 2, ['SN Comb ToF'], 'face', 'B1-TOF2, B-4', ''),
 (37, 'Pad arm 80 x 40 x 3 and guide block, fixed', 1, ['PD Pad arm', 'PD Pad guide block'], 'pad', 'FAB-B2 (to change)', 'arm hangs below the comb pivot block; pad no longer retracts'),
 (38, 'Pad rods, cup plate and two long springs', 1, ['PD Pad slide rods', 'PD Pad backing plate', 'PD Pad spring cup plate', 'PD Pad springs'], 'padrods', 'B-3 (to change)', 'springs 145 mm free, guided in bores through the guide block; 45 mm stroke: 300 N at first touch, 1.65 kN fully in'),
 (39, 'Pad face, UHMW plastic 300 x 100', 1, ['PD Pad UHMW face'], 'padface', 'B-3', '10 mm behind the nib tip'),
 (40, 'Pad contact switch', 1, ['SW Pad contact switch'], 'padface', 'G13', ''),
 (41, 'Bay floor, HDPE 10 mm', 1, ['BY HDPE bay floor'], 'bayfloor', 'FAB-B2', 'front corners cut back: in the B2-F CAD the floor passes through the castors'),
 (42, 'Bay side walls, HDPE', 2, ['BY HDPE side walls'], 'baywall', 'FAB-B2', 'end 140 mm earlier, to clear the castors'),
 (43, 'Rear cover, fixed, with cable grommets', 1, ['BY HDPE rear cover'], 'coverR', 'FAB-B2', ''),
 (44, 'Front cover, removable', 1, ['BY HDPE front cover'], 'coverF', 'FAB-B2', 'shortened to clear the castor beam; not drawn in the assembled views'),
 (45, 'Battery 24 V 20 Ah with BMS', 1, ['PW Battery'], 'bat', 'G14', 'moved 58 mm back to clear the castor beam and its pin'),
 (47, 'Electronics pod', 1, ['EL Electronics pod'], 'pod', 'G26', 'contents listed on the parts-list sheet; not drawn individually'),
 (48, 'Power box: two contactors, lift driver, pre-charge, fuses', 1, ['EL Power box'], 'pbox', 'KM-L8, G16; driver: new line', 'contents on sheet 15'),
 (49, 'Battery isolator key switch', 1, ['EL Battery isolator'], 'pbox', 'S3', ''),
 (50, 'E-stop button', 1, ['SF E-stop'], 'coverR', 'S8', ''),
 (51, 'Reset button', 1, ['SF Reset button'], 'coverR', 'RST-G7', ''),
 (52, 'Sensor post on foot plate', 1, ['SN Sensor post'], 'post', 'FAB-B2', 'foot moved onto the raised cross-member'),
 (53, '2D lidar with bracket and window', 1, ['SN Lidar bracket', 'SN 2D lidar', 'SN Lidar window'], 'post', 'G21', 'moved 45 mm forward, clear of the post'),
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
 (66, 'Bumper carrier: two folded side brackets, backing beam', 1, ['SF Bumper carrier'], 'frontbump', 'new line needed', 'laser-cut and folded 5 mm brackets, bolted to the nose cross-member between the castors; holds 1 kN sideways'),
 (72, 'Under-bin light beam, sender and receiver', 2, ['SF Under-bin light beam'], 'guard', 'new line needed', 'safety single-beam sensors 40 mm above the ground: no lowering while a beam is broken'),
 (67, 'Lift stop block, bolted (2 top, 2 bottom)', 4, ['LM Lift top stop', 'LM Lift bottom stop'], 'rail', 'new line needed', 'saw-cut 30 mm aluminium bar on the inner face of each upright, 2 x M10 through the upright in crush tubes; they stop the carriage beams at 335 mm and at -18 mm'),
 (68, 'Lift limit switch (2 top, 2 bottom)', 4, ['SW Lift top limit', 'SW Lift down limit'], 'mast', 'new line needed', 'top pair trips at 327 mm, bottom pair at 0 mm; one of each pair per stop channel'),
 (69, 'Rail backing flat 30 x 10', 2, ['LM Rail backing flat'], 'rail', 'S12-PLT', ''),
 (70, 'Mast strut 30 x 30 x 2 with lug plates and foot cleats', 2, ['LM Mast strut'], 'mast', 'new line needed', 'takes the tipping moment of the hanging bin to the nose cross-member; one M10 pin at each end; foot cleats in S355'),
 (71, 'Actuator base bracket: angle 100 x 100 x 12', 1, ['LA Actuator base bracket'], 'act', 'new line needed', '2 x M12 through the mast-base cross-member; lug angles on a shim pack set the height of the base pin'),
 (73, 'Cable chain end brackets (chain is loom L7)', 2, ['CH Cable chain'], 'rail', 'new line needed', 'chain 10 x 15 mm inside, about 0.6 m'),
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
    R, p = POSE[st]['lift']; Mv = R @ np.array([0.090, 0.07, 0.085]) + p; A = (0.505, 0.171, 1.10); zl = min(A[2], float(Mv[2])) - 0.17   # A: chain anchor on the mast, Mv: moving end on the carriage
    drvL = [(0.585, 0.125, 0.25), (0.585, 0.32, 0.25), (0.555, 0.32, 0.25), (0.555, 0.32, 0.425), (0.44, 0.32, 0.425), (0.42, 0.32, 0.385), (0.42, 0.388, 0.385), (-0.05, 0.388, 0.385), (-0.05, 0.374, 0.40), (-0.05, 0.374, 0.45)]   # over the cross-member, then along the INNER face of the rail behind the side guard
    encL = [(0.065, 0.388, 0.385), (0.065, 0.388, 0.432), (0.065, 0.4615, 0.432), (0.065, 0.4615, 0.186)]   # over the rail and down the OUTER face of the motor plate, clear of the wheel
    rearL = [(0.572, 0.125, 0.232), (0.572, 0.308, 0.232), (0.555, 0.308, 0.232), (0.555, 0.308, 0.438), (0.44, 0.308, 0.438), (0.42, 0.308, 0.372), (0.42, 0.388, 0.372), (-0.33, 0.388, 0.372), (-0.376, 0.388, 0.372), (-0.378, 0.43, 0.40)]   # along the inner face of the rail, under the gearmotor
    rearL2 = [(-0.33, 0.388, 0.372), (-0.33, 0.398, 0.36), (-0.362, 0.40, 0.215)]; beamA = [(-0.27, 0.388, 0.372), (-0.27, 0.382, 0.05)]; beamB = [(-0.195, 0.388, 0.372), (-0.195, 0.382, 0.05)]
    return [
     ('L1', 'Battery power trunk', 'battery positive through the main fuse to the isolator key and the contactors in the power box; switched feed on to the pod', '2 x 10 mm2', (0.80, 0.10, 0.10), 0.008,
      [[(0.76, -0.022, 0.290), (0.76, 0.13, 0.290), (0.74, 0.20, 0.262), (0.74, 0.20, 0.25)], [(0.66, 0.17, 0.19), (0.66, 0.122, 0.19)]]),
     ('L2', 'Left drive loom', 'pod, through a grommet in the rear cover, over the mast-base cross-member, then along the inner face of the side rail behind the side guard to the left gearmotor and brake; sensor drop over the rail and down the outside of the motor plate', 'motor pair 6 mm2, brake pair, 2 signal cables', (1.00, 0.55, 0.00), 0.006, [drvL, encL]),
     ('L3', 'Right drive loom', 'as L2, mirrored', 'as L2', (1.00, 0.55, 0.00), 0.006, [mir(drvL), mir(encL)]),
     ('L4', 'Rear loom, left and right', 'pod along the inner face of each side rail, under the gearmotor, to rear bumper switches, leg-tip gap sensors, rear markers and the two under-bin light beams', 'stop-loop pair, sensor cable, lamp pair, 2 light-beam cables each side', (0.95, 0.82, 0.10), 0.006,
      [rearL, rearL2, beamA, beamB, mir(rearL), mir(rearL2), mir(beamA), mir(beamB)]),
     ('L5', 'Lift actuator loom', 'lift driver in the power box, up through a grommet in the rear cover, to the actuator motor', 'motor pair 2.5 mm2', (0.55, 0.35, 0.20), 0.007,
      [[(0.66, 0.17, 0.24), (0.66, 0.145, 0.27), (0.66, 0.145, 0.34), (0.66, 0.045, 0.385)]]),
     ('L6', 'Mast-top loom', 'pod, through a grommet in the rear cover, up beside the inner face of the right upright to rear camera, beacon, work lamp, marker, rear radar, microphone, and the channel B lift limit switches (top and bottom)', 'USB cable, 4 lamp pairs, radar cable, 2 limit-switch pairs', (0.10, 0.70, 0.85), 0.007,
      [[(0.58, -0.078, 0.29), (0.58, -0.078, 0.325), (0.552, -0.166, 0.325), (0.552, -0.166, 1.385), (0.529, -0.166, 1.395), (0.529, 0.15, 1.395), (0.529, 0.15, 1.428), (0.50, 0.15, 1.428)], [(0.529, 0.0, 1.395), (0.529, 0.0, 1.428), (0.46, 0.0, 1.437)],
       [(0.552, -0.166, 1.30), (0.575, -0.166, 1.30), (0.575, -0.245, 1.30), (0.452, -0.245, 1.30), (0.452, -0.245, 1.338)], [(0.552, -0.166, 0.66), (0.575, -0.166, 0.66), (0.575, -0.245, 0.66), (0.452, -0.245, 0.66)],
       [(0.529, -0.11, 1.395), (0.529, -0.11, 1.428), (0.47, -0.11, 1.428), (0.458, -0.11, 1.41)], [(0.529, -0.15, 1.395), (0.529, -0.15, 1.428), (0.50, -0.15, 1.428)], [(0.529, 0.082, 1.395), (0.529, 0.082, 1.428), (0.474, 0.082, 1.428), (0.462, 0.082, 1.418)]]),
     ('L7', 'Carriage loom', 'pod up beside the inner face of the left upright to a cable chain anchored on the mast; one hand-off on the carriage, then to the 2 comb distance sensors, comb, nib and pad switches. Also the channel A lift limit switches (top and bottom)', '3 sensor cables, 5 switch pairs', (0.15, 0.35, 0.90), 0.006,
      [[(0.58, 0.078, 0.29), (0.58, 0.078, 0.325), (0.552, 0.166, 0.325), (0.552, 0.166, 1.10), A], [(0.552, 0.166, 1.10), (0.552, 0.166, 1.30), (0.575, 0.166, 1.30), (0.575, 0.245, 1.30), (0.452, 0.245, 1.30), (0.452, 0.245, 1.338)], [(0.552, 0.166, 0.66), (0.575, 0.166, 0.66), (0.575, 0.245, 0.66), (0.452, 0.245, 0.66)],
       [A] + uloop_y(A[1], 0.07, A[0], zl) + [tuple(Mv)],
       lift_pts(st, [(0.090, 0.07, 0.085), (0.085, 0.07, 0.06), (0.085, 0.07, -0.125), (-0.006, 0.07, -0.125), (-0.006, 0.18, -0.125), (-0.006, 0.18, -0.022)]), lift_pts(st, [(-0.006, 0.07, -0.125), (-0.038, 0.05, -0.125), (-0.038, -0.05, -0.125), (-0.006, -0.07, -0.125), (-0.006, -0.18, -0.125), (-0.006, -0.18, -0.022)]),
       lift_pts(st, [(0.085, 0.07, 0.06), (0.047, 0.115, 0.05), (0.047, 0.115, 0.025), (0.002, 0.115, 0.025)]), lift_pts(st, [(-0.006, 0.07, -0.125), (-0.06, 0.06, -0.04), (-0.122, 0.06, -0.04), (-0.122, 0.02, -0.018)]),
       lift_pts(st, [(-0.006, 0.13, -0.125), (-0.006, 0.13, pz + 0.05), (-0.10, 0.16, pz + 0.05), (-0.115, 0.16, pz + 0.02)])]),
     ('L8', 'Sensor-post loom', 'pod along the bay floor and up the post to lidar, front camera, GNSS, LTE antenna, front radar, horn', 'lidar cable, USB cable, 2 coax, radar cable, speaker pair', (0.60, 0.25, 0.80), 0.007,
      [[(0.72, 0.10, 0.24), (0.905, 0.10, 0.24), (0.905, 0.10, 0.428), (0.955, 0.06, 0.428), (1.0, 0.028, 0.45), (1.0, 0.028, 1.05)], [(1.0, 0.028, 0.815), (1.03, 0.02, 0.815)], [(1.0, 0.028, 0.725), (1.02, 0.03, 0.725)],
       [(1.0, 0.028, 0.58), (1.02, 0.02, 0.58)], [(1.0, 0.028, 0.47), (1.025, 0.024, 0.47)]]),
     ('L9', 'Nose loom', 'pod, up through a grommet in the front cover behind the castor beam, along the rear face of the nose cross-member to the headlights; over the member and down the inside of the right bumper side plate to the safety bumper', 'bumper cable (2 channels), 2 lamp pairs', (0.10, 0.62, 0.28), 0.007,
      [[(0.72, -0.10, 0.24), (0.905, -0.10, 0.24), (0.905, -0.10, 0.395), (0.922, -0.10, 0.395)], [(0.922, -0.30, 0.395), (0.922, -0.075, 0.395), (0.922, -0.075, 0.425), (0.922, 0.075, 0.425), (0.922, 0.075, 0.395), (0.922, 0.30, 0.395)],
       [(0.922, 0.30, 0.395), (0.922, 0.30, 0.428), (0.985, 0.30, 0.418)], [(0.922, -0.30, 0.395), (0.922, -0.30, 0.428), (0.985, -0.30, 0.418)],
       [(0.922, -0.14, 0.395), (0.922, -0.14, 0.428), (0.99, -0.14, 0.424), (1.04, -0.14, 0.42), (1.04, -0.14, 0.215), (1.083, -0.14, 0.215), (1.083, -0.10, 0.215)]]),
     ('L10', 'Operator-controls loom', 'pod to E-stop and reset button', '2 stop-loop pairs, lamp and button pairs', (0.90, 0.20, 0.60), 0.006,
      [[(0.64, -0.12, 0.275), (0.64, -0.30, 0.275), (0.64, -0.30, 0.302)], [(0.60, -0.12, 0.275), (0.60, -0.23, 0.275), (0.60, -0.23, 0.302)]]),
     ('L11', 'Safety and control loom', 'pod to power box: the two contactor coils from the safety controller, the mirror contacts of both contactors, pre-charge relay, switched-feed voltage sense, lift up and down commands and the lift-driver fault line', '2 coil pairs, 2 feedback pairs, pre-charge pair, sense pair, 3 signal pairs', (0.95, 0.40, 0.70), 0.006,
      [[(0.70, 0.122, 0.215), (0.70, 0.17, 0.215)]]),
     ('L12', 'Charge loom', 'the two charge pads under the nose, up the inside of the left bumper side plate, over the nose cross-member and down through its own grommet to the 10 A charge fuse in the power box. Kept apart from the bumper cable of L9, which runs on the right side plate', 'charge pair 2.5 mm2', (0.85, 0.45, 0.10), 0.006,
      [[(1.105, -0.06, 0.113), (1.105, 0.06, 0.113), (1.105, 0.14, 0.113), (1.083, 0.14, 0.113), (1.083, 0.14, 0.215), (1.04, 0.14, 0.215), (1.04, 0.14, 0.42), (0.99, 0.14, 0.424), (0.955, 0.14, 0.44), (0.905, 0.14, 0.44), (0.905, 0.14, 0.24), (0.72, 0.19, 0.24), (0.69, 0.19, 0.24)]]),
    ]
# in the exploded view a loom travels with the part it is tied to: L5 with the actuator, L6 and the fixed run of L7 with the mast, the carriage branches of L7 with the carriage, L8 with the sensor post
LEX = dict(L5=['act'], L6=['mast'] * 7, L7=['mast', 'mast', 'mast', 'mast'] + ['carriage'] * 5, L8=['post'] * 5, L11=['pod'])
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
ITEMS_OUT += [dict(item=e['item'], name='%s  %s' % (e['loom'], e['name'].replace(' (proposed route)', '')), qty=1, ref='PC-G7' if e['loom'] == 'L11' else 'PWR-G8, H1', note=e['route'] + '. ' + e['cores'], exgroup='loom', loom=e['loom'])
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
