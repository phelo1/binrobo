---
title: "BinRobo BT-6 concept B (comb-lift carrier): iteration 1"
subtitle: "B1 against the gate criteria frozen 11 Nov 2026 07:51 +03 (unchanged). MuJoCo and hand calcs only; nothing has been built."
author: "Prepared with Hark for Brian"
date: "11 November 2026"
geometry: margin=1.6cm
fontsize: 10pt
colorlinks: true
---

# 1. Result

**Final B1 passes {{NB1}} of 9 gate items (B at the G6 gate: {{NB0}} of 9; B1 before the last firmware fix F9: {{NB7}} of 9). Still failing: {{FAILS}}.** {{VERDICT}}

**Fixed in this iteration** (sections 3-5):

- **Grab (G1): {{G1_POOL}} pooled** (WEB140 {{G1_WEB}}, ESE SL {{G1_SL}}, ESE CL {{G1_CL}}), from {{G1_POOL7}} with F1-F7. The pass mark is 28/30 per bin and 87/90 pooled. {{G1_FH}} false holds and {{G1_KN}} bins knocked over. The last fix is F9 (approach heading taper and a faster yaw pivot); F8, the fix prepared by the previous run, was tried first and recovered none of the failing cases: {{F8_SUB}}.
- **Set-down (G6): {{G6_FINAL}}, from 5/18 at the gate (11/18 with SD2 alone).** This took four changes: the position-based set-down (SD2), the pad on the lift carriage, a 40 mm pad retract when the keeper opens, and an upright interlock relative to the bin's own standing tilt. It was re-run on the final firmware because F9 changes the approach.
- **Stability.** The 10 kg ballast plate moves forward into the tray floor. Castor lift-off goes from {{HC0_LIFT}} to {{HC1_LIFT}} deg at 110 kg, and the castors carry more in every static pose, including the 12 % cross-slope both ways.
- **Grab safety.** No bin was knocked over and there were no false holds in {{GRAB_TOTAL}} grab runs on 5 bin types (final firmware, including the perturbation runs). The 250 mm-wheel ESE 240 now docks: {{SL250_MC}}, where the G6 B never docked it.

**Still failing.**

1. **G3(b), the full-width sharp 40 mm step: the vehicle stops at {{STEP_B}} with its drive wheels at the edge.** This is friction physics for two driven wheels with free castors.
   - The step needs an edge friction of 0.86 on 330 mm wheels; the test sets 0.6.
   - A 560 mm wheel sits exactly on the limit, and in the sim it still {{STEP_RW}}.
   - **Chosen fix: a kerb ramp on each surveyed step** (EUR 20-40 each, a lane-prep item). With a 1:4 ramp: {{STEP_RAMP}}.
   - The frozen G3(b) test has no ramp, so it stays FAIL as written. The criterion has not been changed.
   - The only hardware route is 4WD, roughly EUR 300-450 more. I have not simulated it.
{{OTHER_FAILS}}

**Pad actuator.** The peak pad load over every B1 run is {{PADPK}} N ({{PADPKF}}, mass +10 %). On the final firmware it is {{PADF9}} N with mass +10 % ({{PADF9F}}) and {{PADNOM}} N nominal ({{PADNOMF}}). That is above the 1,000 N rating of the TRU Components TC24-50-1000 POT, so the part is changed to the MSW DSZY4-24-50-100-STD-IP65 (2,500 N dynamic, 4,500 N static, EUR 389.00 at Conrad; section 8.2).

**Cost.** Lean G8 basis, concept B: EUR {{COST_BASE}} all-in. Iteration 1 adds EUR {{COST_DELTA}}, giving **EUR {{COST_NEW}}** plus ramps (EUR 20-40 per surveyed step). That is EUR {{COST_OLD}} as briefed plus the pad actuator change. The mass is {{MASS}} kg against a 120 kg limit (+0.4 kg for the heavier pad actuator, not in the sim).

# 2. Gate table, before and after

Before is B as frozen at the G6 gate (`revG/sim/cg/res/gate_table.json`). The middle column is B1 with D1-D7 and F1-F7, run through the complete frozen suite (`it1/res/B1_*.json` without a tag, scored into `it1/res/gate_it1.json`). After is the final B1 with F9 added, run through the complete frozen suite again (`it1/res/B1_*_f9.json`, scored into `it1/res/gate_it1_f9.json`). Both scorecards come from `it1/summarize_it1.py`.

{{TABLE}}

Criteria file: `revG/sim/cg/CRITERIA_FROZEN.md`, sha256 2cf3f4ecdd104c6b... (matches `CRITERIA_FROZEN.sha256`). It was checked unchanged at the start of the iteration and again before the F9 runs. No threshold, test definition or bin choice was touched. All B1 changes are design and firmware only, and no firmware abort threshold was loosened to pass a test.

# 3. Changes made (each with its reason)

