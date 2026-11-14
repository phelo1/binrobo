exec(open('clash_r2.py').read().split("R={}")[0].replace("mode=sys.argv[1]","mode='imp'"))
import re
import os; pat=os.environ.get('PAT','.')
for st in ('nobin','carry'):
    for n,grp,b,s,src in posed(st):
        if re.search(pat,n):
            bb=s.BoundingBox(); print(st,'%-60s'%n[:60],[round(x,1) for x in (bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax)])
for k in ('lift','pad','padbase','comb','cforkL','cwheelL'):
    for st in ('nobin','carry'): print(k,st,np.round(POSE[st][k][1]*1000,1))
