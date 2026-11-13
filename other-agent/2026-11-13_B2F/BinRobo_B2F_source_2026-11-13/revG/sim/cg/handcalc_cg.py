#!/usr/bin/env python3
"""Concept gate hand calcs (A' vs B): traction / wheel torque, motor check, stability tip angles, structure, mass.
Inputs: sim static load splits (res/calA_ESE240SL_G8_flat110.json, res/B_static_flat_110.json), mass files, bins_g5.
Output: res/handcalc_cg.json"""
import json, math, os, sys
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..','g6'))
from bins_g5 import BINS
g=9.81; th=math.atan(0.12); s,c=math.sin(th),math.cos(th); rw=0.165
J=lambda f: json.load(open(os.path.join(H,'res',f)))
out={}
# ---------------- 1. traction on 12 % (static normal loads from the sims, resistances as modelled in the sims)
A=J('calA_ESE240SL_G8_flat110.json'); Bs=J('B_static_flat_110.json')
mA=115.8+110.0; mB=93.5+110.0
fl_drive=2*0.06*300*0.165/rw; fl_cast=2*0.06*200*0.1/0.1          # sim frictionloss -> equivalent force at the ground (N), both concepts
def binroll(crr): return 2*crr*(98+12)*g*0.45*0.1/0.1              # sim bin-wheel frictionloss (both wheels), N  (fill 97-98 kg)
rows=[]
for name,m,Nd,bin_on_ground in (("A' tow (pad 550 N)",mA,A['drive_N'],True),('B carrier',mB,Bs['driveL']+Bs['driveR'],False)):
    for crr in (0.06,0.09):
        R=m*g*s+fl_drive+fl_cast+(binroll(crr) if bin_on_ground else 0.0)
        # uphill load transfer onto the drive axle (CG height ~0.40 m, wheelbase 0.79 A' / 0.90 B) - small, both ways counted
        rows.append(dict(concept=name,crr_bin=crr,resist_N=round(R),drive_normal_flat_N=round(Nd),mu_req=round(R/(Nd*c),3),
                         torque_per_wheel_Nm=round(R*rw/2,1),power_per_wheel_W_at_0p5=round(R*0.5/2)))
out['traction_12pct']=rows
# ---------------- 2. step 40 mm: quasi-static push needed (sharp edge) per wheel = N*tan(alpha), cos(alpha)=(r-h)/r
def push(N,r,h=0.04): a=math.acos((r-h)/r); return N*math.tan(a)
out['step40_quasistatic']=dict(
    drive_330_per_N=round(push(1,0.165),3),castor_200_per_N=round(push(1,0.10),3),binwheel_200_per_N=round(push(1,0.10),3),binwheel_250_per_N=round(push(1,0.125),3),
    A_full_width_bin_wheels_N=round(push(A['binwheel_ground_N'],0.10)),A_available_traction_N=round(min(0.6*A['drive_N'],2*60/rw)),
    B_full_width_castors_N=round(push(Bs['caster_sum'],0.10)),B_available_traction_N=round(min(0.6*(Bs['driveL']+Bs['driveR']),2*60/rw)),
    note='a 40 mm step is climbed quasi-statically only if the drive wheels can push the unpowered wheels over it; momentum and tyre compliance help in the sim')
# ---------------- 3. motor: MY1016ZL-75-class 24 V 250 W, 40:1, 75 rpm, supplier table rated 36 N m; 25 A limit -> ~60 N m peak (sim cap)
mot=dict(model='MY1016ZL-75 class 24 V 250 W brushed wheelchair gearmotor with 24 V EM brake (40:1, 75 rpm)',rated_Nm=36.0,rated_rpm=75,
         free_speed_mps=round(75*2*math.pi/60*rw,2),peak_Nm_at_25A=60.0,price_GBP_1to12=44.92,
         url='https://www.alibaba.com/product-detail/MY1016Z-24V-250W-120RPM-75RPM-High_60703183903.html')
for r in rows: r['vs_rated']=round(r['torque_per_wheel_Nm']/mot['rated_Nm'],2)
out['motor']=mot
# ---------------- 4. stability, B carrier (CG from the mass file + bin CG in the carry pose)
MB=json.load(open(os.path.join(H,'mass_cgB.json'))); rws=MB['rows']+MB['carriage']
mt=sum(r['kg'] for r in rws); xt=sum(r['kg']*r['p'][0] for r in rws)/mt; zt=sum(r['kg']*r['p'][2] for r in rws)/mt
def bin_cg(binkey,kg):
    B=BINS[binkey]; bx=B['bar_x'][0]; cb=B['cb'][0]; xbt=bx-cb; sc=B['D']/0.74; bh=B['bar_abs'][0]-B['wheel']/2
    me=B['empty']-1.4-1.8; mf=kg-B['empty']; ce=(xbt-0.32*sc,0.42*bh/0.93); cf=(xbt-0.33*sc,0.38*bh/0.93)
    m=me+mf+3.2; x=(me*ce[0]+mf*cf[0]+3.2*xbt)/m; z=(me*ce[1]+mf*cf[1]+3.2*bh)/m
    return x,z,B
