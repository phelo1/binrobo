#!/usr/bin/env python3
"""Compose docs/reviews/COMPARE_B1_vs_RevH.md from work/compare_template.md + work/compare_audit.md + generated tables. ASCII only."""
import os, json, re
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.abspath(os.path.join(H, '..', '..', '..', '..')); RES = os.path.join(H, 'res')
J = lambda f: json.load(open(os.path.join(RES, f)))
T = open(os.path.join(P, 'work', 'compare_template.md')).read()
tab = open(os.path.join(RES, 'tables_cmp.md')).read()
main, rest = tab.split('Extra grab Monte Carlos', 1)
extras = 'Extra grab Monte Carlos' + rest.split('| B1 comb (G1')[0]
combt = '| B1 comb (G1' + rest.split('| B1 comb (G1')[1].split('| design, perturbation')[0]
pert = '| design, perturbation' + rest.split('| design, perturbation')[1].split('Peak loads')[0]
peaks = 'Peak loads' + rest.split('Peak loads')[1]
G = dict(Hraw=J('gate_H__raw.json'), Hfx=J('gate_H__fx.json'), B1=J('gate_B1__f9.json'), FW=J('gate_B1__fwm.json'))
def short(S, k):
    s = S[k]; pf = 'PASS' if s['PASS'] else 'FAIL'
    if k == 'G1': return '%s %d/%d, FH %d' % (pf, s['pooled'], s['n'], s['false_holds'])
    if k == 'G2': return '%s %d/6' % (pf, sum(1 for v in s['runs'].values() if v and v['ok']))
    if k == 'G3': return '%s (a) %s, (b) %s' % (pf, *[('pass' if s[x] and s[x]['ok'] else 'fail %.2f m' % s[x]['dist']) for x in ('one', 'both')])
    if k == 'G4': return '%s %s' % (pf, ' / '.join('%.2f m' % v['stop'] for v in s['runs'].values() if v))
    if k == 'G5': return '%s %.2f m' % (pf, s['run']['swept'])
    if k == 'G6': return '%s %d/18' % (pf, s['passed'])
    if k == 'G7': return pf + (' (fails at both dt)' if not all(v['base'] for v in s['runs'].values() if isinstance(v, dict)) else '')
    if k == 'G8': return '%s %d/8' % (pf, sum(1 for v in s['poses'].values() if v and v['ok']))
    if k == 'G9': return '%s %.1f kg' % (pf, s['kg'] + (1.6 if S is G['FW'] else 0))
