#!/usr/bin/env python3
"""G5 bin-range Monte Carlo: GH grabber against explicit data-sheet bin models (bins_g5.BINS). Approach spread as G3 (lateral +/-80 mm,
yaw +/-6 deg, start 0.6 m out, ground mu 0.3-0.8, hook mu 0.2-0.5, lid closed 70 % / ajar 5-25 deg). Fill alternates empty / full
(max permissible). Bar section: published value, or the D25/D30/D42/moulded-38-42 sweep, cycled so each section gets empty and full.
Capture includes ONE re-dock (handover 6.2). False positive = claim (both latch switches + pull test) while the bar is not truly in both cups.
usage: PYTHONPATH=/workspace/work/pylib python3 mc_g5.py <BIN> <n> <seed> [gh=B2] [tag] [ghp_json]  -> ../results_G6_mc_<BIN>_<gh><tag>.json"""
import json, math, os, pickle, sys, time, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); RES=os.path.join(HERE,'..'); sys.path.insert(0,HERE)
from bins_g5 import BINS
def sample(B,i,rng):
    secs=B['sections']; sh,r0,r1=secs[(i//2)%len(secs)]
    r=rng.uniform(r0,r1) if r1>r0 else r0
    full=(i%2==1)
    u=lambda v: v[0]+rng.uniform(-v[1],v[1])
    habs=u(B['bar_abs']); bx=u(B['bar_x']); cb=max(u(B['cb']),0.036+r+0.002)
    kn=B['knuckles']
    if kn=='maybe': kn=[(round(rng.uniform(0.035,0.06),4),0.005)] if rng.random()<0.5 else []
    wr=B['wheel']/2
    lid=('closed',0.0) if rng.random()<0.7 else ('ajar',math.radians(rng.uniform(5,25)))
    return dict(bin=B['name'],bar_r=round(r,4),bar_shape=sh,bar_x=round(bx,4),cb=round(cb,4),bar_habs=round(habs,4),bar_h=round(habs-wr,4),wheel_r=wr,
                handle_half=round(u(B['web']),4),knuckles=kn,wy=round((B['track']-0.05)/2,4),W=B['W'],D=B['D'],empty=B['empty'],
                dy=round(rng.uniform(-0.08,0.08),3),dyaw=round(rng.uniform(-6,6),2),mu=round(rng.uniform(0.3,0.8),2),mu_hook=round(rng.uniform(0.2,0.5),2),
                fill=float(B['fill_full'] if full else 0.0),lid=[lid[0],round(lid[1],3)])
def make_sim(p,gh='B2',ghp=None,**extra):
    from sim_g5 import Sim, TXm
    binm=dict(gap=p['cb']-p['bar_r'],D=p['D'],W=p['W'],empty=p['empty'],wy=p['wy'],knuckles=[tuple(k) for k in p['knuckles']])
    kw=dict(fill=p['fill'],mu=p['mu'],mu_hook=p['mu_hook'],bar_r=p['bar_r'],bar_shape=p['bar_shape'],bar_x=p['bar_x'],bar_h=p['bar_h'],
            wheel_r=p['wheel_r'],handle_half=p['handle_half'],lid=tuple(p['lid']),tug_pose=(TXm+0.60+(p['wheel_r']-0.10),p['dy'],p['dyaw']),ballast=1,binm=binm)
    if os.environ.get('G6_MASSFILE'): kw.update(massfile=os.environ['G6_MASSFILE'],ballast=99)   # G6: operating mass file
    kw.update(extra); ghp=dict(ghp or {})
    if '_fpads' in ghp: kw['fpads']=ghp.pop('_fpads')
    if '_claim_and' in ghp: kw['claim_and']=ghp.pop('_claim_and')
    if '_phi0' in ghp: kw['phi0']=ghp.pop('_phi0')
    if '_guard' in ghp: kw['square_guard']=ghp.pop('_guard')
    if '_lat' in ghp: kw['lat']=ghp.pop('_lat')            # G5c C5: lateral float travel/spring override
    if '_asym' in ghp: kw['asym']=ghp.pop('_asym')          # G5c C3b: pull-test asymmetry check thresholds
    if '_reapp' in ghp: kw['reapp']=ghp.pop('_reapp')       # G5c C2: camera-guided approach + lateral re-approach
    return Sim(grabber='GH',gh=gh,ghp=ghp or None,**kw)
def run_one(args):
    binkey,i,p,rec,gh,ghp=args
    from scen_g5 import Runner, grab_GH
    t=time.time(); R=None
    try:
        S=make_sim(p,gh,ghp)
        R=Runner(S,rec_hz=10); R.recording=rec; R.contact_every=20
        o=grab_GH(R,tip_to=20.0)
        o['first_result']=o['result']
        if (o['result'] in ('safe_miss','bin_pushed') and o.get('docked')) or (o['result']=='no_dock' and (getattr(R,'guard',False) or os.environ.get('NODOCK_RETRY')=='1')):
            R.phase='R Retry: cam open, mast forward, pull away 0.35 m, re-dock'
            S.cam_state=2; R.ramp_phi(S.kw.get('phi0',8.0),3.0); R.set_drive(0.15); R.run_for(2.5); R.hold(); R.run_for(0.5)
            o2=grab_GH(R,tip_to=20.0); o2['first_result']=o['first_result']; o2['retried']=True; o=o2
        C=S.contacts()
        o.update(peak_hook=round(R.peak.get('hook',(0,))[0]),peak_act=round(R.peak.get('act',(0,))[0]),
                 lid_end_deg=round(math.degrees(S.d.qpos[S.jq('lid')]),1),bin_tilt_abs_end=round(S.bin_tilt_abs(),1),events=R.events,
                 bin_dy_end_mm=round(float((np.linalg.inv(S.d.xmat[S.bid['tug']].reshape(3,3))@(S.d.xpos[S.bid['bin']]-S.d.xpos[S.bid['tug']]))[1])*1000,1),
                 antitip_peak=round(max((e['anti'] for e in R.log),default=0),1))
    except Exception as e:
        import traceback; o=dict(result='error',err=repr(e),tb=traceback.format_exc()[-800:])
    o.update(i=i,params=p,cpu=round(time.time()-t,1),bin=binkey)
    if rec and R is not None: pickle.dump(R.rec,open(os.path.join(HERE,'rec',f'mc_{binkey}_{gh}{os.environ.get("MC_TAG","")}_{i}.pkl'),'wb'))
    return o
def stats(res):
    from collections import Counter
    n=len(res); c=Counter(o['result'] for o in res); c1=Counter(o.get('first_result',o['result']) for o in res)
    claims=[o for o in res if o.get('claim')]; fp=sum(1 for o in res if o['result']=='false_positive' or (o.get('claim') and not o.get('captured')))
    by=lambda f: {k:dict(n=sum(1 for o in res if f(o)==k),ok=sum(1 for o in res if f(o)==k and o['result']=='success')) for k in sorted(set(f(o) for o in res))}
    return dict(n=n,counts=dict(c),first_try_counts=dict(c1),capture=c.get('success',0),capture_rate=round(c.get('success',0)/max(n,1),3),
                first_try=c1.get('success',0),first_try_rate=round(c1.get('success',0)/max(n,1),3),false_positives=fp,claims=len(claims),
                by_fill=by(lambda o:'full' if o['params']['fill']>0 else 'empty'),
                by_section=by(lambda o:f"{o['params']['bar_shape']} D{round(o['params']['bar_r']*2000)}"))
if __name__=='__main__':
    binkey=sys.argv[1]; n=int(sys.argv[2]); seed=int(sys.argv[3]); gh=sys.argv[4] if len(sys.argv)>4 else 'B2'; tag=sys.argv[5] if len(sys.argv)>5 else ''
    ghp=json.loads(sys.argv[6]) if len(sys.argv)>6 and sys.argv[6] else None
    os.environ['MC_TAG']=tag; nrec=int(os.environ.get('NREC','2')); IDX=[int(x) for x in os.environ.get('MC_IDX','').split(',') if x.strip()]
    B=BINS[binkey]; rng=np.random.default_rng(seed); P=[sample(B,i,rng) for i in range(max(n,max(IDX)+1 if IDX else 0))]
    out=os.path.join(RES,f'results_G6_mc_{binkey}_{gh}{tag}.json'); res=[]
    if os.path.exists(out):
        try: res=[o for o in json.load(open(out))['runs'] if o.get('result')!='error']
        except Exception: res=[]
    done={o['i'] for o in res}; t=time.time()
    for i,p in enumerate(P):
        if i in done or (IDX and i not in IDX): continue
        o=run_one((binkey,i,p,i<nrec,gh,ghp)); res.append(o)
        print(binkey,len(res),o['i'],o['result'],o.get('first_result'),o.get('cpu'),o.get('err',''),flush=True)
        res.sort(key=lambda o:o['i']); json.dump(dict(bin=binkey,gh=gh,ghp=ghp,seed=seed,stats=stats(res),runs=res),open(out,'w'),indent=0,default=float)
    print(json.dumps(stats(res)),'wall',round(time.time()-t),flush=True)
