# Rev F.1 bin-recovery manoeuvres (empty bin left the wrong way round by the crew).
#   R1: bin BACKWARDS (handle facing a hedge 0.80 m behind it -> no room for the tug to get round) -> orbit-nudge 180 deg, dock, grab, tow.
#   R2: bin SIDEWAYS, handle side blocked by a parked car -> orbit-nudge 90 deg, dock, grab, tow.
# Perception is emulated: true bin pose + noise (lidar outline fit sigma 15 mm / 1.5 deg; front/back AprilTag resolves the 180 deg ambiguity).
# usage: python recovery.py R1|R2|R3   -> study/recovery_<name>.json + .pkl
import json, math, pickle, sys, time, numpy as np
from sim_revF import Sim
from scenarios import Runner, grab, summary, soft_stop
from model_revF import TX
TXm=TX/1000; W=0.69; BUMP=0.78; import os; RNG=np.random.default_rng(int(os.environ.get('REC_SEED','7')))
def wrap(a): return (a+math.pi)%(2*math.pi)-math.pi
def R90(v): return np.array([-v[1],v[0]])
def tug_pose(S):
    p=S.d.xpos[S.bid['tug']][:2].copy(); return p, math.radians(S.rpy()[2])
def bin_true(S):
    R=S.d.xmat[S.bid['bin']].reshape(3,3); return S.d.xpos[S.bid['bin']][:2].copy(), math.atan2(R[1,0],R[0,0]), math.degrees(math.acos(max(-1,min(1,R[2,2]))))
class Percept:
    """emulated lidar outline fit + tag ID: low-pass filtered noisy bin axle position and yaw"""
    def __init__(s,S): s.S=S; s.A=None; s.b=None
    def update(s):
        A,b,tilt=bin_true(s.S); An=A+RNG.normal(0,0.015,2); bn=b+math.radians(RNG.normal(0,1.5))
        if s.A is None: s.A,s.b=An,bn
        else: s.A=s.A*0.8+An*0.2; s.b=s.b+0.2*wrap(bn-s.b)
        return s.A,s.b,tilt
def goto(R,P,target,psi_f=None,vmax=0.25,Tmax=40,tol=0.04):
    """diff-drive go-to-pose: spin to face the point, drive with heading correction, spin to final heading"""
    S=R.s; st={'m':'turn1'}; target=np.array(target,float)
    def ctl():
        p,psi=tug_pose(S); d=target-p; dist=float(np.linalg.norm(d)); brg=math.atan2(d[1],d[0])
        if st['m']=='turn1':
            e=wrap(brg-psi); R.w=0; dv=1.2*e*W; dv=math.copysign(max(0.07,min(0.3,abs(dv))),dv); R.wd=dv/0.165; R.brake=False
            if abs(e)<math.radians(5) or dist<tol: st['m']='drive'
        elif st['m']=='drive':
            e=wrap(brg-psi); v=max(0.06,min(vmax,0.6*dist))*max(0.0,math.cos(e))
            R.w=v/0.165; R.wd=max(-0.25,min(0.25,1.5*e*W))/0.165; R.brake=False
            if dist<tol or (dist<0.12 and abs(e)>math.radians(60)): st['m']='turn2' if psi_f is not None else 'done'
        elif st['m']=='turn2':
            e=wrap(psi_f-psi); R.w=0; dv=1.2*e*W; dv=math.copysign(max(0.07,min(0.3,abs(dv))),dv); R.wd=dv/0.165; R.brake=False
            if abs(e)<math.radians(3): st['m']='done'
    R.ctrl_fn=ctl; ok=R.until(lambda: st['m']=='done',Tmax); R.ctrl_fn=None; soft_stop(R,2.0); return ok
