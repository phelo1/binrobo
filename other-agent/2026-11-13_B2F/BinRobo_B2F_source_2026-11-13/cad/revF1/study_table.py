# Collects study/<variant>__<test>.json into study_table.json / .csv (variant -> key metrics)
import json, glob, csv, sys
D={}
for f in glob.glob('study/*__*.json'):
    d=json.load(open(f)); D.setdefault(d['variant'],{})[d['test']]=d
def g(d,*p,default=None):
    for k in p:
        if not isinstance(d,dict) or k not in d: return default
        d=d[k]
    return d
ROWS=[]
order=sys.argv[1].split(',') if len(sys.argv)>1 else sorted(D)
for v in order:
    if v not in D: continue
    T=D[v]; c=T.get('cycle',{}); cl=T.get('climb20',{}); b=T.get('bump60',{}); e=T.get('estop20',{}); c15=T.get('climb15',{}); cam=T.get('camber30',{}); tu=T.get('turn_closed',{})
    r=dict(variant=v,desc=c.get('desc') or cl.get('desc') or '',
        tug_kg=c.get('tug_kg') or cl.get('tug_kg'),
        tip_s=c.get('tip_s'),act_50ms_N=c.get('act_peak_50ms_N'),act_raw_N=c.get('act_peak_raw_N'),act_raw_phase=(c.get('act_peak_raw_at') or [0,''])[1][:20],
        tow_hook_p99=g(c,'phase7','hook_p99'),tow_caster_p10=g(c,'phase7','caster_p10'),
        tip_pitch=g(c,'phase5','pitch_max'),tip_caster_unl=g(c,'phase5','caster_unloaded_frac'),
        c20_reached=cl.get('reached_5m'),c20_v=cl.get('avg_v'),c20_caster_unl=g(cl,'phase7','caster_unloaded_frac'),c20_pitch90=g(cl,'phase7','pitch_p90'),
        c20_antitip90=g(cl,'phase7','antitip_p90'),c20_drive_p10=g(cl,'phase7','drive_p10'),c20_torque=g(cl,'phase7','torque_max'),c20_hook=g(cl,'phase7','hook_p99'),c20_hold=cl.get('hold_creep_m'),
        c15_v=c15.get('avg_v'),c15_caster_unl=g(c15,'phase7','caster_unloaded_frac'),
        bump_ok=b.get('reached_4m'),bump_hook_max=g(b,'phase7','hook_max'),bump_hook_p99=g(b,'phase7','hook_p99'),bump_antitip=g(b,'phase7','antitip_max'),bump_pitch=g(b,'phase7','pitch_max'),bump_hgap=g(b,'phase7','hgap_max'),
        estop20_slide=e.get('slide_m'),estop20_stops=e.get('stops'),
        cam30_drift=cam.get('drift_while_driving_m'),cam30_creep=cam.get('creep_after_stop_m'),cam30_roll=g(cam,'phase7','roll_max'),
        turn_arc=tu.get('arc_deg'),turn_time=tu.get('arc_time_s'),turn_hitch=tu.get('hitch_max_arc'),spin_hitch=tu.get('hitch_max_spin'))
    ROWS.append(r)
json.dump(ROWS,open('study_table.json','w'),indent=1)
with open('study_table.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(ROWS[0].keys())); w.writeheader(); [w.writerow(r) for r in ROWS]
keys=['variant','tug_kg','tip_s','act_50ms_N','act_raw_N','tow_hook_p99','tip_pitch','c20_reached','c20_v','c20_caster_unl','c20_pitch90','c20_antitip90','c20_drive_p10','c20_torque','c20_hook','c20_hold','bump_ok','bump_hook_max','bump_hook_p99','bump_antitip','bump_hgap','estop20_slide']
print(' | '.join(k[:9] for k in keys))
for r in ROWS: print(' | '.join(str(r[k])[:9] for k in keys))
