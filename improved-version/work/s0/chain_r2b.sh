#!/bin/bash
# B2-F comparison split over the two cores, then the driving-software check on a quiet machine (two simulator instances).
cd /home/claude/s0
( while pgrep -f "run_batch.py var_r2_pert.txt" > /dev/null; do sleep 10; done
  python3 run_batch.py var_b2f_cmpA.txt /home/claude/b2f_run/revG/sim/cg 1 /home/claude/s0/logs_b2f_cmpA > var_b2f_cmpA.out 2>&1 ) &
( while pgrep -f "lane_r2_extra.sh" > /dev/null; do sleep 10; done
  python3 run_batch.py var_b2f_cmpB.txt /home/claude/b2f_run/revG/sim/cg 1 /home/claude/s0/logs_b2f_cmpB > var_b2f_cmpB.out 2>&1 ) &
wait
while pgrep -f "lanefit_ckpt_x.py" > /dev/null; do sleep 10; done
export B2F_PARAMS="ARMING_SKIPCHK -1" X_COMP=b2f_companion_x X_FIX_RCA=1 X_FIX_RCB=1 X_FIX_RCC=1 X_FIX_APP=1 X_NOSE_DX=0.065 X_ROB_MASS=115.8 X_LIFT_SCALE=1.4
echo "sitl start $(date +%T)" >> chain_r2b.log
./sitl_run_x.sh r2 /home/claude/s0/sitl_q_r2_i1.txt 1 &
sleep 20
./sitl_run_x.sh r2 /home/claude/s0/sitl_q_r2_i0.txt 0 &
wait
echo "sitl end $(date +%T)" >> chain_r2b.log
