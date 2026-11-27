#!/usr/bin/env python3
"""Revision 5.1 (22 Nov): texts and tables for sheets 17 and 18, from the revision 5 facts with Brian's answers applied
(real lane slope, pause for anyone within 5 m, no tail-first). Numbers come from r51/tables/*.json."""
import json
F = json.load(open('/home/claude/s0/r5/facts.json')); T = '/home/claude/s0/r51/tables/'
ps = json.load(open(T + 'pstop_real_slope_r51.json')); mc = json.load(open(T + 'people_mc_r51.json'))['rows']; pp = json.load(open(T + 'person_pause_r51.json'))
def stop(kg, sl, mu, v): return [r['stop_mm'] for r in ps if abs(r['bin_kg'] - kg) < 1 and abs(abs(r['slope_pct']) - sl) < 0.05 and abs(r['grip'] - mu) < 0.005 and abs(r['v'] - v) < 0.005][0]
RULE = [(0, 0.4, 0.4), (3, 0.4, 0.3), (6, 0.3, 0.2), (8.5, 0.2, 0.15)]       # worst slope of each band, speed with a bin, speed empty
wet = [stop(k, sl, 0.30, v) for sl, vb, ve in RULE for k, v in ((110, vb), (0, ve))]; leaf = [stop(k, sl, 0.22, v) for sl, vb, ve in RULE for k, v in ((110, vb), (0, ve))]
print('wet stops', wet, 'leaf stops', leaf)
F['speed_rule'] = [['level or uphill', '0.4 m/s', '0.4 m/s'], ['downhill, up to 3 %', '0.4 m/s', '0.3 m/s'], ['downhill, 3 to 6 %', '0.3 m/s', '0.2 m/s'], ['downhill, steeper than 6 %', '0.2 m/s', '0.15 m/s']]
F['speed_notes'] = [
 'Set for this lane. In the 25 m elevation data the lane falls 13.7 m over 635 m; its one hill, about 145 m long and starting some 80 m from the house, runs at 6 to 8 %. A second, coarser model (30 m, whole metres) gives the same fall and allows up to about 10 % near the top of the hill. The 12 % pitch of revisions 1 to 5 was an assumption of the simulated lane and is removed. Neither model can show a short steeper bit: measure the hill with a level before the first run.',
 'Longest simulated stop under this rule on a wet surface (grip 0.30): %d mm (empty, level, 0.4 m/s). On an 8.5 %% slope: %d mm with a full bin, %d mm empty.' % (max(wet), stop(110, 8.5, 0.30, 0.2), stop(0, 8.5, 0.30, 0.15)),
 'On wet leaves (grip 0.22): %d mm with a full bin and %d mm empty on the 8.5 %% slope. At 0.4 m/s on the level and on a 3 %% slope it is %d to %d mm: past the 130 mm line, inside the 150 mm of foam.' % (stop(110, 8.5, 0.22, 0.2), stop(0, 8.5, 0.22, 0.15), min(stop(0, 0, 0.22, 0.4), stop(110, 3, 0.22, 0.4)), max(stop(0, 0, 0.22, 0.4), stop(110, 3, 0.22, 0.4))),
 'Tail-first driving is dropped: the empty robot comes down the hill nose first at 0.15 m/s. On a wet surface that works up to 10 %% at least (%d mm). On wet leaves it works up to 8.5 %% only, because just the two drive wheels brake: at 9 %% the stop is %d mm and at 10 %% the robot slides %.1f m. If any part of the hill is steeper than 8.5 %% and collects wet leaves, tail first is needed there after all.' % (stop(0, 10, 0.30, 0.15), stop(0, 9, 0.22, 0.15), stop(0, 10, 0.22, 0.15) / 1000.0),
 'The 150 mm of give in the foam and the 0.15 s are assumptions. Measure the stop on the built robot before it runs unattended.']
def rng(test, key, sub=None):
    v = [r[key] if sub is None else r['pauses'][0][sub] for r in pp if r['test'] in (test if isinstance(test, tuple) else (test,))]; return min(v), max(v)
