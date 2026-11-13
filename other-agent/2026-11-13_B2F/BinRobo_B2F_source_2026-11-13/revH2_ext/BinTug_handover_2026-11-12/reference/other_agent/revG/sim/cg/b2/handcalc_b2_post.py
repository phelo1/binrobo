#!/usr/bin/env python3
"""B2 hand calcs needing sim peaks: comb/receiver stress (gate-model ledge 30 x 8 mm HDPE, load at the 26 mm rim; same formula as
cmp/handcalc_cmp.py), lift actuator and pad toggle margins, frame tube stress (50x50x2 RHS). -> b2/res/handcalc_b2_post.json"""
import json, os, glob, math
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(H,'res'); g=9.81
def lip(F,comb_w,recv_w,a=0.026,t=0.008):
    w=min(comb_w,recv_w); return dict(F_N=round(F),comb_mm=round(comb_w*1000),receiver_mm=round(recv_w*1000),coverage_pct=round(100*w/recv_w),
        line_load_N_per_mm=round(F/(w*1000),2),bearing_MPa=round(F/(w*1000*t*1000),2),ledge_bending_MPa=round(6*F*a/(w*t*t)/1e6,1))
pk={}
for f in glob.glob(os.path.join(R,'B2_*.json')):
    n=os.path.basename(f)[3:-5]
    if any(x in n for x in ('grab','_dt025','_pm','_pmu','_pcrr','_donor','_lug','_cr250','_cgfwd','gate')): continue
    d=json.load(open(f))
    for k,v in d.get('peak',{}).items():
        if v[0]>pk.get(k,(0,''))[0]: pk[k]=(v[0],n)
st=[json.load(open(f)) for f in glob.glob(os.path.join(R,'B2_static_*_110.json'))]
lift_static=max([d['lift_N'] for d in st] or [0]); pad_static=max([d['pad_N'] for d in st] or [0])
O=dict(peaks_nominal_carry=pk,static_110kg_lift_N=lift_static,static_110kg_pad_N=pad_static)
F_pk=pk.get('nib_rim_N',(2500,''))[0]
O['lip']={'B2 640 mm comb, ESE 240 SL full, static carry (lift force on 12 % static poses)':lip(lift_static,0.640,0.580),
          'B2 640 mm comb, peak nib/rim force over the nominal carry runs':lip(F_pk,0.640,0.580),
          'B1 160 mm comb, peak 3838 N (COMPARE s.9) - reference':lip(3838,0.160,0.580)}
LA=pk.get('lift_N',(0,''))[0]
O['lift_actuator']=dict(peak_N=LA,static_N=lift_static,unit='QC FDI 24 V 4,000 N IP65 (ACT-B)',margin_peak=round(4000/max(LA,1),2),margin_static=round(4000/max(lift_static,1),2),
                        note='sim actuator force cap 3,000 N (as B1); generic 3 kN option would give %.2f x on the peak'%(3000/max(LA,1)))
O['pad_toggle']=dict(actuator='TRU TC24-50-1000, 1,000 N',need_worst_N=680,case='ESE 240 SL 250 mm wheels full, extension at load-on (smoke6)',margin=round(1000/680,2),
                     locked_stop_peak_N=pk.get('pad_N',(0,''))[0],note='in the carry the pad load goes into the over-centre stop, not the actuator')
# frame: side rail 50x50x2 simply supported drive axle (x 0) to castors (x 0.95), mast-base load at x 0.49 shared by 2 rails; dynamic x2.5
I=(50**4-46**4)/12; Z=I/25
P=(lift_static+60*g)/2; a,b=0.49,0.46; M=P*a*b/0.95
O['frame']=dict(section='50x50x2 RHS S235, I %.0f mm4, Z %.0f mm3'%(I,Z),rail_load_N=round(P),M_static_Nm=round(M),sigma_static_MPa=round(M*1e3/Z,1),sigma_dyn_x2p5_MPa=round(2.5*M*1e3/Z,1),allow_MPa=round(235/1.5),
                mast_upright_M_Nm=round(lift_static*0.205/2),mast_sigma_dyn_MPa=round(2.5*lift_static*0.205/2*1e3/Z,1))
json.dump(O,open(os.path.join(R,'handcalc_b2_post.json'),'w'),indent=1); print(json.dumps(O,indent=1)[:2500])
