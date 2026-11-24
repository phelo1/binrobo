#!/bin/bash
# 24 Nov, part 4: the close cases again with every seed at the full 1.0 m/s (in part 1 two of the three seeds met the person at 0.7 m/s, the degraded-fix limit)
cd /home/claude/s0
until grep -q "final chain done" r6/chain_r6.log; do sleep 10; done
SIDE_TRIG=3.0 r6/stress.sh r6/env_r6_fast_v10.sh r6v near31 near26 near20 run26 run20
echo "part 4 done $(date +%T)" >> r6/chain_r6.log
