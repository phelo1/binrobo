#!/usr/bin/env python3
"""Sequential queue (ONE MuJoCo process at a time, nice 10). usage: queue_cg.py <queue.txt>; lines = shell commands run in cg/;
done lines recorded in <queue>.done; stop by creating <queue>.stop."""
import os, sys, subprocess, time, hashlib
q=sys.argv[1]; H=os.path.dirname(os.path.abspath(__file__)); env=dict(os.environ,PYTHONPATH='/workspace/work/pylib')
while True:
    if os.path.exists(q+'.stop'): break
    done=set(open(q+'.done').read().split('\n')) if os.path.exists(q+'.done') else set()
    todo=[l.strip() for l in open(q) if l.strip() and not l.startswith('#') and hashlib.md5(l.strip().encode()).hexdigest() not in done]
    if not todo: break
    l=todo[0]; t=time.time()
    with open(q+'.log','a') as lg:
        lg.write('\n=== %s START %s\n'%(time.strftime('%H:%M:%S'),l)); lg.flush()
        r=subprocess.run('nice -n 10 '+l,shell=True,cwd=H,env=env,stdout=lg,stderr=subprocess.STDOUT)
        lg.write('=== END rc=%d %.0fs\n'%(r.returncode,time.time()-t))
    open(q+'.done','a').write(hashlib.md5(l.encode()).hexdigest()+'\n')
