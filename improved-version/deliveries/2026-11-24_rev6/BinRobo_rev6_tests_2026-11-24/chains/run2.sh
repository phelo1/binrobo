#!/bin/bash
# usage: run2.sh <env file> <out name> <queue A> [queue B]  [extra env assignments are taken from the caller's environment]
cd /home/claude/s0; source $1; OUT=$2
echo "$OUT start $(date +%T)" >> r6/chain_r6.log
( ./sitl_run_x.sh $OUT $3 0 ) &
if [ -n "$4" ]; then sleep 15; ( ./sitl_run_x.sh $OUT $4 1 ) & fi
wait
echo "$OUT end $(date +%T)" >> r6/chain_r6.log
