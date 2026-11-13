#!/usr/bin/env python3
"""S2 acceptance: simH2 model mass and CG vs params.robot_mass() (tolerance 0.5 kg, 5 mm). Carriage at the height where its
CG is at the params value (z 0.90)."""
import os, sys, json
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H)
import numpy as np, mujoco, simH2 as M
sys.path.insert(0,M.PARAMS); import params as PH
r=PH.robot_mass(); p=M.bin_params('ESE240SL')
S=M.SimB('ESE240SL',p,with_bin=False)
G=M.GEO; q=0.90-(G['car_zero']-G['nib_h']+G['car_dz']); S.d.qpos[S.jq('lift')]=q; mujoco.mj_forward(S.m,S.d)
tug=S.bid['tug']; m=float(S.m.body_subtreemass[tug]); c=S.d.subtree_com[tug]-S.d.xpos[tug]
out=dict(params=dict(m=round(r['m'],3),x=round(r['x'],4),z=round(r['z'],4)),model=dict(m=round(m,3),x=round(float(c[0]),4),y=round(float(c[1]),4),z=round(float(c[2]),4)),lift_q=round(q,3))
out['dm_kg']=round(m-r['m'],3); out['dx_mm']=round(1000*(c[0]-r['x']),1); out['dz_mm']=round(1000*(c[2]-r['z']),1)
out['PASS']=bool(abs(out['dm_kg'])<=0.5 and abs(out['dx_mm'])<=5 and abs(out['dz_mm'])<=5)
# the bin itself (corrected hull, full 240 L at 110 kg): CG behind the front wall and above the base
B=M.bin_params('ESE240SL'); B['fill']=110-13.0; S2=M.SimB('ESE240SL',B)
bb=S2.bid['bin']; cb=S2.d.subtree_com[bb]; mb=float(S2.m.body_subtreemass[bb])
out['bin_ESE240SL_110']=dict(m=round(mb,2),cg_behind_front_wall_m=round(float(B['xlip']-(cb[0]-S2.d.xpos[bb][0])),4),cg_above_ground_m=round(float(cb[2]),4))
json.dump(out,open(os.path.join(H,'res','mass_check_H2.json'),'w'),indent=1); print(json.dumps(out))
