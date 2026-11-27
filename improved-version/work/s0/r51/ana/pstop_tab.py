#!/usr/bin/env python3
# Tabulates the stop tests on the real slopes (22 Nov). Usage: pstop_tab.py <result dir> <out json>
# Each test: the robot drives down a slope at a set speed, the soft nose touches a person, the brakes come on 0.15 s later.
import json, glob, os, sys
rows = []
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*pstop*_r51.json'))):
    r = json.load(open(f))
    rows.append(dict(bin_kg=r['bin_kg'], slope_pct=round(-100 * r['grade'], 1), grip=r['mu'], v=r['v_cmd'], v_at_touch=r.get('v_at_touch'),
                     stop_mm=round(1000 * r['travel_after_touch_m']), slide_mm=round(1000 * (r.get('slide_after_stop_m') or 0)), time_to_stop_s=r.get('time_to_stop_s')))
rows.sort(key=lambda r: (-r['bin_kg'], -r['slope_pct'], -r['grip'], -r['v']))
json.dump(rows, open(sys.argv[2], 'w'), indent=1)
print('bin kg | slope % | grip | speed m/s | stop mm | slide after stop mm | inside 130 mm')
for r in rows: print('%5.0f | %4.1f | %.2f | %.2f | %4d | %d | %s' % (r['bin_kg'], r['slope_pct'], r['grip'], r['v'], r['stop_mm'], r['slide_mm'], 'yes' if r['stop_mm'] <= 130 else 'NO'))
