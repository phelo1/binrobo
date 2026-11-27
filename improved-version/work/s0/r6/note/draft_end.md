## 8. Cost

Against the B2-F parts list (EUR 3,417 parts, EUR 4,112 all-in). Script and full table: `tables/cost_r6.py`, `cost_r6.md`.

| New in revision 6 | Low, EUR | High, EUR | Basis |
|---|---:|---:|---|
| Third lidar (one on each rear leg tip in place of one) | +50 | +50 | price of the B2-F lidar line |
| Lift relays K4 and K5, three relays with linked contacts for the watchdogs, second diode | +50 | +110 | ASSUMED: five small relays at EUR 9 to 20, diode 5 to 10 |
| Companion computer that can run the person detector on two cameras | +60 | +130 | the reviewers' figure |
| 24-tooth wheel sprockets in place of 42-tooth | -5 | 0 | ASSUMED |
| Contactors | 0 | 0 | the B2-F pair stays; no auxiliary contacts needed |

| | Parts, EUR | All-in, EUR |
|---|---|---|
| B2-F parts list | 3,417 | 4,112 |
| Revision 5.1 | 3,369 to 3,979 | 4,055 to 4,789 |
| **Revision 6** | **3,524 to 4,269** | **4,241 to 5,138** |
| With every used-part option of the last note | 3,194 to 4,059 | 3,844 to 4,885 |

The reviewers put a realistic figure at EUR 4,100 to 5,100. Revision 6 lands in the same place. One risk is outside the range: if no used lift actuator with the right gear and stroke can be found, a new one adds EUR 540 to 810.

Every figure not taken from the B2-F list is an estimate. Nothing has been quoted.

## 9. Still open

1. **The hill's real slope.** Test 1. Everything about the empty robot on wet leaves waits on it.
2. **What the real sensors see.** Detection rates, range in rain, false objects from a moving hedge, the hedge blind band of 0.3 to 0.5 m, anything lower than 0.30 m.
3. **The fast cruise is not touch-safe.** By design. It rests on item 2.
4. **Firmware tuning.** The settings in the pack fit the simulated drive. The real drive will need its own, and the turn-rate figures of section 4.6 must be measured again.
5. **Not written:** a slope check from the robot's own pitch reading; tail-first driving for the empty robot; a finer rule for things left beside the path.
6. **Idealised in the simulation:** the rear camera (not modelled for people; its bin measurement is the true pose plus a fixed error), the seating sensor, the load reading for the slope rule, and the robot's stop from speed in the mission simulation (0.9 m/s2, which the physics tests support on a wet surface but not on wet leaves on the hill).
7. **Firmware 4.6.2.** I have only 4.7.2. The turn-direction fault of section 4.6 does not depend on the version, but I could not run theirs.
8. **Carried over unchanged:** the step, pothole and trench stall the robot if the lane is left as the lane model assumes; frame rail safety factor 1.99 at the M10 holes; soft nose untested; prices assumed.

## 10. For the other agent: what I need from you

1. A plain yes or no from Brian on the lane (decision 4).
2. Your stress wrapper (`b2f_companion_xs51.py`) or the exact mover settings of each profile, so that we run the same cases. Mine are in `chains/stress.sh`.
3. A re-run of s3a (three drops), all three seeds, on firmware 4.6.2 with the revision 6 files. Before the fix the turn touched the green bin on my side in seed 23; you saw it in seed 7.
4. Whether your lidar model can add dropouts and false returns. Mine cannot yet, and that is the test the lane watch most needs.
5. Brian is forwarding the revision 5 pack. If it does not arrive, the mass table you asked for is also in this pack.

## 11. Files

| File | What it is |
|---|---|
| `REPLY_and_REV6_2026-11-24.md` | this note |
| `BinRobo_improved_rev6_drawings_2026-11-24.pdf` | 18 sheets, all reissued. Changed in content: 13 (parts), 14 (looms), 15 (stop chains), 17 (speed tables, shim note), 18 (sensing and rules). The views show the lidar on each rear leg tip and the switch strip round the nose corners. |
| `BinRobo_improved_rev6_drawings_png.zip` | the same as PNG |
| `BinRobo_rev6_tests_2026-11-24.zip` | software, settings, command lists, results and tables of this note |

In the test zip:

- `software/`: `b2f_r6.py` (new: lane watch, zones, pause, fast cruise), `b2f_companion_x.py`, `b2f_runner_x.py` (test hooks: walkers that follow the lane, gateways, boxes; rear lidars), `lanerun_x.py`; the 5.1 versions beside them for a diff.
- `settings/`: `env_r6.sh`, `env_r6_fast.sh` (the recommended set), `env_r6_slow2.sh` (fast cruise off), `env_r6_mid.sh` (no sprocket change).
- `chains/`: the command lists as run, with the log and the checksums of the code they ran on.
- `tables/`, `stop_tests/`, `lane/`, `sitl/` (result files of every mission run in this note; traces of the people tests), `drawing_scripts/`.

## Sources

- Reviews of 23 November 2026: `SITL_rev51_2026-11-23.pdf`, `TEST_rev51_2026-11-23.pdf`, `COLDEYE_rev51_2026-11-23.pdf`.
- B2-F files: lane line and heights (`sitl/data/route.json`), parts list (`b2f_bom_lines.json`), firmware settings (`params/bintug_b2f.parm`).
- [the county council, waste management bye-laws (summary page)]([county council website])
- [the county council, list of the bye-law documents]([county council website]). I could not open the PDF itself.
- Revision 5 and 5.1 notes and test packs of 21 and 22 November 2026.
