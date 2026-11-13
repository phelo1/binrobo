# Rev F "hand-truck" bin tug: tug + yaw-free rear frame (turntable on drive axle) carrying hinged tilting mast, floating hook carriage,
# wheel-stop crossbeam, docking funnel and anti-tip rollers. Model frame = bin frame (bin axle x=0, z=100).
import cadquery as cq, json, math, sys
def box(x0,x1,y0,y1,z0,z1):
    x0,x1=sorted((x0,x1));y0,y1=sorted((y0,y1));z0,z1=sorted((z0,z1))
    return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def cyl(axis,c,r,h):
    w=cq.Workplane("XY").cylinder(h,r)
    if axis=='y': w=w.rotate((0,0,0),(1,0,0),90)
    if axis=='x': w=w.rotate((0,0,0),(0,1,0),90)
    return w.translate(c)
def seg(p,q,r):  # round bar between two XZ points at y given in p/q (3D)
    import numpy as np
    p=np.array(p,float);q=np.array(q,float);L=float(np.linalg.norm(q-p));d=(q-p)/L
    w=cq.Workplane("XY").cylinder(L,r)  # along z
    ax=np.cross([0,0,1],d);s=np.linalg.norm(ax)
    if s>1e-9: w=w.rotate((0,0,0),tuple(ax/s),math.degrees(math.atan2(s,d[2])))
    return w.translate(tuple((p+q)/2))
# ---- key geometry (mm). Model frame: bin axle at x=0, z=100 (ground z=0); tug faces +x.
HX,HZ=55.0,930.0          # handle offset from bin axle (bin frame)
TX=670.0                  # tug drive axle (= yaw kingpin) x when docked
PX,PZ=260.0,300.0         # mast hinge pin (on rear frame spine)
KZ=300.0                  # yaw turntable top / rear-frame origin height (at x=TX)
EH=-205.0                 # hook offset from mast axis (toward bin)
S_TOP,S_BOT=730.0,520.0   # carriage float stops (distance along mast from pin)
ACT_BASE=(600.0,340.0); ACT_Y=190.0  # tilt actuator clevis on rear-frame spine (model coords)
ACT_S,ACT_E=900.0,-250.0  # actuator rod-end on mast bracket (mast frame)
HOOK_F=[(-15,-75),(60,-75),(60,30),(80,70),(55,73),(17,30),(17,-16),(-17,-16),(-17,10),(-34,-8),(-34,-30)]
def handle_pos(th):
    t=math.radians(th); return (HX*math.cos(t)+HZ*math.sin(t), -HX*math.sin(t)+HZ*math.cos(t)+100)
def mast_pose(th):
    hx,hz=handle_pos(th); dx,dz=hx-PX,hz-PZ; r=math.hypot(dx,dz); s=math.sqrt(max(r*r-EH*EH,1)); 
    phi=math.degrees(math.atan2(dx,dz)-math.atan2(EH,s)); return phi,s
def mast_pt(s,e,phi):
    c,sn=math.cos(math.radians(phi)),math.sin(math.radians(phi)); return (PX+e*c+s*sn, PZ-e*sn+s*c)
