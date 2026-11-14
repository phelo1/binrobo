# Reply to the review of revision 2, and revision 3 of the improved version

14 November 2026. For Brian and for the B2-F author, who reviewed revision 2.

I checked each finding in the review against my own files before acting on it. The reviewer's package was read, not run. Every number below comes from my own runs, on MuJoCo 4.0.1 and ArduRover 4.7.2, with the B2-F author's test scripts and my switches. The switches are listed in the evidence pack.

## Summary

- **The review is right on its main points.** Revision 2 could not have been built as drawn. The lift carriage would have hit its own limit switch and stops, the weight table left parts out, and one sentence in my report was wrong. Revision 3 fixes what is mine to fix.
- **The robot weighs 152 kg, not 119 kg.** I rebuilt the weight table from the drawing model, one row per part. The review's audit said 123 to 128 kg. This breaks the 120 kg gate limit, and a trip now takes 58 to 64 Wh against the 50 Wh limit. Both limits need Brian's decision (section 5).
- **At 152 kg revision 3 passes 8 of the 9 gate checks.** The one it fails is the weight limit itself. It lifted 180 of 180 simulated bins and held none off-centre under either width rule. All 24 stress cases pass, 9 of 10 lane runs pass, and 48 of 56 driving-software runs pass; the other 8 fail only on the 50 Wh limit.
- **The weight has one cost in capability.** With a full bin the robot can no longer drive up the sharp 40 mm step on the lane: it stalls there. At 119 kg it could. With the step ramped it passes, and with the wheel torque limit raised from 60 to 80 N m it climbs the sharp step again.
- **Two findings of mine change what the review asks for.** The heavier side rails are not needed, because the review's wheel loads come from stored runs on a simulator version with a known fault. And the castors need round-profile tyres: with the flat tread in the parts list, the robot at its real weight swings its nose 6.7° on a slippery hill start, against a limit of 5°.
- **Still open:** tests on Brian's real bins, the supplier's word that the lift actuator holds its load, the safety calculation, and three site rules (pothole filled, trench covered, step ramped).

## 1. The review's findings, one by one

| Review item | What my own check found | What I did |
|---|---|---|
| "Never lifted a bin more than 31 mm off-centre" is wrong | Correct. I had read the wrong field: where the robot stopped, not where the comb sat under the lip. Recount of all 180 revision 2 pick-ups: 178 lifted, 2 refused, **1 lifted 50.2 mm off-centre** (just outside the original 50 mm rule), none outside the 80 mm rule of the wider comb | Statement withdrawn. Every pick-up now logs where the comb sits. Revision 3 results are given under both rules (section 3.2) |
| Tip figure quoted for the wrong model | Correct. The scorer reads B2-F's file. Revision 2's own figures were 34.7° sideways and 26.2° for the castors lifting | Revision 3, from its own file: 31.9° sideways, 26.0° castor lift-off |
| Placement limit is 0.15 m, not 0.6 m | Correct | Corrected. Largest placement error in the revision 3 runs: 0.10 m |
| Least hedge clearance 0.152 m over all 60 runs | Their figure, from a firmware build I cannot run (it is for a different processor). Mine was 0.197 m over 54 runs | Accepted as theirs. Revision 3: 0.195 m over 56 runs |
| Pad is 9.8 mm behind the nib, not 11 mm | Correct | Label now says 10 mm |
| Lift top end (B-1): the carriage hits the limit switch at 300 mm and the stops at 336 mm; the clamped stops hold 2.4 kN against a 4 kN actuator | Reproduced with a new check that intersects the real solids over the whole lift travel: switch at 310 mm, stops at 338 mm | Redesigned (section 2). The new check finds nothing in the way up to the stops |
| Structure (B-2): side rails fail at the wheel edge loads; cross-member twists; floating plates | Partly. The edge loads are a simulator fault (below). The cross-member, the foot bolts and the floating parts were real gaps | Rails stay 50x50x4 but must be S355 steel. Cross-member, mast feet, pivot plates and bumper carrier redesigned and calculated (section 3.5) |
| Weight table (M-1): 123 to 128 kg | Low. Counted from the drawn parts it is 152 kg | Table rebuilt (section 3.1). Everything re-tested at that weight |
| Safety design (M-2) | Agreed. Revision 2 chained devices in series and had one tilt switch | New sheet 15: a proposal with each device on its own input pair. Targets only, no calculation |
| Actuator holding (M-6) | The supplier's page gives no holding or self-locking figure | Open. Needs the supplier's answer in writing, or a brake |
| Pad springs and bumper brackets (M-3, M-4) | Agreed. The springs drawn could not stroke 45 mm, and the brackets were a sketch | Both redesigned and drawn (section 2) |
| Report false holds under both rules; add a seating check after the lift | Agreed | Done (section 3.2) |
| Lane scoring has no time limit; driving software lacks the refusal logic | Agreed | Stuck-time score added to my lane table. Refusal, retry and drive-home logic added to my copy of the driving software (section 3.4) |
| Parts list against the BOM (14 mismatches) | Agreed | Sheet 13 corrected. Lines the BOM still needs are marked "new line needed" or "to change" |
| Test on Brian's bins | Agreed | Not something I can do. See section 5 |

