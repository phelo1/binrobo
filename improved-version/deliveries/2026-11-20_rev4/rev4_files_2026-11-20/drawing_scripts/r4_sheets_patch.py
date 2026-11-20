#!/usr/bin/env python3
"""Writes draw_sheets.py (revision 4) from draw_sheets_r3.py: titles, notes, the safety sheet, the dimension sheet, and a new sheet 17
(bolted joints, lift end stops, speed rule). Facts that come from the test results are read from /home/claude/s0/r4/facts.json at draw time."""
s = open('draw_sheets_r3.py').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)

rep("W, H = 3307, 2339; NSHEETS = 16; SH_EX = 11; SH_PARTS = 13; SH_SAFE = 15; DATE = '2026-11-14'", "W, H = 3307, 2339; NSHEETS = 17; SH_EX = 11; SH_PARTS = 13; SH_SAFE = 15; DATE = '2026-11-20'\nFACTS = json.load(open('/home/claude/s0/r4/facts.json'))")
rep("'BinRobo improved version, rev 3'", "'BinRobo improved version, rev 4'")
rep("'Revision 3, after the review of 14 Nov'", "'Revision 4, after the review of 15 Nov'")
rep("N_SRC = 'Drawn from the other agent\\'s CAD model of B2-F with the changes of revisions 1 to 3: fixed sprung pad, castor beam on a centre pivot, 700 mm comb, bumper 65 mm forward on a sprung carrier, bolted lift stops, frame drawn with its real wall thicknesses.'",
    "N_SRC = 'Drawn from the other agent\\'s CAD model of B2-F with the changes of revisions 1 to 4: fixed sprung pad, castor beam on a centre pivot, 700 mm comb, 60 x 60 side rails, bolted joints throughout, mast struts, a foam safety bumper 300 mm deep, lift stop blocks on the uprights.'")
rep("N_BLK = 'Fasteners, weld seams, cable glands and the inside of the electronics pod are not drawn.", "N_BLK = 'Bolts, crush tubes, cable glands and the inside of the electronics pod are not drawn; sheet 17 lists the bolts of every joint. There are no welds.")
rep("N_OPEN = 'Revision 3 of 14 November 2026. Concept only: what it has passed in simulation and what is still open are in the revision 3 reply note. Weight by this model: 152 kg.'",
    "N_OPEN = 'Revision 4 of 20 November 2026. Concept only: what it has passed in simulation and what is still open are in the revision 4 reply note. Weight by this model: %s kg.' % FACTS['kg']")
rep("20: 'Front bumper bar', 21: 'Charge contact', 22: 'Headlight', 23: 'Mast upright 80 x 40 x 4', 25: 'Mast top tie',", "20: 'Safety bumper, foam', 21: 'Charge pad, under the nose', 22: 'Headlight', 23: 'Mast upright, foot cleats', 25: 'Mast top tie',")
rep("27: 'Lift actuator, 400 mm unit'", "27: 'Lift actuator, own end stops'")
rep("66: 'Bumper carrier', 67: 'Lift stop, bolted', 68: 'Lift limit switch', 72: 'Bumper switch', 73: 'Cable chain bracket', 74: 'Corner plate', 69: 'Rail backing flat', 70: 'Mast foot shoe', 71: 'Actuator base bracket'",
    "66: 'Bumper carrier', 67: 'Lift stop block', 68: 'Lift limit switch', 72: 'Under-bin light beam', 73: 'Cable chain bracket', 74: 'Corner plate, bolted', 69: 'Rail backing flat', 70: 'Mast strut', 71: 'Actuator base bracket'")
