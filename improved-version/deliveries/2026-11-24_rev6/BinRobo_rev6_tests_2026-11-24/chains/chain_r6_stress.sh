#!/bin/bash
# people stress tests, slow settings then fast settings (same code)
cd /home/claude/s0
r6/stress.sh r6/env_r6.sh r6s
SIDE_TRIG=3.0 r6/stress.sh r6/env_r6_fast.sh r6f
echo "stress all done $(date +%T)" >> r6/chain_r6.log
