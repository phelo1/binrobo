#!/usr/bin/env python3
"""BinRobo B2-F = B2 turned round to dock on the bin FRONT wall (EN 840 frontal receiver). Copy of work/revB2/cad_B2.py:
robot unchanged except the pad set-back (GEO pad_in 0.015 from simB2h B2_DOCK=front, via rec_B2F.json); bin = corrected hull (h2/hull_h2.py) in the
front-dock (mirrored) bin frame; poses from rec_B2F.npz (simB2h, B2_DOCK=front, ESE 240 SL 110 kg). usage: cad_B2F.py [nomesh] [nostep|step1|step2]
Original B2 header follows.
BinRobo B2 (comb-lift carrier, B1 + Rev H learnings) CAD, CadQuery 2.8, mm.
Dimensions from docs/reviews/DESIGN_B2.md and the MJCF in revG/sim/cg/b2/simB2.py (GEO, CORNERS) + b2/mass_cgB2.json.
Frames (as the sim): tug frame origin on the ground under the drive-axle centre, +x toward the castors (front), z up.
Parts are built in the frame of the sim body that carries them, so the same meshes are posed from the sim trajectory:
  tug, wheel (instanced L/R), cfork, cwheel, lift (origin = tooth-plate top at the comb face plate), keeper (hinge axis),
  padbase (pad retract slide), pad (sprung pad), bin (bin wheel-axle centre), bw (bin wheel), lid (lid hinge).
ASSUMED packaging (not in the spec) is tagged [A#] and listed in assumptions_B1.md.
Outputs: B2_parts.pkl, BinRobo_B2_no_bin.step, BinRobo_B2_carrying_240L.step."""
import os, sys, json, math, pickle, numpy as np
import cadquery as cq
HERE=os.path.dirname(os.path.abspath(__file__))
M=json.load(open(os.path.join(HERE,'rec_B2F.json'))); G=M['geo']; PB=M['p']; FR=M['frames']
COL=dict(steel=(0.49,0.54,0.59),panel=(0.91,0.93,0.94),dark=(0.23,0.27,0.32),nib=(0.94,0.49,0.10),keeper=(0.95,0.76,0.19),
         pad=(0.15,0.17,0.19),act=(0.74,0.76,0.79),switch=(0.84,0.22,0.18),sensor=(0.12,0.14,0.16),lens=(0.25,0.55,0.95),beacon=(1.0,0.70,0.10),
         rubber=(0.17,0.17,0.18),stripe=(0.98,0.80,0.10),battery=(0.18,0.42,0.87),ballast=(0.45,0.38,0.33),uhmw=(0.96,0.96,0.92),
         tyre=(0.12,0.13,0.15),hub=(0.66,0.69,0.72),binb=(0.24,0.52,0.34),lid=(0.18,0.42,0.28),binlip=(0.36,0.66,0.45),bar=(0.12,0.30,0.19),rail=(0.80,0.82,0.85),green=(0.09,0.70,0.39),copper=(0.80,0.50,0.25))
PARTS=[]   # (name, group, colour, solid, render)
def add(name,grp,col,w,render=True): PARTS.append((name,grp,col,w.val() if isinstance(w,cq.Workplane) else w,render))
def box(x0,x1,y0,y1,z0,z1):
    x0,x1=sorted((x0,x1)); y0,y1=sorted((y0,y1)); z0,z1=sorted((z0,z1)); return cq.Workplane().box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def cylx(x0,x1,y,z,r): return cq.Workplane('YZ').circle(r).extrude(x1-x0).translate((x0,y,z))
def cyly(y0,y1,x,z,r):
    y0,y1=sorted((y0,y1)); return cq.Workplane('XZ').circle(r).extrude(-(y1-y0)).translate((x,y0,z))
