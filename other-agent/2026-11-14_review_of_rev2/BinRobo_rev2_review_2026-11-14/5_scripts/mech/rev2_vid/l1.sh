#!/bin/bash
# one lane chunk (r2_lane_q.sh), waits for the shared lock
S=$(date +%s); exec 9>/tmp/qr2.lock; flock -w 20 9 || { echo LOCKED; exit 0; }
B=$((104 - $(date +%s) + S)); [ $B -lt 60 ] && { echo short; exit 0; }
/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/work/b2f_lanephys/r2_lane_q.sh $((B-8)) 2>&1 | tail -3; date +%T
