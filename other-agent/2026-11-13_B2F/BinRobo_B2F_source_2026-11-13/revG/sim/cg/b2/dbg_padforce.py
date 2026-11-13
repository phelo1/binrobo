import os,sys,math,json,numpy as np
sys.path[:0]=['b2','it1','../g6']; os.environ['CGB_F9']='1'
import mujoco, simB2 as B
from bins_g5 import BINS
b=sys.argv[1]; p=B.bin_params(b); p['fill']=BINS[b]['fill_full']
S=B.SimB(b,p,tug_pose=B.start_pose(p)); R=B.RunnerB(S); g=B.grab(R)
ext=[x for x in S.padlog if x[3]<0]
print(g['result'],g.get('pad_ok'),g.get('bin_tilt_abs'),g.get('wheel_clear_mm'))
def need(L,stroke_extra=0.0):
    cos0=math.cos(math.radians(-2))-0.04/(2*L); pk=(0,None)
    for q,P,cmd,tg in ext:
        e=0.04-q; a=math.acos(min(1,cos0+e/(2*L)))
        if a>math.radians(3):
            F=2*P*math.tan(a)
            if F>pk[0]: pk=(round(F),(round(e*1000,1),round(P),round(math.degrees(a),1)))
    return pk, round(L*(math.sin(math.acos(cos0))+math.sin(math.radians(2)))*1000,1)
for L in (0.06,0.08,0.10):
    print('L',L,'actuator force needed',need(L))
print('P vs e',[(round((0.04-q)*1000,1),P) for q,P,c,t in ext][::3])
