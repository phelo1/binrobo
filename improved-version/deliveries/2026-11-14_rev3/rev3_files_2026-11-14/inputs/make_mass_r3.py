#!/usr/bin/env python3
"""Revision 3 weight table, rebuilt row by row (14 Nov 2026).
Starts from the revision 2 corrected table (mass_cgB2_r2b.json) and applies, as separate labelled rows:
  A. what the independent audit of 14 Nov found missing (their central figures unless I have a better one),
  B. the structural changes of revision 3,
  C. the other design changes of revision 3.
usage: make_mass_r3.py <out.json> [--rail 100x50x4|120x40x3|50x50x4] [--xm 80x80x3|50x50x2] [--ballast KG] [--label TEXT]"""
import json, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--rail', default='50x50x4'); ap.add_argument('--xm', default='50x50x4'); ap.add_argument('--nose', default='50x50x3'); ap.add_argument('--car', type=float, default=22.25); ap.add_argument('--batt-dx', type=float, default=0.0)
ap.add_argument('--ballast', type=float, default=0.0); ap.add_argument('--label', default='improved version, revision 3'); A = ap.parse_args()
KGM = {'50x50x2': 2.93, '50x50x3': 4.25, '50x50x4': 5.45, '80x40x4': 6.71, '100x50x3': 6.60, '100x50x4': 8.59, '120x40x3': 7.07, '120x60x3': 8.01, '80x80x3': 7.07, '80x80x4': 9.22, '80x80x5': 11.3, '60x60x3': 5.19, '40x40x2': 2.31, '40x40x3': 3.30}
M = json.load(open('/home/claude/b2f_review/variants/mass_cgB2_r2b.json')); rows = M['rows']
def find(s):
    r = [x for x in rows if x['name'].startswith(s)]; assert len(r) == 1, (s, len(r)); return r[0]
def add(name, kg, p, d, g='chassis'): rows.append(dict(name=name, kg=round(kg, 3), p=list(p), d=list(d), g=g))
# ---- B. structure
L_RAIL, L_X = 1.35, 0.86
for s_ in ('L', 'R'):
    r = find('Side rail %s' % s_); r['name'] = 'Side rail %s %s RHS S355 %.2f m (rev 3)' % (s_, A.rail, L_RAIL); r['kg'] = round(KGM[A.rail] * L_RAIL, 2)
    h = int(A.rail.split('x')[0]) / 1000.0; r['p'][2] = 0.41 - h / 2; r['d'] = [L_RAIL, int(A.rail.split('x')[1]) / 1000.0, h]