| # | change | type | reason (evidence) |
|---|------------------------------------|------|------------------------------------------|
| D1 | Sprung pad moved from the body (fixed at z 0.45 m) to the **lift carriage**, 0.58 m below the nib top. Face 63 mm inboard of the docked nib front; spring 30 kN/m, 300 N preload, 40 mm stroke, as before | design | Body pad hit the hull before docking (CL run 28, SL 250) and held the bin by friction at set-down (G6 s3.2). On the carriage, the pad sits at the same height relative to the lip on every bin and lowers with the comb |
| D2 | **Pad retract 40 mm** by a 24 V IP65 actuator. Retracted for the approach and from keeper-open onward; extended before the keeper closes. Part changed after the load check (section 8.2): MSW DSZY4-24-50-100-STD-IP65, 2,500 N, with a 40 mm position switch, in place of the 1 kN TRU TC24-50-1000 POT | design | The 250 mm-wheel bin stands leaning 3.8 deg, so its lower back face is ~35 mm closer to the tug than on 200 mm bins. A fixed pad cannot clear it and still hold the bin near upright. The fixed-pad variant was tried: hang tilt 5-6.7 deg and 7 of 10 set-downs HOLD (s4.2) |
| D3 | Lift stroke **250 mm**; carriage zero at nib top 0.855 m (range 0.855-1.105 m) | design | Covers rim-referenced approach for the lowest lip (ESE 240 CL rim 0.882 m) up to the highest carry (SL 250 ledge 1.033 m + lift); the model range was 0.26 m before |
| D4 | **Ballast forward**: the same 10 kg steel plate moves from the side arms at the drive axle (x 0.05 m) to the tray floor (x 0.85 m, z 0.13 m) | design | Castor lift-off about the drive axle {{HC0_LIFT}} -> {{HC1_LIFT}} deg (110 kg bin); castors carry more in every static pose; mu_req 12 % {{HC0_MU}} -> {{HC1_MU}} (hand calc) |
| D5 | Comb-plate contact switch and pad contact switch: 2 x IP67 roller-lever switches on 2 mm sprung travel | design | Inputs for the force-limited approach (F2). Motor current is kept as a back-up only: 30 N at the comb is about 2.5 N m per wheel, too small to read reliably at creep |
| F1 | Comb **pre-set to the measured lip-rim height** minus 25 mm before the approach (rear camera / comb ToF; 3 mm noise modelled) | firmware | The fixed nib height (0.865 m) sat 16-144 mm under the rim, depending on the bin (s4.1), so pick-up travel and pad engagement varied by bin |
| F2 | **Force-limited, contact-sensing final approach**: 0.06 m/s to a 60 mm gap, then a 0.03 m/s creep. Stop on ToF gap <= 4 mm, comb contact > 30 N, pad contact > 30 N, bin motion > 10 mm or bin tilt +2 deg. Lift only if the stop is ToF or comb contact with gap <= 10 mm; otherwise back off 0.4 m and re-approach once, then report | firmware | G6 approach ignored pad contact and kept driving while the bin tipped (CL run 28: tilt 0.6 -> 12.8 deg in 2 s) |
| F3 | Load-on = lift-force rise >= 60 N **and** nib seat switch (tare taken over the first 12 mm of travel); then lift +100 mm (capped at stroke end) | firmware | Pad on the carriage makes force alone ambiguous (an earlier B2 run safe-missed); +100 mm keeps the bin front clear of a 40 mm bump |
| F4 | **SD2 set-down adopted**: comb by position to the recorded pick-up height, keeper opens **and pad retracts**, comb to pick-up - 50 mm (25 mm under the rim), interlock, drive forward 0.6 m | firmware | Force-based set-down was fooled by pad friction (G6: 5/18). SD2 alone gave 11/18 at the gate; with D1/D2 it is 18/18 |
| D6 | Comb tooth **240 -> 160 mm wide**, nib **12 -> 8 mm long** (nib height 20 mm unchanged) | design | First B1 MC: WEB140 22/30 and ESE SL 26/30, 8 bins knocked over. At 2.5 deg docking yaw the 120 mm half-width put one nib end 1.3 mm under the rim (22 mm channel); the lift drove the nib into the rim bottom (474 N) and tipped the bin (`dbg_grab1_WEB3b.txt`). D6 raises the yaw tolerance from about 1.9 to 2.9 deg (worst ToF error) and from about 3 to 5 deg (nominal). Nib bearing at 2.5 kN: 2 MPa on the HDPE ledge |
| F6 | **Yaw alignment and lift aborts**: after the 0.06 m/s phase the tug stops and **pivots in place** until the dual-ToF yaw is within 0.5 deg, then creeps with yaw hold. Lift only if the measured yaw is <= 1.5 deg. Abort the lift and lower if the bin tilts > 3 deg, or if the load comes on > 12 mm below the expected ledge height (rim catch). In the funnel phase the bin-motion abort is 80 mm (as G6); 10 mm only in the creep | firmware | Same evidence as D6. The rim-referenced approach (F1) removed the 70-140 mm of free lift under the lip that hid the yaw problem at G6. The 10 mm motion limit in the funnel stopped one SL run on flare contact |
| D7 | Keeper arm **68 -> 80 mm** (reach 105.5 mm to the bar centre) | design | Second B1 MC (pass 2): ESE SL safe-missed 3 bins with small cb (0.060-0.063). The bar centre was 94 mm from the keeper hinge against a 93.5 mm reach, because the extended pad holds the bin about 1 deg more upright than the G6 body pad and moves the bar 11 mm away (`dbg_keep_SL22.txt`) |
| F7 | Pad extends **during the +100 mm lift**, before the keeper closes | firmware | Gives the bin a defined attitude before the keeper closes. On its own it did not cure the misses (D7 did); it is kept for repeatability |
| F8 | *Tried and rejected.* The 0.06 m/s phase made distance-based (25 s limit, pivot and creep only inside a 0.10 m gap); a funnel stall triggers a 0.6 m back-off aligned to the bin heading and one re-approach | firmware | Written by the previous run for the CL 10 miss. On the 9 failing indices it recovered **none**: {{F8_SUB}}. It addressed a 10 s timeout that was not the cause (section 4.5). Left in the code behind `CGB_F8=1`, off |
| F9 | **Approach heading taper and faster pivot.** The heading-offset limit of the camera-guided reverse is 10 deg far out (was 15) and tapers linearly to 2 deg between a nib gap of 0.50 m and 0.10 m. The yaw pivot may use 0.10 m/s wheel speed (was 0.04) and 12 s (was 6). All aborts are unchanged: 80 mm bin motion in the funnel, 10 mm in the creep, yaw <= 1.5 deg and lateral <= 25 mm to lift | firmware | Root cause of all 9 remaining misses (section 4.5): with k = 5 and a 15 deg limit, a 20 mm lateral error holds the tug 5.7 deg off the bin heading at the 60 mm stop; the slow pivot timed out at 1.6-5.6 deg, so the yaw interlock refused the lift. Far out, the 15 deg swing pushed light off-centre bins 80 mm on the mouth flare. Subset: {{F9_SUB}}. Then the full suite (section 2) |
| F5 | Upright interlock taken **relative to the bin's own standing tilt** (camera reference before the grab): withdraw only if the tilt is within 3 deg of it | firmware | The SL 250 stands at 3.8 deg on its own, which an absolute 4 deg test would refuse |

