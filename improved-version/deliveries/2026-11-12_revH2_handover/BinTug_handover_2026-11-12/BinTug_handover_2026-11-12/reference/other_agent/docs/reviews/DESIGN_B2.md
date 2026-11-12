---
title: "BinRobo B2: B1 combined with what Rev H does better"
subtitle: "Design, frozen-gate proof, lane fit, CAD and costed BOM. Criteria frozen 11 Nov 2026 07:51 +03, unchanged (sha256 2cf3f4ec...8a74 before and after)."
author: "Prepared with Hark for Brian"
date: "11 November 2026"
geometry: margin=1.6cm
fontsize: 9pt
colorlinks: true
---

# 1. Result

**B2 passes 8 of 9 frozen gate items, the same count as B1 and one more than Rev H with its two firmware fixes. The only failure is again G3(b), the full-width sharp 40 mm step.** No cheap hardware change passed it (section 7), so the 1:4 kerb ramps stay as a lane-prep item. The criteria file was not touched and no threshold was loosened.

What B2 changes against B1, in one line each:

- **Comb:** 640 mm self-aligning comb (yaw +/-4 deg, roll +/-3 deg) on the full EN 840 receiver. G1 89/90 pooled, 0 false holds, 0 knocked; extra bins: SL 250 30/30, ESE 140 CL 28/30.
- **Pad:** the EUR 389 MSW DSZY4 is gone. A knee toggle driven 10 mm over centre onto a hard stop now holds the pad, moved by a TRU TC24-50-1000 (EUR 59.99, 155 mm long, upright on the pad arm). The stop carries the bin, not the actuator; the packaging clash is gone. New firmware step F10: the lift pauses at load-on while the pad locks.
- **Frame:** Rev H style, one tube size (50x50x2 RHS) bolted through about 16 laser plates, built by Brian; the folded tray package is deleted (EUR 603 -> EUR 354).
- **Mass:** 92.3 kg (B1 94.1 kg + 1.6 kg comb = 95.7 kg). The 85-90 kg target was not reached honestly: the frame saves about 4.5 kg, but castor lift-off needs 5 kg of ballast at the nose to stay above 20 deg (21.5 deg).
- **Width and turning:** 0.93 m wide (B1 0.97), chamfered nose, castor swivel circles instead of boxes: empty pivot diameter 2.28 m (B1 2.36), loaded 2.39 m.
- **Lane rules:** keep the B1 centre line, keep 0.40 m (was 0.25 m) from the mapped hedge face, and run on 0.3-3 m with an S-shift before every empty pivot after a drop. B1 run under the same rules scores the same (0.326 m sweep, 0.104 m worst sequence; B2 0.325 / 0.104 m): the lane gain comes from the rules, not from the narrower body.
- **Cost:** EUR 4,260 all-in with the new drive, EUR 3,992 on a donor chair (B1 EUR 4,743). That is EUR 2,260 / EUR 1,992 over the EUR 2,000 target, which is not reachable.

# 2. B2 specification and changes from B1

| item | B2 | B1 | why |
|---|---|---|---|
| Overall | nose (bumper) x +1.09 m, tail -0.40 m (rear bumpers); width 0.93 m over the chain cases; nose corners chamfered 45 deg to y +/-0.33 m | nose +1.09, tail -0.37; 0.97 m over the gearmotors | lane margins |
| Frame | one tube size 50x50x2 S235: 2 side rails over the drive tyres (y +/-0.43, z 0.36-0.41), nose and mast-base cross-members, 2 mast uprights, top tie; bolted through ~16 laser plates; HDPE bay floor/covers | folded 2 mm steel tray, 80x40 side arms, 40x40 mast | Rev H simplification; cheaper, Brian can build it |
| Drive | 2 x 330 mm, track 0.80 m; PEWM82M-320W + 3.5:1 chain (new) or donor chair + 2:1 chain (donor variant) | same (new only) | two costed variants |
| Castors | 2 x 200 mm at x 0.95, y +/-0.28 | same | G3 sensitivity: 250 mm did not help |
| Comb | 640 x 130 x 6 mm self-aligning plate (yaw +/-4, roll +/-3 deg, centring springs), 8 x 20 mm nib along the full width, 2 ToFs, seat + contact switches | 160 mm tooth | covers the EN 840 receiver; rigid 640 fails G1 (86/90) |
| Lift | 2 x HGR15 rails, carriage nib top 0.855-1.105 m (250 mm); QC FDI 24 V 4 kN IP65 400 mm unit | same | step peaks still reach the 3 kN model cap (section 4, item 2) |
| Pad | on the carriage 0.58 m below the nib top, 300 x 100 UHMW, die springs 30 kN/m, 300 N preload; 40 mm retract by a knee toggle (2 x 60 mm links) locked 10 mm over centre on a hard stop; TRU TC24-50-1000 (1 kN, 7 mm/s, IP65) upright on the pad arm | MSW DSZY4 2.5 kN in line (did not fit) | cost, packaging, load path |
| Sensing added | 2 leg-tip gap ToFs on the flare tips (lateral offset in the last 0.5 m) | - | Rev H idea; cheap docking cross-check |
| Anti-tip | rollers at x -0.33, y +/-0.42 | y +/-0.44 | width |
| Ballast | 5 kg steel plate on the bay floor at x 1.00 | 10 kg at x 0.85 | castor lift-off >= 20 deg |
| Battery | 24 V 20 Ah LiFePO4 in the front bay (x 0.90); donor variant: donor AGM pair 22 kg, no ballast | x 0.80 | free ballast forward |
| Mass | 92.3 kg new drive / 105.5 kg donor (limit 120) | 94.1 kg (+1.6 comb) |  |
| Firmware | B1 F1-F9 unchanged; F10: lift paused at load-on, pad toggle locks (switch, <= 12 s), then +100 mm; keeper only after the pad lock; pad lock switch is part of the claim | F7: pad extended during the lift | small actuator never pushes the hanging moment |

