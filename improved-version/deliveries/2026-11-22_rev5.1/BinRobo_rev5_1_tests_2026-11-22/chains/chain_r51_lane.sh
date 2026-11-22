#!/bin/bash
# 22 Nov: revision 5 robot (180.0 kg) on the lane WITHOUT the assumed 12 % pitch (X_LANE_WORLD=lane_world_real: EU-DEM profile, steepest 8.4 %).
# Made-good lane. Full bin down, empty return, worst-case trip, stop-and-hold with a full bin on the steepest part, and the empty robot coming
# down the steepest part nose first (as the mission software drives) and tail first, on a wet surface (grip 0.30) and on wet leaves (0.22).
cd /home/claude/s0
echo "lane start $(date +%T)" >> r51/lane_r51.log
LP=/home/claude/b2f_run/work/b2f_lanephys
E="X_LANE_WORLD=lane_world_real X_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.245 X_LIFT_V=0.013 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r5.json B2F_PAD_IN=-0.015 X_ACT_N=6800 X_VLOOK=3 X_VSLOPE=-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.3,0.06:0.3:0.2,0.09:0.2:0.2"
G='{"pad_ret":0.0,"lift_extra1":0.15,"pad_stroke":0.045,"act_N":6800.0}'; V='{"step":"ramp","trench":"covered","pothole":"filled"}'
LC=/home/claude/b2f_review/variants/lane_chain.sh
( env $E CGB_GEO="$G" X_VARIANT="$V" bash $LC runs_r51_real P1 P2a_pf
  echo "lane A end $(date +%T)" >> r51/lane_r51.log
  for m in 0.857:w30 0.629:w22; do d=runs_r51_real_${m#*:}; mkdir -p $LP/$d; [ -e $LP/$d/P2a_pf ] || cp -r $LP/runs_r51_real/P2a_pf $LP/$d/P2a_pf
    env $E CGB_GEO="$G" X_VARIANT="$V" X_MU_SCALE=${m%:*} bash $LC $d X8n X9n X8t X9t; done ) &
( sleep 5; env $E CGB_GEO="$G" X_VARIANT="$V" bash $LC runs_r51_real P7
  until [ -f $LP/runs_r51_real/P1/result.json ]; do sleep 20; done
  env $E CGB_GEO="$G" X_VARIANT="$V" bash $LC runs_r51_real P4a P4b P6a_person_estop ) &
wait
echo "lane end $(date +%T)" >> r51/lane_r51.log