Model-only fix, not a design change: the bin is spawned upright in the model, so the approach now waits for it to settle before taking the camera reference. Without this, the leaning SL 250 triggered a needless back-off and a wrong tilt reference.

# 4. Grab and set-down

## 4.1 Root cause of the G1 failures (contact and geometry dumps)

`it1/dbg_app.py` logs every contact on the bin and the comb/bin geometry through the approach. The logs are `it1/res/dbg_app_CL28.txt` and `dbg_app_SL250full.txt`.

- **ESE 240 CL run 28** (empty bin, cb 74 mm, yaw +1.9 deg, camera seed 203028; reproduced exactly).
  - At a nib gap of 4 mm the body pad touched the hull (61 N).
  - The stop test only watched the nib, the tooth and the face plate, so the tug kept creeping.
  - The pad tipped the empty bin away (tilt 0.6 -> 12.8 deg in 2 s) while the nib gap grew, so the ToF stop never fired. The bin went over.
- **ESE 240 SL with 250 mm wheels**, nominal and full.
  - The bin model stands leaning 3.8 deg front-down, because the bigger wheels lift its hull front 25 mm off the ground.
  - The body pad met the hull at a nib gap of 15 mm (230-246 N), pushed the bin 27-31 mm, and the dock timed out.
  - Raising the approach height (FW2 at the gate) could not fix this, because the contact was the pad and not the comb.

Geometry check against `bins_g5.py` (`it1/geo_check.py`). Each bin was settled alone over its tolerance corners (bar height, cb, comb +/-10 mm).

{{GEOT}}

- **Nib depth.** The nib sits in a 22 mm channel between the body face and the rim. With the G6 nib (12 mm) and a docked gap of up to 7 mm (ToF 4 +/- 3 mm), the margin to the rim is only 3-9 mm at the nib centre, and docking yaw takes it away at the nib ends. That margin is what failed in the first B1 MC (s4.2). The B1 nib is 8 mm long and the tooth 160 mm wide.
- **Comb width.** The tooth (240 mm at G6, 160 mm in B1) fits every lip: 317 mm on the Weber 140, 324 mm on the ESE 140 CL, 384 mm on the 240 L bins.
- **Comb height.** The lip rim spans 0.882-1.009 m across the five bins. The G6 fixed nib-top height of 0.865 m was therefore 16-144 mm low. The rim-referenced approach (F1) plus the 250 mm stroke (D3) covers the full range with the +100 mm carry lift, capped at the stroke end for the SL 250, whose bigger wheels already give 25 mm more hull clearance.
- **Pad clearance.** At z 0.45 m the body pad was 46 mm inboard of the lip root. That left 14-23 mm on 200 mm bins and an interference of 12-17 mm on the SL 250, which is the cause above.

## 4.2 Fix and calibration (labelled calibration, not gate results)

