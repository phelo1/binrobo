#!/usr/bin/env python3
"""Concept gate runner, concept B (straddle comb-lift carrier). Writes ONLY to cg/res/. usage:
  runB.py grab <BIN> <n> <seed>  G1 | climb <mu> <crr_bin> [rev]  G2 | step <one|both>  G3 | estop <fwd|rev>  G4
  runB.py towstab  G5 | rel <BIN> <flat|up12|dn12> <full|empty>  G6 | static <up|dn|crL|crR|flat> <kg>  G8
Env SIM_DT=0.00025 for G7 (tag _dt025)."""
import os, sys, json, time, math, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import mujoco, simB_cg as B
from bins_g5 import BINS
RES=os.path.join(HERE,'res'); TAG=('_dt025' if os.environ.get('SIM_DT')=='0.00025' else '')+('_B2' if os.environ.get('CGB_PADCAR')=='1' else ''); T0=time.time()
def dump(name,o):
    o['cpu_s']=round(time.time()-T0); o['geo']=B.GEO
    json.dump(o,open(os.path.join(RES,name+TAG+'.json'),'w'),indent=1,default=str); print(name,json.dumps({k:v for k,v in o.items() if k not in('events','runs','geo','peak')},default=str)[:900],flush=True)
def set_mu(S,mu):
    for n in ('ground','bump','driveL','driveR','casterL','casterR','binwheelL','binwheelR'):
        g=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_GEOM,n)
        if g>=0: S.m.geom_friction[g][0]=mu
def nominal(binkey,kg=None,full=True,**kw):
    p=B.bin_params(binkey); Bn=BINS[binkey]
    p['fill']=(kg-Bn['empty']) if kg else (Bn['fill_full'] if full else 0.0)
    S=B.SimB(binkey,p,tug_pose=B.start_pose(p),**kw); R=B.RunnerB(S); g=B.grab(R)
    return S,R,g
def monitor(R,MX):
    S=R.s
    def mon():
        if R.i%40: return
        C=S.contacts(); r,p,y=S.rpy()
        MX['roll']=max(MX['roll'],abs(r)); MX['pitch']=max(MX['pitch'],abs(p)); MX['bin_ground']=max(MX['bin_ground'],S.bin_ground())
        MX['cmin']=min(MX['cmin'],C['casterL']+C['casterR']); MX['dmin']=min(MX['dmin'],C['driveL'],C['driveR'])
        MX['seated_all']=MX['seated_all'] and S.seated(); MX['clear_min']=min(MX['clear_min'],S.wheel_clear())
        R.pk('lift_N',abs(S.lift_force())); R.pk('pad_N',C['padg']); R.pk('drive_tyre_N',max(C['driveL'],C['driveR'])); R.pk('nib_rim_N',S.pair('nib','rim')+S.pair('tooth','rim')+S.pair('nib','ledge'))
        R.pk('wheel_torque_Nm',max(abs(S.d.actuator_force[0]),abs(S.d.actuator_force[1])))
    R.mon=mon
