#!/usr/bin/env python3
"""Writes build_model.py (revision 4) from build_model_r3.py: inserts the revision 4 geometry section, and edits the item list and the loom routes.
Revision 4 = the answers to the review of revision 3 (20 Nov 2026): 60x60 rails, no welded joints, mast struts, lift stops on the ties,
a lift actuator with its own end stops, a foam safety bumper with 300 mm of depth, charge contacts under the nose, light beams under the bin."""
s = open('build_model_r3.py').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)

R4 = r'''
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
'''
rep("# ------------------------------------------------------------------ poses of the simulation bodies relative to the robot frame", R4 + "# ------------------------------------------------------------------ poses of the simulation bodies relative to the robot frame")
rep('"""Improved-version model for the drawing set, revision 3 (14 Nov 2026). Sections 1 and 2 are revision 2; section 2b holds the changes made after the review of revision 2.',
    '"""Improved-version model for the drawing set, revision 4 (20 Nov 2026). Sections 1 and 2 are revision 2; 2b is revision 3; 2c holds the changes made after the review of revision 3.')

# ---------------------------------------------------------------- item list
def item(n, new):
    global s
    import re
    m = re.search(r"\n \(%d, .*\n" % n, s); assert m, n
    s = s[:m.start()] + '\n' + new + s[m.end():]
def drop(n): item(n, '')
item(1, " (1, 'Side rail, 60 x 60 x 4 box section, S355', 2, ['FR Side rail'], 'core', 'S12-RAIL (to change)', '60 x 60 in place of 50 x 50: safety factor 2.1 on the largest wheel load of the load cases; S355'),\n")
item(2, " (2, 'Mast-base cross-member, 50 x 50 x 5, S355', 1, ['FR Mast-base'], 'core', 'FAB-B2 (to change)', 'carries the mast feet and the actuator base; butts against the rails'),\n")
item(3, " (3, 'Nose cross-member, 50 x 50 x 4, S355, at rail height', 1, ['FR Nose cross-member'], 'core', 'FAB-B2 (to change)', '4 mm wall, S355: carries the castor pivot plates, the mast strut feet and the bumper carrier. To become 60 x 60 x 4 (reply note, 3.6)'),\n")
item(74, " (74, 'Corner plates 6 mm, bolted: top and bottom at each joint', 8, ['FR Corner plate'], 'core', 'new line needed', 'laser-cut S355; 4 x M8 8.8 per joint through crush tubes; 10 mm packer on the cross-member. No weld'),\n")
item(4, " (4, 'Drive / motor plate, 8 mm, with top flange', 2, ['FR Drive/motor plate'], 'drive', 'FAB-B2 (to change)', '8 mm in place of 6 mm for the sideways tyre load; flange bolted up through the rail with 4 x M8'),\n")
item(11, " (11, 'Pivot pin D20 with two 10 mm clamp plates', 1, ['RK Pivot'], 'pivot', 'S12-PIN; plates: new line', 'plates S355, clamped on the nose cross-member by 4 x M10 through it; bronze bushes in the beam housing'),\n")
item(13, " (13, 'Castor 200 mm: fork, wheel, hub', 2, ['CA Castor'], 'castor', 'DRV-C7 (to change)', 'round-profile tyre; swivel torque to be measured on the bench before ordering two (reply note, section 4)'),\n")
item(20, " (20, 'Safety bumper, foam, 300 mm deep', 1, ['SF Safety bumper'], 'frontbump', 'BMP-L8 (to change)', 'pressure-sensitive bumper to EN ISO 13856-3 with its control unit; 150 mm of travel after it switches (maker to confirm)'),\n")
item(21, " (21, 'Charge contact pad under the nose', 2, ['DK Charge contact'], 'contacts', 'D2 (to change)', 'the dock is a low floor shoe: docking no longer presses the bumper'),\n")
item(23, " (23, 'Mast upright 80 x 40 x 4 with foot cleats', 2, ['LM Mast upright', 'LM Mast foot cleat'], 'mast', 'S12-MAST', 'stands on the cross-member; two angle cleats 60 x 60 x 6, bolted. No weld'),\n")
item(25, " (25, 'Mast top tie 50 x 50 x 2', 1, ['LM Mast top tie'], 'mast', 'FAB-B2', 'bolted down onto the two top stop blocks'),\n")
item(27, " (27, 'Lift actuator 24 V, 6.8 kN, 350 mm, outdoor unit', 1, ['LA Lift actuator'], 'act', 'B-0 (to change)', 'needs: holding force at least 6 kN, IP66, own end-stop switches, 600 mm between pins closed. Drawn: LINAK LA36'),\n")
item(28, " (28, 'Carriage: aluminium plate, two steel beams, bracket', 1, ['LC Carriage plate', 'LC Carriage cross-beam', 'LC Actuator bracket'], 'carriage', 'FAB-B2 (to change)', 'cross-beams 50 x 50 x 4 S355 carry the load to the rail blocks; their ends land on the stop blocks; bolted'),\n")
item(38, " (38, 'Pad rods, cup plate and two long springs', 1, ['PD Pad slide rods', 'PD Pad backing plate', 'PD Pad spring cup plate', 'PD Pad springs'], 'padrods', 'B-3 (to change)', 'springs 145 mm free, guided in bores through the guide block; 45 mm stroke: 300 N at first touch, 1.65 kN fully in'),\n")
item(66, " (66, 'Bumper carrier: two folded side brackets, backing beam', 1, ['SF Bumper carrier'], 'frontbump', 'new line needed', 'laser-cut and folded 5 mm brackets, bolted to the nose cross-member between the castors; holds 1 kN sideways'),\n")
item(72, " (72, 'Under-bin light beam, sender and receiver', 2, ['SF Under-bin light beam'], 'guard', 'new line needed', 'safety single-beam sensors 40 mm above the ground: no lowering while a beam is broken'),\n")
item(67, " (67, 'Lift stop block, bolted (2 top, 2 bottom)', 4, ['LM Lift top stop', 'LM Lift bottom stop'], 'rail', 'new line needed', 'saw-cut 30 mm aluminium bar on the inner face of each upright, 2 x M10 through the upright in crush tubes; they stop the carriage beams at 335 mm and at -18 mm'),\n")
item(68, " (68, 'Lift limit switch (2 top, 2 bottom)', 4, ['SW Lift top limit', 'SW Lift down limit'], 'mast', 'new line needed', 'top pair trips at 327 mm, bottom pair at 0 mm; one of each pair per stop channel'),\n")
item(70, " (70, 'Mast strut 30 x 30 x 2 with lug plates and foot cleats', 2, ['LM Mast strut'], 'mast', 'new line needed', 'takes the tipping moment of the hanging bin to the nose cross-member; one M10 pin at each end; foot cleats in S355'),\n")
item(71, " (71, 'Actuator base bracket: angle 100 x 100 x 12', 1, ['LA Actuator base bracket'], 'act', 'new line needed', '2 x M12 through the mast-base cross-member; lug angles on a shim pack set the height of the base pin'),\n")
rep("EX = dict(core=(0, 0, 0),", "EX = dict(core=(0, 0, 0),")   # explode groups unchanged

