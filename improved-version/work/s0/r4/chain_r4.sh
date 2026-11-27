#!/bin/bash
# Revision 4 mechanical campaign: waits for the softer-pad exploration list, then list C (maps), the full campaign, the torque-boost subset
cd /home/claude/s0
while ! grep -q "soft end" r4/chain_x4.log; do sleep 5; done
pkill -f r4/chain_x4.sh; sleep 1; pkill -f "run_batch.py r4/q_x4_tries1.txt"
for k in c all; do
  echo "r4 $k start $(date +%T)" >> r4/chain_r4.log
  python3 run_batch.py r4/q_r4_$k.txt /home/claude/b2f_run/revG/sim/cg 2 r4/logs/r4_$k > r4/q_r4_$k.out 2>&1
  echo "r4 $k end $(date +%T)" >> r4/chain_r4.log
done
echo "r4 b start $(date +%T)" >> r4/chain_r4.log
python3 run_batch.py r4/q_r4b_sel.txt /home/claude/b2f_run/revG/sim/cg 2 r4/logs/r4b > r4/q_r4b_sel.out 2>&1
echo "r4 b end $(date +%T)" >> r4/chain_r4.log
