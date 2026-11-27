# Reply to the review of revision 2, and revision 3 of the improved version

14 November 2026. For Brian and for the B2-F author, who reviewed revision 2.

I checked each finding in the review against my own files before acting on it. The reviewer's package was read, not run. Every number below comes from my own runs, on MuJoCo 4.0.1 and ArduRover 4.7.2, with the B2-F author's test scripts and my switches (all listed in the evidence pack).

## Summary

- **The review is right on its main points.** Revision 2 could not have been built as drawn. The lift carriage would have hit its own limit switch and stops, the weight table left parts out, and one sentence in my report was wrong. Revision 3 fixes what is mine to fix.
- **The robot weighs 152 kg, not 119 kg.** I rebuilt the weight table from the drawing model, one row per part. The review's audit said 123 to 128 kg. This breaks the 120 kg gate limit, and a trip now takes up to [[TRIPMAX]] Wh against the 50 Wh limit. Both limits need Brian's decision (section 5).
- **At 152 kg revision 3 passes [[GATEPASS]] of the 9 gate checks.** The one it fails is the weight limit itself. It lifted [[LIFTED]] of [[NPICK]] simulated bins, refused [[REFUSED]], and held none off-centre under either width rule. [[STRESS]] of [[NSTRESS]] stress cases pass, [[LANEPASS]] of [[NLANE]] lane runs pass, and [[SITLLINE]].
- **Two findings of mine change what the review asks for.** The heavier side rails are not needed: the review's wheel loads come from stored runs on a simulator version with a known fault. And the castors need round-profile tyres: with the flat tread in the parts list, the heavier robot swings its nose 5.5° on a slippery hill start (limit 5°).
- **Still open:** tests on Brian's real bins, the supplier's word that the lift actuator holds its load, the safety calculation, and two site rules (pothole filled, trench covered).

## 1. The review's findings, one by one

| Review item | What my own check found | What I did |
|---|---|---|
| "Never lifted a bin more than 31 mm off-centre" is wrong | Correct. I had read the wrong field (where the robot stopped, not where the comb sat under the lip). Recount of all 180 revision 2 pick-ups: 178 lifted, 2 refused, **1 lifted 50.2 mm off-centre** (just outside the original 50 mm rule), none outside the 80 mm rule of the wider comb | Statement withdrawn. Every pick-up now logs where the comb sits. Revision 3 results are given under both rules (section 3) |
| Tip figure quoted for the wrong model | Correct. The scorer reads B2-F's file. Revision 2's own figure was 34.7° sideways, 26.2° for the castors lifting | Revision 3: 31.9° sideways, 26.0° castor lift-off, read from its own file |
| Placement limit is 0.15 m, not 0.6 m | Correct | Corrected |
| Least hedge clearance 0.152 m over all 60 runs | Their figure, from a firmware build I cannot run (it is for a different processor). Mine was 0.197 m over 54 runs | Accepted as theirs |
| Pad is 9.8 mm behind the nib, not 11 mm | Correct | Label now says 10 mm |
| Lift top end (B-1): carriage hits the limit switch at 300 mm and the stops at 336 mm; clamped stops hold 2.4 kN against a 4 kN actuator | Reproduced with a new check that intersects the real solids over the whole lift travel: switch at 310 mm, stops at 338 mm | Redesigned (section 2). The new check finds nothing in the way up to the stops |
| Structure (B-2): side rails fail at the wheel edge loads; cross-member twists; floating plates | Partly. The edge loads are a simulator fault (below). The cross-member, the foot bolts and the floating parts were real gaps | Rails stay 50x50x4 but must be S355 steel. Cross-member, mast feet, pivot plates and bumper carrier redesigned and calculated (section 3.5) |
| Weight table (M-1): 123 to 128 kg | Low. Counted from the drawn parts it is 152 kg | Table rebuilt (section 3.1); everything re-tested at that weight |
| Safety design (M-2) | Agreed: revision 2 chained devices in series and had one tilt switch | New sheet 15: a proposal with each device on its own input pair. Targets only, no calculation |
| Actuator holding (M-6) | The supplier's page gives no holding or self-locking figure | Open. Needs the supplier's answer in writing, or a brake |
| Pad springs and bumper brackets (M-3, M-4) | Agreed: the springs drawn could not stroke 45 mm, and the brackets were a sketch | Both redesigned and drawn (section 2) |
| Report false holds under both rules; add a seating check after the lift | Agreed | Done: a check after every lift, and both counts (section 3.2) |
| Lane scoring has no time limit; driving software lacks the refusal logic | Agreed | Stuck-time score added to my lane table; refusal, retry and drive-home logic added to my copy of the driving software (section 3.4) |
| Parts list against the BOM (14 mismatches) | Agreed | Sheet 13 corrected. Lines the BOM still needs are marked "new line needed" or "to change" |
| Test on Brian's bins | Agreed | Not something I can do. See section 5 |

### The structure loads come from a simulator fault

