---
title: "BinRobo: B1 against Rev H"
subtitle: "Same MuJoCo model, same frozen gate (CRITERIA_FROZEN.md, sha256 2cf3f4ec...8a74, unchanged), same lane. Simulation and hand calcs only; nothing has been built."
author: "Prepared with Hark for Brian"
date: "11 November 2026"
geometry: margin=1.5cm
fontsize: 9pt
documentclass: extarticle
colorlinks: true
---

# 1. Result

**Verdict: keep B1. Do not adopt Rev H as a concept.** B1 passes 8 of 9 frozen gate items. Rev H passes 2 of 9 as designed, and 7 of 9 with two firmware fixes. But Rev H only reaches 7 of 9 because our model gives it something the bins do not have: a load-rated lifting lip on the wall opposite the handle.

- **Rev H lifts the bin by the wrong wall.** The EN 840 comb receiver is under the handle (SULO data sheet, our bin model, EN 840 lifters). Rev H docks on the opposite wall and lifts by a ledge there that nothing in the project shows exists or is rated (section 5.1).
- **Even with that ledge modelled at full EN 840 width, every 240 L bin hangs 11-12 deg.** The front wall tapers, so the fixed lower pad only meets it after about 75 mm of swing. As designed, Rev H claims the bin on 64 of 90 runs on the three 240 L bin types without lifting it clear. These are **false holds**, the worst grab outcome (section 3).
- **With two firmware fixes** (FH1: lift to the stroke end; FH2: rear-camera wheel-clearance check before claiming), Rev H reaches G1 88/90 with 0 false holds, and G2, G4, G5, G7 and G8 pass. G3(b) fails exactly as B1 does. G6 fails 15/18: a full 250 mm-wheel ESE 240 cannot be lifted clear at all. On that bin, FH2 turns 3 false holds into safe misses in the extra G1 run.
- **Rev H's own results overstate it.** Its model welds the bin to the robot and has no yaw. Its scoring allows a 1.0 m e-stop from 0.81 m/s and has no climb time limit. It claims a full-width 40 mm step pass that our MuJoCo stalls at 1.34 m, the same stall as B1.
- **Lane fit: both fit, with no hedge contact anywhere.** That includes the 2.9 m narrowing, 180 deg turns at the dock, in the yard and at the bell-mouth with 1-3 bins standing, and all 12 pad sequences with handles to the lane or to the road. Rev H's 1.93 m turning claim is low (2.16 m geometric, 2.10 m MuJoCo). It still turns in less room than B1 (2.42 m).
- **Cost.** Rev H's EUR 1,990 is measured against the old Rev G list. On the same G8 function and safety basis as B1 it is about **EUR 3,154**, against B1's **EUR 4,743**. About EUR 620 of that gap is B1's new drive; on a donor drive, B1 would be about EUR 4,120 (indicative only). The rest is a real saving, because Rev H has fewer, cheaper parts, but it is not worth having with a lift that grips the wrong wall.
- **640 mm full-width comb for B1: adopt it** (section 9). It meets the GGAWB s.3.5 full-width support rule, cuts the lip bearing stress about 4x, and holds the grab rate. It must be the self-aligning version: a rigid 640 mm comb drops to 86/90 (rim catches on yawed docks). The cost is about EUR 50 and +1.6 kg, and with it B1 still passes 8/9.
- **Hybrids worth taking from Rev H** (section 10): the donor-powerchair drive as a costed B1 variant, Rev H's frame simplification, its leg-tip gap sensors as a docking back-up, and its staged build plan. Not its lifting point.

# 2. What was run

- **Rev H** is built in our MuJoCo from `revH_ext/revH/sim/params.py`, not from the drawings: 85.5 kg, 0.97 m track, 318 mm drive wheels, 260 mm nose castors, tail wheels 75 mm up, 0.66 m leg gap, 0.78 m funnel, 600 mm comb, 300 mm stroke, fixed pad 0.45 m below the comb, no keeper (`revG/sim/cg/cmp/simH.py`). The bin is mirrored so its front wall faces the mast. **In Rev H's favour**, that wall carries a lip with the gate-model section at data-sheet comb height and full EN 840 receiver width.
- **Firmware fixes for Rev H, at most two:** FH1 lifts to the stroke end; FH2 checks wheel clearance on the rear camera before claiming the bin. A B1-style sprung pad was tried as a design sensitivity, not a fix. It cut the hang to 5 deg but stopped the ESE 140 CL from docking.
- **B1** is the final iteration-1 design (F1-F7 + F9). Its results are reused from `it1/res/*_f9`. Reproducibility was checked in `cmp/runCMP.py` and the reruns were identical.
- **B1 + 640 mm comb** (`cmp/simB1fw.py`): the EN 840 receiver width lip (480 / 580 mm) with a 640 mm comb, self-aligning (yaw +/-4 deg, roll +/-3 deg) or rigid. The comb is 640 mm = 580 + 2 x 30 mm, so full-width support holds at any accepted dock (the lift interlock allows 25 mm lateral).
- **Everything else is unchanged and identical for both designs:** frozen gate G1-G9, the same seeds, contact settings, motor and brake models, the controller, the camera model, and the bin models from `bins_g5`. The perturbations are mass +/-10 %, ground mu -15 % and bin-wheel crr 0.09, as for B1 in iteration 1.

# 3. Scorecard

Frozen gate items G1-G9 (`res/gate_H__raw.json`, `gate_H__fx.json`, `gate_B1__f9.json`, `gate_B1__fwm.json`). "Inherited" means the 640 mm comb cannot change that result in our model, so the B1 run is carried over; the comb runs that were made are listed in section 9.

