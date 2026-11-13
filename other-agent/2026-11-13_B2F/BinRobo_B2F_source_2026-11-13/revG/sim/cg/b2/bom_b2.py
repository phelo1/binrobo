#!/usr/bin/env python3
"""B2 costed BOM, re-based on revG/bom_revG8.json (Lean-N lines, concept-B removals/additions as bom_revG8.py), plus the iteration-1
lines (it1/cost_it1.py) and the B2 changes. Two variants: NEW drive (PEWM82M-320W + 3.5:1 chain, G8 Lean-N) and DONOR chair drive
(+ 2:1 chain stage so the inherent speed cap is kept). Contingency = G8/G4 rule: checked 5 %, excerpt 8 %, estimate 12 %,
local/used/donor 15 %, logistics 10 %. Price status column: 'verified' = page fetched (checked-*), 'estimated' = est/excerpt.
Outputs b2/res/bom_b2.json, bom_b2_new.csv, bom_b2_donor.csv"""
import json, os, sys, csv, copy
H=os.path.dirname(os.path.abspath(__file__)); RG=os.path.join(H,'..','..','..'); sys.path.insert(0,RG)
G8=json.load(open(os.path.join(RG,'bom_revG8.json'))); IT1=json.load(open(os.path.join(H,'..','it1','res','cost_it1.json')))
B_REMOVE=['ACT-L8','CG-A1','G8','G11','K1','K3','K4','GR-10','GR-08','GR-08D','GR-G6','IND-OPEN','RF-10/11/12','YS-G7','G10']   # bom_revG8.py concept B   # S14 12-Nov-2026: ACT-L8 (Rev G mast actuator, EUR 164.37) is the same FDI 400 mm unit as B-0 (ACT-B lifter, same URL/price); B2 has no Rev G mast -> duplicate removed
lines=[dict(id=r['id'],area=r['area'],item=r['item'],eur=r['real'],status=r['status'],origin=r['origin'],url=r.get('url',''),src='G8 Lean-N') for r in G8['lean_lines'] if r['id'] not in B_REMOVE]
for a in G8['conceptB']['added']:
    lines.append(dict(id=a['id'],area='Bin handling (concept B)',item=a['item'],eur=a['real'],status=a['status'],origin=a['origin'],url='https://www.anodas.lt/en/fdi-linear-actuator-24v-400mm-6mm-s' if a['id']=='B-0' else '',src='G8 concept B'))
for a in IT1['added']:
    lines.append(dict(id=a['id'],area='Bin handling (B1 it1)',item=a['item'],eur=a['eur'],status=a['status'],origin='DE' if 'Conrad' in a['item'] else 'LOCAL' if a['status']=='est' and a['eur']==0 else 'CN',url=a.get('url',''),src='B1 iteration 1'))
def drop(ids,why):
    global lines
    out=[]
    for r in lines:
        if r['id'] in ids: REMOVED.append(dict(r,why=why))
        else: out.append(r)
    lines=out
REMOVED=[]
L=lambda **k: lines.append(dict(dict(origin='LOCAL',url='',src='B2'),**k))
# ---- B2 changes (shared by both variants)
drop(['B1-PADACT'],'B2: pad drive changed to a knee toggle locked over centre + small actuator')
L(id='B2-PADACT',area='Bin handling (B2)',item='Pad toggle actuator TRU COMPONENTS TC24-50-1000 (TC-13492788): 24 V, 50 mm, 1,000 N, 7 mm/s, IP65, L 155 mm, mounted upright on the pad arm; drives the knee toggle (sim need 683 N worst case, ESE 240 SL 250 mm wheels full)',
  eur=59.99,status='checked-11Nov',origin='DE',url='https://www.conrad.com/en/p/tru-components-linear-actuator-tc24-50-1000p-tc-13492784-stroke-length-50-mm-thrust-1000-n-24-v-dc-1-pc-s-3373197.html')
