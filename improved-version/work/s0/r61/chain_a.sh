#!/bin/bash
# 27 Nov: first checks of revision 6.1. Walker tracks (someone walks up and then stands quite still 2.3 m from the turning centre):
# c = at the road-end turn, from the house side; y = in the yard at the house, during or just before the loaded turn there.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r61/env_r61_fast.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
clr r61_stand_c r61_stand_y
PC='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":40,"pause_at":0.295,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PY='[{"kind":"person","a":[22,0.5],"b":[4,0.5],"along":true,"speed":1.0,"pause":40,"pause_at":0.609,"trig":[9.69,-1.36],"trigger_d":0.4,"delay":37}]'
echo "chain_a start $(date +%T)" >> r61/chain.log
( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PC"; ./sitl_run_x.sh r61_stand_c $Q/q_s1a_7.txt 0 ) &
sleep 15; ( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PY"; ./sitl_run_x.sh r61_stand_y $Q/q_s1a_7.txt 1 ) &
wait
echo "chain_a done $(date +%T)" >> r61/chain.log
