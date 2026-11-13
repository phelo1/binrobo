#!/usr/bin/env python3
"""Builds docs/reviews/ITER1_conceptB.md from it1/res/*.json (gate_it1*.json, handcalc_it1.json, cost_it1.json, geo_check.json)
and the frozen G6 gate (../res/gate_table.json, ../res/B_*.json). ASCII only. Run summarize_it1.py (and per tag) first."""
import json, os, glob
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(H,'res'); CG=os.path.join(H,'..'); P=os.path.abspath(os.path.join(H,'..','..','..','..'))
J=lambda f: json.load(open(f)) if os.path.exists(f) else None
S=J(os.path.join(R,'gate_it1_f9.json')); S7=J(os.path.join(R,'gate_it1.json')); G6=J(os.path.join(CG,'res','gate_table.json'))
HC=J(os.path.join(R,'handcalc_it1.json')); C=J(os.path.join(R,'cost_it1.json')); GEO=J(os.path.join(R,'geo_check.json'))
TAGS=[('_pm110f9','mass +10 %'),('_pm090f9','mass -10 %'),('_pmu085f9','friction -15 %'),('_pcrr09f9','bin crr 0.09')]
PT={t:J(os.path.join(R,'gate_it1%s.json'%t)) for t,_ in TAGS}
def B1(n,t='_f9'): return J(os.path.join(R,'B1_'+n+t+'.json'))
def B0(n): return J(os.path.join(CG,'res','B_'+n+'.json'))
pf=lambda b: 'PASS' if b else '**FAIL**'
# ---------------- after-table cells
def g1cell(s):
    b=s['bins']; f=lambda k: '%d/%d'%(b[k]['captured'],b[k]['n']) if isinstance(b[k],dict) else 'missing'
    return 'WEB140 %s; ESE SL %s; ESE CL %s; pooled %d/%d; false holds %d; knocked %d'%(f('WEB140'),f('ESE240SL'),f('ESE240CL'),s['pooled'],s['n'],s['false_holds'],s['knocked'])
def g2cell(s):
    r=[v for v in s['runs'].values() if v]; ok=sum(1 for v in r if v['ok'])
    return '%d/6; %.1f-%.1f s, creep <= %.3f m'%(ok,min(v['t'] for v in r),max(v['t'] for v in r),max(v['creep'] for v in r)) if r else 'missing'
def g3cell(s):
    o,b=s['one'],s['both']
    return 'one side %s (no bin contact, lip seated, clear %.0f mm); full width %s'%('PASS' if o and o['ok'] else 'FAIL',1000*o['clear_min'] if o else 0,('PASS' if b['ok'] else 'stops at %.2f m (drive wheels at the edge)'%b['dist']) if b else 'missing')
def g4cell(s):
    f,r=s['runs']['fwd'],s['runs']['rev']
    return 'castors leading %.2f m / bin leading %.2f m; slide %.3f m'%(f['stop'],r['stop'],max(f['slide'],r['slide'])) if f and r else 'missing'
def g5cell(s):
    r=s['run']; return 'roll %.2f deg; 180 deg pivot swept %.2f m dia (limit 3.2)'%(r['roll'],r['swept']) if r else 'missing'
def g6cell(s):
    bad=['%s %s'%(k,v) for k,v in s['cases'].items() if v!='PASS']
    return '%d/18, %d TIPS%s'%(s['passed'],s['tips'],('. Not passing: '+', '.join(bad)) if bad else '; WEB 140 6/6, ESE CL 6/6, SL 250 6/6 (all docked)')
def g7cell(s):
    r=s['runs']; c=r.get('climb_m25_c09')
    if not isinstance(c,dict): return 'missing'
    return 'climb %.1f / %.1f s at dt 0.5 / 0.25 ms; step and e-stop verdicts %s'%(c['t'][0],c['t'][1],'unchanged' if all(isinstance(v,dict) and v['ok'] for v in r.values()) else 'CHANGED')
