#!/usr/bin/env python3
"""G5 transport + release tests on explicit data-sheet bins (GH grabber, real contact), lean 95 kg tug (mass_g3_sim_L95).
usage: PYTHONPATH=/workspace/work/pylib python3 tow_g5.py <BIN> <test> [gh=B2] [ghp_json] -> ../results_G6_tow_<BIN>_<test>_<gh>.json
tests: rel_flat | rel_up12 | rel_dn12 | rel_flate | rel_up12e | rel_dn12e  (e = empty bin, else full)
       step40 (full, 0.5 m/s, left wheels over a 40 mm sharp step) | towstab (full: 0.5 m/s straight, 90 deg turn, slalom, e-stop)"""
import json, math, os, pickle, sys, time, numpy as np, mujoco
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from sim_g5 import Sim, TXm
from scen_g5 import Runner, grab_GH, tip_more, stand_up, release_GH, bar_clear, tow, soft_stop, heading_hold
from bins_g5 import BINS
CAD=os.path.join(HERE,'..','..','cad')
def nominal(binkey):
    B=BINS[binkey]; sh,r,_=B['sections'][1] if len(B['sections'])>1 else B['sections'][0]   # sweep bins: D30 tube as nominal
    kn=B['knuckles'] if B['knuckles']!='maybe' else [(0.045,0.005)]
    wr=B['wheel']/2
    return dict(bar_r=r,bar_shape=sh,bar_x=B['bar_x'][0],bar_h=B['bar_abs'][0]-wr,wheel_r=wr,handle_half=B['web'][0],lid=('closed',0.0),mu_hook=0.35,
                binm=dict(gap=B['cb'][0]-r,D=B['D'],W=B['W'],empty=B['empty'],wy=(B['track']-0.05)/2,knuckles=kn))
def engage_catch(R, tc=0.08):
    S=R.s; j=S.m.joint('tilt').id; q=float(S.d.qpos[S.jq('tilt')])
    S.m.jnt_range[j]=[q-math.radians(0.2),q+math.radians(0.2)]; S.m.jnt_solref[j]=[tc,1.0]
    S.act_force=50.0; R.phi_cmd=q; R.ev('rest stop + catch engaged at mast %.1f deg, actuator unloaded'%math.degrees(q))
