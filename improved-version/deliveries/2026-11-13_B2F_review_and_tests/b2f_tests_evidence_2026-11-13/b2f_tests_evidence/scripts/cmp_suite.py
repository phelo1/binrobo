#!/usr/bin/env python3
"""Compare a tagged re-run of the B2-F non-grab gate cases with the stored results. usage: cmp_suite.py <res_dir> <stored_dir> <tag> [prefix]"""
import json, sys, os
res, sto, tag = sys.argv[1:4]; pre = sys.argv[4] if len(sys.argv) > 4 else 'B2F_'
def flat(d, p=''):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items(): out.update(flat(v, p + str(k) + '.'))
    elif isinstance(d, list):
        for i, v in enumerate(d): out.update(flat(v, p + str(i) + '.'))
    else: out[p[:-1]] = d
    return out
n = vs = ex = tot = ident = 0; flips = []; missing = []
for f in sorted(os.listdir(sto)):
    if not f.startswith(pre) or not f.endswith('.json') or '_grab_' in f: continue
    stem = f[:-5]; g = os.path.join(res, stem + tag + '.json')
    if not os.path.exists(g): continue
    try: a = json.load(open(os.path.join(sto, f))); b = json.load(open(g))
    except Exception as e: missing.append(f); continue
    if not isinstance(a, dict) or 'ok' not in a: continue
    fa, fb = flat(a), flat(b); ks = [k for k in fa if 'cpu' not in k]; s = sum(1 for k in ks if fa[k] == fb.get(k))
    n += 1; tot += len(ks); ident += s; ex += (s == len(ks)); vs += (a['ok'] == b.get('ok'))
    if a['ok'] != b.get('ok'): flips.append((stem, a['ok'], b.get('ok'), {k: (a.get(k), b.get(k)) for k in ('reached', 'dist_m', 'pitch', 'hold_creep_m', 'stop_dist_m', 'clear_min') if k in a}))
print('tag %s: cases %d | verdict identical %d | identical in every field %d | fields identical %d of %d' % (tag, n, vs, ex, ident, tot))
for x in flips: print('   VERDICT CHANGED:', x)
