#!/usr/bin/env python3
"""G6 task 1: 2D design check of the GH hook throat + pawl (hook frame, mm: origin = cup centre, +x towards the tug, +z up the mast).
For each candidate: (a) does the pawl close over every bar section seated on the floor (+ ice 0/2/5 mm) anywhere across the throat,
(b) minimum closing clearance, (c) retention: the escape gap between the closed pawl and the lip / back wall must be < the smallest
bar (D25) with margin, (d) where a bar of each size ends up after the 0.6 deg ease-off (vane trigger at x=+20 minus ~8 mm).
Pure geometry (no dynamics) - the MuJoCo matrix is the real test.  usage: python3 hook_design_g6.py -> hook_design_g6.json"""
import math, json, os
import geo_g3 as GG
HERE=os.path.dirname(os.path.abspath(__file__))
def corners(cx,cz,hx,hz,ang):
    a=math.radians(ang); ux=(math.cos(a),-math.sin(a)); uz=(math.sin(a),math.cos(a))
    return [(cx+sx*hx*ux[0]+sz*hz*uz[0], cz+sx*hx*ux[1]+sz*hz*uz[1]) for sx,sz in ((-1,-1),(1,-1),(1,1),(-1,1))]
def pt_seg(p,a,b):
    ax,az=a; bx,bz=b; px,pz=p; dx,dz=bx-ax,bz-az; L=dx*dx+dz*dz
    t=0 if L==0 else max(0,min(1,((px-ax)*dx+(pz-az)*dz)/L)); qx,qz=ax+t*dx,az+t*dz; return math.hypot(px-qx,pz-qz)
