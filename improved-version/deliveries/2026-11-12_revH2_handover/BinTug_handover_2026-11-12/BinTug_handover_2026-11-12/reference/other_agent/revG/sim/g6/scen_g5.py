# Rev G scenario runner (derived from Rev F.1 scenarios.py): drive/brake model, actuator force limit, logging, pose recording,
# plus physical-grabber sequences: grab (approach, swing, latch check, pull test, tip), release (stand, cam, pull-down, clear).
import math, numpy as np, mujoco
from sim_g5 import Sim, act_lever
class Runner:
    def __init__(s, sim, rec_hz=12, log_hz=50):
        s.s=sim; s.t=0.0; s.rec=[]; s.log=[]; s.dt=sim.m.opt.timestep
        s.re=max(1,int(1/(rec_hz*s.dt))); s.le=max(1,int(1/(log_hz*s.dt))); s.i=0; s.phase=''; s.events=[]
        s.phi_cmd=math.radians(sim.kw.get('phi0',8.0)); s.brake=True; s.w=0.0; s.wd=0.0; s.grade=(0,0)
        s.peak_act=0; s.peak_act_at=(0,''); s.act_f=0.0; s.peak_act_f=0.0
        s.hitch_cap=None; s.ctrl_fn=None; s.hud_fn=None; s.wc=0.0; s.wdc=0.0; s._bk=None
        s.peak={}; s.tongue_max=0.0; s.cycled=False; s.recording=True; s.wind=None
    def set_drive(s,v,dv=0.0): s.w=v/0.165; s.wd=dv/0.165; s.brake=False
    def hold(s): s.w=0; s.wd=0; s.brake=True
    def pk(s,k,v):
        if v>s.peak.get(k,(0,0,''))[0]: s.peak[k]=(v,round(s.t,3),s.phase)
    def step(s):
        S=s.s; d=S.d
        if s.ctrl_fn is not None and s.i%20==0: s.ctrl_fn()
        w_eff,wd_eff=s.w,s.wd
        if s.hitch_cap is not None and not s.brake:
            h=S.yaw_rel()
            if s.wd*h<0:
                sc=max(0.0,min(1.0,(s.hitch_cap-abs(h))/20.0))
                if sc<1.0:
                    wd_eff=s.wd*sc
                    if abs(s.w)<0.5 and sc<0.5: w_eff=0.15/0.165
        lev,L=S.update_act_limit(); d.ctrl[2]=s.phi_cmd
        a=0.6/0.165*s.dt
        if s.brake: s.wc=0.0; s.wdc=0.0
        else: s.wc+=max(-a,min(a,w_eff-s.wc)); s.wdc+=max(-a,min(a,wd_eff-s.wdc))
        d.ctrl[0]=s.wc-s.wdc/2; d.ctrl[1]=s.wc+s.wdc/2
        lim=150 if s.brake else 60
        S.m.actuator_forcerange[0]=[-lim,lim]; S.m.actuator_forcerange[1]=[-lim,lim]
        if s.brake!=s._bk: S.set_brake(s.brake); s._bk=s.brake
        S.pre_step()
        if s.wind is not None and S.with_bin:   # wind pressure on the lid (N, world vector) applied at the lid centre
            d.xfrc_applied[S.bid['lid']][:3]=s.wind
        mujoco.mj_step(S.m,d); s.t+=s.dt; s.i+=1
        af=abs(d.actuator_force[2]); an=af/max(lev,1e-3)
        if an>s.peak_act: s.peak_act=an; s.peak_act_at=(round(s.t,3),s.phase)
        s.act_f+=(an-s.act_f)*s.dt/0.05
        if s.act_f>s.peak_act_f: s.peak_act_f=s.act_f
        if S.grabber in ('G','F1'):
            tm=S.tongue_mm(); s.tongue_max=max(s.tongue_max,tm)
        elif S.grabber=='GH' and s.i%10==0:
            pl,pr=S.pawl_deg(); s.pawl_min=min(getattr(s,'pawl_min',0.0),pl,pr)
            if getattr(s,'watch_pawl',False) and min(pl,pr)<-3 and not getattr(s,'pawl_bounce',None): s.pawl_bounce=(round(s.t,3),s.phase,round(min(pl,pr),1))
        if s.i%s.le==0 or (S.grabber in('G','F1','GH') and S.with_bin and s.i%getattr(s,'contact_every',4)==0):
            C=S.contacts()
            if S.with_bin:
                hk=C['hookF'] if S.grabber in('G','F1','GH') else S.hook_eq()
                s.pk('hook',hk); s.pk('tongue',C['tongueF']); s.pk('stopbar',C['stopbar'])
            s.pk('act',an)
            if s.i%s.le==0:
                r,p,y=S.rpy()
                e=dict(t=round(s.t,3),ph=s.phase,cmin=min(C['casterL'],C['casterR']),dmin=min(C['driveL'],C['driveR']),
                       anti=C['antitipL']+C['antitipR'],roll=r,pitch=p,yaw=y,mast=S.tilt(),v=S.fwd_speed(),
                       x=float(d.xpos[S.bid['tug']][0]),y_=float(d.xpos[S.bid['tug']][1]),actN=an,ryaw=S.yaw_rel(),shoes=C['shoes'],
                       tq=float(max(abs(d.actuator_force[0]),abs(d.actuator_force[1]))),stop=C['stopbar'])
                if S.with_bin:
                    e.update(tilt=S.bin_tilt_rel(),byaw=S.bin_yaw_rel(),hook=hk,tongueF=C['tongueF'],bw=C['binwheelL']+C['binwheelR'],
                             bx=float(d.xpos[S.bid['bin']][0]),by=float(d.xpos[S.bid['bin']][1]),btilt=S.bin_tilt_abs())
                    if S.grabber in ('G','F1'):
                        e.update(cap=S.captured(),sen=S.sensors(),tg=S.tongue_mm(),bh=S.bar_in_hook().tolist())
                    elif S.grabber=='GH':
                        e.update(cap=S.captured(),sen=S.sensors(),pw=S.pawl_deg(),bh=S.bar_in_hook().tolist(),fl=float(d.qpos[S.jq('float')]))
                s.log.append(e)
        if s.recording and s.i%s.re==0:
            r=dict(t=round(s.t,3),ph=s.phase,g=list(s.grade),P=S.snapshot(),mast=S.tilt(),act=act_lever(d.qpos[S.jq('tilt')])[1],v=S.fwd_speed(),hitch=S.yaw_rel())
            if S.with_bin:
                r.update(tilt=S.bin_tilt_rel(),hook=s.log[-1].get('hook',0) if s.log else 0)
                if S.grabber in ('G','F1'): r.update(tg=S.tongue_mm(),fl=float(d.qpos[S.jq('float')]),lidq=float(d.qpos[S.jq('lid')]))
                if S.grabber=='GH': r.update(pw=S.pawl_deg(),fl=float(d.qpos[S.jq('float')]),lidq=float(d.qpos[S.jq('lid')]),lat=float(d.qpos[S.jq('lat')]))
            if S.grabber=='G': r['lf']=float(d.qpos[S.jq('lidfinger')])
            if s.hud_fn: r['hud']=s.hud_fn()
            s.rec.append(r)
    def run_for(s,T,fn=None):
        for _ in range(int(T/s.dt)):
            if fn and fn(): return True
            s.step()
        return False
    def until(s,cond,Tmax):
        for _ in range(int(Tmax/s.dt)):
            if cond(): return True
            s.step()
        return False
    def ramp_phi(s,target_deg,rate_deg=1.5,cond=None,Tmax=90,check_every=20):
        tgt=math.radians(target_deg); r=math.radians(rate_deg)*s.dt
        for k in range(int(Tmax/s.dt)):
            if cond and k%check_every==0 and cond(): return True
            dlt=tgt-s.phi_cmd
            if abs(dlt)<1e-6 and abs(s.s.d.qpos[s.s.jq('tilt')]-tgt)<math.radians(0.3): return True
            s.phi_cmd+=max(-r,min(r,dlt)); s.step()
        return False
    def ramp_grade(s,gx,gy,T=2.0):
        g0=s.grade; n=int(T/s.dt)
        for k in range(n):
            f=(k+1)/n; s.grade=(g0[0]+(gx-g0[0])*f,g0[1]+(gy-g0[1])*f); s.s.set_grade(*s.grade); s.step()
    def ev(s,msg): s.events.append((round(s.t,2),msg))
