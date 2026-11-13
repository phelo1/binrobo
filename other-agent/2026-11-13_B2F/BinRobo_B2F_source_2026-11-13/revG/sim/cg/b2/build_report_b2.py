#!/usr/bin/env python3
"""Build docs/reviews/DESIGN_B2.md from the B2 result JSONs (b2/res), the B1 / Rev H comparison results (cmp/res, it1/res),
the B2 hand calcs and the B2 BOM. ASCII only. Missing results print as 'not run'."""
import os, sys, json, glob, math
H = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(H, 'res'); CMP = os.path.join(H, '..', 'cmp', 'res'); IT1 = os.path.join(H, '..', 'it1', 'res')
P_ = os.path.abspath(os.path.join(H, '..', '..', '..', '..')); DOC = os.path.join(P_, 'docs', 'reviews', 'DESIGN_B2.md')
sys.path.insert(0, H); import tblfmt as T
def J(*p):
    f = os.path.join(*p); return json.load(open(f)) if os.path.exists(f) else None
G = dict(B2=J(RES, 'gate_B2_.json'), B1=J(CMP, 'gate_B1__f9.json'), FW=J(CMP, 'gate_B1__fwm.json'), H=J(CMP, 'gate_H__fx.json'))
HC = J(RES, 'handcalc_b2.json'); HC0 = HC; HCD = J(RES, 'handcalc_b2_donor.json'); HP = J(RES, 'handcalc_b2_post.json'); HB1 = J(IT1, 'handcalc_it1.json')
BOM = J(RES, 'bom_b2.json'); LB2 = J(RES, 'lanefit_B2.json'); LB1 = J(CMP, 'lanefit_B1.json'); LB1S = J(RES, 'lanefit_B1_srun.json'); LH = J(CMP, 'lanefit_RevH.json')
MB2 = J(H, 'mass_cgB2.json'); MD = J(H, 'mass_cgB2_donor.json')
def R(n): return J(RES, 'B2_' + n + '.json')
def gr(n):
    d = R(n); return '%d/%d, FH %d, knocked %d' % (d['captured'], d['n'], d['false_holds'], d['knocked']) if d else 'not run'
def st(n):
    d = R(n)
    if not d: return 'not run'
    if d['test'] == 'step40': return '%s (%.2f m%s)' % ('PASS' if d['ok'] else 'FAIL', d['dist_m'], ', lift peak %.0f N' % d['peak']['lift_N'][0] if 'lift_N' in d['peak'] else '')
    if d['test'] == 'climb12': return '%s (%.1f s, creep %.3f m)' % ('PASS' if d['ok'] else 'FAIL', d['time_s'] or 0, d['hold_creep_m'])
    if d['test'] == 'estop12': return '%s (stop %.3f m, slide %.3f m)' % ('PASS' if d['ok'] else 'FAIL', d['stop_dist_m'], d['slide_after_stop_m'])
    if d['test'] == 'towstab': return '%s (swept %.2f m)' % ('PASS' if d['ok'] else 'FAIL', d['swept_diameter_m'])
    if d['test'] == 'release': return d['verdict']
    if d['test'] == 'static': return '%s (drive %.0f/%.0f N, castors %.0f N)' % ('PASS' if d['ok'] else 'FAIL', d['driveL'], d['driveR'], d['caster_sum'])
    return str(d.get('ok'))
out = []
def P(s=''): out.append(s)
b2 = G['B2']; nb2 = b2['passed'] if b2 else 0
bn = BOM['new']['totals']; bd = BOM['donor']['totals']
hc110 = HC['design']['cases'][0]; hcd110 = HCD['design']['cases'][0]
P('---'); P('title: "BinRobo B2: B1 combined with what Rev H does better"')
P('subtitle: "Design, frozen-gate proof, lane fit, CAD and costed BOM. Criteria frozen 11 Nov 2026 07:51 +03, unchanged (sha256 2cf3f4ec...8a74 before and after)."')
P('author: "Prepared with Hark for Brian"'); P('date: "11 November 2026"'); P('geometry: margin=1.6cm'); P('fontsize: 9pt'); P('colorlinks: true'); P('---'); P()
P('# 1. Result'); P()
P('**B2 passes %d of 9 frozen gate items, the same count as B1 and one more than Rev H with its two firmware fixes. The only failure is again G3(b), the full-width sharp 40 mm step.** No cheap hardware change passed it (section 7), so the 1:4 kerb ramps stay as a lane-prep item. The criteria file was not touched and no threshold was loosened.' % nb2); P()
P('What B2 changes against B1, in one line each:'); P()
for s in ['**Comb:** 640 mm self-aligning comb (yaw +/-4 deg, roll +/-3 deg) on the full EN 840 receiver. G1 89/90 pooled, 0 false holds, 0 knocked; extra bins: SL 250 %s, ESE 140 CL %s.' % (gr('grab_ESE240SL250').split(',')[0], gr('grab_ESE140CL').split(',')[0]),
          '**Pad:** the EUR 389 MSW DSZY4 is gone. A knee toggle driven 10 mm over centre onto a hard stop now holds the pad, moved by a TRU TC24-50-1000 (EUR 59.99, 155 mm long, upright on the pad arm). The stop carries the bin, not the actuator; the packaging clash is gone. New firmware step F10: the lift pauses at load-on while the pad locks.',
          '**Frame:** Rev H style, one tube size (50x50x2 RHS) bolted through about 16 laser plates, built by Brian; the folded tray package is deleted (EUR 603 -> EUR 354).',
          '**Mass:** %.1f kg (B1 94.1 kg + 1.6 kg comb = 95.7 kg). The 85-90 kg target was not reached honestly: the frame saves about 4.5 kg, but castor lift-off needs 5 kg of ballast at the nose to stay above 20 deg (21.5 deg).' % MB2['total'],
          '**Width and turning:** 0.93 m wide (B1 0.97), chamfered nose, castor swivel circles instead of boxes: empty pivot diameter %.2f m (B1 %.2f), loaded %.2f m.' % (LB2['pivot_D_empty'], LB1['pivot_D_empty'], LB2['pivot_D_load']) if LB2 else '',
          '**Lane rules:** keep the B1 centre line, keep 0.40 m (was 0.25 m) from the mapped hedge face, and run on 0.3-3 m with an S-shift before every empty pivot after a drop. B1 run under the same rules scores the same (%s m sweep, %s m worst sequence; B2 %s / %s m): the lane gain comes from the rules, not from the narrower body.' % (('%.3f' % LB1S['sweep_min']) if LB1S else 'not run', ('%.3f' % LB1S['sequence_min_margin']) if LB1S else 'not run', '%.3f' % LB2['sweep_min'], '%.3f' % LB2['sequence_min_margin']),
          '**Cost:** EUR %s all-in with the new drive, EUR %s on a donor chair (B1 EUR 4,743). That is EUR %s / EUR %s over the EUR 2,000 target, which is not reachable.' % ('{:,.0f}'.format(bn['all_in']), '{:,.0f}'.format(bd['all_in']), '{:,.0f}'.format(bn['gap_to_2000']), '{:,.0f}'.format(bd['gap_to_2000']))]:
    if s: P('- ' + s)