| item | Rev H raw | Rev H + FH1 + FH2 | B1 | B1 + 640 mm comb |
|---|---|---|---|---|
| G1 grab MC (3 x 30) | FAIL 30/90, FH 50 | PASS 88/90, FH 0 | PASS 90/90, FH 0 | PASS 89/90, FH 0 |
| G2 climb 12 % (6) | FAIL 0/6 | PASS 6/6 | PASS 6/6 | PASS 6/6 |
| G3 40 mm step | FAIL (a) fail 4.69 m, (b) fail 1.35 m | FAIL (a) pass, (b) fail 1.34 m | FAIL (a) pass, (b) fail 1.34 m | FAIL (a) pass, (b) fail 1.34 m |
| G4 e-stop 12 % (stop) | FAIL 0.34 m / 0.10 m | PASS 0.20 m / 0.09 m | PASS 0.16 m / 0.08 m | PASS 0.15 m / 0.08 m |
| G5 carry + pivot | FAIL 2.10 m | PASS 2.10 m | PASS 2.42 m | PASS 2.42 m |
| G6 set-down (18) | FAIL 6/18 | FAIL 15/18 | PASS 18/18 | PASS 18/18 |
| G7 dt repeat | PASS (fails at both dt) | PASS | PASS | PASS |
| G8 static (8 poses) | FAIL 0/8 | PASS 8/8 | PASS 8/8 | PASS 8/8 |
| G9 mass <= 120 kg | PASS 85.5 kg | PASS 85.5 kg | PASS 94.1 kg | PASS 95.7 kg |
| **items passed** | **2/9** | **7/9** | **8/9** | **8/9** |

![G1 grab outcome per bin type, all four variants. FH = false hold.](fig_cmp_3_grab.png){width=95%}

Detail per item:

| item | Rev H as designed (raw) | Rev H + FH1 + FH2 (2 firmware fixes) | B1 final (160 mm comb) | B1 + 640 mm full-width comb |
|---|---|---|---|---|
| G1 | **FAIL** WEB 30/30 / SL 0/30 / CL 0/30; pooled 30/90; FH 50; knocked 0 | **PASS** WEB 30/30 / SL 29/30 / CL 29/30; pooled 88/90; FH 0; knocked 0 | **PASS** WEB 30/30 / SL 30/30 / CL 30/30; pooled 90/90; FH 0; knocked 0 | **PASS** WEB 29/30 / SL 30/30 / CL 30/30; pooled 89/90; FH 0; knocked 0 |
| G2 | **FAIL** 0/6; 11.1-25.0 s; creep <= 0.044 m; fail: mu0.30 crr0.06 (grab false_positive, 5.00 m), mu0.30 crr0.09 (grab false_positive, 5.00 m), mu0.25 crr0.06 (grab false_positive, 5.00 m), mu0.25 crr0.09 (grab false_positive, 5.00 m), mu0.22 crr0.06 (grab false_positive, 4.48 m), mu0.22 crr0.09 (grab false_positive, 1.65 m) | **PASS** 6/6; 11.0-11.0 s; creep <= 0.043 m | **PASS** 6/6; 11.1-11.1 s; creep <= 0.035 m | **PASS** 6/6; 11.1-11.1 s; creep <= 0.035 m *[1 of 6 runs re-run with the 640 mm comb, rest inherited]* |
| G3 | **FAIL** one side FAIL (4.69 m, grab false_positive, bin-ground 2319 N, seated True); full width FAIL (1.35 m, grab false_positive, bin-ground 2876 N, seated True) | **FAIL** one side PASS (4.69 m, clear 47 mm); full width FAIL (1.34 m, grab success, bin-ground 0 N, seated True) | **FAIL** one side PASS (4.69 m, clear 88 mm); full width FAIL (1.34 m, grab success, bin-ground 0 N, seated True) | **FAIL** one side PASS (4.69 m, clear 83 mm); full width FAIL (1.34 m, grab success, bin-ground 0 N, seated True) *[1 of 2 runs re-run with the 640 mm comb, rest inherited]* |
| G4 | **FAIL** fwd FAIL 0.34 m, slide 0.003 / rev FAIL 0.10 m, slide 0.001 | **PASS** fwd PASS 0.20 m, slide 0.001 / rev PASS 0.09 m, slide 0.001 | **PASS** fwd PASS 0.16 m, slide 0.001 / rev PASS 0.08 m, slide 0.001 | **PASS** fwd PASS 0.15 m, slide 0.001 / rev PASS 0.08 m, slide 0.001 |
| G5 | **FAIL** FAIL; roll 0.00 deg; pivot swept 2.10 m | **PASS** PASS; roll 0.01 deg; pivot swept 2.10 m | **PASS** PASS; roll 0.00 deg; pivot swept 2.42 m | **PASS** PASS; roll 0.00 deg; pivot swept 2.42 m |
| G6 | **FAIL** 6/18, 0 TIPS; CL flat full FAIL, CL flat empty FAIL, CL up12 full FAIL, CL up12 empty FAIL, CL dn12 full FAIL, CL dn12 empty FAIL, SL250 flat full FAIL, SL250 flat empty FAIL, SL250 up12 full FAIL, SL250 up12 empty FAIL, SL250 dn12 full FAIL, SL250 dn12 empty FAIL | **FAIL** 15/18, 0 TIPS; SL250 flat full FAIL, SL250 up12 full FAIL, SL250 dn12 full FAIL | **PASS** 18/18, 0 TIPS | **PASS** 18/18, 0 TIPS |
| G7 | **PASS** climb_m25_c09 base False / dt025 False t 14.4/14.3 s; step40_one base False / dt025 False; estop12_fwd base False / dt025 False | **PASS** climb_m25_c09 base True / dt025 True t 11.0/11.0 s; step40_one base True / dt025 True; estop12_fwd base True / dt025 True | **PASS** climb_m25_c09 base True / dt025 True t 11.1/11.0 s; step40_one base True / dt025 True; estop12_fwd base True / dt025 True | **PASS** climb_m25_c09 base True / dt025 True t 11.1/11.0 s; step40_one base True / dt025 True; estop12_fwd base True / dt025 True *[inherited from B1 final]* |
| G8 | **FAIL** 0/8 poses; drive >= 362 N, castors >= 272 N; hand-calc min tip 40.9 deg; fail: up 110, up 60, dn 110, dn 60, crL 110, crL 60, crR 110, crR 60 | **PASS** 8/8 poses; drive >= 454 N, castors >= 268 N; hand-calc min tip 40.9 deg | **PASS** 8/8 poses; drive >= 460 N, castors >= 294 N; hand-calc min tip 39.4 deg | **PASS** 8/8 poses; drive >= 460 N, castors >= 294 N; hand-calc min tip 39.4 deg *[inherited from B1 final]* |
| G9 | **PASS** 85.5 kg | **PASS** 85.5 kg | **PASS** 94.1 kg | **PASS** 94.1 kg (+1.6 kg comb, est.: 95.7 kg) |
| **items passed** | **2/9** | **7/9** | **8/9** | **8/9** |

