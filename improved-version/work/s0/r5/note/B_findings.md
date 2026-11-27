## 2. The three reports, finding by finding

This section is for the B2-F author's side: "you" here means the reviewer. All three reports reproduce my revision 4 numbers and I accept their criticisms. Two of them go to how I summarised: the "122 mm longest stop" headline counted the empty robot as tail first when tail-first driving did not exist, and I presented castor brakes as a fix when my own odd result (0.72 m on wet leaves) said they were not. Both were too favourable. The castor-brake recommendation is withdrawn.

### Cold-eye review

| Finding | Revision 5 |
|---|---|
| **B-1** Empty robot cannot hold or stop nose first on a wet 12 % pitch; the standstill monitor cannot see a slide | **Tail first is now built and tested in the lane simulation** (3.2). Tail first, the empty robot stops in 71 mm from 0.2 m/s on the wet pitch and in 171 mm on wet leaves, where nose first it does not stop at all. The rear gets a lidar and a camera (drawn and costed, not yet simulated). Slide: the watchdog is to compare wheel speed with ground speed (satellite and lidar motion, optionally an optical sensor under the frame), so that a slide with locked wheels is seen; that is designed and costed, not simulated. I did not put a sensor on a castor wheel: the castor swivels freely and a cable would wind up. Still open: tail first is not in the mission software, and the real pitch is unmeasured. |
| **B-2** Person protection partial: corners, pivot turns, reversing | Soft nose over the full 936 mm width with switch strips on the front and both side faces. Pivot turns are slowed and every reverse move is commanded at 0.1 m/s, both now in the mission software («PIVOT_MEAS»). A lidar check of the turning circle for unmapped objects is not written; the circle is still checked against the map only. A protective field stops the robot for anything within 0.6 m of the nose, and a camera person check stops it for anyone within 0.5 m of its sides (3.7). And the main change: lidar and camera together watch forward and to the sides, and a second pair is drawn for the rear (1.1). None of it is safety-rated; the slope speed rule is still ordinary software. |
| **M-1** Under-bin beams blocked by the bin's own wheels; guard tied to the pick-up ground | The beams are gone. A ToF sensor behind each leg guard looks down at the spot where the bin wheel will land. It reads the bare ground when the robot arrives and blocks lowering if a later reading is 10 mm short. That also gives the load guard the local ground, as you asked. Simulated (3.3). The guard's forces at 6 mm/s are 108 N at most, under the 125 N foot figure you quote (135 N if the robot is 10 % heavier); at 13 mm/s they are 143 to 147 N, so the last 100 mm are lowered at 6 mm/s. |
| **M-2** Speed rule rests on grip, slope and bumper figures the robot cannot know | Partly answered. The rule now looks 3 m ahead, so the robot is already slow at the brow (your tester's 938 mm case). Slide detection is designed, not simulated (B-1). Grip is still not measured before a descent; a brake check on the first metre of a pitch is the obvious next step and is not written. The soft nose switches at the first touch (a ribbon switch on its face), so there is no switching travel to add; its 150 mm of give is still an assumption. |
| **M-3** Bolted corner joints slip; fatigue detail falls to about 50 | Agreed. Joints are now 4 x M10 8.8 per plate pair (2 through the rail 60 mm apart, 2 through the cross-member 45 mm apart), contact faces bare and wire-brushed, prevailing-torque nuts, re-torque after the first ten trips. Slip check: «SLIP». Fatigue with a slip-resistant joint: «FAT». |
| **M-4** Lift stop order not robust at the top | Top blocks are now reached at +340 mm and the top switch bodies at +346 (sweep: 340.5 and 346). The actuator's own stop, at +331 to +335 with the stroke tolerance you give, is 5 mm or more inside the blocks. |
| **M-5** Bye-law window misread | Agreed, and thank you for tracing it to the inherited code. The companion now has two windows and uses the measured trip time (3.7). My "castor brakes to get the third bin back" argument is withdrawn. |
| **M-6** Cost understated | Agreed; I used your figures for revision 4. Revision 5 costs in 1.3. |
| **M-7** Only low edges can be climbed from a standstill | Tested (3.4): empty, from a standstill with the castors at the edge, 15 mm is climbed and 20 mm is not. The lane condition is now "every edge over 15 mm is ramped". |
| m-1 Nose cross-member | Drawn as 60 x 60 x 4. Safety factor «NOSE_SF». |
| m-2 Mass rows | Actuator 5.75 kg, crush tubes 0.054 kg each: both in the table. |
| m-3 Top tie bolt in aluminium | Steel thread inserts in the blocks. Locking nuts and a re-torque note are on sheet 17. |
| m-4 Lift current limits in the cold | Noted on sheet 17: set both on the bench at 0 C. |
| m-5 Bumper height, kerbs, brambles | Unchanged height (115 to 265 mm). Nuisance stops from brambles are likely and are the price of a low soft nose. |
| m-6 Length and pivot circle | Now 1,736 mm long (1,831 before); pivot circle «PIVOT» m. |
| m-7 Castor brakes | Withdrawn (see above). |
| m-8 PL estimate | Withdrawn for the people functions: they are not rated in revision 5. |
| m-9 Clash results | Same check on revision 5: 15 inherited pairs, none involving a part I drew. |

### Mechanical re-test

| Finding | Revision 5 |
|---|---|
| Tail first is assumed, not built | Built in the lane simulation and tested on the pitch (3.2). Not in the mission software. |
| Slope transitions are not in the map: 938 mm at the brow | The speed rule looks 3 m ahead. In the lane runs the robot «BROW». |
| Castor brakes do not fix wet leaves | Agreed. Withdrawn. |
| The lowering guard does not see 20 mm | With the window referenced to the ground and the margin cut from 15 to 8 mm, the guard sees 20 mm in every case I ran (6 and 13 mm/s, 110 and 25 kg, one wheel and both). 15 mm is seen in two cases of three. The ToF sensors see 10 mm, if the object is there before lowering starts (3.3). |
| Open pothole: hedge clearance 5.6 mm | «POTHOLE» |
| Sharp drop: 0.70 m/s over the edge | «DROP» |
| Empty 40 mm step fails on B2-F too | Noted, thank you: it is the layout. |

### Driving-software re-test

| Finding | Revision 5 |
|---|---|
| 47 of 60; six "too late", one hedge 0.098 m, one wrong alarm | «SITL_SCORE» |
| Trip-start check assumes 50 minutes | Uses the longest trip measured so far that evening plus 5 %, and 78 minutes before any has been measured. |
| Bye-law as two windows | Done: drop-offs from 18:00 with only a quiet-hours limit (22:30, my assumption, for Brian to confirm); pick-ups from 10:00 on collection day, home by 21:00. |
| No-fix hold and the firmware fence race | A fence trip during a no-fix hold is now reported as the no-fix hold it is. |
| Hedge clearance at the pad with the longer robot | The robot is 95 mm shorter. «PADA» |
| Final reverse still partly truth-based; yaw noise idealised; frames treated as independent; bin weight taken from truth | Not changed. These remain idealised sensor models. |
