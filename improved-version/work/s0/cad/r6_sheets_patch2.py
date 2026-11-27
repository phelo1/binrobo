#!/usr/bin/env python3
"""Revision 6 sheet changes, part 2: sheet 17 (two speed tables, shim note, parts wording), sheet 18 (new plan view, rules, tested cases),
facts from r6/facts_r6.json."""
p = '/home/claude/s0/cad/draw_sheets.py'; s = open(p).read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)
rep("FACTS = json.load(open('/home/claude/s0/r51/facts_r51.json'))", "FACTS = json.load(open('/home/claude/s0/r6/facts_r6.json'))")
# ---- sheet 17
rep("The base bracket has a shim pack: on assembly the base pin is set so that the actuator\\'s own stops fall at 331 and at -15 mm, whatever the built length of the unit.'",
    "The base bracket has a shim pack: on assembly the base pin is set so that the actuator\\'s BOTTOM stop falls at -15 mm, 3 mm above the block. Its top stop then falls at 331 to 335 mm, depending on the unit\\'s own stroke (346 to 350 mm): 5 to 9 mm under the +340 block.'")
rep("    dr.text((x, y), 'Speed rule: stop inside the bumper', font=F(26, True), fill=INK); y += 44\n", "    dr.text((x, y), 'Speed rule: touch-safe speed and fast cruise', font=F(26, True), fill=INK); y += 44\n")
rep("'Lidar and camera keep people clear of the robot (sheet 18). The soft nose is the last line: its switch strip acts at the first touch and the foam then has about 150 mm to give (to be measured). The table gives the speeds at which the simulated stop, from the touch to standstill, stays under 130 mm on a wet surface (grip 0.30), with 0.15 s between the touch and the brakes. The rule looks 3 m ahead, so the robot is already slow at the brow of the hill.'",
    "'Two speeds for every slope. TOUCH-SAFE: a touch on the soft nose stops the robot inside the foam (150 mm to give, to be measured; simulated stop under 130 mm on a wet surface, 0.15 s to the brakes). The robot runs at it whenever anyone or anything is near, in the yard and at the road. FAST CRUISE: only on a clear lane (sheet 18); a touch then does NOT stop it inside the foam, so it rests on the sensors. It needs the 2:1 chain stage. Both look ahead along the mapped slope.'")
rep("    y += 12; cw = (430, 330, 330); xx = x\n    for h_, w_ in zip(('Slope, going down', 'Full bin on board', 'Empty, or empty bin'), cw): dr.text((xx, y), h_, font=fb, fill=INK); xx += w_\n    dr.line([(x, y + 28), (x + sum(cw), y + 28)], fill=INK, width=2); y += 38\n    for a_, b_, c_ in FACTS['speed_rule']:\n        xx = x\n        for t, w_ in zip((a_, b_, c_), cw): dr.text((xx, y), t, font=f, fill=INK); xx += w_\n        y += 32\n",
    "    y += 12; cw = (330, 205, 205, 205, 205); xx = x + cw[0]\n    for h_, w_ in (('Touch-safe', cw[1] + cw[2]), ('Fast cruise, clear lane', cw[3] + cw[4])): dr.text((xx, y), h_, font=fb, fill=INK); xx += w_\n    y += 30; xx = x\n    for h_, w_ in zip(('Slope, going down', 'full bin', 'empty', 'full bin', 'empty'), cw): dr.text((xx, y), h_, font=fb, fill=INK); xx += w_\n    dr.line([(x, y + 28), (x + sum(cw), y + 28)], fill=INK, width=2); y += 38\n    for row_ in FACTS['speed_rule']:\n        xx = x\n        for t, w_ in zip(row_, cw): dr.text((xx, y), t, font=f, fill=INK); xx += w_\n        y += 32\n")
rep("              'Stop relay and contactors: the used relay and the two contactors of the B2-F parts list. Bench test: with either contactor held closed by hand, the other still cuts the motors.'):",
    "              'Stop relay and contactors: the used relay and the two contactors of the B2-F parts list. Bench test with the wheels off the ground: a fused jumper across one contactor\\'s main terminals stands in for a weld; the other must still cut the motors and the voltage check must refuse the reset. Never hold a contactor closed by hand.',\n              'Chain stage: 12-tooth motor sprocket and 24-tooth wheel sprocket, 08B chain (2:1). Motor controller current limit 26 A. Third lidar: the same type as the other two.'):")
