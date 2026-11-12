#!/usr/bin/env python3
"""Build the numeric tables for COMPARE_B1_vs_RevH.md from the result JSONs -> res/tables_cmp.md (pasted / included by the report).
Missing results are printed as 'not run' (never as pass)."""
import os, json, glob, math
H = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(H, 'res'); IT1 = os.path.join(H, '..', 'it1', 'res')
def J(f): return json.load(open(f)) if os.path.exists(f) else None
def R(pfx, n, tag, rd=RES):
    d = J(os.path.join(rd, pfx + n + tag + '.json'))
    if d is None and n.startswith('step40'): d = J(os.path.join(rd, pfx + n + '_rw318' + tag + '.json'))  # Rev H rw 0.159 file suffix
    return d
out = []
def P(s=''): out.append(s)

G = dict(B1=J(os.path.join(RES, 'gate_B1__f9.json')), Hraw=J(os.path.join(RES, 'gate_H__raw.json')), Hfx=J(os.path.join(RES, 'gate_H__fx.json')), FW=J(os.path.join(RES, 'gate_B1__fwm.json')))
PROV = J(os.path.join(RES, 'gate_fw_provenance.json')) or {}
PFXS = dict(G1=('grab_',), G2=('climb_',), G3=('step40_',), G4=('estop12_',), G5=('towstab',), G6=('rel_',), G7=('climb_m25_c09_dt025', 'step40_one_dt025', 'estop12_fwd_dt025'), G8=('static_',), G9=())
def fwprov(k):
    ns = [n for n in PROV if any(n.startswith(p) for p in PFXS[k]) and (k == 'G7' or 'dt025' not in n)]
    if k == 'G9': return ' (+1.6 kg comb, est.: 95.7 kg)'
    r = sum(1 for n in ns if PROV[n] == 'fwp32 run')
    return '' if ns and r == len(ns) else (' *[inherited from B1 final]*' if r == 0 else ' *[%d of %d runs re-run with the 640 mm comb, rest inherited]*' % (r, len(ns)))
def g1s(S, key='G1'):
    if not S: return 'not run'
    g = S[key]; b = g['bins']
    return '%s; pooled %d/%d; FH %d; knocked %d' % (' / '.join('%s %s' % (k.replace('ESE240', '').replace('WEB140', 'WEB'), ('%d/%d' % (v['captured'], v['n'])) if isinstance(v, dict) else v) for k, v in b.items()),
                                                  g['pooled'], g['n'], g['false_holds'], g['knocked'])
def g2s(S):
    if not S: return 'not run'
    r = S['G2']['runs']; ok = sum(1 for v in r.values() if v and v['ok'])
    ts = [v['t'] for v in r.values() if v]; cr = [v['creep'] for v in r.values() if v]
    bad = [k for k, v in r.items() if not (v and v['ok'])]
    return '%d/6; %s-%s s; creep <= %.3f m%s' % (ok, min(ts) if ts else '-', max(ts) if ts else '-', max(cr) if cr else 0, ('; fail: ' + ', '.join('%s (grab %s, %.2f m)' % (k, r[k]['grab'], r[k]['dist']) for k in bad if r[k])) if bad else '')
def g3s(S):
    if not S: return 'not run'
    o, b = S['G3']['one'], S['G3']['both']
    f = lambda x: ('PASS (%.2f m, clear %.0f mm)' % (x['dist'], 1000 * x['clear_min']) if x['ok'] else 'FAIL (%.2f m, grab %s, bin-ground %.0f N, seated %s)' % (x['dist'], x['grab'], x['bin_ground'], x['seated'])) if x else 'not run'
    return 'one side %s; full width %s' % (f(o), f(b))
def g4s(S):
    if not S: return 'not run'
    r = S['G4']['runs']; return ' / '.join('%s %s %.2f m, slide %.3f' % (k, 'PASS' if v['ok'] else 'FAIL', v['stop'], v['slide']) if v else k + ' not run' for k, v in r.items())
def g5s(S):
    if not S or not S['G5']['run']: return 'not run'
    v = S['G5']['run']; return '%s; roll %.2f deg; pivot swept %.2f m' % ('PASS' if v['ok'] else 'FAIL', v['roll'], v['swept'])
def g6s(S):
    if not S: return 'not run'
    g = S['G6']; c = g['cases']; bad = ['%s %s' % (k.replace('ESE240', ''), v) for k, v in c.items() if v != 'PASS']
    return '%d/18, %d TIPS%s' % (g['passed'], g['tips'], ('; ' + ', '.join(bad)) if bad else '')
def g7s(S):
    if not S: return 'not run'
    r = S['G7']['runs']; return '; '.join('%s %s' % (k, ('base %s / dt025 %s%s' % (v['base'], v['dt025'], (' t %s/%s s' % tuple(v['t'])) if v['t'][0] else '')) if isinstance(v, dict) else v) for k, v in r.items())
