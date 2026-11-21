#!/usr/bin/env python3
"""Revision 5 reading of the 60-mission score. Uses the B2-F scorer (b2f_score.py, unchanged) for every criterion, then restates two:
  C3r  time window as the bye-law reads (review finding M-5): drop-offs (s1a, s3a) start no earlier than 18:00 the day before and the robot
       is back on the dock by the quiet-hours limit (22:30, my choice); pick-ups (s1b, s3b) are done on collection day and the last bin
       is home (robot on the dock) by 21:00.
  C6r  energy: every trip inside the revision 5 trip budget (75 Wh, the pre-trip guard) and, for three trips, end charge >= 20 %.
Both scores are printed: the B2-F script as it stands, and with C3r / C6r in place of C3 / C6.
usage: r5_score.py <runs dir> [<runs dir> ...]   (later dirs override earlier ones run by run)"""
import json, os, sys, glob, importlib.util
spec = importlib.util.spec_from_file_location('b2f_score', '/home/claude/b2f_run/sitl/b2f/scripts/b2f_score.py')
BS = importlib.util.module_from_spec(spec)
_argv = sys.argv; sys.argv = [_argv[0]]; spec.loader.exec_module(BS); sys.argv = _argv
QUIET = 22 * 60 + 30; BUDGET = 75.0

def rescored(r):
    q = BS.score(r); n = r['scenario']; m = r['metrics']; C = dict(q['crit']); why = dict(q['why'])
    if n in BS.FULL:
        fm = BS.clk(m.get('first_motion_clock')); ld = BS.clk(m.get('last_dock_clock'))
        if n in ('s1a', 's3a'): ok = fm is not None and ld is not None and fm[1] >= 18 * 60 and ld[0] == fm[0] and ld[1] <= QUIET
        else: ok = fm is not None and ld is not None and ld[0] == fm[0] and ld[1] <= 21 * 60
        C.pop('C3', None); C['C3r'] = 'PASS' if ok else 'FAIL'; why['C3r'] = 'first motion %s, last dock %s' % (m.get('first_motion_clock'), m.get('last_dock_clock'))
        tr = m.get('trips') or []; ok = bool(tr) and all(t['wh'] <= BUDGET for t in tr)
        if n in ('s3a', 's3b'): ok = ok and r['soc_end'] >= 0.20
        C.pop('C6', None); C['C6r'] = 'PASS' if ok else 'FAIL'; why['C6r'] = 'trips %s Wh, end charge %.0f %%' % ([t['wh'] for t in tr], 100 * r['soc_end'])
    q2 = dict(q, crit_r=C, why_r=why, verdict_r='PASS' if all(v == 'PASS' for v in C.values()) else 'FAIL')
    q2['hedge_min_m'] = r.get('hedge_min_m'); q2['hedge_min_at'] = r.get('hedge_min_at'); q2['prot_stops'] = m.get('prot_stops'); q2['navcam'] = m.get('navcam')
    q2['trips'] = m.get('trips'); q2['window'] = m.get('window'); q2['soc_end'] = r.get('soc_end')
    return q2

def main():
    runs = {}
    for d in sys.argv[1:]:
        if d.startswith('--'): continue
        for f in sorted(glob.glob(os.path.join(d, '*', 'result.json'))):
            runs[os.path.basename(os.path.dirname(f))] = f
    rows = [rescored(json.load(open(f))) for k, f in runs.items()]
    order = ['s1a', 's1b', 's3a', 's3b', 's4a', 's4b', 's4c', 's5a', 's5b', 's6a', 's6b', 's7', 's8', 's9', 's10a', 's10b', 's11a', 's11b', 's12a', 's12b']
    rows.sort(key=lambda q: (order.index(q['scenario']) if q['scenario'] in order else 99, q['seed']))
    P = sum(q['verdict'] == 'PASS' for q in rows); Pr = sum(q['verdict_r'] == 'PASS' for q in rows)
    L = ['# Revision 5 mission score', '', 'B2-F script as it stands: %d / %d PASS. With the time window and the energy budget restated for revision 5 (C3r, C6r): %d / %d PASS.' % (P, len(rows), Pr, len(rows)), '',
         '| run | expected | outcome | B2-F script | restated | failed (B2-F script) | failed (restated) | hedge min m |', '|---|---|---|---|---|---|---|---|']
    for q in rows:
        f1 = ', '.join('%s (%s)' % (k, q['why'][k]) for k, v in q['crit'].items() if v == 'FAIL') or '-'
        f2 = ', '.join('%s (%s)' % (k, q['why_r'][k]) for k, v in q['crit_r'].items() if v == 'FAIL') or '-'
        L.append('| %s | %s | %s / %s | %s | %s | %s | %s | %s |' % (q['key'], q['expect'], q['result'], q['outcome'], q['verdict'], q['verdict_r'], f1, f2, q['hedge_min_m']))
    out = '\n'.join(L) + '\n'
    for a in sys.argv[1:]:
        if a.startswith('--md='): open(a[5:], 'w').write(out)
        if a.startswith('--json='): json.dump(rows, open(a[7:], 'w'), indent=1)
    print(out)

if __name__ == '__main__': main()