def hook_cheek(): return cq.Workplane("XZ").polyline(HOOK_F).close().extrude(8)
AL=(0.72,0.75,0.78); ST=(0.42,0.44,0.48); BLK=(0.12,0.12,0.13); DG=(0.3,0.3,0.32); GRN=(0.15,0.45,0.25)
PCB=(0.1,0.45,0.25); SEAL=(0.05,0.05,0.05); CON=(0.75,0.6,0.2); NEW=(0.85,0.35,0.1)
def build(theta, with_bin=True, service=False, phi=None, s=None):
    P=[]
    def add(n,w,c,a=1.0,g='tug',mod=''): P.append(dict(name=n,w=w,c=c,a=a,g=g,mod=mod))
    if phi is None: phi,s=mast_pose(theta)
    if s is None: s=S_TOP
    tx=TX
    def T(w): return w.translate((tx,0,0))
    # --- chassis ---
    tray=box(-70,630,-260,260,120,123)
    for b in [box(-70,630,257,260,123,264),box(-70,630,-260,-257,123,264),box(627,630,-257,257,123,264),box(-70,-67,-257,257,123,264)]: tray=tray.union(b)
    for x in (100,300,560):
        for y in (-200,200): tray=tray.cut(cyl('z',(x,y,121.5),6,6))
    add('Chassis tray, bent 3 mm steel, drain holes',T(tray),ST,mod='Chassis')
    deck=box(-70,630,-260,260,264,268).cut(box(240,470,-130,130,262,270))
    add('Top deck 3 mm Al with battery hatch opening',T(deck),(0.62,0.66,0.7),mod='Chassis')
    lid=box(230,480,-140,140,270,276); gas=box(236,474,-134,134,268,270)
    if service: lid=lid.rotate((230,0,273),(230,1,273),-100); gas=gas.rotate((230,0,273),(230,1,273),-100)
    add('Battery hatch lid 3 mm Al',T(lid),(0.55,0.6,0.66),mod='Battery')
    add('Hatch EPDM gasket',T(gas),SEAL,mod='Battery')
    add('Hatch hinge (stainless piano)',T(cyl('y',(228,0,272),5,240)),(0.8,0.8,0.82),mod='Battery')
    for sg in (1,-1): add('Over-centre draw latch (stainless)',T(box(480,496,sg*80-12,sg*80+12,250,282)),(0.8,0.8,0.82),mod='Battery')
    bz=0 if not service else 420
    add('Battery cassette IP67, 24 V 20 Ah LiFePO4 + BMS',T(box(255,455,-115,115,124+bz,250+bz)),(0.2,0.35,0.7),mod='Battery')
    add('Cassette lift handle',T(box(330,380,-12,12,250+bz,262+bz)),BLK,mod='Battery')
    add('IP67 50 A battery connector (plug)',T(cyl('x',(467,0,200+bz),14,24)),CON,mod='Battery')
    add('IP67 battery connector (bulkhead socket)',T(cyl('x',(491,0,200),16,24)),CON,mod='Battery')
    add('IP67 charge port with cap',T(cyl('y',(350,-266,220),14,14)),CON,mod='Battery')
    for i in range(4): add('Ballast plate 10 mm steel (~5.6 kg)',T(box(505,620,-240,240,124+i*10.5,134+i*10.5)),(0.28,0.28,0.3),mod='Chassis')
    # --- drive modules (wheels pushed out 55 mm on hub spacers to clear the docking channel) ---
    for sg in (1,-1):
        m='Drive L' if sg>0 else 'Drive R'
        add('Drive wheel 13" knobbly pneumatic',T(cyl('y',(0,sg*345,165),165,70)),BLK,mod=m)
        add('Wheel hub + taper lock',T(cyl('y',(0,sg*345,165),60,74)),(0.6,0.6,0.62),mod=m)
        add('Output shaft V-ring seal',T(cyl('y',(0,sg*263,165),22,6)),SEAL,mod=m)
        add('24 V wheelchair gearbox',T(box(-45,45,sg*200,sg*255,130,220)),(0.25,0.25,0.28),mod=m)
        add('24 V wheelchair motor',T(cyl('x',(115,sg*218,175),38,140)),(0.2,0.2,0.22),mod=m)
        add('Spring brake (fail-safe)',T(cyl('x',(205,sg*218,175),34,40)),(0.7,0.15,0.15),mod=m)
        add('Drive module IP67 M12 connector',T(cyl('x',(232,sg*218,175),9,14)),CON,mod=m)
    # --- REAR FRAME (yaws on turntable at drive axle): spine, drop leg, wheel-stop crossbeam, funnel arms, anti-tip rollers ---
    add('Yaw turntable bearing 250 mm (steel)',T(cyl('z',(0,0,KZ-27),125,10)),(0.55,0.55,0.6),mod='Rear frame')
    add('Kingpin Ø20 + AS5600 yaw encoder',T(cyl('z',(0,0,KZ-10),14,30)),(0.8,0.2,0.6),mod='Rear frame')
    add('Yaw lock solenoid pin 12 V',T(box(60,100,-15,15,KZ-22,KZ-2)),(0.15,0.25,0.6),mod='Rear frame')
    add('Rear frame plate 6 mm steel',T(box(-130,130,-90,90,KZ-17,KZ-11)),NEW,mod='Rear frame')
    add('Spine beam 60×40 RHS',box(PX-30,TX+60,-30,30,KZ-11,KZ+29),NEW,mod='Rear frame')
    add('Hinge cross plate 8 mm steel',box(PX-40,PX+40,-185,185,KZ-38,KZ-30),NEW,mod='Rear frame')
    add('Spine drop leg 60×40 RHS',seg((PX-20,0,KZ-20),(150,0,120),25),NEW,mod='Rear frame')
    add('Wheel-stop crossbeam Ø32 tube',cyl('y',(120,0,100),16,700),NEW,mod='Rear frame')
    for sg in (1,-1):
        add('Docking funnel arm 40×20 RHS',box(-110,120,sg*315,sg*335,80,120),NEW,mod='Rear frame')
        add('Docking funnel flare 40×20 RHS',box(-110,-180,sg*315,sg*335,80,120).rotate((-110,sg*325,100),(-110,sg*325,101),-sg*25),NEW,mod='Rear frame')
        add('Anti-tip roller 100 mm PU (70 mm clearance)',cyl('y',(-210,sg*365,120),50,36),BLK,mod='Rear frame')
        add('Anti-tip roller bracket',box(-230,-100,sg*335,sg*385,140,160),NEW,mod='Rear frame')
        add('Stop roller 40 mm rubber',cyl('y',(120,sg*270,100),20,50),BLK,mod='Rear frame')
        add('Wheel-contact switch IP67',box(104,116,sg*215-6,sg*215+6,118,132),(0.2,0.6,0.9),mod='Rear frame')
    # --- front: casters, bumper, low lidar, sensor post ---
    add('Caster outrigger 5 mm steel (4WD-ready holes)',T(box(630,740,-260,260,254,264)),ST,mod='Chassis')
    for sg in (1,-1):
        add('Caster 200 mm pneumatic swivel',T(cyl('y',(690,sg*200,100),100,50)),DG,mod='Chassis')
        add('Caster fork + plate',T(box(682,698,sg*200-35,sg*200+35,100,254)),ST,mod='Chassis')
        add('Bumper strut',T(box(735,745,sg*150-10,sg*150+10,180,254)),ST,mod='Bumper')
        add('Sealed bumper microswitch IP67',T(box(735,745,sg*250-8,sg*250+8,160,180)),(0.2,0.2,0.8),mod='Bumper')
        add('TF02-Pro IP65 drop sensor',T(box(712,742,sg*290-18,sg*290+18,264,286)),(0.2,0.2,0.2),mod='Sensors')
    add('Front bumper EVA foam bar',T(box(745,780,-330,330,130,230)),BLK,mod='Bumper')
    add('E-stop IP65 (latching)',T(cyl('z',(100,-200,285),20,34)),(0.85,0.1,0.1),mod='Electronics')
    add('Lidar stub mount',T(box(712,752,-25,25,264,290)),ST,mod='Sensors')
    add('LD06 360° lidar',T(box(712,752,-20,20,290,324)),(0.15,0.15,0.18),mod='Sensors')
    add('Lidar weather dome (acrylic tube)',T(cyl('z',(732,0,317),34,64)),(0.6,0.8,0.95),0.3,mod='Sensors')
    add('Dome cap with drip edge',T(cyl('z',(732,0,352),42,6)),(0.3,0.3,0.32),mod='Sensors')
    add('Front camera IP67',T(box(760,784,-15,15,240,265)),BLK,mod='Sensors')
    add('Sensor post Ø36 tube',T(cyl('z',(700,-240,632),18,736)),ST,mod='Sensors')
    add('RTK GNSS antenna IP67',T(cyl('z',(700,-240,1012),40,24)),(0.95,0.95,0.95),mod='Sensors')
    add('LoRa antenna',T(cyl('z',(700,-200,1100),4,180)),BLK,mod='Sensors')
    add('4G antenna',T(cyl('z',(700,-280,1080),4,140)),BLK,mod='Sensors')
    add('Amber beacon IP65',T(cyl('z',(700,-240,960),25,70)),(1,0.6,0.05),mod='Sensors')
    # --- electronics pod ---
    add('Electronics pod IP67 body (ABS/PC)',T(box(20,200,-110,110,268,380)),(0.85,0.85,0.82),0.55,mod='Electronics')
    add('Pod lid with O-ring',T(box(18,202,-112,112,380,396)),(0.8,0.8,0.78),mod='Electronics')
    add('Gore breather vent',T(cyl('z',(60,80,400),8,8)),(0.9,0.9,0.9),mod='Electronics')
    for y in (-85,-50,-15,20,55,90): add('IP68 bulkhead connector (GX16/M12)',T(cyl('x',(206,y,330),9,14)),CON,mod='Electronics')
    add('Service port cap (USB/Ethernet)',T(cyl('x',(14,60,330),10,12)),CON,mod='Electronics')
    add('Dual 30 A motor driver',T(box(30,130,10,100,272,300)),PCB,mod='Electronics')
    add('Flight controller (ArduPilot)',T(box(140,180,10,50,272,282)),PCB,mod='Electronics')
    add('Pi Zero 2 W',T(box(140,195,55,85,272,277)),PCB,mod='Electronics')
    add('RTK GNSS module',T(box(30,70,-40,0,272,280)),PCB,mod='Electronics')
    add('LoRa radio + 4G modem',T(box(80,130,-45,-5,272,285)),PCB,mod='Electronics')
    add('Buck converters 24→12 V / 24→5 V',T(box(140,195,-45,-5,272,292)),(0.2,0.3,0.6),mod='Electronics')
    add('Fuse block, 40 A main + contactor',T(box(30,130,-100,-55,272,305)),(0.6,0.15,0.15),mod='Electronics')
    add('Actuator + solenoid driver',T(box(140,195,-100,-55,272,288)),PCB,mod='Electronics')
    # --- hinge base (tug) ---
    for sg in (1,-1):
        add('Mast hinge block 10 mm steel',box(PX-20,PX+20,sg*175-8,sg*175+8,KZ-30,PZ+18),ST,mod='Rear frame')
    add('Mast hinge pin Ø20 + bronze bushes',cyl('y',(PX,0,PZ),10,370),(0.8,0.8,0.82),mod='Rear frame')
    add('Actuator clevis post',box(ACT_BASE[0]-20,ACT_BASE[0]+20,ACT_Y-20,ACT_Y+20,KZ-11,ACT_BASE[1]+12),ST,mod='Rear frame')
    add('Actuator post brace',box(ACT_BASE[0]-20,ACT_BASE[0]+20,30,ACT_Y-20,KZ-11,KZ+19),ST,mod='Rear frame')
    # --- tilting mast (built vertical, rotated by phi about the pin) ---
    MP=[]
    def addm(n,w,c,a=1.0,mod='Mast'): MP.append(dict(name=n,w=w,c=c,a=a,g='tug',mod=mod))
    px=PX
    for sg in (1,-1):
        addm('Mast rail 40×40×3 Al',box(px,px+40,sg*150-20,sg*150+20,PZ-20,PZ+980),AL)
        addm('Mast pivot lug 8 mm steel',box(px-10,px+50,sg*150-24,sg*150+24,PZ-30,PZ+60),ST)
        addm('Carriage float stop (top/bottom)',box(px+40,px+55,sg*150-12,sg*150+12,PZ+S_TOP+40,PZ+S_TOP+52),ST)
        addm('Carriage float stop (top/bottom)',box(px+40,px+55,sg*150-12,sg*150+12,PZ+S_BOT-120,PZ+S_BOT-108),ST)
    addm('Mast top plate / rain cap',box(px-20,px+60,-175,175,PZ+980,PZ+990),ST)
    addm('Mast lower cross tube',box(px,px+40,-130,130,PZ+320,PZ+350),AL)
    ab=box(px+ACT_E-15,px+20,ACT_Y-40,ACT_Y-10,PZ+ACT_S-15,PZ+ACT_S+15).union(box(px+ACT_E-15,px+ACT_E+15,ACT_Y-40,ACT_Y+20,PZ+ACT_S-15,PZ+ACT_S+15))
    addm('Actuator bracket 30×30 tube (mast)',ab,ST)
    addm('Rear docking camera IP67',box(px-30,px,-15,15,PZ+940,PZ+970),BLK)
    addm('Carriage return spring',cyl('z',(px+20,0,PZ+S_TOP+20),8,140),(0.8,0.8,0.2))
    # carriage at position s (hook centre at PZ+s when vertical)
    Z=PZ+s; hx_=px+EH  # hook centre x when vertical
    addm('Slide carriage 6 mm steel',box(px-20,px-6,-135,135,Z-90,Z+30),ST,mod='Grabber')
    for sg in (1,-1):
        for dz in (-80,0): addm('UHMW slide pad',box(px-6,px,sg*150-15,sg*150+15,Z+dz,Z+dz+20),(0.95,0.95,0.9),mod='Grabber')
    addm('Crossbar arm (rigid)',box(hx_+15,px-20,-20,20,Z-75,Z-55),ST,mod='Grabber')
    addm('Crossbar 30×20 RHS',box(hx_-15,hx_+15,-215,215,Z-75,Z-55),ST,mod='Grabber')
    addm('Tilt IMU (potted)',box(hx_-10,hx_+10,-15,15,Z-55,Z-45),(0.8,0.2,0.6),mod='Grabber')
    for sg in (1,-1):
        for cy in (sg*190-6, sg*190+14):
            addm('Hook cheek plate 8 mm steel (ramp lead-in)',hook_cheek().translate((hx_,cy,Z)),(0.35,0.37,0.42),mod='Grabber')
        addm('Cheek spacer block',box(hx_+20,hx_+55,sg*190-6,sg*190+6,Z-70,Z-20),(0.45,0.47,0.52),mod='Grabber')
        addm('Latch tongue (angled top, flat underside)',box(hx_-14,hx_+40,sg*190-5,sg*190+5,Z+18,Z+28),(1,0.45,0.1),mod='Grabber')
        addm('Tongue return spring',cyl('x',(hx_+48,sg*190,Z+23),4,16),(0.8,0.8,0.2),mod='Grabber')
        so=sg*190+sg*14
        addm('Release lever 4 mm steel',box(hx_+36,hx_+44,so,so+sg*4,Z-42,Z+24),(0.9,0.75,0.1),mod='Grabber')
        addm('Release solenoid 12 V IP67, 10 mm',box(hx_-12,hx_+30,so+sg*4,so+sg*26,Z-48,Z-32),(0.15,0.25,0.6),mod='Grabber')
        addm('Seat switch IP67 roller lever',box(hx_-8,hx_+8,sg*190-5,sg*190+5,Z-26,Z-16),(0.2,0.6,0.9),mod='Grabber')
        addm('Latch switch IP67',box(hx_+50,hx_+62,sg*190+sg*14,sg*190+sg*24,Z+14,Z+32),(0.2,0.6,0.9),mod='Grabber')
    for p in MP:
        p['w']=p['w'].rotate((PX,0,PZ),(PX,1,PZ),phi); P.append(p)
    # tilt actuator (tug clevis -> mast bracket rod end)
    A=mast_pt(ACT_S,ACT_E,phi); B=ACT_BASE
    import numpy as np
    d=np.array([A[0]-B[0],A[1]-B[1]]); L=float(np.linalg.norm(d)); u=d/L; body=640.0
    add('Tilt actuator IP66, 450 mm, 2,500 N (body)',seg((B[0],ACT_Y,B[1]),(B[0]+u[0]*body,ACT_Y,B[1]+u[1]*body),26),(0.25,0.25,0.27),mod='Rear frame')
    add('Tilt actuator rod',seg((B[0]+u[0]*body,ACT_Y,B[1]+u[1]*body),(A[0],ACT_Y,A[1]),10),(0.85,0.85,0.87),mod='Mast')
    if with_bin:
        def R(w): return w.rotate((0,0,100),(0,1,100),theta)
        body_=cq.Workplane("XY").workplane(offset=40).center(-315,0).rect(550,480).workplane(offset=990).center(-50,0).rect(730,580).loft()
        add('240 L bin body',R(body_),GRN,0.3,'bin')
        add('Bin lid',R(box(-760,15,-300,300,1030,1060)),GRN,0.3,'bin')
        add('Bin handle bar',R(cyl('y',(HX,0,HZ+100),16,540)),(0.1,0.35,0.2),0.95,'bin')
        for sg in (1,-1):
            add('Handle side web',R(box(-10,55,sg*270-10,sg*270+10,980,1035)),(0.1,0.35,0.2),0.9,'bin')
            add('Bin wheel',R(cyl('y',(0,sg*270,100),100,50)),BLK,0.8,'bin')
        add('Bin axle',R(cyl('y',(0,0,100),12,600)),(0.7,0.7,0.7),0.8,'bin')
        add('Bin front feet',R(box(-600,-560,-200,200,0,40)),GRN,0.3,'bin')
    return P,dict(phi=phi,s=s,tx=tx,act_len=L)
