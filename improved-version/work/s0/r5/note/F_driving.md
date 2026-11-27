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

«SITL_SECOND»

**Do the guards work? Faults put in on purpose.** A 90 m stretch of lane with a full bin, keeping left 0.42 m from the hedge; at 300 m a fault is switched on:

«FAULT_TABLE»

The steering faults are the test of the protective field: with a forced turn toward a hedge, the robot stops with 0.13 m or more to spare, backs out and carries on, or holds and calls after the third time. Before I limited how fast the heading command can change, the same fault swung the nose corner to 4 mm from the hedge in under a second, before any check could act; that test is in the files too.

**The bend, on purpose.** I could not reproduce the 1 mm event exactly: it needs a particular Float error at a particular place. Two attempts:

«BEND_TABLE»

**Windows and energy.** Drop-offs start at 18:00 and three bins are out by «DROP_END» (quiet-hours limit 22:30). On your scenario clock the pick-ups start at 18:00, so the third is refused as too late for 21:00, correctly. Started at 16:30: «RET1630». A trip takes «TRIP_MIN» minutes and «TRIP_WH» Wh; three trips leave «SOC3» % in the battery. Your script's limit of 50 Wh a trip was set for B2-F's 0.45 m/s; revision 5 is slower and heavier, and its own budget is 75 Wh, checked before each trip.

**Other runs.** Robot 10 % heavier (198 kg), one drop-off: «M198». Lidar hedge reading switched off, camera only, one drop-off: «CAMONLY_LONG».

**Still idealised in these runs:** the final reverse onto the bin is partly steered on true positions; heading noise is mild; camera frames are treated as independent; the bin's weight is taken as known; the rear lidar and rear camera are not modelled at all, so backing out after a protective stop relies on having just driven over that ground. The camera's left-edge reading is a model (the true edge plus 40 mm of noise, one frame in ten missing), not an image pipeline.

