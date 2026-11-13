#!/usr/bin/env python3
"""Bin Tug Rev H2 parts list, costed on the SAME function and safety basis the other agent used for B2 and for its
re-costing of Rev H: the G8 cost-down lines (revG/bom_revG8*.csv, 11 Nov 2026) for safety, navigation, sensing, comms,
wiring, lights and dock, copied unchanged into ../data/g8_baseline_lines.json. EUR incl. 23 % Irish VAT. Estimates, not quotes.
Writes ../results/bom_revH2_donor.csv, bom_revH2_new.csv and bom_revH2.json.

Price status and contingency follow the project rule (bom_revG8.py): checked = retailer page read (5 %), excerpt = seen in a
search result only (8 %), est = estimate (12 %), LOCAL fabrication or used parts (15 %), logistics 10 %.
'excerpt-12Nov' = seen in the 12 Nov 2026 research report (docs/RESEARCH_2026-11-12.md), page not opened by me."""
import csv, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'results'); os.makedirs(OUT, exist_ok=True)
G8 = json.load(open(os.path.join(HERE, '..', 'data', 'g8_baseline_lines.json')))


def L(id_, area, item, eur, status, origin, src, note=''):
    return dict(id=id_, area=area, item=item, eur=float(eur), status=status, origin=origin, source=src, note=note)


