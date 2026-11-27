#!/usr/bin/env python3
"""Revision 6 (24 Nov): texts and tables for sheets 17 and 18. Numbers come from r6/tables (stop tests at speed, stress tests, trips)."""
import json
F = json.load(open('/home/claude/s0/r51/facts_r51.json')); T = '/home/claude/s0/r6/tables/'
ps = json.load(open(T + 'pstop_speed_r6.json')); SR = json.load(open(T + 'stress_rows_r6.json')); rows = SR['rows']; tr = json.load(open(T + 'trips_r6.json')); kb = json.load(open(T + 'kerb_r6.json'))
def stop(kg, sl, mu, v):
    q = [r['stop_m'] for r in ps if abs(r['bin_kg'] - kg) < 1 and abs(r['slope_pct'] - sl) < 0.05 and abs(r['grip'] - mu) < 0.005 and abs(r['v'] - v) < 0.005]
    assert q, (kg, sl, mu, v); return q[0]
def trip(lab, kind):
    q = [o['min'] for o in tr if o['set'] == lab and o['kind'] == kind]; return (min(q), max(q))
F6 = json.load(open(T + 'pivot_r6.json'))
F['speed_rule'] = [['level or uphill', '0.4 m/s', '0.4 m/s', '1.0 m/s', '1.0 m/s'], ['downhill, up to 3 %', '0.4 m/s', '0.3 m/s', '1.0 m/s', '0.8 m/s'],
                   ['downhill, 3 to 6 %', '0.3 m/s', '0.2 m/s', '0.8 m/s', '0.6 m/s'], ['downhill, steeper than 6 %', '0.2 m/s', '0.15 m/s', '0.6 m/s', '0.4 m/s']]
d5, p5 = trip('rev 5.1', 'drop'), trip('rev 5.1', 'pickup'); d6, p6 = trip('fast', 'drop'), trip('fast', 'pickup')
F['speed_notes'] = [
 'Emergency stop from the fast cruise (brakes on 0.15 s after the trigger, simulated): on the level from 1.0 m/s, %.2f m with a full bin and %.2f m empty on a wet surface; %.2f and %.2f m on wet leaves. On an 8.5 %% slope: %.2f m (full bin, 0.6 m/s) and %.2f m (empty, 0.4 m/s) wet; %.2f and %.2f m on wet leaves.'
   % (stop(110, 0, 0.30, 1.0), stop(0, 0, 0.30, 1.0), stop(110, 0, 0.22, 1.0), stop(0, 0, 0.22, 1.0), stop(110, 8.5, 0.30, 0.6), stop(0, 8.5, 0.30, 0.4), stop(110, 8.5, 0.22, 0.6), stop(0, 8.5, 0.22, 0.4)),
 'So at the fast cruise a touch on the nose is a push of 0.3 to 0.7 m, not a stop inside the foam. The robot may only be that fast when its sensors show the lane clear (sheet 18), and the hardware speed watchdog can only hold the fast limit.',
 'Why 1.0 m/s and not more: the 2:1 chain stage gives about 1.2 m/s flat out (motor 4,600 rpm, 32:1 gearbox, 330 mm wheel) and leaves torque for the hill with a full bin at 1.0 m/s (motor curve ASSUMED). A 40 mm kerb at 1.0 m/s loads the drive wheel with %s N (4,886 N at 0.8 m/s, so the frame factors of revision 5 stand) and the lift with %s N (actuator holding factor %.2f); at 1.2 m/s that factor falls to %.2f.'
   % ('{:,}'.format(kb['wheel_10']), '{:,}'.format(kb['lift_10']), 8800.0 / kb['lift_10'], 8800.0 / kb['lift_12']),
 'Trip time in the mission simulation: %.0f to %.0f minutes for a drop-off and %.0f to %.0f for a pick-up (revision 5.1: %.0f to %.0f and %.0f to %.0f).' % (d6[0], d6[1], p6[0], p6[1], d5[0], d5[1], p5[0], p5[1]),
 'Leaf season (leaves lying on the lane, or October to December): touch-safe 0.35 m/s on the level; fast cruise 1.0, 0.8, 0.6 and 0.5 m/s with a full bin and 1.0, 0.8, 0.5 and 0.15 m/s empty, by slope band. On wet leaves the empty robot holds only to about 9 %%: on a 10 %% slope it slides %.1f m from 0.4 m/s. No empty run down the hill on leaves until the hill has been surveyed.' % stop(0, 10, 0.22, 0.4),
 'With the new chain stage the firmware speed and turn loops must be reset (values in the test pack): the same commands now turn the wheels 1.55 times faster. With them a turn on the spot peaks at %s rad/s, nose corner %s m/s.' % (F6['piv_rate'], F6['piv_corner']),
 'The 150 mm of give in the foam and the 0.15 s are assumptions. Measure the stops on the built robot before it runs unattended.']
