#!/usr/bin/env python3
"""rev2 independent re-test: per-run vision / lidar / energy metrics from result.json (post-processing only).
usage: rev2_metrics.py <runs_dir> [<score.json>] -> prints JSON list to stdout
Definitions
 lidar line-up error  = TRUE lateral offset of the robot from the TRUE pre-grab pose at the first rear-camera check (k=0),
                        i.e. where the lidar-refined bin estimate + EKF put the robot before any camera correction.
                        (runs without cam_checks: the first pre-grab gate attempt, truth.)
 camera error         = lat_cam - lat_true at each camera check (the simulated camera reading vs truth).
 re-approaches        = camera-triggered re-alignments (|lat_cam| > CAM_TOL) + frozen-gate re-alignments (gate MISS on attempt 0).
 refusals             = 'could not line up ... not grabbing' alerts (frozen gate missed twice) + lowlight camera no-detection checks.
"""
import json, os, sys, glob

def clk_min(s):
    if not s: return None
    d, hm = s.split(' '); h, m = hm.split(':'); return int(h) * 60 + int(m)

def one(r):
    m = r['metrics']; cc = m.get('cam_checks') or []; ga = m.get('gates') or []; gr = m.get('grabs') or []
    bins = []
    for b in [g['bin'] for g in gr] + [g['bin'] for g in ga]:
        if b not in bins: bins.append(b)
    per = []
    for b in bins:
        c = [q for q in cc if q['bin'] == b]; g = [q for q in ga if q['bin'] == b]
        c0 = next((q for q in c if q.get('lat_true') is not None), None)
        lineup = c0['lat_true'] if c0 else (g[0]['lat_m'] if g else None)
        cam_err = [round(q['lat_cam'] - q['lat_true'], 3) for q in c if q.get('lat_cam') is not None]
        cam_re = sum(1 for q in c if q.get('lat_cam') is not None and abs(q['lat_cam']) > 0.025 and q['k'] <= 1)
        gate_re = sum(1 for q in g if not q['ok'] and q['attempt'] == 0)
        per.append(dict(bin=b, lineup_m=lineup, cam=[(q.get('lat_cam'), q.get('lat_true')) for q in c], cam_err=cam_err,
                        cam_miss=sum(1 for q in c if q.get('miss')), cam_reapp=cam_re, gate_reapp=gate_re,
                        gate=[(q['lat_m'], q['yaw_deg'], q['ok']) for q in g], grabbed=any(q['bin'] == b for q in gr)))
    refus = sum(1 for a in r['alerts'] if 'could not line up' in str(a))
    tr = m.get('trips') or []
    return dict(key='%s__s%d' % (r['scenario'], r['seed']), scenario=r['scenario'], seed=r['seed'], result=r['result'], outcome=r['outcome'],
                hedge_min_m=r.get('hedge_min_m'), trips_wh=[t['wh'] for t in tr], trip_min=[t['min'] for t in tr], soc_end=r['soc_end'],
                energy_wh=r['energy_wh'], last_dock=m.get('last_dock_clock'), first_motion=m.get('first_motion_clock'),
                placements=[(p['where'], p['err_m'], p['handle_err_deg']) for p in (m.get('placements') or [])],
                dock_lat_mm=[g['lat_mm'] for g in gr], bins=per, refusals=refus, guard=m.get('guard'), yard_exit=m.get('yard_exit'))

if __name__ == '__main__':
    out = []
    for f in sorted(glob.glob(os.path.join(sys.argv[1], '*', 'result.json'))):
        out.append(one(json.load(open(f))))
    if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
        sc = {q['key']: q for q in json.load(open(sys.argv[2]))}
        for o in out:
            q = sc.get(o['key'].split('_m122')[0]) or sc.get(o['key'])
            if q: o['verdict'] = q['verdict']; o['fails'] = {k: q['why'][k] for k, v in q['crit'].items() if v == 'FAIL'}
    json.dump(out, sys.stdout, indent=1)
