import json,glob,os,sys,collections
def stats(dirs):
    runs={}
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d,'*','result.json'))): runs[os.path.basename(os.path.dirname(f))]=json.load(open(f))
    S=dict(n=len(runs)); oc=collections.Counter(r['outcome'] for r in runs.values()); S['outcomes']=dict(oc)
    trips=[t for r in runs.values() for t in (r['metrics'].get('trips') or [])]
    if trips: S['trips']=dict(n=len(trips), wh=[min(t['wh'] for t in trips), max(t['wh'] for t in trips), round(sum(t['wh'] for t in trips)/len(trips),1)], minutes=[min(t['min'] for t in trips), max(t['min'] for t in trips), round(sum(t['min'] for t in trips)/len(trips),1)])
    S['soc_end']={k:r['soc_end'] for k,r in runs.items() if r['scenario'] in ('s3a','s3b')}
    S['last_dock']={k:r['metrics'].get('last_dock_clock') for k,r in runs.items() if r['scenario'] in ('s1a','s1b','s3a','s3b')}
    hm=[(r['hedge_min_m'],k,r.get('hedge_min_at')) for k,r in runs.items() if r.get('hedge_min_m') is not None and (r.get('odo_m') or 0)>0.05]
    hm.sort(); S['hedge_lowest']=hm[:6]
    S['hedge_full_missions']={k:(r['hedge_min_m'],r.get('hedge_min_at')) for k,r in runs.items() if r['scenario'] in ('s1a','s1b','s3a','s3b')}
    pl=[p for r in runs.values() for p in (r['metrics'].get('placements') or [])]
    if pl: S['placements']=dict(n=len(pl), err_max_mm=round(1000*max(p['err_m'] for p in pl)), err_mean_mm=round(1000*sum(p['err_m'] for p in pl)/len(pl)), handle_max_deg=max(p['handle_err_deg'] for p in pl))
    ga=[g for r in runs.values() for g in (r['metrics'].get('gates') or [])]
    if ga: S['gates']=dict(n=len(ga), ok_cam=sum(1 for g in ga if g.get('ok_cam', g['ok'])), ok_truth=sum(1 for g in ga if g['ok']), cam_ok_truth_out=sum(1 for g in ga if g.get('ok_cam') and not g['ok']), worst_lat_mm=round(1000*max(abs(g['lat_m']) for g in ga)), worst_yaw=max(abs(g['yaw_deg']) for g in ga))
    sc=[q for r in runs.values() for q in (r['metrics'].get('seat_checks') or [])]
    if sc: S['seat_checks']=dict(n=len(sc), ok=sum(1 for q in sc if q['ok']))
    S['prot_stops']={k:r['metrics']['prot_stops'] for k,r in runs.items() if r['metrics'].get('prot_stops')}
    S['object_stops']=sum(len(r['metrics'].get('stops') or []) for r in runs.values())
    nv=collections.Counter()
    for r in runs.values():
        for k,v in (r['metrics'].get('navcam') or {}).items(): nv[k]+=v
    if nv.get('n'): S['navcam']=dict(nv); S['navcam_pct']={k:round(100.0*v/nv['n'],1) for k,v in nv.items() if k!='n'}
    S['alerts']={k:r['alerts'] for k,r in runs.items() if r['alerts'] and r['expect']=='pass'}
    S['refused']={k:r['metrics'].get('refused') for k,r in runs.items() if r['metrics'].get('refused')}
    S['windows']={k:r['metrics'].get('window') for k,r in runs.items() if r['scenario'] in ('s3a','s3b')}
    S['collisions']={k:r['collisions'] for k,r in runs.items() if r.get('collisions')}
    return S
if __name__=='__main__':
    out=None; dirs=[]
    for a in sys.argv[1:]:
        if a.startswith('--json='): out=a[7:]
        else: dirs.append(a)
    S=stats(dirs)
    if out: json.dump(S, open(out,'w'), indent=1)
    for k,v in S.items(): print(k, ':', json.dumps(v)[:900])
