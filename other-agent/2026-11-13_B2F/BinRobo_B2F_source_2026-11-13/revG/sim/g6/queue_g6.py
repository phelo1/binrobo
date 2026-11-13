#!/usr/bin/env python3
"""single-process job queue: runs lines of queue.txt in order (one at a time); a line is done when listed in queue.done.
Lines can be appended / reordered while it runs. 'WAITPID <pid>' waits for an existing process."""
import os, subprocess, time
H=os.path.dirname(os.path.abspath(__file__)); import sys; QN=sys.argv[1]; Q=os.path.join(H,QN+'.txt'); D=os.path.join(H,QN+'.done')
env=dict(os.environ,PYTHONPATH='/workspace/work/pylib',NREC=os.environ.get('NREC','2'))
while True:
    done=set(open(D).read().splitlines()) if os.path.exists(D) else set()
    todo=[l.strip() for l in open(Q).read().splitlines() if l.strip() and not l.startswith('#') and l.strip() not in done]
    if not todo:
        if os.path.exists(os.path.join(H,QN+'.stop')): break
        time.sleep(20); continue
    job=todo[0]
    if job.startswith('WAITPID'):
        pid=int(job.split()[1])
        while os.path.exists(f'/proc/{pid}'): time.sleep(10)
    else:
        with open(os.path.join(H,QN+'.log'),'a') as lg:
            lg.write(f'== {time.strftime("%H:%M:%S")} {job}\n'); lg.flush()
            subprocess.run(job,shell=True,cwd=H,env=env,stdout=lg,stderr=subprocess.STDOUT)
    open(D,'a').write(job+'\n')
