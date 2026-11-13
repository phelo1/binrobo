#!/usr/bin/env python3
"""Writes h2/simB2hx.py = the other agent's h2/simB2h.py with two switchable changes, both OFF by default (then the model is identical):
  X_LIFT_RANGE=<m>   lift travel (their file fixes it at 0.25 m after reading CGB_GEO)
  X_ROCKER=1         castor pair on a rocker: both castor forks hang from a beam hinged to the frame about the fore-aft axis on the centre line,
                     with stops at +/-X_ROCK_DEG (default 5 deg = about 24 mm at each castor), pivot X_ROCK_Z above the ground (default 0.20 m), beam mass 1.5 kg
The fixed pad needs no change: their model already takes CGB_GEO='{"pad_ret":0.0}' ("0 = fixed pad").
usage: make_simB2hx.py <cg_dir>"""
import sys, os
cg = sys.argv[1]; src = open(os.path.join(cg, 'h2', 'simB2h.py')).read()
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:60]); return s.replace(a, b)
s = src
s = rep(s, "GEO['lift_range']=0.25", "GEO['lift_range']=float(os.environ.get('X_LIFT_RANGE','0.25'))\nROCK=os.environ.get('X_ROCKER')=='1'; ROCK_DEG=float(os.environ.get('X_ROCK_DEG','5')); ROCK_Z=float(os.environ.get('X_ROCK_Z','0.20'))")
s = rep(s, '''<body name="cfork{side}" pos="{G['cx']} {s*G['cy']} 0.1">''', '''<body name="cfork{side}" pos="{0.0 if ROCK else G['cx']} {s*G['cy']} {0.1-ROCK_Z if ROCK else 0.1}">''')
s = rep(s, "{caster('L',1)}{caster('R',-1)}", '''{('<body name="rocker" pos="%s 0 %s"><joint name="rock" type="hinge" axis="1 0 0" range="%s %s" limited="true" damping="20" solreflimit="0.004 1"/><inertial mass="1.5" pos="0 0 0" diaginertia="0.04 0.004 0.04"/>'%(G['cx'],ROCK_Z,-ROCK_DEG,ROCK_DEG)) if ROCK else ''}{caster('L',1)}{caster('R',-1)}{'</body>' if ROCK else ''}''')
open(os.path.join(cg, 'h2', 'simB2hx.py'), 'w').write(s)
print('wrote h2/simB2hx.py (%d lines; original %d)' % (s.count('\n'), src.count('\n')))
