#!/usr/bin/env python3
"""Writes h2/q_h2.txt: frozen gate suite (same sub-commands, seeds and order as b2/q_b2.txt) for Rev H2 (S3), B2 as designed on the
corrected hull (S11), B2-F (S11b), perturbations (S3 / S11b) and B2 with its pad re-set to a real rear wall (S11r, reported only)."""
import os
H=os.path.dirname(os.path.abspath(__file__))
D={'H2':"CMP_SIM=simH2 CMP_PREFIX=H2_",'B2n':"CMP_SIM=simB2h B2_DOCK=handle CMP_PREFIX=B2n_",'B2F':"CMP_SIM=simB2h B2_DOCK=front CMP_PREFIX=B2F_",
   'B2r':"CMP_SIM=simB2h B2_DOCK=handle CGB_GEO='{\"pad_in\":0.0165}' CMP_PREFIX=B2r_"}
def L(d,args,tag='',extra=''): return "env CGB_F9=1 %s %sIT1_TAG=%s python3 h2/runH2.py %s"%(D[d],extra,tag,args)
REL=[(b,c,f) for b in ('WEB140','ESE240CL','ESE240SL250') for c in ('flat','up12','dn12') for f in ('full','empty')]
def full(d):
    o=['# ---- %s frozen suite'%d]
    o+=[L(d,'grab %s 30 %d'%(b,s)) for b,s in (('WEB140',201),('ESE240SL',202),('ESE240CL',203))]
    o+=[L(d,'climb %.2f %.2f'%(m,c)) for m in (0.30,0.25,0.22) for c in (0.06,0.09)]
    o+=[L(d,'step '+s) for s in ('one','both','both_ramp')]+[L(d,'estop fwd'),L(d,'estop rev'),L(d,'towstab')]
    o+=[L(d,'rel %s %s %s'%x) for x in REL]
    o+=[L(d,a,extra='SIM_DT=0.00025 ') for a in ('climb 0.25 0.09','step one','estop fwd')]
    o+=[L(d,'static %s %d'%(p,k)) for p in ('up','dn','crL','crR') for k in (110,60)]
    o+=[L(d,'grab ESE240SL250 30 204'),L(d,'grab ESE140CL 30 205')]
    return o
def s11r(d):
    return ['# ---- %s: G1 sample (10 per bin) only, reported not gating'%d]+[L(d,'grab %s 10 %d'%(b,s)) for b,s in (('WEB140',201),('ESE240SL',202),('ESE240CL',203))]
def s11(d):
    o=['# ---- %s: G1, G5, G6 only'%d]
    o+=[L(d,'grab %s 30 %d'%(b,s)) for b,s in (('WEB140',201),('ESE240SL',202),('ESE240CL',203))]
    o+=[L(d,'towstab')]+[L(d,'rel %s %s %s'%x) for x in REL]
    return o
PERT=[('PERT_MASS=1.1 ','_pm110'),('PERT_MASS=0.9 ','_pm090'),('PERT_MU=0.85 ','_pmu085'),('PERT_CRR=0.09 ','_pcrr09')]
RED=['grab WEB140 10 201','grab ESE240SL 10 202','grab ESE240CL 10 203','climb 0.22 0.09','climb 0.25 0.06','step one','estop fwd','estop rev','towstab',
     'rel WEB140 up12 full','rel WEB140 dn12 empty','rel ESE240CL flat empty','rel ESE240CL up12 full','rel ESE240SL250 dn12 full','rel ESE240SL250 up12 empty',
     'static up 110','static dn 60','static crL 110']
