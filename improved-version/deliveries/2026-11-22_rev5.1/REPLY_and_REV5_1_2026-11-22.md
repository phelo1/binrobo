# BinRobo improved version: revision 5.1

22 November 2026. Follow-up to Brian's answers of the same day. For Brian and for the other agent.

Revision 5.1 is revision 5 with Brian's five answers applied. The hardware is unchanged. The driving software has one new rule and new settings. Sheets 15, 17 and 18 of the drawing set are reissued; the other fifteen are as issued on 21 November.

## Summary for Brian

- **Slope.** You are right. In the elevation data the lane falls about 14 m over its 635 m, and nearly all of that is one hill about 150 m long that starts some 80 m from the house. The hill runs at 6 to 8 %. The 12 % pitch in the earlier simulations was an assumption in the other agent's lane model, not a measurement. I removed it and ran the hill tests again: they all pass.
- **I could not open your link.** The site refused automated access. I used the lane already mapped in the project files (635 m from the house to the public road). If that is not the lane you mean, tell me.
- **Tail-first driving is dropped.** It was only there for the 12 % pitch. One limit remains: on wet leaves the empty robot can stop on a slope of up to 8.5 %, and the data puts the steepest part at 8.2 %. That is too close to rely on. Please measure the hill once with a spirit level (section 6, test 1).
- **Pause for people.** The robot now stops and stands still while the front camera sees a person or an animal within 5 m, and moves on by itself when they have gone. In 18 simulated runs nobody was touched, and nobody who was in view from the start came nearer than 3.2 m.
- **Any time.** The evening drop-off cannot start before 18:00 under the bye-law, so in winter it always runs in the dark. Night was already the tested case. I took off the 22:30 quiet-hours limit I had added; a drop-off started at 23:30 now runs.
- **Cost.** With used parts and the cheaper stop relay: EUR 4,055 to 4,789 all-in (revision 5: 4,223 to 5,204). Three more used-part options could bring it to about EUR 3,660 to 4,540.
- **Speed.** The robot now goes slower down the hill, so that a touch on the soft nose still stops it inside the foam on wet leaves. A pick-up trip takes about 76 minutes instead of 69, a drop-off 67 instead of 64.

**Decisions for you**

1. Is the mapped lane the right one (635 m, house to public road)?
2. Will you measure the hill (test 1)? If any part is steeper than 8.5 % and collects wet leaves, I should put tail-first driving into the mission software after all.
3. The slower hill speeds cost 3 to 6 minutes on a drop-off and 6 to 8 on a pick-up. They only matter on wet leaves. Keep them, or go back to the revision 5 speeds?

## 1. What changed

| Brian's answer | What I did |
|---|---|
| No certified parts; own testing | Kept the used stop relay and the two contactors already on the B2-F parts list in place of the dearer used safety controller of revision 5. All stop devices are wired in series on its two channels (sheet 15). Section 6 lists the tests that replace the certificates. |
| Software pauses the robot when anyone is near | New rule 1 on sheet 18, in the mission software and tested (section 4). |
| The gradient is not that steep | Checked against two elevation models (section 2). Lane model without the 12 % pitch; hill tests re-run; speed rule reset; tail first dropped (section 3). |
| Mostly daylight, but any time | Quiet-hours limit off (a setting). Night detection rates stay the tested default (section 5). |
| Any used part is fine | Re-priced (section 7). |

## 2. The lane's slope

Source: the lane centre line from OpenStreetMap that the other agent mapped, sampled every 5 m, with heights from two free elevation models (`sitl/data/route.json` in the B2-F files). Script: `tables/lane_grade.py`.

| | EU-DEM, 25 m grid | SRTM, 30 m grid, whole metres |
|---|---|---|
| Height at the house / at the road | 43.1 m / 29.4 m | 43 m / 29 m |
| Fall over 635 m | 13.7 m (2.2 % average) | 14 m (2.2 %) |
| The hill, 75 to 225 m from the house | 9.8 m in 150 m: 6.5 % | 9 m in 150 m: 6 % |
| Steepest 50 m | 7.2 % (115 to 165 m) | about 10 % (50 to 100 m) |
| Steepest 25 m | 7.5 % | not usable: a 1 m rounding step is 4 % over 25 m |
| Steepest 10 m | 7.9 % (145 to 155 m) | not usable |
| Length steeper than 6 % / 7 % / 8 % | 125 m / 55 m / 0 m | not usable |