F['people_rules'] = [
 '1. Lane watch. The three lidars look at the whole width of the lane, all round the robot. A return is hedge if it lies on the hedge face fitted from the scan itself (a face must be long, so a person or a box cannot pass for one), or is joined to it; under a good satellite fix the map gives a second opinion. Anything else is an object, wherever it is. The map and the position are not needed to find it.',
 '2. Near zone. An object within 3 m of the robot\'s outline, in any direction: stop and stand still. Standing still means the firmware holds the drive at zero; the wheels do not twitch.',
 '3. Camera. One sighting of a person or an animal ends the fast cruise. Two in a row within 5 m, with a lidar object at the same place, or within 2.5 m without one: stand still.',
 '4. Restart only when every sensor has shown the zones empty for 3 s, and the first 3 m at 0.2 m/s. After 2 minutes the owner gets a message. After 15 minutes of standing in any 20, the robot holds and raises an alert.',
 '5. Things, not people. A thing may be passed at 0.2 m/s only if the front camera has had it in view and never called it a person, it has not moved for 20 s and it is 0.5 m clear of the path. Anything that turns up beside or behind the robot is waited for like a person. A thing in the path for 2 minutes: path-blocked alert. Once a camera has called something a person it stays one.',
 '6. Fast cruise (sheet 17) only with nothing in the lane within 4 m ahead at 0.4 m/s, growing to 10 m at 1.0 m/s; no camera sighting; both hedge faces in view and no gap in either within 5.5 m ahead (a gateway); a good fix (0.7 m/s under a degraded one); not in the yard or within 20 m of the road.',
 '7. Protective field. Anything at all, hedge included, in the robot\'s own path up to 0.6 m ahead of the nose (1.4 m at 1.0 m/s): stop, back out 0.8 m, start again. Three times in two minutes: hold and call the owner.',
 '8. Turning on the spot: not with anything unknown within 1.75 m of the axle (the circle the nose sweeps), nor with a person or anything moving within 3 m. The robot looks for a full second before a turn and five times a second during it; outside the yard anything that turns up inside 3 m counts as moving. It then stops turning and stands still. The same rule holds while it waits before setting a bin down. The sweep check allows for 20 degrees of overshoot. Reverse moves at 0.1 m/s. Keeping left as before, %.2f m from the hedge.' % F['kl_gap'],
 '9. Last line: the switch strips on the soft nose open the stop chain. Up to the touch-safe speed the robot then stops inside the foam.']
F['tests_head'] = 'Tested cases'
F['tests_intro'] = 'Mission simulation, a loaded robot in the lane at night, three seeds each. "Nose 1.0 m from their line": the person sets off from the hedge when the nose is that far from where they will cross; they walk on without looking. Touch = any contact while the robot is still moving. Camera: a person found in 60 % of pictures. The full table is in the reply note.'
short = {'Walker stops in the path 10 m ahead, then a dog crosses (scenario as written)': 'Walker stops in the path 10 m ahead; a dog crosses'}
SHEET = ['near26', 'near20', 'child35', 'run26', 'run20', 'nearhedge30', 'gapwalk26', 'gaprun26', 'behind', 'side', 'flank', 'stay1000', 'boxfar']
short.update({'The same; nose 1.0 m from their line (the reviewers\' contact case)': 'Walks out of the far hedge into the path; nose 1.0 m from their line (the reviewers\' case)', 'The same; nose 0.4 m from their line': 'Walks out of the far hedge into the path; nose 0.4 m from their line'})
def cut(t):
    t = t.replace('no touch while moving: they walked up to the robot, which had stood still for', 'no touch; they reached the robot after it had stood for').replace('TOUCHED', 'TOUCH')
    return t
F['tests_rows'] = [[short.get(a, a), cut(b), cut(c)] for k in SHEET for a, b, c, key in rows if key == k]
F['people_notes'] = [
 'What it still cannot do. The robot needs up to 0.7 s to be sure of someone who steps out of the hedge, and about a second more to stop from 1.0 m/s. Someone who steps out less than about 1 m in front of the nose at the fast cruise is met by a robot that is still braking: with every run at the full 1.0 m/s, a walker 0.4 m in front of the nose was touched at up to 0.33 m/s and a running child at up to 0.86 m/s; from 1.0 m the robot stopped 0.09 to 0.18 m short. Someone standing against the hedge (within 0.3 to 0.5 m of it) is taken for hedge until they step out; the protective field covers the robot\'s own path. Things lower than 0.30 m are below the lidars: only the camera, then the nose strip.',
 'Every detection figure is assumed: lidar 10 scans a second with 10 mm noise, a person modelled as a 0.5 m disc (a small child 0.3 m); camera 5 pictures a second, 60 % at night. The first job on the built robot is to measure them (reply note, section 7).']
json.dump(F, open('/home/claude/s0/r6/facts_r6.json', 'w'), indent=1); print('facts written;', len(F['tests_rows']), 'test rows')
