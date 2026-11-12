#!/usr/bin/env python3
"""Bin Tug Rev H ("straddle carrier") parts list. EUR incl. VAT, 11 Nov 2026. Estimates, not quotes.
Writes ../results/bom_revH.csv and ../results/bom_revH.json.

Price status follows the project convention (revG/bom_revG.py):
  G4-checked   = line carried unchanged from revG/bom_revG4.csv where the project read the retailer page (6-8 Nov)
  G4-excerpt   = carried from the project, price from a search excerpt
  G4-est       = carried from the project, engineering estimate
  excerpt-11Nov= price seen in a search-result excerpt on 11 Nov 2026 during this review (page not opened)
  est          = estimate made in this review
Contingency is risk-weighted exactly as in COSTDOWN_G4: 5 % checked, 8 % excerpt, 12 % est, 15 % donor/local, 10 % logistics.
"""
import csv, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'results'); os.makedirs(OUT, exist_ok=True)


def R(id_, area, item, eur, status, group, func, note='', revg=''):
    return dict(id=id_, area=area, item=item, eur=float(eur), status=status, group=group, function=func, note=note, revg_line=revg)


L = [
    # ------------------------------------------------------------------ Structure (bolted RHS frame, one steel size)
    R('H-S1', 'Structure', 'Steel: 2 x 6 m 50x50x3 RHS (side rails, cross-members, mast, carriage) + 2 m 30x30x2 braces + flat bar; zinc-rich primer and topcoat', 110, 'est', 'LOCAL', 'mover',
      'Cut list ~8.5 m of 50x50x3. Replaces G1 + G2 (EUR 105) and the EUR 165 laser/press-brake/galvanise uplift the handover lists as not in the total.', 'G1, G2'),
    R('H-S2', 'Structure', 'One laser-cut order, 4-6 mm S355: comb blade, carriage cheeks, 2 motor plates, 4 mast gussets, caster outriggers, actuator lugs, battery trays (~14 parts)', 60, 'est', 'LOCAL', 'mover',
      'Rev G had 53 made parts and 34 DXF patterns; Rev H has about 14 plates and one tube size. Local quote needed (ATC [nearby town]).', 'G1'),
    R('H-S3', 'Structure', 'Carriage rollers: 8 x 6202-2RS bearings on shoulder bolts', 15, 'est', 'CN', 'bin handling', 'Rollers, not slides: lift force 1.2 kN instead of 1.7 kN (statics.json).'),
    R('H-S4', 'Structure', 'Deck, motor and battery covers: HDPE / ply offcuts', 15, 'est', 'LOCAL', 'mover', '', 'G3'),
    R('H-S5', 'Structure', 'Nose casters: 2 x 260 mm flat-free swivel casters', 60, 'est', 'IE', 'mover',
      'CONDITIONAL: the donor chair\'s 200 mm casters work but lose one step case (layout A5 in mech.json). Saving EUR 60 if kept.'),
    R('H-S6', 'Structure', 'Tail anti-tip wheels 2 x 100 mm PU', 8, 'est', 'CN', 'mover', 'Often on the donor chair already.'),
    R('H-S7', 'Structure', 'UHMW guide strips on the inner rails 2 x 600x40x10', 12, 'est', 'IE', 'bin handling'),
    # ------------------------------------------------------------------ Drive (unchanged from Rev G)
    R('G4', 'Drive', 'Donor powerchair: matched 24 V gearmotors + spring brakes, 12.5 in wheels (DoneDeal)', 160, 'G4-est', 'LOCAL', 'mover',
      'Same line and price as Rev G. RISK: used powerchair listings seen on 11 Nov were EUR 209-282 (for-sale.ie). Applies to Rev G equally.', 'G4'),
    R('G5b', 'Drive', 'Tyre sealant for the donor drive tyres (Slime 473 ml)', 17.5, 'G4-checked', 'IE', 'mover', '', 'G5b'),
    R('G6', 'Drive', 'Dual 30 A motor driver, Cytron MDDS30 (7-35 V, 30 A cont / 80 A peak)', 82.95, 'G4-checked', 'NL', 'mover',
      'CONDITIONAL: Cytron MDD20A (20 A cont / 60 A peak, 6-30 V) is GBP 37 at The Pi Hut (excerpt). Saving ~EUR 38 once the donor stall current is measured.', 'G6'),
    R('H-D1', 'Drive', 'Reverse-polarity protection for the driver (ideal-diode module, 50 A)', 8, 'est', 'CN', 'mover', 'The handover lists this as a required substitution not yet in the Rev G total.'),
    R('G9', 'Drive', 'Wheel encoders x2 (hall quadrature kit)', 18, 'G4-checked', 'CN', 'navigation', '', 'G9'),
    # ------------------------------------------------------------------ Bin handling (replaces Hitch & grabber, EUR 247 in G4)
    R('H-L1', 'Bin handling', 'Lift actuator 24 V, 3000 N, 300 mm stroke, IP65, self-locking', 45, 'excerpt-11Nov', 'CN', 'bin handling',
      'Generic 3000 N 300 mm units USD 30-55 (eBay / Alibaba excerpts). Load 1.2 kN: margin 2.5. Replaces the 450 mm tilt actuator the handover calls under-spec.', 'G10'),
    R('H-L2', 'Bin handling', '4 x IP67 roller switches: 2 lip-seated (on the comb), 2 squaring (on the carriage face)', 25.16, 'G4-excerpt', 'DE', 'bin handling',
      'Same Aratas D2SW-3L2H switch the G5 report priced at EUR 6.29 each (RS DE).', 'G13, K2'),
    R('H-L3', 'Bin handling', '2 x leg-tip side-gap sensors (VL53L1X-class ToF, potted)', 10, 'est', 'CN', 'bin handling',
      'Closes the docking loop without relying on the camera: dock_mc.json stress case 82 % -> 99.9 % first try.'),
    R('K5', 'Bin handling', 'Actuator current sensor INA219 (bin weight, not-collected, stall)', 3, 'G4-est', 'CN', 'bin handling', 'Reads weight directly instead of inferring it from tilt current.', 'K5'),
    R('H-L4', 'Bin handling', 'Rubber rest pad + comb buffer', 6, 'est', 'IE', 'bin handling'),
    # ------------------------------------------------------------------ Power
    R('H-P1', 'Power', '2 x 12 V 18 Ah AGM (24 V, 432 Wh nominal)', 93.9, 'excerpt-11Nov', 'DE', 'mover',
      'Kung Long WP18-12SHR EUR 46.95 each (ebay.de excerpt). AGM instead of the 12 Ah LiFePO4 (EUR 129.90): no BMS trip on 2 x 45 A step peaks, charges in frost, 11 kg where the layout wants it.', 'G14'),
    R('H-P2', 'Power', 'Battery trays/straps on the rails, link cable 6 mm2, Anderson SB50 pair, 60 A MIDI fuse + holder', 28, 'est', 'CN', 'mover', '', 'G16, S1'),
    R('G15', 'Power', 'Hasp + padlock on the battery covers', 7, 'G4-est', 'IE', 'theft', '', 'G15'),
    # ------------------------------------------------------------------ Safety & power distribution (unchanged)
    R('S2', 'Safety & power dist.', '6-way blade fuse box + fuses', 9, 'G4-est', 'CN', 'safety', '', 'S2'),
    R('S3', 'Safety & power dist.', 'Battery isolator key switch 100 A', 10, 'G4-est', 'CN', 'safety', '', 'S3'),
    R('S4', 'Safety & power dist.', 'Main contactor 100 A DC, 24 V coil', 28, 'G4-checked', 'DE', 'safety', '', 'S4'),
    R('S5', 'Safety & power dist.', 'Safety latch relay K1 Finder 55.34 + socket', 18, 'G4-checked', 'IE', 'safety', '', 'S5'),
    R('S6', 'Safety & power dist.', 'Relays: charge path, reset, actuator reversing pair', 16, 'G4-est', 'CN', 'safety', '', 'S6'),
    R('S7', 'Safety & power dist.', 'Dual hardware watchdog (missing-pulse detectors + relays)', 8, 'G4-est', 'CN', 'safety', '', 'S7'),
    R('S8', 'Safety & power dist.', 'Mushroom E-stop station IP65', 15, 'G4-checked', 'IE', 'safety', '', 'S8'),
    R('S9', 'Safety & power dist.', '4-ch opto input module + coil clamps', 7, 'G4-est', 'CN', 'safety', '', 'S9'),
    R('S10', 'Safety & power dist.', 'Tamper siren', 4, 'G4-est', 'CN', 'theft', '', 'S10'),
    R('S11', 'Safety & power dist.', 'Supercap / UPS HAT for clean Pi shutdown', 12, 'G4-est', 'CN', 'safety', '', 'S11'),
    R('S13', 'Safety & power dist.', 'Tilt switch in the stop loop', 3, 'G4-est', 'CN', 'safety', '', 'S13'),
    R('S12', 'Safety & power dist.', 'DS18B20 x2 (ice gate, box temperature)', 3, 'G4-est', 'CN', 'safety', '', 'S12'),
    # ------------------------------------------------------------------ Navigation, sensing, comms
    R('G18', 'Navigation', 'Flight controller F405 (ArduPilot Rover)', 35, 'G4-est', 'CN', 'navigation', '', 'G18'),
    R('G19', 'Navigation', 'RTK: LC29H rover + base core boards, 2 antennas, ESP32 NTRIP server', 78, 'G4-excerpt', 'CN', 'navigation', '', 'G19'),
    R('G21', 'Sensing', '2D lidar LDROBOT STL-06N with drip cap', 50, 'G4-excerpt', 'CN', 'obstacle sensing', '', 'G21'),
    R('G22', 'Sensing', 'Nose bumper bar + leg-tip bump strips (tape switches)', 21, 'G4-est', 'IE', 'safety', 'EUR 6 more than Rev G for the second leg tip.', 'G22'),
    R('G23', 'Sensing', 'Pi Zero 2 W + rear IP67 camera + 850 nm IR illuminator', 45, 'G4-est', 'CN', 'navigation', '', 'G23'),
    R('H-N1', 'Sensing', 'High-endurance microSD 32 GB (read-only root + UPS HAT do the protecting)', 12, 'est', 'IE', 'navigation',
      'Rev G: SanDisk Industrial EUR 39.90. The G3 BOM note itself says read-only root + supercap do most of the protection.', 'G23b'),
    R('G24', 'Sensing', 'Retro-reflective ArUco tags for 3 bins (front + back) + dock tag', 10, 'G4-est', 'IE', 'navigation', '', 'G24'),
    R('H-N2', 'Sensing', '2 x 24 GHz vehicle radar HLK-LD2451 (front, rear)', 32.92, 'excerpt-11Nov', 'CZ', 'vehicle detection',
      'EUR 16.46 each incl. VAT at laskakit.cz (excerpt). A G4 feature that is NOT in the Rev G BOM.'),
    R('H-C1', 'Comms', 'Industrial LTE USB dongle (SIM7600G-H / EC25-E class, -40..+85 C) + antenna', 45, 'est', 'CN', 'monitoring',
      'The handover says the E3372 (EUR 35) is out of its temperature range and must be replaced. EU retail for the Waveshare SIM7600G-H dongle is EUR 78 (excerpt).', 'G25'),
    R('H-C2', 'Comms', 'Two-way audio: USB sound card, 3 W amp, IP65 horn speaker, mic capsule', 30, 'est', 'CN', 'two-way audio', 'G4 feature not in the Rev G BOM; the handover estimates EUR 40-70.'),
    # ------------------------------------------------------------------ Enclosure & wiring
    R('G26', 'Enclosure & wiring', 'IP67 ABS electronics box + glands + vent + silica gel (on the mast)', 30, 'G4-est', 'IE', 'mover', '', 'G26'),
    R('G27', 'Enclosure & wiring', 'DC-DC 24->5 V 5 A, RTC, wire, lugs, ferrules, heat-shrink', 40, 'G4-est', 'CN', 'mover', '', 'G27'),
    R('H-W1', 'Enclosure & wiring', 'Connectors: Anderson PP45 for motors and actuator, Superseal for lamps and sensors, glands for the rest', 25, 'est', 'CN', 'mover',
      'Rev G: EUR 60 of keyed Deutsch DT / M12 so the tug could ship in 5 boxes and be plugged together. One robot built on site does not need that.', 'H1'),
    R('H-W2', 'Enclosure & wiring', 'Fasteners: M8/M10 8.8 zinc + nyloc for structure, A2 small screws, rivnuts, threadlock', 30, 'est', 'IE', 'mover',
      'Rev G: EUR 89, of which EUR 51 is Nord-Lock washers for the kingpin-loaded joints that no longer exist.', 'F1'),
    # ------------------------------------------------------------------ Lights (function kept: headlamps, rear red, amber beacon, markers, tape)
    R('L1', 'Lights', 'Dipped headlamps x2, Addview Hammer E60 (cut-off beam)', 35.98, 'G4-checked', 'DE', 'night lights', '', 'L1'),
    R('L2', 'Lights', 'Red position markers x2', 10.95, 'G4-checked', 'DE', 'night lights', '', 'L2'),
    R('H-X1', 'Lights', 'Amber LED beacon 12-24 V on the motor-enable circuit', 15, 'est', 'IE', 'night lights',
      'Rev G: R65/R10 type-approved beacon EUR 30.20 drawing 17 W. Type approval is for road vehicles; a plain LED beacon does the same job on a private lane at ~5 W.', 'L3'),
    R('L4', 'Lights', 'Rear work lamp 3 W', 6, 'G4-est', 'CN', 'night lights', '', 'L4'),
    R('H-X2', 'Lights', 'Reflective tape: red rear, yellow sides, white front', 15, 'est', 'IE', 'night lights', 'Rev G: ECE 104 rolls EUR 30.', 'L5'),
    R('L6', 'Lights', 'MOSFET board + LDR dusk module', 9, 'G4-est', 'CN', 'night lights', '', 'L6'),
    # ------------------------------------------------------------------ Dock (same idea: the dock looks like a bin front)
    R('H-K1', 'Dock', 'Dock post with tag plate and nose block (steel offcuts from H-S1)', 15, 'est', 'LOCAL', 'auto-charge', '', 'D1'),
    R('D2', 'Dock', 'Plated wiping charge contacts (robot-mower type) on the dock post and the carriage face', 26, 'G4-checked', 'DE', 'auto-charge', '', 'D2'),
    R('H-K2', 'Dock', 'Reed switch + magnet + 10 A relay + fuse: contacts dead until the robot is seated', 10, 'est', 'CN', 'auto-charge',
      'Rev G: ESP32 dock controller EUR 25. The robot already measures charge current (D4) and raises the alerts.', 'D3'),
    R('D4', 'Dock', 'Robot charge path: ideal diode, INA226', 9, 'G4-est', 'CN', 'auto-charge', '', 'D4'),
    R('D5', 'Dock', 'IP65 enclosure for the charger', 25, 'G4-checked', 'IE', 'auto-charge', '', 'D5'),
    R('H-K3', 'Dock', '24 V 3 A 3-stage AGM charger', 30, 'est', 'DE', 'auto-charge', 'Often supplied with the donor chair.', 'D6'),
    R('D7', 'Dock', 'Lean-to rain roof (scrap sheet)', 10, 'G4-est', 'IE', 'auto-charge', '', 'D7'),
    R('D8', 'Dock', 'Cable lock to the dock post', 15, 'G4-est', 'IE', 'theft', '', 'D8'),
    R('D9', 'Dock', 'Concrete anchors', 10, 'G4-est', 'IE', 'auto-charge', '', 'D9'),
    R('D10', 'Dock', 'Dock DC wiring 2.5 mm2 ~5 m, inline fuse', 14, 'G4-est', 'IE', 'auto-charge', '', 'D10'),
    R('D11', 'Dock', 'RCD-protected IP66 outdoor socket', 25, 'G4-checked', 'IE', 'auto-charge', 'CONDITIONAL: EUR 0 if an outdoor RCD socket already exists near the dock.', 'D11'),
]

