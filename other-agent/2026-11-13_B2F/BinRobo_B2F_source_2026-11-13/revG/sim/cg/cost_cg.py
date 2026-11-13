#!/usr/bin/env python3
"""Rough parts-cost delta of A' and B against the realistic G6 baseline (cold-eye review: about EUR 4,700 incl. LA36, missing items,
safety relay and contingency). EUR incl. VAT where a shop price exists; 'est' = engineering estimate, not quoted. Output res/cost_cg.json"""
import json, os
H=os.path.dirname(os.path.abspath(__file__))
VAT=1.23
BASE=4700
common=[('Drive: donor powerchair removed (M5: no donor)',-350,'bom_revG6.csv G4'),
        ('2 x MY1016ZL-75 24 V 250 W gearmotor with EM brake (GBP 44.92 each, 1-12 pcs)',round(2*44.92*1.17*VAT),'alibaba.com listing (fetched 11 Nov 2026); VAT/import added'),
        ('2 x 13 in wheel + hub for 17 mm keyed shaft',80,'est'),('2 x 200 mm swivel castors (G6 took them from the donor)',50,'est'),('shipping/duty for the above',40,'est')]
A=[("Sprung load-transfer pad: 2 rollers, slide, 2 die springs, bracket",55,'est'),("Kingpin centring spring-damper (torsion bar + gas damper)",60,'est'),
   ("Tapered-roller trailer hub replacing the M16 kingpin kit (net)",25,'est'),("Upper wheel-stop roller 150 mm",15,'est'),
   ("Wheel-stop bar retract cam + linkage (tow)",45,'est'),("Float clamp (2nd pawl + sealed 24 V solenoid)",30,'est'),
   ("Wheel-on-ground load sensor",20,'est'),("GR-08S as a sealed IP65 solenoid + pawl sensor (missing in the G6 BOM)",30,'est')]
B=[('LINAK LA36 6.8 kN tilt actuator removed',-1058,'review M6: EUR 1,058.45 wetterwinkel.nl'),
   ('TiMOTION TA23 4,000 N push/pull lift actuator, 350 mm (EUR 236.22 ex VAT)',round(236.22*VAT),'shop.atti.it (search excerpt, 11 Nov 2026)'),
   ('Kingpin kit, yaw-lock pin + encoder, float ratchet, pawls, release cord, rest stop, lid finger, GR-G6 hook upgrade, G11 hook carriage removed',-(19+18+6+12+4+10+8+15+25),'bom_revG6.csv'),
   ('GR-08S not needed (no ratchet)',0,'-'),('Lifter: 2 x 1 m linear rail + 4 blocks',90,'est'),('Comb tooth/nib (laser) + keeper fingers; GR-07 cam motor reused as keeper drive',20,'est'),
   ('Sprung lower pad (2 die springs + bracket)',35,'est'),('ToF sensor for the lip root (VL53L1X class)',10,'est'),
   ('Fabrication: no rear frame / tilting mast / funnel arms; adds side arms + lifter mast (net)',-60,'est +/-150'),('Ballast: steel in the arms instead of 2 jerricans',-7,'est')]
def tot(L): return sum(x[1] for x in L)
c=tot(common); a=tot(A); b=tot(B)
cont=0.10
out=dict(baseline_G6_realistic=BASE,common_drive_change=c,A_items=a,B_items=b,
         A_total=round(BASE+(c+a)*(1+cont)),B_total=round(BASE+(c+b)*(1+cont)),contingency_on_deltas=cont,
         A_option_TA23_instead_of_LA36=round(BASE+(c+a-1058+258.54*VAT)*(1+cont)),
         lines=dict(common=common,A=A,B=B))
out['B_minus_A']=out['B_total']-out['A_total']; out['B_minus_A_same_actuator_class']=out['B_total']-out['A_option_TA23_instead_of_LA36']
json.dump(out,open(os.path.join(H,'res','cost_cg.json'),'w'),indent=1); print(json.dumps({k:v for k,v in out.items() if k!='lines'},indent=1))