rep("11: 'Pivot pin D20, hanger plates'", "11: 'Pivot pin D20, clamp plates'")
rep("'Overall size: 1,572 mm long, 930 mm wide, 1,510 mm high (1,617 mm long with a 240 L bin on board).'", "'Overall size: 1,831 mm long, 930 mm wide, 1,510 mm high (1,876 mm long with a 240 L bin on board).'")
rep("(0.95 + 0.152 * math.cos(t), sgn * 0.28 + 0.152 * math.sin(t), 0.13)", "(0.95 + 0.152 * math.cos(t), sgn * 0.28 + 0.152 * math.sin(t), 0.115)")
rep("'Red dashed circles: the room each castor needs to swivel (drawn at the height of the bumper\\'s lower edge). The bumper bar sits 65 mm further forward than on B2-F, on a carrier (item 66) whose two arms and drop legs pass between the castors; the fixed beam behind the bar ends 200 mm from the centre line, 9 mm outside the nearest swivel circle.',",
    "'Red dashed circles: the room each castor needs to swivel (drawn at the height of the bumper\\'s lower edge). The foam safety bumper (item 20) sits on a carrier (item 66): two folded brackets whose drop legs pass between the castors, and a backing beam in front of the swivel circles at a height the castor wheels do not reach. The two charge pads (item 21) are under the nose, behind the bumper.',")
rep("'Bay floor and bay walls (items 41, 42) are cut back to clear the castors. The 5 kg ballast plate is deleted. ' + N_BLK]", "'Bay floor and bay walls (items 41, 42) are cut back to clear the castors. The two light beams (item 72) cross under the bin 40 mm above the ground. ' + N_BLK]")
rep("Its two rods slide in the guide block and two 134 mm springs push against a fixed cup plate behind the arm, so the pad really can move 45 mm;", "Its two rods slide in the guide block and two 145 mm springs, guided in bores through the block, push against a fixed cup plate behind the arm, so the pad really can move 45 mm;")
rep("'Mast gussets (old item 24) and loose foot plates: now the welded foot shoe', 'Ballast plate 5 kg (old item 46): not needed at this weight'", "'Mast gussets and foot plates: now bolted cleats and two struts', 'Ballast plate 5 kg (old item 46)', 'Sliding bumper bar, pins and switches: now the foam bumper', 'Welded corner plates, foot shoes, pivot plates: now bolted'")
rep("'Changed in revision 3: L2, L3 and L4 run along the inner face of the side rails behind the side guards; every loom leaves the bay through a grommet in a cover; L6 runs on the front and top faces of the top tie; L9 runs over the nose cross-member and down a bumper leg; the charge pair is a loom of its own (L12), apart from the stop-loop cables.'",
    "'Changed in revision 4: L6 and L7 run beside the inner faces of the uprights (the struts end on the front faces); L4 also feeds the two light beams under the bin; L9 runs along the rear face of the nose cross-member and down the right bumper bracket to the safety bumper; the charge loom (L12) starts at the two pads under the nose and runs up the left bracket.'")
rep("The two top limit switches are on different looms (L7 and L6), one per stop channel.'", "The lift limit switches (two at the top, two at the bottom) are split between looms L7 and L6, one loom per stop channel.'")

# ---------------------------------------------------------------- safety sheet
rep("'A proposal for the safety design, built from the devices in the B2-F parts list. Item numbers are those of sheet %d. The performance levels are targets; no calculation has been done.' % SH_PARTS", "'A proposal for the safety design. Item numbers are those of sheet %d. The performance levels are targets; the reply note has a first-pass estimate, which is not a verification.' % SH_PARTS")
rep("box(1450, 380, 500, 180, ['Lift driver (in the power box, 48)', 'fuse 7.5 A, pair 2.5 mm2, current limit 4 A', 'runs only at standstill; \"up\" needs both', 'top switches (68) closed; actuator (27)'], PW, LB)",
    "box(1450, 380, 500, 180, ['Lift driver (in the power box, 48)', 'fuse 15 A, pair 2.5 mm2; limit 6 A up, 3 A down', 'fed through two safety relay contacts;', 'the actuator (27) has its own end stops'], PW, LB)")