def g8s(S):
    if not S: return 'not run'
    p = S['G8']['poses']; okn = sum(1 for v in p.values() if v and v['ok'])
    dmin = min(min(v['dL'], v['dR']) for v in p.values() if v); cmin = min(v['castors'] for v in p.values() if v)
    bad = [k for k, v in p.items() if not (v and v['ok'])]
    return '%d/8 poses; drive >= %.0f N, castors >= %.0f N; hand-calc min tip %.1f deg%s' % (okn, dmin, cmin, S['G8']['handcalc_min_tip_deg'], ('; fail: ' + ', '.join(bad)) if bad else '')
def g9s(S): return ('%.1f kg' % S['G9']['kg']) if S else 'not run'
P('| item | Rev H as designed (raw) | Rev H + FH1 + FH2 (2 firmware fixes) | B1 final (160 mm comb) | B1 + 640 mm full-width comb |')
P('|---|---|---|---|---|')
for k, f in (('G1', g1s), ('G2', g2s), ('G3', g3s), ('G4', g4s), ('G5', g5s), ('G6', g6s), ('G7', g7s), ('G8', g8s), ('G9', g9s)):
    cells = []
    for d in ('Hraw', 'Hfx', 'B1', 'FW'):
        S = G[d]; cells.append(('**%s** ' % ('PASS' if S[k]['PASS'] else 'FAIL') if S else '') + f(S) + (fwprov(k) if d == 'FW' else ''))
    P('| %s | %s |' % (k, ' | '.join(cells)))
P('| **items passed** | **%s/9** | **%s/9** | **%s/9** | **%s/9** |' % tuple((G[d]['passed'] if G[d] else '-') for d in ('Hraw', 'Hfx', 'B1', 'FW')))
P()
# extras
P('Extra grab Monte Carlos (reported, not gating):')
P()
for lab, pfx, tag, rd in (('B1 final', 'B1_', '_f9', IT1), ('Rev H raw', 'H_', '_raw', RES), ('Rev H + FH1 + FH2', 'H_', '_fx', RES)):
    xs = []
    for b in ('ESE240SL250', 'ESE140CL'):
        d = R(pfx, 'grab_' + b, tag, rd); xs.append('%s %s' % (b, ('%d/%d, FH %d, knocked %d' % (d['captured'], d['n'], d['false_holds'], d['knocked'])) if d else 'not run'))
    P('- %s: %s' % (lab, '; '.join(xs)))
r1 = R('B1_', 'step40_both_ramp', '_f9'); rH = R('H_', 'step40_both_ramp', '_raw'); rF = R('H_', 'step40_both_ramp', '_fx')
f = lambda x: ('%s (%.2f m, grab %s, bin-ground %.0f N)' % ('PASS' if x['ok'] else 'FAIL', x['dist_m'], x['grab'], x['bin_ground'])) if x else 'not run'
P('- G3(b) with a 1:4 kerb ramp: B1 %s; Rev H raw %s; Rev H fixed %s' % (f(r1), f(rH), f(rF)))
P()
# comb variants for B1
P('| B1 comb (G1, F9) | WEB 140 | ESE 240 SL | ESE 240 CL | pooled | FH | knocked | SL 250 (extra) | ESE 140 CL (extra) |')
P('|---|---|---|---|---|---|---|---|---|')
for lab, tag, rd in (('160 mm (final B1), gate lip', '_f9', IT1), ('160 mm, EN 840 lip', '_f9_en840n', RES),
                     ('640 mm rigid, EN 840 lip', '_f9_fwr32', RES), ('640 mm self-aligning, EN 840 lip', '_f9_fwp32', RES)):
    ds = [R('B1_', 'grab_' + b, tag, rd) for b in ('WEB140', 'ESE240SL', 'ESE240CL', 'ESE240SL250', 'ESE140CL')]
    c = lambda d: ('%d/%d' % (d['captured'], d['n'])) if d else 'not run'
    main = [d for d in ds[:3] if d]
    P('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (lab, c(ds[0]), c(ds[1]), c(ds[2]), ('%d/%d' % (sum(d['captured'] for d in main), sum(d['n'] for d in main))) if main else '-',
                                                         sum(d['false_holds'] for d in main), sum(d['knocked'] for d in main), c(ds[3]), c(ds[4])))