def soft_stop(R, Tmax=3.0):
    S=R.s; R.w=0.0; R.wd=0.0; R.brake=False
    R.until(lambda: abs(S.fwd_speed())<0.02 and abs(R.wc)<0.05, Tmax); R.hold()
def tow(R,v,dist,dv=0.0,Tmax=60):
    S=R.s; x0=S.d.xpos[S.bid['tug']].copy(); R.set_drive(v,dv)
    return R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=dist or abs(S.rpy()[1])>35, Tmax)
def heading_hold(R,v,psi_ref_deg,K=2.0):
    S=R.s
    def ctl():
        e=math.radians((psi_ref_deg-S.rpy()[2]+180)%360-180); R.w=v/0.165; R.wd=max(-0.3,min(0.3,0.69*K*e))/0.165; R.brake=False
    return ctl
# ------------------------------------------------------------------ physical grab (G and F1)
def act_N(S): return abs(S.d.actuator_force[2])/max(act_lever(S.d.qpos[S.jq('tilt')])[0],1e-3)
def bin_rel(S):
    """bin axle centre in the tug frame (x,y m) and bin yaw rel (deg)"""
    Rt=S.d.xmat[S.bid['tug']].reshape(3,3); p=Rt.T@(S.d.xpos[S.bid['bin']]-S.d.xpos[S.bid['tug']]); return float(p[0]),float(p[1]),S.bin_yaw_rel()
def bin_roll_rel(S):
    Rb=S.d.xmat[S.bid['bin']].reshape(3,3); Rt=S.d.xmat[S.bid['tug']].reshape(3,3); R=Rt.T@Rb; return math.degrees(math.atan2(R[2,1],R[2,2]))
