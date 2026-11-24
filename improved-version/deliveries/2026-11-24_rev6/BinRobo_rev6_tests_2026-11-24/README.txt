BinRobo improved version, revision 6 - test pack of 24 November 2026
====================================================================
Reply to the re-test of revision 5.1 (23 November) and to Brian's two points: a round trip took over an hour, and a person was touched
in the reviewers' close step-out case. This pack holds what is new since the 5.1 pack. Read REPLY_and_REV6_2026-11-24.md first.

software/      b2f_r6.py                  NEW. Lane watch on three lidars, stand-still zone, pause and restart, things and people, fast cruise.
                                          Mixed into the mission software (class R6Mixin); switched on with X_R6=1. Settings are listed at its top.
               b2f_companion_x.py         mission software as run here. Changes are marked [revision 6]: R6 hooks in the lane loop, the path
                                          follower and the pivot; pivot watch during the turn; turn direction checked both ways and kept
                                          (pivot_way); bye-law windows by default, old branch deleted; X_RET_BY, X_CREW_FROM, X_LEAF_NOGO;
                                          adaptive energy budget.
               b2f_runner_x.py            mission runner: X_ROB_VMAX; test hooks X_MOVERS_SET (walkers, also along the lane), X_HEDGE_GAP
                                          (gateway), X_OBST_ADD (unmapped box).
               lanerun_x.py               lane-physics runner: X_VDEF (cruise speed), end-zone speed rule, hold test with overrun check.
               *_r51.py                   the 5.1 versions, for a diff
               code_final.md5             checksums of the files in this pack (the last turn tests ran on them)
               code_lane_tests.md5        checksums of the files the lane people tests and r6f_val2 ran on: the same lane watch, before the
                                          three turn fixes of the evening (look for a second before a turn; people rule in the wait for the pad;
                                          arrivals count as moving at a turn outside the yard)
settings/      env_r6.sh                  revision 6 rules on the unchanged 5.1 drive, touch-safe speeds
               env_r6_fast.sh             RECOMMENDED: 2:1 chain stage, firmware loops reset for it, fast cruise
               env_r6_slow2.sh            the same hardware with the fast cruise off
               env_r6_mid.sh              no sprocket change, 0.6 m/s on a clear lane
               env_r6_fast_leaf.sh        leaf-season speed tables            env_r6_fast_v10.sh   test only: 1.0 m/s also under a degraded fix
               sitl_env_r5.sh             the revision 5 base they build on
chains/        chain_r6_*.sh, stress.sh, run2.sh, sitl_run_x.sh and the log chain_r6.log: the mission runs as run, in order, with every stop and
               restart of the day and the reason for it. chain_r6_last.sh is the last of the lane tests; chain_r6_pivpre.sh and _pivpre2.sh are the turn tests after it.
               stress.sh holds the mover settings of every people case.
               q_r6_pstop*.txt, q_r6_kerb.txt (+ .out): the MuJoCo stop and kerb tests. chain_r6_lane.sh: lane physics at speed.
tables/        stress_tab.py, stress_md.py -> stress_r6.json / .md      the people tests (section 3.2)
               stress_v10_r6.json                                      the five closest cases with every seed at the full 1.0 m/s
               piv_an.py -> pivot_people_r6.json                       someone walks up at a turn on the spot (section 4.6)
               trips_tab.py -> trips_r6.json                           trip time and energy by setting (section 4.4)
               pstop_tab_r6.py -> pstop_speed_r6.json / .txt           stop distances, new brake torque (section 4.5)
               lane_tab_r6.py -> lane_fast_r6.json / .txt              whole-lane physics at the fast cruise
               kerb_r6.json                                            kerb strike loads at 0.8, 1.0 and 1.2 m/s
               pivot_rates.py -> pivot_r6.json                         turn rates on the spot (section 4.6)
               r5_score.py -> score_r6_fast.md, score_r6_phantom.md    the 60-mission score (section 5)
               cost_r6.py -> cost_r6.md / .json                        cost (section 8)
               mk_facts_r6.py -> facts_r6.json                         texts of sheets 17 and 18
stop_tests/    result file of each MuJoCo stop and kerb test; mass_cgB2_r5.json = the mass and centre-of-gravity table they use
               (the revision 5 table the physics re-test asked for)
lane/          result.json of each lane-physics run at the fast cruise (runs_r6_fast, grip 0.35; runs_r6_fast_w22, grip 0.22);
               lane_first_try/ = the runs before the end-zone speed rule (P2c touched the hedge 14 m from the road end)
sitl/          result.json of every mission run (name = <set>__<scenario>__s<seed>.json); traces of the close people cases in traces/ (.json.gz).
               WITH THE FINAL LANE WATCH (code_lane_tests.md5):
               r6f_<case>      people cases, fast cruise on           r6s2_<case>     the eleven hardest and the gateway cases, fast cruise off
               r6v_<case>      the close cases with every seed at the full 1.0 m/s (test setting env_r6_fast_v10.sh)
               r6f_val2        drop-off, pick-up, three drops, three pick-ups
               r6f_lookahead_trip   first drop-off with the gateway look-ahead
               ON THE CODE IN THIS PACK (code_final.md5):
               r6f_pivflank_a  someone walks up from the road side BEFORE the turn at the road end and stands inside the nose circle
               r6f_pivflank_a2 the same, arriving DURING the turn          r6f_pivflank_b   from the house side, during the turn
               r6f_val3        a pick-up (the three turn tests are themselves complete drop-offs)
               BEFORE THE LAST TWO CHANGES TO THE LANE WATCH (hedge faces from bins; gateway look-ahead) - see the note for what each shows:
               r6f_suite       the 60-mission score suite, fast cruise            r6f_val   four missions after the pivot fix
               r6f_phantom, r6f_leaf, r6f_leafnogo, r6f_hold600, r6s2_trip, r6m_trip   false sightings, leaf-season tables and switch, hold timer, trips with the fast cruise off and with the middle option
               r6_repro_near26      revision 5.1 software in the reviewers' contact case (touch in 2 of 3)
               before_fixes/   runs kept as evidence of what a fix changed:
                 r6f_suite_before_dirfix   three drops, three seeds, before the turn-direction fix (seed 23: the nose touched the green bin)
                 r6f_pivflank_before_fix   the two pivot tests before the pivot fix (b: touch)
                 r6f_pivflank_before_fix2  the same two on the code of code_lane_tests.md5 (a: the turn began with a person standing 0.7 m away)
                 r6f_pivflank_before_fix3  a, a2, b and a pick-up after the first two turn fixes, before the arrival rule (b: the turn ran on for 1.4 s)
                 r6_gap_before_fix, r6_gap_after_fix1, r6_gap_no_lookahead   the gateway cases before, between and after the two lane-watch fixes
                 r6_before_binfix          all people cases, both settings, before those fixes (126 runs; table tables/stress_before_binfix.md)
drawing_scripts/  build_model.py, draw_sheets.py, r6_sheets_patch.py, r6_sheets_patch2.py, draw_sheets_r51.py (as issued 22 November), make_pdf.py

To repeat a people case:   source settings/env_r6_fast.sh; then the lines of chains/stress.sh for that case; ./sitl_run_x.sh <out> <queue> <instance>
Firmware: ArduRover 4.7.2 SITL (the B2-F binary). I have no 4.6.2 binary.