stab=[]
for kg in (110,60):
    xb,zb,B=bin_cg('ESE240SL',kg); x_axle=0.285-0.004-(B['bar_x'][0]-B['cb'][0])   # bin axle in the tug frame (nib front at lip root + 4 mm)
    Xb=x_axle+xb; Zb=B['wheel']/2+0.065+zb                                     # carried ~65 mm up
    M=mt+kg; X=(mt*xt+kg*Xb)/M; Z=(mt*zt+kg*Zb)/M
    # support: drive contacts (0,+/-0.40), castor contacts (0.90,+/-0.28); anti-tip rollers (-0.36,+/-0.44) touch after ~50 mm
    def tip_side(px,py,qx,qy):
        L=math.hypot(qx-px,qy-py); d=abs((qx-px)*(py-0)-(px-X)*(qy-py))/L; return math.degrees(math.atan(d/Z))
    stab.append(dict(bin_kg=kg,cg_x_m=round(X,3),cg_z_m=round(Z,3),tip_lateral_deg=round(tip_side(0,0.40,0.90,0.28),1),
                     tip_forward_over_castors_deg=round(math.degrees(math.atan((0.90-X)/Z)),1),
                     rear_liftoff_about_drive_axle_deg=round(math.degrees(math.atan(X/Z)),1),
                     rear_tip_with_antitip_rollers_deg=round(math.degrees(math.atan((X+0.36)/Z)),1)))
out['stability_B']=dict(tug_kg=round(mt,1),tug_cg=(round(xt,3),round(zt,3)),cases=stab)
# A': tug alone (track 0.69, castors +/-0.20 at 0.79) and the towed bin on its own wheels (half track wy, CG in the 45 deg tow pose)
MA=json.load(open(os.path.join(H,'mass_cgA.json'))); ma=sum(r['kg'] for r in MA['rows']); xa=sum(r['kg']*(r['cx']-670) for r in MA['rows'])/ma/1000; za=sum(r['kg']*r['cz'] for r in MA['rows'])/ma/1000
def tipA(px,py,qx,qy,X,Z):
    L=math.hypot(qx-px,qy-py); d=abs((qx-px)*(py-0)-(px-X)*(qy-py))/L; return math.degrees(math.atan(d/Z))
binA=[]
for kg in (110,60):
    xb,zb,B=bin_cg('ESE240SL',kg); t=math.radians(45); zc=B['wheel']/2+(-xb*math.sin(t)+zb*math.cos(t)); wy=(B['track']-0.05)/2
    binA.append(dict(bin_kg=kg,bin_cg_height_tow_m=round(zc,3),bin_lateral_tip_deg=round(math.degrees(math.atan(wy/zc)),1)))
out['stability_A']=dict(tug_kg=round(ma,1),tug_cg=(round(xa,3),round(za,3)),tug_lateral_tip_deg=round(tipA(0,0.345,0.79,0.20,xa,za),1),
                        tug_rear_liftoff_unladen_deg=round(math.degrees(math.atan(xa/za)),1),towed_bin=binA)
# ---------------- 5. structure
def rhs(b,h,t): I=(b*h**3-(b-2*t)*(h-2*t)**3)/12; return I/(h/2)   # mm^3, bending about the axis parallel to b
Wa=rhs(40,80,3); Wb=rhs(60,80,4)
F_st=(Bs['driveL']+Bs['driveR'])/2; L=0.45
out['structure_B']=dict(arm_root_moment_static_Nm=round(F_st*L),arm_root_moment_x2p5_Nm=round(2.5*F_st*L),
    RHS80x40x3_W_mm3=round(Wa),stress_static_MPa=round(F_st*L*1e3/Wa,1),stress_x2p5_MPa=round(2.5*F_st*L*1e3/Wa,1),
    RHS80x60x4_W_mm3=round(Wb),stress_x2p5_80x60x4_MPa=round(2.5*F_st*L*1e3/Wb,1),S355_yield_MPa=355,
    comb_tooth=dict(load_static_N=1210,load_peak_N=2600,lever_m=0.13,section='240 x 10 mm S355',stress_peak_MPa=round(2600*0.13*1e3/(240*10**2/6),1)),
    lift_actuator=dict(static_N=1210,peak_sim_N=2400,chosen='TiMOTION TA23 4,000 N push/pull',sf_static=round(4000/1210,1),sf_peak=round(4000/2400,2)),
    note='sim tyre and comb peaks are unfiltered contact spikes at dt 0.5 ms (cf. m6); x2.5 dynamic factor used for sizing, fatigue not checked')
out['structure_A']=dict(pad_force_nom_N=560,pad_spring='2 die springs, k 2,800 N/m each, 25 mm stroke',kingpin='tapered-roller trailer hub >= 500 kg; peak bending from step40 sims in A_step40_*.json loads.kp_bend',
    float_clamp='second pawl on the float rack (or rail brake) to clamp the float at its bottom stop in tow')
out['mass']=dict(A_kg=round(ma,1),B_kg=round(mt,1),limit=120)
json.dump(out,open(os.path.join(H,'res','handcalc_cg.json'),'w'),indent=1); print(json.dumps(out,indent=1))
