import os,sys,math,json,numpy as np
sys.path[:0]=['b2','it1','../g6']; os.environ['CGB_F9']='1'
import mujoco, simB2 as B
from bins_g5 import BINS
b=sys.argv[1]; full=sys.argv[2]=='full'
p=B.bin_params(b); p['fill']=BINS[b]['fill_full'] if full else 0.0
S=B.SimB(b,p,tug_pose=B.start_pose(p)); R=B.RunnerB(S)
last=['']
def mon():
    if R.phase!=last[0]:
        S.contacts(); last[0]=R.phase
        print('%.1f %s | padext %.4f padF %.0f lift %.3f F %.0f tilt %.2f clear %.0f'%(R.t,R.phase[:60],S.d.qpos[S.jq('padext')],S.pair('padg','binhull'),S.lift_q(),S.lift_force(),S.bin_tilt_abs(),S.wheel_clear()*1000),flush=True)
R.mon=mon
g=B.grab(R); print(json.dumps({k:v for k,v in g.items()},default=str)); print(R.events)
