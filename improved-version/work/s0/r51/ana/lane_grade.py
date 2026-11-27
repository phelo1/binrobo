#!/usr/bin/env python3
"""Slope of the lane from the elevation data already in the project (22 Nov). Usage: python3 -I lane_grade.py <route.json> <out json>
route.json (the other agent's): the lane centre line from OpenStreetMap, sampled every 5 m from the house (s = 0) to the road, with the
height of each point from the EU-DEM 25 m model and from SRTM 30 m. Slopes are taken over windows of 5 to 50 m."""
import json, sys
R = json.load(open(sys.argv[1])); s = R['s']; out = dict(length_m=round(s[-1], 1), sources={})
for name, z in R['elev'].items():
    n = len(s); d = dict(house_m=round(z[0], 1), road_m=round(z[-1], 1), fall_m=round(z[0] - z[-1], 1), mean_pct=round(100 * (z[0] - z[-1]) / s[-1], 2), steepest={}, length_steeper={})
    for win in (5, 10, 25, 50):
        best = (0, 0)
        for i in range(n):
            j = next((k for k in range(i, n) if s[k] - s[i] >= win - 1e-6), None)
            if j is None: break
            g = 100 * (z[i] - z[j]) / (s[j] - s[i])
            if g > best[0]: best = (g, s[i])
        d['steepest']['%d m' % win] = dict(pct=round(best[0], 1), from_m=round(best[1]), to_m=round(best[1] + win))
    g10 = []
    for i in range(n - 2): g10.append((s[i], 100 * (z[i] - z[i + 2]) / (s[i + 2] - s[i])))     # 10 m windows on the 5 m samples
    for thr in (3, 5, 6, 7, 8, 9, 10): d['length_steeper']['%d %%' % thr] = 5 * sum(1 for _, g in g10 if g > thr)
    hill = [x for x, g in g10 if g > 5]; d['hill_over_5pct'] = dict(from_m=round(min(hill)) if hill else None, to_m=round(max(hill) + 10) if hill else None)
    up = [(x, -g) for x, g in g10 if g < -1]; d['rises_towards_road'] = dict(length_m=5 * len(up), steepest_pct=round(max((g for _, g in up), default=0), 1), from_m=round(min((x for x, _ in up), default=0)), to_m=round(max((x for x, _ in up), default=0) + 10))
    d['profile_every_25m'] = [(round(s[i]), round(z[i], 1)) for i in range(0, n, 5)]
    out['sources'][name] = d
json.dump(out, open(sys.argv[2], 'w'), indent=1)
for name, d in out['sources'].items():
    print(name, ': house', d['house_m'], 'm, road', d['road_m'], 'm, fall', d['fall_m'], 'm over', out['length_m'], 'm, mean', d['mean_pct'], '%')
    print('   steepest', d['steepest']); print('   length steeper than', d['length_steeper']); print('   hill (over 5 %)', d['hill_over_5pct'], '| rises towards the road', d['rises_towards_road'])
