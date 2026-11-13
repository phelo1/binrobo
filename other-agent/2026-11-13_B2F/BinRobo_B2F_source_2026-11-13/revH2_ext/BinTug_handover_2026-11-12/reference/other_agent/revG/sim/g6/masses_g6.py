#!/usr/bin/env python3
"""G6 mass files for the ballast sweep. Base = revG/cad/mass_g3_sim_L95.json rows (G3 lean + G5) with:
  - sand fill row removed (G6: never wet sand; dry steel punchings or dry gravel only)
  - tilt actuator: XTL450 envelope (1.95 kg body + 0.30 kg rod) -> surplus LINAK LA34 L (4.5 kg weighed listing, trimbio SACT634): body 4.05 + rod 0.45
  - GR-04 pawls: cranked G6 blade, +8 % (0.100 -> 0.108 kg each)
  - ballast fill row at the can position (x 1215, two 10 L cans, floor z 124, internal height 130 mm): CG at half the fill height
Densities (loose bulk, dry): steel punchings 4.1 kg/L (Graepels marine ballast punchings 4.1-4.5 t/m3; RTU study 4.08 freely settled),
dry gravel 1.68 kg/L (Engineering ToolBox).  usage: python3 masses_g6.py -> mass_g6_<label>.json + masses_g6_table.json"""
import json, os, copy
H=os.path.dirname(os.path.abspath(__file__)); CAD=os.path.join(H,'..','..','cad')
M=json.load(open(os.path.join(CAD,'mass_g3_sim_L95.json')))
rows=[r for r in M['rows'] if r['name']!='Sand ballast fill']
for r in rows:
    if r['name'].startswith('Tilt actuator IP66'): r['kg']=4.05; r['name']='Tilt actuator LINAK LA34 L (surplus hoist) body, 4.5 kg incl. rod'
    elif r['name'].startswith('Tilt actuator rod'): r['kg']=0.45; r['name']='Tilt actuator LA34 piston rod'
    elif r['name'].startswith('GR-04'): r['kg']=0.108
DRY=round(sum(r['kg'] for r in rows),2)
DENS=dict(steel=4.1,gravel=1.68); CANL=20.0; H_IN=130.0; Z0=124.0
tab=dict(dry_kg=DRY,can_L=CANL,densities_kg_per_L=DENS,rows=[])
for op in (95,100,105,110):
    fill=round(op-DRY,2)
    for mat in ('steel','gravel'):
        V=fill/DENS[mat]; f=V/CANL; ok=f<=0.95
        tab['rows'].append(dict(operating_kg=op,ballast_kg=fill,material=mat,volume_L=round(V,1),can_fill_pct=round(100*f),fits=bool(ok),cg_z_mm=round(Z0+H_IN*f/2,1)))
        R=copy.deepcopy(rows)
        R.append(dict(name='Ballast fill, dry %s (%.1f L, %.0f %% of 2 x 10 L cans)'%('steel punchings' if mat=='steel' else 'gravel',V,100*f),mod='Chassis',ship='LOCAL',kg=fill,
                      src='%s %.2f kg/L loose bulk'%(mat,DENS[mat]),cx=1215.0,cy=0,cz=round(Z0+H_IN*f/2,1),dx=150,dy=440,dz=max(5,round(H_IN*f))))
        lab='M%d%s'%(op,'' if mat=='steel' else 'g')
        if mat=='steel':   # variant: same ballast as a flat steel-punching box low over the drive axle (x 760, z 140) - packaging to be checked in CAD
            R2=copy.deepcopy(R); R2[-1]['cx']=760.0; R2[-1]['cz']=140.0; R2[-1]['name']+=' [AXLE variant x=760]'
            json.dump(dict(tx=M.get('tx',670.0),label=lab+'ax',total=round(sum(r['kg'] for r in R2),2),rows=R2),open(os.path.join(H,'mass_g6_%sax.json'%lab),'w'),indent=0)
        json.dump(dict(tx=M.get('tx',670.0),label=lab,total=round(sum(r['kg'] for r in R),2),rows=R),open(os.path.join(H,'mass_g6_%s.json'%lab),'w'),indent=0)
json.dump(tab,open(os.path.join(H,'masses_g6_table.json'),'w'),indent=1)
print(json.dumps(tab,indent=1))
