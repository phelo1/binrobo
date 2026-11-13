#!/usr/bin/env python3
"""G6 tow-pose static check: grab <BIN> (full 110 kg gross unless 'e'), tip to 48 deg, settle on flat, then dump every contact pair with its
normal force and world position, the hook (bar-cup) force vector and point, tug pitch, and a moment balance about the drive-axle line.
usage: diag_towpose_g6.py <BIN> [e] [tag] -> diag_towpose_<BIN><e><tag>.json"""
import json, os, sys, math, numpy as np, mujoco
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from sim_g5 import Sim, TXm
from scen_g5 import Runner, grab_GH, tip_more
from tow_g5 import nominal, engage_catch
from bins_g5 import BINS
binkey=sys.argv[1]; empty=len(sys.argv)>2 and sys.argv[2]=='e'; tag=sys.argv[3] if len(sys.argv)>3 else ''
B=BINS[binkey]; kw=nominal(binkey); ghp=dict(json.load(open(os.path.join(HERE,'combos_g6.json')))['H3'])
ghp.update(json.loads(os.environ.get('G6_GHP_EXTRA','{}')))   # G6: hook parameter overrides for fix tests
for k_,n_ in (('_claim_and','claim_and'),('_guard','square_guard'),('_reapp','reapp')):
    if k_ in ghp: kw[n_]=ghp.pop(k_)
mf=os.environ.get('G6_MASSFILE','mass_g6_M110h.json')
S=Sim(grabber='GH',gh='B2',ghp=ghp,fill=0.0 if empty else 110.0-B['empty'],mu=0.6,massfile=mf,ballast=99,tug_pose=(TXm+0.60+(kw['wheel_r']-0.10),0.0,0.0),**kw)
R=Runner(S,rec_hz=1); R.recording=False
g=grab_GH(R,tip_to=25.0); tip_more(R,48.0); engage_catch(R); S.yaw_lock(False); R.hold(); R.run_for(3.0)
f=np.zeros(6); pairs=[]
nm=lambda g:(mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,g) or 'g%d'%g)
Rt=S.d.xmat[S.bid['tug']].reshape(3,3); ax=(S.d.xpos[S.bid['wheelL']]+S.d.xpos[S.bid['wheelR']])/2
for i in range(S.d.ncon):
    c=S.d.contact[i]; mujoco.mj_contactForce(S.m,S.d,i,f)
    if f[0]<1: continue
    F=c.frame.reshape(3,3).T@f[:3]
    p=Rt.T@(c.pos-ax)
    pairs.append(dict(a=nm(c.geom1),b=nm(c.geom2),N=round(float(f[0]),1),Fworld=[round(float(v),1) for v in F],x_from_axle_m=round(float(p[0]),3),z_m=round(float(c.pos[2]),3)))
C=S.contacts()
tug_sub=float(S.m.body_subtreemass[S.bid['tug']]); com=S.d.subtree_com[S.bid['tug']]; cx=float((Rt.T@(com-ax))[0])
out=dict(bin=binkey,empty=empty,massfile=mf,grab=g.get('result'),tug_pitch_deg=round(S.rpy()[1],2),mast_deg=round(S.tilt(),1),bin_tilt_deg=round(S.bin_tilt_abs(),1),
         tug_subtree_kg=round(tug_sub,1),tug_subtree_com_x_from_axle_m=round(cx,3),bin_kg=round(S.bin_mass,1),
         drive_N=round(C['driveL']+C['driveR'],1),caster_N=round(C['casterL']+C['casterR'],1),antitip_N=round(C['antitipL']+C['antitipR'],1),
         flare_N=round(C['flareL']+C['flareR'],1),binwheel_N=round(C['binwheelL']+C['binwheelR'],1),stopbar_N=round(C['stopbar'],1),spine_N=round(C['spine'],1),
         hookF_N=round(C['hookF'],1),pairs=sorted(pairs,key=lambda d:-d['N']))
json.dump(out,open(os.path.join(HERE,'diag_towpose_%s%s%s.json'%(binkey,'e' if empty else '',tag)),'w'),indent=1)
print(json.dumps({k:v for k,v in out.items() if k!='pairs'})); [print(p) for p in out['pairs'][:14]]