Between 325 and 475 m from the house the lane rises towards the road by up to 2 %. The last 60 m fall to the road at 2 to 3 %.

What this does and does not show:

- Both models agree on the total fall and on where the hill is. The hill averages 6 to 7 %.
- They disagree on the steepest part. EU-DEM says just over 8 %. SRTM is coarser and could be read as 10 % near the top of the hill.
- Neither can see anything shorter than about 25 m. A short ramp of 10 or 12 % would not show.
- The 40 mm step, the trench, the pothole and the leaf zones in the simulated lane are also assumptions of the lane model. I have not changed them.

So the working figure is 8.5 %, with 10 % checked as the case where the data is wrong.

## 3. The hill, tested on the real slope

### 3.1 Stop after a touch on the soft nose

MuJoCo, robot 180 kg, full bin 110 kg; the brakes come on 0.15 s after the touch. The foam has about 150 mm to give; my line is 130 mm. Distances in mm, from the touch to standstill. Table: `tables/pstop_real_slope_r51.txt` (38 runs).

| Slope down | Load | Speed, 5.1 rule | Wet (grip 0.30) | Wet leaves (grip 0.22) |
|---|---|---|---:|---:|
| level | full bin | 0.4 m/s | 106 | 118 |
| level | empty | 0.4 m/s | 127 | 139 |
| 3 % | full bin | 0.4 m/s | 119 | 142 |
| 3 % | empty | 0.3 m/s | 92 | 115 |
| 6 % | full bin | 0.3 m/s | 95 | 118 |
| 6 % | empty | 0.2 m/s | 71 | 98 |
| 8.5 % | full bin | 0.2 m/s | 71 | 93 |
| 8.5 % | empty | 0.15 m/s | 64 | 120 |
| 9 % | empty | 0.15 m/s | | 172 |
| 10 % | full bin | 0.2 m/s | 72 | 139 |
| 10 % | empty | 0.15 m/s | 93 | 1,414 (slides) |

At the revision 5 speeds the same slopes give, on wet leaves: 156 mm (8.5 %, full bin, 0.3 m/s), 177 mm (6 %, empty, 0.3 m/s) and 223 mm (8.5 %, empty, 0.2 m/s). On a wet surface without leaves the revision 5 speeds stay inside 130 mm.

Reading:

- On a wet lane every case is inside the line, up to 10 %.
- On wet leaves every case on the hill is inside the line up to 8.5 %. On the level and on the 3 % slope at 0.4 m/s the stop is 139 to 142 mm: past my line, inside the foam.
- The weak case is the empty robot, nose first, on wet leaves. Only its two drive wheels brake, and without a bin more than half its weight is on the castors. It is fine at 8.5 %, needs 172 mm at 9 % and slides at 10 %.

### 3.2 The speed rule for this lane

| Slope, going down | Full bin on board | Empty, or empty bin |
|---|---|---|
| level or uphill | 0.4 m/s | 0.4 m/s |
| downhill, up to 3 % | 0.4 m/s | 0.3 m/s |
| downhill, 3 to 6 % | 0.3 m/s | 0.2 m/s (was 0.3) |
| downhill, steeper than 6 % | 0.2 m/s (was 0.3) | 0.15 m/s, nose first (was 0.2, tail first) |

Setting: `X_VSLOPE="-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.06:0.2:0.15"`.

### 3.3 Whole-lane physics on the real slope

The lane model with the 12 % overlay switched off (`lane_world_real.py`; its steepest point is 8.4 % at 146 m). Made-good lane, as in revision 5. Table: `tables/lane_real_slope_r51.txt` (26 new runs). The run titles in the result files still say "12 % pitch": that is the name of the test.

| Test | On the assumed 12 % pitch (revision 5) | On the real slope |
|---|---|---|
| Full bin, house to road (P1) | pass, 16.7 Wh | pass, 16.6 Wh |
| Same, heavier bin, less grip, at night (P7) | pass, 25.7 Wh | pass, 25.5 Wh |
| Full bin, stop and hold on the steepest part, going down and going up (P4a, P4b) | holds; 2.4 mm creep in 10 s | holds; 1.6 mm |
| Full bin going down, a person steps in (P6a) | stops 1.60 m short | stops 1.53 m short; 1.66 m at the 5.1 speeds, on all three grips |
| Empty, nose first down the hill, a person steps in, wet (X8n, grip 0.30) | stops 1.50 m short | stops 1.70 m short |
| Same on wet leaves (grip 0.22) | **fail**: ran away to 1.5 m/s, stopped 22 mm from the person | stops 1.68 m short; 1.74 m at the 5.1 speeds |
| Empty, nose first, stop and hold on the steepest part, wet leaves (X9n) | ran away to 2.1 m/s | holds; 0.5 mm creep in 10 s (2.5 mm at the 5.1 speeds) |
| Empty, tail first (X8t, X9t) | pass | pass; no longer needed |

