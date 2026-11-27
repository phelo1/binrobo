#!/usr/bin/env python3
"""Rough clash checks on model.pkl, by bounding boxes (so compound or round parts can give false alarms; hits are then looked at by hand).
  1. anything inside the room a nose castor needs to swivel (radius 152 mm round x 950, y +/-280, below z 290)
  2. loom points inside a part's box, in both poses
  3. new or changed parts whose boxes overlap another part's box"""
import pickle, numpy as np, sys
M = pickle.load(open('model.pkl', 'rb')); P = [e for e in M['parts'] if e['kind'] == 'part' and not e['with_bin_only']]; L = [e for e in M['parts'] if e['kind'] == 'loom']
print('1. castor swivel room:')
for e in P:
    if e['grp'] in ('cfork', 'cwheel') or e['name'].startswith(('RK Castor mounting', 'RK Castor cross-beam 50')): continue
    V = e['V_nobin']; n = sum(int((((V[:, 0] - 0.95) ** 2 + (V[:, 1] - sg * 0.28) ** 2 < 0.150 ** 2) & (V[:, 2] < 0.29)).sum()) for sg in (1, -1))
    if n: print('   %-60s %d vertices inside' % (e['name'][:60], n))
SKIP = ('BY HDPE side walls', 'BY HDPE bay floor', 'LM Mast upright', 'FR Nose cross-member', 'RK Castor cross-beam 50')   # hollow or two-part solids: box test not meaningful
print('2. loom points inside part boxes (more than 5 mm inside, at least 12 points):')
for st in ('nobin', 'carry'):
    bb = [(e['V_' + st].min(0), e['V_' + st].max(0)) for e in P]
    for l in L:
        V = l['V_' + st]; hits = {}
        for e, (lo, hi) in zip(P, bb):
            if e['name'].startswith(SKIP): continue
            ins = np.all((V > lo + 0.005) & (V < hi - 0.005), axis=1)
            if ins.sum() >= 12: hits[e['name'][:44]] = int(ins.sum())
        if hits: print('   %-6s L%-2d %-9s %s' % (st, l['item'] - 200, l['exgroup'], hits))
print('3. boxes of new or changed parts overlapping other parts (by more than 3 mm on every axis):')
bb = [(e['V_nobin'].min(0), e['V_nobin'].max(0)) for e in P]; seen = set()
for i, e in enumerate(P):
    if e['src'] == 'CAD' or e['name'].startswith(SKIP): continue
    for j, f in enumerate(P):
        if i == j or f['name'].startswith(SKIP) or (j, i) in seen or (e['body'] == f['body'] != 'tug' and e['item'] == f['item']): continue
        lo = np.maximum(bb[i][0], bb[j][0]); hi = np.minimum(bb[i][1], bb[j][1])
        if np.all(hi - lo > 0.003): seen.add((i, j)); print('   %-46s x %-46s overlap %s mm' % (e['name'][:46], f['name'][:46], ((hi - lo) * 1000).round().astype(int)))
