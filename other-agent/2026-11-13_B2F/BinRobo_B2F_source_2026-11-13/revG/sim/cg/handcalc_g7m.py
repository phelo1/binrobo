#!/usr/bin/env python3
"""Concept gate: drive torque per wheel vs the G7 motor (peiscooter PEWM-39, ELEC_SAFETY_G7.md s.5), 40 mm step torque, speed.
Inputs: res/handcalc_cg.json (traction rows, sim resistances), static sim splits. Output res/handcalc_motor_g7.json"""
import json, math, os
H=os.path.dirname(os.path.abspath(__file__)); J=lambda f: json.load(open(os.path.join(H,'res',f)))
hc=J('handcalc_cg.json'); A=J('calA_ESE240SL_G8_flat110.json'); Bf=J('B_static_flat_110.json')
rw=0.165; h=0.04; a=math.sqrt(rw**2-(rw-h)**2)          # lever of the axle about a 40 mm sharp edge
mot=dict(name='peiscooter PEWM-39 pair (G7 DRV-M7)',vendor_rated_Nm=48.0,derived_rated_Nm=36.9,derived_kt_wheel_Nm_per_A=62.9/40,
         ctrl_cont_A=40,ctrl_peak_A_30s=60,torque_at_40A_Nm=62.9,torque_at_60A_Nm_linear=round(62.9*60/40,1),
         free_speed_mps_24V=round(4000/39*2*math.pi/60*rw,2),src='revG/ELEC_SAFETY_G7.md s.5 (vendor 48 N m; derived 36.9 N m at 23.4 A; 62.9 N m at 40 A)')
rows=[]
for r in hc['traction_12pct']:
    T=r['torque_per_wheel_Nm']
    rows.append(dict(concept=r['concept'],crr_bin=r['crr_bin'],mu_req=r['mu_req'],torque_per_wheel_Nm=T,
        I_per_motor_A=round(T/mot['derived_kt_wheel_Nm_per_A'],1),frac_vendor_rated=round(T/48,2),frac_derived_rated=round(T/36.9,2),
        torque_x1p25=round(T*1.25,1),x1p25_within_40A_limit=T*1.25<=62.9))
# full-width 40 mm step, quasi-static, no push from the other axle: T = W * a
step=[]
for name,Wl,Wr in (("A'",A['driveL'],A['driveR']),('B',Bf['driveL'],Bf['driveR'])):
    W=max(Wl,Wr); T=W*a
    step.append(dict(concept=name,drive_wheel_load_N=round(W),lever_m=round(a,4),torque_needed_Nm=round(T,1),
        within_60Nm_sim_cap=T<=60,within_62p9_at_40A=T<=62.9,within_60A_peak=T<=mot['torque_at_60A_Nm_linear'],x_vendor_rated=round(T/48,2)))
out=dict(motor=mot,climb12=rows,step40_full_width=step,
    verdict=("PEWM-39 fits the 12 % climb for both concepts on vendor rating (A' 0.71, B 0.51 of 48 N m) but A' runs at 0.92 of the derived 36.9 N m "
             "continuous rating at crr 0.09, B at 0.67. Neither concept can climb a full-width sharp 40 mm step quasi-statically inside the 60 N m cap "
             "(needs about 80-90 N m per wheel); that needs the 60 A/30 s controller peak (~94 N m, linear, gearbox peak rating unknown) or the oblique-crossing rule."))
json.dump(out,open(os.path.join(H,'res','handcalc_motor_g7.json'),'w'),indent=1); print(json.dumps(out,indent=1))
