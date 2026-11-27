#!/usr/bin/env python3
"""Revision 3 weight table built from the drawn solids (14 Nov 2026).
Every fabricated part: volume of its solid in the drawing model x density (steel 7.85, aluminium 2.70, UHMW/HDPE 0.95, rubber 1.1 g/cm3).
Bought-in units: the B2-F author's own figures ("as B1" rows of their table) or a catalogue figure, each marked. Then fasteners, wiring and allowances.
usage: mass_from_solids.py <solids.json> <r2b mass json> <out mass json> <out table.md>"""
import json, sys
solids, r2b, outj, outmd = sys.argv[1:5]
S = json.load(open(solids)); B = json.load(open(r2b)); RHO = dict(steel=7.85, alu=2.70, uhmw=0.95, hdpe=0.95, rubber=1.10)
# robot frame of the mass table: origin on the ground under the axle centre, metres (same as the drawing model for the fixed parts)
# (name prefix, where, kind, value)   where: chassis | rocker | car | skip ; kind: a material, 'fix' (kg each, catalogue or assumed) or '-' (inside a bought-in row below)
RULES = [
 ('FR Side rail', 'chassis', 'rhs', 6.71 * 1.35), ('FR Corner plate', 'chassis', 'steel', 0), ('FR Nose', 'chassis', 'rhs', 5.45 * 0.79), ('FR Mast-base', 'chassis', 'rhs', 6.56 * 0.79), ('FR Drive/motor plate', 'chassis', 'steel', 0),
 ('LM Mast upright', 'chassis', 'rhs', 6.71 * 0.96), ('LM Mast foot cleat', 'chassis', 'steel', 0), ('LM Mast strut lug', 'chassis', 'steel', 0), ('LM Mast strut foot', 'chassis', 'steel', 0), ('LM Mast strut', 'chassis', 'rhs', 1.68 * 0.52), ('LM Mast tie cleat', 'chassis', 'steel', 0), ('LM Rail backing flat', 'chassis', 'steel', 0), ('LM Mast top tie', 'chassis', 'rhs', 2.93 * 0.46), ('LM Mast foot shoe', 'chassis', 'steel', 0),
 ('LM Lift top stop', 'chassis', 'alu', 0), ('LM Lift bottom stop', 'chassis', 'alu', 0), ('LM Linear rail', 'chassis', 'fix', 1.36), ('LA Actuator base bracket', 'chassis', 'steel', 0),
 ('RK Pivot hanger plate', 'chassis', 'steel', 0), ('RK Pivot pin', 'chassis', 'steel', 0), ('SF Bumper carrier', 'chassis', 'steel', 0), ('SF Safety bumper', 'chassis', 'fix', 3.5), ('SF Under-bin light beam', 'chassis', 'fix', 0.06), ('CH Cable chain anchor', 'chassis', 'steel', 0),
 ('AT Anti-tip bracket', 'chassis', 'fix', 0.38), ('AT Anti-tip roller', 'chassis', 'rubber', 0), ('GU UHMW guard', 'chassis', 'uhmw', 0), ('GU Mouth flare', 'chassis', 'uhmw', 0), ('BY HDPE', 'chassis', 'hdpe', 0),
 ('SW Lift', 'chassis', 'fix', 0.10),
 ('RK Castor cross-beam pivot housing', 'rocker', 'steel', 0), ('RK Castor cross-beam', 'rocker', 'rhs', 3.77 * 0.72), ('RK Castor mounting plate', 'rocker', 'steel', 0), ('RK Bump stop', 'rocker', 'rubber', 0),
 ('LC Comb face plate', 'car', 'uhmw', 0), ('LC Carriage plate', 'car', 'alu', 0), ('LC Carriage cross-beam', 'car', 'rhs', 5.45 * 0.34), ('LC Rail carriage block', 'car', 'fix', 0.18), ('LC Actuator bracket', 'car', 'steel', 0), ('LC Comb pivot block', 'car', 'steel', 0),
 ('SW Comb contact', 'car', 'fix', 0.05), ('SN Comb ToF', 'car', 'fix', 0.03), ('PD Pad arm', 'car', 'rhs', 5.19 * 0.568), ('PD Pad guide block', 'car', 'alu', 0), ('CH Cable chain bracket on the carriage', 'car', 'steel', 0),
 ('LC Comb plate', 'car', 'steel', 0), ('LC Nib', 'car', 'steel', 0), ('SW Nib seat', 'car', 'fix', 0.02), ('PD Pad UHMW face', 'car', 'uhmw', 0), ('PD Pad slide rods', 'car', 'steel', 0), ('PD Pad backing plate', 'car', 'alu', 0), ('PD Pad springs', 'car', 'fix', 0.35),
 ('SW Pad contact', 'car', 'fix', 0.03), ('PD Pad spring cup plate', 'car', 'alu', 0),
 ('DR ', 'skip', '-', 0), ('CA ', 'skip', '-', 0), ('PW ', 'skip', '-', 0), ('EL ', 'skip', '-', 0), ('SF ', 'skip', '-', 0), ('DK ', 'skip', '-', 0), ('LT ', 'skip', '-', 0), ('SN ', 'skip', '-', 0), ('AU ', 'skip', '-', 0),
 ('CM ', 'skip', '-', 0), ('LA Lift actuator', 'skip', '-', 0), ('BIN', 'skip', '-', 0), ('KP ', 'skip', '-', 0)]
