# Per-part mass table for Rev E. Fabricated parts: CAD volume x density. Bought / hollow parts: datasheet weights.
import json, math, csv
from model_revF import build
RHO={'steel':7850,'al':2700,'abs':1050,'epdm':1300,'acrylic':1190,'uhmw':940,'rubber':1150}
# name -> (kg, source/basis)   (per instance)
FIXED={
 'Yaw turntable bearing 250 mm (steel)':(1.4,'250 mm steel lazy-susan / turntable bearing'),'Kingpin Ø20 + AS5600 yaw encoder':(0.35,'est.'),
 'Yaw lock solenoid pin 12 V':(0.15,'est.'),'Spine beam 60×40 RHS':(2.5,'60x40x2.5 RHS 3.6 kg/m x 0.69 m'),'Spine drop leg 60×40 RHS':(0.95,'60x40x2.5 RHS 3.6 kg/m x 0.26 m'),
 'Docking funnel arm 40×20 RHS':(0.42,'40x20x2 RHS 1.81 kg/m x 0.23 m'),'Actuator clevis post':(0.35,'est.'),'Actuator post brace':(0.2,'est.'),
 'Mast pivot lug 8 mm steel':(0.45,'two 8 mm side plates + boss, est.'),'Anti-tip roller bracket':(0.30,'5 mm bent steel, est.'),
 'Actuator deck clevis':(0.25,'6 mm steel clevis, est.'),'Mast hinge block 10 mm steel':(0.35,'10 mm plate pillow block, est.'),
 'Drive wheel 13" knobbly pneumatic':(3.04,'SuperDroid 13x5.00-6 lug wheel 6.7 lb'),
 'Wheel hub + taper lock':(0.60,'est. steel hub'),
 '24 V wheelchair gearbox':(2.6,'split of 6.0 kg gearmotor+brake (DYD 350 W lists 7.2 kg; typical 5-7 kg)'),
 '24 V wheelchair motor':(2.7,'split of 6.0 kg gearmotor'),
 'Spring brake (fail-safe)':(0.7,'split of 6.0 kg gearmotor'),
 'Battery cassette IP67, 24 V 20 Ah LiFePO4 + BMS':(6.4,'5.4 kg LiFePO4 (RELiON RB24V20) + 1.0 kg IP67 case'),
 'Caster 200 mm pneumatic swivel':(1.30,'BIL 200 mm pneumatic swivel castor 2.16 kg total, wheel share'),
 'Caster fork + plate':(0.86,'BIL castor 2.16 kg total, fork share'),
 'Tilt actuator IP66, 450 mm, 2,500 N (body)':(1.95,'2500 N 450 mm actuators ~2.2 kg total'),
 'Tilt actuator rod':(0.30,'rod share'),
 'Mast rail 40×40×3 Al':(0.44,'40x40x3 Al tube 0.45 kg/m x 0.98 m'),
 'Sensor post Ø36 tube':(1.24,'36x2 steel tube 1.68 kg/m x 0.736 m'),
 'Wheel-stop crossbeam Ø32 tube':(1.04,'32x2 steel tube 1.48 kg/m x 0.70 m'),
 'Crossbeam stub 40×20 RHS':(0.22,'40x20x2 RHS 1.81 kg/m x 0.12 m'),
 'Docking channel arm 40×20 RHS':(0.52,'40x20x2 RHS 1.81 kg/m x 0.29 m'),
 'Docking funnel flare 40×20 RHS':(0.13,'40x20x2 RHS 1.81 kg/m x 0.07 m'),
 'Anti-tip roller 100 mm PU (70 mm clearance)':(0.40,'100 mm PU roller with bearings'),
 'Stop roller 40 mm rubber':(0.08,'est.'),'Wheel-contact switch IP67':(0.03,'est.'),
 'Hub spacer / stub shaft 55 mm':(0.45,'steel spacer + longer studs, est.'),
 'Mast hinge pin Ø20 + bronze bushes':(0.95,'20 mm steel pin 2.47 kg/m x 0.36 + bushes'),
 'Carriage return spring':(0.10,'est.'),'Mast lower cross tube':(0.25,'40x40x3 Al 0.45 kg/m x 0.3 m + ends'),
 'Actuator bracket 30×30 tube (mast)':(0.55,'30x30x2 steel 1.7 kg/m x 0.28 m + clevis'),
 'Crossbar 30×20 RHS':(0.65,'30x20x2 RHS 1.5 kg/m x 0.43 m'),
 'Mast rail 40×40×3 Al':(0.44,'40x40x3 Al tube 0.45 kg/m x 0.98 m'),
 'Electronics pod IP67 body (ABS/PC)':(1.5,'IP67 ABS box ~180x220x130'),'Pod lid with O-ring':(0.35,'est.'),
 'Lidar weather dome (acrylic tube)':(0.08,'3 mm acrylic tube'),'LD06 360° lidar':(0.042,'LD06 datasheet 42 g'),
 'Front camera IP67':(0.15,'est.'),'Rear docking camera IP67':(0.15,'est.'),'RTK GNSS antenna IP67':(0.20,'typ. survey-style patch'),
 'LoRa antenna':(0.03,'est.'),'4G antenna':(0.03,'est.'),'Amber beacon IP65':(0.20,'est.'),'E-stop IP65 (latching)':(0.15,'est.'),
 'Dual 30 A motor driver':(0.25,'est.'),'Flight controller (ArduPilot)':(0.03,'est.'),'Pi Zero 2 W':(0.011,'RPi'),
 'RTK GNSS module':(0.02,'est.'),'LoRa radio + 4G modem':(0.08,'est.'),'Buck converters 24→12 V / 24→5 V':(0.15,'est.'),
 'Fuse block, 40 A main + contactor':(0.35,'est.'),'Actuator + solenoid driver':(0.08,'est.'),
 'IP68 bulkhead connector (GX16/M12)':(0.03,'est.'),'IP67 50 A battery connector (plug)':(0.08,'est.'),'IP67 battery connector (bulkhead socket)':(0.08,'est.'),
 'IP67 charge port with cap':(0.05,'est.'),'Drive module IP67 M12 connector':(0.03,'est.'),'Service port cap (USB/Ethernet)':(0.02,'est.'),'Gore breather vent':(0.005,'est.'),
 'Release solenoid 12 V IP67, 10 mm':(0.12,'typ. 12 V push-pull'),'Seat switch IP67 roller lever':(0.03,'est.'),'Latch switch IP67':(0.03,'est.'),
 'Sealed bumper microswitch IP67':(0.03,'est.'),'TF02-Pro IP65 drop sensor':(0.10,'TF-Luna 5 g + IP65 box'),
 'Hitch yaw encoder AS5600 (potted)':(0.03,'est.'),'Tilt IMU (potted)':(0.03,'est.'),'Tongue return spring':(0.005,'est.'),
 'Lidar stub mount':(0.10,'est.'),'Front bumper EVA foam bar':(0.35,'EVA ~100 kg/m3 + skin'),'Over-centre draw latch (stainless)':(0.08,'est.'),'Cassette lift handle':(0.05,'est.'),
 'Hatch hinge (stainless piano)':(0.15,'est.'),'Yaw pivot housing + bronze bush':(0.45,'steel+bronze, est.'),'Output shaft V-ring seal':(0.01,'est.'),
 'Dome cap with drip edge':(0.05,'est.'),
}
SCALE={'Caster outrigger':0.5,'Slide carriage':6/14,'Mast top plate':0.5}  # model plates drawn thicker than spec
MAT={'Rear frame plate':'steel','Hinge cross plate':'steel','Stub root gusset':'steel','Mast hinge block':'steel','Mast pivot lug':'steel','Carriage float stop':'steel','Actuator deck clevis':'steel','Arm root gusset':'steel','Anti-tip roller bracket':'steel','Chassis tray':'steel','Top deck':'al','Battery hatch lid':'al','Hatch EPDM gasket':'epdm','Ballast plate':'steel','Caster outrigger':'steel',
 'Bumper strut':'steel','Mast gusset':'steel','Mast top plate':'steel','Slide carriage':'steel','UHMW':'uhmw','Crossbar arm':'steel',
 'Hook cheek':'steel','Cheek spacer':'steel','Latch tongue':'steel','Release lever':'steel'}
