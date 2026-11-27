#!/bin/bash
# 22 Nov: "any time" - a drop-off started at 23:30. With the quiet-hours limit at its old value (22:30) the software refuses it;
# with the limit taken off (X_QUIET_END=1800, i.e. 06:00 next morning) it runs.
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 X_R5B=1 X_PPL_PAUSE=1 X_CLOCK=23:30
export X_VSLOPE="-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.06:0.2:0.15"
until grep -q "final end" r51/chain_r51.log; do sleep 15; done
echo "late start $(date +%T)" >> r51/chain_r51.log
( ./sitl_run_x.sh r51_late_quiet2230 /home/claude/s0/r51/sitl_q_late.txt 0 ) &
sleep 20
( X_QUIET_END=1800 ./sitl_run_x.sh r51_late_anytime /home/claude/s0/r51/sitl_q_late.txt 1 ) &
wait
echo "late end $(date +%T)" >> r51/chain_r51.log