def rule(n):
    for r in RULES:
        if n.startswith(r[0]): return r
    raise SystemExit('no rule for ' + n)
LIFT0 = (0.415, 0.0, 0.835)     # lift frame origin in the robot frame with the comb down (m)
rows, car, rocker, skipped = [], [], [], {}
for s_ in S:
    pre, where, kind, val = rule(s_['name'])
    if where == 'skip': skipped.setdefault(pre.strip(), 0); skipped[pre.strip()] += 1; continue
    kg = val if kind in ('fix', 'rhs') else s_['vol_cm3'] * RHO[kind] / 1000.0
    bb = s_['bb']; c = [(bb[0] + bb[1]) / 2000.0, (bb[2] + bb[3]) / 2000.0, (bb[4] + bb[5]) / 2000.0]; d = [max(0.005, (bb[1] - bb[0]) / 1000.0), max(0.005, (bb[3] - bb[2]) / 1000.0), max(0.005, (bb[5] - bb[4]) / 1000.0)]
    how = 'catalogue weight per metre x length' if kind == 'rhs' else ('%.0f cm3 x %.2f' % (s_['vol_cm3'], RHO[kind])) if kind != 'fix' else 'catalogue / estimate'
    e = dict(name=s_['name'], kg=round(kg, 3), p=[round(v, 3) for v in c], d=[round(v, 3) for v in d], how=how, grp=s_['grp'])
    (rows if where == 'chassis' else car if where == 'car' else rocker).append(e)
# merge left/right and repeated solids into one line each for the printed table, keep them separate in the simulator rows
def lump(prefix): 
    r = [x for x in B['rows'] if x['name'].startswith(prefix)]; assert len(r) == 1, (prefix, len(r)); return dict(r[0])
bought = []
for pre, note in (('Drive unit L', 'B2-F author, as B1'), ('Drive unit R', 'B2-F author, as B1'), ('Castor 200 mm L', 'B2-F author'), ('Castor 200 mm R', 'B2-F author'), ('Battery 24 V', 'B2-F author'), ('Electronics pod', 'B2-F author, as B1'),
                  ('Sensors: post', 'B2-F author, as B1'), ('Bumper, lights', 'B2-F author, as B1'), ('Lift actuator', 'ASSUMED 6.5 kg for a LINAK LA36 with 350 mm stroke (their row said 3.5 kg for the old unit)'), ('Rear camera', 'B2-F author'), ('Leg-tip gap', 'B2-F author')):
    r = lump(pre); r['how'] = note; r['g'] = r.get('g', 'chassis')
    if pre == 'Lift actuator': r['kg'] = 6.5; r['p'] = [0.58, 0.0, 0.56]; r['name'] = 'Lift actuator 24 V 6.8 kN, 350 mm stroke, outdoor unit with own end stops'
    bought.append(r)
allow = [dict(name='Fasteners other than the frame joints (BOM line F1; reviewer audit: 2.0 kg)', kg=2.00, p=[0.49, 0, 0.385], d=[0.9, 0.8, 0.4], how='allowance'),
         dict(name='Bolts, nuts, washers and crush tubes of the bolted joints: 44 x M8, 16 x M10, 6 x M12, about 40 crush tubes', kg=5.00, p=[0.62, 0, 0.52], d=[0.9, 0.8, 0.6], how='counted joint by joint: M8 x 85 set 0.045 kg, M10 x 80 set 0.075 kg, M12 x 90 set 0.124 kg, crush tube 0.02 kg'),
         dict(name='Lift cable chain 0.6 m (loom L7)', kg=0.20, p=[0.44, 0.12, 1.0], d=[0.05, 0.1, 0.4], how='catalogue estimate'),
         dict(name='Power box: enclosure, 2 contactors with mirror contacts, lift driver, pre-charge relay and resistor, fuses, isolator', kg=2.20, p=[0.69, 0.265, 0.19], d=[0.16, 0.19, 0.12], how='estimate; reviewer audit: contactors 0 to 1.2 kg, driver 0.2 kg'),
         dict(name='Safety additions: safety controller with speed monitoring, bumper control unit, tilt sensor, light-beam and limit-switch wiring', kg=0.90, p=[0.64, 0, 0.2], d=[0.1, 0.1, 0.08], how='estimate'),
         dict(name='Paint (no welds)', kg=0.40, p=[0.45, 0, 0.5], d=[0.9, 0.8, 0.6], how='allowance')]
