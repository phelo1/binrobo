# iter1 calibration smoke (not a gate run): nominal grab (+ optional flat set-down) per bin. usage: CGB_GEO='{...}' smoke_it1.py [rel]
import os,sys,json,time,numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..')); sys.path.insert(0,os.path.join(H,'..','..','g6'))
import simB_it1 as B
from bins_g5 import BINS
rel=len(sys.argv)>1 and sys.argv[1]=='rel'; bins=sys.argv[2].split(',') if len(sys.argv)>2 else ['WEB140','ESE140CL','ESE240SL','ESE240CL','ESE240SL250']
for b in bins:
    for full in (True,False):
        t=time.time(); p=B.bin_params(b); p['fill']=BINS[b]['fill_full'] if full else 0.0
        S=B.SimB(b,p,tug_pose=B.start_pose(p)); R=B.RunnerB(S); g=B.grab(R)
        o=dict(bin=b,full=full,res=g['result'],tilt=g.get('bin_tilt_abs'),clear=g.get('wheel_clear_mm'),zc=g.get('zc'),qa=g.get('q_app'),dock=g.get('dock'))
        if rel and g['result']=='success':
            sd=B.set_down(R); o.update(sd=sd,tilt_end=round(S.bin_tilt_abs(),1))
        print(json.dumps(o),R.events[-3:],round(time.time()-t,1),flush=True)
