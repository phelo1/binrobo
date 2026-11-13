# Rev F -> F.1 focused parameter study. One (variant, test) per process so runs can go in parallel.
# usage: python study.py <variant> <test>   -> study/<variant>__<test>.json (+ .pkl pose recording if REC)
import json, math, os, pickle, sys, time, numpy as np
from sim_revF import Sim
from scenarios import Runner, grab, release, summary, arc_closed, soft_stop
from model_revF import TX
X0=TX/1000+0.25
VAR={  # name: (Sim kwargs, grab tilt target, description)
 'F0':     (dict(), 48, 'Rev F baseline (4 plates at +0.56 m)'),
 'Bfwd':   (dict(ballast_x=0.70), 48, '4 ballast plates moved forward to +0.70 m'),
 'B2fwd':  (dict(ballast=2, ballast_x=0.70), 48, '2 plates, forward (-8.7 kg)'),
 'Light':  (dict(ballast=0, rear_scale=0.8), 48, 'no ballast + rear frame -20% (~-20 kg)'),
 'D4':     (dict(drive4=True), 48, 'chain 4WD (front wheels chained, fixed)'),
 'Clong':  (dict(caster_x=0.84), 48, 'casters 100 mm further forward'),
 'T40':    (dict(), 40, 'tow tilt 40 deg'),
 'T35':    (dict(), 35, 'tow tilt 35 deg'),
 'Hsoft':  (dict(hook_tc=0.03), 48, 'compliant hook mount (rubber bush)'),
}
def add_variant(name,kw,tilt,desc): VAR[name]=(kw,tilt,desc)
# F.1 candidates (filled in after the single-factor study)
if os.path.exists('f1_config.json'):
    for k,v in json.load(open('f1_config.json')).items(): VAR[k]=(v['kw'],v['tilt'],v['desc'])
def new(kw,fill=96,mu=0.45,terrain='flat',**extra):
    a={k:v for k,v in kw.items() if not k.startswith('_')}; a.update(extra)
    S=Sim(fill=fill,mu=mu,terrain=terrain,tug_x0=X0,**a); return S,Runner(S,rec_hz=12)
def tow(R,v,dist,dv=0.0,Tmax=60):
    S=R.s; x0=S.d.xpos[S.bid['tug']].copy(); R.set_drive(v,dv)
    return R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=dist or abs(S.rpy()[1])>35, Tmax)
def tip_time(R):
    L=[l for l in R.log if l['ph'].startswith('5')]; return round(L[-1]['t']-L[0]['t'],1) if L else None