car_extra = [dict(name='Carriage fasteners', kg=0.40, how='allowance'), dict(name='Carriage loom, grommets', kg=0.20, how='estimate')]
chassis_rows = [dict(name=r['name'], kg=r['kg'], p=r['p'], d=r['d'], g='chassis') for r in rows] + [dict(name=r['name'], kg=r['kg'], p=r['p'], d=r['d'], g=r['g']) for r in bought] + [dict(name=r['name'], kg=r['kg'], p=r['p'], d=r['d'], g='chassis') for r in allow]
CAR = sum(r['kg'] for r in car) + sum(r['kg'] for r in car_extra); ROCK = sum(r['kg'] for r in rocker)
# carriage centre of mass in the robot frame (comb down): lift-frame solids are offset by the lift origin; comb and pad solids are in their own frames, placed by hand below
def car_cg():
    m = 0; mz = 0; mx = 0
    for r in car:
        if r['grp'] == 'lift': x, z = LIFT0[0] + r['p'][0], LIFT0[2] + r['p'][2]
        elif r['grp'] == 'comb': x, z = LIFT0[0] - 0.122 + r['p'][0], LIFT0[2] + r['p'][2]
        else: x, z = 0.296 + r['p'][0], 0.275 + r['p'][2]
        m += r['kg']; mx += r['kg'] * x; mz += r['kg'] * z
    return mx / m, mz / m
cx, cz = car_cg()
SIM_SMALL = 1.5     # comb 0.6 + keeper 0.2 + pad base 0.3 + pad 0.4 kg: bodies the simulator adds itself; taken off the carriage row so the built model weighs what this table says
M = dict(label='improved version, revision 4: table built from the drawn solids', rows=chassis_rows,
         carriage=[dict(name='Lift carriage, sum of its parts (see the table), less the 1.5 kg the simulator adds as separate small bodies', kg=round(CAR - SIM_SMALL, 2), p=[round(cx, 3), 0, round(cz, 3)], d=[0.15, 0.70, 0.6], g='lift')],
         rocker_kg=round(ROCK, 2), car_total=round(CAR, 2))
M['total'] = round(sum(r['kg'] for r in chassis_rows) + CAR + ROCK, 2)
M['note'] = 'total = fixed rows + carriage (%.2f kg, all of it) + castor beam (%.2f kg). The simulator builds comb, keeper, pad base and pad as separate bodies of 1.5 kg, so the carriage row carries the rest.' % (CAR, ROCK)
assert all(x['g'] in ('chassis', 'wheel', 'cast') for x in chassis_rows)
json.dump(M, open(outj, 'w'), indent=1)
L = ['# Revision 4 weight table, built from the drawn solids', '', 'Fabricated parts: solid volume in the drawing model times density. Bought-in units: the figure and its source are in the last column.', '',
     '| Part | kg | How |', '|---|---:|---|']
def emit(title, rr):
    L.append('| **%s** | **%.2f** | |' % (title, sum(r['kg'] for r in rr)))
    agg = {}
    for r in rr:
        k = r['name'].replace(' L ', ' ').replace(' R ', ' ').replace(' L:', ':').replace(' R:', ':'); k = k[3:] if k[2:3] == ' ' and k[:2].isupper() else k
        a = agg.setdefault(k, [0, 0.0, r.get('how', '')]); a[0] += 1; a[1] += r['kg']
    for k, (n, kg, how) in agg.items(): L.append('| %s%s | %.2f | %s |' % (k, ' (x%d)' % n if n > 1 else '', kg, how))
emit('Frame, mast, guards, covers: fabricated', rows); emit('Bought-in units', bought); emit('Allowances', allow); emit('Castor beam (rocks on the pivot)', rocker); emit('Lift carriage (moves with the lift)', car + car_extra)
L += ['| **Total** | **%.2f** | |' % M['total'], '', 'Drawn solids that are inside a bought-in row and not weighed separately: ' + ', '.join('%s (%d)' % kv for kv in sorted(skipped.items())) + '.']
open(outmd, 'w').write('\n'.join(L) + '\n'); print('total %.2f kg: fabricated %.2f, bought-in %.2f, allowances %.2f, castor beam %.2f, carriage %.2f (cg x %.3f z %.3f)' % (M['total'], sum(r['kg'] for r in rows), sum(r['kg'] for r in bought), sum(r['kg'] for r in allow), ROCK, CAR, cx, cz))