r = find('Mast-base cross-member'); r['name'] = 'Mast-base cross-member %s SHS S355 %.2f m (rev 3)' % (A.xm, L_X); r['kg'] = round(KGM[A.xm] * L_X, 2)
r = find('Nose cross-member'); r['name'] = 'Nose cross-member %s %.2f m, at rail height (rev 3)' % (A.nose, L_X); r['kg'] = round(KGM[A.nose] * L_X, 2)
r = find('Mast uprights'); r['name'] = 'Mast uprights 2 x 80x40x4 RHS 0.95 m, standing on the foot shoes (rev 3)'; r['kg'] = round(2 * 6.71 * 0.95, 2)
r = find('Mast foot plates'); r['name'] = 'Mast foot shoes 2: 10 mm S355 top plate 100 x 90 + 10 mm front leg + 2 gussets 6 mm, welded to the upright, bolted M12 through the cross-member (rev 3)'; r['kg'] = 2.50
r = find('Linear rails'); r['name'] = 'Linear rails 2 x 1.0 m HGR15 (2.90) + 4 blocks HGH15CA (0.72) + backing flats 2 x 30x10 x 0.94 m (4.43)'; r['kg'] = 8.05
r = find('Castor-beam pivot'); r['name'] = 'Castor-beam pivot: hanger plates 2 x 10 mm S355 90 x 240 welded to both faces of the nose cross-member (3.39) + D20 pin (0.22) + bronze bushes (0.10) (rev 3)'; r['kg'] = 3.71
r = find('Mast gussets'); r['name'] = 'Rail-tail caps + 4 corner gussets at the cross-member joints (the mast gussets are now part of the foot shoes, the actuator lugs part of the base bracket)'; r['kg'] = 0.50
add('Actuator base bracket: 10 mm S355 plate with two gussets, bolted to the mast-base cross-member (rev 3; audit +1.18 kg)', 1.60, (0.555, 0, 0.36), (0.09, 0.12, 0.09))
# ---- A. audit items not covered above
add('Fasteners, whole robot (BOM line F1; audit central 2.0 kg)', 2.00, (0.49, 0, 0.385), (0.9, 0.8, 0.4))
add('Lift cable chain with end brackets (L7)', 0.25, (0.44, 0.17, 1.0), (0.05, 0.05, 0.4))
add('Lift driver with current limit, in the power box', 0.20, (0.69, 0.26, 0.19), (0.08, 0.06, 0.04))
add('Two safety contactors, if not inside the "as B1" lumps (audit 0 to 1.2 kg, central)', 0.60, (0.69, 0.26, 0.19), (0.1, 0.1, 0.08))
add('Safety additions: second tilt switch, down limit switch wiring, pre-charge resistor and relay, regeneration diode, larger safety controller', 0.30, (0.69, 0.2, 0.2), (0.1, 0.1, 0.08))
add('Weld metal and paint allowance (about 1 % of the fabricated steel)', 0.60, (0.45, 0, 0.5), (0.9, 0.8, 0.6))
# ---- C. other design changes of revision 3
r = find('Lift hard stops'); r['name'] = 'Lift top end: 2 bolted stop blocks (2 x M8 each) + 2 limit switches on brackets + striker; bottom stop blocks 2 (rev 3)'; r['kg'] = 1.70
r = find('Bumper brackets'); r['name'] = 'Bumper carrier: 2 arms 40x40x2 with drop legs (1.57) + carrier tube 25x25x2 0.40 m (0.56) + 2 flange plates (0.40) + 2 sprung guides, 4 switches (0.70) (rev 3)'; r['kg'] = 3.20; r['p'] = [1.06, 0, 0.3]
if A.batt_dx:
    r = find('Battery 24 V'); r['p'][0] = round(r['p'][0] + A.batt_dx, 3); r['name'] += ' moved %+.0f mm' % (A.batt_dx * 1000)
r = find('Ballast')
if A.ballast <= 0: rows.remove(r)
else: r['kg'] = A.ballast; r['name'] = 'Ballast: %.1f kg steel plate on the nose cross-member / bay floor' % A.ballast
# carriage: comb, nib, pad arm, fixed pad, 8 mm 700 mm comb plate; keeper deleted (-0.2); carriage plate 80 mm deeper (audit central +2.3 kg, steel)
car = M['carriage'][0]; car['kg'] = round(A.car - 0.6, 2); car['p'] = [0.40, 0, 0.74]   # the simulator reads carriage[0] only, so everything on the carriage goes in this one row
car['name'] = 'Lift carriage, counted part by part (rev 3): carriage plate 16 mm aluminium 460 x 275 (5.4), UHMW face plate (0.76), actuator bracket 10 mm S355 (0.9), comb pivot block (1.73), comb plate 700 x 122 x 8 S355 (5.36), nib (0.88), pad arm RHS 80x40x3 0.57 m (2.96), pad guide block aluminium (1.8), pad face, rods, cup plate, 2 long springs (1.71), switches and sensors (0.15), fasteners (0.4), loom (0.2). The simulator adds 0.6 kg for the comb body, taken off here.'
assert all(x.get('g') in ('chassis', 'wheel', 'cast') for x in rows), 'a row outside the groups the simulator reads'
M['car_total'] = round(car['kg'] + 0.6, 2); M['rocker_kg'] = round(M['rocker_kg'] + 0.25, 2)
M['total'] = round(sum(x['kg'] for x in rows) + M['car_total'] + M['rocker_kg'], 2); M['label'] = A.label
M['note'] = 'Rebuilt 14 Nov from the revision 2 corrected table: audit items, structural changes and design changes each in their own row. total = rows + carriage (incl. the 0.6 kg comb body) + castor beam.'
json.dump(M, open(A.out, 'w'), indent=1)
print(A.out, 'total', M['total'], 'rows', len(rows), 'carriage', M['car_total'], 'rocker', M['rocker_kg'], 'rail', A.rail, 'xm', A.xm, 'nose', A.nose, 'ballast', A.ballast)