LOGISTICS = [('SHIP-IE', 8), ('SHIP-DE', 35), ('SHIP-NL', 0), ('SHIP-CZ', 8), ('SHIP-CN', 8), ('SHIP-LOCAL', 15)]
CONT = {'G4-checked': 0.05, 'G4-excerpt': 0.08, 'excerpt-11Nov': 0.08, 'G4-est': 0.12, 'est': 0.12}

# Rev G lines that have no counterpart in Rev H (ids and EUR from revG/bom_revG4.csv)
REVG_DELETED = [('G8', 'Yaw-lock solenoid + yaw encoder + tilt IMU', 18), ('G10', 'Tilt actuator 450 mm (under-spec per the handover)', 90),
                ('G11', 'Floating twin-hook carriage', 25), ('K1', 'Latch pawls + release cam', 12), ('K3', 'Mast rest stop + catch', 10),
                ('K4', 'Lid hold-down finger', 8), ('G12', 'Anti-tip and stop rollers', 15), ('RF-10/11/12', 'Kingpin kit', 19),
                ('GR-07', 'Release cam gearmotor', 14), ('GR-10', 'Release cord', 4), ('GR-08', 'Float ratchet rack', 6), ('BT-01', 'Sand ballast cans', 21.98)]

# Rev G as published (bom_revG4.csv totals) and what its own handover says is still owed
REVG = dict(parts=1817.92, logistics=124.21, contingency=189.10, all_in=2131.23,
            by_area={'Structure': 136.98, 'Drive': 278.45, 'Hitch & grabber': 247.00, 'Power': 151.00, 'Safety & power dist.': 142.00, 'Navigation': 113.00,
                     'Sensing': 159.90, 'Comms': 35.00, 'Enclosure & wiring': 219.46, 'Lights': 122.13, 'Dock': 213.00})
