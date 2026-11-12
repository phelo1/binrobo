#!/usr/bin/env python3
"""B2 smoke (calibration, not gate): nominal grab + SD2 set-down per bin/fill; logs pad force vs travel and the knee-toggle actuator
force (F = 2 P tan a), grab/set-down durations. usage: smoke_b2.py [bins] -> b2/res/smoke_b2<TAG>.json"""
import os, sys, json, math, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path[:0]=[H,os.path.join(H,'..','it1'),os.path.join(H,'..','..','g6')]
os.environ.setdefault('CGB_F9','1')
import mujoco, simB2 as B
from bins_g5 import BINS
def act_force(log):
    pk=0.0; at=None
    for q,P,cmd,tg in log:
        e=B.GEO['pad_ret']-q; a=math.acos(min(1.0,0.66606+e/0.12))
        if a>math.radians(3):
            F=2*P*math.tan(a)
            if F>pk: pk,at=F,(round(e*1000,1),round(P),round(math.degrees(a),1))
    return round(pk),at
out=[]
bins=sys.argv[1].split(',') if len(sys.argv)>1 else ['WEB140','ESE140CL','ESE240SL','ESE240CL','ESE240SL250']
for b in bins:
    for full in (True,False):
        p=B.bin_params(b); p['fill']=BINS[b]['fill_full'] if full else 0.0
        S=B.SimB(b,p,tug_pose=B.start_pose(p)); R=B.RunnerB(S); g=B.grab(R); tg=R.t
        o=dict(bin=b,full=full,res=g['result'],why=g.get('why'),padF_loadon=g.get('padF_at_loadon'),tilt=g.get('bin_tilt_abs'),clear=g.get('wheel_clear_mm'),pad_ok=g.get('pad_ok'),t_grab=round(tg,1))
        ext=[x for x in S.padlog if x[3]<0]   # extension moves only
        o['pad_act_peak_N'],o['pad_act_at']=act_force(ext); o['pad_contact_max_ext_N']=max([x[1] for x in ext] or [0])
        if g['result']=='success':
            R.run_for(1.0); o['yaw_deg']=round(math.degrees(S.d.qpos[S.jq('combyaw')]),2)
            S.padlog=[]; t0=R.t; sd=B.set_down(R); o['t_setdown']=round(R.t-t0,1)
            o['sd']='PASS' if sd.get('released') and S.bin_tilt_abs()<8 else ('HOLD' if sd.get('hold') else 'FAIL'); o['tilt_end']=round(S.bin_tilt_abs(),1)
        print(json.dumps(o),flush=True); out.append(o)
json.dump(out,open(os.path.join(H,'res','smoke_b2%s.json'%os.environ.get('SMOKE_TAG','')),'w'),indent=0)
