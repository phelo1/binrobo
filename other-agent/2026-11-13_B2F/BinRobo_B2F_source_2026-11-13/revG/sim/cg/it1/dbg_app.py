# iter1 diagnostic (not a gate run): contact + geometry log during B's approach. usage: dbg_app.py SL250full|SL250empty|CL28
import sys,os,json,math,mujoco,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..')); sys.path.insert(0,os.path.join(H,'..','..','g6'))
import simB_cg as B
from bins_g5 import BINS
case=sys.argv[1]
if case.startswith('SL250'):
    b='ESE240SL250'; p=B.bin_params(b); p['fill']=BINS[b]['fill_full'] if case.endswith('full') else 0.0; pp=p; pose=B.start_pose(p); mu=0.6
else:
    b='ESE240CL'; d=json.load(open(os.path.join(H,'..','res','B_grab_ESE240CL.json'))); r=[x for x in d['runs'] if x['i']==int(case[2:])][0]
    p=dict(r['params']); pp=B.bin_params(b,p); pose=B.start_pose(pp,p['dy'],p['dyaw']); mu=p['mu']
S=B.SimB(b,pp,mu=mu,tug_pose=pose); R=B.RunnerB(S)
nm=lambda g:mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,g)
bing=set(S.gid[n] for n in ('binhull','bar','ledge','rim','lid','binwheelL','binwheelR'))
f=np.zeros(6); xbt=pp['bar_x']-pp['cb']
print('bin',b,'zL_abs %.4f wheel_r %.3f bar_habs %.4f lip rim bottom abs %.4f nib top abs %.4f'%(pp['zL_abs'],pp['wheel_r'],pp['bar_habs'],pp['zL_abs']-0.025,B.GEO['approach_nib_z']))
b0=S.d.xpos[S.bid['bin']].copy()
def pr():
    d={}
    for i in range(S.d.ncon):
        c=S.d.contact[i]
        if (c.geom1 in bing) != (c.geom2 in bing) or (c.geom1 in bing and c.geom2 in bing):
            mujoco.mj_contactForce(S.m,S.d,i,f); k=nm(c.geom1)+'-'+nm(c.geom2)
            if 'ground' in k: continue
            d[k]=(round(d.get(k,(0,))[0]+f[0]),[round(v,3) for v in c.pos])
    q=S.nib_in_bin()
    print('t %.2f %-14s gap %.3f nib_bin %s tilt %.1f moved %.0f mm bin_in_tug %s'%(R.t,R.phase[:14],q[0]-0.006-xbt,q.round(3).tolist(),S.bin_tilt_abs(),1000*np.linalg.norm(S.d.xpos[S.bid['bin']][:2]-b0[:2]),S.bin_in_tug().round(3).tolist()),d,flush=True)
R.mon=lambda: pr() if R.i%500==0 else None
g=B.grab(R,seed=int(sys.argv[2]) if len(sys.argv)>2 else 0); print(g); print(R.events)