def steer_hold(R,v,k=5.0,maxdeg=15.0,bias=0.0):
    """G5c C2: camera-guided reversing. Stanley-type law on the bin centre line: heading ref = bin heading + atan(k*e), e = lateral
    offset of the kingpin (tug origin) from the bin centre line as the camera sees it (+bias = camera error, m)."""
    S=R.s
    def ctl():
        pb=S.d.xpos[S.bid['bin']]; Rb=S.d.xmat[S.bid['bin']].reshape(3,3); psib=math.degrees(math.atan2(Rb[1,0],Rb[0,0]))
        e=float((S.d.xpos[S.bid['tug']]-pb)@Rb[:,1])+bias
        ref=psib+max(-maxdeg,min(maxdeg,math.degrees(math.atan(k*e))))
        er=math.radians((ref-S.rpy()[2]+180)%360-180); R.w=v/0.165; R.wd=max(-0.3,min(0.3,0.69*2.0*er))/0.165; R.brake=False
    return ctl
def approach(R, approach_v=0.10, Tmax=14.0):
    S=R.s; psi0=S.rpy()[2]
    if S.grabber=='G' or (S.grabber=='GH' and S.GHV['mode']=='below'): S.cam_state=2          # cam "open" before the approach: hook low, tongue back, lid finger lifted
    S.yaw_lock(False)     # G3: rear frame yaw FREE while reversing in (as for the charging dock) so the funnel can square it on the bin wheels
    RA=S.kw.get('reapp')
    if RA:
        if not hasattr(R,'cam_bias'):
            rng=np.random.default_rng(int(abs(S.kw['tug_pose'][1])*1e5+abs(S.kw['tug_pose'][2])*100)); R.cam_bias=float(rng.normal(0,RA.get('sigma',0.008)))
        R.phase='1 Approach: camera-guided reversing onto the bin centre line (yaw lock off)'
        R.ctrl_fn=steer_hold(R,-approach_v,RA.get('k',5.0),RA.get('maxdeg',15.0),R.cam_bias) if RA.get('steer',True) else heading_hold(R,-approach_v,psi0)
    else:
        R.phase='1 Approach: reversing into bin (yaw lock off)'; R.ctrl_fn=heading_hold(R,-approach_v,psi0)
    def both():
        C=S.contacts(); return C.get('stopL',0)>20 and C.get('stopR',0)>20
    ok=R.until(lambda: S.contacts()['stopbar']>40, Tmax)
    if ok:
        R.phase='1b Squaring: creep until both wheel-contact switches close'
        if S.kw.get('square_guard'):
            # G5 firmware guard: stop squaring (and stop pushing the bin) if the rear frame swings > 25 deg or the tug creeps > 0.15 m
            x0=S.d.xpos[S.bid['tug']].copy()
            def sq():
                if both(): return True
                if abs(S.yaw_rel())>25 or np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>0.15: R.guard=True; return True
                return False
            R.guard=False; R.until(sq,5.0)
            if R.guard:
                R.ctrl_fn=None; R.hold(); R.ev('SQUARING GUARD: rear frame %.1f deg / creep, stop + back off (no dock)'%S.yaw_rel())
                R.set_drive(0.15); R.run_for(2.0); R.hold(); R.run_for(0.5); return False
        else: R.until(both,5.0)
    R.ctrl_fn=None
    R.ev('wheel-stop contact, both wheels %s'%both() if ok else 'NO wheel-stop contact')
    R.phase='2 Docked: brakes on, yaw lock on'; R.hold(); S.yaw_lock(True); R.run_for(0.5)
    if ok and RA and not getattr(R,'reapp_done',False):
        dy=bin_rel(S)[1]+R.cam_bias; R.dock_dy_mm=round(bin_rel(S)[1]*1000,1)
        if abs(dy)>RA.get('thr',0.030):
            R.reapp_done=True; R.ev('lateral offset %.0f mm (camera %.0f) > %.0f: pull forward %.2f m and re-approach'%(bin_rel(S)[1]*1000,dy*1000,RA.get('thr',0.03)*1000,RA.get('fwd',0.4)))
            R.phase='1r Re-approach: pull forward 0.4 m'; x0=S.d.xpos[S.bid['tug']].copy(); psi1=S.rpy()[2]
            R.ctrl_fn=heading_hold(R,0.15,psi1); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=RA.get('fwd',0.4),8.0)
            R.ctrl_fn=None; R.hold(); R.run_for(0.4)
            return approach(R,approach_v,Tmax)
    return ok