P()
# ------------------------------------------------------------------ 2 spec
P('# 2. B2 specification and changes from B1'); P()
P('| item | B2 | B1 | why |'); P('|---|---|---|---|')
rows = [('Overall', 'nose (bumper) x +1.09 m, tail -0.40 m (rear bumpers); width 0.93 m over the chain cases; nose corners chamfered 45 deg to y +/-0.33 m', 'nose +1.09, tail -0.37; 0.97 m over the gearmotors', 'lane margins'),
        ('Frame', 'one tube size 50x50x2 S235: 2 side rails over the drive tyres (y +/-0.43, z 0.36-0.41), nose and mast-base cross-members, 2 mast uprights, top tie; bolted through ~16 laser plates; HDPE bay floor/covers', 'folded 2 mm steel tray, 80x40 side arms, 40x40 mast', 'Rev H simplification; cheaper, Brian can build it'),
        ('Drive', '2 x 330 mm, track 0.80 m; PEWM82M-320W + 3.5:1 chain (new) or donor chair + 2:1 chain (donor variant)', 'same (new only)', 'two costed variants'),
        ('Castors', '2 x 200 mm at x 0.95, y +/-0.28', 'same', 'G3 sensitivity: 250 mm did not help'),
        ('Comb', '640 x 130 x 6 mm self-aligning plate (yaw +/-4, roll +/-3 deg, centring springs), 8 x 20 mm nib along the full width, 2 ToFs, seat + contact switches', '160 mm tooth', 'covers the EN 840 receiver; rigid 640 fails G1 (86/90)'),
        ('Lift', '2 x HGR15 rails, carriage nib top 0.855-1.105 m (250 mm); QC FDI 24 V 4 kN IP65 400 mm unit', 'same', 'step peaks still reach the 3 kN model cap (section 4, item 2)'),
        ('Pad', 'on the carriage 0.58 m below the nib top, 300 x 100 UHMW, die springs 30 kN/m, 300 N preload; 40 mm retract by a knee toggle (2 x 60 mm links) locked 10 mm over centre on a hard stop; TRU TC24-50-1000 (1 kN, 7 mm/s, IP65) upright on the pad arm', 'MSW DSZY4 2.5 kN in line (did not fit)', 'cost, packaging, load path'),
        ('Sensing added', '2 leg-tip gap ToFs on the flare tips (lateral offset in the last 0.5 m)', '-', 'Rev H idea; cheap docking cross-check'),
        ('Anti-tip', 'rollers at x -0.33, y +/-0.42', 'y +/-0.44', 'width'),
        ('Ballast', '5 kg steel plate on the bay floor at x 1.00', '10 kg at x 0.85', 'castor lift-off >= 20 deg'),
        ('Battery', '24 V 20 Ah LiFePO4 in the front bay (x 0.90); donor variant: donor AGM pair 22 kg, no ballast', 'x 0.80', 'free ballast forward'),
        ('Mass', '%.1f kg new drive / %.1f kg donor (limit 120)' % (MB2['total'], MD['total']), '94.1 kg (+1.6 comb)', ''),
        ('Firmware', 'B1 F1-F9 unchanged; F10: lift paused at load-on, pad toggle locks (switch, <= 12 s), then +100 mm; keeper only after the pad lock; pad lock switch is part of the claim', 'F7: pad extended during the lift', 'small actuator never pushes the hanging moment')]
