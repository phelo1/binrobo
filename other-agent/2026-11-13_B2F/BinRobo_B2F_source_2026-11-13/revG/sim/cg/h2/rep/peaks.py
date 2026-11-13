import json,glob,os,collections
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/../res')
rows=[]
for f in glob.glob('*.json'):
    if f.startswith(('gate','hull','mass','B2n','B2r')) or 'tyrecal' in f or 'tipcalc' in f: continue
    pre=f.split('_')[0]
    if pre not in ('H2','B2F'): continue
    d=json.load(open(f))
    if 'runs' in d:  # grab sets
        continue
    pk=d.get('peak')
    if pk:
        r=dict(wheel=pk.get('drive_tyre_N',[0])[0],comb=pk.get('nib_rim_N',[0])[0],pad=pk.get('pad_N',[0])[0],lift=pk.get('lift_N',[0])[0],
               ph={k:v[2] for k,v in pk.items() if isinstance(v,list) and len(v)>2})
    elif 'lipF' in d:
        r=dict(wheel=d['drive_tyre'],comb=d['lipF'],pad=d['padF'],lift=d['liftF'],ph={})
    elif 'driveL' in d:
        r=dict(wheel=max(d['driveL'],d['driveR']),comb=0,pad=d.get('pad_N',0),lift=d.get('lift_N',0),ph={},castor=d['caster_sum'])
    else: continue
    r['f']=f; r['d']=pre; rows.append(r)
json.dump(rows,open('../rep/peaks.json','w'))
for des in ('H2','B2F'):
    R=[r for r in rows if r['d']==des]
    print('=====',des,len(R))
    for k in ('wheel','comb','pad','lift'):
        s=sorted(R,key=lambda r:-r[k])
        print(k,[(round(r[k]),r['f'].replace('.json',''),r['ph'].get({'wheel':'drive_tyre_N','comb':'nib_rim_N','pad':'pad_N','lift':'lift_N'}[k],'')) for r in s[:12]])
        vals=sorted(r[k] for r in R); n=len(vals); print('   median',round(vals[n//2]),'p90',round(vals[int(0.9*n)]))