def grab_phys(R, tip_to=25.0, swing_rate=1.5, approach_v=0.10, pull=True):
    """returns dict(result=..., claim=..., captured=...). result: success | false_positive | safe_miss | bin_pushed | no_dock"""
    S=R.s; out=dict()
    ok=approach(R,approach_v); out['docked']=ok
    if not ok: out.update(result='no_dock',claim=False,captured=False); return out
    st=dict(cyc=False)
    if S.grabber=='G':
        R.phase='3a Cam to "open": tongue back, hook pulled to the bottom of its float'; S.cam_state=2; R.run_for(1.2)
        def swing_cond():
            if S.sensors(strict=True)[0]: return True
            if S.bin_tilt_abs()>6: st['abort']='bin pushed'; return True
            if act_N(S)>700: st['abort']='actuator stall'; return True
            return False
        R.phase='3b Mast swings back: lip passes under the handle'
        R.ramp_phi(-12.0,swing_rate,cond=swing_cond); R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.run_for(0.3)
        if S.sensors(strict=True)[0] and not st.get('abort'):
            R.phase='3c Cam to "rise": hook rises (ratchet) until the cup meets the bar'; S.cam_state=1; R.run_for(1.8)
            R.phase='3d Cam to "latched": tongue springs out over the bar'; S.cam_state=0; R.run_for(1.0)
            st['cyc']=True
        fq=float(S.d.qpos[S.jq('float')]); out['float_mm']=round(fq*1000,1)
        top=fq>GG_up()-0.004
        seat,latch=S.sensors(); claim=bool(seat and latch and not top)
    else:
        def swing_cond():
            sen=S.sensors()
            if S.tongue_mm()>6: st['cyc']=True
            if sen[0] and sen[1] and st['cyc']: return True
            if S.bin_tilt_abs()>6: st['abort']='bin pushed'; return True
            if act_N(S)>700: st['abort']='actuator stall'; return True
            return False
        R.phase='3 Mast swings back: hook rides onto handle'
        R.ramp_phi(-12.0,swing_rate,cond=swing_cond); R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.run_for(0.6)
        seat,latch=S.sensors(); claim=bool(seat and latch and st['cyc'])
    out['swing_end_phi']=round(S.tilt(),1); out['abort']=st.get('abort'); out['bar_mm']=[round(x,1) for x in S.bar_in_hook()]
    R.ev(f"swing end phi {S.tilt():.1f}  seat {seat} latch {latch} abort {st.get('abort')} bar {out['bar_mm']}")
    if claim and pull:
        R.phase='4 Pull test: mast +2.5 deg, load must rise, switches stay closed'
        f0=act_N(S); t0=S.bin_tilt_rel()
        R.ramp_phi(S.tilt()+2.5,1.0); R.run_for(0.5)
        f1=act_N(S); seat,latch=S.sensors()
        rise=f1-f0; out['pull_rise_N']=round(rise); out['pull_dtilt']=round(S.bin_tilt_rel()-t0,2)
        claim=bool((seat or S.grabber=='G') and latch and (rise>40 or S.bin_tilt_rel()-t0>0.5))
        R.ev(f'pull test rise {rise:.0f} N dtilt {S.bin_tilt_rel()-t0:.2f} -> {"PASS" if claim else "FAIL"}')
    out['claim']=claim; cap0=S.captured(); out['captured_at_claim']=cap0
    if not claim:
        out['captured']=cap0; out['result']='bin_pushed' if (S.bin_tilt_abs()>6 or st.get('abort')=='bin pushed') else 'safe_miss'
        return out
    import os as _os
    if _os.environ.get('G6_RATCHET_TIP')=='1' and getattr(S,'ratchet_on',False):   # G6 fix: ratchet pawl lifted right after the claim, before tipping
        S.ratchet_on=False; jf=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'float'); S.m.jnt_range[jf][0]=-S.GHV['float_down']; S._float_grab=float(S.d.qpos[S.jq('float')])
        R.ev('float ratchet released after claim (tip with free float)')
    R.phase='5 Tipping: mast rocks forward, wheels held by stop bar'
    capt=[True]
    def tip_cond():
        if not S.captured(): capt[0]=False
        return S.bin_tilt_rel()>=tip_to
    R.ramp_phi(75,1.5,cond=tip_cond,Tmax=60); R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.run_for(1.0)
    held=S.captured() and capt[0] and S.bin_tilt_rel()>tip_to-4
    out['tilt_reached']=round(S.bin_tilt_rel(),1); out['captured']=bool(held)
    out['result']='success' if held else 'false_positive'
    R.ev(f"tipped to {S.bin_tilt_rel():.1f} deg, captured throughout {capt[0]}")
    return out
def GG_up():
    import geo_g3 as GG; return GG.G_FLOAT['up']
def tip_more(R,target=48.0):
    S=R.s; R.phase='5 Tipping to tow pose'
    R.ramp_phi(75,1.5,cond=lambda: S.bin_tilt_rel()>=target,Tmax=60); R.phi_cmd=S.d.qpos[S.jq('tilt')]
    R.phase='6 Tow pose reached: yaw lock released'; S.yaw_lock(False); R.run_for(1.0)
