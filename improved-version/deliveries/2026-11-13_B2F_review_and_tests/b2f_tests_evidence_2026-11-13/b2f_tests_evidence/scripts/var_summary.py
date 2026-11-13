#!/usr/bin/env python3
"""Compare a variant's gate cases with the baseline run on the same simulator. usage: var_summary.py <res_dir> <variant_tag> <baseline_tag>"""
import json, sys, glob, os
res, tag, base = sys.argv[1:4]; n = ok = bok = 0; flips = []; clear = []; bclear = []; rows = {}
for f in sorted(glob.glob(os.path.join(res, 'B2F_*%s.json' % tag))):
    stem = os.path.basename(f)[:-5][:-len(tag)]
    if '_grab_' in stem: continue
    g = os.path.join(res, stem + base + '.json')
    if not os.path.exists(g): continue
    v = json.load(open(f)); b = json.load(open(g)); n += 1; ok += bool(v.get('ok')); bok += bool(b.get('ok'))
    if v.get('ok') != b.get('ok'): flips.append((stem, b.get('ok'), v.get('ok')))
    if 'clear_min' in v and stem.split('_')[1] in ('climb', 'estop12', 'step40', 'towstab'): clear.append(v['clear_min']); bclear.append(b['clear_min'])
    rows[stem] = (v, b)
print('%s vs %s: %d cases, pass %d (baseline %d); verdict changes: %s' % (tag, base, n, ok, bok, flips or 'none'))
if clear: print('   bin-wheel clearance while carried, min over climb/E-stop/step/pivot cases: %.0f mm (baseline %.0f mm)' % (min(clear) * 1000, min(bclear) * 1000))
def pick(stem, keys):
    if stem in rows:
        v, b = rows[stem]; print('   %-28s' % stem, ' '.join('%s %s (%s)' % (k, v.get(k), b.get(k)) for k in keys if k in v))
pick('B2F_estop12_fwd', ('stop_dist_m', 'clear_min', 'pitch')); pick('B2F_climb_m22_c09', ('hold_creep_m', 'clear_min')); pick('B2F_step40_both', ('reached', 'dist_m', 'clear_min', 'pitch', 'roll')); pick('B2F_step40_one', ('reached', 'clear_min', 'roll', 'pitch'))
pick('B2F_towstab', ('ok', 'clear_min', 'roll', 'swept_m', 'sweep_m')); 
for st in ('up_110', 'dn_110', 'crL_110', 'crR_110', 'up_60'):
    stem = 'B2F_static_' + st
    if stem in rows:
        v, b = rows[stem]; ks = [k for k in v if isinstance(v[k], (int, float)) and not isinstance(v[k], bool) and k not in ('cpu_s',)][:9]
        print('   %-22s' % stem, ' '.join('%s %s (%s)' % (k, v[k], b.get(k)) for k in ks))
