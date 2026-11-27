# BinRobo improved version: revision 6

24 November 2026. Reply to Brian's two points and to the re-test of revision 5.1 (three reports of 23 November). For Brian and for the other agent.

Revision 6 changes how the robot keeps clear of people and how fast it drives. Hardware: a third lidar, a different sprocket on each wheel, a few relays and a bigger companion computer. All 18 drawing sheets are reissued.

## Summary for Brian

Both of your points are right. I reproduced both before changing anything.

**People.**

- The reviewers' case, on my side: a person walks out of the far hedge at night when the robot's nose is 1 m from their line. With the revision 5.1 software the robot touched them in 2 of 3 runs.
- The cause was not the camera's or the lidar's eyesight. The camera only looks forward, and this person came from the side. The lidar saw them the whole time, but the software only reacted to things already in the robot's own path. That was a hole in my design.
- Revision 6: the lidars now watch the whole width of the lane, all round the robot. A third lidar closes the blind side at the back. Anything within 3 m of the robot, in any direction, makes it stop and stand still. It does not move again until everything has been clear for 3 s.
- Result: ⟦PEOPLE_RESULT⟧
- Every sensor figure in these tests is assumed. They show the rules have no hole of the kind the reviewers found. They do not show what the real sensors will see. That is test 7 to 9 on the built robot.

**Trip time.**

- A round trip was 67 to 77 minutes because the drive was geared for 0.7 m/s flat out and I held the robot to 0.4 m/s, the speed at which a touch on the soft nose stops it inside the foam.
- Revision 6: a smaller sprocket on each wheel (2:1 in place of 3.5:1; no extra cost) and a fast cruise of 1.0 m/s. The robot only cruises fast when its sensors show the lane clear well ahead. Near anything, on the steep part of the hill, at gateways and in the yard it drops back to the old speeds.
- Result: ⟦TRIP_RESULT⟧
- The price: above 0.4 m/s the soft nose is no longer a guarantee. If someone steps out less than about 1 m in front of the nose while the robot is cruising fast, it is still braking when they meet. ⟦TOUCH_RESULT⟧

**Cost.** EUR 4,241 to 5,138 all-in, which is EUR 187 to 349 more than revision 5.1. The third lidar is EUR 50, relays and a diode for the stop circuit EUR 50 to 110, and a companion computer that can run the person detector EUR 60 to 130.

**The rest of the review.** Their two blockers were fair. The stop circuit on sheet 15 is redrawn so that no single failed part keeps the motors live. The hill is still not measured, and until it is I cannot promise the empty robot stops on wet leaves on the steepest part.

**Decisions for you**

1. **Speed.** Three choices, all tested:
   ⟦SPEED_OPTIONS⟧
   I would fit the sprockets, run the first weeks with the fast cruise off, and switch it on once tests 7 to 9 and 13 pass on the real robot.
2. **Third lidar and bigger computer** (EUR 110 to 180 together). I would not build without them: they are what closes the gap the reviewers found.
3. **Measure the hill.** A 2 m board and a phone, half an hour (section 7, test 1). Until then, switch on the leaf-season setting from October to December: the robot then refuses pick-up trips, because on those it goes down the hill with no bin.
4. **Is the mapped lane the right one?** 635 m from the house to the public road. The other agent asked on 6 November and I asked on 22 November. Neither of us has a plain yes.
5. **Bins home by 21:00 or by midnight?** The council's page says 9.00 pm; the other agent reads midnight in the bye-law text. I left it at 21:00. With the fast cruise it makes no practical difference.
6. **Please forward the revision 5 files** of 21 November to the other agent. They say the pack never reached them, and seven of their open questions are answered in it.

## 1. What the re-test found and what I did

| Finding of 23 November | My check | What changed | Section |
|---|---|---|---|
| Someone who steps out close ahead at night is touched (1 of 2 runs) | Confirmed: 2 of 3 runs | Lane watch on the lidars, stand-still zone all round | 2, 3 |
| Someone behind or beside the robot is not seen | Confirmed | Third lidar; the zone covers every side | 3 |
| The robot restarts with a person beside it | Confirmed | Restart only when every sensor is clear | 3 |
| The 15-minute hold never fires | Confirmed | The hold sums all pausing in the last 20 minutes | 3 |
| One false camera person a minute: 87 pauses | Not re-run on 5.1 | A camera sighting must match a lidar object | 3 |
| A round trip takes 68 to 82 minutes | Confirmed: 67 to 77 | Fast cruise, 2:1 chain stage | 4 |
| A loaded turn on the spot touched a parked bin (firmware 4.6.2) | Not reproduced on 4.7.2 | Found and fixed why turns overshoot | 4.5 |
| B-1: the hill is not bounded at 8.5 % | Agreed | Survey method, leaf-season settings | 6 |
| B-2: one shorted diode defeats both contactors | Agreed | Sheet 15 redrawn | 6 |
| 48 of 60 on the frozen score | Re-run | ⟦SCORE_ROW⟧ | 5 |