for r in rows: P('| %s |' % ' | '.join(r))
P()
P('Firmware F10 came from three calibration smokes (labelled calibration, not gate results; `b2/smoke*.log`):'); P()
P('- Pad extending during the +100 mm lift at the real actuator speed: the full bins are already hanging on the retracted pad, and the toggle stalls at its widest angle.')
P('- Pad extended before the lift (bin standing): pad friction plus the bin rocking onto the nib fakes a rim-catch, so the lift aborts (Weber 140 full).')
P('- **Adopted:** pad extended at load-on with the lift held (0 N on the pad at that moment, worst 724 N at the lock). With the 500 N TC24-50-500P the leaning 250 mm-wheel bin stalled the toggle (it needs 683 N with 60 mm links), so the 1,000 N TC24-50-1000 was chosen: margin 1.46.')
P('- The B1 model held the extended pad with a soft position servo at the joint limit. B2 drives the toggle 10 mm past centre onto the stop, so the stop takes the load.')
P()
# ------------------------------------------------------------------ 3 taken / rejected
P('# 3. What was taken from each design, and what was rejected'); P()
P('**Kept from B1 (the base):** the comb-on-receiver principle (lift by the handle-side EN 840 receiver, not the front wall), the straddle with the bin wheels on the drive axle, the lift carriage and keeper, the sprung pad on the carriage, every interlock and the F1-F9 approach firmware, the 330 mm drive and 200 mm castors, and all the G8 safety, navigation, comms and dock lines.'); P()
P('**Taken from Rev H, and why:**'); P()
P('- One tube size and a small plate set (frame cost EUR 603 -> 354, Brian-buildable, fewer DXFs).')
P('- Leg-tip gap sensors (EUR 12): an independent lateral reference in the last 0.5 m of the approach (section 6.3).')
P('- The donor-chair drive, as a costed variant only, with a 2:1 chain stage added so the inherent speed cap is not lost.')
P('- Full-width comb coverage, which Rev H argued for. It was proven on B1 and adopted in its self-aligning form.')
P()
P('**Rejected from Rev H, and why:**'); P()
P('- Lifting by the bin front wall: that wall is not the load-rated receiver (COMPARE s.3). Rev H raw scored 2/9 with 29 false holds on the ESE 240 SL.')
P('- The fixed pad: bins hang 11-12 deg and the 250 mm-wheel bin cannot be lifted clear (COMPARE).')
P('- Reduced-order dynamics as evidence: everything here is the project MuJoCo model.')
P('- 260 mm nose castors: the G3 sensitivity shows castor size does not change the full-width step.')
P('- AGM batteries on the new-drive variant: LiFePO4 is lighter, and the 5 kg ballast is cheaper than the extra AGM mass.')
P()
P('**Rejected within B2, with evidence:**'); P()
P('- A smaller lift actuator (section 4, item 2).')
P('- A passive cam pad driven by carriage travel: the pick-up height varies 0.05-0.17 m between bins, so an absolute cam cannot tell a carried CL bin from an SL 250 being picked up.')
P('- The 500 N pad actuator: it stalls on the SL 250.')
P('- 250 mm castors, lug tyres and a CG shift for G3(b) (section 7).')
P()
# ------------------------------------------------------------------ 4 candidate log
P('# 4. Candidate log (each kept only if it holds or improves the gate)'); P()
P('| # | candidate | decision | evidence |'); P('|---|---|---|---|')
fwt = R('towstab'); s1 = R('step40_one'); sb = R('step40_both')
cl = [('1', '640 mm self-aligning comb', 'ADOPTED', 'B2 G1 %s; G6 18/18; extra SL 250 %s, ESE 140 CL %s. B1+640 had scored 89/90 in COMPARE' % (T.g1s(b2).split(';')[1].strip() if b2 else '-', gr('grab_ESE240SL250'), gr('grab_ESE140CL'))),
      ('2', 'smaller / cheaper lift actuator (the comb peak dropped to 1,952 N)', 'REJECTED', 'B2 lift peak %.0f N on the one-side step and %.0f N on the full-width step (= the 3 kN model cap); static carry %s N. The 1,952 N in COMPARE did not include the step runs. Kept the QC FDI 4 kN IP65 (EUR 137.10 fetched + EUR 25 fittings). Cheaper generic 3 kN IP65 units exist (excerpts, about EUR 50); they are an option only after the T2 cold-force and holding test' % (s1['peak']['lift_N'][0] if s1 else 0, sb['peak']['lift_N'][0] if sb else 0, HP['static_110kg_lift_N'] if HP else '-')),
      ('3', 'pad mechanism (DSZY4: EUR 389, 230 mm vs 140 mm space, 7-9 s)', 'ADOPTED: knee toggle locked over centre + TC24-50-1000', 'Fits upright on the pad arm (155 mm installed). Load path through the stop. Worst actuator need 680 N of 1,000 N (SL 250 full). EUR 59.99 + EUR 12 parts. **Speed not improved:** about 7.7 s per move (7 mm/s); the 16 mm/s 500 N unit stalls on the SL 250. Passive cam rejected (see s.3)'),
      ('4', 'Rev H frame (one tube size, ~14-16 plates), mass to 85-90 kg', 'ADOPTED (frame); mass target NOT met', '50x50x2 frame saves ~4.5 kg vs B1 tray+arms but B1\'s 4 kg mast was under-estimated; bare B2 87.3 kg gives castor lift-off 19.1 deg (< 20), so 5 kg ballast at x 1.00 -> 21.5 deg at %.1f kg. Hand-calc min tip %.1f deg; G8 castors >= %s N' % (MB2['total'], b2['G8']['handcalc_min_tip_deg'] if b2 else 0, min(v['castors'] for v in b2['G8']['poses'].values()) if b2 else '-')),
      ('5', 'leg-tip gap sensors', 'ADOPTED (EUR 12)', 'Camera stress 16 mm sigma: ESE 240 SL %s without, %s with; ESE 240 CL %s without, %s with (section 6.3). Gate runs use the frozen camera model only (sensors not credited)' % (gr('grab_ESE240SL_cam16'), gr('grab_ESE240SL_cam16gap'), gr('grab_ESE240CL_cam16'), gr('grab_ESE240CL_cam16gap'))),
      ('6', 'drive: new PEWM82M + chain vs donor chair', 'BOTH COSTED; new drive is the reference', 'New EUR %s, donor EUR %s all-in. Donor carry tests on 318 mm wheels: section 6.4. Donor keeps the speed-cap layer only with an added 2:1 chain (EUR 90 est.)' % ('{:,.0f}'.format(bn['all_in']), '{:,.0f}'.format(bd['all_in']))),
      ('7', 'full-width 40 mm step without ramps', 'NO CHEAP PASS THAT HOLDS THE GATE; ramps stay', '250 mm castors %s; 20 kg at the nose %s. A bar-tread lug tyre DOES climb it (%s; lugs + nose ballast %s) but fails G1 on the same model (round 3: Weber 140 %s; ESE 240 SL %s): adopting it would trade G1 for G3(b), so it was rejected' % (st('step40_both_cr250'), st('step40_both_cgfwd'), st('step40_both_lug'), st('step40_both_lugcgfwd'), gr('grab_WEB140_lug'), gr('grab_ESE240SL_lug'))),
      ('8', 'lane-fit width + pivot strategy', 'ADOPTED (rules); width alone gives no lane gain', 'B1 with the B2 rules %s; B2 %s (sweep min / worst sequence margin, m). Section 8' % (('%.3f / %.3f' % (LB1S['sweep_min'], LB1S['sequence_min_margin'])) if LB1S else 'not run', '%.3f / %.3f' % (LB2['sweep_min'], LB2['sequence_min_margin'])))]
