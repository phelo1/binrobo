# iter1 diagnostic (not a gate run): B1 grab of a G1 MC case with a contact log from the lift onward. usage: dbg_grab1.py BIN i seed
import sys,os,json,math,mujoco,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..')); sys.path.insert(0,os.path.join(H,'..','..','g6'))
import simB_it1 as B
b,i,seed=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
d=json.load(open(os.path.join(H,'res','B1_grab_%s.json'%b))); r=[x for x in d['runs'] if x['i']==i][0]
p=dict(r['params']); pp=B.bin_params(b,p)
S=B.SimB(b,pp,mu=p['mu'],tug_pose=B.start_pose(pp,p['dy'],p['dyaw'])); R=B.RunnerB(S)
nm=lambda g:mujoco.mj_id2name(S.m,mujoco.mjtObj.mjOBJ_GEOM,g); f=np.zeros(6)
bing=set(S.gid[n] for n in ('binhull','bar','ledge','rim','lid','binwheelL','binwheelR'))
def pr():
    if not (R.phase[:1] in '23' or R.phase.startswith('1c')): return
    dd={}
    for k in range(S.d.ncon):
        c=S.d.contact[k]
        if (c.geom1 in bing)!=(c.geom2 in bing):
            mujoco.mj_contactForce(S.m,S.d,k,f); kk=nm(c.geom1)+'-'+nm(c.geom2)
            if 'ground' in kk: continue
            dd[kk]=round(dd.get(kk,0)+f[0])
    q=S.nib_in_bin(); xbt=pp['bar_x']-pp['cb']
    g=S.gid['nib']; Rb=S.d.xmat[S.bid['bin']].reshape(3,3); Rg=S.d.geom_xmat[g].reshape(3,3)
    ends=[Rb.T@(S.d.geom_xpos[g]+Rg@np.array([-0.006,sy*0.12,0])-S.d.xpos[S.bid['bin']]) for sy in (1,-1)]
    ry=S.rpy()[2]-S.rpy('bin')[2]
    print('   relyaw %.2f deg; nib bin-side face at y=+0.12: %.1f mm, y=-0.12: %.1f mm from body face; outer faces %.1f / %.1f (rim inner face at 22)'%(ry,1000*(ends[0][0]-xbt),1000*(ends[1][0]-xbt),1000*(ends[0][0]-xbt)+12,1000*(ends[1][0]-xbt)+12))
    print('t %.2f %-10s q %.3f F %.0f gap %.3f nibz_bin %.3f zL %.3f tilt %.1f clear %.3f seated %s padext %.3f keeper %.0f'%(R.t,R.phase[:10],S.lift_q(),S.lift_force(),q[0]-0.006-xbt,q[2],pp['zL_abs']-pp['wheel_r'],S.bin_tilt_abs(),S.wheel_clear(),S.seated(),S.d.qpos[S.jq('padext')],math.degrees(S.d.qpos[S.jq('keeper')])),dd,flush=True)
R.mon=lambda: pr() if R.i%500==0 else None
g=B.grab(R,seed=seed*1000+i); print(g); print(R.events)