def stand_up(R):
    S=R.s
    import os as _os
    if _os.environ.get('G6_STRAIGHTEN')=='1' and abs(S.yaw_rel())>1.5 and not getattr(S,'_ylocked',False):   # G6 fix: creep forward on heading until the hitch is straight
        R.phase='8b Straighten: creep forward 0.15 m/s on heading until hitch < 1.5 deg'; psi=S.rpy()[2]; x0=S.d.xpos[S.bid['tug']].copy(); y0=S.yaw_rel()
        def follow():   # steer the tug onto the rear frame's heading while creeping forward (hitch -> 0)
            R.w=0.15/0.165; R.wd=max(-0.3,min(0.3,0.69*1.5*math.radians(S.yaw_rel())))/0.165; R.brake=False
        R.ctrl_fn=follow; R.until(lambda: abs(S.yaw_rel())<1.0 or np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>1.5,15.0)
        R.ctrl_fn=None; soft_stop(R); R.run_for(0.5)
        R.ev('straighten: hitch %.1f -> %.1f deg over %.2f m'%(y0,S.yaw_rel(),float(np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2]))))
        if _os.environ.get('G6_STRAIGHTEN')=='1' and _os.environ.get('G6_PIVOT')=='1' and abs(S.yaw_rel())>1.0:   # G6 fixR7: then pivot in place onto the rear-frame heading (zero-radius turn, max 6 s)
            R.phase='8c Straighten: pivot in place until hitch < 0.8 deg'; y1=S.yaw_rel()
            def piv():
                h=S.yaw_rel(); R.w=0.0; R.wd=math.copysign(min(0.25,max(0.06,0.8*math.radians(abs(h))*4)),h)/0.165; R.brake=False
            R.ctrl_fn=piv; R.until(lambda: abs(S.yaw_rel())<0.8,6.0); R.ctrl_fn=None; R.hold(); R.run_for(0.5)
            R.ev('pivot: hitch %.1f -> %.1f deg'%(y1,S.yaw_rel()))
    if _os.environ.get('G6_PINLOCK')=='1' and abs(S.yaw_rel())>float(_os.environ.get('G6_PINTOL','2.0')):   # G6: real yaw lock is a solenoid PIN - it cannot engage off-centre
        R.pin_fail=True; R.ev('yaw pin cannot engage: hitch at %.1f deg -> release aborted, hold + alert'%S.yaw_rel()); R.hold(); return
    R.phase='9 Yaw locked; standing bin up (wheel-stop holds the wheels)'; R.hold(); S.yaw_lock(True); R.run_for(1.0)
    if _os.environ.get('G6_RATCHET_STAND')=='1' and getattr(S,'ratchet_on',False):   # G6 fixR8: ratchet pawl lifted again for the stand-up (else the locked float lifts the bin by the lip as the mast comes back)
        S.ratchet_on=False; jf=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'float'); S.m.jnt_range[jf][0]=-S.GHV['float_down']; R.ev('float ratchet lifted for stand-up')
    if _os.environ.get('G6_STANDFIX')=='1':   # G6 fix: stand-up ends on the IMU (tug level, castors down) + bin upright to the ground, not on rel tilt
        fg=getattr(S,'_float_grab',None); fq=lambda: float(S.d.qpos[S.jq('float')])
        fup=float(S.GHV.get('float_up',0.13))
        fok=lambda: True if fg is None else ((fq()-fg<0.040 or not S.ratchet_on) and fq()<fup-0.010)   # float within 40 mm of its grab position and off its top stop = hook not lifting the bin
        if _os.environ.get('G6_STANDWORLD')=='sweep':   # diagnostic only: keep standing to rel -8 deg (diag_stand_g6.py logs where the tug levels)
            R.ramp_phi(-4.0,1.5,cond=lambda: S.bin_tilt_rel()<=-8.0,Tmax=80)
        elif _os.environ.get('G6_STANDWORLD')=='1':   # G6 fixR7: stop when the bin is upright in the WORLD (IMU pitch + mast angle), not relative to a pitched tug; never past rel -8 deg
            R.ramp_phi(-4.0,1.5,cond=lambda: (S.bin_tilt_rel()+S.rpy()[1])<=0.3 or S.bin_tilt_rel()<=-8.0,Tmax=80)
        else: R.ramp_phi(-4.0,1.5,cond=lambda: S.bin_tilt_rel()<=0.3,Tmax=80)   # v4: stop on rel tilt (as designed), then interlock - never push the bin past upright; R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.run_for(0.8)
        R.ev('bin upright %.1f deg rel, %.1f abs, tug pitch %.1f deg, mast %.1f, float %+.0f mm vs grab'%(S.bin_tilt_rel(),S.bin_tilt_abs(),S.rpy()[1],S.tilt(),1000*(fq()-(fg or 0))))
        if abs(S.rpy()[1])>2.5 or S.bin_tilt_abs()>3.0 or not fok():
            R.pin_fail=True; R.ev('interlock: tug pitch %.1f deg / float %+.0f mm -> bin may be hanging -> cam NOT opened, hold + alert'%(S.rpy()[1],1000*(fq()-(fg or 0))))
        return
    R.ramp_phi(-4.0,1.5,cond=lambda: S.bin_tilt_rel()<=0.3,Tmax=80); R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.run_for(0.8)
    R.ev('bin upright %.1f deg'%S.bin_tilt_rel())
