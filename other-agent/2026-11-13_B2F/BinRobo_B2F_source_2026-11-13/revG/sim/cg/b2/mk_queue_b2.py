"""B2 queue: frozen suite (as it1/q9 / cmp mk_suite), extras, donor variant, gap-sensor stress, step sensitivities, perturbations."""
import sys
R='python3 b2/runB2.py'; E='env CGB_F9=1 '+('B2_LUG=1 ' if 'lug' in sys.argv[2:] else ''); TP='_lug' if 'lug' in sys.argv[2:] else ''   # round 3: bar-tread lug tyres
def L(cmd,tag='',extra=''): print(f'{E}{extra}IT1_TAG={TP}{tag} {R} {cmd}')
sec=sys.argv[1]
if sec=='suite':
    for b in ('WEB140 30 201','ESE240SL 30 202','ESE240CL 30 203'): L('grab '+b)
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
    for b in ('ESE240SL250 30 204','ESE140CL 30 205'): L('grab '+b)
if sec=='extras':
    # 40 mm full-width step sensitivities (not gate): 250 mm castors, bar-tread lugs, CG forward (20 kg ballast at the nose)
    L('step both','_cr250',"CGB_GEO='{\"cr\":0.125}' "); L('step both','_lug','B2_LUG=1 '); L('step both','_cgfwd','CGB_MASSF=b2/mass_cgB2_cgfwd.json ')
    L('step both','_lugcgfwd','B2_LUG=1 CGB_MASSF=b2/mass_cgB2_cgfwd.json ')
    # donor-drive variant (318 mm wheels, chair drive + 2:1 chain, AGM forward): carry tests
    D="CGB_MASSF=b2/mass_cgB2_donor.json CGB_GEO='{\"rw\":0.159}' "
    for m in ('0.30','0.25','0.22'):
        for c in ('0.06','0.09'): L(f'climb {m} {c}','_donor',D)
    for c in ('step one','step both','step both_ramp','estop fwd','estop rev','towstab','static up 110','static dn 60','static crL 110','static crR 110'): L(c,'_donor',D)
    L('grab ESE240SL 10 202','_donor',D)
    # leg-tip gap sensors: camera stress 16 mm, without / with the sensors (3 mm once the bin is in the flares)
    for b in ('ESE240SL 20 212','ESE240CL 20 213'):
        L('grab '+b,'_cam16','B2_CAMSIG=0.016 '); L('grab '+b,'_cam16gap','B2_CAMSIG=0.016 B2_GAPSENS=1 ')
if sec=='pert':
    for pv,pt in (('PERT_MASS=1.1 ','_pm110'),('PERT_MASS=0.9 ','_pm090'),('PERT_MU=0.85 ','_pmu085'),('PERT_CRR=0.09 ','_pcrr09')):
        for b in ('WEB140 10 201','ESE240SL 10 202','ESE240CL 10 203'): L('grab '+b,pt,pv)
        for c in ('climb 0.22 0.09','climb 0.25 0.06','step one','estop fwd','estop rev','towstab'): L(c,pt,pv)
        for c in ('rel WEB140 up12 full','rel WEB140 dn12 empty','rel ESE240CL flat empty','rel ESE240CL up12 full','rel ESE240SL250 dn12 full','rel ESE240SL250 up12 empty'): L(c,pt,pv)
        for c in ('static up 110','static dn 60','static crL 110'): L(c,pt,pv)
