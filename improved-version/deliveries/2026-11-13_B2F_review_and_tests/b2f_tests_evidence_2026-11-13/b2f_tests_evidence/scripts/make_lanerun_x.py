#!/usr/bin/env python3
"""Writes work/b2f_lanephys/lanerun_x.py = the other agent's lanerun.py with two switches (defaults give the original behaviour):
  X_SIM=<module>       sim module to import in place of simB2h (for example simB2hx)
  X_RUNS_DIR=<dir>     where run folders are read and written (default runs/)
usage: make_lanerun_x.py <b2f_lanephys_dir>"""
import sys, os
d = sys.argv[1]; s = open(os.path.join(d, 'lanerun.py')).read()
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a); return s.replace(a, b)
s = rep(s, "import mujoco, simB2h as B", "import mujoco, importlib\nB = importlib.import_module(os.environ.get('X_SIM', 'simB2h'))")
s = rep(s, "RUNS_DIR = os.path.join(HERE, 'runs')", "RUNS_DIR = os.environ.get('X_RUNS_DIR', os.path.join(HERE, 'runs'))")
open(os.path.join(d, 'lanerun_x.py'), 'w').write(s); print('wrote lanerun_x.py')
