# BinRobo improved version: reply to the review of 21 November, and revision 5

21 November 2026. From the reviewer/tester agent, for Brian and for the B2-F author.

## Summary for Brian

You asked for three things: people avoidance and navigation on lidar and camera together, keeping to the robot's left side of the lane, and a lower price, with the review's other points improved. Revision 5 does the first three. Most of the review's other points are answered; the ones that are not are listed in section 5.

- **Price: about EUR 4,220 to 5,200 all-in, down from 7,340 to 11,330.** That is back at B2-F's level (4,245). It assumes the lift actuator is bought used; new, add about EUR 800. Most prices are assumed, none quoted.
- **People avoidance: two sensors in every direction.** A lidar low on the nose and a camera watch forward; a second lidar (EUR 50) and the rear camera watch backward. Either can stop the robot. The forward pair is in the driving software and tested; the rear pair is drawn and costed but not yet in the software. With both working, a person can step out 0.4 m ahead on the level and not be touched; closer than that, a soft foam nose with switch strips touches first and the robot stops inside the foam. **None of this is a certified safety system.** That is what the price cut costs, and it is your decision (section 6).
- **Keeping left: 0.42 m from the left hedge** on the straights, leaving about 2.7 m of lane free. Closer fails: at 0.30 m the robot gets within 88 mm of the hedge, and holding the edge through sharp bends does not work for a robot this long.
- **A fault of mine that you should know about.** In the first full test of the new lidar-and-camera navigation the robot came within 1 mm of a hedge at a sharp bend, and in another mission it turned on the spot while waiting. I traced both, fixed them, added a protective field that stops the robot for anything in its path, hedge included, and re-ran everything. In the second run no mission comes closer to a hedge than 0.20 m, and faults I put in on purpose are caught with 0.13 m or more to spare. A further test, a person standing still in the robot's path, showed that the lidar logic inherited from B2-F can pass a person standing near a hedge at 0.16 m without stopping; a camera person check now stops the robot at 1.4 m in every such run. On the reviewer's own scoring the count is 48 of 60, unchanged, because the 12 full missions miss energy and time limits set for the faster B2-F robot (3.7).
- **Mechanical re-test at the new weight of 180 kg:** all gate tests pass except weight, 179 of 180 pick-ups lift and one is refused safely, and the robot completes the lane once it is made good. It still cannot climb the 40 mm step, the pothole or the trench as they are today.
- **Still open:** the empty robot is only safe on a wet 12 % pitch when it comes down tail first, and that is tested in the lane simulation but is not yet in the mission software; on wet leaves on that pitch a touch is not a safe stop even with a full bin; the real slope and the highest edge on your lane are not measured; the lane-keeping fixes were tested with injected faults because I could not reproduce the original event on demand.

What I need from you is in section 6: chiefly, whether uncertified people protection is acceptable, and two measurements on the lane.

## 1. Your three directions

### 1.1 People avoidance and navigation on lidar and camera together

Every direction the robot moves in is now watched by two different sensors, and either one can stop it.

| Direction | Lidar | Camera | Last line if both miss |
|---|---|---|---|
| Forward, and sideways during a pivot turn | front lidar, moved down from the post to a shelf on the nose: scan plane 0.30 m up, where it sees legs, children and dogs, with a clear view ahead and to both sides | front camera on the post, finds people to about 6 m | soft nose across the full width, switch strips on the front and both sides |
| Backward (onto a bin, and tail first down a steep pitch) | **new: a second lidar** on the tip of the left leg (EUR 50) | rear camera on the mast | rear bumper switches; every reverse move at 0.1 m/s |
| Under the bin at set-down | - | rear camera: nobody within 1 m | two ToF sensors look at the ground under the bin wheels; load guard on the lift |

The rules (they are on the new sheet 18 with a plan view of the zones):

1. A person or unknown object in the path inside 4 m: slow to 0.25 m/s. Inside 1.5 m: stop and wait. Move on when the path has been clear for 3 s. The lidar does this for anything in the path that is not on its map; the camera does it for any person or dog within 0.5 m of the robot's sides, map or no map.
2. **New: a protective field.** Anything at all, hedge included, inside the robot's own path up to 0.6 m ahead of the nose or within 80 mm of its sides: stop, back out 0.8 m, start again. Three times in two minutes: hold and call you. This one uses neither the map nor the satellite position, so it still works when those are wrong.
3. Turning is slow. On the spot, the nose corner now moves at 0.3 to 0.6 m/s at the peak (it was 1.0 to 1.2 m/s). In the lane the heading command may change at 0.15 rad/s at most. A stopped robot holds its heading.
4. If one sensor stops reporting, carry on at 0.2 m/s on the other and report it. If both stop, stop.

Rules 1 to 3 are in the mission software and tested (3.7); the camera in them is a model with assumed detection rates, not an image pipeline. Rule 4, the rear sensors and tail-first driving are not in it yet.

**What this gives, in numbers.** I simulated a person appearing in the path at a random moment. The robot brakes after two detections in a row. The figure is how far ahead the person can appear and still not be touched, in 99.9 % of cases:

| Case | Lidar and camera | Lidar only | Camera only, day | Camera only, night |
|---|---:|---:|---:|---:|
| Level, full bin, 0.4 m/s | 0.40 m | 0.46 m | 0.90 m | 1.97 m |
| Level, empty, 0.4 m/s | 0.42 m | 0.48 m | 0.92 m | 1.96 m |
| 6 % down, full bin, 0.3 m/s | 0.31 m | 0.37 m | 0.71 m | 1.50 m |
| 12 % down, full bin, 0.2 m/s | 0.25 m | 0.29 m | 0.51 m | 1.05 m |
| 12 % down, empty, tail first, 0.2 m/s | 0.22 m | 0.25 m | 0.47 m | 1.00 m |

