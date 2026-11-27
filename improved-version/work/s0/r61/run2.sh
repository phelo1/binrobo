#!/bin/bash
# usage: run2.sh <env file> <out name> <queue A> [queue B]   (extra env assignments are taken from the caller's environment AFTER the env file)
cd /home/claude/s0; export X_LID_BAD; EXTRA="$R61_EXTRA"; source $1; [ -n "$EXTRA" ] && eval "export $EXTRA"; OUT=$2
echo "$OUT start $(date +%T)" >> r61/chain.log
( ./sitl_run_x.sh $OUT $3 0 ) &
if [ -n "$4" ]; then sleep 15; ( ./sitl_run_x.sh $OUT $4 1 ) & fi
wait
echo "$OUT end $(date +%T)" >> r61/chain.log
