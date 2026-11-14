exec(open('/workspace/work/coldeye_rev2/common.py').read())
out={}
nb=posed('nobin')
tug=[it for it in nb if it[2]=='tug' and not it[0].startswith(('RK Castor mounting','RK Castor cross-beam 50','RK Bump stop'))]
near=[it for it in tug if it[3].BoundingBox().xmax>700 and it[3].BoundingBox().zmin<420]
print('near parts',len(near),flush=True)
res=[]
for deg in (0,2.0,-2.0,2.6,-2.6):
  for s in (1,-1):
    E=roll(envelope(950,s*280),deg)
    for n,grp,b,sh,src in near:
        bb=sh.BoundingBox(); eb=E.BoundingBox()
        if bb.xmax<eb.xmin-30 or eb.xmax<bb.xmin-30 or bb.ymax<eb.ymin-30 or eb.ymax<bb.ymin-30 or bb.zmax<eb.zmin-30 or eb.zmax<bb.zmin-30: continue
        v=vol(common(E,sh)); dd=dist(E,sh) if v<=1 else 0.0
        if v>1 or dd<20: res.append(dict(roll=deg,side=s,part=n[:60],vol_mm3=round(v),gap_mm=round(dd,1)))
out['envelope']=res
for r in res: print(r)
# exact forward-swivelled wheel at roll, distance to bumper parts
fw=[]
for deg in (0,2.0,-2.0,2.6,-2.6):
  for s in (1,-1):
    W=roll(cq.Workplane('XZ').circle(100).extrude(25,both=True).val().moved(cq.Location(cq.Vector(1000,s*280,100))),deg)
    for n,grp,b,sh,src in near:
        if n.startswith(('SF','DK')):
            fw.append(dict(roll=deg,side=s,part=n[:40],gap_mm=round(dist(W,sh),1),vol=round(vol(common(W,sh)))))
out['fwd_wheel']=fw
print('fwd wheel min gap', min(f['gap_mm'] for f in fw), [f for f in fw if f['gap_mm']<20])
json.dump(out,open('env_r2.json','w'),indent=1)
