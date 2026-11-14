#!/usr/bin/env python3
"""[independent tester 2026-11-14] Record ONE G1 pick-up trial of the revision 2 model (simB2hx_r2m, logging-only wrapper of simB2hx_r2)
exactly as runB2.py 'grab <BIN> <n> <seed>' builds trial i (same mc_g5 sample, comb offset, seed, one re-dock on no_dock/safe_miss).
Run with the same env as the q_r2.txt gate lines.  usage: rec_r2_grab.py <BIN> <n> <seed> <i> <out_stem>
-> <out_stem>.npz (25 fps body poses q, t, phase, lift force, nib y) + <out_stem>.json (result)."""
import os, sys, json, numpy as np
P='/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c'; CG=P+'/revG/sim/cg'
sys.path[:0]=[CG+'/h2',CG+'/b2',CG+'/it1',CG,P+'/revG/sim/g6']
import mujoco, importlib, mc_g5
from bins_g5 import BINS
B=importlib.import_module(os.environ.get('CMP_SIM','simB2hx_r2m'))
b,n,seed,i,stem=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
Bn=BINS[b]; rng=np.random.default_rng(seed)
PS=[mc_g5.sample(Bn,k,rng) for k in range(n)]; CD=[float(rng.uniform(-0.010,0.010)) for k in range(n)]
p=dict(PS[i]); p['comb_d']=CD[i]; pp=B.bin_params(b,p)
S=B.SimB(b,pp,mu=p['mu'],tug_pose=B.start_pose(pp,p['dy'],p['dyaw'])); R=B.RunnerB(S)
BODIES=['tug','wheelL','wheelR','cforkL','cforkR','cwheelL','cwheelR','lift','comb','keeper','padbase','pad','bin','bwL','bwR','lid']
bid=[mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_BODY,nm) for nm in BODIES]
Q=[];T=[];PH=[];LF=[]; every=int(round(1/25/R.dt)); st0=R.step
def step():
    st0()
    if R.i%every==0:
        Q.append(np.hstack([S.d.xpos[bid],S.d.xquat[bid]]).astype(np.float32)); T.append(R.i*R.dt); PH.append(str(R.phase))
        try: LF.append(float(abs(S.lift_force())))
        except Exception: LF.append(0.0)
R.step=step
o=B.grab(R,seed=seed*1000+i); o['first_result']=o['result']
if o['result'] in ('safe_miss','no_dock') and not getattr(R,'reapp',False):
    R.phase='R Retry: pull forward 0.6 m, re-dock'; x0=S.d.xpos[S.bid['tug']].copy(); psi=S.rpy()[2]
    R.ctrl_fn=B.heading_hold(R,0.15,psi); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=0.6,8.0); R.ctrl_fn=None; R.hold(); R.run_for(0.4)
    R.reapp=True; o2=B.grab(R,seed=seed*1000+i+500); o2['first_result']=o['first_result']; o2['retried']=True; o=o2
R.run_for(1.5)
o['false_hold']=bool(o.get('claim') and not o.get('captured')); o['params']=p
np.savez_compressed(stem+'.npz',q=np.array(Q),t=np.array(T),ph=np.array(PH),lf=np.array(LF))
json.dump(dict(bin=b,seed=seed,i=i,result=o,events=R.events,mass_tug=float(S.tug_mass) if hasattr(S,'tug_mass') else None),open(stem+'.json','w'),indent=1,default=str)
print('REC',b,seed,i,o['result'],o['first_result'],len(Q),'frames')
