import json, glob, os
import carrier_sitl as C
rows=[]
for d in ('RevH2','B2F'):
    for s in C.SCEN:
        R=json.load(open('sitl_out/%s__%s.json'%(d,s)))
        rows.append(dict(d=d,s=s,exp=R['expect'],res=R['result'],strict=R['strict_pass'],defects=R['defects'],mins=R['sim_min'],wh=R['energy_wh'],
            hedge=R['hedge_min_m'],hedge_at=R['hedge_at_s'],region=R['region_min_m'],bin=R['bin_min_m'],obst=R['obst_min_m'],person=R['person_min_m'],
            stops=R['stops'],pivots=R['pivots'],place=max([p['err_m'] for p in R['placements']] or [0]),hand=max([p['handle_err_deg'] for p in R['placements']] or [0]),
            imax=R['i_motor_max_A'],p95=R['est_lat_p95_m'],below10=R['n_chk_below_0p10'],alerts=R['alerts'],wall=R['wall_s'],events=[e for e in R['events'] if 'alternate' in e[1] or 'pass bin' in e[1] or 'HOLD' in e[1]]))
json.dump(rows,open('res/s9_summary.json','w'),indent=1)
G6={}
for s in C.SCEN:
    try:
        r=json.load(open('../../sitl/out/G6/%s/result.json'%s)); G6[s]=(r['result'],r.get('expect'),round(r['sim_time_s']/60,1),r['energy_wh'],(r.get('lateral') or {}).get('hedge_clear_min_m'))
    except Exception: G6[s]=None
json.dump(G6,open('res/s9_g6_ref.json','w'),indent=1)
for r in rows: print('%-6s %-22s exp=%-5s got=%-5s strict=%-5s %6.1f min %6.1f Wh hedge %+.3f@%s reg %+.3f bin %.3f obst %.3f pers %.2f stops %d place %.2f/%.0f I %.1f p95 %s <0.10:%d %s %s'%(r['d'],r['s'],r['exp'],r['res'],r['strict'],r['mins'],r['wh'],r['hedge'],r['hedge_at'],r['region'],r['bin'],r['obst'],r['person'],r['stops'],r['place'],r['hand'],r['imax'],r['p95'],r['below10'],r['defects'],r['events'][:2]))
print(G6)