The two failures that made me ask for tail-first driving in revision 5 do not happen on an 8.4 % hill.

### 3.4 Whole missions with the new settings

ArduRover simulation with the mission software, pause rule on, 5.1 speed rule, seed 7. Folder `sitl/r51_final*`.

| Mission | Result | Trip time | Energy per trip | Revision 5 |
|---|---|---|---|---|
| Three drop-offs from 18:00 (s3a) | pass; last dock 21:31; charge left 42 % | 76, 67, 67 min | 71 to 75 Wh | 70, 64, 64 min; 21:18; 43 % |
| One pick-up (s1b) | pass | 76 min | 74.5 Wh | 69 min; 70.9 Wh |
| Three pick-ups from 16:30 (s3b) | pass; all home by 20:16; charge left 41 % | 75, 75, 77 min | 73.5 to 74.5 Wh | 68, 68, 71 min; home by 19:57; 43 % |
| Walker and dog (s5a, 3 seeds) | pass | | | pass |

Least clearance to a hedge in these runs: 0.197 m (0.196 m in revision 5). Placements within 54 mm and 1.5 degrees. Scored by the B2-F script as it stands, the full missions still fail its 50 Wh and 21:00 criteria, as they did in revision 5; with those two restated as in revision 5 they pass (`tables/score_r51_final.md`).

Two things to note. A pick-up trip now uses 74.5 Wh against a pre-trip budget of 75 Wh, so the budget should be set to 80 Wh (`X_TRIP_WH=80`); the battery has room (41 to 42 % left after three trips). And three pick-ups started at 18:00, as the B2-F test script has it, still cannot finish by 21:00: the third is refused, as in revision 5. Started once the lorry has been, they can.

## 4. Pause when anyone is near

**The rule.** When the front camera has found a person or an animal within 5 m in two pictures in a row, the robot stops and stands still. It moves on by itself once nobody has been within 5.5 m for 3 s. After 2 minutes it messages the owner and keeps waiting. After 15 minutes it holds and raises an alert. It runs in the lane, on the yard paths and before every pivot turn. Switch: `X_PPL_PAUSE=1`; distance `X_PPL_PAUSE_R`.

The earlier rules stay underneath it: the lidar stop zone, the protective field and the soft nose.

**Tests.** Mission simulation, scenario s5a (a walker in the lane, then a dog crossing), three seeds each. Camera model as in revision 5: 6 m range, 5 pictures a second, a person found in 60 % of pictures at night and 85 % by day. Table: `tables/person_pause_r51.json`.

| Case | Runs | What the robot did | Nearest approach |
|---|---:|---|---|
| Scenario as written (night rate), revision 5 and 5.1 speeds | 6 | stood still 10 to 14 s for the walker, 9 s for the dog; went on by itself | 3.2 to 4.1 m |
| The walker stops and stands for 60 s | 3 | waited 56 s; went on | 3.3 to 3.5 m |
| The walker stands for 200 s | 3 | waited 197 to 199 s; owner message at 2 minutes; went on | 3.2 to 3.6 m |
| Someone steps out 3.5 m ahead and stands 60 s, night rate | 3 | found at 2.2 to 2.6 m; stopped | 1.16 to 1.26 m |
| Same, day rate | 3 | found at 3.1 to 3.4 m; stopped | 1.39 to 1.57 m |

All 18 runs pass with no contact and no alert other than the 2-minute message.

**Limits.**

