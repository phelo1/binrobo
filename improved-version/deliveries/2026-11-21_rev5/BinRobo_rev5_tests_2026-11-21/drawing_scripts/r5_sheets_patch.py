#!/usr/bin/env python3
"""Writes draw_sheets.py (revision 5) from draw_sheets_r4.py: 18 sheets, revision 5 texts, a new sheet 18 (people avoidance and keeping left)."""
import re
s = open('draw_sheets_r4.py').read()
def rp(a, b, n=None):
    global s
    c = s.count(a); assert c >= 1 and (n is None or c == n), (c, a[:70]); s = s.replace(a, b)
rp("NSHEETS = 17", "NSHEETS = 18"); rp("DATE = '2026-11-20'", "DATE = '2026-11-21'"); rp("/home/claude/s0/r4/facts.json", "/home/claude/s0/r5/facts.json")
rp("'BinRobo improved version, rev 4'", "'BinRobo improved version, rev 5'"); rp("revision 4 reply note", "revision 5 reply note")
rp("a foam safety bumper 300 mm deep", "a soft full-width nose with switch strips, lidar and camera for people")
rp("20: 'Safety bumper, foam'", "20: 'Soft nose with switch strips'"); rp("72: 'Under-bin light beam'", "72: 'Under-bin ToF sensor', 75: 'Rear lidar'")
rp("The foam safety bumper (item 20)", "The soft nose (item 20)")
rp("The two light beams (item 72) cross under the bin 40 mm above the ground.", "A ToF sensor behind each leg guard (item 72) looks at the ground where the bin wheel lands. The front lidar sits on a shelf on the nose, 0.30 m above the ground.")
rp("to the safety bumper;", "to the switch strips of the soft nose;"); rp("L4 also feeds the two light beams under the bin", "L4 also feeds the two under-bin ToF sensors and the rear lidar on the left leg tip")
rp("['Safety bumper, front (20)', 'its control unit: two outputs']", "['Soft nose switch strips (20)', 'front, left, right: two channels']")
rp("['Speed and standstill: certified module', 'two wheel sensors (8)']", "['Speed and slide watchdog (own build)', 'wheel sensors (8), ground speed']")
rp("light beams)'", "under-bin sensors)'")
rp("the robot stops inside the bumper travel', 'PL d')", "the robot stops inside the foam', 'not rated')"); rp("'Front safety bumper pressed'", "'Soft nose touched, front or side'")
rp("('A light beam under the bin is broken', 'lowering blocked, or stopped if under way', 'PL c')", "('Under-bin sensor reads short of the bare ground', 'lowering blocked', 'not rated')")
rp("bumper with its control unit, light beams and lift driver", "switch strips, under-bin sensors and lift driver")
rp("Changed from revision 3: a foam safety bumper with its own control unit replaces the two bumper switches; two light beams guard the space under the bin;",
   "Changed in revision 5: lidar and camera keep people clear (sheet 18); the soft nose with switch strips is the last line; ToF sensors look under the bin; nothing here is a certified part except the used safety relays;")
rp("speed and standstill come from a certified module.", "speed and slide are watched by a second, home-built controller with its own ground-speed source.")
rp("'Sliding bumper bar, pins and switches: now the foam bumper'", "'Sliding bumper bar, pins and switches: now the soft nose', 'Certified foam bumper, light beams, certified speed module (revision 4): replaced, see the reply note'")
rp("1,831 mm long, 930 mm wide, 1,510 mm high (1,876 mm long with a 240 L bin on board)", "1,736 mm long, 942 mm wide, 1,510 mm high (1,781 mm long with a 240 L bin on board)")
rp("'overall 1,831'", "'overall 1,736'"); rp("(1.430, -0.35, 0), (1.430, 0.35, 0)", "(1.335, -0.468, 0), (1.335, 0.468, 0)"); rp("'safety bumper 700'", "'soft nose 936'"); rp("(1.430, ", "(1.335, ")
rp("the overall length is 1,876", "the overall length is 1,781"); rp("full 335 mm of travel", "full 340 mm of travel")
rp("'4 x M8 x 90: 2 through the rail, 2 through the cross-member', '8.8', 'crush tubes;", "'4 x M10 x 90: 2 through the rail (60 apart), 2 through the cross-member (45 apart)', '8.8', 'bare brushed faces, lock nuts, crush tubes;")
i = s.index("'4 x M10 x 90: 2 through the rail (60 apart)"); j = s.index("'25 N m')", i); s = s[:j] + "'49 N m')" + s[j + len("'25 N m')"):]
rp("(335, 'stop blocks', RED, 4)", "(340, 'stop blocks', RED, 4)")
rp("'The foam bumper is the last line of protection for a person in front of the robot. After it switches it must still have at least 150 mm to travel, and the robot must stop within that. The table gives the speeds at which the simulated stop, from the bumper touch to standstill, stays under 125 mm on a wet surface (grip 0.30), with 0.15 s between the touch and the brakes.'",
   "'Lidar and camera keep people clear of the robot (sheet 18). The soft nose is the last line: its switch strip acts at the first touch and the foam then has about 150 mm to give (to be measured). The table gives the speeds at which the simulated stop, from the touch to standstill, stays under 130 mm on a wet surface (grip 0.30), with 0.15 s between the touch and the brakes. The rule looks 3 m ahead, so the robot is already slow at the brow of a pitch.'")
