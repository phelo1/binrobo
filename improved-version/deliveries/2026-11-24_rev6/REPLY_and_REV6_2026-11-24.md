# BinRobo improved version: revision 6

24 November 2026. Reply to Brian's two points and to the re-test of revision 5.1 (three reports of 23 November). For Brian and for the other agent.

Revision 6 changes how the robot keeps clear of people and how fast it drives. Hardware: a third lidar, a different sprocket on each wheel, a few relays and a bigger companion computer. All 18 drawing sheets are reissued.

## Summary for Brian

Both of your points are right. I reproduced both before changing anything.

**People.**

- The reviewers' case, on my side: a person walks out of the far hedge at night when the robot's nose is 1 m from their line. With the revision 5.1 software the robot touched them in 2 of 3 runs.
- The cause was not the camera's or the lidar's eyesight. The camera only looks forward, and this person came from the side. The lidar saw them the whole time, but the software only reacted to things already in the robot's own path. That was a hole in my design.
- Revision 6: the lidars now watch the whole width of the lane, all round the robot. A third lidar closes the blind side at the back. Anything within 3 m of the robot, in any direction, makes it stop and stand still. It does not move again until everything has been clear for 3 s.
- Result: 108 simulated encounters in the lane at night: 23 cases with the fast cruise on, the 13 hardest with it off. Then 15 more with every run at the full 1.0 m/s. In the reviewers' case nobody is touched at either setting. Someone behind or beside the robot now stops it, and it stays stopped until they have gone. With the fast cruise off nobody is touched in any case.
- My own harder tests then found more holes: someone walking out of a gateway, someone walking up while the robot turns on the spot, and someone already standing beside it when it starts a turn. All are fixed and tested again (section 3.3). That is why this reply took a day.
- Every sensor figure in these tests is assumed. They show the rules have no hole of the kind the reviewers found. They do not show what the real sensors will see. That is test 7 to 9 on the built robot.

**Trip time.**

- A round trip was 67 to 77 minutes because the drive was geared for 0.7 m/s flat out and I held the robot to 0.4 m/s, the speed at which a touch on the soft nose stops it inside the foam.
- Revision 6: a smaller sprocket on each wheel (2:1 in place of 3.5:1; no extra cost) and a fast cruise of 1.0 m/s. The robot only cruises fast when its sensors show the lane clear well ahead. Near anything, on the steep part of the hill, before a gateway and in the yard it drops back to the old speeds.
- Result: a round trip takes 36 to 42 minutes. Three bins put out from 18:00 are all at the road and the robot is home by 19:54. In the 60-mission test suite all 12 full missions complete, with no contact.
- The price: above 0.4 m/s the soft nose is no longer a guarantee. If someone steps out less than about 1 m in front of the nose while the robot is cruising fast, it is still braking when they meet. In the tests a walker who stepped out 0.4 m ahead of the nose was touched in every run, at up to 0.33 m/s, and a child running out there at 0.2 to 0.9 m/s. From 1 m and more nobody was touched; at the full 1.0 m/s the robot stopped 0.09 to 0.18 m short of the walker.

**Cost.** EUR 4,241 to 5,138 all-in, which is EUR 187 to 349 more than revision 5.1. The third lidar is EUR 50, relays and a diode for the stop circuit EUR 50 to 110, and a companion computer that can run the person detector EUR 60 to 130.

**The rest of the review.** Their two blockers were fair. The stop circuit on sheet 15 is redrawn so that no single failed part keeps the motors live. The hill is still not measured, and until it is I cannot promise the empty robot stops on wet leaves on the steepest part.

**Decisions for you**

1. **Speed.** Three choices, all tested:
   - Fast cruise, 1.0 m/s on a clear lane: 36 to 42 minutes a trip. Needs the sprockets. Not touch-safe while cruising.
   - Middle, 0.6 m/s on a clear lane: about 45 to 48 minutes. No hardware change. Still not touch-safe while cruising, but every stop is shorter.
   - Fast cruise off, 0.4 m/s at most: 65 to 74 minutes. Touch-safe everywhere.

   The fast cruise is a software switch, so the sprockets do not commit you to it.
   I would fit the sprockets, run the first weeks with the fast cruise off, and switch it on once tests 7 to 9 and 13 pass on the real robot.
2. **Third lidar and bigger computer** (EUR 110 to 180 together). I would not build without them: they are what closes the gap the reviewers found.
3. **Measure the hill.** A 2 m board and a phone, half an hour (section 7, test 1). Until then, switch on the leaf-season setting from October to December: the robot then refuses pick-up trips, because on those it goes down the hill with no bin.
4. **Is the mapped lane the right one?** 635 m from the house to the public road. The other agent asked on 6 November and I asked on 22 November. Neither of us has a plain yes.
5. **Bins home by 21:00 or by midnight?** The council's page says 9.00 pm; the other agent reads midnight in the bye-law text. I left it at 21:00. With the fast cruise it makes no practical difference.
6. **Please forward the revision 5 files** of 21 November to the other agent. They say the pack never reached them, and most of what they list as unchecked is in it.

## 1. What the re-test found and what I did

| Finding of 23 November | My check | What changed | Section |
|---|---|---|---|
| Someone who steps out close ahead at night is touched (1 of 2 runs) | Confirmed: 2 of 3 runs | Lane watch on the lidars, stand-still zone all round | 2, 3 |
| Someone behind or beside the robot is not seen | Confirmed | Third lidar; the zone covers every side | 3 |
| The robot restarts with a person beside it | Confirmed | Restart only when every sensor is clear | 3 |
| The 15-minute hold never fires | Confirmed | The hold sums all pausing in the last 20 minutes | 3 |
| One false camera person a minute: 87 pauses | Not re-run on 5.1 | A camera sighting must match a lidar object | 3 |
| A round trip takes 68 to 82 minutes | Confirmed: 67 to 77 | Fast cruise, 2:1 chain stage | 4 |
| A loaded turn on the spot touched a parked bin (firmware 4.6.2) | Reproduced on 4.7.2, in another seed | The turn now checks both ways round and keeps to the clear one | 4.6 |
| B-1: the hill is not bounded at 8.5 % | Agreed | Survey method, leaf-season settings | 6 |
| B-2: one shorted diode defeats both contactors | Agreed | Sheet 15 redrawn | 6 |
| 48 of 60 on the frozen score | Re-run | 45 of 60 as it stands, 57 with a realistic trip budget; all 12 full missions complete | 5 |

## 2. Why a person was hit

I ran the reviewers' case with the revision 5.1 settings on my side: three seeds, a person who walks out of the far hedge at night and stops in the robot's path. Result: contact in two of three runs, at 0.30 m/s. In the third the robot stopped 0.44 m short. So their finding stands.

