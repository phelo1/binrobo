#!/usr/bin/env python3
"""[tester] pick-up summary at 119.39 kg: ESE240CL seed sets 203 (gate), 303/403/503 (their sets), 603 (ours) + WEB140/ESE240SL gate sets.
Counts captured / refusals / false holds / knocked, re-scored with the 80 mm band (model as shipped, tooth_hw 0.35) and the ORIGINAL
50 mm band (seated50/captured50/false_hold50 logged by simB2hx_r2m), and the lateral error (dock dy at first dock, nib y at the end)."""
import json, glob, os, numpy as np, sys
R='/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg/h2/res_r2'
sets=[('ESE240CL',s,'B2F_grab_ESE240CL_r2b%s.json'%t) for s,t in ((203,''),(303,'_s303'),(403,'_s403'),(503,'_s503'),(603,'_s603'))]+[('WEB140',201,'B2F_grab_WEB140_r2b.json'),('ESE240SL',202,'B2F_grab_ESE240SL_r2b.json')]
out={}; rows=[]
for b,s,f in sets:
    p=os.path.join(R,f)
    if not os.path.exists(p): continue
    d=json.load(open(p)); runs=d['runs']
    res=[r['result'] for r in runs]
    cap=sum(r=='success' for r in res); ref=sum(r in('no_dock','safe_miss','refused') for r in res); oth=len(res)-cap-ref
    fh80=sum(bool(r.get('false_hold')) for r in runs); fh50=sum(bool(r.get('false_hold50')) for r in runs)
    cap50=sum(bool(r.get('captured50')) for r in runs); claim=sum(bool(r.get('claim')) for r in runs)
    claim_not_seated50=sum(bool(r.get('claim')) and not r.get('seated50',True) for r in runs)
    kn=sum(bool(r.get('knocked')) for r in runs); reapp=sum(bool(r.get('retried')) for r in runs)
    dy=[abs(r['dock_dys_mm'][0]) for r in runs if r.get('dock_dys_mm') and r['dock_dys_mm'][0] is not None]
    ny=[abs(r['nib_y_mm']) for r in runs if r.get('nib_y_mm') is not None]
    nys=[abs(r['nib_y_mm']) for r in runs if r.get('nib_y_mm') is not None and r['result']=='success']
    o=dict(bin=b,seed=s,n=len(runs),captured=cap,refusals=ref,other=oth,other_results=sorted(set(x for x in res if x!='success' and x not in('no_dock','safe_miss','refused'))),
           retried=reapp,claims=claim,false_holds_80mm=fh80,false_holds_50mm=fh50,captured_50mm=cap50,claimed_but_outside_50mm=claim_not_seated50,knocked=kn,
           dock_dy_first_abs_mm=dict(mean=round(float(np.mean(dy)),1) if dy else None,p95=round(float(np.percentile(dy,95)),1) if dy else None,max=round(float(max(dy)),1) if dy else None),
           nib_y_end_abs_mm_success=dict(mean=round(float(np.mean(nys)),1) if nys else None,max=round(float(max(nys)),1) if nys else None),
           nib_y_end_abs_mm_all_max=round(float(max(ny)),1) if ny else None,
           refusal_idx=[r['i'] for r in runs if r['result']!='success'], over50_idx=[r['i'] for r in runs if r.get('nib_y_mm') is not None and abs(r['nib_y_mm'])>50])
    out['%s_s%d'%(b,s)]=o
cl=[v for k,v in out.items() if k.startswith('ESE240CL')]
tot=lambda k: sum(v[k] for v in cl)
out['ESE240CL_all']=dict(sets=[v['seed'] for v in cl],n=tot('n'),captured=tot('captured'),refusals=tot('refusals'),other=tot('other'),false_holds_80mm=tot('false_holds_80mm'),
    false_holds_50mm=tot('false_holds_50mm'),captured_50mm=tot('captured_50mm'),claimed_but_outside_50mm=tot('claimed_but_outside_50mm'),knocked=tot('knocked'),
    extra_120=dict(n=sum(v['n'] for v in cl if v['seed']!=203),captured=sum(v['captured'] for v in cl if v['seed']!=203),refusals=sum(v['refusals'] for v in cl if v['seed']!=203),
                   false_holds_80mm=sum(v['false_holds_80mm'] for v in cl if v['seed']!=203),false_holds_50mm=sum(v['false_holds_50mm'] for v in cl if v['seed']!=203)))
json.dump(out,open('/workspace/work/out/rev2/mech/pickup_r2b_seeds.json','w'),indent=1)
for k,v in out.items(): print(k,json.dumps(v)[:420])
