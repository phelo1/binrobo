#!/usr/bin/env python3
"""Build fill_r5.json for the note from the result tables. Driving-software entries are filled when the runs exist."""
import json, os, sys, subprocess
sys.path.insert(0, '/home/claude/s0/r5/ana'); import sitl_stats as SS
O = '/home/claude/sitl_out'; T = '/home/claude/s0/r5/pack_tables'; F = {}
F['COST_TABLE'] = open(T + '/cost_r5.md').read().split('\n\n')[0].strip()
F['BROW'] = 'reaches the 12 % pitch at 0.22 m/s with a full bin and stays under 0.23 m/s on it (3.6). The empty descent is covered by the tail-first runs in 3.2.'
F['DROP'] = '0.65 m/s now. The speed rule cannot fix this: the robot is falling off an edge. The answer is the lane condition, every edge over 15 mm ramped.'
F['POTHOLE'] = 'It still stalls in the open pothole, now with 89 mm to the hedge. The pothole has to be filled.'
F['FAT'] = 'a stress range of 44 MPa against 67 MPa allowed (ASSUMED load history)'
F['SLIP'] = '9.0 kN demand per bolt against 11.8 kN with bare wire-brushed faces (factor 1.30; 1.20 against your 443 N m) and 7.8 kN with painted faces, which would slip. Table in 3.5'
F['NOSE_SF'] = '2.45 (you estimated 2.43)'
F['PIVOT'] = '2.81'
F['LOWER_PM'] = 'stopped, 135 N'
F['PIVOT_MEAS'] = 'measured in five missions: turning on the spot peaks at 0.21 to 0.40 rad/s, nose corner 0.30 to 0.57 m/s, against 0.7 to 0.9 rad/s and 1.0 to 1.2 m/s in the first pass; reverse peaks at 0.13 m/s against 0.18. The firmware still overshoots the rate it is asked for (0.13 rad/s), so its turn-rate loop needs tuning on the real robot'
F['BROW'] = F['BROW'].rstrip('.')
F['FAULT_TABLE'] = open(T + '/fault_tests_r5.md').read().strip() if os.path.exists(T + '/fault_tests_r5.md') else '«FAULT_TABLE»'

bt = open(T + '/bend40_r5.md').read().strip()
F['BEND_TABLE'] = ("1. *A position fault put in on purpose.* Float quality with a 1.8 m position bias for the 30 s before the bend, in eight directions. The position estimate goes 1.0 to 1.2 m out, as in the event. Both versions of the software get round every time, never closer to the hedge than where they started. The second pass strays 0.81 to 0.86 m from the centre line at most (first pass 0.97 to 1.02 m) and turns at 0.15 rad/s at most (first pass up to 0.29).\n"
                   "2. *The bend under the tree-cover satellite model, 40 seeds,* 70 m of lane with a full bin:\n\n" + bt + "\n\n"
                   "So these two tests do not prove the event is cured: the first-pass software gets through them too. They show the second pass is steadier at the bend. The cure rests on the cause found in the trace, on the injected faults above, and on re-running the same missions.")

F['NAV_BOTH'] = '86'
F['CAMONLY'] = 'least hedge clearance 0.20 m'
F['CAMONLY_LONG'] = 'completed in 63.8 minutes on 70.9 Wh, least hedge clearance 0.198 m; the camera gave an edge reading in 86 % of the control cycles'
F['M198'] = 'completed, 73.6 Wh (inside the 75 Wh budget, with little to spare), least hedge clearance 0.203 m'
F['DROP_END'] = '21:18'
F['TRIP_MIN'] = '63 to 70'
F['TRIP_WH'] = '69 to 72'
F['SOC3'] = '43'
F['THREE_H'] = '3 hours 30 minutes'
F['RET1630'] = 'two seeds, both bring all three bins home by 19:57 with 43 % left in the battery'
F['PADA'] = 'In the pick-up missions the least clearance is 0.22 to 0.24 m, and it is at the hedge bulge at 417 m, not at the pad.'
F['SITL_SCORE'] = ('First pass: 48 of 60, with three new faults (3.7). Second pass: 48 of 60 on your script and 57 of 60 with the time window and energy budget restated for revision 5. '
                   'No mission comes closer to a hedge than 0.196 m. The wrong alarm in s4c is gone: all three seeds end as the no-fix hold. "Too late" now happens only on the three pick-up days of your 18:00 clock.')
