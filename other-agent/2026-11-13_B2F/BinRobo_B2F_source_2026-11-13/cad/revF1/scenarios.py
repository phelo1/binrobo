# Rev F scenario runner: full grab/tip/tow/stand/release state machine + terrain/grade tests. Records poses for video.
import json, math, sys, numpy as np, mujoco
from sim_revF import Sim, act_lever
R2D=180/math.pi
class Runner:
    def __init__(s, sim, rec_hz=20, log_hz=20):
        s.s=sim; s.t=0.0; s.rec=[]; s.log=[]; s.dt=sim.m.opt.timestep
        s.re=max(1,int(1/(rec_hz*s.dt))); s.le=max(1,int(1/(log_hz*s.dt))); s.i=0; s.phase=''; s.events=[]
        s.phi_cmd=math.radians(sim.kw.get('phi0',8.0)); s.brake=True; s.w=0.0; s.wd=0.0; s.grade=(0,0); s.peak_act=0
        s.peak_act_at=(0,''); s.act_f=0.0; s.peak_act_f=0.0; s.peak_act_f_at=(0,'')   # raw per-step peak and 50 ms-filtered peak
        s.hitch_cap=None; s.capped=0; s.ctrl_fn=None; s.hud_fn=None
    def set_drive(s,v,dv=0.0):  # v m/s forward, dv = right-left wheel speed difference m/s
        s.w=v/0.165; s.wd=dv/0.165; s.brake=False
    def hold(s): s.w=0; s.wd=0; s.brake=True
    def step(s):
        S=s.s; d=S.d
        if s.ctrl_fn is not None and s.i%20==0: s.ctrl_fn()      # 100 Hz outer-loop controller (heading / docking)
        w_eff,wd_eff=s.w,s.wd
        if s.hitch_cap is not None and not s.brake:            # firmware hitch-angle cap (soft): taper steering into the cap over the last 20 deg;
            h=S.yaw_rel()                                       # a spin requested at the cap becomes a forward creep so the bin follows
            if s.wd*h<0:
                sc=max(0.0,min(1.0,(s.hitch_cap-abs(h))/20.0))
                if sc<1.0:
                    if s.i%20==0: s.capped+=1
                    wd_eff=s.wd*sc
                    if abs(s.w)<0.5 and sc<0.5: w_eff=0.15/0.165
        lev,L=S.update_act_limit()
        d.ctrl[2]=s.phi_cmd
        a=0.6/0.165*s.dt
        s.wc=getattr(s,'wc',0.0); s.wdc=getattr(s,'wdc',0.0)
        if s.brake: s.wc=0.0; s.wdc=0.0
        else:
            s.wc+=max(-a,min(a,w_eff-s.wc)); s.wdc+=max(-a,min(a,wd_eff-s.wdc))
        d.ctrl[0]=s.wc-s.wdc/2; d.ctrl[1]=s.wc+s.wdc/2
        lim=150 if s.brake else 60
        S.m.actuator_forcerange[0]=[-lim,lim]; S.m.actuator_forcerange[1]=[-lim,lim]
        if s.brake!=getattr(s,'_bk',None): S.set_brake(s.brake); s._bk=s.brake
        mujoco.mj_step(S.m,d); s.t+=s.dt; s.i+=1
        af=abs(d.actuator_force[2]); an=af/max(lev,1e-3)
        if an>s.peak_act: s.peak_act=an; s.peak_act_at=(round(s.t,3),s.phase)
        s.act_f+=(an-s.act_f)*s.dt/0.05
        if s.act_f>s.peak_act_f: s.peak_act_f=s.act_f; s.peak_act_f_at=(round(s.t,3),s.phase)
        if s.i%s.le==0:
            N=S.normals(); r,p,y=S.rpy()
            s.log.append(dict(t=round(s.t,3),ph=s.phase,cmin=min(N['casterL'],N['casterR']),dmin=min(N['driveL'],N['driveR']),
                bw=N['binwheelL']+N['binwheelR'],stop=N['stopbar'],arm=N['armL']+N['armR'],anti=N['antitipL']+N['antitipR'],
                hit=N['pod']+N['deckrear']+N['spine'],hook=float(S.hook().sum()),roll=r,pitch=p,yaw=y,tilt=S.bin_tilt_rel(),
                byaw=S.bin_yaw_rel(),ryaw=S.yaw_rel(),mast=S.tilt(),fl=S.floatpos(),v=S.fwd_speed(),x=float(d.xpos[S.bid['tug']][0]),
                y_=float(d.xpos[S.bid['tug']][1]),actN=af/max(lev,1e-3),actL=L,hgap=S.hook_gap()*1000 if S.d.eq_active[0] else 0.0,bump=N['bumper'],tq=float(max(abs(d.actuator_force[0]),abs(d.actuator_force[1])))))
        if s.i%s.re==0:
            s.rec.append(dict(t=round(s.t,3),ph=s.phase,g=list(s.grade),P=S.snapshot(),mast=S.tilt(),tilt=S.bin_tilt_rel(),
                act=act_lever(d.qpos[S.jq('tilt')])[1],hook=float(S.hook().sum()),cmin=s.log[-1]['cmin'] if s.log else 0,v=S.fwd_speed(),
                hitch=S.yaw_rel()))
            if s.hud_fn: s.rec[-1]['hud']=s.hud_fn()
    def run_for(s,T,fn=None):
        n=int(T/s.dt)
        for _ in range(n):
            if fn: 
                if fn(): return True
            s.step()
        return False
    def until(s,cond,Tmax):
        n=int(Tmax/s.dt)
        for _ in range(n):
            if cond(): return True
            s.step()
        return False
    def ramp_phi(s,target_deg,rate_deg=1.5,cond=None,Tmax=90):
        tgt=math.radians(target_deg); r=math.radians(rate_deg)*s.dt; n=int(Tmax/s.dt)
        for _ in range(n):
            if cond and cond(): return True
            dlt=tgt-s.phi_cmd
            if abs(dlt)<1e-6 and abs(s.s.d.qpos[s.s.jq('tilt')]-tgt)<math.radians(0.3): return True
            s.phi_cmd+=max(-r,min(r,dlt)); s.step()
        return False
    def ramp_grade(s,gx,gy,T=2.0):
        g0=s.grade; n=int(T/s.dt)
        for k in range(n):
            f=(k+1)/n; s.grade=(g0[0]+(gx-g0[0])*f,g0[1]+(gy-g0[1])*f); s.s.set_grade(*s.grade); s.step()
    def ev(s,msg): s.events.append((round(s.t,2),msg))