# ---------------------------------------------------------------- looms
rep("drvL = [(0.585, 0.125, 0.25), (0.585, 0.355, 0.25), (0.555, 0.355, 0.25), (0.555, 0.355, 0.425), (0.53, 0.398, 0.425), (0.44, 0.398, 0.425), (0.42, 0.398, 0.398), (-0.05, 0.398, 0.398), (-0.05, 0.398, 0.44), (-0.05, 0.42, 0.452)]",
    "drvL = [(0.585, 0.125, 0.25), (0.585, 0.32, 0.25), (0.555, 0.32, 0.25), (0.555, 0.32, 0.425), (0.44, 0.32, 0.425), (0.42, 0.32, 0.385), (0.42, 0.388, 0.385), (-0.05, 0.388, 0.385), (-0.05, 0.374, 0.40), (-0.05, 0.374, 0.45)]")
rep("encL = [(0.065, 0.398, 0.398), (0.065, 0.398, 0.425), (0.065, 0.4615, 0.425), (0.065, 0.4615, 0.186)]", "encL = [(0.065, 0.388, 0.385), (0.065, 0.388, 0.432), (0.065, 0.4615, 0.432), (0.065, 0.4615, 0.186)]")
rep("rearL = [(0.572, 0.125, 0.232), (0.572, 0.342, 0.232), (0.555, 0.342, 0.232), (0.555, 0.342, 0.438), (0.53, 0.398, 0.438), (0.44, 0.398, 0.438), (0.42, 0.398, 0.384), (-0.33, 0.398, 0.384), (-0.378, 0.398, 0.40), (-0.378, 0.43, 0.40)]",
    "rearL = [(0.572, 0.125, 0.232), (0.572, 0.308, 0.232), (0.555, 0.308, 0.232), (0.555, 0.308, 0.438), (0.44, 0.308, 0.438), (0.42, 0.308, 0.372), (0.42, 0.388, 0.372), (-0.33, 0.388, 0.372), (-0.376, 0.388, 0.372), (-0.378, 0.43, 0.40)]")
