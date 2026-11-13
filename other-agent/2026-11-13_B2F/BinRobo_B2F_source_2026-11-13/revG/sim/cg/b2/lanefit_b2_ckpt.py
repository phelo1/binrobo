#!/usr/bin/env python3
"""Checkpointed foreground wrapper for lanefit_b2.py (same computation as its __main__, piece by piece; each finished piece
cached in b2/lanefit_<name>.ckpt.json so the run can be split into <2 min foreground calls).
usage: lanefit_b2_ckpt.py <design.json> <budget_s>; prints DONE when res/lanefit_<name>.json is written."""
import os, sys, json, time, numpy as np
T0=time.time(); H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H)
import lanefit_b2 as L2
LF=L2.LF
D=json.load(open(sys.argv[1])); BUD=float(sys.argv[2])
L2.KL=D.get('kl_gap'); L2.SRUN=D.get('pivot_strategy')=='srun'; L2.GUARD=D.get('guard',0.25)
d=LF.Design(D); ck=os.path.join(H,'lanefit_%s.ckpt.json'%d.name)
C=json.load(open(ck)) if os.path.exists(ck) else {}
jobs=[]
for sg in (1,-1):
    for ld in (True,False): jobs.append(('sweep|%s %s'%('down' if sg>0 else 'up','loaded' if ld else 'empty'),lambda sg=sg,ld=ld: LF.lane_sweep(d,ld,sg)))
jobs+= [('lane_pivot',lambda: LF.lane_pivot_profile(d.r_empty)),('lane_pivot_loaded',lambda: LF.lane_pivot_profile(d.r_load)),
        ('yard_dock',lambda: LF.yard_dock(d)),('mouth',lambda: LF.mouth(d))]
for ms in ('drop','pickup'):
    for n in (1,2,3):
        for ht in ('lane','road'): jobs.append(('seq|%s n%d handle-to-%s'%(ms,n,ht),lambda ms=ms,n=n,ht=ht: LF.sequence(d,n,ht,ms)))
for k,f in jobs:
    if k in C: continue
    t=time.time(); v=f(); C[k]=json.loads(json.dumps(v,default=float)); json.dump(C,open(ck,'w'),default=float)
    print('piece',k,'%.0fs'%(time.time()-t),flush=True)
    if time.time()-T0>BUD: break
if all(k in C for k,_ in jobs):
    R=dict(design=d.name,r_empty=round(d.r_empty,3),r_load=round(d.r_load,3),pivot_D_empty=round(2*d.r_empty,2),pivot_D_load=round(2*d.r_load,2),half_w=d.half_w,kl_gap=L2.KL,guard=L2.GUARD,pivot_strategy=D.get('pivot_strategy'))
    R['sweep']={k.split('|')[1]:C[k] for k,_ in jobs if k.startswith('sweep|')}
    mins=[v['min_clear_m'] for v in R['sweep'].values()]; R['sweep_min']=min(mins); R['sweep_PASS_strict']=R['sweep_min']>0; R['sweep_margin_vs_p95']=round(R['sweep_min']-LF.EST_P95,3)
    R['lane_pivot']=C['lane_pivot']; R['lane_pivot_loaded']=C['lane_pivot_loaded']
    R['lane_pivot_frac_empty']=round(np.mean([m>0 for _,m in R['lane_pivot']]),3); R['lane_pivot_frac_loaded']=round(np.mean([m>0 for _,m in R['lane_pivot_loaded']]),3)
    nar=[m for s_,m in R['lane_pivot_loaded'] if 500<=s_<=516]; R['narrowing_pivot_margin_loaded']=min(nar) if nar else None
    R['yard_dock']=C['yard_dock']; R['mouth']=C['mouth']
    R['sequences']={k.split('|')[1]:C[k] for k,_ in jobs if k.startswith('seq|')}
    allm=[st[1] for v in R['sequences'].values() for st in v['steps'] if st[1] is not None]; R['sequence_min_margin']=min(allm); R['sequences_all_ok']=all(v['ok'] for v in R['sequences'].values())
    json.dump(R,open(os.path.join(H,'res','lanefit_%s.json'%d.name),'w'),indent=1,default=float)
    print('DONE',d.name,'pivot D',R['pivot_D_empty'],R['pivot_D_load'],'sweep min',R['sweep_min'],{k:(v['min_clear_m'],v['at_s']) for k,v in R['sweep'].items()},'seq min',R['sequence_min_margin'],'all ok',R['sequences_all_ok'])
else: print('ckpt',len(C),'/',len(jobs))
