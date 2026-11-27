## 2. Why a person was hit

I ran the reviewers' case with the revision 5.1 settings on my side: three seeds, a person who walks out of the far hedge at night and stops in the robot's path. Result: contact in two of three runs, at 0.28 and 0.30 m/s. In the third the robot stopped 0.44 m short. So their finding stands.

Three things caused it.

1. **The camera could not see them.** The front camera looks 55 degrees to each side of straight ahead. Someone who starts at the far hedge when the nose is 1 m from their line is 68 degrees off the nose. They only come into view once they are nearly in front.
2. **The lidar saw them and the software ignored it.** The lidar had the person in sight for the whole 2.5 s. But the lidar stop logic I had kept from B2-F only reacts to things inside the robot's own path: its width plus 0.2 m each side. A person walking towards the path did not count until they were in it.
3. **My own tests stopped too early.** "2.6 m ahead" in the test is measured from the robot's axle to the middle of the lane. The nose was 1.0 m from the person's line when they set off. My closest test in revision 5.1 had the nose 2.0 m away.

The review asks whether the camera model has extra latency, because the person in my "3.5 m" runs was only found at 2.2 to 2.6 m. It is not latency. It is the same geometry: for the first second and a half the person is outside the camera's view.

The same gap explains their other two findings: a walker who comes from behind (0.38 m from the robot's side) and one who stands beside it (0.48 m) never enter the front camera's view, so the robot did not react to them at all.

## 6. The rest of the review, point by point

### Blockers

**B-1. The hill is not bounded at 8.5 %.** Agreed. I wrote "8.5 % at most" in the summary of the last note and that was wrong: 8.5 % is the smoothed figure, and the raw elevation cells allow 10 % over 25 m. Nothing I can do at a desk settles it. What changes:

- The survey in the test list is now the reviewers' method: a 2 m straightedge with a phone inclinometer, both wheel tracks, every 5 m from the house to 300 m (section 7, test 1).
- A leaf-season speed table, as M-5 asks: 0.35 m/s on the level and gentle slopes, and the fast cruise held to 0.5 m/s with a full bin and 0.15 m/s empty on the steep part. It is a setting, because the robot cannot see leaves.
- A leaf-season switch for the owner (`X_LEAF_NOGO=1`): pick-up trips, where the robot goes down the hill with no bin, are refused with a message. Until the hill is surveyed this should be on from October to December. Tested: the pick-up is refused at the dock.
- If the survey finds more than 8.5 % anywhere, the empty robot needs more braking: tail first down the hill, or brakes on the castors. With a lidar now on each rear leg tip, tail first has the sensing it lacked in revision 5. I have not designed or tested it for revision 6.

**B-2. The stop chain on sheet 15.** Agreed on all six points. Sheet 15 is redrawn:

1. One diode across each contactor, not one across both. A shorted diode now bridges one contactor only.
2. Two chains. The drive stop relay takes the e-stop, the nose and rear strips, tilt and the three watchdogs, and drops both contactors. The lift limit switches and the lift interlock work a separate pair of relays (K4, K5) that cut the lift feed only. The under-bin sensors are plain inputs to the lift driver's enable.
3. Relay outputs. The drive stop relay's three contacts go to contactor 1, contactor 2 and the supply of K4 and K5. Pre-charge is drawn as a sequence: the companion closes K3, the controller side charges through 1 kohm, then the reset closes the contactors.
4. Feedback without auxiliary contacts. The reset is refused unless the voltage on the controller side has fallen below 5 V within 3 s of the last stop. That is the B2-F voltage sense, and it also catches a shorted diode.
5. Single-channel sources (the watchdogs, the speed and tilt electronics) each drive a relay with linked contacts, one contact in each channel. Said on the sheet.
6. The brake coils are fed from the switched side, and drawn.

The sheet no longer claims a performance level. It says what the layout gives: no single stuck contactor, welded relay or shorted diode keeps the motors live. Each row is proved by a test in section 7.

### Major findings

**M-1. What the front camera cannot see.** Section 3. Each of the four gaps has a rule and a test: restart beside a person (cases "side" and "flank"), pivot flanks (the pivot rule and the two road-end tests), a false pause that never ends (a camera sighting must match a lidar object, and the hold now sums the pauses), and the rear side (the two rear lidars are in the simulation; the rear camera still is not).

**M-2. Detector computer.** Accepted. The cost now carries an RK3588-class board or a Pi 5 with an accelerator (EUR 60 to 130). I misread the forum thread in the last note: its last reply fixes the slow model and reaches about 13 pictures a second. And a Pi 5 alone was a poor fallback. Test 11 now runs with the full mission software.

**M-3. Bye-law and clock.**

- The two-window check is now the default and the old "trip takes 50 minutes" branch is deleted.
- The return time is a setting, `X_RET_BY`. I left it at 21:00. The council's own web page says bins must be in by 9.00 pm; the reviewers read midnight in the bye-law text. I could not open that PDF, so I have not checked their reading. 21:00 satisfies both. With the fast cruise it no longer matters: three pick-ups started at 18:00 are home before 20:00.
- New setting `X_CREW_FROM`: a drop-off started after midnight must be finished before the time the lorry may come.
- Not done: the quiet-hours default in the code is still 22:30. It is switched off in the settings file, as in 5.1.

**M-4. The tests on the built robot.** All comments taken. The new list is in section 7. Test 3 as I wrote it (hold a contactor closed by hand) was unsafe and is replaced by the fused jumper.

**M-5. Wet-leaf margins on the level.** Agreed. With a 0.20 s reaction my simulation gives 159 mm at 0.4 m/s for the empty robot on wet leaves, past the foam, and 130 mm at 0.35 m/s. The leaf-season table uses 0.35 m/s.

### Minor findings

| Item | Reply |
|---|---|
| m-1 Energy budget | Now adaptive: the larger of the set budget and 1.25 times the dearest trip so far. |
| m-2 Actuator shim | Corrected on sheet 17: shim to the bottom stop (-15 mm); the top stop then falls at 331 to 335 mm. |
| m-3 Stale text on sheet 13 | Corrected: loom L11 and item 75. All 18 sheets are reissued. |
| m-4 Hedge clearance 0.197 m against "0.20 m" | The rule is what the planner aims for. The least driven clearance is reported separately (section 5). |
| m-5 Pivot nose speed | The cause was in the firmware settings, not the command: section 4.6. The side faces of the nose are the sides of the same foam block, 936 mm wide, so there is no hard part behind them for more than 150 mm. The switch strips now run round the two cut-back corners as well, because in a turn the corner leads. |
| m-6 Score not re-run | Re-run in full, and once more with a false camera person every minute (section 5). |
| m-7 Cost risks | Taken into the range (section 8), except a new actuator: if no used one with the right gear and stroke turns up, add EUR 540 to 810. |

### The mission-simulation report

| Finding | Reply |
|---|---|
| 48 of 60 on the frozen criteria; the 12 full missions fail the 50 Wh limit | Section 5. With the fast cruise a trip uses less energy, because the electronics run for half the time. |
| Contact when someone steps out close ahead | Sections 2 and 3. |
| Behind and beside: no pause at all | Section 3. |
| The 15-minute hold never fires | The hold now counts all pausing in the last 20 minutes. |
| One false person a minute: 87 pauses, +4.7 minutes | A camera sighting only stops the robot if a lidar object is at the same place, or if it is within 2.5 m. Section 3.3. |
| s3a seed 7 on firmware 4.6.2: the loaded pivot ran at 0.30 rad/s and touched the parked green bin | I only have firmware 4.7.2 and could not reproduce the contact. I did find why the turn rate overshoots, and fixed it: section 4.6. Please re-run that seed. |
| The final reverse onto the bin steers on the true pose plus one fixed camera error | Still so. The rear-camera model is idealised. Open. |
| The slope rule picks "full bin" or "empty" from the true bin mass | Still so in the simulation. On the robot the load comes from the lift current when the bin is picked up; if there is no reading, the empty column applies. Test 10 now includes calibrating it. |
| Every pause restarts the no-fix timer | Still so. The robot is standing while it pauses. |

### The physics report

| Finding | Reply |
|---|---|
| 8.5 %, empty, wet leaves, 0.15 m/s: 170 mm against my 120 mm | The difference is the mass table: you had to use a stand-in. Mine is in the pack now (`stop_tests/mass_cgB2_r5.json`). With the new brake torque my figure is 107 mm. |
| Short 25 m ramps of 10 to 12 % slide or run away | Agreed. That is B-1. |
| Meeting the brow at level speed: 496 mm | The slope look-ahead from the map is 3 m at the touch-safe speeds and 8 m at the fast cruise, so the robot is at the hill speed before the brow. This rests on the map. A check against the robot's own pitch reading would cover a wrong map. I have not written it: the mission simulation has no pitch. Open. |
| The hold test only checked creep where the robot ended up | The lane runner now records the overrun past the hold point and fails the run above 1.0 m. |
| Result file names round the slope to whole per cent | Names now carry tenths of a per cent. |
| Send the revision 5 mass table | In the pack. Brian: the reviewers say the revision 5 pack of 21 November never reached them. Please forward `REPLY_and_REV5_2026-11-21.md` and `BinRobo_rev5_tests_2026-11-21.zip`. |

## 7. Tests on the built robot

Do them in this order. No unattended running until 1 to 9 pass. No fast cruise until 13 passes.

| # | Test | How | Pass |
|---:|---|---|---|
| 1 | Hill survey | A 2 m straightedge or straight board with a phone inclinometer or digital level. Both wheel tracks, every 5 m from the house to 300 m, three readings each. Note the cross-fall as well. | No reading over 8 %. Any over 8.5 %: tell me before the robot runs empty down the hill. |
| 2 | Stop chain | Wheels off the ground, motors turning. Press the e-stop, squeeze each switch strip, trip the tilt switch, pull the companion's plug. Measure the voltage on the controller side. | Both contactors drop every time. Voltage under 5 V within 3 s. No restart without the reset button. |
| 3 | One fault at a time | Wheels up. Never hold a contactor by hand. Put a fused jumper across the main terminals of one contactor, press the e-stop; repeat on the other. Then a jumper across one diode. Then short the two loop channels together. Then open one channel. | Motors dead each time. Reset refused each time. |
| 4 | Soft nose | Push a 70 mm post into the foam with a luggage scale: front, both corners, both sides. Repeat after a wet night at 0 C or below. | Switch acts within the first 20 mm. 150 mm of give at no more than 25 kg, also when cold. Use closed-cell or sealed foam. |
| 5 | Stop after a touch | Drive into a padded post at each touch-safe speed: level, mid-hill and steepest part; full bin and empty; dry, hosed wet, and on wet leaves at the steepest part with the robot empty. Film at 240 pictures a second to get the reaction time. | 130 mm or less. Reaction 0.15 s or less. |
| 6 | Holding | Park on the steepest part, full bin and empty, nose down and nose up, wet, and empty nose down on wet leaves. Power off for 10 minutes. | No creep. |
| 7 | People: ahead | Walk towards the robot, stand, step out at 5 m and at 3 m. By day, at dusk and in the dark; dark clothes; a 1 m dummy; a dog. 20 passes each. | Standing still before 3 m in all 20. Log every miss. Twenty clean passes only show the miss rate is under about 14 %. |
| 8 | People: all round | Step out from the side 1 m ahead of the nose. Walk up from behind. Walk past the nose and stop beside the robot. Stand at each flank while it is about to turn at the dock, at the bin and at the road, and walk up while it is turning. | It stands still each time and does not move or turn until you are 3 m away. |
| 9 | False pauses | Ten trips with nobody about, at night and in rain, past the real gateposts and bins. Log where each pause happens. | No more than one pause in the ten trips. |
| 10 | Lift | Run to both ends. Put a 10 mm block, a 20 mm block and a hand-sized 25 mm foam block under a bin wheel and lower. Lift the bin off by hand while lowering. Check the current limits at 0 C. Weigh three bins and note the lift current for each. | Limit switches act before the actuator's own stops. No lowering onto a block. Stops and raises. Lift current tells a full bin from an empty one. |
| 11 | Detector speed | Both cameras and the full mission software running; log pictures a second for ten minutes. | 5 or more on each camera. |
| 12 | Reverse | Back onto a padded post at 0.1 m/s. | The rear strip stops it. |
| 13 | Fast cruise | Only after 1 to 12. A dummy pulled across the lane 3 m, 2 m and 1 m ahead of the nose at 0.6, 0.8 and 1.0 m/s; a dummy standing at a gateway; a box left in the lane. Then tests 5 and 6 at the fast speeds for the stop distance. | Stopped before the dummy at 3 m and 2 m. Note the speed at the touch at 1 m. Stop distances within 20 % of section 4.4. |
| 14 | Lidar | A 0.4 m box in the path; a 0.2 m box, which is below the lidars. | Stands still 3 m from the tall box and reports the path blocked. The nose strip stops it at the low one. |
| 15 | Remote stop | Stop over 4G; then switch 4G off in mid-trip. | Stops. Carries on or holds as set, and says so. |
| 16 | Bolts | Torque wrench on every structural bolt after ten trips. | None has moved. |
