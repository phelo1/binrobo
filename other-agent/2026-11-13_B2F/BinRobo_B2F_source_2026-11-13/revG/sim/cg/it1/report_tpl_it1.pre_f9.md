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

**B1 passes {{NB1}} of 9 gate items (B at the G6 gate: {{NB0}} of 9). Still failing: {{FAILS}}.** Under the frozen decision rule, B1 has **not** cleared the gate.

**Fixed in this iteration** (sections 3-5):

- **Set-down (G6): 18/18, from 5/18 (11/18 with SD2 alone).** Includes the full Weber 140 facing uphill and all six 250 mm-wheel cases. This took four changes:
  - the position-based set-down (SD2);
  - the pad on the lift carriage;
  - a 40 mm pad retract when the keeper opens;
  - an upright interlock relative to the bin's own standing tilt.
- **Stability.** The 10 kg ballast plate moves forward into the tray floor. Castor lift-off goes from {{HC0_LIFT}} to {{HC1_LIFT}} deg at 110 kg, and the castors carry more in every static pose, including the 12 % cross-slope both ways. G2, G4, G5, G7 and G8 still pass.
- **Grab safety.** No bin was knocked over and there were no false holds in {{GRAB_TOTAL}} grab runs on 5 bin types. The 250 mm-wheel ESE 240 now docks: {{SL250_MC}}, where the G6 B never docked it.

**Still failing.**

1. **G1 grab Monte Carlo: {{G1_POOL}} pooled.** That is WEB140 {{G1_WEB}}, ESE SL {{G1_SL}}, ESE CL {{G1_CL}}; the pass mark is 28/30 per bin and 87/90 pooled. Every miss is safe: the tug backs off and reports.
   - The grab had four separate root causes, found one after another:
     - the body pad touched the bin before docking (fixed);
     - a docking yaw of about 2.5 deg put the comb nib under the lip rim (fixed: narrower comb, shorter nib, pivot yaw alignment);
     - the keeper arm was 1 mm short on small-cb bins (fixed);
     - a bin far off-centre rides on the mouth flare, and my new 10 s limit on the slow approach phase gives up before the dock (open).
   - Per the brief, I stopped iterating after the third attempt and report the fourth with evidence (section 4.5).
   - A candidate fix (F8, firmware only) was run on the failing cases: {{F8_SUB}}. It still needs the full G1 re-run.
2. **G3(b), the full-width sharp 40 mm step: the vehicle stops at {{STEP_B}} with its drive wheels at the edge.** This is friction physics for two driven wheels with free castors.
   - The step needs an edge friction of 0.86 on 330 mm wheels; the test sets 0.6.
   - A 560 mm wheel sits exactly on the limit, and in the sim it still {{STEP_RW}}.
   - **Chosen fix: a kerb ramp on each surveyed step** (EUR 20-40 each, a lane-prep item). With a 1:4 ramp: {{STEP_RAMP}}.
   - The frozen G3(b) test has no ramp, so it stays FAIL as written. The criterion has not been changed.
   - The only hardware route is 4WD, roughly EUR 300-450 more. I have not simulated it.

**Cost.** Lean G8 basis, concept B: EUR {{COST_BASE}} all-in. Iteration 1 adds EUR {{COST_DELTA}}, giving **EUR {{COST_NEW}}**. Ramps are extra, at EUR 20-40 per surveyed step. The mass is {{MASS}} kg against a 120 kg limit.

# 2. Gate table, before and after

Before is B as frozen at the G6 gate (`revG/sim/cg/res/gate_table.json`). After is B1, the final design of this iteration, run through the complete frozen suite: `revG/sim/cg/it1/res/B1_*.json`, scored by `it1/summarize_it1.py` into `it1/res/gate_it1.json`.

{{TABLE}}

Criteria file: `revG/sim/cg/CRITERIA_FROZEN.md`, sha256 2cf3f4ec... It was checked unchanged at the start of this iteration. No threshold, test definition or bin choice was touched. B1 changes are design and firmware only.

# 3. Changes made (each with its reason)