F['SUMMARY_SITL'] = ('In the second run no mission comes closer to a hedge than 0.20 m, and faults I put in on purpose are caught with 0.13 m or more to spare. '
                     'A further test, a person standing still in the robot\'s path, showed that the lidar logic inherited from B2-F can pass a person standing near a hedge at 0.16 m without stopping; '
                     'a camera person check now stops the robot at 1.4 m in every such run. On the reviewer\'s own scoring the count is 48 of 60, unchanged, because the 12 full missions miss energy and time limits set for the faster B2-F robot (3.7).')
F['SITL_SECOND'] = (
"The 60 missions again on that code:\n\n"
"| | First pass | Second pass |\n|---|---:|---:|\n"
"| Score on your script, as it stands | 48 of 60 | 48 of 60 |\n"
"| With the time window and energy budget restated (below) | 55 of 60 | 57 of 60 |\n"
"| Least hedge clearance in any mission | 0.001 m | 0.196 m |\n"
"| Missions under your 0.124 m limit | 2 | 0 |\n"
"| Largest set-down error; largest handle angle | 72 mm; 10.8 degrees | 64 mm; 1.2 degrees |\n"
"| Turning on the spot while waiting | 134 degrees | none |\n"
"| False alarms | 1 | 0 |\n"
"| Energy per trip | 70 to 88 Wh | 69 to 72 Wh |\n"
"| Nose corner speed in turns on the spot, peak | 1.0 to 1.2 m/s | 0.30 to 0.57 m/s |\n"
"| Protective stops | not fitted | 0 in 60 missions |\n\n"
"The 12 misses on your script are the 12 full missions, and all of one kind. Every trip uses 69 to 72 Wh against your 50 Wh (C6). The three three-bin evenings finish at 21:17 to 21:18, after your 21:00 (C3). The three pick-up days are refused their third trip on your 18:00 clock (C7). None of the 48 fault and alert scenarios misses. "
"With the window read as the bye-law has it and the energy limit at revision 5's own 75 Wh, 57 of 60 pass, and the other three are those pick-up days (see Windows and energy below). "
"Lidar and camera both gave an edge reading in 86 % of the control cycles, the camera alone in 0.6 %, neither in 3.7 %; they differed by more than 0.25 m in 5.0 %, and in those the lidar's reading was kept 99 times in 100. "
"All 24 pre-grab gates were inside on the camera and in truth, all 21 seating checks passed, and no bin was refused.\n\n"
"**A person standing in the path.** Your person scenario no longer tests a stop. At revision 5 speeds the person and the dog have crossed before the robot is within 1.5 m (closest 1.6 to 2.2 m in every seed, in my revision 4 run as well). So I made the person stand still on the robot's line. "
"That found a hole in the lidar stop logic inherited from B2-F: while the satellite fix is degraded its map filter ignores everything within 1.2 m of a hedge line, and it never stops for anything more than 0.20 m from the robot's side. "
"The cure is the second sensor Brian asked for: a camera person check (a model, with the ASSUMED rates of 1.1) slows the robot at 4 m and stops it at 1.5 m for a person or dog within 0.5 m of its sides, whatever the map and the fix say.\n\n"
"| Test, three seeds each | Lidar logic alone | With the camera person check |\n|---|---|---|\n"
"| Person stands on the robot's line for 60 s | stops in 2 of 3; in the third it **passes at 0.16 m without stopping** | stops in 3 of 3, never closer than 1.40 m, carries on when the person leaves |\n"
"| Person steps out 3.5 m ahead and stands for 60 s | closest 0.91, 0.50 and **0.11 m** | stops in 3 of 3; closest 0.96, 0.77 and 1.13 m |\n"
"| Person stands for 200 s | one waits and alerts; one makes three protective stops and holds 0.44 m away; one **passes at 0.17 m** | 3 of 3 stop 1.4 m or more away and alert \"path blocked\" after 120 s |\n\n"
"The camera check does nothing unless a person or dog is in the scenario, so I re-ran the three person missions and these tests on it and did not re-run the other 57. "
"I tried two lidar-only cures first (a wider stop corridor, and treating only long lines of returns as hedge); neither worked, because the 1.2 m map filter is what hides the person. That filter is there to stop false alarms from hedges when the position is poor, and I have left it alone.")
json.dump(F, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fill_r5.json'), 'w'), indent=1); print(len(F), 'entries')