Extra grab Monte Carlos (reported, not gating):

- B1 final: ESE240SL250 30/30, FH 0, knocked 0; ESE140CL 29/30, FH 0, knocked 0
- Rev H raw: ESE240SL250 0/30, FH 14, knocked 0; ESE140CL 30/30, FH 0, knocked 0
- Rev H + FH1 + FH2: ESE240SL250 11/30, FH 3, knocked 0; ESE140CL 30/30, FH 0, knocked 0
- G3(b) with a 1:4 kerb ramp: B1 PASS (4.71 m, grab success, bin-ground 0 N); Rev H raw FAIL (4.71 m, grab false_positive, bin-ground 674 N); Rev H fixed PASS (4.71 m, grab success, bin-ground 0 N)

Peak loads over the carry runs (G2-G6, dt 0.5 ms): B1: lift_N 3000 (B1_step40_one_f9), pad_N 1063 (B1_step40_both_f9), nib_rim_N 3838 (B1_step40_one_f9); Hraw: lift_N 3000 (H_step40_one_rw318_raw), pad_N 1304 (H_step40_one_rw318_raw), nib_rim_N 3044 (H_step40_one_rw318_raw); Hfx: lift_N 3000 (H_step40_one_rw318_fx), pad_N 1480 (H_step40_one_rw318_fx), nib_rim_N 2723 (H_step40_one_rw318_fx); FW: lift_N 1952 (B1_step40_one_f9_fwp32), pad_N 1073 (B1_towstab_f9_fwp32), nib_rim_N 2806 (B1_step40_one_f9_fwp32)

**How Rev H fails as designed.** Every carry test (G2-G5, G8) starts with a grab on a full ESE 240 SL. As designed, that grab is a false hold: the comb is claimed, but the bin swings 11-12 deg on the front lip and its wheels stay on the ground. So the "carry" drags the bin, and every carry item fails on "bin held". G7 "passes" only because the result is the same failure at both time steps.

**Perturbations** (reported, not gating; B1 rows from iteration 1):

| design, perturbation | G1 (10 per bin) | G2 mu 0.22 / 0.25 | G3 one side | G4 fwd / rev | G5 | G6 6 hardest | G8 3 poses |
|----|----|----|----|----|----|----|----|
| B1, mass +10 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.1 s / PASS 11.1 s | PASS | PASS 0.15 m / PASS 0.08 m | PASS 2.43 m | 6/6 | 3/3 |
| B1, mass -10 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.0 s / PASS 11.0 s | PASS | PASS 0.14 m / PASS 0.09 m | PASS 2.40 m | 6/6 | 3/3 |
| B1, mu -15 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.8 s / PASS 11.2 s | PASS | PASS 0.22 m / PASS 0.11 m | PASS 2.40 m | 6/6 | 3/3 |
| B1, bin crr 0.09 | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.1 s / PASS 11.1 s | PASS | PASS 0.16 m / PASS 0.08 m | PASS 2.42 m | 6/6 | 3/3 |
| Rev H fixed, mass +10 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.1 s / PASS 11.0 s | PASS | PASS 0.20 m / PASS 0.08 m | PASS 2.12 m | 5/6 | 3/3 |
| Rev H fixed, mass -10 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.0 s / PASS 10.9 s | PASS | PASS 0.19 m / PASS 0.09 m | PASS 2.08 m | 5/6 | 3/3 |
| Rev H fixed, mu -15 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.8 s / PASS 11.1 s | PASS | PASS 0.29 m / PASS 0.12 m | PASS 2.08 m | 5/6 | 3/3 |
| Rev H fixed, bin crr 0.09 | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.0 s / PASS 11.0 s | PASS | PASS 0.21 m / PASS 0.09 m | PASS 2.10 m | 5/6 | 3/3 |

Both designs hold under every perturbation: no false holds, no knocked bins, no tips. Rev H's one miss in each row is the full 250 mm-wheel ESE 240 set-down case, which it cannot lift clear at nominal either (a safe miss).

# 4. Rev H's claims next to our re-runs

