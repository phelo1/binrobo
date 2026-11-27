#!/usr/bin/env python3
"""Writes build_model.py (revision 5) from build_model_r4.py: inserts the revision 5 geometry section and edits the item list and loom routes.
Revision 5 (21 Nov 2026) = the answers to the review of revision 4, with Brian's directions: people avoidance and navigation on camera and
lidar together, keep to the left edge of the lane, and a lower price. Geometry: a soft full-width nose with switch strips in place of the
certified 300 mm bumper, a 60x60 nose cross-member, slip-resistant corner joints (M10), top lift stops 5 mm higher, ground-looking ToF
sensors beside the bin wheels in place of the light beams."""
s = open('build_model_r4.py').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)

R5 = r'''
# ------------------------------------------------------------------ 2d. revision 5 (21 Nov 2026): the answers to the review of revision 4
def _bbx(r_): return r_[3].BoundingBox()
# (a) nose cross-member 60x60x4, flush with the rails top and bottom (was 50x50x4: safety factor 1.55). Everything on its top face rises 10 mm,
#     everything on its front or rear face moves 5 mm.
replace('FR Nose cross-member', box(925, 985, -395, 395, 360, 420).faces('<Y or >Y').shell(-4), 'FR Nose cross-member 60x60x4 RHS S355, flush with the rails')
_moved = []
for r_ in PARTS:
    b_ = _bbx(r_)
    if b_.xmin >= 940 and b_.zmin >= 409 and r_[0][:2] not in ('FR', 'RK', 'LM', 'SF', 'DK') and not r_[0].startswith('LT Headlight'):
        r_[3] = r_[3].translate(cq.Vector(0, 0, 10)); r_[5] = 'changed'; _moved.append(r_[0][:28])
print('  raised 10 mm with the nose member:', len(_moved), sorted(set(_moved)))
for r_ in find('LT Headlight'): r_[3] = r_[3].translate(cq.Vector(5, 0, 0)); r_[5] = 'changed'
replace('RK Pivot hanger plate rear', box(915, 925, -60, 60, 170, 420), 'RK Pivot hanger plate rear 10 mm S355, bolted through the nose cross-member')
replace('RK Pivot hanger plate front', box(985, 995, -60, 60, 170, 420), 'RK Pivot hanger plate front 10 mm S355, bolted through the nose cross-member')
replace('RK Pivot pin', cq.Workplane('YZ').circle(10).extrude(96).translate((907, 0, 200)), 'RK Pivot pin D20, bronze bushes in the beam housing, held in both hanger plates')
remove('LM Mast strut foot cleats')
for s, n in ((1, 'L'), (-1, 'R')):
    add('LM Mast strut foot cleats %s on the nose cross-member, two angles 40x40x4 S355' % n, 'tug', 'steel',
        box(935, 975, *sy(s, 176, 180), 420, 485).union(box(935, 975, *sy(s, 140, 180), 420, 424)).union(box(935, 975, *sy(s, 220, 224), 420, 485)).union(box(935, 975, *sy(s, 220, 260), 420, 424)))
# (b) corner joints made slip-resistant: larger plates, 2 x M10 8.8 into the rail (60 mm apart) and 2 x M10 into the cross-member (45 mm apart),
#     bare wire-brushed contact faces, prevailing-torque nuts. The front joints need no packer now.
remove('FR Corner plate')
for s, n in ((1, 'L'), (-1, 'R')):
    for x0, x1, w in ((435, 545, 'rear'), (885, 990, 'front')):
        top = box(x0, x1, *sy(s, 320, 455), 420, 426)
        if w == 'rear': top = top.union(box(465, 515, *sy(s, 320, 393), 410, 420))
        add('FR Corner plate %s %s, top, 6 mm S355, 4 x M10%s' % (n, w, ' (packer on the cross-member)' if w == 'rear' else ''), 'tug', 'steel', top)
        add('FR Corner plate %s %s, bottom, 6 mm S355, 4 x M10' % (n, w), 'tug', 'steel', box(x0, x1, *sy(s, 320, 455), 354, 360))
# (c) lift ends: the top blocks are 45 mm high (were 50), so the carriage beams reach them at +340 mm, 5 mm above the longest actuator stroke;
#     the top limit switch bodies sit 7 mm higher (first touched at +346). The tie stays where it was, held by a bolt in a steel thread insert.
remove('LM Lift top stop block'); remove('SW Lift top limit switch')
for s, n in ((1, 'L'), (-1, 'R')):
    add('LM Lift top stop block %s: 30x45 aluminium bar on the inner face of the upright, 2 x M10 through it side by side; steel thread insert for the tie bolt' % n, 'tug', 'red', box(445, 540, *sy(s, 144, 174), 1325, 1370).union(box(480, 540, *sy(s, 174, 180), 1325, 1370)))
    add('SW Lift top limit switch %s (channel %s), roller lever down to 1,327 mm' % (n, 'A' if s > 0 else 'B'), 'tug', 'switch', box(420, 450, *sy(s, 236, 258), 1345, 1375))
# (d) nose: the certified 300 mm safety bumper, its steel beam and 5 mm brackets go. In their place a soft nose over the full width:
#     200 mm of soft foam in a welded cover, switch strips on the front and on both side faces (so a pivot turn is covered too),
#     on an aluminium board and beam carried by two lighter folded brackets. People are kept clear by lidar and camera; this is the last line.
for pfx in ('SF Bumper carrier side bracket', 'SF Bumper carrier backing beam', 'SF Safety bumper'): remove(pfx)
for s, n in ((1, 'L'), (-1, 'R')):
    add('SF Nose carrier side bracket %s: 4 mm S355, laser-cut and folded' % n, 'tug', 'steel',
        box(990, 1090, *sy(s, 150, 154), 365, 405).union(box(1050, 1090, *sy(s, 150, 154), 150, 365)).union(box(1086, 1090, *sy(s, 154, 190), 150, 365)).union(box(990, 1086, *sy(s, 154, 190), 401, 405)).union(box(985, 989, *sy(s, 100, 154), 360, 420)))
    add('SF Nose switch strip, side %s (ribbon switch along the side face of the foam)' % n, 'tug', 'switch', box(1140, 1250, *sy(s, 468, 471), 170, 210))
add('SF Nose carrier beam 40x40x2 aluminium box, full width, bolted to the bracket legs', 'tug', 'red', box(1090, 1130, -460, 460, 160, 200).faces('<Y or >Y').shell(-2))
add('SF Nose carrier board 2 mm aluminium, full width', 'tug', 'red', box(1130, 1132, -468, 468, 115, 265))
add('SF Soft nose: foam 200 deep x 150 high x 936 wide in a welded cover, corners cut back', 'tug', 'rubber',
    cq.Workplane('XY').polyline([(1132, -468), (1252, -468), (1332, -388), (1332, 388), (1252, 468), (1132, 468)]).close().extrude(150).translate((0, 0, 115)))
add('SF Nose switch strip, front (ribbon switch across the front face of the foam)', 'tug', 'switch', box(1332, 1335, -380, 380, 170, 210))
# (e) under the bin: the two light beams go (the bin's own wheels broke them). One ToF distance sensor on each leg looks down and inwards at
#     the ground where the bin wheel will land; it reads the bare ground on arrival and again before and while the bin comes down.
remove('SF Under-bin light beam')
for s, n in ((1, 'L'), (-1, 'R')):
    add('SN Under-bin ToF sensor %s behind the leg guard, looking through a 16 mm hole at the ground under the bin wheel; on a 4 mm strip from the rail' % n, 'tug', 'switch',
        box(-215, -195, *sy(s, 368, 388), 140, 160).union(box(-207, -203, *sy(s, 372, 388), 160, 360)))
# (f) a second 2D lidar on the tip of the left leg, looking back and to the sides: with the rear camera it gives the same two-sensor watch to the
#     rear as the nose has to the front. Needed for reversing onto a bin and for coming down a steep pitch tail first when empty.
add('SN Rear lidar on the left leg tip, under a hoop guard (same type as the front lidar)', 'tug', 'switch',
    cq.Workplane('XY').circle(20).extrude(34).translate((-342, 425, 424)).union(box(-366, -318, 401, 449, 420, 424)).union(box(-366, -362, 401, 449, 424, 470)).union(box(-366, -318, 401, 449, 466, 470)))
# (g) the front lidar comes down from the post onto a shelf on the nose carrier: scan plane 0.30 m above the ground, where it sees legs, children
#     and dogs and has a clear view forward and to both sides (the driving software already assumed a lidar 0.30 m up)
for r_ in find('SN 2D lidar') + find('SN Lidar window'): r_[3] = r_[3].translate(cq.Vector(0, 0, -575)); r_[5] = 'changed'
replace('SN Lidar bracket', box(1010, 1130, -55, 55, 262, 265).union(box(1127, 1130, -55, 55, 215, 262)), 'SN Lidar bracket: folded 3 mm aluminium shelf riveted to the nose carrier board (replaces the arm on the post)')
'''
rep("# ------------------------------------------------------------------ poses of the simulation bodies relative to the robot frame", R5 + "# ------------------------------------------------------------------ poses of the simulation bodies relative to the robot frame")
rep('revision 4 (20 Nov 2026). Sections 1 and 2 are revision 2; 2b is revision 3; 2c holds the changes made after the review of revision 3.',
    'revision 5 (21 Nov 2026). Sections 1 and 2 are revision 2; 2b is revision 3; 2c is revision 4; 2d holds the changes made after the review of revision 4.')

