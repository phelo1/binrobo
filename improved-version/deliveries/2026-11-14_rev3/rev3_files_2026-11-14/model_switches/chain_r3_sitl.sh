#!/bin/bash
# Revision 3 driving-software check: 152.2 kg, trip budget 65 Wh, camera error drawn afresh at every check, refusal after 3 re-alignments, drive home after a refused grab.
cd /home/claude/s0
export B2F_PARAMS="ARMING_SKIPCHK -1" X_COMP=b2f_companion_x X_FIX_RCA=1 X_FIX_RCB=1 X_FIX_RCC=1 X_FIX_APP=1 X_NOSE_DX=0.065 X_ROB_MASS=152.2 X_LIFT_SCALE=1.4 X_CAM_RNG=1 X_CAM_REFUSE=1 X_CAM_TRIES=3 X_FIX_RTH=1 X_TRIP_WH=65
echo "sitl start $(date +%T)" >> chain_r3_sitl.log
( ./sitl_run_x.sh r3 /home/claude/s0/sitl_q_r3_i0.txt 0 ) &
sleep 20
( ./sitl_run_x.sh r3 /home/claude/s0/sitl_q_r3_i1.txt 1
  echo "main queue 1 done $(date +%T)" >> chain_r3_sitl.log
  X_CAM_SIG=0.025 X_CAM_BIAS=0.010 X_CAM_MISS=0.2 ./sitl_run_x.sh r3camA /home/claude/s0/sitl_q_r3cam.txt 1
  X_CAM_BIAS=0.060 ./sitl_run_x.sh r3camB /home/claude/s0/sitl_q_r3cam.txt 1
  echo "camera stress done $(date +%T)" >> chain_r3_sitl.log ) &
wait
echo "sitl end $(date +%T)" >> chain_r3_sitl.log