| Rev H claim (RESULTS_H1.md) | Rev H value | Our re-run (MuJoCo, frozen gate) |
|---|---|---|
| Lifts the bin 100 mm by the EN 840 front comb lip, carried upright | upright, 100 mm | Lip on the wrong wall (5.1). Modelled anyway: 240 L bins **hang 11.2-12.5 deg**, wheels 37-134 mm clear (fixed); WEB 140 8-9 deg |
| Docking success with one re-approach | 99.95 % (tolerance stack) | As designed: 240 L **0/90 captured, 64 false holds**; 140 L 60/60. Fixed: 88/90 + extras SL250 11/30 with **3 false holds**, ESE 140 CL 30/30 |
| 40 mm full-width step, mu 0.6, 0.5 m/s | pass 4 of 4 | **FAIL, stalls at 1.34 m** (same as B1); passes with a 1:4 ramp (4.71 m) |
| 40 mm one-sided bump | pass 4 of 4 | PASS (fixed), 4.69 m, 47 mm wheel clearance |
| 12 % climb, mu 0.3 | 18 of 18 | Fixed 6/6 (11.0 s, hold creep up to 0.043 m against a 0.05 m limit); as designed 0/6 (false hold) |
| E-stop 12 % down, full 240 L, mu 0.3 | 0.32 m from 0.81 m/s (limit 1.0 m) | Fixed: fwd 0.20 m / rev 0.09 m from 0.5 m/s (limit 0.5 m): PASS |
| Sideways tip, full 240 L | 40.7 deg | Hand calc 40.9 deg upright, 41.6 deg at the hang; G8 8/8 poses (fixed) |
| 180 deg turn | 1.93 m, "fits a 3.6 m lane" (hard-coded True) | 2.16 m geometric with castor swivel; MuJoCo 2.10 m; fits at every lane station incl. the 2.9 m narrowing |
| Lane | 635 m, 3.6 m everywhere, G4 drop layout | 633 m with truth hedge faces; G6 layout (section 6) |
| Mass | 85.5 kg | 85.5 kg used (from params.py; not checked independently) |
| Cost | EUR 1,990 all-in | EUR 3,154 on the G8 function/safety basis (section 8) |
| Lip load factor on steps | up to 3.9 (7.3 on trench) | Peak nib/lip force 2723 N in the carry runs (fixed), against B1 3838 N |

# 5. Audit of the Rev H package

## 5.1 Rev H lifts the bin by the wrong wall

Rev H docks on the bin's front wall, the wall opposite the handle, and treats a ledge on that wall as the EN 840 comb receiver. The package says so in several places:

- `sim/make_iso.py` line 181: the bin's front wall faces the mast and "the bin extends towards -x (handle to the rear)"; line 190 draws the "frontal comb receiver" on that wall.
- `sim/params.py` line 24: `pad_x` is "carriage pad face = bin front wall when docked". Lines 89-91 put the bin CG behind the front wall.
- `RESULTS_H1.md` s.1: "lifts it 100 mm by the EN 840 front comb lip".

On the bins we model, and on EN 840 lifters, the comb receiver is on the handle side, directly under the handle bar:

- **SULO Citybac 240 data sheet, p.2** (`web/downloads/g5bins/sulods-2.png`): callout C, "DIN comb lifting system, double stage", is at the handle end, just under callout B (the continuous handle bar). The wall opposite the handle carries the SULO sticker (D) and no receiver.
- **Project bin model** (`revG/sim/g5/bins_g5.py`, sources in `revG/RESULTS_G5_binrange.md` s.1): on every bin with a published comb height, the handle-bar centre sits about 12 mm above it (ESE 140 CL comb 969 / bar ~981; ESE 240 SL 1005 / ~1017; ESE 240 CL 938 / ~950; SULO comb 998 / bar 1012 scaled). The comb height in the data sheets is the height of the receiver under the handle.
- **EN 840-1:2004** Tables 2/3, dimension 2 (receiver width 480 +/- 5 mm for 140 L, 580 +/- 5 mm for 240 L). The truck comb engages the receiver while the bin's handle faces the truck; the lid hinge is on the same side. Our gate lip model (`it1/simB_it1.py`, `cmp/simB1fw.py`) puts the receiver there.
- **GGAWB Application Guidelines 03/2025 s.3.5**: the receiving section has to be supported over its whole width by the comb teeth. This is the source for the full-width comb question in section 9.

So **Rev H lifts by a feature that is not the receiver.** The front wall of these bins is a tapered, smooth or bead-reinforced moulding with only the rim flange at the top. Nothing in the project shows a ledge there that is rated to carry the bin. To give Rev H its best case, the MuJoCo model (`cmp/simH.py`) still gives the front wall a lip with the gate-model section at data-sheet comb height and full EN 840 receiver width. **Even with that lip, the full 240 L bins hang 11-12 deg** because the front wall tapers in towards the base. The fixed lower pad, 0.45 m below the comb, only meets the wall after about 75 mm of swing. That is the root cause of the false holds in section 3.

What would settle it: measure the front-wall rim of the three bins actually on the lane (ESE / SULO / Weber), and do a hand-lift test by that rim with 110 kg. Until then, Rev H's grab rests on an unproven feature.

## 5.2 Dynamics model and scoring

