#!/bin/bash
# 24 Nov: after the pivot fix (hedge faces fitted along the lane during a turn; one near-test for start, watch and restart)
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r6/env_r6_fast.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
PA='[{"kind":"person","a":[626,-1.2],"b":[600,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.33,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PB='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.35,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
clr r6f_pivflank_a r6f_pivflank_b r6f_val
echo "pivflank (after fix) start $(date +%T)" >> r6/chain_r6.log
( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PA"; ./sitl_run_x.sh r6f_pivflank_a $Q/q_s1a_7.txt 0 ) &
sleep 15; ( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PB"; ./sitl_run_x.sh r6f_pivflank_b $Q/q_s1a_7.txt 1 ) &
wait
echo "pivflank end $(date +%T)" >> r6/chain_r6.log
printf "s1a 7\ns3a 7\n" > $Q/q_val_i0.txt; printf "s1b 7\ns3b 11\n" > $Q/q_val_i1.txt
X_TRIP_MIN=45 r6/run2.sh $F r6f_val $Q/q_val_i0.txt $Q/q_val_i1.txt
echo "validation done $(date +%T)" >> r6/chain_r6.log
