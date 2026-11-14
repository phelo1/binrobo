exec(open('/workspace/work/coldeye_rev2/common.py').read())
import copy
G=g['G']
exec(open('looms_r2_src.py').read())
def loom_solid(pl,r):
    sol=None
    for a,b in zip(pl[:-1],pl[1:]):
        a=np.array(a)*1000; b=np.array(b)*1000; d=b-a; L=np.linalg.norm(d)
        if L<1e-3: continue
        c=cq.Solid.makeCylinder(r,L,cq.Vector(*a),cq.Vector(*(d/L)))
        sol=[c] if sol is None else sol+[c]
    sol+= [cq.Solid.makeSphere(r,cq.Vector(*(np.array(p)*1000)),angleDegrees1=-90,angleDegrees2=90) for p in pl]
    return cq.Compound.makeCompound(sol)
# add a q=340 state (no bin): lift-frame bodies raised by 340-0
z0=POSE['nobin']['lift'][1][2]
P340={k:(R,p.copy()) for k,(R,p) in POSE['nobin'].items()}
for k in ('lift','comb','keeper','padbase','pad'): P340[k]=(P340[k][0],P340[k][1]+np.array([0,0,0.340]))
POSE['q340']=P340
res=[]; mind={}
PROF=rprof()
import bisect
def prof_r(z):
    # envelope radius at height z above ground (wheel+fork+stem), from env.py profile
    if z<0 or z>260: return -1
    if z<=200:
        h=z-100; c=math.sqrt(max(100*100-h*h,0)); rr=math.hypot(50+c,25)
        if -15<=h<=150: rr=max(rr,math.hypot(90,40))
        return rr
    if z<=250: return math.hypot(90,40)
    return 40.0
def env_gap(pl,r,s_,deg):
    best=1e9; th=math.radians(-deg)
    for a,b in zip(pl[:-1],pl[1:]):
        a=np.array(a)*1000; b=np.array(b)*1000
        for t in np.linspace(0,1,60):
            p=a+(b-a)*t
            # undo roll about x axis through (y0,z200)
            y=p[1]; z=p[2]-200; y2=y*math.cos(th)-z*math.sin(th); z2=y*math.sin(th)+z*math.cos(th)+200
            rad=math.hypot(p[0]-950,y2-s_*280)
            # nearest envelope height band within r
            g=1e9
            for dz in np.linspace(-r,r,5):
                pr=prof_r(z2+dz)
                if pr>0: g=min(g,rad-pr-math.sqrt(max(r*r-dz*dz,0)))
            if z2-r>260 and rad<40+r: g=min(g,z2-r-260)  # above stem top
            best=min(best,g)
    return best
import os
for st in os.environ['ST'].split(','):
    parts=posed('nobin' if st=='q340' else st)
    if st=='q340':
        parts=[(n,g_,b,(s.moved(cq.Location(cq.Vector(0,0,340))) if b in ('lift','comb','keeper','padbase','pad') else s),src) for n,g_,b,s,src in parts]
    for lid,lname,route,cores,col,r,pls in looms(st):
        if lid not in os.environ.get('LM','L1,L2,L3,L4,L5,L6,L7,L8,L9,L10,L11').split(','): continue
        for k,pl in enumerate(pls):
            S=loom_solid(pl,r*1000); sb=S.BoundingBox()
            for n,grp,b,sh,src in parts:
                bb=sh.BoundingBox()
                if bb.xmax<sb.xmin-10 or sb.xmax<bb.xmin-10 or bb.ymax<sb.ymin-10 or sb.ymax<bb.ymin-10 or bb.zmax<sb.zmin-10 or sb.zmax<bb.zmin-10: continue
                v=vol(common(S,sh))
                moving=b not in ('tug',) 
                if v>1: res.append((st,lid,k,n[:45],b,round(v)))
            for s_ in (1,-1):
                for deg in (0,2.0,-2.0):
                    out_=env_gap(pl,r*1000,s_,deg)
                    if out_<15: res.append((st,lid,k,'CASTOR ENVELOPE side %d roll %s'%(s_,deg),'env','gap %.1f'%out_))
        print(st,lid,flush=True)
json.dump(res,open('loom_r2_%s_%s.json'%(os.environ['ST'],os.environ.get('LM','all').replace(',','')),'w'),indent=0)
for r in res: print(r)
