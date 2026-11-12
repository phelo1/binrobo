#!/usr/bin/env python3
"""A' CALIBRATION (not a gate run): static flat tow pose, report bin back-face plane in the rear-frame, the foot of the
perpendicular from the drive axle, and the load split. usage: calA.py <BIN> [e] [tag]  (CGA_NOPAD=1 for the bare pose)"""
import os, sys, json, math, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import simA_cg as A; A.set_env()
import mujoco
from sim_g5 import Sim, TXm
from scen_g5 import Runner, grab_GH, tip_more
from tow_g5 import nominal, engage_catch
from bins_g5 import BINS
binkey=sys.argv[1]; empty=len(sys.argv)>2 and sys.argv[2]=='e'; tag=sys.argv[3] if len(sys.argv)>3 else ''
grade=float(os.environ.get('CAL_GRADE','0')); cross=float(os.environ.get('CAL_CROSS','0')); fullkg=float(os.environ.get('CAL_KG','110'))
B=BINS[binkey]; kw=nominal(binkey); ghp=dict(json.load(open(os.path.join(A.G6,'combos_g6.json')))['H3'])
for k_,n_ in (('_claim_and','claim_and'),('_guard','square_guard'),('_reapp','reapp')):
    if k_ in ghp: kw[n_]=ghp.pop(k_)
S=Sim(grabber='GH',gh='B2',ghp=ghp,fill=0.0 if empty else fullkg-B['empty'],mu=0.6,massfile=A.MASSF,ballast=99,tug_pose=(TXm+0.60+(kw['wheel_r']-0.10),0.0,0.0),**kw)
R=Runner(S,rec_hz=1); R.recording=False
g=grab_GH(R,tip_to=25.0)
if getattr(S,'ratchet_on',False):
    S.ratchet_on=False; j=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'float'); S.m.jnt_range[j][0]=-S.GHV['float_down']
tip_more(R,float(os.environ.get("CAL_TIP","48"))); engage_catch(R); S.yaw_lock(False)
if S.GHV.get("ratchet",False) and os.environ.get("CGA_FLOATFREE")!="1": S.ratchet_on=True
if os.environ.get('CGA_SBRET'):
    for n in ('stopbar','stopbar2'):
        gi=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_GEOM,n)
        if gi>=0: S.m.geom_pos[gi][0]+=float(os.environ['CGA_SBRET'])
if os.environ.get('CGA_FLOATLOCK')=='1':   # A' tow pose: ratchet lifted, float settles on its bottom stop, then float locked there
    S.ratchet_on=False; jf=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'float'); lo=-S.GHV['float_down']; S.m.jnt_range[jf]=[lo,S.GHV['float_up']]
    S.float_pull=200.0; R.run_for(1.5); S.float_pull=0.0; S.m.jnt_range[jf]=[lo,lo+0.0005]
R.hold(); R.run_for(2.0)
if grade or cross: R.ramp_grade(grade,cross,2.0)
R.run_for(3.0)
C=S.contacts(); pc,pf=A.pad_state(S)
# bin back face (hull vertices xbb..xb) in rear-frame coords
Rr=S.d.xmat[S.bid['rear']].reshape(3,3); pr=S.d.xpos[S.bid['rear']]; Rb=S.d.xmat[S.bid['bin']].reshape(3,3); pb=S.d.xpos[S.bid['bin']]
mid=S.m.geom_dataid[S.gid['binhull']]; va=S.m.mesh_vertadr[mid]; nv=S.m.mesh_vertnum[mid]
V=S.m.mesh_vert[va:va+nv]; gp=S.m.geom_pos[S.gid['binhull']]; gq=S.m.geom_quat[S.gid['binhull']]
Rg=np.zeros(9); mujoco.mju_quat2Mat(Rg,gq); Rg=Rg.reshape(3,3)
Vb=[gp+Rg@v for v in V]                               # hull vertices in the BIN frame
up=[v for v in Vb if v[2]>0.2]; dn=[v for v in Vb if v[2]<0.2]
hi=sorted(up,key=lambda v:v[0])[-2:]; lo=sorted(dn,key=lambda v:v[0])[-2:]   # back face = most +x (toward tug) top pair + bottom pair
toR=lambda v: Rr.T@(pb+Rb@v-pr)
p0=toR((lo[0]+lo[1])/2); p1=toR((hi[0]+hi[1])/2); t=(p1-p0)/np.linalg.norm(p1-p0); n=np.array([-t[2],0,t[0]])
if n[2]<0: n=-n                                      # n = face normal pointing up/out of the face (toward the tug side, above the face)
axle=Rr.T@(((S.d.xpos[S.bid['wheelL']]+S.d.xpos[S.bid['wheelR']])/2)-pr)
s=float((axle-p0)@t); foot=p0+t*s; L=float(np.linalg.norm(p1-p0))
tug_sub=float(S.m.body_subtreemass[S.bid['tug']])
out=dict(bin=binkey,empty=empty,grade=grade,cross=cross,grab=g.get('result'),tug_pitch=round(S.rpy()[1],2),roll=round(S.rpy()[0],2),bin_tilt=round(S.bin_tilt_abs(),1),
         drive_N=round(C['driveL']+C['driveR'],1),driveL=round(C['driveL'],1),driveR=round(C['driveR'],1),caster_N=round(C['casterL']+C['casterR'],1),
         binwheel_ground_N=round(A.binwheel_ground(S),1),binwheel_all_N=round(C['binwheelL']+C['binwheelR'],1),stopbar_N=round(C['stopbar'],1),
         hook_N=round(C["hookF"],1),float_mm=round(1000*float(S.d.qpos[S.jq("float")]),1),flare_N=round(C['flareL']+C['flareR'],1),antitip_N=round(C['antitipL']+C['antitipR'],1),pad_comp_mm=round(pc*1000,1),pad_N=round(pf,1),
         face_lo=[round(float(v),4) for v in p0],face_hi=[round(float(v),4) for v in p1],face_len=round(L,3),t=[round(float(v),4) for v in t],n_tug_to_bin=[round(float(v),4) for v in -n] ,
         axle_rear=[round(float(v),4) for v in axle],foot_s=round(s,3),foot=[round(float(v),4) for v in foot],tug_kg=round(S.tug_mass,1),bin_kg=round(S.bin_mass,1),captured=S.captured())
json.dump(out,open(os.path.join(HERE,'res','calA_%s%s%s.json'%(binkey,'e' if empty else '',tag)),'w'),indent=1)
print(json.dumps(out))