Firmware F10 came from three calibration smokes (labelled calibration, not gate results; `b2/smoke*.log`):

- Pad extending during the +100 mm lift at the real actuator speed: the full bins are already hanging on the retracted pad, and the toggle stalls at its widest angle.
- Pad extended before the lift (bin standing): pad friction plus the bin rocking onto the nib fakes a rim-catch, so the lift aborts (Weber 140 full).
- **Adopted:** pad extended at load-on with the lift held (0 N on the pad at that moment, worst 724 N at the lock). With the 500 N TC24-50-500P the leaning 250 mm-wheel bin stalled the toggle (it needs 683 N with 60 mm links), so the 1,000 N TC24-50-1000 was chosen: margin 1.46.
- The B1 model held the extended pad with a soft position servo at the joint limit. B2 drives the toggle 10 mm past centre onto the stop, so the stop takes the load.

# 3. What was taken from each design, and what was rejected

**Kept from B1 (the base):** the comb-on-receiver principle (lift by the handle-side EN 840 receiver, not the front wall), the straddle with the bin wheels on the drive axle, the lift carriage and keeper, the sprung pad on the carriage, every interlock and the F1-F9 approach firmware, the 330 mm drive and 200 mm castors, and all the G8 safety, navigation, comms and dock lines.

**Taken from Rev H, and why:**

- One tube size and a small plate set (frame cost EUR 603 -> 354, Brian-buildable, fewer DXFs).
- Leg-tip gap sensors (EUR 12): an independent lateral reference in the last 0.5 m of the approach (section 6.3).
- The donor-chair drive, as a costed variant only, with a 2:1 chain stage added so the inherent speed cap is not lost.
- Full-width comb coverage, which Rev H argued for. It was proven on B1 and adopted in its self-aligning form.

**Rejected from Rev H, and why:**

- Lifting by the bin front wall: that wall is not the load-rated receiver (COMPARE s.3). Rev H raw scored 2/9 with 29 false holds on the ESE 240 SL.
- The fixed pad: bins hang 11-12 deg and the 250 mm-wheel bin cannot be lifted clear (COMPARE).
- Reduced-order dynamics as evidence: everything here is the project MuJoCo model.
- 260 mm nose castors: the G3 sensitivity shows castor size does not change the full-width step.
- AGM batteries on the new-drive variant: LiFePO4 is lighter, and the 5 kg ballast is cheaper than the extra AGM mass.

**Rejected within B2, with evidence:**

- A smaller lift actuator (section 4, item 2).
- A passive cam pad driven by carriage travel: the pick-up height varies 0.05-0.17 m between bins, so an absolute cam cannot tell a carried CL bin from an SL 250 being picked up.
- The 500 N pad actuator: it stalls on the SL 250.
- 250 mm castors, lug tyres and a CG shift for G3(b) (section 7).

# 4. Candidate log (each kept only if it holds or improves the gate)

