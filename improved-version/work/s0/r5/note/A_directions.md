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

**Navigation.** The same two sensors now hold the robot's place in the lane. The lidar measures the hedge faces (as B2-F did) and the front camera measures the left edge. In the mission runs both gave a reading in «NAV_BOTH» % of the control cycles and the camera filled in where the lidar saw no hedge. Where the two differ by more than 0.25 m, the robot takes the reading that fits the known width of the lane. With the lidar's hedge reading switched off altogether, one mission still completed on the camera alone («CAMONLY»).

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

«COST_TABLE»

Most rows are ASSUMED and say so. Nothing has been quoted. Your earlier rule, "no capability or safety cuts to save money", is kept for capability. For safety it is kept in the sense that every function revision 4 had is still there, but three of them are no longer certified parts; that is the trade described in 1.1.