def g8cell(s):
    p=[v for v in s['poses'].values() if v]
    return 'all 8 poses: drive >= %.0f N, castors >= %.0f N; hand calc min tip %.1f deg; castor lift-off %.1f deg (110 kg)'%(min(min(v['dL'],v['dR']) for v in p),min(v['castors'] for v in p),s['handcalc_min_tip_deg'],s['castor_liftoff_110']) if p else 'missing'
cells={'G1':g1cell,'G2':g2cell,'G3':g3cell,'G4':g4cell,'G5':g5cell,'G6':g6cell,'G7':g7cell,'G8':g8cell,'G9':lambda s:'%.1f kg'%s['kg']}
names=[r[0] for r in G6['table']]
tab=['| item | B (G6 gate, frozen design) | B1 with F1-F7 | B1 final (F1-F7 + F9) | final B1 result |','|------------|------------------------------|------|------|----------------------------------|']
for i,k in enumerate(('G1','G2','G3','G4','G5','G6','G7','G8','G9')):
    row=G6['table'][i]; tab.append('| %s | %s: %s | %s | %s | %s |'%(names[i],row[3].replace('**',''),row[4],pf(S7[k]['PASS']),pf(S[k]['PASS']),cells[k](S[k])))
nB0=sum(1 for r in G6['table'][:9] if 'PASS'==r[3]); tab.append('| **Items passed** | **%d/9** | **%d/9** | **%d/9** | |'%(nB0,S7['passed'],S['passed']))
TABLE='\n'.join(tab)
fails=[k for k in ('G1','G2','G3','G4','G5','G6','G7','G8','G9') if not S[k]['PASS']]
# ---------------- G6 matrix
mat=['| bin | flat full | flat empty | up 12 % full | up 12 % empty | down 12 % full | down 12 % empty |','|----|----|----|----|----|----|----|']
for b in ('WEB140','ESE240CL','ESE240SL250'):
    cells0=[]; cells1=[]
    for c in ('flat','up12','dn12'):
        for f in ('full','empty'):
            d0=J(os.path.join(CG,'res','B_rel_%s_%s_%s_SD2.json'%(b,c,f))); d7=B1('rel_%s_%s_%s'%(b,c,f),''); d1=B1('rel_%s_%s_%s'%(b,c,f))
            cells1.append('%s / %s / %s'%(d0['verdict'] if d0 else '-',d7['verdict'] if d7 else '-',d1['verdict'] if d1 else 'missing'))
    mat.append('| %s | %s |'%(b.replace('ESE240','ESE '),' | '.join(cells1)))
MAT='\n'.join(mat)
# set-down detail: worst tilt before withdraw, max hang tilt at grab
rel=[B1('rel_%s_%s_%s'%(b,c,f)) for b in ('WEB140','ESE240CL','ESE240SL250') for c in ('flat','up12','dn12') for f in ('full','empty')]
rel=[d for d in rel if d]
REL_TILT=max(abs(d['release'].get('tilt_before_withdraw',0)) for d in rel) if rel else 0
REL_END=max(d['bin_tilt_abs_end'] for d in rel) if rel else 0
# ---------------- G8 table before/after
g8=['| pose | G6 B drive L / R (N) | G6 B castors (N) | B1 drive L / R (N) | B1 castors (N) | B1 verdict |','|----|----|----|----|----|----|']
for p in ('up','dn','crL','crR'):
    for k in (110,60):
        a=B0('static_%s_%d'%(p,k)); b=B1('static_%s_%d'%(p,k))
        nm={'up':'12 % facing up','dn':'12 % facing down','crL':'12 % cross, left low','crR':'12 % cross, right low'}[p]+', %d kg'%k
        g8.append('| %s | %.0f / %.0f | %.0f | %s | %s | %s |'%(nm,a['driveL'],a['driveR'],a['caster_sum'],('%.0f / %.0f'%(b['driveL'],b['driveR'])) if b else '-',('%.0f'%b['caster_sum']) if b else '-',pf(b['ok']) if b else 'missing'))