w0 = rng(('r51_s5a', 'r51_final_s5a'), None, 'waited_s'); c0 = rng(('r51_s5a', 'r51_final_s5a'), 'contact_min_m')
dog = [r['pauses'][1]['waited_s'] for r in pp if len(r['pauses']) > 1]
n1 = rng('r51_person60near', None, 'first_seen_at_m'); n2 = rng('r51_person60near', 'closest_person_m'); d1 = rng('r51_person60near_day', None, 'first_seen_at_m'); d2 = rng('r51_person60near_day', 'closest_person_m')
w60 = rng('r51_person60', None, 'waited_s'); w200 = rng('r51_person200', None, 'waited_s')
print('pause as written', w0, c0, 'dog', min(dog), max(dog), 'near night', n1, n2, 'near day', d1, d2, 'w60', w60, 'w200', w200, 'runs', len(pp))
F['people_rules'] = [
 '1. Pause for people (new in 5.1): when the front camera has found a person or an animal within 5 m in two pictures in a row, the robot stops and stands still. It moves on by itself once nobody has been within 5.5 m for 3 s. After 2 minutes it messages the owner and keeps waiting; after 15 minutes it holds and raises an alert. The rule runs in the lane, on the yard paths and before every pivot turn.',
 '2. Forward, by lidar: an unknown object in the robot\'s path inside 4 m: slow to 0.25 m/s. Inside 1.5 m: stop and wait; move on when the path has been clear for 3 s. The camera adds a stop for a person or dog within 0.5 m of the robot\'s sides, whatever the map says.',
 '3. Protective field: anything at all, hedge included, inside the robot\'s own path up to 0.6 m ahead of the nose or within 80 mm of its sides: stop, back out 0.8 m, start again from the lane edges. Three times in two minutes: hold and call the owner. It does not use the map or the satellite position.',
 F['people_rules'][2].replace('3. Keeping left', '4. Keeping left'), F['people_rules'][3].replace('4. Turning', '5. Turning'),
 '6. Reverse moves: 0.1 m/s, watched by the rear lidar and the rear camera.',
 '7. Lowering the bin: see sheet 17.', F['people_rules'][6].replace('7. Last line', '8. Last line'), F['people_rules'][7].replace('8. Self-check', '9. Self-check')]
F['people_rows'] = [[r['name'], '%.2f' % r['both']['d999'], '%.2f' % r['lidar']['d999'], '%.2f' % r['cam_day']['d999'], '%.2f' % r['cam_night']['d999']] for r in mc]
F['people_notes'] = [
 F['people_notes'][0],
 'Rule 1 in the mission simulation, %d runs. A walker in the lane, then a dog crossing: the robot stood still %.0f to %.0f s for the walker and %.0f to %.0f s for the dog, and neither came nearer than %.1f m. A walker who stands for 60 s or 200 s: it waits and then goes on by itself. Someone who steps out 3.5 m ahead: found at %.1f to %.1f m at the night rate (%.1f to %.1f m by day); the robot stopped %.2f to %.2f m short of them (%.2f to %.2f m by day).'
   % (len(pp), w0[0], w0[1], min(dog), max(dog), c0[0], n1[0], n1[1], d1[0], d1[1], n2[0], n2[1], d2[0], d2[1]),
 'The table is for someone who appears closer than the camera can react to. Inside these distances the soft nose touches them at a speed at which the robot stops inside the foam (sheet 17).',
 'At night the camera works by its own infra-red light and the lidar needs no light. How well a real detector finds a child, a dog or someone in dark clothes at night is the main thing to test on the built robot.',
 'In the mission software and tested: rules 1 to 5 and the 0.1 m/s reverse. Not yet: the rear sensors (so rule 1 does not yet see someone walking up from behind) and rule 9. No part here is certified; by the owner\'s decision of 22 November the functions are proved by his own tests (reply note, section 6).']
json.dump(F, open('/home/claude/s0/r51/facts_r51.json', 'w'), indent=1)