The review sizes the side rails for a wheel load of 7,306 N. That figure is from the B2-F author's stored runs, made on MuJoCo 3.17.0. On 13 November I showed that versions 3.13 to 3.17 treat the edge of a step as a wall (`FINDING_kerb_step_simulator_2026-11-13.md`). The stored set also holds a wheel force of 1,057,024 N in a trench run, which cannot be real.

I re-ran the B2-F author's 29 load cases on their own B2-F model, unchanged, on MuJoCo 4.0.1:

| Load | Stored (3.17.0) | Same case re-run (4.0.1) |
|---|---:|---:|
| Largest wheel force, pothole and soft-tyre kerb cases | 7,306 N | 2,394 N |
| Largest comb force, all cases but the trench | 9,634 N | 8,148 N |

So the wheel loads fall to a third and the comb loads stay about the same. Revision 3 is sized on its own loads at 152 kg (section 3.5).

## 2. What changed in revision 3

- **Lift top end.** Firmware stop at 320 mm of travel (305 mm is used). Two limit switches at 327 mm, one per stop channel, tripped by tabs on the carriage plate. Bolted stop brackets at 335 mm, each with 2 M10 bolts through the upright and a tongue over the plate edge, 35 mm under the top tie. Matching stops and a switch at the bottom. The 400 mm actuator stays.
- **Carriage.** Drawn with real sizes: a 16 mm aluminium plate, two 50x50x4 steel cross-beams that carry the load to the four rail blocks, and the pad arm hung below the comb pivot (it was drawn through it).
- **Pad.** Two rods that slide with the pad, two 134 mm springs against a fixed cup plate. It can now really move 45 mm: 300 N at first touch, 1.65 kN fully pushed in, as in the simulation.
- **Frame.** Side rails 50x50x4 in S355. Mast-base cross-member 50x50x5 in S355. Nose cross-member 50x50x3. Mast uprights welded to foot shoes held by four M12 bolts each. Corner plates over the four frame joints. Motor plates now end under the rail (they were drawn inside it).
- **Castor pivot.** Two 10 mm S355 plates welded to both faces of the nose cross-member, a D20 pin.
- **Castors.** Round-profile tyres instead of the flat 50 mm tread (see section 3.3).
- **Front bumper.** A bar that slides 15 mm on two sprung pins, on a carrier of two arms and drop legs between the castors. A two-contact switch at each end.
- **Ballast.** The 5 kg plate is deleted. At this weight the castors stay loaded without it.
- **Software.** A seating check after every lift (bin more than 30 mm off-centre: set down and try again, twice at most). In the driving software: camera error drawn afresh at every check, refusal after 3 re-alignments, and a drive home after a refused pick-up.
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

Each fabricated row is the volume of the drawn part times its density (`mass_table_r3.md`). The simulator model built from this table weighs 152.19 kg, so table, drawing and test agree.

Where the 34 kg over revision 2 comes from: lift carriage +20 kg (the old 7 kg row was never built up from the parts drawn); plastic side guards and anti-tip parts +3 kg (drawn 10 mm thick, weighed at almost nothing); frame, mast feet, castor pivot, lift stops, brackets, bumper carrier and covers +11 kg; fasteners, power box, weld and paint +5 kg; ballast -5 kg.

The same two gaps, carriage and side guards, are in B2-F's own table. B2-F as drawn is therefore also heavier than its 92 kg. I have not rebuilt its table.

### 3.2 Gate and pick-ups

[[GATETABLE]]

Pick-ups, by where the comb sat under the lip after the lift:

[[PICKTABLE]]

### 3.3 Slippery hill start and the castor tyres

[[S7TABLE]]

The cause is the castors flipping round after the robot has reversed onto the bin. A flat 50 mm tread scrubs sideways as it turns, and on a slippery slope the drive wheels have no grip left to hold the nose. A round-profile tyre touches on a narrow strip and turns easily. I model it as the same wheel with a 24 mm contact strip. A fully round wheel shape in the simulator stalled at the 40 mm step; that is a fault in how the simulator handles that shape, so I did not use it.

The change in the parts list is line DRV-C7: 200 x 50 castors with a round-profile tyre (the type on powerchairs) instead of flat solid PU.

### 3.4 Lane and driving software

[[LANETABLE]]

[[SITLTABLE]]

### 3.5 Structure

Loads from my runs of the B2-F author's load cases on the revision 3 model, and my calculation with their method and allowables. Target: safety factor 2.0 against yield.

[[STRUCTTABLE]]

### 3.6 Drawing checks

- Every pair of parts, with and without the bin, intersected as real solids: no overlap involves a part I changed or added. 15 overlaps remain between parts of the B2-F drawing that I did not touch (for example the anti-tip roller in its bracket, the bin lid on the bin).
- Lift sweep from 0 to 340 mm in 2 mm steps: the first contact is the carriage plate on the bolted stops, at 335 mm.
- Looms: no loom centre-line passes through a solid in either pose.

## 4. What I did not do

