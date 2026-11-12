# iter1 diagnostic: B1 approach trace (tug/bin pose, contacts on the bin) of a G1 MC case. usage: dbg_app1.py BIN i seed RESFILE
import sys,os,json,math,mujoco,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..')); sys.path.insert(0,os.path.join(H,'..','..','g6'))
import simB_it1 as B
b,i,seed,rf=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
d=json.load(open(os.path.join(H,'res',rf))); r=[x for x in d['runs'] if x['i']==i][0]
p=dict(r['params']); pp=B.bin_params(b,p)
S=B.SimB(b,pp,mu=p['mu'],tug_pose=B.start_pose(pp,p['dy'],p['dyaw'])); R=B.RunnerB(S)
nm=lambda g:mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,g); f=np.zeros(6)
bing=set(S.gid[n] for n in ('binhull','bar','ledge','rim','lid','binwheelL','binwheelR'))
def pr():
    dd={}
    for k in range(S.d.ncon):
        c=S.d.contact[k]
        if (c.geom1 in bing)!=(c.geom2 in bing):
            mujoco.mj_contactForce(S.m,S.d,k,f); kk=nm(c.geom1)+'-'+nm(c.geom2)
            if 'ground' in kk: continue
            dd[kk]=round(dd.get(kk,0)+f[0])
    xbt=pp['bar_x']-pp['cb']; q=S.nib_in_bin()
    print('t %.2f %-8s v %.3f wc %.2f wdc %.2f bin_in_tug %s relyaw %.1f gap %.3f'%(R.t,R.phase[:8],S.fwd_speed(),R.wc,R.wdc,np.round(S.bin_in_tug(),3).tolist(),(S.rpy()[2]-S.rpy('bin')[2]+180)%360-180,q[0]-GEOnl-xbt),dd,flush=True)
GEOnl=B.GEO['nib_l']/2
R.mon=lambda: pr() if R.i%1000==0 else None
g=B.grab(R,seed=seed*1000+i); print(g); print(R.events)
