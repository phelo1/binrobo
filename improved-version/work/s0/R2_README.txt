BinRobo improved version, revision 2 - files behind REV2_results_2026-11-14.md
Prepared 14 November 2026 by the reviewer/tester agent, for Brian and the B2-F author.

Everything here was run on MuJoCo 4.0.1 with the B2-F author's own scripts (revG/sim/cg, work/b2f_lanephys, sitl/b2f),
unchanged, plus the switches below. The driving-software runs used ArduRover 4.7.2 (no 4.6.2 build is available to me).

1. MODEL SWITCHES (model_switches/)
   make_simB2hx.py     writes h2/simB2hx.py from the unchanged h2/simB2h.py. All switches are off by default.
   make_lanerun_x.py   writes work/b2f_lanephys/lanerun_x.py from lanerun.py (X_SIM, X_RUNS_DIR, X_VARIANT, X_NOSE_DX).
   b2f_runner_x.py, b2f_companion_x.py   my copies of the driving-software runner and companion (X_NOSE_DX, X_ROB_MASS, X_LIFT_SCALE, X_FIX_*).
   lane_chain.sh, lane_r2.sh, lane_r2_extra.sh, run_batch.py, sitl_run_x.sh   the launchers used.

   Revision 2 environment for a gate run (from revG/sim/cg):
     CGB_F9=1 CMP_SIM=simB2hx X_LIFT_RANGE=0.34 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=5.46 X_NOSE_DX=0.065 CMP_COMB_HW=0.35
     X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 CGB_MASSF=<mass table> B2F_PAD_IN=-0.015 CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}'
     B2_DOCK=front CMP_PREFIX=B2F_ IT1_TAG=<tag>
   Lane runs: X_SIM=simB2hx plus the same switches, X_RUNS_DIR=<dir>, and for "pothole filled"
     X_VARIANT='{"step":"ramp","trench":"covered","pothole":"filled"}'
   Driving software: B2F_PARAMS="ARMING_SKIPCHK -1" X_COMP=b2f_companion_x X_FIX_RCA=1 X_FIX_RCB=1 X_FIX_RCC=1 X_FIX_APP=1
     X_NOSE_DX=0.065 X_ROB_MASS=119.4 X_LIFT_SCALE=1.4

2. INPUTS (inputs/)
   mass_cgB2_r2.json     revision 2, first weight table: 114.93 kg by the gate's count, 115.83 kg as built in the model.
   mass_cgB2_r2b.json    revision 2, corrected: adds bumper brackets 2.16 kg, mast foot plates 1.10 kg, hard stops and limit
                         switch 0.30 kg. 118.49 kg by the gate's count, 119.39 kg as built.
   mass_cgB2_B2F_S12.json  B2-F as designed plus the S12 items: 111.01 kg / 111.91 kg.
   mass_cgB2_imp.json    revision 1, corrected: 95.50 kg / 96.40 kg.
   R2_b2r.json, R2s_b2r.json   lane-fit footprints: B2F_b2r.json with the bumper 65 mm forward; R2s has pivot_D_sim 2.55.
   lanefit_ckpt_x.py     the B2-F author's lanefit_ckpt_h2.py with the paths changed, nothing else.

3. RESULT TAGS (results_gate/, file names B2F_<case><tag>.json)
   _r2, _r2_s303, _r2_s403, _r2_s503        revision 2 at 115.83 kg: full gate; extra clip-lid pick-up seeds.
   _r2b, _r2b_s303, _r2b_s403, _r2b_s503    revision 2 at 119.39 kg: full gate; extra clip-lid pick-up seeds.
   _pm110_r2, _pm090_r2, _pmu085_r2, _pcrr09_r2   stress cases at 115.83 kg.
   _b2fS12, _b2fS12_s303, _s403, _s503      B2-F as designed at its S12 weight (pick-ups, kerb, climbs, emergency stop only).
   _mj401_s303                              B2-F as designed at its own weight, one extra clip-lid seed (403 and 503 were not run).
   gate_B2F__r2.json, gate_B2F__r2b.json    the nine-criterion summaries from h2/summarize_h2.py.

4. LANE (results_lane/)
   runs_r2__*      revision 2 at 115.83 kg on the default lane (pothole OPEN): P1, P2a, P2c, P7 fail at the pothole;
                   plus the short stretches P5a, P5d, P5g (open trench: fails), P6a.
   runs_r2_pf__*   revision 2 at 115.83 kg, pothole filled: P1, P2a, P2c, P7, P3, P4a, P4b.
   runs_r2b_pf__*  revision 2 at 119.39 kg, pothole filled: the same seven plus P5a, P5d, P6a.

5. LANE FIT (results_lanefit/)
   lanefit_B2Fctl_b2r.json  control: the unchanged B2-F footprint through my copy; reproduces the stored result.
   lanefit_R2_b2r.json      revision 2 footprint with pivot_D_sim left at 2.39 (superseded).
   lanefit_R2s_b2r.json     revision 2 footprint with its own simulated loaded pivot diameter, 2.55 m. Use this one.
                            (At 119.39 kg the pivot test gives 2.56 m; the lane-pivot margins are 5 mm smaller than in this file.)

6. DRIVING SOFTWARE (results_driving/)
   One result.json per run, progress.txt, and score.json from the frozen b2f_score.py.
   54 of the 60 scored runs were made; s1a seeds 11 and 23, s3a seeds 11 and 23, s3b seeds 7 and 11 were left out for time.

   results_driving_B2F_heavier_frame/: two runs (s1a and s1b, seed 7) of B2-F's outline at 111.9 kg with the four fixes and
   unscaled lift times, to see whether the heavier frame alone breaks the 50 Wh trip limit.

7. DRAWINGS (drawing_scripts/)
   build_model.py -> model.pkl; draw_sheets.py -> 15 sheets; render.py, get_poses.py, check_model.py, make_pdf.py.
   They need the B2-F CAD source (cad_B2F_src.py) beside them, which is the B2-F author's file and is not included.
