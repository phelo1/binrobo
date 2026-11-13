#!/usr/bin/env python3
"""Cost delta of A' and B against the G7 BOM (revG/bom_revG7.csv, ALL-IN EUR 8,218.08 incl. logistics + risk-weighted contingency).
Removed lines use the G7 eur_G7 value; added lines are engineering estimates ('est') unless a source is given. 10 % contingency on deltas.
Output res/cost_cg_g7.json"""
import csv, json, os
H=os.path.dirname(os.path.abspath(__file__)); BOM=os.path.join(H,'..','..','bom_revG7.csv')
L={r['id']:r for r in csv.DictReader(open(BOM)) if r['id']}
g=lambda i: float(L[i]['eur_G7'])
BASE=8218.08; VAT=1.23; CONT=0.10
A=[("A' sprung load-transfer pad: 2 rollers, slide, 2 die springs, bracket",55,'est'),
   ("A' yaw centring spring-damper 859 N m/rad + 280 N m s/rad (torsion bar + gas damper)",60,'est'),
   ("Tapered-roller trailer hub replacing the M16 kingpin kit RF-10/11/12 (net)",25,'est'),
   ("Upper wheel-stop roller 150 mm (sim G6_SB2, not in G7 CAD/BOM)",15,'est'),
   ("Wheel-stop bar 60 mm retract cam + linkage (tow)",45,'est'),
   ("Float clamp in tow: 2nd pawl + sealed 24 V solenoid + driver channel",30,'est'),
   ("Wheel-on-ground load sensor for the chase stand-up interlock (G13 switch is not a load sensor)",20,'est')]
Brm=['G10','RF-10/11/12','G8','YS-G7','G11','K1','K3','K4','GR-10','GR-08','GR-08S','GR-08D','GR-G6','IND-OPEN','SHIP-LANDA']
B=[(('removed '+i+': '+L[i]['item'][:70]),-g(i),'bom_revG7.csv') for i in Brm]
B+=[('Lift actuator: Ewellix CAHB-20-F3E carried over as the vertical lift (4,500 N vs 1.2 kN static / 2.4 kN sim peak), shorter stroke',g('G10'),'bom_revG7.csv G10 price (stroke code to quote)'),
    ('Lifter: 2 x 1 m linear rail + 4 carriages',90,'est'),
    ('Comb tooth with 12 mm nib (laser) + keeper fingers; GR-07 cam motor reused as keeper drive',20,'est'),
    ('Sprung lower pad (2 die springs + bracket)',35,'est'),('Lip-root ToF sensor (VL53L1X class) + nib seat switch',15,'est'),
    ('Fabrication net: no rear frame / tilting mast / funnel arms; adds side arms, lifter mast, 0.80 m track axle beam',-60,'est +/-150'),
    ('Ballast: steel plate in the arms instead of BT-01 jerricans + sand',-7,'est')]
opt=[('Option: TiMOTION TA23 4,000 N instead of CAHB-20 (EUR 236.22 ex VAT; IP/cold rating NOT verified)',round(236.22*VAT-g('G10'),2),'shop.atti.it search excerpt')]
tot=lambda X: round(sum(x[1] for x in X),2)
a=tot(A); b=tot(B)
out=dict(baseline_G7_allin=BASE,A_delta_parts=a,B_delta_parts=b,A_delta_with_cont=round(a*(1+CONT)),B_delta_with_cont=round(b*(1+CONT)),
         A_total=round(BASE+a*(1+CONT)),B_total=round(BASE+b*(1+CONT)),B_minus_A=round((b-a)*(1+CONT)),
         B_option_TA23_total=round(BASE+(b+opt[0][1])*(1+CONT)),fab_uncertainty_eur=150,lines=dict(A=A,B=B,B_option=opt),
         note='Both concepts keep the G7 drive (PEWM-39 + Roboteq), safety chain, sensing and dock unchanged; only mechanism lines differ.')
json.dump(out,open(os.path.join(H,'res','cost_cg_g7.json'),'w'),indent=1); print(json.dumps({k:v for k,v in out.items() if k!='lines'},indent=1))
for x in B: print(x)