for r in cl: P('| %s |' % ' | '.join(r))
P()
P('**Rounds (3 allowed, 3 used):**'); P()
P('- **Round 1, calibration smokes (not gate evidence).**')
P('    - Pad sequencing: firmware F10.')
P('    - Pad actuator: the 500 N unit stalls, so it became the 1,000 N unit.')
P('    - Ballast for castor lift-off.')
P('    - Lane-fit sign bug, fixed.')
P('- **Round 2, the full frozen suite plus extras, donor and step sensitivities on B2:** 8/9.')
P('- **Round 3, the frozen suite with lug tyres (the only G3(b) candidate that climbed):** stopped after G1 failed (Weber 140 %s; ESE 240 SL %s, both sets complete). B2 final is the round-2 design.' % (gr('grab_WEB140_lug'), gr('grab_ESE240SL_lug')))
P('- **After round 3, on the round-2 design (reported, not a new round):** the 72 perturbation runs (section 6.1), the gap-sensor stress test (section 6.3) and the B1 lane fit under the B2 rules (section 8).')
P()
P('Pad-actuator speed is the one item the brief asked to fix that B2 does not fix: it trades the speed for cost, packaging and a locked load path. A pick-up takes about 50 s and a set-down about 25 s in the sim (B1 about 45 s / 20 s).'); P()
# ------------------------------------------------------------------ 5 scorecard
P('# 5. Scorecard: B2 vs B1 vs Rev H fixed (frozen gate, CRITERIA_FROZEN.md unchanged)'); P()
P('| item | Rev H + FH1 + FH2 | B1 final (160 mm comb) | B1 + 640 mm comb | **B2** |'); P('|---|---|---|---|---|')
for k, f in (('G1', T.g1s), ('G2', T.g2s), ('G3', T.g3s), ('G4', T.g4s), ('G5', T.g5s), ('G6', T.g6s), ('G7', T.g7s), ('G8', T.g8s), ('G9', T.g9s)):
    cells = []
    for key in ('H', 'B1', 'FW', 'B2'):
        S = G[key]
        if not S: cells.append('not run'); continue
        cells.append(('**PASS**' if S[k]['PASS'] else '**FAIL**') + ': ' + f(S))
    P('| %s | %s |' % (k, ' | '.join(cells)))
P('| **passed** | **%s/9** | **%s/9** | **%s/9** | **%s/9** |' % tuple(G[k]['passed'] if G[k] else '-' for k in ('H', 'B1', 'FW', 'B2')))
P()
P('Notes:'); P()
P('- Rev H + FH1 + FH2 is conditional on a load-rated front-wall lip that the bins do not have (COMPARE s.3).')
P('- In the B1 + 640 mm column, some carry items were inherited from B1 (COMPARE gate_fw_provenance). Every B2 item was run on B2.')
P('- B2 G9 includes 5 kg of ballast. G3(b) with a 1:4 ramp: %s.' % st('step40_both_ramp'))
P()
# ------------------------------------------------------------------ 6 extras
P('# 6. Perturbations, extras and variants (reported, not gating)'); P()
P('## 6.1 Perturbations (reduced suite, as B1 s.7)'); P()
P('| perturbation | G1 (10 per bin: WEB / SL / CL) | G2 mu 0.22 crr 0.09 / mu 0.25 crr 0.06 | G3 one side | G4 fwd / rev | G5 | G6 six hardest | G8 three poses |'); P('|---|---|---|---|---|---|---|---|')
for tg, lab in (('_pm110', 'mass +10 %'), ('_pm090', 'mass -10 %'), ('_pmu085', 'friction -15 %'), ('_pcrr09', 'bin crr 0.09')):
    g1 = ' / '.join(gr('grab_%s%s' % (b, tg)).split(',')[0] for b in ('WEB140', 'ESE240SL', 'ESE240CL'))
    fh = sum((R('grab_%s%s' % (b, tg)) or {}).get('false_holds', 0) + (R('grab_%s%s' % (b, tg)) or {}).get('knocked', 0) for b in ('WEB140', 'ESE240SL', 'ESE240CL'))
    rel = [R('rel_%s%s' % (c, tg)) for c in ('WEB140_up12_full', 'WEB140_dn12_empty', 'ESE240CL_flat_empty', 'ESE240CL_up12_full', 'ESE240SL250_dn12_full', 'ESE240SL250_up12_empty')]
    sta = [R('static_%s%s' % (c, tg)) for c in ('up_110', 'dn_60', 'crL_110')]
    P('| %s | %s; FH+knocked %d | %s / %s | %s | %s / %s | %s | %s | %s |' % (lab, g1, fh, st('climb_m22_c09' + tg), st('climb_m25_c06' + tg), st('step40_one' + tg), st('estop12_fwd' + tg), st('estop12_rev' + tg), st('towstab' + tg),
        ('%d/6' % sum(1 for d in rel if d and d['verdict'] == 'PASS')) if any(rel) else 'not run', ('%d/3' % sum(1 for d in sta if d and d['ok'])) if any(sta) else 'not run'))
