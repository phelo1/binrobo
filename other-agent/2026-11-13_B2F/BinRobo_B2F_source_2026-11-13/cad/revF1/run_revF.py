# Rev F test suite. Saves results JSON + pose recordings (pickle) for the video renderer.
import json, math, pickle, sys, time, numpy as np
from sim_revF import Sim
from scenarios import Runner, grab, release, summary
from model_revF import TX
X0=TX/1000+0.25
OUT={}; REC={}
def new(fill=96,mu=0.45,ballast=4,terrain='flat',**kw):
    S=Sim(fill=fill,mu=mu,ballast=ballast,terrain=terrain,tug_x0=X0,**kw); return S,Runner(S,rec_hz=12)
def tow(R,v,dist,dv=0.0,Tmax=60):
    S=R.s; x0=S.d.xpos[S.bid['tug']].copy(); R.set_drive(v,dv)
    return R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=dist or abs(S.rpy()[1])>35, Tmax)
def save(name,R,extra=None,record=True):
    res=dict(events=R.events,**(extra or {}))
    for ph in ('5','7','8'):
        sm=summary(R,ph=ph)
        if sm: res['phase'+ph]=sm
    res['flipped']=any(abs(l['pitch'])>30 for l in R.log)
    OUT[name]=res
    if record: REC[name]=R.rec
    print(name,json.dumps(res)[:600],flush=True)
t0=time.time()
which=sys.argv[1] if len(sys.argv)>1 else 'all'
# 1. full cycle on flat, wet grass, full bin
if which in('all','cycle'):
    for fill,name in ((96,'cycle_full'),(30,'cycle_30kg'),(0,'cycle_empty')):
        S,R=new(fill=fill)
        ok=grab(R)
        R.phase='7 Towing at 0.5 m/s'
        if ok: tow(R,0.5,6.0)
        R.phase='8 Arrived: braking'; R.hold(); R.run_for(1.5)
        if ok: release(R)
        save(name,R,dict(grab_ok=ok,tug_kg=round(S.tug_mass,1),bin_kg=round(S.bin_mass,1),act_peak_N=round(R.peak_act)),record=(fill in (96,)))
# 2. uphill climbs (grab on flat, then onto grade)
if which in('all','climb'):
    for g in (0.10,0.15,0.20):
        for mu in (0.45,0.8):
            S,R=new(mu=mu); ok=grab(R)
            R.phase='7a Onto %d%% uphill'%round(g*100); R.ramp_grade(g,0,2.0); R.run_for(1.0)
            R.phase='7 Towing uphill %d%%, mu %.2f'%(round(g*100),mu); tow(R,0.5,5.0,Tmax=25)
            R.phase='8 Stop on hill'; R.hold(); R.run_for(3.0)
            save(f'climb_{round(g*100)}_{mu}',R,dict(grade=g,mu=mu),record=(mu==0.45 and g in(0.15,0.20)))
# 3. downhill emergency stop (spring brakes)
if which in('all','estop'):
    for g in (0.10,0.15,0.20):
        for mu in (0.45,0.8):
            S,R=new(mu=mu); ok=grab(R)
            R.phase='7a Onto %d%% downhill'%round(g*100); R.ramp_grade(-g,0,2.0); R.run_for(0.5)
            R.phase='7 Towing downhill %d%%, mu %.2f'%(round(g*100),mu); tow(R,0.5,2.0,Tmax=15)
            x0=float(S.d.xpos[S.bid['tug']][0]); R.phase='8 E-STOP: spring brakes clamp'; R.hold(); R.run_for(5.0)
            slide=float(S.d.xpos[S.bid['tug']][0])-x0; v=S.fwd_speed()
            save(f'estop_{round(g*100)}_{mu}',R,dict(grade=g,mu=mu,slide_m=round(slide,3),v_after5s=round(v,3),stops=abs(v)<0.02),record=(mu==0.45 and g==0.15))
# 4. pothole and bump under left wheels
if which in('all','terrain'):
    for terr,kw,name in (('hole',dict(hole_x=X0+1.0),'pothole_100mm'),('bump',dict(bump=(X0+1.2,0.03,0.345)),'bump_60mm')):
        S,R=new(mu=0.6,terrain=terr,**kw); ok=grab(R)
        R.phase='7 Towing over '+('100 mm pothole' if terr=='hole' else '60 mm bump')+' (left wheels)'
        reached=tow(R,0.5,4.0,Tmax=20); R.phase='8 Stop'; R.hold(); R.run_for(1.0)
        save(name,R,dict(reached_4m=bool(reached)),record=True)
# 5. side slope (camber): park braked, then drive across
if which in('all','camber'):
    for g in (0.20,0.30,0.40):
        S,R=new(mu=0.6); ok=grab(R)
        R.phase='7a Onto %d%% side slope'%round(g*100); R.ramp_grade(0,g,2.5); R.run_for(3.0)
        R.phase='7 Driving across %d%% side slope'%round(g*100); tow(R,0.5,3.0,Tmax=12)
        R.phase='8 Stop'; R.hold(); R.run_for(1.0)
        save(f'camber_{round(g*100)}',R,dict(grade=g),record=(g==0.30))
# 6. turning: 2.5 m radius arc, then spin in place
if which in('all','turn'):
    for mu in (0.6,):
        S,R=new(mu=mu); ok=grab(R)
        y0=S.rpy()[2]
        R.phase='7 Turning: 2.5 m radius arc'; R.set_drive(0.4,0.4*0.69/2.5); R.run_for(10.0)
        yaw_arc=S.rpy()[2]-y0
        R.phase='7b Spin in place'; y1=S.rpy()[2]; R.set_drive(0.0,0.4); R.run_for(6.0)
        yaw_spin=S.rpy()[2]-y1
        R.phase='8 Stop'; R.hold(); R.run_for(1.0)
        save('turn',R,dict(yaw_arc_deg=round(yaw_arc,1),yaw_spin_deg=round(yaw_spin,1),expected_arc_deg=round(math.degrees(4.0/2.5),1),expected_spin_deg=round(math.degrees(6*0.4/0.69),1)),record=True)
json.dump(OUT,open(f'results_{which}.json','w'),indent=1)
pickle.dump(REC,open(f'rec_{which}.pkl','wb'))
print('done',round(time.time()-t0),'s')
