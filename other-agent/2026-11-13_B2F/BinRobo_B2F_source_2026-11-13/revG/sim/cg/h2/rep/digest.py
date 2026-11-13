import json,glob,os
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/../res')
J=lambda f: json.load(open(f))
def grab(f):
    d=J(f); ns=[(r['i'],r['result']) for r in d['runs'] if r['result']!='success']
    return '%d/%d FH%d KN%d %s'%(d['captured'],d['n'],d['false_holds'],d['knocked'],ns)
print('== gate files'); 
for g in ('gate_H2_.json','gate_B2F_.json'):
    d=J(g); print(g); 
    for k,v in d.items(): print('  ',k,json.dumps(v)[:400])
print('== grabs')
for f in sorted(glob.glob('*grab_*.json')): print(f,grab(f))
print('== perturbations')
for f in sorted(glob.glob('*_p*.json')):
    if 'grab' in f: continue
    d=J(f); print(f, {k:d.get(k) for k in ('ok','verdict','time_s','hold_creep_m','stop_dist_m','slide_after_stop_m','dist_m','reached','roll','pitch')})
print('== B2n rel/towstab')
for f in sorted(glob.glob('B2n_*.json')):
    if 'grab' in f: continue
    d=J(f); print(f,d.get('verdict'),d.get('grab'),d.get('ok'))
