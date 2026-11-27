#!/bin/bash
# 27 Nov: step 6 of chain_g again (its mission lists had a relative path and nothing ran): the start settings (fast cruise off) on the frozen
# code: three drop-offs and three pick-ups (seeds 7, 11, 23), a three-drop mission and a three-pick-up mission (seed 7).
cd /home/claude/s0; ST=r61/env_r61_start.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
until grep -q "^chain_j done" r61/chain.log; do sleep 10; done
echo "chain_k start $(date +%T)" >> r61/chain.log
clr r61s_trips; X_TRIP_MIN=80 r61/run2.sh $ST r61s_trips /home/claude/s0/r61/q_start_i0.txt /home/claude/s0/r61/q_start_i1.txt
echo "chain_k done $(date +%T)" >> r61/chain.log