- `sim/dyn.py` is reduced order (x, z, pitch, roll) with penalty contact. **There is no yaw.** The README admits this makes one-sided results optimistic: it passes Rev G over the 50/60 mm one-sided bumps that MuJoCo stalls on (RESULTS_H1 s.3.4).
- `sim/models.py` `make_revh`: **the bin is welded to the robot** (one rigid body). There is no comb-lip contact, no hang and no lip unseating, so a dynamic retention failure cannot happen in that model. "Largest gap between lip and comb 4.2 mm" is computed after the fact, not simulated.
- Scoring in `sim/tests_mech.py` is lenient:
  - e-stop pass (line 116) = stop < **1.0 m** (frozen G4: 0.5 m), and the e-stop starts at **0.81 m/s** (G4: 0.5 m/s). The term `tail_max >= 0` is always true.
  - climb pass (line 118) = speed > 0.85 v at the end. There is no time limit, no 3 s hold-creep check and no bin-held check.
  - The lip load factor (up to 7.28) and the lip gap are reported but never gate.
- `sim/dock_mc.py` is a tolerance stack with assumed sensor errors (99.95 % with one re-approach), not contact physics. The MuJoCo grab MC replaces it in section 3.

## 5.3 Bill of materials

- `results/bom_revH.csv` has 74 rows (63 priced lines in the summary). By price status: est 28 lines (EUR 677), G4-est 25 (EUR 496), G4-checked 11 (EUR 302, **18 % of parts**), excerpt 6 (EUR 325). Most of the money is estimates or carried estimates.
- The donor powerchair is EUR 160 (G4-est, DoneDeal). | | parts | logistics | contingency | **all-in** | basis |
|---|---|---|---|---|---|
| Rev H as claimed | 1682 | 161 | 190 | **1990** | vs Rev G published; 18 % of parts checked |
| Rev H re-based | 2620 | 217 | 318 | **3154** | Rev H mover lines + G8 Lean-D shared-function lines; donor chair EUR 400 |
| B1 (final) | 4007 | 332 | 404 | **4743** | G8 Lean concept B + iteration 1 (new drive) |
| B1 on a donor drive (indicative) | 3467 | 237 | 415 | **4120** | lean Structure/Drive/Power swapped for the G8 donor lines; not designed |
| B1 + 640 mm comb | +45 | - | +5 | **about +50** | estimate (plate + 2-axis pivot) |

Shared-function lines Rev H prices below the G8 Lean-D list (EUR): Safety & power dist. +290, Navigation +3, Sensing +62, Comms +122, Enclosure & wiring +211, Lights +33, Dock -25.DOWN_G8 used EUR 400 (excerpt; listings EUR 380-850).
- Rev H is compared with **Rev G as published (EUR 2,131, a G4-era list)**, not with the G7/G8 safety and function baseline and not with B1. Against the G8 Lean-D lines, Rev H is short EUR 290 on the safety and power-distribution stack, EUR 211 on enclosure and wiring, EUR 122 on comms and EUR 62 on sensing (section 8).

## 5.4 Mission data and layout

- `data/route.json` and `data/grades.json` are identical (md5) to `sitl/data`, which is good.
- `data/drop_layout_default.json` is the **superseded G4 layout** (handles up-lane, drop order F, M, A). The G6 layout has handles to the road and drop order A, M, F. Rev H's set-down direction and its pickup sequence are therefore planned for a layout that is no longer used.
- The mission length is 635 m against 633.06 m (route s end), a small difference.

## 5.5 Lane-width claims

- `sim/mission.py` lines 142-143 set `fits_3p6m_lane=True` for the Rev H pivot as a constant. It is not computed against the lane.
- Every width claim uses 3.6 m. The truth hedge faces narrow to **2.9 m face to face at s = 500-516 m** (both sides 0.60 m in), and the faces are irregular elsewhere.
- The 1.93 m turning width ignores the swivel envelope of the 260 mm nose castors (swivel axis x 0.79 m, reach about 1.03 m from the drive-axle centre).
- Section 6 re-does the lane fit with the truth faces for both designs.

# 6. Lane fit

`cmp/lanefit.py` (kinematic, no MuJoCo), with the same lane geometry as the G6 SITL: the 633 m OSM lane, the truth hedge faces (irregularity and overgrown narrowings, including s = 500-516 m at 2.9 m face to face), the yard (s 0-25), the 12 m bell-mouth, the 0.3 m legal margin to the private boundary, the G6 pads A/M/F, the home spots and the dock. The footprint is the actual part rectangles, with the open U kept open and the castor swivel envelopes included. Scoring is strict: **any footprint point past a truth hedge face is a FAIL**, and so is a bin-to-bin gap under 0.05 m. Every pivot is a 180 deg turn on the spot, and every straight move into or out of a pivot is swept.

![Plan footprints (part rectangles, castor swivel envelopes dotted) with the carried ESE 240 SL and the loaded 180 deg pivot circle.](fig_cmp_1_plan.png){width=85%}

![Least clearance to the truth hedge faces along the lane, loaded, both directions.](fig_cmp_2_lane.png){width=95%}

| lane-fit item (strict: any footprint point past a truth hedge face = FAIL) | B1 | Rev H |
|---|---|---|
| overall width (m) | 0.97 | 1.04 |
| 180 deg pivot diameter, empty / loaded (m) | 2.36 / 2.42 (loaded = MuJoCo G5 swept) | 2.16 / 2.16 (geometric; MuJoCo G5 swept 2.10) |
| lane sweep down loaded: least clearance to a hedge face (m), at s | 0.325 at s 501 | 0.333 at s 501 |
| lane sweep up loaded: least clearance to a hedge face (m), at s | 0.179 at s 417 | 0.180 at s 417 |
| margin over the SITL lateral-estimate p95 (0.124 m) | +0.055 | +0.056 |
| lane stations where a loaded 180 deg pivot fits between the faces | 100 % | 100 % |
| pivot at s 500-516 (2.9 m between faces): least margin (m) | 0.17 | 0.29 |
| dock: loaded 180 deg pivot within 2 m, 0-3 bins at home, margin (m) | 2.07 | 2.20 |
| yard: 180 deg pivot, 0-3 bins at home, margin (m) | 4.79 | 4.92 |
| bell-mouth: 180 deg pivot with 1-3 bins standing, margin (m) | 0.88 | 1.01 |

