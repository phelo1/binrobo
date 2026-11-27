#!/bin/bash
# What the driving day looks like if the castors get brakes: speed rule C (0.5 m/s to 6 % downhill, 0.4 m/s steeper), robot 4 kg heavier. Four missions.
cd /home/claude/s0
while ! grep -q "sitl end" r4/chain_r4_sitl.log 2>/dev/null; do sleep 10; done
export B2F_PARAMS="ARMING_SKIPCHK -1" X_COMP=b2f_companion_x X_FIX_RCA=1 X_FIX_RCB=1 X_FIX_RCC=1 X_FIX_APP=1 X_NOSE_DX=0.324 X_ROB_MASS=181.6 X_LIFT_SCALE=0.8 X_CAM_RNG=1 X_CAM_REFUSE=1 X_CAM_TRIES=3 X_FIX_RTH=1 X_TRIP_WH=75
export X_CAM_AVG=3 X_GATE_CAM=1 X_FINAL_CAM=1 X_SEAT=0.030 X_VSLOPE="-1:0.5:0.5,0.06:0.4:0.4"
( ./sitl_run_x.sh r4ruleC /home/claude/s0/r4/sitl_q_r4c_i0.txt 0 ) &
sleep 20
( ./sitl_run_x.sh r4ruleC /home/claude/s0/r4/sitl_q_r4c_i1.txt 1 ) &
wait
echo "sitlC end $(date +%T)" >> r4/chain_r4_sitl.log
