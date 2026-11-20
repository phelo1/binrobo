#!/bin/bash
# Revision 4 driving-software check: 177.6 kg, nose at 1.43 m, trip budget 75 Wh, slope speed rule, camera-only gate, camera-steered final reverse,
# 3-frame camera average, seating check at the dock, refused trips closed. Two instances.
cd /home/claude/s0
export B2F_PARAMS="ARMING_SKIPCHK -1" X_COMP=b2f_companion_x X_FIX_RCA=1 X_FIX_RCB=1 X_FIX_RCC=1 X_FIX_APP=1 X_NOSE_DX=0.324 X_ROB_MASS=177.6 X_LIFT_SCALE=0.8 X_CAM_RNG=1 X_CAM_REFUSE=1 X_CAM_TRIES=3 X_FIX_RTH=1 X_TRIP_WH=75
export X_CAM_AVG=3 X_GATE_CAM=1 X_FINAL_CAM=1 X_SEAT=0.030 X_VSLOPE="-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.09:0.2:0.15"
echo "sitl start $(date +%T)" >> r4/chain_r4_sitl.log
( ./sitl_run_x.sh r4 /home/claude/s0/r4/sitl_q_r4_i0.txt 0; echo "queue 0 done $(date +%T)" >> r4/chain_r4_sitl.log
  X_CAM_SIG=0.025 X_CAM_BIAS=0.010 X_CAM_MISS=0.2 ./sitl_run_x.sh r4camA /home/claude/s0/r4/sitl_q_r4cam.txt 0
  X_CAM_BIAS=0.060 ./sitl_run_x.sh r4camB /home/claude/s0/r4/sitl_q_r4cam.txt 0 ) &
sleep 20
( ./sitl_run_x.sh r4 /home/claude/s0/r4/sitl_q_r4_i1.txt 1; echo "queue 1 done $(date +%T)" >> r4/chain_r4_sitl.log
  X_CAM_BIAS=0.080 ./sitl_run_x.sh r4camC /home/claude/s0/r4/sitl_q_r4cam.txt 1
  X_CAM_BIAS=0.060 X_SEAT=0 ./sitl_run_x.sh r4camBnoseat /home/claude/s0/r4/sitl_q_r4cam.txt 1 ) &
wait
echo "sitl end $(date +%T)" >> r4/chain_r4_sitl.log
