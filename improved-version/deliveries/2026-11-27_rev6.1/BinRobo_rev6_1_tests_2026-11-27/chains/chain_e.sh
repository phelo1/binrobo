#!/bin/bash
# 27 Nov, third go (scan filter tightened near the lidar, pad wait on lane-watch objects), with the scan filter (X_LID_FILTER): a worse lidar and a real hedge (X_LID_BAD, b2f_r6.lid_degrade). Two levels. Trips with nobody about (how many false stops?),
# then the close people cases (is anyone missed?). Fast cruise on.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r61/env_r61_fast.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
LB1="drop=0.15,dark=0.3,burst=0.02,false=2,rag=0.10,sway=0.03,bram=0.02,bramd=0.2"
LB2="drop=0.3,dark=0.6,burst=0.1,false=6,rag=0.2,sway=0.08,bram=0.05,bramd=0.2"
echo "chain_e start $(date +%T)" >> r61/chain.log
clr r61b2_trip
X_LID_BAD="$LB2" X_TRIP_MIN=60 r61/run2.sh $F r61b2_trip $Q/q_s1a_7.txt $Q/q_s1b_7.txt
echo "bad-lidar trips done $(date +%T)" >> r61/chain.log
X_LID_BAD="$LB1" r61/stress.sh $F r61b1 near26 near20 run26 child35 side behind flank hug gapwalk26
X_LID_BAD="$LB2" r61/stress.sh $F r61b2 near26 near20 run26 child35 side behind flank hug gapwalk26
echo "bad-lidar people done $(date +%T)" >> r61/chain.log
