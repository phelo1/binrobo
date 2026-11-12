#!/usr/bin/env python3
"""G6 task 3: ballast sweep on the real-contact G6 model (GH-B6 grabber = combos_g6 H3, data-sheet bins).
Operating mass set by DRY ballast in the two 10 L cans (steel punchings 4.1 kg/L bulk, or dry gravel 1.68 kg/L) - mass files
mass_g6_<label>.json written by masses_g6.py.  Tests (one nominal run each):
  climb12   full 240 L (ESE 240 SL, 110 kg gross) towed up a 12 % grade on wet leaves, ground/tyre mu 0.30 (G3 wet-leaf value), 5 m at 0.5 m/s,
            then 3 s brake hold on the hill
  climb12x  same at mu 0.25 (sensitivity: slimy leaf mat)
  step40    full 110 kg ESE 240 SL at 0.5 m/s, left wheels over a 40 mm sharp step, mu 0.6 (as G5)
  estop12   full 110 kg, 12 % DOWNHILL, mu 0.30, 0.5 m/s then emergency stop (brakes) -> stopping distance + slide
  estopflat full 110 kg, flat mu 0.6, 0.5 m/s then e-stop
  flat10    full 110 kg, flat mu 0.6, 10 m straight at 0.5 m/s -> drive energy per metre;  flat10e = empty bin
  rel_*     release tests on 12 % (as G5 tow_g5: rel_up12 rel_dn12 rel_up12e rel_dn12e) - delegated to tow_g5.run with this mass file
Loads: kingpin (rear-frame axes: axial, radial, bending moment from cfrc_int about the kingpin point), caster and drive-wheel normal
forces, sampled every 10 ms during the tow phases.  Energy: mechanical drive power sum(tau*omega) at the wheel axles, positive part only;
electrical = mechanical / 0.55 (assumed donor powerchair motor+gearbox efficiency - MODELLED, not simulated) + 6 W electronics.
usage: PYTHONPATH=/workspace/work/pylib python3 ballast_g6.py <label> <test> -> ../results_G6_ballast_<label>_<test>.json"""
import json, math, os, sys, time, numpy as np, mujoco
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from sim_g5 import Sim, TXm
from scen_g5 import Runner, grab_GH, tip_more, tow, soft_stop, heading_hold
from tow_g5 import nominal, engage_catch
from bins_g5 import BINS
ETA=0.55; P_ELEC=6.0
def set_mu(S,mu):
    for n in ('ground','bump','driveL','driveR','casterL','casterR','binwheelL','binwheelR'):
        g=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_GEOM,n)
        if g>=0: S.m.geom_friction[g][0]=mu
def kp_loads(S):
    m,d=S.m,S.d; mujoco.mj_rnePostConstraint(m,d); bid=S.bid['rear']; f=d.cfrc_int[bid]; c=d.subtree_com[m.body_rootid[bid]]; p=d.xpos[bid]
    tau=f[:3]+np.cross(c-p,f[3:]); R=d.xmat[bid].reshape(3,3); F=R.T@f[3:]; T=R.T@tau
    return dict(kp_axial=float(abs(F[2])),kp_radial=float(math.hypot(F[0],F[1])),kp_bend=float(math.hypot(T[0],T[1])),kp_yaw=float(abs(T[2])))
