#!/usr/bin/env python3
"""Lane-physics runs at the fast cruise speeds (24 Nov), beside the revision 5.1 runs at the touch-safe speeds.
usage: python3 -I lane_tab_r6.py <b2f_lanephys dir> <out json>"""
import json, os, sys
LP, out = sys.argv[1], sys.argv[2]
SETS = [('runs_r51_real', 'touch-safe (rev 5 rule)', 0.35), ('runs_r51_v51_m35', 'touch-safe (rev 5.1 rule)', 0.35), ('runs_r6_fast', 'fast cruise', 0.35), ('runs_r6_fast_w22', 'fast cruise', 0.22)]
rows = []
for d, rule, grip in SETS:
    for run in ('P1', 'P7', 'P3', 'P2a_pf', 'P2c', 'P4a', 'P4b'):
        f = os.path.join(LP, d, run, 'result.json')
        if not os.path.exists(f) or (d == 'runs_r51_v51_m35' and run in ('P1', 'P2a_pf')): continue
        r = json.load(open(f)); m = r['metrics']; hold = next((v for k, v in r['results'].items() if k.startswith('hold')), None)
        rows.append(dict(set=d, rule=rule, grip=grip, run=run, verdict=r['verdict'], fails=r['fails'], sim_s=round(r['sim_time_s'] - (r.get('t_start') or 0.0)), energy_Wh=r['energy_Wh'], v_max=round(m['v_max'], 2), seated=m.get('seated_all'),
                         clear_min_mm=(round(1000 * m['clear_min']) if m.get('clear_min', 9) < 8 else None), clear_at=m.get('clear_at'), roll_max=round(m['roll_max'], 1), pitch_max=round(m['pitch_max'], 1), hedge_min=round(m.get('hedge_min', 9), 3), tip_min=round(m.get('tip_min', 99), 1),
                         liftF_max=round(m.get('liftF_max', 0)), hold_creep_mm=(round(1000 * hold['creepT_m'], 1) if hold else None), hold_overrun_m=(hold.get('overrun_m') if hold else None)))
json.dump(rows, open(out, 'w'), indent=1)
print('%-18s %-26s %-5s %-7s %-5s %6s %6s %5s %-6s %8s %6s %6s %7s %s' % ('set', 'rule', 'grip', 'run', 'verd', 'time s', 'Wh', 'v max', 'seated', 'clear mm', 'roll', 'pitch', 'hedge m', 'hold creep mm / overrun m / fails'))
for r in rows: print('%-18s %-26s %-5.2f %-7s %-5s %6d %6.1f %5.2f %-6s %8s %6.1f %6.1f %7.3f %s %s %s' % (r['set'], r['rule'], r['grip'], r['run'], r['verdict'], r['sim_s'], r['energy_Wh'], r['v_max'], r['seated'], r['clear_min_mm'], r['roll_max'], r['pitch_max'], r['hedge_min'], r['hold_creep_mm'], r['hold_overrun_m'], r['fails'] or ''))