| pad sequence (G6 pads A, M, F; drop A-M-F, pickup F-M-A) | B1 result, least margin (m) | Rev H result, least margin (m) |
|---|---|---|
| drop n1 handles to the lane | PASS, 0.202 (A withdraw 0.9 m up-lane) | PASS, 0.007 (A empty pivot beyond the placed bin) |
| drop n1 handles to the road | PASS, 0.104 (A empty pivot beyond the placed bin) | PASS, 0.174 (A withdraw 0.9 m up-lane) |
| drop n2 handles to the lane | PASS, 0.202 (A withdraw 0.9 m up-lane) | PASS, 0.007 (A empty pivot beyond the placed bin) |
| drop n2 handles to the road | PASS, 0.047 (M empty pivot beyond the placed bin) | PASS, 0.174 (A withdraw 0.9 m up-lane) |
| drop n3 handles to the lane | PASS, 0.202 (A withdraw 0.9 m up-lane) | PASS, 0.007 (A empty pivot beyond the placed bin) |
| drop n3 handles to the road | PASS, 0.047 (M empty pivot beyond the placed bin) | PASS, 0.174 (A withdraw 0.9 m up-lane) |
| pickup n1 handles to the lane | PASS, 0.202 (A run-in 1.5 m onto the bin) | PASS, 0.199 (A pass the bin on the way down) |
| pickup n1 handles to the road | PASS, 0.175 (A pass the bin on the way down) | PASS, 0.174 (A run-in 1.5 m onto the bin) |
| pickup n2 handles to the lane | PASS, 0.202 (A run-in 1.5 m onto the bin) | PASS, 0.199 (A pass the bin on the way down) |
| pickup n2 handles to the road | PASS, 0.175 (A pass the bin on the way down) | PASS, 0.174 (A run-in 1.5 m onto the bin) |
| pickup n3 handles to the lane | PASS, 0.202 (A run-in 1.5 m onto the bin) | PASS, 0.199 (A pass the bin on the way down) |
| pickup n3 handles to the road | PASS, 0.175 (A pass the bin on the way down) | PASS, 0.174 (A run-in 1.5 m onto the bin) |

**Reading it.**

- Neither design touches a hedge face anywhere.
- The lane sweep is identical in practice (0.18 m least clearance at s 417 going up). That is only 0.055 m more than the SITL lateral-estimate p95 of 0.124 m, so the corridor guard and the localisation, not the vehicle width, set the hedge risk for both.
- Rev H's smaller pivot gives more room at the narrowing (0.29 m against 0.17 m) and at the bell-mouth.
- **Handle-toward-lane set-down works for both.** Rev H's thinnest case is the empty pivot just beyond the placed bin when handles face the lane (7 mm). B1's thinnest is the same move with handles to the road (47 mm). Both are below the localisation error. In both cases the robot should run on 0.3-0.5 m before pivoting; the margins above are at the closest pivot point the search accepts.

# 7. Hand calcs

`cmp/handcalc_cmp.py` -> `res/handcalc_cmp.json`. The same method for both (iteration-1 method). Rev H masses are from `params.py`, and its bin CG is from the gate bin model carried by the front wall, both upright and at the MuJoCo hang tilt.

| case | M kg | tip lateral deg | tip fwd over castors deg | castor lift-off deg | rear tip deg | castor N flat | mu req 12 % | N m/wheel 12 % |
|---|---|---|---|---|---|---|---|---|
| B1, bin 110 kg | 204.1 | 39.4 | 57.4 | 23.2 | 50.8 | 430 | 0.207 | 24.6 |
| B1, bin 60 kg | 154.1 | 41.0 | 56.6 | 33.2 | 56.7 | 456 | 0.249 | 19.8 |
| B1, bin 0 kg | 94.1 | 48.6 | 55.9 | 57.4 | 70.2 | 474 | 0.415 | 14.0 |
| Rev H, bin 110 kg, hang 0.0 deg | 195.5 | 40.9 | 50.1 | 15.1 | 46.7 | 353 | 0.207 | 23.0 |
| Rev H, bin 110 kg, hang 11.3 deg | 195.5 | 41.6 | 48.8 | 22.5 | 51.4 | 511 | 0.232 | 23.0 |
| Rev H, bin 60 kg, hang 0.0 deg | 145.5 | 41.9 | 50.4 | 18.2 | 49.3 | 306 | 0.231 | 18.4 |
| Rev H, bin 60 kg, hang 11.3 deg | 145.5 | 42.6 | 49.5 | 23.8 | 52.7 | 390 | 0.250 | 18.4 |
| Rev H, bin 0 kg, hang 0.0 deg | 85.5 | 46.7 | 52.4 | 30.9 | 58.4 | 264 | 0.312 | 12.8 |

