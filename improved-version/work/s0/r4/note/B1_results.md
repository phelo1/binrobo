### 3.1 Weight: 177.6 kg

Built from the drawn solids, as in revision 3, and matched by the simulator model.

| Group | Revision 3, kg | Revision 4, kg |
|---|---:|---:|
| Frame, mast, guards, covers | 74.0 | 90.1 |
| Bought-in units | 40.4 | 43.4 |
| Allowances (bolts, power box, paint) | 4.7 | 10.7 |
| Castor beam | 6.0 | 6.0 |
| Lift carriage | 27.1 | 27.4 |
| **Total** | **152.2** | **177.6** |

Where the 25.4 kg comes from (rounded):

| Change | kg |
|---|---:|
| Bolts and crush tubes of the bolted joints (66 bolts, counted joint by joint) | +5.0 |
| Bolted corner plates, cleats and mast struts in place of welded plates and shoes | +5.5 |
| Safety bumper and its carrier, less the old bar | +4.5 |
| Rails 60 x 60 x 4 | +3.4 |
| Actuator (6.5 kg ASSUMED, against 3.5) | +3.0 |
| Thicker motor plates | +1.7 |
| Stop blocks, extra switches, light beams, larger power box | +2.3 |

About 10 kg is the price of bolting everything, 4.5 kg the price of the bumper, and the rest answers the strength findings. The table still carries the inherited rows of the B2-F table unchanged (drive units 2 x 9.68 kg, battery 5.05 kg). Your audit puts the drive units 2 to 8 kg higher, so a weighed prototype could come out at 180 to 186 kg.

What the weight does: 55 % of the empty robot's weight is now on the two castors, which are neither driven nor braked. That shows up twice below: in braking (3.3) and at steps (3.5).

### 3.3 Stopping for a person

I ran 159 stops: the robot drives at a set speed, the bumper is touched, and after 0.15 s (ASSUMED: safety relay, contactors, brakes) both contactors open and the spring brakes apply. The figure is the distance from the touch to standstill, in mm, at 177.6 kg on a wet surface (grip 0.30). The bin stayed on the comb in every loaded run.

| Downhill slope | Full bin: 0.2 | 0.3 | 0.4 | 0.5 m/s | Empty: 0.2 | 0.3 | 0.4 | 0.5 m/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| level | 39 | 69 | 105 | 146 | 48 | 79 | 122 | 175 |
| 3 % | 45 | 82 | 121 | 167 | 56 | 93 | 146 | 208 |
| 6 % | 51 | 95 | 140 | 196 | 66 | 124 | 190 | 279 |
| 9 % | 65 | 121 | 175 | 248 | 95 | 188 | 295 | 439 |
| 12 % | 94 | 161 | 248 | 360 | 389 | 788 | 1,335 | 1,911 |

The empty robot is the worse case, the opposite of what one expects, because only the drive wheels brake and without a bin they carry under half the weight. On the 12 % pitch it needs 289 mm even from 0.15 m/s.

Other cases:

- Reaction time 0.10 / 0.20 s instead of 0.15: full bin, level, 0.5 m/s: 122 / 171 mm.
- Robot 10 % heavier (195 kg): empty, level, 0.4 m/s: 124 mm (122 at 177.6 kg).
- Empty, tail first (drive wheels downhill): 12 % wet: 71 mm from 0.2 m/s, 122 mm from 0.3 m/s.
- Brakes on the castors as well (30 N m each, an option I simulated but did not design): 12 % wet from 0.5 m/s: 167 mm empty, 166 mm with a full bin. Up to 6 %: at most 140 mm from 0.5 m/s.
- Wet leaves (grip 0.22), full bin: 6 %: 114 mm from 0.3 m/s; 12 %: 277 mm from 0.2 m/s. Empty on 12 %: it does not stop at all.

**The speed rule in revision 4.** I assumed the bumper still has 150 mm of travel after it switches (half its depth; the maker must confirm) and set the speeds so that the simulated stop stays under 125 mm:

| Slope | Full bin | Empty, or empty bin |
|---|---|---|
| level or uphill | 0.4 m/s | 0.4 m/s |
| downhill, up to 3 % | 0.4 m/s | 0.3 m/s |
| downhill, 3 to 9 % | 0.3 m/s | 0.2 m/s |
| downhill, steeper than 9 % | 0.2 m/s | tail first, 0.2 m/s |

The longest simulated stop under this rule is 122 mm. Two things are not solved by it:

- **Tail-first travel is not in the driving software.** The lane and mission runs drive the empty robot nose first at 0.15 m/s on the steep pitch, which does not meet the rule. (In the lane model the 12 % pitch is itself an assumption: the map data gives 7.9 % at most.)
- **The rule costs time.** A trip now takes 62 to 72 minutes instead of about 56, and the third bin of an evening no longer fits before 21:00 (3.8).