OWN = [
    # ---- Structure: bolted frame, one tube size, flat laser plates only (no press-brake work)
    L('H2-S1', 'Structure', 'Steel stock: 2 x 6 m 50x50x3 S235 RHS (2 rails, 2 cross-members, 2 mast uprights, top tie, carriage) + 2 m 30x30x2 braces + flat bar', 110, 'est', 'LOCAL', 'H2',
      'Cut list in results/cut_list_revH2.csv (about 8.3 m of 50x50x3).'),
    L('H2-S2', 'Structure', 'One laser order, about 16 flat plates, 4-8 mm S355: comb plate, carriage cheeks, motor plates, mast gussets, caster outriggers, actuator lugs, pad bracket, battery trays', 90, 'est', 'LOCAL', 'H2',
      'Scaled from the other agent\'s G6 fabrication model (EUR 97 for 18 plates). No folded parts, so its EUR 120 press-brake set-up does not apply.'),
    L('H2-S3', 'Structure', 'Zinc-rich coating (Zinga) and topcoat', 52.50, 'est', 'LOCAL', 'G8 FAB-D8 component', 'Same figure the other agent uses.'),
    L('H2-S4', 'Structure', 'Carriage rollers: 8 x 6202-2RS on shoulder bolts + 4 side guide rollers', 18, 'est', 'CN', 'H2', 'Replaces B2\'s 2 x HGR15 rails + 4 blocks (EUR 90). Rollers on painted tube tolerate dirt and rust; profile rails need a flat machined seat.'),
    L('H2-S5', 'Structure', 'Motor, battery and deck covers: HDPE / ply offcuts', 15, 'est', 'LOCAL', 'H2'),
    L('H2-S6', 'Structure', 'Nose castors: 2 x 260 mm swivel, at least 100 kg each', 60, 'est', 'IE', 'H2', 'B2 prices 2 x 200 mm at the same EUR 60. Not priced by the research; get a quote.'),
    L('G12', 'Structure', 'Anti-tip wheels under the rail tips (cheap PU)', 15, 'est', 'LOCAL', 'G8 line G12'),
    L('H2-S7', 'Structure', 'UHMW guide strips on the inner rails, 2 x 600x40x10', 12, 'est', 'CN', 'H2'),
    # ---- Bin handling
    L('H2-L1', 'Bin handling', 'Lift actuator 24 V, 4,000 N, 400 mm stroke, IP65, limit switches (QC/FDI series, the unit the other agent priced) + clevis fittings', 164.37, 'checked-11Nov', 'LT', 'B2 line B-0',
      'One actuator. The B2 list also carries Rev G\'s mast actuator ACT-L8 at the same price - see the note in the summary.'),
    L('H2-L2', 'Bin handling', '640 mm self-aligning comb (yaw +/-4 deg, roll +/-3 deg): 6 mm S355 plate + pivot block, 2 bushes, 2 centring springs, stops', 45, 'est', 'LOCAL', 'B2 line B2-COMB'),
    L('H2-L3', 'Bin handling', 'Fixed rest pad 400 x 120 mm, 12 mm rubber on UHMW, slotted bracket (+/-25 mm depth)', 12, 'est', 'LOCAL', 'H2',
      'Replaces B2\'s sprung pad (EUR 35), toggle (EUR 12), pad actuator (EUR 59.99) and pad switch (EUR 8).'),
    L('H2-L4', 'Bin handling', '4 x IP67 roller-lever switches: 2 comb-seat (in the stop loop), 2 squaring on the carriage face', 25.16, 'excerpt', 'DE', 'G4 price'),
    L('H2-L5', 'Bin handling', '2 x comb ToF sensors (lip height and docking yaw, VL53L1X class, potted)', 20, 'est', 'CN', 'B2 lines B-4 + B1-TOF2'),
    L('H2-L6', 'Bin handling', '2 x rail-tip gap ToF sensors', 12, 'est', 'CN', 'B2 line (Sensing B2)'),
    L('H2-L8', 'Bin handling', '2 x bin-wheel clearance sensors (ToF, VL53L1X class, potted) on the inner rail faces at the bin-wheel station, 45 mm above the ground', 12, 'est', 'CN', 'H2',
      'Firmware FH2: the bin is claimed only when both sensors read clear. A mast camera cannot see the bin wheels once the bin is docked.'),
    L('K5', 'Bin handling', 'Actuator current sensor INA219 (bin weight, stall, not collected)', 3, 'est', 'CN', 'G8 line K5'),
    L('H2-L7', 'Bin handling', 'Rubber buffer under the comb pivot + carriage bump stops', 6, 'est', 'CN', 'H2', 'Softens the step peaks that reach the 3 kN model cap in the other agent\'s MuJoCo runs.'),
]
DRIVE_DONOR = [dict(l, source='G8 Lean-D', note=l.get('why', '')[:160]) for l in G8['donor_drive_power']] + [
    L('H2-D1', 'Drive', 'Pneumatic block-tread 13x5.00-6 wheels or tyres x2, if the donor has solid or worn tyres', 35, 'excerpt-12Nov', 'GB', 'research', 'GBP 14.49 each seen on eBay UK. Decide after the kerb test T5.'),
    L('G5b', 'Drive', 'Tyre sealant (Slime 473 ml)', 17.50, 'checked-6Nov', 'IE', 'G4 line'),
]
DRIVE_NEW = [
    L('DRV-M8', 'Drive', 'Gearmotor pair PEWM82M-320W, 24 V, 32:1, electromagnetic brake with hand release', 315.22, 'checked-11Nov', 'CN', 'B2 line'),
    L('DRV-W8', 'Drive', 'Drive wheels + 3.5:1 chain stage per side (330 mm wheel, sprockets, chain, guard)', 130, 'est', 'IE', 'B2 line'),
    L('CTL-L8', 'Drive', 'Motor controller Basicmicro RoboClaw 2x30A', 148.44, 'checked-11Nov', 'EU', 'B2 line'),
    L('G9', 'Drive', 'Wheel encoders x2', 18, 'checked-6Nov', 'CN', 'B2 line'),
    L('G14', 'Power', 'Battery 24 V 20 Ah LiFePO4: 8 x EVE C40 + Daly 8S 60 A BMS with low-temperature charge cut-off', 139.75, 'checked-10Nov', 'NL', 'B2 line'),
    L('G15', 'Power', 'Battery hatch hasp + padlock', 7, 'est', 'IE', 'B2 line'),
    L('G16', 'Power', 'Reverse-polarity protection, Anderson SB50 pair, charge fuse, TVS', 24, 'checked-10Nov+est', 'CN', 'B2 line'),
    L('HTR-L8', 'Power', 'Pack heater 2 x 24 V silicone pads + cut-out', 24, 'excerpt', 'CN', 'B2 line'),
    L('D6', 'Dock', 'Charger 29.2 V 5 A for 8S LiFePO4', 29, 'checked-6Nov', 'FR', 'B2 line'),
]
SHARED = [dict(l, source='G8 Lean-D', note=l.get('why', '')[:160]) for l in G8['shared_donor']]
LOG_DONOR = {l['id']: l['eur'] for l in G8['logistics_donor']}                       # EUR 217 incl. EUR 40 to collect the donor
LOG_NEW = {'SHIP-PEI': 110.0, 'DUTY': 63.0, 'SHIP-LT': 20.0, 'SHIP-DE': 18.0, 'SHIP-EU': 15.0, 'SHIP-NL': 15.0, 'SHIP-EU2': 15.0, 'SHIP-GB': 15.0, 'SHIP-LOCAL': 15.0,
           'SHIP-CN': 8.0, 'SHIP-FR': 10.0, 'SHIP-IE': 8.0}                          # B2's logistics lines without the Conrad parcel (EUR 19.99): EUR 312

