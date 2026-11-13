import xml.etree.ElementTree as ET, math, json
r=ET.parse('osm_bbox.xml').getroot()
lat0,lon0=53.000000,-8.000000
def xy(la,lo): return ((lo-lon0)*111320*math.cos(math.radians(lat0)),(la-lat0)*111132)
N={n.get('id'):(float(n.get('lat')),float(n.get('lon'))) for n in r.iter('node')}
ways=[]
for w in r.iter('way'):
    t={k.get('k'):k.get('v') for k in w.iter('tag')}
    if 'highway' not in t: continue
    nd=[x.get('ref') for x in w.iter('nd')]
    g=[N[i] for i in nd if i in N]
    P=[xy(*p) for p in g]
    L=sum(math.dist(a,b) for a,b in zip(P,P[1:]))
    dm=min(math.dist((0,0),p) for p in P)
    ways.append(dict(id=w.get('id'),tags=t,nodes=nd,geom=g,len=L,dmin=dm))
ways.sort(key=lambda w:w['dmin'])
for w in ways[:25]:
    P=[xy(*p) for p in w['geom']]
    print(w['id'],w['tags'].get('highway'),w['tags'].get('name',''),w['tags'].get('ref',''),w['tags'].get('access',''),w['tags'].get('surface',''),'len%.0f dmin%.0f'%(w['len'],w['dmin']),'(%.0f,%.0f)->(%.0f,%.0f)'%(*P[0],*P[-1]),w['nodes'][0],w['nodes'][-1])
json.dump(ways,open('osm_highways.json','w'))
