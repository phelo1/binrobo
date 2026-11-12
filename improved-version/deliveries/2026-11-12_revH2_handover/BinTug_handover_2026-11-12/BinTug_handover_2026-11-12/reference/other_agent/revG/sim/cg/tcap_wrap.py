#!/usr/bin/env python3
"""SENSITIVITY ONLY (not a gate run; frozen common term is a 60 N m cap). Runs runA.py/runB.py with the drive torque cap raised to
CG_TCAP N m per wheel (models PEWM-39 on the Roboteq FDCG3260T 60 A / 30 s peak, ~90 N m derived) and writes res/*_tcap<N>.json.
usage: CG_TCAP=90 tcap_wrap.py runB.py step both"""
import os, sys, runpy, builtins, types, mujoco as _mj
T=float(os.environ.get('CG_TCAP','90')); H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..','g6'))
class P(types.ModuleType):
    def __getattr__(s,k): return getattr(_mj,k)
    @staticmethod
    def mj_step(m,d,*a):
        for i in (0,1):
            if abs(m.actuator_forcerange[i][1]-60.0)<1e-9: m.actuator_forcerange[i]=[-T,T]
        return _mj.mj_step(m,d,*a)
prox=P('mujoco_tcap')
_open=builtins.open
def op(f,mode='r',*a,**k):
    if isinstance(f,str) and 'w' in mode and f.endswith('.json') and os.sep+'res'+os.sep in f: f=f[:-5]+'_tcap%d.json'%T
    return _open(f,mode,*a,**k)
builtins.open=op
import importlib
for mod in ('scen_g5','simB_cg'):
    try: M=importlib.import_module(mod); M.mujoco=prox
    except Exception as e: print('patch',mod,e)
script=sys.argv[1]; sys.argv=sys.argv[1:]
runpy.run_path(os.path.join(H,script),run_name='__main__')
