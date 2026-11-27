#!/bin/bash
# after the corrected-mass gate: 120 pick-ups of the clip-lid bin with a 700 mm comb (640 mm as designed)
cd /home/claude/s0
while pgrep -f "run_batch.py var_leanm.txt" > /dev/null; do sleep 20; done
python3 run_batch.py var_c700.txt /home/claude/b2f_run/revG/sim/cg 2 /home/claude/s0/logs_c700 > var_c700.out 2>&1
