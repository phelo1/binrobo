import os,sys,math,json,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path[:0]=[H,os.path.join(H,'..','it1'),os.path.join(H,'..','..','g6')]
os.environ.setdefault('CGB_F9','1'); os.environ.setdefault('CMP_LIP','en840'); os.environ.setdefault('CMP_COMB','fw_pivot')
import mujoco, simB1fw as B
from bins_g5 import BINS
b=sys.argv[1] if len(sys.argv)>1 else 'ESE240SL'
p=B.bin_params(b); p['fill']=BINS[b]['fill_full']
S=B.SimB(b,p,tug_pose=B.start_pose(p)); R=B.RunnerB(S); g=B.grab(R)
print(json.dumps({k:v for k,v in g.items()},default=str))
q=S.nib_in_bin(); P=S.p; xbt=P['bar_x']-P['cb']; zL=P['zL_abs']-P['wheel_r']; nh=B.GEO['nib_h']; nl=B.GEO['nib_l']; top=q[2]+nh/2+0.005
print('nib in bin',q,'xbt',xbt,'zL',zL,'top',top,'inx',(xbt-0.004<q[0]-nl/2),(q[0]+nl/2<xbt+0.026),'inz',(top>zL-0.015),(top<zL+0.006),'iny',abs(q[1]),abs(B.GEO['tooth_hw']-P['lip_w']/2)+0.02)
print('yaw',math.degrees(S.d.qpos[S.jq('combyaw')]),'roll',math.degrees(S.d.qpos[S.jq('combroll')]),'clear',S.wheel_clear())
S.contacts(); print({k:round(v) for k,v in S.contacts().items() if v>1})
