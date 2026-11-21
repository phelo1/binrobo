#!/usr/bin/env python3
"""Writes h2/simB2hx.py = the other agent's h2/simB2h.py with two switchable changes, both OFF by default (then the model is identical):
  X_LIFT_RANGE=<m>   lift travel (their file fixes it at 0.25 m after reading CGB_GEO)
  X_ROCKER=1         castor pair on a rocker: both castor forks hang from a beam hinged to the frame about the fore-aft axis on the centre line,
                     with stops at +/-X_ROCK_DEG (default 5 deg = about 24 mm at each castor), pivot X_ROCK_Z above the ground (default 0.20 m),
                     beam mass X_ROCK_M (default 1.5 kg, as in all runs up to 13 Nov 19:00; 5.46 kg = beam + mounting plates + pivot housing as drawn)
X_ROCK_M, X_DOCK_TRIES and X_DOCK_DYMAX were added on 14 Nov (see below); with them unset the model is the one used for every result up to 13 Nov.
The fixed pad needs no change: their model already takes CGB_GEO='{"pad_ret":0.0}' ("0 = fixed pad").
usage: make_simB2hx.py <cg_dir>"""
import sys, os
cg = sys.argv[1]; src = open(os.path.join(cg, 'h2', 'simB2h.py')).read()
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:60]); return s.replace(a, b)
s = src
s = rep(s, "GEO['lift_range']=0.25", "GEO['lift_range']=float(os.environ.get('X_LIFT_RANGE','0.25'))\nROCK=os.environ.get('X_ROCKER')=='1'; ROCK_DEG=float(os.environ.get('X_ROCK_DEG','5')); ROCK_Z=float(os.environ.get('X_ROCK_Z','0.20')); ROCK_M=float(os.environ.get('X_ROCK_M','1.5')); CTRAIL=float(os.environ.get('X_CAST_TRAIL','0.05')); CROWN=float(os.environ.get('X_CAST_CROWN','0')); CTORS=float(os.environ.get('X_CAST_TORS','0.008')); CASTW=float(os.environ.get('X_CAST_W','0.025')); CSHD=float(os.environ.get('X_CAST_SHOULDER','0'))\ndef CSH(side,fr,cr): return '' if (CSHD<=0 or CASTW>=0.025) else ''.join('<geom name=\"castsh%s%d\" type=\"cylinder\" size=\"%g %g\" pos=\"0 %g 0\" euler=\"90 0 0\" friction=\"%s\" condim=\"3\" contype=\"0\" conaffinity=\"1\"/>'%(side,k,cr-CSHD,(0.025-CASTW)/2,sg*(CASTW+(0.025-CASTW)/2),fr) for k,sg in ((0,1),(1,-1)))")
# X_CAST_SHOULDER=<m>: with X_CAST_W below 0.025, two shoulder rings fill the wheel out to its 50 mm width, lower than the centre strip by this much
#   (0.003 used): the wheel still touches flat ground on the narrow strip, but it bridges the side edge of a hole like a 50 mm tyre. OFF by default (added 14 Nov)
# X_CAST_W=<m>: half-width of the castor tread that touches the ground (their model: 0.025, a flat 50 mm tread). A round-profile tyre touches on a narrow strip; OFF by default (added 14 Nov)
# X_CAST_TRAIL=<m>: castor swivel offset (their model: 0.05). For trying a castor with a shorter offset; OFF by default (added 14 Nov)
s = rep(s, '<body name="cwheel{side}" pos="-0.05 0 ', '<body name="cwheel{side}" pos="{-CTRAIL} 0 ')
# X_CAST_CROWN=<m>: castor tyre with a round (crowned) tread instead of the flat 50 mm tread of their model: the wheel becomes an ellipsoid of the same
#   200 mm diameter whose half-axis along the axle is this value (0.06 gives a crown radius of 36 mm), touching the ground at one point, with
#   spin friction about that point (contact dimension 4, coefficient X_CAST_TORS, default 8 mm = the radius of the contact patch). OFF by default (added 14 Nov)
s = rep(s, '<geom name="caster{side}" type="cylinder" size="{G[\'cr\']} 0.025" {wq} friction="{fr}" condim="3"',
        '<geom name="caster{side}" {("type=\\"ellipsoid\\" size=\\"%g %g %g\\"" % (G[\'cr\'], G[\'cr\'], CROWN)) if CROWN > 0 else ("type=\\"cylinder\\" size=\\"%g %g\\"" % (G[\'cr\'], CASTW))} {wq} friction="{fr if CROWN <= 0 else "%s %g 0.0001" % (mu, CTORS)}" condim="{4 if CROWN > 0 else 3}"')
