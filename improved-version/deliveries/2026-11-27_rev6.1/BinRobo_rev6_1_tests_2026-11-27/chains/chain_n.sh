#!/bin/bash
# 27 Nov: three pick-ups at the start settings (fast cruise off) started at 16:30 in place of 18:00. Started at 18:00 the third does not
# fit before 21:00 and is refused (r61s_trips, s3b). One mission, seed 7, frozen code.
cd /home/claude/s0; ST=r61/env_r61_start.sh; O=/home/claude/sitl_out
until grep -q "^chain_m done" r61/chain.log; do sleep 10; done
echo "chain_n start $(date +%T)" >> r61/chain.log
if [ "$(find $O/r61s_ret1630 -name result.json 2>/dev/null | wc -l)" -lt 1 ]; then
  rm -rf $O/r61s_ret1630 /home/claude/b2f_run/sitl/b2f/ckpt_r61s_ret1630
  X_TRIP_MIN=80 X_PICKUP_CLOCK=16:30 r61/run2.sh $ST r61s_ret1630 /home/claude/s0/r61/q_s3b_7.txt
fi
echo "chain_n done $(date +%T)" >> r61/chain.log
