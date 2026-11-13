#!/usr/bin/env python3
"""B2-F cost review, 13 Nov 2026. Reads the other agent's BOM lines (extracted from BinRobo_B2F_BOM_2026-11-12.xlsx into JSON),
reproduces their totals, then applies the review's proposed changes with their own contingency rule.
Usage: python3 -I cost_b2f_lean.py <b2f_bom_lines.json>"""
import json, sys, csv
L = json.load(open(sys.argv[1]))
LOGI = {'Lines - donor chair': 254.99, 'Lines - new drive': 331.99}; PUB = {'Lines - donor chair': (3209.29, 379.95, 3844.23), 'Lines - new drive': (3417.26, 363.07, 4112.32)}
RATE = dict(est_cn=0.12, est_local=0.15, verified=0.05)
# id -> (new EUR or None to delete, class, what, evidence needed)
FIRM = {
 'GR-07': (None, 'dead part', 'Tow-hitch cam gearmotor (pawl lift). The keeper it drives is inactive in B2-F', 'none'),
 'K2': (None, 'dead part', 'Second latch switch for the two tow hooks. B2-F has no hooks', 'none'),
 'HX-G6': (66.45, 'sourcing', 'Harness: the 13-core and 7-core trailer cables crossed the old tug-to-trailer joint. One rigid frame can use ordinary multicore (about EUR 15 for the same runs)', 'wiring table redrawn'),
 'FAB-B2': (234.12, 'pricing basis', 'Frame line copied from Rev G8 (FAB-D8), which includes a EUR 120 press-brake set-up. B2-F is described as tube plus flat laser-cut plates. The EUR 25 chair-frame clamp plates may also go (not counted)', 'confirm no folded parts; local quote'),
 'G25': (81.90, 'sourcing', 'LTE Cat-1 HAT (Waveshare A7670E, about US$30) in place of the Cat-4 SIM7600G-H (about EUR 77 of this line). Antenna and sun shield kept. GNSS on the modem is not used (RTK receiver present)', 'bench test B12: alerts, clip upload, audio at both ends of the lane'),
}
GATED = {
 'B2-PADACT': (None, 'simplification', 'Pad toggle actuator. On the front wall the pad is never in the way of the bin, so it need not retract. Rev H2 passed G1 89/90 and G6 18/18 in their gate with a fixed pad', 'G1 and G6 on B2-F with the pad fixed'),
 'B2-TOGGLE': (None, 'simplification', 'Knee toggle links, pins, stop block', 'as above'),
 'B1-PADLS': (None, 'simplification', 'Pad position / lock switch', 'as above'),
 'B-1': (25.0, 'simplification', 'Roller carriage (8 bearings + 4 side rollers) on the mast uprights in place of two HGR15 profile rails. Also removes the 10 mm backing flats that S12 asks for under the rail screws', 'bench test B8 (binding under load); gate unaffected'),
}
NEW_ONLY = {  # new-drive variant: AGM instead of the LiFePO4 pack, heater and LFP charger
 'G14': (95.0, 'sourcing', '2 x 12 V 18-22 Ah AGM in place of 8 x EVE C40 + BMS. Charges below 0 C, no heater, about 7 kg heavier (replaces the 5 kg ballast)', 'energy check: 3 trips = about 135 Wh of about 215 Wh usable cold'),
 'HTR-L8': (None, 'sourcing', 'Pack heater not needed with AGM', 'as above'),
 'D6': (25.0, 'sourcing', '24 V AGM charger in place of the 8S LiFePO4 charger', 'as above'),
}
ADD = [('RK-1', 'Structure', 'Castor rocker: castor cross-beam on a centre pivot (M16 shoulder bolt, 2 bushes) with +/-25 mm bump stops, so all four wheels keep their load on twisted ground', 20.0, 0.15)]
out = {}; rows = []
for name, lines in L.items():
    key = 'donor' if 'donor' in name else 'new'
    parts = sum(r['eur'] for r in lines); cont = sum(r['eur'] * r['cont'] for r in lines); logi = LOGI[name]
    contL = cont + 0.10 * logi                                    # their rule: 10 % on logistics
    rep = dict(parts=round(parts, 2), contingency=round(contL, 2), all_in=round(parts + logi + contL, 2), published=PUB[name])
    def apply(ch, base):
        p, c = base
        for r in lines:
            if r['id'] in ch:
                new = ch[r['id']][0] or 0.0; p += new - r['eur']; c += (new - r['eur']) * r['cont']
        return p, c
    chg_new = NEW_ONLY if key == 'new' else {}
    p1, c1 = apply(FIRM, (parts, cont)); p1 += sum(a[3] for a in ADD); c1 += sum(a[3] * a[4] for a in ADD)
    p2, c2 = apply(GATED, (p1, c1)); p3, c3 = apply(chg_new, (p2, c2))
    tot = lambda p, c: round(p + logi + c + 0.10 * logi, 2)
    out[key] = dict(reproduced=rep, firm=dict(parts=round(p1, 2), all_in=tot(p1, c1)), firm_plus_gated=dict(parts=round(p2, 2), all_in=tot(p2, c2)),
                    plus_agm=dict(parts=round(p3, 2), all_in=tot(p3, c3)) if key == 'new' else None, s12_pending_all_in_add=132.25)
    if key == 'donor':
        for grp, ch in (('firm', FIRM), ('needs gate or bench', GATED)):
            for r in lines:
                if r['id'] in ch:
                    new, cls, what, ev = ch[r['id']]; rows.append([grp, r['id'], r['area'], r['eur'], new or 0.0, round((new or 0.0) - r['eur'], 2), cls, what, ev])
        for a in ADD: rows.append(['firm', a[0], a[1], 0.0, a[3], a[3], 'added', a[2], 'lane physics P2, P7 re-run'])
    else:
        for r in lines:
            if r['id'] in NEW_ONLY:
                new, cls, what, ev = NEW_ONLY[r['id']]; rows.append(['new-drive variant only', r['id'], r['area'], r['eur'], new or 0.0, round((new or 0.0) - r['eur'], 2), cls, what, ev])
json.dump(out, open('cost_b2f_lean.json', 'w'), indent=1)
with open('cost_b2f_lean_changes.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['group', 'line', 'area', 'eur_now', 'eur_proposed', 'change_eur', 'kind', 'what', 'evidence_needed']); w.writerows(rows)
for k, v in out.items(): print(k, json.dumps(v))
print(sum(r[5] for r in rows if r[0] == 'firm'), sum(r[5] for r in rows if r[0].startswith('needs')), sum(r[5] for r in rows if r[0].startswith('new')))
