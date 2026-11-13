#!/usr/bin/env python3
"""B-SD2 (POST-FREEZE firmware change, reported beside the frozen B results, never instead of them).
Root cause of the frozen B set-down STUCK/HOLD (res/dbg_B3_*.txt): the 'lift force < 15 %' light test is fooled because the
body-mounted pad (~700 N preload) holds the bin by friction, so the comb stops while the bin is still 20-30 mm up; the bin then
drops back onto the nib and is dragged on withdraw. SD2 lowers by POSITION: comb to the recorded pick-up height (bin wheels on the
ground), keeper opens, comb a further 35 mm down, upright interlock (tilt <= 4 deg), then the same 0.6 m forward withdraw.
Hardware unchanged. usage: sd2_wrap.py runB.py rel <BIN> <case> <full|empty>   -> res/B_rel_..._SD2.json"""
import os, sys, runpy, builtins, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H)
import simB_cg as B
FW2=os.environ.get('SD_FW2')=='1'   # approach height referenced to the bin's wheel size: +25 mm for 250 mm wheels (ToF/camera lip height)
if FW2 and len(sys.argv)>3 and sys.argv[2]=='rel':
    from bins_g5 import BINS as _BN
    B.GEO['approach_nib_z']+=(_BN[sys.argv[3]]['wheel']-0.200)/2
V3=os.environ.get('SD_VARIANT')=='3'   # SD3: keeper stays CLOSED until the comb is 10 mm below the pick-up height (bin pressed onto its wheels), then opens
_open=builtins.open
def op(f,mode='r',*a,**k):
    if isinstance(f,str) and 'w' in mode and f.endswith('.json') and os.sep+'res'+os.sep in f: f=f[:-5]+('_SD3' if V3 else '_SD2')+('F' if FW2 else '')+'.json'
    return _open(f,mode,*a,**k)
builtins.open=op
def set_down2(R):
    S=R.s; out={}
    q0=S.lift_q(); zc=max(0.0,q0-B.GEO['lift_extra'])
    R.phase='10 SD2: comb lowers by position to the pick-up height'; R.ramp_lift(zc-(0.010 if V3 else 0.0),0.02,Tmax=15); R.run_for(0.5)
    out['wheel_clear_at_zc_mm']=round(S.wheel_clear()*1000,1)
    R.phase='11 SD2: keeper opens, comb a further 35 mm down'; S.keeper_cmd=6.0; R.run_for(0.6)
    R.ramp_lift(max(0.0,zc-0.035),0.02,Tmax=10); R.run_for(0.8)
    out['tilt_before_withdraw']=round(S.bin_tilt_abs(),1); out['wheel_clear_before_withdraw_mm']=round(S.wheel_clear()*1000,1)
    if S.bin_tilt_abs()>4.0:
        out.update(released=False,hold=True,why='bin not upright before withdraw'); R.ev('set-down interlock HOLD'); return out
    R.phase='12 Drive forward 0.6 m: comb withdraws'; x0=S.d.xpos[S.bid['tug']].copy(); psi=S.rpy()[2]
    R.ctrl_fn=B.heading_hold(R,0.15,psi); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=0.6,10.0); R.ctrl_fn=None; R.hold()
    R.phase='13 Bin standing alone'; R.run_for(3.0)
    q=S.nib_in_bin(); xbt=S.p['bar_x']-S.p['cb']
    out.update(released=bool(q[0]-xbt>0.10),nib_clear_m=round(float(q[0]-xbt),3),sd='SD3' if V3 else 'SD2')
    return out
B.set_down=set_down2
script=sys.argv[1]; sys.argv=sys.argv[1:]
runpy.run_path(os.path.join(H,script),run_name='__main__')
