#!/usr/bin/env python3
"""Table of driving-software (SITL) runs: their scorer's verdict per run plus the numbers behind the weight question and the camera logic.
usage: sitl_r3_table.py <out_name> [--json out.json]   (reads /home/claude/sitl_out/<out_name>/score.json and runs/*/result.json; run b2f_score.py first)"""
import json, sys, os, glob, re
name = sys.argv[1]; base = '/home/claude/sitl_out/%s' % name; sc = {r['key']: r for r in json.load(open(os.path.join(base, 'score.json')))}; rows = []
for f in sorted(glob.glob(os.path.join(base, 'runs', '*', 'result.json'))):
    r = json.load(open(f)); key = os.path.basename(os.path.dirname(f)); m = r.get('metrics') or {}; s = sc.get(key, {})
    trips = [t['wh'] for t in m.get('trips', [])]; cc = m.get('cam_checks', []); nref = m.get('refused')
    pl = [abs(p.get('err_m', p.get('err', 0)) or 0) for p in m.get('placements', [])] if m.get('placements') else []
    fails = [c for c, v in (s.get('crit') or {}).items() if v == 'FAIL']
    rows.append(dict(key=key, verdict=s.get('verdict'), fails=fails, outcome=r['outcome'], expect=r['expect'], result=r['result'], sim_s=round(r['sim_time_s']), trips_wh=trips, max_trip=max(trips) if trips else None, soc_end=r.get('soc_end'),
                     hedge_min=r.get('hedge_min_m'), cam_checks=len(cc), cam_max_k=max([c.get('k', 0) for c in cc], default=None), refused=nref, alerts=len(r.get('alerts') or []), why_c6=(s.get('why') or {}).get('C6', '')[:90], why_c2=(s.get('why') or {}).get('C2', '')[:60]))
n = len(rows); npass = sum(1 for r in rows if r['verdict'] == 'PASS'); only_c6 = [r['key'] for r in rows if r['fails'] == ['C6']]; other = [(r['key'], r['fails']) for r in rows if r['verdict'] != 'PASS' and r['fails'] != ['C6']]
tr = [t for r in rows for t in r['trips_wh']]; hed = [r['hedge_min'] for r in rows if isinstance(r['hedge_min'], (int, float)) and r['hedge_min'] < 50]
print('%s: %d runs, %d PASS by their scorer; fail on the 50 Wh trip limit only: %d %s; fail on anything else: %s' % (name, n, npass, len(only_c6), only_c6, other or 'none'))
if tr: print('   trips: %d, largest %.2f Wh, smallest %.2f Wh; over 50 Wh: %d; over 60: %d; over 65: %d' % (len(tr), max(tr), min(tr), sum(1 for t in tr if t > 50), sum(1 for t in tr if t > 60), sum(1 for t in tr if t > 65)))
if hed: print('   least hedge clearance %.3f m' % min(hed))
print('   camera: runs with checks %d; most re-alignments in one pick-up %s; runs with a refused grab %d' % (sum(1 for r in rows if r['cam_checks']), max([r['cam_max_k'] for r in rows if r['cam_max_k'] is not None], default=None), sum(1 for r in rows if r['refused'])))
for r in rows:
    if r['trips_wh'] or r['verdict'] != 'PASS' or r['refused']: print('   %-11s %-5s %-22s trips %s  end charge %s  hedge %s  camera checks %s (max k %s)  refused %s  %s' % (r['key'], r['verdict'], r['outcome'][:22], r['trips_wh'], r['soc_end'], r['hedge_min'], r['cam_checks'], r['cam_max_k'], r['refused'], r['fails']))
if '--json' in sys.argv: json.dump(rows, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