a = s.index("'Safety bumper: to EN ISO 13856-3"); b = s.index("rated for outdoor use.',", a) + len("rated for outdoor use.',")
s = s[:a] + "'Soft nose: soft open-cell foam 200 mm deep in a welded cover, full width; ribbon switches on the front and both side faces, two channels; it must give 150 mm under 250 N on a 70 mm post. Home-made, not certified: measure the stop on the built robot.'," + s[b:]
a = s.index("'Light beams: safety single-beam sensors"); b = s.index("rated for outdoor use.',", a) + len("rated for outdoor use.',")
s = s[:a] + "'Under-bin sensors: two ToF distance sensors (the type used at the leg tips), potted, each looking through a hole in the leg guard at the ground under a bin wheel. No lowering if a reading is 10 mm short of the bare ground it saw on arrival.'," + s[b:]
rp("holding force at least 6 kN, IP66, own end-stop switches, 600 mm between the pins closed, 350 mm stroke.", "holding force at least 6 kN, IP66, own end-stop switches, 600 mm between the pins closed, 350 mm stroke. Bought used or surplus and bench-tested (push, hold, end stops) before fitting.")
rp("motion when a standstill is commanded', 'both contactors open, brakes apply', 'PL d')", "motion or a slide when a standstill is commanded', 'both contactors open, brakes apply', 'not rated')")
rp("(reversing is at 0.2 m/s or less)", "(every reverse move is at 0.1 m/s)")
rp("'(in the pod; replaces the', 'safety relay SR-L8)'", "'(in the pod; bought used;', 'replaces relay SR-L8)'")

