#!/bin/bash
cd /home/claude/s0/r3
while pgrep -f "recount_r2b.sh" > /dev/null; do sleep 5; done
( python3 /home/claude/s0/run_batch.py q_r3_loads.txt /home/claude/b2f_run/revG/sim/cg 1 /home/claude/s0/r3/logs_loads > q_r3_loads.out 2>&1 ) &
( python3 /home/claude/s0/run_batch.py q_r3_ballast.txt /home/claude/b2f_run/revG/sim/cg 1 /home/claude/s0/r3/logs_ballast > q_r3_ballast.out 2>&1 ) &
wait
