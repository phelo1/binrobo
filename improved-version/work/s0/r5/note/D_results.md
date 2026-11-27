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