def MX0(): return dict(roll=0.0,pitch=0.0,bin_ground=0.0,cmin=1e9,dmin=1e9,seated_all=True,clear_min=9.0)
def fin(o,R,MX): o.update({k:(round(v,3) if isinstance(v,float) else v) for k,v in MX.items()}); o['peak']=R.peak; o['events']=R.events[-10:]
cmd=sys.argv[1]
if cmd=='grab':
    import mc_g5
    b=sys.argv[2]; n=int(sys.argv[3]); seed=int(sys.argv[4]); Bn=BINS[b]; rng=np.random.default_rng(seed)
    PS=[mc_g5.sample(Bn,i,rng) for i in range(n)]; CD=[float(rng.uniform(-0.010,0.010)) for i in range(n)]
    out=os.path.join(RES,'B_grab_%s%s.json'%(b,TAG)); runs=[]
    if os.path.exists(out): runs=json.load(open(out))['runs']
    done={r['i'] for r in runs}
    for i,p in enumerate(PS):
        if i in done: continue
        t=time.time()
        try:
            p=dict(p); p['comb_d']=CD[i]; pp=B.bin_params(b,p)
            S=B.SimB(b,pp,mu=p['mu'],tug_pose=B.start_pose(pp,p['dy'],p['dyaw'])); R=B.RunnerB(S)
            o=B.grab(R,seed=seed*1000+i); o['first_result']=o['result']
            if o['result'] in ('safe_miss','no_dock') and not getattr(R,'reapp',False):   # one re-dock (as G6 handover 6.2)
                R.phase='R Retry: pull forward 0.6 m, re-dock'; x0=S.d.xpos[S.bid['tug']].copy(); psi=S.rpy()[2]
                R.ctrl_fn=B.heading_hold(R,0.15,psi); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=0.6,8.0); R.ctrl_fn=None; R.hold(); R.run_for(0.4)
                R.reapp=True; o2=B.grab(R,seed=seed*1000+i+500); o2['first_result']=o['first_result']; o2['retried']=True; o=o2
            o['knocked']=bool(S.bin_tilt_abs()>30 and not S.captured()); o['false_hold']=bool(o.get('claim') and not o.get('captured'))
            o['events']=R.events[-6:]
        except Exception as e:
            import traceback; o=dict(result='error',err=repr(e),tb=traceback.format_exc()[-600:])
        o.update(i=i,params=p,cpu=round(time.time()-t,1)); runs.append(o); runs.sort(key=lambda r:r['i'])
        json.dump(dict(bin=b,seed=seed,n=len(runs),captured=sum(1 for r in runs if r['result']=='success'),false_holds=sum(1 for r in runs if r.get('false_hold')),
                       knocked=sum(1 for r in runs if r.get('knocked')),runs=runs),open(out,'w'),indent=0,default=float)
        print(b,i,o['result'],o.get('first_result'),o['cpu'],flush=True)
    sys.exit(0)
if cmd=='climb':
    mu=float(sys.argv[2]); cb=float(sys.argv[3]); rev=len(sys.argv)>4 and sys.argv[4]=='rev'; kgc=float(sys.argv[5]) if len(sys.argv)>5 else 110
    S,R,g=nominal('ESE240SL',kgc,crr_bin=cb); o=dict(test='climb12',mu=mu,crr_bin=cb,rev=rev,grab=g['result'],tug_kg=round(S.tug_mass,1),bin_kg=round(S.bin_mass,1))
    MX=MX0(); monitor(R,MX); psi0=S.rpy()[2]; sg=-1 if rev else 1
    set_mu(S,mu); R.phase='7a onto 12 %'; R.ramp_grade(0.12*sg,0,2.0); R.run_for(1.0)
    x0=S.d.xpos[S.bid['tug']].copy(); dist=lambda: float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])); t0=R.t
    R.phase='7 climbing'; R.ctrl_fn=B.heading_hold(R,0.5*sg,psi0); ok=R.until(lambda: dist()>=5.0,25.0); tc=R.t-t0; R.ctrl_fn=None; d5=dist()
    R.phase='8 brake hold'; R.hold(); xh=S.d.xpos[S.bid['tug']].copy(); R.run_for(3.0); creep=float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-xh[:2]))
    o.update(reached_5m=bool(ok),dist_m=round(d5,2),time_s=round(tc,1),hold_creep_m=round(creep,3),captured_end=S.captured())
    o['ok']=bool(ok and creep<0.05 and S.captured() and g['result']=='success'); fin(o,R,MX)
    dump('B_climb_m%02d_c%02d%s%s'%(round(mu*100),round(cb*100),'_rev' if rev else '','' if kgc==110 else '_kg%d'%kgc),o)
