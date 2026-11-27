#!/bin/bash
# after the corrected-mass gate: the same gate with the S12 sections' weight, then pick-ups and set-downs with 300 mm of lift travel
cd /home/claude/s0
while pgrep -f "run_batch.py var_leanm.txt" > /dev/null; do sleep 20; done
python3 run_batch.py var_leanS12.txt /home/claude/b2f_run/revG/sim/cg 2 /home/claude/s0/logs_leanS12 > var_leanS12.out 2>&1
python3 run_batch.py var_lean300m.txt /home/claude/b2f_run/revG/sim/cg 2 /home/claude/s0/logs_lean300m > var_lean300m.out 2>&1