G8T='\n'.join(g8)
hc0=HC['G6_B']['cases'][0]; hc1=HC['ITER1_B1']['cases'][0]; hc160=HC['ITER1_B1']['cases'][1]
# ---------------- geometry check table
geo=['| bin | standing tilt (deg) | lip rim bottom (m) | ledge underside (m) | back face inboard of lip root at z 0.45 m (mm) |','|----|----|----|----|----|']
for b in ('WEB140','ESE140CL','ESE240SL','ESE240CL','ESE240SL250'):
    g=[o for o in GEO if o['bin']==b]
    fa=[o['face_at']['0.45'] if '0.45' in o['face_at'] else o['face_at'][0.45] for o in g]
    geo.append('| %s | %.1f | %.3f-%.3f | %.3f-%.3f | %.0f-%.0f |'%(b.replace('ESE240','ESE 240 ').replace('ESE140','ESE 140 ').replace('WEB140','Weber 140'),abs(g[0]['pitch_deg']),min(o['rim_bottom_z'] for o in g),max(o['rim_bottom_z'] for o in g),
               min(o['ledge_z'] for o in g),max(o['ledge_z'] for o in g),-1000*max(fa),-1000*min(fa)))
GEOT='\n'.join(geo)
# ---------------- extras
def mc(b):
    d=B1('grab_'+b); return d
X1=mc('ESE240SL250'); X2=mc('ESE140CL')
xs=lambda d,n: ('%s: %d/%d captured, %d false holds, %d knocked'%(n,d['captured'],d['n'],d['false_holds'],d['knocked'])) if d else '%s: not run'%n
EXTRA_MC=xs(X1,'ESE 240 SL with 250 mm wheels (seed 204)')+'; '+xs(X2,'ESE 140 CL (seed 205)')
st_r=B1('step40_both_ramp',''); st_w=B1('step40_both_rw560_tc102kv',''); st_b=B1('step40_both')
# ---------------- perturbations
pt=['| perturbation | G1 (10 per bin) | G2 mu 0.22 / 0.25 | G3 one side | G4 fwd / rev | G5 | G6 6 hardest | G8 3 poses |','|----|----|----|----|----|----|----|----|']
for t,lab in TAGS:
    def L(n,t=t): return J(os.path.join(R,'B1_'+n+t+'.json'))
    g=[L('grab_'+b) for b in ('WEB140','ESE240SL','ESE240CL')]
    g1='%s; fh %d, kn %d'%(' / '.join('%d/%d'%(x['captured'],x['n']) if x else '-' for x in g),sum(x['false_holds'] for x in g if x),sum(x['knocked'] for x in g if x))
    c=[L('climb_m22_c09'),L('climb_m25_c06')]; g2=' / '.join(('PASS %.1f s'%x['time_s'] if x['ok'] else 'FAIL %.2f m'%x['dist_m']) if x else '-' for x in c)
    s1=L('step40_one'); g3=('PASS' if s1['ok'] else 'FAIL') if s1 else '-'
    e=[L('estop12_fwd'),L('estop12_rev')]; g4=' / '.join(('%s %.2f m'%('PASS' if x['ok'] else 'FAIL',x['stop_dist_m'])) if x else '-' for x in e)
    w=L('towstab'); g5=('PASS %.2f m'%w['swept_diameter_m'] if w['ok'] else 'FAIL') if w else '-'
    rr=[L('rel_'+k) for k in ('WEB140_up12_full','WEB140_dn12_empty','ESE240CL_up12_full','ESE240CL_flat_empty','ESE240SL250_up12_empty','ESE240SL250_dn12_full')]
    g6='%d/6%s'%(sum(1 for x in rr if x and x['verdict']=='PASS'),(' ('+', '.join(x['bin'].replace('ESE240','')+' '+x['case']+' '+x['fill']+' '+x['verdict'] for x in rr if x and x['verdict']!='PASS')+')') if any(x and x['verdict']!='PASS' for x in rr) else '')
    ss=[L('static_up_110'),L('static_crL_110'),L('static_dn_60')]; g8='%d/3'%sum(1 for x in ss if x and x['ok'])
    pt.append('| %s | %s | %s | %s | %s | %s | %s | %s |'%(lab,g1,g2,g3,g4,g5,g6,g8))