rep("box(80, 470, 210, 96, ['Dock charge', 'contacts (21)'], PW, LB)", "box(80, 470, 210, 96, ['Charge pads', 'under the nose (21)'], PW, LB)")
rep("""    ins = [['E-stop button (50)', 'two contacts'], ['Front bumper switch, left (72)', 'two contacts'], ['Front bumper switch, right (72)', 'two contacts'], ['Rear bumper switch, left (18)', 'two contacts'], ['Rear bumper switch, right (18)', 'two contacts'],
           ['Two tilt switches (in the pod)', 'one per channel, mounted apart'], ['Speed and standstill monitor', 'two wheel sensors (8), two outputs'], ['Lift top switches (68)', 'channel A on L7, channel B on L6'], ['Watchdogs: flight controller, companion', 'one signal each']]
    y0 = 826; ycs = []
    for k, t in enumerate(ins): box(80, y0 + 76 * k, 520, 64, t, SG, LS); ycs.append(y0 + 76 * k + 32)""",
"""    ins = [['E-stop button (50)', 'two contacts'], ['Safety bumper, front (20)', 'its control unit: two outputs'], ['Rear bumper switch, left (18)', 'two contacts'], ['Rear bumper switch, right (18)', 'two contacts'],
           ['Light beams under the bin, A and B (72)', 'one beam per channel'], ['Tilt: a switch and an inclinometer', 'two different sensors, mounted apart'], ['Speed and standstill: certified module', 'two wheel sensors (8)'],
           ['Lift top switches (68)', 'channel A on L7, channel B on L6'], ['Lift bottom switches (68)', 'channel A on L7, channel B on L6'], ['Watchdogs: flight controller, companion', 'one signal each']]
    y0 = 826; ycs = []
    for k, t in enumerate(ins): box(80, y0 + 68 * k, 520, 58, t, SG, LS); ycs.append(y0 + 68 * k + 29)""")
rep("box(700, 826, 380, 76 * 8 + 64, ['Safety controller', '(in the pod; replaces the', 'safety relay SR-L8)', '', '9 two-channel inputs,', 'each watched for a broken', 'wire and for a short', 'between its two channels', '', '2 safe outputs', '+ pre-charge and', 'lift-enable outputs'], SG, LS)",
    "box(700, 826, 380, 76 * 8 + 64, ['Safety controller', '(in the pod; replaces the', 'safety relay SR-L8)', '', '10 two-channel inputs,', 'each watched for a broken', 'wire and for a short', 'between its two channels', '', '2 safe outputs: contactors', '2 safe outputs: lift relays', '+ pre-charge output'], SG, LS)")
rep("dr.text((1340, 1268), 'lift enable: standstill + both top switches', font=F(16), fill=SG)", "dr.text((1340, 1268), 'lift feed: two relays (standstill, limit switches, light beams)', font=F(16), fill=SG)")
rep("'the screw actuator holds the bin (to be', 'confirmed by its supplier, or a brake added);',", "'the lift actuator holds the bin (self-locking', 'to 8.8 kN by its data sheet);',")
rep("""    SFN = [('E-stop pressed', 'both contactors open, brakes apply', 'PL d'), ('Front or rear bumper pressed', 'both contactors open, brakes apply', 'PL d'), ('Speed above the limit, or motion when a standstill is commanded', 'both contactors open, brakes apply', 'PL d'),
           ('Tilt beyond the limit (two switches)', 'both contactors open, brakes apply', 'PL c'), ('Lift above 327 mm (two switches)', 'lift "up" blocked; above them, bolted stops at 335 mm', 'PL c'),
           ('Lift commanded while moving', 'lift driver not enabled', 'PL c'), ('Flight controller or companion stops answering', 'both contactors open, brakes apply', 'PL b'), ('A contactor fails to open', 'no reset; the other contactor still opens the circuit', 'part of the above')]""",
"""    SFN = [('E-stop pressed', 'both contactors open, brakes apply', 'PL d'), ('Front safety bumper pressed', 'both contactors open, brakes apply; at the speeds of the slope rule (sheet 17) the robot stops inside the bumper travel', 'PL d'),
           ('Rear bumper pressed', 'both contactors open, brakes apply (reversing is at 0.2 m/s or less)', 'PL d'), ('Speed above the slope-rule limit, or motion when a standstill is commanded', 'both contactors open, brakes apply', 'PL d'),
           ('Tilt beyond the limit (two different sensors)', 'both contactors open, brakes apply', 'PL c'), ('A light beam under the bin is broken', 'lowering blocked, or stopped if under way', 'PL c'),
           ('Lift above 327 mm or below 0 mm (two switches each)', 'lift feed cut. Beyond: the actuator\\'s own end stops, then the stop blocks', 'PL c'), ('Lift commanded while moving', 'lift feed stays cut', 'PL c'),
           ('Flight controller or companion stops answering', 'both contactors open, brakes apply', 'PL b'), ('A contactor or lift relay fails to open', 'no reset; the other one still opens the circuit', 'in the above'),
           ('Load comes off the lift early while lowering (firmware, not rated)', 'stop, raise 30 mm, alert', 'none')]""")
