BinRobo improved version, revision 6.1 - test pack of 27 November 2026
======================================================================
Revision 6.1 follows from the open points of the revision 6 note. Hardware is unchanged. The software copes with a worse lidar, keeps
still for someone who stands near a turn, finds someone close to the hedge, and every test in the note ran on one frozen code.
This pack holds what is new since the revision 6 pack. Read REV6_1_2026-11-27.md first.

software/      b2f_r6.py                  lane watch, zones, pause, fast cruise. New, marked [revision 6.1] in the comments:
                                          walker tracks (X_R6_WALK, on by default), proud rule (X_R6_PROUD, 0.55 m), scan filter
                                          (lid_filter, X_LID_FILTER=1), ghost holders (X_R6_GHOST_T, 30 s), "approach to bin blocked",
                                          and the test hook lid_degrade (X_LID_BAD): a worse lidar and a real hedge.
               b2f_companion_x.py         mission software. New: protective field and near field act on two scans running; hedge band
                                          X_PF_BAND; the wait for the pad counts lane-watch objects and runs the people rule;
                                          X_GATE_TRIES (looks at the pre-grab gate); one second of looks before every turn.
               b2f_runner_x.py            mission runner: spoils the front scan when X_LID_BAD is set (the rear scans are spoiled in b2f_r6).
               *_r60.py                   the revision 6 versions, for a diff
               harness.py                 offline replay of the lane watch on a recorded trip: replay, dump, walker (usage at its top)
               patches/p2_fg_NOT_USED.py  the range-jump test that was tried and dropped (note, section 5)
               code_final.md5             checksums of the code and settings every run of chain_g, chain_h and chain_i used
               code_frozen_0218.md5       the same three code files at the freeze; the level-2 trips and the worse-lidar people cases
                                          of chain_e ran between the freeze and chain_g
settings/      env_r61_start.sh           START WITH THIS: 2:1 chain stage, fast cruise off (0.4 m/s and under)
               env_r61_fast.sh            fast cruise on; switch to it after tests 7 to 9 and 13 on the built robot
               env_r61_fast_leaf.sh       leaf-season speed tables      env_r61_mid.sh   no sprocket change, 0.6 m/s on a clear lane
               env_r61_fast_v10.sh        test only: 1.0 m/s also under a degraded fix
               env_r6*.sh, sitl_env_r5.sh the files they build on
chains/        chain_a.sh ... chain_i.sh, stress.sh, stress2.sh, run2.sh, walker_table.sh, sitl_run_x.sh and the log chain.log:
               the runs as run, in order, with every stop and restart and the reason for it.
               chain_a to chain_e: development (walker rule, proud rule, worse lidar). chain_f never ran (see the log).
               chain_g: the regression on the frozen code. chain_h: leaf season, false camera person, middle option.
               chain_i: two baseline runs with the walker rule switched off.
               stress2.sh holds the mover settings of every people case. "side" is the revision 6 case (walker sets off when the
               robot is 3.0 m from their line); "side14" is new (1.4 m, the robot is already beside them).
               q_*.txt: mission lists. sitl_q_r4_i0/i1.txt: the 60-mission suite.
tables/        mk_tables.sh makes all of these from the result files:
               stress_tab.py, stress_md2.py -> stress_fast / _start / _v10 / _b1 / _b2 (.json, .txt), stress_r61.md (section 3.1),
                                               stress_bad_r61.md (section 2.4), stress_v10_r61.md
               react_tab.py -> react_r61.json           time from the first step to the stand-still command, revision 6 against 6.1
               piv_an.py -> turn_people_r61.json / .txt  someone walks up at a turn on the spot (section 3.3)
               trips_tab.py -> trips_r61.json; show.py -> trips_show_r61.txt   trips by setting (sections 2.3 and 4)
               r5_score.py -> score_r61_fast.txt         the 60-mission score (section 4)
               suite_extra.py -> suite_extra_r61.json / .txt; pivot_rates.py -> pivot_rates_r61.txt
               walker_seen_final.txt, walker_close_to_hedge.txt   offline: is a standing person found? (section 2.4)
               replay_level1_pickup.txt, replay_level2_pickup.txt offline replay of a whole pick-up on a spoiled lidar (section 2.3)
               walker_seen_offline.txt                   the same table from before the scan filter was widened (kept for the record)
               mk_facts_r61.py -> facts_r61.json         texts of sheet 18
sitl/          <run folder>__<scenario>__s<seed>.json   the result file of every mission run of revision 6.1
               r61f_ = fast cruise on, r61s_ = start settings, r61v_ = every seed at 1.0 m/s, r61b1_ / r61b2_ = worse lidar level 1 / 2,
               r61m_ = middle option, r61x_ = baseline with the walker rule off, r61_ and r61t_ = development runs
               before_fixes/   runs from before each change of section 2.2 and section 5
               traces/         full time traces (gzip) of the people cases that the note discusses and of the turn tests
drawing_scripts/  draw_sheets.py (revision 6.1 labels, sheet 18), draw_sheets_r6.py (as revision 6), build_model.py, make_pdf.py

Firmware: ArduPilot Rover 4.7.2 in simulation (not in the pack). The other agent's B2-F scripts are needed beside b2f_companion_x.py.
Everything here is simulation. Sensor figures are assumed until measured on the built robot.