PTT='\n'.join(pt)
# peaks for the actuator spec
pk=[]
for n in ('step40_one','step40_both','step40_one_dt025','climb_m25_c09','estop12_fwd','towstab'):
    d=B1(n)
    if d: pk.append((n,d['peak'].get('lift_N',[0])[0],d['peak'].get('pad_N',[0])[0],d['peak'].get('nib_rim_N',[0])[0]))
LIFTPK=max(p[1] for p in pk) if pk else 0; LIFTPK05=max([p[1] for p in pk if 'dt025' not in p[0]] or [0])
padall=[]
for f in glob.glob(os.path.join(R,'B1_*.json')):
    d=J(f)
    if isinstance(d,dict):
        v=d.get('pad_N') if 'pad_N' in d else (d.get('peak',{}) or {}).get('pad_N',[None])[0]
        if v: padall.append((float(v),os.path.basename(f)))
padall.sort(); PADPK=padall[-1][0] if padall else 0; PADPKF=padall[-1][1] if padall else '-'
padf9=[p for p in padall if p[1].endswith('f9.json')]; PADF9=padf9[-1][0] if padf9 else 0; PADF9F=padf9[-1][1] if padf9 else '-'
padnom=[p for p in padall if p[1].endswith('_f9.json')]; PADNOM=padnom[-1][0] if padnom else 0; PADNOMF=padnom[-1][1] if padnom else '-'
clim=B1('climb_m22_c09'); TQ=clim['peak'].get('wheel_torque_Nm',[0])[0] if clim else 0

def fsub(tag):
    tot=0; ok=0; parts=[]; kn=0; fh=0
    for b,n in (('ESE240CL','CL'),('WEB140','WEB'),('ESE240SL250','SL250'),('ESE140CL','ESE140CL')):
        d=B1('grab_%s'%b,tag)
        if d: tot+=d['n']; ok+=d['captured']; kn+=d['knocked']; fh+=d['false_holds']; parts.append('%s %d/%d'%(n,d['captured'],d['n']))
    return ('%d/%d captured (%s), %d knocked, %d false holds'%(ok,tot,', '.join(parts),kn,fh)) if tot else 'not run'
