"""print the frozen-suite queue lines for a design (env prefix) + tag; same list as it1/q9 (full suite) + perturbation subset"""
import sys
env,tag=sys.argv[1],sys.argv[2]; pert=len(sys.argv)>3 and sys.argv[3]=='pert'
R='python3 cmp/runCMP.py'
def L(cmd,t=tag,extra=''): print(f'env {env} {extra}IT1_TAG={t} {R} {cmd}')
if not pert:
    for b in ('WEB140 30 201','ESE240SL 30 202','ESE240CL 30 203','ESE240SL250 30 204','ESE140CL 30 205'): L('grab '+b)
    for m in ('0.30','0.25','0.22'):
        for c in ('0.06','0.09'): L(f'climb {m} {c}')
    for s in ('one','both','both_ramp'): L('step '+s)
    for o in ('fwd','rev'): L('estop '+o)
    L('towstab')
    for b in ('WEB140','ESE240CL','ESE240SL250'):
        for c in ('flat','up12','dn12'):
            for f in ('full','empty'): L(f'rel {b} {c} {f}')
    for c in ('climb 0.25 0.09','step one','estop fwd'): L(c,extra='SIM_DT=0.00025 ')
    for p in ('up','dn','crL','crR'):
        for k in ('110','60'): L(f'static {p} {k}')
else:
    for pv,pt in (('PERT_MASS=1.1 ','pm110'),('PERT_MASS=0.9 ','pm090'),('PERT_MU=0.85 ','pmu085'),('PERT_CRR=0.09 ','pcrr09')):
        t=tag+pt
        for b in ('WEB140 10 201','ESE240SL 10 202','ESE240CL 10 203'): L('grab '+b,t,pv)
        for c in ('climb 0.22 0.09','climb 0.25 0.06','step one','estop fwd','estop rev','towstab'): L(c,t,pv)
        for c in ('rel WEB140 up12 full','rel WEB140 dn12 empty','rel ESE240CL flat empty','rel ESE240CL up12 full','rel ESE240SL250 dn12 full','rel ESE240SL250 up12 empty'): L(c,t,pv)
        for c in ('static up 110','static dn 60','static crL 110'): L(c,t,pv)
