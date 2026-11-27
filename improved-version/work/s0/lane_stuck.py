#!/usr/bin/env python3
"""Stuck-time score for lane runs (the reviewer's rule of 14 Nov, recomputed from my own recordings): the longest time the robot needs to gain 5 m of
net distance along the lane. More than 120 s = FAIL. The time left at the end of a run without another 5 m is printed separately (the robot has arrived).
usage: lane_stuck.py <runs_dir> [<runs_dir> ...] [--json out.json]"""
import sys, os, glob, json
import numpy as np
B = '/home/claude/b2f_run/work/b2f_lanephys'; args = [a for a in sys.argv[1:] if not a.startswith('--')]; out = {}
for d in args:
    for rd in sorted(glob.glob(os.path.join(B, d, '*'))):
        recs = sorted(glob.glob(os.path.join(rd, 'rec_*.npz')))
        if not recs: continue
        T = []; S = []
        for r in recs:
            z = np.load(r, allow_pickle=True); T.append(z['t'].astype(float)); S.append(z['hud'][:, 0].astype(float))
        t = np.concatenate(T); s = np.concatenate(S); o = np.argsort(t, kind='stable'); t = t[o]; s = s[o]; n = len(t); worst = 0.0; at = None; j = 0
        for i in range(0, n, 5):
            j = max(j, i)
            while j < n and abs(s[j] - s[i]) < 5.0: j += 1
            if j >= n: tail = t[-1] - t[i]; break
            if t[j] - t[i] > worst: worst = t[j] - t[i]; at = (float(t[i]), float(s[i]))
        else: tail = 0.0
        res = json.load(open(os.path.join(rd, 'result.json'))) if os.path.exists(os.path.join(rd, 'result.json')) else {}
        k = '%s/%s' % (d, os.path.basename(rd)); out[k] = dict(frozen=res.get('verdict'), stuck_s=round(worst, 1), at_t=at and round(at[0], 1), at_s=at and round(at[1], 1), end_wait_s=round(tail, 1), dist_m=round(abs(s[-1] - s[0]), 1), verdict_120='FAIL' if worst > 120 else 'PASS')
        print('%-34s frozen %-5s  longest time to gain 5 m: %6.1f s (from t %s s, at %s m)  travelled %6.1f m  ->  %s' % (k, res.get('verdict'), worst, at and round(at[0]), at and round(at[1], 1), abs(s[-1] - s[0]), out[k]['verdict_120']))
if '--json' in sys.argv: json.dump(out, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
