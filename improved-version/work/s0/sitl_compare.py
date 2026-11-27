#!/usr/bin/env python3
"""Compare SITL campaigns scored with the other agent's frozen scorer.
usage: sitl_compare.py <stored score.json> <name:out_dir> [<name:out_dir> ...]
Each out_dir holds runs/ and (after b2f_score.py) score.json. Prints one row per scenario and summary statistics."""
import json, sys, os, glob
stored = {r['key']: r for r in json.load(open(sys.argv[1]))}
camps = []
for a in sys.argv[2:]:
    n, d = a.split(':', 1)
    sc = {r['key']: r for r in json.load(open(os.path.join(d, 'score.json')))} if os.path.exists(os.path.join(d, 'score.json')) else {}
    res = {}
    for f in glob.glob(os.path.join(d, 'runs', '*', 'result.json')): res[f.split('/')[-2]] = json.load(open(f))
    camps.append((n, sc, res))
order = ['s1a', 's1b', 's3a', 's3b', 's4a', 's4b', 's4c', 's5a', 's5b', 's6a', 's6b', 's7', 's8', 's9', 's10a', 's10b', 's11a', 's11b', 's12a', 's12b']
print('%-6s | %-22s | %s' % ('scen', 'stored (4.6.2, their machine)', ' | '.join('%-26s' % c[0] for c in camps)))
tot = [0, 0]; ctot = [[0, 0] for _ in camps]
for s in order:
    row = []
    sp = [stored['%s__s%d' % (s, sd)]['verdict'] == 'PASS' for sd in (7, 11, 23)]; tot[0] += sum(sp); tot[1] += 3
    for i, (n, sc, res) in enumerate(camps):
        v = []
        for sd in (7, 11, 23):
            k = '%s__s%d' % (s, sd)
            if k in sc: v.append('P' if sc[k]['verdict'] == 'PASS' else 'F'); ctot[i][0] += sc[k]['verdict'] == 'PASS'; ctot[i][1] += 1
            else: v.append('-')
        row.append('%-26s' % ('%d/%d  %s' % (v.count('P'), 3 - v.count('-'), ''.join(v))))
    print('%-6s | %-29s | %s' % (s, '%d/3  %s' % (sum(sp), ''.join('P' if q else 'F' for q in sp)), ' | '.join(row)))
print('%-6s | %-29s | %s' % ('total', '%d/%d' % tuple(tot), ' | '.join('%-26s' % ('%d/%d' % tuple(c)) for c in ctot)))
print()
for n, sc, res in camps:
    gates = [g for r in res.values() for g in r['metrics'].get('gates', [])]
    first = [g for g in gates if g['attempt'] == 0]; miss1 = [g for g in first if not g['ok']]
    nograb = sum(1 for r in res.values() if r['outcome'] == 'grab gate')
    sd = [p for r in res.values() for p in r['metrics'].get('placements', [])]
    trips = [t for r in res.values() for t in r['metrics'].get('trips', [])]
    cams = [c for r in res.values() for c in r['metrics'].get('cam_checks', [])]
    print('%s: %d runs | pre-grab gate: %d first attempts, %d missed first time, %d runs ended without a grab | first-attempt |lateral| mean %.3f max %.3f m'
          % (n, len(res), len(first), len(miss1), nograb, sum(abs(g['lat_m']) for g in first) / max(len(first), 1), max([abs(g['lat_m']) for g in first] or [0])))
    if sd: print('   set-downs %d: error mean %.3f max %.3f m' % (len(sd), sum(p['err_m'] for p in sd) / len(sd), max(p['err_m'] for p in sd)))
    if trips: print('   trips %d: %.1f-%.1f min, %.1f-%.1f Wh' % (len(trips), min(t['min'] for t in trips), max(t['min'] for t in trips), min(t['wh'] for t in trips), max(t['wh'] for t in trips)))
    if cams: print('   camera checks %d, re-aligns %d' % (len(cams), sum(1 for c in cams if abs(c['lat_cam']) > 0.025)))
    hm = [(r.get('hedge_min_m'), k) for k, r in res.items() if r.get('hedge_min_m') is not None and r.get('odo_m', 0) > 0.05]
    if hm: print('   hedge clearance min over moving runs: %.3f m (%s)' % min(hm))
    for k in sorted(res):
        r = res[k]
        if k.startswith(('s3a', 's3b')) and r['metrics'].get('trips'):
            t = r['metrics']['trips']; print('   %s: %d trips, last dock %s, energy %.0f Wh' % (k, len(t), t[-1].get('clk1'), r.get('energy_wh', 0)))
