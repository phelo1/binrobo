#!/bin/bash
# 22 Nov: three pick-ups on collection day started at 16:30 (as in revision 5), under the revision 5.1 settings.
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 X_R5B=1 X_PPL_PAUSE=1 X_PICKUP_CLOCK=16:30
export X_VSLOPE="-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.06:0.2:0.15"
echo "ret start $(date +%T)" >> r51/chain_r51.log
./sitl_run_x.sh r51_final_ret1630 /home/claude/s0/r51/sitl_q_ret.txt 2
echo "ret end $(date +%T)" >> r51/chain_r51.log