- The camera figures are assumed. How well a real detector finds a child, a dog or someone in dark clothes at night is the main unknown, and the main thing to test (section 6, tests 7 and 8).
- Front camera only. The rear camera and rear lidar are still not in the simulation, so the rule does not yet see someone walking up from behind. The robot reverses only at 0.1 m/s and only at the bin and the dock.
- A person who appears closer than the camera can react to is covered by the lidar and then the soft nose. Sheet 18 has the distances.
- The detector must run at 5 pictures a second on two cameras. The board on the B2-F list (Radxa Zero 3W) has a small neural accelerator. A published benchmark lists small detector models at 18 to 20 pictures a second on that chip; a user on the maker's forum got only 2 to 3 with a plain Python pipeline. So it is possible, not certain (test 11). If it falls short, a used mini PC or a Raspberry Pi 5 is the fallback, about EUR 60 to 100 (ASSUMED).
- False pauses are not modelled: a real detector will sometimes see a person in a gatepost. Each one costs about 5 s. If they are frequent the 3 s clear time and the two-in-a-row rule are the things to tune.

## 5. Any time of day

- Under the bye-law as the other agent read it, bins go out no earlier than 18:00 the evening before. From late October to February that is after dark. So night running is the normal case for the drop-off, and the mission tests were already run with the night detection rate.
- The lidar needs no light. The front and rear cameras work by their own infra-red light (on the parts list since revision 5). The headlights, markers and beacon of the B2-F list stay.
- I had added a quiet-hours limit of 22:30 for drop-offs in revision 5. It is now off (`X_QUIET_END=1800`). Test: a drop-off started at 23:30 was refused with the old limit and ran with the new one (67 min, 71.6 Wh, home at 00:37).
- Still in force: drop-offs wait until 18:00, and pick-ups are home by 21:00. Both come from the bye-law. I have not checked the bye-law text myself.
- Frost and high wind still keep the robot home. Those are B2-F rules and I have not touched them.

## 6. Tests on the built robot, in place of certificates

None of these needs special equipment. Do them in this order; do not run unattended until 1 to 8 pass.

| # | Test | How | Pass |
|---:|---|---|---|
| 1 | Hill slope | A 1 m spirit level and a tape at the five steepest-looking places between 80 and 230 m from the house. Hold the level with its uphill end on the ground; the gap under the other end, in cm, is the slope in %. | Nothing over 8 %. Over 8.5 %: tell me. |
| 2 | Stop chain | Press the e-stop, squeeze each switch strip, trip the tilt switch, pull the companion's plug. | Both contactors drop every time. No restart without the reset button. |
| 3 | One contactor stuck | Hold one contactor closed by hand, press the e-stop. Repeat with the other. | Motors dead both times; reset refused. |
| 4 | Soft nose | Push a 70 mm post into the foam with a luggage scale. | Switch acts within the first 20 mm; 150 mm of give at no more than 25 kg. |
| 5 | Stop after a touch | Drive into a padded post at each speed of the rule: level, mid-hill and steepest part; full bin and empty; dry, then hosed wet. Chalk the travel. | 130 mm or less. |
| 6 | Holding | Park on the steepest part, full bin and empty, nose down and nose up, wet. Power off for 10 minutes. | No creep. |
| 7 | Pause rule | Walk towards the robot, stand, and step out at 5 m and at 3 m. By day, at dusk and in the dark; dark clothes; a 1 m dummy; a dog. 20 passes each. | Stopped before 3 m in all 20. Log every miss. |
| 8 | False pauses | Ten trips with nobody about. | No more than one pause in the ten. |
| 9 | Lidar stop | A 0.4 m cardboard box in the path; then a 0.2 m box, which the lidar cannot see. | Stops 1 m short of the tall box. The nose strip stops it at the low one. |
| 10 | Lift | Run to both ends. Put a 10 mm and a 20 mm block under a bin wheel and lower. Lift the bin off by hand while lowering. | Limit switches act before the actuator's own stops. No lowering onto the block. Stops and raises. |
| 11 | Detector speed | Both cameras running; log pictures per second for ten minutes. | 5 or more on each. |
| 12 | Bolts | Check every structural bolt with a torque wrench after ten trips. | None has moved. |

## 7. Cost with used parts

Against the B2-F parts list (new drive, EUR 3,417 parts, EUR 4,112 all-in). Script and table: `tables/cost_r51.py`, `cost_r51.md`. Rows marked "same" are unchanged from revision 5.

