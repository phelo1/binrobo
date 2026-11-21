#!/bin/bash
# Extras on the final code: 198 kg robot (s1a seed 11) and camera-only edge keeping (s1a seed 7).
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 X_R5B=1
echo "extra2 start $(date +%T)" >> r5/chain_r5b.log
( X_ROB_MASS=198.0 ./sitl_run_x.sh r5b_m198 /home/claude/s0/r5/sitl_q_m198.txt 0 ) &
sleep 20
( X_LID_FACE_OFF=1 ./sitl_run_x.sh r5b_camonly /home/claude/s0/r5/sitl_q_one.txt 1 ) &
wait
echo "extra2 end $(date +%T)" >> r5/chain_r5b.log
