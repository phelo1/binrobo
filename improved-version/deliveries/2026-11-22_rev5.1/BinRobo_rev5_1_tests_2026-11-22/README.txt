BinRobo improved version, revision 5.1 - test pack of 22 November 2026
======================================================================
Follow-up to Brian's answers of 22 November (no certified parts, pause for anyone near, the lane is not that steep, any time of day,
used parts are fine). The hardware model is that of revision 5; this pack holds only what is new. The revision 5 pack of 21 November
(BinRobo_rev5_tests_2026-11-21.zip) is still needed for everything else.

software/      b2f_companion_x.py            mission software as run here: revision 5 final + pause rule (X_PPL_PAUSE) + test clock (X_CLOCK)
               b2f_companion_x_rev5_final.py the revision 5 file, for a diff
               b2f_runner_x.py               mission runner (unchanged since the revision 5 person tests: X_MOVER)
               lanerun_x.py                  lane-physics runner; new switch X_LANE_WORLD
               make_lane_world_real.py       writes lane_world_real.py from the other agent's lane_world.py with the 12 % overlay off
               code.md5
chains/        the command lists and chain scripts exactly as run, with their logs
tables/        lane_grade.py + lane_grade_r51.*        slope of the lane from the two elevation models in route.json
               pstop_tab.py + pstop_real_slope_r51.*   38 stop-after-a-touch tests on slopes of 0 to 10 %
               lane_tab.py + lane_real_slope_r51.*     lane-physics runs on the real slope, with the revision 5 runs on the 12 % pitch
               person_tab.py + person_pause_r51.json   18 pause-rule runs
               people_mc_r51.py + people_mc_r51.*      how close a person can appear (sheet 18 table)
               cost_r51.py + cost_r51.md/json          cost with used parts
               mk_facts_r51.py + facts_r51.json        texts of sheets 17 and 18
               score_r51_final.md                      the revision 5 score script on the six final missions
stop_tests/    result file of each stop test (MuJoCo gate rig, the other agent's cg/ scripts through r4/runY.py)
lane/          result.json of each lane-physics run: runs_r51_real* (revision 5 speeds), runs_r51_v51_* (revision 5.1 speeds);
               suffix m35 / w30 / w22 = leaf-zone grip 0.35 / 0.30 / 0.22
sitl/          result.json of each mission run:
               r51_s5a, r51_person60, r51_person60near, r51_person60near_day, r51_person200   pause rule, revision 5 speeds
               r51_trip_candidate   s1a, s1b with a first version of the speed rule (3 to 6 % empty still at 0.3 m/s)
               r51_final            s1b, s3a, s3b, s5a x3 with the revision 5.1 settings
               r51_final_ret1630    three pick-ups from 16:30
               r51_late_quiet2230, r51_late_anytime   drop-off started at 23:30, with and without the quiet-hours limit
drawing_scripts/  draw_sheets.py (5.1), draw_sheets_r5.py (as issued 21 November), make_pdf.py

Settings of revision 5.1 (on top of r5/sitl_env_r5.sh of the revision 5 pack):
  X_KL_GAP=0.42 X_R5B=1 X_PPL_PAUSE=1
  X_VSLOPE="-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.06:0.2:0.15"
  X_QUIET_END=1800      (no quiet-hours limit; used in r51_late_anytime only)
  recommended, not run: X_TRIP_WH=80
Lane physics: X_LANE_WORLD=lane_world_real

The names of the lane tests (P4a "12 % pitch DOWN" and so on) are the other agent's and are unchanged; with X_LANE_WORLD=lane_world_real
the steepest slope they meet is 8.4 %.
