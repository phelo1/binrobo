#!/bin/bash
# Revision 5 mechanical chain (180.0 kg): list A (stops, lowering, edges, kerb), then the full campaign (gate, 180 pick-ups, loads, climbs).
cd /home/claude/s0
echo "r5 a start $(date +%T)" >> r5/chain_r5.log
python3 run_batch.py r5/q_r5_a.txt /home/claude/b2f_run/revG/sim/cg 2 r5/logs/r5_a > r5/q_r5_a.out 2>&1
echo "r5 all start $(date +%T)" >> r5/chain_r5.log
python3 run_batch.py r5/q_r5_all.txt /home/claude/b2f_run/revG/sim/cg 2 r5/logs/r5_all > r5/q_r5_all.out 2>&1
echo "r5 all end $(date +%T)" >> r5/chain_r5.log