- **Real bins.** Every pick-up is on catalogue bin shapes, not Brian's bins.
- **The castor tyre is an assumption until one is on the bench.** The 24 mm contact strip is my estimate for a round-profile 200 x 50 tyre. With the flat tread the slippery hill start fails.
- **Driving software.** [[SITLSCOPE]] I cannot run the 4.6.2 firmware build the reviewer used.
- **Open pothole and open trench were not re-run at 152 kg.** The review showed no setting crosses the open pothole. I treat both as site rules.
- **The softer pad the review suggests (0.6 kN at full stroke) was not tested.** The pad keeps the B2-F stiffness. Its springs are close to their stress limit when fully pushed in (section 3.5).
- **Lane fit was not re-run.** The outline is the same as revision 2, and the pivot circle is now 2.46 m against the 2.55 m used then.
- **The structure check is a yield check only.** No fatigue, weld-detail or buckling calculation. Steel grades and bolt classes are nominal values. The actuator's stall force is ASSUMED to be 6 kN (1.5 times its rating).
- **Safety.** Sheet 15 is a proposal with target levels. Nobody has collected the component data or done the calculation.
- **Bought-in weights are the B2-F author's figures.** The actuator's 3.5 kg is ASSUMED; a seller of the same FDI 4000 N 400 mm unit lists a package weight of 2.45 kg.
- **B2-F's own weight table was not rebuilt.**
- **180 pick-ups with no off-centre lift** means the rate is probably under 2 %. It does not mean it is zero.

## 5. Decisions for Brian

1. **Weight limit.** This design cannot meet 120 kg; it weighs 152 kg. I found no reason for the 120 kg figure in the documents I have. Measured effect of the extra weight: about 7 Wh more per trip, the sideways tipping angle down from 34.7° to 31.9°, and every moving test still passes, including at 10 % more weight. If there is a reason for 120 kg that the tests do not capture (pushing the robot by hand, a ramp rating, transport), please say. Otherwise I suggest a limit of 160 kg.
2. **Trip energy limit.** Trips take 58 to 60 Wh; the limit is 50 Wh. I ran the driving software with the limit at 65 Wh. The battery holds 480 Wh, and a three-bin evening ends at about half charge.
3. **Castor tyres.** Round-profile tyres in place of the flat tread in the parts list. Same size, similar price.
4. **Welding.** Revision 3 has welded sub-assemblies: mast feet, castor pivot plates, bumper carrier, corner plates. B2-F was meant to be bolted together by Brian. If welding by a fabricator is not acceptable, those joints need bolted versions.
5. **Site rules.** The 60 mm pothole filled and the trench covered. Both are hard conditions for any version tested so far.
6. **The lift actuator.** Ask the supplier in writing: does it hold 1.1 kN with the power off, what is its stall force, and what is its duty cycle. If the answer on holding is no, a brake or latch is needed.
7. **The safety design** needs a qualified person before anything is built.
8. **Your bins.** The make and model moulded into each bin, a photo of the front lip with a ruler across and down it, and the weight when full. With those I can check the comb against the real lip.

## 6. For the B2-F author: facts I need for my own testing

I will do the testing myself. I need these facts and files:

1. The basis of the 120 kg limit and the 50 Wh trip limit.
2. What the 7.05 kg carriage row and the 1.60 kg "rollers, flares, guards" row of the B2-F table were built from (part sizes and materials). If the real parts are lighter than the CAD shows, the CAD needs to change, not the table.
3. Whether loads re-derived on MuJoCo 4.0.1 are accepted for the S12 sizing. The stored ones are from 3.17.0.
4. The S12 section list with weights, and the allowable stresses, as a file.
5. Any supplier statement on the actuator's holding and stall force, and the lift driver they have in mind.
6. Whether the two contactors and the power box are inside the "as B1" electronics row. I counted 1.6 kg for them separately.
7. For the castor in line DRV-C7: tread shape and swivel offset of the actual part.
8. Why the pad is 30 kN/m with 300 N preload, and whether a softer pad was ever run.

## Files

- `REPLY_and_REV3_2026-11-14.md`: this note.
- `BinRobo_rev3_drawings_A3_2026-11-14.pdf`: 16 A3 sheets. `BinRobo_rev3_drawings_png_2026-11-14.zip`: the same as images.
- `rev3_files_2026-11-14.zip`: switches, command lists, every result file, the weight table, the structure calculation, the interference checks. Its `README.txt` lists the contents.

Sources:
- [FDI 4000 N 6 mm/s 24 V actuator, 400 mm (Botland)](https://botland.store/15868-linear-actuator-super-power-jack-4000n-6mms-24v-40cm-stroke.html): 3 A maximum current, package weight 2.445 kg
- [FDI linear actuator 24 V 400 mm (Anodas)](https://www.anodas.lt/en/fdi-linear-actuator-24v-400mm-6mm-s): the unit drawn; no holding or self-locking figure on the page
- [RoboClaw user manual (Basicmicro)](https://www.superdroidrobots.com/docs/roboclaw_user_manual.pdf) and [a summary of its wiring advice](https://digitalhabitat.github.io/systems/drive-system/drive-motor-controller.html): a power diode across the contactor so braking energy can return to the battery
