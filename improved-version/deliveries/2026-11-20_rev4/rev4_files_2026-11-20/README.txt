BinRobo improved version, revision 4 - files behind REPLY_and_REV4_2026-11-20.md
Prepared 20 November 2026 by the reviewer/tester agent, for Brian and the B2-F author.

Everything here was run on MuJoCo 4.0.1 with the B2-F author's own scripts (revG/sim/cg, work/b2f_lanephys, sitl/b2f),
unchanged, plus the switches below. The driving-software runs used ArduRover 4.7.2. The review package of 15 Nov was read, not run.

1. MODEL SWITCHES (model_switches/)
   make_simB2hx.py     writes h2/simB2hx.py from the unchanged h2/simB2h.py. All switches are off by default. New on 20 Nov:
                         X_BOOST=<N m>     short torque boost: when a drive wheel turns at under 30 % of its commanded speed for 0.4 s the
                                           torque cap rises to this value for at most X_BOOST_T (3 s), then rests X_BOOST_COOL (5 s)
                         X_CBRAKE=<N m>    brakes on the two castor wheels (tested as an option; not part of revision 4)
                         X_LIFT_V=<m/s>    lift speed cap (0.013 used: the 6.8 kN outdoor actuator)
                       Torque cap, lift force cap and pad stiffness go in through CGB_GEO (tcap, act_N, pad_k).
   runY.py             my own test script, run from revG/sim/cg. Results are B2F_Y_<name><tag>.json.
                         pstop <v> <grade> <grip> <bin kg|0> <reaction s> [rev]   bumper touch on the move: distance to standstill
                         lower <block mm> <L|both> <bin kg> <margin mm> [nocheck]  lowering onto a block under the bin wheels, with the
                                                                                   load-drop guard (X_LOWER_V: lowering speed, default 0.006)
                         liftpeak <step|kerb> <one|both|nose|tail> <v>   their step and kerb drives with the lift, wheel, comb and pad peaks
                                                                         (X_STEP_AT distance to the step, X_STEP_YAW approach angle, X_STEP_H height)
                         stepempty <one|both> <v>                        the robot without a bin over the step
                         lat <bin kg>                                    sideways force on a drive tyre in turns, pivots and cross-slope stops
   env_r4.sh           the revision 4 switches as one file to source.
   lanerun_x.py        my copy of the lane script. New: X_ACT_N (lift cap), X_VSLOPE (slope speed rule), X_VMAX.
   b2f_companion_x.py  my copy of the driving-software companion. New: X_GATE_CAM (the pre-grab gate decides on a camera reading; the true
                       offset is only logged), X_FINAL_CAM (the last reverse steers on the camera reading), X_CAM_AVG (frames averaged),
                       X_SEAT (seating check at the dock before the lift, from the leg-tip gap sensors), X_VSLOPE, X_VMAX; a refused trip
                       now ends with trip_end; gate and seating refusals are counted in metrics.refused.
   chain_r4*.sh        the queues as they were run.

   Revision 4 environment for a mechanical run (from revG/sim/cg):
     CGB_F9=1 CMP_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.34 X_LIFT_V=0.013 CMP_COMB_HW=0.35
     X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=<mass_cgB2_r4.json> B2F_PAD_IN=-0.015
     CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15,"pad_stroke":0.045,"act_N":6800.0}' B2_DOCK=front CMP_PREFIX=B2F_ IT1_TAG=<tag>
   Lane runs: X_SIM=simB2hx plus the same switches, X_ACT_N=6800, X_VSLOPE=-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.09:0.2:0.15,
     X_RUNS_DIR=<dir>, X_VARIANT='{"step":"ramp","trench":"covered","pothole":"filled"}'
   Driving software: B2F_PARAMS="ARMING_SKIPCHK -1" X_COMP=b2f_companion_x X_FIX_RCA=1 X_FIX_RCB=1 X_FIX_RCC=1 X_FIX_APP=1
     X_NOSE_DX=0.324 X_ROB_MASS=177.6 X_LIFT_SCALE=0.8 X_CAM_RNG=1 X_CAM_REFUSE=1 X_CAM_TRIES=3 X_FIX_RTH=1 X_TRIP_WH=75
     X_CAM_AVG=3 X_GATE_CAM=1 X_FINAL_CAM=1 X_SEAT=0.030 X_VSLOPE=(as above)
   X_VSLOPE format: "<downhill grade>:<m/s with a bin>:<m/s empty>,..." - every entry whose grade is reached applies; -1 means everywhere.

