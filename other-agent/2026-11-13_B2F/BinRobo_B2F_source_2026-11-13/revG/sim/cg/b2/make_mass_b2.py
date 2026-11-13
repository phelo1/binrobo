#!/usr/bin/env python3
"""B2 mass table (kg, x/y/z m in the tug frame) -> mass_cgB2.json (new drive) and mass_cgB2_donor.json (donor-chair drive).
Sources: B1 rows (it1/mass_cgB1.json) for carried-over parts; new frame from section x length (50x50x2 RHS 2.98 kg/m, S235);
plates from area x thickness x 7.85; HDPE 0.95 kg/dm3. Ballast x set by argv (hand calc picks it). usage: make_mass_b2.py <ballast_kg> <ballast_x>"""
import json, sys, os
H=os.path.dirname(os.path.abspath(__file__)); kgb=float(sys.argv[1]) if len(sys.argv)>1 else 5.0; xb=float(sys.argv[2]) if len(sys.argv)>2 else 1.00
T=2.98  # kg/m 50x50x2 RHS
R=[('Side rail L 50x50x2 RHS 1.35 m (x -0.37..0.98, over the drive tyre)',1.35*T,(0.305,0.43,0.385),(1.35,0.05,0.05),'chassis'),
   ('Side rail R 50x50x2 RHS 1.35 m',1.35*T,(0.305,-0.43,0.385),(1.35,0.05,0.05),'chassis'),
   ('Nose cross-member 50x50x2 0.86 m (castor plates below)',0.86*T,(0.955,0,0.265),(0.05,0.86,0.05),'chassis'),
   ('Mast-base cross-member 50x50x2 0.86 m',0.86*T,(0.49,0,0.385),(0.05,0.86,0.05),'chassis'),
   ('Mast uprights 2 x 50x50x2 0.90 m (z 0.41-1.31)',2*0.90*T,(0.49,0,0.86),(0.05,0.45,0.9),'chassis'),
   ('Mast top tie 50x50x2 0.46 m',0.46*T,(0.49,0,1.285),(0.05,0.46,0.05),'chassis'),
   ('Drive/motor plates 2 x 6 mm S355 (laser)',2*0.18*0.30*0.006*7850,(0.0,0,0.27),(0.3,0.9,0.3),'chassis'),
   ('Castor plates 2 x 8 mm S355 (laser)',2*0.16*0.16*0.008*7850,(0.95,0,0.235),(0.16,0.6,0.01),'chassis'),
   ('Mast gussets 4 x 6 mm + actuator lugs 2 + rail-tail caps (laser)',1.6,(0.42,0,0.42),(0.2,0.8,0.1),'chassis'),
   ('Battery/electronics bay: 10 mm HDPE floor 0.48 x 0.76 + 6 mm HDPE covers',0.48*0.76*0.010*950+0.48*0.80*0.006*950,(0.74,0,0.20),(0.48,0.76,0.15),'chassis'),
   ('Drive unit L: PEWM82M-320W gearmotor + spring brake + 3.5:1 chain + 330 mm wheel (B1 mass)',9.68,(0.0,0.40,0.17),(0.3,0.1,0.3),'wheel'),
   ('Drive unit R',9.68,(0.0,-0.40,0.17),(0.3,0.1,0.3),'wheel'),
   ('Castor 200 mm L + fork',2.3,(0.93,0.28,0.10),(0.2,0.08,0.2),'cast'),('Castor 200 mm R + fork',2.3,(0.93,-0.28,0.10),(0.2,0.08,0.2),'cast'),
   ('Battery 24 V 20 Ah LiFePO4 + BMS (front bay)',5.05,(0.90,0,0.18),(0.25,0.18,0.15),'chassis'),
   ('Electronics pod + harness (as B1)',3.39,(0.70,0,0.32),(0.2,0.2,0.1),'chassis'),
   ('Sensors: post, lidar, cameras, radars (as B1)',1.86,(1.00,0,0.60),(0.05,0.05,0.6),'chassis'),
   ('Bumper, lights, dock interface, safety (as B1)',1.95,(1.07,0,0.22),(0.05,0.66,0.1),'chassis'),
   ('Linear rails 2 x 1.0 m HGR15 + 4 carriages',2.9,(0.46,0,0.80),(0.03,0.4,1.0),'chassis'),
   ('Lift actuator QC FDI 24 V 4 kN, 400 mm unit (250 mm used)',3.5,(0.49,0,0.70),(0.08,0.08,0.6),'chassis'),
   ('Rear camera + beacon on the mast top',0.6,(0.45,0,1.31),(0.1,0.3,0.05),'chassis'),
   ('Anti-tip rollers (y +/-0.42) + flares + UHMW guards',1.6,(-0.25,0,0.18),(0.1,0.85,0.1),'chassis'),
   ('Leg-tip gap sensors 2 x ToF (potted)',0.1,(-0.40,0,0.25),(0.05,0.8,0.05),'chassis')]
if kgb>0: R.append(('Ballast: %.1f kg steel plate on the nose cross-member / bay floor'%kgb,kgb,(xb,0,0.15),(0.1,0.6,0.03),'chassis'))
rows=[dict(name=n,kg=round(k,3),p=list(p),d=list(d),g=g) for n,k,p,d,g in R]
# carriage: B1 5.1 kg + 640 mm self-aligning comb (+1.6) - DSZY4/1 kN pad actuator row (0.6) + TC24-50-500P (0.55) + knee toggle (0.3);
# the sim adds the 0.6 kg comb body (simB1fw fw_pivot) on top of this row, so the row = total - 0.6
car_total=5.1+1.6-0.6+0.55+0.3
car=[dict(name='Lift carriage, 640 mm self-aligning comb + nib, pad arm, toggle-locked pad (TC24-50-500P), keeper + GR-07 (total %.2f kg incl. the 0.6 kg comb body in the sim)'%car_total,kg=round(car_total-0.6,3),p=[0.40,0,0.85],d=[0.15,0.64,0.6],g='lift')]
tot=sum(r['kg'] for r in rows)+car_total
json.dump(dict(label='B2',total=round(tot,2),note='total incl. the 0.6 kg comb body',rows=rows,carriage=car,car_total=car_total),open(os.path.join(H,'mass_cgB2.json'),'w'),indent=1)
# donor variant: chair drive units (Rev H 19 kg pair, 318 mm wheels) + 2:1 chain stage (speed cap restored) + 2 x 12 V 18 Ah AGM (10.8 kg) replace the LiFePO4
D=[dict(r) for r in rows]
for r in D:
    if r['name'].startswith('Drive unit'): r['name']=r['name'].replace('PEWM82M-320W gearmotor + spring brake + 3.5:1 chain + 330 mm wheel (B1 mass)','donor chair gearmotor + brake + 2:1 chain stage + 318 mm wheel').replace('Drive unit R','Drive unit R (donor)'); r['kg']=10.3
    if r['name'].startswith('Battery 24 V'): r['name']='Battery = donor AGM pair 2 x 12 V 35 Ah (G8 BAT-D8: 21-30 kg), front bay'; r['kg']=22.0; r['p']=[0.86,0,0.20]
D=[r for r in D if not r['name'].startswith('Ballast')]
totd=sum(r['kg'] for r in D)+car_total
json.dump(dict(label='B2 donor',total=round(totd,2),note='no steel ballast: AGM pair forward replaces it',rows=D,carriage=car,car_total=car_total),open(os.path.join(H,'mass_cgB2_donor.json'),'w'),indent=1)
print('B2 total %.2f kg (ballast %.1f kg at x %.2f); donor %.2f kg'%(tot,kgb,xb,totd))
