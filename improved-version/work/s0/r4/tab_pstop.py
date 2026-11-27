#!/usr/bin/env python3
"""Person-stop map: travel from the bumper touch to standstill. usage: tab_pstop.py <res dir> [--json out]"""
import json, glob, sys, os
D = sys.argv[1]; R = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(D, 'B2F_Y_pstop_*.json')))]
for d in R: d['cb'] = 'X_CBRAKE' in d['env']; d['pm'] = float(d['env'].get('PERT_M', '1'))
def sel(**kw): return [d for d in R if all(d[k] == v for k, v in kw.items())]
def grid(title, rows, V=(0.15, 0.2, 0.3, 0.4, 0.5)):
    print('\n' + title); print('   slope  grip | ' + ' '.join('%5.2f' % v for v in V) + '   m/s')
    for gr in (0, -0.03, -0.06, -0.08, -0.09, -0.12):
        for mu in (0.6, 0.3, 0.22):
            r = {d['v_cmd']: d for d in rows if d['grade'] == gr and d['mu'] == mu}
            if r: print('   %4.0f %%  %.2f | ' % (-gr * 100, mu) + ' '.join(('%5.3f' % r[v]['travel_after_touch_m'] if r[v]['travel_after_touch_m'] < 5 else ' slid') if v in r else '    -' for v in V))
base = dict(t_react=0.15, rev=False, cb=False, pm=1.0)
grid('empty robot, nose first (m from touch to standstill, reaction 0.15 s)', sel(bin_kg=0.0, **base))
grid('full 240 L bin (110 kg), nose first', sel(bin_kg=110.0, **base))
grid('empty robot, tail first', sel(bin_kg=0.0, t_react=0.15, rev=True, cb=False, pm=1.0))
grid('empty robot, nose first, braked castors (30 N m each)', sel(bin_kg=0.0, t_react=0.15, rev=False, cb=True, pm=1.0))
grid('full bin, nose first, braked castors', sel(bin_kg=110.0, t_react=0.15, rev=False, cb=True, pm=1.0))
print('\nother'); 
for d in R:
    if d['pm'] != 1.0 or d['t_react'] != 0.15: print('   kg %3d v %.2f slope %4.0f %% grip %.2f react %.2f mass x%.1f: %.3f m' % (d['bin_kg'], d['v_cmd'], -d['grade'] * 100, d['mu'], d['t_react'], d['pm'], d['travel_after_touch_m']))
print('\nheld the bin in every loaded run:', all(d['captured_end'] for d in R if d['bin_kg'] > 0), ' runs:', len(R))
if '--json' in sys.argv: json.dump([{k: v for k, v in d.items() if k not in ('geo', 'env')} for d in R], open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=0)