def inside(p,poly):
    s=None
    for i in range(4):
        a=poly[i]; b=poly[(i+1)%4]; c=(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
        if s is None: s=c>0
        elif (c>0)!=s: return False
    return True
def poly_dist_pt(poly,p):
    if inside(p,poly): return -1.0
    return min(pt_seg(p,poly[i],poly[(i+1)%4]) for i in range(4))
def poly_poly(P,Q):
    d=min(min(pt_seg(p,Q[i],Q[(i+1)%4]) for i in range(4)) for p in P)
    d=min(d,min(min(pt_seg(q,P[i],P[(i+1)%4]) for i in range(4)) for q in Q))
    if any(inside(p,Q) for p in P) or any(inside(q,P) for q in Q): return -1.0
    return d
def bar_shape(sh,r,cx,cz):
    """tube = circle (returned as ('c',cx,cz,r)); moulded = box 0.8r x r (half sizes) as in sim_g5"""
    return ('c',cx,cz,r) if sh=='tube' else ('b',corners(cx,cz,0.8*r,r,0.0))
def clear(geom,bar):
    if bar[0]=='c': return poly_dist_pt(geom,(bar[1],bar[2]))-bar[3]
    return poly_poly(geom,bar[1])
def rot(poly,P,deg):
    """pawl rotation about pivot P; POSITIVE = open (tip lifts towards the bin, i.e. towards -x then up) = sim joint sign:
    joint axis +y in MuJoCo => positive angle maps x->z... we take the sim convention: positive opening lifts the tip."""
    a=math.radians(deg); c,s=math.cos(a),math.sin(a); out=[]
    for x,z in poly:
        dx,dz=x-P[0],z-P[1]
        # MuJoCo hinge about +y: (x,z) -> (x cos + z sin, -x sin + z cos)
        out.append((P[0]+dx*c+dz*s, P[1]-dx*s+dz*c))
    return out
def pawl_polys(PW):
    """pawl geoms in the hook frame at the closed stop"""
    P=PW['P']; out=[]
    for g in GG.gh_pawl_geoms_v(PW):
        n,cx,cz,hx,hz,ang=g
        out.append(corners(P[0]+cx,P[1]+cz,hx,hz,ang))
    return out
def cup_polys(V):
    return [corners(cx,cz,hx,hz,ang) for (n,cx,cz,hx,hz,ang,y0,y1) in GG.gh_cup(V['hy'],variant='B',lip_chamfer=V.get('lip_chamfer',False),V=V) if (y0+y1)>0]
SECS=[('tube',12.5),('tube',13.5),('tube',15.0),('tube',21.0),('moulded',19.0),('moulded',21.0)]
def analyse(V,label):
    PW=GG.pawl_params(V); cup=cup_polys(V); pw=pawl_polys(PW)
    x_lo=V.get('throat',-24.0); x_hi=24.0; floor=-26.0
    res=dict(label=label,throat_mm=x_hi-x_lo,pawl=PW,cases=[])
    worst=dict(clear=1e9)
    for sh,r in SECS:
        hx=0.8*r if sh=='moulded' else r
        for ice in (0.0,2.0,5.0):
            cz=floor+ice+r
            xs=[x_lo+hx+0.5+k*(x_hi-x_lo-2*hx-1)/10 for k in range(11)] if x_hi-x_lo>2*hx+1 else [(x_lo+x_hi)/2]
            for cx in xs:
                bar=bar_shape(sh,r,cx,cz)
                c0=min(clear(p,bar) for p in pw)
                blocked=0.0
                for k in range(0,131):
                    if min(clear(p,bar) for p in [rot(q,PW["P"],k) for q in pw]) < 0: blocked=k
                closes=(c0>0.3 and blocked==0)
                res['cases'].append(dict(sec=f'{sh} D{2*r:.0f}',ice=ice,x=round(cx,1),clear_mm=round(c0,1),closes=bool(closes),stops_open_deg=blocked))
                if c0<worst['clear']: worst=dict(clear=round(c0,1),sec=f'{sh} D{2*r:.0f}',ice=ice,x=round(cx,1))
    res['worst_closing']=worst
    res['all_close_ice0']=all(c['closes'] for c in res['cases'] if c['ice']==0)
    res['all_close_ice2']=all(c['closes'] for c in res['cases'] if c['ice']==2)
    res['all_close_ice5']=all(c['closes'] for c in res['cases'] if c['ice']==5)
    band=lambda c: -13.0<=c['x']<=4.0          # realistic bar-centre band after the 0.6 deg ease-off (vane at x=+20, ~8 mm ease, +/-4 mm)
    res['band_close_ice5']=all(c['closes'] for c in res['cases'] if c['ice']==5 and band(c))
    res['band_close_ice2']=all(c['closes'] for c in res['cases'] if c['ice']==2 and band(c))
    res['band_min_clear_ice5']=min(c['clear_mm'] for c in res['cases'] if c['ice']==5 and band(c))
    res['fail_ice5']=[c for c in res['cases'] if c['ice']==5 and not c['closes']][:6]
    # retention: largest circle that fits between closed pawl and the lip / back wall = escape gap
    gap=min(poly_poly(p,q) for p in pw for q in cup if True)
    lip=[q for q,(n,*_) in zip(cup,[g for g in GG.gh_cup(V['hy'],variant='B',lip_chamfer=V.get('lip_chamfer',False),V=V) if (g[6]+g[7])>0]) if n.startswith('GH lip')]
    res['escape_gap_lip_mm']=round(min(poly_poly(p,q) for p in pw for q in lip),1)
    # D42 position after the 0.6 deg ease-off: vane trigger puts the bar back face at x=+20, ease moves the hook ~8 mm (0.6 deg x 0.75 m)
    lipall=[c for q in lip for c in q]
    res['lip_outer_x']=round(min(x for x,z in lipall),1); res['lip_top_z']=round(max(z for x,z in lipall),1)
    res['lip_outer_x_above_m13']=round(min([x for x,z in lipall if z>-13] or [0]),1)
    res['D42_after_ease']=dict(centre_x=20-21-8,left_edge=20-21-8-21,lip_inner=x_lo,perch=bool(20-21-8-21<x_lo))
    return res
if __name__=='__main__':
    out=[]
    import sys
    CANDS=[('GH-B5F-130 (baseline)',dict()),
           ('V1 T34 lip0 beak24 (first smoke, lip too proud)',dict(throat=-34.0,lip_w=8.0,lip_top=0.0,pawl=dict(knee=(-16.0,34.0),tip=(-33.0,24.0)))),
           ('V11 T34 w6 lip-2 beak19',dict(throat=-34.0,lip_w=6.0,lip_top=-2.0,pawl=dict(knee=(-18.0,35.0),tip=(-33.0,19.0)))),
           ('H2 = V11 with 8 mm lip (GH-B6 pick candidate)',dict(throat=-34.0,lip_w=8.0,lip_top=-2.0,pawl=dict(knee=(-18.0,35.0),tip=(-33.0,19.0)))),
           ]
    for lab,ov in CANDS:
        V=dict(GG.GH['B2']); V.update(hy=130.0,lip_chamfer=True,ease=0.6); V.update(ov)
        r=analyse(V,lab); out.append(r)
        print(lab,'| throat',r['throat_mm'],'| close ice0/2/5',r['all_close_ice0'],r['all_close_ice2'],r['all_close_ice5'],'| worst',r['worst_closing'],
              '| escape gap',r['escape_gap_lip_mm'],'| band ice2/5',r['band_close_ice2'],r['band_close_ice5'],r['band_min_clear_ice5'],'| lip outer x',r['lip_outer_x'],'above-13',r['lip_outer_x_above_m13'],'lip top z',r['lip_top_z'])
        for c in r['fail_ice5'][:3]: print('    ice5 fail',c)
    json.dump(out,open(os.path.join(HERE,'hook_design_g6.json'),'w'),indent=1)
