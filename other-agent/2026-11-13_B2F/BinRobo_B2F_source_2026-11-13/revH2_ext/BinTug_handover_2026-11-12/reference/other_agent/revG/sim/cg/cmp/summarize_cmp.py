#!/usr/bin/env python3
"""COMPARE scorecard against CRITERIA_FROZEN.md (unchanged; copy of it1/summarize_it1.py with design prefix/res dir). usage:
  summarize_cmp.py <PREFIX B1_|H_> <TAG> <resdir> <design B1|RevH>  -> <resdir>/gate_<PREFIX><TAG>.json
Missing result files are reported as MISSING (never as pass)."""
import json, os, sys
H=os.path.dirname(os.path.abspath(__file__)); PFX=sys.argv[1]; TAG=sys.argv[2]; RES=sys.argv[3]; DES=sys.argv[4]
def L(n,tag=None):
    f=os.path.join(RES,PFX+n+(TAG if tag is None else tag)+'.json')
    if not os.path.exists(f) and n.startswith('step40'): f=os.path.join(RES,PFX+n+'_rw318'+(TAG if tag is None else tag)+'.json')  # Rev H rw 0.159 -> runCMP file suffix
    return json.load(open(f)) if os.path.exists(f) else None
S={}
# G1
g={}; pooled=0; fh=0; kn=0; ok=True
for b in ('WEB140','ESE240SL','ESE240CL'):
    d=L('grab_'+b)
    if not d: g[b]='MISSING'; ok=False; continue
    n=d['n']; c=d['captured']; g[b]=dict(n=n,captured=c,false_holds=d['false_holds'],knocked=d['knocked'],
        non_success=[(r['i'],r['result'],r.get('first_result')) for r in d['runs'] if r['result']!='success'])
    pooled+=c; fh+=d['false_holds']; kn+=d['knocked']; ok=ok and c>=28*n/30
N=sum(v['n'] for v in g.values() if isinstance(v,dict))
S['G1']=dict(bins=g,pooled=pooled,n=N,false_holds=fh,knocked=kn,PASS=bool(ok and N and pooled>=87*N/90 and fh==0 and kn==0))
for b in ('ESE240SL250','ESE140CL'):
    d=L('grab_'+b)
    if d: S['G1_extra_'+b]=dict(n=d['n'],captured=d['captured'],false_holds=d['false_holds'],knocked=d['knocked'],non_success=[(r['i'],r['result']) for r in d['runs'] if r['result']!='success'])
# G2
cl={}
for m in (30,25,22):
    for c in (6,9):
        d=L('climb_m%02d_c%02d'%(m,c)); cl['mu0.%02d crr0.%02d'%(m,c)]=None if not d else dict(ok=d['ok'],t=d['time_s'],dist=d['dist_m'],creep=d['hold_creep_m'],grab=d['grab'],torque_pk=d['peak'].get('wheel_torque_Nm',[None])[0])
S['G2']=dict(runs=cl,PASS=all(v and v['ok'] for v in cl.values()))
# G3
def st(d): return None if not d else dict(ok=d['ok'],reached=d['reached'],dist=d['dist_m'],roll=d['roll'],pitch=d['pitch'],bin_ground=d['bin_ground'],seated=d['seated_all'],clear_min=d['clear_min'],grab=d['grab'],lift_pk=d['peak'].get('lift_N',[None])[0])
S['G3']=dict(one=st(L('step40_one')),both=st(L('step40_both')))
S['G3']['PASS']=bool(S['G3']['one'] and S['G3']['one']['ok'] and S['G3']['both'] and S['G3']['both']['ok'])
S['G3_extra']=dict(both_ramp_1to4=st(L('step40_both_ramp')),both_rw560=st(L('step40_both_rw560')))
# G4
e={o:L('estop12_'+o) for o in ('fwd','rev')}
S['G4']=dict(runs={o:(None if not v else dict(ok=v['ok'],stop=v['stop_dist_m'],slide=v['slide_after_stop_m'],roll=v['roll'],pitch=v['pitch'])) for o,v in e.items()},PASS=all(v and v['ok'] for v in e.values()))
# G5
d=L('towstab'); S['G5']=dict(run=None if not d else dict(ok=d['ok'],roll=d['roll'],swept=d['swept_diameter_m'],pivot=d['pivot_turned_deg']),PASS=bool(d and d['ok']))
# G6
rel={}; tips=0; drops=0
for b in ('WEB140','ESE240CL','ESE240SL250'):
    for c in ('flat','up12','dn12'):
        for f in ('full','empty'):
            d=L('rel_%s_%s_%s'%(b,c,f)); rel['%s %s %s'%(b,c,f)]=None if not d else d['verdict']
            if d and d['verdict']=='TIPS': tips+=1
npass=sum(1 for v in rel.values() if v=='PASS')
S['G6']=dict(cases=rel,passed=npass,tips=tips,PASS=bool(npass==18 and tips==0))
# G7
def v(d): return None if not d else d['ok']
pairs=[('climb_m25_c09',True),('step40_one',False),('estop12_fwd',False)]; g7={}
okall=True
for n,timed in pairs:
    a=L(n); fd=[os.path.join(RES,PFX+n+x+'_dt025'+TAG+'.json') for x in ('','_rw318')]; fd=[x for x in fd if os.path.exists(x)]
    b=json.load(open(fd[0])) if fd else None
    if not a or not b: g7[n]='MISSING'; okall=False; continue
    same=a['ok']==b['ok']; tt=(abs(b['time_s']-a['time_s'])/a['time_s']<=0.10) if timed else True
    g7[n]=dict(base=a['ok'],dt025=b['ok'],t=(a.get('time_s'),b.get('time_s')),ok=bool(same and tt)); okall=okall and same and tt
S['G7']=dict(runs=g7,PASS=okall)
# G8
r8={}
for p in ('up','dn','crL','crR'):
    for k in (110,60):
        d=L('static_%s_%d'%(p,k)); r8['%s %d'%(p,k)]=None if not d else dict(dL=d['driveL'],dR=d['driveR'],castors=d['caster_sum'],antitip=d['antitip'],ok=d['ok'])
HC=json.load(open(os.path.join(H,'res','handcalc_cmp.json')))
hc=HC['B1']['cases'] if DES=='B1' else HC['RevH']['cases']
tipmin=min(min(c['tip_lateral_deg'],c['tip_forward_over_castors_deg'],c.get('rear_tip_on_antitip_deg',c.get('rear_tip_on_tail_wheels_deg'))) for c in hc)
S['G8']=dict(poses=r8,handcalc_min_tip_deg=tipmin,castor_liftoff_110=hc[0]['castor_liftoff_about_drive_axle_deg'],PASS=bool(all(v and v['ok'] for v in r8.values()) and tipmin>=20))
# G9
M=json.load(open(os.path.join(H,'..','it1','mass_cgB1.json') if DES=='B1' else os.path.join(H,'mass_revH.json'))); S['G9']=dict(kg=M['total'],PASS=M['total']<=120)
S['passed']=sum(1 for k in ('G1','G2','G3','G4','G5','G6','G7','G8','G9') if S[k]['PASS'])
json.dump(S,open(os.path.join(H,'res','gate_%s%s.json'%(PFX,TAG)),'w'),indent=1,default=str)
for k in ('G1','G2','G3','G4','G5','G6','G7','G8','G9'): print(k,'PASS' if S[k]['PASS'] else 'FAIL',json.dumps({a:b for a,b in S[k].items() if a!='PASS'},default=str)[:400])
print('passed',S['passed'],'/9')
