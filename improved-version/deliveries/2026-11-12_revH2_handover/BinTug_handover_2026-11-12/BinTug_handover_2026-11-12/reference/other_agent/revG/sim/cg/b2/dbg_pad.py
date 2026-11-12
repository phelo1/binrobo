import os,sys,math,json,numpy as np
H='b2'; sys.path[:0]=[H,'it1','../g6']; os.environ['CGB_F9']='1'
import mujoco, simB2 as B
from bins_g5 import BINS
b=sys.argv[1] if len(sys.argv)>1 else 'ESE240SL'
p=B.bin_params(b); p['fill']=BINS[b]['fill_full']
S=B.SimB(b,p,tug_pose=B.start_pose(p)); R=B.RunnerB(S)
def st(tag):
    S.contacts(); print(tag,'t %.1f padext %.4f pad %.4f padF %.0f padcmd %.4f tgt %.4f lift %.3f liftF %.0f binTilt %.2f clear %.0f'%(R.t,S.d.qpos[S.jq('padext')],S.d.qpos[S.jq('pad')],S.pair('padg','binhull'),S.pad_cmd,S.pad_tgt,S.lift_q(),S.lift_force(),S.bin_tilt_abs(),S.wheel_clear()*1000),flush=True)
st('start'); R.run_for(0.5); st('0.5s')
ok=B.approach(R,seed=0); st('docked %s %s'%(ok,getattr(R,'dock_why',None)))
B.set_pad(S,0.0); 
for k in range(10): R.run_for(0.5); st('ext')
