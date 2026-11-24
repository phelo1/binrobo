#!/bin/bash
# 24 Nov: reproduce the reviewers' contact case with the revision 5.1 settings: someone steps out 2.6 m ahead at night and stands 60 s.
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 X_R5B=1 X_PPL_PAUSE=1 X_TRIP_WH=80
export X_VSLOPE="-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.06:0.2:0.15"
echo "repro start $(date +%T)" >> r6/chain_r6.log
( X_MOVER="person:pause:60,person:trigger_d:2.6" ./sitl_run_x.sh r6_repro_near26 /home/claude/s0/r6/q_s5a_7.txt 0 ) &
sleep 20
( X_MOVER="person:pause:60,person:trigger_d:2.6" ./sitl_run_x.sh r6_repro_near26 /home/claude/s0/r6/q_s5a_11_23.txt 1 ) &
wait
echo "repro end $(date +%T)" >> r6/chain_r6.log
