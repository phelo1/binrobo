import json, math, time, urllib.request, numpy as np
W={w['id']:w for w in json.load(open('osm_highways.json'))}
lat0,lon0=53.000000,-8.000000
def xy(la,lo): return ((lo-lon0)*111320*math.cos(math.radians(lat0)),(la-lat0)*111132)
def ll(x,y): return (lat0+y/111132, lon0+x/(111320*math.cos(math.radians(lat0))))
a=W['0']['geom'][::-1]          # house end -> junction
b=W['0']['geom'][1::-1]         # 2984401652 -> 2984401426
c=W['0']['geom'][::-1]           # -> the public road [road]
pts=[]
for seg in (a,b,c):
    for p in seg:
        if not pts or pts[-1]!=tuple(p): pts.append(tuple(p))
P=np.array([xy(*p) for p in pts])
s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))]
print('route length %.1f m, %d vertices'%(s[-1],len(P)))
# resample every 5 m
ss=np.arange(0,s[-1],5.0); ss=np.r_[ss,s[-1]]
R=np.c_[np.interp(ss,s,P[:,0]),np.interp(ss,s,P[:,1])]
LL=[ll(*p) for p in R]
def topo(locs,ds):
    out=[]
    for i in range(0,len(locs),100):
        q='|'.join('%.6f,%.6f'%p for p in locs[i:i+100])
        for t in range(4):
            try:
                d=json.load(urllib.request.urlopen('https://api.opentopodata.org/v1/%s?locations=%s&interpolation=bilinear'%(ds,q),timeout=40))
                out+= [r['elevation'] for r in d['results']]; break
            except Exception as e: print('retry',ds,e); time.sleep(2)
        time.sleep(1.1)
    return out
el={}
for ds in ('eudem25m','srtm30m'):
    try: el[ds]=topo(LL,ds)
    except Exception as e: print(ds,'failed',e)
json.dump(dict(osm_ways=['0','0','0'],vertices_ll=pts,s=ss.tolist(),xy=R.tolist(),ll=LL,elev=el),open('route.json','w'))
for ds,z in el.items():
    z=np.array(z,float); print(ds,len(z),'min %.1f max %.1f'%(z.min(),z.max()))