REVG_OWED = [   # (item, low, mid, high, source)
    ('GH-B5F-130 grabber change', 15, 15, 15, 'HANDOVER Rev 3.0 s.6'),
    ('Tilt actuator to spec (1,500-2,500 N, IP66, 411 mm stroke): EU-stock units EUR 132-145 vs EUR 90 budgeted', 42, 48, 55, 'HANDOVER s.3; bom_revG.py note on G10'),
    ('BMS rated >= 20 A continuous', 0, 20, 40, 'HANDOVER s.5 (no price given: estimate)'),
    ('Industrial 4G modem to +75 C', 10, 25, 43, 'HANDOVER s.3; EUR 45 est to EUR 78 retail vs EUR 35'),
    ('Driver reverse-polarity protection', 5, 8, 10, 'HANDOVER s.3'),
    ('Frame as drawn in CAD (laser + press-brake + hot-dip galvanise)', 165, 165, 165, 'COSTDOWN_G4 s.5 R1; HANDOVER s.6'),
    ('Lane ramps for sharp lips over 40 mm in the bin-wheel track (EUR 15-40 each, count unknown: 0 / 3 / 6 assumed)', 0, 75, 200, 'HANDOVER s.4.2, s.6'),
    ('24 GHz radars front + rear (G4 feature, no BOM line)', 20, 33, 33, 'HANDOVER s.3; bom_revG4.csv has no radar line'),
    ('Two-way audio (G4 feature, no BOM line)', 40, 55, 70, 'HANDOVER s.3'),
]

