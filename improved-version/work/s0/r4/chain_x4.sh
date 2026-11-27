#!/bin/bash
# exploration runs, 20 Nov: two workers, one list after the other
cd /home/claude/s0
for k in pstop step s7 lift seat soft tries1; do
  echo "$k start $(date +%T)" >> r4/chain_x4.log
  python3 run_batch.py r4/q_x4_$k.txt /home/claude/b2f_run/revG/sim/cg 2 r4/logs/x4_$k > r4/q_x4_$k.out 2>&1
  echo "$k end $(date +%T)" >> r4/chain_x4.log
done