def cylz(z0,z1,x,y,r): return cq.Workplane('XY').circle(r).extrude(z1-z0).translate((x,y,z0))
mm=lambda v:v*1000.0
# ---------------- tug (chassis-fixed) ----------------
TRK=mm(G['track']); RW=mm(G['rw'])
# [B2] one tube size 50x50x2 RHS, bolted through laser plates
for s,n in ((1,'L'),(-1,'R')):
    add('FR Side rail %s 50x50x2 RHS'%n,'tug','steel',box(-370,980,s*405,s*455,360,410).faces('<X or >X').shell(-2))
    add('FR Drive/motor plate %s 6 mm (laser)'%n,'tug','steel',box(-100,100,s*444,s*450,120,410))
    add('DR Gearmotor %s PEWM82M-320W on the rail + 3.5:1 chain'%n,'tug','dark',cylx(-210,-60,s*420,452,40))
    add('DR Chain case %s'%n,'tug','dark',box(-40,40,s*450,s*465,140,452))
    add('DR Axle stub %s'%n,'tug','steel',cyly(s*368,s*444,0,165,15))
    add('FR Rail drop plate %s (to the nose cross-member)'%n,'tug','steel',box(930,980,s*405,s*411,240,410))
    gy=mm(G['guard_y']); add('GU UHMW guard %s'%n,'tug','uhmw',box(-300,380,s*gy,s*(gy+10),60,360))
    fl=box(-40,40,-5,5,60,360).rotate((0,0,0),(0,0,1),s*30).translate((-335,s*(gy+5+20),0)); add('GU Mouth flare %s'%n,'tug','uhmw',fl)
    add('SN Leg-tip gap sensor %s (ToF, potted)'%n,'tug','sensor',box(-380,-360,s*(gy+30),s*(gy+50),200,230))
    add('AT Anti-tip bracket %s'%n,'tug','steel',box(-345,-315,s*420-12,s*420+12,90,360))
    add('AT Anti-tip roller %s D80 (y 420)'%n,'tug','rubber',cyly(s*420-25,s*420+25,-330,90,40))
    add('SF Rear bumper %s (foam + switch)'%n,'tug','rubber',box(-395,-370,s*430-35,s*430+35,330,440))
    add('SF Rear bumper stripe %s'%n,'tug','stripe',box(-397,-394,s*430-35,s*430+35,375,395))
    add('FR Castor plate %s 8 mm (laser)'%n,'tug','steel',box(870,1030,s*280-80,s*280+80,235,243))
add('FR Nose cross-member 50x50x2','tug','steel',box(930,980,-405,405,243,293).faces('<Y or >Y').shell(-2))
add('FR Mast-base cross-member 50x50x2','tug','steel',box(465,515,-405,405,360,410).faces('<Y or >Y').shell(-2))
for s,n in ((1,'L'),(-1,'R')):
    add('LM Mast upright %s 50x50x2'%n,'tug','steel',box(470,520,s*200-25,s*200+25,410,1310))
    add('LM Linear rail %s HGR15 1 m'%n,'tug','rail',box(452,470,s*200-10,s*200+10,300,1300))
    add('LM Mast gusset %s (laser)'%n,'tug','steel',box(520,600,s*200-3,s*200+3,410,490))
add('LM Mast top tie 50x50x2','tug','steel',box(470,520,-230,230,1310,1360))
add('SN Rear camera (lip height, bin tilt)','tug','sensor',box(410,460,-35,35,1360,1395))
add('SN Rear camera lens','tug','lens',cylx(404,410,0,1378,12))
add('SF Amber beacon','tug','beacon',cylz(1360,1418,495,150,32).union(cq.Workplane().sphere(32).translate((495,150,1418))))
add('LA Lift actuator QC FDI 24 V 4 kN (400 mm unit, 250 mm used)','tug','act',cylz(410,1000,500,0,34))
add('LA Lift actuator motor','tug','act',box(520,610,-40,40,440,530))
# battery/electronics bay: 10 mm HDPE floor + 6 mm covers (front cover hidden in renders)
add('BY HDPE bay floor 10 mm','tug','panel',box(500,980,-380,380,120,130))
add('BY HDPE side walls','tug','panel',box(500,930,-386,-380,130,300).union(box(500,930,380,386,130,300)))
add('BY HDPE rear cover (fixed)','tug','panel',box(520,720,-386,386,300,306))
add('BY HDPE front cover (removable, hidden in renders)','tug','panel',box(720,980,-386,386,300,306),render=False)
add('PW Battery 24 V 20 Ah LiFePO4 + BMS (front bay)','tug','battery',box(780,960,-90,90,130,280))
add('BL Ballast plate 5 kg on the bay floor at x 1.00','tug','ballast',box(930,1050,-170,170,130,145))
add('EL Electronics pod','tug','dark',box(560,720,-120,120,130,290))
add('SF E-stop button','tug','switch',cylz(306,335,640,-300,22))
# chamfered bumper (front strip +/-330, 45 deg corners to x 1000 / y 420) + dock contacts
add('SF Front bumper (switch strip)','tug','rubber',box(1050,1090,-330,330,130,230))
for s in (1,-1):
    c=box(0,40,-60,60,130,230).rotate((0,0,0),(0,0,1),s*45).translate((1035,s*375,0)); add('SF Bumper corner %s 45 deg'%('L' if s>0 else 'R'),'tug','rubber',c)
