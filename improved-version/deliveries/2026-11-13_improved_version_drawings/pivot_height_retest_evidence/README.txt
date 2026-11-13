Castor-beam pivot height re-test, 2026-11-13
Improved version (fixed pad, 350 mm lift, castor beam on a centre pivot) with the pivot pin at 287 mm above the ground
(X_ROCK_Z=0.287) instead of 200 mm. Same scripts, seeds and scorer as the earlier runs (tags _lean = 200 mm, _lean287 = 287 mm).

Gate (gate_B2F__lean287.json): 8 of 9. G1 (pick-ups) fails:
  WEB140 30/30, ESE240SL 30/30, ESE240CL 26/30 (2 did not dock; 2 lifted the bin 34 and 72 mm off-centre, not properly seated, while the robot's own switches reported a good hold).  At 200 mm: 90/90.
  Sideways error when first arriving at the bin, mean / largest (mm):  WEB140 15.1 / 43 (200 mm: 13.2 / 39)
                                                                      ESE240SL 22.2 / 73 (18.3 / 48)   ESE240CL 24.6 / 89 (15.8 / 47)
Lane runs (lane_lean287_*.json), all with the 40 mm step ramped 1:4: P1, P2a, P7, P2c all pass; clearances as at 200 mm.
Not run at 287 mm: the sharp-step lane runs (both versions already stall there on the empty return).
Conclusion: keep the pin at 200 mm, where every passing test was run. Cause of the loss of accuracy not yet identified.
