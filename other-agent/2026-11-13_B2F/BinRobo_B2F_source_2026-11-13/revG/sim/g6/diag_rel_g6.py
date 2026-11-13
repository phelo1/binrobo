#!/usr/bin/env python3
"""G6 release diagnostic: run tow_g5.run(<BIN>,<test>) with the GH-B6 hook at G6_MASSFILE and log, every 0.05 s from the tow stop onward:
mast angle, bin tilt (rel tug / abs gravity), tug pitch, bin wheel + stop-bar normal forces, bar centre in the cradle frame, pawl angles,
float position, bar-hook and bar-pawl contact forces, cam state.  usage: diag_rel_g6.py <BIN> <test> [tag]  -> diag_rel_<BIN>_<test><tag>.json"""
import json, os, sys, math, numpy as np, mujoco
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
os.environ.setdefault('G6_MASSFILE',os.path.join(HERE,'mass_g6_M110h.json'))
import scen_g5, tow_g5
binkey,test=sys.argv[1],sys.argv[2]; tag=sys.argv[3] if len(sys.argv)>3 else ''
ghp=json.load(open(os.path.join(HERE,'combos_g6.json')))['H3']
LOG=[]; ON=[False]; PAIRS=[]
def pawl_bar_F(S):
    f=np.zeros(6); bar=S.gid['bar']; out=0.0; hook=0.0
    for i in range(S.d.ncon):
        c=S.d.contact[i]
        if bar not in (c.geom1,c.geom2): continue
        o=c.geom2 if c.geom1==bar else c.geom1; n=mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,o) or ''
        mujoco.mj_contactForce(S.m,S.d,i,f)
        if n.startswith('pw'): out+=f[0]
        elif n.startswith('hk'): hook+=f[0]
    return out,hook
orig_rel=scen_g5.release_GH
def rel(R,*a,**k):
    S=R.s; prev=R.step
    def st():
        prev()
        if R.i%6000==0:
            f=np.zeros(6); pairs={}
            for i in range(S.d.ncon):
                c=S.d.contact[i]; mujoco.mj_contactForce(S.m,S.d,i,f)
                if f[0]<5: continue
                nm=lambda g:(mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,g) or 'g%d'%g)+'@'+(mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_BODY,S.m.geom_bodyid[g]) or '')
                k=nm(c.geom1)+' | '+nm(c.geom2); pairs[k]=round(pairs.get(k,0)+f[0],1)
            PAIRS.append((round(R.t,2),R.phase[:30],round(S.rpy()[1],2),pairs))
        if R.i%100==0:
            C=S.contacts(); pf,hf=pawl_bar_F(S); p=S.bar_in_hook()
            LOG.append(dict(t=round(R.t,2),ph=R.phase[:40],mast=round(S.tilt(),2),btr=round(S.bin_tilt_rel(),2),bta=round(S.bin_tilt_abs(),2),
                pitch=round(S.rpy()[1],2),bw=round(C['binwheelL']+C['binwheelR'],1),stop=round(C.get('stopL',0)+C.get('stopR',0),1),hull=round(C['binhull'],1),
                bar=[round(v,1) for v in p],pawl=[round(v,1) for v in S.pawl_deg()],fl=round(float(S.d.qpos[S.jq('float')])*1000,1),
                pawlF=round(pf,1),hookF=round(hf,1),cam=S.cam_state,camtq=[round(float(S.d.actuator_force[S.aid(n)]),3) for n in ('camL','camR')],
                pawlq_frc=[round(float(S.d.qfrc_constraint[S.jv(n)]),3) for n in ('pawlL','pawlR')],
                binxyz=[round(float(v),3) for v in S.d.xpos[S.bid['bin']]],bv=round(float(np.linalg.norm(S.d.qvel[S.jv('binfree'):S.jv('binfree')+3])),3),
                actN=round(R.act_f),bwz=[round(float(S.d.xpos[S.bid[n]][2])*1000,1) for n in ('bwL','bwR')],anti=round(C['antitipL']+C['antitipR'],1),cmin=round(min(C['casterL'],C['casterR']),1),ryaw=round(S.yaw_rel(),2)))
    R.step=st
    o=orig_rel(R,*a,**k); R.step=prev; return o
scen_g5.release_GH=rel; tow_g5.release_GH=rel
o,R=tow_g5.run(binkey,test,'B2',dict(ghp))
RL=[{k:(round(v,3) if isinstance(v,float) else v) for k,v in e.items() if k in('t','ph','cmin','dmin','anti','pitch','roll','mast','tilt','bw','hook','btilt','actN','v','ryaw','byaw','x','y_')} for e in R.log[::10]]
json.dump(dict(out={k:v for k,v in o.items() if k!='events'},events=R.events,log=LOG,rlog=RL,pairs=PAIRS),open(os.path.join(HERE,'diag_rel_%s_%s%s.json'%(binkey,test,tag)),'w'),indent=0,default=str)
print(json.dumps({k:v for k,v in o.items() if k not in('events','ghp')},default=str)); print(R.events[-8:])
