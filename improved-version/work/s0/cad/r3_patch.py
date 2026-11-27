#!/usr/bin/env python3
"""Writes build_model.py (revision 3) from build_model_r2.py: inserts the revision 3 geometry section, and edits the item list and the loom routes."""
import re
s = open('build_model_r2.py').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70]); s = s.replace(a, b)

R3 = r'''
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
'''
rep("# ------------------------------------------------------------------ poses of the simulation bodies relative to the robot frame", R3 + "# ------------------------------------------------------------------ poses of the simulation bodies relative to the robot frame")
rep('"""Improved-version model for the drawing set.', '"""Improved-version model for the drawing set, revision 3 (14 Nov 2026). Sections 1 and 2 are revision 2; section 2b holds the changes made after the review of revision 2.')

# ---------------------------------------------------------------- item list
def item(n, new):
    global s
    m = re.search(r"^ \(%d, .*\),\n" % n, s, re.M); assert m, n
    s = s[:m.start()] + new + s[m.end():]
item(1, " (1, 'Side rail, 50 x 50 x 4 box section, S355', 2, ['FR Side rail'], 'core', 'S12-RAIL', 'drawn with its 4 mm wall; must be S355 (safety factor 2.2; 1.5 in S235)'),\n")
item(2, " (2, 'Mast-base cross-member, 50 x 50 x 5, S355', 1, ['FR Mast-base'], 'core', 'FAB-B2 (to change)', '5 mm wall for the twist from the mast (was 2 mm)'),\n")
item(3, " (3, 'Nose cross-member, 50 x 50 x 3, at rail height', 1, ['FR Nose cross-member'], 'core', 'FAB-B2 (to change)', '3 mm wall (was 2 mm); carries the castor pivot plates and the bumper arms'),\n (74, 'Corner plate 6 mm, welded over each frame joint', 4, ['FR Corner plate'], 'core', 'new line needed', ''),\n")
item(4, " (4, 'Drive / motor plate, 6 mm, with top flange', 2, ['FR Drive/motor plate'], 'drive', 'FAB-B2', 'ends under the rail; flange bolted up through the rail with 4 x M8'),\n")
item(13, " (13, 'Castor 200 mm: fork, wheel, hub', 2, ['CA Castor'], 'castor', 'DRV-C7 (to change)', 'needs a round-profile tyre, not the flat 50 mm tread of the BOM line: see the reply note, section 3.3'),\n")
item(11, " (11, 'Pivot pin D20 with two 10 mm hanger plates', 1, ['RK Pivot'], 'pivot', 'S12-PIN; plates: new line', 'plates S355, welded to both faces of the nose cross-member; bronze bushes in the beam housing'),\n")
item(20, " (20, 'Front bumper bar with rubber strip', 1, ['SF Front bumper', 'SF Bumper corner'], 'frontbump', 'BMP-L8, G22', 'slides 15 mm on two sprung pins; 65 mm further forward than B2-F'),\n")
item(23, " (23, 'Mast upright 80 x 40 x 4', 2, ['LM Mast upright'], 'mast', 'S12-MAST', 'welded all round (5 mm fillet) to its foot shoe; top at 1,370 mm'),\n")
item(24, "")
item(26, " (26, 'Linear rail HGR15, 940 mm', 2, ['LM Linear rail'], 'rail', 'B-1', 'starts above the cross-member, on a backing flat'),\n")
item(27, " (27, 'Lift actuator 24 V 4 kN, 400 mm IP65 unit', 1, ['LA Lift actuator'], 'act', 'B-0 (to change)', 'BOM line is the 300 mm unit. Travel used 305 mm; firmware stop 320, switches 327, bolted stops 335 mm; holding force to be confirmed by the supplier'),\n")
item(28, " (28, 'Carriage: aluminium plate, two steel beams, bracket', 1, ['LC Carriage plate', 'LC Carriage cross-beam', 'LC Actuator bracket'], 'carriage', 'FAB-B2 (to change)', 'cross-beams 50 x 50 x 4 S355 carry the load to the rail blocks; striker tabs for the limit switches; tongue for the pad arm'),\n")
item(29, " (29, 'Rail carriage block HGH15CA', 4, ['LC Rail carriage'], 'carriage', 'B-1', '200 mm apart'),\n")
item(30, " (30, 'Comb face plate, sprung, UHMW plastic', 1, ['LC Comb face plate'], 'face', 'FAB-B2', ''),\n")
item(31, " (31, 'Comb pivot block with D20 pin and centring springs', 1, ['LC Comb pivot block'], 'face', 'FAB-B2, S12-PIN', ''),\n")
item(32, " (32, 'Comb plate 700 x 122 x 8 mm with lifting nib', 1, ['LC Comb plate', 'LC Nib'], 'comb', 'B2-COMB (to change)', '60 mm wider than B2-F; 8 mm S355 (BOM says 640 x 6)'),\n")
item(37, " (37, 'Pad arm 80 x 40 x 3 and guide block, fixed', 1, ['PD Pad arm', 'PD Pad guide block'], 'pad', 'FAB-B2 (to change)', 'arm hangs below the comb pivot block; pad no longer retracts'),\n")
item(38, " (38, 'Pad rods, cup plate and two long springs', 1, ['PD Pad slide rods', 'PD Pad backing plate', 'PD Pad spring cup plate', 'PD Pad springs'], 'padrods', 'B-3 (to change)', '45 mm sprung stroke: 300 N at first touch, 1.65 kN fully pushed in'),\n")
item(39, " (39, 'Pad face, UHMW plastic 300 x 100', 1, ['PD Pad UHMW face'], 'padface', 'B-3', '10 mm behind the nib tip'),\n")
item(43, " (43, 'Rear cover, fixed, with cable grommets', 1, ['BY HDPE rear cover'], 'coverR', 'FAB-B2', ''),\n")
item(46, "")
item(48, " (48, 'Power box: two contactors, lift driver, pre-charge, fuses', 1, ['EL Power box'], 'pbox', 'KM-L8, G16; driver: new line', 'contents on sheet 15'),\n")
item(53, " (53, '2D lidar with bracket and window', 1, ['SN Lidar bracket', 'SN 2D lidar', 'SN Lidar window'], 'post', 'G21', 'moved 45 mm forward, clear of the post'),\n")
item(66, " (66, 'Bumper carrier: two arms, drop legs, beam, two pins', 1, ['SF Bumper carrier', 'SF Bumper guide'], 'frontbump', 'new line needed', 'welded to the nose cross-member, between the castors; holds 1 kN sideways'),\n (72, 'Front bumper switch, two contacts', 2, ['SW Front bumper switch'], 'frontbump', 'BMP-L8', 'one contact of each switch in each stop channel'),\n")
item(67, " (67, 'Lift stop bracket, bolted (2 top, 2 bottom)', 4, ['LM Lift top stop', 'LM Lift bottom stop'], 'rail', 'new line needed', 'top stops catch the carriage plate at 335 mm, 35 mm under the top tie'),\n")
item(68, " (68, 'Lift limit switch (2 top, 1 bottom)', 3, ['SW Lift top limit', 'SW Lift down limit'], 'mast', 'new line needed', 'top pair trips at 327 mm, one per stop channel'),\n")
item(69, " (69, 'Rail backing flat 30 x 10', 2, ['LM Rail backing flat'], 'rail', 'S12-PLT', ''),\n")
item(70, " (70, 'Mast foot shoe, 10 mm top plate and front leg', 2, ['LM Mast foot shoe'], 'mast', 'S12-PLT (to change)', '2 x M12 down through the cross-member in crush tubes + 2 x M12 through the front leg'),\n")
item(71, " (71, 'Actuator base bracket, 10 mm', 1, ['LA Actuator base bracket'], 'act', 'new line needed', '2 x M12 through the mast-base cross-member'),\n (73, 'Cable chain end brackets (chain is loom L7)', 2, ['CH Cable chain'], 'rail', 'new line needed', 'chain 10 x 15 mm inside, about 0.6 m'),\n")
rep("ballast=(0, 0, -.32), ", "ballast=(0, 0, -.32), ")

