# iter1 diagnostic: creep-phase yaw trace (tug yaw, bin yaw, true relative yaw, nib gap, contacts on the bin). usage: dbg_app3.py BIN i seed RESFILE
import sys,os,json,math,mujoco,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..')); sys.path.insert(0,os.path.join(H,'..','..','g6'))
import simB_it1 as B
b,i,seed,rf=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
d=json.load(open(os.path.join(H,'res',rf))); r=[x for x in d['runs'] if x['i']==i][0]
p=dict(r['params']); pp=B.bin_params(b,p)
S=B.SimB(b,pp,mu=p['mu'],tug_pose=B.start_pose(pp,p['dy'],p['dyaw'])); R=B.RunnerB(S)
nm=lambda g:mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,g); f=np.zeros(6)
bing=set(S.gid[n] for n in ('binhull','bar','ledge','rim','lid','binwheelL','binwheelR'))
xbt=pp['bar_x']-pp['cb']; st={'ph':None}
def pr():
    if not (R.phase.startswith('1c') or R.phase.startswith('1b')) : return
    if R.phase!=st['ph'] or R.i%250==0:
        st['ph']=R.phase; dd={}
        for k in range(S.d.ncon):
            c=S.d.contact[k]
            if (c.geom1 in bing)!=(c.geom2 in bing):
                mujoco.mj_contactForce(S.m,S.d,k,f); kk=nm(c.geom1)+'-'+nm(c.geom2)
                if 'ground' in kk: continue
                dd[kk]=round(dd.get(kk,0)+f[0])
        q=S.nib_in_bin()
        print('t %.2f %-6s tugyaw %.2f binyaw %.2f rel %.2f gap %.3f dy %.3f wd %.3f'%(R.t,R.phase[:6],S.rpy()[2],S.rpy('bin')[2],(S.rpy()[2]-S.rpy('bin')[2]+180)%360-180,q[0]-B.GEO['nib_l']/2-xbt,S.bin_in_tug()[1],R.wd*B.RW),dd,flush=True)
R.mon=pr
g=B.grab(R,seed=seed*1000+i); print(g); print(R.events)