| # | candidate | decision | evidence |
|---|---|---|---|
| 1 | 640 mm self-aligning comb | ADOPTED | B2 G1 pooled 89/90; G6 18/18; extra SL 250 30/30, FH 0, knocked 0, ESE 140 CL 28/30, FH 0, knocked 0. B1+640 had scored 89/90 in COMPARE |
| 2 | smaller / cheaper lift actuator (the comb peak dropped to 1,952 N) | REJECTED | B2 lift peak 2558 N on the one-side step and 3000 N on the full-width step (= the 3 kN model cap); static carry 1150 N. The 1,952 N in COMPARE did not include the step runs. Kept the QC FDI 4 kN IP65 (EUR 137.10 fetched + EUR 25 fittings). Cheaper generic 3 kN IP65 units exist (excerpts, about EUR 50); they are an option only after the T2 cold-force and holding test |
| 3 | pad mechanism (DSZY4: EUR 389, 230 mm vs 140 mm space, 7-9 s) | ADOPTED: knee toggle locked over centre + TC24-50-1000 | Fits upright on the pad arm (155 mm installed). Load path through the stop. Worst actuator need 680 N of 1,000 N (SL 250 full). EUR 59.99 + EUR 12 parts. **Speed not improved:** about 7.7 s per move (7 mm/s); the 16 mm/s 500 N unit stalls on the SL 250. Passive cam rejected (see s.3) |
| 4 | Rev H frame (one tube size, ~14-16 plates), mass to 85-90 kg | ADOPTED (frame); mass target NOT met | 50x50x2 frame saves ~4.5 kg vs B1 tray+arms but B1's 4 kg mast was under-estimated; bare B2 87.3 kg gives castor lift-off 19.1 deg (< 20), so 5 kg ballast at x 1.00 -> 21.5 deg at 92.3 kg. Hand-calc min tip 37.1 deg; G8 castors >= 273.5 N |
| 5 | leg-tip gap sensors | ADOPTED (EUR 12) | Camera stress 16 mm sigma: ESE 240 SL 20/20, FH 0, knocked 0 without, 20/20, FH 0, knocked 0 with; ESE 240 CL 17/20, FH 1, knocked 0 without, 19/20, FH 0, knocked 0 with (section 6.3). Gate runs use the frozen camera model only (sensors not credited) |
| 6 | drive: new PEWM82M + chain vs donor chair | BOTH COSTED; new drive is the reference | New EUR 4,260, donor EUR 3,992 all-in. Donor carry tests on 318 mm wheels: section 6.4. Donor keeps the speed-cap layer only with an added 2:1 chain (EUR 90 est.) |
| 7 | full-width 40 mm step without ramps | NO CHEAP PASS THAT HOLDS THE GATE; ramps stay | 250 mm castors FAIL (1.34 m, lift peak 1979 N); 20 kg at the nose FAIL (1.34 m, lift peak 3000 N). A bar-tread lug tyre DOES climb it (PASS (4.71 m, lift peak 2116 N); lugs + nose ballast PASS (4.71 m, lift peak 3000 N)) but fails G1 on the same model (round 3: Weber 140 26/30, FH 0, knocked 1; ESE 240 SL 22/30, FH 2, knocked 0): adopting it would trade G1 for G3(b), so it was rejected |
| 8 | lane-fit width + pivot strategy | ADOPTED (rules); width alone gives no lane gain | B1 with the B2 rules 0.326 / 0.104; B2 0.325 / 0.104 (sweep min / worst sequence margin, m). Section 8 |

**Rounds (3 allowed, 3 used):**

- **Round 1, calibration smokes (not gate evidence).**
    - Pad sequencing: firmware F10.
    - Pad actuator: the 500 N unit stalls, so it became the 1,000 N unit.
    - Ballast for castor lift-off.
    - Lane-fit sign bug, fixed.
- **Round 2, the full frozen suite plus extras, donor and step sensitivities on B2:** 8/9.
- **Round 3, the frozen suite with lug tyres (the only G3(b) candidate that climbed):** stopped after G1 failed (Weber 140 26/30, FH 0, knocked 1; ESE 240 SL 22/30, FH 2, knocked 0, both sets complete). B2 final is the round-2 design.
- **After round 3, on the round-2 design (reported, not a new round):** the 72 perturbation runs (section 6.1), the gap-sensor stress test (section 6.3) and the B1 lane fit under the B2 rules (section 8).

Pad-actuator speed is the one item the brief asked to fix that B2 does not fix: it trades the speed for cost, packaging and a locked load path. A pick-up takes about 50 s and a set-down about 25 s in the sim (B1 about 45 s / 20 s).

# 5. Scorecard: B2 vs B1 vs Rev H fixed (frozen gate, CRITERIA_FROZEN.md unchanged)

