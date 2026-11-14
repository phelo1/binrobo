exec(open('/workspace/work/coldeye_rev2/common.py').read())
rho=dict(steel=7.85e-6,hdpe=0.95e-6,uhmw=0.94e-6,rubber=1.2e-6)
want=['LM Mast upright','LM Rail backing flat','LM Mast foot plate','LM Lift hard stop','SW Lift top limit','LA Actuator base bracket','SF Bumper bracket','RK Pivot hanger','RK Pivot pin','RK Castor cross-beam','RK Castor mounting','RK Bump stop','FR Side rail','LC Comb plate','LC Carriage plate','PD Pad slide rods','PD Pad die','PD Pad springs','PD Pad guide','BL Ballast','LM Mast gusset','EL Main fuse','LC Nib']
tot={}
for name,grp,col,w,rd,src in PARTS:
    for p in want:
        if name.startswith(p):
            v=vol(w); tot.setdefault(p,[0,0,[]]); tot[p][0]+=v; tot[p][1]+=1; tot[p][2].append(name[:50])
for p,(v,n,names) in tot.items(): print('%-28s n=%d vol %.0f cm3  steel %.2f kg   %s'%(p,n,v/1000,v*7.85e-6,names[0]))