rep("'Targets are my proposal from the risk graph of ISO 13849-1 (serious injury possible, slow machine, private lane). They are not a calculation: the component data (failure rates, diagnostic coverage, common-cause measures) still have to be collected and the levels verified.'",
    "'Targets are my proposal from the risk graph of ISO 13849-1 (serious injury possible, slow machine, private lane). The reply note has a first-pass estimate from typical component values. It is not a verification: that needs the data of the parts actually bought and a qualified person.'")
rep("('Lift (L5)', 'fuse 7.5 A; 2.5 mm2. The supplier lists 3 A maximum for the actuator; the driver limit is set to 4 A so a stalled lift is cut off by current, not by the fuse.'),",
    "('Lift (L5)', 'fuse 15 A; 2.5 mm2. The data sheet gives about 10 A at the full 6.8 kN; the driver limit is set to 6 A going up (about 3 kN, twice the load of a full bin) and 3 A going down, so a stalled lift is cut off by current, not by the fuse.'),")
rep("('Stop-loop and limit-switch pairs', '0.5 mm2, on a 2 A fuse; the two channels of a device never share a cable with motor or charge wires (L9 and L12 are separate for this reason).'),",
    "('Stop-loop, light-beam and limit-switch pairs', '0.5 mm2, on a 2 A fuse; the two channels of a device never share a cable with motor or charge wires.'),")
rep("""    for tx in ('The lift driver is described here by what it must do (24 V, 10 A or more, adjustable current limit, fault output, enable input). No part is chosen or priced.',
               'The safety controller replaces the safety relay in the parts list because nine devices need their own monitored inputs. No part is chosen or priced.',
               'That the actuator holds its load without power is not on the supplier\\'s page. Ask the supplier in writing, or add a brake or a latch.',
               'The supplier lists no position signal on this actuator: lift height comes from the load-on event and time, bounded by the switches and stops.',
               'The pack heater (BOM HTR-L8) is not placed. Connectors are not chosen.'):""",
"""    for tx in ('The stop distances behind the slope rule come from simulation with a 0.15 s reaction time and a bumper that still has 150 mm to travel after it switches. Both must be measured on the built robot.',
               'The empty robot brakes on its drive wheels only and carries over half its weight on the castors. On a 12 % pitch it needs grip above 0.3 to hold nose-first. See the reply note for the options.',
               'Safety controller, contactors with mirror contacts, bumper with its control unit, light beams and lift driver are described by what they must do. Candidate types are in the reply note; none is ordered.',
               'Lift height comes from the load-on event and time, bounded by switches, the actuator\\'s own stops and the blocks. A position signal from the actuator would be better.',
               'The pack heater (BOM HTR-L8) is not placed. Connectors are not chosen.'):""")
rep("'Changed from revision 2: each stop device has its own two-channel input instead of being chained in series; two tilt switches; feedback from both contactors; the lift is interlocked with standstill and with two top switches; pre-charge and a path for braking energy are added.',",
    "'Changed from revision 3: a foam safety bumper with its own control unit replaces the two bumper switches; two light beams guard the space under the bin; the lift has bottom switches on both channels and its feed is cut by two safety relays, not by the driver\\'s enable input; tilt is sensed by two different sensors; speed and standstill come from a certified module.',")