| comb / lip case (gate-model ledge 30 x 8 mm, not measured) | force N | comb mm | receiver covered | line load N/mm | ledge bending MPa |
|---|---|---|---|---|---|
| B1 160 mm comb, ESE 240 SL full, static carry | 1578 | 160 | 28 % | 9.86 | 24.0 |
| B1 160 mm comb, ESE 240 SL full, peak carry (G3/G5 runs) | 2500 | 160 | 28 % | 15.62 | 38.1 |
| B1 160 mm comb, Weber 140 full, static | 986 | 160 | 33 % | 6.16 | 15.0 |
| B1-FW 640 mm comb, ESE 240 SL full, static carry | 1485 | 640 | 100 % | 2.56 | 6.2 |
| B1-FW 640 mm comb, ESE 240 SL full, peak carry | 2500 | 640 | 100 % | 4.31 | 10.5 |
| Rev H 600 mm comb on the FRONT rim, Weber 140 full, static | 611 | 600 | 100 % | 1.27 | 3.1 |
| Rev H 600 mm comb on the FRONT rim, ESE 240 full (pad variant), static | 1300 | 600 | 100 % | 2.24 | 5.5 |
| Rev H own claim (statics.json): 110 kg on 390 mm x 10 mm | 1079 | 390 | 100 % | 2.77 | 6.7 |

- **Traction and torque are the same.** Both need mu 0.21-0.25 on 12 %, at 23-25 N m per wheel with a full 240 L.
- **Rev H's castor lift-off angle is lower** (15.1 deg upright, 22.5 deg at the hang, against B1's 23.2 deg). Its nose castors carry less when climbing, and the tail wheels touch at 10.6 deg of pitch.
- **Tip-over is not a problem for either design:** the least tip angle is 39-41 deg against the 20 deg limit.
- **Lip contact.** The lip section is the gate-model assumption (30 x 8 mm HDPE ledge, load at the 26 mm rim), not a measurement. On it, B1's 160 mm comb bends the ledge to 24 MPa static and 38 MPa at the peak carry load. That is above HDPE yield (about 20-25 MPa) and covers only 28 % of the 580 mm receiver. A 640 mm comb brings this to 6 MPa static and 10.5 MPa peak. Rev H's 600 mm comb is also low (3-6 MPa), but on a wall that has no rated ledge.

# 8. Cost

`cmp/cost_cmp.py` -> `res/cost_cmp.json`. All figures are EUR all-in, including logistics and contingency.

| | parts | logistics | contingency | **all-in** | basis |
|---|---|---|---|---|---|
| Rev H as claimed | 1682 | 161 | 190 | **1990** | vs Rev G published; 18 % of parts checked |
| Rev H re-based | 2620 | 217 | 318 | **3154** | Rev H mover lines + G8 Lean-D shared-function lines; donor chair EUR 400 |
| B1 (final) | 4007 | 332 | 404 | **4743** | G8 Lean concept B + iteration 1 (new drive) |
| B1 on a donor drive (indicative) | 3467 | 237 | 415 | **4120** | lean Structure/Drive/Power swapped for the G8 donor lines; not designed |
| B1 + 640 mm comb | +45 | - | +5 | **about +50** | estimate (plate + 2-axis pivot) |

Shared-function lines Rev H prices below the G8 Lean-D list (EUR): Safety & power dist. +290, Navigation +3, Sensing +62, Comms +122, Enclosure & wiring +211, Lights +33, Dock -25.

- Rev H's EUR 1,990 is compared, in its own package, with Rev G as published (EUR 2,131, a G4-era list). Since then, the G7 safety review and the G8 cost-down have set the function and safety baseline that B1 carries.
- **On that baseline Rev H is about EUR 3,154, and B1 is EUR 4,743.** B1 is built on new drive motors and a new frame (Lean). On the donor-chair drive it would be about EUR 4,120, which is indicative only: that geometry is not designed.
- The EUR 1,000 or so that remains is Rev H's real saving: one tube size, about 14 plates, one actuator and a rigid comb. **It is not worth taking while the lift grips a wall with no receiver.**
- Price quality: 18 % of Rev H's parts money is checked. B1's iteration-1 additions are checked (Conrad, 11 Nov), and its basis is the G8 list.

# 9. Should B1 adopt the 640 mm full-width comb?

| B1 comb (G1, F9) | WEB 140 | ESE 240 SL | ESE 240 CL | pooled | FH | knocked | SL 250 (extra) | ESE 140 CL (extra) |
|---|---|---|---|---|---|---|---|---|
| 160 mm (final B1), gate lip | 30/30 | 30/30 | 30/30 | 90/90 | 0 | 0 | 30/30 | 29/30 |
| 160 mm, EN 840 lip | 30/30 | 30/30 | 30/30 | 90/90 | 0 | 0 | not run | not run |
| 640 mm rigid, EN 840 lip | 30/30 | 27/30 | 29/30 | 86/90 | 0 | 0 | not run | not run |
| 640 mm self-aligning, EN 840 lip | 29/30 | 30/30 | 30/30 | 89/90 | 0 | 0 | 30/30 | 29/30 |

B1 with the 640 mm self-aligning comb, other affected groups: G6 set-down 18/18 PASS, 0 TIPS; G5 towstab PASS; G3(a) one side PASS; G4 fwd PASS; G4 rev PASS; G2 mu 0.22 crr 0.09 PASS.

**Recommendation: yes. Adopt a 640 mm self-aligning comb (yaw +/-4 deg, roll +/-3 deg on stops and springs). Do not fit a rigid 640 mm comb.**