def run(binkey,test,gh='B2',ghp=None):
    B=BINS[binkey]; kw=nominal(binkey); full=not test.endswith('e'); out=dict(bin=binkey,test=test,gh=gh,ghp=ghp)
    ghp=dict(ghp or {})
    ghp.update(json.loads(os.environ.get('G6_GHP_EXTRA','{}')))   # G6: hook parameter overrides for fix tests
    for k_,n_ in (('_fpads','fpads'),('_claim_and','claim_and'),('_phi0','phi0'),('_guard','square_guard'),('_lat','lat'),('_asym','asym'),('_reapp','reapp')):
        if k_ in ghp: kw[n_]=ghp.pop(k_)
    ghp=ghp or None
    terrain='flat'; extra={}
    if test=='step40': terrain='bump'; extra=dict(bump=(TXm+0.60+1.6,0.040,kw['binm']['wy']+0.075))
    fill=B['fill_full'] if full else 0.0
    if test in('step40','towstab'): fill=110.0-B['empty']          # 110 kg gross
    S=Sim(grabber='GH',gh=gh,ghp=ghp,fill=fill,mu=0.6,massfile=os.environ.get('G6_MASSFILE',os.path.join(CAD,'mass_g3_sim_L95.json')),ballast=99,
          tug_pose=(TXm+0.60+(kw['wheel_r']-0.10),float(os.environ.get('REL_DY','0')),float(os.environ.get('REL_DYAW','0'))),terrain=terrain,**kw,**extra)   # G6: pose variation
    R=Runner(S,rec_hz=12); out['tug_kg']=round(S.tug_mass,1); out['bin_kg']=round(S.bin_mass,1)
    g=grab_GH(R,tip_to=25.0); out['grab']={k:g.get(k) for k in ('result','claim','captured','float_mm','bar_mm')}
    if g.get('result')!='success': out['ok']=False; return out,R
    if not hasattr(S,'_float_grab'): S._float_grab=float(S.d.qpos[S.jq('float')])
    if os.environ.get('G6_RATCHET_TIP')=='1' and getattr(S,'ratchet_on',False):   # G6 fix: ratchet pawl lifted after a good claim, float free during tip/tow/stand-up
        S.ratchet_on=False; j=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'float'); S.m.jnt_range[j][0]=-S.GHV['float_down']; R.ev('float ratchet released for tip/tow')   # G6: float position at latch (firmware would store the float sensor reading)
    tip_more(R,48.0)
    if os.environ.get('G6_RATCHET_TIP')=='1' and S.GHV.get('ratchet',False): S.ratchet_on=True   # G6 fix: ratchet re-engaged in the tow pose (one-way: float may rise during stand-up)
    if test in ('step40','towstab'):
        engage_catch(R); S.yaw_lock(False); R.watch_pawl=True; R.peak={}
        mx=dict(roll=0.0,anti=0.0,cmin=1e9,byaw=0.0)
        prev=R.step
        def st():
            prev()
            if R.i%20==0:
                C=S.contacts(); r_,p_,y_=S.rpy(); mx['roll']=max(mx['roll'],abs(r_)); mx['anti']=max(mx['anti'],C['antitipL']+C['antitipR'])
                mx['cmin']=min(mx['cmin'],min(C['casterL'],C['casterR'])); mx['byaw']=max(mx['byaw'],abs(S.bin_yaw_rel()))
        R.step=st
        psi0=S.rpy()[2]; x0=S.d.xpos[S.bid['tug']].copy()
        if test=='step40':
            R.phase='7 Towing at 0.5 m/s over a 40 mm sharp step (left wheels), catch engaged'; R.ctrl_fn=heading_hold(R,0.5,psi0)
            reached=R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=4.5,25.0)
        else:
            R.phase='7a Tow 0.5 m/s straight 2 m'; R.ctrl_fn=heading_hold(R,0.5,psi0)
            R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=2.0,10.0)
            R.phase='7b 90 deg turn at 0.5 m/s'; R.ctrl_fn=heading_hold(R,0.5,psi0+90,K=1.2); R.run_for(7.0)
            R.phase='7c Slalom +/-25 deg at 0.5 m/s'
            for k,a in enumerate((25,-25,25,0)): R.ctrl_fn=heading_hold(R,0.5,psi0+90+a,K=1.5); R.run_for(3.0)
            R.phase='7d Emergency stop from 0.5 m/s (brakes)'; R.ctrl_fn=None; R.hold(); R.run_for(2.0); reached=True
        R.ctrl_fn=None; out['dist_m']=round(float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])),2)
        R.phase='8 Stop'; soft_stop(R); R.run_for(1.0)
        out.update(reached=bool(reached),still_captured=bool(S.captured()),pawl_bounce=getattr(R,'pawl_bounce',None),pawl_min_deg=round(getattr(R,'pawl_min',0),1),
                   peak_hook=round(R.peak.get('hook',(0,))[0]),max_roll_deg=round(mx['roll'],1),antitip_peak_N=round(mx['anti'],1),
                   caster_min_N=round(mx['cmin'],1),max_bin_yaw_deg=round(mx['byaw'],1))
        out['ok']=bool(reached and S.captured() and not out['pawl_bounce'])
        return out,R
    MON=dict(ryaw=0.0,pitch_dev=0.0,anti=0.0,cmin=1e9,phase_ryaw='')
    prev0=R.step
    def stm():
        prev0()
        if R.i%40==0:
            y=abs(S.yaw_rel())
            if y>MON['ryaw']: MON['ryaw']=y; MON['phase_ryaw']=R.phase[:40]
            C=S.contacts(); MON['anti']=max(MON['anti'],C['antitipL']+C['antitipR']); MON['cmin']=min(MON['cmin'],C['casterL'],C['casterR'])
            MON['pitch_dev']=max(MON['pitch_dev'],abs(S.rpy()[1]))
    R.step=stm
    grade={'rel_flat':0,'rel_up12':0.12,'rel_dn12':-0.12,'rel_flate':0,'rel_up12e':0.12,'rel_dn12e':-0.12}[test]
    if grade<0 and os.environ.get('G6_DNLOCK')=='1':   # G6 fix: yaw pin engaged (hitch straight) before descending with a bin
        R.ev('yaw pin engaged before descent at hitch %.1f deg'%S.yaw_rel()); S.yaw_lock(True); S._ylocked=True
    if grade: R.phase='7a Onto %+.1f%% grade (tug facing %s)'%(grade*100,'uphill' if grade>0 else 'downhill'); R.ramp_grade(grade,0,2.0); R.run_for(1.0)
    R.phase='7 Towing 1 m'; tow(R,0.3,1.0,Tmax=10); soft_stop(R); R.run_for(0.5)
    o=release_GH(R); out['release']=o
    v=S.d.qvel[S.jv('binfree'):S.jv('binfree')+3]; out['bin_speed_end']=round(float(np.linalg.norm(v)),3)
    out['bin_stable']=bool(S.bin_tilt_abs()<8 and np.linalg.norm(v)<0.05)
    out['ok']=bool(o.get('released') and out['bin_stable']); out['events']=R.events
    out['mon']={k:(round(v,1) if isinstance(v,float) else v) for k,v in MON.items()}; out['bin_tilt_abs_end']=round(S.bin_tilt_abs(),1)
    out['env']={k:os.environ.get(k) for k in ('G6_MASSFILE','G6_YAWRANGE','G6_PINLOCK','G6_DNLOCK','G6_SB2','REL_DY','REL_DYAW','SIM_DT') if os.environ.get(k)}
    return out,R
if __name__=='__main__':
    binkey=sys.argv[1]; test=sys.argv[2]; gh=sys.argv[3] if len(sys.argv)>3 else 'B2'; ghp=json.loads(sys.argv[4]) if len(sys.argv)>4 and sys.argv[4] else None
    t=time.time(); o,R=run(binkey,test,gh,ghp); o['cpu_s']=round(time.time()-t); o.setdefault('events',R.events)
    tag=sys.argv[5] if len(sys.argv)>5 else ''
    json.dump(o,open(os.path.join(HERE,'..','results_G6_tow_%s_%s_%s%s.json'%(binkey,test,gh,tag)),'w'),indent=1,default=str)
    if os.environ.get('TOW_REC')=='1': pickle.dump(R.rec,open(os.path.join(HERE,'rec','tow_%s_%s_%s%s.pkl'%(binkey,test,gh,tag)),'wb'))
    print(json.dumps({k:v for k,v in o.items() if k!='events'},default=str)[:1500],flush=True)
