#!/usr/bin/env python3
"""Revision 5: how close can a person appear in front of the robot and still not be touched, when lidar and camera both watch the way ahead?
Monte Carlo over the moment the person appears. Stopping distances are the MuJoCo results of revision 5 (touch/command to standstill, 0.15 s
brake reaction included). Detection figures are ASSUMED until measured on the built robot:
  lidar  10 scans/s, a standing adult's legs seen in a scan with probability 0.90 (a small child or dog 0.80)
  camera  5 frames/s on the companion's NPU, a person found in a frame with probability 0.85 by day, 0.60 at night with the infra-red light
  two detections in a row are asked for before the robot brakes (rejects single false readings); processing delay 0.15 s
usage: people_mc.py <pstop json of revision 5> <out json>"""
import json, sys, numpy as np
P = json.load(open(sys.argv[1])); rng = np.random.default_rng(5)
def stop_m(case):   # MuJoCo stop distance for (label, v): from the person-stop table
    return case
LID = dict(hz=10.0, p_adult=0.90, p_small=0.80); CAM = dict(hz=5.0, p_day=0.85, p_night=0.60); NEED = 2; PROC = 0.15
def t_detect(n, hz, p):
    """time from appearance to the NEED-th consecutive detection (s); the first sample comes at a random phase"""
    t = rng.random(n) / hz; run = np.zeros(n, int); done = np.zeros(n, bool); out = np.full(n, 99.0)
    for k in range(200):
        hit = rng.random(n) < p; run = np.where(hit, run + 1, 0); new = (~done) & (run >= NEED); out[new] = t[new]; done |= new; t = t + 1.0 / hz
        if done.all(): break
    return out
def case(v, stop, n=200000, small=False, night=False, lid=True, cam=True):
    tl = t_detect(n, LID['hz'], LID['p_small' if small else 'p_adult']) if lid else np.full(n, 99.0)
    tc = t_detect(n, CAM['hz'], CAM['p_night' if night else 'p_day']) if cam else np.full(n, 99.0)
    td = np.minimum(tl, tc) + PROC; need = v * td + stop      # distance used from the appearance to standstill
    return dict(d50=round(float(np.percentile(need, 50)), 2), d99=round(float(np.percentile(need, 99)), 2), d999=round(float(np.percentile(need, 99.9)), 2))
ROWS = [('level, full bin, 0.4 m/s', 0.4, 'full_0_0.4'), ('level, empty, 0.4 m/s', 0.4, 'empty_0_0.4'), ('6 % down, full bin, 0.3 m/s', 0.3, 'full_6_0.3'), ('6 % down, empty, 0.3 m/s', 0.3, 'empty_6_0.3'),
        ('12 % down, full bin, 0.2 m/s', 0.2, 'full_12_0.2'), ('12 % down, empty, tail first, 0.2 m/s', 0.2, 'rev_12_0.2'), ('12 % down on wet leaves, empty, tail first, 0.2 m/s', 0.2, 'rev_12_0.2_leaf')]
out = []
print('distance a person can appear at and still not be touched (m): median / 99 % / 99.9 % of cases'); print('%-52s %6s | %-18s %-18s %-18s %-18s' % ('', 'stop m', 'lidar + camera', 'lidar only', 'camera only, day', 'camera only, night'))
for name, v, key in ROWS:
    if key not in P: continue
    s = P[key]; r = dict(name=name, v=v, stop_m=s)
    for lab, kw in (('both', {}), ('lidar', dict(cam=False)), ('cam_day', dict(lid=False)), ('cam_night', dict(lid=False, night=True)), ('both_night_small', dict(night=True, small=True))): r[lab] = case(v, s, **kw)
    out.append(r); f = lambda d: '%.2f / %.2f / %.2f' % (d['d50'], d['d99'], d['d999'])
    print('%-52s %6.3f | %-18s %-18s %-18s %-18s' % (name, s, f(r['both']), f(r['lidar']), f(r['cam_day']), f(r['cam_night'])))
json.dump(dict(assumed=dict(lidar=LID, camera=CAM, need_in_a_row=NEED, processing_s=PROC), rows=out), open(sys.argv[2], 'w'), indent=1)