| item | Rev H + FH1 + FH2 | B1 final (160 mm comb) | B1 + 640 mm comb | **B2** |
|---|---|---|---|---|
| G1 | **PASS**: WEB 30/30 / SL 29/30 / CL 29/30; pooled 88/90; FH 0; knocked 0 | **PASS**: WEB 30/30 / SL 30/30 / CL 30/30; pooled 90/90; FH 0; knocked 0 | **PASS**: WEB 29/30 / SL 30/30 / CL 30/30; pooled 89/90; FH 0; knocked 0 | **PASS**: WEB 30/30 / SL 30/30 / CL 29/30; pooled 89/90; FH 0; knocked 0 |
| G2 | **PASS**: 6/6; 11.0-11.0 s; creep <= 0.043 m | **PASS**: 6/6; 11.1-11.1 s; creep <= 0.035 m | **PASS**: 6/6; 11.1-11.1 s; creep <= 0.035 m | **PASS**: 6/6; 11.0-11.1 s; creep <= 0.038 m |
| G3 | **FAIL**: one side PASS (4.69 m, clear 47 mm); full width FAIL (1.34 m, grab success, bin-ground 0 N, seated True) | **FAIL**: one side PASS (4.69 m, clear 88 mm); full width FAIL (1.34 m, grab success, bin-ground 0 N, seated True) | **FAIL**: one side PASS (4.69 m, clear 83 mm); full width FAIL (1.34 m, grab success, bin-ground 0 N, seated True) | **FAIL**: one side PASS (4.68 m, clear 83 mm); full width FAIL (1.34 m, grab success, bin-ground 0 N, seated True) |
| G4 | **PASS**: fwd PASS 0.20 m, slide 0.001 / rev PASS 0.09 m, slide 0.001 | **PASS**: fwd PASS 0.16 m, slide 0.001 / rev PASS 0.08 m, slide 0.001 | **PASS**: fwd PASS 0.15 m, slide 0.001 / rev PASS 0.08 m, slide 0.001 | **PASS**: fwd PASS 0.15 m, slide 0.001 / rev PASS 0.08 m, slide 0.001 |
| G5 | **PASS**: PASS; roll 0.01 deg; pivot swept 2.10 m | **PASS**: PASS; roll 0.00 deg; pivot swept 2.42 m | **PASS**: PASS; roll 0.00 deg; pivot swept 2.42 m | **PASS**: PASS; roll 0.00 deg; pivot swept 2.39 m |
| G6 | **FAIL**: 15/18, 0 TIPS; SL250 flat full FAIL, SL250 up12 full FAIL, SL250 dn12 full FAIL | **PASS**: 18/18, 0 TIPS | **PASS**: 18/18, 0 TIPS | **PASS**: 18/18, 0 TIPS |
| G7 | **PASS**: climb_m25_c09 base True / dt025 True t 11.0/11.0 s; step40_one base True / dt025 True; estop12_fwd base True / dt025 True | **PASS**: climb_m25_c09 base True / dt025 True t 11.1/11.0 s; step40_one base True / dt025 True; estop12_fwd base True / dt025 True | **PASS**: climb_m25_c09 base True / dt025 True t 11.1/11.0 s; step40_one base True / dt025 True; estop12_fwd base True / dt025 True | **PASS**: climb_m25_c09 base True / dt025 True t 11.0/11.0 s; step40_one base True / dt025 True; estop12_fwd base True / dt025 True |
| G8 | **PASS**: 8/8 poses; drive >= 454 N, castors >= 268 N; hand-calc min tip 40.9 deg | **PASS**: 8/8 poses; drive >= 460 N, castors >= 294 N; hand-calc min tip 39.4 deg | **PASS**: 8/8 poses; drive >= 460 N, castors >= 294 N; hand-calc min tip 39.4 deg | **PASS**: 8/8 poses; drive >= 445 N, castors >= 274 N; hand-calc min tip 37.1 deg |
| G9 | **PASS**: 85.5 kg | **PASS**: 94.1 kg | **PASS**: 94.1 kg | **PASS**: 92.3 kg |
| **passed** | **7/9** | **8/9** | **8/9** | **8/9** |

Notes:

- Rev H + FH1 + FH2 is conditional on a load-rated front-wall lip that the bins do not have (COMPARE s.3).
- In the B1 + 640 mm column, some carry items were inherited from B1 (COMPARE gate_fw_provenance). Every B2 item was run on B2.
- B2 G9 includes 5 kg of ballast. G3(b) with a 1:4 ramp: PASS (4.71 m, lift peak 1185 N).

# 6. Perturbations, extras and variants (reported, not gating)

## 6.1 Perturbations (reduced suite, as B1 s.7)

| perturbation | G1 (10 per bin: WEB / SL / CL) | G2 mu 0.22 crr 0.09 / mu 0.25 crr 0.06 | G3 one side | G4 fwd / rev | G5 | G6 six hardest | G8 three poses |
|---|---|---|---|---|---|---|---|
| mass +10 % | 10/10 / 10/10 / 10/10; FH+knocked 0 | PASS (11.1 s, creep 0.035 m) / PASS (11.1 s, creep 0.033 m) | PASS (4.68 m, lift peak 2431 N) | PASS (stop 0.155 m, slide 0.001 m) / PASS (stop 0.080 m, slide 0.001 m) | PASS (swept 2.40 m) | 6/6 | 3/3 |
| mass -10 % | 10/10 / 10/10 / 10/10; FH+knocked 0 | PASS (11.0 s, creep 0.035 m) / PASS (11.0 s, creep 0.035 m) | PASS (4.69 m, lift peak 3000 N) | PASS (stop 0.147 m, slide 0.001 m) / PASS (stop 0.079 m, slide 0.001 m) | PASS (swept 2.37 m) | 6/6 | 3/3 |
| friction -15 % | 10/10 / 10/10 / 10/10; FH+knocked 0 | PASS (11.6 s, creep 0.033 m) / PASS (11.1 s, creep 0.037 m) | PASS (4.69 m, lift peak 1948 N) | PASS (stop 0.218 m, slide 0.001 m) / PASS (stop 0.114 m, slide 0.001 m) | PASS (swept 2.37 m) | 6/6 | 3/3 |
| bin crr 0.09 | 10/10 / 10/10 / 10/10; FH+knocked 0 | PASS (11.1 s, creep 0.038 m) / PASS (11.0 s, creep 0.033 m) | PASS (4.68 m, lift peak 2558 N) | PASS (stop 0.152 m, slide 0.001 m) / PASS (stop 0.079 m, slide 0.001 m) | PASS (swept 2.39 m) | 6/6 | 3/3 |

