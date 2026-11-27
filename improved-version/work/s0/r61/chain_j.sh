#!/bin/bash
# 27 Nov: one more people case on the frozen code. In the fast-cruise set the walker of "hugstand" stopped 9 m behind the robot (the robot
# had come further up the lane than at the start settings), so there the case was the same as "hug". hugstand31 moves the stopping point to
# where the fast robot stands: the walker stops 0.35 m from the far hedge, beside the robot, for 30 s. Clean lidar, level 1, level 2.
cd /home/claude/s0; Q=/home/claude/s0/r6; F=r61/env_r61_fast.sh
clr() { for n in "$@"; do rm -rf /home/claude/sitl_out/$n /home/claude/b2f_run/sitl/b2f/ckpt_$n; done; }
until grep -q "^chain_i done" r61/chain.log; do sleep 10; done
echo "chain_j start $(date +%T)" >> r61/chain.log
export X_MOVERS_SET='[{"kind":"person","a":[334,-1.4],"b":[270,-1.4],"along":true,"speed":1.2,"pause":30,"pause_at":0.31,"trig":[303,1.0],"trigger_d":1.5}]'
clr r61f_hugstand31 r61b1_hugstand31 r61b2_hugstand31
r61/run2.sh $F r61f_hugstand31 $Q/q_s5a_7.txt $Q/q_s5a_11_23.txt
X_LID_BAD="drop=0.15,dark=0.3,burst=0.02,false=2,rag=0.10,sway=0.03,bram=0.02,bramd=0.2" r61/run2.sh $F r61b1_hugstand31 $Q/q_s5a_7.txt $Q/q_s5a_11_23.txt
X_LID_BAD="drop=0.3,dark=0.6,burst=0.1,false=6,rag=0.2,sway=0.08,bram=0.05,bramd=0.2" r61/run2.sh $F r61b2_hugstand31 $Q/q_s5a_7.txt $Q/q_s5a_11_23.txt
echo "chain_j done $(date +%T)" >> r61/chain.log
