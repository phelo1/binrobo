# iter1: comb / nib / pad geometry vs bins_g5 for every bin the carrier must take (G1 bins + SL250 + ESE140CL). Bin settled alone 1.5 s,
# then measured in a frame aligned with the bin's ground footprint (x toward the tug/handle side). Not a gate run.
import sys,os,json,math,itertools,mujoco,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..')); sys.path.insert(0,os.path.join(H,'..','..','g6'))
import simB_cg as B
from bins_g5 import BINS
G=B.GEO
def meas(b,bar_d,cb_d,comb_d,fill):
    Bn=BINS[b]; p=B.bin_params(b); p['bar_habs']=Bn['bar_abs'][0]+bar_d; p['cb']=Bn['cb'][0]+cb_d; p['comb_d']=comb_d; p['fill']=fill
    p=B.bin_params(b,p)
    S=B.SimB(b,p,tug_pose=(6.0,0,0)); 
    for _ in range(3000): mujoco.mj_step(S.m,S.d)
    Rb=S.d.xmat[S.bid['bin']].reshape(3,3); pb=S.d.xpos[S.bid['bin']]
    pitch=math.degrees(math.atan2(-Rb[2,0],Rb[2,2]))
    W=lambda v: pb+Rb@np.array(v)
    xbt=p['bar_x']-p['cb']; zL=p['zL_abs']-p['wheel_r']
    root=W([xbt,0,zL]); rimb=W([xbt+0.026,0,zL-0.025])
    bh=p['bar_h']; xbb=min(-0.025,xbt-0.110)
    pB=W([xbb,0,-0.06]); pT=W([xbt,0,bh])
    def face_x(z):
        f=(z-pB[2])/(pT[2]-pB[2]); return float(pB[0]+f*(pT[0]-pB[0]))
    return dict(bin=b,bar_d=bar_d,cb_d=cb_d,comb_d=comb_d,fill=fill,pitch_deg=round(pitch,2),root_x=round(root[0],4),root_z=round(root[2],4),rim_bottom_z=round(rimb[2],4),
                ledge_z=round(root[2],4),face_at={z:round(face_x(z)-root[0],4) for z in (0.25,0.30,0.35,0.40,0.45,0.50)},wheel_r=p['wheel_r'],lip_w=round(p['lip_w'],3),zL_abs_nom=round(p['zL_abs'],4))
out=[]
for b in ('WEB140','ESE140CL','ESE240SL','ESE240CL','ESE240SL250'):
    Bn=BINS[b]
    for bar_d,cb_d,comb_d,fill in itertools.product((-Bn['bar_abs'][1],Bn['bar_abs'][1]),(-Bn['cb'][1],Bn['cb'][1]),(-0.01,0.01),(0.0,)):
        out.append(meas(b,bar_d,cb_d,comb_d,fill))
    out.append(meas(b,0,0,0,Bn['fill_full']))
json.dump(out,open(os.path.join(H,'res','geo_check.json'),'w'),indent=0,default=str)
for b in ('WEB140','ESE140CL','ESE240SL','ESE240CL','ESE240SL250'):
    R=[o for o in out if o['bin']==b]
    f=lambda k: (min(o[k] for o in R),max(o[k] for o in R))
    fa=lambda z: (min(o['face_at'][z] for o in R),max(o['face_at'][z] for o in R))
    print(b,'pitch',f('pitch_deg'),'ledge z',f('ledge_z'),'rim bottom z',f('rim_bottom_z'),'face-root dx @0.27/0.45:',fa(0.30),fa(0.45),'lip_w',f('lip_w'))