def arc_closed(R, v, radius, angle_deg, Kp=1.5, W=0.69, Tmax=30.0, dv_max=0.45):
    """Closed-loop bend: reference heading advances at v/R; dv = W*(v/R + Kp*heading error). Stops when target heading reached."""
    S=R.s; y0=S.rpy()[2]; t0=R.t; st=dict(yref=0.0)
    def unwrap(a): return (a+180)%360-180
    def ctl():
        tt=R.t-t0; yref=min(math.degrees(v/radius*tt),angle_deg); e=math.radians(unwrap(yref-(S.rpy()[2]-y0)))
        ff=v/radius if yref<angle_deg else 0.0
        R.w=v/0.165; R.wd=max(-dv_max,min(dv_max,W*(ff+Kp*e)))/0.165; R.brake=False; st['yref']=yref
    R.ctrl_fn=ctl; ctl()
    ok=R.until(lambda: unwrap(S.rpy()[2]-y0)>=angle_deg-1.0, Tmax); R.ctrl_fn=None
    return ok, unwrap(S.rpy()[2]-y0), R.t-t0
def soft_stop(R, Tmax=3.0):
    """F.1 normal stop: ramp wheel speed down at the 0.6 m/s^2 drive limit, then apply the spring brakes (e-stop still clamps at once)."""
    S=R.s; R.w=0.0; R.wd=0.0; R.brake=False
    R.until(lambda: abs(S.fwd_speed())<0.02 and abs(R.wc)<0.05, Tmax); R.hold()
