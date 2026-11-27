#!/usr/bin/env python3
"""Writes draw_sheets.py (revision 3) from draw_sheets_r2.py."""
s = open('draw_sheets_r2.py').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)
rep("NSHEETS = 15;", "NSHEETS = 16;")
rep("'BinRobo improved version, rev 2'", "'BinRobo improved version, rev 3'")
rep("'Revision 2, after the review of 13 Nov'", "'Revision 3, after the review of 14 Nov'")
rep("with the revision 2 changes: fixed sprung pad, 340 mm lift travel on a 400 mm actuator, castor beam on a centre pivot, 700 mm comb, bumper 65 mm forward, heavier frame sections (S12).'",
    "with the changes of revisions 1 to 3: fixed sprung pad, castor beam on a centre pivot, 700 mm comb, bumper 65 mm forward on a sprung carrier, bolted lift stops, frame drawn with its real wall thicknesses.'")
rep("N_BLK = 'Block-level model: fasteners, brackets, cable glands and the inside of the electronics pod are not modelled.'", "N_BLK = 'Fasteners, weld seams, cable glands and the inside of the electronics pod are not drawn. Bought-in units (drive units, castors, actuator, sensors) are drawn as blocks.'")
rep("N_OPEN = 'Revision 2 of 14 November 2026. Concept only: what it has passed in simulation and what is still open are in the revision 2 results note.'",
    "N_OPEN = 'Revision 3 of 14 November 2026. Concept only: what it has passed in simulation and what is still open are in the revision 3 reply note. Weight by this model: 152 kg.'")
rep("3: 'Nose cross-member, raised'", "3: 'Nose cross-member'"); rep("11: 'Pivot pin and hangers'", "11: 'Pivot pin D20, hanger plates'"); rep("20: 'Front bumper'", "20: 'Front bumper bar'")
rep("24: 'Mast gusset', ", ""); rep("28: 'Carriage plate'", "28: 'Carriage plate, aluminium'"); rep("38: 'Pad rods and springs, 45 mm'", "38: 'Pad rods, long springs'"); rep("39: 'Pad face, 11 mm behind nib'", "39: 'Pad face, 10 mm behind nib'")
rep("46: 'Ballast plate', ", ""); rep("66: 'Bumper bracket', 67: 'Lift hard stop', 68: 'Lift top limit switch'", "66: 'Bumper carrier', 67: 'Lift stop, bolted', 68: 'Lift limit switch', 72: 'Bumper switch', 73: 'Cable chain bracket', 74: 'Corner plate'")
rep("70: 'Mast foot plate'", "70: 'Mast foot shoe'"); rep("211: 'Safety and control loom'}", "211: 'Safety and control loom', 212: 'Charge loom'}")
rep("The bumper now sits 65 mm further forward on two bracket plates (item 66) and clears a castor swivelled forward by 15 mm.'",
    "The bumper bar sits 65 mm further forward than on B2-F, on a carrier (item 66) whose two arms and drop legs pass between the castors; the fixed beam behind the bar ends 200 mm from the centre line, 9 mm outside the nearest swivel circle.'")
rep("'Bay floor, bay walls and ballast (items 41, 42, 46) are cut back to clear the castors. ' + N_BLK]", "'Bay floor and bay walls (items 41, 42) are cut back to clear the castors. The 5 kg ballast plate is deleted. ' + N_BLK]")
rep("The fixed pad (item 39) sits 11 mm behind the nib tip on 45 mm of spring travel, presses on the front wall lower down and stops the bin swinging.'",
    "The fixed pad (item 39) sits 10 mm behind the nib tip. Its two rods slide in the guide block and two 134 mm springs push against a fixed cup plate behind the arm, so the pad really can move 45 mm; it presses on the front wall lower down and stops the bin swinging.'")
