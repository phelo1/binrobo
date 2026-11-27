#!/usr/bin/env python3
"""Table of lane runs. usage: lane_table.py <runs_dir> [<runs_dir> ...] (directories under work/b2f_lanephys)"""
import json, sys, os, glob, ast
B = '/home/claude/b2f_run/work/b2f_lanephys'
for d in sys.argv[1:]:
    for f in sorted(glob.glob(os.path.join(B, d, '*', 'result.json'))):
        j = json.load(open(f)); m = j.get('metrics') or {}
        if isinstance(m, str): m = ast.literal_eval(m)
        g = lambda k, s=1.0, n=0: ('%.*f' % (n, m[k] * s)) if isinstance(m.get(k), (int, float)) else '-'
        print('%-12s %-20s %-5s sim %5.0f s  E %5.1f Wh  bin-wheel clear %s mm  hedge %s m  roll %s  pitch %s  tip %s deg  lift %s N  %s' % (
            d, j['run'], j['verdict'], j['sim_time_s'], j['energy_Wh'], g('clear_min', 1000) if m.get('clear_min', 9) < 8 else '-', g('hedge_min', 1, 3) if m.get('hedge_min', 9) < 8 else '-',
            g('roll_max', 1, 1), g('pitch_max', 1, 1), g('tip_min', 1, 1), g('liftF_max'), j.get('fails') if j['verdict'] != 'PASS' else ''))
