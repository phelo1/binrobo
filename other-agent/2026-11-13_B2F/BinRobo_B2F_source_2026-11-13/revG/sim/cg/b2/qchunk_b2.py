#!/usr/bin/env python3
"""Foreground chunk runner for q_b2.txt (replaces the detached queue after the sandbox stop).
Runs pending lines (same md5 .done bookkeeping as cmp/queue_cmp.py) one at a time, nice 10, under a wall budget (s).
Each line runs under `timeout` (child PID killed by timeout itself, no pkill). Grab lines resume from their per-run json;
a grab json is backed up before the run and restored if a kill left it unreadable. Non-grab lines are only started when the
remaining budget >= their estimate. usage: qchunk_b2.py <budget_s>"""
import os, sys, subprocess, time, hashlib, json, shutil, re
H=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); q=os.path.join(H,'b2','q_b2.txt')
env=dict(os.environ,PYTHONPATH='/workspace/work/pylib'); B=float(sys.argv[1]); T0=time.time()
def pending():
    done=set(open(q+'.done').read().split())
    return [l.strip() for l in open(q) if l.strip() and not l.startswith('#') and hashlib.md5(l.strip().encode()).hexdigest() not in done]
def est(l):
    if ' static ' in l: return 22
    if ' grab ' in l: return 35
    return 45
while True:
    todo=pending()
    if not todo: print('QUEUE EMPTY'); break
    l=todo[0]; left=B-(time.time()-T0)
    if left<est(l): break
    out=None
    if ' grab ' in l:
        m=re.search(r'IT1_TAG=(\S*) .* grab (\S+) ',l); out=os.path.join(H,'b2','res','B2_grab_%s%s.json'%(m.group(2),m.group(1)))
        if os.path.exists(out): shutil.copy(out,out+'.bak')
    t=time.time()
    with open(q+'.log','a') as lg:
        lg.write('\n=== %s START %s\n'%(time.strftime('%H:%M:%S'),l)); lg.flush()
        r=subprocess.run('timeout -s TERM %d nice -n 10 %s'%(int(left-3),l),shell=True,cwd=H,env=env,stdout=lg,stderr=subprocess.STDOUT)
        lg.write('=== END rc=%d %.0fs\n'%(r.returncode,time.time()-t))
    if out and os.path.exists(out):
        try: json.load(open(out))
        except Exception:
            if os.path.exists(out+'.bak'): shutil.copy(out+'.bak',out); print('restored',out)
    if r.returncode==0:
        open(q+'.done','a').write(hashlib.md5(l.encode()).hexdigest()+'\n'); print('DONE %.0fs'%(time.time()-t),l.split('IT1_TAG=')[1])
    else:
        print('PARTIAL rc=%d %.0fs'%(r.returncode,time.time()-t),l.split('IT1_TAG=')[1]); break
print('pending',len(pending()))
