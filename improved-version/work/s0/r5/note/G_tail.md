## 5. What is still open

1. **Nothing in the people protection is certified.** Lidar, camera, protective field and soft nose are ordinary parts and ordinary software. The detection rates behind the table in 1.1 are assumed.
2. **Tail first is not in the mission software.** It is tested in the lane simulation only. Until it is, the empty robot should stay off anything steeper than 8 %.
3. **Wet leaves on a steep pitch.** At grip 0.22 a touch on the nose is not a safe stop on 12 % even at 0.2 m/s with a full bin (288 mm). Grip is not measured before a descent; a brake check on the first metre of a pitch is the obvious next step and is not written.
4. **The real lane is not measured.** The 12 % pitch is B2-F's assumption; the map data it used shows 7.9 % at most. The highest edge is not measured either.
5. **The lane as it is today stops the robot** at the step, the pothole and the trench (3.6).
6. **The driving-software faults of 3.7 were found by luck**, on the third trip of one mission. I have tested the fixes by injecting faults, but I could not reproduce the original event on demand. More seeds and more three-bin evenings would be the honest next test.
7. **The lidar stop logic has a blind band.** With a poor satellite fix it ignores anything within 1.2 m of a hedge, and it never stops for anyone more than 0.20 m to the side of the robot (3.7). The camera person check covers this in the model; how well a real detector does it at night is unknown, and the lidar logic itself is not cured.
8. **The rear lidar and rear camera are drawn and costed, not simulated.**
9. **Side rail at the M10 holes:** factor 1.99 on the kerb case at 0.8 m/s (3.5). Bolting the rail with M8 and keeping M10 for the cross-member would bring it back to about 2.05 and still pass the slip check on the rail pair (6.8 kN demand against 7.5 kN, bare faces); I have not redrawn it.
10. **Soft nose:** home-made. Its 150 mm of give, and whether a ribbon switch survives hedges and brambles, need a bench test.
11. **Prices:** mostly assumed; nothing quoted. The used actuator is the largest single uncertainty.
12. **Sensor models in the mission runs** remain idealised as listed at the end of 3.7. The firmware's turn-rate loop overshoots what it is asked for and needs tuning on the real robot.

## 6. Decisions for you, Brian

1. **Accept people protection that is not certified?** Revision 5 does what you asked: lidar and camera together, about the price of B2-F. The cost is that no part of it carries a safety rating. If the robot will only ever run on your own lane, mostly at night, I think that is a reasonable trade. If a child or a visitor is likely to meet it unattended, I would put the certified bumper back (about EUR 650 to 1,500 more).
2. **Measure two things on the lane** before anything is built: the steepest slope over any 2 m, and the highest edge across the lane. They decide whether tail first matters at all (not if nothing is over 8 %) and what has to be ramped.
3. **Used or new lift actuator?** Used saves about EUR 800 all-in if a sound one can be found.
4. **Quiet-hours limit.** I assumed drop-offs may run until 22:30. Three bins from 18:00 finish at about «DROP_END».
5. **When does the collection crew pass?** Pick-ups should start as soon as the bins are emptied; three take about «THREE_H», so they must start by 17:30 to be done by 21:00.
6. **Closer to the hedge?** 0.42 m is the safe figure. Trimming the hedge at 417 m would allow 0.35 m.

## 7. Facts I need from the B2-F author

I do my own testing; these are the inputs I cannot get any other way.

1. The make, type and tyre hardness of the drive wheel in the parts list, and of the 200 mm castor.
2. Whether the 12 % pitch (G12, 138 to 152 m) rests on anything measured, and the source of the wet-leaf grip figure 0.35.
3. Whether the lidar in your design is meant to sit on the post, as in your CAD, or at 0.30 m on the nose, as your mission world assumes. I have drawn it on the nose.
4. In the companion: is the right-hedge guard in `lane()` (the line "never closer than 0.35 m to the right face either") meant to limit a move to the left? As written it pushes the robot further right when the right face is near. I replaced it (3.7).
5. The stop command `att(self.yaw, 0.0)` re-sent each cycle: is the slow rotation it allows known? It showed on a 40 s wait.
6. Does the tree-cover satellite model (RtkMultipath) have a documented basis for the size of its Float errors? In the event of 3.7 the position estimate was 1.1 m out after 30 s of Float, and in my 40 passes of the bend it was more than 0.5 m out in 30.
7. In `obstacle_ahead()` the map filter widens from 0.40 m to 1.2 m when the fix is degraded. What false alarms was that set against? It hides a person standing near a hedge (3.7), and under the tree-cover model the fix is degraded much of the time.
8. Scenario s5a: at what robot speed was it designed? At 0.4 m/s the person and the dog are gone before the robot is within 1.5 m, so it no longer tests a stop.

## 8. Files

| File | What it is |
|---|---|
| `REPLY_and_REV5_2026-11-21.md` | this note |
| `BinRobo_improved_rev5_drawings_2026-11-21.pdf` | 18 sheets, A3, all redrawn. 1 to 10: views with and without the bin. 11, 12: exploded views. 13: parts list. 14: wiring looms. 15: safety functions, stop chain, power and fusing. 16: main dimensions. 17: bolted joints, lift stops, speed rule, lowering. **18 (new): people avoidance and keeping left.** |
| `BinRobo_improved_rev5_drawings_png.zip` | the same sheets as images |
| `BinRobo_rev5_tests_2026-11-21.zip` | every script, switch, command list and result file behind this note, with a README. Includes the whole first pass of the driving software and the faulty test versions. |

## Sources

- Review package of 21 November 2026 (three reports and the zip) from the B2-F author's side, as relayed by Brian. Read, not run.
- Used lift actuator, listing ended, USD 293.82: https://ebay.com/itm/204527003587
- New LA36 6,800 N listing, USD 799.99: https://ebay.com/itm/225614402810
- Used LINAK actuators, range of listings: https://www.ebay.com/b/linak-actuator/bn_7024728114
- The review's price for a new LA36 (EUR 939.91 including VAT): https://www.techniektotaal.com/en/actuator-la36-24v-6800n-stroke-200mm-eos-linak.html
- The review's weight for the LA36: https://www.eboatwatch.com/products/la36
- LINAK LA36 data sheet, Schmersal safety-bumper data and NIST IR 8029, as listed in the revision 4 note.