Smoke runs (`it1/smoke_it1.py`) on nominal 5 bins x full/empty:

- **Fixed pad on the carriage, 23 mm inboard (cheapest, no actuator).** Grab 10/10, but the bins hang 5.0-6.7 deg. 7 of 10 flat set-downs HOLD. The bin lands on its front edge with the wheels 20 mm up, and the pad pressure keeps it there (`it1/dbg_sd.py`). Rejected.
- **Retractable pad (D1 + D2), adopted.** Grab 10/10, hang tilt 0.7-3.1 deg, flat set-down 10/10.
- **First B1 Monte Carlo (pass 1, with D1-D5 and F1-F5; results kept in `it1/res/calib_pass1/`).**
  - WEB140 22/30 (7 knocked over); ESE SL 26/30 (1 knocked over). Every failure was a nib-under-rim catch at a docking yaw of 2-2.5 deg, plus one funnel-contact abort.
  - The suite was stopped and D6 and F6 were added (second attempt on the grab).
  - A targeted re-run of the 15 failing indices gave WEB140 8/8 and ESE SL 6/7. The one miss (SL run 25) is safe: the keeper did not reach the bar, with no knock-over and no false hold.
  - **Pass 2** (D1-D6, F1-F6; `it1/res/calib_pass2/`): G2-G8 all passed, but G1 was stopped at WEB140 29/30 and ESE SL 20/23. Three safe misses on small-cb bins came from the keeper reach (D7). F7 alone did not fix them; D7 did (subset 11/11: SL 7/7, CL 4/4).
  - The complete suite was then re-run from scratch on B1 (D1-D7, F1-F7): G1 86/90 (WEB140 29, ESE SL 30, ESE CL 27), everything else as in the middle column of section 2.
  - F8 was tried on the failing indices and failed; F9 was found from new traces, checked on a subset, and the complete frozen suite was run a fourth time on the final B1 (D1-D7, F1-F7, F9). The gate numbers in this report come from that run.

## 4.3 Set-down matrix (G6, 18 cases)

Each cell gives three results: the G6 gate result with SD2 on the frozen hardware / B1 with F1-F7 / final B1 with F9.

{{MAT}}

The largest bin tilt at the interlock was {{REL_TILT}} deg. The largest final standing tilt was {{REL_END}} deg (the SL 250 standing on its own lean). The Weber 140 full facing uphill, open after two attempts at the gate, now passes: the pad lowers with the comb and retracts before the keeper releases the bar.

## 4.4 Extra grab runs (reported, not gating)

{{EXTRA_MC}}.

## 4.5 The last G1 misses: F8 rejected, root cause corrected, F9 adopted

After the third suite, G1 stood at 86/90: WEB140 run 22 and ESE CL runs 2 and 10 were no-docks, and CL run 24 a safe miss (the extra MCs had five more no-docks of the same kinds). All were safe.

**F8 (prepared by the previous run) failed.** On the 9 failing indices: {{F8_SUB}}. Its premise was wrong.

- The new trace `it1/res/dbg_app2_CL10.txt` logs the bin's own world displacement. In CL run 10 the 0.15 m/s phase ends at t = 9.1 s because **the bin has already been pushed 80 mm** (79 mm along the approach, bin yaw -11 deg) by the mouth flare. The 0.06 m/s phase uses the same 80 mm test, so it ends at once and the creep starts 0.72 m out. The 10 s limit never came into play.
- The push comes from the steering: the camera-guided reverse (k = 5, heading limit 15 deg) swings the tug from +3 to -14 deg relative to an empty bin offset by -79 mm, and the flare meets the bin wheel at an angle. F8 kept the same 80 mm test, so it only turned the miss into "funnel stall", and the re-approach repeated it (CL 10 and 24).

**The larger mode (7 of 9) was the yaw interlock**, from `it1/res/dbg_app3_CL2.txt` and `dbg_app3_WEB22.txt`:

- The tug reached the 60 mm stop 3.7-6.8 deg off the bin heading, because the steering law holds about 5.7 deg of heading for 20 mm of lateral error.
- The F6 pivot was limited to 0.04 m/s per wheel (0.2-0.35 deg/s) and timed out after 6 s at 1.6-5.6 deg. The creep trims only about 1 deg, so the dock yaw stayed above the 1.5 deg lift limit and the lift was refused.
- In several of these runs the first dock was well aligned but was rejected on a camera lateral reading above 25 mm (a 2-sigma camera bias), so the re-approach decided the run.

**F9** (section 3) attacks both: the heading limit is 10 deg far out and tapers to 2 deg near the bin, so the tug arrives square, and the pivot can finish. No abort threshold was changed.

- Subset of the previously failing indices plus neighbours: {{F9_SUB}}.
- Full re-run of the frozen suite with F9: G1 {{G1_POOL}} pooled; extra MCs: {{EXTRA_MC}}.

# 5. Ballast and stability

