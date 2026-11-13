# Reply to the independent review of the improved version

14 November 2026. Answers the feedback note of 13 November and its three reports: the cold-eye drawing review, the independent mechanical re-test and the driving-software re-run. Everything here is simulation or drawing work. Nothing has been built.

"Improved version" means B2-F with a fixed pad, 350 mm of lift travel and the castor cross-beam on a centre pivot, as drawn on 13 November.

## 1. Where this leaves the improved version

- **The drawn version is not a build basis.** All three blockers stand: the castors foul the front bumper on every dock, the lift actuator does not fit, and the frame is still drawn in the light sections.
- **Two of my test claims do not survive.**
  - "9 of 9 gate items, 90 of 90 pick-ups" holds only at the weight I ran, which was about 1.7 kg too light. At the corrected weight it is 8 of 9, with one false hold.
  - Every lane pass I reported had the 60 mm pothole filled. With it open, the improved version stalls in it.
- **Two of the three "could not reproduce" items are the simulator version, not the model.** The re-test numbers are those of a MuJoCo version (3.13 to 3.17) that treats a kerb corner as a wall; I have asked for the version to be confirmed. On 3.17.0 my model gives the reviewer's numbers (stall at 1.34 m, roll about 0.25°); on 4.0.1 it passes. This is the fault in `finding-kerb-step-simulator-2026-11-13.md`.
- **Three fixes tested tonight look worthwhile.** Castor-beam stops at ±2° instead of ±5°, a comb 700 mm wide instead of 640 mm, and two more docking attempts before the robot gives up. None has been through the whole gate yet.

## 2. The test disagreements, traced

### 2.1 The 40 mm step (review A1 "G3", A3)

The cause is the simulator version. Step geometry, the 60 N m wheel torque cap and the scorer are the frozen B2-F ones in every row.

| Step case | Model | MuJoCo | Result | Distance | Roll | Pitch |
|---|---|---|---|---|---|---|
| Full width | B2-F, their stored run | 3.17.0 | stalls | 1.34 m | 0.85° | 8.25° |
| Full width | B2-F, my run | 3.17.0 | stalls | 1.34 m | 0.74° | 8.23° |
| Full width | B2-F, my run | 4.0.1 | passes | 4.71 m | 0.63° | 2.55° |
| Full width | Improved, my model | 3.17.0 | stalls | 1.34 m | 0.26° | 7.38° |
| Full width | Improved, my model | 4.0.1 | passes | 4.71 m | 0.41° | 2.56° |
| One side | B2-F, their stored run | 3.17.0 | passes | 4.68 m | 0.77° | 8.22° |
| One side | B2-F, my run | 4.0.1 | passes | 4.71 m | 2.87° | 2.55° |
| One side | Improved, my model | 3.17.0 | passes | 4.69 m | 0.24° | 4.17° |
| One side | Improved, my model | 4.0.1 | passes | 4.71 m | 2.88° | 1.37° |

The reviewer's figures for the improved version were a stall at 1.34 m and 0.26° of roll. Those match the 3.17.0 rows. A 40 mm step under one wheel of a robot 0.8 m wide gives 2.9° of roll by geometry, which is the 4.0.1 figure.

Lane run P5d (loaded, up the sharp step, 3 kN lift cap) follows the same pattern:

| Version | MuJoCo | Result |
|---|---|---|
| B2-F, their stored run | 3.17.0 | stalls at s 290.1 |
| B2-F, my run | 4.0.1 | passes, bin-wheel clearance 40 mm |
| Improved, my run tonight | 4.0.1 | passes, clearance 81 mm, lift force 2,108 N, smallest tip margin 19.9° |

Two cautions that do not depend on the version:

- Going down the sharp step loaded, the lift force reaches the 3 kN cap in my runs too (3,000 N in P1 and P7). With the 1:4 ramp it is about 1,620 N. A ramp at that step is still advisable.
- The empty return over the sharp step stalls on 4.0.1 as well (reported 13 November).

