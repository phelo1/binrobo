## 4. Trip time

### 4.1 Why it was slow

- The lane is 635 m, so a round trip is 1,270 m of lane plus the yard work at each end.
- The B2-F drive (4,600 rpm motor, 32:1 gearbox, 3.5:1 chain, 330 mm wheel) turns the wheel at 0.71 m/s flat out. B2-F capped the lane speed at 0.5 m/s.
- I then held it to 0.4 m/s on the level and 0.15 to 0.3 m/s down the hill. Those are the speeds at which a touch on the soft nose stops the robot inside the foam. I call them the touch-safe speeds.
- 1,270 m at 0.4 m/s is 53 minutes before the hill, the yard and any stop.

### 4.2 The fast cruise

Two speed tables now. The touch-safe table is unchanged. The fast table applies only while all of these hold:

- the robot is in the lane proper: more than 30 m from the house and 20 m from the road end;
- the lidars show both hedge faces (so not at a gateway or a gap in the hedge) and the robot is more than 0.25 m from them;
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
- **Torque.** The taller gearing gives less push for the same motor current. The controller's current limit goes from about 15 A to 26 A to keep the same wheel torque as before (60 N m); the controller on the parts list is a 30 A unit. Full bin up the steepest part at 1.0 m/s would need 0.59 N m from each motor, which is inside the rating as I read it. The motor curve is ASSUMED: I have no data sheet. In practice the robot never climbs with a full bin.
- **Brakes.** The spring brakes sit on the motors, so the same change cuts their torque at the wheel from 60 to 34 N m. Every stop and hold test in this note uses 34.
- **Firmware.** The same command now turns the wheels 1.55 times faster, so the speed and turn loops are reset (section 4.6).

Why not faster than 1.0 m/s: the stop distance grows with the square of the speed, the lift load on a kerb strike reaches 4,628 N at 1.2 m/s (4,070 N at 1.0), and the people tests below are already at their limit at 1.0.

### 4.4 Results

⟦TRIPS⟧

### 4.5 Stopping from the fast cruise

MuJoCo, robot 180 kg, full bin 110 kg, brake torque 34 N m a wheel, brakes on 0.15 s after the trigger. Distance from the trigger to standstill, in metres. Table: `tables/pstop_speed_r6.txt` (⟦NPSTOP⟧ runs).

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

- The foam gives 150 mm. Every figure here is two to four times that. At the fast cruise a touch on the nose is a push of 0.3 to 0.7 m, not a stop inside the foam.
- The stand-still zone is 3 m, and the robot looks 10 m ahead at 1.0 m/s. So the fast cruise is safe for anyone the sensors find in time, and not for someone they miss. That is the trade.
- The empty robot on wet leaves is again the weak case: 0.61 m at 8.5 % and no stop at all at 10 %. Hence the leaf-season table and switch.
- The touch-safe table of revision 5.1 still holds with the weaker brakes: 63 to 141 mm at its own speeds, wet and on wet leaves, up to 8.5 % (and 1.1 m sliding for the empty robot at 10 % on leaves, as before).

Other physics at speed:

- **Kerb.** A 40 mm kerb struck at 1.0 m/s with a full bin loads the drive wheel with 4,520 N and the lift with 4,070 N. At 0.8 m/s it was 4,886 N and 3,858 N, so the frame checks of revision 5 stand. The actuator's holding factor falls from 2.28 to 2.16. The bin stays on the comb. A rigid wheel with no give in the tyre would see 6,214 N at 1.0 m/s: fit pneumatic or soft tyres, as drawn.
- **Whole lane.** On the lane model with the real slope, made good as in revision 5: full bin down (P1, and P7 heavier at night), empty up and back (P2a, P2c), and the stop-and-hold tests on the steepest part (P4a, P4b) all pass at the fast speeds, on grip 0.35 and again on 0.22. Lane time 741 to 878 s against 1,745 to 1,818 s. The bin stays seated; the hold creeps 1.6 to 1.7 mm with no overrun. The speed trace peaks at 1.2 m/s for an instant as the wheels drop into the 60 mm pothole at 290 m. Table: `tables/lane_fast_r6.txt` (16 runs).

### 4.6 Turning on the spot

⟦PIVOT⟧