| # | change | type | reason (evidence) |
|---|------------------------------------|------|------------------------------------------|
| D1 | Sprung pad moved from the body (fixed at z 0.45 m) to the **lift carriage**, 0.58 m below the nib top. Face 63 mm inboard of the docked nib front; spring 30 kN/m, 300 N preload, 40 mm stroke, as before | design | Body pad hit the hull before docking (CL run 28, SL 250) and held the bin by friction at set-down (G6 s3.2). On the carriage, the pad sits at the same height relative to the lip on every bin and lowers with the comb |
| D2 | **Pad retract 40 mm** by a 24 V, 50 mm, 1 kN IP65 mini actuator with pot feedback. Retracted for the approach and from keeper-open onward; extended after the keeper closes | design | The 250 mm-wheel bin stands leaning 3.8 deg, so its lower back face is ~35 mm closer to the tug than on 200 mm bins. A fixed pad cannot clear it and still hold the bin near upright. The fixed-pad variant was tried: hang tilt 5-6.7 deg and 7 of 10 set-downs HOLD (s4.2) |
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
  - The complete suite was then re-run from scratch on the final B1 (D1-D7, F1-F7).

## 4.3 Set-down matrix (G6, 18 cases)

Each cell gives the G6 gate result with SD2 on the frozen hardware, then the B1 result.

{{MAT}}

The largest bin tilt at the interlock was {{REL_TILT}} deg. The largest final standing tilt was {{REL_END}} deg (the SL 250 standing on its own lean). The Weber 140 full facing uphill, open after two attempts at the gate, now passes: the pad lowers with the comb and retracts before the keeper releases the bar.

## 4.4 Extra grab runs (reported, not gating)

{{EXTRA_MC}}.

## 4.5 The open G1 cause (fourth root cause), with evidence

`it1/res/dbg_app1_CL10.txt` traces ESE 240 CL run 10: empty bin, sampled offset -79 mm and yaw +2.9 deg.

- The camera-guided reverse leaves the bin 100-124 mm off the comb centre line. Its right wheel rides on the mouth flare (`binwheelR-flare1`, 18-151 N), and the tug crawls at 0.02-0.04 m/s.
- The 0.06 m/s phase then hits its 10 s limit at a nib gap of 0.72 m. The tug stops, pivots and starts the 0.03 m/s creep from 0.72 m out. There the 10 mm bin-motion abort fires on the flare contact, and the re-approach (0.4 m back-off) starts from a worse yaw (17.7 deg).
- The G6 approach had no time limit on this phase and simply kept going to the ToF stop. It docked this case.
- The other CL miss with the same signature is run 24. Run 2 failed its re-approach on yaw: the pivot left 3.5 deg against the 1.5 deg limit.
- The WEB140, SL 250 and ESE 140 CL misses are no-docks of the same kinds.

**Candidate F8 (firmware, default off in the gate runs):**

- The 0.06 m/s phase becomes distance-based (25 s limit), and the pivot and creep start only inside a 0.10 m gap.
- A funnel stall triggers a 0.6 m back-off aligned to the bin heading, then one re-approach.
- Result on the failing indices only: {{F8_SUB}}. This is not a gate result: G1 must be re-run in full with F8 before G1 can be claimed.

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

The complete frozen suite was run on B1 (G1-G9). The three half-timestep repeats (G7, dt 0.25 ms: climb mu 0.25 crr 0.09, one-side step, e-stop) are in the table in section 2.

**Perturbation runs.** Each is a reduced suite on the final B1. Mass +/-10 % (tug and bin) counts as two runs, so the brief's three perturbations give four columns of runs. These are reported, not gating.

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
- **Pad actuator.** 50 mm, 1 kN, IP65, with pot feedback. Peak pad load in the suite: {{PADPK}} N. That is above 1 kN, but it is taken by the spring and the end stop, not by the actuator screw. Spec the actuator holding force at at least 2 kN, or put a mechanical end stop in the extended position.
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
  - D2, the pad retract actuator TRU Components TC24-50-1000 POT, EUR 81.99 at Conrad (fetched 11 Nov);
  - D5, two contact switches (EUR 16, estimate);
  - D7, the keeper arm lengthened to 80 mm (same part, re-drawn);
  - D6, the comb narrowed to 160 mm with an 8 mm nib (same plate), plus a second comb ToF for the yaw measurement in F6 (EUR 10, estimate);
  - D4, the ballast plate moved to the tray (no cost);
  - D3, the lift stroke set to 250 mm (no cost change; G8 priced the 400 mm unit as an upper bound).
- **Cost delta:** EUR {{COST_DELTA}} all-in, including EUR 19.99 Conrad shipping and the G8 contingency rule (`it1/res/cost_it1.json`).

## 8.4 Firmware sequence (approach, lift, carry, set-down) with interlocks