elif cmd=='step':
    side=sys.argv[2]; p=B.bin_params('ESE240SL'); x0=B.start_pose(p)[0]
    # bump ahead of the castors in the tug's +x travel direction (tug ends the grab ~1.2 m back from its start pose)
    S,R,g=nominal('ESE240SL',110,terrain='bump',bump=(30.0,0.040,0.40 if side=='one' else 0.0,0.25 if side=='one' else 2.0))
    gb=S.gid['bump']; S.m.geom_pos[gb][0]=float(S.d.xpos[S.bid['tug']][0])+1.6
    if side=='oblique':   # full-width step crossed at 30 deg (firmware rule for surveyed full-width steps): wheels meet it one at a time
        a=math.radians(30); S.m.geom_quat[gb]=[math.cos(a/2),0,0,math.sin(a/2)]; S.m.geom_pos[gb][1]=0.0; S.m.geom_size[gb][1]=3.0
    mujoco.mj_forward(S.m,S.d)
    o=dict(test='step40',side=side,grab=g['result']); MX=MX0(); monitor(R,MX); psi0=S.rpy()[2]
    xs=S.d.xpos[S.bid['tug']].copy(); dist=lambda: float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-xs[:2]))
    R.phase='7 0.5 m/s over a 40 mm sharp step'; R.ctrl_fn=B.heading_hold(R,0.5,psi0); ok=R.until(lambda: dist()>=4.5,25.0); R.ctrl_fn=None; B.soft_stop(R); R.run_for(1.0)
    o.update(reached=bool(ok),dist_m=round(dist(),2),captured_end=S.captured()); fin(o,R,MX)
    o['ok']=bool(ok and S.captured() and MX['seated_all'] and MX['bin_ground']<1.0 and MX['roll']<15 and MX['pitch']<15)
    dump('B_step40_'+side,o)
elif cmd=='estop':
    ori=sys.argv[2]; S,R,g=nominal('ESE240SL',110); o=dict(test='estop12',orient=ori,grab=g['result']); MX=MX0(); monitor(R,MX); psi0=S.rpy()[2]
    set_mu(S,0.30); v=0.5 if ori=='fwd' else -0.5; gx=-0.12 if ori=='fwd' else 0.12      # travel direction always downhill
    R.phase='7a onto 12 % downhill'; R.ramp_grade(gx,0,2.0); R.run_for(0.5)
    x0=S.d.xpos[S.bid['tug']].copy(); R.phase='7 0.5 m/s downhill'; R.ctrl_fn=B.heading_hold(R,v,psi0)
    R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=2.0,12.0); v0=S.fwd_speed(); xs=S.d.xpos[S.bid['tug']].copy()
    R.ctrl_fn=None; R.phase='8 E-STOP'; R.hold(); t0=R.t; R.until(lambda: abs(S.fwd_speed())<0.01,6.0); ts=R.t-t0
    dstop=float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-xs[:2])); R.run_for(4.0); slide=float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-xs[:2]))-dstop
    o.update(v0=round(v0,2),stop_dist_m=round(dstop,3),stop_time_s=round(ts,2),slide_after_stop_m=round(slide,3),captured_end=S.captured()); fin(o,R,MX)
    o['ok']=bool(dstop<=0.5 and slide<0.05 and S.captured() and MX['seated_all'] and MX['roll']<15 and MX['pitch']<15)
    dump('B_estop12_'+ori,o)
elif cmd=='towstab':
    S,R,g=nominal('ESE240SL',110); o=dict(test='towstab',grab=g['result']); MX=MX0(); monitor(R,MX); psi0=S.rpy()[2]
    x0=S.d.xpos[S.bid['tug']].copy()
    R.phase='7a straight 2 m'; R.ctrl_fn=B.heading_hold(R,0.5,psi0); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=2.0,10.0)
    R.phase='7b 90 deg turn'; R.ctrl_fn=B.heading_hold(R,0.5,psi0+90,K=1.2); R.run_for(7.0)
    R.phase='7c slalom'
    for a in (25,-25,25,0): R.ctrl_fn=B.heading_hold(R,0.5,psi0+90+a,K=1.5); R.run_for(3.0)
    R.phase='7d e-stop'; R.ctrl_fn=None; R.hold(); R.run_for(2.0)
    # 180 deg pivot on the spot, swept envelope about the start point of the pivot
    R.phase='7e pivot 180 deg on the spot'; c0=S.d.xpos[S.bid['tug']][:2].copy(); psi1=S.rpy()[2]; rmax=[0.0]
    corners=[(1.09,0.38),(1.09,-0.38),(-0.37,0.48),(-0.37,-0.48)]
    mid=S.m.geom_dataid[S.gid['binhull']]; va=S.m.mesh_vertadr[mid]; nv=S.m.mesh_vertnum[mid]; V=S.m.mesh_vert[va:va+nv].copy()
    gp=S.m.geom_pos[S.gid['binhull']].copy(); Rg=np.zeros(9); mujoco.mju_quat2Mat(Rg,S.m.geom_quat[S.gid['binhull']]); Rg=Rg.reshape(3,3)
    def env():
        Rt=S.d.xmat[S.bid['tug']].reshape(3,3); pt=S.d.xpos[S.bid['tug']]
        for (cx,cy) in corners: q=pt+Rt@np.array([cx,cy,0]); rmax[0]=max(rmax[0],float(np.linalg.norm(q[:2]-c0)))
        Rb=S.d.xmat[S.bid['bin']].reshape(3,3); pb=S.d.xpos[S.bid['bin']]
        for v in V: q=pb+Rb@(gp+Rg@v); rmax[0]=max(rmax[0],float(np.linalg.norm(q[:2]-c0)))
    def piv():
        R.w=0.0; R.wd=0.25/0.165; R.brake=False
    R.ctrl_fn=piv; turned=[0.0]; last=[psi1]
    def done_():
        y=S.rpy()[2]; d=(y-last[0]+180)%360-180; turned[0]+=d; last[0]=y
        if R.i%100==0: env()
        return turned[0]>=180.0
    okp=R.until(done_,30.0); R.ctrl_fn=None; R.hold(); R.run_for(1.0); env()
    drift=float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-c0))
    o.update(pivot_done=bool(okp),pivot_turned_deg=round(turned[0],1),swept_diameter_m=round(2*rmax[0],2),pivot_centre_drift_m=round(drift,3),captured_end=S.captured()); fin(o,R,MX)
    o['ok']=bool(S.captured() and MX['seated_all'] and MX['roll']<10 and okp and 2*rmax[0]<=3.2)
    dump('B_towstab',o)
