#!/bin/bash
# 24 Nov, added after the review items M-1 "restart beside a person" and "pivot flanks":
#  flank    (s5a) someone walks up the lane towards the robot on its right, stops beside it for 30 s, walks on
#  pivflank (s1a) the robot is turning on the spot at the road end; someone walks up and stands 1.4 m from the turning centre for 30 s
#                 a: from the road side (in front of the robot as it arrives)   b: from the house side (behind it)
cd /home/claude/s0; Q=/home/claude/s0/r6
until grep -q "${WAIT_FOR:-mid option done}" r6/chain_r6.log; do sleep 30; done
FL='[{"kind":"person","a":[324,-0.6],"b":[280,-0.6],"along":true,"speed":1.2,"pause":30,"pause_at":0.398,"trig":[303,1.0],"trigger_d":1.5}]'
PA='[{"kind":"person","a":[626,-1.2],"b":[600,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.33,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
PB='[{"kind":"person","a":[609,-1.2],"b":[633,-1.2],"along":true,"speed":1.0,"pause":30,"pause_at":0.35,"trig":[617.9,0.19],"trigger_d":0.4,"delay":6}]'
for pair in "r6/env_r6.sh r6s" "${FASTENV:-r6/env_r6_fast.sh} r6f"; do
  set -- $pair
  rm -rf /home/claude/sitl_out/${2}_flank /home/claude/b2f_run/sitl/b2f/ckpt_${2}_flank
  X_MOVERS_SET="$FL" r6/run2.sh $1 ${2}_flank $Q/q_s5a_7.txt $Q/q_s5a_11_23.txt
done
for v in a b; do
  if [ $v = a ]; then M="$PA"; else M="$PB"; fi
  rm -rf /home/claude/sitl_out/r6f_pivflank_$v /home/claude/b2f_run/sitl/b2f/ckpt_r6f_pivflank_$v
  X_TRIP_MIN=45 X_MOVERS_SET="$M" r6/run2.sh ${FASTENV:-r6/env_r6_fast.sh} r6f_pivflank_$v $Q/q_s1a_7.txt $Q/q_s1a_11.txt
done
echo "extra done $(date +%T)" >> r6/chain_r6.log