The stopping distances in this are simulated. The detection rates are ASSUMED until they are measured on the built robot: lidar 10 scans a second with a 90 % chance per scan of finding an adult's legs; camera 5 frames a second with 85 % per frame by day and 60 % at night under infra-red. Someone who steps out closer than these distances is touched by the soft nose, at a speed from which the robot stops inside the foam (3.1).

**What this does not give.** Neither sensor is a certified safety device, and nor is the home-made soft nose. Revision 4 had a certified bumper and a certified speed monitor; revision 5 trades those for two-sensor coverage in every direction and a much lower price. That is your decision to make, and I think it is a reasonable one for a private lane, but it should be said plainly: a qualified person would not sign this off as a safety system as it stands.

**Navigation.** The same two sensors now hold the robot's place in the lane. The lidar measures the hedge faces (as B2-F did) and the front camera measures the left edge. In the mission runs both gave a reading in 86 % of the control cycles and the camera filled in where the lidar saw no hedge. Where the two differ by more than 0.25 m, the robot takes the reading that fits the known width of the lane. With the lidar's hedge reading switched off altogether, one mission still completed on the camera alone (least hedge clearance 0.20 m).

**This is where my first attempt went wrong, and you should know it.** In the first full run of revision 5 the robot came within 1 mm of the right hedge at the sharp bend 75 m from the house. My camera model took the far hedge of the bend for the left edge, and my rule for a disagreement was "use the nearer reading", so the robot steered away from a hedge that was not there and into one that was. Nothing stopped it, because hedges on the map are filtered out of the obstacle check. That is fixed and re-tested (3.7), and the protective field in rule 2 is the result: the robot must stop for a hedge whatever its map says.

### 1.2 Keeping to its left side of the lane

B2-F's software already kept left, 0.42 m from the hedge face. I tried to pull it in closer and to hold the left edge through bends:

| Setting | Least clearance to the hedge in a full trip | |
|---|---:|---|
| 0.42 m from the hedge | 0.213 m | kept |
| 0.35 m | 0.146 m | passes the 0.124 m limit with 22 mm to spare |
| 0.30 m | 0.088 m | **fails** |
| 0.42 m, staying left through sharp bends as well | 0.047 m | **fails**: the long robot needs the middle of the lane to get round |

These trials were run on the first-pass software. With the second pass (3.7) the 0.42 m setting gives 0.20 m at the same place, so 0.35 m would now be marginal.

So 0.42 m stays. The robot's left side runs 0.42 m from the left hedge on the straights and moves to the middle only for sharp bends. That leaves about 2.7 m of lane to its right for anyone passing. If you want it closer, the hedge at station 417 m is what limits it: trimming that bulge would allow 0.35 m.

### 1.3 Price

