#!/usr/bin/env python3
"""Tables from the revision 4 map runs (res_r4x): step by castor strip width, approach distance, speed and torque; empty robot on the step;
slippery hill start by strip width; lift shock and wheel load by tyre stiffness. usage: tab_c_r4.py <res dir> [--json out]"""
import json, glob, os, re, sys
D = sys.argv[1].rstrip('/') + '/'; OUT = {}
rows = {}
for f in sorted(glob.glob(D + 'B2F_Y_liftpeak_step_*_r4w*.json')):
    m = re.search(r'step_(one|both)_v(\d+)(_at(\d+))?_r4w(\d+)(t60|b100)', f)
    if not m: continue
    d = json.load(open(f)); side, v, _, at, w, mode = m.groups()
    rows[(side, int(v) / 10.0, float(at) / 10 if at else 1.6, mode, int(w))] = d
print('40 mm step with a full 240 L bin: P = over, S = stalled (distance m). Columns: castor contact strip width, mm')
W = sorted({k[4] for k in rows}); print('  side  v    at   torque | ' + ' '.join('%7d' % w for w in W)); T = []
for side in ('both', 'one'):
    for v in sorted({k[1] for k in rows}, reverse=True):
        for at in (1.6, 3.0):
            for mode in ('t60', 'b100'):
                r = {k[4]: d for k, d in rows.items() if k[:4] == (side, v, at, mode)}
                if not r: continue
                print('  %-4s %.1f  %.1f  %-5s  | ' % (side, v, at, mode) + ' '.join(('      P' if r[w]['reached'] else 'S %5.2f' % r[w]['dist_m']) if w in r else '      -' for w in W))
                T.append(dict(side=side, v=v, at=at, torque=mode, res={w: (True if r[w]['reached'] else r[w]['dist_m']) for w in r}))
OUT['step'] = T
pk = [d for d in rows.values() if d['reached']]
if pk: print('  over the step: lift peak %d..%d N, wheel peak %d..%d N, comb %d..%d N; seated in all: %s; bin on the ground in any: %s' % (min(d['lift_peak_N'] for d in pk), max(d['lift_peak_N'] for d in pk), min(d['wheel_peak_N'] for d in pk), max(d['wheel_peak_N'] for d in pk), min(d['comb_peak_N'] for d in pk), max(d['comb_peak_N'] for d in pk), all(d['seated_all'] for d in rows.values()), any(d['bin_ground_N'] > 0 for d in rows.values())))
print('  held the bin at the end in every run:', all(d['captured_end'] for d in rows.values()), ' runs', len(rows))
E = []
print('\nempty robot on the 40 mm step (castors already trailing)')
for f in sorted(glob.glob(D + 'B2F_Y_stepempty_*.json')):
    d = json.load(open(f)); tg = re.search(r'_r4w\d+(t60|b100)', f).group(1); print('  %-4s v %.1f %-5s: %s (%.2f m), wheel peak %d N, heading %.1f deg' % (d['side'], d['v'], tg, 'over' if d['reached'] else 'STALL', d['dist_m'], d['wheel_peak_N'], d['yaw_end_deg']))
    E.append(dict(side=d['side'], v=d['v'], torque=tg, reached=d['reached'], dist=d['dist_m']))
OUT['step_empty'] = E
print('\nslippery hill start (grip 0.22, bin CG +60 mm): strip width: heading swing deg / raw castor min N / 100 ms min N / reached'); S7 = []
for f in sorted(glob.glob(D + 'B2F_S7_climb_m22_c06_r4w*.json')):
    d = json.load(open(f)); w = int(re.search(r'r4w(\d+)', f).group(1)); print('   %2d mm: %.2f  %6.1f  %6.1f  %s' % (w, d['yaw_dev'], d['castor_min_N'], d['castor_ma100ms_min_N'], d['reached'])); S7.append(dict(w=w, yaw=d['yaw_dev'], raw=d['castor_min_N'], ma=d['castor_ma100ms_min_N'], reached=d['reached']))
OUT['s7'] = S7
print('\nlift shock and wheel load, kerb nose-first, lift cap 12 kN (so the shock is not clipped)'); K = []
for f in sorted(glob.glob(D + 'B2F_Y_liftpeak_kerb_*.json')):
    d = json.load(open(f)); tg = re.search(r'_r4(cap12\w*)\.json', f).group(1); print('  %-10s v %.1f tyre %-28s reached %-5s lift peak %5d (static %d) wheel %5d comb %5d pad %5d sag %.2f mm' % (tg, d['v'], d['tyre'][:28], d['reached'], d['lift_peak_N'], d['lift_static_N'], d['wheel_peak_N'], d['comb_peak_N'], d['pad_peak_N'], d['carriage_sag_mm']))
    K.append(dict(tag=tg, v=d['v'], lift=d['lift_peak_N'], static=d['lift_static_N'], wheel=d['wheel_peak_N'], comb=d['comb_peak_N'], reached=d['reached']))
OUT['kerb'] = K
for f in sorted(glob.glob(D + 'B2F_tyrecal*.json')):
    d = json.load(open(f)); print('  tyrecal', os.path.basename(f), d.get('tyre'), d.get('drive_N'), d.get('deflection_mm'), d.get('k_secant_N_per_m'))
if '--json' in sys.argv: json.dump(OUT, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=0)