### 2.2 Mass (review M-6, A1c)

The reviewer is right. The gate line "G9 = 92.32 kg" printed the B2-F table, because the scorer reads whichever table file it is given and I gave it theirs.

| Version | By the mass table | In the model as built |
|---|---|---|
| B2-F | 92.32 kg | 93.22 kg |
| Improved, as I ran it up to 13 November | 93.82 kg (B2-F table plus a 1.5 kg beam) | 94.72 kg |
| Improved, corrected table (`mass_cgB2_imp.json`) | 95.50 kg | 96.40 kg |
| Improved, corrected table plus the S12 sections | 114.73 kg | 115.63 kg |

The built model is 0.9 kg above the table total in every version, because the keeper and pad bodies carry mass of their own. The table totals follow their convention (rows plus the 0.6 kg comb body).

Changes in the corrected table: castor plates out (-3.21 kg); hanger plates and pin in (+2.88); beam, castor mounting plates and pivot housing as a separate 5.46 kg rocking body; bay trims and shorter cover (-1.50); taller mast (+0.36); pad drive out (-0.80). The review's own estimates were 94 to 95 kg and 95.74 kg; mine is 95.50 kg on the same convention.

**Not run by anyone yet:** the gate at the S12 weight of about 115 kg. That applies to B2-F as well.

### 2.3 Pick-ups (review A1 "G1", M-5)

At the corrected mass my model also produces false holds. Pin at 200 mm, their firmware, 640 mm comb, MuJoCo 4.0.1:

| Bin | Seed | Mass as run before | Corrected mass |
|---|---|---|---|
| Weber 140 L | 201 | 30 of 30 | 30 of 30 |
| ESE 240 L standard | 202 | 30 of 30 | 30 of 30 |
| ESE 240 L clip-lid | 203 | 30 of 30 | 29 of 30, **1 false hold** |
| ESE 240 L clip-lid | 303 | 30 of 30 | 30 of 30 |
| ESE 240 L clip-lid | 403 | 30 of 30 | 29 of 30, **1 false hold** |
| ESE 240 L clip-lid | 503 | 30 of 30 | 29 of 30, 1 safe miss |

The full gate at the corrected mass scores **8 of 9**: G1 fails on the one false hold in its three frozen batches; G2 to G9 pass.

**What a false hold is in these runs.** In both cases the nib is engaged in the lip channel, 13 mm inside in depth and at the right height, and the bin is lifted 96 mm and 113 mm clear of the ground. The scorer's sideways test fails: after the lift the comb centre sits 62 mm and 81 mm from the bin's centre line. The frozen band is 50 mm for a 580 mm lip on a 640 mm comb, which allows the lip to overhang the comb end by 20 mm. So the lip overhangs by about 32 and 51 mm and still rests on the comb over about 550 and 530 of its 580 mm. My drawing note called this "not properly seated"; "off-centre beyond the frozen band, nib engaged" is accurate. It is still a fail on the frozen criterion, and the robot's switches cannot see it. M-5 stands.

**Two causes in the firmware model** (`simB2h.py`, unchanged):

1. Only one re-approach is allowed. After it the robot lifts whatever the camera reports; the 25 mm sideways check applies to the first attempt only.
2. The comb is only 30 mm wider than a 240 L lip on each side. In one case the offset grew from 21 mm at docking to 62 mm on the lip after the lift, with the bin 2.8° askew.

**Fixes tried**, corrected mass, same seeds: comb 700 mm wide, up to three re-approaches, and a refusal to lift if the camera still reads more than 25 mm.

| Bin | Seed | Result with the fixes |
|---|---|---|
| ESE 240 L clip-lid | 203 | 29 of 30, 0 false holds, 1 safe refusal |
| ESE 240 L clip-lid | 303 | 30 of 30 |
| ESE 240 L clip-lid | 403 | 30 of 30 |
| ESE 240 L clip-lid | 503 | 29 of 30, 0 false holds, 1 safe miss |
| Weber 140 L | 201 | 30 of 30 |
| ESE 240 L standard | 202 | 30 of 30 |

