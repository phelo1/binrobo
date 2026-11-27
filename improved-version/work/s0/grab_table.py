#!/usr/bin/env python3
"""Table of pick-up batches: captured, false holds, other non-successes, sideways error on first arrival. usage (from revG/sim/cg): grab_table.py <tag> [<tag> ...]"""
import json, glob, os, sys, numpy as np
for tag in sys.argv[1:]:
    tot = [0, 0, 0]
    for f in sorted(glob.glob('h2/res/B2F_grab_*%s.json' % tag)):
        bn = os.path.basename(f)[9:-5 - len(tag)]
        if '_' in bn and not bn.startswith('ESE240SL250'): continue
        j = json.load(open(f)); r = j['runs']; first = []
        for x in r:
            ev = [e[1] for e in x['events'] if e[1].startswith('docked')]
            if ev: first.append(abs(float(ev[0].split('bin dy ')[1].split(' mm')[0])))
        ok = sum(x['result'] == 'success' for x in r); fh = sum(bool(x.get('false_hold')) for x in r); tot[0] += ok; tot[1] += len(r); tot[2] += fh
        bad = [(x['i'], x['result'], x.get('dock_dy_mm')) for x in r if x['result'] != 'success']
        print('%-18s %-11s seed %s  %2d/%2d  false holds %d  first arrival |dy| mean %4.1f max %3.0f mm  %s' % (tag, bn, j['seed'], ok, len(r), fh, np.mean(first), np.max(first), bad or ''))
    print('%-18s total %d/%d, false holds %d' % (tag, *tot))
