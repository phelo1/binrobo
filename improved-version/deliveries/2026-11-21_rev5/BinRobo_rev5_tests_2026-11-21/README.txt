BinRobo improved version, revision 5 - files behind REPLY_and_REV5_2026-11-21.md
Prepared 21 November 2026 by the reviewer/tester agent, for Brian and the B2-F author.

Everything here was run on MuJoCo 4.0.1 with the B2-F author's own scripts (revG/sim/cg, work/b2f_lanephys, sitl/b2f),
unchanged, plus the switches below. The driving-software runs used ArduRover 4.7.2. The review package of 21 Nov was read, not run.

1. MODEL SWITCHES (model_switches/)
   make_simB2hx.py     writes h2/simB2hx.py from the unchanged h2/simB2h.py (as in revision 4).
   runY.py             my own test script, run from revG/sim/cg. Results are B2F_Y_<name><tag>.json. New on 21 Nov:
                         lower ...            a ToF ray under each bin wheel: output "tof" = bare reading, reading with the block, how much short;
                                              X_TRIP_N overrides the 80 N minimum trip level of the load guard (tag _nNN)
                         stepempty / liftpeak X_STEP_AT (distance to the edge, m), X_STEP_H (edge height, m), X_STEP_YAW (approach angle)
   env_r5.sh           the revision 5 switches for a mechanical run (X_NOSE_DX=0.245, mass_cgB2_r5.json).
   lanerun_x.py        my copy of the lane script. New: rev (tail first) in a drive step, X_VLOOK (slope rule looks this many metres ahead),
                       X_VREV, X_MU_SCALE (grip scale for the whole run), runs X8n/X8t (empty robot down the 12 % pitch, person steps in,
                       nose first / tail first) and X9n/X9t (stop and hold half-way down).
   b2f_companion_x.py  my copy of the driving-software companion AS RUN in the second pass (md5 in r5b_code.md5).
                       First-pass switches: X_KL_GAP (keep-left gap), X_VREV, X_VLOOK, X_BYELAW=1 (two windows, measured trip time;
                       X_QUIET_END, X_PICK_FROM, X_TRIP_MIN, X_PICKUP_CLOCK), X_NAV_CAM=1 (camera reading of the left edge; X_NAV_CAM_SIG,
                       X_NAV_CAM_MISS), X_LID_FACE_OFF=1 (stress: no lidar hedge faces), X_NOFIX_NOW=1, X_BEND_KEEP=1 (trial, not adopted).
                       Second pass, all behind X_R5B=1: stop command latches the heading; hedge faces ignore the 20-degree cone ahead and
                       look to 4.5 m on the far side; camera model follows the left boundary only; disagreement rule (fits the lane width,
                       else the nearer); side guard 0.35 m right / 0.20 m left; protective field (X_PF_D 0.60 m, X_PF_W 0.08 m);
                       heading-command rate limit (X_HDG_RATE 0.15 rad/s); pivot cap (X_PIVOT_RATE 0.20 rad/s); bin outline per scan.
                       Tests only: X_FAULT='<lid|cam|steer>:<station>:<seconds>:<value>,...'.
                       Added after the 60 missions: camera person check (X_CAM_PEOPLE default 1, X_PPL_W 0.50 m, X_PPL_P detection probability).
                       It does nothing unless a person or dog is in the scenario. r5b_code.md5 lists which runs used which file.
   b2f_companion_x_as_run_for_the_60.py   the companion exactly as it ran the 60 second-pass missions (before the camera person check).
   b2f_companion_x_widecorridor_trial.py  a lidar-only cure for the person-beside-the-path case that did not work (kept for the record).
   b2f_companion_x_first_pass.py   the companion as it ran the first 60 missions; b2f_companion_x_rev4.py the revision 4 one.
   r5b_patch_companion.py          the first step of the second pass as a patch script, with notes on the later hand edits.
   b2f_runner_x.py     my runner. New, tests only: X_GPS_FAULT='<s0>:<s1>:<direction deg>:<metres>' (Float quality with a position bias) and
                       X_MOVER='person:pause:60,person:trigger_d:3.5' (change the person or dog of a scenario).
   sitl_env_r5.sh      the revision 5 driving-software switches; chain_r5*.sh the queues as they were run; chain_r5*.log when.

   Revision 5 lane runs: X_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.245 X_LIFT_V=0.013
     CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=<mass_cgB2_r5.json> B2F_PAD_IN=-0.015
     X_ACT_N=6800 X_VLOOK=3 X_VSLOPE=-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.3,0.06:0.3:0.2,0.09:0.2:0.2
   X_VSLOPE format: "<downhill grade>:<m/s with a bin>:<m/s empty>,..." - every entry whose grade is reached applies; -1 means everywhere.