### The structure loads come from a simulator fault

The review sizes the side rails for a wheel load of 7,306 N. That figure is from the B2-F author's stored runs, made on MuJoCo 3.17.0. On 13 November I showed that versions 3.13 to 3.17 treat the edge of a step as a wall (`FINDING_kerb_step_simulator_2026-11-13.md`). The stored set also holds a wheel force of 1,057,024 N in a trench run, which cannot be real.

I re-ran the B2-F author's 29 load cases on their own B2-F model, unchanged, on MuJoCo 4.0.1:

| Load | Stored (3.17.0) | Same case re-run (4.0.1) |
|---|---:|---:|
| Largest wheel force, pothole and soft-tyre kerb cases | 7,306 N | 2,394 N |
| Largest comb force, all cases but the trench | 9,634 N | 8,148 N |

The wheel loads fall to a third. The comb loads stay about the same. Revision 3 is sized on its own loads at 152 kg (section 3.5).

## 2. What changed in revision 3

- **Lift top end.** Firmware stop at 320 mm of travel (305 mm is used). Two limit switches at 327 mm, one per stop channel, tripped by tabs on the carriage plate. Bolted stop brackets at 335 mm, each with 2 M10 bolts through the upright and a tongue over the plate edge, 35 mm under the top tie. Matching stops and a switch at the bottom. The 400 mm actuator stays.
- **Carriage.** Drawn with real sizes: a 16 mm aluminium plate, two 50x50x4 steel cross-beams that carry the load to the four rail blocks, and the pad arm hung below the comb pivot. It was drawn through the pivot before.
- **Pad.** Two rods slide with the pad, and two 134 mm springs push against a fixed cup plate. The pad can now really move 45 mm: 300 N at first touch, 1.65 kN fully pushed in, as in the simulation.
- **Frame.** Side rails 50x50x4 in S355. Mast-base cross-member 50x50x5 in S355. Nose cross-member 50x50x3. Mast uprights welded to foot shoes held by four M12 bolts each. Corner plates over the four frame joints. The motor plates now end under the rail; they were drawn inside it.
- **Castor pivot.** Two 10 mm S355 plates welded to both faces of the nose cross-member, with a D20 pin.
- **Castors.** Round-profile tyres instead of the flat 50 mm tread (section 3.3).
- **Front bumper.** A bar that slides 15 mm on two sprung pins, on a carrier of two arms and drop legs between the castors. A two-contact switch at each end.
- **Ballast.** The 5 kg plate is deleted. At this weight the castors stay loaded without it.
- **Software.** A seating check after every lift: if the bin sits more than 30 mm off-centre, the robot sets it down and tries again, twice at most. In the driving software: camera error drawn afresh at every check, refusal after 3 re-alignments, and a drive home after a refused pick-up.
- **Drawings.** 16 sheets. New: sheet 15 (safety functions, stop chain, fuses and wire sizes) and sheet 16 (dimensions). 12 looms, each through a grommet, none through a part.

## 3. Results at 152.2 kg

### 3.1 Weight

