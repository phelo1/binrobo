#!/usr/bin/env python3
"""ITER1 hand calcs for B: stability vs ballast position (G6 B mass_cgB vs iter1 mass_cgB1), drive normal load and mu_req on 12 %,
torque per wheel. Same method as ../handcalc_cg.py (support polygon: drive (0,+/-0.40), castors (0.90,+/-0.28), anti-tip (-0.36,+/-0.44)).
Carry height: iter1 lifts +100 mm after load-on (G6: +75 mm). Output res/handcalc_it1.json"""
import json, math, os, sys
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','..','g6'))
from bins_g5 import BINS
g=9.81; th=math.atan(0.12); s,c=math.sin(th),math.cos(th); rw=0.165
def bin_cg(binkey,kg):
    B=BINS[binkey]; bx=B['bar_x'][0]; cb=B['cb'][0]; xbt=bx-cb; sc=B['D']/0.74; bh=B['bar_abs'][0]-B['wheel']/2
    me=B['empty']-1.4-1.8; mf=kg-B['empty']; ce=(xbt-0.32*sc,0.42*bh/0.93); cf=(xbt-0.33*sc,0.38*bh/0.93)
    m=me+mf+3.2; x=(me*ce[0]+mf*cf[0]+3.2*xbt)/m; z=(me*ce[1]+mf*cf[1]+3.2*bh)/m
    return x,z,B
def stab(massf,lift,ballast_x=None):
    M_=json.load(open(massf)); rws=[dict(r) for r in M_['rows']+M_['carriage']]
    if ballast_x is not None:
        for r in rws:
            if r['name'].startswith('Ballast'): r['p']=[ballast_x,0,0.13]
    mt=sum(r['kg'] for r in rws); xt=sum(r['kg']*r['p'][0] for r in rws)/mt; zt=sum(r['kg']*r['p'][2] for r in rws)/mt
    out=[]
    for kg in (110,60,0):
        if kg:
            xb,zb,B=bin_cg('ESE240SL',kg); x_axle=0.285-0.004-(B['bar_x'][0]-B['cb'][0]); Xb=x_axle+xb; Zb=B['wheel']/2+lift+zb
        else: Xb=Zb=0.0
        M=mt+kg; X=(mt*xt+kg*Xb)/M; Z=(mt*zt+kg*Zb)/M
        def tip_side(px,py,qx,qy):
            L=math.hypot(qx-px,qy-py); d=abs((qx-px)*(py-0)-(px-X)*(qy-py))/L; return math.degrees(math.atan(d/Z))
        Nd=M*g*(0.90-X)/0.90                                   # flat static drive-axle load
        Nd_up=M*g*(c*(0.90-X)-s*Z)/0.90                        # facing uphill (castors uphill), drive-axle load on 12 %
        resist=M*g*s+2*0.06*300*0.165/rw+2*0.06*200*0.1/0.1      # grade + sim tyre/castor frictionloss (bin carried: no bin-wheel term)
        out.append(dict(bin_kg=kg,M=round(M,1),cg_x=round(X,3),cg_z=round(Z,3),tip_lateral_deg=round(tip_side(0,0.40,0.90,0.28),1),
                        tip_forward_over_castors_deg=round(math.degrees(math.atan((0.90-X)/Z)),1),
                        castor_liftoff_about_drive_axle_deg=round(math.degrees(math.atan(X/Z)),1),
                        rear_tip_on_antitip_deg=round(math.degrees(math.atan((X+0.36)/Z)),1),
                        drive_N_flat=round(Nd),castor_N_flat=round(M*g-Nd),drive_N_12up=round(Nd_up),mu_req_12=round(resist/Nd_up,3),
                        torque_per_wheel_12_Nm=round(resist*rw/2,1),torque_x1p25=round(1.25*resist*rw/2,1)))
    return dict(tug_kg=round(mt,1),tug_cg=[round(xt,3),round(zt,3)],cases=out)
R=dict(G6_B=stab(os.path.join(H,'..','mass_cgB.json'),0.065),ITER1_B1=stab(os.path.join(H,'mass_cgB1.json'),0.090))
R['ballast_sweep_110kg']=[dict(ballast_x=bx,**{k:v for k,v in stab(os.path.join(H,'mass_cgB1.json'),0.090,bx)['cases'][0].items() if k in ('castor_liftoff_about_drive_axle_deg','mu_req_12','drive_N_12up','tip_forward_over_castors_deg')}) for bx in (0.05,0.25,0.45,0.65,0.85,1.0)]
json.dump(R,open(os.path.join(H,'res','handcalc_it1.json'),'w'),indent=1)
for k in ('G6_B','ITER1_B1'): print(k,R[k]['tug_kg'],R[k]['tug_cg'],[ (c['bin_kg'],c['castor_liftoff_about_drive_axle_deg'],c['tip_lateral_deg'],c['tip_forward_over_castors_deg'],c['rear_tip_on_antitip_deg'],c['mu_req_12'],c['torque_per_wheel_12_Nm'],c['torque_x1p25']) for c in R[k]['cases']])
for r in R['ballast_sweep_110kg']: print(r)
