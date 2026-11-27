#!/bin/bash
# when the suite is done: stop part 2 before it starts its own (longer) follow-up, start part 3
cd /home/claude/s0
until grep -q "suite fast done" r6/chain_r6.log; do sleep 5; done
pkill -f chain_r6_final2.sh; pkill -f "r6/run2.sh"; pkill -f sitl_run_x.sh; sleep 0.5; pkill -9 -f b2f_runner_x.py; pkill -9 -f "bin/ardurover"; sleep 2
echo "--- part 2 stopped after the suite, part 3 start $(date +%T)" >> r6/chain_r6.log
exec r6/chain_r6_final3.sh
