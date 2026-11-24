#!/usr/bin/env python3
"""What the score does not show, for a set of mission runs: trips, pauses, stops, placements, clearances, turn directions.
usage: suite_extra.py <sitl_out name> [<out json>]"""
import json, glob, sys, os, collections
d = '/home/claude/sitl_out/' + sys.argv[1]; rows = []
for f in sorted(glob.glob(d + '/runs/*/result.json')):
    r = json.load(open(f)); m = r['metrics']
    rows.append(dict(key=os.path.basename(os.path.dirname(f)), scen=r['scenario'], seed=r['seed'], expect=r['expect'], result=r['result'], outcome=r['outcome'], alerts=[a[:70] for a in r['alerts']],
                     trips=[(t['kind'], t['min'], t['wh'], t['clk0'], t['clk1']) for t in m.get('trips', []) if 'min' in t], hedge=r['hedge_min_m'], hedge_at=r.get('hedge_min_at'),
                     contact_min=r.get('contact_min_m'), contact_with=r.get('contact_with'), collisions=len(r['collisions']),
                     place=[(p['err_m'], p['handle_err_deg']) for p in m.get('placements', [])], seat=[s.get('err_mm', s.get('err')) for s in m.get('seat_checks', [])],
                     pauses=[dict(where=p.get('where'), by=p.get('by'), s=p.get('s'), range=p.get('range'), wait=p.get('wait_s'), person=p.get('person'), static=p.get('passed_static'), v_in=p.get('v_in')) for p in m.get('ppl_pauses', [])],
                     pf=m.get('prot_stops', []), stops=len(m.get('stops', [])), pivot_way=m.get('pivot_way', []), soc_end=r['soc_end'], last_dock=m.get('last_dock_clock'), first=m.get('first_motion_clock'), sim_min=round(r['sim_time_s'] / 60.0, 1)))
if len(sys.argv) > 2: json.dump(rows, open(sys.argv[2], 'w'), indent=1)
print('%d runs in %s' % (len(rows), sys.argv[1]))
by = collections.defaultdict(list)
for q in rows: by[q['scen']].append(q)
print('outcome against expectation, by scenario:')
for s, qs in by.items(): print('  %-5s expect %-6s | %s' % (s, qs[0]['expect'], ', '.join('s%d %s/%s' % (q['seed'], q['result'], q['outcome']) for q in qs)))
tr = [(q['scen'], q['seed'], t) for q in rows for t in q['trips']]
for kind in ('drop', 'pickup'):
    tt = [t for _, _, t in tr if t[0].startswith(kind)]
    if tt: print('%s trips: %d, %.1f to %.1f min (mean %.1f), %.1f to %.1f Wh (mean %.1f)' % (kind, len(tt), min(t[1] for t in tt), max(t[1] for t in tt), sum(t[1] for t in tt) / len(tt), min(t[2] for t in tt), max(t[2] for t in tt), sum(t[2] for t in tt) / len(tt)))
for q in rows:
    if q['scen'] in ('s3a', 's3b'): print('  %s s%d: %s | first motion %s, last dock %s, charge left %.0f %%' % (q['scen'], q['seed'], ', '.join('%.1f min %.1f Wh' % (t[1], t[2]) for t in q['trips']), q['first'], q['last_dock'], 100 * q['soc_end']))
h = min(rows, key=lambda q: q['hedge'] if q['hedge'] is not None else 9); print('least hedge clearance %.3f m (%s s%d at %s)' % (h['hedge'], h['scen'], h['seed'], h['hedge_at']))
pl = [(p[0], p[1], q['scen'], q['seed']) for q in rows for p in q['place']]
if pl: print('placements: %d, worst %.3f m (%s s%d), mean %.3f m; worst handle angle %.1f deg' % (len(pl), max(pl)[0], max(pl)[2], max(pl)[3], sum(p[0] for p in pl) / len(pl), max(abs(p[1]) for p in pl)))
cm = [(q['contact_min'], q['contact_with'], q['scen'], q['seed']) for q in rows if q['contact_min'] is not None]
if cm: print('nearest approach to a bin, car or other standing thing: %.3f m (%s, %s s%d)' % min(cm))
print('runs with a contact: %s' % ([(q['scen'], q['seed']) for q in rows if q['collisions']] or 'none'))
ps = [(q['scen'], q['seed'], p) for q in rows for p in q['pauses']]
print('stand-still pauses: %d in %d runs; by place: %s; by sensor: %s; called a person: %d; passed as a static thing: %d' % (len(ps), len(set((a, b) for a, b, _ in ps)), dict(collections.Counter(p['where'] for _, _, p in ps)), dict(collections.Counter(p['by'] for _, _, p in ps)), sum(1 for _, _, p in ps if p['person']), sum(1 for _, _, p in ps if p['static'])))
pc = collections.Counter(a for a, _, _ in ps); print('   pauses by scenario: %s' % dict(pc))
wt = [p['wait'] for _, _, p in ps if p['wait'] is not None]
if wt: print('   waits: %.1f to %.1f s, total %.0f s' % (min(wt), max(wt), sum(wt)))
print('protective-field stops: %d; lidar path stops (old rule): %d' % (sum(len(q['pf']) for q in rows), sum(q['stops'] for q in rows)))
pw = [w for q in rows for w in q['pivot_way']]
if pw: print('near-half turns checked both ways: %d; one way blocked (under 0.15 m) in %d; clearance on the way taken: %.2f m at least' % (len(pw), sum(1 for w in pw if min(w['ccw_m'], w['cw_m']) < 0.15), min(max(w['ccw_m'], w['cw_m']) for w in pw)))
al = collections.Counter(a for q in rows for a in q['alerts']); print('alerts:'); [print('   %3d x %s' % (n, a)) for a, n in al.most_common()]
