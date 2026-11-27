import json,glob,os,sys
out=[]
for p in ['a','b']:
    for d in ['m45','45','m135','135','0','180','90','m90']:
        f='r5%s_gps_%s/runs/tune__s7'%(p,d)
        if not os.path.exists(f+'/result.json'): continue
        r=json.load(open(f+'/result.json')); tr=json.load(open(f+'/trace.json'))['trace']
        lat=[e['lat'] for e in tr if 68<=e['s']<=92 and e['state'].startswith('LANE')]
        g=max([e['gdr'] or 0 for e in tr if 60<=e['s']<=80])
        w=max([abs(e['w']) for e in tr if 68<=e['s']<=92 and e['state'].startswith('LANE')])
        out.append(dict(software='first pass' if p=='a' else 'second pass', dir=d.replace('m','-'), pose_err_max=round(g,2), lat_min=round(min(lat),2), lat_max=round(max(lat),2), w_max=round(w,2), hedge_min=r['hedge_min_m'], outcome=r['outcome'], prot=len(r['metrics'].get('prot_stops') or [])))
        print(out[-1], flush=True)
json.dump(out, open('/home/claude/s0/r5/pack_tables/gps_fault_bend_r5.json','w'), indent=1)