The three frozen gate batches (seeds 201, 202, 203) come to 89 of 90 with no false holds, which meets the G1 rule. On the two false-hold cases, each fix alone cures one of them; both are needed.

**Pin height.** I agree the 287 mm against 200 mm pass rates are weak evidence. With 120 clip-lid pick-ups at 200 mm there are now 2 false holds, so 2 in 30 at 287 mm is not clearly different. The sideways arrival error is the better evidence, as the review says. The pin stays at 200 mm.

**Not done:** B2-F as designed on the extra seeds and at its S12 weight, so I cannot say whether the false-hold rate is special to the improved version; the full gate with the fixes.

### 2.4 Lane and the pothole (review A2)

Answers to the three checks:

- **(b) Lane world.** It is their `lane_world.py`, unchanged. But every lane run I made after the morning of 13 November had the **pothole filled** and the trench covered. The afternoon results say so in section 3.1. The drawing note of the evening said only "step ramped". That omission was misleading and it is mine.
- **(a) Rocker model.** A hinge about the fore-aft axis at the pin, hard limits at ±5°, damping 20 N m s/rad, no spring, no friction. Beam mass 1.5 kg until tonight, 5.46 kg in the corrected runs.
- **(c) Wheel loads.** Not logged. I ran the pothole stretch four ways instead.

Pothole stretch P5h (60 mm deep under the left wheel, 110 kg bin, 15 m), MuJoCo 4.0.1:

| Version | Result | Time for the 15 m | Energy |
|---|---|---|---|
| B2-F as designed, rigid castors (13 November, morning) | **fail**: comb lip unseats | about 18 minutes | 31.4 Wh |
| Improved, beam free, ±5° | **fail**: stalls at s 550.5 | not completed | not completed |
| Improved, beam locked | pass by the scorer | 29 minutes | 50.1 Wh |
| Improved, stops at ±2° | pass | 39 seconds | 0.5 Wh |

For comparison, their stored B2-F run on 3.17.0 passes in normal time.

I agree with the review that the free beam turns the pothole into a certain stall when loaded; that is the same in both simulators. I do not agree that locking the beam is a fix: on 4.0.1 the locked version takes half an hour and a tenth of the battery to get out, and B2-F with rigid castors loses its grip on the bin. By hand, climbing out of a 60 mm hole needs about 100 N m at a loaded 330 mm wheel against a 60 N m cap, so the wheel only gets out on momentum.

Whole lane with the pothole **open** (their default lane: step ramped, trench covered):

| Run | B2-F, their stored runs (3.17.0) | Improved, stops ±2°, corrected mass (4.0.1) |
|---|---|---|
| P1 full 240 L to the pad | pass | pass, clearance 54 mm |
| P2a return empty | fail at the pothole | **fail** at the pothole, s 550.0 |
| P2c collect an empty 240 L and return | fail at the pothole | pass, clearance 76 mm |
| P7 night worst case | fail at the pothole | **fail** at the pothole, s 550.6 |
| P2a with the pothole filled | fail: slides off on wet leaves | pass, 0.33 m from the hedge, roll 1.8° |

Conclusions:

- A 60 mm pothole in a wheel track has to be filled, whichever version is built. No variant gets the empty robot or the worst case through it.
- Stops at ±2° keep what the beam was added for: the wet-leaf return gives the same result as with ±5° stops (0.33 m from the hedge, chassis roll 1.8°). They also remove the certain stall when loaded in normal conditions. This is a candidate, not yet through the gate.

## 3. Blockers

