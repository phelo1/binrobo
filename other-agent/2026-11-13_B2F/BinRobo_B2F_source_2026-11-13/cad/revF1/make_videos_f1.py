# Rev F.1 + recovery video chapters. usage: python make_videos_f1.py <chapter numbers comma-separated | all>
import json, pickle, sys, os, glob
import render_video as RV
from model_revF import TX
os.makedirs('videos',exist_ok=True)
X0=TX/1000+0.25
def J(f):
    try: return json.load(open(f))
    except Exception: return {}
def P(f): return pickle.load(open(f,'rb'))
def after(rec,prefixes,back=6):
    i=next((k for k,r in enumerate(rec) if any(r['ph'].startswith(p) for p in prefixes)),0); return rec[max(0,i-back):]
F1=lambda t: J(f'study/F1__{t}.json'); F0=lambda t: J(f'study/F0__{t}.json')
g=lambda d,*k: (lambda x: x)(__import__('functools').reduce(lambda a,b: a.get(b,{}) if isinstance(a,dict) else {},k,d)) or '?'
HEDGE=(0.25,0.45,0.22); WALL=(0.55,0.52,0.48)
REC_SCN={'R1':[(-1.81,0.0,0.6,0.25,3.0,0.6,HEDGE)],'R1a':[(-1.11,0.0,0.6,0.25,3.0,0.6,HEDGE)],'R2':[(-0.55,-1.50,0.6,0.55,0.25,0.6,WALL)]}
def chapters():
    c=F1('cycle'); c20=F1('climb20'); c15=F1('climb15'); e=F1('estop20'); b=F1('bump60'); b0=F0('bump60'); cam=F1('camber30'); tu=F1('turn_closed'); t0=F0('turn_open')
    r1=J('study/recovery_R1.json'); r2=J('study/recovery_R2.json'); r1a=J('study/recovery_R1a.json')
    return [
     (1,'study/F1__cycle.pkl',None,'1 · Rev F.1 full cycle: dock, latch, tip, tow, soft stop, stand up, release',
      ['1 · Rev F.1 full cycle (wet grass)','108 kg bin, ballast forward, rollers at 100 mm, rubber hook bush',
       f"Tips to 48° in {c.get('tip_s','?')} s · actuator peak {c.get('act_peak_raw_N','?')} N (Rev F: 2,500 N spike at the hard stop)",
       'Slow actuator phases at 8× speed'],dict(speed_map={'3':8,'5':8,'9':8,'1':2,'2':2,'4':2,'6':2,'7':2,'8':2,'10':2,'11':2,'12':2})),
     (2,'study/F1__climb20.pkl',('7a',),'2 · Rev F.1 towing up a 20% wet-grass slope',
      ['2 · 20% climb, wet grass (μ 0.45)',f"Made 5 m at {c20.get('avg_v','?')} m/s average (0.5 commanded: wheels slipping)",
       f"Rev F: {F0('climb20').get('avg_v','?')} m/s · 15% climb: {c15.get('avg_v','?')} m/s · this is the traction limit for a ~105 kg 2WD tug"],dict(skip=2)),
     (3,'study/F1__estop20.pkl',('7a',),'3 · Rev F.1 emergency stop, 20% downhill, wet grass',
      ['3 · Downhill emergency stop',f"20% wet grass, full bin, 0.5 m/s",f"Spring brakes stop it in {e.get('slide_m','?')} m (Rev F {F0('estop20').get('slide_m','?')} m)"],dict(skip=1)),
     (4,'study/F0__bump60.pkl',('7',),'4a · Rev F on a TRUE 60 mm step: stuck (rollers ground, drive wheels lifted)',
      ['4 · 60 mm sharp step under the left wheels','Correction: the Rev F "60 mm" test was really 30 mm high',
       'Rev F at a true 60 mm: caster climbs, rollers ground, drive wheels lift: STUCK',
       f"Rev F.1 (rollers 100 mm, casters forward): gets over · hook peak {g(b,'phase7','hook_max')} N, 99th pct {g(b,'phase7','hook_p99')} N"],
      dict(skip=2,max_frames=70,terrain=[(X0+1.05,X0+1.35,0.095,0.595,0.06,'#8a6d4a')])),
     (5,'study/F1__bump60.pkl',('7',),'4b · Rev F.1 over the same 60 mm step',None,dict(skip=1,terrain=[(X0+1.05,X0+1.35,0.095,0.595,0.06,'#8a6d4a')])),
     (6,'study/F1__camber30.pkl',('7a',),'5 · Rev F.1 on a 30% side slope',
      ['5 · 30% side slope (camber), damp ground',f"Drifts {cam.get('drift_while_driving_m','?')} m downslope over 3 m of travel",
       f"Creep after stopping {cam.get('creep_after_stop_m','?')} m · roll-over: {'YES' if cam.get('flipped') else 'no'}"],dict(skip=2,az=-15,el=18)),
     (7,'study/F1__turn_closed.pkl',('7',),'6 · Closed-loop heading control round a 2.5 m bend, then a spin request',
      ['6 · Turning with the bin in tow',f"Open-loop (Rev F): {t0.get('arc_deg','?')}° of 92° · closed-loop P heading (F.1): {tu.get('arc_deg','?')}° in {tu.get('arc_time_s','?')} s",
       f"Spin-in-place request: 60° hitch cap holds the hitch to {tu.get('hitch_max_spin','?')}° (Rev F hit the 70° stop)"],dict(skip=1,span=3.2)),
     (8,'study/recovery_R2.pkl',None,'7 · Recovery: empty bin left SIDEWAYS, handle side blocked by a wall',
      ['7 · Recovery: sideways bin, handle side blocked','Lidar + tag spot the pose · bumper swings it 90° round its wheels · dock · grab',
       f"Result: {'SUCCESS' if r2.get('success') else 'FAILED'} · rotated {r2.get('rotated_deg','?')}° · whole job {r2.get('sim_time_s','?')} s (48 s of it tipping)"],
      dict(speed_map={'R1':2,'R2':2,'R3':3,'R4':1,'R5':2,'R6':3,'R7':1,'1':1,'2':2,'3':8,'4':2,'5':8,'6':2,'R8':2},span=4.0,el=48,az=-60,cen_w=0.5,boxes=REC_SCN['R2'])),
     (9,'study/recovery_R1.pkl',None,'8 · Recovery: empty bin left BACKWARDS, hedge 1.5 m behind',
      ['8 · Recovery: backwards bin, hedge behind it','Not enough room to dock from the handle side → swing the bin 180° round its wheels',
       f"Result: {'SUCCESS' if r1.get('success') else 'FAILED'} · rotated {r1.get('rotated_deg','?')}° (bin rolled {(r1.get('events') or [[0,'']])[1][1].split('moved ')[-1] if r1.get('events') else '?'}) · {r1.get('sim_time_s','?')} s total"],
      dict(speed_map={'R1':2,'R2':2,'R3':3,'R4':1,'R5':2,'R6':3,'R7':1,'1':1,'2':2,'3':8,'4':2,'5':8,'6':2,'R8':2},span=4.2,el=48,az=-60,cen_w=0.5,boxes=REC_SCN['R1'])),
     (10,'study/recovery_R1a.pkl',('R4',),'9 · Failure mode: hedge only 0.8 m behind - the bin wedges',
      ['9 · Failure mode: bin hard up against the hedge','Swinging it, the bin also rolls ~0.6 m towards its handle per 90° → wedges at ~95°',
       'Firmware response: stop, photo + 4G alert, go home, retry next window'],
      dict(speed_map={'R4':3,'R5':2},span=4.0,el=48,az=-60,cen_w=0.5,boxes=REC_SCN['R1a'],max_frames=150)),
    ]
def render_one(n):
    for (num,f,start,title,card,kw) in chapters():
        if num!=n: continue
        if not os.path.exists(f): print('missing',f); return
        rec=P(f); rec=after(rec,start) if start else rec
        if card: RV.title_card(f'videos/f1card_{num:02d}.mp4',card,secs=4 if len(card)>3 else 3)
        RV.render(rec,f'videos/f1_{num:02d}.mp4',title,**kw); print('rendered',num,flush=True)
if __name__=='__main__':
    arg=sys.argv[1]
    if arg=='intro':
        RV.title_card('videos/f1card_00.mp4',['Bin tug Rev F.1','Optimised Rev F + bin-recovery manoeuvres','MuJoCo physics, CAD meshes · all numbers are simulation estimates'],secs=4)
    else:
        for n in [int(x) for x in arg.split(',')]: render_one(n)
