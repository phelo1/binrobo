#!/usr/bin/env python3
"""Revision 5 list A tables: lowering (ground-looking sensors and load guard), edges, kerb, sideways tyre force. usage: tab_a_r5.py <res dir>"""
import json, glob, sys, re
D = sys.argv[1].rstrip('/') + '/'
print('lowering: block mm / where / bin kg | speed mm/s, trip N | ToF short mm (L, R) -> blocks at 10 mm? | guard result, peak N on the block')
for f in sorted(glob.glob(D + 'B2F_Y_lower_*.json')):
    d = json.load(open(f)); t = d.get('tof', {}); sh = (t.get('L', {}).get('short_mm'), t.get('R', {}).get('short_mm')); tr = d.get('tripped')
    tag = re.search(r'_k\d+_m\d+(.*)\.json', f).group(1)
    print('  %3d %-4s %3d kg | %4.0f %3s %-14s | %s -> %-5s | %-22s peak %4s N%s' % (d['obst_mm'], d['where'], d['bin_kg'], d.get('lower_mm_s', 6), d.get('trip_drop_N', ''), tag[:14], sh, max(x or 0 for x in sh) > 10.0, d.get('result'), d.get('peak_block_N'), '' if d.get('check', True) else '  (guard off)'))
print('\nedges')
for f in sorted(glob.glob(D + 'B2F_Y_stepempty*_r5.json')) + sorted(glob.glob(D + 'B2F_Y_liftpeak_step*_r5.json')):
    d = json.load(open(f)); n = f.split('B2F_Y_')[1][:-8]; print('  %-44s at %.2f m  %s (%.2f m)' % (n, d.get('step_at_m', 0), 'over ' if d['reached'] else 'STALL', d['dist_m']))
print('\nkerb, lift cap out of the way')
for f in sorted(glob.glob(D + 'B2F_Y_liftpeak_kerb*_r5cap12*.json')):
    d = json.load(open(f)); print('  %-40s v %.1f lift %5d (static %d) wheel %5d comb %5d pad %5d reached %s' % (f.split('B2F_Y_')[1][:-5], d['v'], d['lift_peak_N'], d['lift_static_N'], d['wheel_peak_N'], d['comb_peak_N'], d['pad_peak_N'], d['reached']))
for f in sorted(glob.glob(D + 'B2F_Y_lat_*_r5.json')):
    d = json.load(open(f)); print('  sideways tyre force', f.split('B2F_Y_')[1][:-5], d['max_lat_N'])