rep("rearL2 = [(-0.33, 0.398, 0.384), (-0.33, 0.398, 0.36), (-0.362, 0.40, 0.215)]",
    "rearL2 = [(-0.33, 0.388, 0.372), (-0.33, 0.398, 0.36), (-0.362, 0.40, 0.215)]; beamA = [(-0.27, 0.388, 0.372), (-0.27, 0.382, 0.05)]; beamB = [(-0.195, 0.388, 0.372), (-0.195, 0.382, 0.05)]")
rep("[rearL, rearL2, mir(rearL), mir(rearL2)]),", "[rearL, rearL2, beamA, beamB, mir(rearL), mir(rearL2), mir(beamA), mir(beamB)]),")
rep("to rear bumper switches, leg-tip gap sensors, rear markers', 'stop-loop pair, sensor cable, lamp pair each side'", "to rear bumper switches, leg-tip gap sensors, rear markers and the two under-bin light beams', 'stop-loop pair, sensor cable, lamp pair, 2 light-beam cables each side'")
# L6 mast-top loom: up beside the inner face of the right upright (the strut now ends on the front face)
rep("[[(0.58, -0.06, 0.29), (0.58, -0.06, 0.325), (0.573, -0.185, 0.325), (0.573, -0.185, 1.385), (0.529, -0.17, 1.395), (0.529, 0.15, 1.395), (0.529, 0.15, 1.428), (0.50, 0.15, 1.428)], [(0.529, 0.0, 1.395), (0.529, 0.0, 1.428), (0.46, 0.0, 1.437)],\n       [(0.573, -0.185, 1.325), (0.573, -0.245, 1.325), (0.452, -0.245, 1.325), (0.452, -0.245, 1.338)],",
    "[[(0.58, -0.078, 0.29), (0.58, -0.078, 0.325), (0.552, -0.166, 0.325), (0.552, -0.166, 1.385), (0.529, -0.166, 1.395), (0.529, 0.15, 1.395), (0.529, 0.15, 1.428), (0.50, 0.15, 1.428)], [(0.529, 0.0, 1.395), (0.529, 0.0, 1.428), (0.46, 0.0, 1.437)],\n       [(0.552, -0.166, 1.30), (0.575, -0.166, 1.30), (0.575, -0.245, 1.30), (0.452, -0.245, 1.30), (0.452, -0.245, 1.338)], [(0.552, -0.166, 0.66), (0.575, -0.166, 0.66), (0.575, -0.245, 0.66), (0.452, -0.245, 0.66)],")
rep("rear camera, beacon, work lamp, marker, rear radar, microphone, and the channel B lift top limit switch', 'USB cable, 4 lamp pairs, radar cable, limit-switch pair'", "rear camera, beacon, work lamp, marker, rear radar, microphone, and the channel B lift limit switches (top and bottom)', 'USB cable, 4 lamp pairs, radar cable, 2 limit-switch pairs'")
rep("up the front of the right upright to", "up beside the inner face of the right upright to")
# L7 carriage loom
rep("[[(0.58, 0.06, 0.29), (0.58, 0.06, 0.325), (0.573, 0.185, 0.325), (0.573, 0.185, 1.10), (0.573, 0.172, 1.10), A], [(0.573, 0.185, 1.10), (0.573, 0.185, 1.325), (0.573, 0.245, 1.325), (0.452, 0.245, 1.325), (0.452, 0.245, 1.338)], [(0.573, 0.185, 0.70), (0.573, 0.245, 0.70), (0.452, 0.245, 0.70)],",
    "[[(0.58, 0.078, 0.29), (0.58, 0.078, 0.325), (0.552, 0.166, 0.325), (0.552, 0.166, 1.10), A], [(0.552, 0.166, 1.10), (0.552, 0.166, 1.30), (0.575, 0.166, 1.30), (0.575, 0.245, 1.30), (0.452, 0.245, 1.30), (0.452, 0.245, 1.338)], [(0.552, 0.166, 0.66), (0.575, 0.166, 0.66), (0.575, 0.245, 0.66), (0.452, 0.245, 0.66)],")