- **Why the full width.** GGAWB Application Guidelines 03/2025 s.3.5 requires the receiving section to be supported over its complete width by the comb teeth. EN 840-1 gives the receiver as 480 / 580 mm (140 / 240 L). B1's 160 mm tooth covers 28-33 % of it. On the gate-model ledge:
  - The peak lip force in B1's carry runs is 3,838 N (G3(a) one side, 160 mm). That is 24 N/mm, or about 58 MPa ledge bending scaled from the hand-calc section, against HDPE yield of about 20-25 MPa.
  - With the 640 mm comb the peak is 2,806 N spread over the full 580 mm receiver. That is about 4.8 N/mm and 12 MPa.
  - The peak lift-actuator force in the same test also drops, from the 3,000 N cap to 1,952 N, because the bin no longer rocks on a narrow tooth.
  - Static carry goes from 24 MPa to 6 MPa.
  - The 160 mm tooth is the one place where B1 loads the bin harder than the standard truck lifter the bins are designed for.
- **Why self-aligning.** A rigid 640 mm comb loses 4 grabs (86/90, below the 87/90 pooled pass mark, 0 false holds). In every failed run the residual yaw (1.7-2.6 deg) puts one comb end 10-15 mm forward, under the rim flange instead of in the receiver. The lift then aborts with "load 24-28 mm below the expected ledge". The self-aligning comb takes up that yaw. It scores 89/90 on the gate bins, 30/30 on the 250 mm-wheel ESE 240 and 29/30 on the ESE 140 CL, with 0 false holds and 0 knocked.
- **Nothing else got worse.** Re-run with the 640 mm self-aligning comb: G6 18/18 (0 tips), G5 PASS (pivot 2.42 m), G3(a) PASS, G4 fwd/rev PASS (0.155 m), and G2 hardest case PASS. Wheel clearance is 84 mm against 88 mm, and the hang is 3.3 deg against 3.2 deg. The 640 mm comb fits inside B1's guards (0.716 m between them), so the lane fit is unchanged.
- **Cost and mass:** about EUR 50 all-in (laser plate plus two bushes, two springs and stops; estimate) and about +1.6 kg on the carriage. G9 becomes about 95.7 kg.
- **Before freezing it:** measure the receiver on the bins actually on the lane (width, ledge depth and the rib pattern). Bench-test the comb on one full 240 L bin, including a 2-3 deg yawed dock.

# 10. Hybrids worth taking

| Take from Rev H into B1 | Why | What it needs first | Effect |
|---|---|---|---|
| **Staged build** (Rev H s.8: stage 1 = mover + lift on a hand controller) | It tests the one thing simulation cannot: the comb on Brian's real bins. That happens before about EUR 1,000 of autonomy, safety and dock parts are bought | Nothing. Reorder the B1 build plan | Lowers the risk of the build; no cost change |
| **Donor-powerchair drive** (Rev H's mover; G8 Lean-D) | It replaces B1's new motors, frame drive parts and pack. Indicative all-in EUR 4,120 against EUR 4,743 | A donor chair with at least 8 deg rating and the G8 T1-D pull test (450 N at walking pace for 3 min). Re-run G2/G3/G4 with the donor torque and wheel size. The B1 tray geometry must take the donor motor plates | About EUR -620 (indicative) |
| **Frame simplification** (one 50x50x3 tube size, about 14 laser plates) | B1's frame lines are the largest non-drive item in the Lean list | A frame redraw, then re-checks of G8 statics and of mass/CG | Not costed; Rev H prices its frame at EUR 280 against B1 Lean at EUR 625 |
| **Leg-tip gap sensors** (Rev H dock stress case: 98.5 % to 99.9 % with 4 mm gap sensors) | A cheap back-up if the real camera is worse than the 8 mm the gate assumes | Bench-measure the camera first. B1 already docks 90/90 at 8 mm | About EUR 20-30, only if needed |

**Not worth taking:**

- **The front-wall lift.** It has no receiver to lift by (section 5.1).
- **The fixed lower pad.** It is the cause of the 11-12 deg hang.
- **The 260 mm nose castors.** They help Rev H's step cases in its own model, but G3(b) is drive-limited in MuJoCo for both designs.
- **The smaller pivot circle.** B1 already fits every lane-fit case.

# 11. Limits of this comparison

- Rev H was rebuilt from `params.py` into our model. Parts that `params.py` does not fix (brackets, the exact pad face and the lip shape) are our modelling choices. Each one was made in Rev H's favour where there was a choice: full-width lip, data-sheet comb height, best-case sensors.
- Neither design has a measured lip section. The 640 mm comb case rests on the GGAWB rule and the gate-model ledge, not on a bin test.
- The lane fit is kinematic, with the SITL estimate error added as a margin, not simulated with SITL. The G6 SITL regression has not been re-run for either design.
- Costs: B1 donor variant and the 640 mm comb delta are estimates.

# 12. Files

- Report: `docs/reviews/COMPARE_B1_vs_RevH.md` / `.pdf`; progress log `docs/reviews/PROGRESS_compare.md`.
- Models: `revG/sim/cg/cmp/simH.py` (Rev H), `simB1fw.py` (B1 comb variants), `runCMP.py`, queue `q_b1.txt`.
- Results: `revG/sim/cg/cmp/res/` (`H_*_raw`, `H_*_fx`, `H_*_fxpm110/pm090/pmu085/pcrr09`, `B1_*_f9_fwp32`, `B1_*_f9_fwr32`, `B1_*_f9_en840n`); scorecards `gate_H__raw.json`, `gate_H__fx.json`, `gate_B1__f9.json`, `gate_B1__fwm.json` (+ `gate_fw_provenance.json`); `lanefit_B1.json`, `lanefit_RevH.json`, `lanefit_table.md`; `handcalc_cmp.json`; `cost_cmp.json`; `tables_cmp.md`; `peaks_cmp.json`.
- Figures: `docs/reviews/fig_cmp_1_plan.png`, `fig_cmp_2_lane.png`, `fig_cmp_3_grab.png`.
