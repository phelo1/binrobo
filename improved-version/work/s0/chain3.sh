#!/bin/bash
# after the corrected-mass gate: the same gate with the castor-beam stops at +/-2 deg, then with the S12 sections' weight (stops +/-5 deg)
cd /home/claude/s0
while pgrep -f "run_batch.py var_leanm.txt" > /dev/null; do sleep 20; done
python3 run_batch.py var_leanm_s2.txt /home/claude/b2f_run/revG/sim/cg 2 /home/claude/s0/logs_leanm_s2 > var_leanm_s2.out 2>&1
python3 run_batch.py var_leanS12.txt /home/claude/b2f_run/revG/sim/cg 2 /home/claude/s0/logs_leanS12 > var_leanS12.out 2>&1
