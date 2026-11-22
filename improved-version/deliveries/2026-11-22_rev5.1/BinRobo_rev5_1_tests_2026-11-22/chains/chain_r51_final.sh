#!/bin/bash
# 22 Nov: missions under the revision 5.1 settings: pause rule on, speed rule for the real lane
# (downhill 3 to 6 %: 0.3 m/s with a bin, 0.2 m/s empty; steeper than 6 %: 0.2 m/s with a bin, 0.15 m/s empty).
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 X_R5B=1 X_PPL_PAUSE=1
export X_VSLOPE="-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.06:0.2:0.15"
echo "final start $(date +%T)" >> r51/chain_r51.log
( ./sitl_run_x.sh r51_final /home/claude/s0/r51/sitl_q_final_i0.txt 0 ) &
sleep 20
( ./sitl_run_x.sh r51_final /home/claude/s0/r51/sitl_q_final_i1.txt 1 ) &
wait
echo "final end $(date +%T)" >> r51/chain_r51.log