def release_G(R, retries=2):
    """cam -> 1 (tongue back) -> 2 (ratchet up, cord pulls hook down), mast forward, drive clear. Returns released flag."""
    S=R.s; stand_up(R)
    released=False
    for k in range(retries+1):
        R.phase=f'10 Release cam: tongue retracts{" (retry %d)"%k if k else ""}'
        S.cam_state=1; R.run_for(1.5)
        if S.tongue_mm()>30: released=True; break
        R.ev(f'tongue did not retract (try {k+1}): {S.tongue_mm():.1f} mm, latch switch still closed'); S.cam_state=0
        R.phase=f'10b Unload and retry ({k+1})'
        R.phi_cmd+=math.radians(1.5); R.run_for(0.8); R.phi_cmd-=math.radians(1.5); R.run_for(0.8)
    if not released: R.ev('RELEASE FAILED: latch still closed'); return False
    R.phase='11 Cam to "open": ratchet lifted, cord pulls hook below the bar'; S.cam_state=2; R.run_for(1.5)
    R.phase='12 Mast forward: lip passes under the bar'; R.ramp_phi(10.0,3.0); R.run_for(0.5)
    R.phase='13 Driving clear'; R.set_drive(0.25); R.run_for(3.0); R.hold()
    R.phase='14 Cam home'; S.cam_state=0; R.run_for(0.8)
    return True
def release_F1(R):
    """Rev F.1 sequence as written: stand, solenoid pulse (tongue retracts), mast forward 9 deg, drive away"""
    S=R.s; stand_up(R)
    R.phase='10 Solenoid pulse: tongue retracted'; S.cam_state=1; R.run_for(1.0)
    R.phase='11 Mast forward 9 deg (F.1 sequence)'; R.ramp_phi(9.0,3.0); R.run_for(0.5)
    R.phase='12 Driving away'; R.set_drive(0.3); R.run_for(4.0); R.hold(); S.cam_state=0; R.run_for(1.0)
    return True
# ------------------------------------------------------------------ F.1 idealised latch (traction/mass tests)
def grab_eq(R, tilt_target=48.0):
    S=R.s
    R.phase='1 Approach: reversing into bin'; R.set_drive(-0.10)
    ok=R.until(lambda: S.contacts()['stopbar']>40, 12); R.hold(); R.run_for(0.5)
    R.phase='3 Mast swings back'
    sid=S.sid['hookc']
    def gap():
        Rt=S.d.xmat[S.bid['tug']].reshape(3,3); hk=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_SITE,'hookL')
        return Rt.T@(S.d.site_xpos[hk]-S.d.site_xpos[S.sid['handleL']])
    R.ramp_phi(-6.0,1.5,cond=lambda: gap()[0]<=0.002)
    R.phi_cmd=S.d.qpos[S.jq('tilt')]; S.latch_soft(True); S.latch(True,capture=False); R.run_for(0.6); S.latch_soft(False)
    R.phase='5 Tipping'; R.ramp_phi(75,1.5,cond=lambda: S.bin_tilt_rel()>=tilt_target)
    R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.phase='6 Tow pose'; S.yaw_lock(False); R.run_for(1.5)
    return S.bin_tilt_rel()>tilt_target-3

