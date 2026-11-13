#!/usr/bin/env python3
"""G6 sim sanity checks at the operating mass file (default M110h): model mass vs mass file, static ground reaction vs weight, drive/caster split
vs a hand moment balance from the mass-file CG, max contact penetration, solref/timestep ratio, actuator limits. Also reports the legacy
ballast_x=0.70 placement for comparison.  usage: sanity_g6.py [label] -> ../results_G6_sanity_<label>.json"""
import json, os, sys, math, numpy as np, mujoco
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import sim_g5
from sim_g5 import Sim, TXm, load_rows, composite
from tow_g5 import nominal
lab=sys.argv[1] if len(sys.argv)>1 else 'M110h'; mf='mass_g6_%s.json'%lab
out=dict(label=lab)
M=json.load(open(os.path.join(HERE,mf))); out['massfile_total_kg']=round(sum(r['kg'] for r in M['rows']),2)
for leg in (False,True):
    rows=load_rows(mf,99,0.70 if leg else None); m,c,_=composite(rows,np.zeros(3))
    out['cg_from_axle_%s'%('legacy' if leg else 'fixed')]=dict(x_m=round(float(c[0]),3),z_m=round(float(c[2]),3))
def settle(with_bin, T=3.0):
    kw=nominal('ESE240SL'); S=Sim(grabber='GH',gh='B2',ghp={k:v for k,v in json.load(open(os.path.join(HERE,'combos_g6.json')))['H3'].items() if not k.startswith('_')},fill=0.0,mu=0.6,massfile=mf,ballast=99,
            tug_pose=(TXm+0.60+(kw['wheel_r']-0.10)+(0 if with_bin else 3.0),0.0,0.0),**{k:v for k,v in kw.items() if k not in('_reapp',)})
    for k in ('_claim_and','_guard','_reapp'): pass
    S.set_brake(True)
    for a in (0,1): S.m.actuator_forcerange[a]=[-150,150]
    n=int(T/S.m.opt.timestep)
    for i in range(n): S.pre_step(); mujoco.mj_step(S.m,S.d)
    g=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_GEOM,'ground'); f=np.zeros(6); Fz=0.0; pen=0.0
    for i in range(S.d.ncon):
        c=S.d.contact[i]; pen=min(pen,c.dist)
        if g in (c.geom1,c.geom2): mujoco.mj_contactForce(S.m,S.d,i,f); Fz+=f[0]
    C=S.contacts(); tot=float(sum(S.m.body_mass))
    return S,dict(model_total_kg=round(tot,2),tug_kg=round(S.tug_mass,2),bin_kg=round(S.bin_mass,2),ground_Fz_N=round(Fz,1),weight_N=round(tot*9.81,1),
                  err_pct=round(100*(Fz-tot*9.81)/(tot*9.81),2),drive_N=round(C['driveL']+C['driveR'],1),caster_N=round(C['casterL']+C['casterR'],1),
                  max_penetration_mm=round(-pen*1000,2))
S,o=settle(False); out['tug_alone_static']=o
cg=out['cg_from_axle_fixed']['x_m']; xc=0.84-0.05; W=o['tug_kg']*9.81
out['tug_alone_hand_calc']=dict(caster_x_m=xc,drive_N=round(W*(xc-cg)/xc,1),caster_N=round(W*cg/xc,1),note='wheels+castors carry everything; tyre contact at axle x')
S2,o2=settle(True); out['tug_and_empty_bin_static']=o2
m=S.m; out['model']=dict(timestep=m.opt.timestep,integrator=int(m.opt.integrator),cone=int(m.opt.cone),noslip_iterations=m.opt.noslip_iterations,
     default_geom_solref=[0.008,1],solref_over_dt=round(0.008/m.opt.timestep,1),pawl_limit_solref=0.004,pawl_over_dt=round(0.004/m.opt.timestep,1),
     drive_torque_limit_Nm=60,brake_torque_limit_Nm=150,brake_kv=20000,wheel_r_m=0.165,max_tractive_N=round(2*60/0.165),max_brake_force_N=round(2*150/0.165))
json.dump(out,open(os.path.join(HERE,'..','results_G6_sanity_%s.json'%lab),'w'),indent=1)
print(json.dumps(out,indent=1))
