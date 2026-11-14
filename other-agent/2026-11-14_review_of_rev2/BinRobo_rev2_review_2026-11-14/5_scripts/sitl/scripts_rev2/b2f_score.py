#!/usr/bin/env python3
"""B2-F lane SITL scorer - applies CRITERIA_B2F_SITL.md (frozen, sha256 586b61b8...) to the scored runs.
Written and frozen (md5 in P/sitl/b2f/FROZEN_CODE_B2F.md5) BEFORE any scored run. Never edited after results are seen.

Reading of the criteria fixed here, before scoring:
 C1  hedge_min_m (truth, footprint incl. carried bin) >= 0.124 m; applies when the robot moved (odo_m > 0.05).
 C2  every set-down: err_m <= 0.15 and handle_err_deg <= 10.
 C3  full missions (s1a s1b s3a s3b): first-motion clock >= 18:00, last dock on the same evening <= 21:00,
     every pad placement clock >= 18:00. A missing first-motion or last-dock clock is a FAIL.
 C4  legal_min_m >= 0.00 whenever measured (every run); s12b additionally needs the firmware fence HOLD.
 C5a s7: stop distance <= 0.30 m.
 C5b every run: no contact with any obstacle / standing bin (contact_min_m > 0, no collisions); where the robot came to rest
     near a person / dog / car, that truth gap >= 0.50 m.
 C5c s6a s6b: firmware HOLD within 2.5 s and rolled distance <= 1.0 m.
 C6  full missions: every trip <= 50 Wh; s3a s3b end SOC >= 0.20; s8: the guard refused the trip (no motion).
 C7  pass-expected runs: result == pass. alert-expected runs: result == alert with the named outcome.
 C8  every grab preceded by a pre-grab gate inside lateral 0.05 m / yaw 3 deg (truth). Gate attempts that missed are
     reported; a grab is never made without an OK gate (the run alerts instead, which C7 scores).
Usage: b2f_score.py [out_dir] -> writes score.json + score.md in out_dir/.."""
import json, os, sys, glob

OUT = sys.argv[1] if len(sys.argv) > 1 else '/workspace/work/out/b2f_lane/sitl/runs'
EXPECT_OUT = dict(s4c='no fix hold', s6a='companion freeze -> firmware HOLD', s6b='companion freeze -> firmware HOLD', s7='e-stop',
                  s8='energy guard', s9='bin missing', s10a='bin tipped', s10b='bin blocked', s11a='wind no-go', s11b='frost no-go',
                  s12a='pad outside geofence', s12b='firmware fence hold')
FULL = ('s1a', 's1b', 's3a', 's3b')


def clk(s):
    """'D-1 18:28' -> (day, minutes)"""
    if not s: return None
    d, hm = s.split(' '); day = int(d[1:]) if len(d) > 1 else 0; h, m = hm.split(':'); return day, int(h) * 60 + int(m)