2. INPUTS (inputs/)
   mass_cgB2_r4.json      revision 4 weight table, built from the drawn solids: 177.60 kg.
   solids_r4.json         volume and bounding box of every drawn solid; mass_from_solids_r4.py turns it into tables/mass_table_r4.md.
   mass_cgB2_r3s.json     revision 3 table (152.20 kg), for comparison.

3. RESULT TAGS (file names B2F_<case><tag>.json)
   results_mechanical/        _r4, _r4_s303, _r4_s403, _r4_s503   revision 4 at 177.6 kg, 60 N m: full gate, 180 pick-ups, nose-uphill climbs
                              (S7), high-bin statics, their S5/S6 load cases, stress cases (_pm110 = 195 kg, _pm090, _pmu085, _pcrr09).
   results_torque_boost/      _r4b   the same gate, climb and load cases with the 100 N m boost switched on (information; not adopted).
                              tables/boost_compare_r4.txt: no verdict changes in 47 pairs.
   results_maps_and_safety/   B2F_Y_pstop_*      person-stop map (empty, full bin, tail first, braked castors, 195 kg, reaction 0.10/0.20 s)
                              B2F_Y_lower_*      lowering guard (…_v13 = at 13 mm/s)
                              B2F_Y_liftpeak_step_*_r4w<mm><t60|b100>   40 mm step by castor strip width; _at30 = step 3.0 m ahead (castors
                                                 trailing) instead of their 1.6 m; _yawNN = meeting the edge at NN degrees; _hNN = step height
                              B2F_Y_stepempty_*  the same without a bin
                              B2F_S7_*_r4w<mm>   slippery hill start by castor strip width
                              B2F_Y_liftpeak_kerb_*_r4cap12[tNN]  kerb with the lift cap raised to 12 kN (rigid tyre, and tyres t20/t30/t65)
                              B2F_Y_lat_*        sideways drive-tyre force
   results_exploration_on_rev3/   _x4...  the same kinds of runs on the revision 3 model (152.2 kg), made first to check the review's findings.
   results_lane/              runs_r4_pf (step ramped, trench covered, pothole filled, plus the as-is step, pothole, trench and person cases),
                              runs_r4_b100 (as-is features with the boost), runs_r4_sharp (empty return over the sharp step).
   results_driving/           60 missions (20 scenarios x seeds 7, 11, 23) with score.json.
   results_driving_other_speed_rules/   r4_ruleA_partial (4 missions under the first, faster rule: 0.5 m/s on the level with a bin) and
                              r4ruleC (4 missions under the rule that castor brakes would allow, robot at 181.6 kg).
   results_driving_camera_stress/   r4camA (noise 25 mm, bias 10 mm, 20 % missed frames), r4camB (bias 60 mm), r4camC (bias 80 mm),
                              r4camBnoseat (bias 60 mm without the seating check).

4. TABLES (tables/)
   mass_table_r4.md, clash_r4.json, facts.json (speed rule and notes printed on sheet 17), pstop_r4.json, the collected gate, pick-up,
   structure and driving tables (pack_tables/), and the scripts that made them.

5. DRAWING SCRIPTS (drawing_scripts/)
   r4_patch.py writes build_model.py from build_model_r3.py; r4_sheets_patch.py writes draw_sheets.py from draw_sheets_r3.py;
   clash_check.py is the solid-overlap and lift-sweep check (--qmin, --step).

Known limits are listed in section 7 of the reply note.