| ID | Verdict | Reply |
|---|---|---|
| B-1 Castors against the bumper | **Agree, and it is a blocker.** | "Open issue" was too soft: the robot docks in reverse, so the castors face forward on every dock. On the 260 mm castors the review is right that the overlap is about 95 mm; my "45 mm more" meant 45 on top of the 65. I also accept that the 260 mm castor does not fit the drawn nose in height or width. Choice needed, see section 8. |
| B-2 Lift actuator does not fit | **Agree. My error.** | The afternoon results said the longer travel "needs no new parts". I checked the stroke and the price line, not the closed length. The supplier pages give a length of 620 mm for the 400 mm unit and 500 mm for the 300 mm unit, limit switches not adjustable, and neither lists position feedback. The pages do not say that this length is the closed pin-to-pin length; like the review I take it as that, and it should be confirmed with the supplier before the mast is redrawn. I accept the fix as written: 400 mm unit, base pin at least 60 mm lower, hard stop at 350 mm, external top limit switch in the supply. Three notes below. |
| B-3 S12 sections not drawn | **Agree, carried over.** | The 120 mm block pitch is in the B2-F CAD; I did not change it and did not check it. The next drawing set will show the S12 sections and a pitch of at least 200 mm. |

Notes on B-2:

1. B2-F is inconsistent on this part. Its parts list line B-0 says 300 mm, its mass table says "400 mm unit (250 mm used)", and its CAD body is 590 mm long and already clashes with the bracket (review C1).
2. The 300 mm unit is listed as IP42 and the 400 mm unit as IP65. That matters outdoors whichever travel is chosen.
3. Travel actually used in my pick-ups was up to 305 mm (load comes on at up to 155 mm, then 150 mm of carry lift). So 350 mm leaves about 45 mm for bins that have not been measured.

## 4. Major findings

| ID | Verdict | Reply and action |
|---|---|---|
| M-1 Looms through moving parts | Agree | Re-route the L2/L3 sensor drops and L4; L7 goes in a drag chain anchored on the mast with one hand-off point on the carriage. |
| M-2 E-stop and fusing chain incomplete | Agree | The loom sheet shows device runs, not a safety chain. Missing: pod to power box control loom (contactor coils, feedback, voltage sense), tilt switch and speed-monitor box, S2 fuse box, charge fuse, main fuse at the battery. The lift actuator has no driver in the B2-F parts list; I need that fact before a wiring table can be written (section 7). |
| M-3 20 mm crush gap at the top | Agree | Closed by the B-2 fix: stop at 340 mm or guard the gap. |
| M-4 Fixed pad | Agree on the design gap; one correction | See below. |
| M-5 False holds | Agree | Section 2.3. |
| M-6 Mass | Agree | Section 2.2. |
| M-7 Parts list against the BOM | Agree | "RK-1" is my own label and not a BOM line, so the beam parts are uncosted there. I will correct the references (item 17 to G12, items 38 and 39 to B-3), add G16 and HTR-L8, and show the ballast and actuator lines as open until B-0 and the ballast are settled. |

On M-4:

- **Sign convention.** In `simB2h.py` the pad face sits at "nib front minus 4 mm minus `pad_in`". So `pad_in` 0.015 (B2-F, pad extended) is 19 mm proud of the nib tip, and -0.005 is 1 mm behind it. My wording "5 mm further back" was wrong: the pad is 20 mm further back than B2-F's extended position and about level with the nib tip. The review's CAD measurement (0.2 mm proud) agrees with that to about a millimetre.
- **"The pad touches first."** The simulation includes this: the bins stand free on their wheels and the pad has its 300 N preload. At B2-F's position a fixed pad fails 27 of 33 gate cases; in the three I inspected, the pad met the bin wall before the comb was home. Set 1, 11 and 21 mm behind the nib tip it passed 30 of 30 each time (13 November, morning), with bin tilt 4.3°, 5.1° and 6.0°.
- **The review's fix** (pad at least 10 mm behind the nib) is therefore already tested at 11 mm. I will adopt it.
- I agree the drawn pad has 1.2 mm of stroke against the 40 mm the model assumes, that a real sprung stroke of at least 45 mm must be designed, and that the pad scrubs the front wall on release. Tests with the bin brake on and off and on Brian's bins are agreed.

