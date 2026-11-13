import json,sys
for f in sys.argv[1:]:
    R=json.load(open(f)); print('==',R['design'],'pivotD',R['pivot_D_empty'],R['pivot_D_load'],'sweep',R['sweep_min'],{k:(v['min_clear_m'],v['at_s']) for k,v in R['sweep'].items()},'lane pivot frac',R['lane_pivot_frac_empty'],R['lane_pivot_frac_loaded'],'nar',R.get('narrowing_pivot_margin_loaded'))
    yd=[(k,v[0]) for k,v in list(R['yard_dock'].items())+list(R['mouth'].items())]
    print(' yard/dock/mouth min', min(yd,key=lambda t:t[1]), 'fails',[k for k,v in yd if v<=0])
    for k,v in R['sequences'].items():
        ms=[s[1] for s in v['steps'] if s[1] is not None]; w=min(v['steps'],key=lambda s:9 if s[1] is None else s[1])
        print('  %-26s %s min %.3f  worst: %s'%(k,'OK  ' if v['ok'] else 'FAIL',min(ms),w))
