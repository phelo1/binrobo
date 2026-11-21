#!/bin/bash
# Fault-injection tests of the second-pass guards: scenario 'tune' (s 290 -> 380, full 240 L bin), seed 7.
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 X_R5B=1 B2F_SEG=290,380
INST=${1:-0}
run() { echo "fault $1 start $(date +%T)" >> r5/chain_r5b.log; X_FAULT="$2" ./sitl_run_x.sh r5bf_fault_$1 /home/claude/s0/r5/sitl_q_tune7.txt $INST; }
run none ""
run steerL8 "steer:300:8:0.6"
run steerR40 "steer:300:40:-0.6"
run steerL90 "steer:300:90:0.6"
run cam05 "cam:300:30:0.5"
run cam25 "cam:300:30:2.5"
run lidp08 "lid:300:30:0.8"
run lidm05 "lid:300:30:-0.5"
echo "fault end $(date +%T)" >> r5/chain_r5b.log
