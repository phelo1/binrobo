# iter1 diagnostic: keeper vs handle bar during phase 3 of a B1 grab. usage: dbg_keep.py BIN i seed RESFILE
import sys,os,json,math,mujoco,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..')); sys.path.insert(0,os.path.join(H,'..','..','g6'))
import simB_it1 as B
b,i,seed,rf=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
d=json.load(open(os.path.join(H,'res',rf))); r=[x for x in d['runs'] if x['i']==i][0]
p=dict(r['params']); pp=B.bin_params(b,p)
S=B.SimB(b,pp,mu=p['mu'],tug_pose=B.start_pose(pp,p['dy'],p['dyaw'])); R=B.RunnerB(S)
def pr():
    if not R.phase[:1] in '23': return
    S.contacts(); kb=S.d.xpos[S.bid['keeper']]; Rk=S.d.xmat[S.bid['lift']].reshape(3,3)
    bar=S.d.geom_xpos[S.gid['bar']]; tip=S.d.geom_xpos[S.gid['keeptip']]
    rel=lambda v: Rk.T@(v-kb)
    print('t %.2f %-6s keeper %.1f deg  bar rel hinge (x,z) %s  tip rel hinge %s  keeptip-bar %.0f N  tilt %.1f  bar_r %.4f'%(R.t,R.phase[:6],math.degrees(S.d.qpos[S.jq('keeper')]),np.round(rel(bar)[[0,2]],4).tolist(),np.round(rel(tip)[[0,2]],4).tolist(),S.pair('keeptip','bar')+S.pair('keeptip2','bar'),S.bin_tilt_abs(),pp['bar_r']),flush=True)
R.mon=lambda: pr() if R.i%400==0 else None
g=B.grab(R,seed=seed*1000+i); print(g)
