#!/usr/bin/env python3
"""Replay the frozen world energy model on a saved trace and split each trip into mass-proportional and time-based parts.
usage: rev2_energy_split.py <run_dir> <robot_mass_kg>   (post-processing only)"""
import sys, os, json, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'scripts_base'))
import b2f_scen as SCN
rd, mrob = sys.argv[1], float(sys.argv[2])
res = json.load(open(os.path.join(rd, 'result.json'))); tr = json.load(open(os.path.join(rd, 'trace.json')))['trace']
sc = SCN.build(res['scenario'], res['seed']); w = sc['world']; S = w.S
bm = {k: b['mass'] for k, b in w.bins.items()}
T = np.array([q['t'] for q in tr]); out = []
for trip in res['metrics']['trips']:
    i0, i1 = np.searchsorted(T, trip['t0']), np.searchsorted(T, trip['t1'])
    Em = 0.0; Emr = 0.0; vprev = 0.0
    for i in range(max(i0, 1), i1):
        q = tr[i]; dt = q['t'] - tr[i - 1]['t']
        if dt <= 0: continue
        v = q['v']; a = (v - vprev) / dt; vprev = v
        gx, gy = S.ter.grad(q['x'], q['y']); grade = gx * math.cos(q['yaw']) + gy * math.sin(q['yaw'])
        mv = 1 if abs(v) > 0.01 else 0
        f_per_kg = 9.81 * 0.03 * mv + 9.81 * grade * (1 if v >= 0 else -1) * mv + max(a, 0) * (1 if v >= 0 else -1)
        m = mrob + (bm.get(q['carry'], 0.0) if q['carry'] else 0.0)
        ptr = max(0.0, m * f_per_kg * abs(v)) / 0.60 + 0.08 * m * 9.81 * abs(q['w']) * 0.40 / 0.60
        e = ptr * dt / 3600.0; Em += e; Emr += e * mrob / m
    out.append(dict(kind=trip['kind'], wh=trip['wh'], min=trip['min'], traction_wh=round(Em, 2), traction_robot_share_wh=round(Emr, 2),
                    other_wh=round(trip['wh'] - Em, 2), dwh_per_kg_robot=round(Emr / mrob, 4)))
print(json.dumps(out, indent=1))
