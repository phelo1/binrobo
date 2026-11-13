# Rev G and Rev F.1 grabber (hook) geometry, shared by the CAD model (model_revG.py) and the MuJoCo model (sim_revG.py).
# Hook frame (mm): origin = cup centre; +x = towards the tug (mast-normal), +z = up along the mast; y = across the bin.
# Every piece is a box: (piece_id, cx, cz, hx, hz, ang_deg, y0, y1). ang = rotation about +y (MuJoCo/CadQuery convention:
# local x maps to (cos a, -sin a) in (x,z)). Pieces are the contact surfaces; CAD part IDs are given per piece.
import math
def seg(A,B,t,side=+1):
    """box along segment A->B (x,z) with thickness t on the left (side=+1) or right (side=-1) of the direction"""
    dx,dz=B[0]-A[0],B[1]-A[1]; L=math.hypot(dx,dz); ux,uz=dx/L,dz/L; nx,nz=-uz,ux   # left normal
    cx=(A[0]+B[0])/2+side*nx*t/2; cz=(A[1]+B[1])/2+side*nz*t/2
    return cx,cz,L/2,t/2,math.degrees(math.atan2(-dz,dx))
def ab(x0,x1,z0,z1): return ((x0+x1)/2,(z0+z1)/2,abs(x1-x0)/2,abs(z1-z0)/2,0.0)

# ---------------- Rev G "cradle hook": one wide hook, cup opens up, fixed lip on the bin side carries the tipping pull,
# cup floor carries the tow load, self-locking sliding tongue closes the cup top, long upper flare guides high bars down
# and doubles as a lid stop; counterbalanced float carriage (net +10 N up) so the hook rises to seat the bar.
G_W=125.0                       # half width of the cradle (contact length 250 mm)
# Approach from BELOW: the release cam pulls the hook to the bottom of its float (tongue retracted), the mast swings the lip under
# the bar into the hand gap, a vane switch says "bar over the cup", the cam lets the counterbalanced hook rise until the cup floor
# meets the bar (a ratchet on the mast rail lets it rise but not fall), then the tongue springs out over the bar.
G_PIECES=[
 ('GR-04 floor',)+ab(-28,30,-34,-24)+(-G_W,G_W),
 ('GR-04 back wall',)+ab(26,38,-34,20)+(-G_W,G_W),
 ('GR-05 lip',)+ab(-40,-28,-34,8)+(-G_W,G_W),
 ('GR-07 tongue guide',)+ab(32,68,30,46)+(-G_W,G_W),
 ('GR-03 cheek L lip',)+ab(-42,-28,-40,8)+(G_W,G_W+8),
 ('GR-03 cheek L floor',)+ab(-28,26,-40,-24)+(G_W,G_W+8),
 ('GR-03 cheek L rear',)+ab(26,68,-40,48)+(G_W,G_W+8),
 ('GR-03 cheek R lip',)+ab(-42,-28,-40,8)+(-G_W-8,-G_W),
 ('GR-03 cheek R floor',)+ab(-28,26,-40,-24)+(-G_W-8,-G_W),
 ('GR-03 cheek R rear',)+ab(26,68,-40,48)+(-G_W-8,-G_W),
]
G_TONGUE=dict(x0=-24,x1=44,z0=20,z1=28,y=115,retract=64,k=150.0,pre=6.0)   # extended tip at x=-22; spring N/m, preload N
# lid finger: U-shaped 6 mm spring-wire finger hinged on the cradle above the tongue guide (hook frame, mm); a torsion spring presses it
# onto the lid (it rides on the lid whatever the bin height); the release cam cord lifts it clear during approach/release.
G_LIDFINGER=dict(pivot=(40,72),length=270,down_deg=28,y=(-100,100),k=1.0,pre=2.5,lift_rad=2.4)
G_FLOAT=dict(ref=0.730,down=0.075,up=0.120,net_up=12.0,pitch=0.008,pull=80.0)  # float about s=0.73 (nominal bar), ratchet pitch 8 mm
G_MOUNT=dict(k=120e3,c=1500.0,travel=0.010)                                # elastomer cradle mount: N/m, N s/m, +/- m (x and z)
G_VANE=dict(xback=16.0,zmin=-30.0,zmax=175.0)   # 'bar over cup' vane: sprung vane 4 mm proud of the back wall, closes when the bar's back face reaches x=+20 (hook frame, mm)
# ---------------- Rev F.1 hook "as drawn" (model_revF.HOOK_F, two 28 mm hooks at y = +/-198), for the like-for-like comparison
F_PIECES=[]
for sg in (1,-1):
    y0,y1=sorted((sg*184,sg*212))
    F_PIECES+= [('F floor',)+ab(-17,17,-26,-16)+(y0,y1),
               ('F back',)+ab(17,60,-75,30)+(y0,y1),
               ('F lower',)+ab(-17,60,-75,-26)+(y0,y1),
               ('F lip',)+ab(-25,-17,-30,10)+(y0,y1),
               ('F lip ramp',)+seg((-34,-8),(-17,10),8,-1)+(y0,y1),
               ('F lip low',)+ab(-34,-17,-30,-8)+(y0,y1)]