### 3.4 Lowering the bin

The firmware knows the lift height at which the bin left the ground at the pick-up. On the way down, while the bin is still more than 15 mm above that height, it watches the load on the lift. If the load falls by more than 80 N (or 10 % of the bin's weight), something is under the bin: it stops and raises 30 mm.

| Case (block under one bin wheel unless stated) | Lowering at 6 mm/s | at 13 mm/s |
|---|---|---|
| No block, 110 / 60 / 25 kg bin | normal set-down, no false stop | same |
| 25 mm block, 110 kg | stopped, block carried 109 N | stopped, 158 N |
| 40 mm block, 110 kg | stopped, 107 N | stopped, 130 N |
| 60 mm block, 110 kg | stopped, 109 N | stopped, 122 N |
| 60 mm block, 60 kg / 25 kg bin | stopped, 83 / 81 N | stopped, 86 / 86 N |
| 60 mm bar under both wheels, 110 kg | stopped, 109 N | stopped, 122 N |
| 15 mm block, 110 kg | **not seen**: 859 N | **not seen**: 865 N |
| 60 mm block, guard switched off | 907 N | - |

Limits: the guard does not see anything thinner than about 20 mm. Two light beams cross under the bin 40 mm above the ground and block lowering while either is broken; they see a foot but not a flat hand. The guard is firmware, not a rated safety function. The lift driver limits the current to 3 A on the way down (about 0.5 kN of push, to be set on the bench) so the comb and pad arm cannot press hard by themselves.

### 3.5 Steps, castors and drive torque

This is where I have to correct my own revision 3 position.

**The 40 mm sharp step, full bin, met square on.** P = over, S = stalled. Columns: width of the castor's contact strip in the model.

| Speed | Edge ahead | Torque | 16 | 24 | 32 | 36 | 40 | 44 | 50 mm |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 m/s | 1.6 m (your test) | 60 N m | P | P | S | S | S | P | P |
| 0.5 m/s | 3.0 m (castors trailing) | 60 N m | S | S | S | S | S | P | S |
| 0.5 m/s | either | boost to 100 N m | P | P | P | P | P | P | P |
| 0.4 m/s | either | 60, or boost to 100 | | S | | | | | |
| 0.3 m/s | either | 60, or boost to 100 | | S | | | | | |

With the castors pointing the right way, revision 4 does not get over the sharp step at 60 N m even at 0.5 m/s. A short boost to 100 N m gets it over at 0.5 m/s, but not at the 0.4 m/s the speed rule now allows: the castors climb and then the drive wheels stall on the edge.

The reason is simple arithmetic. To lift itself square on to a 40 mm edge without a run-up, a 330 mm drive wheel carrying 1,160 N (full bin) needs about 125 N m. The robot has 60. It only ever crossed that step on momentum at 0.5 m/s.

**What does work at 60 N m and 0.3 to 0.4 m/s:**

| | Square on | Edge met at an angle |
|---|---|---|
| Full bin | 25 mm (30 mm at 0.4 m/s only) | 40 mm, at 10, 20 and 30 degrees, at 0.2 to 0.4 m/s |
| Empty robot | 20 mm | 30 mm at 20 degrees; 40 mm only where one side meets the edge at a time |

The empty robot is the weak case again: 963 N sits on the castors and the lightly loaded drive wheels cannot push them up a 40 mm edge (they would need about 1,280 N of push and have about 470 N of grip in the dry). The boost does not help there.

**So I withdraw the request to raise the torque limit.** 60 N m stays. The boost is not adopted: it does not solve the step at safe speed, and 100 N m on both wheels draws about 70 A by the motor figures in your M-8, above the 60 A battery protection. The runs with the boost are in the files as information.

**What follows for the lane:** an edge of more than about 20 mm across the full width has to be ramped, or crossed at an angle with a full bin. This applies to any robot of this layout (two driven wheels at the back, two castors at the front), so I ask the B2-F author whether B2-F was ever run empty over the sharp step (section 9).

**Castor tyre width and the slippery hill start** (grip 0.22, bin weight 60 mm off-centre), revision 4:

| Contact strip, mm | 16 | 24 | 32 | 36 | 40 | 44 | 50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Heading swing, degrees | 2.6 | 1.3 | 1.8 | 2.3 | 1.5 | 2.0 | 13.3 |
| Least castor load, raw, N | 422 | 81 | 63 | 62 | 32 | 67 | 0 |
| Least castor load, 100 ms average, N | 569 | 525 | 540 | 536 | 549 | 546 | 491 |

All reached the top. Only the full-width 50 mm model swings off course. The raw load dips under 50 N for an instant at 40 and 50 mm; the 100 ms average never falls under 490 N. I report both, as you asked.
