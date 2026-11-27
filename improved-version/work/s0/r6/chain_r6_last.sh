#!/bin/bash
# 24 Nov, last part, on the final code (r6/code_final.md5): hedge faces fitted from 0.25 m bins; gateway look-ahead in the fast cruise.
# Both change lane driving, so the people cases are run again. The 60-mission suite is not (time): four missions and the pivot tests are.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r6/env_r6_fast.sh; S=r6/env_r6_slow2.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
# A. the gateway cases
SIDE_TRIG=3.0 r6/stress.sh $F r6f gapwalk26 gaprun26
r6/stress.sh $S r6s2 gapwalk26 gaprun26
echo "gaps (final) done $(date +%T)" >> r6/chain_r6.log
# B1. all people cases, fast cruise on
SIDE_TRIG=3.0 r6/stress.sh $F r6f
echo "people fast (final) done $(date +%T)" >> r6/chain_r6.log
# B2. the eleven hardest people cases, fast cruise off
r6/stress.sh $S r6s2 near26 near20 run26 run20 child35 side behind flank nearhedge30 stay1000 boxfar
echo "people off (final) done $(date +%T)" >> r6/chain_r6.log
# C. missions: drop-off, pick-up, three drops, three pick-ups; then the two pivot tests
clr r6f_val2 r6f_pivflank_a r6f_pivflank_b; printf "s1a 7\ns3a 7\n" > $Q/q_val_i0.txt; printf "s1b 7\ns3b 11\n" > $Q/q_val_i1.txt
X_TRIP_MIN=45 r6/run2.sh $F r6f_val2 $Q/q_val_i0.txt $Q/q_val_i1.txt
PA='[{"kind":"person","a":[626,-1.2],"b":[600,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.33,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PB='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.35,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PA"; ./sitl_run_x.sh r6f_pivflank_a $Q/q_s1a_7.txt 0 ) &
sleep 15; ( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PB"; ./sitl_run_x.sh r6f_pivflank_b $Q/q_s1a_7.txt 1 ) &
wait
echo "missions (final) done $(date +%T)" >> r6/chain_r6.log
# D. the close cases with every seed at the full 1.0 m/s
SIDE_TRIG=3.0 r6/stress.sh r6/env_r6_fast_v10.sh r6v near31 near26 near20 run26 run20
echo "last chain done $(date +%T)" >> r6/chain_r6.log