F_TONGUE=dict(x0=-14,x1=40,z0=18,z1=28,y=(186,210),retract=35,k=200.0,pre=8.0)
F_FLOAT=dict(rest=0.730,down=0.210,up=0.0,k=200.0,springref=0.3)          # F.1: carriage pressed to its top stop by ~60 N
F_MOUNT=dict(k=2.0e6,c=4000.0,travel=0.0015)                              # F.1 rubber bush (stiff)

# =====================================================================================================================
# G3: Rev 2.2 "G-hook" = TWIN single-plate hooks (10 mm), upward-opening cup, gravity(+torsion-spring) latch pawl per hook
# whose bar-facing face is an ARC CONCENTRIC WITH ITS PIVOT (a bar pushing on it makes no opening moment), float carriage,
# cam release. Hook frame as above (mm): origin = cup centre, +x towards the tug at mast upright, +z up the mast.
# Variants (dict GH[...]):
#   'A'  = Rev 2.2 as literally specified: passive snap-over. Float spring-balanced, centred (500 N/m) so the lip chamfer
#          meets a nominal (1.03 m) bar; 45 deg chamfer on the lip top + the 120 mm entry ramp on the lip's outer face. The ramp
#          must fit in the EN 840 hand gap (35-60 mm bar-to-body), so it can only lean 10 mm over 120 mm (~5 deg from
#          vertical). Pawl has a leading chamfer so the bar can push it open. Release = cam lifts pawls at upright, mast forward.
#   'B1' = iteration 1: approach from BELOW. Cam 'open' = pawls lifted + float pulled to its bottom stop; mast swings until
#          the back-wall seat vane closes; cam 'rise' = float released (net +12 N up, one-way ratchet) until the cup floor
#          meets the bar; cam 'closed' = pawls drop. Release = cam 'open' (pawls up, ratchet lifted, cord pulls the hook down
#          under the bar = drop-away), mast forward. Float +/-60 mm, hooks at +/-190 mm (as specified).
#   'B2' = iteration 2: B1 + float -100/+130 mm (230 mm: 0.95-1.10 m bars PLUS the ~80 mm the hook drops when the mast swings back 12-15 deg) + hooks moved in to +/-150 mm (fits
#          120-140 L handles, 340-420 mm between webs).
#   'B3' = iteration 3: B2 + lip top sloped 45 deg into the cup + mast ease-off 0.6 deg (instead of 1.0) before the rise.
def gh_cup(hy, t=10.0, variant='B1', lip_chamfer=False, V=None):
    """G6: V['throat'] = x of the lip inner face (default -24 = GH-B2..B5F-130, 48 mm throat); V['lip_w'] lip width (default 12)"""
    V=V or {}; th=float(V.get('throat',-24.0)); lw=float(V.get('lip_w',12.0)); sh=th+24.0
    out=[]
    for sg in (1,-1):
        y0,y1=sorted((sg*(hy-t/2),sg*(hy+t/2)))
        out+=[('GH floor',)+ab(th,24,-36,-26)+(y0,y1),
              ('GH back wall',)+ab(24,36,-36,260)+(y0,y1),
              (('GH lip',)+ab(th-lw,th,-36,float(V.get('lip_top',-10.0)) if sh==0 and 'lip_top' not in V else float(V['lip_top'])-min(lw-1.0,6.0)*0.0)+(y0,y1)) if lip_chamfer else (('GH lip',)+ab(th-lw,th,-36,0)+(y0,y1)),
              ('GH web',)+ab(36,96,-46,24)+(y0,y1),
              ('GH lower',)+ab(th-lw,36,-56,-36)+(y0,y1)]
        if lip_chamfer:   # B3: lip top sloped 45 deg INTO the cup, so a bar landing on the lip edge slides into the cup as the hook rises
            if sh==0 and 'lip_top' not in V: out+=[('GH lip slope',)+seg((-38,2),(-23,-13),10,-1)+(y0,y1)]
            else:
                lt=float(V.get('lip_top',-12.0)); c=min(lw-1.0,6.0)   # G6: 45 deg chamfer of size c on the lip's inner top corner, kept inside the lip outline
                out+=[('GH lip slope',)+seg((th-c,lt),(th,lt-c),c*0.7,-1)+(y0,y1)]
        if variant=='A':
            out+=[('GH lip chamfer',)+seg((-46,-14),(-30,2),8,-1)+(y0,y1),
                  ('GH entry ramp',)+seg((-46,-120),(-40,-14),8,-1)+(y0,y1),
                  ('GH ramp foot',)+ab(-46,-36,-120,-56)+(y0,y1)]
    return out