add('SF Front bumper stripe','tug','stripe',box(1089,1092,-330,330,170,190))
for s in (1,-1): add('DK Dock charge contact %s'%('L' if s>0 else 'R'),'tug','copper',box(1090,1096,s*120-30,s*120+30,140,160))
add('SN Sensor post D40','tug','steel',cylz(306,1060,1000,0,20))
add('SN Front camera','tug','sensor',box(1015,1060,-40,40,700,750)); add('SN Front camera lens','tug','lens',cylx(1060,1066,0,725,13))
add('SN Lidar bracket','tug','steel',box(1015,1035,-15,15,800,830)); add('SN 2D lidar','tug','sensor',cylz(830,905,1035,0,50)); add('SN Lidar window','tug','lens',cylz(845,885,1035,0,51))
add('SN GNSS antenna','tug','panel',cylz(1060,1078,1000,0,45).union(cylz(1078,1090,1000,0,30)))
# ---------------- wheels ----------------
add('DR Drive wheel 330 mm (tyre)','wheel','tyre',cyly(-35,35,0,0,RW).cut(cyly(-40,40,0,0,RW-45)))
add('DR Drive wheel hub','wheel','hub',cyly(-30,30,0,0,RW-45).cut(cyly(-40,40,0,0,30)).union(cyly(-36,36,0,0,30)))
add('CA Castor fork 200 mm','cfork','steel',box(-90,10,-40,-30,-15,150).union(box(-90,10,30,40,-15,150)).union(box(-90,10,-40,40,140,150)).union(cylz(150,160,0,0,40)))
add('CA Castor wheel 200 mm','cwheel','tyre',cyly(-25,25,0,0,100).cut(cyly(-30,30,0,0,65)))
add('CA Castor hub','cwheel','hub',cyly(-22,22,0,0,65).union(cyly(-35,35,0,0,10)))
# ---------------- lift carriage (origin = tooth-plate top at the face plate) ----------------
Lt=mm(G['tooth_len']); nl=mm(G['nib_l']); nh=mm(G['nib_h']); hw=mm(G['tooth_hw']); cx0=-Lt+nl
add('LC Comb face plate (sprung, 10 mm)','lift','dark',box(0,10,-200,200,-50,150))
add('LC Carriage plate','lift','dark',box(10,40,-230,230,-30,165))
for s in (1,-1):
    for z0 in (-25,95): add('LC Rail carriage','lift','rail',box(40,52,s*200-22,s*200+22,z0,z0+60))
