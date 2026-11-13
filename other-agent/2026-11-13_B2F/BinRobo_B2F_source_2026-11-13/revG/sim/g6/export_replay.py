"""Run one real MuJoCo grab+tilt+tow+release (G6 hook, M110h, ESE 240 SL full, 12% uphill) and export geoms + body poses for a three.js replay."""
import json,os,sys,numpy as np,mujoco
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
os.environ['G6_MASSFILE']=os.path.join(HERE,'mass_g6_M110h.json')
import sim_g5, tow_g5
CAP={}
def snap(s):
    CAP['S']=s; return {'q':np.round(np.hstack([s.d.xpos,s.d.xquat]),4).tolist()}
sim_g5.Sim.snapshot=snap
ghp=json.load(open(os.path.join(HERE,'..','results_G6_ballast_M110h_rel_up12.json')))['results']['ESE240SL']['ghp']
o,R=tow_g5.run('ESE240SL','rel_up12','B2',ghp)
S=CAP['S']; m=S.m
G=[]
for g in range(m.ngeom):
    if m.geom_rgba[g][3]<0.02: continue
    t=int(m.geom_type[g]); e=dict(b=int(m.geom_bodyid[g]),t=t,s=np.round(m.geom_size[g],4).tolist(),p=np.round(m.geom_pos[g],4).tolist(),q=np.round(m.geom_quat[g],4).tolist(),c=np.round(m.geom_rgba[g],2).tolist(),n=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,g) or '')
    if t==mujoco.mjtGeom.mjGEOM_MESH:
        mi=m.geom_dataid[g]; va,vn=m.mesh_vertadr[mi],m.mesh_vertnum[mi]; fa,fn=m.mesh_faceadr[mi],m.mesh_facenum[mi]
        e['v']=np.round(m.mesh_vert[va:va+vn],4).ravel().tolist(); e['f']=m.mesh_face[fa:fa+fn].ravel().tolist()
    if t==mujoco.mjtGeom.mjGEOM_PLANE: continue
    G.append(e)
F=[dict(t=r['t'],ph=r['ph'],pw=r.get('pw'),tilt=round(r.get('tilt',0),1),q=r['P']['q']) for r in R.rec]
json.dump(dict(geoms=G,frames=F,events=R.events,ok=o.get('ok'),bodies=[mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,b) for b in range(m.nbody)]),open(os.path.join(HERE,'rec','replay_G6.json'),'w'),separators=(',',':'))
print('ok',o.get('ok'),'geoms',len(G),'frames',len(F),'bodies',m.nbody)
