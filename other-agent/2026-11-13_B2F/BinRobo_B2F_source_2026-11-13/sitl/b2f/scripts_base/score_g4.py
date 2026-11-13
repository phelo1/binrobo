#!/usr/bin/env python3
"""Rev G4 scoring (out/G4). score_g4.py regress  -> table of out/<scenario>/result.json for scenarios.ALL_G3
                   score_g3.py robust <tag> [...] -> per-scenario score over seeds (out/robust/<tag>/)
A run is 'as expected' when its result equals the scenario's expected result (pass / alert / stopped / fail)."""
import json, os, sys, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
import scenarios
def load(p):
    try: return json.load(open(p))
    except Exception: return None
def cls(r):
    exp = r.get('expect', 'pass'); ok = r['result'] == exp
    if r['result'] == 'pass' and (r.get('metrics') or {}).get('placement_oot'): return False, 'PASS but PLACEMENT >0.6 m'   # G4: truth placement tolerance
    if r['result'] == 'pass': c = 'PASS'
    elif r['result'] in ('alert', 'stopped'): c = 'EXPECTED-ALERT' if ok else 'ALERT (unexpected)'
    else: c = 'FAIL (expected)' if ok else 'FAIL'
    return ok, c
if sys.argv[1] == 'regress':
    rows = []; n_ok = 0; n = 0
    for sc in scenarios.ALL_G4:
        r = load(os.path.join(ROOT, 'out', 'G4', sc, 'result.json'))
        if r is None or r.get('result') == 'running': rows.append(dict(scenario=sc, missing=True)); continue
        ok, c = cls(r); n += 1; n_ok += ok
        rows.append(dict(scenario=sc, result=r['result'], expect=r.get('expect'), cls=c, ok=ok, sim_s=r['sim_time_s'], wall_s=r['wall_s'],
                         wh=r['energy_wh'], pack_wh=r.get('pack_wh_out'), legal=r.get('legal_min_inside_m'), rev_v=r.get('rev_speed_max'),
                         fence=r['fence_breach'], outcome=r['outcome'], alerts=len(r['alerts']), hedge=r.get('hedge_overlap_m')))
    for x in rows:
        if x.get('missing'): print('%-26s MISSING' % x['scenario']); continue
        print('%-30s %-18s exp=%-7s %s %6.0fs %6.1fWh legal=%s hedge=%s fence=%s | %s' % (x['scenario'], x['cls'], x['expect'], 'ok ' if x['ok'] else 'BAD',
              x['sim_s'], x['wh'], x['legal'], x['hedge'], x['fence'], x['outcome'][:80]))
    print('== %d/%d as expected' % (n_ok, n))
    json.dump(rows, open(os.path.join(ROOT, 'out', 'G4', 'regress_G4.json'), 'w'), indent=1)
else:
    for tag in sys.argv[2:]:
        per = collections.defaultdict(list); breaches = 0; allr = []
        for p in sorted(glob.glob(os.path.join(ROOT, 'out', 'G4', 'robust', tag, '*', 'result.json'))):
            r = load(p)
            if r is None: continue
            sc = os.path.basename(os.path.dirname(p)).rsplit('_seed', 1)[0]; ok, c = cls(r)
            per[sc].append(dict(seed=r.get('seed'), ok=ok, cls=c, result=r['result'], outcome=r['outcome'], legal=r.get('legal_min_inside_m'),
                                rev_v=r.get('rev_speed_max'), fence=r['fence_breach'], hedge=r.get('hedge_overlap_m'))); breaches += bool(r['fence_breach'])
        n = sum(len(v) for v in per.values()); ok = sum(x['ok'] for v in per.values() for x in v)
        print('== %s: %d/%d as expected (%.0f %%), geofence breaches %d' % (tag, ok, n, 100.0 * ok / max(n, 1), breaches))
        for sc, v in per.items(): print('  %-24s %d/%d  %s' % (sc, sum(x['ok'] for x in v), len(v), '; '.join('seed%s: %s' % (x['seed'], x['outcome']) for x in v if not x['ok'])[:200]))
        json.dump(dict(per), open(os.path.join(ROOT, 'out', 'G4', 'robust_%s.json' % tag), 'w'), indent=1)
