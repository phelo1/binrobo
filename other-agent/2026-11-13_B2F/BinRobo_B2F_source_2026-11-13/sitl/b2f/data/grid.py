import json, math, time, urllib.request, numpy as np
lat0,lon0=53.000000,-8.000000
def ll(x,y): return (lat0+y/111132, lon0+x/(111320*math.cos(math.radians(lat0))))
xs=np.arange(-280,141,20.); ys=np.arange(-580,81,20.)
locs=[ll(x,y) for y in ys for x in xs]; z=[]
for i in range(0,len(locs),100):
    q='|'.join('%.6f,%.6f'%p for p in locs[i:i+100])
    for t in range(5):
        try:
            d=json.load(urllib.request.urlopen('https://api.opentopodata.org/v1/eudem25m?locations=%s&interpolation=bilinear'%q,timeout=40)); z+=[r['elevation'] for r in d['results']]; break
        except Exception as e: print('retry',e); time.sleep(3)
    time.sleep(1.2)
Z=np.array(z,float).reshape(len(ys),len(xs))
json.dump(dict(xs=xs.tolist(),ys=ys.tolist(),z=Z.tolist(),src='OpenTopoData eudem25m bilinear'),open('dem_grid.json','w'))
print(Z.shape,Z.min(),Z.max())
