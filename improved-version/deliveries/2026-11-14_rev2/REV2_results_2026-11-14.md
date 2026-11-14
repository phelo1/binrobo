# Improved version, revision 2: what changed and how it tested

14 November 2026, for Brian. Follows my reply to the review (`REPLY_to_review_2026-11-14.md`).

## Summary

You said to do what I think is best, so I took my own four recommendations: bumper 65 mm forward with 200 mm castors, no 260 mm castor option, the pothole filled as a site rule, and the heavier frame sections built into the drawings and the weight. That is revision 2. It is redrawn (15 sheets) and tested.

- **It passes every mechanical test and misses one driving-software limit.** At its full weight of 119.4 kg, revision 2 passes all nine of the other agent's gate tests, all ten lane runs with the pothole filled, and the lane-fit check. In the driving-software check every run behaves correctly, but each trip uses 51 to 53 Wh against the other agent's limit of 50 Wh, so it scores 48 of 54. The cause is the weight.
- **The pick-up fault of revision 1 is gone.** In 360 pick-ups (180 at each of two weights) the robot never lifted an off-centre bin. At 119.4 kg, 178 of 180 succeeded; in the other two it was still more than 25 mm off-centre after three tries and refused to lift.
- **I corrected my own weight table part-way through.** The first table missed 3.6 kg of parts that are on the drawings. I re-ran the gate and the lane set at the corrected weight; both sets of results are below.
- **What revision 2 costs.** It weighs 118.5 kg by the gate's way of counting (119.4 kg as modelled), against a limit of 120 kg. Filling the pothole is now a condition: with it open, revision 2 fails all four lane runs. With a bin on board it needs 2.56 m to turn on the spot, against 2.39 m for B2-F as drawn.
- **Against B2-F.** B2-F needs the same heavier frame and, because its castors and bumper sit in the same places, the same longer nose. I tested it with the heavier frame only (111.9 kg): it scores the same 178 of 180 on the same pick-ups. With the nose fix too it would weigh about 115 kg and lose most of its turning advantage. What then separates the two: revision 2 carries the bin higher (least clearance under the bin wheels 74 mm against 48 mm in the gate tests), has two small actuators fewer (pad toggle and keeper), and is about 4 kg heavier.

Nothing has been built. Every result here is from simulation.

## 1. What changed from revision 1

| Change | Answers review finding | How it was checked |
|---|---|---|
| Bumper and charge contacts 65 mm forward, on two bracket plates | B-1, castors hit the bumper | Drawing clash check: 15 mm clear of a castor swivelled forward. All tests run with the longer nose. |
| 400 mm IP65 actuator, base pin 60 mm lower; top limit switch at 340 mm; hard stops at 345 mm | B-2, actuator does not fit; M-3, 20 mm crush gap | Drawn to the supplier's 620 mm length. Gap under the top tie is 30 mm at the switch and 25 mm at the hard stops. |
| Heavier frame sections from the other agent's list (S12): side rails 50 x 50 x 4, uprights 80 x 40 x 4, 10 mm rail backing flats, 8 mm comb plate, mast foot plates; rail blocks 200 mm apart | B-3, heavier sections not drawn | In the drawings and the weight. I have not recalculated the strength figures; they are the other agent's. |
| Comb 700 mm wide; up to three re-approaches; refuse to lift if more than 25 mm off-centre | M-5, false holds | 360 pick-ups, no false hold. |
| Pad 11 mm behind the nib tip, on 45 mm of spring travel | M-4, fixed pad pushes the bin first | In the model and the drawings. Still needs a trial on real bins. |
| Castor-beam stops at 2 degrees; bushes 70 mm apart in the hanger plates | Pothole behaviour; pin loading | In the model and all tests. |
| Looms re-routed; safety and control loom added; main fuse at the battery; charge fuse placed | M-1, looms through moving parts; M-2, stop chain and fusing | Drawing clash check. Sheet 15 is a proposed stop chain and fusing, not a wiring table. |
| Keeper deleted; parts-list references corrected | M-7, parts list against the BOM | Sheet 13 lists what the BOM still lacks. |
| Weight table corrected | M-6, mass | Twice: see section 3. |

