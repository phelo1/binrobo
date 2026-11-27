#!/bin/bash
# 24 Nov: the 20 scenarios x 3 seeds of the B2-F score suite with the revision 6 fast settings, then extras.
cd /home/claude/s0; Q=/home/claude/s0/r6
until grep -q "stress all done" r6/chain_r6.log; do sleep 30; done
export X_TRIP_MIN=45
r6/run2.sh r6/env_r6_fast.sh r6f_suite /home/claude/s0/r4/sitl_q_r4_i0.txt /home/claude/s0/r4/sitl_q_r4_i1.txt
# extras: pick-up day from 16:30; false camera persons once a minute on one drop-off and one pick-up; leaf-season speeds on one pick-up
printf "s3b 7\n" > $Q/q_s3b_7.txt
( X_PICKUP_CLOCK=16:30 r6/run2.sh r6/env_r6_fast.sh r6f_ret1630 $Q/q_s3b_7.txt ) 
X_PHANTOM=1 r6/run2.sh r6/env_r6_fast.sh r6f_phantom $Q/q_s1a_7.txt $Q/q_s1b_7.txt
X_VFAST="-1:1.0:1.0,0.005:0.8:0.8,0.03:0.6:0.5,0.06:0.5:0.15" X_VSLOPE="-1:0.35:0.35,0.005:0.35:0.3,0.03:0.3:0.2,0.06:0.2:0.15" r6/run2.sh r6/env_r6_fast.sh r6f_leaf $Q/q_s1a_7.txt $Q/q_s1b_7.txt
r6/run2.sh r6/env_r6.sh r6s_trip $Q/q_s1a_7.txt $Q/q_s1b_7.txt
echo "suite all done $(date +%T)" >> r6/chain_r6.log
# added: the gateway cases, both speed sets
r6/stress.sh r6/env_r6.sh r6s gapwalk26 gaprun26
r6/stress.sh r6/env_r6_fast.sh r6f gapwalk26 gaprun26
echo "gap cases done $(date +%T)" >> r6/chain_r6.log
# added: the middle option - no sprocket change (wheel speed 0.8 m/s flat out as B2-F), cruise 0.6 m/s on a clear lane
r6/run2.sh r6/env_r6_mid.sh r6m_trip /home/claude/s0/r6/q_s1a_7.txt /home/claude/s0/r6/q_s1b_7.txt
echo "mid option done $(date +%T)" >> r6/chain_r6.log
