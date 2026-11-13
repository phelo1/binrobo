#!/usr/bin/env python3
"""Foreground chunk runner for an h2 queue (copy of b2/qchunk_b2.py, queue file as an argument). Runs pending lines (md5 .done
bookkeeping) one at a time, nice 10, each under `timeout` (the child is killed by timeout itself, no pkill), inside a wall budget.
Grab lines resume from their per-run json (backed up before, restored if a kill left it unreadable). A non-grab line is started
only if the remaining budget >= its estimate. A line that has been cut by the budget 3 times is marked SKIPPED (logged) and the
queue moves on. usage: qchunk_h2.py <queue> <budget_s>"""
import os, sys, subprocess, time, hashlib, json, shutil, re
H=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); q=os.path.abspath(sys.argv[1])
env=dict(os.environ,PYTHONPATH='/workspace/work/pylib'); B=float(sys.argv[2]); T0=time.time()
for ext in ('.done','.cuts'):
    if not os.path.exists(q+ext): open(q+ext,'w').close()
md=lambda l: hashlib.md5(l.encode()).hexdigest()
def pending():
    done=set(open(q+'.done').read().split())
    return [l.strip() for l in open(q) if l.strip() and not l.startswith('#') and md(l.strip()) not in done]
def est(l):
    m=re.search(r'#est=(\d+)',l)
    if m: return int(m.group(1))
    if ' static ' in l: return 22
    if ' rel ' in l: return 21
    if ' grab ' in l: return 25
    return 28
while True:
    todo=pending()
    if not todo: print('QUEUE EMPTY'); break
    l=todo[0]; left=B-(time.time()-T0)
    if left<est(l): break
    out=None
    if ' grab ' in l:
        mp=re.search(r'CMP_PREFIX=(\S+)',l); mt=re.search(r'IT1_TAG=(\S*)',l); mb=re.search(r' grab (\S+) ',l); mr=re.search(r'H2_RES=(\S+)',l)
        rd=mr.group(1) if mr else os.path.join(H,'h2','res')
        out=os.path.join(rd,'%sgrab_%s%s.json'%(mp.group(1),mb.group(1),mt.group(1) if mt else ''))
        if os.path.exists(out): shutil.copy(out,out+'.bak')
    t=time.time(); cmd=l.split('#est=')[0]
    with open(q+'.log','a') as lg:
        lg.write('\n=== %s START %s\n'%(time.strftime('%H:%M:%S'),l)); lg.flush()
        r=subprocess.run('timeout -s TERM %d nice -n 10 %s'%(int(left-2),cmd),shell=True,cwd=H,env=env,stdout=lg,stderr=subprocess.STDOUT)
        lg.write('=== END rc=%d %.0fs\n'%(r.returncode,time.time()-t))
    if out and os.path.exists(out):
        try: json.load(open(out))
        except Exception:
            if os.path.exists(out+'.bak'): shutil.copy(out+'.bak',out); print('restored',out)
    if r.returncode==0:
        open(q+'.done','a').write(md(l)+'\n'); print('DONE %.0fs'%(time.time()-t),l[-90:])
    else:
        cuts=open(q+'.cuts').read().split().count(md(l))+1; open(q+'.cuts','a').write(md(l)+'\n')
        if cuts>=3 and ' grab ' not in l:
            open(q+'.done','a').write(md(l)+'\n'); open(q+'.log','a').write('=== SKIPPED after 3 cuts: %s\n'%l); print('SKIPPED',l[-90:])
        else: print('PARTIAL rc=%d %.0fs'%(r.returncode,time.time()-t),l[-90:])
        break
print('pending',len(pending()))
