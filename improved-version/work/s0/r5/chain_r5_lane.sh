#!/bin/bash
# Revision 5 on the lane (180.0 kg): made-good lane, as-is features, and the empty robot down the 12 % pitch nose first and tail first.
cd /home/claude/s0
echo "lane start $(date +%T)" >> r5/lane_r5.log
LP=/home/claude/b2f_run/work/b2f_lanephys
E="X_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.245 X_LIFT_V=0.013 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r5.json B2F_PAD_IN=-0.015 X_ACT_N=6800 X_VLOOK=3 X_VSLOPE=-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.3,0.06:0.3:0.2,0.09:0.2:0.2"
G='{"pad_ret":0.0,"lift_extra1":0.15,"pad_stroke":0.045,"act_N":6800.0}'; V='{"step":"ramp","trench":"covered","pothole":"filled"}'
LC=/home/claude/b2f_review/variants/lane_chain.sh
( env $E CGB_GEO="$G" X_VARIANT="$V" bash $LC runs_r5_pf P1 P2a_pf P2c
  echo "lane A end $(date +%T)" >> r5/lane_r5.log
  for m in 0.857:w30 0.629:w22; do d=runs_r5_${m#*:}; mkdir -p $LP/$d; [ -e $LP/$d/P2a_pf ] || cp -r $LP/runs_r5_pf/P2a_pf $LP/$d/P2a_pf
    env $E CGB_GEO="$G" X_VARIANT="$V" X_MU_SCALE=${m%:*} bash $LC $d X8t X8n X9t X9n; done ) &
( env $E CGB_GEO="$G" X_VARIANT="$V" bash $LC runs_r5_pf P7 P3 P4a P4b
  env $E CGB_GEO="$G" bash $LC runs_r5_pf P5a_drop_sharp_3kN P6a_person_estop P6b_dog_crossing P5d_up_sharp_3kN P5h_pothole P5g_trench_open ) &
wait
echo "lane end $(date +%T)" >> r5/lane_r5.log
