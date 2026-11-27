#!/usr/bin/env python3
"""One markdown row per mission run: time, stops, clearances, placement, line-ups. usage: trips_md.py <out json> <label>=<sitl_out name> ..."""
import json, glob, sys, os
rows = []
for a in sys.argv[2:]:
    lab, d = a.split('=')
    for f in sorted(glob.glob('/home/claude/sitl_out/%s/runs/*/result.json' % d)):
        r = json.load(open(f)); m = r['metrics']; pp = m.get('ppl_pauses') or []
        lane = [p for p in pp if p.get('where') == 'lane']; other = [p for p in pp if p.get('where') != 'lane']
        tr = [t for t in m.get('trips', []) if 'min' in t]; gates = m.get('gates') or []
        rows.append(dict(set=lab, run=d, scen=r['scenario'], seed=r['seed'], result=r['result'], outcome=r['outcome'], alerts=[x[:90] for x in r['alerts']],
                         trips=[(t['kind'].split(' ')[0], t['min'], t['wh'], t['clk0'], t['clk1']) for t in tr], sim_min=round(r['sim_time_s'] / 60.0, 1), soc_end=r.get('soc_end'),
                         corridor_stops=len(m.get('stops') or []), near_field_trips=len(m.get('prot_stops') or []),
                         pauses_lane=[(round(p['s']), p.get('by'), p['range'], p.get('wait_s'), bool(p.get('person'))) for p in lane],
                         pauses_other=[(p.get('where'), round(p['s']), p.get('by'), p['range'], p.get('wait_s'), bool(p.get('person'))) for p in other],
                         hedge=r['hedge_min_m'], contact_min=r.get('contact_min_m'), contact_with=r.get('contact_with'), contacts=len(r['collisions']),
                         place=[p['err_m'] for p in m.get('placements') or []], gate_tries=max([g['attempt'] for g in gates], default=-1) + 1, grabs=[g['result'][:20] for g in m.get('grabs') or []],
                         last_dock=m.get('last_dock_clock'), fast=m.get('r6_fast')))
json.dump(rows, open(sys.argv[1], 'w'), indent=1)
for o in rows:
    print('%-8s %-4s s%-3s %-16s | trips %s | corridor stops %d, near-field %d | pauses lane %s other %s | hedge %s | place %s | contacts %d nearest %s %s | gate tries %d | dock %s | alerts %s' % (
        o['set'], o['scen'], o['seed'], o['outcome'][:16], [(k, mn) for k, mn, wh, c0, c1 in o['trips']], o['corridor_stops'], o['near_field_trips'], o['pauses_lane'], o['pauses_other'], o['hedge'], o['place'], o['contacts'], o['contact_min'], o['contact_with'], o['gate_tries'], o['last_dock'], o['alerts'][:1]))