def f8(): return fsub('_f8')
F8S=f8(); F9S=fsub('_f9s')
gt=[B1('grab_'+b) for b in ('WEB140','ESE240SL','ESE240CL','ESE240SL250','ESE140CL')]+[B1('grab_'+b,t) for t,_ in TAGS for b in ('WEB140','ESE240SL','ESE240CL')]
GRAB_TOTAL=sum(d['n'] for d in gt if d)
gb=lambda k: ('%d/30'%S['G1']['bins'][k]['captured']) if isinstance(S['G1']['bins'][k],dict) else '-'
def fmt(x,n=0): return ('%.'+str(n)+'f')%x
T=open(os.path.join(H,'report_tpl_it1.md')).read()
g7b=lambda k: ('%d/30'%S7['G1']['bins'][k]['captured']) if isinstance(S7['G1']['bins'][k],dict) else '-'
rep={'{{F8_SUB}}':F8S,'{{F9_SUB}}':F9S,'{{G1_POOL7}}':'%d/%d'%(S7['G1']['pooled'],S7['G1']['n']),'{{G1_WEB7}}':g7b('WEB140'),'{{G1_SL7}}':g7b('ESE240SL'),'{{G1_CL7}}':g7b('ESE240CL'),'{{NB7}}':str(S7['passed']),'{{PADPKF}}':PADPKF,'{{PADNOM}}':fmt(PADNOM),'{{PADF9}}':fmt(PADF9),'{{PADF9F}}':PADF9F,'{{PADNOMF}}':PADNOMF,'{{COST_OLD}}':'4,412','{{GRAB_TOTAL}}':str(GRAB_TOTAL),'{{SL250_MC}}':(('%d/%d in its 30-run MC'%(X1['captured'],X1['n'])) if X1 else '-'),'{{G1_WEB}}':gb('WEB140'),'{{G1_SL}}':gb('ESE240SL'),'{{G1_CL}}':gb('ESE240CL'),'{{TABLE}}':TABLE,'{{NB0}}':str(nB0),'{{NB1}}':str(S['passed']),'{{FAILS}}':', '.join(fails) if fails else 'none','{{MAT}}':MAT,'{{G8T}}':G8T,'{{GEOT}}':GEOT,'{{PTT}}':PTT,
     '{{EXTRA_MC}}':EXTRA_MC,'{{REL_TILT}}':fmt(REL_TILT,1),'{{REL_END}}':fmt(REL_END,1),
     '{{HC0_LIFT}}':fmt(hc0['castor_liftoff_about_drive_axle_deg'],1),'{{HC1_LIFT}}':fmt(hc1['castor_liftoff_about_drive_axle_deg'],1),'{{HC160_LIFT}}':fmt(hc160['castor_liftoff_about_drive_axle_deg'],1),
     '{{HC0_MU}}':fmt(hc0['mu_req_12'],3),'{{HC1_MU}}':fmt(hc1['mu_req_12'],3),'{{HC1_LAT}}':fmt(hc1['tip_lateral_deg'],1),'{{HC1_FWD}}':fmt(hc1['tip_forward_over_castors_deg'],1),'{{HC1_REAR}}':fmt(hc1['rear_tip_on_antitip_deg'],1),
     '{{HC1_TQ}}':fmt(hc1['torque_per_wheel_12_Nm'],1),'{{HC1_TQ125}}':fmt(hc1['torque_x1p25'],1),
     '{{G1_POOL}}':'%d/%d'%(S['G1']['pooled'],S['G1']['n']),'{{G1_KN}}':str(S['G1']['knocked']),'{{G1_FH}}':str(S['G1']['false_holds']),
     '{{STEP_RAMP}}':('PASS: %.2f m, bin held and seated, no bin-ground contact (run with F1-F7)'%(st_r['dist_m'])) if st_r and st_r['ok'] else 'see file',
     '{{STEP_RW}}':('stops at %.2f m'%st_w['dist_m']) if st_w else 'not run','{{STEP_B}}':('%.2f m'%st_b['dist_m']) if st_b else '-',
     '{{LIFTPK}}':fmt(LIFTPK),'{{LIFTPK05}}':fmt(LIFTPK05),'{{PADPK}}':fmt(PADPK),
     '{{COST_DELTA}}':fmt(C['delta']['all_in']),'{{COST_NEW}}':'{:,.0f}'.format(C['new_all_in']),'{{COST_BASE}}':'{:,.0f}'.format(C['basis']['all_in']),
     '{{SWEPT}}':fmt(S['G5']['run']['swept'],2) if S['G5']['run'] else '-','{{MASS}}':fmt(S['G9']['kg'],1)}
others=[k for k in fails if k!='G3']
OTH=''.join('%d. **%s fails on the final B1**: %s. See section 2.\n'%(i+2,k,cells[k](S[k])) for i,k in enumerate(others))
rep['{{OTHER_FAILS}}']=OTH.rstrip('\n')
rep['{{G6_FINAL}}']='%d/18, %d tips'%(S['G6']['passed'],S['G6']['tips'])
rep['{{VERDICT}}']=('Under the frozen decision rule, B1 has **not** cleared the gate: the only open item is G3(b), the full-width sharp step, which is handled by lane ramps rather than by the vehicle.' if fails==['G3'] else ('Under the frozen decision rule, B1 has **not** cleared the gate.' if fails else 'B1 clears the gate.'))
for k,v in rep.items(): T=T.replace(k,v)
assert '{{' not in T,[l for l in T.split('\n') if '{{' in l]
out=os.path.join(P,'docs','reviews','ITER1_conceptB.md'); open(out,'w').write(T)
bad=sorted(set(ch for ch in T if ord(ch)>127)); print('written',out,'non-ascii:',bad)
