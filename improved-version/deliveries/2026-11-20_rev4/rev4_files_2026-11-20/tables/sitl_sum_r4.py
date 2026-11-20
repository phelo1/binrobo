#!/usr/bin/env python3
"""Compact summary of a driving-software run set. usage: sitl_sum_r4.py <out_name> [...]"""
import json, glob, sys, statistics as st
for name in sys.argv[1:]:
    R = {f.split('/')[-2]: json.load(open(f)) for f in sorted(glob.glob('/home/claude/sitl_out/%s/runs/*/result.json' % name))}
    T = [t for d in R.values() for t in d['metrics'].get('trips', []) if 'wh' in t]; P = [p for d in R.values() for p in d['metrics'].get('placements', [])]
    G = [g for d in R.values() for g in d['metrics'].get('gates', [])]; SC = [s for d in R.values() for s in d['metrics'].get('seat_checks', [])]
    RF = [(k, r) for k, d in R.items() for r in d['metrics'].get('refused', [])]; CC = [c for d in R.values() for c in d['metrics'].get('cam_checks', [])]
    print('== %s: %d runs; results: %s' % (name, len(R), {o: sum(1 for d in R.values() if d.get('outcome') == o) for o in sorted({d.get('outcome') for d in R.values()})}))
    if T: print('   trips %d: Wh %.1f..%.1f (mean %.1f); minutes %.1f..%.1f (mean %.1f)' % (len(T), min(t['wh'] for t in T), max(t['wh'] for t in T), st.mean(t['wh'] for t in T), min(t['min'] for t in T), max(t['min'] for t in T), st.mean(t['min'] for t in T)))
    if P: print('   placements %d: error mm max %.0f mean %.0f; handle angle max %.1f deg' % (len(P), max(p['err_m'] for p in P) * 1000, st.mean(p['err_m'] for p in P) * 1000, max(abs(p['handle_err_deg']) for p in P)))
    if G:
        k = list(G[0].keys()); print('   gate records %d, keys %s' % (len(G), k))
        if 'ok_cam' in G[0]: print('   gate: camera OK %d, truth OK %d; camera OK but truth outside %d; camera refused but truth inside %d' % (sum(g['ok_cam'] for g in G), sum(g['ok'] for g in G), sum(1 for g in G if g['ok_cam'] and not g['ok']), sum(1 for g in G if not g['ok_cam'] and g['ok'])))
        print('   gate worst true lateral %.0f mm, worst true yaw %.2f deg' % (max(abs(g.get('lat_m', 0)) for g in G) * 1000, max(abs(g.get('yaw_deg', g.get('yaw', 0))) for g in G)))
    if SC: print('   seating checks %d: ok %d; worst measured %.1f mm, worst true %.1f mm; worst sensor error %.1f mm' % (len(SC), sum(s['ok'] for s in SC), max(abs(s['meas_mm']) for s in SC), max(abs(s['true_mm']) for s in SC), max(abs(s['meas_mm'] - s['true_mm']) for s in SC)))
    print('   refused:', RF); print('   camera checks %d' % len(CC))
    ends = [(k, d['metrics'].get('last_dock_clock')) for k, d in R.items() if len(d['metrics'].get('trips', [])) >= 2]; print('   multi-trip runs, last time on the dock:', ends)
    soc = [d.get('end_soc', d['metrics'].get('end_soc')) for d in R.values()]; 
    h = [d['metrics'].get('hedge_min', d.get('hedge_min')) for d in R.values()]; print('   keys of result:', [k for k in list(R.values())[0].keys()][:14])
