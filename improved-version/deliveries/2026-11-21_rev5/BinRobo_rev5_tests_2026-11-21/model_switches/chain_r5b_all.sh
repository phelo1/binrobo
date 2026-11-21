#!/bin/bash
# Revision 5, second pass: the 60 missions again, then the extras.
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 X_R5B=1
echo "r5b 60 start $(date +%T)" >> r5/chain_r5b.log
( ./sitl_run_x.sh r5b /home/claude/s0/r4/sitl_q_r4_i0.txt 0 ) &
sleep 20
( ./sitl_run_x.sh r5b /home/claude/s0/r4/sitl_q_r4_i1.txt 1 ) &
wait
echo "r5b 60 end $(date +%T)" >> r5/chain_r5b.log
( X_PICKUP_CLOCK=16:30 ./sitl_run_x.sh r5b_ret1630 /home/claude/s0/r5/sitl_q_ret_i0.txt 0; X_ROB_MASS=198.0 ./sitl_run_x.sh r5b_m198 /home/claude/s0/r5/sitl_q_m198.txt 0 ) &
sleep 20
( X_PICKUP_CLOCK=16:30 ./sitl_run_x.sh r5b_ret1630 /home/claude/s0/r5/sitl_q_ret_i1.txt 1; X_LID_FACE_OFF=1 ./sitl_run_x.sh r5b_camonly /home/claude/s0/r5/sitl_q_one.txt 1 ) &
wait
echo "r5b extras end $(date +%T)" >> r5/chain_r5b.log
