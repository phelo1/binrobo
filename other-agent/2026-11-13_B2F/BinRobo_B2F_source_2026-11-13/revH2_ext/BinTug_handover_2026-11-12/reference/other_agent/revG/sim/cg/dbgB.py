import sys,os,json,time,mujoco,numpy as np; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import simB_cg as B
b=sys.argv[1]; fill=float(sys.argv[2])
p=B.bin_params(b); p['fill']=fill
S=B.SimB(b,p,mu=0.6,tug_pose=B.start_pose(p)); R=B.RunnerB(S)
ok=B.approach(R,retry=False); print('docked',ok,R.events)
nm=lambda g:mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,g)
lg=set(S.gid[n] for n in ('nib','tooth','faceplate','padg','keeptip','keeptip2'))
f=np.zeros(6)
for k in range(14):
    R.ramp_lift(min(0.02*(k+1),0.25),0.03)
    pr={}
    for i in range(S.d.ncon):
        c=S.d.contact[i]
        if c.geom1 in lg or c.geom2 in lg:
            mujoco.mj_contactForce(S.m,S.d,i,f); key=nm(c.geom1)+'-'+nm(c.geom2); pr[key]=round(pr.get(key,0)+f[0])
    print('q %.3f F %.0f nib_bin %s clear %.3f tilt %.1f'%(S.lift_q(),S.lift_force(),S.nib_in_bin().round(3).tolist(),S.wheel_clear(),S.bin_tilt_abs()),pr)
print('zL bin',p['zL_abs']-p['wheel_r'],'xbt',p['bar_x']-p['cb'],'bar_h',p['bar_h'])
