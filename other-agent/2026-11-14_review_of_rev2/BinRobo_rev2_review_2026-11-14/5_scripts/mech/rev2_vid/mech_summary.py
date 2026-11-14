#!/usr/bin/env python3
"""[tester] collect perturbations (24, 119.39 kg), step sensitivity (rocker/pin) and the audit-mass reduced gate (125.64 kg count)
from revG/sim/cg/h2/res_r2 -> /workspace/work/out/rev2/mech/{perturbations_r2b,sensitivity_r2b,gate_audit_mass_r2baud}.json"""
import json, os
R='/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg/h2/res_r2'; O='/workspace/work/out/rev2/mech'
T='/workspace/work/rev2/files/results_gate'
def L(n,d=R):
    p=os.path.join(d,'B2F_'+n+'.json'); return json.load(open(p)) if os.path.exists(p) else None
def brief(d):
    if d is None: return 'MISSING'
    t=d.get('test') or ('grab' if 'runs' in d else '?')
    if 'runs' in d: return dict(n=d['n'],captured=d['captured'],false_holds=d['false_holds'],knocked=d['knocked'],fh50=sum(bool(r.get('false_hold50')) for r in d['runs']),ok=d['captured']>=d['n']-0 and d['false_holds']==0)
    keep=('ok','verdict','reached','reached_5m','dist_m','time_s','hold_creep_m','stop_dist_m','slide_after_stop_m','roll','pitch','clear_min','seated_all','bin_ground','swept_diameter_m','bin_stable','captured','driveL','driveR','caster_sum','antitip','tipmin')
    o={k:d[k] for k in keep if k in d}
    if 'peak' in d and d['peak'].get('lift_N'): o['lift_pk_N']=d['peak']['lift_N'][0]
    return o
tests=[('grab ESE240SL x5','grab_ESE240SL'),('climb mu0.22 crr0.09','climb_m22_c09'),('step one side','step40_one'),('estop fwd','estop12_fwd'),('release CL up12 full','rel_ESE240CL_up12_full'),('release SL250 dn12 full','rel_ESE240SL250_dn12_full')]
pert={}
for tag,lab in (('pm110','mass x1.1'),('pm090','mass x0.9'),('pmu085','friction x0.85'),('pcrr09','bin crr 0.09')):
    pert[lab]={t:dict(ours_r2b=brief(L('%s_%s_r2b'%(n,tag))),theirs_r2_115kg=brief(L('%s_%s_r2'%(n,tag),T))) for t,n in tests}
npass=sum(1 for v in pert.values() for t in v.values() if isinstance(t['ours_r2b'],dict) and t['ours_r2b'].get('ok'))
json.dump(dict(mass_kg_sim=119.39,n=24,passed=npass,cases=pert),open(O+'/perturbations_r2b.json','w'),indent=1)
print('PERT passed',npass,'of 24')
for lab,v in pert.items():
    for t,x in v.items(): print(' ',lab,'|',t,'|',json.dumps(x['ours_r2b'])[:200])
sens={}
for tag,lab in (('r2b','rocker stops +/-2 deg, pin 200 mm (as designed)'),('r2b_rd4','rocker stops +/-4 deg'),('r2b_rlk','rocker locked (+/-0.05 deg)'),('r2b_z150','pivot pin 150 mm'),('r2b_z250','pivot pin 250 mm')):
    g=L('grab_ESE240CL_'+tag) if tag!='r2b' else None
    sens[lab]=dict(step_one=brief(L('step40_one_'+tag)),step_both=brief(L('step40_both_'+tag)),
                   grab_CL_i0_i14=(None if g is None else [(r['i'],r['result']) for r in g['runs']]))
json.dump(sens,open(O+'/sensitivity_step_r2b.json','w'),indent=1)
for k,v in sens.items(): print('SENS',k,json.dumps(v)[:330])
aud={}
for lab,n in (('G1 grab ESE240CL x30','grab_ESE240CL'),('G2 climb mu0.22 crr0.06','climb_m22_c06'),('G2 climb mu0.22 crr0.09','climb_m22_c09'),('G3 step one','step40_one'),('G3 step both','step40_both'),
              ('G4 estop fwd','estop12_fwd'),('G4 estop rev','estop12_rev'),('G5 towstab','towstab'),('G6 rel CL up12 full','rel_ESE240CL_up12_full'),('G6 rel CL dn12 full','rel_ESE240CL_dn12_full'),
              ('G8 static crL 110','static_crL_110'),('G8 static crR 110','static_crR_110'),('G8 static dn 110','static_dn_110'),('G8 tipcalc','tipcalc')):
    a=L(n+'_r2baud'); b=L(n+'_r2b')
    if n=='tipcalc': aud[lab]=dict(audit=a and dict(tipmin=a['tipmin'],castor_liftoff_110=a['cases'][0]['castor_liftoff_about_drive_axle_deg'],M=a['cases'][0]['M']),base=b and dict(tipmin=b['tipmin'],castor_liftoff_110=b['cases'][0]['castor_liftoff_about_drive_axle_deg'],M=b['cases'][0]['M']))
    else: aud[lab]=dict(audit=brief(a),base_119kg=brief(b))
m=json.load(open('/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg/h2/mass_cgB2_r2b_aud.json'))
json.dump(dict(mass_file='revG/sim/cg/h2/mass_cgB2_r2b_aud.json',gate_count_kg=m['total'],G9='FAIL (>120 kg)' if m['total']>120 else 'PASS',tests=aud),open(O+'/gate_audit_mass_r2baud.json','w'),indent=1)
for k,v in aud.items(): print('AUD',k,json.dumps(v)[:300])