elif cmd=='rel':
    b,case,fl=sys.argv[2],sys.argv[3],sys.argv[4]
    S,R,g=nominal(b,full=(fl=='full')); o=dict(test='release',bin=b,case=case,fill=fl,grab=g['result']); MX=MX0(); monitor(R,MX); psi0=S.rpy()[2]
    gx={'flat':0.0,'up12':0.12,'dn12':-0.12}[case]
    if gx: R.phase='7a onto %+.0f %% (tug facing %s)'%(gx*100,'uphill' if gx>0 else 'downhill'); R.ramp_grade(gx,0,2.0); R.run_for(1.0)
    x0=S.d.xpos[S.bid['tug']].copy(); R.phase='7 carry 1 m'; R.ctrl_fn=B.heading_hold(R,0.3,psi0)
    R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=1.0,10.0); R.ctrl_fn=None; B.soft_stop(R); R.run_for(0.5)
    sd=B.set_down(R); v=S.d.qvel[S.jv('binfree'):S.jv('binfree')+3]
    o.update(release=sd,bin_tilt_abs_end=round(S.bin_tilt_abs(),1),bin_speed_end=round(float(np.linalg.norm(v)),3))
    o['bin_stable']=bool(S.bin_tilt_abs()<8 and np.linalg.norm(v)<0.05)
    o['ok']=bool(g['result']=='success' and sd.get('released') and o['bin_stable'])
    o['verdict']='PASS' if o['ok'] else ('TIPS' if S.bin_tilt_abs()>30 else ('HOLD' if sd.get('hold') else ('STUCK' if not sd.get('released') else 'FAIL')))
    fin(o,R,MX); dump('B_rel_%s_%s_%s'%(b,case,fl),o)
elif cmd=='static':
    pose,kg=sys.argv[2],float(sys.argv[3])
    S,R,g=nominal('ESE240SL',kg); gx,gy={'flat':(0,0),'up':(0.12,0),'dn':(-0.12,0),'crL':(0,0.12),'crR':(0,-0.12)}[pose]
    R.hold(); R.ramp_grade(gx,gy,2.0); R.run_for(3.0); C=S.contacts()
    o=dict(test='static',pose=pose,kg=kg,grab=g['result'],driveL=round(C['driveL'],1),driveR=round(C['driveR'],1),caster_sum=round(C['casterL']+C['casterR'],1),
           antitip=round(C['antitip0']+C['antitip1'],1),bin_ground=round(S.bin_ground(),1),captured=S.captured(),roll=round(S.rpy()[0],2),pitch=round(S.rpy()[1],2),lift_N=round(S.lift_force()),pad_N=round(C['padg']))
    o['ok']=bool(min(C['driveL'],C['driveR'])>=100 and C['casterL']+C['casterR']>=50 and S.captured())
    dump('B_static_%s_%d'%(pose,kg),o)