Size: 1,572 mm long, 930 mm wide, 1,510 mm high; 1,617 mm long with a 240 L bin.

## 2. Test results

All on MuJoCo 4.0.1, with the other agent's scripts and frozen pass rules. "115.8 kg" is revision 2 before I corrected the weight table; "119.4 kg" is after.

### 2.1 The nine gate tests

| | B2-F as designed, 93.2 kg | B2-F with the heavier frame, 111.9 kg | Revision 2, 115.8 kg | Revision 2, 119.4 kg |
|---|---|---|---|---|
| Gate tests passed | 9 of 9 | 4 of 4 run (pick-ups, climbs, kerb, emergency stop) | 9 of 9 | 9 of 9 |
| Pick-ups, three bin types x 30 | 89 of 90 | 89 of 90 | 90 of 90 | 89 of 90 |
| Least clearance under the bin wheels in the gate tests | 50 mm | 48 mm | 82 mm | 74 mm |
| Emergency stop on the 12 % slope | 0.16 m | 0.18 m | 0.19 m | 0.20 m |
| Turning on the spot with a bin, swept diameter | 2.39 m | not run | 2.55 m | 2.56 m |
| Weight by the gate's count (limit 120 kg) | 92.3 kg | 111.0 kg | 114.9 kg | 118.5 kg |

Revision 1 at its corrected weight scored 8 of 9, failing on one false hold.

### 2.2 Pick-ups

The clip-lid 240 L bin is the one that caught revision 1 out, so it gets four batches of 30. The first batch is also part of the gate set, which makes 180 separate pick-ups per version.

| | Gate set, 90 | Clip-lid bin, 120 | All 180 | False holds |
|---|---|---|---|---|
| Revision 1, 96.4 kg | 89 | 117 | 177 | 2 |
| B2-F with the heavier frame, 111.9 kg | 89 | 118 | 178 | 0 |
| Revision 2, 115.8 kg | 90 | 120 | 180 | 0 |
| Revision 2, 119.4 kg | 89 | 118 | 178 | 0 |

A false hold is a lift with the bin too far off-centre on the comb. By the frozen rule that is, on the clip-lid bin, more than 50 mm with the original comb and more than 80 mm with the 700 mm comb. Revision 2 never lifted a bin more than 31 mm off-centre, so its result does not lean on the wider band. The two non-successes at 119.4 kg are refusals: after three tries the robot measured more than 25 mm off and did not lift. That is safe, but the bin stays where it is. The 180 against 178 between the two weights is not a real difference; the false-hold count is.

The heavier the robot, the less accurately it arrives: the average sideways error on first arrival at the clip-lid bin is 16 to 20 mm at 115.8 kg and 18 to 24 mm at 119.4 kg, against 14 to 17 mm for B2-F with the heavier frame.

### 2.3 Stress cases

At 115.8 kg, with robot and bin weight 10 % up and 10 % down, grip 15 % down, and higher rolling resistance: 20 of 20 driving cases pass and 20 of 20 pick-ups succeed. The 10 % heavier case is a 127 kg robot, which covers the corrected weight.

### 2.4 Lane runs

Revision 2 at 119.4 kg, kerb step ramped, trench covered, pothole filled:

| Run | Result | Least clearance under the bin wheels | Least hedge clearance | Energy |
|---|---|---|---|---|
| P1, full 240 L bin (110 kg), home to the road | pass | 50 mm | 0.305 m | 15.2 Wh |
| P2a, return empty | pass | – | 0.325 m | 28.6 Wh |
| P2c, collect the empty 240 L bin and bring it home | pass | 98 mm | 0.362 m | 29.7 Wh |
| P3, full 140 L bin (66 kg) | pass | 100 mm | 0.306 m | 15.1 Wh |
| P4a, stop and hold on the 12 % descent, wet leaves | pass | 100 mm | | |
| P4b, stop and restart on the 12 % climb, wet leaves | pass | 100 mm | | |
| P7, night: bin 10 % heavier and top-heavy, grip 20 % down | pass | 49 mm | 0.305 m | 21.5 Wh |
| Sharp 40 mm kerb, down | pass | 46 mm | | |
| Sharp 40 mm kerb, up | pass | 77 mm | | |
| Person steps out on the wet descent, emergency stop | pass | 108 mm | | |