def pert(d): return ['# ---- %s perturbations (reduced suite, as b2/q_b2.txt round 2)'%d]+[L(d,a,tag,ex) for ex,tag in PERT for a in RED]
T15="0.065,0.5;0.5,0.95,0.02"; T20="0.045,0.5;0.5,0.95,0.02"   # S6 tyre: static deflection 8 mm / ~5 mm under the full-bin wheel load (h2/res/*tyrecal*)
def X(d,args,tag='',extra='',est=None): return "env CGB_F9=1 %s %sIT1_TAG=%s python3 h2/runX.py %s%s"%(D[d],extra,tag,args,(' #est=%d'%est if est else ''))
def tip(d): return [X(d,'tipcalc',est=25)]
def s5(d): return ['# ---- %s S5 retention'%d]+[X(d,'ret %s %s %.1f'%(b,f,v),extra=('H2_KEEPER=1 ' if k else '')+('H2_S5V=2 ' if f=='step' else ''),est=30) for k in (0,1) for b in ('ESE240SL','WEB140') for f in ('step','trench','pothole') for v in (0.5,0.8)]
def s6(d):
    alt='{"cr":0.10}' if d=='H2' else '{"cr":0.13}'; alt80='{"cr":0.10,"tcap":80}' if d=='H2' else '{"cr":0.13,"tcap":80}'
    V=[('_r','0.5 nose',''),('_r','0.8 nose',''),('_r80',"0.5 nose","CGB_GEO='{\"tcap\":80}' "),('_r','0.5 tail',''),('_rcas','0.5 nose',"CGB_GEO='%s' "%alt),('_r','0.5 nose ramp',''),
       ('_t15','0.5 nose',"H2_TYRE_POST='%s' "%T15),('_t20','0.5 nose',"H2_TYRE_POST='%s' "%T20),('_t15','0.8 nose',"H2_TYRE_POST='%s' "%T15),
       ('_t15_80','0.5 nose',"H2_TYRE_POST='%s' CGB_GEO='{\"tcap\":80}' "%T15),('_t15','0.5 tail',"H2_TYRE_POST='%s' "%T15),('_t15cas','0.5 nose',"H2_TYRE_POST='%s' CGB_GEO='%s' "%(T15,alt)),
       ('_r80','0.8 nose',"CGB_GEO='{\"tcap\":80}' "),('_r80','0.5 tail',"CGB_GEO='{\"tcap\":80}' "),('_t15_80cas','0.5 nose',"H2_TYRE_POST='%s' CGB_GEO='%s' "%(T15,alt80))]
    return ['# ---- %s S6 kerb'%d,X(d,'tyrecal','_t20',"H2_TYRE_POST='%s' "%T20,est=20)]+[X(d,'kerb '+a,t,e,est=40) for t,a,e in V]
def s7(d):
    hc="H2_BINCG_DZ=0.06 "
    return ['# ---- %s S7 nose-light'%d]+[X(d,'climbn %.2f 0.06'%m,'_cg60','H2_S7F=1 '+hc,est=30) for m in (0.22,0.25,0.30)]+[X(d,'climbn 0.22 0.06','_cg0','H2_S7F=1 ',est=30)]+\
           [L(d,'static %s %d'%(p_,k),'_cg60',hc) for p_ in ('up','dn','crL','crR') for k in (110,60)]+[X(d,'tipcalc','_cg60',hc,est=25)]
GAPS=[-10,0,10,20,30,40,50,60]; S4B=[('WEB140',201),('ESE240SL',202),('ESE240CL',203),('ESE240SL250',204),('ESE140CL',205)]
def s4():
    o=['# ---- H2 S4 pad tolerance map (H2_PADGAP = nominal wall-to-pad gap at pad height, m)']
    for gp in GAPS:
        e="H2_PADGAP=%.3f "%(gp/1000.0); t='_g%+03d'%gp
        for b,sd in S4B: o+=[L('H2','grab %s 10 %d'%(b,sd),t,e),L('H2','rel %s flat full'%b,t,e),L('H2','rel %s flat empty'%b,t,e)]
    return o
LIPV=[('_lsr004',"H2_LIP_SOLREF=0.004,1 "),('_lsr016',"H2_LIP_SOLREF=0.016,1 "),('_lsi80',"H2_LIP_SOLIMP=0.8,0.95,0.002 "),('_lsi95',"H2_LIP_SOLIMP=0.95,0.999,0.002 "),
      ('_lmu25',"H2_LIP_MU=0.25 "),('_lmu45',"H2_LIP_MU=0.45 ")]
def s10(d):
    o=['# ---- %s S10 contact sensitivity'%d]
    for t,e in LIPV:
        o+=[L(d,'grab ESE240SL 10 202',t,e),X(d,'ret ESE240SL step 0.8',t,e,est=30),X(d,'ret ESE240SL pothole 0.8',t,e,est=30)]
    return o