All four perturbation sets pass every item run. With mass -10 % the one-side step lift peak reaches the 3,000 N model cap (as the nominal full-width step does), which supports keeping the 4 kN lift actuator. Friction -15 % lengthens the forward e-stop to 0.218 m (limit 0.5 m). The bin crr 0.09 set gives carry results identical to nominal: the setting reaches the model (bin-wheel friction loss 0.318 -> 0.477), but in every carry test the bin is lifted off its wheels, so bin rolling resistance only acts in docking and set-down (G1 and G6, both PASS).

## 6.2 Extra bins (the 250 mm-wheel and ESE 140 CL bins)

- ESE 240 SL with 250 mm wheels (seed 204): 30/30, FH 0, knocked 0. ESE 140 CL (seed 205): 28/30, FH 0, knocked 0.
- G6 on the SL 250 (part of the frozen G6): all six cases PASS, standing tilt 3.8 deg, its own lean.

## 6.3 Leg-tip gap sensors (camera stress test)

The camera lateral sigma is doubled to 16 mm (seeds 212/213, 20 runs each). Once the bin is inside the flares, the gap sensors replace the camera lateral estimate with 3 mm sigma.

| bin | camera 16 mm only | + leg-tip gap sensors |
|---|---|---|
| ESE240SL | 20/20, FH 0, knocked 0 | 20/20, FH 0, knocked 0 |
| ESE240CL | 17/20, FH 1, knocked 0 | 19/20, FH 0, knocked 0 |

The ESE 240 SL is not sensitive to the doubled camera noise. On the ESE 240 CL the sensors turn 17/20 with one false hold into 19/20 with none. This is one seed per bin and 20 runs each, so it supports the EUR 12 adoption but does not prove a rate; the frozen gate does not credit the sensors.

## 6.4 Donor-drive variant (318 mm chair wheels, AGM forward, 105.5 kg)

The torque cap stays the frozen 60 N m; with the 2:1 chain stage the real donor torque is higher. Results:

| test | result |
|---|---|
| G2 mu 0.30 crr 0.06 | PASS (11.0 s, creep 0.035 m) |
| G2 mu 0.30 crr 0.09 | PASS (11.0 s, creep 0.035 m) |
| G2 mu 0.25 crr 0.06 | PASS (11.0 s, creep 0.036 m) |
| G2 mu 0.25 crr 0.09 | PASS (11.0 s, creep 0.036 m) |
| G2 mu 0.22 crr 0.06 | PASS (11.2 s, creep 0.036 m) |
| G2 mu 0.22 crr 0.09 | PASS (11.2 s, creep 0.036 m) |
| G3 one side | PASS (4.68 m, lift peak 3000 N) |
| G3 full width | FAIL (1.34 m, lift peak 2777 N) |
| G3 full width, 1:4 ramp | PASS (4.71 m, lift peak 1187 N) |
| G4 fwd | PASS (stop 0.166 m, slide 0.001 m) |
| G4 rev | PASS (stop 0.087 m, slide 0.001 m) |
| G5 | PASS (swept 2.40 m) |
| G8 up 110 | PASS (drive 866/878 N, castors 363 N) |
| G8 dn 60 | PASS (drive 500/531 N, castors 590 N) |
| G8 cross L 110 | PASS (drive 668/949 N, castors 490 N) |
| G8 cross R 110 | PASS (drive 943/693 N, castors 474 N) |
| G1 ESE 240 SL (10 runs) | 10/10, FH 0, knocked 0 |

Hand calc donor (110 kg bin): castor lift-off 25.4 deg, mu_req on 12 % 0.217, torque 24.9 N m per wheel (x1.25 31.1).

**Speed-cap point.** A chair geared for about 1.7 m/s loses the inherent gearing layer of the G8 speed limit (G8 s.3 layer a). In B2 the donor variant puts a 2:1 chain stage on each chair gearbox (about 0.83 m/s free), which restores that layer. The variant is only acceptable with this stage; without it, it would be a safety cut.

# 7. The full-width 40 mm step G3(b)

**Hand calc.** For a driven wheel at a 40 mm edge with free castors, quasi-statically:

- The edge friction needed is mu = tan(a) = **0.86** for a 330 mm wheel (contact angle 40.7 deg). This is geometric: it does not depend on load or CG.
- The torque needed is W r sin(a) = **84 N m** per wheel at 780 N wheel load.
- Against that, the test friction is 0.6, the frozen cap is 60 N m and the real PEWM82M + 3.5:1 gives 53 N m at 25.8 A.
- Bigger wheels lower the friction need but raise the torque need:
    - 400 mm: mu 0.75, 94 N m
    - 560 mm: mu 0.60, 112 N m
    - 700 mm: mu 0.52, 127 N m
- A lug or grouser tyre removes the friction limit, but not the torque limit. Keeping 60 N m would need the wheel load below 557 N, so 55 % of the weight would have to sit on the castors, which breaks G2 traction.