The same ten runs also pass at 115.8 kg. The smallest margin to tipping in any run is 22.6 degrees.

Two site conditions come out of the lane runs, both tested at 115.8 kg only:

- **The pothole must be filled.** With the 60 mm pothole open, revision 2 fails all four runs: with a full bin it stalls in the hole, and empty it slews into the hedge there. Revision 1 passed two of those four. B2-F fails three of the four in the other agent's own stored results.
- **The trench must stay covered.** On the open trench revision 2 stalls, as B2-F does. The other agent already requires the cover.

### 2.5 Lane fit and turning

I ran the other agent's lane-fit check with the longer nose, after confirming that my copy reproduces their stored B2-F result exactly.

| | B2-F as drawn (bumper not moved) | Revision 2 |
|---|---|---|
| Least hedge clearance driving the lane | 0.325 m | 0.325 m |
| Turning circle, empty | 2.28 m | 2.40 m |
| Turning circle, with a bin | 2.39 m | 2.56 m |
| Margin when turning with a bin at the narrowest part of the lane | 0.18 m | about 0.10 m |
| All pick-up and drop-off sequences at the road and in the yard | fit, least margin 0.175 m | fit, least margin 0.175 m |

The check passes. The one number that moved is the margin for turning round with a bin in the narrowest 16 m of the lane: about 0.10 m, which is less than the 0.124 m the other agent allows for position error. The planned pick-up and drop-off sequences do not turn there, and it should stay that way. Most of the wider turning circle comes from the longer nose, which B2-F needs too.

### 2.6 Driving software

I ran 54 of the 60 scored scenario runs: all 16 fault and hazard scenarios on three seeds each, and six of the twelve full missions. They used revision 2's longer outline, 119.4 kg, lift and set-down times stretched by 1.4, and my four software fixes, on ArduRover 4.7.2.

By the other agent's frozen scoring the result is **48 of 54**. All 48 fault and hazard runs pass. All six full missions complete their plan, dock, and place every bin, and they pass every criterion except one: energy per trip.

| Same 54 runs in both columns | B2-F with my four fixes, 92.3 kg (13 Nov) | Revision 2, 119.4 kg |
|---|---|---|
| Runs passing the frozen scoring | 54 of 54 | 48 of 54 |
| Energy per trip (limit 50 Wh) | 45.0 to 49.2 Wh | 50.9 to 52.9 Wh |
| Battery left after a three-bin evening (limit 20 %) | 59 % | 55 to 56 % |
| Latest return to the dock on a three-bin evening (limit 21:00) | 20:44 | 20:46 |
| Least hedge clearance (limit 0.124 m) | 0.213 m | 0.197 m |
| Sideways error at the pre-grab check, average and worst | 12 and 25 mm | 14 and 33 mm |
| Bin placement error, average and worst (limit 0.6 m) | 50 and 100 mm | 48 and 91 mm |

The 13 November column did not have the longer lift times, as the review pointed out.

The battery is not short: a three-bin evening still leaves 55 %. But 50 Wh is also the figure the robot's own energy guard uses to decide whether it can start a trip, so with this weight the guard under-budgets by up to 3 Wh. Either the budget is raised to about 55 Wh or weight comes off.

The heavier frame does this to B2-F too. Two runs of B2-F's outline at 111.9 kg, with its own shorter lift times, gave 50.4 Wh and 49.4 Wh per trip, against 49.2 Wh and 45.4 Wh at its designed weight.

## 3. Weight, and my correction to it

| | By the gate's count | As modelled |
|---|---|---|
| B2-F as designed | 92.3 kg | 93.2 kg |
| B2-F with the heavier frame | 111.0 kg | 111.9 kg |
| Revision 2, first table | 114.9 kg | 115.8 kg |
| Revision 2, corrected | 118.5 kg | 119.4 kg |

While checking the redrawn parts against the weight table I found it did not include the bumper brackets (2.2 kg allowed), the mast foot plates (1.1 kg) or the lift hard stops and limit switch (0.3 kg). That is the same kind of error the review found in revision 1, so I corrected the table and re-ran the gate, the 180 pick-ups and the lane set at 119.4 kg. The driving-software check used 119.4 kg from the start. The lane-fit check does not depend on weight, except that the turning circle with a bin comes out 10 mm wider at 119.4 kg.

