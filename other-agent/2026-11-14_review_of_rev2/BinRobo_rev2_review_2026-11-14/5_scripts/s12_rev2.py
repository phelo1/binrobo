#!/usr/bin/env python3
"""Cold-eye S12 re-run for BinRobo revision 2 with the DRAWN sections (sheet labels; CAD solids where the label and CAD differ are noted).
Loads: envelope of (a) the other agent's revision-2 gate results at 119.4 kg (/workspace/work/rev2/files/results_gate/*_r2b.json) and
(b) the B2-F S12 peaks (P/revG/sim/cg/h2/res, incl. pothole / compliant kerb / step categories), categorised exactly as s12_struct.py does.
Every allowable or geometric value not on the drawings is tagged ASSUMED. Writes s12_rev2.json and s12_rev2.md here."""
import json, glob, math, os, runpy
H='/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg/h2'
src=open(os.path.join(H,'s12_struct.py')).read().split("DES = {")[0]
ns={'__file__':os.path.join(H,'s12_struct.py')}; exec(src,ns)
rhs=ns['rhs']; peaks=ns['peaks']; G=9.81
# (b) B2-F peaks
PB=peaks('B2F_')
# (a) rev2 peaks: reuse peaks() on the rev2 result dir
ns['RES']='/workspace/work/rev2/files/results_gate'
exec(src.split("def peaks")[0].split("def J")[0],ns)
import types
def peaks_dir(d,suffix):
    P={}
    for f in glob.glob(os.path.join(d,'B2F_*%s.json'%suffix)):
        b=os.path.basename(f)
        if 'grab_' in b or 'tipcalc' in b: continue
        dd=json.load(open(f))
        if 'peak' in dd:
            pk=dd['peak']; r=dict(wheel=pk.get('drive_tyre_N',[0])[0],comb=pk.get('nib_rim_N',[0])[0],pad=pk.get('pad_N',[0])[0],lift=pk.get('lift_N',[0])[0],torque=pk.get('wheel_torque_Nm',[0])[0])
        elif 'driveL' in dd: r=dict(wheel=max(dd['driveL'],dd['driveR']),castor=dd['caster_sum'])
        else: continue
        c=ns['cat'](b,dd)
        for k,v in r.items():
            if (c,k) not in P or v>P[(c,k)][0]: P[(c,k)]=(v,b)
    return P
PR=peaks_dir('/workspace/work/rev2/files/results_gate','_r2b')
def env(c,k):
    a=PB.get((c,k),(0,'-')); b=PR.get((c,k),(0,'-'))
    return max(a,b,key=lambda t:t[0])
L={}
L['wheel_carry']=env('carry','wheel'); L['wheel_static']=env('static','wheel')
L['wheel_edge']=max(env('pothole','wheel'),env('kerb_compliant','wheel'),key=lambda t:t[0])
L['wheel_step_rigid_info']=env('step_rigid','wheel')
L['comb_carry']=env('carry','comb')
L['comb_all']=max([env(c,'comb') for c in ('carry','pothole','step_rigid','kerb_compliant','kerb_rigid','trench')],key=lambda t:t[0])
L['comb_r2_max']=max([v for (c,k),v in PR.items() if k=='comb'],key=lambda t:t[0])
L['torque_r2_max']=max([v for (c,k),v in PR.items() if k=='torque'],key=lambda t:t[0])
L['castor_static_r2']=max([v for (c,k),v in PR.items() if k=='castor'],key=lambda t:t[0])
L['lift_r2_max']=max([v for (c,k),v in PR.items() if k=='lift'],key=lambda t:t[0])
rows=[]
def row(item,lev,F,M,sig,sf,note=''):
    rows.append(dict(item=item,level=lev,F_N=None if F is None else round(F),M_Nm=None if M is None else round(M,1),stress_MPa=None if sig is None else round(sig,1),SF=round(sf,2),note=note))
FY235=235; FY355=355; FYB88=640; FYB129=1080   # ASSUMED nominal yields (EN 10025 S235/S355, ISO 898-1 8.8 / 12.9)
# 1 side rail 50x50x4 (label; CAD still 50x50x2), M = F x x_mast (S12 model), x_mast 0.49
s4=rhs(50,50,4); s2=rhs(50,50,2); s805=rhs(80,80,5)
for lev,key in (('static','wheel_static'),('carry','wheel_carry'),('edge','wheel_edge')):
    F=L[key][0]; M=F*0.49
    row('side rail 50x50x4 S235 (sheet 13 item 1)',lev,F,M,M*1e3/s4['Z'],FY235/(M*1e3/s4['Z']),L[key][1])
    if lev=='edge': row('  same, 80x80x5 (S12 edge fix, NOT drawn)',lev,F,M,M*1e3/s805['Z'],FY235/(M*1e3/s805['Z']))
