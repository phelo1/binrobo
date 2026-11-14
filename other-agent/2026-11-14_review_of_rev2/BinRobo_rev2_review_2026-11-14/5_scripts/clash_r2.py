import runpy, numpy as np, json, math, sys, itertools, pickle
import cadquery as cq
from OCP.gp import gp_Trsf
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
mode=sys.argv[1]  # imp or b2f
if mode=='imp':
    g=runpy.run_path('model_parts_r2.py'); PARTS=g['PARTS']; POSE=g['POSE']
else:
    import os; os.chdir('/workspace/work/coldeye_imp/b2f')
    sys.argv=['x','nomesh','nostep']; g=runpy.run_path('cad_B2F_src.py'); PARTS=[list(p)+['CAD'] for p in g['PARTS']]
    M=g['M']; Q=np.load('rec_B2F.npz')['q']; qmat=g['qmat']; BODIES=M['bodies']
    def poses(frame):
        q=Q[frame]; Rt=qmat(q[0,3:]); pt=q[0,:3]; return {n:(Rt.T@qmat(q[k,3:]),Rt.T@(q[k,:3]-pt)) for k,n in enumerate(BODIES)}
    POSE=dict(nobin=poses(M['frames']['start']),carry=poses(M['frames']['carrying']))
INST={'wheel':['wheelL','wheelR'],'cfork':['cforkL','cforkR'],'cwheel':['cwheelL','cwheelR'],'bw':['bwL','bwR']}
def tr(R,p):
    T=gp_Trsf(); T.SetValues(*[float(v) for v in (R[0,0],R[0,1],R[0,2],p[0]*1000,R[1,0],R[1,1],R[1,2],p[1]*1000,R[2,0],R[2,1],R[2,2],p[2]*1000)]); return cq.Location(T)
def vol(s): 
    pr=GProp_GProps(); BRepGProp.VolumeProperties_s(s.wrapped,pr); return pr.Mass()
def common(a,b):
    op=BRepAlgoAPI_Common(a.wrapped,b.wrapped); op.Build(); s=cq.Shape.cast(op.Shape()); return s
def posed(st):
    out=[]
    for name,grp,col,w,rd,src in PARTS:
        if grp in('bin','bw','lid') and st=='nobin': continue
        for b in INST.get(grp,[grp]):
            R,p=POSE[st][b]; s=w.moved(tr(R,p)); out.append((name+('' if b==grp else ' '+b[-1]),grp,b,s,src))
    return out
def clashes(items,minv=1.0):
    bb=[(it,it[3].BoundingBox()) for it in items]; res=[]
    for (a,ba),(b,bb2) in itertools.combinations(bb,2):
        if ba.xmax<bb2.xmin or bb2.xmax<ba.xmin or ba.ymax<bb2.ymin or bb2.ymax<ba.ymin or ba.zmax<bb2.zmin or bb2.zmax<ba.zmin: continue
        try: c=common(a[3],b[3]); v=vol(c)
        except Exception as e: v=-1
        if v>minv or v<0:
            cb=c.BoundingBox() if v>0 else None
            res.append(dict(a=a[0],b=b[0],ga=a[1],gb=b[1],vol_mm3=round(v,1),bbox=None if cb is None else [round(x) for x in (cb.xmin,cb.xmax,cb.ymin,cb.ymax,cb.zmin,cb.zmax)]))
    return res
R={}
for st in ('nobin','carry'):
    it=posed(st); R[st]=clashes(it); print(st,len(it),'parts',len(R[st]),'overlaps',flush=True)
# volumes of all parts for mass
R['vol']={n:round(vol(w),0) for n,grp,col,w,rd,src in PARTS}
json.dump(R,open('clash_%s_r2.json'%mode,'w'),indent=1)
