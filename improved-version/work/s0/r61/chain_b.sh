#!/bin/bash
# 27 Nov: walker tracks, second version (walking is judged only while the robot stands). c and y again, then a plain drop-off and pick-up
# (no stop with nobody about is the pass mark), then the same two trips with the firmware turn-rate limit ATC_STR_RAT_MAX 13 deg/s.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r61/env_r61_fast.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
mkdir -p /home/claude/sitl_out/r61_before_fixes; for n in r61_stand_c r61_stand_y; do [ -d /home/claude/sitl_out/$n ] && mv /home/claude/sitl_out/$n /home/claude/sitl_out/r61_before_fixes/${n}_walk_v1; done
clr r61_stand_c r61_stand_y r61_plain r61_ratmax
PC='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":40,"pause_at":0.295,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PY='[{"kind":"person","a":[22,0.5],"b":[4,0.5],"along":true,"speed":1.0,"pause":40,"pause_at":0.609,"trig":[9.69,-1.36],"trigger_d":0.4,"delay":37}]'
echo "chain_b start $(date +%T)" >> r61/chain.log
( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PC"; ./sitl_run_x.sh r61_stand_c $Q/q_s1a_7.txt 0 ) &
sleep 15; ( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PY"; ./sitl_run_x.sh r61_stand_y $Q/q_s1a_7.txt 1 ) &
wait
echo "stand c y (v2) done $(date +%T)" >> r61/chain.log
X_TRIP_MIN=45 r61/run2.sh $F r61_plain $Q/q_s1a_7.txt $Q/q_s1b_7.txt
echo "plain done $(date +%T)" >> r61/chain.log
R61_EXTRA='X_TRIP_MIN=45 B2F_PARAMS="$B2F_PARAMS;ATC_STR_RAT_MAX 13"' r61/run2.sh $F r61_ratmax $Q/q_s1a_7.txt $Q/q_s1b_7.txt
echo "ratmax done $(date +%T)" >> r61/chain.log