rep("'Wiring looms L1 to L11 are drawn in colour.'", "'Wiring looms L1 to L12 are drawn in colour.'"); rep("'L1 to L11 are wiring looms; each travels with the part it is tied to.'", "'L1 to L12 are wiring looms; each travels with the part it is tied to.'")
rep("%d their CAD, %d changed, %d new (11 of the new ones are looms).", "%d their CAD, %d changed, %d new (12 of the new ones are looms).")
rep("'Lines the BOM still lacks: the castor beam parts (items 10 to 12), bumper brackets, lift driver, hard stops and top limit switch, front camera (item 54). BOM lines not placed in the drawing: pack heater HTR-L8.',",
    "'\"new line needed\": the BOM has no line for it yet. \"to change\": the BOM line exists but describes the B2-F part. Still without a line: castor beam parts (10, 12), front camera (54), lift driver. To come out of the BOM: B2-PADACT, B2-TOGGLE, B1-PADLS, GR-07 and the ballast lines. Not placed in the drawing: pack heater HTR-L8.',")
rep("for p in ('Keeper with its motor and switch (old item 36): the front dock has nothing for it to hold', 'Pad toggle actuator, knee toggle links and toggle-lock switch (the pad is fixed)', 'Rail drop plates and fixed castor plates (replaced by the pivoting castor beam)'):",
    "for p in ('Keeper with its motor and switch (old item 36)', 'Pad toggle actuator, links and toggle-lock switch', 'Rail drop plates and fixed castor plates', 'Mast gussets (old item 24) and loose foot plates: now the welded foot shoe', 'Ballast plate 5 kg (old item 46): not needed at this weight'):")
rep("'The robot is drawn faint and the eleven looms in colour,", "'The robot is drawn faint and the twelve looms in colour,")
rep("the chain is sized for the full 345 mm of travel. Cables pass through the carriage plate in two grommet holes.',", "the chain is sized for the full 335 mm of travel and has a bracket at each end (item 73). The two top limit switches are on different looms (L7 and L6), one per stop channel.',")
rep("'Changed from the first issue: the wheel-sensor drops of L2 and L3 now run outside the motor plates, L4 runs under the gearmotors, L5 starts at the lift driver in the power box, and L11 carries the safety signals between pod and power box.'],",
    "'Changed in revision 3: L2, L3 and L4 run along the inner face of the side rails behind the side guards; every loom leaves the bay through a grommet in a cover; L6 runs on the front and top faces of the top tie; L9 runs over the nose cross-member and down a bumper leg; the charge pair is a loom of its own (L12), apart from the stop-loop cables.'],")
