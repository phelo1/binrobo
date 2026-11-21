import json,sys,math,collections
import numpy as np
def wrap(a): return (a+math.pi)%(2*math.pi)-math.pi
for p in sys.argv[1:]:
    tr=json.load(open(p+'/trace.json'))['trace']
    acc=collections.defaultdict(list); ey=collections.defaultdict(list)
    for e in tr:
        if e['state'] in ('LANE_DOWN_LOADED','LANE_UP','LANE_DOWN','LANE_UP_LOADED'):
            k=(e['state'], int(e['t']//4000))
            acc[k].append(e['w'])
            if e['eyaw'] is not None: ey[k].append(wrap(e['eyaw']-e['yaw']))
    print(p.split('/')[-3]+'/'+p.split('/')[-1], {k:(round(float(np.std(v)),3), round(float(np.std(ey[k])),4), round(float(np.mean(ey[k])),4)) for k,v in sorted(acc.items())}, flush=True)
