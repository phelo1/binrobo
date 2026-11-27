# BinRobo improved version: reply to the review of 21 November, and revision 5

21 November 2026. From the reviewer/tester agent, for Brian and for the B2-F author.

## Summary for Brian

You asked for three things: people avoidance and navigation on lidar and camera together, keeping to the robot's left side of the lane, and a lower price, with the review's other points improved. Revision 5 does the first three. Most of the review's other points are answered; the ones that are not are listed in section 5.

- **Price: about EUR 4,220 to 5,200 all-in, down from 7,340 to 11,330.** That is back at B2-F's level (4,245). It assumes the lift actuator is bought used; new, add about EUR 800. Most prices are assumed, none quoted.
- **People avoidance: two sensors in every direction.** A lidar low on the nose and a camera watch forward; a second lidar (EUR 50) and the rear camera watch backward. Either can stop the robot. The forward pair is in the driving software and tested; the rear pair is drawn and costed but not yet in the software. With both working, a person can step out 0.4 m ahead on the level and not be touched; closer than that, a soft foam nose with switch strips touches first and the robot stops inside the foam. **None of this is a certified safety system.** That is what the price cut costs, and it is your decision (section 6).
- **Keeping left: 0.42 m from the left hedge** on the straights, leaving about 2.7 m of lane free. Closer fails: at 0.30 m the robot gets within 88 mm of the hedge, and holding the edge through sharp bends does not work for a robot this long.
- **A fault of mine that you should know about.** In the first full test of the new lidar-and-camera navigation the robot came within 1 mm of a hedge at a sharp bend, and in another mission it turned on the spot while waiting. I traced both, fixed them, added a protective field that stops the robot for anything in its path, hedge included, and re-ran everything. «SUMMARY_SITL»
- **Mechanical re-test at the new weight of 180 kg:** all gate tests pass except weight, 179 of 180 pick-ups lift and one is refused safely, and the robot completes the lane once it is made good. It still cannot climb the 40 mm step, the pothole or the trench as they are today.
- **Still open:** the empty robot is only safe on a wet 12 % pitch when it comes down tail first, and that is tested in the lane simulation but is not yet in the mission software; on wet leaves on that pitch a touch is not a safe stop even with a full bin; the real slope and the highest edge on your lane are not measured; the lane-keeping fixes were tested with injected faults because I could not reproduce the original event on demand.

What I need from you is in section 6: chiefly, whether uncertified people protection is acceptable, and two measurements on the lane.

