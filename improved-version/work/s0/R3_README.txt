BinRobo improved version, revision 3 - files behind REPLY_and_REV3_2026-11-14.md
Prepared 14 November 2026 by the reviewer/tester agent, for Brian and the B2-F author.

Everything here was run on MuJoCo 4.0.1 with the B2-F author's own scripts (revG/sim/cg, work/b2f_lanephys, sitl/b2f),
unchanged, plus the switches below. The driving-software runs used ArduRover 4.7.2 (the 4.6.2 build in the review package
is for a different processor and does not run here). The review package itself was read, not run.

1. MODEL SWITCHES (model_switches/)
   make_simB2hx.py     writes h2/simB2hx.py from the unchanged h2/simB2h.py. All switches are off by default. New on 14 Nov:
                         X_POSTHOLD=<m>    seating check after the lift (0.030 used), X_POSTHOLD_SIG (8 mm), X_POSTHOLD_TRIES (2);
                                           every pick-up result also gets nib_y_mm (where the comb sits across the lip)
                         X_CAST_W=<m>      half-width of the castor tread on the ground (their model 0.025; 0.012 used = round-profile tyre)
                         X_CAST_SHOULDER=<m>  with X_CAST_W: shoulder rings out to the 50 mm width, lower than the centre strip by this much (0.003)
                         X_CAST_CROWN, X_CAST_TORS   castor wheel as an ellipsoid. NOT used in the final runs: it stalls at the 40 mm step
                         X_CAST_TRAIL      castor swivel offset (their 0.05; tried 0.035 and 0.025, not used)
                         X_ACC             acceleration limit on the drive command (tried, not used)
   env_r3.sh           the revision 3 switches as one file to source.
   b2f_companion_x.py  my copy of the driving-software companion. New: X_TRIP_WH, X_CAM_RNG, X_CAM_REFUSE, X_CAM_TRIES, X_FIX_RTH,
                         X_CAM_BIAS, X_CAM_MISS (the last two for stress runs only).
   s7_trace.py         the nose-uphill climb of h2/runX.py with heading, castor angles and wheel command logged over time.

   Revision 3 environment for a mechanical run (from revG/sim/cg):
     CGB_F9=1 CMP_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.065 CMP_COMB_HW=0.35
     X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=<mass_cgB2_r3s.json> B2F_PAD_IN=-0.015
     CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15,"pad_stroke":0.045}' B2_DOCK=front CMP_PREFIX=B2F_ IT1_TAG=<tag>
   Lane runs: X_SIM=simB2hx plus the same switches, X_RUNS_DIR=<dir>, X_VARIANT='{"step":"ramp","trench":"covered","pothole":"filled"}'
   Driving software: B2F_PARAMS="ARMING_SKIPCHK -1" X_COMP=b2f_companion_x X_FIX_RCA=1 X_FIX_RCB=1 X_FIX_RCC=1 X_FIX_APP=1
     X_NOSE_DX=0.065 X_ROB_MASS=152.2 X_LIFT_SCALE=1.4 X_CAM_RNG=1 X_CAM_REFUSE=1 X_CAM_TRIES=3 X_FIX_RTH=1 X_TRIP_WH=65

2. INPUTS (inputs/)
   mass_cgB2_r3s.json     revision 3 weight table, built from the drawn solids: 152.20 kg, and 152.19 kg as built in the simulator.
                          (The final drawing model gives 152.19 kg: 10 g of cable holes were added to the covers after the runs started.)
   solids_r3_final.json   volume and bounding box of every drawn solid; mass_from_solids.py turns it into the table (tables/mass_table_r3.md).
   mass_cgB2_r2b.json     revision 2 corrected table (118.49 kg), the source of the bought-in rows.
   mass_cgB2_r3.json, mass_cgB2_r3pre*.json, make_mass_r3.py   earlier hand-built estimates (141.6 to 142.7 kg), superseded.