NM = dict(G1='G1 grab MC (3 x 30)', G2='G2 climb 12 % (6)', G3='G3 40 mm step', G4='G4 e-stop 12 % (stop)', G5='G5 carry + pivot', G6='G6 set-down (18)', G7='G7 dt repeat', G8='G8 static (8 poses)', G9='G9 mass <= 120 kg')
sc = ['| item | Rev H raw | Rev H + FH1 + FH2 | B1 | B1 + 640 mm comb |', '|---|---|---|---|---|']
for k in NM: sc.append('| %s | %s |' % (NM[k], ' | '.join(short(G[d], k) for d in ('Hraw', 'Hfx', 'B1', 'FW'))))
sc.append('| **items passed** | **%d/9** | **%d/9** | **%d/9** | **%d/9** |' % tuple(G[d]['passed'] for d in ('Hraw', 'Hfx', 'B1', 'FW')))
# hand calc table
HC = J('handcalc_cmp.json'); hc = ['| case | M kg | tip lateral deg | tip fwd over castors deg | castor lift-off deg | rear tip deg | castor N flat | mu req 12 % | N m/wheel 12 % |', '|---|---|---|---|---|---|---|---|---|']
for c in HC['B1']['cases']: hc.append('| B1, bin %d kg | %.1f | %.1f | %.1f | %.1f | %.1f | %d | %.3f | %.1f |' % (c['bin_kg'], c['M'], c['tip_lateral_deg'], c['tip_forward_over_castors_deg'], c['castor_liftoff_about_drive_axle_deg'], c['rear_tip_on_antitip_deg'], c['castor_N_flat'], c['mu_req_12'], c['torque_per_wheel_12_Nm']))
for c in HC['RevH']['cases']: hc.append('| Rev H, bin %d kg, hang %.1f deg | %.1f | %.1f | %.1f | %.1f | %.1f | %d | %.3f | %.1f |' % (c['bin_kg'], c['hang_tilt_deg'], c['M'], c['tip_lateral_deg'], c['tip_forward_over_castors_deg'], c['castor_liftoff_about_drive_axle_deg'], c['rear_tip_on_tail_wheels_deg'], c['castor_N_flat'], c['mu_req_12'], c['torque_per_wheel_12_Nm']))
hc += ['', '| comb / lip case (gate-model ledge 30 x 8 mm, not measured) | force N | comb mm | receiver covered | line load N/mm | ledge bending MPa |', '|---|---|---|---|---|---|']
for k, v in HC['lip'].items(): hc.append('| %s | %d | %d | %d %% | %.2f | %.1f |' % (k, v['F_N'], v['comb_mm'], v['coverage_pct'], v['line_load_N_per_mm'], v['ledge_bending_MPa']))
# cost table
C = J('cost_cmp.json'); r = C['revH_claim']; rb = C['revH_rebased']; b = C['B1']; bd = C['B1_donor_indicative']
ct = ['| | parts | logistics | contingency | **all-in** | basis |', '|---|---|---|---|---|---|',
      '| Rev H as claimed | %.0f | %.0f | %.0f | **%.0f** | vs Rev G published; 18 %% of parts checked |' % (r['parts'], r['logistics'] + r['duty'], r['contingency'], r['all_in']),
      '| Rev H re-based | %.0f | %.0f | %.0f | **%.0f** | Rev H mover lines + G8 Lean-D shared-function lines; donor chair EUR 400 |' % (rb['parts'], rb['logistics'], rb['contingency'], rb['all_in']),
      '| B1 (final) | %.0f | %.0f | %.0f | **%.0f** | G8 Lean concept B + iteration 1 (new drive) |' % (b['basis']['parts'] + b['delta']['parts'], b['basis']['logistics'] + b['delta']['logistics'], b['basis']['contingency'] + b['delta']['contingency'], b['all_in']),
      '| B1 on a donor drive (indicative) | %.0f | %.0f | %.0f | **%.0f** | lean Structure/Drive/Power swapped for the G8 donor lines; not designed |' % (bd['parts'], bd['logistics'], bd['contingency'], bd['all_in']),
      '| B1 + 640 mm comb | +%.0f | - | +%.0f | **about +%.0f** | estimate (plate + 2-axis pivot) |' % (C['fw_comb_delta']['eur_est'], 0.12 * C['fw_comb_delta']['eur_est'], 1.12 * C['fw_comb_delta']['eur_est'])]
ct += ['', 'Shared-function lines Rev H prices below the G8 Lean-D list (EUR): ' + ', '.join('%s %+.0f' % (k, v) for k, v in C['shared_gap'].items()) + '.']
PK = J('peaks_cmp.json')
rep = {'SCORE_COMPACT': '\n'.join(sc), 'TABLES_MAIN': main.strip() + '\n\n' + extras.strip() + '\n\n' + peaks.strip(), 'TABLES_PERT': pert.strip(),
       'AUDIT_SECTION': open(os.path.join(P, 'work', 'compare_audit.md')).read().strip(), 'LANEFIT': open(os.path.join(RES, 'lanefit_table.md')).read().strip(),
       'HANDCALC': '\n'.join(hc), 'COST': '\n'.join(ct), 'COMB_TABLE': combt.strip(),
       'PEAK_H': '%.0f' % PK['Hfx']['nib_rim_N'][0], 'PEAK_B1': '%.0f' % PK['B1']['nib_rim_N'][0]}
for f in ('COMB_TEXT', 'HYBRIDS', 'COMB_PLACEHOLDER'):
    p = os.path.join(P, 'work', 'compare_%s.md' % f.lower()); rep[f] = open(p).read().strip() if os.path.exists(p) else '(pending)'
for k, v in rep.items(): T = T.replace(k, v)
T = T.replace('\u2013', '-').replace('\u2014', '-').replace('\u00b0', ' deg').replace('\u2019', "'")
bad = sorted(set(ch for ch in T if ord(ch) > 127)); assert not bad, bad
open(os.path.join(P, 'docs', 'reviews', 'COMPARE_B1_vs_RevH.md'), 'w').write(T); print('ok', len(T))
