### 4.6 Turning on the spot

Three separate things were wrong here. The first is the reviewers' "real, if rare, collision with a bin in the yard".

**Which way round.** I reproduced their failure on my side, in seed 23 of the three-drop mission, on firmware 4.7.2: just after lifting the black bin at the house, the nose swept into the green bin parked beside it.

- The turn to face the lane there is a half turn, 183 degrees.
- The software took "the short way round" and worked it out afresh every cycle from the heading estimate. A degree of noise decided between left and right.
- One way round clears the green bin by 0.6 m. The other goes through it. The check before the turn only looked at the way it expected to go.
- Fix: for a near half turn the software checks both ways round against the map and the known objects, takes the way with more room, and keeps to it for the whole turn.
- In the 60 missions there were 51 such turns. One way was blocked in 6 of them. The way taken had at least 0.57 m of room. No contact.

This fault does not depend on the firmware version, so I expect it is what the reviewers saw in seed 7 on 4.6.2.

**How fast.** They also saw the turn run at 0.30 rad/s against a command of 0.13. The cause is in the firmware settings of B2-F, not in the command:

- the turn-rate feed-forward (0.8) is 1.5 times what this drive needs, and
- the minimum-throttle setting adds a fixed amount to every small command.

With the 2:1 chain stage the same settings would have been worse: 0.49 rad/s in my first fast trip. I set the feed-forward from the gearing (0.35), scaled the other gains by the same ratio and lowered the minimum throttle from 5 to 3 %. In the 60 missions:

| | Revision 5 settings (60 missions of 21 Nov) | Revision 6 (60 missions) |
|---|---|---|
| Loaded turn on the spot: highest rate | 0.40 rad/s | 0.28 rad/s |
| Speed of the nose corner at that rate | 0.56 m/s | 0.39 m/s |
| Time above 0.30 rad/s, nine loaded turns | 2.0 s | none |
| Setting off on a curved path from rest: highest rate | 0.68 rad/s | 0.57 rad/s |

So it is better, and it is still short of the 0.22 rad/s the review asks for (m-5). The brief swing when the robot sets off round a parked car lasts about half a second. A hard limit in the firmware (`ATC_STR_RAT_MAX` 13 degrees a second) would hold everything at 0.22. I have not tested that setting, so it is not in the pack.

**People at a turn.** Rule 8 of section 3.1. Two tests, each a drop-off in which someone walks up while the loaded robot is turning at the road end, stands 1.4 m from the turning centre for 30 s and walks on:

| Case | Result |
|---|---|
| They come from the road side, in front of the robot | Camera finds them at 4.8 m. The robot stops turning and stands for 43 s, until they have gone. It was never turning with them inside 3 m. Trip completed. |
| They come from the house side, behind the robot | The rear lidars find them as they cross the 3 m line. The robot stops turning 0.6 s later, with them 2.3 m away, and stands for 43 s. Trip completed. |

My first version of this rule failed both tests, and the second one with a touch:

- While the robot stands across the lane, the hedge faces were still being fitted along the robot's own axis. A person walking up beside it was taken for hedge. Now the faces are fitted along the lane during a turn.
- The restart only asked "is anything moving?", so the robot turned on with a person standing still inside the circle. Now one test is used to start the turn, to watch it and to restart it.

I am glad the reviewers asked for this test. Both runs before the fix are in the pack (`sitl/r6f_pivflank_before_fix`).

## 5. The 60-mission score

The same 20 scenarios and three seeds as the reviewers' suite, with the fast-cruise settings, firmware 4.7.2. Scored by the B2-F script unchanged, and again with two criteria restated as in revision 5 (the bye-law windows; 75 Wh a trip). Table: `tables/score_r6_fast.md`.

| | Revision 5.1 (the reviewers' run) | Revision 6, fast cruise |
|---|---|---|
| B2-F script as it stands | 48 of 60 | 45 of 60 |
| With the bye-law windows and a realistic trip budget | 56 of 60 | 57 of 60 |

- **The 12 full missions all complete.** They fail one frozen criterion only: 50 Wh a trip. A trip now uses 56 to 58 Wh (5.1: 71 to 76). A 290 kg robot cannot do this lane on 50 Wh; that limit was set for the 92 kg B2-F.
- **They now fit the frozen 18:00 to 21:00 window.** Three bins out from 18:00: home at 19:46 to 19:48. Three pick-ups from 18:00: home at 19:53 to 19:54. Charge left 52 % (5.1: 41 to 42 %).
- **Three runs fail that passed before: s10b**, a garden sack in front of the bin at pick-up. The robot now stops 3 m from the sack and after two minutes reports "path blocked". The scorer expects the words "bin blocked", which came from a bin check the robot no longer reaches. The owner gets an alert and walks down either way. I have left it.
- The other 45 fault and hazard runs end as the script expects.
- **No contact in any run.** Least hedge clearance 0.186 m (limit 0.124 m; the reviewers' 5.1 run 0.175 m). Nearest approach to a parked bin 0.22 m.
- **Placement:** worst 0.129 m, mean 0.046 m, against a limit of 0.15 m (the reviewers' 5.1 run: 0.106 and 0.055 m). The worst case is nearer the limit than before. The softer firmware gains are the likely reason; I have not chased it.
- **Stops with nobody about:** 4 in the 60 runs, 3.2 to 3.4 s each: two leaving the yard, one at a turn at the road end, one beside the tipped bin.

⟦SCORE_AFTER⟧
