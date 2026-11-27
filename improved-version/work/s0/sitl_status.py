#!/usr/bin/env python3
"""List the outcome of every finished SITL run in <out>/runs. usage: sitl_status.py <out_name> [stored score.json]"""
import json, os, sys, glob
out = '/home/claude/sitl_out/%s/runs' % sys.argv[1]
st = {}
if len(sys.argv) > 2:
    for r in json.load(open(sys.argv[2]))['runs'] if isinstance(json.load(open(sys.argv[2])), dict) and 'runs' in json.load(open(sys.argv[2])) else []: st[r.get('run') or r.get('key')] = r
for d in sorted(glob.glob(out + '/*/result.json')):
    r = json.load(open(d)); k = d.split('/')[-2]; m = r['metrics']
    g = ['%s%+.3f' % ('ok' if q['ok'] else 'MISS', q['lat_m']) for q in m.get('gates', [])]
    print('%-10s %-6s %-36s sim %6.0f s hedge %s gates %s setdowns %s' % (k, r['result'], r['outcome'][:36], r['sim_time_s'], r.get('hedge_min_m'), g, [round(q.get('err_m', 9), 3) for q in m.get('setdowns', [])]))
