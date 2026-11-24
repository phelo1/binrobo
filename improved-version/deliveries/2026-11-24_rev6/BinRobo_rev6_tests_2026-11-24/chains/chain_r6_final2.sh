#!/bin/bash
# 24 Nov, final code and settings (firmware reset for the 2:1 stage; pivot watch; reworked pause timers). Everything in the note comes from this chain.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r6/env_r6_fast.sh; S=r6/env_r6_slow2.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
# 1. people stress, fast cruise
# 2. the 20 scenarios x 3 seeds of the B2-F score suite, fast cruise
clr r6f_suite; X_TRIP_MIN=45 r6/run2.sh $F r6f_suite /home/claude/s0/r4/sitl_q_r4_i0.txt /home/claude/s0/r4/sitl_q_r4_i1.txt
echo "suite fast done $(date +%T)" >> r6/chain_r6.log
# 3. someone walks up while the robot turns on the spot at the road end (a: from the road side, b: from the house side), stands 1.4 m from the turning centre for 30 s
PA='[{"kind":"person","a":[626,-1.2],"b":[600,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.33,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PB='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.35,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
clr r6f_pivflank_a r6f_pivflank_b
X_TRIP_MIN=45 X_MOVERS_SET="$PA" r6/run2.sh $F r6f_pivflank_a $Q/q_s1a_7.txt $Q/q_s1a_11.txt
X_TRIP_MIN=45 X_MOVERS_SET="$PB" r6/run2.sh $F r6f_pivflank_b $Q/q_s1a_7.txt $Q/q_s1a_11.txt
# 4. extras, fast: three pick-ups from 16:30; a false camera person once a minute; leaf-season speed tables; the leaf-season switch
printf "s3b 7\n" > $Q/q_s3b_7.txt; clr r6f_ret1630 r6f_phantom r6f_leaf r6f_leafnogo
X_TRIP_MIN=45 X_PICKUP_CLOCK=16:30 r6/run2.sh $F r6f_ret1630 $Q/q_s3b_7.txt
X_TRIP_MIN=45 X_PHANTOM=1 r6/run2.sh $F r6f_phantom $Q/q_s1a_7.txt $Q/q_s1b_7.txt
X_TRIP_MIN=45 X_VFAST="-1:1.0:1.0,0.005:0.8:0.8,0.03:0.6:0.5,0.06:0.5:0.15" X_VSLOPE="-1:0.35:0.35,0.005:0.35:0.3,0.03:0.3:0.2,0.06:0.2:0.15" r6/run2.sh $F r6f_leaf $Q/q_s1a_7.txt $Q/q_s1b_7.txt
X_TRIP_MIN=45 X_LEAF_NOGO=1 r6/run2.sh $F r6f_leafnogo $Q/q_s1b_7.txt
echo "extras fast done $(date +%T)" >> r6/chain_r6.log
# 5. people stress with the fast cruise switched off, same hardware
r6/stress.sh $S r6s2
echo "stress slow2 done $(date +%T)" >> r6/chain_r6.log
# 6. trips: fast cruise off on the new hardware; the middle option on the unchanged 5.1 drive
clr r6s2_trip r6m_trip
r6/run2.sh $S r6s2_trip $Q/q_s1a_7.txt $Q/q_s1b_7.txt
r6/run2.sh r6/env_r6_mid.sh r6m_trip $Q/q_s1a_7.txt $Q/q_s1b_7.txt
# 7. the gateway cases, both settings
SIDE_TRIG=3.0 r6/stress.sh $F r6f gapwalk26 gaprun26
r6/stress.sh $S r6s2 gapwalk26 gaprun26
echo "trips and gaps done $(date +%T)" >> r6/chain_r6.log
# 8. the score suite again with a false camera person once a minute
clr r6f_suite_ph; X_TRIP_MIN=45 X_PHANTOM=1 r6/run2.sh $F r6f_suite_ph /home/claude/s0/r4/sitl_q_r4_i0.txt /home/claude/s0/r4/sitl_q_r4_i1.txt
echo "final chain done $(date +%T)" >> r6/chain_r6.log
