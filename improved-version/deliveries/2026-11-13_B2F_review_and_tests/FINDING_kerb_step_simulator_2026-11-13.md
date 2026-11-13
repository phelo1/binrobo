# Finding: the "40 mm kerb" failure is caused by the simulator version

13 November 2026. From the first runs of the other agent's own gate code in my session (run with Brian's standing approval). Evidence files are in `kerb_finding_evidence.zip`.

## 1. Result

**The one gate item that every design fails, G3(b) "sharp full-width 40 mm step", fails because of how MuJoCo 3.13 to 3.17 handles a wheel on a sharp edge. On MuJoCo 3.2 to 3.12 and on 4.0.1 the same code, unchanged, passes it.**

The stored results were produced with MuJoCo 3.17.0 (section 2). In versions 3.13.0 to 3.17.0 the contact between a cylinder wheel and the corner of a box step is given a horizontal contact direction, as if the step were a wall. A wheel can never climb a wall. The correct direction points from the corner to the wheel centre, 40.7 degrees from vertical for a 330 mm wheel on a 40 mm edge.

| MuJoCo | Contact direction at the corner, degrees from vertical (correct: 40.7) | One driven wheel, 78 kg, 0.5 m/s, 60 N m cap | B2 gate "step both" | B1 "step both" | Rev H "step both" |
|---|---|---|---|---|---|
| 3.2.7 | 40.7 | climbs | pass | - | - |
| 3.3.5 | 40.5 | climbs | pass | pass | pass |
| 3.8.1 | 40.5 | climbs | pass | - | - |
| 3.12.0 | 40.5 | climbs | pass | pass | pass |
| 3.13.0 | **90.0** | **stuck** | - | - | - |
| 3.14.0 | **90.0** | **stuck** | fail | - | - |
| 3.16.0 | **90.0** | **stuck** | fail | - | - |
| 3.17.0 | **90.0** | **stuck** | fail, 1.34 m (as stored) | fail, 1.34 m (as stored) | fail, 1.34 m |
| 4.0.1 | 40.5 | climbs | pass, 4.71 m | pass, 4.71 m | pass, 4.71 m |

"-" means not run. The first two result columns come from `wheel_edge.py`, a 40-line model of my own with the gate's contact settings. The last three are the other agent's unchanged runners (`b2/runB2.py`, `cmp/runCMP.py`) with their own command lines.

A hand calculation agrees with the passing versions (`kerb_energy.py`): to roll both loaded drive wheels over a 40 mm corner at friction 0.6 with the 60 N m cap, the robot must supply about 5 J from its momentum, and it arrives with about 14 J after the impact. From a standstill against the edge it cannot climb (it would need friction 0.86), which is the other agent's own static figure and is correct.

## 2. Their results reproduce here

With MuJoCo 3.17.0 and their command lines (`env CGB_F9=1 IT1_TAG= python3 b2/runB2.py ...`, run from `revG/sim/cg`):

- 38 non-grab B2 gate cases (climb, E-stop, set-down, static, step, carry and pivot): **38 of 38 verdicts identical** to the stored files; 2,690 of 2,833 result fields identical. The rest differ in the third significant figure (for example hold creep 0.035 against 0.038 m), which fits a different processor.
- Grab batch, Weber 140, 30 attempts, seed 201: 30 of 30 captured as stored; 28 of 30 runs numerically identical.
- On MuJoCo 4.0.1 the same 38 cases give 37 identical verdicts. The one that changes is the full-width step, from fail to pass. The flat-ground cases are almost bit-identical between 3.17.0 and 4.0.1 (E-stop: 74 of 75 fields).

So 4.0.1 keeps their flat-ground behaviour and has the correct edge contact. It is the version to use from here on.

## 3. What this changes

| Statement in Handover Rev 4.0 | Status now |
|---|---|
| Gate: "8/9; only the sharp full-width 40 mm step fails (needs a ramp)" | The failure is a simulator artefact for B1, B2 and Rev H. B2-F has the same wheels and drive, so it very likely passes too: **to be run** (I do not have the B2-F source) |
| Lane physics P5d, P5e: sharp 40 mm up-step fails, "needs grip 0.86" | Same artefact for a robot arriving at speed. Re-run on 4.0.1 |
| Lane physics P5g, P5i: wheel wedges in the 40 x 200 mm trench | Leaving the trench is the same 40 mm edge. Re-run |
| Lane physics P2a, P2c, P7: trapped in the 60 mm pothole | Suspect, but may be partly real: the hand calculation says a 60 mm edge is beyond the robot at 0.5 m/s (18 J needed, about 10 J available). Re-run |
| "Ramp or fill every edge over 25 mm"; "add drive-axle suspension" | Not supported until the re-runs are in. The light-load slip on wet leaves (F4) is not an edge effect and stands |
| My own review, finding 7 ("kerb results come from rigid wheels") | Understated. The cause is the contact direction, not tyre stiffness |

Not changed: grab, lift, set-down, E-stop, slope hold, tip angles, lane fit, SITL, and the cost.

## 4. For the other agent

1. Run `wheel_edge.py` in your environment. If it prints `contact_normal_deg_from_vertical: [90.0, ...]`, your MuJoCo has the fault.
2. Move to MuJoCo 4.0.1 (`pip install mujoco==4.0.1`), or 3.12.0, and add `wheel_edge.py` as a pre-flight check before any gate run.
3. Re-run, with the frozen criteria unchanged: G3(a), G3(b) for B2-F and Rev H2; lane physics P2a, P2c, P5d, P5e, P5g, P5i, P7; then one full gate pass to confirm nothing else moved.
4. Report both sets side by side. Do not delete the 3.17.0 results.

## 5. Limits

- A rigid wheel on a perfectly sharp edge is still a model. A real 40 mm kerb test (test F1) is still needed before the lane is declared passable without ramps.
- I have not run B2-F: its source is not in the package I was given.
- I have not looked for the cause inside MuJoCo, only measured the behaviour version by version.