# Savings that keep every function. Each waits on the test named; none is in the totals.
SAVINGS = [
    ('Generic 3 kN / 400 mm IP65 actuator instead of the 4 kN unit', 115, 'T2: cold force and holding test; step peaks measured on the built robot (the model caps at 3 kN)', 'B2 lists the same option at EUR 80-110'),
    ('H2 harness: one rigid body, one electronics box, no cable across a hitch (replaces the Rev G 13-core trailer harness HX-G6)', 61, 'Harness redrawn for H2 and reviewed against ELEC_SAFETY_G7', 'applies to B2 too'),
    ('LTE Cat-1 modem (Waveshare A7670E class) instead of the SIM7600G-H Cat-4 HAT', 60, 'Bench check: alerts, photo upload and two-way audio over Cat-1 at the dock and at the road end', 'research: US$29.99 against GBP 86.99'),
    ('Cytron MDDS30 instead of the RoboClaw 2x30A', 72, 'Only if motor over-current protection is moved to fuses and firmware, and encoders are read by the flight controller', 'changes the protection method - owner decision'),
]
# Items the research report rates as optional for a private one-off (docs/RESEARCH_2026-11-12.md Q6). Listed, NOT taken: they are safety items.
SAFETY_OPTIONAL = [('Second series contactor (KM2)', 28.66), ('Independent speed / standstill monitor (SLS-L8 + SPD-S8)', 40.0)]
B2 = dict(new=dict(parts=3558.41, logistics=331.99, contingency=369.43, all_in=4259.83), donor=dict(all_in=3992.0),
          duplicate_actuator=dict(id='ACT-L8', eur=164.37, note='B2\'s list keeps Rev G\'s mast actuator ACT-L8 (EUR 164.37) from the G8 lines and adds the concept-B lifter B-0 at the same price; '
                                  'B2 has one lift actuator. b2/bom_b2.py B_REMOVE does not list ACT-L8. Removing it with its 5 % contingency takes about EUR 173 off both B2 totals. To be confirmed by its authors.'))
REVH_CLAIM = dict(all_in=1990.13, rebased_by_other_agent=3154.5,
                  note='My Rev H figure of EUR 1,990 was built on the older G4 list. The other agent is right that it left out the G7/G8 safety, wiring and comms additions.')


def cont_rate(l):
    st = l['status'].split('+')[-1] if '+' in l['status'] else l['status']
    if l['origin'] == 'LOCAL' or l['id'] in ('SR-L8', 'DNR-D8'): return 0.15
    if st.startswith('checked'): return 0.05
    if st.startswith('excerpt'): return 0.08
    return 0.12


