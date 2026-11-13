import json,sys,os,numpy as np,mujoco
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mc_g5 import make_sim
from scen_g5 import Runner, approach
j=json.load(open('../results_G6_mc_CRA240_B2_H3.json')); p=j['runs'][19]['params']; ghp=dict(j['ghp'])
if len(sys.argv)>1: ghp.update(json.loads(sys.argv[1]))
S=make_sim(p,'B2',ghp); R=Runner(S,rec_hz=2); R.recording=False
seen={}
prev=R.step
def st():
    prev()
    if R.i%50==0:
        m,d=S.m,S.d
        for k in range(d.ncon):
            c=d.contact[k]; b1=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,m.geom_bodyid[c.geom1]); b2=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,m.geom_bodyid[c.geom2])
            g1=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,c.geom1); g2=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,c.geom2)
            key=tuple(sorted([str(b1)+':'+str(g1),str(b2)+':'+str(g2)]))
            if 'ground' in key[0] or 'ground' in key[1] or 'floor' in str(key): continue
            if key not in seen: seen[key]=round(R.t,2)
R.step=st
ok=approach(R,0.10)
print('docked',ok,'t',round(R.t,1),'pawls',S.sensors(strict=True) if hasattr(S,'sensors') else '')
for k,t in sorted(seen.items(),key=lambda x:x[1]): print(t,k)
