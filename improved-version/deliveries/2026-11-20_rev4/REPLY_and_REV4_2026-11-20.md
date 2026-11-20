# Reply to the review of revision 3, and revision 4 of the improved version

20 November 2026. For Brian and the B2-F author. From the reviewer / tester agent.

Files with this note: the 17-sheet drawing set (PDF and PNG) and a zip of every script, command list and result file.

## Summary

The review of revision 3 was right on its blocker and on all eight major findings. Revision 4 answers them, and it is drawn and tested. It is still a concept, not something to build from, and the testing turned up two problems that neither design had been tested for before.

**What revision 4 now does (all by simulation):**

- Stops for a person inside the travel of its front bumper. The longest simulated stop is 122 mm against 150 mm assumed available. This needed a 300 mm foam safety bumper and a speed that depends on the slope.
- Notices something under the bin when it lowers, if the thing is thicker than about 20 mm.
- Has no welded joint. Every joint is bolted, with a bolt and torque table on the new sheet 17.
- Has a lift actuator that holds the bin (8.8 kN by its data sheet) and switches itself off before it reaches the hard stops.
- Passes eight of the nine gate tests at 60 N m, 179 of 180 pick-ups with one safe refusal, all 24 stress cases, and every lane run on a lane whose three rough spots (step, trench, pothole) have been made good.
- Drives its missions on camera readings alone, without the two true-position shortcuts your driving re-test found.

**What it costs:**

- **Weight: 177.6 kg**, up from 152.2. Bolting costs about 10 kg, the bumper 4.5 kg, the strength fixes the rest. The 120 kg gate fails.
- **Time: a trip takes 62 to 72 minutes** instead of about 56, because of the slope speed rule. Two bins fit between 18:00 and 21:00; the third does not. Energy is not the limit: an aged, cold battery still ends a three-trip evening above 30 %.

**The two new problems:**

1. **The empty robot brakes badly downhill.** Only the two drive wheels have brakes, and without a bin 55 % of the weight sits on the castors. On a 12 % wet slope, nose first, the empty robot needs 0.29 m to stop even from 0.15 m/s, and on wet leaves it does not stop. With a full bin it is fine (94 mm from 0.2 m/s). This applies to B2-F as well; no earlier test covered it. In the lane model the 12 % pitch is an assumption, so the first step is to measure the real one.
2. **The 40 mm sharp step was only ever crossed on momentum.** At the speeds that are safe for people, revision 4 gets over a 25 mm edge square on with a full bin and a 20 mm edge when empty. A full bin gets over 40 mm if the edge is met at an angle; the empty robot does not. More torque does not solve it, so I withdraw my request for 80 N m. Higher edges on the lane need a small ramp.

**One strength row misses my own limit:** the nose cross-member has a safety factor of 1.55 on your hardest load case (2.0 wanted). It needs a 60 x 60 section. I found this after the test campaign had run, so it is noted on the drawings but not yet drawn in.

**What I recommend** (details in section 8): measure the steepest slope and the highest edge on the lane; design brakes for the castors, which in simulation fix both the empty-robot braking and the lost third bin (trips of 55 minutes, three bins home by 20:45); judge the weight by what the robot does, with a cap on a weighed prototype.

Where I made mistakes in revision 3, they are named in section 1: the castor load figure I quoted for the slippery hill start was an average, not the raw minimum; "the castors need round-profile tyres" was more than the evidence showed; and two sentences on the drawings and in the reply were wrong.

## 1. The three reports, finding by finding

I checked each finding against my own files and runs before changing anything. "Agreed" means I reproduced it.

### Cold-eye review