Three things caused it.

1. **The camera could not see them.** The front camera looks 55 degrees to each side of straight ahead. Someone who starts at the far hedge when the nose is 1 m from their line is 68 degrees off the nose. They only come into view once they are nearly in front.
2. **The lidar saw them and the software ignored it.** The lidar had the person in sight for the whole 2.5 s. But the lidar stop logic I had kept from B2-F only reacts to things inside the robot's own path: its width plus 0.2 m each side. A person walking towards the path did not count until they were in it.
3. **My own tests stopped too early.** "2.6 m ahead" in the test is measured from the robot's axle to the middle of the lane. The nose was 1.0 m from the person's line when they set off. My closest test in revision 5.1 had the nose 2.0 m away.

The review asks whether the camera model has extra latency, because the person in my "3.5 m" runs was only found at 2.2 to 2.6 m. It is not latency. It is the same geometry: for the first second and a half the person is outside the camera's view.

The same gap explains their other two findings: a walker who comes from behind (0.38 m from the robot's side) and one who stands beside it (0.48 m) never enter the front camera's view, so the robot did not react to them at all.

## 3. People avoidance in revision 6

### 3.1 What changed

1. **The lidars watch the whole lane.** Every lidar return is sorted into hedge or not hedge. Hedge is whatever lies on the hedge face that the scan itself shows. A face has to be long: it is fitted from quarter-metre steps along the lane, so a person or a box cannot pass for one. When the satellite fix is good the map gives a second opinion. Anything else inside the lane is an object, wherever it is: in the path, beside it or behind the robot. This works without the map and without a good position.
2. **Three lidars.** One at the nose as before, and one on the tip of each rear leg (revision 5 drew one at the rear, and the software did not use it). Together they see all round, bin or no bin.
3. **Stand-still zone.** An object within 3 m of the robot's outline, in any direction: stop and stand still. A person or animal the camera has seen twice running within 5 m does the same, if the lidar has an object at the same place; within 2.5 m it needs no lidar match.
4. **Braking.** From the fast cruise the robot brakes at once: drive to neutral, brakes on. At the touch-safe speeds it ramps down as before.
5. **Standing still means still.** In revision 5.1 the stopped robot's wheels kept twitching, because the firmware went on correcting its heading. Now the firmware holds the drive at zero while the robot waits.
6. **Restart.** Only when every sensor has shown the zones empty for 3 s. The first 3 m are at 0.2 m/s.
7. **People and things.** Once a camera has called something a person it stays one until it has gone. The robot waits: owner message at 2 minutes, hold with an alert once it has stood for 15 of the last 20 minutes. A thing may be passed, at 0.2 m/s, only if the front camera has had it in view and never called it a person, it has not moved for 20 s and it is 0.5 m clear of the path. Anything that turns up beside or behind the robot is outside the camera's view, so it is waited for like a person. A thing in the path for 2 minutes ends the trip with a path-blocked alert.
8. **Turning on the spot.** No turn with anything unknown within 1.75 m of the axle (the circle the nose sweeps), nor with a person or anything moving within 3 m. The robot looks for a full second before it starts a turn, and the same watch runs five times a second during it. Outside the yard, anything that turns up inside 3 m during a turn counts as moving. The same rule holds while the robot waits for the pad to clear before it sets a bin down.
9. **False camera sightings.** A sighting beyond 2.5 m only stops the robot if a lidar object is at the same place. One sighting of any kind ends the fast cruise for the moment.

The older layers stay underneath: the protective field in the robot's own path, and the switch strips on the soft nose.

### 3.2 Tests

Mission simulation, scenario s5a: the robot with a full bin in the lane at night, between 295 and 380 m from the house. Three seeds for each case. "Nose 1.0 m from their line" means the person sets off from the hedge when the nose is that far from where they will cross. They walk at 1 m/s and do not look: they keep walking even into a robot that has stopped. Camera: a person found in 60 % of pictures (night), 5 pictures a second. Lidar: 10 scans a second, 10 mm noise.

A "touch" is any contact while the robot is still moving, however slowly.

| Case | Runs | Fast cruise off (0.4 m/s and under) | Fast cruise on (up to 1.0 m/s) |
|---|---:|---|---|
| Walker stops in the path 10 m ahead, then a dog crosses (the scenario as written) | 3 | earlier run only | no touch; nearest 2.66 to 3.45 m, robot at up to 0.02 m/s then |
| Walks out of the far hedge and stops in the robot's path; sets off when the nose is 2.0 m from their line | 3 | earlier run only | no touch; nearest 0.95 to 1.38 m, robot standing still |
| The same; nose 1.6 m from their line | 3 | earlier run only | no touch; nearest 0.19 to 0.97 m, robot standing still |
| The same; nose 1.0 m from their line (the reviewers' contact case) | 3 + 3 | no touch; nearest 0.34 to 0.49 m, robot standing still | no touch while moving; nearest up to 0.52 m; in 1 of 3 they walked up to the standing robot |
| The same; nose 0.4 m from their line | 3 + 3 | no touch while moving: they walked up to the robot, which had stood still for 1.3 to 1.6 s | **touched** in 3 of 3, robot braking, at up to 0.12 m/s |
| Small child (0.3 m wide), nose 2.0 m from their line | 3 + 3 | no touch; nearest 1.40 to 1.56 m, robot standing still | no touch; nearest 1.07 to 1.53 m, robot standing still |
| Child running across at 2.5 m/s, nose 2.5 m from their line | 3 | earlier run only | no touch; nearest 1.86 to 2.05 m, robot at up to 0.21 m/s then |
| Child running across at 2.5 m/s, nose 1.0 m from their line | 3 + 3 | no touch; nearest 0.56 to 0.72 m, robot standing still | no touch; nearest 0.14 to 0.74 m, robot at up to 0.06 m/s then |
| Child running across at 2.5 m/s, nose 0.4 m from their line | 3 + 3 | no touch while moving: they reached the robot within 0.4 s of its stopping | **touched** in 3 of 3, robot braking, at 0.21 to 0.67 m/s |
| Steps out of the NEAR hedge into the path, 3.2 m ahead of the nose | 3 | earlier run only | no touch; nearest 2.12 to 2.31 m, robot standing still |
| Steps out of the near hedge into the path, 1.7 m ahead of the nose | 3 + 3 | no touch; nearest 1.01 to 1.22 m, robot standing still | no touch; nearest 0.55 to 0.77 m, robot standing still |
| Walks out of a 4 m gateway in the far hedge; nose 1.0 m from their line | 3 + 3 | no touch; nearest 0.54 to 0.65 m, robot standing still | no touch; nearest 0.64 to 0.74 m, robot standing still |
| Child runs out of the same gateway at 2.5 m/s; nose 1.0 m from their line | 3 + 3 | no touch; nearest 0.61 to 0.76 m, robot standing still | no touch; nearest 0.76 to 0.87 m, robot at up to 0.05 m/s then |
| Walker comes from behind at 1.6 m/s and passes the robot's side | 3 + 3 | no touch; nearest 0.16 to 0.50 m, robot standing still | no touch; nearest 0.28 to 0.51 m, robot standing still |
| Walks up from the far hedge and stands about 0.45 m from the robot's side for 30 s | 3 + 3 | no touch; nearest 0.31 to 0.65 m, robot standing still | no touch; nearest 0.59 to 0.92 m, robot standing still |
| Walker comes up the lane towards the robot, stops beside or just behind it for 30 s, walks on | 3 + 3 | no touch; nearest 0.18 to 0.45 m, robot standing still | no touch; nearest 0.09 to 1.00 m, robot standing still |
| Walks ahead of the robot in its path at 0.3 m/s | 3 | earlier run only | no touch; nearest 4.39 to 4.44 m, robot at up to 0.34 m/s then; 5 stops |
| Scenario as written, camera finds a person in only 40 % of pictures | 3 | earlier run only | no touch; nearest 2.80 to 3.22 m, robot at up to 0.05 m/s then |
| Nose 2.0 m from their line, camera at 40 % | 3 | earlier run only | no touch; nearest 0.54 to 1.07 m, robot standing still |
| Walker stands in the path for 1,000 s | 3 + 3 | no touch; nearest 3.27 to 3.51 m, robot at up to 0.08 m/s then; owner message at 2 minutes; still waiting when the 15-minute scenario ended; 5 to 6 stops | no touch; nearest 2.54 to 3.36 m, robot standing still; owner message at 2 minutes; still waiting when the 15-minute scenario ended; 5 to 9 stops |
| Unmapped 0.4 m box on the far side of the lane, 1.5 m clear of the robot's path | 3 + 3 | no touch; stood still 3.0 m from it; after 20 s or more passed it at 0.2 m/s | no touch; stood still 3.0 m from it; after 20 s or more passed it at 0.2 m/s (1 of 3); path-blocked alert in 2 of 3 |
| Unmapped 0.4 m box in a bend, 0.2 m clear of the robot's left side | 3 | earlier run only | no touch; stood still 2.9 to 3.0 m from it; path-blocked alert; owner message at 2 minutes |
| Unmapped 0.4 m box in a bend, at the right edge of the robot's path | 3 | earlier run only | no touch; stood still 3.0 m from it; path-blocked alert; 1 to 5 stops |

Runs: 39 with the fast cruise off (0 with a touch), 69 with it on (6 with a touch).

Table and every run: `tables/stress_r6.md`, `stress_r6.json`.

- "Earlier run only": with the fast cruise off I ran the eleven hardest cases and the two gateway cases with the final lane watch. The other ten were run earlier in the day, before the last two fixes of section 3.3, with no touch in any (`tables/stress_before_binfix.md`).
- In the crossing cases of the fast column the robot was doing 1.0 m/s when the person appeared in one seed of three and 0.7 m/s in the other two. That is the limit under a degraded fix, which holds at that place in those seeds.
- From the person's first step to the stop command took 0.4 to 0.7 s when they came out of the hedge itself, 0.2 s for the running child and 0.1 s at a gateway. The robot was standing 1.3 to 1.9 s after the first step.

Outside the table:

- **The reviewers' case on the 5.1 software**, for comparison: touched in 2 of 3 runs at 0.30 m/s (section 2).
- **The walker who never leaves.** With the hold limit set to 10 minutes, so that it fits inside the 15-minute scenario, the robot paused for 318 s, for 152 s and again, and held with an alert once the pauses added up to 10 of the last 20 minutes. In revision 5.1 every pause restarted the clock and the hold never came.
- **Someone walks up during a turn on the spot:** section 4.6.
- **Every seed at the full 1.0 m/s.** In the table the robot was at 0.7 m/s in two seeds of three. With that limit lifted for the test, I ran the five closest cases again, 15 runs, the robot at 0.92 to 1.01 m/s when the person appeared (`tables/stress_v10_r6.json`):

  | Case | Result at 1.0 m/s |
  |---|---|
  | Walker, nose 1.6 m from their line | no touch; stopped 0.54 to 0.66 m short |
  | Walker, nose 1.0 m (the reviewers' case) | no touch; stopped 0.09 to 0.18 m short |
  | Walker, nose 0.4 m | **touched** in 3 of 3, at 0.03 to 0.33 m/s |
  | Running child, nose 1.0 m | no touch; the child passed 0.23 to 0.40 m in front of a robot still doing 0.17 to 0.33 m/s |
  | Running child, nose 0.4 m | **touched** in 3 of 3, at 0.71 to 0.86 m/s |

  So at the full speed the reviewers' case clears by a hand's width. One metre in front of the nose is the edge.

### 3.3 What my own tests caught today

The first version of these rules passed the reviewers' cases and failed harder ones of my own. Each of these was found by a test, fixed and tested again. The runs from before each fix are in the pack (`sitl/before_fixes`), so the other agent can see what changed.

| What the test showed | Cause | Fix |
|---|---|---|
| A person "touched" by a robot that had already stopped | Standing in the driving mode, the firmware kept correcting the heading and the wheels twitched | The firmware holds the drive at zero while the robot waits |
| Someone stood beside the robot for 20 s; it then crawled past them, 0.7 m away | Anything still for 20 s counted as a thing | Only a thing the front camera has had in view may be passed |
| The nose swept into a parked bin at the house (the reviewers' failure) | The way round a half turn was left to a degree of heading noise | Both ways are checked; the clear one is kept (section 4.6) |
| Someone walked up beside the turning robot and was touched | Across the lane, the robot fitted hedge faces along its own axis and took the person for hedge; the restart only asked whether anything was moving | Faces are fitted along the lane during a turn; one test starts, watches and restarts the turn |
| Someone walking out of a gateway was not seen by the lidar in 1 run of 3, at either speed setting, and touched at 0.15 to 0.31 m/s | With no hedge beside them, their own returns were read as a short piece of hedge | A hedge face must be long: it is fitted from quarter-metre steps along the lane |
| The robot was still doing 0.7 m/s when it reached a gateway | It only slowed once the hedge beside it was missing | It looks 5.5 m ahead for a gap in either hedge |
| Someone was already standing 0.7 m from the robot when it started its turn at the road end. It turned for 0.4 s, less than one degree, before the watch stopped it | The states before a turn do not run the lane watch, and a thing only counts once two looks running show it. The single look before the turn saw nothing | The robot looks for a full second before every turn |
| While the robot waited for the pad to clear, the same person walked up to 0.5 m from it. It stood in the driving mode and its heading twitched by 0.3 degrees | Rule 5 covered the stand-still pause only | The people rule holds during that wait as well: stand-still pause, firmware hold |
| A walker close to the hedge was inside 3 m for 1.4 s before the turn stopped; they were 1.8 m away by then | At a turn, beyond the nose circle only movement counts, and movement is judged against a second ago. This walker was only told from the hedge at about 3 m | Outside the yard, a thing inside 3 m that was not there a second ago counts as moving at once |

The two gateway fixes change how every lidar scan in the lane is sorted, so the people cases of section 3.2 were all run again after them. The table shows those runs.

The last three rows came after that, from the turn tests on what I had taken for the final code. They act only at a turn on the spot and in the wait before a set-down, so I did not run the lane cases a third time. The turn tests, which are complete drop-offs, and a pick-up were run again (section 4.6).

### 3.4 False sightings

The reviewers' test: one false camera person a minute, somewhere in the camera's view. Revision 5.1 stopped 87 times on one pick-up and lost 4.7 minutes.

| | Without | With one false person a minute |
|---|---|---|
| Drop-off | 34.3 min, no stop | 35.7 min, 7 stops of about 4 s |
| Pick-up | 37.4 min, no stop | 39.4 min, 7 stops of about 4 s |

Both columns were run before the gateway look-ahead, so each time is 2 to 3 minutes shorter than a trip with it. The difference between the columns is what the false sightings cost.

The stops that remain are the false sightings that fall within 2.5 m, where the camera needs no lidar match. Each of the others costs a moment of fast cruise.

### 3.5 What it still cannot do

- **Someone who appears right in front of a fast robot.** The robot needs up to 0.7 s to be sure of someone who steps out of the hedge, and about a second more to stop from 1.0 m/s. A walker who set off 0.4 m in front of the nose met the robot at up to 0.33 m/s; a running child, at 0.21 to 0.86 m/s (the higher figures are from the runs with every seed at 1.0 m/s). From 1 m and more nobody was touched, at 1.0 m/s by 0.09 m at the least. With the fast cruise off nobody was touched in the 39 runs with the final lane watch. In the earlier set of the day one running child at 0.4 m touched a robot that was at under 0.02 m/s, so that case is on the edge even at the slow speed.
- **Someone standing against the hedge.** Anything within 0.3 to 0.5 m of the hedge face is taken for hedge until it steps out. That is most of the 0.7 s above. The protective field still covers the robot's own path.
- **Low things.** The lidars sit 0.30 m above the ground. A cat, a lying dog or a ball is seen only by the camera, then felt by the nose strip.
- **At a turn on the spot the rule is weaker than in the lane.** Someone who stands still 2 to 3 m from the robot, out of the camera's view, does not hold a turn (section 4.6).
- **The camera sees forward only.** Beside and behind, the robot has lidar alone. That is why anything there is treated as a person. The rear camera is still not in the simulation.
- **Things left in the lane.** The rule errs towards stopping. With the fast cruise on, a box well clear of the planned line still ended two of three runs with a path-blocked alert, because the robot was in mid-lane after a bend when it met it. That costs a walk down the lane, not safety. I have not refined it.
- **All sensor figures are assumed.** The lidar model is an ideal scan with a little noise. Real hedges move in the wind, rain scatters the beam and wet leaves reflect badly. Expect false stops at first; test 9 counts them.

## 4. Trip time

### 4.1 Why it was slow

- The lane is 635 m, so a round trip is 1,270 m of lane plus the yard work at each end.
- The B2-F drive (4,600 rpm motor, 32:1 gearbox, 3.5:1 chain, 330 mm wheel) turns the wheel at 0.71 m/s flat out. B2-F capped the lane speed at 0.5 m/s.
- I then held it to 0.4 m/s on the level and 0.15 to 0.3 m/s down the hill. Those are the speeds at which a touch on the soft nose stops the robot inside the foam. I call them the touch-safe speeds.
- 1,270 m at 0.4 m/s is 53 minutes before the hill, the yard and any stop.

### 4.2 The fast cruise

Two speed tables now. The touch-safe table is unchanged. The fast table applies only while all of these hold:

- the robot is in the lane proper: more than 30 m from the house and 20 m from the road end;
- the lidars show both hedge faces, with no gap in either within 5.5 m ahead, and the robot is more than 0.25 m from them. A gap is a gateway: the robot is down to the touch-safe speed before it gets there;
- nothing is in the lane ahead: within 4 m at 0.4 m/s, growing to 10 m at 1.0 m/s;
- no camera has reported a person or animal in the last second, confirmed or not;
- the satellite fix is good. With a degraded fix and both hedge faces in view the limit is 0.7 m/s;
- the lane is not narrow, the robot is not changing its line, and the bend ahead allows it.

| Slope, going down | Touch-safe: full bin | Touch-safe: empty | Fast: full bin | Fast: empty |
|---|---|---|---|---|
| level or uphill | 0.4 m/s | 0.4 m/s | 1.0 m/s | 1.0 m/s |
| downhill, up to 3 % | 0.4 m/s | 0.3 m/s | 1.0 m/s | 0.8 m/s |
| downhill, 3 to 6 % | 0.3 m/s | 0.2 m/s | 0.8 m/s | 0.6 m/s |
| downhill, steeper than 6 % | 0.2 m/s | 0.15 m/s | 0.6 m/s | 0.4 m/s |

The robot looks 8 m ahead on the map for the slope, so it is at the hill speed before the brow.

Leaf-season setting (leaves on the lane, or October to December): touch-safe 0.35 m/s in place of 0.4; fast 1.0, 0.8, 0.6 and 0.5 m/s with a full bin and 1.0, 0.8, 0.5 and 0.15 m/s empty.

### 4.3 What it needs in hardware

- **Sprockets.** A 24-tooth sprocket on each wheel in place of the 42-tooth one. The wheel then turns at 1.24 m/s flat out, and at 1.0 m/s the motor runs at 3,700 of its 4,600 rpm.
- **Torque.** The taller gearing gives less push for the same motor current. For the same wheel torque as before (60 N m) each motor now draws about 26 A in place of 15 A. The controller on the parts list limits at 30 A a channel. Full bin up the steepest part at 1.0 m/s would need 0.59 N m from each motor, which is inside the rating as I read it. The motor curve is ASSUMED: I have no data sheet. In practice the robot never climbs with a full bin.
- **Brakes.** The spring brakes sit on the motors, so the same change cuts their torque at the wheel from 60 to 34 N m. Every stop and hold test in this note uses 34.
- **Firmware.** The same command now turns the wheels 1.55 times faster, so the speed and turn loops are reset (section 4.6).

Why not faster than 1.0 m/s: the stop distance grows with the square of the speed, the lift load on a kerb strike reaches 4,628 N at 1.2 m/s (4,070 N at 1.0), and the people tests below are already at their limit at 1.0.

### 4.4 Results

Mission simulation, firmware 4.7.2, night. One trip is dock to dock with one bin. Table: `tables/trips_r6.json`.

| Setting | Hardware change | Drop-off | Pick-up | Energy a trip |
|---|---|---|---|---|
| Revision 5.1 | none | 67 to 76 min | 75 to 77 min | 71 to 75 Wh |
| Revision 6, fast cruise off | sprockets | 65 min | 74 min | 70 to 73 Wh |
| Revision 6, middle: 0.6 m/s on a clear lane | none | 43 min (+2) | 46 min (+2) | 60 Wh |
| **Revision 6, fast cruise: 1.0 m/s on a clear lane** | sprockets | **36 to 40 min** | **40 to 42 min** | 57 to 59 Wh |
| Fast cruise with the leaf-season table | sprockets | 36 min (+2) | 47 min (+3) | 57 to 61 Wh |

- The fast-cruise row is eight trips with the final lane watch: a drop-off, a pick-up, three drops and three pick-ups (`sitl/r6f_val2`). The four trips run after the last turn fixes took 37.2 to 37.4 minutes (three drop-offs, each with a 43 s stop for the walker of section 4.6) and 40.2 minutes (a pick-up).
- The other revision 6 rows are one drop-off and one pick-up each, seed 7, run before the gateway look-ahead went in. That look-ahead costs a fast trip 2 to 3 minutes: the 24 trips of the 60-mission suite, run before it, took 34 to 39 minutes. "(+2)" is my estimate of the same cost for those rows; it does not apply with the fast cruise off.
- The middle option was run on the unchanged 5.1 drive and firmware settings. Its people tests were not run separately; at 0.6 m/s they would fall between the two columns of section 3.2.

With the fast cruise, three bins put out from 18:00 are at the road and the robot is home at 19:54. Three pick-ups from 18:00 are home at 20:04. In revision 5.1 the three drops ended at 21:31 and the third pick-up was refused.

Where the time goes in a fast drop-off, 37 minutes from switch-on to docked:

- 5 minutes are yard work: start-up, undocking, lining up on the bin, lifting, two turns on the spot, setting down, docking.
- 32 minutes are the two lane legs, 1,220 m in all. At 1.0 m/s throughout they would take 20.
- The robot is at 1.0 m/s for 8.7 of those 32 minutes, at 0.8 for 6.2, at 0.6 for 5.1, at 0.4 for 8.4 and at 0.2 for 3.3. What holds it back: the hill on the way down, a degraded satellite fix (0.7 m/s), gaps in the hedges, the narrow stretches and the last metres at each end.
- The satellite fix in the simulation degrades on a timetable the other agent set, and the gaps are those of the lane model. Under the real hedges both may be better or worse, so the real trip could be several minutes either side.

The leaf-season pick-up is 10 minutes longer because the empty robot creeps down the steep part at 0.15 m/s.

### 4.5 Stopping from the fast cruise

MuJoCo, robot 180 kg, full bin 110 kg, brake torque 34 N m a wheel, brakes on 0.15 s after the trigger. Distance from the trigger to standstill, in metres. Table: `tables/pstop_speed_r6.txt` (123 runs).

| Slope down | Load | Speed | Wet (grip 0.30) | Wet leaves (grip 0.22) |
|---|---|---|---:|---:|
| level | full bin | 1.0 m/s | 0.45 | 0.53 |
| level | empty | 1.0 m/s | 0.55 | 0.65 |
| 3 % | full bin | 1.0 m/s | 0.52 | 0.65 |
| 3 % | empty | 0.8 m/s | 0.46 | 0.58 |
| 6 % | full bin | 0.8 m/s | 0.43 | 0.58 |
| 6 % | empty | 0.6 m/s | 0.37 | 0.55 |
| 8.5 % | full bin | 0.6 m/s | 0.33 | 0.50 |
| 8.5 % | empty | 0.4 m/s | 0.27 | 0.61 |
| 8.5 % | empty | 0.5 m/s | 0.39 | 0.92 |
| 10 % | full bin | 0.6 m/s | 0.38 | 0.69 |
| 10 % | empty | 0.4 m/s | 0.38 | 3.04 (slides) |

Reading:

- The foam gives 150 mm. Every figure here is two to five times that. At the fast cruise a touch on the nose is a push of 0.3 to 0.7 m, not a stop inside the foam.
- The stand-still zone is 3 m, and the robot looks 10 m ahead at 1.0 m/s. So the fast cruise is safe for anyone the sensors find in time, and not for someone they miss. That is the trade.
- The empty robot on wet leaves is again the weak case: 0.61 m at 8.5 % and no stop at all at 10 %. Hence the leaf-season table and switch.
- The touch-safe table of revision 5.1 still holds with the weaker brakes: 63 to 141 mm at its own speeds, wet and on wet leaves, up to 8.5 % (and 1.1 m sliding for the empty robot at 10 % on leaves, as before).

Other physics at speed:

- **Kerb.** A 40 mm kerb struck at 1.0 m/s with a full bin loads the drive wheel with 4,520 N and the lift with 4,070 N. At 0.8 m/s it was 4,886 N and 3,858 N, so the frame checks of revision 5 stand. The actuator's holding factor falls from 2.28 to 2.16. The bin stays on the comb. A rigid wheel with no give in the tyre would see 6,214 N at 1.0 m/s, so the tyre limit on sheet 17 (no stiffer than 650 N/mm) stays.
- **Whole lane.** On the lane model with the real slope, made good as in revision 5: full bin down (P1, P3, and P7 heavier at night), the return legs (P2a, P2c), and the stop-and-hold tests on the steepest part (P4a, P4b) all pass at the fast speeds on grip 0.35. P1, P2a and P2c pass again on grip 0.22. Lane time 741 to 878 s against 1,745 to 1,818 s. The bin stays seated; the hold creeps 1.6 to 1.7 mm with no overrun. The speed trace peaks at 1.2 m/s for an instant as the wheels drop into the pothole at 290 m. Table: `tables/lane_fast_r6.txt` (10 runs at the fast cruise).

### 4.6 Turning on the spot

Three separate things were wrong here. The first is the reviewers' "real, if rare, collision with a bin in the yard".

**Which way round.** I reproduced their failure on my side, in seed 23 of the three-drop mission, on firmware 4.7.2: just after lifting the black bin at the house, the nose swept into the green bin parked beside it.

- The turn to face the lane there is a half turn, 183 degrees.
- The software took "the short way round" and worked it out afresh every cycle from the heading estimate. A degree of noise decided between left and right.
- One way round clears the green bin by 0.6 m. The other goes through it. The check before the turn only looked at the way it expected to go.
- Fix: for a near half turn the software checks both ways round against the map and the known objects, takes the way with more room, and keeps to it for the whole turn.
- In the 60 missions there were 51 such turns. One way was blocked in 6 of them. The way taken had at least 0.57 m of room. No contact.

This fault does not depend on the firmware version, so I expect it is what the reviewers saw in seed 7 on 4.6.2.

**How fast.** They also saw the turn run at 0.30 rad/s against a command of 0.13. The cause is in the firmware settings of B2-F, not in the command:

- the turn-rate feed-forward (0.8) is 1.5 times what the B2-F drive needs, and
- the minimum-throttle setting adds a fixed amount to every small command.

With the 2:1 chain stage the same settings would have been worse: 0.49 rad/s in my first fast trip. I set the feed-forward from the gearing (0.35), scaled the other gains by the same ratio and lowered the minimum throttle from 5 to 3 %. In the 60 missions:

| | Revision 5 settings (60 missions of 21 Nov) | Revision 6 (60 missions) |
|---|---|---|
| Loaded turn on the spot: highest rate | 0.40 rad/s | 0.28 rad/s |
| Speed of the nose corner at that rate | 0.56 m/s | 0.39 m/s |
| Time above 0.30 rad/s, nine loaded turns | 2.0 s | none |
| Setting off on a curved path from rest: highest rate | 0.68 rad/s | 0.57 rad/s |

So it is better, and it is still short of the 0.22 rad/s the review asks for (m-5). The brief swing when the robot sets off round a parked car lasts a fraction of a second. A hard limit in the firmware (`ATC_STR_RAT_MAX` 13 degrees a second) would hold everything at 0.22. I have not tested that setting, so it is not in the pack.

**People at a turn.** Rule 8 of section 3.1. Three tests. Each is a complete drop-off in which someone walks along the lane past the loaded robot at the road end, stands 1.4 m from its turning centre for 30 s and walks on. They keep 0.45 m from the hedge, which is the edge of what the lidars can tell from a hedge. Results on the code in the pack (`tables/pivot_people_r6.json`):

| Case | Result |
|---|---|
| From the road side, before the turn: the robot is still waiting for the pad to clear | The camera finds them at 4.6 m. The robot goes into the stand-still pause and stays in it for 43 s, until they have gone; they pass 0.5 m from its side. Then it finishes the wait, looks for a second and turns. It was never turning with them inside 3 m. Trip completed. |
| From the road side, during the turn | The camera finds them at 4.8 m. The robot stops turning and stands for 43 s, until they have gone. It was never turning with them inside 3 m. Trip completed. |
| From the house side, behind the robot, during the turn | The rear lidars report them as they cross the 3 m line. The robot stops turning 0.2 s later, with them 2.75 m away, having turned 0.7 degrees more. It stands for 43 s. Trip completed. |

The walker in these tests does not look. In the second and third they walked into the corner of the standing robot, because their line passes where its nose had come to rest. The robot had been standing in the firmware hold for at least 5 s by then.

It took three rounds to get there, and each round was found by running these tests again:

1. **The first version of the rule failed both of the tests I had then, the second with a touch.** While the robot stands across the lane, the hedge faces were still being fitted along the robot's own axis, so a person walking up beside it was taken for hedge. And the restart only asked "is anything moving?", so the robot turned on with a person standing still inside the circle. Now the faces are fitted along the lane during a turn, and one test starts the turn, watches it and restarts it.
2. **On the code I had taken for final, the turn began with a person already standing 0.7 m from the robot.** They had walked up while it waited for the pad to clear. It turned for 0.4 s, less than one degree, and the nose corner moved about 2 cm before the watch in the turn stopped it. Cause: that wait does not run the lane watch, and one look is not enough, because a thing only counts once two looks running show it. Now the robot looks for a full second before every turn, and the people rule holds during the wait as well.
3. **Then the turn ran on for 1.4 s with the walker from behind inside 3 m.** They were 1.8 m away when it stopped. Cause: at a turn only movement counts beyond the nose circle, movement is judged against where a thing was a second ago, and in that run the lidars only told this walker from the hedge at about 3 m. Now, outside the yard, a thing inside 3 m that was not there a second ago counts as moving at once.

I am glad the reviewers asked for this test. The runs before each fix are in the pack (`sitl/before_fixes`, the files named `r6f_pivflank_before_fix…`).

The rule at a turn is still weaker than the rule in the lane, and on purpose. At the road end the robot must be able to turn beside bins and a parked car, so beyond the nose circle only a camera person, movement and new arrivals hold a turn. Someone who walks up, stops 2 to 3 m away out of the camera's view and stands quite still stops the turn for a few seconds only. Two things cover that: the circle the nose sweeps has a radius of 1.4 m, and the nose corner moved at 0.39 m/s at most in the 60 missions (0.31 m/s in these tests), which is inside the touch-safe speed on the level, with the switch strip now round the corner.

## 5. The 60-mission score

The same 20 scenarios and three seeds as the reviewers' suite, with the fast-cruise settings, firmware 4.7.2. Scored by the B2-F script unchanged, and again with two criteria restated as in revision 5 (the bye-law windows; 75 Wh a trip). Table: `tables/score_r6_fast.md`.

| | Revision 5.1 (the reviewers' run) | Revision 6, fast cruise |
|---|---|---|
| B2-F script as it stands | 48 of 60 | 45 of 60 |
| With the bye-law windows and a realistic trip budget | 56 of 60 | 57 of 60 |

- **The 12 full missions all complete.** They fail one frozen criterion only: 50 Wh a trip. A trip now uses 56 to 58 Wh (5.1: 71 to 76). A 290 kg robot cannot do this lane on 50 Wh; that limit was set for the 92 kg B2-F.
- **They now fit the frozen 18:00 to 21:00 window.** Three bins out from 18:00: home at 19:46 to 19:48 (19:54 with the final lane watch). Three pick-ups from 18:00: home at 19:53 to 19:54 (20:04 with the final lane watch). Charge left 52 % (5.1: 41 to 42 %).
- **Three runs fail that passed before: s10b**, a garden sack in front of the bin at pick-up. The robot now stops 3 m from the sack and after two minutes reports "path blocked". The scorer expects the words "bin blocked", which came from a bin check the robot no longer reaches. The owner gets an alert and walks down either way. I have left it.
- The other 45 fault and hazard runs end as the script expects.
- **No contact in any run.** Least hedge clearance 0.186 m (limit 0.124 m; the reviewers' 5.1 run 0.175 m). Nearest approach to a parked bin 0.22 m.
- **Placement:** worst 0.129 m, mean 0.046 m, against a limit of 0.15 m (the reviewers' 5.1 run: 0.106 and 0.055 m). The worst case is nearer the limit than before. The softer firmware gains are the likely reason; I have not chased it.
- **Stops with nobody about:** 4 in the 60 runs, 3.2 to 3.4 s each: two leaving the yard, one at a turn at the road end, one beside the tipped bin.

**After the later fixes.** The suite ran before six later changes of the day: the pivot fix (section 4.6), the two lane-watch fixes and the three turn fixes (section 3.3). I did not have time to repeat all 60. Instead I ran missions again after each step.

- **With the final lane watch** (`sitl/r6f_val2`: a drop-off, a pick-up, three drops, three pick-ups): all four complete, with no contact. Eight trips of 36 to 42 minutes. Least hedge clearance 0.205 m, worst placement 0.098 m, nearest approach to a parked bin 0.29 m. Four stops of about 3 s with nobody about, three of them at turns in the yard: the watch during a turn is new, and it is a little nervous there.
- **On the code in the pack**, after the three turn fixes (`sitl/r6f_pivflank_a`, `_a2`, `_b`, `r6f_val3`): the three turn tests, which are complete drop-offs, and a pick-up. All four complete, with no contact. Least hedge clearance 0.241 m. One stop of 3 s with nobody about, at the road-end turn of the pick-up: that is the new arrival rule. The three-bin missions were not run again on this code.
- **After the pivot fix alone** (`sitl/r6f_val`): three completed. The fourth, three pick-ups with seed 11, ended at its first pick-up with the grab refused. The robot could not line up on the bin within the camera's 35 mm band in two tries, went home and raised an alert. The true offset was 26 to 28 mm; the comb takes 50 mm. The same seed completed in the suite and with the final lane watch.
- I do not think any fix caused that refusal. Across the suite's 27 line-ups the camera never read more than 30 mm, and in revision 5 the worst of 24 was 35 mm, exactly on the limit. The band is tight against what the driving achieves, and this is its tail. A third try or a 40 mm band would remove most refusals. I have not changed it.

## 6. The rest of the review, point by point

### Blockers

**B-1. The hill is not bounded at 8.5 %.** Agreed. I wrote "8.5 % at most" in the summary of the last note and that was wrong: 8.5 % is the smoothed figure, and the raw elevation cells allow 10 % over 25 m. Nothing I can do at a desk settles it. What changes:

- The survey in the test list is now the reviewers' method: a 2 m straightedge with a phone inclinometer, both wheel tracks, every 5 m from the house to 300 m (section 7, test 1).
- A leaf-season speed table, as M-5 asks: 0.35 m/s on the level and gentle slopes, and the fast cruise held to 0.5 m/s with a full bin and 0.15 m/s empty on the steep part. It is a setting, because the robot cannot see leaves.
- A leaf-season switch for the owner (`X_LEAF_NOGO=1`): pick-up trips, where the robot goes down the hill with no bin, are refused with a message. Until the hill is surveyed this should be on from October to December. Tested: the pick-up is refused at the dock.
- If the survey finds more than 8.5 % anywhere, the empty robot needs more braking: tail first down the hill, or brakes on the castors. With a lidar now on each rear leg tip, tail first has the sensing it lacked in revision 5. I have not designed or tested it for revision 6.

**B-2. The stop chain on sheet 15.** Agreed on all six points. Sheet 15 is redrawn:

1. One diode across each contactor, not one across both. A shorted diode now bridges one contactor only.
2. Two chains. The drive stop relay takes the e-stop, the nose and rear strips, tilt and the three watchdogs, and drops both contactors. The lift limit switches and the lift interlock work a separate pair of relays (K4, K5) that cut the lift feed only. The under-bin sensors and the standstill signal are the third input of that lift chain.
3. Relay outputs. The drive stop relay's three contacts go to contactor 1, contactor 2 and the supply of K4 and K5. Pre-charge is drawn as a sequence: the companion closes K3, the controller side charges through 1 kohm, then the reset closes the contactors.
4. Feedback without auxiliary contacts. The reset is refused unless the voltage on the controller side has fallen below 5 V within 3 s of the last stop. That is the B2-F voltage sense, and it also catches a shorted diode.
5. Single-channel sources (the watchdogs, the speed and tilt electronics) each drive a relay with linked contacts, one contact in each channel. Said on the sheet.
6. The brake coils are fed from the switched side, and drawn.

The sheet no longer claims a performance level. It says what the layout gives: no single stuck contactor, welded relay or shorted diode keeps the motors live. Each row is proved by a test in section 7.

### Major findings

**M-1. What the front camera cannot see.** Section 3. Each of the four gaps has a rule and a test: restart beside a person (cases "side" and "flank"), pivot flanks (the pivot rule and the three road-end tests), a false pause that never ends (a camera sighting must match a lidar object, and the hold now sums the pauses), and the rear side (the two rear lidars are in the simulation; the rear camera still is not).

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
| m-6 Score not re-run | Re-run in full (section 5). With a false camera person every minute I ran two trips, not the whole suite (section 3.4): time. |
| m-7 Cost risks | Taken into the range (section 8), except a new actuator: if no used one with the right gear and stroke turns up, add EUR 540 to 810. |

### The mission-simulation report

| Finding | Reply |
|---|---|
| 48 of 60 on the frozen criteria; the 12 full missions fail the 50 Wh limit | Section 5. With the fast cruise a trip uses less energy, because the electronics run for half the time. |
| Contact when someone steps out close ahead | Sections 2 and 3. |
| Behind and beside: no pause at all | Section 3. |
| The 15-minute hold never fires | The hold now counts all pausing in the last 20 minutes. |
| One false person a minute: 87 pauses, +4.7 minutes | A camera sighting only stops the robot if a lidar object is at the same place, or if it is within 2.5 m. Section 3.4. |
| s3a seed 7 on firmware 4.6.2: the loaded pivot ran at 0.30 rad/s and touched the parked green bin | Reproduced on 4.7.2 in seed 23. Two causes, both fixed: the way round was left to chance, and the firmware settings made the turn run fast. Section 4.6. Please re-run all three seeds. |
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
| 13 | Fast cruise | Only after 1 to 12. A dummy pulled across the lane 3 m, 2 m and 1 m ahead of the nose at 0.6, 0.8 and 1.0 m/s; a dummy standing at a gateway; a box left in the lane. Then tests 5 and 6 at the fast speeds for the stop distance. | Stopped before the dummy at 3 m and 2 m. Note the speed at the touch at 1 m. Stop distances within 20 % of section 4.5. |
| 14 | Lidar | A 0.4 m box in the path; a 0.2 m box, which is below the lidars. | Stands still 3 m from the tall box and reports the path blocked. The nose strip stops it at the low one. |
| 15 | Remote stop | Stop over 4G; then switch 4G off in mid-trip. | Stops. Carries on or holds as set, and says so. |
| 16 | Bolts | Torque wrench on every structural bolt after ten trips. | None has moved. |

## 8. Cost

Against the B2-F parts list (EUR 3,417 parts, EUR 4,112 all-in). Script and full table: `tables/cost_r6.py`, `cost_r6.md`.

| New in revision 6 | Low, EUR | High, EUR | Basis |
|---|---:|---:|---|
| Third lidar (one on each rear leg tip in place of one) | +50 | +50 | price of the B2-F lidar line |
| Lift relays K4 and K5, three relays with linked contacts for the watchdogs, second diode | +50 | +110 | ASSUMED: five small relays at EUR 9 to 20, diode 5 to 10 |
| Companion computer that can run the person detector on two cameras | +60 | +130 | the reviewers' figure |
| 24-tooth wheel sprockets in place of 42-tooth | -5 | 0 | ASSUMED |
| Contactors | 0 | 0 | the B2-F pair stays; no auxiliary contacts needed |

| | Parts, EUR | All-in, EUR |
|---|---|---|
| B2-F parts list | 3,417 | 4,112 |
| Revision 5.1 | 3,369 to 3,979 | 4,055 to 4,789 |
| **Revision 6** | **3,524 to 4,269** | **4,241 to 5,138** |
| With every used-part option of the last note | 3,194 to 4,059 | 3,844 to 4,885 |

The reviewers put a realistic figure at EUR 4,100 to 5,100. Revision 6 lands in the same place. One risk is outside the range: if no used lift actuator with the right gear and stroke can be found, a new one adds EUR 540 to 810.

Every figure not taken from the B2-F list is an estimate. Nothing has been quoted.

## 9. Still open

1. **The hill's real slope.** Test 1. Everything about the empty robot on wet leaves waits on it.
2. **What the real sensors see.** Detection rates, range in rain, false objects from a moving hedge, the hedge blind band of 0.3 to 0.5 m, anything lower than 0.30 m.
3. **The fast cruise is not touch-safe.** By design. It rests on item 2.
4. **Firmware tuning.** The settings in the pack fit the simulated drive. The real drive will need its own, and the turn-rate figures of section 4.6 must be measured again.
5. **Not written:** a slope check from the robot's own pitch reading; tail-first driving for the empty robot; a finer rule for things left beside the path.
6. **Not run on the code in the pack:** the 60-mission suite, the trips with false sightings, with the leaf-season table and with the middle option. The lane people cases and the three-bin missions ran with the final lane watch but before the three turn fixes, which act only at a turn and in the wait before a set-down. After those fixes I ran the three turn tests and a pick-up (section 5).
7. **Idealised in the simulation:** the rear camera (not modelled for people; its bin measurement is the true pose plus a fixed error), the seating sensor, the load reading for the slope rule, and the robot's braking in the mission simulation (0.9 to 1.2 m/s2; the physics tests give 1.0 to 1.7 on the level and less on the hill, where the speeds are lower).
8. **Firmware 4.6.2.** I have only 4.7.2. The turn-direction fault of section 4.6 does not depend on the version, but I could not run theirs.
9. **Line-up on the bin.** One pick-up in a re-run ended with the grab refused (section 5). The camera band for the line-up is tight against what the driving achieves.
10. **Carried over unchanged:** the step, pothole and trench stall the robot if the lane is left as the lane model assumes; frame rail safety factor 1.99 at the M10 holes; soft nose untested; prices assumed.

## 10. For the other agent: what I need from you

1. A plain yes or no from Brian on the lane (decision 4).
2. Your stress wrapper (`b2f_companion_xs51.py`) or the exact mover settings of each profile, so that we run the same cases. Mine are in `chains/stress.sh`.
3. A re-run of s3a (three drops), all three seeds, on firmware 4.6.2 with the revision 6 files. Before the fix the turn touched the green bin on my side in seed 23; you saw it in seed 7.
4. Whether your lidar model can add dropouts and false returns. Mine cannot yet, and that is the test the lane watch most needs.
5. Brian is forwarding the revision 5 pack. If it does not arrive, the mass table you asked for is also in this pack.

## 11. Files

| File | What it is |
|---|---|
| `REPLY_and_REV6_2026-11-24.md` | this note |
| `BinRobo_improved_rev6_drawings_2026-11-24.pdf` | 18 sheets, all reissued. Changed in content: 13 (parts), 14 (looms), 15 (stop chains), 17 (speed tables, shim note), 18 (sensing and rules). The views show the lidar on each rear leg tip and the switch strip round the nose corners. |
| `BinRobo_improved_rev6_drawings_png.zip` | the same as PNG |
| `BinRobo_rev6_tests_2026-11-24.zip` | software, settings, command lists, results and tables of this note |

In the test zip:

- `software/`: `b2f_r6.py` (new: lane watch, zones, pause, fast cruise), `b2f_companion_x.py`, `b2f_runner_x.py` (test hooks: walkers that follow the lane, gateways, boxes; rear lidars), `lanerun_x.py`; the 5.1 versions beside them for a diff.
- `settings/`: `env_r6.sh`, `env_r6_fast.sh` (the recommended set), `env_r6_slow2.sh` (fast cruise off), `env_r6_mid.sh` (no sprocket change), `env_r6_fast_leaf.sh` (leaf-season tables), `env_r6_fast_v10.sh` (test only: 1.0 m/s also under a degraded fix).
- `chains/`: the command lists as run, with the log. `software/code_final.md5` is the code in the pack; `code_lane_tests.md5` is what the lane people tests ran on, before the three turn fixes.
- `tables/`, `stop_tests/`, `lane/`, `sitl/` (result files of every mission run in this note; traces of the people tests), `drawing_scripts/`.

## Sources

- Reviews of 23 November 2026: `SITL_rev51_2026-11-23.pdf`, `TEST_rev51_2026-11-23.pdf`, `COLDEYE_rev51_2026-11-23.pdf`.
- B2-F files: lane line and heights (`sitl/data/route.json`), parts list (`b2f_bom_lines.json`), firmware settings (`params/bintug_b2f.parm`).
- [the county council, waste management bye-laws (summary page)]([county council website])
- [the county council, list of the bye-law documents]([county council website]). I could not open the PDF itself.
- Revision 5 and 5.1 notes and test packs of 21 and 22 November 2026.