P()
P('All four perturbation sets pass every item run. With mass -10 % the one-side step lift peak reaches the 3,000 N model cap (as the nominal full-width step does), which supports keeping the 4 kN lift actuator. Friction -15 % lengthens the forward e-stop to 0.218 m (limit 0.5 m). The bin crr 0.09 set gives carry results identical to nominal: the setting reaches the model (bin-wheel friction loss 0.318 -> 0.477), but in every carry test the bin is lifted off its wheels, so bin rolling resistance only acts in docking and set-down (G1 and G6, both PASS).'); P()
P('## 6.2 Extra bins (the 250 mm-wheel and ESE 140 CL bins)'); P()
P('- ESE 240 SL with 250 mm wheels (seed 204): %s. ESE 140 CL (seed 205): %s.' % (gr('grab_ESE240SL250'), gr('grab_ESE140CL')))
P('- G6 on the SL 250 (part of the frozen G6): all six cases PASS, standing tilt 3.8 deg, its own lean.'); P()
P('## 6.3 Leg-tip gap sensors (camera stress test)'); P()
P('The camera lateral sigma is doubled to 16 mm (seeds 212/213, 20 runs each). Once the bin is inside the flares, the gap sensors replace the camera lateral estimate with 3 mm sigma.'); P()
P('| bin | camera 16 mm only | + leg-tip gap sensors |'); P('|---|---|---|')
for b in ('ESE240SL', 'ESE240CL'): P('| %s | %s | %s |' % (b, gr('grab_%s_cam16' % b), gr('grab_%s_cam16gap' % b)))
P()
P('The ESE 240 SL is not sensitive to the doubled camera noise. On the ESE 240 CL the sensors turn 17/20 with one false hold into 19/20 with none. This is one seed per bin and 20 runs each, so it supports the EUR 12 adoption but does not prove a rate; the frozen gate does not credit the sensors.'); P()
P('## 6.4 Donor-drive variant (318 mm chair wheels, AGM forward, 105.5 kg)'); P()
P('The torque cap stays the frozen 60 N m; with the 2:1 chain stage the real donor torque is higher. Results:'); P()
P('| test | result |'); P('|---|---|')
for n, lab in (('climb_m30_c06_donor', 'G2 mu 0.30 crr 0.06'), ('climb_m30_c09_donor', 'G2 mu 0.30 crr 0.09'), ('climb_m25_c06_donor', 'G2 mu 0.25 crr 0.06'), ('climb_m25_c09_donor', 'G2 mu 0.25 crr 0.09'), ('climb_m22_c06_donor', 'G2 mu 0.22 crr 0.06'), ('climb_m22_c09_donor', 'G2 mu 0.22 crr 0.09'),
               ('step40_one_rw318_donor', 'G3 one side'), ('step40_both_rw318_donor', 'G3 full width'), ('step40_both_ramp_rw318_donor', 'G3 full width, 1:4 ramp'), ('estop12_fwd_donor', 'G4 fwd'), ('estop12_rev_donor', 'G4 rev'), ('towstab_donor', 'G5'),
               ('static_up_110_donor', 'G8 up 110'), ('static_dn_60_donor', 'G8 dn 60'), ('static_crL_110_donor', 'G8 cross L 110'), ('static_crR_110_donor', 'G8 cross R 110'), ('grab_ESE240SL_donor', 'G1 ESE 240 SL (10 runs)')):
    P('| %s | %s |' % (lab, gr(n) if n.startswith('grab') else st(n)))
P()
P('Hand calc donor (110 kg bin): castor lift-off %.1f deg, mu_req on 12 %% %.3f, torque %.1f N m per wheel (x1.25 %.1f).' % (hcd110['castor_liftoff_about_drive_axle_deg'], hcd110['mu_req_12'], hcd110['torque_per_wheel_12_Nm'], hcd110['torque_x1p25'])); P()
P('**Speed-cap point.** A chair geared for about 1.7 m/s loses the inherent gearing layer of the G8 speed limit (G8 s.3 layer a). In B2 the donor variant puts a 2:1 chain stage on each chair gearbox (about 0.83 m/s free), which restores that layer. The variant is only acceptable with this stage; without it, it would be a safety cut.'); P()
# ------------------------------------------------------------------ 7 step
P('# 7. The full-width 40 mm step G3(b)'); P()
s40 = HC0['step40']
P('**Hand calc.** For a driven wheel at a 40 mm edge with free castors, quasi-statically:'); P()
P('- The edge friction needed is mu = tan(a) = **%.2f** for a 330 mm wheel (contact angle %.1f deg). This is geometric: it does not depend on load or CG.' % (s40['mu_edge_needed'], s40['contact_angle_deg']))
P('- The torque needed is W r sin(a) = **%.0f N m** per wheel at %d N wheel load.' % (s40['torque_needed_Nm'], s40['wheel_load_N']))
P('- Against that, the test friction is 0.6, the frozen cap is 60 N m and the real PEWM82M + 3.5:1 gives 53 N m at 25.8 A.')
P('- Bigger wheels lower the friction need but raise the torque need:')
P('    - 400 mm: mu %.2f, %.0f N m' % (s40['wheel_400']['mu'], s40['wheel_400']['T_Nm']))
P('    - 560 mm: mu %.2f, %.0f N m' % (s40['wheel_560']['mu'], s40['wheel_560']['T_Nm']))
P('    - 700 mm: mu %.2f, %.0f N m' % (s40['wheel_700']['mu'], s40['wheel_700']['T_Nm']))
P('- A lug or grouser tyre removes the friction limit, but not the torque limit. Keeping 60 N m would need the wheel load below %d N, so 55 %% of the weight would have to sit on the castors, which breaks G2 traction.' % s40['max_wheel_load_for_60Nm_N'])
P()
P('| cheap change (sim, full-width step, otherwise B2) | result |'); P('|---|---|')
for n, lab in (('step40_both', 'B2 as designed'), ('step40_both_cr250', '250 mm castors'), ('step40_both_lug', '330 mm OD bar-tread tyre, 18 lugs 12 mm deep'), ('step40_both_cgfwd', '20 kg ballast at the nose (CG forward)'), ('step40_both_lugcgfwd', 'lugs + 20 kg at the nose'), ('step40_both_ramp', '1:4 kerb ramp (lane prep)')):
    P('| %s | %s |' % (lab, st(n)))
