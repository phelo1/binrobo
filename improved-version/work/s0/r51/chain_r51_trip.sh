#!/bin/bash
# 22 Nov: one drop-off and one pick-up mission with the speed rule set for the real lane (nothing steeper than 8.4 %):
# slopes over 6 % at 0.2 m/s with a bin and 0.15 m/s empty, so that a touch stops inside the foam on wet leaves too. Pause rule on.
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 X_R5B=1 X_PPL_PAUSE=1
export X_VSLOPE="-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.3,0.06:0.2:0.15"
until grep -q "person end" r51/chain_r51.log; do sleep 10; done
echo "trip start $(date +%T)" >> r51/chain_r51.log
( ./sitl_run_x.sh r51_trip /home/claude/s0/r51/sitl_q_s1a7.txt 0 ) &
sleep 20
( ./sitl_run_x.sh r51_trip /home/claude/s0/r51/sitl_q_s1b7.txt 1 ) &
wait
echo "trip end $(date +%T)" >> r51/chain_r51.log
