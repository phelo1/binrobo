#!/usr/bin/env python3
"""Torque-boost subset against the 60 N m runs, file by file. usage: cmp_boost.py <res dir>"""
import json, glob, os, sys
D = sys.argv[1].rstrip('/') + '/'; n = 0; diff = 0; trig = 0; worse = []
KEYS = ('ok', 'reached', 'stop', 'dist', 'creep', 'swept', 'yaw_dev')
def flat(d, pre=''):
    o = {}
    for k, v in d.items():
        if k in ('geo', 'env', 'events', 'trace', 'cpu_s'): continue
        if isinstance(v, dict): o.update(flat(v, pre + k + '.'))
        elif isinstance(v, (int, float, bool)) or v is None: o[pre + k] = v
    return o
for f in sorted(glob.glob(D + 'B2F_*_r4b.json')):
    g = f.replace('_r4b.json', '_r4.json')
    if not os.path.exists(g): print('no twin', os.path.basename(f)); continue
    a = flat(json.load(open(g))); b = flat(json.load(open(f))); n += 1
    ev = json.load(open(f)).get('events') or []; t = any('boost' in str(e) for e in ev); trig += t
    pk = [k for k in a if any(s in k for s in ('peak', '_pk', 'wheel', 'comb', 'lift')) and isinstance(a[k], (int, float)) and isinstance(b.get(k), (int, float))]
    ch = [(k, a[k], b[k]) for k in pk if abs(b[k] - a[k]) > 0.02 * max(1.0, abs(a[k]))]
    okc = [(k, a[k], b.get(k)) for k in a if k.split('.')[-1] in ('ok', 'reached') and a[k] != b.get(k)]
    if ch or okc or t:
        diff += 1; print('%-44s boost %-5s' % (os.path.basename(f)[4:-9], t), 'verdicts changed:', okc, '| peaks:', [(k, round(x), round(y)) for k, x, y in ch][:5])
    if okc: worse.append(os.path.basename(f))
print('%d pairs; %d differ; boost triggered in %d; verdict changed in %d' % (n, diff, trig, len(worse)))
