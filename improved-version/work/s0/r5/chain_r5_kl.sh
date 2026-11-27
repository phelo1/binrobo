#!/bin/bash
# keep-left gap trial: one drop mission at three gaps
cd /home/claude/s0; source r5/sitl_env_r5.sh
( X_KL_GAP=0.42 ./sitl_run_x.sh r5kl42 /home/claude/s0/r5/sitl_q_one.txt 0; X_KL_GAP=0.30 ./sitl_run_x.sh r5kl30 /home/claude/s0/r5/sitl_q_one.txt 0 ) &
sleep 20
( X_KL_GAP=0.35 ./sitl_run_x.sh r5kl35 /home/claude/s0/r5/sitl_q_one.txt 1 ) &
wait; echo "kl end $(date +%T)" >> r5/chain_r5_sitl.log