| cheap change (sim, full-width step, otherwise B2) | result |
|---|---|
| B2 as designed | FAIL (1.34 m, lift peak 3000 N) |
| 250 mm castors | FAIL (1.34 m, lift peak 1979 N) |
| 330 mm OD bar-tread tyre, 18 lugs 12 mm deep | PASS (4.71 m, lift peak 2116 N) |
| 20 kg ballast at the nose (CG forward) | FAIL (1.34 m, lift peak 3000 N) |
| lugs + 20 kg at the nose | PASS (4.71 m, lift peak 3000 N) |
| 1:4 kerb ramp (lane prep) | PASS (4.71 m, lift peak 1185 N) |

**The lug tyre: round 3.** The lugs interlock with the edge, so the climb no longer depends on friction. Momentum at 0.5 m/s covers the torque shortfall that the quasi-static hand calc predicts. It passes in the sim, so round 3 re-ran the frozen suite with lug tyres.

G1 failed:

- Weber 140: 26/30, FH 0, knocked 1.
- ESE 240 SL: 22/30, FH 2, knocked 0.
- Cause: approach heading and lateral control degrade on the rigid lugs. Docking was off by 50 mm and by -300 to -400 mm, and one re-approach was 33 deg off.

A real rubber lug is compliant and may behave better, but that is a hope, not evidence, so lugs were rejected. A cheap lug wheel exists: Wanda P328 13x5.00-6 open-centre, OD 320 mm, GBP 79.50 each at Parnells/B&Q, page fetched; +EUR 180 all-in. Worth one field test: dock 20 times on lug tyres, and climb a real 40 mm kerb at 110 kg (bench test T5).

A brief pad-assisted lift is not possible. The comb only hooks upward under the receiver and the keeper is a light finger, so the robot cannot push down on the bin to unload its drive wheels.

**Decision:** the 1:4 ramps stay as a lane-prep item (EUR 20-40 per surveyed step, not in the BOM), and the route refuses unsurveyed full-width steps over 25 mm. G3 stays FAIL as frozen. The two hardware routes are lug tyres, if a field test shows docking holds, and 4WD (about EUR 300-450, not simulated).

# 8. Lane fit (cmp/lanefit.py unchanged; b2/lanefit_b2.py adds the B2 rules; hedge contact = FAIL)

| design / rules | pivot dia. empty / loaded (m) | min hedge clearance, lane sweep (m) | vs p95 estimate error 0.124 m | min margin, all 12 pad sequences (m) | worst empty pivot after a drop (m) | sequences |
|---|---|---|---|---|---|---|
| Rev H (COMPARE) | 2.16 / 2.16 | 0.180 (s 417.1) | +0.056 | 0.007 | 0.007 | all PASS |
| B1 (COMPARE, SITL rules) | 2.36 / 2.42 | 0.179 (s 417.0) | +0.055 | 0.047 | 0.047 | all PASS |
| B1 with the B2 rules | 2.36 / 2.42 | 0.326 (s 417.0) | +0.202 | 0.104 | 0.104 | all PASS |
| **B2 with the B2 rules** | 2.28 / 2.39 | 0.325 (s 417.0) | +0.201 | 0.104 | 0.104 | all PASS |

The B2 lane rules:

- **Width:** 0.93 m, keeping the B1 centre line, so there is 0.02 m more on each side.
- **Corridor guard:** 0.40 m from the mapped hedge face, up from the SITL 0.25 m. The narrowing at s 500-516 is still centred.
- **Empty pivots after a drop:** run on 0.3-3.0 m with an S-shift of up to 0.6 x the run before the 180 deg pivot.
- **Smaller swept circle:** chamfered nose and true castor swivel circles.

**B1 under the B2 rules** (`design_B1_srun.json`: same guard, keep-left gap and S-run pivots, B1 footprint): sweep min 0.326 m and worst sequence margin 0.104 m, against B2 0.325 / 0.104 m. The two are equal at the binding points (s 417 lane sweep; the empty pivot after a handle-to-road drop, limited by the placed bin and the road boundary). So the lane-fit gain over B1 as run in COMPARE (0.179 / 0.047 m) comes from the route rules, which B1 could adopt too; the 0.04 m narrower body and the smaller pivot circle add no measurable lane margin.

No footprint point crosses a truth hedge face anywhere (strict scoring). The worst sequence margin (0.104 m) is below the 0.124 m p95 localisation error and stays flagged in section 11 (risk B6). These rules are a SITL change: route planner guard and pivot planner.

# 9. Hand calcs

| quantity | B2 (110 kg bin) | B1 | limit / note |
|---|---|---|---|
| castor lift-off about the drive axle (deg) | 21.5 | 23.2 | >= 20 (Brian) |
| lateral tip (deg) | 37.1 | 39.4 | >= 20 (G8) |
| forward tip over castors (deg) | 55.3 | 57.4 | >= 20 |
| rear tip onto anti-tip rollers (deg) | 48.5 | 50.8 | >= 20 |
| mu_req on 12 % (traction) | 0.209 | 0.207 | <= 0.22 (G2 lowest mu) |
| torque per wheel on 12 % (N m) | 24.5 | 24.6 |  |
| torque x1.25 (N m) | 30.6 | 30.8 | PEWM82M+3.5:1: 34.8 @ 17 A |
| castor load, 12 % facing up (N) | 552 | - | > 0 |
| CG height loaded (m) | 0.49 | 0.451 |  |

