#!/usr/bin/env python3
# Tabulates the pause-when-anyone-is-near tests (22 Nov). Usage: person_tab.py <sitl_out dir> <out json>
import json, glob, os, sys
root, out = sys.argv[1], sys.argv[2]
sets = [('r51_final_s5a', 'scenario as written, under the revision 5.1 speed rule'), ('r51_s5a', 'scenario as written: a walker comes up the lane, then a dog crosses (night rate 0.60)'),
        ('r51_person60', 'the walker stops and stands in the lane for 60 s'),
        ('r51_person60near', 'the walker steps out 3.5 m in front of the robot and stands 60 s (night rate 0.60)'),
        ('r51_person60near_day', 'same, daylight detection rate 0.85'),
        ('r51_person200', 'the walker stands in the lane for 200 s (owner message at 120 s)')]
rows = []
for d, what in sets:
    for f in sorted(glob.glob(os.path.join(root, d, 'runs', '*', 'result.json'))):
        r = json.load(open(f)); m = r.get('metrics', {}); pp = m.get('ppl_pauses', [])
        rows.append(dict(test=d, what=what, seed=r.get('seed'), result=r.get('result'), outcome=r.get('outcome'),
                         closest_person_m=r.get('person_rest_min_m'), contact_min_m=r.get('contact_min_m'), contact_with=r.get('contact_with'),
                         collisions=r.get('collisions'), hedge_min_m=r.get('hedge_min_m'), alerts=r.get('alerts'),
                         pauses=[dict(first_seen_at_m=round(p.get('range', 0), 2), waited_s=round(p.get('wait_s', 0), 1), station_m=round(p.get('s', 0))) for p in pp],
                         sim_time_s=r.get('sim_time_s'), energy_wh=r.get('energy_wh')))
json.dump(rows, open(out, 'w'), indent=1)
for r in rows:
    print(r['test'], r['seed'], r['result'], '| closest person', r['closest_person_m'], '| contact_min', r['contact_min_m'], r['contact_with'],
          '| coll', r['collisions'], '| alerts', len(r['alerts'] or []), '| pauses', [(p['first_seen_at_m'], p['waited_s']) for p in r['pauses']])
