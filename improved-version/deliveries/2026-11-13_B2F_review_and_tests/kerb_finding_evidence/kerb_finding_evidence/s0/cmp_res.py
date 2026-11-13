#!/usr/bin/env python3
"""Compare a re-run result JSON with the other agent's stored one. usage: cmp_res.py <stored.json> <new.json>"""
import json, sys
def flat(d, p=''):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items(): out.update(flat(v, p + str(k) + '.'))
    elif isinstance(d, list):
        for i, v in enumerate(d): out.update(flat(v, p + str(i) + '.'))
    else: out[p[:-1]] = d
    return out
a, b = flat(json.load(open(sys.argv[1]))), flat(json.load(open(sys.argv[2])))
skip = ('cpu_s', 'wall', 'time_s_wall'); n = same = 0; worst = (0.0, None); diffs = []
for k, va in a.items():
    if any(s in k for s in skip): continue
    n += 1; vb = b.get(k, '<missing>')
    if va == vb: same += 1; continue
    if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool):
        rel = abs(va - vb) / max(abs(va), abs(vb), 1e-9); 
        if rel > worst[0]: worst = (rel, k)
        diffs.append((k, va, vb, rel))
    else: diffs.append((k, va, vb, None))
print('%s: %d fields, %d identical, %d differ; worst relative difference %.2g (%s)' % (sys.argv[2].split('/')[-1], n, same, len(diffs), worst[0], worst[1]))
for k, va, vb, rel in diffs[:12]: print('    %-34s stored %s   now %s' % (k[:34], va, vb))
