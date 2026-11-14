exec(open('/workspace/work/coldeye_rev2/common.py').read())
nb={n:s for n,g_,b,s,src in posed('nobin') if b=='tug'}
def f(p): 
    r=[k for k in nb if k.startswith(p)]; return r
pairs=[('RK Pivot hanger plate rear','FR Nose cross-member'),('RK Pivot hanger plate front','FR Nose cross-member'),
('SF Bumper bracket L','FR Nose cross-member'),('SF Bumper bracket L','SF Front bumper (switch'),('SF Bumper bracket L','RK Pivot hanger plate front'),
('LM Mast foot plate L','FR Mast-base cross-member'),('LM Mast upright L','LM Mast foot plate L'),('LM Mast gusset L','LM Mast upright L'),('LM Mast gusset L','FR Mast-base cross-member'),
('LA Actuator base bracket','FR Mast-base cross-member'),('LM Rail backing flat L','LM Mast upright L'),('LM Linear rail L','LM Rail backing flat L'),
('LM Lift hard stop L','LM Linear rail L'),('SW Lift top limit','LM Mast upright L'),('SW Lift top limit','LM Linear rail L'),('LM Mast top tie','LM Mast upright L'),
('RK Castor cross-beam pivot housing','RK Castor cross-beam 50'),('DK Dock charge contact L','SF Bumper bracket L'),('SN Sensor post','FR Nose cross-member'),('LT Headlight L','FR Nose cross-member')]
for a,b in pairs:
    A=f(a); B=f(b)
    if not A or not B: print('missing',a,b,A,B); continue
    sa=nb[A[0]]; sb=nb[B[0]]
    print('%-40s %-34s dist %.1f mm  overlap %.0f mm3'%(a,b,dist(sa,sb),vol(common(sa,sb))))
# contact face area for bracket vs cross-member: grow bracket by 0.5mm in z
