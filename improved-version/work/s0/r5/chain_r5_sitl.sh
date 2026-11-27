#!/bin/bash
# Revision 5 driving software: the 60 missions, then extras (collection-day returns started at 16:30; keeping left on the camera alone; 198 kg).
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 $R5_EXTRA
echo "sitl start $(date +%T) extra=$R5_EXTRA" >> r5/chain_r5_sitl.log
( ./sitl_run_x.sh r5 /home/claude/s0/r4/sitl_q_r4_i0.txt 0 ) &
sleep 20
( ./sitl_run_x.sh r5 /home/claude/s0/r4/sitl_q_r4_i1.txt 1 ) &
wait
echo "sitl 60 end $(date +%T)" >> r5/chain_r5_sitl.log
( X_PICKUP_CLOCK=16:30 ./sitl_run_x.sh r5ret1630 /home/claude/s0/r5/sitl_q_ret_i0.txt 0; X_ROB_MASS=198.0 ./sitl_run_x.sh r5m198 /home/claude/s0/r5/sitl_q_m198.txt 0 ) &
sleep 20
( X_PICKUP_CLOCK=16:30 ./sitl_run_x.sh r5ret1630 /home/claude/s0/r5/sitl_q_ret_i1.txt 1; X_LID_FACE_OFF=1 ./sitl_run_x.sh r5camonly /home/claude/s0/r5/sitl_q_one.txt 1 ) &
wait
echo "sitl end $(date +%T)" >> r5/chain_r5_sitl.log
