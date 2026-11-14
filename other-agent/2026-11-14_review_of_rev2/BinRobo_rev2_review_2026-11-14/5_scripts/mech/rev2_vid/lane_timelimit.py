#!/usr/bin/env python3
"""[tester] time-limit re-score of every rev2 lane run (work/b2f_lanephys/runs_r2b_*): longest interval in which the chainage s
takes to gain 5 m of net progress (first passage, direction of travel; includes planned stops and the grab). Rule added by the tester (not in the frozen lane
criteria): any run stuck > 120 s is a FAIL in practice. -> /workspace/work/out/rev2/mech/lane_timelimit_r2b.json"""
import os, glob, json, numpy as np
L='/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/work/b2f_lanephys'; LIM=120.0; GAIN=5.0
def longest(t,s):
    p=s if s[-1]>=s[0] else -s
    pm=np.maximum.accumulate(p)          # best progress so far
    best=(0.0,0,len(t)-1,False)
    for i in range(len(t)):
        j=np.searchsorted(pm,p[i]+GAIN)  # first time progress reaches p[i]+5 m
        if j>=len(t): d=t[-1]-t[i]; end=True
        else: d=t[j]-t[i]; end=False
        if d>best[0]: best=(d,i,min(j,len(t)-1),end)
    return best
out=[]
for d in sorted(glob.glob(L+'/runs_r2b_*/*')):
    if os.path.islink(d): continue
    fs=sorted(glob.glob(d+'/rec_*.npz'))
    if not fs: continue
    t=np.concatenate([np.load(f)['t'] for f in fs]).astype(float); s=np.concatenate([np.load(f)['hud'][:,0] for f in fs]).astype(float)
    k=slice(None,None,5); t,s=t[k],s[k]          # 5 Hz
    dur,a,b,endst=longest(t,s)
    rj=d+'/result.json'; r=json.load(open(rj)) if os.path.exists(rj) else None
    v=r['verdict'] if r else ('TRUNCATED' if glob.glob(d+'/TRUNCATED') else 'INCOMPLETE')
    o=dict(dir=os.path.basename(os.path.dirname(d)),run=os.path.basename(d),verdict_frozen=v,sim_s=round(float(t[-1]-t[0]),1),
           longest_stuck_s=round(dur,1),stuck_at_s=round(float(np.median(s[a:b+1])),1),stuck_t0=round(float(t[a]),1),stuck_t1=round(float(t[b]),1),
           E_Wh=(r or {}).get('energy_Wh'),still_stuck_at_end=bool(endst and dur>LIM),end_window_open=bool(endst))
    o['verdict_timelimit']='FAIL' if (dur>LIM or v=='FAIL' or o['still_stuck_at_end']) else (v if v!='TRUNCATED' else 'TRUNCATED')
    out.append(o); print(json.dumps(o))
json.dump(dict(rule='stuck time = longest time to gain 5 m of net chainage progress (includes grab/set-down/planned stops, all < 45 s); FAIL if > 120 s (tester rule, not frozen)',runs=out),open('/workspace/work/out/rev2/mech/lane_timelimit_r2b.json','w'),indent=1)
