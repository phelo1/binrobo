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

