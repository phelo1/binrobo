#!/usr/bin/env python3
"""Run a list of the other agent's gate commands (one per line, as in their q_b2.txt) with N workers, from the cg/ folder.
usage: run_batch.py <cmds.txt> <cg_dir> <workers> <logdir>"""
import sys, os, subprocess, time, shlex
from concurrent.futures import ThreadPoolExecutor
cmds = [l.strip() for l in open(sys.argv[1]) if l.strip()]; cg = sys.argv[2]; nw = int(sys.argv[3]); logd = sys.argv[4]; os.makedirs(logd, exist_ok=True)
def run(i_cmd):
    i, c = i_cmd; t0 = time.time()
    with open(os.path.join(logd, '%03d.log' % i), 'w') as lg:
        r = subprocess.run(shlex.split(c), cwd=cg, stdout=lg, stderr=subprocess.STDOUT)
    return i, c, r.returncode, time.time() - t0
t0 = time.time()
with ThreadPoolExecutor(nw) as ex:
    for i, c, rc, dt in ex.map(run, enumerate(cmds)):
        print('%3d rc %d %5.0f s  %s' % (i, rc, dt, c.split('runB2.py ')[-1].split('runCMP.py ')[-1]), flush=True)
print('batch done in %.0f s' % (time.time() - t0))