s = rep(s, ' contype="0" conaffinity="1"/></body></body>\'\'\'', ' contype="0" conaffinity="1"/>{CSH(side,fr,G[\'cr\'])}</body></body>\'\'\'')
s = rep(s, '''<body name="cfork{side}" pos="{G['cx']} {s*G['cy']} 0.1">''', '''<body name="cfork{side}" pos="{0.0 if ROCK else G['cx']} {s*G['cy']} {0.1-ROCK_Z if ROCK else 0.1}">''')
s = rep(s, "{caster('L',1)}{caster('R',-1)}", '''{('<body name="rocker" pos="%s 0 %s"><joint name="rock" type="hinge" axis="1 0 0" range="%s %s" limited="true" damping="20" solreflimit="0.004 1"/><inertial mass="%s" pos="0 0 %s" diaginertia="%s 0.004 %s"/>'%(G['cx'],ROCK_Z,-ROCK_DEG,ROCK_DEG,ROCK_M,(0.0 if ROCK_M==1.5 else 0.27-ROCK_Z),0.04*ROCK_M/1.5,0.04*ROCK_M/1.5)) if ROCK else ''}{caster('L',1)}{caster('R',-1)}{'</body>' if ROCK else ''}''')
# docking firmware switches (both OFF by default = their behaviour: one re-approach, then lift whatever the camera says about the sideways offset)
#   X_DOCK_TRIES=<n>   allow up to n re-approaches while the camera-measured sideways offset is over the 25 mm threshold (theirs: 1)
#   X_DOCK_DYMAX=<m>   after the last approach, refuse to lift (safe "no dock") if the camera-measured offset is still above this
s = rep(s, "GEO['lift_range']=float(os.environ.get('X_LIFT_RANGE','0.25'))", "GEO['lift_range']=float(os.environ.get('X_LIFT_RANGE','0.25')); XTRIES=int(os.environ.get('X_DOCK_TRIES','1')); XDYMAX=float(os.environ.get('X_DOCK_DYMAX','0'))")
s = rep(s, "R.reapp=True; return approach(R,cam_sigma,thr,seed+1000,retry=False)\n    R.dock_why=why\n    return bool(good)",
        "R.reapp=True; return approach(R,cam_sigma,thr,seed+1000,retry=(int(retry)-1 if XTRIES>1 else False))\n    R.dock_why=why\n    return bool(good and (XDYMAX<=0 or abs(dy)<=XDYMAX))")
