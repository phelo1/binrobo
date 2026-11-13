#!/usr/bin/env python3
"""ITER1 cost delta for B on the lean G8 basis (revG/bom_revG8.json conceptB, all-in EUR 4,274.74). Contingency rule as G8:
5 % checked, 12 % estimate, 10 % logistics. Output res/cost_it1.json"""
import json, os
H=os.path.dirname(os.path.abspath(__file__)); B8=json.load(open(os.path.join(H,'..','..','..','bom_revG8.json')))['conceptB']['totals']
ADD=[dict(id='B1-PADACT',item='Pad retract actuator MSW Drive System Europe DSZY4-24-50-100-STD-IP65 (part 00070063): 24 V, 100 mm stroke (40 mm used), 2,500 N dynamic / 4,500 N static, IP65, self-locking ACME screw (Conrad 1386475). Replaces TRU TC24-50-1000 POT (1,000 N < 1,157 N suite peak pad load)',eur=389.00,status='checked-11Nov',k=0.05,
          url='https://www.conrad.com/en/brands/drive-system-europe-by-msw.html'),
     dict(id='B1-PADLS',item='Pad position switch at 40 mm extension (DSZY4-STD has end-of-stroke limits only; IP67 roller-lever switch)',eur=8.0,status='est',k=0.12,url=''),
     dict(id='B1-SW',item='Comb-plate contact switch + pad contact switch: 2 x IP67 roller-lever limit switch on 2 mm sprung travel',eur=16.0,status='est',k=0.12,url=''),
     dict(id='B1-TOF2',item='Second comb ToF (VL53L1X class) at the other tooth end for the dual-ToF yaw measurement (F6)',eur=10.0,status='est',k=0.12,url=''),
     dict(id='B1-KEEP',item='Keeper arm 68 -> 80 mm (same part, re-drawn) (D7)',eur=0.0,status='est',k=0.12,url=''),
     dict(id='B1-COMB',item='Comb tooth narrowed to 160 mm, nib shortened to 8 mm (same plate, re-drawn) (D6)',eur=0.0,status='est',k=0.12,url=''),
     dict(id='B1-PADARM',item='Pad arm moved from the body to the lift carriage (same steel, re-drawn bracket); sprung pad B-3 kept',eur=0.0,status='est',k=0.12,url=''),
     dict(id='B1-BAL',item='Ballast 10 kg steel plate moved from the side arms to the tray floor (same plate, new bolt holes)',eur=0.0,status='est',k=0.12,url=''),
     dict(id='B1-ACT',item='Lift actuator: 250 mm stroke specified (G8 B line already priced the FDI family at the 400 mm figure, upper bound) - no change',eur=0.0,status='checked-11Nov',k=0.05,url='')]
LOG=[dict(id='B1-SHIP',item='Conrad shipping (no other Conrad line in the G8 BOM)',eur=19.99,k=0.10)]
parts=sum(a['eur'] for a in ADD); log=sum(l['eur'] for l in LOG); cont=sum(a['eur']*a['k'] for a in ADD+LOG)
out=dict(basis=B8,added=ADD,logistics=LOG,delta=dict(parts=round(parts,2),logistics=round(log,2),contingency=round(cont,2),all_in=round(parts+log+cont,2)),
         new_all_in=round(B8['all_in']+parts+log+cont,2),lane_prep=dict(item='Rubber kerb ramp or cold-lay asphalt fillet 1:4 per surveyed full-width sharp step > 25 mm',eur_each='20-40',count='unknown until the lane survey',in_bom=False))
json.dump(out,open(os.path.join(H,'res','cost_it1.json'),'w'),indent=1); print(out['delta'],out['new_all_in'])