P()
P('**The lug tyre: round 3.** The lugs interlock with the edge, so the climb no longer depends on friction. Momentum at 0.5 m/s covers the torque shortfall that the quasi-static hand calc predicts. It passes in the sim, so round 3 re-ran the frozen suite with lug tyres.')
P()
P('G1 failed:')
P()
P('- Weber 140: %s.' % gr('grab_WEB140_lug'))
P('- ESE 240 SL: %s.' % gr('grab_ESE240SL_lug'))
P('- Cause: approach heading and lateral control degrade on the rigid lugs. Docking was off by 50 mm and by -300 to -400 mm, and one re-approach was 33 deg off.')
P()
P('A real rubber lug is compliant and may behave better, but that is a hope, not evidence, so lugs were rejected. A cheap lug wheel exists: Wanda P328 13x5.00-6 open-centre, OD 320 mm, GBP 79.50 each at Parnells/B&Q, page fetched; +EUR 180 all-in. Worth one field test: dock 20 times on lug tyres, and climb a real 40 mm kerb at 110 kg (bench test T5).')
P()
P('A brief pad-assisted lift is not possible. The comb only hooks upward under the receiver and the keeper is a light finger, so the robot cannot push down on the bin to unload its drive wheels.'); P()
P('**Decision:** the 1:4 ramps stay as a lane-prep item (EUR 20-40 per surveyed step, not in the BOM), and the route refuses unsurveyed full-width steps over 25 mm. G3 stays FAIL as frozen. The two hardware routes are lug tyres, if a field test shows docking holds, and 4WD (about EUR 300-450, not simulated).'); P()
# ------------------------------------------------------------------ 8 lane
P('# 8. Lane fit (cmp/lanefit.py unchanged; b2/lanefit_b2.py adds the B2 rules; hedge contact = FAIL)'); P()
def lrow(L, lab):
    if not L: return '| %s | not run | | | | | |' % lab
    seq = [st_[1] for v in L['sequences'].values() for st_ in v['steps'] if st_[1] is not None]
    piv = [st_[1] for v in L['sequences'].values() for st_ in v['steps'] if st_[1] is not None and 'empty pivot beyond' in st_[0]]
    nar = [m for s_, m in L['lane_pivot_loaded'] if 500 <= s_ <= 516]
    return '| %s | %.2f / %.2f | %.3f (s %s) | %+.3f | %.3f | %.3f | %s |' % (lab, L['pivot_D_empty'], L['pivot_D_load'], L['sweep_min'], min(v['at_s'] for v in L['sweep'].values() if v['min_clear_m'] == L['sweep_min']),
                                                                        L['sweep_min'] - 0.124, min(seq), min(piv) if piv else float('nan'), 'all PASS' if all(v['ok'] for v in L['sequences'].values()) else 'FAIL')
P('| design / rules | pivot dia. empty / loaded (m) | min hedge clearance, lane sweep (m) | vs p95 estimate error 0.124 m | min margin, all 12 pad sequences (m) | worst empty pivot after a drop (m) | sequences |')
P('|---|---|---|---|---|---|---|')
P(lrow(LH, 'Rev H (COMPARE)')); P(lrow(LB1, 'B1 (COMPARE, SITL rules)')); P(lrow(LB1S, 'B1 with the B2 rules')); P(lrow(LB2, '**B2 with the B2 rules**'))
P()
P('The B2 lane rules:'); P()
P('- **Width:** 0.93 m, keeping the B1 centre line, so there is 0.02 m more on each side.')
P('- **Corridor guard:** 0.40 m from the mapped hedge face, up from the SITL 0.25 m. The narrowing at s 500-516 is still centred.')
P('- **Empty pivots after a drop:** run on 0.3-3.0 m with an S-shift of up to 0.6 x the run before the 180 deg pivot.')
P('- **Smaller swept circle:** chamfered nose and true castor swivel circles.')
P()
P('**B1 under the B2 rules** (`design_B1_srun.json`: same guard, keep-left gap and S-run pivots, B1 footprint): sweep min %s m and worst sequence margin %s m, against B2 %.3f / %.3f m. The two are equal at the binding points (s 417 lane sweep; the empty pivot after a handle-to-road drop, limited by the placed bin and the road boundary). So the lane-fit gain over B1 as run in COMPARE (0.179 / 0.047 m) comes from the route rules, which B1 could adopt too; the 0.04 m narrower body and the smaller pivot circle add no measurable lane margin.' % (('%.3f' % LB1S['sweep_min']) if LB1S else 'not run', ('%.3f' % LB1S['sequence_min_margin']) if LB1S else 'not run', LB2['sweep_min'], LB2['sequence_min_margin'])); P()
P('No footprint point crosses a truth hedge face anywhere (strict scoring). The worst sequence margin (0.104 m) is below the 0.124 m p95 localisation error and stays flagged in section 11 (risk B6). These rules are a SITL change: route planner guard and pivot planner.'); P()
# ------------------------------------------------------------------ 9 hand calcs
P('# 9. Hand calcs'); P()
P('| quantity | B2 (110 kg bin) | B1 | limit / note |'); P('|---|---|---|---|')
hb = HB1['ITER1_B1']['cases'][0]
for k, lab, lim in (('castor_liftoff_about_drive_axle_deg', 'castor lift-off about the drive axle (deg)', '>= 20 (Brian)'), ('tip_lateral_deg', 'lateral tip (deg)', '>= 20 (G8)'), ('tip_forward_over_castors_deg', 'forward tip over castors (deg)', '>= 20'),
                    ('rear_tip_on_antitip_deg', 'rear tip onto anti-tip rollers (deg)', '>= 20'), ('mu_req_12', 'mu_req on 12 % (traction)', '<= 0.22 (G2 lowest mu)'), ('torque_per_wheel_12_Nm', 'torque per wheel on 12 % (N m)', ''),
                    ('torque_x1p25', 'torque x1.25 (N m)', 'PEWM82M+3.5:1: 34.8 @ 17 A'), ('castor_N_12up', 'castor load, 12 % facing up (N)', '> 0'), ('cg_z', 'CG height loaded (m)', '')):
    P('| %s | %s | %s | %s |' % (lab, hc110.get(k, '-'), hb.get(k, '-'), lim))