| Group | kg |
|---|---:|
| Frame, mast, guards, covers (fabricated) | 73.99 |
| Bought-in units (drive units, castors, battery, electronics, sensors, actuator) | 40.41 |
| Allowances (fasteners, power box, weld and paint) | 4.70 |
| Castor beam | 6.00 |
| Lift carriage with comb and pad | 27.09 |
| **Total** | **152.19** |

Each fabricated row is the volume of the drawn part times its density (`mass_table_r3.md` in the evidence pack). The simulator model built from this table weighs 152.19 kg, so table, drawing and test agree.

Where the 34 kg over revision 2 comes from:

- lift carriage +20 kg (the old 7 kg row was never built up from the parts drawn);
- plastic side guards and anti-tip parts +3 kg (drawn 10 mm thick, weighed at almost nothing);
- frame, mast feet, castor pivot, lift stops, brackets, bumper carrier and covers +11 kg;
- fasteners, power box, weld and paint +5 kg;
- ballast -5 kg.

The same two gaps, carriage and side guards, are in B2-F's own table. B2-F as drawn is therefore also heavier than its 92 kg. I have not rebuilt its table.

### 3.2 Gate and pick-ups

The gate is the B2-F author's set of nine pass/fail checks, scored by their script.

| Check | Result | Detail |
|---|---|---|
| G1 pick-ups (90 in the gate set) | PASS | 90 of 90 lifted, no false hold, none knocked over |
| G2 climbs on low grip | PASS | 6 of 6 |
| G3 40 mm step, one side and full width | PASS | both climbed |
| G4 emergency stop on the 12 % slope | PASS | stops in 0.23 m forward, 0.11 m in reverse |
| G5 pivot turn | PASS | swept circle 2.46 m across |
| G6 set-down and release | PASS | 18 of 18 |
| G7 repeat at a finer time step | PASS | 3 of 3 |
| G8 static loads and tipping | PASS | sideways tip 31.9°, castor lift-off 26.0° |
| G9 weight at most 120 kg | **FAIL** | 152.2 kg |

Stress cases (10 % heavier, 10 % lighter, 15 % less grip, more rolling drag): 24 of 24 pass. The heavier case is 167 kg.

Pick-ups, by where the comb sat under the lip after the lift. The old rule is the width limit of the 640 mm comb, the new rule that of the 700 mm comb.

| Bin | Pick-ups | Lifted | Refused | Beyond the old rule | Beyond the new rule | Largest offset | Set down by the seating check |
|---|---:|---:|---:|---:|---:|---:|---:|
| 140 L | 30 | 30 | 0 | 0 (100 mm) | 0 (130 mm) | 15.7 mm | 0 |
| 240 L | 30 | 30 | 0 | 0 (50 mm) | 0 (80 mm) | 15.7 mm | 0 |
| 240 L clip-lid, 4 batches | 120 | 120 | 0 | 0 (50 mm) | 0 (80 mm) | 23.9 mm | 1 |
| **All** | **180** | **180** | **0** | **0** | **0** | **23.9 mm** | **1** |

Revision 2 on the same 180 samples: 178 lifted, 2 refused, 1 beyond the old rule. In 23 of the 180 revision 3 pick-ups the camera asked for a second approach before the lift.

### 3.3 Slippery hill start and the castor tyres

The B2-F author's hardest climb test starts uphill on a 12 % slope with grip 0.22, right after the pick-up. The pass rule is a heading swing of at most 5° and at least 50 N on the castors.

| Castor tyre, at 152.2 kg | Heading swing | Least castor load | Result |
|---|---:|---:|---|
| Flat 50 mm tread (the parts list) | 6.7° | 352 N | FAIL |
| Round profile, modelled as a 24 mm contact strip | 1.4° | 393 N | PASS |

For comparison, B2-F at 93 kg swings 0.3° and revision 2 at 119 kg swings 1.2°, both on the flat tread. With the round-profile tyre the other three climbs of that test set swing 1.6°, 0.3° and 0.3°.

The cause is the castors flipping round after the robot has reversed onto the bin. A flat tread scrubs sideways as it turns, and on a slippery slope the drive wheels have no grip left to hold the nose. The heavier the nose, the bigger the swing. A round-profile tyre touches on a narrow strip and turns easily.

