#!/bin/bash
# 27 Nov, after the environment restart of 05:08: what chain_h, chain_i, chain_j and chain_k would have run, on the same frozen code.
# A step is skipped if all its result files are already there, so this script can be started again after another restart.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r61/env_r61_fast.sh; ST=r61/env_r61_start.sh; O=/home/claude/sitl_out
clr() { for n in "$@"; do rm -rf $O/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
have() { [ "$(find $O/$1 -name result.json 2>/dev/null | wc -l)" -ge "$2" ]; }
LB1="drop=0.15,dark=0.3,burst=0.02,false=2,rag=0.10,sway=0.03,bram=0.02,bramd=0.2"; LB2="drop=0.3,dark=0.6,burst=0.1,false=6,rag=0.2,sway=0.08,bram=0.05,bramd=0.2"
echo "chain_m start $(date +%T)" >> r61/chain.log
pkill -f sitl_run_x.sh; pkill -f b2f_runner_x.py; pkill -f "bin/ardurover"; sleep 2
# 1 hugstand31: the walker stops beside the fast robot (clean lidar, level 1, level 2)
HS='[{"kind":"person","a":[334,-1.4],"b":[270,-1.4],"along":true,"speed":1.2,"pause":30,"pause_at":0.31,"trig":[303,1.0],"trigger_d":1.5}]'
have r61f_hugstand31 3 || { clr r61f_hugstand31; X_MOVERS_SET="$HS" r61/run2.sh $F r61f_hugstand31 $Q/q_s5a_7.txt $Q/q_s5a_11_23.txt; }
have r61b1_hugstand31 3 || { clr r61b1_hugstand31; X_MOVERS_SET="$HS" X_LID_BAD="$LB1" r61/run2.sh $F r61b1_hugstand31 $Q/q_s5a_7.txt $Q/q_s5a_11_23.txt; }
have r61b2_hugstand31 3 || { clr r61b2_hugstand31; X_MOVERS_SET="$HS" X_LID_BAD="$LB2" r61/run2.sh $F r61b2_hugstand31 $Q/q_s5a_7.txt $Q/q_s5a_11_23.txt; }
echo "m1 hugstand31 done $(date +%T)" >> r61/chain.log
# 2 baselines with the walker rule off (X_R6_WALK=0): c = road end, y = yard
PC='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":40,"pause_at":0.295,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PY='[{"kind":"person","a":[22,0.5],"b":[4,0.5],"along":true,"speed":1.0,"pause":40,"pause_at":0.609,"trig":[9.69,-1.36],"trigger_d":0.4,"delay":37}]'
if ! have r61x_turn_c_nowalk 1 || ! have r61x_turn_y_nowalk 1; then
  clr r61x_turn_c_nowalk r61x_turn_y_nowalk
  ( source $F; export X_R6_WALK=0 X_TRIP_MIN=45 X_MOVERS_SET="$PC"; ./sitl_run_x.sh r61x_turn_c_nowalk $Q/q_s1a_7.txt 0 ) & sleep 15
  ( source $F; export X_R6_WALK=0 X_TRIP_MIN=45 X_MOVERS_SET="$PY"; ./sitl_run_x.sh r61x_turn_y_nowalk $Q/q_s1a_7.txt 1 ) & wait
fi
echo "m2 baselines done $(date +%T)" >> r61/chain.log
# 3 start settings: three drop-offs, three pick-ups, a three-drop mission, a three-pick-up mission
have r61s_trips 8 || { clr r61s_trips; X_TRIP_MIN=80 r61/run2.sh $ST r61s_trips /home/claude/s0/r61/q_start_i0.txt /home/claude/s0/r61/q_start_i1.txt; }
echo "m3 start trips done $(date +%T)" >> r61/chain.log
# 4 extras: leaf-season tables, a false camera person once a minute, the leaf-season switch, the middle option
have r61f_leaf 2 || { clr r61f_leaf; X_TRIP_MIN=45 r61/run2.sh r61/env_r61_fast_leaf.sh r61f_leaf $Q/q_s1a_7.txt $Q/q_s1b_7.txt; }
have r61f_phantom 2 || { clr r61f_phantom; X_TRIP_MIN=45 X_PHANTOM=1 r61/run2.sh $F r61f_phantom $Q/q_s1a_7.txt $Q/q_s1b_7.txt; }
have r61f_leafnogo 1 || { clr r61f_leafnogo; X_TRIP_MIN=45 X_LEAF_NOGO=1 r61/run2.sh $F r61f_leafnogo $Q/q_s1b_7.txt; }
have r61m_trip 2 || { clr r61m_trip; r61/run2.sh r61/env_r61_mid.sh r61m_trip $Q/q_s1a_7.txt $Q/q_s1b_7.txt; }
echo "chain_m done $(date +%T)" >> r61/chain.log