rp("Revision 4, after the review of 15 Nov", "Revision 5, after the review of 21 Nov")
S18 = r'''
def sheet_sensing(n=18):
    img, dr = new_sheet(n, 'People avoidance and keeping left', 'Lidar and camera together: proposal for revision 5. Two different sensors watch every direction the robot moves in, and either one can stop it. None of them is a certified safety device.')
    SC = 150.0; cx, cy = 900, 1420
    def P(x, y): return (cx - y * SC, cy - x * SC)          # robot x (forward) is up the page, robot y (left) is left on the page
    def poly(pts, **kw): dr.polygon([P(*p) for p in pts], **kw)
    def sector(x, y, r, a0, a1, **kw): px, py = P(x, y); dr.pieslice([px - r * SC, py - r * SC, px + r * SC, py + r * SC], a0, a1, **kw)
    gap = FACTS['kl_gap']; yl = 0.471 + gap; yr = yl - 4.1; x0, x1 = -3.3, 7.4
    poly([(x0, yl), (x1, yl), (x1, yr), (x0, yr)], fill=(236, 236, 232)); poly([(x0, yl), (x1, yl), (x1, yl + 0.45), (x0, yl + 0.45)], fill=(150, 185, 140)); poly([(x0, yr), (x1, yr), (x1, yr - 0.45), (x0, yr - 0.45)], fill=(150, 185, 140))
    sector(1.08, 0, 4.0, 135, 405, fill=(255, 244, 200), outline=(200, 170, 60)); sector(-0.342, 0.425, 2.0, -15, 195, fill=(255, 244, 200), outline=(200, 170, 60))
    sector(1.08, 0, 1.5, 135, 405, fill=(250, 208, 200), outline=(200, 90, 70)); sector(-0.342, 0.425, 1.0, -15, 195, fill=(250, 208, 200), outline=(200, 90, 70))
    poly([(x0, yl), (x1, yl), (x1, yl + 0.45), (x0, yl + 0.45)], fill=(150, 185, 140)); poly([(x0, yr), (x1, yr), (x1, yr - 0.45), (x0, yr - 0.45)], fill=(150, 185, 140))
    for apex, ang0, rng_, col in (((1.04, 0.0), 0.0, 6.0, (40, 90, 200)), ((0.43, 0.0), 180.0, 3.2, (40, 90, 200))):     # camera cones: outline only
        pts = [apex] + [(apex[0] + rng_ * math.cos(math.radians(ang0 + a)), apex[1] + rng_ * math.sin(math.radians(ang0 + a))) for a in range(-55, 56, 5)]
        pp = [P(*p) for p in pts]; dr.line(pp + [pp[0]], fill=col, width=4)
    pfp = [P(*p) for p in ((0.93, -0.551), (1.932, -0.551), (1.932, 0.551), (0.93, 0.551))]; dr.line(pfp + [pfp[0]], fill=(170, 20, 20), width=5)     # protective field: anything at all
    poly([(-0.401, -0.468), (1.132, -0.468), (1.252, -0.468), (1.332, -0.388), (1.332, 0.388), (1.252, 0.468), (-0.401, 0.468)], fill=(120, 126, 134), outline=INK)
    poly([(1.132, -0.468), (1.252, -0.468), (1.332, -0.388), (1.332, 0.388), (1.252, 0.468), (1.132, 0.468)], fill=(225, 120, 60), outline=INK)
    for (x, y), r in (((1.08, 0.0), 0.05), ((-0.342, 0.425), 0.03)):
        px, py = P(x, y); dr.ellipse([px - r * SC * 1.6, py - r * SC * 1.6, px + r * SC * 1.6, py + r * SC * 1.6], fill=(30, 30, 30))
    f = F(21); fb = F(21, True)
    def lab(x, y, t, dx=0, dy=0, bold=False): px, py = P(x, y); dr.text((px + dx, py + dy), t, font=fb if bold else f, fill=INK)
    lab(6.6, 1.6, 'front camera: people, to 6 m', bold=True); lab(5.3, -0.3, 'slow zone, 4 m: 0.25 m/s', dx=10); lab(2.75, -0.3, 'stop zone, 1.5 m', dx=10); lab(0.78, -0.55, 'soft nose, switch strips', dx=14, dy=0); lab(1.95, -0.55, 'protective field 0.6 m: stops for anything, hedge included', dx=14, dy=-22)
    lab(1.08, 0.0, 'front lidar', dx=18, dy=-12); lab(-0.342, 0.425, 'rear lidar', dx=-120, dy=14); lab(-1.2, -0.1, 'rear zones: 1 m stop, 2 m slow', dx=0); lab(-2.95, 0.55, 'rear camera', bold=True)
    lab(0.5, yl + 0.42, 'left edge of the lane', dx=-250, dy=-10, bold=True); lab(3.0, yr, 'the rest of the lane stays free: about %.1f m' % (4.1 - gap - 0.942), dx=-430, dy=-14)
    pa, pb = P(0.3, 0.471), P(0.3, yl); dr.line([pa, pb], fill=(200, 30, 30), width=5); dr.text((pb[0] - 6, pb[1] + 12), '%.2f m' % gap, font=fb, fill=(200, 30, 30))
    dr.text((70, 2040), 'Plan view, robot driving up the page, drawn to scale (lane 3.6 m between verges). Yellow: slow zone. Red: stop zone. Dark red box: protective field. Blue outline: what each camera sees.', font=F(19), fill=GREY)
    x = 1930; y = 180; w = 1300
    def head(t):
        nonlocal y
        dr.text((x, y), t, font=F(26, True), fill=INK); y += 42
    def para(t):
        nonlocal y
        for ln in wrap(dr, t, f, w): dr.text((x, y), ln, font=f, fill=INK); y += 28
        y += 8
    head('The rules')
    for t in FACTS['people_rules']: para(t)
    y += 6; head('How close can a person appear and still not be touched?')
    para('Simulated: a person appears in the path at a random moment; the robot brakes after two detections in a row. Distance needed in 99.9 % of cases, in metres:')
    cols = (560, 180, 180, 190, 190); heads = ('Case', 'both', 'lidar only', 'camera, day', 'camera, night'); xx = x
    for h_, w_ in zip(heads, cols): dr.text((xx, y), h_, font=fb, fill=INK); xx += w_
    dr.line([(x, y + 28), (x + sum(cols), y + 28)], fill=INK, width=2); y += 36
    for row in FACTS['people_rows']:
        xx = x
        for c_, w_ in zip(row, cols): dr.text((xx, y), str(c_), font=f, fill=INK); xx += w_
        y += 30
    y += 14
    for t in FACTS['people_notes']: para(t)
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, 'right column ends at y', int(y), flush=True)

'''
rp("JOBS = {}\n", S18 + "JOBS = {}\n", 1)
m = re.search(r"JOBS\.update\(\{9: sheet_under.*?\}\)", s); assert m and '17: sheet_joints' in m.group(0), m.group(0)[-80:]
s = s[:m.start()] + m.group(0).replace("17: sheet_joints", "17: sheet_joints, 18: sheet_sensing") + s[m.end():]
open('draw_sheets.py', 'w').write(s); print('wrote draw_sheets.py', len(s))

# NOTE (21 Nov, late): after this patch was run, these edits were made directly in draw_sheets.py (the file in the pack is the one that drew the sheets):
#   sheet 16 labels: 'castor axis to nose face 385', 'soft nose 205', 'soft nose 115 to 265', 'top of the nib at the stop blocks 1,195', 'overall width 942';
#   sheet 18: slow zone 4 m at 0.25 m/s (as the mission software does it), protective-field box, label positions.
#   sheet 17 footnote: locking nuts, bare faces, re-torque after ten trips.
#   sheet 17 'Top tie' row: steel thread insert in the block.
#   sheet 15: under-bin ToF box, 'not rated' wording, open points brought up to revision 5 (edited directly in draw_sheets.py).
