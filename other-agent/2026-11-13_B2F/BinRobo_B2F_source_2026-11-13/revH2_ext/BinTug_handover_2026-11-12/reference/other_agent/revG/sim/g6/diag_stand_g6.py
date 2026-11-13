#!/usr/bin/env python3
"""G6 stand-up time series: runs tow_g5 release test <BIN> <test> with current env, logs every 0.2 s from stand-up start:
mast, bin rel tilt, tug pitch, bin world tilt (rel+pitch), float vs grab, contact normal forces (castors, drive, bin wheels, stop bar, spine, flares, hook).
usage: diag_stand_g6.py BIN TEST TAG GHP_JSON -> diag_stand_<BIN>_<TEST>_<TAG>.json"""
import json, os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import scen_g5, tow_g5
binkey,test,tag=sys.argv[1],sys.argv[2],sys.argv[3]
SER=[]; orig=scen_g5.stand_up
def su(R):
    S=R.s; prev=R.step; fg=getattr(S,'_float_grab',0.0)
    def st():
        prev()
        if R.i%int(0.2/R.dt)==0:
            C=S.contacts(); p=S.rpy()[1]; r=S.bin_tilt_rel()
            SER.append(dict(t=round(R.t,2),ph=R.phase[:30],mast=round(S.tilt(),2),rel=round(r,2),pitch=round(p,2),world=round(r+p,2),babs=round(S.bin_tilt_abs(),2),
                float_mm=round(1000*(float(S.d.qpos[S.jq('float')])-fg),1),rat=bool(getattr(S,'ratchet_on',False)),
                **{k:round(C[k],0) for k in ('casterL','casterR','driveL','driveR','binwheelL','binwheelR','stopbar','stopL','stopR','spine','flareL','flareR','hookF') if k in C}))
    R.step=st; orig(R)
scen_g5.stand_up=su
ghp=json.loads(sys.argv[4])
o,R=tow_g5.run(binkey,test,'B2',ghp)
json.dump(dict(out={k:v for k,v in o.items() if k!='events'},events=R.events,series=SER),open(os.path.join(HERE,'diag_stand_%s_%s_%s.json'%(binkey,test,tag)),'w'),indent=0,default=str)
for e in SER[::3]: print(e)
print(o.get('ok'),o.get('release'))