# ---------------------------------------------------------------- item list
def item(n, new):
    global s
    import re
    m = re.search(r"\n \(%d, .*\n" % n, s); assert m, n
    s = s[:m.start()] + '\n' + new + s[m.end():]
item(3, " (3, 'Nose cross-member, 60 x 60 x 4, S355, flush with the rails', 1, ['FR Nose cross-member'], 'core', 'FAB-B2 (to change)', '60 x 60 in place of 50 x 50: carries the castor pivot plates, the mast strut feet and the nose carrier'),\n")
item(74, " (74, 'Corner plates 6 mm, bolted: top and bottom at each joint', 8, ['FR Corner plate'], 'core', 'new line needed', 'laser-cut S355; 4 x M10 8.8 per plate pair through crush tubes; contact faces bare and wire-brushed, prevailing-torque nuts, so the joint does not slip'),\n")
item(18, " (18, 'Rear bumper with safety switch', 2, ['SF Rear bumper'], 'rearbump', 'BMP-L8, G22', 'every reverse move is held to 0.1 m/s and watched by the rear camera'),\n")
item(20, " (20, 'Soft nose: 200 mm foam, full width, with switch strips', 1, ['SF Soft nose', 'SF Nose switch strip'], 'frontbump', 'BMP-L8 (to change)', 'home-made: soft foam in a welded cover, ribbon switches on the front and both side faces into the stop chain. Last line behind lidar and camera; not a certified part'),\n")
item(66, " (66, 'Nose carrier: two folded brackets, aluminium beam and board', 1, ['SF Nose carrier'], 'frontbump', 'new line needed', '4 mm folded brackets bolted to the nose cross-member between the castors'),\n")
item(72, " (72, 'Under-bin ToF sensor behind the leg guard', 2, ['SN Under-bin ToF'], 'guard', 'B2-GAP (2 more)', 'same sensor as the leg-tip gap sensors; looks at the ground where the bin wheel lands: no lowering if it reads 10 mm short of the bare ground'),\n")
item(67, " (67, 'Lift stop block, bolted (2 top, 2 bottom)', 4, ['LM Lift top stop', 'LM Lift bottom stop'], 'rail', 'new line needed', 'saw-cut 30 x 45 aluminium bar on the inner face of each upright, 2 x M10 through the upright; they stop the carriage beams at 340 mm and at -18 mm'),\n")
item(68, " (68, 'Lift limit switch (2 top, 2 bottom)', 4, ['SW Lift top limit', 'SW Lift down limit'], 'mast', 'new line needed', 'top pair trips at 327 mm (bodies first touched at 346), bottom pair at 0 mm; one of each pair per stop channel'),\n")
item(25, " (25, 'Mast top tie 50 x 50 x 2', 1, ['LM Mast top tie'], 'mast', 'FAB-B2', 'bolted down onto the two top stop blocks, into steel thread inserts'),\n")
item(53, " (53, 'Front 2D lidar on a shelf on the nose', 1, ['SN Lidar bracket', 'SN 2D lidar', 'SN Lidar window'], 'frontbump', 'G21', 'moved down from the post: scan plane 0.30 m up. People, children, dogs and obstacles ahead and to both sides; the left hedge face for keeping left'),\n")
item(54, " (54, 'Front camera', 1, ['SN Front camera'], 'post', 'new line needed', 'second sensor for people ahead and for the left edge of the lane; same type as the rear camera'),\n")
s = s.replace("\n (59, ", "\n (75, 'Rear lidar on the left leg tip', 1, ['SN Rear lidar'], 'rearbump', 'G21 (1 more)', 'people and obstacles behind and beside the tail: for every reverse move and for coming down a steep pitch tail first when empty'),\n (59, ", 1)
item(59, " (59, 'Rear camera with infra-red light', 1, ['SN Rear camera'], 'masttop', 'G23', 'bin pose at the pick-up; people behind before any reverse move and before lowering'),\n")
# looms: the nose loom runs along the rear face of the nose member, which is now 5 mm further back
n922 = s.count('(0.922, '); s = s.replace('(0.922, ', '(0.917, '); print('  loom points moved off the nose member:', n922)
for sg_ in ('', '-'):
    assert s.count('(0.985, %s0.30, 0.418)' % sg_) == 1; s = s.replace('(0.985, %s0.30, 0.418)' % sg_, '(0.992, %s0.30, 0.428), (0.992, %s0.30, 0.416)' % (sg_, sg_))
s = s.replace("down the inside of the right bumper side plate to the safety bumper', 'bumper cable (2 channels)", "down the inside of the right nose bracket to the three switch strips of the soft nose', 'switch-strip cable (2 channels)")
s = s.replace("and the two under-bin light beams", "and the two under-bin ToF sensors")
assert s.count("[(1.0, 0.028, 0.815), (1.03, 0.02, 0.815)]") == 1
s = s.replace("[(1.0, 0.028, 0.815), (1.03, 0.02, 0.815)]", "[(1.0, 0.028, 0.45), (1.0, 0.06, 0.45), (1.045, 0.06, 0.45), (1.045, 0.06, 0.30), (1.045, 0.045, 0.30)]")
s = s.replace("up the post to lidar, front camera, GNSS, LTE antenna, front radar, horn'", "up the post to the front camera, GNSS, LTE antenna, front radar and horn; a branch down to the front lidar on the nose'")
open('build_model.py', 'w').write(s); print('wrote build_model.py', len(s))
