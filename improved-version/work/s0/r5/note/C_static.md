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
| 20 mm block, robot 10 % heavier | «LOWER_PM» | - |
| 25 mm block, 25 kg bin, trip level 50 N | stopped, 51 N | - |

So the guard now sees 20 mm in every case, which it did not in revision 4. At 6 mm/s the block carries 108 N at most at the nominal weight, and 135 N if the robot is 10 % heavier, which is over the 125 N figure. The last 100 mm are therefore lowered at 6 mm/s. Still not covered: something under 15 to 20 mm that slides in after the ToF check, and a real sensor's noise, which is not in the model (the type used reads to a few millimetres at this range; ASSUMED).

### 3.4 Edges

At 60 N m and 180 kg, a sharp edge across the full width:

| | From a standstill at the edge | With a 3 m run at 0.3 m/s | Met at 20 degrees |
|---|---|---|---|
| Empty robot | 15 mm (20 mm stalls) | 20 mm (25 mm stalls) | 30 mm |
| Full bin | 20 mm at least (castors at the edge) | 25 mm (30 mm at 0.4 m/s only) | 40 mm |

The lane condition is therefore: **every edge over 15 mm across the lane is ramped.** That replaces my revision 4 figure of 20 mm, which depended on a run-up, as the review said.

## 4. What changed in the design

- **Nose:** soft foam nose, 200 mm deep, across the full width, with switch strips on the front and both sides; aluminium carrier. The certified bumper, its steel beam and control unit are gone. The robot is 1,736 mm long, 95 mm shorter than revision 4.
- **Sensors:** front lidar moved down to the nose (scan plane 0.30 m); a second lidar on the left leg tip for the rear; front camera used for people and for the left edge; two ToF sensors under the bin in place of the light beams.
- **Frame:** nose cross-member 60 x 60 x 4; corner joints 4 x M10 per plate pair with bare contact faces and locking nuts.
- **Lift:** top stop blocks 5 mm higher, top switches 7 mm higher; tie bolts in steel inserts; actuator bought used.
- **Software, lane simulation:** tail-first descent; speed rule looks 3 m ahead; rear obstacle watch when backing.
- **Software, missions:** camera as second source for the left edge and as a person check; a protective field that stops for anything in the path; guards on both hedges; slow pivots and a limit on how fast the heading may change; a stopped robot holds its heading; bye-law as two windows with the measured trip time; reverse moves at 0.1 m/s; bin outline measured scan by scan; a fence trip during a no-fix hold reported correctly.
- **Not changed:** drive units, battery, 60 N m limit, comb, pad, castor beam, mast, rails.

Weight: **180.0 kg** (177.6 before). The lighter nose saves 2.4 kg; the 60 x 60 nose member, the M10 joints with their larger corner plates and the review's crush-tube correction add 5.6 kg; the review's actuator correction takes off 0.75 kg.