def score(r):
    n = r['scenario']; m = r['metrics']; C = {}; why = {}
    def put(k, ok, w): C[k] = 'PASS' if ok else 'FAIL'; why[k] = w
    moved = (r.get('odo_m') or 0) > 0.05
    if moved and r.get('hedge_min_m') is not None:
        put('C1', r['hedge_min_m'] >= 0.124, 'hedge min %.3f m at t/s %s' % (r['hedge_min_m'], r.get('hedge_min_at')))
    pl = m.get('placements') or []
    if pl:
        bad = [p for p in pl if p['err_m'] > 0.15 or p['handle_err_deg'] > 10]
        put('C2', not bad, '; '.join('%s %.3f m %.1f deg' % (p['where'], p['err_m'], p['handle_err_deg']) for p in pl))
    if n in FULL:
        fm = clk(m.get('first_motion_clock')); ld = clk(m.get('last_dock_clock'))
        padpl = [clk(p['clock']) for p in pl if p['where'].startswith('pad') and p.get('clock')]
        ok = fm is not None and ld is not None and fm[1] >= 18 * 60 and ld[0] == fm[0] and ld[1] <= 21 * 60 and all(q[1] >= 18 * 60 for q in padpl)
        put('C3', ok, 'first motion %s, last dock %s' % (m.get('first_motion_clock'), m.get('last_dock_clock')))
    if r.get('legal_min_m') is not None or n == 's12b':
        ok = r.get('legal_min_m') is not None and r['legal_min_m'] >= 0.0
        if n == 's12b': ok = ok and r['outcome'] == 'firmware fence hold'
        put('C4', ok, 'boundary margin %s m' % r.get('legal_min_m'))
    if n == 's7':
        e = m.get('estop'); put('C5a', bool(e) and e['stop_m'] <= 0.30, 'stop %s m' % (e and e['stop_m']))
    cm = r.get('contact_min_m'); rest = [q for q in (r.get('person_rest_min_m'), r.get('car_rest_min_m')) if q is not None]
    ok = (cm is None or cm > 0) and not r.get('collisions') and all(q >= 0.50 for q in rest)
    put('C5b', ok, 'contact min %s (%s), at-rest gaps person %s car %s' % (cm, r.get('contact_with'), r.get('person_rest_min_m'), r.get('car_rest_min_m')))
    if n in ('s6a', 's6b'):
        c = m.get('crash') or {}
        ok = c.get('hold_t') is not None and c['hold_t'] <= 2.5 and c.get('rolled_30s_m') is not None and c['rolled_30s_m'] <= 1.0 and c.get('mode') is not None
        put('C5c', ok, 'HOLD %s s, rolled %s m' % (c.get('hold_t'), c.get('rolled_30s_m')))
    if n in FULL or n == 's8':
        tr = m.get('trips') or []
        if n == 's8':
            g = m.get('guard') or []; put('C6', r['outcome'] == 'energy guard' and (r.get('odo_m') or 0) < 0.05, 'guard %s' % g)
        else:
            ok = bool(tr) and all(t['wh'] <= 50.0 for t in tr)
            if n in ('s3a', 's3b'): ok = ok and r['soc_end'] >= 0.20
            put('C6', ok, 'trips %s Wh, end SOC %.3f' % ([t['wh'] for t in tr], r['soc_end']))
    if r['expect'] == 'pass': put('C7', r['result'] == 'pass', 'result %s / %s' % (r['result'], r['outcome']))
    else: put('C7', r['result'] == 'alert' and r['outcome'] == EXPECT_OUT[n], 'result %s / %s (expected alert: %s)' % (r['result'], r['outcome'], EXPECT_OUT[n]))
    gr = m.get('grabs') or []; ga = m.get('gates') or []
    if gr or ga:
        ok_g = [g for g in ga if g['ok']]
        put('C8', len(ok_g) >= len(gr) and (len(gr) > 0 or not ga or ok_g), 'gates %s' % ['%s %.3f m %.2f deg %s' % (g['bin'], g['lat_m'], g['yaw_deg'], 'OK' if g['ok'] else 'MISS') for g in ga])
    verdict = 'PASS' if all(v == 'PASS' for v in C.values()) else 'FAIL'
    return dict(key='%s__s%d' % (n, r['seed']), scenario=n, seed=r['seed'], title=r['title'], expect=r['expect'], result=r['result'], outcome=r['outcome'],
                verdict=verdict, crit=C, why=why, alerts=r['alerts'], sim_s=r['sim_time_s'])


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(OUT, '*', 'result.json'))):
        rows.append(score(json.load(open(f))))
    order = ['s1a', 's1b', 's3a', 's3b', 's4a', 's4b', 's4c', 's5a', 's5b', 's6a', 's6b', 's7', 's8', 's9', 's10a', 's10b', 's11a', 's11b', 's12a', 's12b']
    rows.sort(key=lambda q: (order.index(q['scenario']) if q['scenario'] in order else 99, q['seed']))
    base = os.path.dirname(OUT.rstrip('/'))
    json.dump(rows, open(os.path.join(base, 'score.json'), 'w'), indent=1)
    P = sum(q['verdict'] == 'PASS' for q in rows)
    L = ['# B2-F SITL strict score: %d / %d PASS' % (P, len(rows)), '', '| run | expect | outcome | verdict | failed criteria |', '|---|---|---|---|---|']
    for q in rows:
        fails = ', '.join('%s (%s)' % (k, q['why'][k]) for k, v in q['crit'].items() if v == 'FAIL') or '-'
        L.append('| %s | %s | %s / %s | %s | %s |' % (q['key'], q['expect'], q['result'], q['outcome'], q['verdict'], fails))
    open(os.path.join(base, 'score.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
