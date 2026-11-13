import json, pickle, subprocess, sys, os, glob
import render_video as RV
RES={}; REC={}
for f in glob.glob('results_*.json'): RES.update(json.load(open(f)))
for f in glob.glob('rec_*.pkl'): REC.update(pickle.load(open(f,'rb')))
os.makedirs('videos',exist_ok=True)
def after(rec,ph_prefixes):
    i=next((k for k,r in enumerate(rec) if r['ph'][:2].strip() in ph_prefixes or r['ph'][:1] in ph_prefixes),0)
    return rec[max(0,i-6):]
CH=[]  # (name, clip file, title card lines)
def clip(num,key,title,card,start=None,**kw):
    if key not in REC: print('missing',key); return
    rec=REC[key] if start is None else after(REC[key],start)
    out=f'videos/{num:02d}_{key}.mp4'; card_f=f'videos/card_{num:02d}.mp4'
    RV.title_card(card_f,card,secs=3)
    RV.render(rec,out,title,**kw); CH.append((key,card_f,out)); print('rendered',out,flush=True)
which=sys.argv[1] if len(sys.argv)>1 else 'all'
r=RES
def ev(k): return r.get(k,{})
jobs=[]
if which in('all','a','a1'):
    c=ev('cycle_full'); p5=c.get('phase5',{})
    clip(1,'cycle_full','1 · Full cycle: dock, latch, tip, tow, stand up, release',
         ['1 · Full cycle on wet grass','108 kg bin (96 kg load), wet grass friction 0.45',
          f"Tipped to 48° in ~48 s · actuator ~1.1 kN of 2.5 kN · anti-tip rollers catch the tug ({p5.get('pitch_max','?')}° pitch)",
          'Slow actuator phases shown at 4× speed'])
if which in('all','a'):
    t=ev('turn')
    clip(2,'turn','2 · Towing round a 2.5 m bend, then spinning in place',
         ['2 · Turning with the bin in tow',f"Rear frame yaws freely on the turntable",
          f"Arc: tug turned {t.get('yaw_arc_deg','?')}° (target {t.get('expected_arc_deg','?')}°) · spin: {t.get('yaw_spin_deg','?')}°"],start=('6',),speed_phases=())
if which in('all','b'):
    for n,g in ((3,15),(4,20)):
        k=f'climb_{g}_0.45'; c=ev(k); p7=c.get('phase7',{})
        clip(n,k,f'3 · Uphill tow at {g}% on wet grass',[f'3 · Climbing {g}% wet grass','Full 108 kg bin, 0.5 m/s, 2WD',
             f"Distance made {p7.get('dist','?')} m of 5 m · min caster load {p7.get('caster_min','?')} N · flipped: {'yes' if c.get('flipped') else 'no'}"],start=('6',),speed_phases=())
    k='estop_15_0.45'; c=ev(k)
    clip(5,k,'4 · Emergency stop going downhill, 15% wet grass',['4 · Downhill emergency stop','15% grade, wet grass, full bin, 0.5 m/s',
         f"Spring brakes clamp · slide {c.get('slide_m','?')} m · stopped: {'yes' if c.get('stops') else 'no'}"],start=('6',),speed_phases=())
if which in('all','c'):
    from model_revF import TX
    X0=TX/1000+0.25
    TER={'pothole_100mm':[(X0+1.0,X0+1.4,0.125,0.565,0.002,'#3d3428')],'bump_60mm':[(X0+1.05,X0+1.35,0.095,0.595,0.06,'#8a6d4a')]}
    for n,k,lab in ((6,'pothole_100mm','100 mm pothole'),(7,'bump_60mm','60 mm sharp bump')):
        c=ev(k)
        clip(n,k,f'5 · Towing over a {lab} (left wheels)',[f'5 · {lab[0].upper()+lab[1:]} under the left wheels','Full bin, 0.5 m/s, damp ground',
             f"Got across: {'yes' if c.get('reached_4m') else 'NO'} · max roll {c.get('phase7',{}).get('roll_max','?')}°"],start=('6',),speed_phases=(),terrain=TER[k])
    k='camber_30'; c=ev(k)
    clip(8,k,'6 · 30% side slope: parked, then driving across',['6 · Side slope (camber) 30%','Full bin, parked on brakes, then driving across',
         f"Max roll {c.get('phase7',{}).get('roll_max','?')}° · tipped over: {'yes' if c.get('flipped') else 'no'}"],start=('6',),speed_phases=(),az=-15,el=18)
json.dump([list(x) for x in CH],open(f'videos/chapters_{which}.json','w'))
