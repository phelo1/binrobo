#!/usr/bin/env python3
"""Concept gate runner, concept A'. Writes ONLY to cg/res/. usage:
  runA.py grab <BIN> <n> <seed>         G1 (mc_g5 sampler; grab + re-dock + tip to A' tow pose)
  runA.py climb <mu> <crr_bin>          G2   | runA.py step <one|both>  G3 | runA.py estop  G4 | runA.py towstab  G5
  runA.py rel <BIN> <rel_flat|rel_up12|rel_dn12|...e>   G6
Env SIM_DT for G7 repeats (tag suffix _dt025)."""
import os, sys, json, time, math, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import simA_cg as A; A.set_env()
import mujoco, sim_g5, scen_g5, tow_g5
import ballast_g6
from bins_g5 import BINS
RES=os.path.join(HERE,'res'); TAG=('_dt025' if os.environ.get('SIM_DT')=='0.00025' else '')+('_'+os.environ['CGA_TAGX'] if os.environ.get('CGA_TAGX') else '')
CRR_BIN=[None]
_Sim=sim_g5.Sim
def SimA(**kw):
    kw['massfile']=A.MASSF; kw['ballast']=99
    if os.environ.get('CGA_FILL'): kw['fill']=float(os.environ['CGA_FILL'])
    S=_Sim(**kw)
    if CRR_BIN[0] is not None and S.with_bin:
        for j in ('baxL','baxR'): S.m.dof_frictionloss[S.jv(j)]=CRR_BIN[0]*(kw.get('fill',0)+12)*9.81*0.45*0.1
    return S
ballast_g6.Sim=SimA; tow_g5.Sim=SimA
def dump(name,o):
    o['cpu_s']=round(time.time()-T0); o['env']={k:v for k,v in os.environ.items() if k.startswith(('G6_','CGA_','EST_','SIM_DT'))}
    json.dump(o,open(os.path.join(RES,name+TAG+'.json'),'w'),indent=1,default=str); print(name,json.dumps({k:v for k,v in o.items() if k not in('events','runs','loads','env')},default=str)[:900],flush=True)
T0=time.time(); cmd=sys.argv[1]
if cmd=='climb':
    mu=float(sys.argv[2]); CRR_BIN[0]=float(sys.argv[3])
    o=ballast_g6.run('cgA','climb12_m%02d'%round(mu*100)); o['crr_bin']=CRR_BIN[0]
    dump('A_climb_m%02d_c%02d'%(round(mu*100),round(CRR_BIN[0]*100)),o)
elif cmd=='step':
    if sys.argv[2] in ('both','oblique'): os.environ['CGA_BUMPW']='1'
    if sys.argv[2]=='oblique': os.environ['CGA_BUMPYAW']='30'
    o=ballast_g6.run('cgA','step40'); o['side']=sys.argv[2]; dump('A_step40_'+sys.argv[2],o)
elif cmd=='estop':
    os.environ['EST_MU']='0.30'; o=ballast_g6.run('cgA','estop12'); dump('A_estop12',o)
elif cmd=='towstab':
    o,R=tow_g5.run('ESE240SL','towstab','B2',dict(json.load(open(os.path.join(A.G6,'combos_g6.json')))['H3']))
    o['hitch_max_deg']=round(max((abs(e['ryaw']) for e in R.log if e['ph'].startswith('7')),default=0),1); o['events']=R.events[-8:]; dump('A_towstab',o)
elif cmd=='rel':
    b,t=sys.argv[2],sys.argv[3]
    o,R=tow_g5.run(b,t,'B2',dict(json.load(open(os.path.join(A.G6,'combos_g6.json')))['H3'])); o['events']=R.events[-12:]
    o['verdict']='PASS' if o.get('ok') else ('TIPS' if o.get('bin_tilt_abs_end',0)>30 else ('HOLD' if (o.get('release') or {}).get('pin_fail') else ('STUCK' if not (o.get('release') or {}).get('released') else 'FAIL')))
    dump('A_rel_%s_%s'%(b,t),o)
elif cmd=='grab':
    import mc_g5
    from scen_g5 import Runner, grab_GH
    b=sys.argv[2]; n=int(sys.argv[3]); seed=int(sys.argv[4]); B=BINS[b]; rng=np.random.default_rng(seed); PS=[mc_g5.sample(B,i,rng) for i in range(n)]
    ghp=dict(json.load(open(os.path.join(A.G6,'combos_g6.json')))['H3']); out=os.path.join(RES,'A_grab_%s%s.json'%(b,TAG)); runs=[]
    if os.path.exists(out): runs=json.load(open(out))['runs']
    done={r['i'] for r in runs}
    for i,p in enumerate(PS):
        if i in done: continue
        t=time.time()
        try:
            S=mc_g5.make_sim(p,'B2',dict(ghp)); R=Runner(S,rec_hz=10); R.recording=False; R.contact_every=20
            o=grab_GH(R,tip_to=20.0); o['first_result']=o['result']
            if (o['result'] in ('safe_miss','bin_pushed') and o.get('docked')) or (o['result']=='no_dock' and getattr(R,'guard',False)):
                S.cam_state=2; R.ramp_phi(S.kw.get('phi0',8.0),3.0); R.set_drive(0.15); R.run_for(2.5); R.hold(); R.run_for(0.5)
                o2=grab_GH(R,tip_to=20.0); o2['first_result']=o['first_result']; o2['retried']=True; o=o2
            if o['result']=='success':
                if getattr(S,'ratchet_on',False):
                    S.ratchet_on=False; jf=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'float'); S.m.jnt_range[jf][0]=-S.GHV['float_down']
                scen_g5.tip_more(R,48.0); R.hold(); R.run_for(1.0)
                o['tow_pose_captured']=bool(S.captured()); o['result']='success' if o['tow_pose_captured'] else 'lost_in_tip'
            o.update(bin_tilt_abs_end=round(S.bin_tilt_abs(),1),knocked=bool(S.bin_tilt_abs()>30 and not S.captured()),false_hold=bool(o.get('claim') and not o.get('captured_at_claim',True)))
            o={k:v for k,v in o.items() if k in('result','first_result','retried','claim','captured','captured_at_claim','tow_pose_captured','abort','bin_tilt_abs_end','knocked','false_hold','float_mm','pull_rise_N')}
        except Exception as e:
            import traceback; o=dict(result='error',err=repr(e),tb=traceback.format_exc()[-600:])
        o.update(i=i,params=p,cpu=round(time.time()-t,1)); runs.append(o); runs.sort(key=lambda r:r['i'])
        ok=sum(1 for r in runs if r['result']=='success')
        json.dump(dict(bin=b,seed=seed,n=len(runs),captured=ok,false_holds=sum(1 for r in runs if r.get('false_hold')),knocked=sum(1 for r in runs if r.get('knocked')),runs=runs),open(out,'w'),indent=0,default=float)
        print(b,i,o['result'],o.get('first_result'),o['cpu'],flush=True)