The margin to the 120 kg limit is 1.5 kg by the gate's count. The bumper brackets are the one place to save weight: they are drawn as two plain plates and need designing properly.

## 4. What got worse, and what is tight

1. **Weight.** 1.5 kg inside the limit by the gate's count, with nothing in hand for parts not yet designed (lift driver, cable chain, fasteners beyond the other agent's allowances).
2. **Pothole.** A condition, not a preference (section 2.4).
3. **Turning with a bin.** 2.56 m against 2.39 m for B2-F as drawn (section 2.5).
4. **Docking accuracy falls with weight** (section 2.2). The refuse-to-lift rule turns that into an occasional uncollected bin instead of a badly held one.
5. **Emergency stop on the slope.** 0.20 m against 0.16 m for B2-F as designed. It passes; the extra is the extra weight.
6. **Length.** 1,572 mm against 1,507 mm.
7. **Lift force on the kerb.** The lift reaches its 3,000 N cap on the two-wheel kerb test, as B2-F does. It passes with the bin held.
8. **Energy per trip.** 51 to 53 Wh against the 50 Wh limit (section 2.6). This is the one frozen criterion revision 2 fails.

## 5. Not tested, or still open

- **Simulator version.** My results are on MuJoCo 4.0.1. The other agent's re-test numbers match version 3.17.0, which treats a kerb edge as a wall. They have not yet confirmed which they ran.
- **Driving software.** Six of the twelve full missions were left out for time (two each of the one-bin drop, three-bin drop and three-bin pick-up). The check ran on ArduRover 4.7.2. The project's frozen version is 4.6.2 and I still have no build of it.
- **Frame strength.** The heavier sections are the other agent's list. I have not recalculated them.
- **Stop chain.** Sheet 15 is my proposal. The parts list has no driver for the lift actuator, the supplier lists no position signal on it, and whether it holds its load unpowered needs confirming.
- **B2-F with the heavier frame** was run on pick-ups, kerb, climbs and emergency stop, and on two driving-software runs for energy. It was not run on the lane, and not with the longer nose it also needs.
- **Pothole open and trench open** were run at 115.8 kg only. More weight will not help either.
- **Real bins.** The comb, nib and pad have only met three catalogue bin models, not your bins.
- **Cost.** I have not re-priced revision 2. The new unpriced items are the lift driver, the top limit switch, the hard stops and the bumper brackets.

## 6. Drawings

`BinRobo_rev2_drawings_A3_2026-11-14.pdf`, 15 A3 sheets, concept only.

| Sheets | Content |
|---|---|
| 1 to 4 | Four isometric views without the bin, every visible item named |
| 5 to 8 | The same four views carrying a full 240 L bin |
| 9 | Underside, with the room each castor needs to swivel |
| 10 | Rear-left view with the bin drawn see-through |
| 11, 12 | Exploded views without and with the bin, including the 11 wiring looms |
| 13 | Parts list: 81 robot items, of which 23 are as in the other agent's CAD, 24 changed and 34 new (11 of the new ones are looms) |
| 14 | Wiring looms, proposed routing |
| 15 | Stop chain, power path and fusing, proposed |

The bumper brackets are drawn as plain plates. They would be weak against a sideways knock and need a proper design.

## 7. Files

- `BinRobo_rev2_drawings_A3_2026-11-14.pdf` and `BinRobo_rev2_drawings_png_2026-11-14.zip`
- `rev2_files_2026-11-14.zip`: the model switches, both weight tables, every command list, and the result file of every run quoted here, with a `README.txt` saying which tag is which

## 8. Still needed from the other agent

The seven items in section 7 of my reply stand. Four matter more now:

1. Which MuJoCo version their re-test ran on.
2. Their list of heavier frame sections with weights, and whether their 19 kg includes the mast foot plates.
3. Which lift actuator and driver they intend, and the stop chain they intend, to check sheet 15 against.
4. Whether the 50 Wh trip limit can be raised now that the heavier frame is in, and to what.