**Comb and receiver** (gate-model ledge 30 x 8 mm HDPE, load at the 26 mm rim; same formula as COMPARE; the lip section is an assumption, not a measurement):

| case | force (N) | comb / receiver (mm) | coverage | line load (N/mm) | bearing (MPa) | ledge bending (MPa) |
|---|---|---|---|---|---|---|
| B2 640 mm comb, ESE 240 SL full, static carry (lift force on 12 % static poses) | 1150 | 640 / 580 | 100 % | 1.98 | 0.25 | 4.8 |
| B2 640 mm comb, peak nib/rim force over the nominal carry runs | 2881 | 640 / 580 | 100 % | 4.97 | 0.62 | 12.1 |
| B1 160 mm comb, peak 3838 N (COMPARE s.9) - reference | 3838 | 160 / 580 | 28 % | 23.99 | 3.00 | 58.5 |

- **Lift actuator:** peak 3000 N, static 1150 N on a 4 kN unit, margin 1.33 peak / 3.48 static. sim actuator force cap 3,000 N (as B1); generic 3 kN option would give 1.00 x on the peak.
- **Pad toggle:** worst actuator need 680 N of 1,000 N (margin 1.47). Peak pad force on the locked stop in the carry runs: 1096 N, taken by the stop.
- **Frame:** side rail 50x50x2 RHS S235, I 147712 mm4, Z 5908 mm3. Load 869 N per rail, M 206 N m, sigma 34.9 MPa static and 87.3 MPa at x2.5 dynamic, against an allowable 157 MPa. Mast upright sigma at x2.5: 49.9 MPa.

# 10. Cost (b2/res/bom_b2.json, bom_b2_new.csv, bom_b2_donor.csv)

The BOM is re-based on revG/bom_revG8.json:

- Lean-N lines, minus the concept-B removals, plus the concept-B additions.
- Plus the B1 iteration-1 lines.
- Plus the B2 changes: pad DSZY4 out; TC24-50-1000, toggle, 640 mm comb and gap sensors in; folded tray package out, one-tube frame in.
- Contingency follows the G8 rule.

| | parts | logistics | contingency | **all-in** | gap to EUR 2,000 | price-verified share of parts |
|---|---|---|---|---|---|---|
| **B2, new drive** (PEWM82M + 3.5:1 chain) | 3,558 | 332 | 369 | **4,260** | +2,260 | 39 % |
| **B2, donor chair** (+ 2:1 chain, AGM reused) | 3,350 | 255 | 386 | **3,992** | +1,992 | 27 % |
| B1 (iteration 1, reference) | | | | 4,743 | +2,743 | |

**Line status.** Every line in the CSVs is marked as verified (page fetched; G8 lines checked 6-11 Nov, the B2 lines fetched today) or estimated (estimate or search excerpt).

**B2 changes vs B1, all-in before contingency:**

- Pad actuator: -389.00 + 59.99 (Conrad, fetched) + 12 toggle parts
- Frame: -602.78 + 60 (B frame net) + 354.12 (FAB-D8 method)
- Comb: +45
- Gap sensors: +12

**Why EUR 2,000 is not reachable.** The core is already about EUR 2,700 all-in before any sensor, comms, dock or light (G8 s.9): drive, frame, lift, safety stack, computer and wiring. Brian's rules allow no capability or safety cuts, so the honest gap stays at about EUR 2,000-2,300.

**Donor price risk.** The donor line uses the G8 excerpt price of EUR 400. Current Irish listings seen today run EUR 1,200-2,500 for working outdoor chairs (DoneDeal excerpts), and UK classifieds GBP 300-1,250. Above about EUR 630 for the chair, the donor variant is no cheaper than the new drive. Pull test T1-D before paying.

**Options not in the totals:**

- Generic 3 kN IP65 lift actuator, about -EUR 80-110 (excerpt), only if bench test T2 passes.
- TC24-50-500P pad actuator (faster): rejected, it stalls on the SL 250.
- Lane prep: 1:4 ramps at EUR 20-40 per surveyed step.

# 11. Open risks and the bench tests still needed