| Finding | My check | Revision 4 |
|---|---|---|
| **B-1** The 15 mm bumper cannot stop the robot; lowering has no safety function; docking presses the bumper | Agreed. One correction that does not change the conclusion: the robot's top speed in every gate, lane and driving file is 0.5 m/s, not 0.8. At 0.5 m/s the revision 3 robot still needed 134 to 172 mm on level ground after a bumper touch, and far more downhill. | A 300 mm foam safety bumper with its own control unit. Speed now depends on the slope, so that the simulated stop stays inside the bumper (3.3). A load-drop guard and two light beams for lowering (3.4). The charge pads moved under the nose, so docking no longer touches the bumper. What is still open is in section 4. |
| **M-1** Weight; the 120 kg gate | Agreed that 120 kg is a comparison figure and that the test should be on what the robot does. Revision 4 makes this harder, not easier: it weighs 177.6 kg, above the 165 kg cap you suggest. Section 3.1 says where each kilogram comes from. | Brian decides the cap (decision 3). I report the functional results (energy, step, stop, tip) in section 3. |
| **M-2** Side rail and fatigue at the welded corner plate | Agreed. On the rigid-tyre load I ran the tyre question directly instead of arguing it (3.6): a hard solid tyre that sinks 1.3 mm under the standing load gives a 4.0 kN wheel load on the kerb, against 9.4 kN for the rigid model. | Rails are 60 x 60 x 4 S355. The corner plates are bolted, so no weld is left on the rail. Rail safety factor 2.10 on the design wheel load, 2.46 on the hard-tyre kerb load, 0.88 on the rigid-model peak (information). Fatigue check with bolted plates: stress range 44 MPa against 67 MPa allowed, on an ASSUMED load history. |
| **M-3** Actuator's own end stops, closed length, stop load | Agreed. | The actuator is drawn with its pin spacing: 600 mm closed, 615 mm with the comb down. Its base bracket sits on a shim pack, so the actuator's own stops are set on assembly to −15 and +331 mm of lift travel: outside the limit switches (0 and 327) and inside the stop blocks (−18 and +335). The actuator therefore switches itself off before it can stall on a block. Sheet 17 shows the order. Blocks and bolts are sized for 9.5 kN (1.4 times the rated 6.8 kN, ASSUMED until the maker states the stall force): bolt safety factor 4.6. |
| **M-4** Welds in a bolted DIY build | Agreed. | No welded joint is left: frame corners, mast feet, mast struts, lift stops, castor pivot, castor beam, bumper carrier and actuator brackets are all bolted. Sheet 17 has the bolt table with torques. Bolting costs about 10 kg against welding. |
| **M-5** Safety sheet gaps (10 items) | Agreed on all ten. | 1: a first-pass estimate is in section 5; it is not a verification. 2: the safety controller is described by what it must do (10 two-channel inputs, two safe output pairs, speed monitoring); I did not pick a type. 3: rear bumper switches specified with two NC contacts. 4: contactors with mirror contacts are required on sheet 15 and in the parts list. 5: the lift feed now runs through two safety relay contacts; the driver's enable input is no longer the safety function. 6: lowering, see 3.4. 7: holding, see M-6. 8: speed and standstill monitoring is asked of a certified module with two wheel sensors, not of home-built boards. 9: tilt is sensed by one switch and one inclinometer. 10: docking no longer presses the bumper. |
| **M-6** Actuator data conflicts | Agreed. The two listings of the FDI unit disagree on sealing (IP42 against IP65) and length (595 against 620 mm), and neither gives a holding force. | That unit is dropped. Drawn instead: an outdoor actuator of the LINAK LA36 class, 24 V, 6.8 kN, 350 mm stroke. Its data sheet gives a self-locking force of at least 8.8 kN, IP66 and built-in end stops (Sources). Measured shock on the lift in simulation: 3.1 kN at 0.5 m/s over the kerb, 4.0 kN at 0.8 m/s (3.6). Weight 6.5 kg is ASSUMED: I did not find it stated. Still to get in writing before ordering: weight, stall force, price. |
| **M-7** Castor round-tyre claim | Agreed: I overclaimed. I mapped the slippery hill start against the width of the castor's contact strip (3.5). Only the full 50 mm flat model fails. Every width from 16 to 44 mm passes on heading. | The requirement is reworded: a crowned or rounded tyre whose contact strip is no wider than about 40 mm. The bench test you propose (swivel torque under load) stays as the check before ordering. |
| **M-8** Goalpost moves | Torque: I withdraw the request for 80 N m. The limit stays at 60 N m (3.5). Energy: agreed, restated as the charge left at the end of the evening (3.8). Weight: see M-1. | See 3.5 and 3.8. |
| **m-1** Pad springs too close to solid | Agreed. | Springs 145 mm free, 135 mm fitted: 15.8 mm left before solid at full stroke (9.9 needed). Both ends are guided: the springs run in bores through the guide block and sit in 5 mm pockets in the cup plate. |
| **m-2** Actuator body inside its base bracket | Agreed. | New base bracket. The clash check no longer excuses this pair and finds no overlap. |
| **m-3** Mast foot bolts | Agreed. | Each upright stands on two angle cleats (2 x M12 down through the cross-member, 2 x M8 through the upright, all in crush tubes). Two struts now carry the tipping load of the hanging bin to the nose cross-member. Safety factors in 3.6. |
| **m-4** Motor plate under sideways tyre load | Agreed that it was not checked. | Plate is 8 mm with a top flange bolted up through the rail. I measured the sideways tyre force in simulation: at most 904 N (pivot turn with a full bin). Safety factor 2.37 at that load. |
| **m-5** Sheet 13 said 2.2, the calculation 2.04 | Agreed, my slip. | Corrected; sheet 13 now quotes the revision 4 figure. |
| **m-6** Comb clears the guards by 8 mm a side | Checked: the comb pivots (±4 degrees), it does not slide sideways. At full swing its ends move 0.9 mm towards the guards. | No change. |
| **m-7** "Comb loads stay about the same" | Agreed, the sentence was wrong: the 8,148 N was B2-F's keeper-on case. Like for like the load falls from 9,634 to 4,550 N. | Withdrawn. |
| **m-8** Rail blocks only 10 mm behind the plate at the stops | Agreed. | The plate no longer meets the stops. The steel ends of the two carriage cross-beams land on the stop blocks. In the sweep (1 mm steps, from −25 mm to past the top stops) the first contacts are the beams on the blocks at −18 and +335, then the switch bodies at −25 and +339; nothing else touches. |
| **m-9** No hole patterns, torques, pin spacing | Partly answered. | Sheet 17: bolt sizes, counts and torques for every joint, the actuator pin spacing, the order of the lift stops. There are still no part drawings, tolerances or hole positions: this remains a concept. |
| **m-10** Unpriced lines; old lines to delete | Agreed. | Sheet 13 lists the deleted lines. Rough prices for the new safety parts are in section 6; several are still unknown. |

### Mechanical re-test

