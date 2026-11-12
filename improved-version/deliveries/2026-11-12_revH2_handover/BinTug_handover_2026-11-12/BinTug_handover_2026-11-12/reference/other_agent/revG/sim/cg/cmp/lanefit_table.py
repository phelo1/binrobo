#!/usr/bin/env python3
"""Lane-fit tables for COMPARE_B1_vs_RevH from res/lanefit_B1.json and res/lanefit_RevH.json -> res/lanefit_table.md"""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); R = {n: json.load(open(os.path.join(H, 'res', 'lanefit_%s.json' % n))) for n in ('B1', 'RevH')}
o = []; P = o.append
def mn(d, key): return min(v[0] for k, v in d.items() if key(k))
P('| lane-fit item (strict: any footprint point past a truth hedge face = FAIL) | B1 | Rev H |'); P('|---|---|---|')
P('| overall width (m) | %.2f | %.2f |' % (2 * R['B1']['half_w'], 2 * R['RevH']['half_w']))
P('| 180 deg pivot diameter, empty / loaded (m) | %.2f / %.2f (loaded = MuJoCo G5 swept) | %.2f / %.2f (geometric; MuJoCo G5 swept 2.10) |' % (R['B1']['pivot_D_empty'], R['B1']['pivot_D_load'], R['RevH']['pivot_D_empty'], R['RevH']['pivot_D_load']))
for k in ('down loaded', 'up loaded'):
    P('| lane sweep %s: least clearance to a hedge face (m), at s | %s | %s |' % (k, *['%.3f at s %.0f' % (R[n]['sweep'][k]['min_clear_m'], R[n]['sweep'][k]['at_s']) for n in ('B1', 'RevH')]))
P('| margin over the SITL lateral-estimate p95 (0.124 m) | %+.3f | %+.3f |' % (R['B1']['sweep_margin_vs_p95'], R['RevH']['sweep_margin_vs_p95']))
P('| lane stations where a loaded 180 deg pivot fits between the faces | %.0f %% | %.0f %% |' % (100 * R['B1']['lane_pivot_frac_loaded'], 100 * R['RevH']['lane_pivot_frac_loaded']))
P('| pivot at s 500-516 (2.9 m between faces): least margin (m) | %s | %s |' % tuple('%.2f' % min(m for s, m in R[n]['lane_pivot_loaded'] if 500 <= s <= 516) for n in ('B1', 'RevH')))
P('| dock: loaded 180 deg pivot within 2 m, 0-3 bins at home, margin (m) | %.2f | %.2f |' % tuple(mn(R[n]['yard_dock'], lambda k: k.startswith('dock')) for n in ('B1', 'RevH')))
P('| yard: 180 deg pivot, 0-3 bins at home, margin (m) | %.2f | %.2f |' % tuple(mn(R[n]['yard_dock'], lambda k: k.startswith('yard')) for n in ('B1', 'RevH')))
P('| bell-mouth: 180 deg pivot with 1-3 bins standing, margin (m) | %.2f | %.2f |' % tuple(mn(R[n]['mouth'], lambda k: not k.split(', ')[1].startswith('0')) for n in ('B1', 'RevH')))
P('')
P('| pad sequence (G6 pads A, M, F; drop A-M-F, pickup F-M-A) | B1 result, least margin (m) | Rev H result, least margin (m) |'); P('|---|---|---|')
for k in R['B1']['sequences']:
    cells = []
    for n in ('B1', 'RevH'):
        v = R[n]['sequences'][k]; ms = [s[1] for s in v['steps'] if s[1] is not None]; worst = min(ms) if ms else None
        wl = [s[0] for s in v['steps'] if s[1] == worst][0] if ms else ''
        cells.append('%s, %.3f (%s)' % ('PASS' if v['ok'] else 'FAIL', worst, wl.split(' (')[0]))
    P('| %s | %s | %s |' % (k.replace('handle-to-', 'handles to the '), *cells))
open(os.path.join(H, 'res', 'lanefit_table.md'), 'w').write('\n'.join(o) + '\n'); print('\n'.join(o))