# ---------------------------------------------------------------- looms
rep("drvL = [(0.585, 0.125, 0.25), (0.585, 0.36, 0.25), (0.56, 0.36, 0.25), (0.56, 0.36, 0.425), (0.53, 0.398, 0.425), (-0.05, 0.398, 0.425), (-0.05, 0.42, 0.452)]",
    "drvL = [(0.585, 0.125, 0.25), (0.585, 0.355, 0.25), (0.555, 0.355, 0.25), (0.555, 0.355, 0.425), (0.53, 0.398, 0.425), (0.44, 0.398, 0.425), (0.42, 0.398, 0.398), (-0.05, 0.398, 0.398), (-0.05, 0.398, 0.44), (-0.05, 0.42, 0.452)]   # over the cross-member, then along the INNER face of the rail behind the side guard")
rep("encL = [(0.065, 0.398, 0.425), (0.065, 0.458, 0.425), (0.065, 0.458, 0.186)]", "encL = [(0.065, 0.398, 0.398), (0.065, 0.398, 0.425), (0.065, 0.4615, 0.425), (0.065, 0.4615, 0.186)]")
rep("rearL = [(0.572, 0.125, 0.232), (0.572, 0.346, 0.232), (0.546, 0.346, 0.232), (0.546, 0.346, 0.432), (0.53, 0.398, 0.432), (0.44, 0.398, 0.432), (0.42, 0.398, 0.385), (-0.33, 0.398, 0.385), (-0.372, 0.43, 0.40)]",
    "rearL = [(0.572, 0.125, 0.232), (0.572, 0.342, 0.232), (0.555, 0.342, 0.232), (0.555, 0.342, 0.438), (0.53, 0.398, 0.438), (0.44, 0.398, 0.438), (0.42, 0.398, 0.384), (-0.33, 0.398, 0.384), (-0.378, 0.398, 0.40), (-0.378, 0.43, 0.40)]")
