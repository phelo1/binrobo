#!/usr/bin/env python3
"""Smoke (calibration, not gate): nominal grab + flat carry + SD2 set-down per bin/fill for the comb variant set by CMP_LIP/CMP_COMB.
Prints captured, comb yaw/roll, nib-lip contact y-span (coverage) and force."""
import os, sys, json, math, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path[:0]=[H,os.path.join(H,'..','it1'),os.path.join(H,'..','..','g6')]
os.environ.setdefault('CGB_F9','1')
import mujoco, simB1fw as B
from bins_g5 import BINS
def lipspan(S):
    ys=[];F=0.0;f=np.zeros(6);Rb=S.d.xmat[S.bid['bin']].reshape(3,3)
    ids={S.gid[n] for n in ('nib','tooth')}; lids={S.gid[n] for n in ('ledge','rim')}
    for i in range(S.d.ncon):
        c=S.d.contact[i]
        if (c.geom1 in ids and c.geom2 in lids) or (c.geom2 in ids and c.geom1 in lids):
            mujoco.mj_contactForce(S.m,S.d,i,f); F+=f[0]; ys.append(float((Rb.T@(c.pos-S.d.xpos[S.bid['bin']]))[1]))
    return (round(min(ys)*1000),round(max(ys)*1000)) if ys else None, round(F)
out=[]
bins=sys.argv[1].split(',') if len(sys.argv)>1 else ['WEB140','ESE140CL','ESE240SL','ESE240CL','ESE240SL250']
for b in bins:
    for full in (True,False):
        p=B.bin_params(b); p['fill']=BINS[b]['fill_full'] if full else 0.0
        S=B.SimB(b,p,tug_pose=B.start_pose(p)); R=B.RunnerB(S); g=B.grab(R)
        o=dict(bin=b,full=full,res=g['result'],tilt=g.get('bin_tilt_abs'),clear=g.get('wheel_clear_mm'))
        if g['result']=='success':
            R.run_for(1.0); S.contacts(); o['span_mm'],o['lipF']=lipspan(S)
            if os.environ.get('CMP_COMB')=='fw_pivot': o['yaw_deg']=round(math.degrees(S.d.qpos[S.jq('combyaw')]),2); o['roll_deg']=round(math.degrees(S.d.qpos[S.jq('combroll')]),2)
            sd=B.set_down(R); o['sd']='PASS' if sd.get('released') and S.bin_tilt_abs()<8 else ('HOLD' if sd.get('hold') else 'FAIL'); o['tilt_end']=round(S.bin_tilt_abs(),1)
        print(json.dumps(o),flush=True); out.append(o)
tag=os.environ.get('CMP_LIP','model')+'_'+os.environ.get('CMP_COMB','narrow')
json.dump(out,open(os.path.join(H,'res','smoke_%s.json'%tag),'w'),indent=0)
