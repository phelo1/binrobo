#!/usr/bin/env python3
"""Revision 5.1 (22 Nov): how close can a person appear in front of the robot and still not be touched - same model as revision 5
(r5/people_mc.py), with the speeds of the 5.1 speed rule and the stop distances measured on the real lane's slopes (steepest 8.5 %).
Detection figures are ASSUMED until measured on the built robot: lidar 10 scans/s, adult's legs seen with probability 0.90; camera 5 frames/s,
person found with probability 0.85 by day and 0.60 at night with the infra-red light; two detections in a row; 0.15 s processing.
usage: people_mc_r51.py <pstop table json of r51> <out json>"""
import json, sys, numpy as np
T = json.load(open(sys.argv[1])); rng = np.random.default_rng(5)
def stop(bin_kg, slope, grip, v):
    for r in T:
        if abs(r['bin_kg'] - bin_kg) < 1 and abs(abs(r['slope_pct']) - slope) < 0.05 and abs(r['grip'] - grip) < 0.005 and abs(r['v'] - v) < 0.005: return r['stop_mm'] / 1000.0
    raise KeyError((bin_kg, slope, grip, v))
LID = dict(hz=10.0, p_adult=0.90, p_small=0.80); CAM = dict(hz=5.0, p_day=0.85, p_night=0.60); NEED = 2; PROC = 0.15
def t_detect(n, hz, p):
    t = rng.random(n) / hz; run = np.zeros(n, int); done = np.zeros(n, bool); out = np.full(n, 99.0)
    for k in range(200):
        hit = rng.random(n) < p; run = np.where(hit, run + 1, 0); new = (~done) & (run >= NEED); out[new] = t[new]; done |= new; t = t + 1.0 / hz
        if done.all(): break
    return out
def case(v, s, n=200000, small=False, night=False, lid=True, cam=True):
    tl = t_detect(n, LID['hz'], LID['p_small' if small else 'p_adult']) if lid else np.full(n, 99.0)
    tc = t_detect(n, CAM['hz'], CAM['p_night' if night else 'p_day']) if cam else np.full(n, 99.0)
    need = v * (np.minimum(tl, tc) + PROC) + s
    return dict(d50=round(float(np.percentile(need, 50)), 2), d99=round(float(np.percentile(need, 99)), 2), d999=round(float(np.percentile(need, 99.9)), 2))
ROWS = [('level, full bin, 0.4 m/s', 0.4, (110, 0, 0.30)), ('level, empty, 0.4 m/s', 0.4, (0, 0, 0.30)), ('6 % down, full bin, 0.3 m/s', 0.3, (110, 6, 0.30)), ('6 % down, empty, 0.2 m/s', 0.2, (0, 6, 0.30)),
        ('8.5 % down, full bin, 0.2 m/s', 0.2, (110, 8.5, 0.30)), ('8.5 % down, empty, 0.15 m/s', 0.15, (0, 8.5, 0.30)),
        ('8.5 % down on wet leaves, full bin, 0.2 m/s', 0.2, (110, 8.5, 0.22)), ('8.5 % down on wet leaves, empty, 0.15 m/s', 0.15, (0, 8.5, 0.22))]
out = []
print('distance a person can appear at and still not be touched (m): median / 99 % / 99.9 % of cases'); print('%-46s %6s | %-18s %-18s %-18s %-18s' % ('', 'stop m', 'lidar + camera', 'lidar only', 'camera only, day', 'camera only, night'))
for name, v, (kg, sl, mu) in ROWS:
    s = stop(kg, sl, mu, v); r = dict(name=name, v=v, stop_m=s)
    for lab, kw in (('both', {}), ('lidar', dict(cam=False)), ('cam_day', dict(lid=False)), ('cam_night', dict(lid=False, night=True)), ('both_night_small', dict(night=True, small=True))): r[lab] = case(v, s, **kw)
    out.append(r); f = lambda d: '%.2f / %.2f / %.2f' % (d['d50'], d['d99'], d['d999'])
    print('%-46s %6.3f | %-18s %-18s %-18s %-18s' % (name, s, f(r['both']), f(r['lidar']), f(r['cam_day']), f(r['cam_night'])))
json.dump(dict(assumed=dict(lidar=LID, camera=CAM, need_in_a_row=NEED, processing_s=PROC), rows=out), open(sys.argv[2], 'w'), indent=1)
