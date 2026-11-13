#!/usr/bin/env python3
"""Collect cg/res/*.json into the gate scorecard (applies CRITERIA_FROZEN.md exactly). Output res/summary_cg.json + res/summary_cg.md"""
import json, os, glob
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(H,'res')
def L(f):
    p=os.path.join(R,f); return json.load(open(p)) if os.path.exists(p) else None
S={}; md=[]
def item(k,v): S[k]=v
# G1 grab
for c in ('A','B'):
    g=[]; tot=0; ok=0; fh=0; kn=0; err=0
    for b in ('WEB140','ESE240SL','ESE240CL'):
        d=L('%s_grab_%s.json'%(c,b))
        if not d: g.append((b,None)); continue
        n=len([r for r in d['runs'] if r['result']!='error']); e=len(d['runs'])-n; cap=sum(1 for r in d['runs'] if r['result']=='success')
        f=sum(1 for r in d['runs'] if r.get('false_hold')); k=sum(1 for r in d['runs'] if r.get('knocked'))
        first=sum(1 for r in d['runs'] if r.get('first_result')=='success')
        from collections import Counter
        g.append((b,dict(n=n,captured=cap,first_try=first,false_holds=f,knocked=k,errors=e,results=dict(Counter(r['result'] for r in d['runs'])))))
        tot+=n; ok+=cap; fh+=f; kn+=k; err+=e
    done=all(x[1] for x in g)
    passed=done and all(x[1]['captured']>=28 and x[1]['n']>=30 for x in g) and ok>=87 and fh==0 and kn==0
    item(c+'_G1',dict(per_bin=dict(g),pooled=ok,n=tot,false_holds=fh,knocked=kn,complete=done,PASS=passed))
# G2 climb
for c in ('A','B'):
    rr={}
    for mu in (30,25,22):
        for cr in (6,9):
            d=L('%s_climb_m%02d_c%02d.json'%(c,mu,cr))
            rr['mu%.2f_crr%.2f'%(mu/100,cr/100)]=None if not d else dict(ok=d['ok'],dist=d['dist_m'],time=d['time_s'],creep=d['hold_creep_m'])
    item(c+'_G2',dict(runs=rr,PASS=all(v and v['ok'] for v in rr.values()),n_pass=sum(1 for v in rr.values() if v and v['ok'])))
# G3 step
d1=L('A_step40_one.json'); d2=L('A_step40_both.json')
def a_step(d): return None if not d else dict(ok=bool(d['ok'] and d['hitch_yaw_max_deg']<=15 and d['hitch_yaw_max_deg']<39 and d['roll_max_deg']<15),reached=d.get('reached'),dist=d['dist_m'],hitch=d['hitch_yaw_max_deg'],roll=d['roll_max_deg'],kp_bend=d['loads'].get('kp_bend',[None])[0])
item('A_G3',dict(one=a_step(d1),both=a_step(d2)))
S['A_G3']['PASS']=all(v and v['ok'] for v in (S['A_G3']['one'],S['A_G3']['both']))
e1=L('B_step40_one.json'); e2=L('B_step40_both.json')
def b_step(d): return None if not d else dict(ok=d['ok'],reached=d['reached'],dist=d['dist_m'],pitch=d['pitch'],roll=d['roll'],bin_ground=d['bin_ground'],seated=d['seated_all'],peak_lift=d['peak'].get('lift_N',[None])[0],peak_tyre=d['peak'].get('drive_tyre_N',[None])[0])
item('B_G3',dict(one=b_step(e1),both=b_step(e2))); S['B_G3']['PASS']=all(v and v['ok'] for v in (S['B_G3']['one'],S['B_G3']['both']))
# G4 estop
d=L('A_estop12.json'); item('A_G4',dict(run=None if not d else dict(ok=d['ok'],stop=d['stop_dist_m'],slide=d['slide_after_stop_m'],hitch=d['hitch_yaw_max_deg']),PASS=bool(d and d['ok'] and d['roll_max_deg']<15)))
bb={o:L('B_estop12_%s.json'%o) for o in ('fwd','rev')}
item('B_G4',dict(runs={o:(None if not v else dict(ok=v['ok'],stop=v['stop_dist_m'],slide=v['slide_after_stop_m'],pitch=v['pitch'],roll=v['roll'])) for o,v in bb.items()},PASS=all(v and v['ok'] for v in bb.values())))
# G5 towstab
d=L('A_towstab.json'); item('A_G5',dict(run=None if not d else dict(ok=d['ok'],hitch=d.get('hitch_max_deg'),roll=d['max_roll_deg'],castor_min=d['caster_min_N']),PASS=bool(d and d['ok'] and d.get('hitch_max_deg',99)<39 and d['max_roll_deg']<10)))
d=L('B_towstab.json'); item('B_G5',dict(run=None if not d else dict(ok=d['ok'],roll=d['roll'],swept=d['swept_diameter_m'],pivot=d['pivot_turned_deg'],drift=d['pivot_centre_drift_m']),PASS=bool(d and d['ok'])))
# G6 release
for c in ('A','B'):
    tab={}; vs=[]
    for b in ('WEB140','ESE240CL','ESE240SL250'):
        for case in ('flat','up12','dn12'):
            for f in ('full','empty'):
                if c=='A': fn='A_rel_%s_rel_%s%s.json'%(b,case,'' if f=='full' else 'e')
                else: fn='B_rel_%s_%s_%s.json'%(b,case,f)
                d=L(fn); v=None if not d else d.get('verdict'); tab['%s %s %s'%(b,case,f)]=v; vs.append(v)
    item(c+'_G6',dict(cells=tab,n_pass=sum(1 for v in vs if v=='PASS'),n=len(vs),tips=sum(1 for v in vs if v=='TIPS'),PASS=all(v=='PASS' for v in vs)))
