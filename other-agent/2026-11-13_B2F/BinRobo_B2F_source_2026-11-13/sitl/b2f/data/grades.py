import json, numpy as np
R=json.load(open('route.json')); s=np.array(R['s'])
out={}
for ds,z in R['elev'].items():
    z=np.array(z,float)
    res={'z_start_house':z[0],'z_end_road':z[-1],'z_min':z.min(),'z_max':z.max(),'net_drop':z[0]-z[-1],
         'avg_grade_pct':100*abs(z[-1]-z[0])/s[-1]}
    climb=np.sum(np.clip(np.diff(z),0,None)); desc=-np.sum(np.clip(np.diff(z),None,0))
    res['total_climb_m']=climb; res['total_descent_m']=desc
    res['mean_abs_grade_pct']=100*(climb+desc)/s[-1]
    for win in (10,25,50):
        g=[]; 
        for i in range(len(s)):
            j=np.searchsorted(s,s[i]+win)
            if j<len(s): g.append((s[i],100*(z[j]-z[i])/(s[j]-s[i])))
        g=np.array(g); k=np.argmax(np.abs(g[:,1]))
        res[f'max_grade_{win}m_pct']=g[k,1]; res[f'max_grade_{win}m_at_s']=g[k,0]
    out[ds]=res
json.dump(out,open('grades.json','w'),indent=1)
for ds,r in out.items(): print(ds,{k:round(float(v),2) for k,v in r.items()})