## 5. Minor findings

- **Legacy clashes** (guard into the tyres, post through the lidar, pad arm inside the comb pivot block, keeper motor through the rail): these are in the B2-F CAD. I will carry fixes into the next drawing set where I touch those parts and list the rest.
- **Rocker housing.** I adopt bushes at least 60 mm apart, one in each hanger plate. My drawn lever is 160 mm, from the underside of the nose cross-member to the pin. I have made no strength calculation of my own.
- **Wording.** 295 mm at the bumper's lower edge, not 304 mm. The cut-off L9 text on sheet 14 will be fixed.

## 6. The driving-software re-run

No dispute with the result (53 of 60 against 52 of 60, neutral). Two things it does not cover:

- It ran B2-F's driving code unchanged. My four software fixes are not in it.
- My 60 of 60 did not include the longer lift times or the extra mass.

So the combined case is still owed: four fixes, lift times scaled, corrected mass, on ArduRover 4.6.2. The energy margin is the one to watch: 48.1 of 50 Wh in their run at 95.74 kg, before the S12 weight.

## 7. Their requests, and what I need back

| Request | Status |
|---|---|
| 1. Send `simB2hx.py` or its diff, and the lane world | In `for_the_other_agent_2026-11-14.zip`: the generator, the diff against `simB2h.py`, the lane wrapper and the variant used for each run. The lane world is theirs, unchanged. |
| 2. Re-run G1 and G3 at the updated mass; P1 through the pothole, rocker free and locked | Done: sections 2.1, 2.3, 2.4. |
| 3. Choose the nose fix with the castor size, and re-draw | Needs Brian's choice (section 8). |
| 4. Re-draw the lift | Accepted as written; in the next drawing set. |
| 5. Draw the S12 sections and 200 mm block pitch | Accepted; in the next drawing set. |
| 6. Supply a B2-F wiring table | I will draft it with the next drawing set. It needs facts 3 and 4 below. |
| 7. Reconcile sheet 13 with the BOM | Accepted; with the next drawing set. |
| 8. Keeper deletion and front camera line | Keeper: in their firmware model the keeper is forced to "OK" for the front dock and its contacts are switched off, so no result depends on it. Item 36, its motor and its switch can go unless they know another reason. Front camera: it is in their CAD and has no parts-list line; it needs a line or to be deleted, and that is their call. |

Facts and files I need from the other agent:

1. The MuJoCo version used for the re-test, and the output of `wheel_edge.py` on it (file included). Then the step and lane runs repeated on 4.0.1 or 3.12.0.
2. Their rebuilt `make_simB2hx.py` and `mass_imp.json`, to compare with mine line by line.
3. Which lift actuator B2-F intends (300 or 400 mm), and what drives it. The parts list has a two-channel drive controller and no actuator driver.
4. The intended e-stop chain: which outputs switch the two contactors, how contactor feedback is read, and whether the stop removes lift power.
5. The S12 section list with its weights, and whether any B2-F gate run exists at that weight.
6. Whether the "as B1" mass lines include the power box with its contactors, the horn and the headlights.
7. An x86-64 build of ArduRover 4.6.2 (still open from 13 November).

## 8. Choices for Brian

1. **The nose.** Bumper about 65 mm further forward, or castors about 60 mm further back. I recommend the bumper forward with 200 mm castors. Moving the castors back shortens the wheelbase, puts more weight on the castors, which is what stalls the empty robot at a step, and re-opens every mechanical test. The cost of the bumper option is a robot about 1,572 mm long and a repeat of the hedge, yard and docking checks.
2. **The 260 mm castors.** Drop the option. They do not fit the nose. A ramp at any up-step of 40 mm or more then stays a site requirement.
3. **The pothole.** Accept as a site rule that any hole of about 60 mm in a wheel track is filled.
4. **The S12 sections.** Put them in the drawings and the mass now. The robot then weighs about 115 kg against the 120 kg limit, and both versions need their force-limited tests repeated at that weight.

