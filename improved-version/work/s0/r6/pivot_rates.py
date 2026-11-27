#!/usr/bin/env python3
# Turning on the spot: the highest turn rate with the robot not travelling (|v| < 0.08 m/s), by mission state, and the speed of the
# nose corner that goes with it (corner 1.39 m from the axle). usage: pivot_rates.py <sitl_out name or run dir> ...
import json, glob, os, sys, collections
RC = 1.39
tot = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0])
for a in sys.argv[1:]:
    d = a if os.path.isdir(a) else '/home/claude/sitl_out/' + a
    fs = sorted(glob.glob(d + '/runs/*/trace.json')) or sorted(glob.glob(d + '/trace.json'))
    for f in fs:
        try: t = json.load(open(f))['trace']
        except Exception: continue
        per = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
        for k, q in zip(t[:-1], t[1:]):
            if abs(k['v']) >= 0.08: continue
            w = abs(k['w']); dt = min(max(q['t'] - k['t'], 0.0), 0.5); o = per[k['state']]
            o[0] = max(o[0], w)
            if w > 0.22: o[1] += dt
            if w > 0.30: o[2] += dt
        for st, o in per.items():
            g = tot[(os.path.basename(d.rstrip('/')), st)]; g[0] = max(g[0], o[0]); g[1] += o[1]; g[2] += o[2]; g[3] += 1
rows = collections.defaultdict(dict)
for (nm, st), g in tot.items(): rows[nm][st] = g
for nm, r in rows.items():
    print(nm)
    for st, g in sorted(r.items(), key=lambda x: -x[1][0])[:8]:
        print('   %-18s peak %.2f rad/s = nose corner %.2f m/s | over 0.22 rad/s: %.1f s, over 0.30: %.1f s (in %d runs)' % (st, g[0], g[0] * RC, g[1], g[2], g[3]))
    pk = max(g[0] for g in r.values()); print('   highest: %.2f rad/s, nose corner %.2f m/s' % (pk, pk * RC))