CONDITIONAL = [   # (name, saving, condition)
    ('Keep the donor chair\'s 200 mm nose casters', 60, 'Accept one lost step case: unladen, 60 mm square step at 0.5 m/s (layout A5).'),
    ('Cytron MDD20A instead of MDDS30', 38, 'Bench-measure donor stall current first: needs < 60 A peak, < 20 A continuous per motor.'),
    ('Outdoor RCD socket already at the dock', 25, 'Brian to confirm (open item in the handover).'),
    ('Donor chair comes with a working 24 V charger', 30, 'Check on viewing.'),
    ('Tail wheels from the donor anti-tippers, steel offcuts from a local fabricator', 30, 'Sourcing.'),
]
UPSIDE_RISK = [('Donor powerchair costs EUR 220-280 instead of EUR 160', 90), ('Laser plates + steel at retail one-off prices', 50),
               ('Industrial LTE dongle bought in the EU (EUR 78)', 33)]

STAGES = {   # spend only what the next proof needs
    'Stage 1: mover + lift, driven by hand controller': ['mover', 'bin handling'],
    'Stage 2: autonomy and safety chain': ['navigation', 'obstacle sensing', 'safety'],
    'Stage 3: unattended extras': ['auto-charge', 'night lights', 'monitoring', 'vehicle detection', 'two-way audio', 'theft'],
}


