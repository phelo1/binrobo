import json,os
O='/home/claude/sitl_out'
names=[('none','no fault'),('steerL8','steering forced 20 degrees toward the near (left) hedge for 8 s'),('steerL90','the same for 90 s'),('steerR40','steering forced 20 degrees toward the far hedge for 40 s'),
       ('cam05','camera reading stuck at 0.5 m for 30 s (true 0.9 m)'),('cam25','camera reading stuck at 2.5 m for 30 s'),('lidp08','lidar left-face reading 0.8 m too far for 30 s'),('lidm05','lidar left-face reading 0.5 m too near for 30 s')]
L=['| Fault | Outcome | Protective stops | Least hedge clearance | The same on the first version of the second pass |','|---|---|---:|---:|---|']; rows=[]
for k,txt in names:
    def rd(pref):
        f='%s/%s_fault_%s/runs/tune__s7/result.json'%(O,pref,k)
        if not os.path.exists(f): return None
        r=json.load(open(f)); m=r['metrics']; return dict(outcome=r['outcome'], result=r['result'], hedge=r['hedge_min_m'], prot=len(m.get('prot_stops') or []), stops=len(m.get('stops') or []), nav=m.get('navcam'))
    a=rd('r5bf'); b=rd('r5b1'); c=rd('r5b'); rows.append(dict(fault=k, text=txt, final=a, first_version=b, before_last_edits=c))
    if a is None: continue
    oc='completed' if a['result']=='pass' else 'held and alerted ("%s")'%a['outcome']
    L.append('| %s | %s | %d | %.3f m | %s |'%(txt, oc, a['prot'], a['hedge'], '-' if b is None else '%.3f m, %d protective stop%s'%(b['hedge'], b['prot'], '' if b['prot']==1 else 's')))
open('/home/claude/s0/r5/pack_tables/fault_tests_r5.md','w').write('\n'.join(L)+'\n'); json.dump(rows, open('/home/claude/s0/r5/pack_tables/fault_tests_r5.json','w'), indent=1)
print('\n'.join(L))
