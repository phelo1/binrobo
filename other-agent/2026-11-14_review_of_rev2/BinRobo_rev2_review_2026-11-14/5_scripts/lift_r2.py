exec(open('/workspace/work/coldeye_rev2/common.py').read())
out={}
MOV={'lift','comb','keeper','padbase','pad'}
nb=posed('nobin'); ca=posed('carry')
tug=[it for it in nb if it[2]=='tug']
fixed_top=[it for it in tug if it[3].BoundingBox().zmax>1000 or it[0].startswith(('LM','LA','SW Lift'))]
def shift(items,dz): return [(n,g,b,s.moved(cq.Location(cq.Vector(0,0,dz))),src) for n,g,b,s,src in items]
z0=POSE['nobin']['lift'][1][2]*1000; zc=POSE['carry']['lift'][1][2]*1000; qc=zc-z0
out['lift_z_q0']=round(z0,1); out['q_carry']=round(qc,1)
mv0=[it for it in nb if it[2] in MOV]
mvc=[it for it in ca if it[2] in MOV or it[2] in ('bin','bwL','bwR','lid')]
def cross(A,B):
    r=[]
    for a in A:
        ba=a[3].BoundingBox()
        for b in B:
            bb=b[3].BoundingBox()
            if ba.xmax<bb.xmin or bb.xmax<ba.xmin or ba.ymax<bb.ymin or bb.ymax<ba.ymin or ba.zmax<bb.zmin or bb.zmax<ba.zmin: continue
            c=common(a[3],b[3]); v=vol(c)
            if v>1: r.append(dict(a=a[0][:45],b=b[0][:45],vol=round(v),bbox=bbox(c)))
    return r
# expected rail/actuator sliding contacts filtered later
for q in (295,300.1,310,336.1,340,346.1,352):
    A=shift(mv0,q); r=cross(A,fixed_top)
    r=[x for x in r if not (x['b'].startswith('LM Linear rail') and x['a'].startswith(('LC Rail carriage','LC Carriage plate'))) and not x['b'].startswith('LA Lift actuator FDI') ]
    out['q%s'%q]=r; print('q',q,r,flush=True)
# minimum vertical gap top of moving parts to top tie, per q
tie=[it for it in tug if it[0].startswith('LM Mast top tie')][0][3]
top=max(s.BoundingBox().zmax for n,g,b,s,src in mv0 if s.BoundingBox().xmax>440)
out['moving_top_q0']=round(top,1)
for q in (340,345,346.1):
    out['gap_top_tie_q%s'%q]=round(tie.BoundingBox().zmin-(top+q),1)
# with bin at q=340
Ab=shift(mvc,340-qc); out['bin_q340']=cross(Ab,tug)
binp=[it for it in Ab if it[2] in('bin','lid','bwL','bwR')]
out['bin_q340_zmax_xmax']=[round(max(s.BoundingBox().zmax for *_,s,src in [(i[0],i[1],i[2],i[3],i[4]) for i in binp])),round(max(i[3].BoundingBox().xmax for i in binp))]
out['bin_wheel_bottom_q340']=round(min(i[3].BoundingBox().zmin for i in binp if i[2] in ('bwL','bwR')))
out['bin_wheel_bottom_carry']=round(min(i[3].BoundingBox().zmin for i in mvc if i[2] in ('bwL','bwR')))
# comb vs bin/mast distances at carry
comb=[i for i in ca if i[0].startswith('LC Comb plate')][0][3]
for n,g,b,s,src in ca:
    if n.startswith(('LM Mast upright','LM Linear rail','BIN','LM Rail backing','LM Lift hard')):
        out.setdefault('comb_dist_carry',{})[n[:40]+' '+b]=round(dist(comb,s),1)
json.dump(out,open('lift_r2.json','w'),indent=1)
for k,v in out.items():
    if not k.startswith('q'): print(k,v)
