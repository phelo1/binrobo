# iter1 diagnostic: set-down trace (contacts, bin pitch sign, wheel/front clearance). usage: CGB_GEO=.. dbg_sd.py BIN full|empty [up12|dn12|flat]
import os,sys,json,math,mujoco,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..')); sys.path.insert(0,os.path.join(H,'..','..','g6'))
import simB_it1 as B
from bins_g5 import BINS
b=sys.argv[1]; full=sys.argv[2]=='full'; case=sys.argv[3] if len(sys.argv)>3 else 'flat'
p=B.bin_params(b); p['fill']=BINS[b]['fill_full'] if full else 0.0
S=B.SimB(b,p,tug_pose=B.start_pose(p)); R=B.RunnerB(S)
nm=lambda g:mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,g); f=np.zeros(6)
def pr(tag):
    d={}
    for i in range(S.d.ncon):
        c=S.d.contact[i]; k=nm(c.geom1)+'-'+nm(c.geom2)
        if 'drive' in k or 'caster' in k: continue
        mujoco.mj_contactForce(S.m,S.d,i,f); d[k]=round(d.get(k,0)+f[0])
    Rb=S.d.xmat[S.bid['bin']].reshape(3,3); Rt=S.d.xmat[S.bid['tug']].reshape(3,3); Rr=Rt.T@Rb
    pitch=math.degrees(math.atan2(-Rr[2,0],Rr[2,2]))
    print(tag,'t %.1f %-12s q %.3f F %.0f pitch_rel %+.1f clear %.3f padq %.4f padext %.4f seated %s'%(R.t,R.phase[:12],S.lift_q(),S.lift_force(),pitch,S.wheel_clear(),S.d.qpos[S.jq('pad')],S.d.qpos[S.jq('padext')],S.seated()),d,flush=True)
g=B.grab(R); print(g); pr('after grab')
gx={'flat':0.0,'up12':0.12,'dn12':-0.12}[case]; psi0=S.rpy()[2]
if gx: R.ramp_grade(gx,0,2.0); R.run_for(1.0)
B.soft_stop(R); R.run_for(0.5); pr('pre-sd')
R.mon=lambda: pr('mon') if R.i%1000==0 else None
sd=B.set_down(R); print(sd); pr('end')