# ---- sheet 18: new function, the old one stays in the file unused
new18 = r'''
def sheet_sensing_r6(n=18):
    """[revision 6] people avoidance: three lidars, lane watch, near zone, camera, fast cruise."""
    img, dr = new_sheet(n, 'People avoidance: lane watch, near zone, fast cruise', 'Revision 6: three lidars see all round the robot and find anything standing or moving in the lane; the camera says whether it is a person. Nothing here is certified: detection rates are assumed until measured.')
    SC = 135.0; cx, cy = 900, 1500
    def P(x, y): return (cx - y * SC, cy - x * SC)
    def poly(pts, **kw): dr.polygon([P(*p) for p in pts], **kw)
    def over(pts, rgba):
        ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).polygon([P(*p) for p in pts], fill=rgba); img.paste(Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB'))
    gap = FACTS['kl_gap']; yl = 0.471 + gap; yr = yl - 4.1; x0, x1 = -3.9, 8.6
    poly([(x0, yl), (x1, yl), (x1, yr), (x0, yr)], fill=(236, 236, 232))
    # near zone: 3 m from the outline, all round
    bx0, bx1, bh = -0.401, 1.332, 0.468; nz = []
    for (qx, qy, a0) in ((bx1, bh, 0), (bx0, bh, 90), (bx0, -bh, 180), (bx1, -bh, 270)):
        for a in range(a0, a0 + 91, 6): nz.append((qx + 3.0 * math.cos(math.radians(a)), qy + 3.0 * math.sin(math.radians(a))))
    over(nz, (225, 70, 50, 58)); dr.line([P(*p) for p in nz + [nz[0]]], fill=(190, 50, 40), width=4)
    wedge = [(1.04, 0.0)] + [(1.04 + 5.0 * math.cos(math.radians(a)), 5.0 * math.sin(math.radians(a))) for a in range(-55, 56, 5)]
    over(wedge, (70, 130, 230, 62)); dr.line([P(*p) for p in wedge[1:]], fill=(40, 90, 200), width=3)
    cam = [(1.04, 0.0)] + [(1.04 + 6.0 * math.cos(math.radians(a)), 6.0 * math.sin(math.radians(a))) for a in range(-55, 56, 5)]; pp = [P(*p) for p in cam]; dr.line(pp + [pp[0]], fill=(40, 90, 200), width=4)
    poly([(x0, yl), (x1, yl), (x1, yl + 0.45), (x0, yl + 0.45)], fill=(150, 185, 140)); poly([(x0, yr), (x1, yr), (x1, yr - 0.45), (x0, yr - 0.45)], fill=(150, 185, 140))
    for d_, w_ in ((0.6, 5), (1.4, 2)):
        pfp = [P(*p) for p in ((0.93, -0.551), (1.332 + d_, -0.551), (1.332 + d_, 0.551), (0.93, 0.551))]; dr.line(pfp + [pfp[0]], fill=(170, 20, 20), width=w_)
    poly([(-0.401, -0.468), (1.132, -0.468), (1.252, -0.468), (1.332, -0.388), (1.332, 0.388), (1.252, 0.468), (-0.401, 0.468)], fill=(120, 126, 134), outline=INK)
    poly([(1.132, -0.468), (1.252, -0.468), (1.332, -0.388), (1.332, 0.388), (1.252, 0.468), (1.132, 0.468)], fill=(225, 120, 60), outline=INK)
    for (x, y) in ((1.08, 0.0), (-0.342, 0.425), (-0.342, -0.425)):
        px, py = P(x, y); dr.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(30, 30, 30))
    # a walker inside the lane and one joined to the hedge
    for (x, y, col) in ((6.9, -1.1, (200, 30, 30)), (4.6, yr + 0.12, (110, 110, 110))):
        px, py = P(x, y); dr.ellipse([px - 0.25 * SC, py - 0.25 * SC, px + 0.25 * SC, py + 0.25 * SC], outline=col, width=5)
    f = F(21); fb = F(21, True)
    def lab(x, y, t, dx=0, dy=0, bold=False, col=INK): px, py = P(x, y); dr.text((px + dx, py + dy), t, font=fb if bold else f, fill=col)
    lab(8.2, 1.7, 'slow range: anything in the lane up to 4 m ahead (10 m at 1.0 m/s) ends the fast cruise', dx=250, dy=-64, bold=True)
    lab(6.9, -1.1, 'in the lane: an object', dx=44, dy=-12, col=(200, 30, 30)); lab(4.6, yr + 0.12, 'joined to the hedge: not seen as an object', dx=70, dy=-12, col=(90, 90, 90))
    lab(6.1, 2.1, 'camera view, 6 m', dx=-40, dy=0, bold=True); lab(5.3, -0.2, 'camera pause zone, 5 m', dx=10, bold=True, col=(30, 70, 170))
    lab(3.35, -1.2, 'near zone: 3 m all round, any lidar. Stand still', dx=200, bold=True, col=(170, 40, 30))
    lab(1.95, -0.55, 'protective field 0.6 m (1.4 m at 1.0 m/s): anything at all', dx=260, dy=-10)
    lab(1.08, 0.0, 'front lidar', dx=16, dy=-12); lab(-0.342, 0.425, 'rear lidar', dx=-118, dy=12); lab(-0.342, -0.425, 'rear lidar (new)', dx=16, dy=12, bold=True)
    lab(0.5, yl + 0.42, 'left edge of the lane', dx=-250, dy=-10, bold=True)
    pa, pb = P(0.3, 0.471), P(0.3, yl); dr.line([pa, pb], fill=(200, 30, 30), width=5); dr.text((pb[0] - 6, pb[1] + 12), '%.2f m' % gap, font=fb, fill=(200, 30, 30))
    dr.text((70, 2090), 'Plan view to scale, robot driving up the page (lane 3.6 m between verges). Red: near zone. Blue: camera pause zone and view. Dark red boxes: protective field at 0.4 and 1.0 m/s.', font=F(19), fill=GREY)
    x = 1960; y = 176; w = 1280; f2 = F(19); fb2 = F(19, True)
    def head(t):
        nonlocal y
        dr.text((x, y), t, font=F(25, True), fill=INK); y += 38
    def para(t, ft=None, col=INK, lead=25):
        nonlocal y
        for ln in wrap(dr, t, ft or f2, w): dr.text((x, y), ln, font=ft or f2, fill=col); y += lead
        y += 6
    head('The rules')
    for t in FACTS['people_rules']: para(t)
    y += 4; head(FACTS['tests_head'])
    para(FACTS['tests_intro'], F(18), GREY, 23)
    cols = (560, 360, 360); xx = x
    for h_, w_ in zip(('Case', 'at 0.4 m/s and under', 'fast cruise, 1.0 m/s'), cols): dr.text((xx, y), h_, font=fb2, fill=INK); xx += w_
    dr.line([(x, y + 26), (x + sum(cols), y + 26)], fill=INK, width=2); y += 32
    for row in FACTS['tests_rows']:
        la = wrap(dr, row[0], F(17), cols[0] - 14); lb = wrap(dr, row[1], F(17), cols[1] - 12); lc = wrap(dr, row[2], F(17), cols[2] - 12)
        for k, t in enumerate(la): dr.text((x, y + 21 * k), t, font=F(17), fill=INK)
        for k, t in enumerate(lb): dr.text((x + cols[0], y + 21 * k), t, font=F(17), fill=INK)
        for k, t in enumerate(lc): dr.text((x + cols[0] + cols[1], y + 21 * k), t, font=F(17), fill=INK)
        y += 21 * max(len(la), len(lb), len(lc)) + 5
    y += 8
    for t in FACTS['people_notes']: para(t, F(18), INK, 23)
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, 'right column ends at y', int(y), flush=True)

'''
rep("JOBS = {}\n", new18 + "JOBS = {}\n")
rep("15: sheet_safety, 16: sheet_dims, 17: sheet_joints, 18: sheet_sensing})", "15: sheet_safety, 16: sheet_dims, 17: sheet_joints, 18: sheet_sensing_r6})")
s += "# [revision 6, 24 Nov] r6_sheets_patch.py + r6_sheets_patch2.py: all sheets relabelled rev 6; sheet 15 stop chains; sheet 17 two speed tables; sheet 18 redrawn (sheet_sensing_r6). 5.1 copy: draw_sheets_r51.py.\n"
open(p, 'w').write(s); print('sheet patch 2 applied')