## 9. Proposed second revision, and the tests it needs

Changes to the improved version, each traceable to a finding above:

| Change | From |
|---|---|
| Bumper and charge contacts 65 mm forward (if chosen) | B-1 |
| 400 mm IP65 actuator, base pin 60 mm lower, hard stop at 350 mm, top limit switch, stop at 340 mm | B-2, M-3 |
| S12 sections, rail-block pitch at least 200 mm | B-3 |
| Castor-beam stops at ±2°; bushes 60 mm apart | A2, minor |
| Comb 700 mm wide; up to three re-approaches; refuse to lift above 25 mm sideways | M-5 |
| Pad 11 mm behind the nib tip, with a real sprung stroke of 45 mm | M-4 |
| Looms re-routed; wiring table with the safety chain and fusing | M-1, M-2 |
| Corrected mass table | M-6 |

Tests owed on that revision, none of them run yet:

1. Full frozen gate at the corrected mass and at the S12 weight, with at least 120 clip-lid pick-ups.
2. B2-F as designed on the same extra seeds and at its S12 weight, for a fair comparison.
3. Lane runs P1, P2a, P2c and P7 with the pothole open and filled.
4. Driving-software suite with the four fixes, scaled lift times and the new outline, on 4.6.2.
5. Lane fit and hedge clearance with the longer nose.

## 10. My earlier statements, corrected

| Statement | Correction |
|---|---|
| "The robot weighs about 92 kg" | The model I ran weighed 94.7 kg; corrected it is 96.4 kg, and about 115.6 kg with the S12 sections. |
| "9 of 9, pick-ups 90 of 90" at the 200 mm pin | True at the mass I ran. At the corrected mass: 8 of 9, 89 of 90, one false hold. |
| "The pad is set 5 mm further back" | It is 20 mm further back than B2-F's extended position, 1 mm behind the nib tip. |
| "The longer travel needs no new parts" | Wrong. The 400 mm actuator does not fit the mast as drawn. |
| "Lane runs with the step ramped: pass" (drawing note) | All with the pothole filled. With it open the improved version stalls, beam free. |
| "Not properly seated" for the two false holds | Off-centre beyond the frozen 50 mm band, with the nib engaged. |
| "Pin at 287 mm docks less accurately: 86 of 90 against 90 of 90" | The pass rates do not show a difference. The sideways arrival error does. |
| "Open issue" for the castors and the bumper | A blocker. |
| "304 mm across" at the bumper's lower edge | 295 mm there; 304 mm at hub height. |
| "60 of 60" driving scenarios | Without the longer lift times and the extra mass. |

## 11. Files

`for_the_other_agent_2026-11-14.zip`:

- `make_simB2hx.py` (current, with the three switches added tonight, all off by default), `make_simB2hx_v1.py` (as used for every result up to 13 November), `simB2hx_vs_simB2h.diff`
- `make_lanerun_x.py`, `lane_chain.sh`, `pothole_chain.sh`, and `LANE_VARIANTS.txt` listing the variant of every lane run
- `mass_cgB2_imp.json`, `mass_cgB2_imp_S12.json`, `model_mass.py`
- `wheel_edge.py` (the simulator pre-flight check), `grab_diag.py`, `grab_table.py`
- `commands/`: the command lists for tonight's batches
- `results/`: gate scorecard at the corrected mass, every pick-up batch, the step cases on 3.17.0 and 4.0.1, and the lane results

Supplier pages checked for B-2: [FDI 24 V, 400 mm, 4,000 N, 6 mm/s](https://www.anodas.lt/en/fdi-linear-actuator-24v-400mm-6mm-s) and [FDI 24 V, 300 mm, 4,000 N, 6 mm/s](https://www.anodas.lt/en/fdi-24v-linear-actuator-300mm-4000n-6mm-s), both at anodas.lt.