2. INPUTS (inputs/)
   mass_cgB2_r5.json      revision 5 weight table, built from the drawn solids: 180.00 kg. solids_r5.json, mass_from_solids_r5.py as before.
   mass_cgB2_r4.json      revision 4 table (177.60 kg), for comparison.

3. RESULTS
   results_mechanical/        tag _r5 (and _r5_s303/_s403/_s503): gate G1-G9, 180 pick-ups, nose-uphill hill starts (S7), statics, the
                              review's S5/S6 load cases, 24 stress cases (_pm110 = 198 kg, _pm090, _pmu085, _pcrr09).
   results_maps_and_safety/   B2F_Y_pstop_*     person-stop map (…_rev = tail first, _r5pm110 = 198 kg)
                              B2F_Y_lower_*     ToF reading and load guard by block height (_v13 = 13 mm/s, _n50 = 50 N trip level,
                                                _nocheck = guard off)
                              B2F_Y_stepempty_*, B2F_Y_liftpeak_step_*   edges by height, run-up and angle (_r5at30 = 3 m run-up)
                              B2F_Y_liftpeak_kerb_*_r5cap12[t20]   kerb with the lift cap out of the way (rigid tyre; t20 = 650 N/mm tyre)
                              B2F_Y_lat_*       sideways drive-tyre force
   results_lane/              runs_r5_pf (lane made good, plus the as-is step, pothole, trench, person and dog cases),
                              runs_r5_w30 and runs_r5_w22 (empty robot on the 12 % pitch at grip 0.30 and 0.22: X8n, X8t, X9n, X9t).
                              NOTE: runs_r5_w22 X9n is marked PASS by the script but the robot slid 12 m; the note counts it as a failure.
   results_driving_first_pass/   the first 60 missions of revision 5 (X_R5B off). Contains the near hedge strike (s3a seed 7), the
                              turn-on-the-spot (s3a seed 23) and the false tipped alarm (s3b seed 7).
   results_driving/           the 60 missions with the second pass (X_R5B=1). score by the B2-F script, and tables/score_r5b.md with
                              the time window and energy budget restated for revision 5.
   results_driving_extras/    r5b_fix (the three failed missions and others re-run on the first version of the second pass; the bend and
                              position-fault runs below were made on the version just before the last pivot / path-start edits),
                              r5b_ret1630 (two pick-up days with the clock started at 16:30), r5b_m198 (198 kg, s1a seed 11),
                              r5b_camonly (no lidar hedge faces, s1a seed 7).
   results_driving_fault_tests/  r5bf_fault_* (the code of the 60 missions), r5b_fault_* (the same before the last pivot / path-start / reverse-speed edits, which
                              these lane-only runs do not exercise) and r5b1_fault_* (first version of the second pass: no heading-rate
                              limit, shorter and narrower field) on scenario "tune" s 290-380; r5a_gps_* / r5b_gps_* (Float with a 1.8 m bias before the bend, eight directions,
                              first pass / second pass); r5b_bend40 / r5a_bend40 (the bend under the tree-cover model, many seeds);
                              r5a_s4a16 / r5b_s4a16 (scenario s4a, 16 seeds: not a useful stress, its Float zone carries no position error).
   results_driving_person_tests/  scenario s5a with the person made to stand in the robot's path (X_MOVER):
                              r5b0_person60 / 60near / 200   on the code of the 60 missions (lidar logic alone): seed 23 passes the person at 0.16 m
                              r5b00_*, r5b01_*               two lidar-only cures that did not work (long-line face filter; that plus a wider corridor)
                              r5b_s5a_final, r5b_person60 / 60near / 200   final code with the camera person check
                              r5b_person60_nocam             final code with the camera person check switched off (control)
   results_keep_left_trials/  keep-left gap 0.42 / 0.35 / 0.30 m, and 0.42 m held through bends (r5kl42bk). First-pass software.

4. TABLES (tables/)
   mass_table_r5.md, clash_r5.json, facts.json (texts printed on sheets 17 and 18), collect_r5.json (gate, pick-ups), struct_r5.txt/.json
   (hand calculation), person_stop_r5.txt, people_mc_r5.txt (how close a person can appear), list_a_r5.txt (lowering, edges, kerb),
   lane_speed_r5.json (speed against the rule in the lane runs), cost_r5.md, score_r5a_firstpass.md, score_r5b.md, driving_stats_r5b.json,
   fault_tests_r5.md, gps_fault_bend_r5.json, bend40_r5.md, person_tests_r5.json, turn_rates_r5b.txt, and the scripts that made them.

5. DRAWING SCRIPTS (drawing_scripts/)
   r5_patch.py writes build_model.py from build_model_r4.py; r5_sheets_patch.py writes draw_sheets.py from draw_sheets_r4.py (the late
   label edits are noted at its end; draw_sheets.py here is the file that drew the sheets); clash_check.py is the overlap and sweep check.

Known limits are listed in section 5 of the reply note.