| | G6 B | B1 |
|------------------------------|--------|--------|
| Castor lift-off about the drive axle, 110 kg bin | {{HC0_LIFT}} deg | {{HC1_LIFT}} deg ({{HC160_LIFT}} deg at 60 kg) |
| Lateral tip / forward over castors / rear onto anti-tip rollers (110 kg) | 40.4 / 59.4 / 49.2 deg | {{HC1_LAT}} / {{HC1_FWD}} / {{HC1_REAR}} deg |
| mu_req on 12 % (hand calc, conservative against the sim) | {{HC0_MU}} | {{HC1_MU}} |

On a 12 % slope facing downhill, the static tilt is 6.8 deg against a castor lift-off of {{HC1_LIFT}} deg. The castors therefore stay loaded well before the anti-tip rollers (50 mm clearance) are needed. The rollers stay as the dynamic back-stop.

Sim, static on 12 % with the tug held 3 s (G8 poses, including the cross-slope both ways):

{{G8T}}

The hand-calc sweep is in `it1/res/handcalc_it1.json`. Moving the ballast further forward, to x 1.0 m, gives 24.0 deg but raises mu_req to 0.209. The drive needs 24.6 N m per wheel on 12 %, which is **{{HC1_TQ125}} N m with x1.25**, matching the 31 N m specified. The lean G8 drive (PEWM82M-320W + 3.5:1 chain) gives 34.8 N m at 17 A.

# 6. The 40 mm full-width step

| option | sim | cost | capability kept |
|--------------------------|-----------------------------|----------|-----------------|
| As built (330 mm drive, castors) | stops at {{STEP_B}}, drive wheels at the edge | - | no (full-width sharp steps) |
| **Kerb ramp 1:4 on each surveyed step (chosen)** | {{STEP_RAMP}} | EUR 20-40 per step, lane prep | yes, on the surveyed lane |
| 560 mm drive wheels (chain ratio x1.7, so the torque cap scales to 102 N m; servo gain re-tuned) | {{STEP_RW}} | wheels + sprockets + frame change | no: 560 mm is exactly the mu 0.6 limit; about 700 mm would be needed |
| 4WD (driven front wheels in place of castors) | not simulated | about EUR 300-450 (2 motors, controller channel, wheels) | yes, plus mass and a skid-steer pivot |

**Decision: ramps.** A ramp is cheaper than any hardware route unless the lane has more than about 10 sharp full-width steps. It is also the only option that passes in the sim.

- **Lane-prep item:** survey every full-width step over 25 mm in the wheel tracks. Fit a rubber kerb ramp or a cold-lay asphalt fillet at 1:4 or flatter to each one.
- **Route file:** mark the ramped steps, set 0.3 m/s over them, and refuse unsurveyed steps that the lidar or camera sees.
- **One-side steps** (one wheel only) still pass G3(a) without a ramp.

# 7. Final suite, timestep repeats and perturbations

The complete frozen suite was run on the final B1 (G1-G9, with F9). The three half-timestep repeats (G7, dt 0.25 ms: climb mu 0.25 crr 0.09, one-side step, e-stop) are in the table in section 2.

**Perturbation runs.** Each is a reduced suite on the final B1 (with F9; tags `_pm110f9`, `_pm090f9`, `_pmu085f9`, `_pcrr09f9`). Mass +/-10 % (tug and bin) counts as two runs, so the brief's three perturbations give four columns of runs. These are reported, not gating.

{{PTT}}

Notes:

- The G1 column uses 10 runs per bin (seeds 301-303).
- G6 covers the six cases that were hardest at the gate.
- G8 covers 12 % up at 110 kg, cross-slope at 110 kg and 12 % down at 60 kg.
- Friction -15 % scales every contact friction, including the climb mu (0.22 -> 0.19).
- Bin crr 0.09 forces the bin-wheel rolling resistance to 0.09 in every test.

# 8. Updated B spec (B1)

## 8.1 Geometry

| item | value |
|------------------------|-------------------------------------------|
| Overall | nose (bumper) x +1.09 m, tail x -0.37 m from the drive axle; width 0.76 m body / 0.96 m over the anti-tip rollers |
| Drive | 2 x 330 mm wheels, track 0.80 m (centres y +/-0.40); the bin rides between them, its wheels about on the drive axle |
| Castors | 2 x 200 mm at x 0.95 m, y +/-0.28 m |
| Straddle opening | UHMW guards at y +/-0.358 m (716 mm clear) from x -0.30 to +0.38 m, 30 deg flares at the mouth |
| Anti-tip rollers | x -0.33 m, y +/-0.44 m, about 50 mm off the ground |
| Comb | face plate at x 0.415 m; tooth 130 x 160 x 10 mm S355 with an 8 mm long x 20 mm high nib; 2 ToF sensors at the tooth ends (yaw and gap); contact switch on the sprung comb plate; keeper fingers at y +/-0.10 m on an 80 mm arm, GR-07 cam motor |
| Lift | 2 x 1 m linear rails, carriage nib top 0.855-1.105 m (stroke **250 mm**) |
| Pad | on the carriage, centre 0.58 m below the nib top, 300 x 100 mm UHMW face, 63 mm inboard of the docked nib front, retract 40 mm; die springs 30 kN/m, 300 N preload, 40 mm stroke |
| Ballast | 10 kg steel plate on the tray floor at x 0.85 m |
| Mass | {{MASS}} kg operating, including ballast (limit 120) |

