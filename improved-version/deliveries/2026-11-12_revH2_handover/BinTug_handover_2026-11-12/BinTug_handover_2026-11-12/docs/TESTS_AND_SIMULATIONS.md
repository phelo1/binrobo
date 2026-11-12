# Rev H2: tests and simulations still to be done

12 November 2026. Nothing below has been done. Items are in the order they should be done, because early ones can stop the project cheaply. Each has a pass mark. Do not change a pass mark after seeing a result; record a miss as a miss.

Three lists:

- **Part A.** Checks before any money is spent (B0 to B2): one afternoon.
- **Part B.** Bench and field tests on hardware (B3 to B12, F1 to F8).
- **Part C.** Simulations for the next agent (S0 to S14). MuJoCo and ArduPilot SITL were not available in the session that produced Rev H2, so none of these has been run.

Who does what: tests marked **Brian** need the real bins or the lane. Simulations need only this package plus the other agent's full archive (`BinRobo_full.zip`) for SITL.

---

## Part A. Before spending anything

| ID | Test | How | Pass mark | If it fails |
|---|---|---|---|---|
| **B0** | Which side is the comb receiver on? (**Brian**, 5 min) | On each of the three bins, find the stepped rim with ribs behind it that a truck's comb goes under. Photograph each bin from the side with the lid shut | The receiver is on the wall opposite the handle, on all three bins | If it is on the handle side, stop: Rev H2 is wrong and B2 stands. If a bin has no receiver, it is not an EN 840 bin: tell the next agent |
| **B0b** | Buy EN 840-1:2020 | From NSAI or another standards body. Read the frontal-receiver figure, dimensions 13 to 27, and the Annex B comb | The 640 x 75 mm comb plate and its teeth fit the receiver and clear the ribs (180 mm pitch, 6 mm thick) | Redraw the comb before cutting it |
| **B1** | Measure the bins (**Brian**, 1 h) | Tape, straight edge, plumb line. Fill in the table below for each bin, standing on level ground, lid shut | Comb seat height 860 to 1,030 mm. Front-wall set-back at 500 mm below the seat line between 0 and 50 mm. Width over the wheels under 640 mm | Set-back over 50 mm: lengthen the pad slots. Width over 640 mm: widen the 0.66 m slot. Then update `params.py` and re-run `hang.py` and `dock_mc.py` |
| **B2** | Proof-load the receiver on a mock comb (**Brian**, 2 h) | Clamp a 640 mm length of 50 x 6 flat, top edge rounded, to a fixed frame at lip height, with a padded board 500 mm below it set as in `DESIGN_RevH2.md` s.6. Hang each bin by its front receiver. Load in 20 kg steps to 110 kg gross (240 L) or 70 kg (140 L) with water containers or sand. Hold 10 min. Then 20 lift-and-lower cycles with a jack under the frame or by hand hoist | No whitening, cracking or permanent set. Receiver deflection under load no more than 1.5 % of its length (9 mm on 580 mm). Hang angle 2 deg or less. Bin wheels at least 60 mm clear at 100 mm lift | Do not build a rim-lifting robot for that bin. Fallback is a base cradle; tell the next agent |

Table for B1, one row per bin:

| Bin (maker, litres, year) | Comb seat height mm | Receiver width mm | Front wall behind the seat line at 450 / 500 / 550 mm below it, mm | Wheel diameter mm | Axle to front wall mm | Width over wheels mm | Width of body at 300 mm height mm | Lid overhang at the front mm |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

---

## Part B. Hardware tests

### Bench tests (stage 1 of the build)