rep("rearL2 = [(-0.33, 0.398, 0.385), (-0.33, 0.398, 0.36), (-0.362, 0.40, 0.215)]", "rearL2 = [(-0.33, 0.398, 0.384), (-0.33, 0.398, 0.36), (-0.362, 0.40, 0.215)]")
rep("'pod to left gearmotor and brake; sensor drop over the rail and down the outside of the motor plate'", "'pod, through a grommet in the rear cover, over the mast-base cross-member, then along the inner face of the side rail behind the side guard to the left gearmotor and brake; sensor drop over the rail and down the outside of the motor plate'")
rep("'lift driver in the power box, up through the rear cover, to the actuator motor'", "'lift driver in the power box, up through a grommet in the rear cover, to the actuator motor'")
# L6: on the front and top faces of the top tie, not through it; second top limit switch (channel B) on this loom
rep("(0.573, -0.185, 1.385), (0.529, -0.17, 1.395), (0.529, 0.15, 1.395), (0.50, 0.15, 1.427)], [(0.529, 0.0, 1.395), (0.50, 0.0, 1.428), (0.46, 0.0, 1.437)],",
    "(0.573, -0.185, 1.385), (0.529, -0.17, 1.395), (0.529, 0.15, 1.395), (0.529, 0.15, 1.428), (0.50, 0.15, 1.428)], [(0.529, 0.0, 1.395), (0.529, 0.0, 1.428), (0.46, 0.0, 1.437)],\n       [(0.573, -0.185, 1.325), (0.573, -0.245, 1.325), (0.452, -0.245, 1.325), (0.452, -0.245, 1.338)],")
