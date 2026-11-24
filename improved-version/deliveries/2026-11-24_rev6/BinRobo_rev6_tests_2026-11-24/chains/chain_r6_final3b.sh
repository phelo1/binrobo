#!/bin/bash
# 24 Nov, part 3b (after the pivot fix and its validation): the rest. Lane driving is unchanged by that fix.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r6/env_r6_fast.sh; S=r6/env_r6_slow2.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
# 4. extras, fast: leaf-season speed tables; a false camera person once a minute; the leaf-season switch
clr r6f_phantom r6f_leaf r6f_leafnogo
X_TRIP_MIN=45 X_VFAST="-1:1.0:1.0,0.005:0.8:0.8,0.03:0.6:0.5,0.06:0.5:0.15" X_VSLOPE="-1:0.35:0.35,0.005:0.35:0.3,0.03:0.3:0.2,0.06:0.2:0.15" r6/run2.sh $F r6f_leaf $Q/q_s1a_7.txt $Q/q_s1b_7.txt
X_TRIP_MIN=45 X_PHANTOM=1 r6/run2.sh $F r6f_phantom $Q/q_s1a_7.txt $Q/q_s1b_7.txt
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
# 8. the 48 fault and hazard runs of the score suite again with a false camera person once a minute (the 12 full missions are not repeated: time)
clr r6f_suite_ph; X_TRIP_MIN=45 X_PHANTOM=1 r6/run2.sh $F r6f_suite_ph $Q/q_short_i0.txt $Q/q_short_i1.txt
echo "final chain done $(date +%T)" >> r6/chain_r6.log
