#!/usr/bin/env python3
"""Summarise grab batches. usage: grab_summary.py <res_dir> <tag> [stored_dir]"""
import json, sys, glob, os
res, tag = sys.argv[1:3]; sto = sys.argv[3] if len(sys.argv) > 3 else None; tot = cap = fh = kn = 0
for f in sorted(glob.glob(os.path.join(res, 'B2F_grab_*%s.json' % tag))):
    stem = os.path.basename(f)[:-5]
    if tag and not stem.endswith(tag): continue
    if not tag and stem.count('_') != 2: continue
    d = json.load(open(f)); runs = d.get('runs', []); wc = [r['wheel_clear_mm'] for r in runs if r.get('captured')]; tl = [r['bin_tilt_abs'] for r in runs if r.get('captured')]
    line = '%-34s captured %d/%d  false holds %d  knocked %d  wheel clearance %.0f-%.0f mm  tilt max %.1f deg' % (stem, d.get('captured', 0), len(runs), d.get('false_holds', 0), d.get('knocked', 0), min(wc) if wc else 0, max(wc) if wc else 0, max(tl) if tl else 0)
    if sto:
        s = json.load(open(os.path.join(sto, stem.replace(tag, '') + '.json'))); line += '   | stored %d/%d' % (s['captured'], s['n'])
    print(line); tot += len(runs); cap += d.get('captured', 0); fh += d.get('false_holds', 0); kn += d.get('knocked', 0)
print('TOTAL %s: %d/%d captured, %d false holds, %d knocked' % (tag or '(stored)', cap, tot, fh, kn))
