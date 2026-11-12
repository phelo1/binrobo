#!/usr/bin/env python3
"""G6 task 5: fit candidate tilt actuators to the mast by moving the rear-frame clevis pin (RF-13, ACT_BASE) and, if needed, the
mast rod-end bracket (MA-56, ACT_S/ACT_E). Model frame (mm): mast hinge pin PX,PZ = 260,300; phi = mast tilt (deg, + = towards tug).
Operating window: phi -2 deg (deepest grab swing seen in G5, 1 mm margin) to 73.4 deg (tow pose 70.7 + catch overtravel).
Force: G5 Monte Carlo peak actuator force 2,141 N at the current geometry (lever 222-337 mm); the demand scales with the moment, so
F_new(phi) = F_old_peak * max over phi of lever_old/lever_new.  usage: python3 actuator_fit_g6.py -> actuator_fit_g6.json"""
import math, json, os
HERE=os.path.dirname(os.path.abspath(__file__))
PX,PZ=260.0,300.0; B0=(600.0,340.0); S0,E0=900.0,-250.0
PHI_LO,PHI_HI=-2.0,73.4; F_PEAK=2141.0; MARGIN=4.0
def mp(phi,S=S0,E=E0):
    c,s=math.cos(math.radians(phi)),math.sin(math.radians(phi)); return (PX+E*c+S*s, PZ-E*s+S*c)
def L(phi,B=B0,S=S0,E=E0): A=mp(phi,S,E); return math.hypot(A[0]-B[0],A[1]-B[1])
def lev(phi,B=B0,S=S0,E=E0):
    A=mp(phi,S,E); d=(A[0]-B[0],A[1]-B[1]); n=math.hypot(*d); u=(d[0]/n,d[1]/n); r=(A[0]-PX,A[1]-PZ); return abs(r[0]*u[1]-r[1]*u[0])
PH=[PHI_LO+k*(PHI_HI-PHI_LO)/60 for k in range(61)]
# candidates: name, built-in dimension (retracted pin-pin) as f(S), max stroke, rated push N, speed mm/s (no load, full load) + rated load for interpolation, IP, temp, source
CANDS=[
 dict(id='LA34-L-12std',name='LINAK LA34, long "L" install (patient-lift version), 12 mm pitch, standard 24 V motor',bid=lambda S:S+267,smax=600,F=10000,v0=8.2,v1=4.8,Fv=10000,amps=7,ip='IPX6',temp='+5..+40 C',src='LA34 data sheet'),
 dict(id='LA34-L-16std',name='LINAK LA34 L, 16 mm pitch, standard motor',bid=lambda S:S+267,smax=600,F=7000,v0=10.8,v1=7.9,Fv=7000,amps=7,ip='IPX6',temp='+5..+40 C',src='LA34 data sheet'),
 dict(id='LA34-L-20fast',name='LINAK LA34 L, 20 mm pitch, fast motor',bid=lambda S:S+267,smax=600,F=5000,v0=18.0,v1=13.2,Fv=5000,amps=10,ip='IPX6',temp='+5..+40 C',src='LA34 data sheet'),
 dict(id='LA34-S-16std',name='LINAK LA34 standard install (S+210), 16 mm pitch, std motor (max 400 mm stroke)',bid=lambda S:S+210,smax=400,F=7000,v0=10.8,v1=7.9,Fv=7000,amps=7,ip='IPX6',temp='+5..+40 C',src='LA34 data sheet'),
 dict(id='LA31-12',name='LINAK LA31 (CARELINE), stroke > 300 mm: BID S+212, max 350 mm stroke, 4,000 N above 250 mm stroke',bid=lambda S:S+212,smax=350,F=4000,v0=None,v1=None,Fv=None,amps=None,ip='IPX6',temp='+5..+40 C',src='LA31 data sheet'),
 dict(id='LA36-24V',name='LINAK LA36 TECHLINE 24 V, IP66/IP69K, BID 250+S (S>300)',bid=lambda S:S+250,smax=1200,F=6800,v0=None,v1=None,Fv=None,amps=None,ip='IP66 dyn / IP69K static',temp='-30 (50 % load)..+85 C, full +5..+40 C',src='LA36 data sheet'),
]
def fit(c, move_mast=False):
    best=None
    Sgrid=[S0] if not move_mast else [S0-k*10 for k in range(0,26)]
    for Sm in Sgrid:
        for bx in range(520,700,4):
            for bz in range(300,420,4):
                B=(float(bx),float(bz)); Ls=[L(p,B,Sm,E0) for p in PH]; lo,hi=min(Ls),max(Ls)
                lev_min=min(lev(p,B,Sm,E0) for p in PH)
                if lev_min<60: continue
                need=hi-lo
                for S in range(int(math.ceil(need+2*MARGIN)),c['smax']+1):
                    r=c['bid'](S); e=r+S
                    if r+MARGIN<=lo and hi<=e-MARGIN:
                        ratio=max(lev(p)/lev(p,B,Sm,E0) for p in PH); Freq=F_PEAK*ratio
                        sc=(Freq<=c['F']/1.5, -abs(bx-B0[0])-abs(bz-B0[1])-abs(Sm-S0), -S)
                        if best is None or sc>best[0]:
                            best=(sc,dict(base=B,mast_S=Sm,stroke=S,retracted=r,extended=e,L_lo=round(lo,1),L_hi=round(hi,1),
                                         margin_retracted=round(lo-r,1),margin_extended=round(e-hi,1),lever_min=round(lev_min,1),
                                         F_required=round(Freq),F_rated=c['F'],force_SF=round(c['F']/Freq,2),
                                         dL_dphi_max=round(max(abs(L(p+0.5,B,Sm,E0)-L(p-0.5,B,Sm,E0)) for p in PH),2)))
                        break
    return best[1] if best else None
if __name__=='__main__':
    out=dict(window_deg=[PHI_LO,PHI_HI],current=dict(base=B0,L_lo=round(min(L(p) for p in PH),1),L_hi=round(max(L(p) for p in PH),1),
             lever_min=round(min(lev(p) for p in PH),1),dL_dphi_max=round(max(abs(L(p+0.5)-L(p-0.5)) for p in PH),2)),cands=[])
    print('current geometry',out['current'])
    for c in CANDS:
        r=fit(c); mm=False
        if r is None: r=fit(c,move_mast=True); mm=True
        d={k:v for k,v in c.items() if k!='bid'}; d.update(fit=r,mast_bracket_moved=mm)
        if r and c['v0']:
            v=c['v0']-(c['v0']-c['v1'])*min(1.0,r['F_required']/c['Fv']); d['speed_at_peak_mm_s']=round(v,1)
            d['phi_rate_deg_s_worst']=round(v/r['dL_dphi_max'],2); d['tip_time_s_0_to_70']=round(sum(abs(L(p+1,r['base'],r['mast_S'])-L(p,r['base'],r['mast_S'])) for p in range(0,70))/v,1)
        out['cands'].append(d); print(c['id'],'mast moved' if mm else '',r, d.get('speed_at_peak_mm_s'), d.get('tip_time_s_0_to_70'))
    json.dump(out,open(os.path.join(HERE,'actuator_fit_g6.json'),'w'),indent=1)