# 2 mast upright 80x40x4 strong axis, e = 0.4254 (S12) + 0.025 (upright centre moved from x 495 to 520)
e=0.3454+0.08+0.025; sm=rhs(40,80,4)
for lev,key in (('carry','comb_carry'),('comb_all','comb_all')):
    F=L[key][0]; Mu=F*e/2; sig=Mu*1e3/sm['Z']
    row('mast upright 80x40x4 S235 at the foot (e %.3f m)'%e,lev,F,Mu,sig,FY235/sig,L[key][1])
    # mast-base cross-member 50x50x2 torsion: each upright's foot moment enters the cross-member as torsion, carried to the side rail
    tau=Mu*1e3/s2['Wt']; row('mast-base cross-member 50x50x2 torsion (foot moment of one upright) - NOT in S12',lev,F,Mu,tau,0.577*FY235/tau)
    s5=rhs(80,80,5); tau5=Mu*1e3/s5['Wt']; row('  same with 80x80x5 cross-member',lev,F,Mu,tau5,0.577*FY235/tau5)
    # foot bolts: plate only bears on the cross-member over x 470-515 (45 mm); bolt-row lever 35 mm ASSUMED; 2 bolts per row ASSUMED
    for lever,lab in ((0.035,'35 mm (bolts inside the 45 mm the plate shares with the cross-member) ASSUMED'),(0.08,'80 mm (if the plate were fully supported) ASSUMED')):
        Tb=Mu/lever/2
        row('  foot bolts M10 8.8, lever %s'%lab,lev,Tb,Mu,Tb/58.0,58.0*FYB88/Tb)
        row('  foot bolts M12 8.8, lever %s'%lab,lev,Tb,Mu,Tb/84.3,84.3*FYB88/Tb)
# 3 HGH15 blocks at 200 mm pitch (drawn) and M4 rail screws 12.9 into the 10 mm flat
for lev,key in (('carry','comb_carry'),('comb_all','comb_all')):
    F=L[key][0]; M=F*(0.3454+0.08); Pb=M/0.20/2
    row('HGH15CA block, C0 23.47 kN, pitch 0.200 m (drawn)',lev,Pb,M,None,23470/Pb)
    Tb=Pb/2; row('  HGR15 rail screws M4 12.9 into 10 mm flat (2 per block length ASSUMED)',lev,Tb,None,Tb/8.78,8.78*FYB129/Tb)
    row('  same, M4 8.8 (grade not stated on the drawings)',lev,Tb,None,Tb/8.78,8.78*FYB88/Tb)
    # thread strip in a 10 mm S235 flat: engagement 10 mm, A_s ~ 0.6 pi d L ASSUMED
    As=0.6*math.pi*4*10; row('  M4 thread strip in the 10 mm S235 flat',lev,Tb,None,Tb/As,0.577*FY235*As/Tb)
# 4 comb plate 8 mm x 130 S355, 700 wide (load on the 580 mm receiver), pivot pin
for lev,key in (('carry','comb_carry'),('comb_all','comb_all')):
    F=L[key][0]; Zc=8*130**2/6
    for case,arm in (('symmetric',240**2/2/580.),('one half at the roll stop',120.)):
        M=F*arm/1000; row('comb plate 8 x 130 S355 (%s)'%case,lev,F,M,M*1e3/Zc,FY355/(M*1e3/Zc))
    for d in (16,20):
        sig=F*20/(math.pi*d**3/32); row('comb pivot pin D%d 8.8 (20 mm cantilever, S12 ASSUMED; size not on rev 2 drawings)'%d,lev,F,F*0.02,sig,FYB88/sig)
# 5 rocker: kerb strike at 80 N m (S12) and at the 150 N m peak in the rev 2 result files; bushes in each hanger plate, 70 mm apart, D16 x 8 (plate thickness)
cst=L['castor_static_r2'][0]
for T,lab in ((80.0,'80 N m/wheel (S12)'),(L['torque_r2_max'][0],'%.0f N m/wheel (peak logged in rev 2 gate files)'%L['torque_r2_max'][0])):
    Fh=2*T/0.165; Mp=Fh*0.200
    Fb=Mp/0.070+1.5*cst/2   # couple + half of 3 g vertical on the near bush (ASSUMED superposition)
    p=Fb/(16*8); row('rocker bush D16 x 8 bronze (in 8 mm hanger plate), 70 mm apart, kerb %s'%lab,'kerb',Fb,Mp,p,60.0/p,'60 MPa static bronze allowable ASSUMED')
    Mpin=Mp/2; sig=Mpin*1e3/(math.pi*16**3/32); row('  pivot pin d16 8.8, couple applied at the housing, simply supported on the bushes',lab,Mpin*0+Fb,Mpin,sig,FYB88/sig)
    Mh=Fh/2*0.160; Zh=90*8**2/6; sh=Mh*1e3/Zh; row('  hanger plate 8 x 90 S235 weak axis, lever 160 mm (cross-member underside to pin)',lab,Fh/2,Mh,sh,FY235/sh,'plates drawn 6 mm clear of the cross-member: no joint')
