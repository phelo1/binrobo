#!/bin/bash
# 27 Nov: the full set on the frozen revision 6.1 code (r61/code_final.md5 is written at the start).
# 1 turn tests  2 people, fast cruise on (25 cases)  3 people, start settings (15 cases)  4 five closest cases with every seed at 1.0 m/s
# 5 the 60-mission suite, fast cruise on  6 start settings: three drop-offs, three pick-ups, three drops, three pick-ups
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r61/env_r61_fast.sh; ST=r61/env_r61_start.sh; SC=/home/claude/b2f_run/sitl/b2f/scripts
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
# the code is frozen from the level-2 trips of chain_e (02:18) on
( md5sum $SC/b2f_r6.py $SC/b2f_companion_x.py $SC/b2f_runner_x.py; md5sum r61/env_r61_fast.sh r61/env_r61_start.sh r61/env_r61_fast_v10.sh r6/env_r6_fast.sh r6/env_r6.sh r61/stress.sh r61/run2.sh r61/chain_f.sh ) > r61/code_final.md5
n0=$(grep -c "bad-lidar people done" r61/chain.log); until [ $(grep -c "bad-lidar people done" r61/chain.log) -gt ${CHF_N0:-$n0} ]; do sleep 10; done
echo "chain_f start $(date +%T)" >> r61/chain.log
PA='[{"kind":"person","a":[626,-1.2],"b":[600,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.33,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PA2='[{"kind":"person","a":[626,-1.2],"b":[600,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.33,"trig":[617.9,0.19],"trigger_d":0.4,"delay":10}]'
PB='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.35,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PC='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":40,"pause_at":0.295,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PY='[{"kind":"person","a":[22,0.5],"b":[4,0.5],"along":true,"speed":1.0,"pause":40,"pause_at":0.609,"trig":[9.69,-1.36],"trigger_d":0.4,"delay":37}]'
pair() { clr $1 $3; ( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$2"; ./sitl_run_x.sh $1 $Q/q_s1a_7.txt 0 ) & sleep 15; ( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$4"; ./sitl_run_x.sh $3 $Q/q_s1a_7.txt 1 ) & wait; }
pair r61f_turn_a "$PA" r61f_turn_a2 "$PA2"; pair r61f_turn_b "$PB" r61f_turn_c "$PC"
clr r61f_turn_y r61f_pick; ( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PY"; ./sitl_run_x.sh r61f_turn_y $Q/q_s1a_7.txt 0 ) & sleep 15; ( source $F; export X_TRIP_MIN=45; ./sitl_run_x.sh r61f_pick $Q/q_s1b_7.txt 1 ) & wait
echo "1 turn tests done $(date +%T)" >> r61/chain.log
r61/stress.sh $F r61f
echo "2 people fast done $(date +%T)" >> r61/chain.log
r61/stress.sh $ST r61s near26 near20 run26 run20 child35 side behind flank hug hugstand nearhedge30 stay1000 boxfar gapwalk26 gaprun26
echo "3 people start done $(date +%T)" >> r61/chain.log
r61/stress.sh r61/env_r61_fast_v10.sh r61v near31 near26 near20 run26 run20
echo "4 people v10 done $(date +%T)" >> r61/chain.log
clr r61f_suite; X_TRIP_MIN=45 r61/run2.sh $F r61f_suite /home/claude/s0/r4/sitl_q_r4_i0.txt /home/claude/s0/r4/sitl_q_r4_i1.txt
echo "5 suite fast done $(date +%T)" >> r61/chain.log
clr r61s_trips; X_TRIP_MIN=80 r61/run2.sh $ST r61s_trips r61/q_start_i0.txt r61/q_start_i1.txt
echo "6 start trips done $(date +%T)" >> r61/chain.log
clr r61b1_trip; X_LID_BAD="drop=0.15,dark=0.3,burst=0.02,false=2,rag=0.10,sway=0.03,bram=0.02,bramd=0.2" X_TRIP_MIN=60 r61/run2.sh $F r61b1_trip $Q/q_s1a_7.txt $Q/q_s1b_7.txt
echo "7 level-1 trips done $(date +%T)" >> r61/chain.log
echo "chain_f done $(date +%T)" >> r61/chain.log
