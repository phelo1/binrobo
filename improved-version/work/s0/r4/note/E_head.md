# Reply to the review of revision 3, and revision 4 of the improved version

20 November 2026. For Brian and the B2-F author. From the reviewer / tester agent.

Files with this note: the 17-sheet drawing set (PDF and PNG) and a zip of every script, command list and result file.

## Summary

The review of revision 3 was right on its blocker and on all eight major findings. Revision 4 answers them, and it is drawn and tested. It is still a concept, not something to build from, and the testing turned up two problems that neither design had been tested for before.

**What revision 4 now does (all by simulation):**

- Stops for a person inside the travel of its front bumper. The longest simulated stop is 122 mm against 150 mm assumed available. This needed a 300 mm foam safety bumper and a speed that depends on the slope.
- Notices something under the bin when it lowers, if the thing is thicker than about 20 mm.
- Has no welded joint. Every joint is bolted, with a bolt and torque table on the new sheet 17.
- Has a lift actuator that holds the bin (8.8 kN by its data sheet) and switches itself off before it reaches the hard stops.
- Passes eight of the nine gate tests at 60 N m, 179 of 180 pick-ups with one safe refusal, all 24 stress cases, and «LANE_SUM».
- Drives its missions on camera readings alone, without the two true-position shortcuts your driving re-test found.

**What it costs:**

- **Weight: 177.6 kg**, up from 152.2. Bolting costs about 10 kg, the bumper 4.5 kg, the strength fixes the rest. The 120 kg gate fails.
- **Time: a trip takes 62 to 72 minutes** instead of about 56, because of the slope speed rule. Two bins fit between 18:00 and 21:00; the third does not. Energy is not the limit: an aged, cold battery still ends a three-trip evening above 30 %.

**The two new problems:**

1. **The empty robot brakes badly downhill.** Only the two drive wheels have brakes, and without a bin 55 % of the weight sits on the castors. On a 12 % wet slope, nose first, the empty robot needs 0.29 m to stop even from 0.15 m/s, and on wet leaves it does not stop. With a full bin it is fine (94 mm from 0.2 m/s). This applies to B2-F as well; no earlier test covered it. In the lane model the 12 % pitch is an assumption, so the first step is to measure the real one.
2. **The 40 mm sharp step was only ever crossed on momentum.** At the speeds that are safe for people, revision 4 gets over a 25 mm edge square on with a full bin and a 20 mm edge when empty. A full bin gets over 40 mm if the edge is met at an angle; the empty robot does not. More torque does not solve it, so I withdraw my request for 80 N m. Higher edges on the lane need a small ramp.

**One strength row misses my own limit:** the nose cross-member has a safety factor of 1.55 on your hardest load case (2.0 wanted). It needs a 60 x 60 section. I found this after the test campaign had run, so it is noted on the drawings but not yet drawn in.

**What I recommend** (details in section 8): measure the steepest slope and the highest edge on the lane; design brakes for the castors, which in simulation fix both the empty-robot braking and the lost third bin (trips of 55 minutes, three bins home by 20:45); judge the weight by what the robot does, with a cap on a weighed prototype.

Where I made mistakes in revision 3, they are named in section 1: the castor load figure I quoted for the slippery hill start was an average, not the raw minimum; "the castors need round-profile tyres" was more than the evidence showed; and two sentences on the drawings and in the reply were wrong.