| Finding | My check | Revision 4 |
|---|---|---|
| The step result flips with the castor strip width (30 passes, 36 stalls, 50 passes) | Reproduced, and I found the cause. In your step test the edge is 1.6 m ahead of the axle, so the castors meet it 0.55 m after the robot has reversed onto the bin: they are still pointing backwards (152 to 185 degrees) and swing round on the edge. Which width passes is then chance. With the edge 3.0 m ahead, every width passed on the revision 3 model at 60 N m. | The real limit is elsewhere and I had not seen it: section 3.5. |
| Slippery hill start: raw castor load 48.8 N is under the 50 N rule | Agreed, and this was my reporting error. The "393 N least castor load" I quoted was the 100 ms average. The raw minima in my four runs were 67, 49, 32 and 0 N: three of four fail the raw rule. | Section 3.5 gives both numbers for revision 4. |
| The sharp step needs 80 N m | Superseded by 3.5. | |
| Open pothole and open trench were not run | Agreed. | Run now (3.7). |
| The seating check changed nothing | True at 8 mm camera noise. It earns its place when the camera is wrong by more: with a 60 or 80 mm camera bias the gate is fooled and the seating check catches it (3.8). | Kept. |
| 23 of 180 pick-ups needed a second approach | Agreed. | Revision 4: 28 of 180 (3.2). |
| The lift runs at its 3 kN cap | Agreed. | The new actuator has 6.8 kN and holds 8.8 kN. The shock is now measured with the cap out of the way (3.6). |
| The gate file's tip hand-calculation block was stale (36.5 degrees) | Agreed: the scorer reads B2-F's untagged file. | My collection script now feeds it revision 4's own calculation: 32.3 degrees. |

### Driving-software re-test

| Finding | My check | Revision 4 |
|---|---|---|
| 12 of 60 missions fail the 50 Wh trip limit only | Agreed. | Section 3.8: the same 12 missions fail it, and seven of them now fail for other reasons as well. |
| The pre-grab gate and the final reverse use the true position | Agreed: both were "oracles". | Removed. The gate decides on a camera reading and the final reverse steers on one. The true values are only logged, so the two can be compared. |
| No seating check in the companion | Agreed. | Added: at the dock, before the lift, from the two leg-tip gap sensors. Over 30 mm: pull out, correct, dock again; still over: no lift, drive home, alert. |
| D1 A refused trip is never closed | Agreed. | Fixed: a refusal ends with "back on the dock" and the trip is logged. |
| D2 Each camera check moves the estimate by the full noisy reading | Agreed. | Three frames are averaged. |
| D3 A missing frame on the last try refuses | Unchanged; it errs on the safe side. | |
| D4 Gate refusals are not counted | Agreed. | Gate and seating refusals are now in `metrics.refused`. |
| D5 A robot 38 mm off was accepted | Agreed that the margin is thin. | The camera gate keeps a 35 mm band; the seating check is a second, independent measurement behind it. |

## 2. What changed in revision 4

- **Front:** foam safety bumper 300 mm deep, 150 high, 700 wide, on a bolted carrier. Charge pads under the nose. The robot is 1,831 mm long (1,876 with a 240 L bin), 275 mm longer than revision 3.
- **Frame:** side rails 60 x 60 x 4 S355. Every joint bolted, with top and bottom corner plates and crush tubes. Motor plates 8 mm with a flange.
- **Mast:** uprights on bolted cleats; two struts from the uprights down to the nose cross-member; lift stop blocks bolted to the inner faces of the uprights.
- **Lift:** outdoor actuator, 6.8 kN, 350 mm stroke, holds 8.8 kN, own end stops; two limit switches at each end; base bracket on shims.
- **Pad:** longer springs with guided ends.
- **Lowering:** load-drop guard in the firmware, two light beams under the bin, 3 A current limit on the way down.
- **Speed:** set by slope and by whether a full bin is on board (3.3).
- **Safety chain:** 10 two-channel inputs, lift feed through safety relays, tilt by two different sensors, bought-in speed monitoring.
- **Driving software:** camera-only gate and final reverse, three-frame average, seating check, refused trips closed and counted.
- **Not changed:** the 60 N m torque limit, the battery, the drive units, the comb, the castor beam on its centre pivot.

## 3. Results

### 3.1 Weight: 177.6 kg

Built from the drawn solids, as in revision 3, and matched by the simulator model.

| Group | Revision 3, kg | Revision 4, kg |
|---|---:|---:|
| Frame, mast, guards, covers | 74.0 | 90.1 |
| Bought-in units | 40.4 | 43.4 |
| Allowances (bolts, power box, paint) | 4.7 | 10.7 |
| Castor beam | 6.0 | 6.0 |
| Lift carriage | 27.1 | 27.4 |
| **Total** | **152.2** | **177.6** |

Where the 25.4 kg comes from (rounded):

| Change | kg |
|---|---:|
| Bolts and crush tubes of the bolted joints (66 bolts, counted joint by joint) | +5.0 |
| Bolted corner plates, cleats and mast struts in place of welded plates and shoes | +5.5 |
| Safety bumper and its carrier, less the old bar | +4.5 |
| Rails 60 x 60 x 4 | +3.4 |
| Actuator (6.5 kg ASSUMED, against 3.5) | +3.0 |
| Thicker motor plates | +1.7 |
| Stop blocks, extra switches, light beams, larger power box | +2.3 |

About 10 kg is the price of bolting everything, 4.5 kg the price of the bumper, and the rest answers the strength findings. The table still carries the inherited rows of the B2-F table unchanged (drive units 2 x 9.68 kg, battery 5.05 kg). Your audit puts the drive units 2 to 8 kg higher, so a weighed prototype could come out at 180 to 186 kg.

What the weight does: 55 % of the empty robot's weight is now on the two castors, which are neither driven nor braked. That shows up twice below: in braking (3.3) and at steps (3.5).

### 3.2 Gate and pick-ups at 177.6 kg, 60 N m

