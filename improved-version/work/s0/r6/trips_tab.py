#!/usr/bin/env python3
"""Trip time and energy by speed set. usage: trips_tab.py <out json> <label=sitl_out dir> ..."""
import json, glob, sys, os
out = []
for arg in sys.argv[2:]:
    lab, d = arg.split('=')
    for f in sorted(glob.glob('/home/claude/sitl_out/%s/runs/*/result.json' % d)):
        r = json.load(open(f)); m = r['metrics']
        if not m.get('trips'): continue
        for t in m['trips']:
            out.append(dict(set=lab, scen=r['scenario'], seed=r['seed'], kind=t['kind'].split(' ')[0], what=t['kind'], min=t['min'], wh=t['wh'], clk0=t['clk0'], clk1=t['clk1'], result=r['result'], outcome=r['outcome'], soc_end=r['soc_end'], hedge=r['hedge_min_m'],
                            pauses=len(m.get('ppl_pauses', [])), pf=len(m.get('prot_stops', [])), fast=m.get('r6_fast')))
json.dump(out, open(sys.argv[1], 'w'), indent=1)
labs = []
for o in out:
    if o['set'] not in labs: labs.append(o['set'])
print('%-10s %-8s %5s  %-22s %-22s %s' % ('set', 'kind', 'trips', 'minutes', 'Wh', 'least hedge m'))
for lab in labs:
    for kind in ('drop', 'pickup'):
        q = [o for o in out if o['set'] == lab and o['kind'] == kind]
        if q: print('%-10s %-8s %5d  %5.1f to %5.1f (mean %4.1f)  %5.1f to %5.1f (mean %4.1f)  %.3f' % (lab, kind, len(q), min(o['min'] for o in q), max(o['min'] for o in q), sum(o['min'] for o in q) / len(q), min(o['wh'] for o in q), max(o['wh'] for o in q), sum(o['wh'] for o in q) / len(q), min(o['hedge'] for o in q)))
