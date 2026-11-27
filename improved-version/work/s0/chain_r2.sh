#!/bin/bash
# after the revision 2 gate: its stress variations, then B2-F as designed for comparison (S12 weight; and the extra clip-lid seeds at its own weight)
cd /home/claude/s0
while pgrep -f "run_batch.py var_r2.txt" > /dev/null; do sleep 20; done
python3 run_batch.py var_r2_pert.txt /home/claude/b2f_run/revG/sim/cg 1 /home/claude/s0/logs_r2_pert > var_r2_pert.out 2>&1
python3 run_batch.py var_b2f_cmp.txt /home/claude/b2f_run/revG/sim/cg 1 /home/claude/s0/logs_b2f_cmp > var_b2f_cmp.out 2>&1
