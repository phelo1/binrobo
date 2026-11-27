#!/bin/bash
# 27 Nov: extras on the frozen revision 6.1 code, after chain_g. These are the runs the revision 6 note listed as "not run on the code in the pack".
# 1 leaf-season speed tables (drop-off, pick-up)  2 a false camera person once a minute (drop-off, pick-up)  3 the leaf-season switch (pick-up refused)
# 4 the middle option, no sprocket change (drop-off, pick-up)
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r61/env_r61_fast.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
until grep -q "^chain_g done" r61/chain.log; do sleep 10; done
echo "chain_h start $(date +%T)" >> r61/chain.log
clr r61f_leaf r61f_phantom r61f_leafnogo r61m_trip
X_TRIP_MIN=45 r61/run2.sh r61/env_r61_fast_leaf.sh r61f_leaf $Q/q_s1a_7.txt $Q/q_s1b_7.txt
X_TRIP_MIN=45 X_PHANTOM=1 r61/run2.sh $F r61f_phantom $Q/q_s1a_7.txt $Q/q_s1b_7.txt
X_TRIP_MIN=45 X_LEAF_NOGO=1 r61/run2.sh $F r61f_leafnogo $Q/q_s1b_7.txt
r61/run2.sh r61/env_r61_mid.sh r61m_trip $Q/q_s1a_7.txt $Q/q_s1b_7.txt
echo "chain_h done $(date +%T)" >> r61/chain.log
