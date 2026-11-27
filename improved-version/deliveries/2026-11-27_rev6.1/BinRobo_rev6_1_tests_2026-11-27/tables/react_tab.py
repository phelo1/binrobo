#!/usr/bin/env python3
"""People cases: time from the person's first step to the stand-still command, and what the robot was doing. Revision 6 runs against 6.1.
usage: react_tab.py <out json> <prefix:label> ... [--cases a,b,c]"""
import json, glob, math, gzip, os, sys
def load(p): return json.load(gzip.open(p + '.gz', 'rt'))['trace'] if os.path.exists(p + '.gz') else json.load(open(p))['trace']
args = [a for a in sys.argv[2:] if ':' in a]; cases = sys.argv[sys.argv.index('--cases') + 1].split(',') if '--cases' in sys.argv else ['near26', 'near20', 'run26', 'run20', 'child35', 'gapwalk26', 'gaprun26', 'nearhedge30', 'side', 'side14']
out = []
for a in args:
    pf, lab = a.split(':')
    for c in cases:
        for rd in sorted(glob.glob('/home/claude/sitl_out/%s_%s/runs/*/' % (pf, c))):
            if not os.path.exists(rd + 'result.json'): continue
            try: tr = load(rd + 'trace.json')
            except Exception: continue
            res = json.load(open(rd + 'result.json')); rows = [q for q in tr if q['mv']]
            if not rows: continue
            m0 = rows[0]['mv'][0]; mvd = [q for q in rows if math.hypot(q['mv'][0][0] - m0[0], q['mv'][0][1] - m0[1]) > 0.05]
            if not mvd: continue
            t_go = mvd[0]['t'] - 0.12; pp = [p for p in res['metrics'].get('ppl_pauses', []) if p['t'] >= rows[0]['t'] - 0.2]
            hold = next((q['t'] for q in tr if q['t'] >= t_go and q['mode'] == 'HOLD'), None); still = next((q['t'] for q in tr if hold and q['t'] >= hold and abs(q['v']) < 0.02), None)
            v0 = next(q['v'] for q in tr if q['t'] >= t_go)
            out.append(dict(set=lab, case=c, seed=res['seed'], v_at_first_step=round(v0, 2), pause_by=pp[0]['by'] if pp else None, pause_after_s=round(pp[0]['t'] - t_go, 2) if pp else None, pause_range=pp[0]['range'] if pp else None,
                            hold_after_s=round(hold - t_go, 2) if hold else None, still_after_s=round(still - t_go, 2) if still else None, contacts=len(res['collisions']), outcome=res['outcome']))
json.dump(out, open(sys.argv[1], 'w'), indent=1)
for c in cases:
    for a in args:
        lab = a.split(':')[1]; rr = [o for o in out if o['case'] == c and o['set'] == lab]
        if rr: print('%-12s %-9s v %s | stand-still command after %s s (%s) | firmware hold after %s | still after %s | contacts %s' % (c, lab, [o['v_at_first_step'] for o in rr], [o['pause_after_s'] for o in rr], [o['pause_by'] for o in rr], [o['hold_after_s'] for o in rr], [o['still_after_s'] for o in rr], [o['contacts'] for o in rr]))