L(id='B2-TOGGLE',area='Bin handling (B2)',item='Knee toggle: 2 x 60 mm links 6 mm S355 (laser, in FAB-B2), 3 x D10 shoulder pins + bronze bushes, over-centre stop block; B1-PADLS switch reused as the lock switch',eur=12.0,status='est')
L(id='B2-COMB',area='Bin handling (B2)',item='640 mm self-aligning comb (yaw +/-4 deg, roll +/-3 deg): 6 mm S355 comb plate (laser) + pivot block, 2 bushes, 2 centring springs, end stops; replaces the 160 mm tooth',eur=45.0,status='est')
L(id='B2-GAP',area='Sensing (B2)',item='Leg-tip gap sensors: 2 x VL53L1X ToF boards, potted, on the flare tips (lateral offset in the last 0.5 m of the approach)',eur=12.0,status='est',origin='CN')
drop(['FAB-L8','B-5'],'B2: one-tube bolted frame replaces the folded tray package and the B frame net')
L(id='FAB-B2',area='Structure',item='B2 frame, one tube size: 50x50x2 S235 RHS ~7.5 m (2 rails, 2 cross-members, 2 mast uprights, top tie) saw-cut and drilled by Brian, bolted through ~16 laser-cut 4-8 mm S355 plates (drive/motor plates, castor plates, mast gussets, actuator lugs, comb, carriage cheeks, pad arm, toggle links, battery tray); 10/6 mm HDPE bay floor and covers; Zinga cold galvanising. Priced as G8 FAB-D8 (same own-build method and plate count)',
  eur=354.12,status='est',url='revG/bom_revG8_donor.csv FAB-D8')
LUG=os.environ.get('B2_BOM_LUG','0')=='1'   # round 3 option (REJECTED: lug tyres fail G1): bar-tread lug drive tyres
if LUG:
    L(id='B2-LUGW',area='Drive',item='2 x 13x5.00-6 open-centre lug wheel (Wanda P328 4-ply, OD 320 mm, 17 mm lugs, inner tube, steel rim, 6205 bearings, hub 90 mm), Parnells via B&Q GBP 79.50 each; sprocket plate bolted to the rim (in the chain-stage line). Gives G3(b) full-width 40 mm step without ramps (sim, round 3)',
      eur=round(2*79.50*1.15,2),status='checked-11Nov',origin='UK',url='https://www.diy.com/departments/13x5-00-6-open-centre-cleated-rotovator-lug-ind-plant-tyre-on-a-25mm-ball-bear/5056116803764_BQ.prd')
    L(id='B2-LUGF',area='Drive',item='Tyre foam fill / puncture sealant for the lug tyres (2 x 13x5.00-6)',eur=20.0,status='est',origin='IE')
NEWONLY=dict(new=['DRV-M8','DRV-W8','DRV-C7','G14','HTR-L8','D6'],donor=[])
base=copy.deepcopy(lines)
def cont(rows,log):
    c=0.0
    for r in rows:
        st=r['status'].split('+')[-1]
        k=0.15 if (r['origin']=='LOCAL' and r['eur']) or r['id']=='SR-L8' else 0.05 if st.startswith('checked') else 0.08 if st.startswith('excerpt') else 0.12
        r['cont_rate']=k; c+=r['eur']*k
    return c+0.10*sum(log.values())
