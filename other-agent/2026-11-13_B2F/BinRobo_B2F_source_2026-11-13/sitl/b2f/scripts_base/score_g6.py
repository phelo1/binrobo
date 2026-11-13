#!/usr/bin/env python3
"""Rev G6 scoring (out/G6).  score_g6.py regress            -> table for scenarios.ALL_G6 (+ G3 / G4 comparison)
                            score_g6.py robust <tag> [...]   -> per-scenario score over seeds (out/G6/robust/<tag>/)
A run is 'as expected' when its result equals the scenario's expected result. A PASS with a truth placement > 0.6 m is NOT
as expected (G4 rule). Hitch: every run with kingpin-stop hits or a peak within 3 deg of the cap is listed.
G6 s6 (cold-eye review M3): a STRICT score is reported next to the old one. Strict = old 'as expected' AND truth hedge clearance
>= 0 (tug or towed-bin footprint never crosses the truth hedge face; sim metric lateral.hedge_clear_min_m) AND zero frames at the
hitch stop (hitch_limit_hits == 0). Applied to every run, including expected alerts (a hedge strike or stop hit is a defect
whatever the mission outcome). The review's tighter 0.10 m hedge margin is reported as a count only (HEDGE_REVIEW_M)."""
import json, os, sys, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
import scenarios
OUT = os.path.join(ROOT, 'out', os.environ.get('BT_SCORE_DIR', 'G6'))   # G6 s3: score another result set (e.g. G6/before_95kg)


def load(p):
    try: return json.load(open(p))
    except Exception: return None


def cls(r):
    exp = r.get('expect', 'pass'); ok = r['result'] == exp
    if r['result'] == 'pass' and (r.get('metrics') or {}).get('placement_oot'): return False, 'PASS but PLACEMENT >0.6 m'
    if r['result'] == 'pass': c = 'PASS'
    elif r['result'] in ('alert', 'stopped'): c = 'EXPECTED-ALERT' if ok else 'ALERT (unexpected)'
    else: c = 'FAIL (expected)' if ok else 'FAIL'
    return ok, c


HEDGE_STRICT_M = 0.0; HEDGE_REVIEW_M = 0.10


def strict(r, ok):
    """(ok_strict, [defects]) -- old verdict plus the M3 hedge / hitch-stop defects."""
    d = []; h = (r.get('lateral') or {}).get('hedge_clear_min_m'); n = r.get('hitch_limit_hits') or 0
    if h is not None and h < HEDGE_STRICT_M: d.append('hedge %+.2f m' % h)
    if n > 0: d.append('%d stop frames' % n)
    return (ok and not d), d


def row(sc, r):
    ok, c = cls(r); ok_s, defects = strict(r, ok); la = r.get('lateral') or {}; x = la.get('xte') or {}
    m = r.get('metrics') or {}
    return dict(scenario=sc, result=r['result'], expect=r.get('expect'), cls=c, ok=ok, ok_strict=ok_s, defects=defects, sim_s=r['sim_time_s'], wall_s=r['wall_s'],
                wh=r['energy_wh'], pack_wh=r.get('pack_wh_out'), soc_end=r.get('soc_end'), legal=r.get('legal_min_inside_m'),
                fence=r['fence_breach'], outcome=r['outcome'], alerts=[a['text'] for a in r.get('alerts', [])],
                hitch_max=r.get('hitch_max_deg'), hitch_hits=r.get('hitch_limit_hits'), guards=len(r.get('hitch_guard') or []),
                cap=r.get('hitch_cap_deg'), mass=r.get('mass_kg'), xte_sd=x.get('sd'), xte_p95=x.get('p95_abs'), xte_max=x.get('max_abs'),
                hedge_min=la.get('hedge_clear_min_m'), hedge_at=la.get('hedge_clear_at'), fence_min=la.get('fence_clear_min_m'),
                est_sd=(la.get('est_err') or {}).get('sd'), placement=m.get('placement'), stops=len(r.get('stops') or []),
                flips=m.get('flips'), uturn_stops=m.get('uturn_stops'), finish_clock=m.get('finish_clock'),
                deadline_margin_min=m.get('deadline_margin_min'), hedge_overlap=r.get('hedge_overlap_m'))


