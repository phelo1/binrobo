#!/usr/bin/env python3
"""Build docs/reviews/CONCEPT_GATE_G6.md from cg/res (frozen-criteria scorecard + post-freeze findings). ASCII only."""
import json, os, glob
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(H,'res'); P=os.path.abspath(os.path.join(H,'..','..','..'))
def L(f):
    p=os.path.join(R,f); return json.load(open(p)) if os.path.exists(p) else None
S=L('summary_cg.json'); HC=L('handcalc_cg.json'); HM=L('handcalc_motor_g7.json'); C=L('cost_cg_g7.json')
pf=lambda b: 'PASS' if b else '**FAIL**'
def g1(c):
    s=S[c+'_G1']; pb=s['per_bin']
    if not s['complete']: return 'incomplete','-'
    t='; '.join('%s %d/%d'%(b.replace('ESE240','ESE '),pb[b]['captured'],pb[b]['n']) for b in ('WEB140','ESE240SL','ESE240CL'))
    return t+'; pooled %d/%d; false holds %d; knocked %d'%(s['pooled'],s['n'],s['false_holds'],s['knocked']),pf(s['PASS'])
def g2(c):
    r=S[c+'_G2']['runs']; bad=[k for k,v in r.items() if not v['ok']]
    t='%d/6'%S[c+'_G2']['n_pass']
    if bad: t+='; fails '+', '.join('%s (%.2f m in 25 s)'%(k.replace('mu','mu ').replace('_crr',' crr '),r[k]['dist']) for k in bad)
    else: t+='; 11.0-11.1 s, creep <= %.3f m'%max(v['creep'] for v in r.values())
    return t,pf(S[c+'_G2']['PASS'])
def g3(c):
    s=S[c+'_G3']; o,b=s['one'],s['both']
    if c=='A': t="one side %s (hitch %.1f deg); full width stops at %.2f m"%('PASS' if o['ok'] else 'FAIL',o['hitch'],b['dist'])
    else: t="one side %s (no bin contact, lip seated); full width stops at %.2f m"%('PASS' if o['ok'] else 'FAIL',b['dist'])
    return t,pf(s['PASS'])
def g4(c):
    if c=='A': r=S['A_G4']['run']; return 'stop %.2f m, slide %.3f m'%(r['stop'],r['slide']),pf(S['A_G4']['PASS'])
    r=S['B_G4']['runs']; return 'castors leading %.2f m / bin leading %.2f m; slide 0.001 m'%(r['fwd']['stop'],r['rev']['stop']),pf(S['B_G4']['PASS'])
def g5(c):
    r=S[c+'_G5']['run']
    if c=='A': return 'hitch max %.1f deg, roll %.1f deg, bin held'%(r['hitch'],r['roll']),pf(S['A_G5']['PASS'])
    return 'roll %.2f deg; 180 deg pivot swept %.2f m dia (limit 3.2)'%(r['roll'],r['swept']),pf(S['B_G5']['PASS'])
def g6(c):
    s=S[c+'_G6']; parts=[]
    for b,lab in (('WEB140','WEB 140'),('ESE240CL','ESE CL'),('ESE240SL250','SL 250')):
        cells={k[len(b)+1:]:v for k,v in s['cells'].items() if k.startswith(b+' ')}
        okn=sum(1 for v in cells.values() if v=='PASS'); badc=['%s %s'%(k.replace('12',''),v) for k,v in cells.items() if v!='PASS']
        parts.append('%s %d/6%s'%(lab,okn,(' ('+', '.join(badc)+')') if badc else ''))
    t='%d/18, %d TIPS. '%(s['n_pass'],s['tips'])+'; '.join(parts)
    if c=='B': t+='. SL 250: grab pushes the bin (no capture) in all 6'
    return t,pf(s['PASS'])
def g7(c):
    r=S[c+'_G7']['runs'][0]; return 'climb %.1f / %.1f s at dt 0.5 / 0.25 ms; step and e-stop verdicts unchanged'%(r['t05'],r['t025']),pf(S[c+'_G7']['PASS'])
def g8(c):
    s=S[c+'_G8']; bad=[k for k,v in s['poses'].items() if not v['ok']]
    if c=='A':
        t='castors 0 N on 12 %% facing up (110 and 60 kg); others OK; hand calc: tug rear lift-off %.1f deg, towed bin lateral %.1f deg'%(HC['stability_A']['tug_rear_liftoff_unladen_deg'],HC['stability_A']['towed_bin'][0]['bin_lateral_tip_deg'])
    else:
        cs=HC['stability_B']['cases']
        t='all 8 poses: drive >= %d N, castors >= %d N; hand calc: lateral %.1f deg, forward %.1f deg, rear tip-over %.1f deg (anti-tip rollers; castor lift-off %.1f deg at 110 kg)'%(
            min(min(v['dL'],v['dR']) for v in s['poses'].values()),min(v['castors'] for v in s['poses'].values()),
            min(c_['tip_lateral_deg'] for c_ in cs),min(c_['tip_forward_over_castors_deg'] for c_ in cs),min(c_['rear_tip_with_antitip_rollers_deg'] for c_ in cs),cs[0]['rear_liftoff_about_drive_axle_deg'])
    return t,pf(s['PASS'])