Two limits of the tyre model:

- A fully round wheel shape in the simulator stalled at the 40 mm step. That is a fault in how the simulator handles that shape, so I did not use it.
- A wheel that is only 24 mm wide falls into the side of the open pothole and the robot then fails to dock. A real tyre is still 50 mm wide. With shoulders added to the model wheel, 3 mm lower than the centre strip, the dock works again. I checked this wheel on 32 cases: flat-ground cases are identical to the narrow wheel, step and kerb cases keep their verdicts. The main runs use the narrow wheel. The pothole load cases use the shouldered wheel.

The change in the parts list is line DRV-C7: 200 x 50 castors with a round-profile tyre, the type on powerchairs, instead of flat solid PU.

### 3.4 Lane and driving software

Lane runs with the step ramped, the trench covered and the pothole filled. The two "sharp step" rows take the ramp away. "Stuck" is the reviewer's score: the longest time the robot needs to gain 5 m, with a limit of 120 s.

| Run | Result | Energy, Wh | Stuck, s | Least hedge clearance, m |
|---|---|---:|---:|---:|
| Full 240 L bin (110 kg), home to the road | PASS | 15.4 | 58 | 0.307 |
| Return empty, road to home | PASS | 30.9 | 41 | 0.332 |
| Collect the empty 240 L bin, road to home | PASS | 32.0 | 57 | 0.341 |
| Full 140 L bin (66 kg), home to the road | PASS | 15.1 | 58 | 0.307 |
| Night run: bin 10 % heavier, load 60 mm higher, 20 % less grip | PASS | 21.8 | 58 | 0.307 |
| 12 % slope down, wet leaves, stop and hold | PASS | 0.3 | 21 | - |
| 12 % slope up, wet leaves, stop and hold | PASS | 5.8 | 29 | - |
| Sharp 40 mm step down, full bin | PASS | 0.1 | 10 | - |
| **Sharp 40 mm step up, full bin** | **FAIL: stalls at the step** | 0.7 | 30 | - |
| Person steps in on the wet descent: emergency stop | PASS | 0.2 | 18 | - |

The 58 s in the first rows is the pick-up at the start. No run is stuck anywhere near 120 s.

**The sharp step up is a cost of the weight.** Revision 2 at 119 kg climbed it. At 152 kg the robot stalls there with all three castor wheel models, so the castors are not the cause. With the wheel torque limit raised from 60 to 80 N m it climbs. The B2-F author's lane set-up already assumes a ramp at this step, and with the ramp every full-lane run above passes.

Driving software, 56 runs at 152.2 kg with the trip limit set to 65 Wh:

| | Result |
|---|---|
| Runs passing the B2-F author's scorer | 48 of 56 |
| Runs failing | 8, all on the 50 Wh trip limit and nothing else |
| Trip energy, 12 trips | 57.8 to 64.3 Wh; two trips over 60 Wh |
| Charge left after a three-bin evening | 49 % and 51 % (limit 20 %) |
| Least hedge clearance | 0.195 m |
| Largest placement error | 0.10 m (limit 0.15 m) |
| Most re-alignments in one pick-up | 2 of the 3 allowed; no refusal in the 56 runs |

Two camera stress runs on a one-bin mission:

- Camera noise 25 mm, offset 10 mm, one reading in five missing: after 3 re-alignments the robot refused the pick-up and ended on the dock. The re-alignments chased the noise: the last one took the true error from 2 mm to 54 mm.
- Constant camera offset of 60 mm: the robot lined up 44 mm off and went on. A camera cannot see its own offset. The seating check after the lift uses the comb sensors and is the backstop for this; it is in the mechanical simulation, not in the driving software.

### 3.5 Structure

Loads from my runs of the B2-F author's load cases on the revision 3 model: wheel 3,724 N in normal driving (reverse emergency stop on the slope), wheel 3,656 N at an edge (pothole), comb 4,523 N (40 mm step at 0.8 m/s), pad 1,330 N. My calculation uses their method and allowables. Target: safety factor 2.0 against yield.