| Change | Low, EUR | High, EUR | Since revision 5 |
|---|---:|---:|---|
| Frame: box section from an offcut rack or scrap yard, laser-cut plates, bolts | -70 | +125 | was -14 to +181 |
| Lift actuator, bought used | +86 | +236 | same; now the only option priced |
| Lift rails and carriages, bought used | -45 | -20 | new |
| Lift stop blocks and limit switches | +40 | +80 | same |
| Soft nose with switch strips | +20 | +160 | same |
| Second lidar, front camera with infra-red light, under-bin sensors, ground-speed source | +102 | +142 | same |
| Stop relay and contactors: keep those of the B2-F list | 0 | 0 | was +39 to +269 |
| Castor beam pivot parts, pad springs | +20 | +40 | same |
| B2-F lines not needed; simpler 4G board and harness | -201 | -201 | same |
| **Sum** | **-48** | **+562** | was +92 to +907 |

| | Parts, EUR | All-in, EUR |
|---|---|---|
| B2-F parts list | 3,417 | 4,112 |
| Revision 5 | 3,509 to 4,324 | 4,223 to 5,204 |
| **Revision 5.1** | **3,369 to 3,979** | **4,055 to 4,789** |
| With the three options below | 3,039 to 3,769 | 3,657 to 4,536 |

Options not counted, because each needs a part to be found first (all ASSUMED): a used gearmotor pair from a mobility-scooter breaker (-150 to -200; the gear ratio and shaft must suit the chain stage), a used motor controller (-40 to -70), a used companion computer, lidar or cameras (-20 to -60). I would not buy used battery cells: the new ones are only EUR 140 and their capacity is known.

Every figure not taken from the B2-F list is an estimate. The spread is wide because nothing has been quoted.

## 8. Still open

1. **The real slope**, until test 1 is done. Everything in section 3 stands on 25 to 30 m elevation data.
2. **Wet leaves on the hill.** The empty robot's margin there is thin at 8.5 % and gone at 9 %.
3. **The person detector.** Assumed rates, front camera only, false pauses not modelled, speed on the chosen board unproven.
4. **Carried over from revision 5, unchanged:** the lidar stop logic's blind band near hedges; rear sensors not simulated; the step, pothole and trench stall the robot if the lane is left as it is assumed to be; frame rail safety factor 1.99 at the M10 holes; soft nose untested; prices assumed; firmware turn-rate overshoot.
5. **Not re-run:** the 60-mission score, the fault injections and the bend tests of revision 5. The 5.1 changes only slow the robot on the hill and add a stop, so I re-ran one evening of drop-offs, one day of pick-ups, single trips and the people scenario instead (26 mission runs in all).

## 9. For the other agent: facts I need

1. Is the lane in `route.json` (OSM ways 0, 0, 0) the lane Brian means? He sent a map link I could not open.
2. Does anything Brian said or measured lie behind the 12 % pitch, the 40 mm step, the trench, the pothole or the leaf zones in `lane_world.py`? The file says all are assumed.
3. Do the contactors of line KM-L8 have auxiliary contacts? The reset feedback on sheet 15 needs one on each.
4. Has a person detector been timed on the Radxa Zero 3W with two cameras?
5. The source of the 18:00 and 21:00 bye-law times.

## 10. Files

| File | What it is |
|---|---|
| `REPLY_and_REV5_1_2026-11-22.md` | this note |
| `BinRobo_improved_rev5_1_drawings_2026-11-22.pdf` | 18 sheets; 15, 17 and 18 are new |
| `BinRobo_improved_rev5_1_drawings_png.zip` | the same as PNG |
| `BinRobo_rev5_1_tests_2026-11-22.zip` | scripts, settings, results and tables of this note |

In the test zip: `software/b2f_companion_x.py` (pause rule, clock setting; everything else as revision 5), `software/lanerun_x.py` and `make_lane_world_real.py` (lane without the 12 % overlay), `chains/` (the command lists as run), `tables/`, `stop_tests/`, `lane/`, `sitl/`, `drawing_scripts/`.

## Sources

- Lane line and heights: `sitl/data/route.json`, `build_route.py` in the B2-F files (OpenStreetMap ways; EU-DEM 25 m and SRTM 30 m through OpenTopoData).
- B2-F parts list: `b2f_bom_lines.json` (new-drive variant).
- [Qengineering, YoloV5 NPU: benchmark table for RK3566/68/88](https://github.com/Qengineering/YoloV5-NPU)
- [Radxa forum: Optimizing Object Detection on Radxa Zero 3 (RK3566), performance issues](https://forum.radxa.com/t/optimizing-object-detection-on-radxa-zero-3-rk3566-performance-issues/25700)
- Revision 5 note and test pack of 21 November 2026.
