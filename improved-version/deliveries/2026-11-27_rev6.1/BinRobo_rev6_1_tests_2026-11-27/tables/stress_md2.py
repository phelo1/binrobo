#!/usr/bin/env python3
"""Markdown table and sheet rows from stress-test tables (stress_tab.py output), revision 6.1: any number of columns.
usage: stress_md2.py <out md> <out rows json> <stress json>[,<stress json>...] <set>=<column heading> [<set>=<column heading> ...] [--cases a,b,c]
Every phrase is built from the run records; nothing is typed in by hand."""
import json, sys
args = [a for a in sys.argv[1:] if not a.startswith('--cases')]; only = None
if '--cases' in sys.argv: only = sys.argv[sys.argv.index('--cases') + 1].split(','); args = [a for a in args if a != ','.join(only)]
R = sum((json.load(open(f)) for f in args[2].split(',')), []); by = {}
for r in R: by.setdefault(r['case'], {})[r['set']] = r
def rng(v, fmt='%.2f'):
    a, b = fmt % min(v), fmt % max(v); return a if a == b else (a + ' to ' + b)
def cell(r):
    if r is None: return 'earlier run only'
    runs = r['runs']; n = len(runs); touch = [q for q in runs if q.get('touch')]; clean = [q for q in runs if not q.get('touch')]; txt = []
    if touch:
        tv = [q['touch']['v'] for q in touch]
        if max(tv) < 0.02: txt.append('TOUCHED in %d of %d as the robot came to rest (under 0.02 m/s)' % (len(touch), n))
        elif min(tv) < 0.02: txt.append('TOUCHED in %d of %d, robot braking, at up to %.2f m/s' % (len(touch), n, max(tv)))
        else: txt.append('TOUCHED in %d of %d, robot braking, at %s m/s' % (len(touch), n, rng(tv)))
    nb = [q for q in clean if q['near']]
    if nb:
        g = [q['near']['gap'] for q in nb]; still = [q['near']['still_for'] for q in nb]; vv = [abs(q['near']['v']) for q in nb]
        walked = [q for q in nb if q['near']['gap'] < 0.06]; pre = 'no touch' if not touch else 'other runs: no touch'
        if len(walked) == len(nb) and max(still) < 0.5: txt.append('%s while moving: they reached the robot within %.1f s of its stopping' % (pre, max(still)))
        elif len(walked) == len(nb): txt.append('%s while moving: they walked up to the robot, which had stood still for %s s' % (pre, rng(still, '%.1f')))
        elif walked: txt.append('%s while moving; nearest up to %.2f m; in %d of %d they walked up to the standing robot' % (pre, max(g), len(walked), len(nb)))
        elif max(vv) < 0.02: txt.append('%s; nearest %s m, robot standing still' % (pre, rng(g)))
        else: txt.append('%s; nearest %s m, robot at up to %.2f m/s then' % (pre, rng(g), max(vv)))
    elif not touch:
        rg = [q['pauses'][0]['range'] for q in runs if q['pauses']]
        txt.append('no touch; stood still %s m from it' % rng(rg, '%.1f') if rg else 'no touch')
    outc = [q['outcome'] for q in runs]; st = [q for q in runs if any(p.get('static') for p in q['pauses'])]
    if st: txt.append('after 20 s or more passed it at 0.2 m/s' + ('' if len(st) == n else ' (%d of %d)' % (len(st), n)))
    nblk = sum(1 for o in outc if 'path blocked' in o); nhold = sum(1 for q in runs if any('holding' in a for a in q['alerts']))
    if nhold: txt.append('held with an alert in %d of %d' % (nhold, n))
    elif nblk: txt.append('path-blocked alert' + ('' if nblk == n else ' in %d of %d' % (nblk, n)))
    if any(any('waiting' in a for a in q['alerts']) for q in runs): txt.append('owner message at 2 minutes')
    if any('time limit' in o for o in outc) and not nblk and not nhold: txt.append('still waiting when the 15-minute scenario ended')
    np_ = [len(q['pauses']) for q in runs]
    if max(np_) > 3: txt.append('%s stops' % rng(np_, '%d'))
    return '; '.join(txt)
SETS = [a.split('=', 1) for a in args[3:]]
rows = []; md = ['| Case | Runs | ' + ' | '.join(h for _, h in SETS) + ' |', '|---|---:|' + '---|' * len(SETS)]
CAN = ['asis', 'near35', 'near31', 'near26', 'near20', 'child35', 'run40', 'run26', 'run20', 'nearhedge45', 'nearhedge30', 'gapwalk26', 'gaprun26', 'behind', 'side', 'side14', 'flank', 'hug', 'hugstand', 'hugstand31', 'slowwalk', 'low40', 'low40near', 'stay1000', 'boxfar', 'boxpath', 'boxside']
order = [c for c in CAN if c in by and (only is None or c in only) and any(k in by[c] for k, _ in SETS)]
tot = {k: [0, 0] for k, _ in SETS}
for c in order:
    d = by[c]; what = next(iter(d.values()))['what']; n = ' + '.join(str(len(d[k]['runs'])) for k, _ in SETS if k in d)
    for k, _ in SETS:
        if k in d: tot[k][0] += len(d[k]['runs']); tot[k][1] += sum(1 for q in d[k]['runs'] if q.get('touch'))
    cells = [(cell(d[k]) if k in d else 'not run') for k, _ in SETS]; rows.append([what] + cells + [c]); md.append('| %s | %s | %s |' % (what, n, ' | '.join(cells)))
md.append(''); md.append('Runs: ' + '; '.join('%s: %d (%d with a touch)' % (h, tot[k][0], tot[k][1]) for k, h in SETS) + '.')
open(args[0], 'w').write('\n'.join(md) + '\n'); json.dump(dict(rows=rows, totals=tot, sets=SETS), open(args[1], 'w'), indent=1); print('\n'.join(md))
