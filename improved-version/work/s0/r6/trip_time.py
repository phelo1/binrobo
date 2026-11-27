#!/usr/bin/env python3
# where the time of a trip goes: seconds per state, and in the lane states seconds per speed band and per 50 m of lane.
# usage: trip_time.py <trace.json>
import json, sys, collections
t = json.load(open(sys.argv[1]))['trace']
st = collections.OrderedDict(); band = collections.Counter(); seg = collections.defaultdict(lambda: [0.0, 0.0])
for a, b in zip(t[:-1], t[1:]):
    dt = b['t'] - a['t']; k = a['state']; st[k] = st.get(k, 0.0) + dt
    if k.startswith('LANE'):
        v = abs(a['v']); band['%.1f' % (round(v * 5) / 5)] += dt
        q = seg[(k, int(a['s'] // 50) * 50)]; q[0] += dt; q[1] += abs(a['v']) * dt
tot = sum(st.values()); print('total %.1f min' % (tot / 60))
for k, v in st.items(): print('  %-22s %6.0f s  %4.1f %%' % (k, v, 100 * v / tot))
print('lane time by speed band (m/s):', ', '.join('%s: %.0f s' % (k, v) for k, v in sorted(band.items())))
for (k, s0), (dt, dist) in sorted(seg.items()): print('  %-18s s %3d-%3d: %5.0f s, mean %.2f m/s' % (k, s0, s0 + 50, dt, dist / max(dt, 1e-6)))