rep("[(0.529, -0.15, 1.395), (0.50, -0.15, 1.427)], ", "[(0.529, -0.15, 1.395), (0.529, -0.15, 1.428), (0.50, -0.15, 1.428)], ")
rep("'pod up the front of the right upright to rear camera, beacon, work lamp, marker, rear radar, microphone'", "'pod, through a grommet in the rear cover, up the front of the right upright to rear camera, beacon, work lamp, marker, rear radar, microphone, and the channel B lift top limit switch'")
rep("'USB cable, 4 lamp pairs, radar cable'", "'USB cable, 4 lamp pairs, radar cable, limit-switch pair'")
# L7: limit switches on the left side (top channel A, bottom)
rep("Mv = R @ np.array([0.060, 0.07, 0.10]) + p; A = (0.475, 0.172, 1.10)", "Mv = R @ np.array([0.090, 0.07, 0.085]) + p; A = (0.505, 0.171, 1.10)")
rep("[(0.573, 0.185, 1.10), (0.573, 0.185, 1.313), (0.573, 0.231, 1.313), (0.482, 0.231, 1.313)],",
    "[(0.573, 0.185, 1.10), (0.573, 0.185, 1.325), (0.573, 0.245, 1.325), (0.452, 0.245, 1.325), (0.452, 0.245, 1.338)], [(0.573, 0.185, 0.70), (0.573, 0.245, 0.70), (0.452, 0.245, 0.70)],")
rep("lift_pts(st, [(0.060, 0.07, 0.10), (0.047, 0.07, 0.10), (0.047, 0.07, -0.08), (-0.006, 0.07, -0.08), (-0.006, 0.18, -0.08), (-0.006, 0.18, -0.022)]), lift_pts(st, [(-0.006, 0.07, -0.08), (-0.006, -0.18, -0.08), (-0.006, -0.18, -0.022)]),",
    "lift_pts(st, [(0.090, 0.07, 0.085), (0.085, 0.07, 0.06), (0.085, 0.07, -0.125), (-0.006, 0.07, -0.125), (-0.006, 0.18, -0.125), (-0.006, 0.18, -0.022)]), lift_pts(st, [(-0.006, 0.07, -0.125), (-0.038, 0.05, -0.125), (-0.038, -0.05, -0.125), (-0.006, -0.07, -0.125), (-0.006, -0.18, -0.125), (-0.006, -0.18, -0.022)]),")
rep("lift_pts(st, [(0.047, 0.07, 0.10), (0.047, 0.115, 0.025), (0.002, 0.115, 0.025)]), lift_pts(st, [(-0.006, 0.07, -0.08), (-0.06, 0.06, -0.04), (-0.122, 0.06, -0.04), (-0.122, 0.02, -0.018)]),",
    "lift_pts(st, [(0.085, 0.07, 0.06), (0.047, 0.115, 0.05), (0.047, 0.115, 0.025), (0.002, 0.115, 0.025)]), lift_pts(st, [(-0.006, 0.07, -0.125), (-0.06, 0.06, -0.04), (-0.122, 0.06, -0.04), (-0.122, 0.02, -0.018)]),")
rep("lift_pts(st, [(-0.006, 0.13, -0.08), (-0.006, 0.13, pz + 0.05),", "lift_pts(st, [(-0.006, 0.13, -0.125), (-0.006, 0.13, pz + 0.05),")
rep("then to the 2 comb distance sensors, comb, nib and pad switches. Also the lift top limit switch', '3 sensor cables, 4 switch pairs'", "then to the 2 comb distance sensors, comb, nib and pad switches. Also the channel A lift top limit switch and the down limit switch', '3 sensor cables, 5 switch pairs'")
rep("LEX = dict(L5=['act'], L6=['mast'] * 5, L7=['mast', 'mast', 'mast'] + ['carriage'] * 5, L8=['post'] * 5, L11=['pod'])", "LEX = dict(L5=['act'], L6=['mast'] * 6, L7=['mast', 'mast', 'mast', 'mast'] + ['carriage'] * 5, L8=['post'] * 5, L11=['pod'])")
# L8, L9 through grommets in the front cover; L9 over the top of the nose cross-member, along a bumper arm and down its leg; charge pair on its own loom L12
rep("[[(0.72, 0.10, 0.24), (0.905, 0.10, 0.24), (0.905, 0.10, 0.425), (0.955, 0.06, 0.425), (1.0, 0.028, 0.45), (1.0, 0.028, 1.05)], [(1.0, 0.028, 0.815), (1.03, 0.02, 0.815)],",
    "[[(0.72, 0.10, 0.24), (0.905, 0.10, 0.24), (0.905, 0.10, 0.428), (0.955, 0.06, 0.428), (1.0, 0.028, 0.45), (1.0, 0.028, 1.05)], [(1.0, 0.028, 0.815), (1.03, 0.02, 0.815)],")