add('LC Actuator bracket','lift','dark',box(40,100,-45,45,120,150))
add('LA Lift actuator rod D30','lift','act',cylz(-300,135,85,0,15))
add('LC Comb pivot block (yaw +/-4, roll +/-3, centring springs)','lift','steel',box(cx0+10,-2,-50,50,-30,-10))
add('SW Comb contact switch (roller lever, 30 N)','lift','switch',box(-22,0,95,135,10,40).union(cyly(100,130,-28,25,7)))
for s in (1,-1): add('SN Comb ToF (gap + yaw) %s'%('L' if s>0 else 'R'),'lift','sensor',box(-12,0,s*180-15,s*180+15,-20,10))
add('KP Keeper hinge shaft','lift','steel',cyly(-150,150,0,100,8)); add('KP Keeper cam motor GR-07','lift','dark',box(-5,60,150,210,70,140))
# comb (own body in the sim: origin at the nib/tooth junction)
add('LC Comb plate 640 mm, 6 mm S355 (self-aligning)','comb','dark',box(0,Lt-nl,-hw,hw,-10,0))
add('LC Nib 8 long x 20 high, 640 mm','comb','nib',box(-nl,0,-hw,hw,-10,nh))
add('SW Nib seat switch (flush)','comb','switch',box(2,18,-20,20,-6,0.0))
# pad arm + toggle-locked pad
pz=nh-mm(G['pad_dz']); pfx=mm(G['face_x']-G['tooth_len'])-4-mm(G['pad_in'])-mm(G['face_x'])
add('PD Pad arm (on the carriage)','lift','dark',box(0,14,-40,40,pz-60,-10).union(box(-30,14,-40,40,-40,-10)))
add('PD Pad guide block','lift','dark',box(pfx+75,14,-120,120,pz-35,pz+35).cut(cylx(pfx,20,-90,pz,9)).cut(cylx(pfx,20,90,pz,9)))
add('PD Toggle actuator TRU TC24-50-1000 (upright on the arm, L 155)','lift','act',cylz(pz+75,pz+250,-25,0,20).union(box(-50,0,-22,22,pz+200,pz+250)))
add('PD Toggle actuator rod','lift','steel',cylz(pz+45,pz+75,-25,0,6))
add('PD Knee toggle: 2 x 60 mm links + over-centre stop','lift','keeper',box(-32,-18,-30,30,pz-5,pz+60).union(box(-60,-18,-12,12,pz-4,pz+4)))
add('SW Pad toggle-lock switch','lift','switch',box(14,34,-120,-95,pz+40,pz+60))
add('PD Pad slide rods + spring cups','padbase','steel',cylx(20,100,-90,0,8).union(cylx(20,100,90,0,8)).union(box(20,30,-130,130,-30,30)))
add('PD Pad UHMW face 300x100','pad','pad',box(0,20,-150,150,-50,50))
add('PD Pad die springs 30 kN/m','pad','act',cylx(20,40,-60,0,14).union(cylx(20,40,60,0,14)))
add('SW Pad contact switch','pad','switch',box(5,22,150,172,-15,15))
kl=mm(G['keep_l'])
add('KP Keeper arm 80 mm (handle keeper: no bar on the front wall, inactive in B2-F)','keeper','keeper',box(-kl+4,0,-120,120,16,24).union(box(-kl-4,-kl+12,-112,-88,-6,24)).union(box(-kl-4,-kl+12,88,112,-6,24)))
add('KP Keeper fingers','keeper','keeper',cyly(75,125,-kl,0,12).union(cyly(-125,-75,-kl,0,12)))
# ---------------- 240 L bin: CORRECTED hull (revG/sim/cg/h2/hull_h2.py, S1), front-dock frame as simB2h B2_DOCK=front ----------------
# bin body frame = sim 'bin' body: origin at the wheel-axle centre, MIRRORED (front wall + EN 840 receiver at +x, handle/hinge/wheels at -x)
sys.path.insert(0,'/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg/h2'); import hull_h2 as HH
HG=M['hull']; X=lambda x:-x
up,lo=HH.meshes(HG)
def quadz(pts,z): # pts list of (x,y,z) at one z -> ordered polygon in mm, mirrored
    P_=[(mm(X(x)),mm(y)) for x,y,zz in pts if abs(zz-z)<1e-9]; c=np.mean(P_,0); P_.sort(key=lambda p:math.atan2(p[1]-c[1],p[0]-c[0])); return [(a,b,mm(z)) for a,b in P_]