def run(label,test):
    if test.startswith('rel_'):
        import tow_g5
        C=json.load(open(os.path.join(HERE,'combos_g6.json')))['H3']; out={}
        for b in ('WEB140','ESE240SL'):
            os.environ['G6_MASSFILE']=os.path.join(HERE,'mass_g6_%s.json'%label)
            o,R=tow_g5.run(b,test,'B2',dict(C)); out[b]={k:v for k,v in o.items() if k!='events'}; out[b]['events']=o.get('events',R.events)[-6:]
        return dict(label=label,test=test,results=out,ok=all(v.get('ok') for v in out.values()))
    binkey=os.environ.get('G6_BIN','ESE240SL'); B=BINS[binkey]; kw=nominal(binkey)
    C=json.load(open(os.path.join(HERE,'combos_g6.json')))['H3']; ghp=dict(C); ghp.update(json.loads(os.environ.get('G6_GHP_EXTRA','{}')))
    for k_,n_ in (('_claim_and','claim_and'),('_guard','square_guard'),('_reapp','reapp')):
        if k_ in ghp: kw[n_]=ghp.pop(k_)
    terrain='flat'; extra={}
    if test=='step40': terrain='bump'; extra=dict(bump=(TXm+0.60+1.6,0.040,kw['binm']['wy']+0.075))
    fill=0.0 if test.endswith('e') else 110.0-B['empty']
    S=Sim(grabber='GH',gh='B2',ghp=ghp,fill=fill,mu=0.6,massfile=os.path.join(HERE,'mass_g6_%s.json'%label),ballast=99,
          tug_pose=(TXm+0.60+(kw['wheel_r']-0.10),float(os.environ.get('REL_DY','0')),float(os.environ.get('REL_DYAW','0'))),terrain=terrain,**kw,**extra)
    R=Runner(S,rec_hz=2); R.recording=False
    out=dict(label=label,test=test,tug_kg=round(S.tug_mass,1),bin_kg=round(S.bin_mass,1))
    g=grab_GH(R,tip_to=25.0); out['grab']=g.get('result')
    if g.get('result')!='success': out['ok']=False; return out
    if os.environ.get('G6_RATCHET_TIP')=='1' and getattr(S,'ratchet_on',False):   # G6 fix: ratchet released after the claim
        S.ratchet_on=False; j=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'float'); S.m.jnt_range[j][0]=-S.GHV['float_down']
    tip_more(R,48.0); engage_catch(R); S.yaw_lock(False); R.watch_pawl=True
    if os.environ.get('G6_RATCHET_TIP')=='1' and S.GHV.get('ratchet',False): S.ratchet_on=True   # G6 fix: ratchet re-engaged in the tow pose (one-way: float may rise during stand-up)
    MX=dict(ryaw=0.0,roll=0.0,anti=0.0,byaw=0.0,cap_all=True); pk={}; cmin=[1e9]; dmin=[1e9]; E=[0.0]; prev=R.step; rec=[False]
    def st():
        prev()
        if R.i%20==0 and rec[0]:
            for k,v in kp_loads(S).items():
                if v>pk.get(k,(0,))[0]: pk[k]=(round(v,1),round(R.t,2),R.phase[:30])
            Cn=S.contacts(); cmin[0]=min(cmin[0],Cn['casterL'],Cn['casterR']); dmin[0]=min(dmin[0],Cn['driveL'],Cn['driveR'])
            r_,p_,y_=S.rpy(); MX['ryaw']=max(MX['ryaw'],abs(S.yaw_rel())); MX['roll']=max(MX['roll'],abs(r_)); MX['anti']=max(MX['anti'],Cn['antitipL']+Cn['antitipR'])
            MX['byaw']=max(MX['byaw'],abs(S.bin_yaw_rel())); MX['cap_all']=MX['cap_all'] and S.captured()
            for k in ('casterL','casterR','driveL','driveR'):
                if Cn[k]>pk.get(k,(0,))[0]: pk[k]=(round(Cn[k],1),round(R.t,2),R.phase[:30])
        if rec[0]:
            P=sum(float(S.d.actuator_force[a])*float(S.d.qvel[S.jv(j)]) for a,j in ((0,'axleL'),(1,'axleR')))
            E[0]+=max(P,0.0)*R.dt
    R.step=st
    psi0=S.rpy()[2]; x0=S.d.xpos[S.bid['tug']].copy(); dist=lambda: float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2]))
    if test.startswith('climb'):
        mu=0.25 if test=='climb12x' else (int(test.split('_m')[1])/100 if '_m' in test else 0.30)
        R.phase='7a onto 12 % uphill (tug facing uphill)'; set_mu(S,mu); R.ramp_grade(0.12,0,2.0); R.run_for(1.0)
        x0=S.d.xpos[S.bid['tug']].copy(); rec[0]=True; t0=R.t
        R.phase='7 climbing 12 %% wet leaves mu %.2f, full 110 kg bin'%mu; R.ctrl_fn=heading_hold(R,0.5,psi0)
        ok=R.until(lambda: dist()>=5.0,25.0); tc=R.t-t0; R.ctrl_fn=None; d5=dist()
        # wheel slip: drive wheel surface speed vs ground speed
        R.phase='8 brake hold on 12 %'; R.hold(); xh=S.d.xpos[S.bid['tug']].copy(); R.run_for(3.0)
        out.update(mu=mu,reached_5m=bool(ok),dist_m=round(d5,2),time_s=round(tc,1),avg_v=round(d5/tc,2),hold_creep_m=round(float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-xh[:2])),3),
                   mech_J=round(E[0]),Wh_per_m=round((E[0]/ETA+P_ELEC*tc)/3600/max(d5,0.01),3))
        out['ok']=bool(ok and out['hold_creep_m']<0.05 and S.captured())
    elif test=='step40':
        rec[0]=True; R.phase='7 towing 0.5 m/s over a 40 mm sharp step (left wheels)'; R.ctrl_fn=heading_hold(R,0.5,psi0)
        ok=R.until(lambda: dist()>=4.5,25.0); R.ctrl_fn=None; R.phase='8 stop'; soft_stop(R); R.run_for(1.0)
        out.update(reached=bool(ok),dist_m=round(dist(),2)); out['ok']=bool(ok and S.captured() and not getattr(R,'pawl_bounce',None))
    elif test.startswith('estop'):
        mu=float(os.environ.get('EST_MU',0.30)) if test=='estop12' else 0.6; grade=-0.12 if test=='estop12' else 0.0
        set_mu(S,mu)
        if grade and os.environ.get('G6_DNLOCK')=='1': S.yaw_lock(True); R.ev('yaw pin engaged before descent')   # G6 fix candidate
        if grade: R.phase='7a onto 12 % downhill'; R.ramp_grade(grade,0,2.0); R.run_for(0.5)
        rec[0]=True; R.phase='7 towing 0.5 m/s'; R.ctrl_fn=heading_hold(R,float(os.environ.get('EST_V',0.5)),psi0); R.until(lambda: dist()>=2.0,12.0)
        v0=S.fwd_speed(); xs=S.d.xpos[S.bid['tug']].copy(); R.ctrl_fn=None; R.phase='8 E-STOP (spring brakes)'; R.hold()
        t0=R.t; R.until(lambda: abs(S.fwd_speed())<0.01,6.0); ts=R.t-t0; dstop=float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-xs[:2]))
        R.run_for(4.0); slide=float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-xs[:2]))-dstop
        out.update(mu=mu,grade=grade,v0=round(v0,2),stop_dist_m=round(dstop,3),stop_time_s=round(ts,2),slide_after_stop_m=round(slide,3),
                   max_bin_yaw_deg=None)
        out['ok']=bool(dstop<0.5 and slide<0.05 and S.captured())
    elif test.startswith('flat10'):
        rec[0]=True; t0=R.t; R.phase='7 flat tow 10 m at 0.5 m/s'; R.ctrl_fn=heading_hold(R,0.5,psi0)
        ok=R.until(lambda: dist()>=10.0,40.0); tc=R.t-t0; R.ctrl_fn=None
        out.update(reached=bool(ok),time_s=round(tc,1),mech_J=round(E[0]),Wh_per_m=round((E[0]/ETA+P_ELEC*tc)/3600/max(dist(),0.01),4)); out['ok']=bool(ok)
    out.update(hitch_yaw_max_deg=round(MX['ryaw'],1),bin_yaw_max_deg=round(MX['byaw'],1),roll_max_deg=round(MX['roll'],1),antitip_peak_N=round(MX['anti'],1),captured_throughout=MX['cap_all'])
    out.update(loads=pk,caster_min_N=round(cmin[0],1),drive_min_N=round(dmin[0],1),still_captured=bool(S.captured()),pawl_bounce=getattr(R,'pawl_bounce',None))
    return out
if __name__=='__main__':
    lab,test=sys.argv[1],sys.argv[2]; t=time.time(); o=run(lab,test); o['cpu_s']=round(time.time()-t)
    tag=sys.argv[3] if len(sys.argv)>3 else ''
    o['env']={k:os.environ.get(k) for k in ('G6_BIN','REL_DY','REL_DYAW','EST_MU','EST_V','SIM_DT') if os.environ.get(k)}
    json.dump(o,open(os.path.join(HERE,'..','results_G6_ballast_%s_%s%s.json'%(lab,test,tag)),'w'),indent=1,default=str)
    print(json.dumps(o,default=str)[:1500],flush=True)