def grab(R, tilt_target=48.0):
    S=R.s
    R.phase='1 Approach: reversing into bin'; R.set_drive(-0.10)
    ok=R.until(lambda: S.normals()['stopbar']>40, 12); R.ev('wheel-stop contact' if ok else 'NO wheel-stop contact')
    R.phase='2 Docked: brakes on'; R.hold(); R.run_for(0.5)
    R.phase='3 Mast swings back: hooks ride over handle'
    R.ramp_phi(-6.0,1.5,cond=lambda: S.gap_vec()[0]<=0.002)
    g=S.gap_vec(); R.ev('hook reached handle, offset mm '+str((g*1000).round(1)))
    if abs(g[0])<0.01 and abs(g[2])<0.035 and abs(g[1])<0.02:
        R.phi_cmd=S.d.qpos[S.jq('tilt')]; S.latch_soft(True); S.latch(True,capture=False); R.run_for(0.6); S.latch_soft(False)
        R.ev('latched: float spring seated handle (residual %.0f mm)'%(S.hook_gap()*1000))
    else: R.ev('LATCH FAILED'); return False
    R.phase='4 Latched: seat+latch switches ON'; R.run_for(1.0)
    R.phase='5 Tipping: mast rocks forward, wheels held by stop bar'
    ok=R.ramp_phi(75,1.5,cond=lambda: S.bin_tilt_rel()>=tilt_target)
    R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.ev('tipped to %.1f deg, mast %.1f deg'%(S.bin_tilt_rel(),S.tilt()))
    R.phase='6 Tow pose reached: actuator self-locks, yaw lock released'; S.yaw_lock(False); R.run_for(1.5)
    return S.bin_tilt_rel()>tilt_target-3
def release(R):
    S=R.s
    R.phase='9 Yaw re-centred and locked; standing bin up'; R.hold(); S.yaw_lock(True); R.run_for(1.5)
    R.ramp_phi(0.0,1.5,cond=lambda: S.bin_tilt_rel()<=0.5)
    R.phi_cmd=S.d.qpos[S.jq('tilt')]; R.run_for(1.0); R.ev('bin upright %.1f deg'%S.bin_tilt_rel())
    R.phase='10 Solenoids pulse: latch released'; S.latch(False); R.run_for(1.0)
    R.phase='11 Mast forward 9 deg: hooks clear handle'; R.ramp_phi(9.0,3.0); R.run_for(0.5)
    R.phase='12 Driving away'; R.set_drive(0.3); R.run_for(4.0); R.hold(); R.run_for(1.0)
def summary(R,t0=0,ph=None):
    L=[l for l in R.log if l['t']>=t0 and (ph is None or l['ph'].startswith(ph))]
    if not L: return {}
    return dict(caster_min=round(min(l['cmin'] for l in L)),drive_min=round(min(l['dmin'] for l in L)),
        stopbar_max=round(max(l['stop'] for l in L)),antitip_max=round(max(l['anti'] for l in L)),arm_max=round(max(l['arm'] for l in L)),
        tug_hit_max=round(max(l['hit'] for l in L)),hook_max=round(max(l['hook'] for l in L)),act_max_N=round(max(l['actN'] for l in L)),
        pitch_max=round(max(abs(l['pitch']) for l in L),1),roll_max=round(max(abs(l['roll']) for l in L),1),
        tilt_min=round(min(l['tilt'] for l in L),1),tilt_max=round(max(l['tilt'] for l in L),1),bin_yaw_max=round(max(abs(l['byaw']) for l in L),1),
        torque_max=round(max(l['tq'] for l in L),1),dist=round(L[-1]['x']-L[0]['x'],2),v_end=round(L[-1]['v'],2),
        caster_p10=round(float(np.percentile([l['cmin'] for l in L],10))),caster_unloaded_frac=round(float(np.mean([l['cmin']<20 for l in L])),2),
        drive_p10=round(float(np.percentile([l['dmin'] for l in L],10))),hook_p99=round(float(np.percentile([l['hook'] for l in L],99))),
        pitch_p90=round(float(np.percentile([abs(l['pitch']) for l in L],90)),1),hgap_max=round(max(l.get('hgap',0) for l in L),1),
        antitip_p90=round(float(np.percentile([l['anti'] for l in L],90))))