| Gate test | Result |
|---|---|
| G1 pick-ups, three bin types | 90 of 90 held, none knocked over |
| G2 hill start on 12 %, grip 0.22 to 0.30 | pass; creep 33 to 35 mm |
| G3 40 mm step, your test | pass on one side and on both, but see 3.5: this is not a robust result |
| G4 emergency stop, 12 % downhill, wet, full bin, from 0.5 m/s | 0.281 m |
| G5 pivot turn | swept circle 3.00 m (limit 3.2) |
| G6 set-down and release, 18 cases | all pass |
| G7 time-step check | pass |
| G8 tipping | static poses pass; hand calculation 32.3 degrees (31.6 with the bin's weight 60 mm off-centre) |
| G9 weight under 120 kg | **fail: 177.6 kg** |

180 pick-ups with scattered start positions: 179 lifted, 1 refused safely, none lifted more than 50 mm off-centre (largest 29.5 mm). 28 needed more than one approach; one was set down and re-gripped by the seating check. All 24 stress cases pass (robot 10 % heavier and lighter, 15 % less grip, more rolling resistance).

### 3.3 Stopping for a person

I ran 159 stops: the robot drives at a set speed, the bumper is touched, and after 0.15 s (ASSUMED: safety relay, contactors, brakes) both contactors open and the spring brakes apply. The figure is the distance from the touch to standstill, in mm, at 177.6 kg on a wet surface (grip 0.30). The bin stayed on the comb in every loaded run.

| Downhill slope | Full bin: 0.2 | 0.3 | 0.4 | 0.5 m/s | Empty: 0.2 | 0.3 | 0.4 | 0.5 m/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| level | 39 | 69 | 105 | 146 | 48 | 79 | 122 | 175 |
| 3 % | 45 | 82 | 121 | 167 | 56 | 93 | 146 | 208 |
| 6 % | 51 | 95 | 140 | 196 | 66 | 124 | 190 | 279 |
| 9 % | 65 | 121 | 175 | 248 | 95 | 188 | 295 | 439 |
| 12 % | 94 | 161 | 248 | 360 | 389 | 788 | 1,335 | 1,911 |

The empty robot is the worse case, the opposite of what one expects, because only the drive wheels brake and without a bin they carry under half the weight. On the 12 % pitch it needs 289 mm even from 0.15 m/s.

Other cases:

- Reaction time 0.10 / 0.20 s instead of 0.15: full bin, level, 0.5 m/s: 122 / 171 mm.
- Robot 10 % heavier (195 kg): empty, level, 0.4 m/s: 124 mm (122 at 177.6 kg).
- Empty, tail first (drive wheels downhill): 12 % wet: 71 mm from 0.2 m/s, 122 mm from 0.3 m/s.
- Brakes on the castors as well (30 N m each, an option I simulated but did not design): 12 % wet from 0.5 m/s: 167 mm empty, 166 mm with a full bin. Up to 6 %: at most 140 mm from 0.5 m/s.
- Wet leaves (grip 0.22), full bin: 6 %: 114 mm from 0.3 m/s; 12 %: 277 mm from 0.2 m/s. Empty on 12 %: it does not stop at all.

**The speed rule in revision 4.** I assumed the bumper still has 150 mm of travel after it switches (half its depth; the maker must confirm) and set the speeds so that the simulated stop stays under 125 mm:

| Slope | Full bin | Empty, or empty bin |
|---|---|---|
| level or uphill | 0.4 m/s | 0.4 m/s |
| downhill, up to 3 % | 0.4 m/s | 0.3 m/s |
| downhill, 3 to 9 % | 0.3 m/s | 0.2 m/s |
| downhill, steeper than 9 % | 0.2 m/s | tail first, 0.2 m/s |

The longest simulated stop under this rule is 122 mm. Two things are not solved by it:

- **Tail-first travel is not in the driving software.** The mission runs drive the empty robot nose first at 0.15 m/s on the steep pitch, which does not meet the rule. (In the lane model the 12 % pitch is itself an assumption: the map data gives 7.9 % at most.)
- **The rule costs time.** A trip now takes 62 to 72 minutes instead of about 56, and the third bin of an evening no longer fits before 21:00 (3.8).

### 3.4 Lowering the bin

The firmware knows the lift height at which the bin left the ground at the pick-up. On the way down, while the bin is still more than 15 mm above that height, it watches the load on the lift. If the load falls by more than 80 N (or 10 % of the bin's weight), something is under the bin: it stops and raises 30 mm.

| Case (block under one bin wheel unless stated) | Lowering at 6 mm/s | at 13 mm/s |
|---|---|---|
| No block, 110 / 60 / 25 kg bin | normal set-down, no false stop | same |
| 25 mm block, 110 kg | stopped, block carried 109 N | stopped, 158 N |
| 40 mm block, 110 kg | stopped, 107 N | stopped, 130 N |
| 60 mm block, 110 kg | stopped, 109 N | stopped, 122 N |
| 60 mm block, 60 kg / 25 kg bin | stopped, 83 / 81 N | stopped, 86 / 86 N |
| 60 mm bar under both wheels, 110 kg | stopped, 109 N | stopped, 122 N |
| 15 mm block, 110 kg | **not seen**: 859 N | **not seen**: 865 N |
| 60 mm block, guard switched off | 907 N | - |

Limits: the guard does not see anything thinner than about 20 mm. Two light beams cross under the bin 40 mm above the ground and block lowering while either is broken; they see a foot but not a flat hand. The guard is firmware, not a rated safety function. The lift driver limits the current to 3 A on the way down (about 0.5 kN of push, to be set on the bench) so the comb and pad arm cannot press hard by themselves.

### 3.5 Steps, castors and drive torque

This is where I have to correct my own revision 3 position.

**The 40 mm sharp step, full bin, met square on.** P = over, S = stalled. Columns: width of the castor's contact strip in the model.

| Speed | Edge ahead | Torque | 16 | 24 | 32 | 36 | 40 | 44 | 50 mm |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 m/s | 1.6 m (your test) | 60 N m | P | P | S | S | S | P | P |
| 0.5 m/s | 3.0 m (castors trailing) | 60 N m | S | S | S | S | S | P | S |
| 0.5 m/s | either | boost to 100 N m | P | P | P | P | P | P | P |
| 0.4 m/s | either | 60, or boost to 100 | | S | | | | | |
| 0.3 m/s | either | 60, or boost to 100 | | S | | | | | |

With the castors pointing the right way, revision 4 does not get over the sharp step at 60 N m even at 0.5 m/s. A short boost to 100 N m gets it over at 0.5 m/s, but not at the 0.4 m/s the speed rule now allows: the castors climb and then the drive wheels stall on the edge.

The reason is simple arithmetic. To lift itself square on to a 40 mm edge without a run-up, a 330 mm drive wheel carrying 1,160 N (full bin) needs about 125 N m. The robot has 60. It only ever crossed that step on momentum at 0.5 m/s.

**What does work at 60 N m and 0.3 to 0.4 m/s:**

| | Square on | Edge met at an angle |
|---|---|---|
| Full bin | 25 mm (30 mm at 0.4 m/s only) | 40 mm, at 10, 20 and 30 degrees, at 0.2 to 0.4 m/s |
| Empty robot | 20 mm | 30 mm at 20 degrees; 40 mm only where one side meets the edge at a time |

The empty robot is the weak case again: 963 N sits on the castors and the lightly loaded drive wheels cannot push them up a 40 mm edge (they would need about 1,280 N of push and have about 470 N of grip in the dry). The boost does not help there.

**So I withdraw the request to raise the torque limit.** 60 N m stays. The boost is not adopted: it does not solve the step at safe speed, and 100 N m on both wheels draws about 70 A by the motor figures in your M-8, above the 60 A battery protection. The runs with the boost are in the files as information.

**What follows for the lane:** an edge of more than about 20 mm across the full width has to be ramped, or crossed at an angle with a full bin. This applies to any robot of this layout (two driven wheels at the back, two castors at the front), so I ask the B2-F author whether B2-F was ever run empty over the sharp step (section 9).

**Castor tyre width and the slippery hill start** (grip 0.22, bin weight 60 mm off-centre), revision 4:

| Contact strip, mm | 16 | 24 | 32 | 36 | 40 | 44 | 50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Heading swing, degrees | 2.6 | 1.3 | 1.8 | 2.3 | 1.5 | 2.0 | 13.3 |
| Least castor load, raw, N | 422 | 81 | 63 | 62 | 32 | 67 | 0 |
| Least castor load, 100 ms average, N | 569 | 525 | 540 | 536 | 549 | 546 | 491 |

All reached the top. Only the full-width 50 mm model swings off course. The raw load dips under 50 N for an instant at 40 and 50 mm; the 100 ms average never falls under 490 N. I report both, as you asked.

### 3.6 Loads and structure

Largest loads in the revision 4 runs:

| Load | N | Case |
|---|---:|---|
| Drive wheel, carrying | 3,497 | emergency stop in reverse on 12 % |
| Drive wheel, your load cases with the compliant tyre | 4,754 | pothole at 0.8 m/s |
| Drive wheel, kerb at 0.8 m/s on a hard solid tyre (735 N/mm) | 4,069 | my run |
| Drive wheel, rigid-tyre model | 11,403 | sharp step at 0.8 m/s; information |
| Comb, carrying | 2,421 | |
| Comb, kerb at 0.5 / 0.8 m/s | 3,048 / 7,838 | rigid tyre |
| Lift, kerb at 0.5 / 0.8 m/s | 3,068 / 4,028 | lift cap raised so the shock is not clipped |
| Pad | 1,414 | |

The comb load at 0.8 m/s is nearly double the revision 3 figure (4.5 kN). The reason is the new actuator: the old one slipped at 3 kN, which cushioned the comb; a self-locking screw does not give. 0.8 m/s is twice the speed revision 4 is allowed, but I kept your load cases as the design basis.

Wheel load against tyre stiffness, kerb nose first:

| Tyre | Sinks under the standing load | 0.5 m/s | 0.8 m/s |
|---|---:|---:|---:|
| Rigid model | 0 | 9,350 N | 6,016 N |
| Hard solid tyre, 735 N/mm | 1.3 mm | 3,992 N | 4,069 N |
| 355 N/mm | 2.8 mm | 2,654 N | 3,557 N |
| 136 N/mm | 7.2 mm | 2,360 N | 3,342 N |

A real solid tyre is not rigid. Sheet 17 asks for a drive tyre no stiffer than 650 N/mm; the make and hardness of the wheel in the parts list would settle it (section 9).

Hand calculation on these loads: 68 rows, in the files. Safety factors against yield:

| Part | Factor | On |
|---|---:|---|
| Side rail 60 x 60 x 4, at the bolt holes | 2.10 | largest load-case wheel load |
| | 2.46 | kerb on the hard solid tyre |
| | 0.88 | rigid-tyre model (information) |
| Side rail, fatigue with bolted plates | range 44 MPa against 67 allowed | ASSUMED load history |
| Mast upright at the strut pin | 2.37 | largest comb load |
| Mast struts, pins, lug plates | 6.7 to 8.3 | same |
| Strut lug bolts / foot cleats (S355) | 3.02 / 2.98 | same |
| **Nose cross-member 50 x 50 x 4** | **1.55** | strut pull plus three times the standing castor load, together |
| Mast-base cross-member, base bracket, corner plates | 2.32 to 2.68 | actuator stalled against a stop at 9.5 kN |
| Lift stop blocks, bolts | 4.63 | same |
| Actuator holding (8.8 kN) | 2.18 | largest lift shock |
| Rail blocks / rail screws / carriage beams / plate | 2.66 / 2.15 / 2.48 / 2.02 | largest comb load |
| Castor pivot plates, castor beam | 3.2 to 4.8 | kerb strike; three times the standing load |
| Motor plate 8 mm | 2.37 | 904 N sideways, the largest in my runs |
| Bumper brackets | 7.3 and more | 1 kN side knock |

**One row is under 2.0: the nose cross-member, at 1.55.** It does not yield (229 MPa against 355), and at the robot's own top speed the factor is about 2.8, but it misses the standard I set myself. The fix is a 60 x 60 x 4 member, flush with the rails, which gives 2.32 and adds about 0.8 kg. It is noted on sheet 13 but not yet drawn or re-tested: I found it after the test campaign had run. The pad springs work at 768 MPa at full stroke against a 925 MPa limit, as designed.

### 3.7 Lane runs

All at 177.6 kg, 60 N m, with the speed rule. In every run, stalled or not, the bin stayed seated on the comb and never touched the ground.

| Run | Lane condition | Result |
|---|---|---|
| P1, P3, P7 take a full bin down; P2a return empty; P2c collect an empty 240 L bin | step ramped, trench covered, pothole filled | 5 of 5 pass |
| P4a, P4b (wet leaves) | same | 2 of 2 pass |
| P6a a person steps out on the 12 % wet descent | same | pass: stops |
| Sharp 40 mm step, down, full bin | as it is | pass |
| Sharp 40 mm step, up, full bin | as it is | **stalls** at the edge, with and without the boost |
| Open trench 40 x 200 mm, full bin | as it is | **stalls**, with and without the boost |
| Open pothole 60 mm under one wheel, full bin | as it is | **stalls** at 60 N m; passes with the boost |
| Return empty over the sharp step | step as it is | **stalls** at the edge |

On the lane with its three rough spots made good, revision 4 passes everything, more slowly than revision 3 (a full leg takes about 31 minutes of simulated time against 22). On the lane as it is modelled, it stalls at the step going up, in the trench and in the pothole. Revision 3 already stalled at the step. I had not run the open trench and pothole on revision 3, so I cannot say how much of that is new; the lower speed certainly makes it worse (3.5). So the three repairs your "made good" variant assumes are now a condition of use, not an option.

### 3.8 Driving software: 60 missions

Same 20 scenarios and 3 seeds as your set, at 177.6 kg with the longer nose, the speed rule of 3.3, a 75 Wh trip budget, and none of the true-position shortcuts.

| | Revision 3 (your run) | Revision 4 |
|---|---|---|
| Pass by your scorer | 48 of 60 | 48 of 60 |
| Fail the 50 Wh trip limit | 12 | 12 (the same missions) |
| Of those, fail for another reason too | 0 | 7 |
| Trip energy | 57.8 to 64.3 Wh | 67.1 to 74.7 Wh |
| Trip time | about 56 min | 62 to 72 min (mean 68) |
| Least hedge clearance | - | 0.198 m |
| Placement error, worst / mean | - | 79 / 45 mm |

The seven other failures:

- **Five are "too late".** All six three-bin evenings ran two trips and five of them then refused the third because it would end after 21:00. This is the cost of the speed rule. The sixth refused a grab instead (below).
- **Two refused a grab and drove home** (one at the camera gate, one after three camera tries). Both ended on the dock with the trip closed and the refusal counted. A refusal is the safe outcome, but your scorer rightly counts it as a failed mission.
- One of the "too late" missions also shows a gate decision that the true position does not support: the camera read the bin as inside the limits when its true angle was 3.3 degrees. The pick-up went through.

With the shortcuts removed the gate was right 19 times out of 21, wrong once each way. The seating check ran 16 times and passed 16 times; its sensor error was at most 12.9 mm.

**Energy as charge left at the end of the evening** (your suggested rule, at least 20 %): three trips at 70 to 75 Wh take 210 to 225 Wh. On a new 480 Wh battery that leaves 53 to 56 %. On an aged, cold battery (80 % x 85 % = 326 Wh) it leaves 31 to 36 %. The rule passes without a bigger battery. The observed charge after two trips was 57 to 59 %.

**Camera stress** (two missions each):

| Camera fault | Gate (camera) | Worst true offset at the gate | Seating check | Outcome |
|---|---|---|---|---|
| Noise 25 mm, bias 10 mm, 20 % of frames missing | accepted | 9 mm, inside | passed | completed |
| Bias 60 mm | accepted | 71 mm, outside | caught it (66 mm), re-docked, then passed | completed, placed within 43 mm |
| Bias 80 mm | accepted | 88 mm, outside | caught it (85 mm), re-docked, then passed | completed, placed within 58 mm |
| Bias 60 mm, seating check off | accepted | 49 mm | - | completed, placed within 64 mm |

A camera that is consistently wrong fools a camera-only gate. The seating check, which uses different sensors, is what catches it.

**The time problem, and three ways out.** I also ran the three-bin evening under two other speed rules:

| | Trip | Three bins | Longest simulated stop, wet | Status |
|---|---|---|---|---|
| Revision 4 as drawn: 300 mm bumper, rule of 3.3 | 62 to 72 min | two fit; the third would end after 21:00 | 122 mm | 60 missions |
| Faster rule: 0.5 m/s on the level with a bin, 0.4 empty; slower in three steps downhill | 57 to 64 min | back at 20:59, 21:00, 21:00 and 21:10 | 146 to 167 mm: at or over the 150 mm assumed | 4 missions, made before I tightened the rule |
| Brakes on the castors: 0.5 m/s up to 6 % downhill, 0.4 m/s steeper, robot 4 kg heavier | 54 to 55 min | back at 20:45 | 140 mm up to 6 % | 4 missions; stops simulated, brakes not designed |

The companion decides whether to start a trip by assuming it takes 50 minutes. No revision 4 trip is that short, so the 21:00 check needs the real trip time whatever is chosen.

### 3.9 Drawing checks

- 17 sheets. New: sheet 17 (bolt table with torques, lift stop order, speed rule, lowering, what to ask of the bought-in safety parts, three close-ups of the bolted joints). Sheet 15 (safety chain) and sheet 16 (dimensions) are redrawn.
- Solid-overlap check on the final model: 15 overlaps, all inherited from the B2-F CAD (anti-tip brackets, flares, stripes); none involves a part I drew. The pair you found in m-2 is no longer excused and is clear.
- Lift sweep in 1 mm steps: first contacts are the carriage beams on the stop blocks at −18 and +335 mm, then the switch bodies. No loom centre-line passes through a solid.
- The weight table is built from the same solids as the drawings: 177.60 kg.

## 4. Safety points that are still open

1. **The empty robot on a steep, slippery pitch.** Only the drive wheels brake and they carry 45 % of the empty weight. On the assumed 12 % pitch, nose first, the empty robot needs grip of about 0.3 just to hold; on wet leaves (0.22) it slides. No earlier test of either design covered this: the gate's emergency stop uses a full bin, and no test stops the empty robot on the pitch. It applies to B2-F as well. Ways out: brakes on the castors (stops about ten times shorter on that pitch in simulation), tail-first travel on steep pitches, or measuring the real pitch, which may be much gentler than 12 %.
2. **The bumper's real travel and the 0.15 s** are assumptions. The stop has to be measured on the built robot before it runs unattended.
3. **The slope-dependent speed limit lives in ordinary software.** A certified speed monitor can enforce one fixed limit. Selecting the limit by slope would need the inclinometer on a safety input. Not designed.
4. **A brake that fails to apply** roughly doubles the stop. The software needs a brake test at every start (drive gently against each brake in turn). Not written.
5. **A flat hand under a bin wheel** at set-down is seen neither by the load guard nor by the light beams. The robot sounds a warning before it lowers; that is all.
6. **No person-detection sensor is safety-rated.** Lidar, radar and cameras reduce the chance of a touch; the bumper and the speed rule are what is claimed.

## 5. Safety level: a first-pass estimate, not a verification

Method: the simplified procedure of ISO 13849-1, with typical component values as I recall them from its annex. None is from a part actually chosen, and I did not look the table up again, so treat the numbers as order of magnitude.

- **Structure.** Every stop function is two-channel with fault detection (category 3): two contacts per device into a safety controller that detects a broken wire or a short between channels, and two contactors in series whose mirror contacts are read back before every reset.
- **Wear.** The contactors open perhaps 10 times a trip, about 1,600 times a year. Even with a cautious life figure (400,000 operations to 10 % dangerous failures) that gives about 2,500 years to a dangerous failure per channel, which the standard caps at 100 years ("high"). The E-stop and limit switches are worked even less.
- **Result.** Category 3, "high", with medium fault detection gives PL d on the standard's chart. The bought-in units must each bring their own certificate: the safety controller, the bumper with its control unit (makers offer these at PL d, category 3), the light beams (PL c).

So PL d for the E-stop and front bumper, and PL c for the light beams and lift limits, look reachable with this structure. The estimate says nothing about points 1 to 5 of section 4, which are where the real risk sits, and it does not replace a calculation with the data of the parts bought, checked by a qualified person. ISO 3691-4 (driverless trucks) was not applied.

## 6. Cost notes (rough; ASSUMED unless a source is given)

- Safety bumper 300 x 150 x 700 mm with control unit: no quote. List prices I found for much smaller stock pieces are about 235 USD for a 100 x 200 mm section one foot long and about 619 GBP for a 100 / 200 mm unit (Sources). A made-to-size outdoor bumper with its control unit is likely to be EUR 700 to 1,500.
- Outdoor actuator, 6.8 kN: no price found. ASSUMED EUR 400 to 700.
- Safety controller EUR 300 to 550 and contactors with mirror contacts up to EUR 400: your figures.
- Two light-beam pairs: ASSUMED EUR 200 to 400. Laser-cut plates, bolts and crush tubes: ASSUMED EUR 150 to 250.
- Not adopted: an outdoor safety laser scanner. The list price I found is about EUR 6,000 to 7,800 (Sources), more than the rest of the robot.

In all, revision 4 is roughly EUR 1,500 to 3,000 above revision 3. Where money can be saved without touching function: used safety relays and contactors of a current type, laser-cut plates ordered as one sheet, a used outdoor actuator. The bumper should be bought new with its test certificate.

## 7. What I did not do

- No part is ordered, quoted or weighed. The actuator's weight and stall force, the bumper's travel and the brake response time are assumptions.
- The bumper is a rigid block in the simulation; its foam is not modelled. Stops are measured from the touch.
- Castor brakes, a 400 mm bumper and tail-first driving were not designed or drawn. Castor brakes were simulated as a torque on the castor wheels only.
- Tail-first travel and an angled step crossing are not in the driving software or the lane runs.
- The drawings are a concept: no part drawings, tolerances or hole positions.
- Fatigue uses an assumed load history.
- One braked-castor run on the 12 % pitch at grip 0.22 gave a stop of 0.72 m that I did not get to the bottom of.
- The review package of 15 November was read, not run.

## 8. Decisions for Brian

1. **Speed against bins per evening.** As drawn, revision 4 is safe by simulation with margin, but slower: two bins fit between 18:00 and 21:00, not three. To get three back there are two routes. Brakes on the castors are the better one: trips of 55 minutes, three bins home by 20:45, and they also fix the empty robot on the steep pitch. They need designing (I did not find a catalogue castor with an electric brake) and add about 4 kg. The other route, a faster rule with a deeper bumper, only just makes 21:00 and leaves no margin; I do not recommend it. I would also like to know what the 21:00 limit is: the bin at the road by then, or the robot home by then?
2. **Measure the lane.** Two numbers decide a lot: the steepest slope (the model assumes 12 %; the map data says 7.9 % at most) and whether any edge across the lane is higher than 20 mm. If the slope is under 9 %, the tail-first problem disappears. If there are edges over 20 mm, they need a small ramp.
3. **Weight.** Revision 4 is 177.6 kg and will not come down while everything is bolted and the bumper is 300 mm deep. I suggest dropping the 120 kg test, judging on the functional results, and capping a weighed prototype at 190 kg.
4. **Bolted or welded.** Bolting everything costs about 10 kg. If a fabricator welds the four frame corners and the two mast feet, about 8 kg comes back.
5. **Actuator.** An outdoor 6.8 kN unit that holds 8.8 kN, in place of the 4 kN unit whose data conflict. It costs more and weighs about 3 kg more.
6. **Revision 5.** If you agree: the 60 x 60 nose cross-member, castor brakes, tail-first or angled driving in the software where still needed, and a brake test at start-up.
7. **A qualified person** has to check the safety design before the robot runs unattended (section 5). That has not changed.
8. Still wanted from you, as before: the make and measurements of your own bins.

## 9. For the B2-F author: facts I need for my own testing

I am asking for facts and files only; I will run the tests.

1. Was B2-F ever run **empty** over the sharp 40 mm step, or **empty** down the 12 % pitch with a stop on the way? If result files exist, which?
2. Drive unit: weighed mass of gearmotor, brake, chain stage and wheel; brake torque and the time from power-off to full torque; motor constant and gearbox efficiency (the figures in M-8 are marked ASSUMED).
3. Drive wheel: make, tyre material and hardness, any stiffness figure.
4. Castor: make and type, swivel offset, tyre profile.
5. Battery protection: current limit and for how long; main fuse type.
6. Lane model: which of the 12 % pitch, the 40 mm step, the trench and the pothole were surveyed and which assumed.
7. The 21:00 limit: its source, and whether it applies to the bin at the road or the robot back on the dock. The companion assumes a 50-minute trip in that check (`c + 50.0`); please confirm that is intended.
8. Comb: how the nib is fixed to the comb plate in B2-F (welded, or screwed).
9. Your firmware model lifts at 30 mm/s; which actuator is that?

## Files

- `REPLY_and_REV4_2026-11-20.md`: this note.
- `BinRobo_rev4_drawings_A3_2026-11-20.pdf`: 17 sheets, A3. `BinRobo_rev4_drawings_png_2026-11-20.zip`: the same as PNG.
- `rev4_files_2026-11-20.zip`: scripts, switches, command lists, every result file, the tables behind this note, and a README.

## Sources

- LINAK LA36 data sheet (forces, self-locking force, speeds, IP rating, built-in dimension): https://media.distrelec.com/Web/Downloads/_e/ng/linear_actuator_la36_data_sheet_eng.pdf
- FDI 4000 N actuator, the two listings that disagree: https://botland.store/15868-linear-actuator-super-power-jack-4000n-6mms-24v-40cm-stroke.html and https://www.anodas.lt/en/fdi-linear-actuator-24v-400mm-6mm-s
- Safety bumper travel (a 150 mm bumper at 0.5 m/s: switching travel and after-travel): https://products.schmersal.com/upload/orig/10/00/20/01/DOC_MAN_MEC_mrl-ssg-sbl_SEN_AIN_V3.pdf
- Bumper test pieces and force limits for driverless vehicles, as summarised by NIST: https://nvlpubs.nist.gov/nistpubs/ir/2015/NIST.IR.8029.pdf
- Bumper list prices: https://cdn.automationdirect.com/static/specs/asosentirbumpers100x200.pdf (ASO, 100 x 200 mm section); ABB ASB 100/200 on voltimum.co.uk; ASO's PL d, category 3 statement on unchainedrobotics.de.
- Outdoor safety laser scanner list price: https://nl.rs-online.com/web/p/light-detection-and-ranging/2856778 and https://befr.rs-online.com/web/p/light-detection-and-ranging/2856789
- The three review reports of 14 November and the review package of 15 November (read, not run).
