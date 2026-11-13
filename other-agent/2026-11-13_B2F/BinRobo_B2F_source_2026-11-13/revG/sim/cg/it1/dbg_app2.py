# iter1 diagnostic: approach trace with bin WORLD displacement (dx,dy along the initial tug axes), tilt and phase.
# usage: dbg_app2.py BIN i seed RESFILE   (honours CGB_F8)
import sys,os,json,math,mujoco,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..')); sys.path.insert(0,os.path.join(H,'..','..','g6'))
import simB_it1 as B
b,i,seed,rf=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
d=json.load(open(os.path.join(H,'res',rf))); r=[x for x in d['runs'] if x['i']==i][0]
p=dict(r['params']); pp=B.bin_params(b,p)
S=B.SimB(b,pp,mu=p['mu'],tug_pose=B.start_pose(pp,p['dy'],p['dyaw'])); R=B.RunnerB(S)
b00=S.d.xpos[S.bid['bin']].copy(); Rt0=S.d.xmat[S.bid['tug']].reshape(3,3).copy()
st={'ph':None}
def pr():
    dv=Rt0.T@(S.d.xpos[S.bid['bin']]-b00)
    if R.phase!=st['ph'] or R.i%1000==0:
        st['ph']=R.phase
        print('t %.2f %-10s bin d_ax %+.3f d_lat %+.3f |d| %.3f tilt %.1f binyaw %.1f'%(R.t,R.phase[:10],dv[0],dv[1],math.hypot(dv[0],dv[1]),S.bin_tilt_abs(),S.rpy('bin')[2]),flush=True)
R.mon=pr
g=B.grab(R,seed=seed*1000+i); print(g); print(R.events)