3. RESULT TAGS (file names B2F_<case><tag>.json)
   results_mechanical/      _r3, _r3_s303, _r3_s403, _r3_s503   FINAL: revision 3 at 152.2 kg, narrow castor tread. Full gate, 180 pick-ups,
                            nose-uphill climbs (S7), high-bin statics (cg60), their S5/S6 load cases, 24 stress cases (_pm110, _pm090, _pmu085, _pcrr09).
                            _r3w0.008, _r3w0.012   the two castor tread widths tried on the step and the slippery climb, at 148 kg.
                            _r3sh, _r3sh2          shouldered castor wheel (X_CAST_W=0.012 X_CAST_SHOULDER=0.003, and 0.002 for one repeat): 32 spot checks and the
                                                   pothole load cases. _lsr004_r3sh is the pothole run with 18.8 kN on a wheel that is left out of the sizing.
                            _r3flat                flat 50 mm castor tread at 152.2 kg: slippery climb (fails), step, pothole.
                            _r3noph                narrow tread with the seating check off: pothole dock (still fails, so the check is not the cause).
                            gate_B2F__r3.json      the nine-criterion summary from h2/summarize_h2.py.
   results_first_passes/    _r3n, _r3p   preliminary structure, flat castor tread, 137.7 kg without and 142.7 kg with ballast.
                            _r3a         first table (142.5 kg), round-wheel castor: step "both" fails (simulator shape fault).
                            _r3c         148 kg, round-wheel castor (stopped during the pick-ups).
                            _r3d         148 kg, narrow tread (stopped when the carriage cross-beams were added).
                            s7_trace_*.json   time traces of the slippery climb for the variants named in the file.
   results_B2F_loads_on_4.0.1/   _mj401   the B2-F author's 29 load cases on their own B2-F model, re-run on MuJoCo 4.0.1.

4. LANE (results_lane/)   runs_r3_pf__*   revision 3 at 152.2 kg, step ramped, trench covered, pothole filled. lane_stuck.py is the stuck-time score.
   runs_r3_flat__, runs_r3_sh__, runs_r3_t80__P5d_up_sharp_3kN   the sharp 40 mm step up, repeated with the flat castor tread, the shouldered wheel
   (both stall) and with the wheel torque limit at 80 N m (CGB_GEO tcap 80: climbs). All start from the P1 snapshots of runs_r3_pf.

5. DRIVING SOFTWARE (results_driving/, results_driving_camera_stress/)
   One result.json per run, their scorer's score.json, progress.txt. 56 runs: all 48 short scenario runs and 8 of the 12 full missions
   (s1a and s1b seeds 7, 11, 23; s3a seed 7; s3b seed 23). s3a 11, s3a 23, s3b 7 and s3b 11 were not run. r3camA: camera noise 25 mm, offset 10 mm, 20 % of readings missing.
   r3camB: camera offset 60 mm (forces a refusal).

6. TABLES (tables/)
   mass_table_r3.md                        the weight table, one row per part.
   struct_r3.py, struct_r3_final.txt/json  my structure calculation and its output on the final loads.
   collect_r3.py, mech_r3.json             the mechanical results gathered into one file.
   loads_B2F_stored_vs_mujoco401.csv       stored load peaks (MuJoCo 3.17.0) against my re-run of the same cases (4.0.1).
   clash_r2.json, clash_r3.json            solid-against-solid interference, lift sweep and loom check for revisions 2 and 3.
   recount_r2b_summary.json, nib_r2b_*.jsonl   the recount of the 180 revision 2 pick-ups by comb position.
   sitl_r3_table.py, sitl_r3.json, lane_r3_stuck.json   driving-software and lane tables.

7. DRAWING SCRIPTS (drawing_scripts/)
   build_model_r2.py + r3_patch.py -> build_model.py (the model); draw_sheets_r2.py + r3_sheets_patch.py -> draw_sheets.py (the sheets);
   clash_check.py (interference, lift sweep, looms); solids_list.py (volumes for the weight table); render.py, get_poses.py, make_pdf.py.