def mass_table(theta=0):
    P,info=build(theta,with_bin=False); rows=[]
    for p in P:
        n=p['name'];sh=p['w'].val();bb=sh.BoundingBox();c=sh.Center()
        if n in FIXED: m,src=FIXED[n]
        else:
            mat=[v for k,v in MAT.items() if k in n]
            if not mat: raise SystemExit('no mass for '+n)
            m=sh.Volume()*1e-9*RHO[mat[0]];src=f'CAD volume x {mat[0]} {RHO[mat[0]]} kg/m3'
            for k,v in SCALE.items():
                if k in n: m*=v;src+=f' (x{v:.2f} to spec thickness)'
        rows.append(dict(name=n,mod=p['mod'],kg=m,cx=c.x,cy=c.y,cz=c.z,dx=bb.xlen,dy=bb.ylen,dz=bb.zlen,src=src))
    return rows,info
if __name__=='__main__':
    rows,info=mass_table()
    info=[info['phi'],info['s'],info['tx']]
    tot=sum(r['kg'] for r in rows);cg=[sum(r['kg']*r[k] for r in rows)/tot for k in('cx','cy','cz')]
    with open('mass_table_revF.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();[w.writerow(r) for r in rows]
    bymod={}
    for r in rows: bymod[r['mod']]=bymod.get(r['mod'],0)+r['kg']
    print('total %.2f kg'%tot,'CG (tug frame, mm, x from drive axle): %.0f %.0f %.0f'%(cg[0]-info[2],cg[1],cg[2]))
    for k,v in sorted(bymod.items(),key=lambda x:-x[1]): print(f'  {k:12s} {v:6.2f}')
    json.dump(dict(rows=rows,info=info,total=tot,cg=cg),open('mass_revF.json','w'))
