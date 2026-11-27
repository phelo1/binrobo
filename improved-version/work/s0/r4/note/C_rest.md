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

## 4. Safety points that are still open

1. **The empty robot on a steep, slippery pitch.** Only the drive wheels brake and they carry 45 % of the empty weight. On the assumed 12 % pitch, nose first, the empty robot needs grip of about 0.3 just to hold; on wet leaves (0.22) it slides. No earlier test of either design covered this: the gate's emergency stop uses a full bin, and no lane run takes the empty robot down the pitch. It applies to B2-F as well. Ways out: brakes on the castors (stops about ten times shorter on that pitch in simulation), tail-first travel on steep pitches, or measuring the real pitch, which may be much gentler than 12 %.
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