def waypoints_around(c,p0,p1,r,obst_ok):
    """points on a circle of radius r round c from p0's bearing to p1's bearing, going whichever way keeps every point obstacle-free"""
    a0=math.atan2(*(p0-c)[::-1]); a1=math.atan2(*(p1-c)[::-1]); best=None
    for sgn in (1,-1):
        span=(a1-a0)%(2*math.pi) if sgn>0 else (a0-a1)%(2*math.pi)
        n=max(1,int(span/math.radians(40))); pts=[c+r*np.array([math.cos(a0+sgn*span*k/n),math.sin(a0+sgn*span*k/n)]) for k in range(1,n)]
        if all(obst_ok(q) for q in pts) and (best is None or span<best[0]): best=(span,pts)
    return best[1] if best else None
def orbit_nudge(R,P,rotate_deg,sgn=1,mode='wheels',v=0.10,Tmax=70):
    """Nudge the empty bin round with the front bumper while the tug follows the arc, heading kept tangent.
       mode 'wheels': push the FEET end, bin swings round its wheel axle (it also rolls towards its handle ~0.6 m per 90 deg).
       mode 'feet'  : push the WHEEL end sideways, bin pivots on its front feet (wheels skid sideways, no rolling)."""
    S=R.s; A,b,_=P.update(); st=dict(prev=b,acc=0.0)
    pv,sb=(0.0,0.88) if mode=='wheels' else (0.59,-0.12)      # pivot and bumper-centre stations along the bin axis (m from axle towards feet)
    sg=1.0 if sb>pv else -1.0
    def frame(A,b):
        f=-np.array([math.cos(b),math.sin(b)]); t=sgn*sg*R90(f); return f,t
    f,t=frame(A,b); Bref=A+sb*f-0.25*t; pre=Bref-(BUMP+0.30)*t
    R.phase='R3 Moving to the push pose beside the bin'+("'s front corner" if mode=='wheels' else "'s wheel end")
    if mode=='feet':   # the wheel end is near the obstacle: approach along the push line, turning only where the nose has room
        goto(R,P,pre-0.7*t+0.35*f,None,vmax=0.25)
    if not goto(R,P,pre,math.atan2(t[1],t[0]),vmax=0.2): R.ev('push pose not reached'); return False,0.0
    R.phase=f'R4 Nudge: bumper swings the bin {rotate_deg:.0f} deg '+('round its wheels' if mode=='wheels' else 'on its front feet')
    A0=A.copy(); lev=abs(0.45 if mode=='wheels' else 0.59)
    def ctl():
        A,b,_=P.update(); st['acc']+=wrap(b-st['prev'])*sgn; st['prev']=b
        f,t=frame(A,b); p,psi=tug_pose(S); h=np.array([math.cos(psi),math.sin(psi)])
        B=p+BUMP*h; eps=wrap(psi-math.atan2(t[1],t[0])); nl=R90(t); el=float((B-(A+sb*f))@nl)
        om=-2.0*(eps+2.5*el)+sgn*v/max(lev,0.3)
        R.w=v/0.165; R.wd=max(-0.3,min(0.3,om*W))/0.165; R.brake=False
    R.ctrl_fn=ctl
    ok=R.until(lambda: st['acc']>=math.radians(rotate_deg-4) or float(np.linalg.norm(P.A-A0))>1.8,Tmax); R.ctrl_fn=None
    rot=math.degrees(st['acc']); R.ev('nudge (%s) rotated bin %.0f deg, axle moved %.2f m'%(mode,rot,np.linalg.norm(P.A-A0)))
    R.phase='R5 Backing off the bin'; R.set_drive(-0.15); R.run_for(2.0); soft_stop(R)
    return rot>=rotate_deg-6, rot
