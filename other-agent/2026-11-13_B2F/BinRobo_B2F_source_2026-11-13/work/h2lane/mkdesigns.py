import json,copy
P='/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c'
H=json.load(open(P+'/revH2_ext/BinTug_handover_2026-11-12/revH2/reference_out/RevH2_lanefit_design.json'))
B=json.load(open(P+'/revG/sim/cg/b2/design_B2.json'))
# 1 Rev H2 as delivered (cmp rules)
d=copy.deepcopy(H); d['name']='RevH2_cmp'; json.dump(d,open('RevH2_cmp.json','w'),indent=1)
# 2 Rev H2 with B2 lane rules: true castor swivel circles instead of boxes, B1 centre line, guard 0.40, srun
d=copy.deepcopy(H); d['name']='RevH2_b2r'
d['parts']=[p for p in d['parts'] if 'castor' not in p[4]]
d['circles']=[[0.875,0.30,0.185],[0.875,-0.30,0.185]]
d['kl_gap']=round(0.40+(0.485-d['half_w']),3); d['guard']=0.40; d['pivot_strategy']='srun'
d['src']+=' | S8 B2-rules variant: castor boxes replaced by true swivel circles r0.185 @ (0.875,+/-0.30) (params.py note)'
json.dump(d,open('RevH2_b2r.json','w'),indent=1)
# 3 B2-F: B2 footprint, docking on the bin FRONT wall: handle points away from the mast (handle_dir -1);
# bin = plumb ESE240SL incl handle (0.772 x 0.583, as Rev H2 JSON) with its front wall at B2's comb face x=0.2692
bF=[[0.2692-0.772,0.2915],[0.2692-0.772,-0.2915],[0.2692,-0.2915],[0.2692,0.2915]]
for nm,rules in (('B2F_cmp',False),('B2F_b2r',True)):
    d=copy.deepcopy(B); d['name']=nm; d['bin']=bF; d['handle_dir']=-1
    if not rules:
        for k in ('kl_gap','pivot_strategy','guard'): d.pop(k,None)
        d.pop('circles'); d['parts']+= [[0.95-0.152,0.95+0.152,0.28-0.152,0.28+0.152,'castor L swivel as box'],[0.95-0.152,0.95+0.152,-0.28-0.152,-0.28+0.152,'castor R swivel as box']]
    d['src']='B2-F (S8, 12 Nov): B2 plan turned round to dock on the bin front wall; handle_dir -1; bin plumb ESE240SL incl handle, front wall at B2 comb face x 0.269; pivot_D_sim 2.39 kept from B2 G5 (handle-side bin, MuJoCo) as a floor. '+B['src']
    json.dump(d,open(nm+'.json','w'),indent=1)