# ---------------------------------------------------------------- dimension sheet
rep("hdim(P, (-0.401, 0, 0), (1.171, 0, 0), bot + 150, 'overall 1,572', up=False)", "hdim(P, (-0.401, 0, 0), (1.430, 0, 0), bot + 150, 'overall 1,831', up=False)")
rep("hdim(P, (0.95, 0, 1.42), (1.155, 0, 1.42), top - 40, 'to bumper face 205')", "hdim(P, (0.95, 0, 1.42), (1.430, 0, 1.42), top - 40, 'to the bumper face 480'); hdim(P, (1.130, 0, 0), (1.430, 0, 0), bot + 80, 'bumper 300', up=False)")
rep("vdim(P, (1.171, 0, 0.13), (1.171, 0, 0.23), rgt + 40, 'bumper 130 to 230', side='r'); vdim(P, (1.171, 0, 0.36), (1.171, 0, 0.41), rgt + 40, 'rails 360 to 410', side='r')", "vdim(P, (1.430, 0, 0.115), (1.430, 0, 0.265), rgt + 40, 'bumper 115 to 265', side='r'); vdim(P, (1.430, 0, 0.36), (1.430, 0, 0.42), rgt + 40, 'rails 360 to 420', side='r')")
rep("vdim(P, (1.171, 0, 0), (1.171, 0, 1.42), rgt + 270, 'top of the mast 1,420'); vdim(P, (1.171, 0, 0), (1.171, 0, 1.51), rgt + 330, 'top of the beacon 1,510')", "vdim(P, (1.430, 0, 0), (1.430, 0, 1.42), rgt + 270, 'top of the mast 1,420'); vdim(P, (1.430, 0, 0), (1.430, 0, 1.51), rgt + 330, 'top of the beacon 1,510')")
rep("vdim(P, (-0.401, 0, 0), (-0.401, 0, 1.19), lft - 180, 'top of the nib at the bolted stops 1,190')", "vdim(P, (-0.401, 0, 0), (-0.401, 0, 1.19), lft - 180, 'top of the nib at the stop blocks 1,190')")
rep("hdim(P, (-0.401, 0.465, 0), (1.171, 0.465, 0), top - 40, 'overall 1,572'); vdim(P, (1.171, -0.33, 0), (1.171, 0.33, 0), rgt + 50, 'bumper bar 660'); vdim(P, (1.171, -0.465, 0), (1.171, 0.465, 0), rgt + 120, 'overall width 930')",
    "hdim(P, (-0.401, 0.465, 0), (1.430, 0.465, 0), top - 40, 'overall 1,831'); vdim(P, (1.430, -0.35, 0), (1.430, 0.35, 0), rgt + 50, 'safety bumper 700'); vdim(P, (1.430, -0.465, 0), (1.430, 0.465, 0), rgt + 120, 'overall width 930')")
rep("""    notes(dr, 60, 2010, ['Heights: castor pivot pin 200; drive wheels 330 diameter; castors 200 diameter, 280 either side of the centre line; lowest fixed part 120 (bay floor). Lift: firmware stop at 320 of travel, limit switches at 327, bolted stops at 335; at the stops the carriage plate is 35 below the top tie.',
                         'With a 240 L bin on board the overall length is 1,617. The pivot-turn circle measured in simulation is 2.46 m across. Dimensions are of this concept model, not of a built machine.'], w=2300)""",
"""    notes(dr, 60, 2010, ['Heights: castor pivot pin 200; drive wheels 330 diameter; castors 200 diameter, 280 either side of the centre line; lowest fixed part 100 (charge pads). Lift actuator: 600 between its pins when closed, 350 stroke; base pin 335 above the ground; with the comb down the pins are 615 apart. Sheet 17 gives the order of the lift end stops.',
                         'With a 240 L bin on board the overall length is 1,876. The pivot-turn circle measured in simulation is %s m across. Dimensions are of this concept model, not of a built machine.' % FACTS['pivot']], w=2300)""")