# G7 dt
for c,files in (('A',[('A_climb_m25_c09','time_s'),('A_step40_one',None),('A_estop12',None)]),('B',[('B_climb_m25_c09','time_s'),('B_step40_one',None),('B_estop12_fwd',None)])):
    rr=[]
    for f,key in files:
        a=L(f+'.json'); b=L(f+'_dt025.json')
        if not (a and b): rr.append(dict(case=f,complete=False)); continue
        same=a['ok']==b['ok']; within=True
        if key and a.get(key) and b.get(key): within=abs(a[key]-b[key])/a[key]<=0.10
        rr.append(dict(case=f,ok_dt05=a['ok'],ok_dt025=b['ok'],t05=a.get(key) if key else None,t025=b.get(key) if key else None,PASS=bool(same and within)))
    item(c+'_G7',dict(runs=rr,PASS=all(r.get('PASS') for r in rr)))
# G8 static
rrA={}
for pose in ('up','dn','crL','crR'):
    for kg in (110,60):
        d=L('calA_ESE240SL_G8_%s%d.json'%(pose,kg))
        rrA['%s %d'%(pose,kg)]=None if not d else dict(dL=d['driveL'],dR=d['driveR'],castors=d['caster_N'],ok=bool(min(d['driveL'],d['driveR'])>=100 and d['caster_N']>=50 and d['captured']))
item('A_G8',dict(poses=rrA,PASS=all(v and v['ok'] for v in rrA.values())))
rrB={}
for pose in ('up','dn','crL','crR'):
    for kg in (110,60):
        d=L('B_static_%s_%d.json'%(pose,kg))
        rrB['%s %d'%(pose,kg)]=None if not d else dict(dL=d['driveL'],dR=d['driveR'],castors=d['caster_sum'],ok=d['ok'])
item('B_G8',dict(poses=rrB,PASS=all(v and v['ok'] for v in rrB.values())))
hc=L('handcalc_cg.json')
if hc:
    S['A_G9']=dict(kg=hc['mass']['A_kg'],PASS=hc['mass']['A_kg']<=120); S['B_G9']=dict(kg=hc['mass']['B_kg'],PASS=hc['mass']['B_kg']<=120)
json.dump(S,open(os.path.join(R,'summary_cg.json'),'w'),indent=1,default=str)
for k in sorted(S): print(k,'PASS' if S[k].get('PASS') else 'FAIL',json.dumps({kk:vv for kk,vv in S[k].items() if kk!='PASS'},default=str)[:300])
