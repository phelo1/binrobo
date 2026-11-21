#!/bin/bash
# Bend stress: scenario 'tune' s 40 -> 110 (the sharp bend at s 73-77 under the tree-cover satellite model), full 240 L bin, seeds 1..40.
# Second pass first, then the first-pass software for comparison.
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 B2F_SEG=40,110
echo "bend b start $(date +%T)" >> r5/chain_r5b.log
X_R5B=1 ./sitl_run_x.sh r5b_bend40 /home/claude/s0/r5/sitl_q_tune40.txt 2
echo "bend a start $(date +%T)" >> r5/chain_r5b.log
./sitl_run_x.sh r5a_bend40 /home/claude/s0/r5/sitl_q_tune40.txt 2
echo "bend end $(date +%T)" >> r5/chain_r5b.log
