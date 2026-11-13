#!/usr/bin/env python3
"""smoke / calibration: nominal grab (+ optional set-down) per bin. usage: smoke.py <simmodule> <BIN,BIN> <full|empty|both> [sd]"""
import os, sys, json, time
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..','..','g6'))
import importlib; B=importlib.import_module(sys.argv[1]); from bins_g5 import BINS
fills=['full','empty'] if sys.argv[3]=='both' else [sys.argv[3]]
for b in sys.argv[2].split(','):
    for fl in fills:
        t=time.time(); p=B.bin_params(b); p['fill']=BINS[b]['fill_full'] if fl=='full' else 0.0
        S=B.SimB(b,p,tug_pose=B.start_pose(p)); R=B.RunnerB(S); g=B.grab(R)
        keys=('result','dock','zc','q_app','lift_rise_N','seat_switch','wheel_clear_mm','bin_tilt_abs','seated','why','padF_at_loadon','claim','wheel_cam')
        o={k:g.get(k) for k in keys if k in g}
        S.contacts(); o['pad_N']=round(S.pair('padg','binhull')); o['lift_N']=round(S.lift_force())
        if len(sys.argv)>4 and g['result']=='success':
            sd=B.set_down(R); o['sd']={k:sd.get(k) for k in ('released','hold','tilt_before_withdraw','nib_clear_m')}; o['tilt_end']=round(S.bin_tilt_abs(),1)
        print(b,fl,json.dumps(o),'ev',R.events[-3:],'%.0fs'%(time.time()-t),flush=True)
