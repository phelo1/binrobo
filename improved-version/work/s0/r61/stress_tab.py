#!/usr/bin/env python3
"""People stress tests of revision 6: one row per case and speed set. For every run the trace gives the nearest approach of a person or
animal to the robot's outline and what the robot was doing at that moment.
usage: stress_tab.py <out json> <prefix:label> [<prefix:label> ...]      e.g. r6s:slow r6f:fast"""
import json, glob, math, os, sys
CASES = [('asis', 'Walker stops in the path 10 m ahead, then a dog crosses (scenario as written)'),
         ('near35', "Walks out of the far hedge and stops in the robot's path; nose 2.0 m from their line when they set off"),
         ('near31', "Walks out of the far hedge and stops in the robot's path; nose 1.6 m from their line when they set off"),
         ('near26', "Walks out of the far hedge and stops in the robot's path; nose 1.0 m from their line when they set off (the reviewers' contact case)"),
         ('near20', "Walks out of the far hedge and stops in the robot's path; nose 0.4 m from their line when they set off"),
         ('child35', 'Small child (0.3 m wide), nose 2.0 m from their line'),
         ('run40', 'Child running across at 2.5 m/s, nose 2.5 m from their line'),
         ('run26', 'Child running across at 2.5 m/s, nose 1.0 m from their line'),
         ('run20', 'Child running across at 2.5 m/s, nose 0.4 m from their line'),
         ('nearhedge45', 'Steps out of the NEAR hedge into the path, 3.2 m ahead of the nose'),
         ('nearhedge30', 'Steps out of the near hedge into the path, 1.7 m ahead of the nose'),
         ('gapwalk26', 'Walks out of a 4 m gateway in the far hedge; nose 1.0 m from their line'),
         ('gaprun26', 'Child runs out of the same gateway at 2.5 m/s; nose 1.0 m from their line'),
         ('behind', "Walker comes from behind at 1.6 m/s and passes the robot's side"),
         ('side', "Walks up from the far hedge and stands about 0.45 m from the robot's side for 30 s; they set off when the robot is 3.0 m from their line"),
         ('side14', "Walks from the far hedge straight at the robot's side: they set off when the robot is already beside them (1.4 m from their line)"),
         ('flank', 'Walker comes up the lane towards the robot, stops beside or just behind it for 30 s, walks on'),
         ('hug', 'Walker comes up the lane towards the robot, 0.35 m from the far hedge, and walks past it'),
         ('hugstand', 'Walker comes up the lane 0.35 m from the far hedge and stops there for 30 s: 3 m behind the robot at the start settings, 9 m behind it with the fast cruise'),
         ('hugstand31', 'Walker comes up the lane 0.35 m from the far hedge and stops there, beside the robot, for 30 s (stopping point set for the fast cruise)'),
         ('slowwalk', 'Walks ahead of the robot in its path at 0.3 m/s'),
         ('low40', 'Scenario as written, camera finds a person in only 40 % of pictures'),
         ('low40near', 'Nose 2.0 m from their line, camera at 40 %'),
         ('stay1000', 'Walker stands in the path for 1,000 s'),
         ('boxfar', "Unmapped 0.4 m box on the far side of the lane, 1.5 m clear of the robot's path"),
         ('boxpath', "Unmapped 0.4 m box in a bend, 0.2 m clear of the robot's left side"),
         ('boxside', "Unmapped 0.4 m box in a bend, at the right edge of the robot's path")]
X0, X1, HW = -0.397, 1.335, 0.465
def rdist(bx, by): return math.hypot(max(X0 - bx, bx - X1, 0.0), max(abs(by) - HW, 0.0))
def one(d):
    r = json.load(open(os.path.join(d, 'result.json'))); m = r['metrics']; out = dict(seed=r['seed'], result=r['result'], outcome=r['outcome'], contacts=len(r['collisions']), alerts=r['alerts'], hedge=r['hedge_min_m'],
        pauses=[dict(by=p.get('by', 'cam'), range=p['range'], wait=p.get('wait_s'), person=p.get('person'), static=p.get('passed_static')) for p in m.get('ppl_pauses', [])], min_s=round(r['sim_time_s'] / 60.0, 1))
    t = json.load(open(os.path.join(d, 'trace.json')))['trace']; best = None; still_since = None
    for q in t:
        if abs(q['v']) < 0.01 and abs(q['w']) < 0.02: still_since = q['t'] if still_since is None else still_since
        else: still_since = None
        for mv in q['mv']:
            dx, dy = mv[0] - q['x'], mv[1] - q['y']; c, s = math.cos(q['yaw']), math.sin(q['yaw']); bx = dx * c + dy * s; by = -dx * s + dy * c
            rr = mv[2] if len(mv) > 2 and isinstance(mv[2], (int, float)) else 0.25
            g = rdist(bx, by) - rr
            if best is None or g < best['gap']: best = dict(gap=round(g, 2), t=q['t'], v=round(q['v'], 3), w=round(q['w'], 3), still_for=(round(q['t'] - still_since, 1) if still_since is not None else 0.0), side=('front' if bx > X1 - 0.05 else ('rear' if bx < X0 + 0.05 else 'flank')))
    out['near'] = best; out['vmax'] = round(max(abs(q['v']) for q in t), 2)
    if r['collisions']:      # robot speed at the first touch, and the speed it was doing when the person or animal first appeared
        tc = r['collisions'][0]['t']; qc = min(t, key=lambda q: abs(q['t'] - tc)); out['touch'] = dict(t=tc, v=round(abs(qc['v']), 3), what=r['collisions'][0].get('what'))
    ap = next((q for q in t if q['mv']), None); out['v_appear'] = round(abs(ap['v']), 2) if ap else None
    out['v_in'] = [p.get('v_in') for p in m.get('ppl_pauses', [])]
    return out
rows = []
for arg in sys.argv[2:]:
    pf, lab = arg.split(':')
    for key, what in CASES:
        runs = [one(d) for d in sorted(glob.glob('/home/claude/sitl_out/%s_%s/runs/*' % (pf, key))) if os.path.exists(os.path.join(d, 'result.json'))]
        if runs: rows.append(dict(set=lab, case=key, what=what, runs=runs))
json.dump(rows, open(sys.argv[1], 'w'), indent=1)
for r in rows:
    nb = [q['near'] for q in r['runs'] if q['near']]
    moving = sum(1 for q in r['runs'] if q['contacts'] > 0); gaps = [n['gap'] for n in nb]
    print('%-5s %-12s runs %d | touches %d at %s m/s | v when they appear %s | nearest %s m | robot speed then %s | still for %s s | results %s | pauses %s' % (r['set'], r['case'], len(r['runs']), moving, [q['touch']['v'] for q in r['runs'] if q.get('touch')], [q.get('v_appear') for q in r['runs']],
          ('%.2f..%.2f' % (min(gaps), max(gaps))) if gaps else '-', [n['v'] for n in nb], [n['still_for'] for n in nb], sorted(set(q['outcome'][:18] for q in r['runs'])), [len(q['pauses']) for q in r['runs']]))