1. **Pre-approach** (at about 1.2 m, tug square to the bin's handle side).
   - The rear camera reads the bin's standing tilt (reference for I6) and the lip-rim height.
   - Pad retracts (pot confirms 40 mm). Keeper open.
   - Comb moves to rim - 25 mm. If the measured rim is outside 0.85-1.03 m, abort with "unknown bin".
2. **Approach.** Camera-guided reversing at 0.15 m/s until the nib gap is under 0.20 m (abort if the bin moves 80 mm). Then 0.06 m/s to a 60 mm gap.
   - **Stop and pivot in place** until the dual-ToF yaw is within 0.5 deg.
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
5. **Secure.** The pad extends during the +100 mm lift (pot confirms), then the keeper closes on the bar.
   - *I3*, claim = lift rise >= 60 N AND seat switch AND keeper on the bar. Otherwise: keeper open, pad retract, comb back to the approach height, back off, one retry, then report.
6. **Carry.**
   - Speed limit 0.5 m/s, 0.3 m/s on surveyed ramps and over 8 % grade. Pivot on the spot at 0.25 m/s per wheel.
   - *I4:* seat switch and keeper must stay made. If either opens, e-stop. Lift motion inhibited while driving.
   - *I5:* tilt switch and IMU (> 15 deg) feed the stop loop.
7. **Set-down.** Stop. If the bin must face the lane, **pivot in place** first.
   - Comb by position to zc (the bin's wheels land).
   - Keeper opens and the pad retracts (pot confirms).
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
- **Timing.** Pick-up takes about 30-40 s and set-down about 15-20 s, from the sim phases. The pivot takes about 10 s.

# 10. Open items and risks

| # | item | severity | next step |
|---|------------------------------|--------|------------------------------|
| 1 | G3(b) full-width sharp step fails as frozen (physics of 2WD plus castors) | high on lanes with such steps | lane survey; ramps (EUR 20-40 each); 4WD only if there are many steps |
| 2 | Bin models are bins_g5. The SL 250 lean (hull front 25 mm off the ground) may not match a real 250 mm-wheel bin, which has taller front feet | medium | measure Brian's bins: lip height, back-face profile, standing tilt |
| 3 | Pad actuator holding force: the suite peak pad load is above the 1 kN rating | medium | end stop in the extended position, or a 2 kN unit |
| 4 | Contact peaks (lift, nib on rim) are not timestep-converged (review m6) | low-medium | x2.5 sizing factor kept |
| 5 | HDPE lip life under a 12 mm nib with the comb peaks | medium | scrap-bin field test |
| 6 | Camera/ToF lip-height measurement is modelled at 3 mm sigma, not tested | medium | bench test on the three bin types |

# 11. Method, deviations and files

**Method.**

- MuJoCo, one process at a time at nice 10, PYTHONPATH /workspace/work/pylib.
- dt 0.5 ms, with 0.25 ms for the G7 repeats.
- Bin models bins_g5. The frozen common model terms are unchanged.
- G1 uses the gate seeds 201-203. Extra MCs use seeds 204-205, perturbations 301-303.

**Deviations.**

- The sandbox rebooted once, at about 10:15 +03. The queue was restarted in-session and skips finished runs.
- A few calibration smokes and diagnostics were run through the same queue before the suite. They are labelled calibration, not gate results.
- The 560 mm wheel run also re-tuned the drive servo gain and the torque cap with the chain ratio. That is a sensitivity run only; the frozen common term stays at 60 N m.
- The perturbations are reduced suites (section 7), not the full G1-G9.
- The first two full B1 suites were stopped part-way through G1 when the grab MC failed. Their results are kept as calibration in `res/calib_pass1/` and `res/calib_pass2/`. Every gate number in this report comes from the third, complete run on the final design.

**Files.** All under `revG/sim/cg/it1/`; the frozen gate files are untouched.

- Sim: `simB_it1.py` (D1-D5, F1-F5) and `runB_it1.py` (adds perturbations and the ramp step).
- Mass: `mass_cgB1.json`.
- Queue: `queue_it1.py` and `q3.txt` with its log.
- Results: `res/B1_*.json`; scorecards `res/gate_it1*.json`.
- Diagnostics: `dbg_app.py`, `dbg_grab1.py`, `dbg_sd.py`, `geo_check.py`, `smoke_it1.py`.
- Superseded results: `res/calib_pass1/`, `res/calib_pass2/`.
- Keeper diagnostic: `dbg_keep.py`.
- Hand calcs: `handcalc_it1.py`. Cost: `cost_it1.py`.
- Report builder: `make_report_it1.py` with `report_tpl_it1.md`.
- Progress log: `docs/reviews/PROGRESS_iter1.md`.
