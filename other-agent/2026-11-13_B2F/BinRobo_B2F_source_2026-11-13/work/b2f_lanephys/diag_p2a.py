import sys, numpy as np, mujoco, pickle, os, math
import lanerun as LR, lane_world as LW, simB2h as B
cfg = LR.RUNS['P2a']; S, R, L = LR.build(cfg)
ck = pickle.load(open('runs/P2a/ckpt.pkl','rb')); LR.set_state(S, ck['state'])
m=S.m; d=S.d
for w in ('wheelL','wheelR','cwheelL','cwheelR','tug'):
    b=L.bid[w]; p=d.xpos[b]; s,l=LW.project(p[:2][None]); print(w, 's %.3f lat %.3f z-surf %.3f'%(s[0],l[0], p[2]-LW.surface_z(p[0],p[1],cfg['variant'])[0]))
f=np.zeros(6)
for i in range(d.ncon):
    c=d.contact[i]; mujoco.mj_contactForce(m,d,i,f); print(mujoco.mj_id2name(m,5,c.geom1), mujoco.mj_id2name(m,5,c.geom2), np.round(f[:3],1), np.round(c.frame[:3],2))
print('tug mass', m.body_subtreemass[L.bid['tug']], 'B.GEO cx cy', B.GEO['cx'], B.GEO['cy'])
