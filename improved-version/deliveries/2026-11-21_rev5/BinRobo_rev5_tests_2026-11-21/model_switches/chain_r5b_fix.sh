#!/bin/bash
# Revision 5, second pass (X_R5B=1): targeted re-runs of the three missions that went wrong, the long-wait scenario, then the float-fix stress at the s 73 bend
# (scenario s4a, 16 seeds) with the first-pass software and with the second pass.
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42
echo "fix start $(date +%T)" >> r5/chain_r5b.log
( X_R5B=1 ./sitl_run_x.sh r5b_fix /home/claude/s0/r5/sitl_q_fix_i0.txt 0; X_R5B=1 ./sitl_run_x.sh r5b_s4a16 /home/claude/s0/r5/sitl_q_s4a16.txt 0 ) &
sleep 20
( X_R5B=1 ./sitl_run_x.sh r5b_fix /home/claude/s0/r5/sitl_q_fix_i1.txt 1; ./sitl_run_x.sh r5a_s4a16 /home/claude/s0/r5/sitl_q_s4a16.txt 1 ) &
wait
echo "fix end $(date +%T)" >> r5/chain_r5b.log