rep("pod up the front of the left upright to a cable chain", "pod up beside the inner face of the left upright to a cable chain")
rep("Also the channel A lift top limit switch and the down limit switch', '3 sensor cables, 5 switch pairs'", "Also the channel A lift limit switches (top and bottom)', '3 sensor cables, 5 switch pairs'")
rep("LEX = dict(L5=['act'], L6=['mast'] * 6,", "LEX = dict(L5=['act'], L6=['mast'] * 7,")
# L5 actuator loom
rep("[[(0.66, 0.17, 0.24), (0.66, 0.145, 0.27), (0.66, 0.145, 0.325), (0.64, 0.03, 0.36)]]),", "[[(0.66, 0.17, 0.24), (0.66, 0.145, 0.27), (0.66, 0.145, 0.34), (0.66, 0.045, 0.385)]]),")
# L9 nose loom: along the rear face of the nose cross-member, over the top at the centre; bumper cable down the inside of the right side plate
rep("[[(0.72, -0.10, 0.24), (0.905, -0.10, 0.24), (0.905, -0.10, 0.428), (0.955, -0.10, 0.428)], [(0.955, -0.30, 0.428), (0.955, 0.30, 0.428)], [(0.955, 0.30, 0.428), (0.985, 0.30, 0.418)], [(0.955, -0.30, 0.428), (0.985, -0.30, 0.418)],\n       [(0.955, -0.09, 0.428), (0.99, -0.09, 0.424), (1.07, -0.09, 0.412), (1.07, -0.117, 0.412), (1.07, -0.117, 0.212), (1.098, -0.117, 0.212), (1.098, -0.19, 0.212), (1.122, -0.19, 0.205)],\n       [(1.098, -0.117, 0.212), (1.098, 0.19, 0.212), (1.122, 0.19, 0.205)]]),",
    "[[(0.72, -0.10, 0.24), (0.905, -0.10, 0.24), (0.905, -0.10, 0.395), (0.922, -0.10, 0.395)], [(0.922, -0.30, 0.395), (0.922, -0.075, 0.395), (0.922, -0.075, 0.425), (0.922, 0.075, 0.425), (0.922, 0.075, 0.395), (0.922, 0.30, 0.395)],\n       [(0.922, 0.30, 0.395), (0.922, 0.30, 0.428), (0.985, 0.30, 0.418)], [(0.922, -0.30, 0.395), (0.922, -0.30, 0.428), (0.985, -0.30, 0.418)],\n       [(0.922, -0.14, 0.395), (0.922, -0.14, 0.428), (0.99, -0.14, 0.424), (1.04, -0.14, 0.42), (1.04, -0.14, 0.215), (1.083, -0.14, 0.215), (1.083, -0.10, 0.215)]]),")
rep("'pod, up through a grommet in the front cover behind the castor beam, over the top of the nose cross-member to the headlights; along the top of the right bumper arm, down the outside of its leg and along the top of the carrier beam to the two bumper switches', '2 stop-loop pairs (one per channel), 2 lamp pairs'",
    "'pod, up through a grommet in the front cover behind the castor beam, along the rear face of the nose cross-member to the headlights; over the member and down the inside of the right bumper side plate to the safety bumper', 'bumper cable (2 channels), 2 lamp pairs'")
# L12 charge loom: from the two pads under the nose, up the inside of the left side plate
rep("[[(1.158, -0.12, 0.150), (1.125, -0.12, 0.158), (1.10, -0.12, 0.158), (1.10, 0.12, 0.158), (1.125, 0.12, 0.158), (1.158, 0.12, 0.150)],\n       [(1.10, 0.09, 0.158), (1.043, 0.09, 0.158), (1.043, 0.117, 0.158), (1.043, 0.117, 0.412), (0.99, 0.117, 0.424), (0.955, 0.14, 0.44), (0.905, 0.14, 0.44), (0.905, 0.14, 0.24), (0.72, 0.19, 0.24), (0.69, 0.19, 0.24)]]),",
    "[[(1.105, -0.06, 0.113), (1.105, 0.06, 0.113), (1.105, 0.14, 0.113), (1.083, 0.14, 0.113), (1.083, 0.14, 0.215), (1.04, 0.14, 0.215), (1.04, 0.14, 0.42), (0.99, 0.14, 0.424), (0.955, 0.14, 0.44), (0.905, 0.14, 0.44), (0.905, 0.14, 0.24), (0.72, 0.19, 0.24), (0.69, 0.19, 0.24)]]),")
rep("'the two charge contacts, through the bumper bar, with a flexible tail, under the carrier beam, up beside the left leg and arm, over the nose cross-member and down through its own grommet to the 10 A charge fuse in the power box. Kept apart from the stop-loop cables of L9, which run on top of the carrier beam'",
    "'the two charge pads under the nose, up the inside of the left bumper side plate, over the nose cross-member and down through its own grommet to the 10 A charge fuse in the power box. Kept apart from the bumper cable of L9, which runs on the right side plate'")
rep("zl = min(A[2], float(Mv[2])) - 0.22", "zl = min(A[2], float(Mv[2])) - 0.17")
open('build_model.py', 'w').write(s); print('wrote build_model.py', len(s))