| | All-in, EUR |
|---|---:|
| B2-F parts list (the review's figure) | 4,245 |
| Revision 3 (the review's figure) | 4,851 to 6,794 |
| Revision 4 (the review's figure) | 7,341 to 11,334 |
| **Revision 5, lift actuator bought used** | **4,220 to 5,200** |
| Revision 5, lift actuator bought new | 5,050 to 6,000 |

Revision 5 is back at about the price of B2-F, and EUR 3,100 to 6,100 below revision 4. What came out:

- The certified foam bumper and its control unit (EUR 650 to 1,500) became a home-made soft nose with switch strips (about EUR 130 to 270).
- The certified speed monitor and its sensors (EUR 380 to 1,000) became a second small controller with its own ground-speed source (about EUR 40 to 65 with B2-F's own parts).
- The two light-beam pairs (EUR 200 to 400), which could not work as drawn anyway, became two ToF sensors (EUR 12).
- The lift actuator is the same type but bought used and bench-tested (about EUR 250 to 400 against 940 to 1,060 new). One used unit was listed at about USD 294 (Sources). If no used unit turns up, the new price applies: that is the second row.
- The safety controller and the contactors are bought used.

The full table, line by line against the B2-F parts list:

| Change against the B2-F parts list | Low, EUR | High, EUR | Basis |
|---|---:|---:|---|
| Frame: box section, laser-cut plates, bolts (line FAB-B2 was 354) | -14 | +181 | ASSUMED: 55 kg of section at EUR 2.2 to 3.0 a kg, 25 kg of cut plate at EUR 6 to 10 a kg, bolts 50 to 80 |
| Lift actuator, bought used (line B-0 was 164) | +86 | +236 | used unit EUR 250 to 400: one used listing at about USD 294 (Sources). New: EUR 940 to 1,060 |
| Lift stop blocks and four limit switches | +40 | +80 | ASSUMED |
| Soft nose with three switch strips; rear bumpers kept (lines BMP-L8 and G22 were 170) | +20 | +160 | ASSUMED: foam and cover 45 to 80, ribbon switches 60 to 150, aluminium 25 to 40 |
| Second lidar, for the rear | +50 | +50 | price of line G21 |
| Front camera with infra-red light | +30 | +45 | ASSUMED, as the rear camera |
| Two ToF sensors under the bin | +12 | +12 | price of line B2-GAP |
| Ground-speed source for the watchdog | +10 | +35 | ASSUMED |
| Safety controller, bought used (line SR-L8 was 61) | +39 | +189 | ASSUMED: EUR 100 to 250 used |
| Contactors with mirror contacts, used (line KM-L8 was 57) | +0 | +80 | ASSUMED |
| Castor beam pivot parts, longer pad springs | +20 | +40 | ASSUMED |
| B2-F lines not needed: pad actuator and switch, hitch motor and switch, ballast | -121 | -121 | their prices |
| Sourcing: simpler 4G board, plain multicore harness | -80 | -80 | my cost review of 13 November |
| **Sum of changes** | **+92** | **+907** | |

Most rows are ASSUMED and say so. Nothing has been quoted. Your earlier rule, "no capability or safety cuts to save money", is kept for capability. For safety it is kept in the sense that every function revision 4 had is still there, but three of them are no longer certified parts; that is the trade described in 1.1.

## 2. The three reports, finding by finding

This section is for the B2-F author's side: "you" here means the reviewer. All three reports reproduce my revision 4 numbers and I accept their criticisms. Two of them go to how I summarised: the "122 mm longest stop" headline counted the empty robot as tail first when tail-first driving did not exist, and I presented castor brakes as a fix when my own odd result (0.72 m on wet leaves) said they were not. Both were too favourable. The castor-brake recommendation is withdrawn.

### Cold-eye review

| Finding | Revision 5 |
|---|---|
| **B-1** Empty robot cannot hold or stop nose first on a wet 12 % pitch; the standstill monitor cannot see a slide | **Tail first is now built and tested in the lane simulation** (3.2). Tail first, the empty robot stops in 71 mm from 0.2 m/s on the wet pitch and in 171 mm on wet leaves, where nose first it does not stop at all. The rear gets a lidar and a camera (drawn and costed, not yet simulated). Slide: the watchdog is to compare wheel speed with ground speed (satellite and lidar motion, optionally an optical sensor under the frame), so that a slide with locked wheels is seen; that is designed and costed, not simulated. I did not put a sensor on a castor wheel: the castor swivels freely and a cable would wind up. Still open: tail first is not in the mission software, and the real pitch is unmeasured. |
| **B-2** Person protection partial: corners, pivot turns, reversing | Soft nose over the full 936 mm width with switch strips on the front and both side faces. Pivot turns are slowed and every reverse move is commanded at 0.1 m/s, both now in the mission software (measured in five missions: turning on the spot peaks at 0.21 to 0.40 rad/s, nose corner 0.30 to 0.57 m/s, against 0.7 to 0.9 rad/s and 1.0 to 1.2 m/s in the first pass; reverse peaks at 0.13 m/s against 0.18. The firmware still overshoots the rate it is asked for (0.13 rad/s), so its turn-rate loop needs tuning on the real robot). A lidar check of the turning circle for unmapped objects is not written; the circle is still checked against the map only. A protective field stops the robot for anything within 0.6 m of the nose, and a camera person check stops it for anyone within 0.5 m of its sides (3.7). And the main change: lidar and camera together watch forward and to the sides, and a second pair is drawn for the rear (1.1). None of it is safety-rated; the slope speed rule is still ordinary software. |
| **M-1** Under-bin beams blocked by the bin's own wheels; guard tied to the pick-up ground | The beams are gone. A ToF sensor behind each leg guard looks down at the spot where the bin wheel will land. It reads the bare ground when the robot arrives and blocks lowering if a later reading is 10 mm short. That also gives the load guard the local ground, as you asked. Simulated (3.3). The guard's forces at 6 mm/s are 108 N at most, under the 125 N foot figure you quote (135 N if the robot is 10 % heavier); at 13 mm/s they are 143 to 147 N, so the last 100 mm are lowered at 6 mm/s. |
| **M-2** Speed rule rests on grip, slope and bumper figures the robot cannot know | Partly answered. The rule now looks 3 m ahead, so the robot is already slow at the brow (your tester's 938 mm case). Slide detection is designed, not simulated (B-1). Grip is still not measured before a descent; a brake check on the first metre of a pitch is the obvious next step and is not written. The soft nose switches at the first touch (a ribbon switch on its face), so there is no switching travel to add; its 150 mm of give is still an assumption. |
| **M-3** Bolted corner joints slip; fatigue detail falls to about 50 | Agreed. Joints are now 4 x M10 8.8 per plate pair (2 through the rail 60 mm apart, 2 through the cross-member 45 mm apart), contact faces bare and wire-brushed, prevailing-torque nuts, re-torque after the first ten trips. Slip check: 9.0 kN demand per bolt against 11.8 kN with bare wire-brushed faces (factor 1.30; 1.20 against your 443 N m) and 7.8 kN with painted faces, which would slip. Table in 3.5. Fatigue with a slip-resistant joint: a stress range of 44 MPa against 67 MPa allowed (ASSUMED load history). |
| **M-4** Lift stop order not robust at the top | Top blocks are now reached at +340 mm and the top switch bodies at +346 (sweep: 340.5 and 346). The actuator's own stop, at +331 to +335 with the stroke tolerance you give, is 5 mm or more inside the blocks. |
| **M-5** Bye-law window misread | Agreed, and thank you for tracing it to the inherited code. The companion now has two windows and uses the measured trip time (3.7). My "castor brakes to get the third bin back" argument is withdrawn. |
| **M-6** Cost understated | Agreed; I used your figures for revision 4. Revision 5 costs in 1.3. |
| **M-7** Only low edges can be climbed from a standstill | Tested (3.4): empty, from a standstill with the castors at the edge, 15 mm is climbed and 20 mm is not. The lane condition is now "every edge over 15 mm is ramped". |
| m-1 Nose cross-member | Drawn as 60 x 60 x 4. Safety factor 2.45 (you estimated 2.43). |
| m-2 Mass rows | Actuator 5.75 kg, crush tubes 0.054 kg each: both in the table. |
| m-3 Top tie bolt in aluminium | Steel thread inserts in the blocks. Locking nuts and a re-torque note are on sheet 17. |
| m-4 Lift current limits in the cold | Noted on sheet 17: set both on the bench at 0 C. |
| m-5 Bumper height, kerbs, brambles | Unchanged height (115 to 265 mm). Nuisance stops from brambles are likely and are the price of a low soft nose. |
| m-6 Length and pivot circle | Now 1,736 mm long (1,831 before); pivot circle 2.81 m. |
| m-7 Castor brakes | Withdrawn (see above). |
| m-8 PL estimate | Withdrawn for the people functions: they are not rated in revision 5. |
| m-9 Clash results | Same check on revision 5: 15 inherited pairs, none involving a part I drew. |

### Mechanical re-test

| Finding | Revision 5 |
|---|---|
| Tail first is assumed, not built | Built in the lane simulation and tested on the pitch (3.2). Not in the mission software. |
| Slope transitions are not in the map: 938 mm at the brow | The speed rule looks 3 m ahead. In the lane runs the robot reaches the 12 % pitch at 0.22 m/s with a full bin and stays under 0.23 m/s on it (3.6). The empty descent is covered by the tail-first runs in 3.2. |
| Castor brakes do not fix wet leaves | Agreed. Withdrawn. |
| The lowering guard does not see 20 mm | With the window referenced to the ground and the margin cut from 15 to 8 mm, the guard sees 20 mm in every case I ran (6 and 13 mm/s, 110 and 25 kg, one wheel and both). 15 mm is seen in two cases of three. The ToF sensors see 10 mm, if the object is there before lowering starts (3.3). |
| Open pothole: hedge clearance 5.6 mm | It still stalls in the open pothole, now with 89 mm to the hedge. The pothole has to be filled. |
| Sharp drop: 0.70 m/s over the edge | 0.65 m/s now. The speed rule cannot fix this: the robot is falling off an edge. The answer is the lane condition, every edge over 15 mm ramped. |
| Empty 40 mm step fails on B2-F too | Noted, thank you: it is the layout. |

### Driving-software re-test

| Finding | Revision 5 |
|---|---|
| 47 of 60; six "too late", one hedge 0.098 m, one wrong alarm | First pass: 48 of 60, with three new faults (3.7). Second pass: 48 of 60 on your script and 57 of 60 with the time window and energy budget restated for revision 5. No mission comes closer to a hedge than 0.196 m. The wrong alarm in s4c is gone: all three seeds end as the no-fix hold. "Too late" now happens only on the three pick-up days of your 18:00 clock. |
| Trip-start check assumes 50 minutes | Uses the longest trip measured so far that evening plus 5 %, and 78 minutes before any has been measured. |
| Bye-law as two windows | Done: drop-offs from 18:00 with only a quiet-hours limit (22:30, my assumption, for Brian to confirm); pick-ups from 10:00 on collection day, home by 21:00. |
| No-fix hold and the firmware fence race | A fence trip during a no-fix hold is now reported as the no-fix hold it is. |
| Hedge clearance at the pad with the longer robot | The robot is 95 mm shorter. In the pick-up missions the least clearance is 0.22 to 0.24 m, and it is at the hedge bulge at 417 m, not at the pad. |
| Final reverse still partly truth-based; yaw noise idealised; frames treated as independent; bin weight taken from truth | Not changed. These remain idealised sensor models. |

## 3. Test results

Everything below is simulation at the revision 5 weight of 180.0 kg, 60 N m drive limit, on the B2-F author's own scripts plus my switches. Assumed inputs are marked. As in section 2, "you" and "your" in this section mean the reviewer.

### 3.1 Stopping for a person, and the speed rule

Distance from the first touch on the nose to standstill, wet surface (grip 0.30), 0.15 s from touch to brakes. The rule is set so that this stays inside 130 mm, against 150 mm of give assumed in the foam.

| Slope down | With a bin: speed, stop | Empty: speed, stop |
|---|---|---|
| Level or uphill | 0.4 m/s, 106 mm | 0.4 m/s, 127 mm |
| Up to 3 % | 0.4 m/s, 119 mm | 0.3 m/s, 92 mm |
| 3 to 6 % | 0.3 m/s, 95 mm | 0.3 m/s, 129 mm |
| 6 to 9 % | 0.3 m/s, 118 mm | tail first, 0.2 m/s, 53 mm |
| Over 9 % | 0.2 m/s, 107 mm | tail first, 0.2 m/s, 71 mm |

The rule now uses the steepest slope within 3 m ahead, so the robot is already slow when it reaches a brow.

Where the rule's margins end:

| Case | Stop |
|---|---|
| Full bin, 12 %, wet leaves (grip 0.22), 0.2 m/s | 288 mm: **outside the foam** |
| Empty, tail first, 12 %, wet leaves, 0.2 m/s | 171 mm: just outside |
| Empty, **nose first**, 12 %, wet, 0.2 m/s | 354 mm; on wet leaves it does not stop |
| Robot 10 % heavier: empty tail first 12 % / full bin 12 % / empty level 0.4 m/s | 72 / 95 / 130 mm |
| Reaction 0.20 s instead of 0.15: full bin 9 % at 0.3 m/s / empty level 0.4 m/s | 133 / 147 mm |

So on wet leaves on the steepest pitch a touch is not a safe stop even at 0.2 m/s with a full bin; there the two sensors have to do the work (1.1), or the leaves have to be swept. The bin stayed on the robot in all 61 runs.

### 3.2 The empty robot on the 12 % pitch, in the lane simulation

Your B-1 was about this case, so I built it: the empty robot crossing the steep pitch nose first and tail first, on a wet surface and on wet leaves, once stopping for a person who steps into the lane and once stopping and holding half-way down.

| | Wet (grip 0.30) | Wet leaves (grip 0.22) |
|---|---|---|
| **Tail first**, person steps in | controlled stop with 2.7 m to spare, waits, carries on | the same |
| **Tail first**, stop and hold half-way | holds: 0.4 mm of creep in 3 s | holds: 30 mm of creep in 3 s, then still |
| **Nose first**, person steps in | controlled stop with 1.8 m to spare | **runs away**: reaches 1.4 m/s, stops 0.74 m after the brakes go on with the person 0.71 m ahead |
| **Nose first**, stop and hold half-way | stops 0.18 m late, creeps 14 mm | **cannot stop**: slides 12 m to the foot of the pitch, reaching 2.1 m/s |

The lane script marked the last case PASS because the robot was still when it measured the hold; I count it as a failure. Tail first is the only way the empty robot is safe on that pitch, as your review said. It is tested here in the lane simulation only: the mission software still drives nose first at 0.2 m/s on steep ground, which stops in 79 mm on a wet 8 % slope but needs 354 mm on a wet 12 % one. Until tail first is in the mission software and the real pitch is measured, an empty robot should not be sent down anything steeper than 8 %.

### 3.3 Lowering the bin

Two layers, both simulated at 180 kg.

**Before lowering: the ToF sensors.** One behind each leg guard, looking through a hole at the ground where the bin wheel will land. It remembers the bare-ground reading from when the robot arrived, and lowering is blocked if a later reading is 10 mm short.

| Block under the wheel | 10 mm | 15 mm | 20 mm | 25 mm | 40 mm | 60 mm | none |
|---|---:|---:|---:|---:|---:|---:|---:|
| Reading short by | 11.9 mm | 17.8 | 23.8 | 29.7 | 47.5 | 71.3 | 0.0 |
| Lowering | blocked | blocked | blocked | blocked | blocked | blocked | allowed |

**While lowering: the load guard**, for something that arrives after the ToF check. Its window now ends 8 mm above the expected touchdown (15 mm before).

| Case | At 6 mm/s | At 13 mm/s |
|---|---|---|
| No block, 110 / 60 / 25 kg bin | normal set-down | normal set-down |
| 10 mm block, 110 kg | not seen: 860 N | - |
| 15 mm block, 110 kg | not seen: 848 N | stopped, 147 N |
| 15 mm block, 25 kg bin | stopped, 80 N | - |
| 20 mm block, 110 kg / 25 kg / under both wheels | stopped, 108 / 81 / 108 N | stopped, 110 N |
| 25, 40, 60 mm block, 110 kg | stopped, 108 to 109 N | stopped, 143 to 144 N |
| 20 mm block, robot 10 % heavier | stopped, 135 N | - |
| 25 mm block, 25 kg bin, trip level 50 N | stopped, 51 N | - |

So the guard now sees 20 mm in every case, which it did not in revision 4. At 6 mm/s the block carries 108 N at most at the nominal weight, and 135 N if the robot is 10 % heavier, which is over the 125 N figure. The last 100 mm are therefore lowered at 6 mm/s. Still not covered: something under 15 to 20 mm that slides in after the ToF check, and a real sensor's noise, which is not in the model (the type used reads to a few millimetres at this range; ASSUMED).

### 3.4 Edges

At 60 N m and 180 kg, a sharp edge across the full width:

| | From a standstill at the edge | With a 3 m run at 0.3 m/s | Met at 20 degrees |
|---|---|---|---|
| Empty robot | 15 mm (20 mm stalls) | 20 mm (25 mm stalls) | 30 mm |
| Full bin | 20 mm at least (castors at the edge) | 25 mm (30 mm at 0.4 m/s only) | 40 mm |

The lane condition is therefore: **every edge over 15 mm across the lane is ramped.** That replaces my revision 4 figure of 20 mm, which depended on a run-up, as the review said.

### 3.5 Gate, pick-ups, loads and structure at 180.0 kg

| Gate test | Result |
|---|---|
| G1 pick-ups, three bin types | 90 of 90 held, none knocked over |
| G2 hill start on 12 %, grip 0.22 to 0.30 | pass; rolls back 34 mm |
| G3 40 mm step, your test | pass with your run-up; see 3.4 for what it can do from a standstill |
| G4 emergency stop, 12 % downhill, wet, full bin, from 0.5 m/s | 0.280 m forward, 0.122 m in reverse |
| G5 pivot turn | swept circle 2.81 m (limit 3.2; revision 4 was 3.00) |
| G6 set-down and release, 18 cases | all pass |
| G7 time-step check | pass |
| G8 tipping | static poses pass; hand calculation 32.3 degrees (31.6 with the bin's weight 60 mm off-centre) |
| G9 weight under 120 kg | **fail: 180.0 kg** |

180 pick-ups with scattered start positions: 179 lifted, 1 refused safely, none lifted more than 50 mm off-centre (largest 29.4 mm); 30 needed more than one approach and one was set down and re-gripped. The four slippery hill starts nose uphill all reach the top. All 24 stress cases pass (robot 10 % heavier and lighter, 15 % less grip, more rolling resistance).

Largest loads:

| Load | N | Case |
|---|---:|---|
| Drive wheel, carrying | 3,497 | emergency stop in reverse on 12 % |
| Drive wheel, your load cases with the compliant tyre | 4,160 | pothole at 0.5 m/s |
| Drive wheel, kerb at 0.8 m/s on the stiffest tyre allowed (650 N/mm) | 4,886 | my run |
| Drive wheel, rigid-tyre model | 12,707 | sharp step at 0.8 m/s; information |
| Comb, carrying | 2,393 | |
| Comb, kerb at 0.5 / 0.8 m/s | 3,003 / 7,271 | rigid tyre (7,946 at 0.8 m/s on the 650 N/mm tyre) |
| Lift, kerb at 0.5 / 0.8 m/s | 3,017 / 3,858 | lift cap raised so the shock is not clipped |
| Pad | 1,410 | |
| Sideways force on a drive tyre | 831 (full bin), 584 (empty) | pivots, turns and cross-slope stops |

Hand calculation on these loads, 62 rows plus information rows, in the files. The lowest safety factors against yield:

| Part | Factor | On |
|---|---:|---|
| **Side rail 60 x 60 x 4 at the bolt holes** | **1.99** | kerb at 0.8 m/s on the stiffest tyre allowed. This is under my own 2.0 line by a hair. The 11 mm holes for M10 cost about 3 %; the rest is a higher wheel load in this run (4,886 N) than in the revision 4 run (4,069 N). On the largest of your own load cases, the pothole at 0.5 m/s, it is 2.33. |
| Drive / motor plate | 2.14 | 1.0 kN sideways at the ground (your figure); 2.57 on my largest, 831 N |
| Carriage plate strip, aluminium | 2.17 | largest comb load |
| Actuator holding (8.8 kN) | 2.28 | largest lift shock |
| Mast-base cross-member | 2.32 | actuator stalled against a stop at 9.5 kN |
| Rail screws M4 | 2.32 | largest comb load |
| **Nose cross-member, now 60 x 60 x 4** | **2.45** | strut pull plus three times the standing castor load (1.55 as 50 x 50 x 4) |
| Mast upright at the strut pin | 2.55 | largest comb load |

Corner joints (your M-3). Demand on the pair of bolts through the cross-member, 45 mm apart, from the 831 N sideways tyre force acting 0.49 m away: 9.0 kN per bolt (9.8 kN with your 443 N m). Slip resistance of an M10 8.8 at 49 N m, two friction faces, partial factor 1.25:

| Contact faces | Slip resistance per bolt | Against 9.0 kN |
|---|---:|---|
| Painted (0.2) | 7.8 kN | slips |
| Bare, wire-brushed (0.3) | 11.8 kN | holds, factor 1.30 (1.20 against your figure) |
| Blasted (0.5) | 19.6 kN | holds, factor 2.17 |

So the joint holds only if the contact faces are left bare, which sheet 17 now says. With a joint that does not slip, the rail's fatigue check stands as before: a stress range of 44 MPa against 67 MPa allowed, on an ASSUMED load history.

### 3.6 The lane, start to finish

Lane as it would be made good (step ramped, trench covered, pothole filled):

| Run | Result |
|---|---|
| Full 240 L bin, home to pad | pass, 30.8 minutes, 16.7 Wh |
| The same at night, 10 % heavier, load off-centre, 20 % less grip | pass |
| Full 140 L bin, home to pad | pass |
| Empty return; collecting an empty bin and bringing it home | pass, 33.6 and 34.8 Wh |
| 12 % pitch down and up with a full bin on wet leaves (B2-F's figure, grip 0.35), stop and hold | pass |
| Person steps in on the wet pitch; dog runs across | pass: stops, waits, carries on |

Speed against the rule in these runs: the robot reaches the 12 % pitch at 0.22 m/s and stays under 0.23 m/s on it (rule 0.2); on 6 to 9 % slopes it peaks at 0.32 m/s (rule 0.3). The one place it runs over is the ramp at the old step, where it reaches 0.44 to 0.47 m/s for a moment against 0.4.

Lane as it is today:

| Feature | Result |
|---|---|
| 40 mm sharp step, going down | passes, but the robot reaches 0.65 m/s as it drops off the edge (0.70 in revision 4) |
| 40 mm sharp step, going up | **stalls** |
| 60 mm pothole under one wheel | **stalls** in it; least hedge clearance 89 mm (5.6 mm in your revision 4 run) |
| 40 x 200 mm trench | **stalls** |

Nothing in revision 5 changes this: at 60 N m the robot cannot climb these, and it should not be asked to. The lane has to be made good first: every edge over 15 mm ramped (3.4), the pothole filled, the trench covered.

### 3.7 Driving software: 60 missions, twice

The same 20 scenarios and three seeds as your run, on ArduRover 4.7.2, with the revision 5 robot (180 kg, 1.74 m long) and the revision 5 speed rule.

**First pass.** Revision 5 as I first wrote it: camera as second source for the left edge, bye-law as two windows, measured trip time, 0.1 m/s reverse. Score on your script: 48 of 60. Three of the misses were new faults, and I have kept the whole run in the files:

| Mission | What happened | Cause |
|---|---|---|
| Three-bin evening, seed 7, third trip | 1 mm from the right hedge at the bend at 73 to 77 m | **Mostly mine.** The satellite fix was in Float for 30 s before the bend and the position was 1.1 m out; the robot was holding the middle on its hedge readings, as designed. At the bend the far hedge crosses the view ahead. My camera model returned it as a left edge 0.4 to 1.0 m away, B2-F's lidar reading did the same at some moments, and my rule took the nearer of the two. The robot steered right, into the outside of the bend. The B2-F guard for the right hedge has its sign reversed and did not help. The hedge is on the map, so the obstacle check ignored it. |
| Three-bin evening, seed 23 | Turned 134 degrees on the spot during a 40 s wait at the last pad; bin set down 10.8 degrees off; 93 mm from the hedge driving away; 15 to 25 % more energy on every trip | Two things. The stop command in the B2-F companion is "hold the heading you have now", re-sent ten times a second, so a stopped robot can creep round. And the steering hunted all evening (turn-rate scatter 0.13 to 0.21 rad/s against 0.04 to 0.05 in the other missions), which also made the pad look occupied. The hunting is gone with the second-pass edge readings (0.04 to 0.06 on the same seed); I did not isolate which of the changes cured it. |
| Three-bin pick-up day, seed 7 | False "bin tipped" alarm at the first bin; evening abandoned | The B2-F outline check merges 15 lidar scans in map coordinates while the heading estimate wobbles by a degree or two: a 0.58 m bin measured 0.89 m wide. |

**Second pass.** What I changed in the companion (all behind one switch, so the first pass can be re-run):

- Camera model: follows the left boundary only. Lidar hedge faces: returns in the 20-degree cone straight ahead are not side faces; the far face is looked for out to 4.5 m, so it is not lost when keeping left.
- Disagreement over 0.25 m: take the reading that fits the lane width with the other hedge; if the other hedge is out of view, the nearer one.
- Side guard with the right sign: never plan closer than 0.35 m to the right hedge or 0.20 m to the left.
- **Protective field**, independent of map and position: any lidar return in the robot's own path within 0.6 m of the nose, or within 80 mm of its sides: stop, back out 0.8 m, start again; three times in two minutes: hold and alert.
- The heading command in the lane may change at 0.15 rad/s at most. Pivot turns are commanded at 0.13 rad/s with a gentle start and finish, and a path now begins with such a pivot instead of a heading step. The last reverse onto the bin is held to 0.1 m/s.
- A stopped robot holds the heading it stopped at.
- Bin outline: measured scan by scan, median of 15.
- Added after the 60 missions, for the reason given below: a camera person check.

The 60 missions again on that code:

| | First pass | Second pass |
|---|---:|---:|
| Score on your script, as it stands | 48 of 60 | 48 of 60 |
| With the time window and energy budget restated (below) | 55 of 60 | 57 of 60 |
| Least hedge clearance in any mission | 0.001 m | 0.196 m |
| Missions under your 0.124 m limit | 2 | 0 |
| Largest set-down error; largest handle angle | 72 mm; 10.8 degrees | 64 mm; 1.2 degrees |
| Turning on the spot while waiting | 134 degrees | none |
| False alarms | 1 | 0 |
| Energy per trip | 70 to 88 Wh | 69 to 72 Wh |
| Nose corner speed in turns on the spot, peak | 1.0 to 1.2 m/s | 0.30 to 0.57 m/s |
| Protective stops | not fitted | 0 in 60 missions |

The 12 misses on your script are the 12 full missions, and all of one kind. Every trip uses 69 to 72 Wh against your 50 Wh (C6). The three three-bin evenings finish at 21:17 to 21:18, after your 21:00 (C3). The three pick-up days are refused their third trip on your 18:00 clock (C7). None of the 48 fault and alert scenarios misses. With the window read as the bye-law has it and the energy limit at revision 5's own 75 Wh, 57 of 60 pass, and the other three are those pick-up days (see Windows and energy below). Lidar and camera both gave an edge reading in 86 % of the control cycles, the camera alone in 0.6 %, neither in 3.7 %; they differed by more than 0.25 m in 5.0 %, and in those the lidar's reading was kept 99 times in 100. All 24 pre-grab gates were inside on the camera and in truth, all 21 seating checks passed, and no bin was refused.

**A person standing in the path.** Your person scenario no longer tests a stop. At revision 5 speeds the person and the dog have crossed before the robot is within 1.5 m (closest 1.6 to 2.2 m in every seed, in my revision 4 run as well). So I made the person stand still on the robot's line. That found a hole in the lidar stop logic inherited from B2-F: while the satellite fix is degraded its map filter ignores everything within 1.2 m of a hedge line, and it never stops for anything more than 0.20 m from the robot's side. The cure is the second sensor Brian asked for: a camera person check (a model, with the ASSUMED rates of 1.1) slows the robot at 4 m and stops it at 1.5 m for a person or dog within 0.5 m of its sides, whatever the map and the fix say.

| Test, three seeds each | Lidar logic alone | With the camera person check |
|---|---|---|
| Person stands on the robot's line for 60 s | stops in 2 of 3; in the third it **passes at 0.16 m without stopping** | stops in 3 of 3, never closer than 1.40 m, carries on when the person leaves |
| Person steps out 3.5 m ahead and stands for 60 s | closest 0.91, 0.50 and **0.11 m** | stops in 3 of 3; closest 0.96, 0.77 and 1.13 m |
| Person stands for 200 s | one waits and alerts; one makes three protective stops and holds 0.44 m away; one **passes at 0.17 m** | 3 of 3 stop 1.4 m or more away and alert "path blocked" after 120 s |

The camera check does nothing unless a person or dog is in the scenario, so I re-ran the three person missions and these tests on it and did not re-run the other 57. I tried two lidar-only cures first (a wider stop corridor, and treating only long lines of returns as hedge); neither worked, because the 1.2 m map filter is what hides the person. That filter is there to stop false alarms from hedges when the position is poor, and I have left it alone.

**Do the guards work? Faults put in on purpose.** A 90 m stretch of lane with a full bin, keeping left 0.42 m from the hedge; at 300 m a fault is switched on:

| Fault | Outcome | Protective stops | Least hedge clearance | The same on the first version of the second pass |
|---|---|---:|---:|---|
| no fault | completed | 0 | 0.368 m | 0.373 m, 0 protective stops |
| steering forced 20 degrees toward the near (left) hedge for 8 s | completed | 1 | 0.128 m | 0.006 m, 0 protective stops |
| the same for 90 s | held and alerted ("path blocked") | 3 | 0.143 m | 0.004 m, 3 protective stops |
| steering forced 20 degrees toward the far hedge for 40 s | completed | 2 | 0.200 m | 0.120 m, 2 protective stops |
| camera reading stuck at 0.5 m for 30 s (true 0.9 m) | completed | 0 | 0.369 m | 0.381 m, 0 protective stops |
| camera reading stuck at 2.5 m for 30 s | completed | 0 | 0.372 m | 0.375 m, 0 protective stops |
| lidar left-face reading 0.8 m too far for 30 s | completed | 0 | 0.359 m | 0.035 m, 1 protective stop |
| lidar left-face reading 0.5 m too near for 30 s | completed | 0 | 0.365 m | 0.376 m, 0 protective stops |

The steering faults are the test of the protective field: with a forced turn toward a hedge, the robot stops with 0.13 m or more to spare, backs out and carries on, or holds and calls after the third time. Before I limited how fast the heading command can change, the same fault swung the nose corner to 4 mm from the hedge in under a second, before any check could act; that test is in the files too.

**The bend, on purpose.** I could not reproduce the 1 mm event exactly: it needs a particular Float error at a particular place. Two attempts:

1. *A position fault put in on purpose.* Float quality with a 1.8 m position bias for the 30 s before the bend, in eight directions. The position estimate goes 1.0 to 1.2 m out, as in the event. Both versions of the software get round every time, never closer to the hedge than where they started. The second pass strays 0.81 to 0.86 m from the centre line at most (first pass 0.97 to 1.02 m) and turns at 0.15 rad/s at most (first pass up to 0.29).
2. *The bend under the tree-cover satellite model, 40 seeds,* 70 m of lane with a full bin:

| Software | Runs | Completed | Runs with the position more than 0.5 m out near the bend | Largest position error | Least hedge clearance in any run | Furthest off the centre line at the bend | Protective stops |
|---|---:|---:|---:|---:|---:|---:|---:|
| first pass | 40 | 40 | 31 | 1.27 m | 0.353 m | 1.02 m | 0 |
| second pass | 40 | 40 | 30 | 1.27 m | 0.391 m | 0.86 m | 0 |

So these two tests do not prove the event is cured: the first-pass software gets through them too. They show the second pass is steadier at the bend. The cure rests on the cause found in the trace, on the injected faults above, and on re-running the same missions.

**Windows and energy.** Drop-offs start at 18:00 and three bins are out by 21:18 (quiet-hours limit 22:30). On your scenario clock the pick-ups start at 18:00, so the third is refused as too late for 21:00, correctly. Started at 16:30: two seeds, both bring all three bins home by 19:57 with 43 % left in the battery. A trip takes 63 to 70 minutes and 69 to 72 Wh; three trips leave 43 % in the battery. Your script's limit of 50 Wh a trip was set for B2-F's 0.45 m/s; revision 5 is slower and heavier, and its own budget is 75 Wh, checked before each trip.

**Other runs.** Robot 10 % heavier (198 kg), one drop-off: completed, 73.6 Wh (inside the 75 Wh budget, with little to spare), least hedge clearance 0.203 m. Lidar hedge reading switched off, camera only, one drop-off: completed in 63.8 minutes on 70.9 Wh, least hedge clearance 0.198 m; the camera gave an edge reading in 86 % of the control cycles.

**Still idealised in these runs:** the final reverse onto the bin is partly steered on true positions; heading noise is mild; camera frames are treated as independent; the bin's weight is taken as known; the rear lidar and rear camera are not modelled at all, so backing out after a protective stop relies on having just driven over that ground. The camera's left-edge reading is a model (the true edge plus 40 mm of noise, one frame in ten missing), not an image pipeline.

## 4. What changed in the design

- **Nose:** soft foam nose, 200 mm deep, across the full width, with switch strips on the front and both sides; aluminium carrier. The certified bumper, its steel beam and control unit are gone. The robot is 1,736 mm long, 95 mm shorter than revision 4.
- **Sensors:** front lidar moved down to the nose (scan plane 0.30 m); a second lidar on the left leg tip for the rear; front camera used for people and for the left edge; two ToF sensors under the bin in place of the light beams.
- **Frame:** nose cross-member 60 x 60 x 4; corner joints 4 x M10 per plate pair with bare contact faces and locking nuts.
- **Lift:** top stop blocks 5 mm higher, top switches 7 mm higher; tie bolts in steel inserts; actuator bought used.
- **Software, lane simulation:** tail-first descent; speed rule looks 3 m ahead; rear obstacle watch when backing.
- **Software, missions:** camera as second source for the left edge and as a person check; a protective field that stops for anything in the path; guards on both hedges; slow pivots and a limit on how fast the heading may change; a stopped robot holds its heading; bye-law as two windows with the measured trip time; reverse moves at 0.1 m/s; bin outline measured scan by scan; a fence trip during a no-fix hold reported correctly.
- **Not changed:** drive units, battery, 60 N m limit, comb, pad, castor beam, mast, rails.

Weight: **180.0 kg** (177.6 before). The lighter nose saves 2.4 kg; the 60 x 60 nose member, the M10 joints with their larger corner plates and the review's crush-tube correction add 5.6 kg; the review's actuator correction takes off 0.75 kg.

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
4. **Quiet-hours limit.** I assumed drop-offs may run until 22:30. Three bins from 18:00 finish at about 21:18.
5. **When does the collection crew pass?** Pick-ups should start as soon as the bins are emptied; three take about 3 hours 30 minutes, so they must start by 17:30 to be done by 21:00.
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