# ---------------------------------------------------------------- sheet 17: bolted joints, lift end stops, speed rule
S17 = r'''
def sheet_joints(n=17):
    img, dr = new_sheet(n, 'Bolted joints, lift end stops and the speed rule', 'Every joint of the frame and mast is bolted: nothing is welded. Bolt sizes come from the hand calculation in the reply note. Positions are of this concept model.')
    f = F(19); fb = F(19, True); x = 70; y = 180
    dr.text((x, y), 'Bolted joints', font=F(26, True), fill=INK); y += 44
    cols = (560, 470, 150, 330, 150); heads = ('Joint (item)', 'Bolts, each joint', 'Class', 'Through', 'Torque')
    xx = x
    for h_, w_ in zip(heads, cols): dr.text((xx, y), h_, font=fb, fill=INK); xx += w_
    dr.line([(x, y + 28), (x + sum(cols), y + 28)], fill=INK, width=2); y += 36
    J = [('Rail to cross-member, 4 joints (74)', '4 x M8 x 90: 2 through the rail, 2 through the cross-member', '8.8', 'crush tubes; top and bottom plate 6 mm', '25 N m'),
         ('Mast foot, 2 uprights (23)', '2 x M12 x 80 down through the cross-member; 2 x M8 x 70 through the upright', '8.8', 'crush tubes; two angle cleats 60 x 60 x 6', '85 / 25 N m'),
         ('Mast strut, 2 struts (70)', 'M10 pin at each end; lug plates 2 x M8 x 70 through the upright; foot cleats 2 x M8 x 80 through the nose member', '8.8', 'crush tubes; pins with lock nuts, not clamped', '25 N m'),
         ('Lift stop blocks, 4 blocks (67)', '2 x M10 x 100 through the upright', '8.8', 'crush tubes; 6 mm packer', '49 N m'),
         ('Top tie (25)', '1 x M8 x 80 down into each top stop block', '8.8', 'tapped hole in the block', '25 N m'),
         ('Actuator base bracket (71)', '2 x M12 x 90 through the cross-member; lug angles 2 x M8 each on a shim pack', '8.8', 'crush tubes; shims set the pin height', '85 / 25 N m'),
         ('Castor pivot clamp plates (11)', '4 x M10 x 90 through the nose member and both plates', '8.8', 'crush tubes', '49 N m'),
         ('Bumper carrier (66)', '2 x M8 x 80 per bracket through the nose member; 2 x M8 per bracket to the backing beam', '8.8', 'crush tubes in the member', '25 N m'),
         ('Drive / motor plate (4)', '4 x M8 x 85 up through the rail per plate', '8.8', 'crush tubes', '25 N m'),
         ('Carriage: beams, bracket, pad arm (28, 37)', '8 x M8 beams to plate; 4 x M8 bracket; 3 x M10 pad arm to tongue', '8.8', 'tapped or nutted', '25 / 49 N m'),
         ('Linear rails (26)', 'M4 x 16 at 60 mm pitch into the 10 mm backing flat', '12.9', 'tapped', '4.5 N m')]
    for row in J:
        cells = [wrap(dr, t, f, w_ - 16) for t, w_ in zip(row, cols)]; xx = x
        for c_, w_ in zip(cells, cols):
            for k, t in enumerate(c_): dr.text((xx, y + 24 * k), t, font=f, fill=INK)
            xx += w_
        y += 24 * max(len(c_) for c_ in cells) + 9; dr.line([(x, y - 5), (x + sum(cols), y - 5)], fill=(210, 214, 220), width=1)
    y += 6
    for t in wrap(dr, 'A crush tube is a steel sleeve inside the box section, as long as the section is wide, so the bolt can be tightened without squashing the walls. Torques are for class 8.8 bolts, lightly oiled. About 66 structural bolts in all (the weight table counts them).', F(18), sum(cols)):
        dr.text((x, y), t, font=F(18), fill=GREY); y += 23
    # ---------------- lift travel line
    y += 30; dr.text((x, y), 'Lift end stops, in the order the carriage meets them', font=F(26, True), fill=INK); y += 50
    x0, x1 = x + 60, x + sum(cols) - 60; q0, q1 = -30.0, 345.0; X = lambda q: x0 + (x1 - x0) * (q - q0) / (q1 - q0); yl = y + 150
    dr.line([(x0, yl), (x1, yl)], fill=INK, width=4)
    dr.rectangle([X(0), yl - 9, X(305), yl + 9], fill=(170, 205, 170), outline=INK); dr.text((X(120), yl + 16), 'travel used: 0 to 305 mm', font=f, fill=INK)
    marks = [(-18, 'stop blocks', RED, 3), (-15, "actuator's own stop", BLUE, 2), (0, 'bottom switches (2)', INK, 1), (320, 'firmware stop', GREY, 1), (327, 'top switches (2)', INK, 2), (331, "actuator's own stop", BLUE, 3), (335, 'stop blocks', RED, 4)]
    for q, t, col, lvl in marks:
        xq = X(q); up = q > 100; yy = yl - 26 - 30 * lvl
        dr.line([(xq, yl - 14), (xq, yy + 24)], fill=col, width=3)
        lab = '%+d  %s' % (q, t) if q < 0 else '%d  %s' % (q, t); tw = dr.textlength(lab, font=fb)
        dr.text((xq - tw + 10 if up else xq - 10, yy), lab, font=fb, fill=col)
    y = yl + 60
    for t in wrap(dr, 'Going up, the carriage meets the firmware stop, then the two limit switches (which cut the lift feed), then the actuator\'s own end-stop switch, and only then the stop blocks. Going down the order is the same. The actuator therefore switches itself off before it can stall on a block. The base bracket has a shim pack: on assembly the base pin is set so that the actuator\'s own stops fall at 331 and at -15 mm, whatever the built length of the unit.', F(18), sum(cols)):
        dr.text((x, y), t, font=F(18), fill=INK); y += 23
    # ---------------- right column: speed rule and what the bumper must do
    x = 2090; y = 180; wR = 1150
    dr.text((x, y), 'Speed rule: stop inside the bumper', font=F(26, True), fill=INK); y += 44
    for t in wrap(dr, 'The foam bumper is the last line of protection for a person in front of the robot. After it switches it must still have at least 150 mm to travel, and the robot must stop within that. The table gives the speeds at which the simulated stop, from the bumper touch to standstill, stays under 125 mm on a wet surface (grip 0.30), with 0.15 s between the touch and the brakes.', F(19), wR):
        dr.text((x, y), t, font=F(19), fill=INK); y += 25
    y += 12; cw = (430, 330, 330); xx = x
    for h_, w_ in zip(('Slope, going down', 'Full bin on board', 'Empty, or empty bin'), cw): dr.text((xx, y), h_, font=fb, fill=INK); xx += w_
    dr.line([(x, y + 28), (x + sum(cw), y + 28)], fill=INK, width=2); y += 38
    for a_, b_, c_ in FACTS['speed_rule']:
        xx = x
        for t, w_ in zip((a_, b_, c_), cw): dr.text((xx, y), t, font=f, fill=INK); xx += w_
        y += 32
    y += 8
    for t in FACTS['speed_notes']:
        for k, l_ in enumerate(wrap(dr, t, F(18), wR - 20)): dr.text((x + (0 if k == 0 else 16), y), ('- ' if k == 0 else '') + l_, font=F(18), fill=INK); y += 23
        y += 6
    y += 20; dr.text((x, y), 'Lowering the bin', font=F(26, True), fill=INK); y += 42
    for t in FACTS['lower_notes']:
        for k, l_ in enumerate(wrap(dr, t, F(18), wR - 20)): dr.text((x + (0 if k == 0 else 16), y), ('- ' if k == 0 else '') + l_, font=F(18), fill=INK); y += 23
        y += 6
    y += 20; dr.text((x, y), 'What to ask of the bought-in safety parts', font=F(26, True), fill=INK); y += 42
    for t in ('Safety bumper: to EN ISO 13856-3, with its control unit; 300 mm deep, 150 high, 700 wide; at least 150 mm of travel left after it switches at 0.4 m/s; force on a 70 mm post no more than 250 N over that travel; rated for outdoor use.',
              'Light beams: safety single-beam sensors (type 2 or better), sender and receiver, 0.8 m range, rated for outdoor use.',
              'Lift actuator: holding force at least 6 kN, IP66, own end-stop switches, 600 mm between the pins closed, 350 mm stroke.',
              'Castors: 200 mm, crowned or rounded tyre (contact strip no wider than about 40 mm). Bench check before ordering two: the torque to swivel the wheel under a 50 kg load.',
              'Drive tyres: no stiffer than 650 N/mm (they sink at least 1.5 mm under the robot standing with a full bin).'):
        for k, l_ in enumerate(wrap(dr, t, F(18), wR - 20)): dr.text((x + (0 if k == 0 else 16), y), ('- ' if k == 0 else '') + l_, font=F(18), fill=INK); y += 23
        y += 6
    print('  sheet 17 right column ends at y', int(y))
    # ---------------- close-up views of the bolted joints (covers, guards, bay and looms left out)
    HIDE = {14, 41, 42, 43, 44, 45, 47, 48, 49, 65}
    def closeup(rect, title, state, az, el, look, span, want, hide=HIDE, fs=18):
        x0, y0, x1, y1 = rect; dr.rectangle(rect, outline=(170, 175, 182), width=2); dr.text((x0 + 12, y0 + 8), title, font=F(21, True), fill=INK)
        S = RN.Scene(state, style=lambda e: None if e['kind'] == 'loom' or e['item'] in hide or e['item'] > 100 or not e['render'] else (*e['col'], 1.0))
        w = int((x1 - x0) * 0.50); h = y1 - y0 - 60; mpp = max(span[0] / w, span[1] / h); vi, pm = S.render(az, el, np.array(look, float), mpp, w, h)
        ox = (x0 + x1 - w) // 2; oy = y0 + 48; img.paste(Image.fromarray(vi), (ox, oy)); anc = anchors(S, pm)
        shown = callouts(dr, (ox, oy), pm, anc, want, (x0 + 6, y0 + 44, x1 - 6, y1 - 6), font=fs, minpx=30); print('  close-up', title[:30], 'labels', len(shown), flush=True)
    yb0 = 1330
    closeup((70, yb0, 1060, 2060), 'Mast foot, strut and rail corner (from the front left)', 'nobin', -135.0, RN.ISO_EL, (0.70, 0.22, 0.60), (0.80, 0.86), [1, 2, 3, 23, 70, 74, 71, 27, 11, 10, 52, 67, 26, 29, 28])
    closeup((1080, yb0, 2070, 2060), 'Mast and lift stops (from the rear left)', 'nobin', -45.0, RN.ISO_EL, (0.49, 0.0, 1.02), (0.62, 0.92), [23, 25, 67, 68, 26, 28, 29, 69, 73, 62, 60, 59, 27, 70])
    closeup((2090, max(yb0, int(y) + 30), 3240, 2060), 'Nose from below: bumper carrier, charge pads, castor pivot', 'nobin', -135.0, 28.0, (1.12, 0.0, 0.26), (0.95, 0.62), [3, 10, 11, 12, 13, 20, 21, 66, 22, 1, 74, 52])
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, flush=True)

'''
rep("new_sheet(n, 'Safety functions, stop chain, power path and fusing (proposed)'", "new_sheet(n, 'Safety functions, stop chain, power and fusing'")
rep("JOBS = {}\n", S17 + "JOBS = {}\n")
rep("13: sheet_parts, 14: sheet_looms, 15: sheet_safety, 16: sheet_dims})", "13: sheet_parts, 14: sheet_looms, 15: sheet_safety, 16: sheet_dims, 17: sheet_joints})")
rep('import os, sys, math\n', 'import os, sys, math, json\n')
open('draw_sheets.py', 'w').write(s); print('wrote draw_sheets.py', len(s))
