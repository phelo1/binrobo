# diagnostic only (not a gate run): B release of a gate case with the carry 1 m, contact log during set-down. usage: dbgB3.py BIN case full|empty
import sys,os,mujoco,numpy as np; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import simB_cg as B
from bins_g5 import BINS
b,case,fl=sys.argv[1],sys.argv[2],sys.argv[3]
p=B.bin_params(b); p['fill']=BINS[b]['fill_full'] if fl=='full' else 0.0
S=B.SimB(b,p,tug_pose=B.start_pose(p)); R=B.RunnerB(S)
nm=lambda g:mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,g)
lg=set(S.gid[n] for n in ('nib','tooth','faceplate','padg','keeptip','keeptip2'))
f=np.zeros(6)
def pr(tag):
    d={}
    for i in range(S.d.ncon):
        c=S.d.contact[i]
        if c.geom1 in lg or c.geom2 in lg:
            mujoco.mj_contactForce(S.m,S.d,i,f); k=nm(c.geom1)+'-'+nm(c.geom2); d[k]=round(d.get(k,0)+f[0])
    print(tag,'t %.1f %s q %.3f F %.0f nib %s clear %.3f tilt %.1f seated %s tugx %.3f'%(R.t,R.phase[:14],S.lift_q(),S.lift_force(),S.nib_in_bin().round(3).tolist(),S.wheel_clear(),S.bin_tilt_abs(),S.seated(),S.d.xpos[S.bid['tug']][0]),d,flush=True)
g=B.grab(R); print(g)
psi0=S.rpy()[2]; gx={'flat':0.0,'up12':0.12,'dn12':-0.12}[case]
if gx: R.ramp_grade(gx,0,2.0); R.run_for(1.0)
x0=S.d.xpos[S.bid['tug']].copy(); R.phase='7 carry'; R.ctrl_fn=B.heading_hold(R,0.3,psi0)
R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=1.0,10.0); R.ctrl_fn=None; B.soft_stop(R); R.run_for(0.5)
pr('pre-setdown'); R.mon=lambda: pr('mon') if R.i%1000==0 else None
sd=B.set_down(R); print(sd); pr('end')