def mesh(P,tol=2.0):
    out=[]
    for p in P:
        v,t=p['w'].val().tessellate(tol,0.5); bb=p['w'].val().BoundingBox()
        out.append(dict(name=p['name'],V=[[q.x,q.y,q.z] for q in v],T=[list(x) for x in t],c=p['c'],a=p['a'],g=p['g'],mod=p['mod'],
                        cen=[(bb.xmin+bb.xmax)/2,(bb.ymin+bb.ymax)/2,(bb.zmin+bb.zmax)/2]))
    return out
if __name__=='__main__':
    for th in (0,24,48):
        phi,s=mast_pose(th); print('theta',th,'phi %.1f s %.0f'%(phi,s))
    allm={}
    for key,th,kw in [('dock',0,{}),('tow',48,{}),('t24',24,{}),('approach',0,dict(phi=8.0,s=S_TOP))]:
        P,info=build(th,**kw); allm[key]=dict(mesh=mesh(P),info=info); print(key,info)
        if key in('dock','tow'):
            asm=cq.Assembly()
            for i,p in enumerate(P): asm.add(p['w'],name=f"{i:03d}_{p['name']}"[:60],color=cq.Color(*p['c'],p['a']))
            asm.save(f'bin_tug_revF_{key}.step')
            bins=[p for p in P if p['g']=='bin' and 'handle' not in p['name'].lower()]
            tug=[p for p in P if p['g']=='tug']
            hits=set()
            for b in bins:
                bb=b['w'].val().BoundingBox()
                for p in tug:
                    pb=p['w'].val().BoundingBox()
                    if pb.xmin>bb.xmax or pb.xmax<bb.xmin or pb.zmin>bb.zmax or pb.zmax<bb.zmin or pb.ymin>bb.ymax or pb.ymax<bb.ymin: continue
                    try:
                        if b['w'].intersect(p['w']).val().Volume()>5: hits.add((b['name'],p['name']))
                    except Exception: pass
            print(key,'bin-tug interference',hits)
        if key=='tow':
            tg=None
            for p in P:
                if p['g']=='tug': tg=p['w'] if tg is None else tg.union(p['w'])
            cq.exporters.export(tg,'bin_tug_revF.stl')
    json.dump(allm,open('mesh_revF.json','w')); print('parts',len(allm['tow']['mesh']))