## 8.2 Actuators and drive

- **Lift actuator.** Stroke 250 mm. Static load about 1.15 kN (110 kg bin plus a 5.1 kg carriage).
  - Sim peak {{LIFTPK05}} N at dt 0.5 ms, up to {{LIFTPK}} N including the dt 0.25 ms repeat. The peaks come on the one-side step; the model caps at 3 kN.
  - Spec: dynamic push at least 1.5 kN; holding or back-drive at least 4 kN (self-locking screw); 20-30 mm/s; IP65 or better; cold-rated; limit switches or a pot.
  - The G8 FDI 4 kN IP65 family is the lean choice, in a 250 or 300 mm stroke.
- **Pad actuator: rating exceeded, part changed.**
  - Peak pad contact load over every B1 result file: **{{PADPK}} N** ({{PADPKF}}, mass +10 %, F1-F7). Final firmware: {{PADF9}} N with mass +10 % ({{PADF9F}}), {{PADNOM}} N nominal ({{PADNOMF}}). The peaks come on the one-side step and the tow-stability run, with the pad extended and still, so the screw holds them.
  - The TRU Components TC24-50-1000 POT is rated 1,000 N with no published holding force. **Exceeded.**
  - **New part: MSW Drive System Europe DSZY4-24-50-100-STD-IP65** (part 00070063, Conrad item 1386475): 24 V, 100 mm stroke (40 mm used), **2,500 N dynamic, 4,500 N static** (datasheet), IP65, self-locking ACME screw, -20 to +65 C, 0.97 kg. **EUR 389.00** incl. VAT, in stock: <https://www.conrad.com/en/p/drive-system-europe-by-msw-linear-actuator-dszy4-24-50-100-std-ip65-00070063-stroke-length-100-mm-thrust-2500-n-24-v-dc-1-1386475.html> (datasheet: <https://asset.conrad.com/media10/add/160267/c1/-/en/001386475DS02/tehnicni-podatki-1386475-elektricni-cilinder-24-vdc-dolzina-hoda-100-mm-2500-n-drive-system-europe-dszy4-24-50-100-ip65.pdf>).
  - Margin on {{PADPK}} N: 2.2x dynamic, 3.9x static.
  - The STD version has end-of-stroke switches only, so a roller-lever switch marks the 40 mm extended position (EUR 8, estimate). The current limit stays as a back-up.
  - It runs at 4.4-6 mm/s, so 40 mm takes 7-9 s. The firmware waits for the switch (section 8.4). The sim pad is a fast position servo, so this time is not in the sim phases; the end states are the same because the pad moves only while the bin is held by the comb or standing on its wheels.
  - Cheaper alternative shown on the same Conrad page: TRU Components TC24-100-2500 (2,500 N, 100 mm, IP65, 6 mm/s, EUR 93.99). No holding force is published, so it needs a bench hold test before it can replace the DSZY4.
- **Drive.** 24.6 N m per wheel on 12 % at 0.5 m/s with a 110 kg bin, so **31 N m per wheel** continuous with x1.25.
  - The full-width step is not a torque case (section 6).
  - The lean PEWM82M-320W + 3.5:1 chain gives 34.8 N m at 17 A, within the RoboClaw 2 x 30 A.

## 8.3 Parts removed and added versus G6 (concept A tow) and versus the G6-gate B

- **Removed versus G6 (as at the gate):**
  - kingpin kit, yaw-lock pin and AS5600, yaw stops;
  - twin-hook carriage, latch pawls, mast rest stop, lid finger, release cord, float ratchet, GR-08S solenoid and driver, GH-B5F upgrade, feeler sensors;
  - in fabrication: rear frame, tilting mast, funnel arms, spine and drop leg.
  The tilt-mast actuator becomes the vertical lift actuator.
- **Added versus G6 (as at the gate):**
  - 2 x 1 m linear rails and 4 carriages;
  - comb tooth with nib and keeper fingers (GR-07 reused);
  - sprung pad;
  - lip ToF and nib seat switch;
  - side arms in RHS 80x60x4, lifter mast, 0.80 m axle beam;
  - 10 kg steel ballast plate.
- **New in B1 (iteration 1):**
  - D1, the pad arm on the carriage (same steel);
  - D2, the pad retract actuator MSW DSZY4-24-50-100-STD-IP65, EUR 389.00 at Conrad (fetched 11 Nov; replaces the TRU TC24-50-1000 POT at EUR 81.99), plus a 40 mm position switch (EUR 8, estimate);
  - D5, two contact switches (EUR 16, estimate);
  - D7, the keeper arm lengthened to 80 mm (same part, re-drawn);
  - D6, the comb narrowed to 160 mm with an 8 mm nib (same plate), plus a second comb ToF for the yaw measurement in F6 (EUR 10, estimate);
  - D4, the ballast plate moved to the tray (no cost);
  - D3, the lift stroke set to 250 mm (no cost change; G8 priced the 400 mm unit as an upper bound).