def poly(pts): return cq.Wire.makePolygon([cq.Vector(*p) for p in pts],close=True)
hu=cq.Solid.makeLoft([poly(quadz(up,HG['zrt'])),poly(quadz(up,HG['zt']))],True)
hl=cq.Solid.makeLoft([poly(quadz(lo,HG['zb'])),poly(quadz(lo,HG['zrt']))],True)
add('BIN 240 L body, corrected hull (front taper 35 mm, rear draft 30 mm + wheel recess)','bin','binb',cq.Workplane().add(hu).union(cq.Workplane().add(hl)))
bh=mm(HG['bh']); bx=mm(HG['bx']); r=mm(HG['r']); xbt=mm(HG['xb']); xf=mm(HG['xf']); hwb=mm(HG['hw']); wr=mm(HG['wr']); hh=mm(PB['handle_half'])
add('BIN Handle bar D27 (rear)','bin','bar',cyly(-hh-20,hh+20,X(bx),bh,r))
wx0=xbt-10; wx1=bx+10
for s in (1,-1): add('BIN Handle bracket','bin','binb',box(X(wx0),X(wx1),s*(hh+10)-10,s*(hh+10)+10,bh-12-35,bh-12+35))
zR=mm(HG['zL_rear']); add('BIN Plain rim 20 x 8 (handle side, no receiver)','bin','binlip',box(X(xbt),X(xbt+20),-(hwb-30),hwb-30,zR,zR+8))
zF=mm(HG['zL_front']); lw=mm(HG['lw'])
add('BIN EN 840 frontal receiver ledge 30 x 8, 580 mm (front wall)','bin','binlip',box(X(xf),X(xf-30),-lw/2,lw/2,zF,zF+8))
add('BIN EN 840 receiver rim 25 mm down-turn','bin','binlip',box(X(xf-22),X(xf-30),-lw/2,lw/2,zF-25,zF))
add('BIN Axle','bin','hub',cyly(-mm(PB['wy']),mm(PB['wy']),0,0,10))
add('BIN Wheel 200 mm','bw','tyre',cyly(-25,25,0,0,wr).cut(cyly(-30,30,0,0,wr-30)))
add('BIN Wheel hub','bw','hub',cyly(-20,20,0,0,wr-30))
lidx=xbt+5; lhl=(lidx-xf)/2   # lid body at x = -lidx (rear hinge), lid extends +x towards the front wall
add('BIN Lid (hinge at the rear)','lid','lid',box(-15,2*lhl+15,-hwb-8,hwb+8,0,30))
# ---------------- meshes for the renderer ----------------
def mesh(w,tol=0.6,ang=0.12):
    v,t=w.tessellate(tol,ang); return np.array([[p.x,p.y,p.z] for p in v],np.float32)/1000.0,np.array(t,np.int32)
if 'nomesh' not in sys.argv:
    out=[]
    for n,g,c,w,rd in PARTS:
        V,T=mesh(w); out.append(dict(name=n,grp=g,col=COL[c],V=V,T=T,render=rd))
    pickle.dump(out,open(os.path.join(HERE,'B2F_parts.pkl'),'wb')); print('mesh parts',len(out),'tris',sum(len(o['T']) for o in out),flush=True)
# ---------------- STEP assemblies ----------------
def qmat(q):
    w,x,y,z=q; return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def poses(frame):
    d=np.load(os.path.join(HERE,'rec_B2F.npz')); q=d['q'][frame]; B=M['bodies']; Rt=qmat(q[0,3:]); pt=q[0,:3]; P={}
    for k,n in enumerate(B):
        R=Rt.T@qmat(q[k,3:]); p=Rt.T@(q[k,:3]-pt); P[n]=(R,p*1000)
    return P
def loc(R,p):
    from OCP.gp import gp_Trsf
    T=gp_Trsf(); v=[float(x) for x in (R[0,0],R[0,1],R[0,2],p[0],R[1,0],R[1,1],R[1,2],p[1],R[2,0],R[2,1],R[2,2],p[2])]; T.SetValues(*v); return cq.Location(T)
INST={'wheel':['wheelL','wheelR'],'cfork':['cforkL','cforkR'],'cwheel':['cwheelL','cwheelR'],'bw':['bwL','bwR']}
def assembly(frame,with_bin,name):
    P=poses(frame); asm=cq.Assembly(name=name); used={}
    for n,g,c,w,rd in PARTS:
        if g in('bin','bw','lid') and not with_bin: continue
        for b in INST.get(g,[g]):
            R,p=P[b]; nm=n+('' if b==g else ' '+b[-1]); k=used.get(nm,0); used[nm]=k+1; nm=nm if k==0 else '%s #%d'%(nm,k+1)
            asm.add(w,name=nm.replace('/','-'),loc=loc(R,p),color=cq.Color(*COL[c]))
    return asm
if 'nostep' not in sys.argv:
    if 'step2' not in sys.argv: a=assembly(FR['start'],False,'BinRobo_B2F'); a.save(os.path.join(HERE,'BinRobo_B2F_no_bin.step')); print('step1 done',flush=True)
    if 'step1' not in sys.argv: a2=assembly(FR['carrying'],True,'BinRobo_B2F_carrying_240L'); a2.save(os.path.join(HERE,'BinRobo_B2F_carrying_240L.step'))
    json.dump(dict(parts=[p[0] for p in PARTS],n=len(PARTS),frames=FR),open(os.path.join(HERE,'cad_B2F_parts.json'),'w'),indent=1); print('step done',flush=True)