def totals(lines, log):
    parts = sum(l['eur'] for l in lines); lg = sum(log.values()); cont = sum(l['eur'] * cont_rate(l) for l in lines) + 0.10 * lg
    by = {}
    for l in lines: by[l['area']] = round(by.get(l['area'], 0) + l['eur'], 2)
    chk = sum(l['eur'] for l in lines if l['status'].startswith('checked'))
    return dict(parts=round(parts, 2), logistics=round(lg, 2), contingency=round(cont, 2), all_in=round(parts + lg + cont, 2), lines=len(lines), by_area=by,
                price_checked_share_pct=round(100 * chk / parts))


def write(name, lines, log, t):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['id', 'area', 'item', 'eur', 'price_status', 'origin', 'source', 'contingency_rate', 'note'])
        for l in lines: w.writerow([l['id'], l['area'], l['item'], '%.2f' % l['eur'], l['status'], l['origin'], l['source'], cont_rate(l), l.get('note', '')])
        for k, v in log.items(): w.writerow([k, 'Logistics', 'shipping / duty / collection', '%.2f' % v, 'est', '', 'G8', 0.10, ''])
        for k in ('parts', 'logistics', 'contingency', 'all_in'): w.writerow(['TOTAL', '', k, '%.2f' % t[k]])


if __name__ == '__main__':
    donor = OWN + DRIVE_DONOR + SHARED
    new = OWN + DRIVE_NEW + SHARED
    td = totals(donor, LOG_DONOR); tn = totals(new, LOG_NEW)
    write('bom_revH2_donor.csv', donor, LOG_DONOR, td); write('bom_revH2_new.csv', new, LOG_NEW, tn)
    sav = sum(s[1] for s in SAVINGS); sav_all = round(sav * 1.10)
    b2fix = round(B2['duplicate_actuator']['eur'] * 1.05, 2)
    summary = dict(date='2026-11-12', basis='G8 Lean-D function and safety lines (other agent), unchanged', h2_donor=td, h2_new=tn,
                   h2_donor_with_gated_savings=round(td['all_in'] - sav_all), h2_new_with_gated_savings=round(tn['all_in'] - sav_all), gated_savings=SAVINGS, gated_savings_parts=sav,
                   safety_items_rated_optional_by_research_not_taken=SAFETY_OPTIONAL, b2_published=B2,
                   b2_without_duplicate_actuator=dict(new=round(B2['new']['all_in'] - b2fix, 2), donor=round(B2['donor']['all_in'] - b2fix, 2)),
                   revh_claim=REVH_CLAIM, target_2000_gap_donor=round(td['all_in'] - 2000), donor_price_sensitivity='each EUR 100 on the donor adds EUR 115 all-in; research saw complete chairs at EUR 600-1,250 asking in Ireland and motor-gearbox pairs from GBP 135 on eBay UK',
                   h2_vs_b2=dict(donor_vs_published=round(B2['donor']['all_in'] - td['all_in']), new_vs_published=round(B2['new']['all_in'] - tn['all_in']),
                                 donor_vs_corrected=round(B2['donor']['all_in'] - b2fix - td['all_in']), new_vs_corrected=round(B2['new']['all_in'] - b2fix - tn['all_in'])))
    json.dump(dict(summary=summary, lines_donor=donor, lines_new=new, logistics_donor=LOG_DONOR, logistics_new=LOG_NEW), open(os.path.join(OUT, 'bom_revH2.json'), 'w'), indent=1)
    print('H2 donor', {k: v for k, v in td.items() if k != 'by_area'}); print(td['by_area'])
    print('H2 new  ', {k: v for k, v in tn.items() if k != 'by_area'}); print(tn['by_area'])
    print('gated savings', sav, '->', summary['h2_donor_with_gated_savings'], summary['h2_new_with_gated_savings'])
    print('B2 corrected', summary['b2_without_duplicate_actuator'], 'H2 vs B2', summary['h2_vs_b2'])
