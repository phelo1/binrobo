#!/bin/bash
# 27 Nov: 'proud of the face' rule for the joined-to-the-hedge test. Turn tests b and c again (the walker 0.3 to 0.45 m from the hedge),
# then a plain drop-off and pick-up (pass mark: no stop with nobody about).
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r61/env_r61_fast.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
for n in r61_stand_c r61_stand_y r61_plain; do [ -d /home/claude/sitl_out/$n ] && mv /home/claude/sitl_out/$n /home/claude/sitl_out/r61_before_fixes/${n}_before_proud; done
clr r61_stand_c r61_piv_b r61_plain
PC='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":40,"pause_at":0.295,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PB='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.35,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
echo "chain_c start $(date +%T)" >> r61/chain.log
( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PC"; ./sitl_run_x.sh r61_stand_c $Q/q_s1a_7.txt 0 ) &
sleep 15; ( source $F; export X_TRIP_MIN=45 X_MOVERS_SET="$PB"; ./sitl_run_x.sh r61_piv_b $Q/q_s1a_7.txt 1 ) &
wait
echo "stand c, pivot b (proud) done $(date +%T)" >> r61/chain.log
X_TRIP_MIN=45 r61/run2.sh $F r61_plain $Q/q_s1a_7.txt $Q/q_s1b_7.txt
echo "plain (proud) done $(date +%T)" >> r61/chain.log
