#!/bin/bash
# 24 Nov, after the last chain: the look before a turn on the spot now lasts a full second (b2f_companion_x.pivot). The run of the final
# chain showed the turn starting with a person already standing 0.7 m from the robot (kept in r6f_pivflank_before_fix2/a).
# Also: the people rule now holds while the robot waits for the pad to clear (op_wait_clear).
# a = someone walks up from the road side BEFORE the turn and stands in the swept circle; a2 = the same, arriving DURING the turn;
# b = from the house side during the turn. Then a pick-up and a three-drop mission as a check on every other turn.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r6/env_r6_fast.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
clr r6f_pivflank_a r6f_pivflank_a2 r6f_pivflank_b r6f_val3
PA='[{"kind":"person","a":[626,-1.2],"b":[600,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.33,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PA2='[{"kind":"person","a":[626,-1.2],"b":[600,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.33,"trig":[617.9,0.19],"trigger_d":0.4,"delay":10}]'
PB='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.35,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
echo "pivpre start $(date +%T)" >> r6/chain_r6.log
( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PA"; ./sitl_run_x.sh r6f_pivflank_a $Q/q_s1a_7.txt 0 ) &
sleep 15; ( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PB"; ./sitl_run_x.sh r6f_pivflank_b $Q/q_s1a_7.txt 1 ) &
wait
echo "pivot a b (pre-check fix) done $(date +%T)" >> r6/chain_r6.log
printf "s1b 7\n" > $Q/q_val3_i1.txt
( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PA2"; ./sitl_run_x.sh r6f_pivflank_a2 $Q/q_s1a_7.txt 0 ) &
sleep 15; ( source $F; export X_TRIP_MIN=45; ./sitl_run_x.sh r6f_val3 $Q/q_val3_i1.txt 1 ) &
wait
echo "pivot a2 + pick-up (pre-check fix) done $(date +%T)" >> r6/chain_r6.log
