import sys,os,json,mujoco,numpy as np; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import simB_cg as B
b=sys.argv[1]; fill=float(sys.argv[2])
p=B.bin_params(b); p['fill']=fill
S=B.SimB(b,p,mu=0.6,tug_pose=B.start_pose(p)); R=B.RunnerB(S)
nm=lambda g:mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,g)
lg=set(S.gid[n] for n in ('nib','tooth','faceplate','padg','keeptip','keeptip2'))
f=np.zeros(6)
def pr(tag):
    d={}
    for i in range(S.d.ncon):
        c=S.d.contact[i]
        if c.geom1 in lg or c.geom2 in lg:
            mujoco.mj_contactForce(S.m,S.d,i,f); k=nm(c.geom1)+'-'+nm(c.geom2); d[k]=round(d.get(k,0)+f[0])
    print(tag,'t %.1f q %.3f F %.0f nib %s clear %.3f tilt %.1f seated %s'%(R.t,S.lift_q(),S.lift_force(),S.nib_in_bin().round(3).tolist(),S.wheel_clear(),S.bin_tilt_abs(),S.seated()),d,flush=True)
R.mon=lambda: pr('mon') if R.i%2000==0 else None
o=B.grab(R); print(o); print(R.events)
sd=B.set_down(R); print(sd); pr('end')
print('zL',p['zL_abs'],'xbt',p['bar_x']-p['cb'])
