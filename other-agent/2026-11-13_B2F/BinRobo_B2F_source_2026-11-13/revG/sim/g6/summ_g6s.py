#!/usr/bin/env python3
"""compact print of G6 suite results matching a glob (default all run-3 tow/ballast files)"""
import json, glob, os, sys
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(H,'..')
pat=sys.argv[1] if len(sys.argv)>1 else '*M110h*'
for f in sorted(glob.glob(os.path.join(R,'results_G6_*%s*.json'%pat))):
    try: d=json.load(open(f))
    except Exception as e: print(os.path.basename(f),'ERR',e); continue
    n=os.path.basename(f)[11:-5]
    if 'release' in d:
        ev=[e[1] for e in d.get('events',[])][-2:]
        print(n,'OK' if d.get('ok') else 'FAIL','rel',d['release'].get('released'),'tilt_end',d.get('bin_tilt_abs_end'),'mon',d.get('mon'),'|',' / '.join(ev)[:200])
    elif 'stats' in d:
        print(n,d['stats']['capture'],d['stats']['first_try'],d['stats']['n'],'fp',d['stats']['false_positives'],d['stats']['counts'])
    else:
        keep={k:d.get(k) for k in ('ok','grab','dist_m','time_s','stop_dist_m','slide_after_stop_m','hold_creep_m','hitch_yaw_max_deg','max_bin_yaw_deg','bin_yaw_max_deg','roll_max_deg','max_roll_deg','caster_min_N','antitip_peak_N','pawl_bounce','still_captured','captured_throughout','peak_hook','cpu_s') if k in d}
        print(n,keep)