def variant(name):
    rows=copy.deepcopy(base); log={k:v['eur'] for k,v in G8['logistics_lean'].items()}; log['SHIP-CONRAD']=19.99
    if LUG:
        log['SHIP-PARNELLS']=20.0
        if name=='new': rows.append(dict(id='B2-PUCR',area='Drive',item='Credit: 2 x 330 mm solid PU drive wheels no longer bought (inside DRV-W8, est.)',eur=-50.0,status='est',origin='IE',url='',src='B2'))
    if name=='donor':
        rows=[r for r in rows if r['id'] not in ('DRV-M8','DRV-W8','DRV-C7','G14','HTR-L8','D6')]
        D={r['id']:r for r in G8['donor_lines']}
        for i in ('DNR-D8','BAT-D8'):
            r=D[i]; rows.append(dict(id=i,area=r['area'],item=r['item'],eur=r['real'],status=r['status'],origin=r['origin'],url=r.get('url',''),src='G8 Lean-D'))
        rows.append(dict(id='B2-DCH',area='Drive',item='Donor speed-cap chain stage 2:1 per side (12T on the chair gearbox output, 24T plate sprocket on the chair wheel, dead stub axle + 2 bearings, 08B chain, slotted motor plate): 1.67 -> ~0.83 m/s free, so the inherent gearing speed cap (G8 s.3 layer a) is kept; chair wheels and castors reused',
                         eur=90.0,status='est',origin='LOCAL',url='',src='B2'))
        log.pop('SHIP-PEI',None); log['SHIP-NL']=8.0; log['COLLECT']=40.0
    parts=sum(r['eur'] for r in rows); lg=sum(log.values()); c=cont(rows,log)
    for r in rows: r['price_status']='verified' if r['status'].startswith('checked') else 'estimated'
    ver=sum(r['eur'] for r in rows if r['price_status']=='verified')
    by={}
    for r in rows: by[r['area']]=round(by.get(r['area'],0)+r['eur'],2)
    return dict(rows=rows,logistics=log,totals=dict(parts=round(parts,2),logistics=round(lg,2),contingency=round(c,2),all_in=round(parts+lg+c,2),gap_to_2000=round(parts+lg+c-2000,2),
                verified_parts_eur=round(ver,2),verified_share=round(ver/parts,3),n_lines=len(rows)),by_area=by)
R=dict(lug_tyres=LUG,basis='revG/bom_revG8.json Lean-N lines - concept-B removals + concept-B additions + B1 iteration-1 lines + B2 changes',removed=REMOVED,
       new=variant('new'),donor=variant('donor'),B1_ref=IT1['new_all_in'],
       options=[dict(item='Generic 24 V 3 kN IP65 300 mm lift actuator (AliExpress class) instead of the FDI 4 kN (ACT-B)',delta_eur='about -80 to -110',status='excerpt only; needs bench test T2 (cold force, holding) and an IP check before it replaces ACT-B',
                     url='https://www.aliexpress.com/w/wholesale-3000n-linear-actuator.html'),
                dict(item='TRU TC24-50-500P (500 N, 16 mm/s, 3 s pad move) instead of TC24-50-1000',delta_eur=10.0,status='checked-11Nov EUR 69.99',note='faster, but stalls on the leaning 250 mm-wheel ESE 240 full (needs 683 N): not adopted')],
       lane_prep=dict(item='1:4 rubber kerb ramp / cold-lay fillet per surveyed full-width sharp step > 25 mm',eur_each='20-40',in_bom=False))
json.dump(R,open(os.path.join(H,'res','bom_b2.json'),'w'),indent=1)
for v in ('new','donor'):
    with open(os.path.join(H,'res','bom_b2_%s.csv'%v),'w',newline='') as f:
        w=csv.writer(f); w.writerow(['id','area','item','eur','price_status','status','origin','contingency_rate','source','url'])
        for r in R[v]['rows']: w.writerow([r['id'],r['area'],r['item'],'%.2f'%r['eur'],r['price_status'],r['status'],r['origin'],r['cont_rate'],r['src'],r['url']])
        for k,e in R[v]['logistics'].items(): w.writerow([k,'Logistics','shipping/duty/collection','%.2f'%e,'estimated','est','','0.10','G8 logistics',''])
        t=R[v]['totals']; w.writerow(['TOTAL','','parts','%.2f'%t['parts']]); w.writerow(['TOTAL','','logistics','%.2f'%t['logistics']]); w.writerow(['TOTAL','','contingency','%.2f'%t['contingency']]); w.writerow(['TOTAL','','ALL-IN','%.2f'%t['all_in']]); w.writerow(['GAP','','to EUR 2,000','%.2f'%t['gap_to_2000']])
    print(v,R[v]['totals'])
print('removed',[(r['id'],r['eur']) for r in REMOVED],'B1 ref',R['B1_ref'])
