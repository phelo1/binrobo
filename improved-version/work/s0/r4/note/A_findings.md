## 1. The three reports, finding by finding

I checked each finding against my own files and runs before changing anything. "Agreed" means I reproduced it.

### Cold-eye review

| Finding | My check | Revision 4 |
|---|---|---|
| **B-1** The 15 mm bumper cannot stop the robot; lowering has no safety function; docking presses the bumper | Agreed. One correction that does not change the conclusion: the robot's top speed in every gate, lane and driving file is 0.5 m/s, not 0.8. At 0.5 m/s the revision 3 robot still needed 134 to 172 mm on level ground after a bumper touch, and far more downhill. | A 300 mm foam safety bumper with its own control unit. Speed now depends on the slope, so that the simulated stop stays inside the bumper (3.3). A load-drop guard and two light beams for lowering (3.4). The charge pads moved under the nose, so docking no longer touches the bumper. What is still open is in section 4. |
| **M-1** Weight; the 120 kg gate | Agreed that 120 kg is a comparison figure and that the test should be on what the robot does. Revision 4 makes this harder, not easier: it weighs 177.6 kg, above the 165 kg cap you suggest. Section 3.1 says where each kilogram comes from. | Brian decides the cap (decision 1). I report the functional results (energy, step, stop, tip) in section 3. |
| **M-2** Side rail and fatigue at the welded corner plate | Agreed. On the rigid-tyre load I ran the tyre question directly instead of arguing it (3.6): a hard solid tyre that sinks 1.3 mm under the standing load gives a 4.0 kN wheel load on the kerb, against 9.4 kN for the rigid model. | Rails are 60 x 60 x 4 S355. The corner plates are bolted, so no weld is left on the rail. Rail safety factor «RAIL_SF» on the design wheel load, «RAIL_SF_T20» on the hard-tyre kerb load, «RAIL_SF_RIGID» on the rigid-model peak (information). Fatigue check with bolted plates: «RAIL_FAT». |
| **M-3** Actuator's own end stops, closed length, stop load | Agreed. | The actuator is drawn with its pin spacing: 600 mm closed, 615 mm with the comb down. Its base bracket sits on a shim pack, so the actuator's own stops are set on assembly to −15 and +331 mm of lift travel: outside the limit switches (0 and 327) and inside the stop blocks (−18 and +335). The actuator therefore switches itself off before it can stall on a block. Sheet 17 shows the order. Blocks and bolts are sized for 9.5 kN (1.4 times the rated 6.8 kN, ASSUMED until the maker states the stall force): bolt safety factor «STOP_SF». |
| **M-4** Welds in a bolted DIY build | Agreed. | No welded joint is left: frame corners, mast feet, mast struts, lift stops, castor pivot, castor beam, bumper carrier and actuator brackets are all bolted. Sheet 17 has the bolt table with torques. Bolting costs about 9 kg against welding. |
| **M-5** Safety sheet gaps (10 items) | Agreed on all ten. | 1: a first-pass estimate is in section 5; it is not a verification. 2: the safety controller is described by what it must do (10 two-channel inputs, two safe output pairs, speed monitoring); I did not pick a type. 3: rear bumper switches specified with two NC contacts. 4: contactors with mirror contacts are required on sheet 15 and in the parts list. 5: the lift feed now runs through two safety relay contacts; the driver's enable input is no longer the safety function. 6: lowering, see 3.4. 7: holding, see M-6. 8: speed and standstill monitoring is asked of a certified module with two wheel sensors, not of home-built boards. 9: tilt is sensed by one switch and one inclinometer. 10: docking no longer presses the bumper. |
| **M-6** Actuator data conflicts | Agreed. The two listings of the FDI unit disagree on sealing (IP42 against IP65) and length (595 against 620 mm), and neither gives a holding force. | That unit is dropped. Drawn instead: an outdoor actuator of the LINAK LA36 class, 24 V, 6.8 kN, 350 mm stroke. Its data sheet gives a self-locking force of at least 8.8 kN, IP66 and built-in end stops (Sources). Measured shock on the lift in simulation: 3.1 kN at 0.5 m/s over the kerb, 4.0 kN at 0.8 m/s (3.6). Weight 6.5 kg is ASSUMED: I did not find it stated. Still to get in writing before ordering: weight, stall force, price. |
| **M-7** Castor round-tyre claim | Agreed: I overclaimed. I mapped the slippery hill start against the width of the castor's contact strip (3.5). Only the full 50 mm flat model fails. Every width from 16 to 44 mm passes on heading. | The requirement is reworded: a crowned or rounded tyre whose contact strip is no wider than about 40 mm. The bench test you propose (swivel torque under load) stays as the check before ordering. |
| **M-8** Goalpost moves | Torque: I withdraw the request for 80 N m. The limit stays at 60 N m (3.5). Energy: agreed, restated as the charge left at the end of the evening (3.8). Weight: see M-1. | See 3.5 and 3.8. |
| **m-1** Pad springs too close to solid | Agreed. | Springs 145 mm free, 135 mm fitted: 15.8 mm left before solid at full stroke (9.9 needed). Both ends are guided: the springs run in bores through the guide block and sit in 5 mm pockets in the cup plate. |
| **m-2** Actuator body inside its base bracket | Agreed. | New base bracket. The clash check no longer excuses this pair and finds no overlap. |
| **m-3** Mast foot bolts | Agreed. | Each upright stands on two angle cleats (2 x M12 down through the cross-member, 2 x M8 through the upright, all in crush tubes). Two struts now carry the tipping load of the hanging bin to the nose cross-member. Safety factors in 3.6. |
| **m-4** Motor plate under sideways tyre load | Agreed that it was not checked. | Plate is 8 mm with a top flange bolted up through the rail. I measured the sideways tyre force in simulation: at most 904 N (pivot turn with a full bin). Safety factor «PLATE_SF» at that load. |
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
| 23 of 180 pick-ups needed a second approach | Agreed. | Revision 4: «REAPP» (3.2). |
| The lift runs at its 3 kN cap | Agreed. | The new actuator has 6.8 kN and holds 8.8 kN. The shock is now measured with the cap out of the way (3.6). |
| The gate file's tip hand-calculation block was stale (36.5 degrees) | Agreed: the scorer reads B2-F's untagged file. | My collection script now feeds it revision 4's own calculation: «TIP_DEG» degrees. |

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
