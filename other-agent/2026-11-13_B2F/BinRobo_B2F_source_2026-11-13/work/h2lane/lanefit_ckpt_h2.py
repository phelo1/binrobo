#!/usr/bin/env python3
"""Checkpointed foreground wrapper for lanefit_b2.py (same computation as its __main__, piece by piece; each finished piece
cached in b2/lanefit_<name>.ckpt.json so the run can be split into <2 min foreground calls).
usage: lanefit_b2_ckpt.py <design.json> <budget_s>; prints DONE when res/lanefit_<name>.json is written."""
import os, sys, json, time, numpy as np
T0=time.time(); H='/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/work/h2lane/res'; sys.path.insert(0,'/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg/b2')
import lanefit_b2 as L2
PDS=float(os.environ.get('PAD_DS','0'))
if PDS:
    _ds=L2.LF.SC.DROP_SPOTS
    def _sh(S):
        r=_ds(S); return {k:dict(v,s=v['s']-PDS) for k,v in r.items()}
    L2.LF.SC.DROP_SPOTS=_sh
LF=L2.LF
D=json.load(open(sys.argv[1])); BUD=float(sys.argv[2])
L2.KL=D.get('kl_gap'); L2.SRUN=D.get('pivot_strategy')=='srun'; L2.GUARD=D.get('guard',0.25)
d=LF.Design(D); d.name=d.name+('_pad%+.2f'%-PDS if PDS else ''); ck=os.path.join(H,'lanefit_%s.ckpt.json'%d.name)
C=json.load(open(ck)) if os.path.exists(ck) else {}
jobs=[]
for sg in (1,-1):
    for ld in (True,False): jobs.append(('sweep|%s %s'%('down' if sg>0 else 'up','loaded' if ld else 'empty'),lambda sg=sg,ld=ld: LF.lane_sweep(d,ld,sg)))
jobs+= [('lane_pivot',lambda: LF.lane_pivot_profile(d.r_empty)),('lane_pivot_loaded',lambda: LF.lane_pivot_profile(d.r_load)),
        ('yard_dock',lambda: LF.yard_dock(d)),('mouth',lambda: LF.mouth(d))]
import seqsplit as SQ
SEQK=[]
for ms in ('drop','pickup'):
    for n in (1,2,3):
        for ht in ('lane','road'):
            key='%s n%d handle-to-%s'%(ms,n,ht); SEQK.append((key,n))
            if 'seq|'+key in C: continue
            for k in range(n): jobs.append(('seqk|%s|%d'%(key,k),lambda ms=ms,n=n,ht=ht,k=k: SQ.sequence_k(d,n,ht,ms,k)))
def _sig(key,k):
    ms,nn,ht=key.split(' '); n=int(nn[1:]); order=['A','M','F'][:n]
    if ms=='pickup': order=order[::-1]
    st=order[:k] if ms=='drop' else order[k+1:]
    return (ms,ht,order[k],tuple(st))
def _reuse(jk):
    if not jk.startswith('seqk|'): return False
    _,key,k=jk.split('|'); sg=_sig(key,int(k))
    for ck_ in list(C.keys()):
        if ck_.startswith('seqk|'):
            _,key2,k2=ck_.split('|')
            if _sig(key2,int(k2))==sg: C[jk]=C[ck_]; print('reuse',jk,'<-',ck_); return True
    return False
for k,f in jobs:
    if k in C: continue
    if _reuse(k): json.dump(C,open(ck,'w'),default=float); continue
    t=time.time(); v=f(); C[k]=json.loads(json.dumps(v,default=float)); json.dump(C,open(ck,'w'),default=float)
    print('piece',k,'%.0fs'%(time.time()-t),flush=True)
    if time.time()-T0>BUD: break
for key,n in SEQK:
    if 'seq|'+key not in C and all(('seqk|%s|%d'%(key,k)) in C for k in range(n)):
        st=[x for k in range(n) for x in C['seqk|%s|%d'%(key,k)]]; C['seq|'+key]=dict(ok=all(x[1] is None or x[1]>0 for x in st),steps=st)
json.dump(C,open(ck,'w'),default=float)
jobs=[j for j in jobs if not j[0].startswith('seqk|')]+[('seq|'+key,None) for key,_ in SEQK]
if all(k in C for k,_ in jobs):
    R=dict(design=d.name,r_empty=round(d.r_empty,3),r_load=round(d.r_load,3),pivot_D_empty=round(2*d.r_empty,2),pivot_D_load=round(2*d.r_load,2),half_w=d.half_w,kl_gap=L2.KL,guard=L2.GUARD,pivot_strategy=D.get('pivot_strategy'))
    R['sweep']={k.split('|')[1]:C[k] for k,_ in jobs if k.startswith('sweep|')}
    mins=[v['min_clear_m'] for v in R['sweep'].values()]; R['sweep_min']=min(mins); R['sweep_PASS_strict']=R['sweep_min']>0; R['sweep_margin_vs_p95']=round(R['sweep_min']-LF.EST_P95,3)
    R['lane_pivot']=C['lane_pivot']; R['lane_pivot_loaded']=C['lane_pivot_loaded']
    R['lane_pivot_frac_empty']=round(np.mean([m>0 for _,m in R['lane_pivot']]),3); R['lane_pivot_frac_loaded']=round(np.mean([m>0 for _,m in R['lane_pivot_loaded']]),3)
    nar=[m for s_,m in R['lane_pivot_loaded'] if 500<=s_<=516]; R['narrowing_pivot_margin_loaded']=min(nar) if nar else None
    R['yard_dock']=C['yard_dock']; R['mouth']=C['mouth']
    R['sequences']={key:C['seq|'+key] for key,_ in SEQK}
    allm=[st[1] for v in R['sequences'].values() for st in v['steps'] if st[1] is not None]; R['sequence_min_margin']=min(allm); R['sequences_all_ok']=all(v['ok'] for v in R['sequences'].values())
    json.dump(R,open(os.path.join(H,'lanefit_%s.json'%d.name),'w'),indent=1,default=float)
    print('DONE',d.name,'pivot D',R['pivot_D_empty'],R['pivot_D_load'],'sweep min',R['sweep_min'],{k:(v['min_clear_m'],v['at_s']) for k,v in R['sweep'].items()},'seq min',R['sequence_min_margin'],'all ok',R['sequences_all_ok'])
else: print('ckpt',len(C),'/',len(jobs))