def dock(R,P,obst_ok,Tmax=60):
    S=R.s; A,b,_=P.update(); hd=np.array([math.cos(b),math.sin(b)]); fdir=-hd; c=A+0.33*fdir
    pre=A+(TXm+0.60)*hd; p,_=tug_pose(S)
    R.phase='R6 Driving round to the handle side'
    wps=waypoints_around(c,p,pre,1.55,obst_ok) or []
    for q in wps: goto(R,P,q,None,vmax=0.25)
    for attempt in range(3):
        goto(R,P,pre,math.atan2(hd[1],hd[0]),vmax=0.2)
        p,psi=tug_pose(S); el=float((p-A)@R90(hd)); eh=math.degrees(wrap(psi-b))
        if abs(el)<0.06 and abs(eh)<5: break
        R.ev('pre-dock pose off by %.0f mm / %.1f deg: re-try %d'%(el*1000,eh,attempt+1))
        R.set_drive(0.15); R.run_for(2.0); soft_stop(R)
    else:
        R.ev('could not reach the pre-dock pose'); return None,None
    R.phase='R7 Reversing onto the bin: lidar/tag line-following'
    def ctl():
        A,b,_=P.update(); hd=np.array([math.cos(b),math.sin(b)]); n=R90(hd); p,psi=tug_pose(S)
        e=float((p-A)@n); eps=wrap(psi-b); ed=max(-0.26,min(0.26,4.0*e)); om=-3.0*(eps-ed)
        dist=float((p-A)@hd); v=0.10 if dist>TXm+0.15 else 0.06
        R.w=-v/0.165; R.wd=max(-0.2,min(0.2,om*W))/0.165; R.brake=False
    R.ctrl_fn=ctl; R.until(lambda: float((tug_pose(S)[0]-P.A)@np.array([math.cos(P.b),math.sin(P.b)]))<=TXm+0.04 or S.normals()['stopbar']>40,Tmax); R.ctrl_fn=None
    p,psi=tug_pose(S); A,b,_=P.update(); e=float((p-A)@R90(np.array([math.cos(b),math.sin(b)])))
    R.ev('pre-contact alignment: lateral %.0f mm, heading %.1f deg'%(e*1000,math.degrees(wrap(psi-b)))); return e,math.degrees(wrap(psi-b))