Q=full('H2')+tip('H2')+tip('B2F')+s11('B2n')+full('B2F')+s5('H2')+s5('B2F')+s6('H2')+s6('B2F')+s7('H2')+s7('B2F')+s4()+pert('H2')+pert('B2F')+s10('H2')+s10('B2F')+s11r('B2r')
open(os.path.join(H,'q_h2.txt'),'w').write('\n'.join(Q)+'\n'); print(len([l for l in Q if not l.startswith('#')]),'lines')

# ---------------- 2026-11-12 RESUME TRIMS (declared in PROGRESS_H2.md before running) ----------------
def s5t(d):
    o=s5(d)
    if d=='B2F': o=[l for l in o if 'H2_KEEPER=1' not in l or ' 0.8 #' in l]          # B2-F keeper only at 0.8 m/s
    return o
REDT=['grab ESE240SL 5 202','climb 0.22 0.09','step one','estop fwd','rel ESE240CL up12 full','rel ESE240SL250 dn12 full']
def s5diag(d): return ['# ---- %s S5 trench/pothole re-run with distance + bin-wheel crossing record (H2_S5DIAG=1, no other effect)'%d]+[X(d,'ret %s %s %.1f'%(b,f,v),extra='H2_S5DIAG=1 ',est=30) for b in ('ESE240SL','WEB140') for f in ('trench','pothole') for v in (0.5,0.8)]
def pertt(d): return ['# ---- %s perturbations (TRIMMED: 6 lines per perturbation)'%d]+[L(d,a,tag,ex) for ex,tag in PERT for a in REDT]
def s11rt(d): return ['# ---- %s: G1 sample (TRIMMED 5 per bin) only, reported not gating'%d]+[L(d,'grab %s 5 %d'%(b,s)) for b,s in (('WEB140',201),('ESE240SL',202),('ESE240CL',203))]
def s6t(d):
    o=s6(d)
    if d=='B2F':
        keep=("'_r'", "0.8 nose","ramp","_r80","_rcas","_t15 ","_t15_80cas","tyrecal")
        o=[o[0],o[1]]+[l for l in o[2:] if (" IT1_TAG=_r python3 h2/runX.py kerb 0.5 nose #" in l or "IT1_TAG=_r python3 h2/runX.py kerb 0.5 nose ramp" in l
             or "IT1_TAG=_r80 python3 h2/runX.py kerb 0.5 nose #" in l or "IT1_TAG=_rcas " in l or "IT1_TAG=_t15 python3 h2/runX.py kerb 0.5 nose #" in l or "IT1_TAG=_t15_80cas " in l)]
    return o
def s7t(d): return [l for l in s7(d) if not l.split('#')[0].rstrip().endswith(' 60')]       # high-CG statics at 110 kg only
GAPST=[-10,0,20,40,60]; S4BT=[('WEB140',201),('ESE240SL',202),('ESE240CL',203)]
def s4t():
    o=['# ---- H2 S4 pad tolerance map TRIMMED (5 gaps x 3 bins, G1 5 seeds + G6 flat full)']
    for gp in GAPST:
        e="H2_PADGAP=%.3f "%(gp/1000.0); t='_g%+03d'%gp
        for b,sd in S4BT: o+=[L('H2','grab %s 5 %d'%(b,sd),t,e),L('H2','rel %s flat full'%b,t,e)]
    return o
def s10t(d):
    V=LIPV if d=='H2' else [x for x in LIPV if x[0] in ('_lsr004','_lmu25')]
    V=[x for x in V if x[0] in ('_lsr004','_lsr016','_lmu25','_lmu45')]
    o=['# ---- %s S10 contact sensitivity TRIMMED'%d]
    for t,e in V: o+=[L(d,'grab ESE240SL 5 202',t,e),X(d,'ret ESE240SL step 0.8',t,'H2_S5V=2 '+e,est=30),X(d,'ret ESE240SL pothole 0.8',t,e,est=30)]
    return o
Q=full('H2')+tip('H2')+tip('B2F')+s11('B2n')+full('B2F')+s5t('H2')+s5t('B2F')+s5diag('H2')+s5diag('B2F')+pertt('H2')+pertt('B2F')+s11rt('B2r')+s6t('H2')+s6t('B2F')+s7t('H2')+s7t('B2F')+s4t()+s10t('H2')+s10t('B2F')
open(os.path.join(H,'q_h2.txt'),'w').write('\n'.join(Q)+'\n'); print(len([l for l in Q if not l.startswith('#')]),'lines (trimmed)')
