### 3.2 Gate and pick-ups at 177.6 kg, 60 N m

| Gate test | Result |
|---|---|
| G1 pick-ups, three bin types | 90 of 90 held, none knocked over |
| G2 hill start on 12 %, grip 0.22 to 0.30 | pass; rolls back 33 to 35 mm |
| G3 40 mm step, your test | pass on one side and on both, but see 3.5: this is not a robust result |
| G4 emergency stop, 12 % downhill, wet, full bin, from 0.5 m/s | 0.281 m |
| G5 pivot turn | swept circle 3.00 m (limit 3.2) |
| G6 set-down and release, 18 cases | all pass |
| G7 time-step check | pass |
| G8 tipping | static poses pass; hand calculation 32.3 degrees (31.6 with the bin's weight 60 mm off-centre) |
| G9 weight under 120 kg | **fail: 177.6 kg** |

180 pick-ups with scattered start positions: 179 lifted, 1 refused safely, none lifted more than 50 mm off-centre (largest 29.5 mm). 28 needed more than one approach; one was set down and re-gripped by the seating check. All 24 stress cases pass (robot 10 % heavier and lighter, 15 % less grip, more rolling resistance).

### 3.6 Loads and structure

Largest loads in the revision 4 runs:

| Load | N | Case |
|---|---:|---|
| Drive wheel, carrying | 3,497 | emergency stop in reverse on 12 % |
| Drive wheel, your load cases with the compliant tyre | 4,754 | pothole at 0.8 m/s |
| Drive wheel, kerb at 0.8 m/s on a hard solid tyre (735 N/mm) | 4,069 | my run |
| Drive wheel, rigid-tyre model | 11,403 | sharp step at 0.8 m/s; information |
| Comb, carrying | 2,421 | |
| Comb, kerb at 0.5 / 0.8 m/s | 3,048 / 7,838 | rigid tyre |
| Lift, kerb at 0.5 / 0.8 m/s | 3,068 / 4,028 | lift cap raised so the shock is not clipped |
| Pad | 1,414 | |

The comb load at 0.8 m/s is nearly double the revision 3 figure (4.5 kN). The reason is the new actuator: the old one slipped at 3 kN, which cushioned the comb; a self-locking screw does not give. 0.8 m/s is twice the speed revision 4 is allowed, but I kept your load cases as the design basis.

Wheel load against tyre stiffness, kerb nose first:

| Tyre | Sinks under the standing load | 0.5 m/s | 0.8 m/s |
|---|---:|---:|---:|
| Rigid model | 0 | 9,350 N | 6,016 N |
| Hard solid tyre, 735 N/mm | 1.3 mm | 3,992 N | 4,069 N |
| 355 N/mm | 2.8 mm | 2,654 N | 3,557 N |
| 136 N/mm | 7.2 mm | 2,360 N | 3,342 N |

A real solid tyre is not rigid. Sheet 17 asks for a drive tyre no stiffer than 650 N/mm; the make and hardness of the wheel in the parts list would settle it (section 9).

Hand calculation on these loads: 68 rows, in the files. Safety factors against yield:

| Part | Factor | On |
|---|---:|---|
| Side rail 60 x 60 x 4, at the bolt holes | 2.10 | largest load-case wheel load |
| | 2.46 | kerb on the hard solid tyre |
| | 0.88 | rigid-tyre model (information) |
| Side rail, fatigue with bolted plates | range 44 MPa against 67 allowed | ASSUMED load history |
| Mast upright at the strut pin | 2.37 | largest comb load |
| Mast struts, pins, lug plates | 6.7 to 8.3 | same |
| Strut lug bolts / foot cleats (S355) | 3.02 / 2.98 | same |
| **Nose cross-member 50 x 50 x 4** | **1.55** | strut pull plus three times the standing castor load, together |
| Mast-base cross-member, base bracket, corner plates | 2.32 to 2.68 | actuator stalled against a stop at 9.5 kN |
| Lift stop blocks, bolts | 4.63 | same |
| Actuator holding (8.8 kN) | 2.18 | largest lift shock |
| Rail blocks / rail screws / carriage beams / plate | 2.66 / 2.15 / 2.48 / 2.02 | largest comb load |
| Castor pivot plates, castor beam | 3.2 to 4.8 | kerb strike; three times the standing load |
| Motor plate 8 mm | 2.37 | 904 N sideways, the largest in my runs |
| Bumper brackets | 7.3 and more | 1 kN side knock |

**One row is under 2.0: the nose cross-member, at 1.55.** It does not yield (229 MPa against 355), and at the robot's own top speed the factor is about 2.8, but it misses the standard I set myself. The fix is a 60 x 60 x 4 member, flush with the rails, which gives 2.32 and adds about 0.8 kg. It is noted on sheet 13 but not yet drawn or re-tested: I found it after the test campaign had run. The pad springs work at 768 MPa at full stroke against a 925 MPa limit, as designed.