def totals(lines, logistics):
    parts = sum(l['eur'] for l in lines)
    cn_lines = sum(1 for l in lines if l['group'] == 'CN')
    duty = 3.0 * cn_lines * 0.5                         # AliExpress parcels combine lines: the project counted ~9-10 duty lines for 20+ CN lines
    logi = sum(v for _, v in logistics) + duty
    cont = sum(l['eur'] * (0.15 if l['group'] == 'LOCAL' else CONT[l['status']]) for l in lines) + 0.10 * logi
    return dict(parts=round(parts, 2), logistics=round(logi, 2), duty=round(duty, 2), contingency=round(cont, 2), all_in=round(parts + logi + cont, 2), lines=len(lines))


if __name__ == '__main__':
    T = totals(L, LOGISTICS)
    by_area = {}; by_func = {}
    for l in L:
        by_area[l['area']] = round(by_area.get(l['area'], 0) + l['eur'], 2); by_func[l['function']] = round(by_func.get(l['function'], 0) + l['eur'], 2)
    owed = {k: sum(o[i] for o in REVG_OWED) for k, i in (('low', 1), ('mid', 2), ('high', 3))}
    revg_done = {k: round(REVG['all_in'] + v * 1.10, 0) for k, v in owed.items()}        # owed parts + 10 % contingency, logistics unchanged
    cond = sum(c[1] for c in CONDITIONAL)
    lean_all_in = round(T['all_in'] - cond * 1.10, 0)
    stages = {}; run = 0.0
    for name, funcs in STAGES.items():
        p = sum(l['eur'] for l in L if l['function'] in funcs); run += p
        stages[name] = dict(parts=round(p), cumulative_parts=round(run))
    carried = sum(1 for l in L if l['status'].startswith('G4'));
    summary = dict(rev_h=T, rev_h_by_area=by_area, rev_h_by_function=by_func, rev_g_published=REVG, rev_g_owed=REVG_OWED, rev_g_owed_totals=owed,
                   rev_g_completed_all_in=revg_done, rev_h_conditional=CONDITIONAL, rev_h_conditional_total=cond, rev_h_lean_all_in=lean_all_in,
                   upside_risk=UPSIDE_RISK, stages=stages, revg_deleted=REVG_DELETED, revg_deleted_total=round(sum(d[2] for d in REVG_DELETED), 2),
                   lines_carried_from_revg=carried, lines_new_or_changed=len(L) - carried,
                   target_1200_gap=round(T['all_in'] - 1200), date='2026-11-11')
    with open(os.path.join(OUT, 'bom_revH.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['id', 'area', 'item', 'eur', 'status', 'order_group', 'function', 'rev_g_line', 'note'])
        for l in L: w.writerow([l['id'], l['area'], l['item'], '%.2f' % l['eur'], l['status'], l['group'], l['function'], l['revg_line'], l['note']])
        for k, v in LOGISTICS: w.writerow([k, 'Logistics', 'shipping', '%.2f' % v, 'est', '', '', '', ''])
        w.writerow(['DUTY', 'Logistics', 'EUR 3 customs duty per non-EU line (half of the CN lines assumed to combine)', '%.2f' % T['duty'], 'est', '', '', '', ''])
        w.writerow(['', '', 'TOTAL parts', '%.2f' % T['parts']]); w.writerow(['', '', 'TOTAL incl. shipping + duty', '%.2f' % (T['parts'] + T['logistics'])])
        w.writerow(['', '', 'Risk-weighted contingency', '%.2f' % T['contingency']]); w.writerow(['', '', 'ALL-IN', '%.2f' % T['all_in']])
    json.dump(dict(lines=L, logistics=LOGISTICS, summary=summary), open(os.path.join(OUT, 'bom_revH.json'), 'w'), indent=1)
    print('Rev H:', T)
    print('by area', by_area); print('by function', by_func)
    print('Rev G published', REVG['all_in'], '| owed', owed, '| completed', revg_done)
    print('conditional savings', cond, '-> lean all-in', lean_all_in)
    print('stages', stages); print('deleted Rev G lines', summary['revg_deleted_total'], '| carried lines', carried, 'new/changed', len(L) - carried)
    print('gap to 1200:', summary['target_1200_gap'])