old9 = s[s.index("     ('L9', 'Nose loom'"):s.index("     ('L10', 'Operator-controls loom'")]
new9 = """     ('L9', 'Nose loom', 'pod, up through a grommet in the front cover behind the castor beam, over the top of the nose cross-member to the headlights; along the top of the right bumper arm, down the outside of its leg and along the top of the carrier beam to the two bumper switches', '2 stop-loop pairs (one per channel), 2 lamp pairs', (0.10, 0.62, 0.28), 0.007,
      [[(0.72, -0.10, 0.24), (0.905, -0.10, 0.24), (0.905, -0.10, 0.428), (0.955, -0.10, 0.428)], [(0.955, -0.30, 0.428), (0.955, 0.30, 0.428)], [(0.955, 0.30, 0.428), (0.985, 0.30, 0.418)], [(0.955, -0.30, 0.428), (0.985, -0.30, 0.418)],
       [(0.955, -0.09, 0.428), (0.99, -0.09, 0.424), (1.07, -0.09, 0.412), (1.07, -0.117, 0.412), (1.07, -0.117, 0.212), (1.098, -0.117, 0.212), (1.098, -0.19, 0.212), (1.122, -0.19, 0.205)],
       [(1.098, -0.117, 0.212), (1.098, 0.19, 0.212), (1.122, 0.19, 0.205)]]),
"""
s = s.replace(old9, new9)
L12 = '''     ('L12', 'Charge loom', 'the two charge contacts, through the bumper bar, with a flexible tail, under the carrier beam, up beside the left leg and arm, over the nose cross-member and down through its own grommet to the 10 A charge fuse in the power box. Kept apart from the stop-loop cables of L9, which run on top of the carrier beam', 'charge pair 2.5 mm2', (0.85, 0.45, 0.10), 0.006,
      [[(1.158, -0.12, 0.150), (1.125, -0.12, 0.158), (1.10, -0.12, 0.158), (1.10, 0.12, 0.158), (1.125, 0.12, 0.158), (1.158, 0.12, 0.150)],
       [(1.10, 0.09, 0.158), (1.043, 0.09, 0.158), (1.043, 0.117, 0.158), (1.043, 0.117, 0.412), (0.99, 0.117, 0.424), (0.955, 0.14, 0.44), (0.905, 0.14, 0.44), (0.905, 0.14, 0.24), (0.72, 0.19, 0.24), (0.69, 0.19, 0.24)]]),
'''
rep("      [[(0.70, 0.122, 0.215), (0.70, 0.17, 0.215)]]),\n", "      [[(0.70, 0.122, 0.215), (0.70, 0.17, 0.215)]]),\n" + L12)
rep("'L11', 'Safety and control loom', 'pod to power box: the two contactor coils from the safety relay, the contactor feedback contacts, switched-feed voltage sense, lift up and down commands', '2 coil pairs, feedback pair, sense pair, 2 command pairs'",
    "'L11', 'Safety and control loom', 'pod to power box: the two contactor coils from the safety controller, the mirror contacts of both contactors, pre-charge relay, switched-feed voltage sense, lift up and down commands and the lift-driver fault line', '2 coil pairs, 2 feedback pairs, pre-charge pair, sense pair, 3 signal pairs'")
rep("ref='HX-G6, PWR-G8, H1'", "ref='PC-G7' if e['loom'] == 'L11' else 'PWR-G8, H1'")
open('build_model.py', 'w').write(s); print('wrote build_model.py', len(s))
