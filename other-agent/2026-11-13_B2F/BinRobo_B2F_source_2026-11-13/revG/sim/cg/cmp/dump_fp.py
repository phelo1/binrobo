#!/usr/bin/env python3
"""B1 plan footprint in the tug frame (origin = drive-axle centre on the ground, +x = castor end): every tug geom AABB corner
(compiled model) + the carried ESE 240 SL hull/wheels after a nominal grab. Writes res/fp_B1.json."""
import os, sys, json, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path[:0]=[H,os.path.join(H,'..','it1'),os.path.join(H,'..','..','g6')]
os.environ.setdefault('CGB_F9','1')
import mujoco, importlib; B=importlib.import_module(os.environ.get('CMP_SIM','simB_it1'))
from bins_g5 import BINS
p=B.bin_params('ESE240SL'); p['fill']=BINS['ESE240SL']['fill_full']
S=B.SimB('ESE240SL',p,tug_pose=B.start_pose(p)); R=B.RunnerB(S); g=B.grab(R); R.run_for(1.0)
Rt=S.d.xmat[S.bid['tug']].reshape(3,3); pt=S.d.xpos[S.bid['tug']]
def tf(w): return (Rt.T@(w-pt))[:2]
tug=[]; binp=[]
tugbodies=set(); 
for b in range(S.m.nbody):
    r=b
    while r!=0 and r!=S.bid['tug']: r=S.m.body_parentid[r]
    if r==S.bid['tug']: tugbodies.add(b)
for gi in range(S.m.ngeom):
    bd=S.m.geom_bodyid[gi]; nm=mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,gi) or ''
    if bd in tugbodies:
        Rg=S.d.geom_xmat[gi].reshape(3,3); c=S.d.geom_xpos[gi]; sz=S.m.geom_size[gi]; t=S.m.geom_type[gi]
        if t==mujoco.mjtGeom.mjGEOM_BOX: ext=sz
        elif t==mujoco.mjtGeom.mjGEOM_CYLINDER: ext=np.array([sz[0],sz[0],sz[1]])
        elif t==mujoco.mjtGeom.mjGEOM_SPHERE: ext=np.array([sz[0]]*3)
        else: continue
        for sx in (-1,1):
            for sy in (-1,1):
                for sz_ in (-1,1): tug.append([round(float(v),4) for v in tf(c+Rg@(ext*np.array([sx,sy,sz_])))]+[nm])
mid=S.m.geom_dataid[S.gid['binhull']]; va=S.m.mesh_vertadr[mid]; nv=S.m.mesh_vertnum[mid]; V=S.m.mesh_vert[va:va+nv]
gp=S.m.geom_pos[S.gid['binhull']]; Rg=np.zeros(9); mujoco.mju_quat2Mat(Rg,S.m.geom_quat[S.gid['binhull']]); Rg=Rg.reshape(3,3)
Rb=S.d.xmat[S.bid['bin']].reshape(3,3); pb=S.d.xpos[S.bid['bin']]
for v in V: binp.append([round(float(x),4) for x in tf(pb+Rb@(gp+Rg@v))])
for w in ('bwL','bwR'): binp.append([round(float(x),4) for x in tf(S.d.xpos[S.bid[w]])])
hand=tf(S.d.geom_xpos[S.gid['bar']])
json.dump(dict(grab=g['result'],tug=tug,bin=binp,bar_xy=[float(hand[0]),float(hand[1])],bin_origin=[float(x) for x in tf(pb)]),open(os.path.join(H,'res','fp_%s.json'%os.environ.get('CMP_SIM','simB_it1')),'w'),indent=0)
print('grab',g['result'],'bar',hand,'bin origin',tf(pb))