def run(var,test,record=False):
    kw,tilt,desc=VAR[var]; out=dict(variant=var,test=test,desc=desc)
    if test=='cycle':
        S,R=new(kw,mu=0.45); ok=grab(R,tilt)
        R.phase='7 Towing at 0.5 m/s'; t0=R.t
        if ok: tow(R,0.5,6.0)
        R.phase='8 Arrived: '+('soft stop then brake' if kw.get('_soft') else 'braking'); (soft_stop(R) if kw.get('_soft') else R.hold()); R.run_for(1.5)
        if ok: release(R)
        out.update(grab_ok=ok,tug_kg=round(S.tug_mass,1),bin_kg=round(S.bin_mass,1),tip_s=tip_time(R),
                   act_peak_raw_N=round(R.peak_act),act_peak_raw_at=R.peak_act_at,act_peak_50ms_N=round(R.peak_act_f),act_peak_50ms_at=R.peak_act_f_at)
    elif test.startswith('climb'):
        g=int(test[5:])/100
        S,R=new(kw,mu=0.45); ok=grab(R,tilt)
        R.phase='7a Onto %d%% uphill'%round(g*100); R.ramp_grade(g,0,2.0); R.run_for(1.0)
        R.phase='7 Towing uphill %d%%, wet grass mu 0.45'%round(g*100); t0=R.t; reached=tow(R,0.5,5.0,Tmax=25); tclimb=R.t-t0
        R.phase='8 Stop and hold on hill'; xh=float(S.d.xpos[S.bid['tug']][0]); R.hold(); R.run_for(3.0)
        out.update(grade=g,reached_5m=bool(reached),climb_s=round(tclimb,1),avg_v=round(5.0/tclimb,2) if reached else 0,
                   hold_creep_m=round(float(S.d.xpos[S.bid['tug']][0])-xh,3),tug_kg=round(S.tug_mass,1))
    elif test.startswith('estop'):
        g=int(test[5:])/100
        S,R=new(kw,mu=0.45); ok=grab(R,tilt)
        R.phase='7a Onto %d%% downhill'%round(g*100); R.ramp_grade(-g,0,2.0); R.run_for(0.5)
        R.phase='7 Towing downhill %d%%, wet grass mu 0.45'%round(g*100); tow(R,0.5,2.0,Tmax=15)
        x0=float(S.d.xpos[S.bid['tug']][0]); R.phase='8 E-STOP: spring brakes clamp'; R.hold(); R.run_for(5.0)
        v=S.fwd_speed(); out.update(grade=g,slide_m=round(float(S.d.xpos[S.bid['tug']][0])-x0,3),stops=bool(abs(v)<0.02))
    elif test in ('bump60','bump60slow'):
        vb=0.5 if test=='bump60' else 0.25
        S,R=new(kw,mu=0.6,terrain='bump',bump=(X0+1.2,0.06,0.345)); ok=grab(R,tilt)
        R.phase='7 Towing over a 60 mm step (left wheels) at %.2f m/s'%vb; reached=tow(R,vb,4.0,Tmax=30); R.phase='8 Stop'; R.hold(); R.run_for(1.0)
        out.update(reached_4m=bool(reached))
    elif test=='camber30':
        S,R=new(kw,mu=0.6); ok=grab(R,tilt)
        R.phase='7a Onto 30% side slope'; R.ramp_grade(0,0.3,2.5); R.run_for(3.0)
        y0=float(S.d.xpos[S.bid['tug']][1])
        R.phase='7 Driving across 30% side slope'; tow(R,0.5,3.0,Tmax=12)
        R.phase='8 Stop on side slope'; y1=float(S.d.xpos[S.bid['tug']][1]); x1=float(S.d.xpos[S.bid['tug']][0]); R.hold(); R.run_for(3.0)
        out.update(drift_while_driving_m=round(float(S.d.xpos[S.bid['tug']][1])-y0,3),
                   creep_after_stop_m=round(float(np.hypot(S.d.xpos[S.bid['tug']][0]-x1,S.d.xpos[S.bid['tug']][1]-y1)),3),
                   flipped=any(abs(l['roll'])>30 for l in R.log))
    elif test in('turn_open','turn_closed'):
        S,R=new(kw,mu=0.6); ok=grab(R,tilt); y0=S.rpy()[2]
        if test=='turn_open':
            R.phase='7 2.5 m bend, OPEN-LOOP wheel speeds'; R.set_drive(0.4,0.4*0.69/2.5); R.run_for(10.0); arc=S.rpy()[2]-y0; tt=10.0; okk=arc>=90
        else:
            R.hitch_cap=60
            R.phase='7 2.5 m bend, CLOSED-LOOP heading (P) + 60 deg hitch cap'; okk,arc,tt=arc_closed(R,0.4,2.5,92.0,Kp=1.5,Tmax=25)
        hmax=max(abs(l['ryaw']) for l in R.log if l['ph'].startswith('7'))
        R.phase='7b Spin-in-place request'+(' (hitch cap 60 deg)' if test=='turn_closed' else ' (no cap)')
        y1=S.rpy()[2]; R.set_drive(0.0,0.4); R.run_for(6.0); spin=S.rpy()[2]-y1
        hs=max(abs(l['ryaw']) for l in R.log if l['ph'].startswith('7b'))
        R.phase='8 Stop'; R.hold(); R.run_for(1.0)
        out.update(arc_deg=round(arc,1),arc_target=92.0,arc_time_s=round(tt,1),arc_ok=bool(okk),hitch_max_arc=round(hmax,1),
                   spin_deg=round(spin,1),hitch_max_spin=round(hs,1),cap_events=R.capped)
    out['events']=R.events
    for ph in ('5','7','8'):
        sm=summary(R,ph=ph)
        if sm: out['phase'+ph]=sm
    out['pitch_flip']=any(abs(l['pitch'])>30 for l in R.log)
    return out,R
if __name__=='__main__':
    var,test=sys.argv[1],sys.argv[2]; rec=len(sys.argv)>3 and sys.argv[3]=='rec'
    t=time.time(); os.makedirs('study',exist_ok=True)
    out,R=run(var,test); out['cpu_s']=round(time.time()-t)
    json.dump(out,open(f'study/{var}__{test}.json','w'),indent=1)
    if rec: pickle.dump(R.rec,open(f'study/{var}__{test}.pkl','wb'))
    print(var,test,'done',out['cpu_s'],'s',flush=True)
