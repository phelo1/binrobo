## 3. People avoidance in revision 6

### 3.1 What changed

1. **The lidars watch the whole lane.** Every lidar return is sorted into hedge or not hedge. Hedge is whatever lies on the hedge face that the scan itself shows; when the satellite fix is good the map gives a second opinion. Anything else inside the lane is an object, wherever it is: in the path, beside it or behind the robot. This works without the map and without a good position.
2. **Three lidars.** One at the nose as before, and one on the tip of each rear leg (revision 5 had one rear lidar, and the bin hid one side from it). Together they see all round, bin or no bin.
3. **Stand-still zone.** An object within 3 m of the robot's outline, in any direction: stop and stand still. A person or animal the camera has seen twice running within 5 m does the same, if the lidar has an object at the same place; within 2.5 m it needs no lidar match.
4. **Braking.** From the fast cruise the robot brakes at once: drive to neutral, brakes on. At the touch-safe speeds it ramps down as before.
5. **Standing still means still.** In revision 5.1 the stopped robot's wheels kept twitching, because the firmware went on correcting its heading. Now the firmware holds the drive at zero while the robot waits.
6. **Restart.** Only when every sensor has shown the zones empty for 3 s. The first 3 m are at 0.2 m/s.
7. **People and things.** Once a camera has called something a person it stays one until it has gone. The robot waits: owner message at 2 minutes, hold with an alert once it has stood for 15 of the last 20 minutes. A thing may be passed, at 0.2 m/s, only if the front camera has had it in view and never called it a person, it has not moved for 20 s and it is 0.5 m clear of the path. Anything that turns up beside or behind the robot is outside the camera's view, so it is waited for like a person. A thing in the path for 2 minutes ends the trip with a path-blocked alert.
8. **Turning on the spot.** No turn with anything unknown within 1.75 m of the axle (the circle the nose sweeps), nor with a person or anything moving within 3 m. The same watch runs five times a second during the turn.
9. **False camera sightings.** A sighting beyond 2.5 m only stops the robot if a lidar object is at the same place. One sighting of any kind ends the fast cruise for the moment.

The older layers stay underneath: the protective field in the robot's own path, and the switch strips on the soft nose.

### 3.2 Tests

Mission simulation, scenario s5a: the robot with a full bin in the lane at night, between 295 and 380 m from the house. Three seeds for each case. "Nose 1.0 m from their line" means the person sets off from the hedge when the nose is that far from where they will cross. They walk at 1 m/s and do not look: they keep walking even into a robot that has stopped. Camera: a person found in 60 % of pictures (night), 5 pictures a second. Lidar: 10 scans a second, 10 mm noise.

A "touch" is any contact while the robot is still moving, however slowly.

⟦STRESS_TABLE⟧

Three more cases outside the table:

⟦EXTRA_PEOPLE⟧

### 3.3 False sightings

⟦PHANTOM⟧

### 3.4 What it still cannot do

- **Someone who appears right in front of a fast robot.** The robot needs about half a second to be sure something is there and about a second to stop from 1.0 m/s. ⟦LIMIT_FAST⟧ With the fast cruise off there was no touch in any case.
- **Someone standing against the hedge.** Anything within 0.3 to 0.5 m of the hedge face is taken for hedge until it steps out. That is the half second above. The protective field still covers the robot's own path.
- **Low things.** The lidars sit 0.30 m above the ground. A cat, a lying dog or a ball is seen only by the camera, then felt by the nose strip.
- **The camera sees forward only.** Beside and behind, the robot has lidar alone. That is why anything there is treated as a person. The rear camera is still not in the simulation.
- **Things left in the lane.** The rule errs towards stopping. A box well clear of the planned line still ended two of three runs with a path-blocked alert, because the robot was in mid-lane after a bend when it met it. That costs a walk down the lane, not safety. I have not refined it.
- **All sensor figures are assumed.** The lidar model is an ideal scan with a little noise. Real hedges move in the wind, rain scatters the beam and wet leaves reflect badly. Expect false stops at first; test 9 counts them.