| # | risk | severity | bench / field test |
|---|---|---|---|
| B1 | Lift actuator cold force and holding (FDI 4 kN, no cold datasheet figure); step peaks reach the 3 kN model cap | high | T2: -20 C for 4 h, then a 3.1 kN lift on a lever rig; holding under 4 kN; current < 3 A; IP65 hose test |
| B2 | Pad toggle actuator TC24-50-1000: rated -15 C (TRU datasheet class), 7 mm/s, holding not published (the toggle lock makes holding irrelevant in the carry) | medium | Cold test at -15/-20 C: extension against 700 N at a 33 deg knee; 1,000 cycles; lock switch |
| B3 | Drive torque, heat and speed cap: PEWM82M at 24 A on a long 12 % climb; donor chair torque and gear ratio unknown | high | T1 drive dyno / drag test: 450 N drawbar, 0.5 m/s, 3 min, winding < 110 C; T1-D pull test on any donor before paying; free-speed check <= 1.0 m/s with the chain |
| B4 | Real bin receivers: geometry, rim height, ledge strength under an 8 mm nib on 640 mm, 250 mm-wheel bin lean | high | Measure Brian's bins (receiver width and depth, rim height, back-face profile at the pad height, standing tilt); scrap-bin proof load of 2.5 kN on a 640 mm comb |
| B5 | G3(b) full-width step needs lane ramps | high on lanes with such steps | Lane survey; ramp per step; route refuses unsurveyed steps |
| B6 | Lane margins below the localisation p95 at the tightest points (section 8) | medium | SITL re-run with the B2 guard/pivot rules; GNSS + lidar lateral error measured on the lane |
| B7 | Mass and CG are estimates (frame from sections; B1 mast was light); lift-off margin 1.5 deg | medium | Weigh the built frame and do a tilt-table test; adjust the ballast to keep >= 20 deg |
| B8 | Gap sensors (ToF) in rain and leaf litter, mounted low on the flares | low | Wet-weather test; the camera stays the primary sensor |
| B9 | Contact peaks are not time-step converged (review m6) | low-medium | x2.5 sizing factor kept |
| B10 | Donor chair price and availability (EUR 400 excerpt vs EUR 1,200+ listings) | cost only | Buy only after T1-D; otherwise the new drive |
| B11 | G3(b) hardware fix (lug tyre) unproven: passes the step in the sim but degrades docking (G1) on rigid sim lugs | option | T5: one pair of 13x5.00-6 lug wheels (about EUR 185); 20 docks + a 40 mm full-width kerb at 110 kg; adopt only if docking holds |

# 12. CAD and renders

The B2 CAD is CadQuery, built from the same numbers as b2/simB2.py and b2/mass_cgB2.json. The bin and carriage poses come from a B2 MuJoCo grab recording (`work/revB2/rec_B2.py`). Renders use the B1 software rasteriser (numba z-buffer, no OpenGL).

- STEP files: `BinRobo_B2_no_bin.step` and `BinRobo_B2_carrying_240L.step`.
- Renders: `B2_render_1_front34.png`, `B2_render_2_carry_240L.png` and `B2_render_3_comb_closeup.png` (all in /workspace/work/out/revB2/).
- Assumptions are listed in `assumptions_B2.md`.

![Plan: B1 vs B2 footprints, bin and loaded pivot circle](fig_b2_1_plan.png){width=95%}

![Lane sweep: minimum clearance to the hedge face, B1 vs B2](fig_b2_2_lane.png){width=95%}

![G1 grab Monte Carlo per bin type](fig_b2_3_grab.png){width=95%}

![B2 front 3/4 view (design render)](../../work/revB2/B2_render_1_front34.png){width=95%}

![B2 carrying a 240 L bin (pose from MuJoCo)](../../work/revB2/B2_render_2_carry_240L.png){width=95%}

![B2 comb, keeper and toggle-locked pad (section)](../../work/revB2/B2_render_3_comb_closeup.png){width=95%}

# 13. Method and files

**Method.**

- One MuJoCo process at nice 10, through the queue (`cmp/queue_cmp.py b2/q_b2.txt`). After a sandbox stop the last 77 lines (lug SL set, gap-sensor stress, perturbations) were finished in the foreground by `b2/qchunk_b2.py` (same queue file and done list, per-run resume of grab sets), and the B1 lane fit under the B2 rules by `b2/lanefit_b2_ckpt.py` (same computation as `lanefit_b2.py`, cached piece by piece).
- Frozen common model terms unchanged: dt 0.5 ms (0.25 ms for G7), 60 N m drive cap, 330 mm wheels and 200 mm castors in every gate run, camera sigma 8 mm with one re-dock. Seeds are as B1.
- B2 design parameters were calibrated before the suite with smokes labelled calibration (`b2/smoke*.log`).
- The lane fit is kinematic: `cmp/lanefit.py`, imported unchanged, plus the B2 rules in `b2/lanefit_b2.py`.

**Files.** All under revG/sim/cg/b2/ unless noted.

- Sim and runner: `simB2.py`, `runB2.py`.
- Mass and hand calcs: `make_mass_b2.py`, `mass_cgB2*.json`, `handcalc_b2*.py`.
- Queue: `mk_queue_b2.py`, `q_b2.txt` and its log, `qchunk_b2.py`.
- Results: `res/B2_*.json`, scorecard `res/gate_B2_.json`.
- Lane fit: `lanefit_b2.py`, `lanefit_b2_ckpt.py`, `design_B2.json`, `design_B1_srun.json`, `res/lanefit_B2.json`, `res/lanefit_B1_srun.json`.
- BOM: `bom_b2.py`, `res/bom_b2*.{json,csv}`.
- Figures and report: `figs_b2.py`, `build_report_b2.py`.
- Diagnostics: `dbg_pad.py`, `dbg_grab.py`, `dbg_padforce.py`.
- CAD and renders: `work/revB2/` (`cad_B2.py`, `stills_B2.py`, `scene.py`, `raster.py`, `rec_B2.*`).
- Progress log: `docs/reviews/PROGRESS_B2.md`.
