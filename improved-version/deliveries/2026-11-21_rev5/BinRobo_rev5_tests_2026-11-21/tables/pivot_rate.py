import json,sys,math
R=math.hypot(1.335,0.471)
for p in sys.argv[1:]:
    tr=json.load(open(p+'/trace.json'))['trace']
    piv=[abs(e['w']) for e in tr if str(e['state']).startswith('PIVOT')]
    still=[abs(e['w']) for e in tr if abs(e['v'])<0.03 and not str(e['state']).startswith('PIVOT') and e['state'] not in ('BOOT',)]
    lane=[abs(e['w']) for e in tr if str(e['state']).startswith('LANE')]
    rev=[abs(e['v']) for e in tr if e['v']<-0.02]
    print(p.split('/')[-3]+'/'+p.split('/')[-1], 'pivot states: max %.2f rad/s (nose corner %.2f m/s); other turning at standstill: max %.2f rad/s (%.2f m/s); in the lane: max %.2f rad/s; fastest reverse %.2f m/s'%(max(piv or [0]), max(piv or [0])*R, max(still or [0]), max(still or [0])*R, max(lane or [0]), max(rev or [0])), flush=True)
