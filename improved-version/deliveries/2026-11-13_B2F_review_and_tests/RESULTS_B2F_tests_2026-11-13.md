# B2-F: my test results, 13 November 2026

Run in my own session on the other agent's source pack (`BinRobo_B2F_source_2026-11-13.zip`), with Brian's standing approval. Their code, frozen criteria and command lines are unchanged. Evidence is in `b2f_tests_evidence_2026-11-13.zip`.

All of this is simulation. Nothing has been built, the lane has not been surveyed, and the bins have not been checked.

## 1. Bottom line

1. **B2-F passes 9 of 9 gate items on a simulator version with correct kerb contact** (MuJoCo 4.0.1), scored by the other agent's own scorecard script. The stored 8 of 9 was on MuJoCo 3.17.0, which treats a kerb corner as a wall.
2. **A simpler, more capable candidate also passes 9 of 9**: no pad actuator, a longer carry lift, and a castor rocker. Grabs 90 of 90. Bin-wheel clearance while carried goes from 50 mm to 87 mm. The empty-return lane failure is fixed.
3. **Two lane hazards are real in both simulator versions**: the 60 mm pothole on a wheel track and the open 200 mm trench. Both are assumed features. If the survey finds them, fill the pothole and cover the trench.
4. **Two points in my review of this morning were wrong** and are corrected in section 5.

## 2. Their results reproduce here

| Check | Result |
|---|---|
| 38 non-grab B2-F gate cases on MuJoCo 3.17.0 (their version) | 38 of 38 verdicts identical to the stored files; 2,758 of 2,833 result fields identical |
| Same 38 cases on MuJoCo 4.0.1 | 37 identical verdicts; the full-width 40 mm step changes from fail to pass |
| My variant model file with its switches off | Bit-identical to their model on 4 cases |

## 3. B2-F as designed, on the corrected simulator

Gate (their `summarize_h2.py`, frozen criteria):

| Item | Stored, 3.17.0 | Mine, 4.0.1 |
|---|---|---|
| G1 grab | pass, 90/90 | pass, 89/90; plus 30/30 and 30/30 on the two extra bins; no false holds, none knocked |
| G2 climb and hold | pass | pass |
| G3 40 mm step, one side and full width | **fail** (full width stalls at 1.34 m) | **pass** (4.71 m) |
| G4 E-stop | pass | pass |
| G5 carry and pivot | pass | pass |
| G6 set-down, 18 cases | pass | pass |
| G7 time-step repeat | pass | pass |
| G8 static loads and tips | pass | pass |
| G9 mass | pass | pass |
| **Total** | **8 of 9** | **9 of 9** |

Lane physics (their `lanerun.py`):

| Run | Stored, 3.17.0 | Mine, 4.0.1 |
|---|---|---|
| P5d sharp 40 mm up-step, loaded | fail, stalls | **pass**, 40 mm bin-wheel clearance |
| P5a sharp 40 mm drop, loaded | pass, 3 mm clearance | pass, 11 mm clearance |
| P5g open trench 40 x 200 mm, loaded | fail, stalls, bin touches ground | **fail**, stalls; bin no longer touches ground |
| P5h 60 mm pothole under one wheel, loaded | pass | **fail**: comb lip unseats |
| P1 full trip with a 110 kg bin (pothole as assumed) | pass, 1,323 s | **fail**: stuck at the pothole for about 17 minutes, lip unseats, then completes and sets down |
| P2a_pf empty return, pothole filled | fail: slides off the lane on the wet-leaf slope | **fail**, same way |

Not re-run yet: P2a, P2c, P3, P4a, P4b, P5b, P5c, P5e, P5f, P5i, P6a, P6b, P7, and all SITL.

## 4. Design changes tested

All on MuJoCo 4.0.1, compared with B2-F as designed on the same version.

