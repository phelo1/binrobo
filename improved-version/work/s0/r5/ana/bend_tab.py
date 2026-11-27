import json,os,glob,sys
import numpy as np
O='/home/claude/sitl_out'; out={}; L=['| Software | Runs | Completed | Runs with the position more than 0.5 m out near the bend | Largest position error | Least hedge clearance in any run | Furthest off the centre line at the bend | Protective stops |','|---|---:|---:|---:|---:|---:|---:|---:|']
for camp,name in (('r5a_bend40','first pass'),('r5b_bend40','second pass')):
    rows=[]
    for f in sorted(glob.glob('%s/%s/runs/*/result.json'%(O,camp))):
        r=json.load(open(f)); m=r['metrics']; d=os.path.dirname(f)
        try: tr=json.load(open(d+'/trace.json'))['trace']
        except Exception: continue
        seg=[e for e in tr if 55<=e['s']<=92 and str(e['state']).startswith('LANE')]
        g=max([e['gdr'] or 0 for e in seg] or [0]); lat=[e['lat'] for e in seg] or [0]
        rows.append(dict(seed=r['seed'], outcome=r['outcome'], result=r['result'], hedge=r['hedge_min_m'], hedge_at=(r.get('hedge_min_at') or [None,None])[1], pose_err=round(g,2), lat_min=round(min(lat),2), lat_max=round(max(lat),2), prot=len(m.get('prot_stops') or []), wmax=round(max([abs(e['w']) for e in seg] or [0]),2)))
    out[camp]=rows
    if not rows: continue
    L.append('| %s | %d | %d | %d | %.2f m | %.3f m | %.2f m | %d |'%(name, len(rows), sum(q['result']=='pass' for q in rows), sum(q['pose_err']>0.5 for q in rows), max(q['pose_err'] for q in rows), min(q['hedge'] for q in rows), max(max(abs(q['lat_min']),abs(q['lat_max'])) for q in rows), sum(q['prot'] for q in rows)))
json.dump(out, open('/home/claude/s0/r5/pack_tables/bend40_r5.json','w'), indent=1); open('/home/claude/s0/r5/pack_tables/bend40_r5.md','w').write('\n'.join(L)+'\n'); print('\n'.join(L))
for camp,rows in out.items():
    for q in rows:
        if q['pose_err']>0.5 or q['hedge']<0.3 or q['prot']: print(camp,q)