SCN={
 'R1':dict(desc='Empty bin BACKWARDS, hedge 1.5 m behind its handle (tug needs ~2.1 m to dock from that side): swing it 180 deg round its wheels by nudging, dock, grab',
           bin=(0.0,0.0,180.0), tug=(2.6,-1.0,150.0), walls=[(-1.81,0.0,0.6,0.25,3.0,0.6)], rot=180, sgn=1, mode='wheels',
           obst=lambda q: q[0]>-1.56+0.65),
 'R1b':dict(desc='Backwards bin, hedge 0.80 m behind: alternative tried - pivot on its feet by pushing the wheel end',
           bin=(0.0,0.0,180.0), tug=(2.6,-1.0,150.0), walls=[(-1.11,0.0,0.6,0.25,3.0,0.6)], rot=180, sgn=-1, mode='feet',
           obst=lambda q: q[0]>-0.86+0.65),
 'R1a':dict(desc='Backwards bin, hedge only 0.80 m behind: swing round its wheels - bin rolls towards its handle and wedges (failure mode)',
           bin=(0.0,0.0,180.0), tug=(2.6,-1.0,150.0), walls=[(-1.11,0.0,0.6,0.25,3.0,0.6)], rot=180, sgn=1, mode='wheels',
           obst=lambda q: q[0]>-0.86+0.65),
 'R2':dict(desc='Empty bin SIDEWAYS, handle side blocked by a wall/gatepost: orbit-nudge 90 deg, dock, grab',
           bin=(0.0,0.0,-90.0), tug=(2.6,1.0,200.0), walls=[(-0.55,-1.50,0.6,0.55,0.25,0.6)], rot=90, sgn=1, mode='wheels',
           obst=lambda q: q[1]>-1.25+0.60 or q[0]>0.65),
 'R3':dict(desc='Empty bin BACKWARDS pushed hard against the hedge (0.15 m): try the same 180 deg nudge (expected to need a pull-out first)',
           bin=(0.0,0.0,180.0), tug=(2.6,-1.0,150.0), walls=[(-0.46,0.0,0.6,0.25,3.0,0.6)], rot=180, sgn=1,
           obst=lambda q: q[0]>-0.21+0.65),
}
def run(name):
    c=SCN[name]
    F1={k:v for k,v in json.load(open('f1_config.json'))['F1']['kw'].items() if not k.startswith('_')}   # Rev F.1 geometry
    S=Sim(fill=0,mu=float(os.environ.get('REC_MU','0.6')),terrain='flat',**F1,tug_pose=c['tug'],bin_pose=c['bin'],walls=c['walls'],bumper_hits_bin=True,multiccd=True,bin_solref=float(__import__('os').environ.get('BIN_SOLREF','0.02')))
    R=Runner(S,rec_hz=12); P=Percept(S); out=dict(name=name,desc=c['desc'],bin_kg=round(S.bin_mass,1)); t0=time.time()
    def hud():
        A,b,tilt=bin_true(S); p,psi=tug_pose(S)
        return f"t = {R.t:5.1f} s\nbin heading {math.degrees(b):6.0f}°  (target 0°)\nbin upright: {'yes' if tilt<20 else 'NO'}\nbumper push {R.log[-1]['bump'] if R.log else 0:4.0f} N\nhook load {S.hook().sum():4.0f} N   bin tilt {S.bin_tilt_rel():4.1f}°"
    R.hud_fn=hud
    R.phase='R1 Arrived: lidar scan + rear camera'; R.hold(); R.run_for(1.5)
    A,b,tilt=P.update()
    face='handle side AWAY / blocked' if abs(wrap(b))>math.radians(30) else 'handle side toward lane'
    R.ev(f'perceived bin at ({A[0]:.2f},{A[1]:.2f}) heading {math.degrees(b):.0f} deg, upright={tilt<20} -> {face}')
    R.phase='R2 Classified: '+('bin upright, handle side blocked -> re-orient by nudging' if tilt<20 else 'bin TIPPED -> alert')
    R.run_for(1.0)
    ok_rot,rot=orbit_nudge(R,P,c['rot'],c['sgn'],c.get('mode','wheels'))
    A,b,_=bin_true(S); out.update(rotated_deg=round(rot,1),bin_heading_after=round(math.degrees(b),1),t_nudge_done=round(R.t,1))
    if abs(math.degrees(wrap(b)))>25:
        out.update(success=False,fail='bin not re-oriented within 25 deg of the lane'); R.ev('FAILED: '+out['fail'])
    else:
        ok=False; out['dock_attempts']=0
        for attempt in range(2):           # firmware: a failed latch backs off and re-docks once before giving up
            out['dock_attempts']+=1
            e,eh=dock(R,P,c['obst'])
            if e is None: out['fail']='pre-dock pose not reachable'; break
            out.update(dock_lat_mm=round(e*1000),dock_head_deg=round(eh,1))
            ok=grab(R,48.0)
            if ok: break
            R.phase='R7b Latch missed: hooks up, pull forward 1 m, re-dock'; R.ramp_phi(8.0,3.0); R.set_drive(0.15); R.run_for(6.0); soft_stop(R)
        out['grab_ok']=bool(ok)
        if ok:
            R.phase='R8 Towing the recovered bin away'; R.set_drive(0.4); R.run_for(4.0); soft_stop(R); R.run_for(1.0)
        out['success']=bool(ok)
    out['sim_time_s']=round(R.t,1); out['events']=R.events; out['cpu_s']=round(time.time()-t0)
    L=R.log; out['bumper_peak_N']=round(max(l['bump'] for l in L)); out['hook_peak_N']=round(max(l['hook'] for l in L))
    out['bin_tipped']=bool(max(bin_true(S)[2] for _ in [0])>60 and not out.get('grab_ok'))
    return out,R
if __name__=='__main__':
    name=sys.argv[1]; out,R=run(name); tag=sys.argv[2] if len(sys.argv)>2 else name
    out['mu']=float(os.environ.get('REC_MU','0.6')); out['seed']=int(os.environ.get('REC_SEED','7'))
    json.dump(out,open(f'study/recovery_{tag}.json','w'),indent=1)
    if tag==name: pickle.dump(R.rec,open(f'study/recovery_{name}.pkl','wb'))
    print(json.dumps(out)[:1500])