assert s.count("ok=approach(R,seed=seed); out['docked']=ok") == 2   # their file defines grab() twice; the second definition is the one in use
s = s.replace("ok=approach(R,seed=seed); out['docked']=ok", "ok=approach(R,seed=seed,retry=(XTRIES if XTRIES>1 else True)); out['docked']=ok")
#   X_NOSE_DX=<m>      front bumper and the four nose points of the plan outline moved forward by this much (revision 2: 0.065)
s = rep(s, "XDYMAX=float(os.environ.get('X_DOCK_DYMAX','0'))", "XDYMAX=float(os.environ.get('X_DOCK_DYMAX','0')); NOSE_DX=float(os.environ.get('X_NOSE_DX','0'))")
s = rep(s, '<geom name="bumper" type="box" pos="1.07 0 0.18"', '<geom name="bumper" type="box" pos="{1.07+NOSE_DX} 0 0.18"')
s = rep(s, "CORNERS=[(1.09,0.33),(1.09,-0.33),(1.0,0.42),(1.0,-0.42),", "CORNERS=[(1.09+NOSE_DX,0.33),(1.09+NOSE_DX,-0.33),(1.0+NOSE_DX,0.42),(1.0+NOSE_DX,-0.42),")
# post-hold seating check (OFF by default; added 14 Nov after the review of revision 2)
#   X_POSTHOLD=<m>        after the lift, measure how far the bin sits off the comb centre (nib position across the lip, as a camera or the two
#                         comb sensors would see it, with Gaussian error X_POSTHOLD_SIG, default 8 mm). Outside the band: set the bin down with
#                         their own set_down(), and pick it up again; after X_POSTHOLD_TRIES lifts (default 2) leave it standing and report no_dock.
#   Every pick-up result also gets nib_y_mm (truth) so false holds can be counted under any band. This adds an output field only.
s += """
# [X] post-hold seating check, see make_simB2hx.py
XPH=float(os.environ.get('X_POSTHOLD','0')); XPHSIG=float(os.environ.get('X_POSTHOLD_SIG','0.008')); XPHTRIES=int(os.environ.get('X_POSTHOLD_TRIES','2'))
_grab_once=grab
def grab(R,seed=0):
    out=_grab_once(R,seed); S=R.s; log=[]; k=0
    while XPH>0 and out.get('claim') and out.get('result') in ('success','false_positive'):
        meas=float(S.nib_in_bin()[1])+float(np.random.default_rng(seed*13+k+7).normal(0,XPHSIG)); log.append(round(meas*1000,1))
        if abs(meas)<=XPH: break
        R.ev('post-hold check: bin %.0f mm off the comb centre (limit %.0f mm): set down'%(meas*1000,XPH*1000))
        sd=set_down(R); k+=1
        if not sd.get('released') or k>=XPHTRIES:
            out=dict(out,result='no_dock',claim=False,captured=bool(S.captured()),why='post-hold check: off-centre after %d lifts'%k,released=bool(sd.get('released'))); break
        out=_grab_once(R,seed+7000*k)
    out['posthold_mm']=log; out['nib_y_mm']=round(float(S.nib_in_bin()[1])*1000,1)
    return out
"""
# acceleration limit on the open-road drive command (OFF by default; added 14 Nov)
#   X_ACC=<m/s2>          heading_hold() no longer steps the wheel-speed command from rest to cruise: the forward command rises at this rate
#                         (the driving software already does this: ATC_ACCEL_MAX 0.4 in params/bintug_b2f.parm). Slowing down is not limited.
s += """
# [X] acceleration limit on heading_hold, see make_simB2hx.py
XACC=float(os.environ.get('X_ACC','0'))
_heading_hold0=heading_hold
def heading_hold(R,v,psi_ref_deg,K=2.0):
    ctl0=_heading_hold0(R,v,psi_ref_deg,K); st={}
    def ctl():
        if 't' not in st: st['t']=R.t; st['w']=0.0 if getattr(R,'brake',False) else float(getattr(R,'w',0.0))
        ctl0()
        if XACC>0:
            dt=max(0.0,R.t-st['t']); lim=abs(st['w'])+XACC/RW*dt
            if abs(R.w)>lim and R.w*st['w']>=0: R.w=math.copysign(lim,R.w)
            elif R.w*st['w']<0: R.w=math.copysign(min(abs(R.w),XACC/RW*dt),R.w)
        st['t']=R.t; st['w']=float(R.w)
    return ctl
"""
# stall torque boost (OFF by default; added 20 Nov after the review of revision 3)
#   X_BOOST=<N m>         the wheel torque limit stays at GEO tcap (60 N m) in normal driving. If a drive wheel turns at less than 30 % of its
#                         commanded speed for 0.4 s while the command is at least X_BOOST_VMIN (0.10 m/s: never while creeping onto a bin),
#                         the limit rises to this value for at most X_BOOST_T seconds (3), then falls back; the next boost waits X_BOOST_COOL (5 s).
#                         Wheel speed is used, not ground speed, so wheel-spin on a slippery slope does not trigger it. The brake limit does not change.
s = rep(s, "lim=150*GEO['tcap']/60.0 if s.brake else GEO['tcap']", "lim=150*GEO['tcap']/60.0 if s.brake else (_tqlim(s) if XBOOST>0 else GEO['tcap'])")
s += """
# [X] stall torque boost, see make_simB2hx.py
XBOOST=float(os.environ.get('X_BOOST','0')); XBOOST_T=float(os.environ.get('X_BOOST_T','3')); XBOOST_COOL=float(os.environ.get('X_BOOST_COOL','5')); XBOOST_VMIN=float(os.environ.get('X_BOOST_VMIN','0.10'))
def _tqlim(s):
    st=s.__dict__.setdefault('_bst',dict(stall=None,on=None,off=-1e9,n=0,tot=0.0,ok=None)); S=s.s; d=S.d
    cl,cr_=abs(float(d.ctrl[0])),abs(float(d.ctrl[1])); wl,wr=abs(float(d.qvel[S.jv('axleL')])),abs(float(d.qvel[S.jv('axleR')]))
    cmd=max(cl,cr_)*RW; stalled=(cl*RW>=XBOOST_VMIN and wl<0.3*cl) or (cr_*RW>=XBOOST_VMIN and wr<0.3*cr_); moving=(wl>=0.8*cl and wr>=0.8*cr_)
    if st['on'] is not None:
        if moving:
            if st['ok'] is None: st['ok']=s.t
        else: st['ok']=None
        if s.t-st['on']>=XBOOST_T or (st['ok'] is not None and s.t-st['ok']>=0.5) or cmd<XBOOST_VMIN:
            st['tot']+=s.t-st['on']; st['on']=None; st['off']=s.t; st['stall']=None; st['ok']=None
        else: return XBOOST
    if stalled and s.t-st['off']>=XBOOST_COOL:
        if st['stall'] is None: st['stall']=s.t
        elif s.t-st['stall']>=0.4: st['on']=s.t; st['n']+=1; st['ok']=None; s.ev('torque boost %d on (%.0f N m)'%(st['n'],XBOOST)); return XBOOST
    else: st['stall']=None
    return GEO['tcap']
"""
# braked castors (OFF by default; added 20 Nov): an option to shorten the stop of the EMPTY robot, which carries half its weight on the castors
#   X_CBRAKE=<N m>        each castor wheel gets a brake of this torque (0.1 m wheel radius: 30 N m = 300 N at the ground), applied and
#                         released together with the drive-wheel brakes
s = rep(s, """<position name="padact" joint="padext" kp="100000" kv="3000" forcerange="-1500 1500"/>""", """<position name="padact" joint="padext" kp="100000" kv="3000" forcerange="-1500 1500"/>{('<velocity name="cbL" joint="caxL" kv="0" forcerange="-%g %g"/><velocity name="cbR" joint="caxR" kv="0" forcerange="-%g %g"/>'%(XCB,XCB,XCB,XCB)) if XCB>0 else ''}""")
s = rep(s, "ROCK=os.environ.get('X_ROCKER')=='1';", "XCB=float(os.environ.get('X_CBRAKE','0')); ROCK=os.environ.get('X_ROCKER')=='1';")
s = rep(s, "        for a in (0,1): s.m.actuator_gainprm[a][0]=kv; s.m.actuator_biasprm[a][2]=-kv", "        for a in (0,1): s.m.actuator_gainprm[a][0]=kv; s.m.actuator_biasprm[a][2]=-kv\n        if XCB>0:\n            for n in ('cbL','cbR'): a=s.aid(n); kc=(2000.0 if on else 0.0); s.m.actuator_gainprm[a][0]=kc; s.m.actuator_biasprm[a][2]=-kc")
# lift speed limit
#   X_LIFT_V=<m/s>        the lift never moves faster than this (their firmware lifts at 0.03 m/s and lowers at 0.02 m/s; the FDI unit does 0.006,
#                         a LINAK LA36 6.8 kN unit 0.013 under load). OFF by default
s = rep(s, "        r=rate*s.dt\n        for k in range(int(Tmax/s.dt)):", "        XLV=float(os.environ.get('X_LIFT_V','0'))\n        if XLV>0 and rate>XLV: Tmax=Tmax*rate/XLV+5; rate=XLV\n        r=rate*s.dt\n        for k in range(int(Tmax/s.dt)):")
open(os.path.join(cg, 'h2', 'simB2hx.py'), 'w').write(s)
print('wrote h2/simB2hx.py (%d lines; original %d)' % (s.count('\n'), src.count('\n')))