- **Cost delta:** EUR {{COST_DELTA}} all-in, including EUR 19.99 Conrad shipping and the G8 contingency rule (`it1/res/cost_it1.json`). New total **EUR {{COST_NEW}} plus ramps**; with the TRU actuator it was EUR {{COST_OLD}} (`it1/res/cost_it1_preF9pad.json`).

## 8.4 Firmware sequence (approach, lift, carry, set-down) with interlocks

1. **Pre-approach** (at about 1.2 m, tug square to the bin's handle side).
   - The rear camera reads the bin's standing tilt (reference for I6) and the lip-rim height.
   - Pad retracted (end-of-stroke switch). Keeper open.
   - Comb moves to rim - 25 mm. If the measured rim is outside 0.85-1.03 m, abort with "unknown bin".
2. **Approach.** Camera-guided reversing at 0.15 m/s until the nib gap is under 0.20 m (abort if the bin moves 80 mm). Then 0.06 m/s to a 60 mm gap.
   - *F9:* the steering may hold the tug at most 10 deg off the bin heading far out; the limit tapers linearly to 2 deg between a nib gap of 0.50 and 0.10 m.
   - **Stop and pivot in place** (up to 0.10 m/s per wheel, 12 s) until the dual-ToF yaw is within 0.5 deg.
   - Then a **0.03 m/s creep** with yaw hold.
3. **Stop** on the first of these:
   - ToF gap <= 4 mm (dock);
   - comb contact switch, over 30 N (dock if the gap is <= 10 mm);
   - pad contact switch;
   - bin motion over 10 mm or bin tilt +2 deg (camera);
   - overrun 30 mm.
   - *I1:* lift only after a dock stop with the gap <= 10 mm, measured yaw <= 1.5 deg and a lateral offset <= 25 mm. Otherwise back off 0.4 m and re-approach once. A second failure is reported as "no dock". Never push on.
4. **Lift.** Tare the lift load cell over the first 12 mm of travel. Load-on = rise >= 60 N **and** nib seat switch closed (*I2*).
   - *I2b:* load-on more than 12 mm below the expected ledge height (measured rim + 25 mm) is a rim catch. A bin tilt of more than 3 deg during the lift also aborts. Either way: stop, lower to the approach height, back off, re-approach once.
   - Record the pick-up height zc, then lift to zc + 100 mm (capped at the stroke end).
5. **Secure.** The pad extends during the +100 mm lift; the keeper closes on the bar only when the pad's 40 mm switch is made (7-9 s with the DSZY4).
   - *I3*, claim = lift rise >= 60 N AND seat switch AND keeper on the bar. Otherwise: keeper open, pad retract, comb back to the approach height, back off, one retry, then report.
6. **Carry.**
   - Speed limit 0.5 m/s, 0.3 m/s on surveyed ramps and over 8 % grade. Pivot on the spot at 0.25 m/s per wheel.
   - *I4:* seat switch and keeper must stay made. If either opens, e-stop. Lift motion inhibited while driving.
   - *I5:* tilt switch and IMU (> 15 deg) feed the stop loop.
7. **Set-down.** Stop. If the bin must face the lane, **pivot in place** first.
   - Comb by position to zc (the bin's wheels land).
   - Keeper opens and the pad retracts (end-of-stroke switch, 7-9 s).
   - Comb to zc - 50 mm.
   - *I6:* the bin tilt must be within 3 deg of its pre-grab reference, and the lift force must be at its unladen tare. Otherwise HOLD, re-lift to zc + 20 mm, retry once, then report.
   - Drive forward 0.6 m at 0.15 m/s. *I7:* ToF confirms the nib is more than 100 mm clear before the tug turns.
8. **Faults.**
   - Actuator over-current or position error stops the lift (no forced moves).
   - E-stop holds the actuator position (self-locking screw).
   - A dead pack is handled through the Anderson aux socket and a hold-to-run pendant (as G8).

# 9. What the SITL lane model needs changed for B

- **Vehicle.** A carrier, not a tug plus a towed bin.
  - Remove the hitch and kingpin articulation, the towed-bin trailer dynamics and the jack-knife checks.
  - The footprint is the tug plus the carried bin inside the straddle: about 1.46 x 0.96 m.
- **Turning.** Pivot on the spot. The 180 deg pivot sweeps {{SWEPT}} m diameter with a 240 L bin carried. Replace the three-point and yard U-turn manoeuvres with pivots wherever the lane gives that circle, and keep 0.10 m truth clearance to the hedge.
- **Pickups.** No relay flip.
  - B approaches any standing bin from its handle side, so the bin's yaw on the pad does not matter if there is about 1.6 m clear behind the handle.
  - Add a check per drop spot that this approach space exists.
- **Set-down with the handle toward the lane** becomes a pivot in place before set-down. Delete the relay-flip set-down branch.
- **Release outcome table.** Use the B1 matrix of section 4.3: 18/18 on flat and on 12 % up and down, full and empty. This replaces the tow release table (review M4).
- **Approach branches.** Add the contact-abort, back-off and single re-approach path, and the "no dock" and "unknown bin" reports. Add the set-down HOLD and retry path.
- **Steps.** Use a route attribute for ramped steps. Refuse any unsurveyed full-width step over 25 mm (no climb attempt).
- **Timing.** Pick-up takes about 30-40 s and set-down about 15-20 s, from the sim phases, plus about 5 s at pick-up and 8 s at set-down for the slower DSZY4 pad actuator. The 180 deg pivot takes about 10 s; the F9 yaw pivot at the bin up to 12 s.
- **Approach model.** Use the F9 steering (heading limit 10 deg tapering to 2 deg over the last 0.4 m) and the dock yaw interlock (<= 1.5 deg) with one re-approach; the no-dock rate from G1 is the outcome table.

# 10. Open items and risks

| # | item | severity | next step |
|---|------------------------------|--------|------------------------------|
| 1 | G3(b) full-width sharp step fails as frozen (physics of 2WD plus castors) | high on lanes with such steps | lane survey; ramps (EUR 20-40 each); 4WD only if there are many steps |
| 2 | Bin models are bins_g5. The SL 250 lean (hull front 25 mm off the ground) may not match a real 250 mm-wheel bin, which has taller front feet | medium | measure Brian's bins: lip height, back-face profile, standing tilt |
| 3 | Pad actuator: suite peak {{PADPK}} N exceeded the 1 kN TRU unit; changed to the 2.5 kN / 4.5 kN static DSZY4 (EUR 389) | closed in design; low | bench check the 40 mm switch and the 7-9 s cycle; optional hold test of the EUR 94 TRU TC24-100-2500 |
| 4 | Contact peaks (lift, nib on rim) are not timestep-converged (review m6) | low-medium | x2.5 sizing factor kept |
| 5 | HDPE lip life under the 8 mm nib with the comb peaks | medium | scrap-bin field test |
| 6 | Camera/ToF lip-height measurement is modelled at 3 mm sigma, not tested | medium | bench test on the three bin types |
| 7 | F9 steering and pivot are sim-tuned on bins_g5 models with a modelled camera (8 mm) and dual-ToF yaw (1 deg) | medium | yard test with the three bin types, including far off-centre empty bins |

# 11. Method, deviations and files

**Method.**

- MuJoCo, one process at a time at nice 10, PYTHONPATH /workspace/work/pylib.
- dt 0.5 ms, with 0.25 ms for the G7 repeats.
- Bin models bins_g5. The frozen common model terms are unchanged.
- G1 uses the gate seeds 201-203. Extra MCs use seeds 204-205, perturbations 301-303.

**Deviations.**

- The sandbox rebooted at about 10:15 +03 and again before 11:47 +03. Each time the queue was restarted in-session; it skips finished runs. The run interrupted by the second reboot (a mass +10 % static) was re-run.
- A few calibration smokes and diagnostics were run through the same queue before the suite. They are labelled calibration, not gate results.
- The 560 mm wheel run also re-tuned the drive servo gain and the torque cap with the chain ratio. That is a sensitivity run only; the frozen common term stays at 60 N m.
- The perturbations are reduced suites (section 7), not the full G1-G9.
- The first two full B1 suites were stopped part-way through G1 when the grab MC failed. Their results are kept as calibration in `res/calib_pass1/` and `res/calib_pass2/`. The third, complete run (F1-F7) is the middle column of section 2. Every final gate number comes from the fourth, complete run with F9 (`_f9` files).
- The F1-F7 perturbation runs that had finished before F9 (mass +10 %, files with tag `_pm110`) are superseded by the F9 perturbation sets and are not reported.
- The 1:4 ramp step and the 560 mm wheel runs (section 6) were run with F1-F7; F9 only changes the approach to the bin, which in those tests is from the nominal pose.

**Files.** All under `revG/sim/cg/it1/`; the frozen gate files are untouched.

- Sim: `simB_it1.py` (D1-D7, F1-F9; F8 off, F9 by `CGB_F9=1`; pre-F9 copy `simB_it1.pre_f9.py`) and `runB_it1.py` (adds perturbations and the ramp step).
- Mass: `mass_cgB1.json`.
- Queue: `queue_it1.py`, `q3.txt`-`q9.txt` with their logs (`q9.txt.log` holds the final suite).
- Results: `res/B1_*.json`; scorecards `res/gate_it1*.json`.
- Diagnostics: `dbg_app.py`, `dbg_app1.py`, `dbg_app2.py`, `dbg_app3.py`, `dbg_grab1.py`, `dbg_sd.py`, `geo_check.py`, `smoke_it1.py`.
- Superseded results: `res/calib_pass1/`, `res/calib_pass2/`.
- Keeper diagnostic: `dbg_keep.py`.
- Hand calcs: `handcalc_it1.py`. Cost: `cost_it1.py`.
- Report builder: `make_report_it1.py` with `report_tpl_it1.md`.
- Progress log: `docs/reviews/PROGRESS_iter1.md`.