# ---- safety sheet rewritten
a = s.index("# ------------------------------------------------------------------ safety chain and fusing (proposal)"); b = s.index("JOBS = {}")
NEW = r'''# ------------------------------------------------------------------ safety functions, stop chain, power path and fusing (proposal, revision 3)
def sheet_safety(n=15):
    img, dr = new_sheet(n, 'Safety functions, stop chain, power path and fusing (proposed)', 'A proposal for the safety design, built from the devices in the B2-F parts list. Item numbers are those of sheet %d. The performance levels are targets; no calculation has been done.' % SH_PARTS)
    f = F(18); fb = F(18, True)
    def box(x, y, w, h, lines, col=INK, fill=(255, 255, 255), bold_first=True):
        dr.rounded_rectangle([x, y, x + w, y + h], 8, fill=fill, outline=col, width=3); th = 23 * len(lines); yy = y + (h - th) // 2
        for k, t in enumerate(lines):
            ft = fb if (k == 0 and bold_first) else f; tw = dr.textlength(t, font=ft); dr.text((x + (w - tw) / 2, yy), t, font=ft, fill=INK); yy += 23
    def line(pts, col=INK, width=4, dash=False, arrow=True):
        for a_, b_ in zip(pts[:-1], pts[1:]):
            if dash:
                L = math.hypot(b_[0] - a_[0], b_[1] - a_[1]); nseg = max(int(L / 18), 1)
                for k in range(nseg): dr.line([(a_[0] + (b_[0] - a_[0]) * k / nseg, a_[1] + (b_[1] - a_[1]) * k / nseg), (a_[0] + (b_[0] - a_[0]) * (k + 0.55) / nseg, a_[1] + (b_[1] - a_[1]) * (k + 0.55) / nseg)], fill=col, width=width)
            else: dr.line([a_, b_], fill=col, width=width)
        if arrow:
            (x1_, y1_), (x2_, y2_) = pts[-2], pts[-1]; ang = math.atan2(y2_ - y1_, x2_ - x1_)
            dr.polygon([(x2_, y2_), (x2_ - 18 * math.cos(ang - 0.42), y2_ - 18 * math.sin(ang - 0.42)), (x2_ - 18 * math.cos(ang + 0.42), y2_ - 18 * math.sin(ang + 0.42))], fill=col)
    PW = (170, 30, 30); SG = (22, 92, 170); LB = (252, 244, 240); LS = (240, 246, 252)
    # ---------------- power path
    dr.text((80, 176), 'Power path', font=F(26, True), fill=PW)
    box(80, 226, 210, 96, ['Battery', '24 V 20 Ah (45)'], PW, LB); box(330, 226, 210, 96, ['Main fuse 50 A', 'at the battery (65)'], PW, LB); box(580, 226, 190, 96, ['Isolator key', '(49)'], PW, LB)
    box(900, 226, 160, 96, ['Contactor', 'KM1'], PW, LB); box(1100, 226, 160, 96, ['Contactor', 'KM2'], PW, LB)
    for a_, b_ in ((290, 330), (540, 580), (770, 900), (1060, 1100)): line([(a_, 274), (b_, 274)], PW)
    line([(1260, 274), (1380, 274), (1380, 470)], PW, arrow=False); line([(1380, 274), (1450, 274)], PW); line([(1380, 470), (1450, 470)], PW)
    dr.text((1272, 236), 'switched', font=F(16, True), fill=PW); dr.text((1272, 284), 'feed', font=F(16, True), fill=PW)
    box(1450, 216, 500, 116, ['Drive controller (in the pod)', '2 gearmotors with spring brakes (5)', 'motor pairs 6 mm2, 30 A limit each'], PW, LB)
    box(1450, 380, 500, 180, ['Lift driver (in the power box, 48)', 'fuse 7.5 A, pair 2.5 mm2, current limit 4 A', 'runs only at standstill; "up" needs both', 'top switches (68) closed; actuator (27)'], PW, LB)
    # pre-charge and regeneration paths round the contactor pair
    line([(840, 274), (840, 412), (1320, 412), (1320, 274)], PW, width=3, dash=True, arrow=False); box(925, 388, 310, 48, ['pre-charge relay K3 + 1 kohm'], PW, (255, 255, 255), bold_first=False)
    line([(1340, 274), (1340, 354), (860, 354), (860, 274)], PW, width=3, dash=True); box(940, 332, 280, 44, ['diode: braking energy back'], PW, (255, 255, 255), bold_first=False)
    line([(810, 274), (810, 470)], PW); box(640, 470, 340, 76, ['Fuse box S2 (in the pod)', '15 A feed, 1.5 mm2'], PW, LB); line([(810, 546), (810, 590)], PW)
    box(640, 590, 340, 140, ['Stays on after a stop:', 'flight controller, companion,', 'satellite receiver, 4G modem,', 'lights, safety controller'], PW, LB)
    dr.text((652, 430), 'unswitched feed', font=F(16, True), fill=PW)
    box(80, 470, 210, 96, ['Dock charge', 'contacts (21)'], PW, LB); box(330, 470, 210, 96, ['10 A fuse +', 'ideal diode (48)'], PW, LB); line([(290, 518), (330, 518)], PW); line([(540, 518), (560, 518), (560, 274)], PW)
    dr.text((84, 574), 'loom L12, 2.5 mm2', font=F(16), fill=PW)
    # ---------------- stop chain
    dr.text((80, 770), 'Stop chain: every device on its own input pair', font=F(26, True), fill=SG)
    ins = [['E-stop button (50)', 'two contacts'], ['Front bumper switch, left (72)', 'two contacts'], ['Front bumper switch, right (72)', 'two contacts'], ['Rear bumper switch, left (18)', 'two contacts'], ['Rear bumper switch, right (18)', 'two contacts'],
           ['Two tilt switches (in the pod)', 'one per channel, mounted apart'], ['Speed and standstill monitor', 'two wheel sensors (8), two outputs'], ['Lift top switches (68)', 'channel A on L7, channel B on L6'], ['Watchdogs: flight controller, companion', 'one signal each']]
    y0 = 826; ycs = []
    for k, t in enumerate(ins): box(80, y0 + 76 * k, 520, 64, t, SG, LS); ycs.append(y0 + 76 * k + 32)
    for yc in ycs: line([(600, yc - 7), (700, yc - 7)], SG, width=3); line([(600, yc + 7), (700, yc + 7)], SG, width=3)
    box(700, 826, 380, 76 * 8 + 64, ['Safety controller', '(in the pod; replaces the', 'safety relay SR-L8)', '', '9 two-channel inputs,', 'each watched for a broken', 'wire and for a short', 'between its two channels', '', '2 safe outputs', '+ pre-charge and', 'lift-enable outputs'], SG, LS)
    box(700, 1560, 380, 70, ['Reset button (51), monitored'], SG, LS); line([(890, 1560), (890, 1498)], SG)
    line([(1020, 826), (1020, 322)], SG, arrow=True); line([(1080, 1040), (1180, 1040), (1180, 322)], SG)
    dr.text((1030, 600), 'coil KM1', font=F(16, True), fill=SG); dr.text((1190, 700), 'coil KM2', font=F(16, True), fill=SG); dr.text((1030, 622), '(loom L11)', font=F(16), fill=SG)
    line([(1240, 322), (1240, 1595), (1080, 1595)], SG, dash=True); dr.text((1250, 1180), 'feedback: the mirror contacts of', font=F(16), fill=SG); dr.text((1250, 1202), 'BOTH contactors, in series; a reset', font=F(16), fill=SG); dr.text((1250, 1224), 'is accepted only if both are closed', font=F(16), fill=SG)
    line([(1080, 1300), (1982, 1300), (1982, 470), (1950, 470)], SG, width=3); dr.text((1340, 1268), 'lift enable: standstill + both top switches', font=F(16), fill=SG)
    box(925, 388, 310, 48, ['pre-charge relay K3 + 1 kohm'], PW, (255, 255, 255), bold_first=False); box(940, 332, 280, 44, ['diode: braking energy back'], PW, (255, 255, 255), bold_first=False)   # labels drawn again, over the coil lines
    box(1450, 640, 500, 250, ['On any stop', 'both contactors open;', 'drive and lift lose power;', 'the spring brakes apply;', 'the screw actuator holds the bin (to be', 'confirmed by its supplier, or a brake added);', 'computers, lights and alerts stay on'], INK, (246, 246, 246))
    # ---------------- right-hand panel
    x = 2020; y = 176; dr.text((x, y), 'Safety functions and target levels', font=F(24, True), fill=INK); y += 36
    cw = (430, 520, 110); hd = ('What triggers it', 'What happens', 'Target'); xx = x
    for h_, w_ in zip(hd, cw): dr.text((xx, y), h_, font=F(19, True), fill=INK); xx += w_
    dr.line([(x, y + 24), (x + sum(cw) + 140, y + 24)], fill=INK, width=2); y += 30
    SFN = [('E-stop pressed', 'both contactors open, brakes apply', 'PL d'), ('Front or rear bumper pressed', 'both contactors open, brakes apply', 'PL d'), ('Speed above the limit, or motion when a standstill is commanded', 'both contactors open, brakes apply', 'PL d'),
           ('Tilt beyond the limit (two switches)', 'both contactors open, brakes apply', 'PL c'), ('Lift above 327 mm (two switches)', 'lift "up" blocked; above them, bolted stops at 335 mm', 'PL c'),
           ('Lift commanded while moving', 'lift driver not enabled', 'PL c'), ('Flight controller or companion stops answering', 'both contactors open, brakes apply', 'PL b'), ('A contactor fails to open', 'no reset; the other contactor still opens the circuit', 'part of the above')]
    for a_, b_, c_ in SFN:
        la = wrap(dr, a_, F(18), cw[0] - 14); lb = wrap(dr, b_, F(18), cw[1] - 14)
        for k, t in enumerate(la): dr.text((x, y + 23 * k), t, font=F(18), fill=INK)
        for k, t in enumerate(lb): dr.text((x + cw[0], y + 23 * k), t, font=F(18), fill=INK)
        dr.text((x + cw[0] + cw[1], y), c_, font=F(16, True), fill=INK); y += 23 * max(len(la), len(lb)) + 8
    for t in wrap(dr, 'Targets are my proposal from the risk graph of ISO 13849-1 (serious injury possible, slow machine, private lane). They are not a calculation: the component data (failure rates, diagnostic coverage, common-cause measures) still have to be collected and the levels verified.', F(18), 1190):
        dr.text((x, y), t, font=F(18), fill=RED); y += 23
    y += 16; dr.text((x, y), 'Fuses and wire sizes', font=F(24, True), fill=INK); y += 36
    for hd_, tx in (('Battery trunk (L1)', 'main fuse 50 A at the battery positive; 10 mm2 to the isolator, the contactors and the drive controller.'), ('Motor pairs (L2, L3)', '6 mm2; current limit 30 A per channel in the drive controller.'),
                    ('Lift (L5)', 'fuse 7.5 A; 2.5 mm2. The supplier lists 3 A maximum for the actuator; the driver limit is set to 4 A so a stalled lift is cut off by current, not by the fuse.'),
                    ('Charge (L12)', 'fuse 10 A and ideal diode in the power box; 2.5 mm2; joins the battery side of the isolator.'), ('Electronics (unswitched)', 'fuse box S2: 15 A feed in 1.5 mm2; branch fuses 2 to 5 A in 0.5 to 0.75 mm2.'),
                    ('Stop-loop and limit-switch pairs', '0.5 mm2, on a 2 A fuse; the two channels of a device never share a cable with motor or charge wires (L9 and L12 are separate for this reason).'),
                    ('Pre-charge and braking energy', 'a 1 kohm 2 W resistor through relay K3 charges the drive controller before the contactors close; a power diode across the contactor pair lets braking energy return to the battery when they are open. Both follow the drive-controller maker\'s manual.')):
        dr.text((x, y), hd_, font=fb, fill=INK); y += 23
        for t in wrap(dr, tx, F(18), 1176): dr.text((x + 14, y), t, font=F(18), fill=GREY); y += 23
        y += 5
    y += 12; dr.text((x, y), 'Open points', font=F(24, True), fill=RED); y += 34
    for tx in ('The lift driver is described here by what it must do (24 V, 10 A or more, adjustable current limit, fault output, enable input). No part is chosen or priced.',
               'The safety controller replaces the safety relay in the parts list because nine devices need their own monitored inputs. No part is chosen or priced.',
               'That the actuator holds its load without power is not on the supplier\'s page. Ask the supplier in writing, or add a brake or a latch.',
               'The supplier lists no position signal on this actuator: lift height comes from the load-on event and time, bounded by the switches and stops.',
               'The pack heater (BOM HTR-L8) is not placed. Connectors are not chosen.'):
        for k, t in enumerate(wrap(dr, tx, F(18), 1176)): dr.text((x + (0 if k == 0 else 16), y), ('- ' if k == 0 else '') + t, font=F(18), fill=INK); y += 23
        y += 5
    print('  safety sheet right panel ends at y', int(y))
    notes(dr, 60, 1700, ['Red: power. Blue: the stop chain. Solid lines are wires; dashed lines are the pre-charge path, the braking-energy diode and the contactor feedback loop.',
                         'Changed from revision 2: each stop device has its own two-channel input instead of being chained in series; two tilt switches; feedback from both contactors; the lift is interlocked with standstill and with two top switches; pre-charge and a path for braking energy are added.',
                         'Inside the electronics pod (item 47), not drawn: ' + '; '.join(p.split(' (')[0] for p in POD) + '.',
                         'A stop removes motion power only. The computers stay up so the robot can report where it stopped and why. This sheet is a proposal to be checked, not a wiring table.'], w=1880)
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, flush=True)

# ------------------------------------------------------------------ dimension sheet: side and plan views, to scale
def sheet_dims(n=16):
    img, dr = new_sheet(n, 'Main dimensions', 'Side view from the right and plan view from above, robot without the bin, comb at its lowest position. Parallel projection: both views are to the same scale. Dimensions in mm, taken from the model.')
    S = RN.Scene('nobin', style=lambda e: None if e['kind'] == 'loom' or not e['render'] else (*e['col'], 1.0)); fd = F(20, True)
    views = [('side', 90.0, 0.0, (60, 190, 1820, 1990)), ('plan', 90.0, -89.99, (1850, 190, 3250, 1990))]; fits = [S.fit(az, el) for _, az, el, _ in views]
    mpp = max(max(wm / (c[2] - c[0] - 430.0), hm / (c[3] - c[1] - 430.0)) for (_, _, _, c), (_, (wm, hm)) in zip(views, fits))
    def hdim(P, xa, xb, yy, txt, up=True):
        (ax, ay), (bx, by) = P(xa), P(xb); dr.line([(ax, ay), (ax, yy)], fill=GREY, width=1); dr.line([(bx, by), (bx, yy)], fill=GREY, width=1); dr.line([(ax, yy), (bx, yy)], fill=BLUE, width=3)
        for x_, sg in ((ax, 1), (bx, -1)): dr.polygon([(x_, yy), (x_ + sg * 16, yy - 6), (x_ + sg * 16, yy + 6)], fill=BLUE)
        tw = dr.textlength(txt, font=fd); dr.text(((ax + bx - tw) / 2, yy - 30 if up else yy + 6), txt, font=fd, fill=BLUE)
    def vdim(P, pa, pb, xx, txt, side=None):
        """vertical dimension at pixel column xx; text turned 90 degrees beside the line, or (side='r') written level to the right for short spans"""
        (ax, ay), (bx, by) = P(pa), P(pb); dr.line([(ax, ay), (xx, ay)], fill=GREY, width=1); dr.line([(bx, by), (xx, by)], fill=GREY, width=1); dr.line([(xx, ay), (xx, by)], fill=BLUE, width=3)
        lo, hi = max(ay, by), min(ay, by)
        dr.polygon([(xx, lo), (xx - 6, lo - 16), (xx + 6, lo - 16)], fill=BLUE); dr.polygon([(xx, hi), (xx - 6, hi + 16), (xx + 6, hi + 16)], fill=BLUE)
        tw = int(dr.textlength(txt, font=fd)) + 8
        if side == 'r': dr.text((xx + 12, (lo + hi) / 2 - 12), txt, font=fd, fill=BLUE); return
        t = Image.new('RGBA', (tw, 30), (255, 255, 255, 0)); ImageDraw.Draw(t).text((4, 2), txt, font=fd, fill=BLUE + (255,)); t = t.rotate(90, expand=True); img.paste(t, (int(xx - 36), int(min((lo + hi) / 2 - tw / 2, lo - tw - 2))), t)
    for (name, az, el, c), (look, (wm, hm)) in zip(views, fits):
        w, h = int(wm / mpp) + 4, int(hm / mpp) + 4; vi, pm = S.render(az, el, look, mpp, w, h); ox = (c[0] + c[2] - w) // 2; oy = (c[1] + c[3] - h) // 2 + (30 if name == 'side' else 0)
        img.paste(Image.fromarray(vi), (ox, oy)); dr.rectangle(c, outline=(190, 195, 202), width=2); dr.text((c[0] + 14, c[1] + 10), 'Side view (nose to the right)' if name == 'side' else 'Plan view (nose to the right, left side up)', font=F(26, True), fill=INK)
        P = lambda p: tuple(S.project([p], az, el, look, mpp, w, h)[0] + np.array([ox, oy])); top = oy - 10; bot = oy + h + 10; lft = ox - 10; rgt = ox + w + 10
        if name == 'side':
            gy = P((0, 0, 0))[1]; dr.line([(ox - 40, gy), (ox + w + 40, gy)], fill=INK, width=3)
            hdim(P, (-0.401, 0, 0), (1.171, 0, 0), bot + 150, 'overall 1,572', up=False); hdim(P, (0, 0, 0), (0.95, 0, 0), bot + 80, 'drive axle to castor swivel axis 950', up=False); hdim(P, (-0.401, 0, 0), (0, 0, 0), bot + 80, '401', up=False)
            hdim(P, (0, 0, 1.42), (0.415, 0, 1.42), top - 40, 'axle to comb face 415'); hdim(P, (0.95, 0, 1.42), (1.155, 0, 1.42), top - 40, 'to bumper face 205')
            vdim(P, (1.171, 0, 0.13), (1.171, 0, 0.23), rgt + 40, 'bumper 130 to 230', side='r'); vdim(P, (1.171, 0, 0.36), (1.171, 0, 0.41), rgt + 40, 'rails 360 to 410', side='r')
            vdim(P, (1.171, 0, 0), (1.171, 0, 1.42), rgt + 270, 'top of the mast 1,420'); vdim(P, (1.171, 0, 0), (1.171, 0, 1.51), rgt + 330, 'top of the beacon 1,510')
            vdim(P, (-0.401, 0, 0), (-0.401, 0, 0.275), lft - 40, 'pad centre 275'); vdim(P, (-0.401, 0, 0), (-0.401, 0, 0.855), lft - 110, 'top of the nib, comb down 855'); vdim(P, (-0.401, 0, 0), (-0.401, 0, 1.19), lft - 180, 'top of the nib at the bolted stops 1,190')
        else:
            hdim(P, (-0.401, 0.465, 0), (1.171, 0.465, 0), top - 40, 'overall 1,572'); vdim(P, (1.171, -0.33, 0), (1.171, 0.33, 0), rgt + 50, 'bumper bar 660'); vdim(P, (1.171, -0.465, 0), (1.171, 0.465, 0), rgt + 120, 'overall width 930')
            vdim(P, (-0.401, -0.358, 0), (-0.401, 0.358, 0), lft - 40, 'between the side guards 716'); vdim(P, (-0.401, -0.35, 0), (-0.401, 0.35, 0), lft - 110, 'comb 700'); vdim(P, (-0.401, -0.4, 0), (-0.401, 0.4, 0), lft - 180, 'drive wheel track 800')
            hdim(P, (-0.37, -0.465, 0), (0.98, -0.465, 0), bot + 80, 'side rails 1,350', up=False); hdim(P, (0.49, -0.465, 0), (0.955, -0.465, 0), bot + 150, 'mast-base to nose cross-member 465', up=False)
    notes(dr, 60, 2010, ['Heights: castor pivot pin 200; drive wheels 330 diameter; castors 200 diameter, 280 either side of the centre line; lowest fixed part 120 (bay floor). Lift: firmware stop at 320 of travel, limit switches at 327, bolted stops at 335; at the stops the carriage plate is 35 below the top tie.',
                         'With a 240 L bin on board the overall length is 1,617. The pivot-turn circle measured in simulation is 2.46 m across. Dimensions are of this concept model, not of a built machine.'], w=2300)
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, flush=True)

'''
s = s[:a] + NEW + s[b:]
rep("13: sheet_parts, 14: sheet_looms, 15: sheet_safety})", "13: sheet_parts, 14: sheet_looms, 15: sheet_safety, 16: sheet_dims})")
rep("  14     wiring looms (proposed routing)", "  14     wiring looms (proposed routing)\n  15     safety functions, stop chain, power path, fusing (proposal)\n  16     main dimensions, side and plan views")
open('draw_sheets.py', 'w').write(s); print('wrote draw_sheets.py', len(s))
