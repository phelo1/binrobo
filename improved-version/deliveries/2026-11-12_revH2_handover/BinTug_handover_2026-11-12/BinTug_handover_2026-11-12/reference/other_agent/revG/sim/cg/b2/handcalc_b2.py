#!/usr/bin/env python3
"""B2 hand calcs, same method as it1/handcalc_it1.py (support polygon drive (0,+/-0.40), castors (0.90,+/-0.28), anti-tip (-0.36,+/-at_y)),
carry height +100 mm (iter1). Adds: ballast sweep for castor lift-off, drive traction/torque on 12 %, the 40 mm step (edge geometry),
comb receiver stress (gate-model ledge 30 x 8 mm HDPE, load at the 26 mm rim), frame tube stress, toggle actuator force.
usage: handcalc_b2.py <massfile> [tag] -> res/handcalc_b2<tag>.json"""
import json, math, os, sys
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','..','g6'))
from bins_g5 import BINS
g=9.81; th=math.atan(0.12); s,c=math.sin(th),math.cos(th)
def bin_cg(binkey,kg):
    B=BINS[binkey]; bx=B['bar_x'][0]; cb=B['cb'][0]; xbt=bx-cb; sc=B['D']/0.74; bh=B['bar_abs'][0]-B['wheel']/2
    me=B['empty']-1.4-1.8; mf=kg-B['empty']; ce=(xbt-0.32*sc,0.42*bh/0.93); cf=(xbt-0.33*sc,0.38*bh/0.93)
    m=me+mf+3.2; x=(me*ce[0]+mf*cf[0]+3.2*xbt)/m; z=(me*ce[1]+mf*cf[1]+3.2*bh)/m
    return x,z,B
def rows_of(massf,ballast=None):
    M_=json.load(open(massf)); rws=[dict(r) for r in M_['rows']]+[dict(M_['carriage'][0],kg=M_.get('car_total',M_['carriage'][0]['kg']))]
    if ballast is not None:
        rws=[r for r in rws if not r['name'].startswith('Ballast')]
        if ballast[0]>0: rws.append(dict(name='Ballast',kg=ballast[0],p=[ballast[1],0,0.15]))
    return rws
def stab(rws,lift=0.090,rw=0.165,aty=0.42):
    mt=sum(r['kg'] for r in rws); xt=sum(r['kg']*r['p'][0] for r in rws)/mt; zt=sum(r['kg']*r['p'][2] for r in rws)/mt
    out=[]
    for kg in (110,60,0):
        if kg:
            xb,zb,B=bin_cg('ESE240SL',kg); x_axle=0.285-0.004-(B['bar_x'][0]-B['cb'][0]); Xb=x_axle+xb; Zb=B['wheel']/2+lift+zb
        else: Xb=Zb=0.0
        M=mt+kg; X=(mt*xt+kg*Xb)/M; Z=(mt*zt+kg*Zb)/M
        def tip_side(px,py,qx,qy):
            L=math.hypot(qx-px,qy-py); d=abs((qx-px)*(py-0)-(px-X)*(qy-py))/L; return math.degrees(math.atan(d/Z))
        Nd=M*g*(0.90-X)/0.90; Nd_up=M*g*(c*(0.90-X)-s*Z)/0.90
        resist=M*g*s+2*0.06*300*0.165/rw+2*0.06*200*0.1/0.1
        out.append(dict(bin_kg=kg,M=round(M,1),cg_x=round(X,3),cg_z=round(Z,3),tip_lateral_deg=round(tip_side(0,0.40,0.90,0.28),1),
                        tip_forward_over_castors_deg=round(math.degrees(math.atan((0.90-X)/Z)),1),
                        castor_liftoff_about_drive_axle_deg=round(math.degrees(math.atan(X/Z)),1),
                        rear_tip_on_antitip_deg=round(math.degrees(math.atan((X+0.36)/Z)),1),
                        drive_N_flat=round(Nd),castor_N_flat=round(M*g-Nd),drive_N_12up=round(Nd_up),castor_N_12up=round(M*g*c-Nd_up),mu_req_12=round(resist/Nd_up,3),
                        torque_per_wheel_12_Nm=round(resist*rw/2,1),torque_x1p25=round(1.25*resist*rw/2,1)))
    return dict(tug_kg=round(mt,2),tug_cg=[round(xt,3),round(zt,3)],cases=out)
if __name__=='__main__':
    massf=sys.argv[1]; tag=sys.argv[2] if len(sys.argv)>2 else ''; rw=0.159 if 'donor' in tag else 0.165
    R=dict(massfile=os.path.relpath(massf,H),design=stab(rows_of(massf),rw=rw))
    R['ballast_sweep_110kg']=[dict(kg=k,x=x,**{a:b for a,b in stab(rows_of(massf,(k,x)),rw=rw)['cases'][0].items() if a in('M','castor_liftoff_about_drive_axle_deg','mu_req_12','castor_N_12up')},tug_kg=stab(rows_of(massf,(k,x)),rw=rw)['tug_kg']) for k in (0,3,5,8,10) for x in (0.85,1.00)]
    # 40 mm full-width step: edge geometry for a driven wheel with free-rolling castors (quasi-static): mu_edge = tan(a), T = W_w r sin(a)
    a=math.acos((rw-0.040)/rw); Ww=R['design']['cases'][0]['drive_N_flat']/2
    R['step40']=dict(contact_angle_deg=round(math.degrees(a),1),mu_edge_needed=round(math.tan(a),2),wheel_load_N=round(Ww),torque_needed_Nm=round(Ww*rw*math.sin(a),1),
                     torque_cap_frozen_Nm=60.0,max_wheel_load_for_60Nm_N=round(60/(rw*math.sin(a))),
                     note='friction need is geometric (independent of load and CG); interlock (lugs) removes it but the torque need stays > the 60 N m frozen cap and the real motor (53 N m at 25.8 A)')
    for D_ in (0.33,0.40,0.56,0.70):
        r_=D_/2; a_=math.acos((r_-0.04)/r_); R['step40']['wheel_%d'%round(D_*1000)]=dict(mu=round(math.tan(a_),2),T_Nm=round(Ww*r_*math.sin(a_),1))
    json.dump(R,open(os.path.join(H,'res','handcalc_b2%s.json'%tag),'w'),indent=1)
    d=R['design']; print(tag or 'B2',d['tug_kg'],d['tug_cg'],[(c_['bin_kg'],c_['castor_liftoff_about_drive_axle_deg'],c_['tip_lateral_deg'],c_['tip_forward_over_castors_deg'],c_['rear_tip_on_antitip_deg'],c_['mu_req_12'],c_['torque_per_wheel_12_Nm'],c_['castor_N_12up']) for c_ in d['cases']])
    for r in R['ballast_sweep_110kg']: print(r)
    print(R['step40'])