GH_PAWL=dict(P=(40.0,52.0),tip=(-22.0,14.0),t=8.0,w=8.0,yoff=-13.0,open_deg=130.0,mass=0.10,k=0.20,pre=0.25)
# Pawl: 6-8 mm laser-cut plate beside each hook plate (inboard), pivot on the tall back wall at P, blade reaching over the cup
# to just above the lip. Joint: 0 = closed stop, POSITIVE = open (tip lifts towards the bin, then swings up and back over the
# pivot, out of the bar's path at 130 deg). Gravity closes it at every mast angle (CG stays bin-side of the pivot); a torsion
# spring (0.25 N m preload) holds it against shocks. NOTE: the pawl is NOT self-locking against an upward bar push (the
# same rotation opens it for release); with the bin on its wheels the bar cannot leave the cup anyway (lip + tall back wall +
# float ratchet); the pawl only matters if the bin lifts off its wheels. Bounce-open is measured in the tow sims.
def pawl_params(V=None):
    """G6: V['pawl'] may override tip / add a knee (cranked 'beak' blade): dict(tip=(x,z), knee=(x,z), P=(x,z))"""
    P=dict(GH_PAWL); P.update((V or {}).get('pawl',{}) or {}); return P
def gh_pawl_geoms_v(P):
    """underside of the blade on the line pivot->(knee->)tip, plate thickness t above it; offsets relative to the pivot"""
    px,pz=P['P']; pts=[(0.0,0.0)]
    if P.get('knee'): pts.append((P['knee'][0]-px,P['knee'][1]-pz))
    pts.append((P['tip'][0]-px,P['tip'][1]-pz))
    out=[('pawl blade%d'%i,)+seg(pts[i],pts[i+1],P['t'],-1) for i in range(len(pts)-1)]
    if P.get('knee'): out.append(('pawl knee',)+ab(pts[1][0]-P['t']/2,pts[1][0]+P['t']/2,pts[1][1],pts[1][1]+P['t']))
    out.append(('pawl boss',)+ab(-7,7,-7,7)); return out
def gh_pawl_geoms(variant, P=None):
    return gh_pawl_geoms_v(P or GH_PAWL)
def gh_pawl_cg(P=None):
    P=P or GH_PAWL; px,pz=P['P']; pts=[(0.0,0.0)]
    if P.get('knee'): pts.append((P['knee'][0]-px,P['knee'][1]-pz))
    pts.append((P['tip'][0]-px,P['tip'][1]-pz))
    L=[math.hypot(pts[i+1][0]-pts[i][0],pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1)]
    cx=sum(l*(pts[i][0]+pts[i+1][0])/2 for i,l in enumerate(L))/sum(L); cz=sum(l*(pts[i][1]+pts[i+1][1])/2 for i,l in enumerate(L))/sum(L)
    return (cx*0.9,cz*0.9)
def pawl_length(P=None):
    P=P or GH_PAWL; px,pz=P['P']; pts=[(px,pz)]+([tuple(P['knee'])] if P.get('knee') else [])+[tuple(P['tip'])]
    return sum(math.hypot(pts[i+1][0]-pts[i][0],pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1))
GH={
 'A': dict(hy=190.0,float_down=0.060,float_up=0.060,ref=0.700,mode='passive',rest=0.004,kc=500.0,net_up=0.0,ratchet=False),
 'B1':dict(hy=190.0,float_down=0.060,float_up=0.060,ref=0.700,mode='below',net_up=12.0,pull=80.0,ratchet=True,pitch=0.008),
 'B2':dict(hy=150.0,float_down=0.100,float_up=0.130,ref=0.700,mode='below',net_up=30.0,pull=150.0,ratchet=True,pitch=0.008),
 'B3':dict(hy=150.0,float_down=0.100,float_up=0.130,ref=0.700,mode='below',net_up=30.0,pull=150.0,ratchet=True,pitch=0.008,lip_chamfer=True,ease=0.6),
}
GH_MOUNT=dict(k=1.2e6,c=4000.0,travel=0.002)     # rubber bush between carriage and hook crossbar (x,z)
GH_LAT=dict(k=600.0,c=60.0,travel=0.040,friction=6.0)   # lateral float +/-40 mm on UHMW pads, light centring springs
GH_VANE=dict(xback=20.0,zmin=-40.0,zmax=260.0)    # back-wall seat vane: closes when the bar's tug-side face reaches x=+20
