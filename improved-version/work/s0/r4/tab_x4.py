#!/usr/bin/env python3
"""Tables from the exploration runs (res_x4)."""
import json, glob, os, re, sys
D = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/b2f_run/revG/sim/cg/h2/res_x4/'
rows = {}
for f in sorted(glob.glob(D + 'B2F_step40_*_x4w*.json')):
    m = re.search(r'step40_(one|both)_x4w(\d+)(tr\d+)?(t60|b100|t80)', f)
    if not m: continue
    d = json.load(open(f)); side, w, tr, mode = m.groups()
    rows[(side, tr or '', mode, int(w))] = ('pass' if d['ok'] else 'STALL %.2f' % d['dist_m'], d['peak'].get('lift_N', [0])[0], d['peak'].get('wheel_torque_Nm', [0])[0])
print('40 mm step, by castor contact strip width (mm): result')
for side in ('both', 'one'):
    for mode in ('t60', 'b100', 't80'):
        r = [(k[3], v) for k, v in rows.items() if k[0] == side and k[1] == '' and k[2] == mode]
        if r: print('  %-4s %-4s ' % (side, mode) + ' | '.join('%d: %s' % (w, v[0]) for w, v in sorted(r)))
for k, v in sorted(rows.items()):
    if k[1]: print('  trail', k, v)
print('\nslippery hill start (S7, grip 0.22, bin CG +60 mm): heading swing deg / raw castor min N / 100 ms min N / ok raw / ok filtered')
for mode in ('t60', 'b100'):
    out = []
    for f in sorted(glob.glob(D + 'B2F_S7_climb_m22_c06_x4w*%s.json' % mode)):
        d = json.load(open(f)); w = int(re.search(r'x4w(\d+)', f).group(1)); out.append((w, d['yaw_dev'], d['castor_min_N'], d['castor_ma100ms_min_N'], d['ok'], d['ok_filtered'], d['reached']))
    print('  ' + mode); [print('    %2d mm: %.2f  %6.1f  %6.1f  %s %s reached %s' % o) for o in sorted(out)]
print('\nlift shock load (their step and kerb drives, full 240 L bin)')
for f in sorted(glob.glob(D + 'B2F_Y_liftpeak_*.json')):
    d = json.load(open(f)); print('  %-46s cap %5.0f tyre %-26s reached %-5s lift peak %5d static %5d sag %5.2f mm wheel %5d comb %5d pad %5d seated %s ground %d boost %s' % (os.path.basename(f)[15:-5], d['act_cap_N'], d['tyre'][:26], d['reached'], d['lift_peak_N'], d['lift_static_N'], d['carriage_sag_mm'], d['wheel_peak_N'], d['comb_peak_N'], d['pad_peak_N'], d['seated_all'], d['bin_ground_N'], (d['boost'] or {}).get('n')))
for f in sorted(glob.glob(D + 'B2F_tyrecal*.json')):
    d = json.load(open(f)); print('  tyrecal', os.path.basename(f), d['tyre'], d['drive_N'], d['deflection_mm'], d['k_secant_N_per_m'])