def g9(c): return '%.1f kg'%S[c+'_G9']['kg'],pf(S[c+'_G9']['PASS'])
rows=[('G1 Grab MC',g1),('G2 Climb 12 %',g2),('G3 40 mm step',g3),('G4 E-stop 12 % down',g4),('G5 Tow/carry stability',g5),('G6 Release / set-down',g6),('G7 dt repeat',g7),('G8 Static stability',g8),('G9 Mass',g9)]
tab=[]
for name,fn in rows:
    a,av=fn('A'); b,bv=fn('B'); tab.append((name,av,a,bv,b))
nA=sum(1 for r in tab if r[1]=='PASS'); nB=sum(1 for r in tab if r[3]=='PASS')
# post-freeze B-SD2 matrix
sd2={}
for b in ('WEB140','ESE240CL','ESE240SL250'):
    for case in ('flat','up12','dn12'):
        for f in ('full','empty'):
            d=L('B_rel_%s_%s_%s_SD2.json'%(b,case,f)); sd2['%s %s %s'%(b,case,f)]=None if not d else (d['verdict'],d['grab'])
sd2_pass=sum(1 for v in sd2.values() if v and v[0]=='PASS'); sd2_n=sum(1 for v in sd2.values() if v); sd2_tips=sum(1 for v in sd2.values() if v and v[0]=='TIPS')
json.dump(dict(table=tab,nA=nA,nB=nB,sd2=sd2,sd2_pass=sd2_pass,sd2_n=sd2_n,sd2_tips=sd2_tips),open(os.path.join(R,'gate_table.json'),'w'),indent=1)
print(nA,nB,sd2_pass,sd2_n,sd2_tips)
for r in tab: print(r)
for k,v in sd2.items(): print(k,v)
# ---------------- fill the template
T=open(os.path.join(H,'gate_report_tpl.md')).read()
md=['| item | A\' | A\' result | B | B result |','|'+'-'*12+'|'+'-'*7+'|'+'-'*38+'|'+'-'*7+'|'+'-'*38+'|']
for name,av,a,bv,b in tab: md.append('| %s | %s | %s | %s | %s |'%(name,av,a,bv,b))
md.append('| **Items passed** | **%d/9** | | **%d/9** | |'%(nA,nB))
mr=[]
for r in HM['climb12']:
    mr.append('| %s, bin crr %.2f | %.3f | %.1f N m | %.1f A | %.2f | %.2f |'%(r['concept'].split(' (')[0],r['crr_bin'],r['mu_req'],r['torque_per_wheel_Nm'],r['I_per_motor_A'],r['frac_vendor_rated'],r['frac_derived_rated']))
st={x['concept']:x['torque_needed_Nm'] for x in HM['step40_full_width']}
cl=[v for k,v in sd2.items() if k.startswith('ESE240CL') and v]; clp=sum(1 for v in cl if v[0]=='PASS')
bad=['%s=%s%s'%(k.replace('ESE240','ESE '),v[0],' (grab %s)'%v[1] if v[1]!='success' else '') for k,v in sd2.items() if v and v[0]!='PASS']
s1A,s1B=S['A_G1'],S['B_G1']
def g1s(s,n): return ('%s grab: %d/%d pooled, %d false holds, %d knocked over -> G1 %s.'%(n,s['pooled'],s['n'],s['false_holds'],s['knocked'],'PASS' if s['PASS'] else 'FAIL')) if s['complete'] else '%s grab MC incomplete.'%n
rep={'{{NA}}':str(nA),'{{NB}}':str(nB),'{{TABLE}}':'\n'.join(md),'{{MOTORROWS}}':'\n'.join(mr),'{{STEPA}}':'%.0f'%st["A'"],'{{STEPB}}':'%.0f'%st['B'],
     '{{SD2PASS}}':str(sd2_pass),'{{SD2N}}':str(sd2_n),'{{SD2TIPS}}':str(sd2_tips),'{{SD2LIST}}':('not passing: '+', '.join(bad)) if bad else 'all pass',
     '{{CLSD2}}':'%d/%d'%(clp,len(cl)),'{{G1SENTENCE}}':'Grab Monte Carlo (G1, 3 bins x 30 runs, frozen designs): '+g1s(s1A,"A'")+' '+g1s(s1B,'B')}
for k,v in rep.items(): T=T.replace(k,v)
assert '{{' not in T, [l for l in T.split('\n') if '{{' in l]
out=os.path.join(P,'docs','reviews','CONCEPT_GATE_G6.md'); open(out,'w').write(T)
bad_chars=sorted(set(ch for ch in T if ord(ch)>127)); print('written',out,'non-ascii:',bad_chars)