| Change | How tested | Result |
|---|---|---|
| **Castor rocker** (castor pair on a centre pivot, stops at +/-5 deg) | 33 gate cases + 30 grabs; lane P2a_pf; lane P1 | Gate: no verdict changes, 30/30 grabs. **P2a_pf: fail to pass** (stays 0.31 m from the hedge; roll 1.8 deg against 9.1). P1 with the pothole: still fails, stalls in the pothole |
| **Longer lift travel only** (350 mm) | 33 gate cases + 30 grabs | No change at all. The firmware lifts 100 mm of carriage travel after load-on whatever the travel |
| **Longer carry lift** (350 mm travel, lift 150 mm after load-on) | 33 gate cases + 30 grabs | No verdict changes, 30/30. Clearance while carried **98 mm** against 50 mm; on the 250 mm-wheel bin 87 to 108 mm against 38 to 58 |
| **Fixed pad at the designed position** (their setting `pad_in` 0.015, never retracts) | 33 gate cases + 29 grabs | **Fails** 27 of 33 cases. In the three I inspected the bin wall meets the pad before the comb is home ("no dock"). Moving the pad further forward makes it worse |
| **Fixed pad set back** 5, 15, 25 mm behind the comb tip, with the longer carry lift | 3 set-downs + 30 grabs each | All pass, 30/30 each. Bin tilt 4.3, 5.1, 6.0 deg (2.4 as designed). Clearance at 5 mm back: 70 to 129 mm |
| **Combined candidate**: fixed pad 5 mm back + 350 mm travel with 150 mm carry lift + rocker | Full frozen gate: 38 cases, 90 grabs, 3 time-step repeats | **9 of 9. Grabs 90/90**, no false holds. Clearance while carried 87 mm. Hold creep 0.026 m (0.031). E-stop 0.177 m (0.161) |

Limits of the candidate result: one seed set; the tip hand calculation in the scorecard did not pick up the higher bin (my estimate: castor lift-off about 22 deg against 23, still above 20); not yet run on the lane with a bin, in the perturbation set, or on the two extra bins; mast height for 350 mm of travel not checked in CAD.

## 5. Corrections to my review of this morning

| Review finding | Correction |
|---|---|
| 1. "The lift stroke is too short" | Wrong cause. The stroke is not what limits the lift: about 29 mm of the 100 mm is used up as the bin settles onto the pad. The fix needs a larger lift command as well as more travel. With both, clearance nearly doubles |
| 3. "The pad does not need an actuator" | Half right. A fixed pad at the designed position fails. A fixed pad set 5 mm behind the comb tip works, at the cost of 2 deg more tilt, which the longer lift more than covers |
| 2. Castor rocker | Confirmed for the empty-return slip. It does not help in the pothole |
| 7. Kerb results | Confirmed and stronger: B2-F passes the 40 mm kerb, up and down, on the gate and on the lane |

## 6. What this means for the design and cost

- **Lane preparation shrinks**: no ramps needed for 40 mm edges in simulation. Still needed if the survey finds them: fill any pothole near 60 mm, cover any open trench. A real kerb test is still required.
- **Drive-axle suspension is not needed** for the failure it was proposed for; the rocker (about EUR 20) fixes it.
- **The pad actuator, toggle and lock switch can go** (about EUR 80 of parts) if the candidate holds up in the remaining tests.
- Cost position is otherwise as in `REVIEW_B2F_2026-11-13.md`: about EUR 3,460 (donor drive) to EUR 3,650 (new drive, AGM battery), before about EUR 130 of structural upgrades.

## 7. Next runs, in order

1. Candidate on the lane with a bin: P1, P3, P5a, P5d, P4a, P4b, with the pothole filled and the trench covered.
2. Candidate through the perturbation set and the two extra bins.
3. As-designed and candidate: P2a, P2c, P7 on 4.0.1.
4. SITL: reproduce the 52 of 60, then look at the four failing scenarios.
5. Cost re-issue with verified prices.

## 8. How to repeat this

- MuJoCo 4.0.1 (`pip install mujoco==4.0.1`), plus `cadquery` for the geometry module the gate imports.
- Gate: their command lines from `h2/q_h2.txt`, run from `revG/sim/cg`. My tagged copies are in the evidence zip (`commands/`).
- Variant model: `make_simB2hx.py` writes `h2/simB2hx.py` from their `h2/simB2h.py` with two switches, `X_LIFT_RANGE` and `X_ROCKER`. The fixed pad and carry lift use their own settings: `CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}'` and `B2F_PAD_IN=-0.005`.
- Lane: `make_lanerun_x.py` writes `lanerun_x.py` with switches for the model module and the run folder. Their code has the project path fixed in `lane_world.py`; I linked that path to my copy and took `sitl/data/route.json` from the 12 November archive.
