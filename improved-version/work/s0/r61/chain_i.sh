#!/bin/bash
# 27 Nov: the "before" figure for the walker rule, on the frozen 6.1 code with only that rule switched off (X_R6_WALK=0):
# someone walks up, then stands quite still 2.3 m from the turning centre for 40 s, out of the camera's view. c = road end, y = yard.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r61/env_r61_fast.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
until grep -q "^chain_h done" r61/chain.log; do sleep 10; done
echo "chain_i start $(date +%T)" >> r61/chain.log
PC='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":40,"pause_at":0.295,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PY='[{"kind":"person","a":[22,0.5],"b":[4,0.5],"along":true,"speed":1.0,"pause":40,"pause_at":0.609,"trig":[9.69,-1.36],"trigger_d":0.4,"delay":37}]'
clr r61x_turn_c_nowalk r61x_turn_y_nowalk
( source $F; export X_R6_WALK=0 X_TRIP_MIN=45 X_MOVERS_SET="$PC"; ./sitl_run_x.sh r61x_turn_c_nowalk $Q/q_s1a_7.txt 0 ) & sleep 15
( source $F; export X_R6_WALK=0 X_TRIP_MIN=45 X_MOVERS_SET="$PY"; ./sitl_run_x.sh r61x_turn_y_nowalk $Q/q_s1a_7.txt 1 ) & wait
echo "chain_i done $(date +%T)" >> r61/chain.log
