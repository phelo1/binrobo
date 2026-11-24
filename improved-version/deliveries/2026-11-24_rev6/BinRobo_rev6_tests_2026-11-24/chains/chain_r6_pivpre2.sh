#!/bin/bash
# 24 Nov, last: at a turn outside the yard a thing inside the zone that was not there a second ago counts as moving (b2f_r6.r6_near_pivot).
# Pivot test b on the code before this showed the turn running on for 1.4 s with the walker inside 3 m (kept in r6f_pivflank_before_fix3/b).
# b and a2 again; a (someone standing there before the turn); then a pick-up and a drop-off as a check on every other turn.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r6/env_r6_fast.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
mkdir -p /home/claude/sitl_out/r6f_pivflank_before_fix3
clr r6f_pivflank_a r6f_pivflank_a2 r6f_pivflank_b r6f_val3 r6f_val4
PA='[{"kind":"person","a":[626,-1.2],"b":[600,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.33,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PA2='[{"kind":"person","a":[626,-1.2],"b":[600,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.33,"trig":[617.9,0.19],"trigger_d":0.4,"delay":10}]'
PB='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.35,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
echo "pivpre2 start $(date +%T)" >> r6/chain_r6.log
( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PB"; ./sitl_run_x.sh r6f_pivflank_b $Q/q_s1a_7.txt 0 ) &
sleep 15; ( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PA2"; ./sitl_run_x.sh r6f_pivflank_a2 $Q/q_s1a_7.txt 1 ) &
wait
echo "pivot b a2 (arrival rule) done $(date +%T)" >> r6/chain_r6.log
printf "s1b 7\n" > $Q/q_val3_i1.txt
( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PA"; ./sitl_run_x.sh r6f_pivflank_a $Q/q_s1a_7.txt 0 ) &
sleep 15; ( source $F; export X_TRIP_MIN=45; ./sitl_run_x.sh r6f_val3 $Q/q_val3_i1.txt 1 ) &
wait
echo "pivot a + pick-up (arrival rule) done $(date +%T)" >> r6/chain_r6.log
