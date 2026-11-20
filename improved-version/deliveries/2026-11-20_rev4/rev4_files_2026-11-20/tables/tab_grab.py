#!/usr/bin/env python3
"""Pick-up batches: results, comb offset under the lip (truth), set-downs by the seating check, re-approaches. usage: tab_grab.py <files...>"""
import json, sys, os
tot = dict(n=0, lifted=0, refused=0, b50=0, b80=0, ph=0, reapp=0, mx=0.0, other=0)
for f in sys.argv[1:]:
    d = json.load(open(f)); T = d['runs']; res = {}
    for t in T: res[t['result']] = res.get(t['result'], 0) + 1
    L = [t for t in T if t['result'] in ('success', 'false_positive')]; ny = [abs(t.get('nib_y_mm', 0.0)) for t in L]
    wide = 'WEB140' in f; lim = (100, 130) if wide else (50, 80)
    ph = sum(1 for t in T if len(t.get('posthold_mm', [])) > 1); ra = sum(1 for t in T if t.get('reapp'))
    print('%-46s n %3d %s | lifted %d, max offset %.1f mm, beyond %d mm: %d, beyond %d mm: %d | set down by the check: %d | re-approach: %d | file says captured %s false_holds %s knocked %s'
          % (os.path.basename(f)[9:-5], len(T), res, len(L), max(ny) if ny else 0, lim[0], sum(1 for v in ny if v > lim[0]), lim[1], sum(1 for v in ny if v > lim[1]), ph, ra, d.get('captured'), d.get('false_holds'), d.get('knocked')))
    tot['n'] += len(T); tot['lifted'] += len(L); tot['refused'] += res.get('no_dock', 0); tot['other'] += len(T) - len(L) - res.get('no_dock', 0)
    tot['b50'] += sum(1 for v in ny if v > lim[0]); tot['b80'] += sum(1 for v in ny if v > lim[1]); tot['ph'] += ph; tot['reapp'] += ra; tot['mx'] = max(tot['mx'], max(ny) if ny else 0)
print('ALL', tot)
