#!/usr/bin/env python3
"""Lane-physics runs on the lane without the assumed 12 % pitch (22 Nov). Usage: python3 -I lane_tab.py <b2f_lanephys dir> <out json>
Dirs: runs_r51_real* = revision 5 speed rule (0.3 m/s with a bin, 0.2 m/s empty on slopes over 6 %); runs_r51_v51_* = revision 5.1 rule
(0.2 / 0.15 m/s). Suffix: none or m35 = the other agent's leaf-zone grip 0.35, w30 = 0.30 (wet), w22 = 0.22 (wet leaves).
For comparison the revision 5 runs on the 12 % pitch (runs_r5_pf, runs_r5_w30, runs_r5_w22) are listed where they exist.
The run titles inside the result files still say '12 % pitch': that is the test's name; the slope each one met is in the column."""
import json, os, sys
LP, out = sys.argv[1], sys.argv[2]
SETS = [('runs_r5_pf', '12 % pitch (rev 5)', 'rev 5', 0.35), ('runs_r5_w30', '12 % pitch (rev 5)', 'rev 5', 0.30), ('runs_r5_w22', '12 % pitch (rev 5)', 'rev 5', 0.22),
        ('runs_r51_real', 'real slope', 'rev 5', 0.35), ('runs_r51_real_w30', 'real slope', 'rev 5', 0.30), ('runs_r51_real_w22', 'real slope', 'rev 5', 0.22),
        ('runs_r51_v51_m35', 'real slope', 'rev 5.1', 0.35), ('runs_r51_v51_w30', 'real slope', 'rev 5.1', 0.30), ('runs_r51_v51_w22', 'real slope', 'rev 5.1', 0.22)]
RUNS = ['P1', 'P7', 'P2a_pf', 'P4a', 'P4b', 'P6a_person_estop', 'X8n', 'X9n', 'X8t', 'X9t']
rows = []
for d, lane, rule, grip in SETS:
    for run in RUNS:
        f = os.path.join(LP, d, run, 'result.json')
        if not os.path.exists(f): continue
        if d.startswith('runs_r51_v51') and run in ('P1', 'P2a_pf'): continue      # copies of the runs_r51_real runs (start snapshots only)
        if d in ('runs_r51_real_w30', 'runs_r51_real_w22') and run == 'P2a_pf': continue
        r = json.load(open(f)); m = r['metrics']; res = r['results']
        hold = next((v for k, v in res.items() if k.startswith('hold')), None); es = res.get('estop')
        ev = [e[1] for e in r.get('events', []) if 'stop' in str(e[1])]
        rows.append(dict(set=d, lane=lane, speed_rule=rule, leaf_zone_grip=grip, run=run, verdict=r['verdict'], fails=r['fails'], v_max=round(m['v_max'], 3), pitch_max_deg=round(m['pitch_max'], 2),
                         gap_to_person_m=(round(m['gap_min'], 3) if m['gap_min'] < 8.9 else None), hold_slope_pct=(hold or {}).get('grade_pct'), hold_creep_10s_mm=(round(1000 * hold['creepT_m'], 1) if hold else None),
                         estop_m=(round(es['stop_m'], 3) if es else None), energy_Wh=r['energy_Wh'], stop_event=(ev[0] if ev else None)))
json.dump(rows, open(out, 'w'), indent=1)
print('%-20s %-18s %-8s %-5s %-17s %-5s %-6s %-7s %-10s %-10s %s' % ('set', 'lane', 'rule', 'grip', 'run', 'verd', 'v_max', 'gap m', 'hold slope', 'creep mm', 'fails / stop'))
for r in rows:
    print('%-20s %-18s %-8s %-5.2f %-17s %-5s %-6.2f %-7s %-10s %-10s %s' % (r['set'], r['lane'], r['speed_rule'], r['leaf_zone_grip'], r['run'], r['verdict'], r['v_max'], r['gap_to_person_m'], r['hold_slope_pct'], r['hold_creep_10s_mm'], (r['fails'] or r['stop_event'] or '')))
