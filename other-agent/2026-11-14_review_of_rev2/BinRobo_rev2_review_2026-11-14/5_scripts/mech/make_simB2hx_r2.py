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
s = rep(s, "GEO['lift_range']=0.25", "GEO['lift_range']=float(os.environ.get('X_LIFT_RANGE','0.25'))\nROCK=os.environ.get('X_ROCKER')=='1'; ROCK_DEG=float(os.environ.get('X_ROCK_DEG','5')); ROCK_Z=float(os.environ.get('X_ROCK_Z','0.20')); ROCK_M=float(os.environ.get('X_ROCK_M','1.5'))")
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
open(os.path.join(cg, 'h2', 'simB2hx_r2.py'), 'w').write(s)
print('wrote h2/simB2hx_r2.py (%d lines; original %d)' % (s.count('\n'), src.count('\n')))