# ------------------------------------------------------------------ G3: G-hook (twin hooks + pawls)
def grab_GH(R, tip_to=25.0, swing_rate=1.5, approach_v=0.10, pull=True):
    S=R.s; V=S.GHV; out=dict(variant=S.kw.get('gh'))
    ok=approach(R,approach_v); out['docked']=ok
    if not ok: out.update(result='no_dock',claim=False,captured=False); return out
    st=dict(cyc=False)
    def abort_chk():
        if S.bin_tilt_abs()>6: st['abort']='bin pushed'; return True
        if act_N(S)>900: st['abort']='actuator stall'; return True
        return False
    if V['mode']=='below':
        R.phase='3a Cam OPEN: pawls up, hook pulled to the bottom of its float'; S.cam_state=2; R.run_for(1.2)
        R.phase='3b Mast swings back: lips pass under the handle bar'
        def swc():
            if S.sensors(strict=True)[0]: st['seat']=True; return True
            return abort_chk()
        R.ramp_phi(-15.0,swing_rate,cond=swc); R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.run_for(0.3)
        if st.get('seat') and not st.get('abort'):
            R.phase='3c Mast eases off 0.6 deg (unload the back wall), cam RISE: float rises (ratchet) until the cups meet the bar'
            R.phi_cmd+=math.radians(V.get('ease',1.0)); R.run_for(0.4); S.cam_state=1; R.run_for(1.8)
            R.phase='3d Cam CLOSED: pawls drop over the bar'; S.cam_state=0; R.run_for(1.0); st['cyc']=True
            if V.get('reclose'):
                # G6 firmware: one re-rise if the latch switch did not close or a cup-floor feeler is open (bar left high by back-wall friction)
                def feel_ok():
                    rr_=S.kw.get('bar_r',0.016)*1000; th0=float(V.get('throat',-24.0)); T0=float(V.get('feel_T',12.0))
                    return all(th0<q[0]<24 and -26-4<(q[2]-rr_)<-26+T0 for q in S.bar_at_hooks())
                if not S.sensors()[1] or not feel_ok():
                    out['reclose']=True; R.ev('re-rise: latch %s feelers %s -> cam RISE, ease a further %.1f deg, close again'%(S.sensors()[1],feel_ok(),V['reclose']))
                    R.phase='3e Re-rise: cam RISE, mast eases a further %.1f deg, cam CLOSED'%V['reclose']
                    S.cam_state=1; R.run_for(0.3); R.phi_cmd+=math.radians(V['reclose']); R.run_for(1.8); S.cam_state=0; R.run_for(1.0)
        fq=float(S.d.qpos[S.jq('float')]); out['float_mm']=round(fq*1000,1)
        top=fq>V['float_up']-0.004
        seat,latch=S.sensors(); seat=bool(st.get('seat'))      # seat vane gated the rise; after the 0.6 deg ease-off it may reopen
        claim=bool(latch and st['cyc'] and not top)
    else:
        S.cam_state=0
        def cond():
            pl,pr=S.pawl_deg()
            if min(pl,pr)<-8: st['cyc']=True
            sen=S.sensors()
            if sen[0] and sen[1] and st['cyc']: return True
            return abort_chk()
        R.phase='3 Mast swings back: bar rides the ramp, snaps over the lip, pushes the pawls up'
        R.ramp_phi(-12.0,swing_rate,cond=cond); R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.run_for(0.6)
        out['float_mm']=round(float(S.d.qpos[S.jq('float')])*1000,1)
        seat,latch=S.sensors(); claim=bool(seat and latch and st['cyc'])
    out['swing_end_phi']=round(S.tilt(),1); out['abort']=st.get('abort'); out['bar_mm']=[round(float(x),1) for x in S.bar_in_hook()]
    out['pawls_deg']=[round(x,1) for x in S.pawl_deg()]
    # G5 instrumentation: per-hook "bar on cup floor" feeler (bar underside within 6 mm of the floor at z=-26 and inside the throat |x|<24)
    rr=S.kw.get('bar_r',0.016)*1000*(1 if S.kw.get('bar_shape','tube')=='tube' else 1)
    hh=S.kw.get('handle_half',0.27)*1000; p_=S.bar_in_hook(); hyk=S.GHV['hy']
    # feeler only sees something when its plate overlaps the bar or a web (plate entirely outside the outer web -> open)
    th_=float(S.GHV.get('throat',-24.0)); T_=float(S.GHV.get('feel_T',12.0))
    out['feel']=[dict(x=round(float(q[0]),1),h=round(float(q[2]-rr+26),1),over=bool(abs(yk-p_[1])-5<hh+20)) for q,yk in zip(S.bar_at_hooks(),(hyk,-hyk))]   # G6: h = bar underside above the steel cup floor (mm)
    out['cupfloor']=[bool(th_<q[0]<24 and (q[2]-rr)<-26+T_ and (q[2]-rr)>-26-4 and abs(yk-p_[1])-5<hh+20) for q,yk in zip(S.bar_at_hooks(),(hyk,-hyk))]
    out['lat_mm']=round(float(S.d.qpos[S.jq('lat')])*1000,1); out['dock_dy_mm']=getattr(R,'dock_dy_mm',None); out['reapp']=bool(getattr(R,'reapp_done',False))
    out['bin_dy_dock_mm']=round(bin_rel(S)[1]*1000,1)
    R.ev(f"swing end phi {S.tilt():.1f} seat {seat} latch {latch} abort {st.get('abort')} bar {out['bar_mm']} pawls {out['pawls_deg']}")
    if claim and pull:
        R.phase='4 Pull test: mast +2.5 deg, load must rise, switches stay closed'
        f0=act_N(S); t0=S.bin_tilt_rel(); y0=S.bin_yaw_rel(); r0=bin_roll_rel(S); l0=float(S.d.qpos[S.jq('lat')])
        R.ramp_phi(S.tilt()+2.5,1.0); R.run_for(0.5)
        f1=act_N(S); seat,latch=S.sensors(); rise=f1-f0
        out['pull_rise_N']=round(rise); out['pull_dtilt']=round(S.bin_tilt_rel()-t0,2)
        out['pull_dyaw']=round(S.bin_yaw_rel()-y0,3); out['pull_droll']=round(bin_roll_rel(S)-r0,3); out['pull_dlat_mm']=round((float(S.d.qpos[S.jq('lat')])-l0)*1000,2)
        claim=bool(latch and (rise>40 or S.bin_tilt_rel()-t0>0.5))
        AS=S.kw.get('asym')
        if AS and claim and (abs(out['pull_droll'])>AS.get('roll',9e9) or abs(out['pull_dyaw'])>AS.get('yaw',9e9) or abs(out['pull_dlat_mm'])>AS.get('lat',9e9)):
            claim=False; R.ev('claim refused: pull-test asymmetry droll %.2f dyaw %.2f dlat %.1f'%(out['pull_droll'],out['pull_dyaw'],out['pull_dlat_mm']))
        R.ev(f'pull test rise {rise:.0f} N dtilt {S.bin_tilt_rel()-t0:.2f} -> {"PASS" if claim else "FAIL"}')
    if S.kw.get('claim_and') and claim and not all(out['cupfloor']):
        claim=False; R.ev('claim refused: cup-floor feelers %s (both must close)'%out['cupfloor'])
    out['claim']=claim; out['captured_at_claim']=S.captured()
    if not claim:
        out['captured']=out['captured_at_claim']; out['result']='bin_pushed' if (S.bin_tilt_abs()>6 or st.get('abort')=='bin pushed') else 'safe_miss'
        return out
    import os as _os
    if _os.environ.get('G6_RATCHET_TIP')=='1' and getattr(S,'ratchet_on',False):   # G6 fix: ratchet pawl lifted right after the claim, before tipping
        S.ratchet_on=False; jf=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'float'); S.m.jnt_range[jf][0]=-S.GHV['float_down']; S._float_grab=float(S.d.qpos[S.jq('float')])
        R.ev('float ratchet released after claim (tip with free float)')
    R.phase='5 Tipping: mast rocks forward, wheels held by stop bar'
    capt=[True]
    def tip_cond():
        if not S.captured(): capt[0]=False
        return S.bin_tilt_rel()>=tip_to
    R.ramp_phi(75,1.5,cond=tip_cond,Tmax=60); R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.run_for(1.0)
    held=S.captured() and capt[0] and S.bin_tilt_rel()>tip_to-4
    out['tilt_reached']=round(S.bin_tilt_rel(),1); out['captured']=bool(held)
    out['result']='success' if held else 'false_positive'
    R.ev(f"tipped to {S.bin_tilt_rel():.1f} deg, captured throughout {capt[0]}")
    return out