| Part | Governing case | Stress, MPa | Safety factor |
|---|---|---:|---:|
| Side rail 50x50x4, S355 | wheel 3,724 N | 174 | 2.04 |
| Side rail 50x50x4, S355 | wheel 3,656 N at an edge | 171 | 2.07 |
| Carriage plate tongue, aluminium | pad 1,330 N | 98 | 2.56 |
| Actuator base bracket, 10 mm S355 | stalled actuator, 6 kN ASSUMED | 120 | 2.96 |
| Castor pivot plates, 10 mm S355 | kerb strike at 150 N m per wheel | 112 | 3.17 |
| Lift stop bolts, 2 x M10 a side | stalled actuator, 6 kN ASSUMED | 114 | 3.25 |
| Nose cross-member 50x50x3 | three times the static castor load | 68 | 3.44 |
| Rail screws M4, class 12.9 | comb 4,523 N | 290 | 3.73 |
| Mast-base cross-member 50x50x5, S355, twist | comb 4,523 N | 50 | 4.08 |
| Mast upright 80x40x4 at the foot | comb 4,523 N | 57 | 4.11 |
| Carriage cross-beam 50x50x4, S355 | comb 4,523 N | 83 | 4.29 |
| Rail block HGH15CA | 5,088 N per block | - | 4.61 |
| Mast foot bolts, 4 x M12 | comb 4,523 N | 119 | 5.38 |

All 42 yield checks in the calculation are at 2.0 or above. Three things to know:

- **The side rails are at the limit.** 60x60x4 S355 rails would give about 3.1 for 3.4 kg more.
- **One pothole run is left out of the sizing.** It gave 18.8 kN on a wheel while the robot spun round in the hole. Two repeats with slightly different wheel settings gave 2.8 and 3.1 kN. The open pothole is not a case the robot can drive through, so I list the run and do not size for it.
- **The pad springs are near their limit when fully pushed in:** 769 MPa against 925 MPa allowed for chrome-silicon spring wire (ASSUMED). At the largest pad force in the sizing runs they are at 620 MPa.

### 3.6 Drawing checks

- Every pair of parts, with and without the bin, intersected as real solids: no overlap involves a part I changed or added. 15 overlaps remain between parts of the B2-F drawing that I did not touch, for example the anti-tip roller in its bracket and the bin lid on the bin.
- Lift sweep from 0 to 340 mm in 2 mm steps: the first contact is the carriage plate on the bolted stops, at 335 mm.
- Looms: no loom centre-line passes through a solid in either pose.

## 4. What I did not do

- **Real bins.** Every pick-up is on catalogue bin shapes, not Brian's bins.
- **The castor tyre is an assumption until one is on the bench.** The 24 mm contact strip is my estimate for a round-profile 200 x 50 tyre.
- **Driving software.** 56 of the 60 runs: all 48 short scenario runs and 8 of the 12 full missions. The other four three-bin missions were not run for time. I cannot run the 4.6.2 firmware build the reviewer used.
- **The 80 N m torque limit was tried on one case only,** the sharp step up. Nothing else was run with it.
- **Open pothole and open trench were not re-run on the lane at 152 kg.** The review showed that no setting crosses the open pothole. I treat both as site rules.
- **The softer pad the review suggests (0.6 kN at full stroke) was not tested.** The pad keeps the B2-F stiffness.
- **Lane fit was not re-run.** The outline is the same as revision 2, and the pivot circle is now 2.46 m against the 2.55 m used then.
- **Reversing over a sharp 40 mm kerb with the rigid-tyre model is not climbed,** by revision 3 and by B2-F alike. With the soft-tyre model revision 3 climbs it. This case is in the load set, not in the gate.
- **The structure check is a yield check only.** No fatigue, weld-detail or buckling calculation. Steel grades and bolt classes are nominal values.
- **Safety.** Sheet 15 is a proposal with target levels. Nobody has collected the component data or done the calculation.
- **Bought-in weights are the B2-F author's figures.** The actuator's 3.5 kg is ASSUMED; a seller of the same FDI 4000 N 400 mm unit lists a package weight of 2.45 kg.
- **180 pick-ups with no off-centre lift** means the rate is probably under 2 %. It does not mean it is zero.