| ID | Test | How | Pass mark | Decides |
|---|---|---|---|---|
| **B3** | Does the bin stay on the comb over bumps? | Full 240 L bin on the stage 1 robot under hand control. Drive off a 40 mm step, across a 40 mm trench and over a 40 mm batten on one side, at 0.5 and 0.8 m/s, 5 runs each. Video the receiver at 120 frames/s or more | The lip never lifts more than 5 mm off the teeth; comb-seat switches do not open; no damage to the receiver | Whether the keeper (clamp bar over the rim) is fitted |
| **B4** | Lift actuator (the other agent's test T2) | Lift a 125 kg dummy load on the carriage at 24 V and at 20 V, warm and after a night outdoors near 0 °C or colder. Then hold 165 kg unpowered for 30 min. Log current | Lifts 125 kg at 20 V cold without stalling; creep under 2 mm in 30 min; no back-drive | Whether a cheaper 3 kN unit is acceptable (saves about EUR 115) |
| **B5** | Donor drive (the other agent's test T1-D), before buying | Luggage scale and rope on the seller's driveway. Then on the bench: no-load wheel speed at 24 V, brake hold | At least 450 N drawbar pull at walking pace for 3 min. Brakes hold 470 N with the power off. Record the top wheel speed | Whether to buy that chair. If top speed is over 0.8 m/s at the 318 mm wheel, the speed monitor is not optional |
| **B6** | Weigh the robot | Bathroom scale under each wheel in turn, others packed level. Unladen, and with a full 240 L bin | Unladen 95 kg or less on 2 x 18 Ah AGM (105 kg on donor AGM). Castors carry 30 to 40 % unladen and at least 20 % with a full bin | Correct `MASS_ITEMS` and re-run everything |
| **B7** | Tilt | Jack the nose up until the castors lift, full 240 L bin on board, brakes on. Then one side until a wheel lifts. Chock everything | Castors stay down to 20 deg nose-up. No wheel lifts under 30 deg sideways | Under 20 deg: move the batteries forward |
| **B8** | Carriage | Full stroke 20 times with 110 kg on the comb, clean, then with grit on the uprights | No binding; side play under 2 mm; actuator current within 20 % of the first run | Roller layout |
| **B9** | Stop chain | Each E-stop, each bumper, the remote stop, a comb-seat switch, the tilt switch, loss of the companion heartbeat: one at a time, robot moving at 0.5 m/s on the level | Each one drops both contactors and applies the brakes; reset only by the reset button | Follow `reference/other_agent/revG/ELEC_SAFETY_G7.md` for the full list |
| **B10** | Claim logic FH1 / FH2 | Set the pad 40 mm too far back on purpose. Dock and lift a full bin | The robot lifts further until both clearance sensors read clear, or refuses the bin and lowers it. It never drives off with a wheel on the ground | Sensor position and thresholds |
| **B11** | Pad setting | After B1, set the pad as in `DESIGN_RevH2.md` s.6. Lift each bin | Hang 2 deg or less on every bin; wheel clearance 60 mm or more at 100 mm lift | One pad setting for all three bins, or a compromise |
| **B12** | Gated savings | Cat-1 modem: alerts, photo upload and two-way audio at the dock and at the road end. Harness redrawn for a single rigid body | Works at both ends of the lane | About EUR 60 and EUR 61 |

### Field tests on the lane

| ID | Test | How | Pass mark | If it fails |
|---|---|---|---|---|
| **F1** | 40 mm kerb | A 40 x 90 mm timber batten screwed down across the lane. Full 240 L bin. Nose-first at 0.5 and 0.8 m/s, square and at 15 deg, full width and one side, dry and wet. 10 runs each | 9 of 10 or better in every case; bin stays seated | Fit 1:4 ramps at the known steps (the other agent's lane-prep item). Try 80 N m torque limit and a short run-up |
| **F2** | The 12 % grade | Climb, stop and hold 5 min, descend, E-stop from 0.5 m/s going down. Dry, wet, and on wet leaves | Climbs at 0.4 m/s or more; no creep on the brakes; stops within 0.5 m | Lower the speed on the grade; check tyre pressure and tread |
| **F3** | Docking trials | 30 approaches per bin from offsets up to +/-80 mm and +/-6 deg; day, dusk and rain | 28 of 30 or better per bin; no false holds; no bin knocked over (the G1 marks) | Tune the approach; check tag placement on the bin's front face |
| **F4** | Set-down trials | Each bin, full and empty, on the level, facing up the 12 % and facing down it: 18 cases | The bin stands, does not roll, and is not dragged as the robot leaves, in all 18 | Change the set-down pad positions or the layout |
| **F5** | The narrowing | Drive through the 2.9 m section (s 500 to 516 m) with a bin; pivot 180 deg at each drop pad | At least 0.3 m to the hedge everywhere | Trim the hedge or move the pivot point |
| **F6** | A whole evening | Three bins out; next day three back. Log time and energy | Within the 156 Wh plan; no manual help | Larger battery or 0.8 m/s on the open lane |
| **F7** | Wind and slope | Leave each empty bin where the robot sets it down on a windy day | Bins stay put | Move the pads; see `bin_on_slope` in `revH2/results/statics.json` |
| **F8** | People, pets, cars | The other agent's obstacle and car-on-the-home-slot tests | As in their SITL scenarios | - |

---

## Part C. Simulations for the next agent

Set-up. The other agent's MuJoCo gate is in `reference/other_agent/revG/sim/cg/`. The frozen pass marks are in `CRITERIA_FROZEN.md` (sha256 in `CRITERIA_FROZEN.sha256`); **do not edit that file**. The runner is `cmp/runCMP.py` (sim module chosen by the environment variable `CMP_SIM`; sub-commands `grab`, `climb`, `step`, `estop`, `towstab`, `rel`, `static`; `SIM_DT=0.00025` for G7; `PERT_MASS`, `PERT_MU`, `PERT_CRR` for perturbations). Their Rev H model is `cmp/simH.py`, generated by `cmp/make_simH.py` from `it1/simB_it1.py`, and it reads my Rev H parameters from `revH_ext/revH/sim/params.py`. Their B2 model is `b2/simB2.py` with runner `b2/runB2.py`. Read `docs/reviews/PROGRESS_compare.md` and `PROGRESS_B2.md` for the exact commands they used. Needs `mujoco` and `numpy`.

| ID | Simulation | What to do | Pass mark or output |
|---|---|---|---|
| **S0** | Reproduce | Run one B2 item and one Rev H item from the reference files and compare with their stored JSON in `cmp/res/` and `b2/res/` | Same result to the stored precision. If not, stop and find out why |
| **S1** | Correct the bin model | In the bin hull (`cmp/simH.py` about line 132 and the same block in the other sim files): give the front wall the drawn taper (about 35 mm on the Craemer 240; scale the SULO and Weber drawings the same way) and put the large taper and wheel recess at the rear. Put the comb receiver on the front wall for every bin, at data-sheet height and EN 840 width. On the handle side model what is really there: a handle bar on brackets and a plain rim. Keep the old hull selectable so both can be run | A short note with the scaled drawings, and a hull check plot for each bin |
| **S2** | Build `simH2.py` | From `revH2/sim/params.py` (`ROBOT`, `MASS_ITEMS`): 640 mm self-aligning comb as in `b2/simB2.py` (yaw +/-4, roll +/-3 deg, centring springs); fixed pad 0.50 m below the comb with `pad_setback` as a parameter; comb travel 0.80 to 1.20 m; 318 mm drive wheels at 0.97 m track; 260 mm castors at x 0.82; anti-tip wheels; no keeper. Firmware: their approach steps, plus FH1 and FH2 | Model loads; mass and CG match `params.robot_mass()` to 0.5 kg and 5 mm |
| **S3** | The frozen gate on Rev H2 | G1 to G9 unchanged, on the corrected hull. Extras as they ran for B2: 30 grabs each on the 250 mm-wheel ESE 240 and the ESE 140 CL; perturbations mass +/-10 %, friction -15 %, bin-wheel crr 0.09 | Their marks: G1 28/30 per bin and 87/90, no false holds; G2 5 m in 25 s, creep under 0.05 m; G4 stop within 0.5 m; G5 swept 3.2 m or less; G6 18/18; G8 wheel loads and 20 deg tips; G9 120 kg. G3(b) is expected to fail as it does for every design |
| **S4** | Pad tolerance map | Sweep the wall-to-pad gap from -10 mm (pad proud) to +60 mm on each bin; run G1 (10 seeds) and the G6 flat cases at each | The band of pad settings that passes. This tells Brian how carefully the pad must be set, and whether one setting serves all bins |
| **S5** | Retention | Full 240 L and 140 L bins over a 40 mm step down, a 40 mm trench and a 60 mm pothole on one side, at 0.5 and 0.8 m/s, with and without a keeper | Minimum tooth engagement stays above half the tooth height; peak lip force (my rigid-tyre estimate is 3 to 6.5 x the bin weight; expect less). Feeds B3 |
| **S6** | The 40 mm kerb | G3(b) with: a compliant tyre (contact stiffness and damping matched to a 13 x 5.00-6 tyre at 1.5 to 2 bar); 0.5 and 0.8 m/s; 60 and 80 N m; nose-first and tail-first; 260 against 200 mm castors; a 1:4 ramp | Which changes pass. Published powerchair kerb ratings (70 to 75 mm on 300 mm wheels) suggest the rigid-wheel model is pessimistic |
| **S7** | Nose-light cases | 12 % climb nose-uphill at friction 0.22 to 0.30 with the bin's centre of gravity 60 mm higher than the gate model; G8 with the higher CG | Castor load stays above 50 N; heading holds within 5 deg. If not, move the batteries forward in `params.py` and repeat |
| **S8** | Lane fit | `cmp/lanefit.py` on `revH2/reference_out/RevH2_lanefit_design.json`, then `b2/lanefit_b2.py` with the B2 lane rules. Replace the plumb bin outline in the JSON with the carried pose from S3 (`cmp/dump_fp.py`). Needs `sitl/scripts_g6` and `sitl/data`, which are in the reference folder | Every station and all 12 pad sequences pass; pivot 3.2 m or less. My geometry-only figure is 2.22 m, with 0.34 m a side at the 2.9 m narrowing |
| **S9** | SITL regression | The G6 scenarios (`sitl/scripts_g6/scenarios.py`, layout `sitl/config_g6/drop_layout_default.json`) with a single rigid differential-drive body and the Rev H2 footprint: one-bin and three-bin drops and pick-ups, car on the home slot, RTK float, obstacle stops. Needs the full SITL set-up from `BinRobo_full.zip` | Their G6 scenario marks. Compare times and energy with `mission.json` (46.8 min and 45.7 Wh for one bin at 0.5 m/s) |
| **S10** | Numerical checks | G7 time-step repeat; sensitivity of G1 and S5 to the comb-lip contact parameters (`solref`, `solimp`, friction 0.25 to 0.45) | Results do not flip within the range |
| **S11** | B2 on the corrected bin | Run B2's G1, G5 and G6 on the S1 hull, docking on the handle side as designed | Shows what B2's comb engages on a real bin. Needed for a fair final choice |
| **S12** | Structure | Take peak wheel, comb and pad forces from S3, S5 and S6. Check side-rail bending (hand calc safety factor 1.64 at 3 g), mast-foot bolts, comb plate and pivot block, roller contact stress, castor outriggers | Safety factor 2 or more on yield at the simulated peaks, or thicker section (50 x 50 x 4) |
| **S13** | Energy and heat | Motor current and battery energy for a three-bin evening at 0 °C on the lane profile, donor AGM and 2 x 18 Ah | Within the plan; motor current under the controller's continuous rating on the 12 % |
| **S14** | Cost | Re-run `bom_revH2.py` after any design change and after price checks. Ask B2's authors to confirm the duplicate actuator line | An updated all-in figure with the share of checked prices stated |

## What has been done already, so it is not repeated

Reduced-order results in `revH2/RESULTS_H2.md`: hang geometry for seven bins; climb, kerb, E-stop and static items against the frozen thresholds in a model without contact or yaw; obstacle sweeps; grades; lift and frame statics; a docking tolerance stack; evening timing and energy; the parts list on the G8 basis. Treat all of it as an indication to be confirmed by S3 to S9, not as gate results.
