#!/usr/bin/env python3
# Stop tests at higher speeds (24 Nov): emergency stop (brakes on 0.15 s after the trigger), re-geared drive (wheel torque caps scaled 2:3.5).
# usage: pstop_tab_r6.py <result dir> <out json>
import json, glob, os, sys
rows = []
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*pstop*_r6.json'))):
    r = json.load(open(f))
    rows.append(dict(t_react=r.get('t_react', 0.15), bin_kg=r['bin_kg'], slope_pct=round(-100 * r['grade'], 1), grip=r['mu'], v=r['v_cmd'], v_at_touch=r.get('v_at_touch'), stop_m=r['travel_after_touch_m'], braking_m=r.get('braking_m'),
                     time_s=r.get('time_to_stop_s'), slide_m=r.get('slide_after_stop_m'), captured=r.get('captured_end')))
rows.sort(key=lambda r: (r['grip'], -r['bin_kg'], r['slope_pct'], r['v']))
json.dump(rows, open(sys.argv[2], 'w'), indent=1)
slow = [r for r in rows if abs(r['t_react'] - 0.15) > 1e-6]; rows = [r for r in rows if abs(r['t_react'] - 0.15) <= 1e-6]
for grip in sorted(set(r['grip'] for r in rows), reverse=True):
    for kg in (110.0, 0.0):
        sub = [r for r in rows if r['grip'] == grip and r['bin_kg'] == kg]
        if not sub: continue
        vs = sorted(set(r['v'] for r in sub)); print('\ngrip %.2f, %s: stop distance m (trigger to standstill) by slope and speed' % (grip, 'full bin' if kg else 'empty'))
        print('slope %  ' + '  '.join('%5.2f' % v for v in vs))
        for sl in sorted(set(r['slope_pct'] for r in sub)):
            d = {r['v']: r for r in sub if r['slope_pct'] == sl}
            print('%6.1f   ' % sl + '  '.join(('%5.2f%s' % (d[v]['stop_m'], '*' if (d[v]['time_s'] or 0) >= 7.9 else ' ')) if v in d else '   -  ' for v in vs))
print('\n* = not stopped within 8 s (sliding)')

if slow:
    print('\nlonger reaction time (brakes on 0.20 s after the touch), wet leaves, level:')
    for r in slow: print('  %s, %.2f m/s: %.3f m' % ('full bin' if r['bin_kg'] else 'empty', r['v'], r['stop_m']))