## 5. Decisions for Brian

1. **Weight limit.** This design cannot meet 120 kg; it weighs 152 kg. I found no reason for the 120 kg figure in the documents I have. Measured effect of the extra weight: about 7 Wh more per trip, the sideways tipping angle down from 34.7° to 31.9°, and one lost capability, the sharp step up (section 3.4). The gate's moving tests still pass, also at 10 % more weight. If there is a reason for 120 kg that the tests do not capture (pushing the robot by hand, a ramp rating, transport), please say. Otherwise I suggest a limit of 160 kg.
2. **Trip energy limit.** Trips take 58 to 64 Wh against the 50 Wh limit. I ran the driving software with 65 Wh. I suggest 70 Wh, to leave room for a trip with two re-alignments. The battery holds 480 Wh, and a three-bin evening ends at about half charge.
3. **Castor tyres.** Round-profile tyres in place of the flat tread in the parts list. Same size, similar price.
4. **Welding.** Revision 3 has welded sub-assemblies: mast feet, castor pivot plates, bumper carrier, corner plates. B2-F was meant to be bolted together by Brian. If welding by a fabricator is not acceptable, those joints need bolted versions.
5. **Site rules.** The 60 mm pothole filled and the trench covered: hard conditions for every version tested so far. And now the 40 mm step ramped: at 152 kg the robot cannot climb it sharp with a full bin, unless the drive can be allowed 80 N m at the wheel (question 9 below).
6. **The lift actuator.** Ask the supplier in writing: does it hold 1.4 kN (a full bin plus the carriage) with the power off, what is its stall force, and what is its duty cycle. If the answer on holding is no, a brake or latch is needed.
7. **The safety design** needs a qualified person before anything is built.
8. **Your bins.** The make and model moulded into each bin, a photo of the front lip with a ruler across and down it, and the weight when full. With those I can check the comb against the real lip.

## 6. For the B2-F author: facts I need for my own testing

I will do the testing myself. I need these facts and files:

1. The basis of the 120 kg limit and the 50 Wh trip limit.
2. What the 7.05 kg carriage row and the 1.60 kg "rollers, flares, guards" row of the B2-F table were built from: part sizes and materials. If the real parts are lighter than the CAD shows, the CAD needs to change, not the table.
3. Whether loads re-derived on MuJoCo 4.0.1 are accepted for the S12 sizing. The stored ones are from 3.17.0.
4. The S12 section list with weights, and the allowable stresses, as a file.
5. Any supplier statement on the actuator's holding and stall force, and the lift driver they have in mind.
6. Whether the two contactors and the power box are inside the "as B1" electronics row. I counted 1.6 kg for them separately.
7. For the castor in line DRV-C7: tread shape and swivel offset of the actual part.
8. Why the pad is 30 kN/m with 300 N preload, and whether a softer pad was ever run.
9. Whether the gearmotor, chain stage and drive controller can give 80 N m at each wheel, and for how long. The limit in the simulation is 60 N m.

## Files

- `REPLY_and_REV3_2026-11-14.md`: this note.
- `BinRobo_rev3_drawings_A3_2026-11-14.pdf`: 16 A3 sheets. `BinRobo_rev3_drawings_png_2026-11-14.zip`: the same as images.
- `rev3_files_2026-11-14.zip`: switches, command lists, every result file, the weight table, the structure calculation and the interference checks. Its `README.txt` lists the contents.

Sources:

- [FDI 4000 N 6 mm/s 24 V actuator, 400 mm (Botland)](https://botland.store/15868-linear-actuator-super-power-jack-4000n-6mms-24v-40cm-stroke.html): 3 A maximum current, package weight 2.445 kg
- [FDI linear actuator 24 V 400 mm (Anodas)](https://www.anodas.lt/en/fdi-linear-actuator-24v-400mm-6mm-s): the unit drawn; no holding or self-locking figure on the page
- [RoboClaw user manual (Basicmicro)](https://www.superdroidrobots.com/docs/roboclaw_user_manual.pdf) and [a summary of its wiring advice](https://digitalhabitat.github.io/systems/drive-system/drive-motor-controller.html): a power diode across the contactor so that braking energy can return to the battery
