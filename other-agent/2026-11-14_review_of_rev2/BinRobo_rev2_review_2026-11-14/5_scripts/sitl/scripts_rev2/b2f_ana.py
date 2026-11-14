"""quick look at one run: python b2f_ana.py <key> [every]"""
import json, sys, os, numpy as np
OUT = os.environ.get('B2F_OUT', '/workspace/work/out/b2f_lane/sitl/runs')
k = sys.argv[1]; ev = int(sys.argv[2]) if len(sys.argv) > 2 else 50
r = json.load(open(os.path.join(OUT, k, 'result.json')))
print({q: r[q] for q in ['result', 'outcome', 'alerts', 'sim_time_s', 'hedge_min_m', 'hedge_min_at', 'legal_min_m', 'contact_min_m', 'contact_with', 'person_rest_min_m', 'car_rest_min_m', 'energy_wh', 'odo_m', 'collisions', 'chain_trips']})
m = r['metrics']; print('metrics', json.dumps({q: v for q, v in m.items()})[:1500])
print('chunks', r['chunks'])
T = json.load(open(os.path.join(OUT, k, 'trace.json')))['trace']
mov = [x for x in T if abs(x['v']) > 0.1 and x['state'].startswith('LANE') and x['ltg'] is not None]
if mov:
    print('lane samples', len(mov), 'lat-ltg mean %.3f sd %.3f' % (np.mean([x['lat'] - x['ltg'] for x in mov]), np.std([x['lat'] - x['ltg'] for x in mov])))
for x in T[::ev]:
    print(x['t'], x['state'], x['op'], 's%.1f' % x['s'], 'lat%.2f' % x['lat'], x['ltg'], 'v%.2f' % x['v'], x['spd'], x['mode'], x['fix'], 'hc%.2f' % x['hc'], x['clk'])
for e in r['events']:
    if e['kind'] != 'fw' or 'mode' in e['text'] or 'FENCE' in e['text']: print('  EV', e['t'], e['kind'], e['text'])