P()
if HP:
    P('**Comb and receiver** (gate-model ledge 30 x 8 mm HDPE, load at the 26 mm rim; same formula as COMPARE; the lip section is an assumption, not a measurement):'); P()
    P('| case | force (N) | comb / receiver (mm) | coverage | line load (N/mm) | bearing (MPa) | ledge bending (MPa) |'); P('|---|---|---|---|---|---|---|')
    for k, v in HP['lip'].items(): P('| %s | %d | %d / %d | %d %% | %.2f | %.2f | %.1f |' % (k, v['F_N'], v['comb_mm'], v['receiver_mm'], v['coverage_pct'], v['line_load_N_per_mm'], v['bearing_MPa'], v['ledge_bending_MPa']))
    P(); la = HP['lift_actuator']; pt = HP['pad_toggle']; fr = HP['frame']
    P('- **Lift actuator:** peak %.0f N, static %s N on a 4 kN unit, margin %.2f peak / %.2f static. %s.' % (la['peak_N'], la['static_N'], la['margin_peak'], la['margin_static'], la['note']))
    P('- **Pad toggle:** worst actuator need %d N of 1,000 N (margin %.2f). Peak pad force on the locked stop in the carry runs: %.0f N, taken by the stop.' % (pt['need_worst_N'], pt['margin'], pt['locked_stop_peak_N']))
    P('- **Frame:** side rail %s. Load %d N per rail, M %d N m, sigma %.1f MPa static and %.1f MPa at x2.5 dynamic, against an allowable %d MPa. Mast upright sigma at x2.5: %.1f MPa.' % (fr['section'], fr['rail_load_N'], fr['M_static_Nm'], fr['sigma_static_MPa'], fr['sigma_dyn_x2p5_MPa'], fr['allow_MPa'], fr['mast_sigma_dyn_MPa']))
P()
# ------------------------------------------------------------------ 10 cost
P('# 10. Cost (b2/res/bom_b2.json, bom_b2_new.csv, bom_b2_donor.csv)'); P()
P('The BOM is re-based on revG/bom_revG8.json:'); P()
P('- Lean-N lines, minus the concept-B removals, plus the concept-B additions.')
P('- Plus the B1 iteration-1 lines.')
P('- Plus the B2 changes: pad DSZY4 out; TC24-50-1000, toggle, 640 mm comb and gap sensors in; folded tray package out, one-tube frame in.')
P('- Contingency follows the G8 rule.')
P()
P('| | parts | logistics | contingency | **all-in** | gap to EUR 2,000 | price-verified share of parts |'); P('|---|---|---|---|---|---|---|')
for lab, t in (('**B2, new drive** (PEWM82M + 3.5:1 chain)', bn), ('**B2, donor chair** (+ 2:1 chain, AGM reused)', bd)):
    P('| %s | %s | %s | %s | **%s** | +%s | %.0f %% |' % (lab, '{:,.0f}'.format(t['parts']), '{:,.0f}'.format(t['logistics']), '{:,.0f}'.format(t['contingency']), '{:,.0f}'.format(t['all_in']), '{:,.0f}'.format(t['gap_to_2000']), 100 * t['verified_share']))
P('| B1 (iteration 1, reference) | | | | %s | +%s | |' % ('{:,.0f}'.format(BOM['B1_ref']), '{:,.0f}'.format(BOM['B1_ref'] - 2000)))
P()
P('**Line status.** Every line in the CSVs is marked as verified (page fetched; G8 lines checked 6-11 Nov, the B2 lines fetched today) or estimated (estimate or search excerpt).'); P()
P('**B2 changes vs B1, all-in before contingency:**'); P()
P('- Pad actuator: -389.00 + 59.99 (Conrad, fetched) + 12 toggle parts')
P('- Frame: -602.78 + 60 (B frame net) + 354.12 (FAB-D8 method)')
P('- Comb: +45')
P('- Gap sensors: +12')
P()
P('**Why EUR 2,000 is not reachable.** The core is already about EUR 2,700 all-in before any sensor, comms, dock or light (G8 s.9): drive, frame, lift, safety stack, computer and wiring. Brian\'s rules allow no capability or safety cuts, so the honest gap stays at about EUR 2,000-2,300.'); P()
P('**Donor price risk.** The donor line uses the G8 excerpt price of EUR 400. Current Irish listings seen today run EUR 1,200-2,500 for working outdoor chairs (DoneDeal excerpts), and UK classifieds GBP 300-1,250. Above about EUR 630 for the chair, the donor variant is no cheaper than the new drive. Pull test T1-D before paying.'); P()
P('**Options not in the totals:**'); P()
P('- Generic 3 kN IP65 lift actuator, about -EUR 80-110 (excerpt), only if bench test T2 passes.')
P('- TC24-50-500P pad actuator (faster): rejected, it stalls on the SL 250.')
P('- Lane prep: 1:4 ramps at EUR 20-40 per surveyed step.')
P()
# ------------------------------------------------------------------ 11 risks + bench
P('# 11. Open risks and the bench tests still needed'); P()
P('| # | risk | severity | bench / field test |'); P('|---|---|---|---|')
for r in (('B1', 'Lift actuator cold force and holding (FDI 4 kN, no cold datasheet figure); step peaks reach the 3 kN model cap', 'high', 'T2: -20 C for 4 h, then a 3.1 kN lift on a lever rig; holding under 4 kN; current < 3 A; IP65 hose test'),
          ('B2', 'Pad toggle actuator TC24-50-1000: rated -15 C (TRU datasheet class), 7 mm/s, holding not published (the toggle lock makes holding irrelevant in the carry)', 'medium', 'Cold test at -15/-20 C: extension against 700 N at a 33 deg knee; 1,000 cycles; lock switch'),
          ('B3', 'Drive torque, heat and speed cap: PEWM82M at 24 A on a long 12 % climb; donor chair torque and gear ratio unknown', 'high', 'T1 drive dyno / drag test: 450 N drawbar, 0.5 m/s, 3 min, winding < 110 C; T1-D pull test on any donor before paying; free-speed check <= 1.0 m/s with the chain'),
          ('B4', 'Real bin receivers: geometry, rim height, ledge strength under an 8 mm nib on 640 mm, 250 mm-wheel bin lean', 'high', 'Measure Brian\'s bins (receiver width and depth, rim height, back-face profile at the pad height, standing tilt); scrap-bin proof load of 2.5 kN on a 640 mm comb'),
          ('B5', 'G3(b) full-width step needs lane ramps', 'high on lanes with such steps', 'Lane survey; ramp per step; route refuses unsurveyed steps'),
          ('B6', 'Lane margins below the localisation p95 at the tightest points (section 8)', 'medium', 'SITL re-run with the B2 guard/pivot rules; GNSS + lidar lateral error measured on the lane'),
          ('B7', 'Mass and CG are estimates (frame from sections; B1 mast was light); lift-off margin 1.5 deg', 'medium', 'Weigh the built frame and do a tilt-table test; adjust the ballast to keep >= 20 deg'),
          ('B8', 'Gap sensors (ToF) in rain and leaf litter, mounted low on the flares', 'low', 'Wet-weather test; the camera stays the primary sensor'),
          ('B9', 'Contact peaks are not time-step converged (review m6)', 'low-medium', 'x2.5 sizing factor kept'),
          ('B10', 'Donor chair price and availability (EUR 400 excerpt vs EUR 1,200+ listings)', 'cost only', 'Buy only after T1-D; otherwise the new drive'),
          ('B11', 'G3(b) hardware fix (lug tyre) unproven: passes the step in the sim but degrades docking (G1) on rigid sim lugs', 'option', 'T5: one pair of 13x5.00-6 lug wheels (about EUR 185); 20 docks + a 40 mm full-width kerb at 110 kg; adopt only if docking holds')):
    P('| %s |' % ' | '.join(r))
