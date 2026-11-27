#!/usr/bin/env python3
"""Pivot tests (someone walks up at a turn on the spot): what the robot did, from the trace and the result file.
usage: piv_an.py <run dir> ...   (run inside the settings: source r6/env_r6_fast.sh first, for the robot outline)"""
import sys, json, glob, math, os
sys.path.insert(0, '/home/claude/b2f_run/sitl/b2f/scripts')
from b2f_world import ROB
def gap(r, m):
    c, s = math.cos(r['yaw']), math.sin(r['yaw']); dx, dy = m[0] - r['x'], m[1] - r['y']
    bx, by = dx * c + dy * s, -dx * s + dy * c
    ex = max(ROB['x0'] - bx, bx - ROB['x1'], 0.0); ey = max(abs(by) - ROB['hw'], 0.0)
    return math.hypot(ex, ey) - m[2], math.hypot(dx, dy)
out = {}
for d in sys.argv[1:]:
    rd = glob.glob(d.rstrip('/') + '/runs/*/')[0]; tr = json.load(open(rd + 'trace.json'))['trace']; res = json.load(open(rd + 'result.json'))
    rows = [(r, r['mv'][0]) for r in tr if r.get('mv')]
    g = [(r['t'], *gap(r, m), r['w'], r['v'], r['yaw'], r['state'], r['mode']) for r, m in rows]
    t_app = g[0][0]; turning = lambda x: abs(x[3]) > 0.02 and x[7] != 'HOLD'
    in3 = [x for x in g if x[1] < 3.0]; t3 = in3[0][0] if in3 else None
    turn_in3 = [x for x in in3 if turning(x)]
    piv = [x for x in g if x[6].startswith('PIVOT')]; t_piv = piv[0][0] if piv else None
    hold = [x for x in g if x[7] == 'HOLD']; t_hold = hold[0][0] if hold else None
    # yaw travelled while the person was within 3 m of the outline (twitch of a standing robot included)
    yaw_in3 = sum(abs((b[5] - a[5] + math.pi) % (2 * math.pi) - math.pi) for a, b in zip(in3, in3[1:]) if b[0] - a[0] < 0.5 and b[7] != 'HOLD' and a[7] != 'HOLD')
    mn = min(g, key=lambda x: x[1]); mn_turn = min(turn_in3, key=lambda x: x[1]) if turn_in3 else None
    pp = res['metrics'].get('ppl_pauses', []); pv = [p for p in pp if p.get('where') == 'pivot' and p['t'] >= t_app - 1]
    o = dict(run=('/'.join(d.rstrip('/').split('/')[-2:]) if 'before_fix' in d else os.path.basename(d.rstrip('/'))), result=res['result'], outcome=res['outcome'], contacts=len(res.get('collisions', [])),
             person_appears_t=t_app, state_then=g[0][6], pivot_from_t=t_piv, within_3m_from_t=t3,
             hold_from_t=t_hold, gap_at_hold=round(hold[0][1], 2) if hold else None, axle_at_hold=round(hold[0][2], 2) if hold else None,
             s_from_3m_to_hold=None if (t3 is None or t_hold is None) else round(t_hold - t3, 1),
             turning_with_person_inside_3m_s=round(0.2 * len(turn_in3), 1), deg_turned_with_person_inside_3m=round(math.degrees(yaw_in3), 1),
             nearest_while_turning=None if mn_turn is None else dict(gap=round(mn_turn[1], 2), w=round(mn_turn[3], 3), t=mn_turn[0]),
             nearest=dict(gap=round(mn[1], 2), axle=round(mn[2], 2), w=round(mn[3], 3), v=round(mn[4], 3), mode=mn[7], t=mn[0]),
             pauses=[dict(t=p['t'], by=p['by'], range=p['range'], wait_s=p.get('wait_s'), person=p.get('person')) for p in pv],
             peak_rate_in_turn=round(max(abs(r['w']) for r in tr if r['state'].startswith('PIVOT_LOADED')), 3),
             trip_min=[round(c.get('min', 0), 1) if isinstance(c, dict) else c for c in res.get('chain_trips', [])][:3])
    out[o['run']] = o
    print(json.dumps(o))
if os.environ.get('PIV_OUT'): json.dump(out, open(os.environ['PIV_OUT'], 'w'), indent=1)