sb=rhs(40,50,3); Fv1=3*cst/2; Mb=Fv1*0.28; row('castor beam 50x40x3 S235 (3 g on one castor, 0.28 m from pin)','static x3',Fv1,Mb,Mb*1e3/sb['Z'],FY235/(Mb*1e3/sb['Z']))
# 6 bumper brackets 2 x 8 mm (drawn), sideways knock and frontal push. Upper arm 60 x 8 (x 980-1115, z 300-360), leg 30 x 8 (z 156-300)
for F,lab in ((500.,'500 N lateral (person / post scrape) ASSUMED'),(2*80/0.165,'970 N lateral (drive torque cap 80 N m, pivot turn against a post)'),(2*L['torque_r2_max'][0]/0.165,'%.0f N lateral (rev 2 logged torque peak)'%(2*L['torque_r2_max'][0]/0.165))):
    f=F/2
    Mu=f*0.155; su=Mu*1e3/(60*8**2/6); T=f*0.15; tu=T*1e3/(0.30*60*8**2); vm=math.sqrt(su**2+3*tu**2)
    row('bumper bracket upper arm 60 x 8 S235, weak-axis bending + torsion, %s'%lab,'knock',f,Mu,vm,FY235/vm)
    Ml=f*0.120; sl=Ml*1e3/(30*8**2/6); row('bumper bracket leg 30 x 8 S235 weak axis, %s'%lab,'knock',f,Ml,sl,FY235/sl)
for F,lab in ((2*80/0.165,'970 N frontal'),(2*L['torque_r2_max'][0]/0.165,'%.0f N frontal'%(2*L['torque_r2_max'][0]/0.165))):
    f=F/2; Ml=f*0.144; sl=Ml*1e3/(8*30**2/6); row('bumper bracket leg 30 x 8 in-plane, %s'%lab,'push',f,Ml,sl,FY235/sl)
# 7 actuator base bracket 8 mm plate + 10 mm foot, pin 36 mm from the plate, 4 kN (actuator rating; stall can exceed it)
F=4000.; M=F*0.036
row('actuator base bracket vertical plate 8 x 100 S235, 4 kN at 36 mm','lift',F,M,M*1e3/(100*8**2/6),FY235/(M*1e3/(100*8**2/6)))
row('actuator base bracket foot 10 x 100 S235, 4 kN at 36 mm','lift',F,M,M*1e3/(100*10**2/6),FY235/(M*1e3/(100*10**2/6)))
Mt=F*0.040; tau=Mt*1e3/s2['Wt']; row('mast-base cross-member 50x50x2 torsion from actuator thrust (40 mm offset)','lift',F,Mt,tau,0.577*FY235/tau)
Mb=F*0.81/4; sbm=Mb*1e3/s2['Z']; row('mast-base cross-member 50x50x2 bending, 4 kN at mid-span 0.81 m (simply supported ASSUMED)','lift',F,Mb,sbm,FY235/sbm)
# 8 lift hard stop: two rail clamps 1200 N each (Zimmer HK1501A datasheet) vs actuator 4 kN
row('lift hard stop = 2 rail clamps (1,200 N each, Zimmer HK1501A) vs actuator 4,000 N','overrun',4000,None,None,2400/4000.)
out=dict(loads={k:[round(v[0],1),v[1]] for k,v in L.items()},rows=rows)
json.dump(out,open('s12_rev2.json','w'),indent=1)
md=['| element | case | force (N) | M (N m) | stress (MPa) | SF | note |','|---|---|---|---|---|---|---|']
for r in rows: md.append('| %s | %s | %s | %s | %s | %.2f | %s |'%(r['item'],r['level'],r['F_N'],'-' if r['M_Nm'] is None else r['M_Nm'],'-' if r['stress_MPa'] is None else r['stress_MPa'],r['SF'],r['note']))
open('s12_rev2.md','w').write('Loads: '+json.dumps(out['loads'])+'\n\n'+'\n'.join(md)+'\n')
print(open('s12_rev2.md').read())