P()
# ------------------------------------------------------------------ 12 CAD
P('# 12. CAD and renders'); P()
P('The B2 CAD is CadQuery, built from the same numbers as b2/simB2.py and b2/mass_cgB2.json. The bin and carriage poses come from a B2 MuJoCo grab recording (`work/revB2/rec_B2.py`). Renders use the B1 software rasteriser (numba z-buffer, no OpenGL).'); P()
P('- STEP files: `BinRobo_B2_no_bin.step` and `BinRobo_B2_carrying_240L.step`.')
P('- Renders: `B2_render_1_front34.png`, `B2_render_2_carry_240L.png` and `B2_render_3_comb_closeup.png` (all in /workspace/work/out/revB2/).')
P('- Assumptions are listed in `assumptions_B2.md`.')
P()
for f, c in (('fig_b2_1_plan.png', 'Plan: B1 vs B2 footprints, bin and loaded pivot circle'), ('fig_b2_2_lane.png', 'Lane sweep: minimum clearance to the hedge face, B1 vs B2'), ('fig_b2_3_grab.png', 'G1 grab Monte Carlo per bin type')):
    P('![%s](%s){width=95%%}' % (c, f)); P()
for f, c in (('B2_render_1_front34.png', 'B2 front 3/4 view (design render)'), ('B2_render_2_carry_240L.png', 'B2 carrying a 240 L bin (pose from MuJoCo)'), ('B2_render_3_comb_closeup.png', 'B2 comb, keeper and toggle-locked pad (section)')):
    P('![%s](../../work/revB2/%s){width=95%%}' % (c, f)); P()
# ------------------------------------------------------------------ 13 files
P('# 13. Method and files'); P()
P('**Method.**'); P()
P('- One MuJoCo process at nice 10, through the queue (`cmp/queue_cmp.py b2/q_b2.txt`). After a sandbox stop the last 77 lines (lug SL set, gap-sensor stress, perturbations) were finished in the foreground by `b2/qchunk_b2.py` (same queue file and done list, per-run resume of grab sets), and the B1 lane fit under the B2 rules by `b2/lanefit_b2_ckpt.py` (same computation as `lanefit_b2.py`, cached piece by piece).')
P('- Frozen common model terms unchanged: dt 0.5 ms (0.25 ms for G7), 60 N m drive cap, 330 mm wheels and 200 mm castors in every gate run, camera sigma 8 mm with one re-dock. Seeds are as B1.')
P('- B2 design parameters were calibrated before the suite with smokes labelled calibration (`b2/smoke*.log`).')
P('- The lane fit is kinematic: `cmp/lanefit.py`, imported unchanged, plus the B2 rules in `b2/lanefit_b2.py`.')
P()
P('**Files.** All under revG/sim/cg/b2/ unless noted.'); P()
P('- Sim and runner: `simB2.py`, `runB2.py`.')
P('- Mass and hand calcs: `make_mass_b2.py`, `mass_cgB2*.json`, `handcalc_b2*.py`.')
P('- Queue: `mk_queue_b2.py`, `q_b2.txt` and its log, `qchunk_b2.py`.')
P('- Results: `res/B2_*.json`, scorecard `res/gate_B2_.json`.')
P('- Lane fit: `lanefit_b2.py`, `lanefit_b2_ckpt.py`, `design_B2.json`, `design_B1_srun.json`, `res/lanefit_B2.json`, `res/lanefit_B1_srun.json`.')
P('- BOM: `bom_b2.py`, `res/bom_b2*.{json,csv}`.')
P('- Figures and report: `figs_b2.py`, `build_report_b2.py`.')
P('- Diagnostics: `dbg_pad.py`, `dbg_grab.py`, `dbg_padforce.py`.')
P('- CAD and renders: `work/revB2/` (`cad_B2.py`, `stills_B2.py`, `scene.py`, `raster.py`, `rec_B2.*`).')
P('- Progress log: `docs/reviews/PROGRESS_B2.md`.')
P()
txt = '\n'.join(out)
bad = [c for c in txt if ord(c) > 126]
if bad: print('NON-ASCII', set(bad)); txt = txt.encode('ascii', 'replace').decode()
open(DOC, 'w').write(txt); print('wrote', DOC, len(txt))