P()
rel = [R('B1_', 'rel_%s_%s_%s' % (b, cs, fl), '_f9_fwp32') for b in ('WEB140', 'ESE240CL', 'ESE240SL250') for cs in ('flat', 'up12', 'dn12') for fl in ('full', 'empty')]
okr = [x for x in rel if x]
P('B1 with the 640 mm self-aligning comb, other affected groups: G6 set-down %s; %s.' % (
    ('%d/%d PASS, %d TIPS' % (sum(1 for x in okr if x['verdict'] == 'PASS'), len(okr), sum(1 for x in okr if x['verdict'] == 'TIPS'))) if okr else 'not run',
    '; '.join('%s %s' % (n, ('PASS' if x['ok'] else 'FAIL') if x else 'not run') for n, x in (('G5 towstab', R('B1_', 'towstab', '_f9_fwp32')), ('G3(a) one side', R('B1_', 'step40_one', '_f9_fwp32')),
                                                                                         ('G4 fwd', R('B1_', 'estop12_fwd', '_f9_fwp32')), ('G4 rev', R('B1_', 'estop12_rev', '_f9_fwp32')),
                                                                                         ('G2 mu 0.22 crr 0.09', R('B1_', 'climb_m22_c09', '_f9_fwp32'))))))
P()
# perturbations
P('| design, perturbation | G1 (10 per bin) | G2 mu 0.22 / 0.25 | G3 one side | G4 fwd / rev | G5 | G6 6 hardest | G8 3 poses |')
P('|----|----|----|----|----|----|----|----|')
for des, pfx, rd, tags in (('B1', 'B1_', IT1, (('pm110f9', 'mass +10 %'), ('pm090f9', 'mass -10 %'), ('pmu085f9', 'mu -15 %'), ('pcrr09f9', 'bin crr 0.09'))),
                           ('Rev H fixed', 'H_', RES, (('_fxpm110', 'mass +10 %'), ('_fxpm090', 'mass -10 %'), ('_fxpmu085', 'mu -15 %'), ('_fxpcrr09', 'bin crr 0.09')))):
    for t, lab in tags:
        t = t if t.startswith('_') else '_' + t
        L = lambda n: R(pfx, n, t, rd)
        g = [L('grab_' + b) for b in ('WEB140', 'ESE240SL', 'ESE240CL')]
        g1 = '%s; FH %d, kn %d' % (' / '.join('%d/%d' % (x['captured'], x['n']) if x else '-' for x in g), sum(x['false_holds'] for x in g if x), sum(x['knocked'] for x in g if x))
        c = [L('climb_m22_c09'), L('climb_m25_c06')]; g2 = ' / '.join(('PASS %.1f s' % x['time_s'] if x['ok'] else 'FAIL %.2f m' % x['dist_m']) if x else '-' for x in c)
        s1 = L('step40_one'); g3 = ('PASS' if s1['ok'] else 'FAIL') if s1 else '-'
        e = [L('estop12_fwd'), L('estop12_rev')]; g4 = ' / '.join(('%s %.2f m' % ('PASS' if x['ok'] else 'FAIL', x['stop_dist_m'])) if x else '-' for x in e)
        w = L('towstab'); g5 = ('PASS %.2f m' % w['swept_diameter_m'] if w['ok'] else 'FAIL') if w else '-'
        rr = [L('rel_' + k) for k in ('WEB140_up12_full', 'WEB140_dn12_empty', 'ESE240CL_up12_full', 'ESE240CL_flat_empty', 'ESE240SL250_up12_empty', 'ESE240SL250_dn12_full')]
        g6 = '%d/6' % sum(1 for x in rr if x and x['verdict'] == 'PASS')
        ss = [L('static_up_110'), L('static_crL_110'), L('static_dn_60')]; g8 = '%d/3' % sum(1 for x in ss if x and x['ok'])
        P('| %s, %s | %s | %s | %s | %s | %s | %s | %s |' % (des, lab, g1, g2, g3, g4, g5, g6, g8))
P()
# peaks
def peaks(pfx, tag, rd):
    pk = {}
    for f in glob.glob(os.path.join(rd, pfx + '*' + tag + '.json')):
        if '_dt025' in f: continue
        d = J(f)
        if isinstance(d, dict) and isinstance(d.get('peak'), dict):
            for k in ('lift_N', 'pad_N', 'nib_rim_N', 'wheel_torque_Nm'):
                v = d['peak'].get(k)
                if v and v[0] > pk.get(k, (0, ''))[0]: pk[k] = (v[0], os.path.basename(f))
    return pk
PK = dict(B1=peaks('B1_', '_f9', IT1), Hraw=peaks('H_', '_raw', RES), Hfx=peaks('H_', '_fx', RES), FW=peaks('B1_', '_f9_fwp32', RES))
P('Peak loads over the carry runs (G2-G6, dt 0.5 ms): ' + '; '.join('%s: %s' % (d, ', '.join('%s %.0f (%s)' % (k, v[0], v[1].replace('.json', '')) for k, v in p.items() if k != 'wheel_torque_Nm')) for d, p in PK.items()))
json.dump(PK, open(os.path.join(RES, 'peaks_cmp.json'), 'w'), indent=1)
open(os.path.join(RES, 'tables_cmp.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
