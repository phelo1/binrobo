#!/usr/bin/env python3
"""Writes work/b2f_lanephys/lanerun_x.py = the other agent's lanerun.py with two switches (defaults give the original behaviour):
  X_SIM=<module>       sim module to import in place of simB2h (for example simB2hx)
  X_RUNS_DIR=<dir>     where run folders are read and written (default runs/)
  X_NOSE_DX=<m>        front bumper this much further forward (used with the same switch in simB2hx)
  X_VARIANT=<json>     lane variant for every run, e.g. {"step":"sharp","trench":"covered","pothole":"filled"}
usage: make_lanerun_x.py <b2f_lanephys_dir>"""
import sys, os
d = sys.argv[1]; s = open(os.path.join(d, 'lanerun.py')).read()
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a); return s.replace(a, b)
s = rep(s, "import mujoco, simB2h as B", "import mujoco, importlib\nB = importlib.import_module(os.environ.get('X_SIM', 'simB2h'))")
s = rep(s, "RUNS_DIR = os.path.join(HERE, 'runs')", "RUNS_DIR = os.environ.get('X_RUNS_DIR', os.path.join(HERE, 'runs'))")
s = rep(s, "cfg = RUNS[rid]; d = rundir(rid)", "cfg = dict(RUNS[rid]); cfg['variant'] = json.loads(os.environ['X_VARIANT']) if os.environ.get('X_VARIANT') else cfg['variant']; d = rundir(rid)")
assert s.count('1.09 * ') == 2   # their bumper position for obstacle distances, twice
s = s.replace('1.09 * ', "(1.09 + float(os.environ.get('X_NOSE_DX', '0'))) * ")
open(os.path.join(d, 'lanerun_x.py'), 'w').write(s); print('wrote lanerun_x.py')
