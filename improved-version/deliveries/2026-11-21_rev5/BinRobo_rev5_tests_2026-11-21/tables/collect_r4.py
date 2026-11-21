#!/usr/bin/env python3
"""Collects the revision 4 mechanical results (tag given) into one JSON and a printed summary. Reads result files only.
Their gate scorer reads the tipping hand calculation from a file without a tag (B2-F's own). Here it is run on a folder of links in which that
file is this tag's own tip calculation, so the G8 block of the gate file belongs to the model under test.
usage (from revG/sim/cg): collect_r4.py <tag> <mass json> <out.json>"""
import json, glob, os, sys, subprocess, re
tag, massf, outp = sys.argv[1:4]; RES = 'h2/res'; O = dict(tag=tag)
L = lambda n: json.load(open(os.path.join(RES, 'B2F_%s%s.json' % (n, tag))))
# gate, their scorer
import shutil, tempfile
GD = tempfile.mkdtemp(prefix='gate' + tag)
for f in glob.glob(os.path.join(RES, 'B2F_*%s.json' % tag)) + glob.glob(os.path.join(RES, 'B2F_*%s_s*.json' % tag)): os.symlink(os.path.abspath(f), os.path.join(GD, os.path.basename(f)))
shutil.copy(os.path.join(RES, 'B2F_tipcalc%s.json' % tag), os.path.join(GD, 'B2F_tipcalc.json'))
g = subprocess.run(['python3', 'h2/summarize_h2.py', 'B2F_', tag, GD, 'B2F', massf], capture_output=True, text=True).stdout
for f in glob.glob(os.path.join(GD, 'gate_*.json')): shutil.copy(f, os.path.join(RES, os.path.basename(f)))
O['gate'] = {m.group(1): m.group(2) for m in re.finditer(r'^(G\d) (PASS|FAIL)', g, re.M)}; O['gate_lines'] = [l[:400] for l in g.splitlines() if re.match(r'G\d ', l)]
# pick-ups
LIP = dict(WEB140=0.48, ESE240SL=0.58, ESE240CL=0.58); P = []; tot = dict(n=0, lifted=0, refused=0, fh_their=0, off50=0, off80=0, setdowns=0, knocked=0)
for f in sorted(glob.glob(os.path.join(RES, 'B2F_grab_*%s*.json' % tag))):
    b = os.path.basename(f)
    if not re.search(r'%s(_s\d+)?\.json$' % re.escape(tag), b): continue
    if re.search(r'_p(m\d|mu|crr)', b): continue      # stress-case pick-ups are counted with the stress cases
    d = json.load(open(f)); bn = d['bin']; runs = d['runs']; band_old = abs(0.32 - LIP[bn] / 2) + 0.02; band_new = abs(0.35 - LIP[bn] / 2) + 0.02
    lifted = [r for r in runs if r.get('claim')]; ny = [abs(r['nib_y_mm']) / 1000.0 for r in lifted]
    row = dict(file=b, bin=bn, seed=d['seed'], n=len(runs), lifted=len(lifted), refused=len(runs) - len(lifted), false_holds_their_score=d['false_holds'], knocked=d['knocked'],
               beyond_640_band=sum(1 for v in ny if v > band_old), beyond_700_band=sum(1 for v in ny if v > band_new), band_640_mm=round(band_old * 1000), band_700_mm=round(band_new * 1000),
               max_off_mm=round(max(ny) * 1000, 1) if ny else None, setdowns=sum(max(len(r.get('posthold_mm', [])) - 1, 0) for r in runs), results={k: sum(1 for r in runs if r['result'] == k) for k in sorted(set(r['result'] for r in runs))},
               retries=sum(1 for r in runs if r.get('reapp')), dock_dy_max=round(max(abs(r['dock_dy_mm']) for r in runs if r.get('dock_dy_mm') is not None), 1))
    P.append(row)
    for k, v in (('n', row['n']), ('lifted', row['lifted']), ('refused', row['refused']), ('fh_their', row['false_holds_their_score']), ('off50', row['beyond_640_band']), ('off80', row['beyond_700_band']), ('setdowns', row['setdowns']), ('knocked', row['knocked'])): tot[k] += v
O['pickups'] = P; O['pickups_total'] = tot
# nose-light climbs and statics with the high bin
S7 = []
for f in sorted(glob.glob(os.path.join(RES, 'B2F_S7_climb*%s.json' % tag))):
    d = json.load(open(f)); S7.append(dict(file=os.path.basename(f), reached=d['reached'], yaw_dev=round(d['yaw_dev'], 2), castor_min_raw_N=round(d['castor_min_N'], 1), castor_min_100ms_N=round(d['castor_ma100ms_min_N'], 1), castor_mean_N=d.get('castor_mean_N'), frac_below_50N=d.get('castor_frac_below_50N'), ok_raw=d['ok'], ok_filtered=d['ok_filtered']))
O['s7'] = S7
for nm in ('tipcalc', 'tipcalc_cg60'):
    try: d = L(nm); O[nm] = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in d.items() if not isinstance(v, (dict, list))}
    except Exception as e: O[nm] = str(e)
# stress cases
PT = []
for f in sorted(glob.glob(os.path.join(RES, 'B2F_*_pm*%s.json' % tag)) + glob.glob(os.path.join(RES, 'B2F_*_pcrr*%s.json' % tag))):
    d = json.load(open(f)); b = os.path.basename(f)
    if 'grab' in b: ok = d['captured'] == d['n'] and d['false_holds'] == 0 and d['knocked'] == 0; det = '%d of %d' % (d['captured'], d['n'])
    else: ok = bool(d.get('ok')); det = ''
    PT.append(dict(file=b, ok=ok, detail=det))
O['stress'] = PT; O['stress_pass'] = sum(1 for p in PT if p['ok']); O['stress_n'] = len(PT)
json.dump(O, open(outp, 'w'), indent=1)
print('GATE', O['gate']); print('PICK-UPS', tot)
for r in P: print('   %-10s seed %-4s n %d lifted %d refused %d their-false-holds %d | beyond %d mm band %d, beyond %d mm band %d | largest offset %s mm | set-downs %d | retries %d | %s' % (r['bin'], r['seed'], r['n'], r['lifted'], r['refused'], r['false_holds_their_score'], r['band_640_mm'], r['beyond_640_band'], r['band_700_mm'], r['beyond_700_band'], r['max_off_mm'], r['setdowns'], r['retries'], r['results']))
print('S7', S7); print('TIP', O.get('tipcalc')); print('TIP cg60', O.get('tipcalc_cg60')); print('STRESS %d of %d' % (O['stress_pass'], O['stress_n']), [p['file'] for p in PT if not p['ok']])