if __name__ == '__main__' and sys.argv[1] == 'regress':
    rows = []; n_ok = n = 0
    g3 = {x['scenario']: x for x in (load(os.path.join(ROOT, 'out', 'regress_G3.json')) or [])}
    for sc in scenarios.ALL_G6:
        r = load(os.path.join(OUT, sc, 'result.json'))
        if r is None or r.get('result') == 'running': rows.append(dict(scenario=sc, missing=True)); continue
        x = row(sc, r); n += 1; n_ok += x['ok']
        g4 = load(os.path.join(ROOT, 'out', 'G4', sc, 'result.json'))
        x['g3'] = (g3.get(sc) or {}).get('cls'); x['g3_ok'] = (g3.get(sc) or {}).get('ok')
        x['g4'] = cls(g4)[1] if g4 and g4.get('result') not in (None, 'running') else None
        x['g4_ok'] = cls(g4)[0] if g4 and g4.get('result') not in (None, 'running') else None
        rows.append(x)
    for x in rows:
        if x.get('missing'): print('%-30s MISSING' % x['scenario']); continue
        print('%-30s %-18s exp=%-7s %s %6.0fs %6.1fWh hitch %4.1f/%s g%d hedge=%s xte=%s | G3 %s | G4 %s | %s' % (
            x['scenario'], x['cls'], x['expect'], 'ok ' if x['ok'] else 'BAD', x['sim_s'], x['wh'], x['hitch_max'] or 0, x['hitch_hits'], x['guards'],
            x['hedge_min'], x['xte_sd'], x['g3'], x['g4'], x['outcome'][:70]))
    g3n = [x for x in rows if not x.get('missing') and x.get('g3_ok') is not None]
    print('== G6 %d/%d as expected | on the G3 set: G6 %d/%d vs G3 %d/%d' % (n_ok, n, sum(x['ok'] for x in g3n), len(g3n), sum(bool(x['g3_ok']) for x in g3n), len(g3n)))
    g4n = [x for x in rows if not x.get('missing') and x.get('g4_ok') is not None]
    print('== on the %d scenarios with a G4 result: G6 %d vs G4 %d' % (len(g4n), sum(x['ok'] for x in g4n), sum(bool(x['g4_ok']) for x in g4n)))
    hh = [x for x in rows if not x.get('missing') and ((x['hitch_hits'] or 0) > 0 or (x['hitch_max'] or 0) >= (x['cap'] or 28) - 3)]
    print('== hitch: %d runs with stop hits or peak >= cap-3:' % len(hh))
    for x in hh: print('   %-30s peak %.1f deg, %s frames at the stop, %d guard events' % (x['scenario'], x['hitch_max'], x['hitch_hits'], x['guards']))
    ns = sum(x['ok_strict'] for x in rows if not x.get('missing'))
    print('== STRICT (M3: hedge clearance >= 0 and no hitch-stop frames): %d/%d (old criteria %d/%d)' % (ns, n, n_ok, n))
    for x in rows:
        if not x.get('missing') and x['ok'] and not x['ok_strict']: print('   flips to FAIL: %-28s %s' % (x['scenario'], ', '.join(x['defects'])))
    nr = sum(1 for x in rows if not x.get('missing') and x['hedge_min'] is not None and x['hedge_min'] < HEDGE_REVIEW_M)
    print('== runs with truth hedge clearance < %.2f m (review threshold, count only): %d' % (HEDGE_REVIEW_M, nr))
    json.dump(rows, open(os.path.join(OUT, 'regress_G6.json'), 'w'), indent=1)
elif __name__ == '__main__':
    for tag in sys.argv[2:]:
        per = collections.defaultdict(list); breaches = 0
        for p in sorted(glob.glob(os.path.join(OUT, 'robust', tag, '*', 'result.json'))):
            r = load(p)
            if r is None or r.get('result') == 'running': continue
            sc = os.path.basename(os.path.dirname(p)).rsplit('_seed', 1)[0]; x = row(sc, r); x['seed'] = r.get('seed')
            per[sc].append(x); breaches += bool(r['fence_breach'])
        n = sum(len(v) for v in per.values()); ok = sum(x['ok'] for v in per.values() for x in v)
        oks = sum(x['ok_strict'] for v in per.values() for x in v)
        print('== %s: %d/%d as expected (%.0f %%), geofence breaches %d | STRICT %d/%d' % (tag, ok, n, 100.0 * ok / max(n, 1), breaches, oks, n))
        for sc, v in per.items():
            print('  %-28s %d/%d strict %d/%d %s' % (sc, sum(x['ok'] for x in v), len(v), sum(x['ok_strict'] for x in v), len(v), '; '.join('seed%s: %s' % (x['seed'], x['outcome']) for x in v if not x['ok'])[:220]))
        json.dump(dict(per), open(os.path.join(OUT, 'robust_%s.json' % tag), 'w'), indent=1)