def bar_clear(S):
    """bar centre distance from the cup centre (mm) and whether it is outside every hook/pawl"""
    p=S.bar_in_hook(); return float(np.hypot(p[0],p[2])), bool(not (-60<p[0]<60 and -60<p[2]<70))
def release_GH(R, retries=2, clear_mode='mast'):
    """B: cam OPEN (pawls up, ratchet lifted, cord pulls the hooks DOWN under the bar = drop-away), then mast forward / drive clear.
    A: as specified - cam lifts the pawls at mast upright, mast forward 9 deg, drive away."""
    S=R.s; V=S.GHV; stand_up(R); out=dict()
    if getattr(R,'pin_fail',False): out.update(opened=False,released=False,pin_fail=True); return out
    if V['mode']=='passive':
        R.phase='10 Release cam lifts pawls (mast upright)'; S.cam_state=1; R.run_for(1.0)
        R.phase='11 Mast forward 9 deg (spec sequence)'; R.ramp_phi(9.0,3.0); R.run_for(0.5)
        R.phase='12 Driving away'; R.set_drive(0.25); R.run_for(3.0); R.hold(); S.cam_state=0
    else:
        opened=False
        for k in range(retries+1):
            R.phase=f'10 Cam OPEN: pawls lift, ratchet lifts, hooks pulled down{" (retry %d)"%k if k else ""}'
            S.cam_state=2; R.run_for(1.5)
            pl,pr=S.pawl_deg(); p=S.bar_in_hook(); r=S.kw.get('bar_r',0.016)*1000
            if min(-pl,-pr)>60 and p[2]-r>2: opened=True; break
            R.ev(f'release not clear (try {k+1}): pawls {pl:.0f}/{pr:.0f} deg, bar z {p[2]:.0f} mm')
            if k==retries: break
            R.phase=f'10b Unload and retry ({k+1}): mast eases forward 0.8 deg, cam re-cycled'
            S.cam_state=0; R.run_for(0.6); R.phi_cmd+=math.radians(0.8); R.run_for(0.8)
        out['opened']=opened
        if not opened:
            pl,pr=S.pawl_deg(); p=S.bar_in_hook()
            why='pawls open but bar %.0f mm from the cup (bin not standing on its wheels / already dropped)'%float(np.hypot(p[0],p[2])) if min(-pl,-pr)>60 else 'latch/pawl still closed'
            R.ev('RELEASE FAILED: %s -> hold + alert, manual lever'%why); out.update(released=False,fail_reason=why); return out
        if clear_mode=='mast':
            R.phase='11 Mast forward: lips pass under the bar'; R.ramp_phi(10.0,3.0); R.run_for(0.5)
            R.phase='12 Driving clear'; R.set_drive(0.25); R.run_for(3.0); R.hold()
        else:
            R.phase='11 Driving clear with mast held (hooks stay low)'; R.set_drive(0.20); R.run_for(2.0); R.hold()
            R.ramp_phi(10.0,3.0)
        R.phase='13 Cam home'; S.cam_state=0; R.run_for(0.8)
    R.phase='14 Bin standing alone'; R.run_for(3.0)
    d,clr=bar_clear(S); out.update(released=bool(clr),bar_dist_mm=round(d),bin_tilt_end=round(S.bin_tilt_abs(),1))
    return out
